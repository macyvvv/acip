from collections import Counter
from selftest_common import ROOT, iter_text_files, rel, read, internal_markdown_links, pass_result, fail, print_results

INDEXED_DIRS = {"basis", "adr", "wbs", "docs", "catalog", "registry", "contracts", "runbooks", "control"}

def run():
    referenced = Counter()
    markdown_files = []
    for p in iter_text_files():
        if p.suffix == ".md":
            markdown_files.append(p)
            for target in internal_markdown_links(read(p)):
                candidate = (p.parent / target).resolve()
                if candidate.exists():
                    referenced[candidate.relative_to(ROOT).as_posix()] += 1

    results = []
    for p in markdown_files:
        r = rel(p)
        if p.parts and p.relative_to(ROOT).parts[0] in INDEXED_DIRS:
            text = read(p)
            if not text.lstrip().startswith("# "):
                results.append(fail("orphan/dead doc", r, "missing H1 title", "warning"))
            # Root READMEs and index docs may be entrypoints. Others with no inbound link are warning.
            if referenced[r] == 0 and not p.name.startswith("README") and "INDEX" not in p.name and "CHECKLIST" not in p.name:
                results.append(fail("orphan/dead doc", r, "no inbound markdown reference", "warning"))
    if not results:
        results.append(pass_result("orphan/dead doc detection"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Orphan Dead Document Detection", run()))
