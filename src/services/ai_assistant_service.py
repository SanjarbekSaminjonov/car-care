import json
from dataclasses import dataclass
from typing import Protocol

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.assistant.models import AssistantInteraction, AssistantInteractionStatus
from integrations.ai.openai_compatible import ChatCompletionResult, OpenAICompatibleChatProvider
from integrations.ai.settings import AIAssistantSettingsError, get_ai_assistant_settings
from queries.assistant_context import get_car_context_for_user
from services.telegram_account_service import get_telegram_account_for_chat


SYSTEM_PROMPT = (
    "You are the CarCare assistant. Answer practical car maintenance questions for "
    "the Telegram user. Use the provided car context for user-specific facts. If the "
    "context is missing, say what information is missing instead of inventing it. "
    "Keep answers concise and safe, and recommend a qualified mechanic for safety "
    "critical issues."
)


class ChatProvider(Protocol):
    provider_name: str
    model_name: str

    def complete_chat(self, *, messages: list[dict[str, str]]) -> ChatCompletionResult:
        ...


class AIAssistantProviderFailure(RuntimeError):
    """Raised when the AI provider cannot answer."""


@dataclass(frozen=True)
class AIAssistantAnswer:
    answer: str
    interaction: AssistantInteraction


def _build_messages(*, question: str, car_context: dict) -> list[dict[str, str]]:
    context_text = json.dumps(car_context, ensure_ascii=False)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Car context JSON:\n"
                f"{context_text}\n\n"
                "User question:\n"
                f"{question}"
            ),
        },
    ]


def _get_default_provider() -> ChatProvider:
    assistant_settings = get_ai_assistant_settings()
    assistant_settings.validate_for_provider()
    return OpenAICompatibleChatProvider(
        api_key=assistant_settings.api_key,
        base_url=assistant_settings.base_url,
        model_name=assistant_settings.model,
        timeout_seconds=assistant_settings.timeout_seconds,
        provider_name=assistant_settings.provider,
    )


def answer_car_question_for_chat(
    *,
    chat_id: int,
    telegram_user_id: int,
    question: str,
    provider: ChatProvider | None = None,
) -> AIAssistantAnswer:
    normalized_question = question.strip()
    if not normalized_question:
        raise ValidationError("Question is required.")

    telegram_account = get_telegram_account_for_chat(
        chat_id=chat_id,
        telegram_user_id=telegram_user_id,
    )
    assistant_settings = get_ai_assistant_settings()
    max_records = assistant_settings.max_context_records
    car_context = get_car_context_for_user(
        user_id=telegram_account.user_id,
        max_records=max_records,
    )
    chat_provider = provider or _get_default_provider()
    messages = _build_messages(question=normalized_question, car_context=car_context)

    try:
        result = chat_provider.complete_chat(messages=messages)
    except AIAssistantSettingsError:
        raise
    except Exception as exc:
        interaction = AssistantInteraction.objects.create(
            telegram_account=telegram_account,
            user=telegram_account.user,
            chat_id=chat_id,
            question=normalized_question,
            provider=chat_provider.provider_name,
            model_name=chat_provider.model_name,
            status=AssistantInteractionStatus.FAILED,
            car_context=car_context,
            error_message=str(exc)[:2000],
            completed_at=timezone.now(),
        )
        raise AIAssistantProviderFailure("AI assistant provider failed.") from exc

    interaction = AssistantInteraction.objects.create(
        telegram_account=telegram_account,
        user=telegram_account.user,
        chat_id=chat_id,
        question=normalized_question,
        answer=result.content,
        provider=chat_provider.provider_name,
        model_name=chat_provider.model_name,
        status=AssistantInteractionStatus.SUCCEEDED,
        car_context=car_context,
        response_metadata=result.metadata,
        completed_at=timezone.now(),
    )
    return AIAssistantAnswer(answer=result.content, interaction=interaction)
