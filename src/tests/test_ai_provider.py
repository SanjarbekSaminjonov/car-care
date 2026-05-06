import json
from unittest import mock

from django.test import SimpleTestCase

from integrations.ai.openai_compatible import OpenAICompatibleChatProvider


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class OpenAICompatibleChatProviderTests(SimpleTestCase):
    def test_complete_chat_posts_openai_compatible_payload(self) -> None:
        provider = OpenAICompatibleChatProvider(
            api_key="test-key",
            base_url="https://ai.example.test/v1/",
            model_name="test-model",
            timeout_seconds=7,
        )
        response = FakeHTTPResponse(
            {
                "id": "chatcmpl_1",
                "choices": [{"message": {"content": "Check tire pressure."}}],
                "usage": {"total_tokens": 12},
            }
        )

        with mock.patch(
            "integrations.ai.openai_compatible.request.urlopen",
            return_value=response,
        ) as urlopen:
            result = provider.complete_chat(messages=[{"role": "user", "content": "Hi"}])

        http_request = urlopen.call_args.args[0]
        self.assertEqual(http_request.full_url, "https://ai.example.test/v1/chat/completions")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 7)
        self.assertEqual(http_request.headers["Authorization"], "Bearer test-key")
        self.assertEqual(result.content, "Check tire pressure.")
        self.assertEqual(result.metadata["usage"]["total_tokens"], 12)
