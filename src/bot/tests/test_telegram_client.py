import json
from unittest import mock
from urllib import parse

from django.test import SimpleTestCase

from bot.clients.telegram import TelegramBotClient


class TelegramBotClientTests(SimpleTestCase):
    def test_get_updates_requests_callback_updates(self) -> None:
        client = TelegramBotClient(token="token-123")

        with mock.patch.object(TelegramBotClient, "_get_json", return_value={"result": []}) as get_json:
            updates = client.get_updates(
                offset=100,
                timeout=1,
                allowed_updates=["message", "callback_query"],
            )

        self.assertEqual(updates, [])
        url = get_json.call_args.args[0]
        query = parse.parse_qs(parse.urlsplit(url).query)
        self.assertEqual(query["offset"], ["100"])
        self.assertEqual(query["timeout"], ["1"])
        self.assertEqual(json.loads(query["allowed_updates"][0]), ["message", "callback_query"])
