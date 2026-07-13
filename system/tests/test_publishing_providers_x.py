from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from system.scripts.publishing.providers import PublishError
from system.scripts.publishing.providers_x import XProvider, _oauth1_header


def test_missing_credentials_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("X_API_KEY", "X_API_KEY_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(PublishError, match="X_API_KEY"):
        XProvider().publish("x", "hello", "text_syndicate")


def test_wrong_platform_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_API_KEY", "k")
    monkeypatch.setenv("X_API_KEY_SECRET", "ks")
    monkeypatch.setenv("X_ACCESS_TOKEN", "t")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "ts")
    with pytest.raises(PublishError, match="platform='x'"):
        XProvider().publish("threads", "hello", "text_syndicate")


def test_oauth1_header_shape() -> None:
    header = _oauth1_header("POST", "https://api.x.com/2/tweets", "key", "keysecret", "token", "tokensecret")
    assert header.startswith("OAuth ")
    assert "oauth_consumer_key=" in header
    assert "oauth_signature=" in header
    assert "oauth_signature_method=" in header
    assert "HMAC-SHA1" in header


def test_publish_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_API_KEY", "key")
    monkeypatch.setenv("X_API_KEY_SECRET", "keysecret")
    monkeypatch.setenv("X_ACCESS_TOKEN", "token")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "tokensecret")

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"data": {"id": "1234567890", "text": "hello"}}).encode("utf-8")

    def fake_urlopen(request, timeout=30):
        assert request.get_header("Authorization").startswith("OAuth ")
        assert json.loads(request.data.decode("utf-8")) == {"text": "hello world"}
        return _FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = XProvider().publish("x", "hello world", "text_syndicate")
    assert result.provider == "x"
    assert result.platform == "x"
    assert result.external_post_id == "1234567890"


def test_publish_http_error_raises_publish_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_API_KEY", "key")
    monkeypatch.setenv("X_API_KEY_SECRET", "keysecret")
    monkeypatch.setenv("X_ACCESS_TOKEN", "token")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "tokensecret")

    def fake_urlopen(request, timeout=30):
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", hdrs=None, fp=__import__("io").BytesIO(b'{"detail": "bad token"}')
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(PublishError, match="401"):
        XProvider().publish("x", "hello world", "text_syndicate")
