from dataclasses import dataclass

from bot.formatters.messages import format_help_message, format_start_message
from bot.keyboards.main_menu import build_main_menu_keyboard, build_webapp_inline_keyboard


@dataclass(frozen=True)
class BotReply:
    chat_id: int
    text: str
    reply_markup: dict | None = None


class CommandHandlers:
    def handle_start(self, chat_id: int) -> BotReply:
        return BotReply(
            chat_id=chat_id,
            text=format_start_message(),
            reply_markup=build_main_menu_keyboard(),
        )

    def handle_help(self, chat_id: int) -> BotReply:
        return BotReply(
            chat_id=chat_id,
            text=format_help_message(),
            reply_markup=build_main_menu_keyboard(),
        )

    def handle_app(self, chat_id: int) -> BotReply:
        reply_markup = build_webapp_inline_keyboard()
        if reply_markup is None:
            return BotReply(
                chat_id=chat_id,
                text="Web App URL hali sozlanmagan. TELEGRAM_WEBAPP_URL ni production URL bilan to'ldiring.",
            )
        return BotReply(
            chat_id=chat_id,
            text="CarCare Web App",
            reply_markup=reply_markup,
        )
