from types import SimpleNamespace
from unittest import mock

from django.test import TestCase

from apps.telegram.models import BotConversationState
from bot.dispatchers.update_dispatcher import UpdateDispatcher


class AIAssistantDispatcherTests(TestCase):
    def test_ask_command_with_inline_question_returns_answer(self) -> None:
        dispatcher = UpdateDispatcher()
        update = {
            "message": {
                "chat": {"id": 7001},
                "from": {"id": 8001, "username": "driver"},
                "text": "/ask Should I change oil?",
            }
        }

        with mock.patch(
            "bot.handlers.ai_assistant.answer_car_question_for_chat",
            return_value=SimpleNamespace(answer="Change it every 8,000-10,000 km."),
        ) as answer:
            reply = dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertEqual(reply.text, "Change it every 8,000-10,000 km.")
        answer.assert_called_once()
        self.assertEqual(answer.call_args.kwargs["question"], "Should I change oil?")

    def test_ask_command_without_question_uses_persisted_one_step_flow(self) -> None:
        dispatcher = UpdateDispatcher()
        start_update = {
            "message": {
                "chat": {"id": 7002},
                "from": {"id": 8002, "username": "driver2"},
                "text": "/ai",
            }
        }

        start_reply = dispatcher.dispatch(start_update)

        self.assertIsNotNone(start_reply)
        self.assertTrue(
            BotConversationState.objects.filter(
                chat_id=7002,
                flow_name="ai_assistant",
                state_name="awaiting_question",
            ).exists()
        )

        question_update = {
            "message": {
                "chat": {"id": 7002},
                "from": {"id": 8002, "username": "driver2"},
                "text": "Why is the engine hot?",
            }
        }
        with mock.patch(
            "bot.handlers.ai_assistant.answer_car_question_for_chat",
            return_value=SimpleNamespace(answer="Stop safely and check coolant level."),
        ):
            reply = dispatcher.dispatch(question_update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertEqual(reply.text, "Stop safely and check coolant level.")
        self.assertFalse(
            BotConversationState.objects.filter(
                chat_id=7002,
                flow_name="ai_assistant",
            ).exists()
        )
