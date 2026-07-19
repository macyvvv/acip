# Verification v1.2.0 (Release Candidate)

Verified in a clean venv, 2026-07-20, against issue #151's acceptance criteria.

- editable install (`pip install -e ".[dev]"`): passed
- ruff check: passed, no errors
- pytest: 59 passed
- coverage (`--cov-fail-under=80`): 98.05% (threshold 80%)
- `validate --character airi`: passed
- `plan --character airi --count 40`: passed, exact bucket-weight quotas preserved
- `generate --character airi --count 3 --dry-run`: passed, no API key required
- `generate` with a real `OPENAI_API_KEY`: not performed in this verification pass
  (real spend, requires explicit operator go-ahead)
- `--resume`: verified via mocked-adapter tests (all-succeed / all-fail /
  partial-failure / resume-skips-completed-slots / resume-on-completed-run-is-noop)
- `validate --run-id` -> `export --run-id`: verified end-to-end via CLI subprocess
  test; export correctly refuses to run without a prior `review.jsonl`
- Path resolution is cwd-independent: verified by invoking the CLI from a
  directory outside the package (subprocess test)
- Python compatibility target: 3.11-3.14
- CI: `.github/workflows/somia-dataset-generator-ci.yml` at the repository
  root (a workflow file nested inside the package's own directory, as v1.1.0
  had, is never actually picked up by GitHub Actions -- this was a real gap,
  not just a style preference)
