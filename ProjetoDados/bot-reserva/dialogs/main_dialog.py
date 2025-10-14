from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice
from dialogs.reserva_hotel import ReservaHotelDialog

class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__("MainDialog")
        self.user_state = user_state

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ReservaHotelDialog(user_state))
        self.add_dialog(
            WaterfallDialog("MainWaterfall", [self.menu_step, self.route_step])
        )
        self.initial_dialog_id = "MainWaterfall"

    async def menu_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Escolha uma opção:"),
                choices=[Choice("Fazer Reserva de Hotel"), Choice("Ajuda")],
            ),
        )

    async def route_step(self, step_context: WaterfallStepContext):
        option = step_context.result.value
        if option == "Fazer Reserva de Hotel":
            return await step_context.begin_dialog("ReservaHotelDialog")
        elif option == "Ajuda":
            await step_context.context.send_activity(
                MessageFactory.text(
                    "Eu posso te ajudar a fazer uma reserva de hotel."
                )
            )
        return await step_context.end_dialog()
