from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib
import os


@dataclass(frozen=True)
class AnalyticsFetchResult:
    provider: str
    business_id: str
    metrics: dict[str, float]
    fetched_at: str
    notes: str


class AnalyticsFetchError(RuntimeError):
    pass


class AnalyticsProvider(ABC):
    """One adapter per platform (X/Threads/note.com/...). Mirrors
    platform/system/platform/scripts/somia/providers.py's registry shape: swapping platforms
    should never require touching the execution adapter."""

    name: str = "unset"

    @abstractmethod
    def fetch(self, business_id: str) -> AnalyticsFetchResult:
        raise NotImplementedError


class DryRunProvider(AnalyticsProvider):
    """No network call, no API key. Default provider so the analytics role is
    exercisable end-to-end before any platform API access is set up. Real
    per-platform providers (X, Threads, note.com) each need their own API
    access set up first -- X's analytics-capable API tiers are paid, Threads
    requires Meta Graph API app approval, and note.com has no official public
    analytics API -- so this dry_run path is not a placeholder for "any day
    now," it's genuinely the only provider available until those are set up."""

    name = "dry_run"

    def fetch(self, business_id: str) -> AnalyticsFetchResult:
        return AnalyticsFetchResult(
            provider=self.name,
            business_id=business_id,
            metrics={},
            fetched_at=datetime.now(timezone.utc).isoformat(),
            notes="dry-run: no platform API called, no metrics available yet",
        )


_REGISTRY: dict[str, type[AnalyticsProvider]] = {
    "dry_run": DryRunProvider,
}

# Real platform providers (X, Threads, note.com) are registered here once
# built; each needs its own API access set up by the operator first (see
# DryRunProvider docstring). `git_activity` is registered now: a real,
# credential-free interim proxy provider (repo-activity metrics, not
# platform audience/engagement data) -- see providers_git_activity.py.
_OPTIONAL_PROVIDER_MODULES: dict[str, str] = {
    "git_activity": "system.scripts.analytics.providers_git_activity",
}


def register_provider(provider_cls: type[AnalyticsProvider]) -> None:
    _REGISTRY[provider_cls.name] = provider_cls


def get_provider(name: str | None = None) -> AnalyticsProvider:
    resolved_name = name or os.environ.get("ANALYTICS_PROVIDER", "dry_run")
    if resolved_name not in _REGISTRY and resolved_name in _OPTIONAL_PROVIDER_MODULES:
        importlib.import_module(_OPTIONAL_PROVIDER_MODULES[resolved_name])
    provider_cls = _REGISTRY.get(resolved_name)
    if provider_cls is None:
        known = ", ".join(sorted(set(_REGISTRY) | set(_OPTIONAL_PROVIDER_MODULES)))
        raise AnalyticsFetchError(f"Unknown ANALYTICS_PROVIDER '{resolved_name}'. Known providers: {known}")
    return provider_cls()
