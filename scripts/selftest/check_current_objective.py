from selftest_common import iter_text_files, rel, read, pass_result, fail, print_results

APPROVED_OBJECTIVES = {
    "Canonical Asset Production",
    "Agent OS Foundation",
    "Repository Operating System Stabilization",
}

def run():
    results = []
    for p in iter_text_files():
        if p.suffix not in {".md", ".yml", ".yaml"}:
            continue
        text = read(p)
        if "Current Objective" in text:
            if not any(obj in text for obj in APPROVED_OBJECTIVES):
                results.append(fail("current objective drift", rel(p), "Current Objective present but not approved value"))
    if not results:
        results.append(pass_result("current objective drift"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Current Objective Drift", run()))
