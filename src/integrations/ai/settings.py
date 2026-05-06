from dataclasses import dataclass

from django.conf import settings


class AIAssistantSettingsError(RuntimeError):
    """Raised when AI assistant runtime settings are not usable."""


@dataclass(frozen=True)
class AIAssistantRuntimeSettings:
    enabled: bool
    provider: str
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int
    max_context_records: int

    def validate_for_provider(self) -> None:
        if not self.enabled:
            raise AIAssistantSettingsError("AI assistant is disabled.")
        if not self.api_key.strip():
            raise AIAssistantSettingsError("AI_ASSISTANT_API_KEY is required.")
        if not self.base_url.strip():
            raise AIAssistantSettingsError("AI_ASSISTANT_BASE_URL is required.")
        if not self.model.strip():
            raise AIAssistantSettingsError("AI_ASSISTANT_MODEL is required.")
        if self.timeout_seconds <= 0:
            raise AIAssistantSettingsError("AI_ASSISTANT_TIMEOUT_SECONDS must be positive.")
        if self.max_context_records <= 0:
            raise AIAssistantSettingsError("AI_ASSISTANT_MAX_CONTEXT_RECORDS must be positive.")


def get_ai_assistant_settings() -> AIAssistantRuntimeSettings:
    return AIAssistantRuntimeSettings(
        enabled=bool(settings.AI_ASSISTANT_ENABLED),
        provider=str(settings.AI_ASSISTANT_PROVIDER),
        api_key=str(settings.AI_ASSISTANT_API_KEY),
        base_url=str(settings.AI_ASSISTANT_BASE_URL),
        model=str(settings.AI_ASSISTANT_MODEL),
        timeout_seconds=int(settings.AI_ASSISTANT_TIMEOUT_SECONDS),
        max_context_records=int(settings.AI_ASSISTANT_MAX_CONTEXT_RECORDS),
    )
