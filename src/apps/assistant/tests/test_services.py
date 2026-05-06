from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.assistant.models import AssistantInteraction, AssistantInteractionStatus
from apps.cars.models import Car, CarMembership, MembershipRole, MembershipStatus
from apps.maintenance.models import MaintenanceRecord, MaintenanceStatus
from apps.telegram.models import TelegramAccount
from integrations.ai.openai_compatible import ChatCompletionResult
from services.ai_assistant_service import (
    AIAssistantProviderFailure,
    answer_car_question_for_chat,
)


class FakeProvider:
    provider_name = "fake-provider"
    model_name = "fake-model"

    def __init__(self, *, answer: str = "Use 5W-30 oil.", error: Exception | None = None) -> None:
        self.answer = answer
        self.error = error
        self.messages: list[dict[str, str]] = []

    def complete_chat(self, *, messages: list[dict[str, str]]) -> ChatCompletionResult:
        self.messages = messages
        if self.error is not None:
            raise self.error
        return ChatCompletionResult(
            content=self.answer,
            metadata={"usage": {"total_tokens": 42}},
        )


@override_settings(AI_ASSISTANT_MAX_CONTEXT_RECORDS=2)
class AIAssistantServiceTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="driver", password="x")
        self.account = TelegramAccount.objects.create(
            user=self.user,
            telegram_user_id=9001,
            chat_id=9101,
        )
        self.car = Car.objects.create(
            plate_number="01A123BC",
            normalized_plate_number="01A123BC",
            brand="Toyota",
            model="Corolla",
            year=2022,
            current_odometer=52_000,
        )
        CarMembership.objects.create(
            car=self.car,
            user=self.user,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
        )
        MaintenanceRecord.objects.create(
            car=self.car,
            event_date=timezone.localdate(),
            odometer=51_000,
            title="Oil change",
            description="Synthetic oil",
            total_amount="350000",
            created_by=self.user,
            status=MaintenanceStatus.FINAL,
        )

    def test_answer_logs_success_with_car_context(self) -> None:
        provider = FakeProvider(answer="Oil change is due soon.")

        result = answer_car_question_for_chat(
            chat_id=self.account.chat_id,
            telegram_user_id=self.account.telegram_user_id,
            question="When should I change oil?",
            provider=provider,
        )

        interaction = AssistantInteraction.objects.get()
        self.assertEqual(result.interaction, interaction)
        self.assertEqual(interaction.status, AssistantInteractionStatus.SUCCEEDED)
        self.assertEqual(interaction.answer, "Oil change is due soon.")
        self.assertEqual(interaction.provider, "fake-provider")
        self.assertEqual(interaction.model_name, "fake-model")
        self.assertEqual(interaction.response_metadata["usage"]["total_tokens"], 42)
        self.assertEqual(interaction.car_context["cars"][0]["plate_number"], "01A123BC")
        self.assertIn("Toyota", provider.messages[1]["content"])

    def test_provider_failure_logs_failed_interaction(self) -> None:
        provider = FakeProvider(error=RuntimeError("upstream unavailable"))

        with self.assertRaises(AIAssistantProviderFailure):
            answer_car_question_for_chat(
                chat_id=self.account.chat_id,
                telegram_user_id=self.account.telegram_user_id,
                question="Diagnose noise",
                provider=provider,
            )

        interaction = AssistantInteraction.objects.get()
        self.assertEqual(interaction.status, AssistantInteractionStatus.FAILED)
        self.assertEqual(interaction.answer, "")
        self.assertIn("upstream unavailable", interaction.error_message)
        self.assertEqual(interaction.car_context["cars"][0]["recent_maintenance"][0]["title"], "Oil change")
