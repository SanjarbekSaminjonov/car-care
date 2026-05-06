from django.core.exceptions import ValidationError

from apps.telegram.models import TelegramAccount
from bot.handlers.commands import BotReply
from bot.handlers.errors import format_validation_error
from integrations.ai.settings import AIAssistantSettingsError
from services.ai_assistant_service import (
    AIAssistantProviderFailure,
    answer_car_question_for_chat,
)
from services.conversation_state_service import clear_flow_state, get_flow_state, save_flow_state

FLOW_NAME = "ai_assistant"


class AIAssistantHandlers:
    def start_ask(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        question: str = "",
    ) -> BotReply:
        if question.strip():
            return self._answer_question(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                question=question,
            )

        save_flow_state(
            chat_id=chat_id,
            flow_name=FLOW_NAME,
            state_name="awaiting_question",
            state_payload={},
        )
        return BotReply(
            chat_id=chat_id,
            text="Mashina bo'yicha savolingizni yozing.",
        )

    def cancel(self, chat_id: int) -> BotReply:
        clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        return BotReply(chat_id=chat_id, text="AI assistant flow bekor qilindi.")

    def handle_flow_input(
        self,
        *,
        chat_id: int,
        text: str,
        telegram_user_id: int | None = None,
    ) -> BotReply | None:
        state = get_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
        if state is None:
            return None

        if state.state_name == "awaiting_question":
            clear_flow_state(chat_id=chat_id, flow_name=FLOW_NAME)
            return self._answer_question(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                question=text,
            )

        return None

    def _answer_question(
        self,
        *,
        chat_id: int,
        telegram_user_id: int | None,
        question: str,
    ) -> BotReply:
        if telegram_user_id is None:
            return BotReply(
                chat_id=chat_id,
                text="Telegram foydalanuvchi aniqlanmadi. /start bilan qayta urinib ko'ring.",
            )

        try:
            answer = answer_car_question_for_chat(
                chat_id=chat_id,
                telegram_user_id=telegram_user_id,
                question=question,
            )
        except ValidationError as exc:
            return BotReply(chat_id=chat_id, text=format_validation_error(exc))
        except TelegramAccount.DoesNotExist:
            return BotReply(
                chat_id=chat_id,
                text="Telegram account topilmadi. /start bilan qayta urinib ko'ring.",
            )
        except AIAssistantSettingsError:
            return BotReply(
                chat_id=chat_id,
                text="AI assistant hozir sozlanmagan. Administratorga murojaat qiling.",
            )
        except AIAssistantProviderFailure:
            return BotReply(
                chat_id=chat_id,
                text="AI assistant javob bera olmadi. Keyinroq qayta urinib ko'ring.",
            )

        return BotReply(chat_id=chat_id, text=answer.answer)
