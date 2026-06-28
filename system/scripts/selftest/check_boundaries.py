from selftest_common import iter_text_files, rel, read, pass_result, issue, print_results, is_selftest_script

# Use separated fragments so this checker does not match itself.
HARD_PROHIBITED = [
    "auto" + "_post(",
    "publish" + "_to_platform(",
    "run" + "_runtime_agent(",
    "scrape" + "_platform(",
]

RUNTIME_PATTERNS = [
    "runtime agent execution is approved",
    "auto posting is approved",
    "platform api integration is approved",
]

HUMAN_ROUTINE_PATTERNS = [
    "human must manually",
    "human should manually",
    "human is responsible for routine",
    "human performs routine",
]

def run():
    results = []
    for p in iter_text_files():
        if is_selftest_script(p):
            continue
        text = read(p)
        lower = text.lower()
        for kw in HARD_PROHIBITED:
            if kw in text:
                results.append(issue("prohibited runtime keyword", rel(p), kw))
        for pat in RUNTIME_PATTERNS:
            if pat in lower and "unless explicitly approved" not in lower:
                results.append(issue("runtime boundary drift", rel(p), pat))
        for pat in HUMAN_ROUTINE_PATTERNS:
            if pat in lower:
                results.append(issue("human boundary drift", rel(p), pat, "warning"))
    if not results:
        results.append(pass_result("boundary validation"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Boundary Validation", run()))
