import json
from dataclasses import dataclass
from typing import Any
from urllib import parse, request


@dataclass(frozen=True)
class TelegramBotClient:
    token: str

    @property
    def base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.token}"

    def get_updates(self, *, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            query["offset"] = offset
        url = f"{self.base_url}/getUpdates?{parse.urlencode(query)}"
        response = self._get_json(url)
        return list(response.get("result", []))

    def send_message(self, *, chat_id: int, text: str, reply_markup: dict | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = json.dumps(reply_markup)
        data = parse.urlencode(payload).encode("utf-8")
        url = f"{self.base_url}/sendMessage"
        return self._post_json(url, data=data)

    def _get_json(self, url: str) -> dict[str, Any]:
        with request.urlopen(url, timeout=35) as raw_response:  # noqa: S310
            payload = raw_response.read().decode("utf-8")
        return json.loads(payload)


    def _post_json(self, url: str, data: bytes) -> dict[str, Any]:
        req = request.Request(url=url, data=data, method="POST")
        with request.urlopen(req, timeout=35) as raw_response:  # noqa: S310
            payload = raw_response.read().decode("utf-8")
        return json.loads(payload)
