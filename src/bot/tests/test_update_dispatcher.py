from unittest import mock

from django.test import TestCase

from apps.telegram.models import ProcessedTelegramUpdate, TelegramAccount
from bot.dispatchers.update_dispatcher import UpdateDispatcher
from bot.keyboards.inline import ODOMETER_CONFIRM_CALLBACK
from services.conversation_state_service import get_flow_state, save_flow_state


class UpdateDispatcherTests(TestCase):
    def setUp(self) -> None:
        self.dispatcher = UpdateDispatcher()

    def test_dispatch_start_command(self) -> None:
        update = {"message": {"chat": {"id": 1}, "text": "/start"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertEqual(reply.chat_id, 1)

    def test_dispatch_addcar_command(self) -> None:
        update = {"message": {"chat": {"id": 2}, "text": "/addcar"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Davlat raqamini", reply.text)

    def test_dispatch_addmaintenance_command(self) -> None:
        update = {"message": {"chat": {"id": 4}, "text": "/addmaintenance"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("owner/manager huquqli mashina yo'q", reply.text)

    def test_dispatch_addodometer_command(self) -> None:
        update = {"message": {"chat": {"id": 5}, "text": "/addodometer"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("owner/manager huquqli mashina yo'q", reply.text)

    def test_dispatch_cars_command(self) -> None:
        update = {"message": {"chat": {"id": 3}, "text": "/cars"}}

        with mock.patch("bot.handlers.car_flow.list_cars_for_chat", return_value=[]):
            reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("hali mashina yo'q", reply.text)


    def test_dispatch_main_menu_button_text_routes_to_commands(self) -> None:
        test_cases = [
            ("🚗 Mening mashinalarim", "hali mashina yo'q"),
            ("➕ Mashina qo'shish", "Davlat raqamini"),
            ("🛠 Servis qo'shish", "owner/manager huquqli mashina yo'q"),
            ("📈 Odometr yangilash", "owner/manager huquqli mashina yo'q"),
            ("📋 Servis tarixi", "Servis tarixi topilmadi"),
            ("🔗 Mashina ulashish", "Qaysi mashina"),
            ("❓ Yordam", "Yordam menyusi"),
        ]

        for index, (button_text, expected_text) in enumerate(test_cases, start=1):
            with self.subTest(button_text=button_text):
                update = {"message": {"chat": {"id": 1100 + index}, "text": button_text}}

                with mock.patch("bot.handlers.car_flow.list_cars_for_chat", return_value=[]):
                    reply = self.dispatcher.dispatch(update)

                self.assertIsNotNone(reply)
                assert reply is not None
                self.assertIn(expected_text, reply.text)

    def test_dispatch_unknown_message_returns_none(self) -> None:
        update = {"message": {"chat": {"id": 1}, "text": "hello"}}

        self.assertIsNone(self.dispatcher.dispatch(update))

    def test_main_menu_command_interrupts_existing_flow_state(self) -> None:
        save_flow_state(
            chat_id=1201,
            flow_name="odometer_manual",
            state_name="awaiting_plate",
            state_payload={},
        )
        update = {"message": {"chat": {"id": 1201}, "text": "📈 Odometr yangilash"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("owner/manager huquqli mashina yo'q", reply.text)
        self.assertIsNone(get_flow_state(chat_id=1201, flow_name="odometer_manual"))

    def test_callback_query_routes_to_active_flow(self) -> None:
        save_flow_state(
            chat_id=1202,
            flow_name="odometer_manual",
            state_name="awaiting_confirm",
            state_payload={"plate_number": "01A123BC", "value": 120500},
        )
        update = {
            "callback_query": {
                "id": "callback-1",
                "from": {"id": 8102, "username": "driver8102"},
                "message": {"chat": {"id": 1202}},
                "data": ODOMETER_CONFIRM_CALLBACK,
            },
        }

        with mock.patch("bot.handlers.odometer_flow.create_odometer_for_chat") as create_entry:
            create_entry.return_value = mock.Mock(car=mock.Mock(plate_number="01A123BC"), value=120500)
            reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Odometr saqlandi", reply.text)
        create_entry.assert_called_once()
        self.assertEqual(create_entry.call_args.kwargs["telegram_user_id"], 8102)


class UpdateDispatcherPersistenceTests(TestCase):
    def test_dispatch_syncs_telegram_account_when_user_is_present(self) -> None:
        dispatcher = UpdateDispatcher()
        update = {
            "message": {
                "chat": {"id": 9090},
                "from": {
                    "id": 8080,
                    "username": "driver8080",
                    "first_name": "Driver",
                    "language_code": "uz",
                },
                "text": "/start",
            }
        }

        reply = dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        account = TelegramAccount.objects.get(telegram_user_id=8080)
        self.assertEqual(account.chat_id, 9090)
        self.assertEqual(account.username, "driver8080")

    def test_dispatch_records_successful_update_id(self) -> None:
        dispatcher = UpdateDispatcher()
        update = {
            "update_id": 7001,
            "message": {
                "chat": {"id": 9091},
                "from": {"id": 8081},
                "text": "/start",
            },
        }

        reply = dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        processed_update = ProcessedTelegramUpdate.objects.get(update_id=7001)
        self.assertEqual(processed_update.chat_id, 9091)
        self.assertEqual(processed_update.telegram_user_id, 8081)
        self.assertEqual(processed_update.update_type, "message")
        self.assertEqual(processed_update.status, ProcessedTelegramUpdate.Status.PROCESSED)
        self.assertIsNotNone(processed_update.processed_at)

    def test_duplicate_update_id_is_not_dispatched_twice(self) -> None:
        dispatcher = UpdateDispatcher()
        update = {"update_id": 7002, "message": {"chat": {"id": 9092}, "text": "/start"}}

        first_reply = dispatcher.dispatch(update)

        self.assertIsNotNone(first_reply)
        with mock.patch.object(dispatcher.command_handlers, "handle_start") as handle_start:
            duplicate_reply = dispatcher.dispatch(update)

        self.assertIsNone(duplicate_reply)
        handle_start.assert_not_called()
        self.assertEqual(ProcessedTelegramUpdate.objects.filter(update_id=7002).count(), 1)

    def test_failed_dispatch_does_not_record_update_id(self) -> None:
        dispatcher = UpdateDispatcher()
        update = {"update_id": 7003, "message": {"chat": {"id": 9093}, "text": "/start"}}

        with mock.patch.object(dispatcher.command_handlers, "handle_start", side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                dispatcher.dispatch(update)

        self.assertFalse(ProcessedTelegramUpdate.objects.filter(update_id=7003).exists())
