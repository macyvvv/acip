from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from system.scripts.publishing import providers_x
from system.scripts.publishing.providers import PublishError
from system.scripts.publishing.providers_x import XProvider, _oauth1_header


def _clear_oauth2_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("X_OAUTH2_CLIENT_ID", "X_OAUTH2_CLIENT_SECRET", "X_OAUTH2_ACCESS_TOKEN", "X_OAUTH2_REFRESH_TOKEN"):
        monkeypatch.delenv(name, raising=False)


def _clear_oauth1_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("X_API_KEY", "X_API_KEY_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"):
        monkeypatch.delenv(name, raising=False)


def _isolate_oauth2_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    state_path = tmp_path / "x_token_state.json"
    monkeypatch.setattr(providers_x, "_OAUTH2_STATE_PATH", state_path)
    return state_path


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


# ---- OAuth 1.0a fallback path (exercised only when no OAuth2 creds/state) --

def test_missing_credentials_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth2_env(monkeypatch)
    _clear_oauth1_env(monkeypatch)
    _isolate_oauth2_state(monkeypatch, tmp_path)
    with pytest.raises(PublishError, match="X_API_KEY"):
        XProvider().publish("x", "hello", "text_syndicate")


def test_wrong_platform_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth2_env(monkeypatch)
    _isolate_oauth2_state(monkeypatch, tmp_path)
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


def test_publish_success_oauth1(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth2_env(monkeypatch)
    _isolate_oauth2_state(monkeypatch, tmp_path)
    monkeypatch.setenv("X_API_KEY", "key")
    monkeypatch.setenv("X_API_KEY_SECRET", "keysecret")
    monkeypatch.setenv("X_ACCESS_TOKEN", "token")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "tokensecret")

    def fake_urlopen(request, timeout=30):
        assert request.get_header("Authorization").startswith("OAuth ")
        assert json.loads(request.data.decode("utf-8")) == {"text": "hello world"}
        return _FakeResponse({"data": {"id": "1234567890", "text": "hello"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = XProvider().publish("x", "hello world", "text_syndicate")
    assert result.provider == "x"
    assert result.platform == "x"
    assert result.external_post_id == "1234567890"
    assert "OAuth 1.0a" in result.notes


def test_publish_http_error_raises_publish_error_oauth1(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth2_env(monkeypatch)
    _isolate_oauth2_state(monkeypatch, tmp_path)
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


# ---- OAuth 2.0 path (preferred) -----------------------------------------

def test_oauth2_bootstraps_from_env_and_refreshes_on_first_use(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth1_env(monkeypatch)
    state_path = _isolate_oauth2_state(monkeypatch, tmp_path)
    monkeypatch.setenv("X_OAUTH2_CLIENT_ID", "client-id")
    monkeypatch.setenv("X_OAUTH2_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("X_OAUTH2_ACCESS_TOKEN", "initial-access-token")
    monkeypatch.setenv("X_OAUTH2_REFRESH_TOKEN", "initial-refresh-token")

    calls = []

    def fake_urlopen(request, timeout=30):
        calls.append(request.full_url)
        if request.full_url == providers_x.OAUTH2_TOKEN_URL:
            assert request.get_header("Authorization").startswith("Basic ")
            return _FakeResponse(
                {"access_token": "new-access-token", "refresh_token": "new-refresh-token", "expires_in": 7200}
            )
        assert request.get_header("Authorization") == "Bearer new-access-token"
        return _FakeResponse({"data": {"id": "42"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = XProvider().publish("x", "hello world", "text_syndicate")

    assert result.external_post_id == "42"
    assert "OAuth 2.0" in result.notes
    # State file must now hold the rotated tokens, not the original .env ones.
    saved = json.loads(state_path.read_text())
    assert saved["access_token"] == "new-access-token"
    assert saved["refresh_token"] == "new-refresh-token"


def test_oauth2_reuses_unexpired_cached_token_without_refreshing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth1_env(monkeypatch)
    _clear_oauth2_env(monkeypatch)
    state_path = _isolate_oauth2_state(monkeypatch, tmp_path)

    from datetime import datetime, timedelta, timezone

    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    state_path.write_text(json.dumps({"access_token": "still-valid-token", "refresh_token": "rt", "expires_at": future}))

    def fake_urlopen(request, timeout=30):
        assert request.full_url != providers_x.OAUTH2_TOKEN_URL, "should not refresh an unexpired token"
        assert request.get_header("Authorization") == "Bearer still-valid-token"
        return _FakeResponse({"data": {"id": "99"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = XProvider().publish("x", "hello world", "text_syndicate")
    assert result.external_post_id == "99"


def test_oauth2_refreshes_expired_cached_token(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_oauth1_env(monkeypatch)
    _clear_oauth2_env(monkeypatch)
    state_path = _isolate_oauth2_state(monkeypatch, tmp_path)
    monkeypatch.setenv("X_OAUTH2_CLIENT_ID", "client-id")
    monkeypatch.setenv("X_OAUTH2_CLIENT_SECRET", "client-secret")

    from datetime import datetime, timedelta, timezone

    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    state_path.write_text(json.dumps({"access_token": "stale-token", "refresh_token": "old-refresh", "expires_at": past}))

    def fake_urlopen(request, timeout=30):
        if request.full_url == providers_x.OAUTH2_TOKEN_URL:
            sent = urllib.parse.parse_qs(request.data.decode("utf-8"))
            assert sent["refresh_token"][0] == "old-refresh"
            assert sent["grant_type"][0] == "refresh_token"
            return _FakeResponse({"access_token": "fresh-token", "refresh_token": "fresh-refresh", "expires_in": 7200})
        assert request.get_header("Authorization") == "Bearer fresh-token"
        return _FakeResponse({"data": {"id": "7"}})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = XProvider().publish("x", "hello world", "text_syndicate")
    assert result.external_post_id == "7"
    saved = json.loads(state_path.read_text())
    assert saved["access_token"] == "fresh-token"
    assert saved["refresh_token"] == "fresh-refresh"
