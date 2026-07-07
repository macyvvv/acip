from __future__ import annotations

from pathlib import Path
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


def api_key() -> str:
    key = os.environ.get("SOMIA_VIDEO_API_KEY", "").strip()
    if not key:
        raise VideoGenerationError("SOMIA_VIDEO_API_KEY is not set (required for fal.ai-hosted providers).")
    return key


def fal_request(method: str, url: str, key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
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
        raise VideoGenerationError(f"fal.ai request failed ({exc.code}) for {url}: {body}") from exc


def submit(model_id: str, payload: dict, key: str) -> dict:
    return fal_request("POST", f"{FAL_QUEUE_BASE}/{model_id}", key, payload)


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
