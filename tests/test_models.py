from __future__ import annotations

import unittest

import requests

from ikki.config import ModelProfile
from ikki.models import (
    EchoModelProvider,
    ModelAuthenticationError,
    ModelFactory,
    ModelHTTPError,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelResponseError,
    ModelTimeoutError,
)
from ikki.models.anthropic import AnthropicModelProvider
from ikki.models.openai_compatible import OpenAICompatibleModelProvider


class ModelInterfaceTest(unittest.TestCase):
    def test_model_request_response_and_echo_provider(self) -> None:
        request = ModelRequest(messages=[ModelMessage(role="user", content="hello")])

        response = EchoModelProvider().complete(request)

        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.text, "Ikki 已接收任务：hello")

    def test_factory_constructs_echo_without_secret(self) -> None:
        provider = ModelFactory(env={}).create(
            "local_test",
            ModelProfile(provider="echo"),
        )

        self.assertIsInstance(provider, EchoModelProvider)

    def test_factory_requires_remote_secret(self) -> None:
        profile = ModelProfile(
            provider="openai-compatible",
            model="gpt-test",
            base_url="https://example.test/v1",
            api_key_env="OPENAI_API_KEY",
        )

        with self.assertRaisesRegex(ModelAuthenticationError, "OPENAI_API_KEY"):
            ModelFactory(env={}).create("remote", profile)

    def test_factory_constructs_openai_and_anthropic(self) -> None:
        openai_profile = ModelProfile(
            provider="openai-compatible",
            model="gpt-test",
            base_url="https://example.test/v1",
            api_key_env="OPENAI_API_KEY",
        )
        anthropic_profile = ModelProfile(
            provider="anthropic",
            model="claude-test",
            base_url="https://example.test",
            api_key_env="ANTHROPIC_API_KEY",
        )

        openai_provider = ModelFactory(env={"OPENAI_API_KEY": "secret"}).create(
            "openai",
            openai_profile,
        )
        anthropic_provider = ModelFactory(env={"ANTHROPIC_API_KEY": "secret"}).create(
            "claude",
            anthropic_profile,
        )

        self.assertIsInstance(openai_provider, OpenAICompatibleModelProvider)
        self.assertIsInstance(anthropic_provider, AnthropicModelProvider)


class RemoteModelTest(unittest.TestCase):
    def test_openai_compatible_success(self) -> None:
        session = FakeSession(FakeResponse({"choices": [{"message": {"content": "ok"}}]}))
        provider = OpenAICompatibleModelProvider(
            profile=ModelProfile(
                provider="openai-compatible",
                model="gpt-test",
                base_url="https://example.test/v1",
                api_key_env="OPENAI_API_KEY",
                temperature=0.2,
                timeout_seconds=10,
            ),
            api_key="secret",
            session=session,
        )

        response = provider.complete(_request())

        self.assertEqual(response.text, "ok")
        self.assertEqual(session.last_url, "https://example.test/v1/chat/completions")
        self.assertEqual(session.last_json["messages"][0]["content"], "hello")

    def test_openai_compatible_http_timeout_and_invalid_response(self) -> None:
        provider_500 = OpenAICompatibleModelProvider(
            profile=_openai_profile(),
            api_key="secret",
            session=FakeSession(FakeResponse({"error": "bad"}, status_code=500, text="bad")),
        )
        provider_timeout = OpenAICompatibleModelProvider(
            profile=_openai_profile(),
            api_key="secret",
            session=FakeSession(exception=requests.Timeout()),
        )
        provider_invalid = OpenAICompatibleModelProvider(
            profile=_openai_profile(),
            api_key="secret",
            session=FakeSession(FakeResponse({"choices": []})),
        )

        with self.assertRaises(ModelHTTPError):
            provider_500.complete(_request())
        with self.assertRaises(ModelTimeoutError):
            provider_timeout.complete(_request())
        with self.assertRaises(ModelResponseError):
            provider_invalid.complete(_request())

    def test_anthropic_success_and_invalid_response(self) -> None:
        success_session = FakeSession(FakeResponse({"content": [{"type": "text", "text": "ok"}]}))
        provider = AnthropicModelProvider(
            profile=ModelProfile(
                provider="anthropic",
                model="claude-test",
                base_url="https://example.test",
                api_key_env="ANTHROPIC_API_KEY",
            ),
            api_key="secret",
            session=success_session,
        )
        invalid_provider = AnthropicModelProvider(
            profile=ModelProfile(
                provider="anthropic",
                model="claude-test",
                base_url="https://example.test",
                api_key_env="ANTHROPIC_API_KEY",
            ),
            api_key="secret",
            session=FakeSession(FakeResponse({"content": []})),
        )

        response = provider.complete(_request())

        self.assertEqual(response.text, "ok")
        self.assertEqual(success_session.last_url, "https://example.test/v1/messages")
        with self.assertRaises(ModelResponseError):
            invalid_provider.complete(_request())


class FakeResponse:
    def __init__(self, data: object, status_code: int = 200, text: str = "") -> None:
        self._data = data
        self.status_code = status_code
        self.text = text

    def json(self) -> object:
        return self._data


class FakeSession:
    def __init__(self, response: FakeResponse | None = None, exception: Exception | None = None) -> None:
        self._response = response
        self._exception = exception
        self.last_url: str | None = None
        self.last_json: dict[str, object] | None = None

    def post(self, url: str, headers: dict[str, str], json: dict[str, object], timeout: float) -> FakeResponse:
        self.last_url = url
        self.last_json = json
        if self._exception is not None:
            raise self._exception
        assert self._response is not None
        return self._response


def _request() -> ModelRequest:
    return ModelRequest(
        messages=[ModelMessage(role="user", content="hello")],
        temperature=0.2,
        timeout_seconds=10,
    )


def _openai_profile() -> ModelProfile:
    return ModelProfile(
        provider="openai-compatible",
        model="gpt-test",
        base_url="https://example.test/v1",
        api_key_env="OPENAI_API_KEY",
    )
