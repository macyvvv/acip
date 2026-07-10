from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib
import os


@dataclass(frozen=True)
class PublishResult:
    provider: str
    platform: str
    business_id: str
    external_post_id: str | None
    published_at: str
    notes: str


class PublishError(RuntimeError):
    pass


class PublishingProvider(ABC):
    """One adapter per platform (X/Threads/note.com/...). Mirrors
    system/scripts/analytics/providers.py's registry shape: swapping
    platforms should never require touching the scheduler."""

    name: str = "unset"

    @abstractmethod
    def publish(self, platform: str, final_text: str, business_id: str) -> PublishResult:
        raise NotImplementedError


class DryRunProvider(PublishingProvider):
    """No network call, no API key, no external side effect. Default and only
    provider until the operator obtains real platform credentials -- X's
    posting-capable API tier is paid, Threads posting requires Meta Graph API
    app approval, and note.com has no official public posting API at all, so
    this is not a placeholder for "any day now," it's genuinely the only
    provider available until those are independently set up."""

    name = "dry_run"

    def publish(self, platform: str, final_text: str, business_id: str) -> PublishResult:
        return PublishResult(
            provider=self.name,
            platform=platform,
            business_id=business_id,
            external_post_id=None,
            published_at=datetime.now(timezone.utc).isoformat(),
            notes="dry-run: no platform API called, nothing was actually posted",
        )


_REGISTRY: dict[str, type[PublishingProvider]] = {
    "dry_run": DryRunProvider,
}

# Real platform providers are registered here once built; each needs its own
# API access set up by the operator first (see DryRunProvider docstring).
# Deliberately empty: no credentials exist yet for "x" (system.scripts.publishing
# .providers_x), "threads" (...providers_threads), or "notecom" (...providers_
# notecom) -- listing a module path here before it exists would turn an
# unresolvable-provider request into a raw ModuleNotFoundError instead of the
# clean PublishError below. Add an entry only once that module is actually
# written and the operator has real credentials to test it against.
_OPTIONAL_PROVIDER_MODULES: dict[str, str] = {}


def register_provider(provider_cls: type[PublishingProvider]) -> None:
    _REGISTRY[provider_cls.name] = provider_cls


def get_provider(name: str | None = None) -> PublishingProvider:
    resolved_name = name or os.environ.get("PUBLISHING_PROVIDER", "dry_run")
    if resolved_name not in _REGISTRY and resolved_name in _OPTIONAL_PROVIDER_MODULES:
        importlib.import_module(_OPTIONAL_PROVIDER_MODULES[resolved_name])
    provider_cls = _REGISTRY.get(resolved_name)
    if provider_cls is None:
        known = ", ".join(sorted(set(_REGISTRY) | set(_OPTIONAL_PROVIDER_MODULES)))
        raise PublishError(f"Unknown PUBLISHING_PROVIDER '{resolved_name}'. Known providers: {known}")
    return provider_cls()
