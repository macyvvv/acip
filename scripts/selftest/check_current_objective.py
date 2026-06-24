from selftest_common import iter_text_files, rel, read, pass_result, issue, print_results, is_template_or_report

APPROVED_OBJECTIVES = {
    "Canonical Asset Production",
    "Agent OS Foundation",
    "Repository Operating System Stabilization",
}

PLACEHOLDER_OK = {
    "current_objective:",
    "Current Objective",
    "- current_objective:",
}

def line_mentions_current_objective(line: str) -> bool:
    return "Current Objective" in line or "current_objective" in line

def run():
    results = []
    for p in iter_text_files():
        if p.suffix not in {".md", ".yml", ".yaml"}:
            continue
        if is_template_or_report(p):
            continue
        lines = read(p).splitlines()
        for line in lines:
            if not line_mentions_current_objective(line):
                continue
            if any(obj in line for obj in APPROVED_OBJECTIVES):
                continue
            # Headings, empty fields, and template labels are not drift.
            stripped = line.strip()
            if stripped in PLACEHOLDER_OK or stripped.endswith(":") or stripped.startswith("#"):
                continue
            results.append(issue("current objective drift", rel(p), f"unapproved line: {stripped}"))
    if not results:
        results.append(pass_result("current objective drift"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Current Objective Drift", run()))
