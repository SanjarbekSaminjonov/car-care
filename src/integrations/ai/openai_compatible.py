import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request


class ChatCompletionProviderError(RuntimeError):
    """Raised when the upstream chat completion provider fails."""


@dataclass(frozen=True)
class ChatCompletionResult:
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class OpenAICompatibleChatProvider:
    api_key: str
    base_url: str
    model_name: str
    timeout_seconds: int = 30
    provider_name: str = "openai-compatible"

    def complete_chat(self, *, messages: list[dict[str, str]]) -> ChatCompletionResult:
        payload = json.dumps(
            {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.2,
            }
        ).encode("utf-8")
        http_request = request.Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as raw_response:  # noqa: S310
                response_payload = raw_response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ChatCompletionProviderError(
                f"AI provider returned HTTP {exc.code}: {detail[:500]}"
            ) from exc
        except error.URLError as exc:
            raise ChatCompletionProviderError(f"AI provider request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ChatCompletionProviderError("AI provider request timed out.") from exc

        try:
            data = json.loads(response_payload)
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ChatCompletionProviderError("AI provider returned an invalid response.") from exc

        if not isinstance(content, str) or not content.strip():
            raise ChatCompletionProviderError("AI provider returned an empty response.")

        metadata = {
            "id": data.get("id"),
            "object": data.get("object"),
            "created": data.get("created"),
            "usage": data.get("usage", {}),
        }
        return ChatCompletionResult(content=content.strip(), metadata=metadata)
