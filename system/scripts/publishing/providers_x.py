from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from system.scripts.publishing.providers import PublishError, PublishingProvider, PublishResult, register_provider

# X API v2 tweet creation (POST /2/tweets). Two auth modes are supported --
# this repo's operator ended up with a complete OAuth 2.0 User Context
# credential set (Client ID/Secret + access/refresh token, obtained via the
# newer X Developer Console's authorization flow) but only a partial OAuth
# 1.0a set (Consumer Key/Secret; the Access Token/Secret pair was never
# generated), so OAuth 2.0 is the default/primary path. OAuth 1.0a stays
# available for whichever credential set is actually complete.
#
# Auth mode selection: X_OAUTH2_ACCESS_TOKEN present -> OAuth 2.0 (preferred).
# Otherwise falls back to OAuth 1.0a if that credential set is present.
#
# As of 2026-02, X's pricing is pay-per-use by default for new developers:
# $0.015/post created (no link), $0.20/post if the body contains a link --
# this repo's existing "no link in the post body" strategy (see
# text_syndicate/marketing drafts, chosen for X algorithm reach reasons) also
# happens to be the cheap path.

TWEETS_URL = "https://api.x.com/2/tweets"
OAUTH2_TOKEN_URL = "https://api.x.com/2/oauth2/token"

# OAuth 2.0 access tokens expire (X issues short-lived tokens, refreshed via
# a single-use, ROTATING refresh_token -- every refresh returns a NEW
# refresh_token that must replace the old one, or the next refresh fails).
# Persisted here (gitignored: contains live, rotating secrets) rather than
# only in .env, since .env is a static file this code does not rewrite on
# every run -- the state file is what actually stays current across
# scheduled invocations. Bootstrapped from .env's X_OAUTH2_ACCESS_TOKEN/
# X_OAUTH2_REFRESH_TOKEN the first time it's needed.
_OAUTH2_STATE_PATH = Path("system/runtime/publishing/oauth2/x_token_state.json")
_EXPIRY_SAFETY_MARGIN_SECONDS = 60


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise PublishError(f"{name} is not set (required for the X publishing provider).")
    return value


def _env_optional(name: str) -> str:
    return os.environ.get(name, "").strip()


# ---- OAuth 2.0 (preferred) --------------------------------------------

def _load_oauth2_state() -> dict:
    if _OAUTH2_STATE_PATH.exists():
        return json.loads(_OAUTH2_STATE_PATH.read_text(encoding="utf-8"))
    # Bootstrap from .env on first use.
    access_token = _env("X_OAUTH2_ACCESS_TOKEN")
    refresh_token = _env("X_OAUTH2_REFRESH_TOKEN")
    return {"access_token": access_token, "refresh_token": refresh_token, "expires_at": None}


def _save_oauth2_state(state: dict) -> None:
    _OAUTH2_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _OAUTH2_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _refresh_oauth2_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    body = urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh_token}).encode("utf-8")
    request = urllib.request.Request(
        OAUTH2_TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise PublishError(f"X OAuth2 token refresh failed ({exc.code}): {error_body}") from exc


def _get_valid_oauth2_access_token() -> str:
    state = _load_oauth2_state()
    expires_at = state.get("expires_at")
    if expires_at is not None:
        expires_at_dt = datetime.fromisoformat(expires_at)
        if datetime.now(timezone.utc) < expires_at_dt - timedelta(seconds=_EXPIRY_SAFETY_MARGIN_SECONDS):
            return str(state["access_token"])

    # Missing expiry (first bootstrap from .env, never validated yet) or
    # actually expired -- either way, refresh now rather than gambling on an
    # unvalidated/expired token failing the real publish call.
    client_id = _env("X_OAUTH2_CLIENT_ID")
    client_secret = _env("X_OAUTH2_CLIENT_SECRET")
    refreshed = _refresh_oauth2_token(client_id, client_secret, str(state["refresh_token"]))

    new_access_token = refreshed.get("access_token")
    new_refresh_token = refreshed.get("refresh_token")
    expires_in = refreshed.get("expires_in")
    if not new_access_token or not new_refresh_token:
        raise PublishError(f"X OAuth2 refresh response missing access_token/refresh_token: {refreshed}")

    new_expires_at = (
        (datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))).isoformat() if expires_in else None
    )
    _save_oauth2_state({"access_token": new_access_token, "refresh_token": new_refresh_token, "expires_at": new_expires_at})
    return str(new_access_token)


def _publish_oauth2(final_text: str) -> dict:
    access_token = _get_valid_oauth2_access_token()
    body = json.dumps({"text": final_text}).encode("utf-8")
    request = urllib.request.Request(
        TWEETS_URL,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise PublishError(f"X API request failed ({exc.code}): {error_body}") from exc


# ---- OAuth 1.0a (fallback, requires a complete Consumer+Access token set) --

def _percent_encode(value: str) -> str:
    # OAuth 1.0a requires RFC 3986 encoding; urllib's default safe="/" set
    # does not escape a few characters OAuth's spec does (e.g. "~" must stay
    # unescaped, which quote's default already handles -- the deliberate
    # difference is safe="" here, so "/" itself IS escaped, unlike a URL path).
    return urllib.parse.quote(value, safe="~")


def _oauth1_header(method: str, url: str, api_key: str, api_key_secret: str, access_token: str, access_token_secret: str) -> str:
    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }
    param_string = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in sorted(oauth_params.items())
    )
    base_string = "&".join([method.upper(), _percent_encode(url), _percent_encode(param_string)])
    signing_key = f"{_percent_encode(api_key_secret)}&{_percent_encode(access_token_secret)}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")
    oauth_params["oauth_signature"] = signature
    header_params = ", ".join(f'{_percent_encode(k)}="{_percent_encode(v)}"' for k, v in sorted(oauth_params.items()))
    return f"OAuth {header_params}"


def _publish_oauth1(final_text: str) -> dict:
    api_key = _env("X_API_KEY")
    api_key_secret = _env("X_API_KEY_SECRET")
    access_token = _env("X_ACCESS_TOKEN")
    access_token_secret = _env("X_ACCESS_TOKEN_SECRET")

    auth_header = _oauth1_header("POST", TWEETS_URL, api_key, api_key_secret, access_token, access_token_secret)
    body = json.dumps({"text": final_text}).encode("utf-8")
    request = urllib.request.Request(
        TWEETS_URL,
        data=body,
        method="POST",
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise PublishError(f"X API request failed ({exc.code}): {error_body}") from exc


class XProvider(PublishingProvider):
    """Posts a tweet via X API v2 (POST /2/tweets). Real money per call
    (pay-per-use pricing) -- only reached when a policy explicitly selects
    provider="x" (see system/runtime/publishing/policy.json); dry_run stays
    the default everywhere else."""

    name = "x"

    def publish(self, platform: str, final_text: str, business_id: str) -> PublishResult:
        if platform != "x":
            raise PublishError(f"XProvider only handles platform='x', got '{platform}'")

        if _env_optional("X_OAUTH2_ACCESS_TOKEN") or _OAUTH2_STATE_PATH.exists():
            payload = _publish_oauth2(final_text)
            auth_note = "OAuth 2.0 user context (auto-refreshed)"
        else:
            payload = _publish_oauth1(final_text)
            auth_note = "OAuth 1.0a user context"

        tweet_id = payload.get("data", {}).get("id")
        if not tweet_id:
            raise PublishError(f"X API response missing tweet id: {payload}")

        return PublishResult(
            provider=self.name,
            platform=platform,
            business_id=business_id,
            external_post_id=str(tweet_id),
            published_at=datetime.now(timezone.utc).isoformat(),
            notes=f"posted via X API v2 (POST /2/tweets), {auth_note}",
        )


register_provider(XProvider)
