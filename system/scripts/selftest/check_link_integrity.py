from pathlib import Path
from selftest_common import ROOT, iter_text_files, rel, read, internal_markdown_links, pass_result, fail, print_results

def run():
    results = []
    for p in iter_text_files():
        if p.suffix != ".md":
            continue
        for target in internal_markdown_links(read(p)):
            candidate = (p.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                results.append(fail("link integrity", rel(p), f"link escapes repo: {target}"))
                continue
            if not candidate.exists():
                results.append(fail("link integrity", rel(p), f"missing target: {target}"))
    if not results:
        results.append(pass_result("link integrity"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Link Integrity", run()))
