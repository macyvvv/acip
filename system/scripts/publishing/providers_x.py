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
from datetime import datetime, timezone

from system.scripts.publishing.providers import PublishError, PublishingProvider, PublishResult, register_provider

# X API v2 tweet creation (POST /2/tweets), authenticated via OAuth 1.0a User
# Context -- the only auth mode that can post as a specific user account
# (OAuth 2.0 App-Only / bearer tokens are read-only). As of 2026-02, X's
# pricing is pay-per-use by default for new developers: $0.015/post created
# (no link), $0.20/post if the body contains a link -- this repo's existing
# "no link in the post body" strategy (see text_syndicate/marketing drafts,
# chosen for X algorithm reach reasons) also happens to be the cheap path.
#
# Required credentials (read from environment only, never logged):
#   X_API_KEY, X_API_KEY_SECRET       -- the App's consumer key/secret
#   X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET -- the User Context access token/secret,
#                                             generated for the posting account
#                                             (@Colophon__00__), with Read+Write
#                                             app permission enabled BEFORE the
#                                             access token was generated -- an
#                                             access token generated while the
#                                             app was still Read-only will not
#                                             gain write access just by flipping
#                                             the app permission afterward; it
#                                             must be regenerated.

TWEETS_URL = "https://api.x.com/2/tweets"


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise PublishError(f"{name} is not set (required for the X publishing provider).")
    return value


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
    # POST /2/tweets takes no query params and a JSON (not form-encoded) body,
    # so the signature base string's parameter set is exactly the oauth_*
    # params themselves -- no query-string or form-body params to merge in.
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


class XProvider(PublishingProvider):
    """Posts a tweet via X API v2 (POST /2/tweets), OAuth 1.0a User Context.
    Real money per call (pay-per-use pricing) -- only reached when a policy
    explicitly selects provider="x" (see system/runtime/publishing/policy.json);
    dry_run stays the default everywhere else."""

    name = "x"

    def publish(self, platform: str, final_text: str, business_id: str) -> PublishResult:
        if platform != "x":
            raise PublishError(f"XProvider only handles platform='x', got '{platform}'")

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
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise PublishError(f"X API request failed ({exc.code}): {error_body}") from exc

        tweet_id = payload.get("data", {}).get("id")
        if not tweet_id:
            raise PublishError(f"X API response missing tweet id: {payload}")

        return PublishResult(
            provider=self.name,
            platform=platform,
            business_id=business_id,
            external_post_id=str(tweet_id),
            published_at=datetime.now(timezone.utc).isoformat(),
            notes="posted via X API v2 (POST /2/tweets), OAuth 1.0a user context",
        )


register_provider(XProvider)
