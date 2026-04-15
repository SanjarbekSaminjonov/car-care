from unittest import mock

from django.test import SimpleTestCase

from bot.handlers.odometer_flow import OdometerFlowHandlers


class OdometerFlowHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = OdometerFlowHandlers()

    @mock.patch("bot.handlers.odometer_flow.save_flow_state")
    def test_start_flow(self, save_state) -> None:
        reply = self.handlers.start_manual_update(chat_id=51)

        self.assertIn("Davlat raqamini", reply.text)
        save_state.assert_called_once()

    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_invalid_value_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(state_name="awaiting_value", state_payload={"plate_number": "01A123BC"})

        reply = self.handlers.handle_flow_input(chat_id=51, text="12k")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("faqat raqam", reply.text)

    @mock.patch("bot.handlers.odometer_flow.clear_flow_state")
    @mock.patch("bot.handlers.odometer_flow.create_odometer_for_chat")
    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_confirm_happy_path(self, get_state, create_entry, clear_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={"plate_number": "01A123BC", "value": 120500},
        )
        create_entry.return_value = mock.Mock(car=mock.Mock(plate_number="01A123BC"), value=120500)

        reply = self.handlers.handle_flow_input(chat_id=51, text="yes")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Odometr saqlandi", reply.text)
        clear_state.assert_called_once()
