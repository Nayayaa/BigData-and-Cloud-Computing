# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from aiohttp import web
from aiohttp.web import Request, Response, json_response

from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    MemoryStorage,
    ConversationState,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity

from config import DefaultConfig
from bot.main_bot import MainBot
from dialogs.main_dialog import MainDialog

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
CONFIG = DefaultConfig()

# -----------------------------------------------------------------------------
# Adapter and State
# -----------------------------------------------------------------------------
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# In-memory storage for demo purposes (you can switch to Blob/Redis later)
MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)

# The root dialog and bot
DIALOG = MainDialog(USER_STATE)
BOT = MainBot(DIALOG, CONVERSATION_STATE, USER_STATE)

# -----------------------------------------------------------------------------
# Global on_error handler for the Adapter
# -----------------------------------------------------------------------------
async def on_error(turn_context: TurnContext, error: Exception):
    # Log to stderr so you see it in docker logs
    print(f"\n[on_turn_error] {error}\n", file=sys.stderr)
    traceback.print_exc()

    # Send a trace activity (useful in Emulator)
    await turn_context.send_activity("Desculpe, ocorreu um erro ao processar sua mensagem.")

    # Clear out state to avoid stuck dialogs
    await CONVERSATION_STATE.delete(turn_context)
    await USER_STATE.delete(turn_context)

ADAPTER.on_turn_error = on_error

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _rewrite_service_url_for_docker(activity: Activity) -> None:
    """
    When chatting via Bot Framework Emulator on the HOST, the Emulator sets a
    serviceUrl like 'http://localhost:52840/...'. From inside a Docker container,
    'localhost' is the *container*, not the Host, so replies fail.

    We rewrite 'localhost' to 'host.docker.internal' so the bot can call back
    to the Emulator running on the Host (supported on Docker Desktop Win/macOS).
    """
    try:
        su = activity.service_url or ""
        if su.startswith("http://localhost") or su.startswith("https://localhost"):
            u = urlparse(su)
            # preserve scheme/port; swap hostname
            new_netloc = f"host.docker.internal:{u.port}" if u.port else "host.docker.internal"
            new_url = urlunparse((u.scheme, new_netloc, u.path, u.params, u.query, u.fragment))
            activity.service_url = new_url
    except Exception:
        # don't let a rewrite issue break the request
        pass

# -----------------------------------------------------------------------------
# AIOHTTP request handler
# -----------------------------------------------------------------------------
async def messages(req: Request) -> Response:
    """
    Bot Framework endpoint. The Emulator (or Channel) will POST activities here.
    """
    if "application/json" not in req.headers.get("Content-Type", ""):
        return Response(status=415)  # Unsupported Media Type

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    # Important for Docker + Emulator on Host:
    _rewrite_service_url_for_docker(activity)

    # Process the activity with the adapter
    invoke_response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    if invoke_response:
        return json_response(data=invoke_response.body, status=invoke_response.status)
    return Response(status=201)

# -----------------------------------------------------------------------------
# AIOHTTP app
# -----------------------------------------------------------------------------
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Bind to all interfaces so Docker port mapping works (0.0.0.0:3978)
        web.run_app(APP, host="0.0.0.0", port=CONFIG.PORT)
    except Exception as error:
        print(f"[FATAL] {error}", file=sys.stderr)
        raise
