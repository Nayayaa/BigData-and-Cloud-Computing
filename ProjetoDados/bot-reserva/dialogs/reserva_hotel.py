from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt, NumberPrompt, ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice
import aiohttp
from config import DefaultConfig

class ReservaHotelDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(ReservaHotelDialog, self).__init__("ReservaHotelDialog")
        self.user_state = user_state

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                "ReservaHotelWaterfall",
                [
                    self.ask_name_step,
                    self.ask_email_step,
                    self.ask_checkin_step,
                    self.ask_checkout_step,
                    self.ask_guests_step,
                    self.ask_roomtype_step,
                    self.confirm_and_save_step,
                ],
            )
        )
        self.initial_dialog_id = "ReservaHotelWaterfall"

    async def ask_name_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Qual é o seu nome completo?")),
        )

    async def ask_email_step(self, step_context: WaterfallStepContext):
        step_context.values["nome"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Qual é o seu e-mail?")),
        )

    async def ask_checkin_step(self, step_context: WaterfallStepContext):
        step_context.values["email"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Data de check-in (YYYY-MM-DD):")),
        )

    async def ask_checkout_step(self, step_context: WaterfallStepContext):
        step_context.values["checkin"] = step_context.result
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Data de check-out (YYYY-MM-DD):")),
        )

    async def ask_guests_step(self, step_context: WaterfallStepContext):
        step_context.values["checkout"] = step_context.result
        return await step_context.prompt(
            NumberPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Quantos hóspedes?")),
        )

    async def ask_roomtype_step(self, step_context: WaterfallStepContext):
        step_context.values["hospedes"] = int(step_context.result)
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Tipo de quarto?"),
                choices=[Choice("Standard"), Choice("Deluxe"), Choice("Suite")],
            ),
        )

    async def confirm_and_save_step(self, step_context: WaterfallStepContext):
        step_context.values["tipo_quarto"] = step_context.result.value
        chat_history = (
            "Q: Qual é o seu nome completo?\nA: {nome}\n"
            "Q: Qual é o seu e-mail?\nA: {email}\n"
            "Q: Data de check-in (YYYY-MM-DD)?\nA: {checkin}\n"
            "Q: Data de check-out (YYYY-MM-DD)?\nA: {checkout}\n"
            "Q: Quantos hóspedes?\nA: {hospedes}\n"
            "Q: Tipo de quarto?\nA: {tipo_quarto}\n"
        ).format(
            nome=step_context.values["nome"],
            email=step_context.values["email"],
            checkin=step_context.values["checkin"],
            checkout=step_context.values["checkout"],
            hospedes=step_context.values["hospedes"],
            tipo_quarto=step_context.values["tipo_quarto"]
        )

        dados = {
            "nome": step_context.values["nome"],
            "email": step_context.values["email"],
            "checkin": step_context.values["checkin"],
            "checkout": step_context.values["checkout"],
            "hospedes": step_context.values["hospedes"],
            "tipoQuarto": step_context.values["tipo_quarto"],
            "chatHistory": chat_history,
        }

        url = DefaultConfig.BACKEND_URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=dados, timeout=20) as resp:
                    if resp.status in (200, 201):
                        try:
                            body = await resp.json()
                            reserva_id = body.get("id", "(sem id)")
                        except Exception:
                            reserva_id = "(sem id)"
                        await step_context.context.send_activity(
                            MessageFactory.text(f"Reserva criada com sucesso! Número: {reserva_id}")
                        )
                    else:
                        txt = await resp.text()
                        await step_context.context.send_activity(
                            MessageFactory.text(f"Não foi possível salvar a reserva (HTTP {resp.status}). {txt}")
                        )
        except Exception as e:
            await step_context.context.send_activity(
                MessageFactory.text(f"Erro ao comunicar com o backend: {e}")
            )

        return await step_context.end_dialog()
