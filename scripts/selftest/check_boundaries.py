from selftest_common import iter_text_files, rel, read, pass_result, fail, print_results

HARD_PROHIBITED = [
    "auto_post(",
    "publish_to_platform(",
    "run_runtime_agent(",
    "scrape_platform(",
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
        text = read(p)
        lower = text.lower()
        for kw in HARD_PROHIBITED:
            if kw in text:
                results.append(fail("prohibited runtime keyword", rel(p), kw))
        for pat in RUNTIME_PATTERNS:
            if pat in lower and "unless explicitly approved" not in lower:
                results.append(fail("runtime boundary drift", rel(p), pat))
        for pat in HUMAN_ROUTINE_PATTERNS:
            if pat in lower:
                results.append(fail("human boundary drift", rel(p), pat, "warning"))
    if not results:
        results.append(pass_result("boundary validation"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Boundary Validation", run()))
