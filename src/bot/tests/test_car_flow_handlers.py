from unittest import mock

from django.test import SimpleTestCase

from bot.handlers.car_flow import CarFlowHandlers


class CarFlowHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = CarFlowHandlers()

    @mock.patch("bot.handlers.car_flow.save_flow_state")
    def test_start_add_car_sets_initial_state(self, save_state) -> None:
        start_reply = self.handlers.start_add_car(chat_id=11)
        self.assertIn("Davlat raqamini", start_reply.text)
        save_state.assert_called_once()

    @mock.patch("bot.handlers.car_flow.clear_flow_state")
    def test_cancel_clears_state(self, clear_state) -> None:
        reply = self.handlers.cancel(chat_id=22)

        self.assertEqual(reply.text, "Joriy flow bekor qilindi.")
        clear_state.assert_called_once()

    @mock.patch("bot.handlers.car_flow.get_flow_state")
    def test_invalid_year_reprompts(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_year",
            state_payload={"plate_number": "10A777BC", "brand": "Kia", "model": "K5"},
        )

        reply = self.handlers.handle_flow_input(chat_id=33, text="year-2022")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Yil raqam bo'lishi kerak", reply.text)
