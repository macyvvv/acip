from scripts.hygiene.audit_code_quality import audit_code_quality


def test_code_quality_audit_runs() -> None:
    report = audit_code_quality()
    assert report.checked_files is not None
