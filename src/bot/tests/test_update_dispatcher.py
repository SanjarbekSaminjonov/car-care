from unittest import mock

from django.test import SimpleTestCase

from bot.dispatchers.update_dispatcher import UpdateDispatcher


class UpdateDispatcherTests(SimpleTestCase):
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
        self.assertIn("Qaysi mashina", reply.text)

    def test_dispatch_addodometer_command(self) -> None:
        update = {"message": {"chat": {"id": 5}, "text": "/addodometer"}}

        reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("Davlat raqamini", reply.text)

    def test_dispatch_cars_command(self) -> None:
        update = {"message": {"chat": {"id": 3}, "text": "/cars"}}

        with mock.patch("bot.handlers.car_flow.list_cars_for_chat", return_value=[]):
            reply = self.dispatcher.dispatch(update)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("hali mashina yo'q", reply.text)

    def test_dispatch_unknown_message_returns_none(self) -> None:
        update = {"message": {"chat": {"id": 1}, "text": "hello"}}

        self.assertIsNone(self.dispatcher.dispatch(update))
