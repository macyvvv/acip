from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

from system.scripts.somia.providers import VideoGenerationError

# Shared fal.ai queue-API client, used by every fal-hosted provider adapter
# (providers_pika.py, providers_kling.py, ...). One vendor's endpoint schema
# differs from another's, but the submit/poll/fetch protocol and auth are
# identical across all fal-hosted models.
FAL_QUEUE_BASE = "https://queue.fal.run"
DEFAULT_POLL_INTERVAL_SECONDS = 3
DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("SOMIA_FAL_TIMEOUT_SECONDS", "600"))

# Transient failure modes worth retrying: rate limit (429), and the vendor's
# own 5xx range. A 4xx other than 429 means the request itself is wrong
# (bad payload, auth) and retrying it verbatim will never succeed.
RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}
DEFAULT_MAX_RETRIES = int(os.environ.get("SOMIA_FAL_MAX_RETRIES", "4"))
DEFAULT_RETRY_BASE_SECONDS = float(os.environ.get("SOMIA_FAL_RETRY_BASE_SECONDS", "2"))


def api_key() -> str:
    key = os.environ.get("SOMIA_VIDEO_API_KEY", "").strip()
    if not key:
        raise VideoGenerationError("SOMIA_VIDEO_API_KEY is not set (required for fal.ai-hosted providers).")
    return key


def fal_request(
    method: str,
    url: str,
    key: str,
    payload: dict | None = None,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_base_seconds: float = DEFAULT_RETRY_BASE_SECONDS,
) -> dict:
    """A single transient blip (429/5xx) during a multi-minute paid render
    used to kill the whole job with no retry. Retries those codes with
    exponential backoff (retry_base_seconds * 2**attempt); anything else
    (4xx auth/payload errors) fails immediately since retrying an
    identically-wrong request can't succeed."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    attempt = 0
    while True:
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Key {key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in RETRYABLE_HTTP_CODES and attempt < max_retries:
                time.sleep(retry_base_seconds * (2**attempt))
                attempt += 1
                continue
            raise VideoGenerationError(f"fal.ai request failed ({exc.code}) for {url}: {body}") from exc
        except urllib.error.URLError as exc:
            if attempt < max_retries:
                time.sleep(retry_base_seconds * (2**attempt))
                attempt += 1
                continue
            raise VideoGenerationError(f"fal.ai request failed (network error) for {url}: {exc}") from exc


def submit(model_id: str, payload: dict, key: str) -> dict:
    return fal_request("POST", f"{FAL_QUEUE_BASE}/{model_id}", key, payload)


def _payload_fingerprint(model_id: str, payload: dict) -> str:
    canonical = json.dumps({"model_id": model_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def submit_resumable(model_id: str, payload: dict, key: str, checkpoint_path: Path) -> dict:
    """Same as submit(), but persists {model_id, payload fingerprint,
    status_url, response_url} to checkpoint_path first. If the process dies
    mid-poll and is re-run against the same content dir, the next call with
    an identical model_id/payload reuses the already-submitted job instead
    of resubmitting (and re-billing) it. A different model_id/payload
    invalidates the checkpoint rather than reusing a stale, unrelated job."""
    fingerprint = _payload_fingerprint(model_id, payload)
    if checkpoint_path.exists():
        try:
            saved = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            saved = {}
        if saved.get("fingerprint") == fingerprint:
            return {"status_url": saved["status_url"], "response_url": saved["response_url"]}
    submission = submit(model_id, payload, key)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "status_url": submission["status_url"],
                "response_url": submission["response_url"],
            }
        ),
        encoding="utf-8",
    )
    return submission


def clear_checkpoint(checkpoint_path: Path) -> None:
    checkpoint_path.unlink(missing_ok=True)


def await_result(
    status_url: str,
    response_url: str,
    key: str,
    *,
    poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while True:
        status_payload = fal_request("GET", status_url, key)
        status = status_payload.get("status")
        if status == "COMPLETED":
            return fal_request("GET", response_url, key)
        if status not in {"IN_QUEUE", "IN_PROGRESS"}:
            raise VideoGenerationError(f"Unexpected fal.ai status '{status}' for {status_url}: {status_payload}")
        if time.monotonic() >= deadline:
            raise VideoGenerationError(f"Timed out after {timeout_seconds}s waiting on {status_url}")
        time.sleep(poll_interval_seconds)


def download(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        dest_path.write_bytes(response.read())


def upload(path: str | Path, key: str, *, content_type: str = "image/png") -> str:
    """Upload a local file to fal's CDN storage and return its access URL, so
    it can be used as an image_url input (e.g. for image-to-image). Two-step
    flow: get a short-lived upload token, then PUT/POST the bytes to it."""
    auth = fal_request("POST", "https://rest.alpha.fal.ai/storage/auth/token?storage_type=fal-cdn-v3", key, payload={})
    token = auth["token"]
    base_url = auth["base_url"]
    data = Path(path).read_bytes()
    request = urllib.request.Request(
        f"{base_url}/files/upload",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": content_type,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VideoGenerationError(f"fal.ai upload failed ({exc.code}): {body}") from exc
    return result["access_url"]
