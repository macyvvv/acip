from __future__ import annotations

from system.scripts.hygiene.validate_repository_layout import ROOT_ALLOWLIST, validate_repository_layout


def test_repository_layout_allowlist_contains_expected_entries() -> None:
    assert "README.md" in ROOT_ALLOWLIST
    assert "platform" in ROOT_ALLOWLIST
    assert "businesses" in ROOT_ALLOWLIST


def test_repository_layout_report_only_returns_list() -> None:
    violations = validate_repository_layout(report_only=True)
    assert isinstance(violations, list)
