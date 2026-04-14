from unittest import mock

from django.test import SimpleTestCase

from bot.handlers.maintenance_flow import MaintenanceFlowHandlers


class MaintenanceFlowHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = MaintenanceFlowHandlers()

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    def test_start_flow(self, save_state) -> None:
        reply = self.handlers.start_add_maintenance(chat_id=44)

        self.assertIn("Qaysi mashina", reply.text)
        save_state.assert_called_once()

    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_invalid_odometer_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_odometer",
            state_payload={"plate_number": "01A124BC", "title": "Brake check"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="12k")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Odometr faqat raqam", reply.text)

    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_invalid_confirmation_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={
                "plate_number": "01A125BC",
                "title": "ATF service",
                "odometer": 99000,
                "item_name": "ATF",
                "item_amount": "350000",
            },
        )

        reply = self.handlers.handle_flow_input(chat_id=46, text="ok")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("'yes'", reply.text)
