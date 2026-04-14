from unittest import mock

from django.test import SimpleTestCase

from services.conversation_state_service import (
    cleanup_expired_flow_states,
    clear_flow_state,
    get_flow_state,
    save_flow_state,
)


class ConversationStateServiceTests(SimpleTestCase):
    @mock.patch("services.conversation_state_service.BotConversationState")
    @mock.patch("services.conversation_state_service.TelegramAccount")
    def test_save_flow_state_calls_update_or_create(self, telegram_account_model, state_model) -> None:
        telegram_account_model.objects.filter.return_value.first.return_value = None

        save_flow_state(
            chat_id=1,
            flow_name="car_add",
            state_name="awaiting_plate",
            state_payload={"plate_number": "01A123BC"},
        )

        state_model.objects.update_or_create.assert_called_once()

    @mock.patch("services.conversation_state_service.BotConversationState")
    def test_get_flow_state_uses_non_expired_filter(self, state_model) -> None:
        queryset = state_model.objects.filter.return_value
        queryset.order_by.return_value.first.return_value = None

        get_flow_state(chat_id=1, flow_name="car_add")

        state_model.objects.filter.assert_called_once()

    @mock.patch("services.conversation_state_service.BotConversationState")
    def test_clear_flow_state_deletes(self, state_model) -> None:
        state_model.objects.filter.return_value.delete.return_value = (2, {})

        deleted = clear_flow_state(chat_id=1, flow_name="car_add")

        self.assertEqual(deleted, 2)

    @mock.patch("services.conversation_state_service.BotConversationState")
    def test_cleanup_expired_flow_states_deletes(self, state_model) -> None:
        state_model.objects.filter.return_value.delete.return_value = (3, {})

        deleted = cleanup_expired_flow_states()

        self.assertEqual(deleted, 3)
