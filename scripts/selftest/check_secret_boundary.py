from selftest_common import iter_text_files, rel, read, pass_result, fail, print_results
import re

PATTERNS = [
    ("openai key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("github token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("aws access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----")),
]

ALLOWLIST_FILES = {
    ".env.example",
}

def run():
    results = []
    for p in iter_text_files():
        if p.name in ALLOWLIST_FILES:
            continue
        text = read(p)
        for name, pattern in PATTERNS:
            if pattern.search(text):
                results.append(fail("secret boundary", rel(p), f"possible {name}"))
    if not results:
        results.append(pass_result("secret boundary"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Secret Boundary", run()))
