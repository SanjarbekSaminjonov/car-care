from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase
from django.utils import timezone

from bot.handlers.maintenance_flow import MaintenanceFlowHandlers
from bot.keyboards.inline import (
    MAINTENANCE_CANCEL_CALLBACK,
    MAINTENANCE_CONFIRM_CALLBACK,
    MAINTENANCE_DATE_TODAY_CALLBACK,
)


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


class MaintenanceFlowHandlersTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handlers = MaintenanceFlowHandlers()

    def test_start_flow_auto_selects_single_manageable_car(self) -> None:
        car = _car("40B413YA")

        with (
            mock.patch("bot.handlers.maintenance_flow.list_manageable_cars_for_chat", return_value=[car]),
            mock.patch("bot.handlers.maintenance_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_add_maintenance(chat_id=44)

        self.assertIn("40B413YA uchun servis nomini", reply.text)
        save_state.assert_called_once_with(
            chat_id=44,
            flow_name="maintenance_add",
            state_name="awaiting_title",
            state_payload={"plate_number": "40B413YA"},
        )

    def test_start_flow_lists_multiple_manageable_cars(self) -> None:
        cars = [
            _car("40B413YA", current_odometer=120000),
            _car("01A123BC", brand="Toyota", model="Corolla", year=2022),
        ]

        with (
            mock.patch("bot.handlers.maintenance_flow.list_manageable_cars_for_chat", return_value=cars),
            mock.patch("bot.handlers.maintenance_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_add_maintenance(chat_id=44)

        self.assertIn("Servis yozuvi qo'shish uchun mashinani tanlang", reply.text)
        self.assertIn("1. 40B413YA | Chevrolet Cobalt (2015) | 120000 km", reply.text)
        self.assertIn("2. 01A123BC | Toyota Corolla (2022)", reply.text)
        save_state.assert_called_once_with(
            chat_id=44,
            flow_name="maintenance_add",
            state_name="awaiting_car_selection",
            state_payload={},
        )

    def test_start_flow_without_manageable_cars_returns_access_message(self) -> None:
        with (
            mock.patch("bot.handlers.maintenance_flow.list_manageable_cars_for_chat", return_value=[]),
            mock.patch("bot.handlers.maintenance_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.start_add_maintenance(chat_id=44)

        self.assertIn("owner/manager huquqli mashina yo'q", reply.text)
        save_state.assert_not_called()

    def test_selects_car_by_list_number(self) -> None:
        cars = [_car("40B413YA"), _car("01A123BC")]
        state = mock.Mock(state_name="awaiting_car_selection", state_payload={})

        with (
            mock.patch("bot.handlers.maintenance_flow.get_flow_state", return_value=state),
            mock.patch("bot.handlers.maintenance_flow.list_manageable_cars_for_chat", return_value=cars),
            mock.patch("bot.handlers.maintenance_flow.save_flow_state") as save_state,
        ):
            reply = self.handlers.handle_flow_input(chat_id=44, text="2")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("01A123BC uchun servis nomini", reply.text)
        save_state.assert_called_once_with(
            chat_id=44,
            flow_name="maintenance_add",
            state_name="awaiting_title",
            state_payload={"plate_number": "01A123BC"},
        )

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_title_step_asks_for_service_date(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_title",
            state_payload={"plate_number": "01A124BC"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="Oil change")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Servis qachon qilingan", reply.text)
        self.assertIn("2026-04-20", reply.text)
        self.assertEqual(
            reply.reply_markup,
            {"inline_keyboard": [[{"text": "Bugun", "callback_data": MAINTENANCE_DATE_TODAY_CALLBACK}]]},
        )
        save_state.assert_called_once_with(
            chat_id=45,
            flow_name="maintenance_add",
            state_name="awaiting_event_date",
            state_payload={"plate_number": "01A124BC", "title": "Oil change"},
        )

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_event_date_today_button_proceeds_to_odometer(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_event_date",
            state_payload={"plate_number": "01A124BC", "title": "Oil change"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text=MAINTENANCE_DATE_TODAY_CALLBACK)

        today = timezone.localdate().isoformat()
        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn(f"Servis sanasi: {today}", reply.text)
        self.assertIn("Odometr qiymatini", reply.text)
        save_state.assert_called_once_with(
            chat_id=45,
            flow_name="maintenance_add",
            state_name="awaiting_odometer",
            state_payload={
                "plate_number": "01A124BC",
                "title": "Oil change",
                "event_date": today,
            },
        )

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_event_date_text_proceeds_to_odometer(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_event_date",
            state_payload={"plate_number": "01A124BC", "title": "Oil change"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="20.04.2026")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Servis sanasi: 2026-04-20", reply.text)
        save_state.assert_called_once_with(
            chat_id=45,
            flow_name="maintenance_add",
            state_name="awaiting_odometer",
            state_payload={
                "plate_number": "01A124BC",
                "title": "Oil change",
                "event_date": "2026-04-20",
            },
        )

    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_invalid_event_date_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_event_date",
            state_payload={"plate_number": "01A124BC", "title": "Oil change"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="kecha")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Sana tushunarsiz", reply.text)
        self.assertIsNotNone(reply.reply_markup)

    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_invalid_odometer_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_odometer",
            state_payload={"plate_number": "01A124BC", "title": "Brake check", "event_date": "2026-04-20"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="12k")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Odometr faqat raqam", reply.text)

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_odometer_step_asks_for_clear_expense_name(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_odometer",
            state_payload={"plate_number": "01A124BC", "title": "Brake check", "event_date": "2026-04-20"},
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="99000")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Servis xarajati nomini", reply.text)
        self.assertIn("motor moyi", reply.text)
        save_state.assert_called_once()

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_item_name_step_asks_for_clear_amount(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_item_name",
            state_payload={
                "plate_number": "01A124BC",
                "title": "Brake check",
                "event_date": "2026-04-20",
                "odometer": 99000,
            },
        )

        reply = self.handlers.handle_flow_input(chat_id=45, text="Motor moyi")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("xarajat summasini", reply.text)
        save_state.assert_called_once()

    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_amount_step_returns_inline_confirmation_keyboard(self, get_state, save_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_item_amount",
            state_payload={
                "plate_number": "01A125BC",
                "title": "ATF service",
                "event_date": "2026-04-20",
                "odometer": 99000,
                "item_name": "ATF",
            },
        )

        reply = self.handlers.handle_flow_input(chat_id=46, text="350000")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Sana: 2026-04-20", reply.text)
        self.assertIn("Xarajat: ATF", reply.text)
        self.assertNotIn("yes", reply.text.lower())
        self.assertEqual(
            reply.reply_markup,
            {
                "inline_keyboard": [
                    [
                        {"text": "✅ Tasdiqlash", "callback_data": MAINTENANCE_CONFIRM_CALLBACK},
                        {"text": "Bekor qilish", "callback_data": MAINTENANCE_CANCEL_CALLBACK},
                    ]
                ]
            },
        )
        save_state.assert_called_once()

    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_invalid_confirmation_recovery(self, get_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={
                "plate_number": "01A125BC",
                "title": "ATF service",
                "event_date": "2026-04-20",
                "odometer": 99000,
                "item_name": "ATF",
                "item_amount": "350000",
            },
        )

        reply = self.handlers.handle_flow_input(chat_id=46, text="ok")

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("tugmalardan", reply.text)
        self.assertIsNotNone(reply.reply_markup)

    @mock.patch("bot.handlers.maintenance_flow.clear_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.save_flow_state")
    @mock.patch("bot.handlers.maintenance_flow.create_maintenance_for_chat")
    @mock.patch("bot.handlers.maintenance_flow.get_flow_state")
    def test_confirm_happy_path_passes_event_date(self, get_state, create_record, save_state, clear_state) -> None:
        get_state.return_value = mock.Mock(
            state_name="awaiting_confirm",
            state_payload={
                "plate_number": "01A125BC",
                "title": "ATF service",
                "event_date": "2026-04-20",
                "odometer": 99000,
                "item_name": "ATF",
                "item_amount": "350000",
            },
        )
        create_record.return_value = mock.Mock(
            id="record-1",
            car=mock.Mock(plate_number="01A125BC"),
            title="ATF service",
        )

        reply = self.handlers.handle_flow_input(
            chat_id=46,
            text=MAINTENANCE_CONFIRM_CALLBACK,
            telegram_user_id=777,
        )

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Servis yozuvi saqlandi", reply.text)
        self.assertEqual(create_record.call_args.kwargs["event_date"].isoformat(), "2026-04-20")
        clear_state.assert_called_once()
        save_state.assert_called_once()
