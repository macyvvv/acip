from system.scripts.hygiene.audit_repository_root import audit_repository_root


def test_root_hygiene_reports_allowlist() -> None:
    report = audit_repository_root()
    assert "README.md" in report.allowlist
    assert report.candidates is not None
