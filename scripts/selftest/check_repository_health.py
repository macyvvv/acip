from selftest_common import ROOT, CheckResult, pass_result, fail, print_results

REQUIRED_DIRS = [
    "basis", "adr", "wbs", "docs", "catalog", "registry", "contracts",
    "runbooks", "control", "scripts", ".github", ".github/ISSUE_TEMPLATE", ".github/workflows"
]

REQUIRED_FILES = [
    "docs/packs/README_REPOSITORY_COMPLETE_PACK.md",
    "docs/packs/README_AGENT_OS.md",
    "docs/packs/README_RUNTIME_READINESS.md",
    "basis/026_autonomy_first_policy.md",
    "basis/037_autonomous_workflow_policy.md",
    "basis/042_execution_contract_policy.md",
    "basis/046_runtime_readiness_boundary.md",
    "basis/053_repository_selftest_policy.md",
    "adr/ADR-0016-repository-operating-system-self-test.md",
    "wbs/WBS-0011-repository-operating-system-self-test.md",
]

def run():
    results = []
    for d in REQUIRED_DIRS:
        results.append(pass_result(f"required dir: {d}") if (ROOT / d).is_dir() else fail("required dir", d, "missing"))
    for f in REQUIRED_FILES:
        results.append(pass_result(f"required file: {f}") if (ROOT / f).is_file() else fail("required file", f, "missing"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Repository Health", run()))
