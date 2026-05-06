from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from bot.handlers.odometer_flow import OdometerFlowHandlers
from bot.keyboards.inline import ODOMETER_CANCEL_CALLBACK, ODOMETER_CONFIRM_CALLBACK


def _car(
    plate_number: str,
    *,
    brand: str = "Chevrolet",
    model: str = "Cobalt",
    year: int = 2015,
    current_odometer: int | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        plate_number=plate_number,
        normalized_plate_number="".join(plate_number.upper().split()),
        brand=brand,
        model=model,
        year=year,
        current_odometer=current_odometer,
    )


class OdometerFlowHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = OdometerFlowHandlers()

    def test_start_flow_auto_selects_single_manageable_car(self) -> None:
        car = _car("40B413YA", current_odometer=120000)

        with (
            mock.patch("bot.handlers.odometer_flow.list_manageable_cars_for_chat", return_value=[car]),
            mock.patch("bot.handlers.odometer_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_manual_update(chat_id=51)

        self.assertIn("40B413YA uchun odometr", reply.text)
        save_state.assert_called_once_with(
            chat_id=51,
            flow_name="odometer_manual",
            state_name="awaiting_value",
            state_payload={"plate_number": "40B413YA"},
        )

    def test_start_flow_lists_multiple_manageable_cars(self) -> None:
        cars = [
            _car("40B413YA", current_odometer=120000),
            _car("01A123BC", brand="Toyota", model="Corolla", year=2022),
        ]

        with (
            mock.patch("bot.handlers.odometer_flow.list_manageable_cars_for_chat", return_value=cars),
            mock.patch("bot.handlers.odometer_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_manual_update(chat_id=51)

        self.assertIn("Odometr yangilash uchun mashinani tanlang", reply.text)
        self.assertIn("1. 40B413YA | Chevrolet Cobalt (2015) | 120000 km", reply.text)
        self.assertIn("2. 01A123BC | Toyota Corolla (2022)", reply.text)
        self.assertIn("Raqam yoki davlat raqamini yuboring", reply.text)
        save_state.assert_called_once_with(
            chat_id=51,
            flow_name="odometer_manual",
            state_name="awaiting_car_selection",
            state_payload={},
        )

    def test_start_flow_without_manageable_cars_returns_access_message(self) -> None:
        with (
            mock.patch("bot.handlers.odometer_flow.list_manageable_cars_for_chat", return_value=[]),
            mock.patch("bot.handlers.odometer_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_manual_update(chat_id=51)

        self.assertIn("owner/manager huquqli mashina yo'q", reply.text)
        save_state.assert_not_called()

    def test_selects_car_by_list_number(self) -> None:
        cars = [_car("40B413YA"), _car("01A123BC")]
        state = mock.Mock(state_name="awaiting_car_selection", state_payload={})

        with (
            mock.patch("bot.handlers.odometer_flow.get_flow_state", return_value=state),
            mock.patch("bot.handlers.odometer_flow.list_manageable_cars_for_chat", return_value=cars),
            mock.patch("bot.handlers.odometer_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.handle_flow_input(chat_id=51, text="2")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("01A123BC uchun odometr", reply.text)
        save_state.assert_called_once_with(
            chat_id=51,
            flow_name="odometer_manual",
            state_name="awaiting_value",
            state_payload={"plate_number": "01A123BC"},
        )

    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_invalid_value_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(state_name="awaiting_value", state_payload={"plate_number": "01A123BC"})

        reply = self.handlers.handle_flow_input(chat_id=51, text="12k")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("faqat raqam", reply.text)

    @mock.patch("bot.handlers.odometer_flow.save_flow_state")
    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_value_step_returns_inline_confirmation_keyboard(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(state_name="awaiting_value", state_payload={"plate_number": "01A123BC"})

        reply = self.handlers.handle_flow_input(chat_id=51, text="120500")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Tasdiqlang", reply.text)
        self.assertNotIn("yes", reply.text.lower())
        self.assertEqual(
            reply.reply_markup,
            {
                "inline_keyboard": [
                    [
                        {"text": "✅ Tasdiqlash", "callback_data": ODOMETER_CONFIRM_CALLBACK},
                        {"text": "Bekor qilish", "callback_data": ODOMETER_CANCEL_CALLBACK},
                    ]
                ]
            },
        )
        save_state.assert_called_once()

    @mock.patch("bot.handlers.odometer_flow.clear_flow_state")
    @mock.patch("bot.handlers.odometer_flow.create_odometer_for_chat")
    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_confirm_happy_path(self, get_state, create_entry, clear_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={"plate_number": "01A123BC", "value": 120500},
        )
        create_entry.return_value = mock.Mock(car=mock.Mock(plate_number="01A123BC"), value=120500)

        reply = self.handlers.handle_flow_input(
            chat_id=51,
            text=ODOMETER_CONFIRM_CALLBACK,
            telegram_user_id=777,
        )

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Odometr saqlandi", reply.text)
        clear_state.assert_called_once()

    @mock.patch("bot.handlers.odometer_flow.clear_flow_state")
    @mock.patch("bot.handlers.odometer_flow.get_flow_state")
    def test_confirm_cancel_button_clears_flow(self, get_state, clear_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={"plate_number": "01A123BC", "value": 120500},
        )

        reply = self.handlers.handle_flow_input(chat_id=51, text=ODOMETER_CANCEL_CALLBACK)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("bekor qilindi", reply.text)
        clear_state.assert_called_once()
