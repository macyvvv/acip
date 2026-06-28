from collections import Counter
from selftest_common import ROOT, iter_text_files, rel, read, internal_markdown_links, pass_result, issue, print_results, is_template_or_report

ENTRYPOINT_NAMES = {
    "README.md",
    "README_REPOSITORY_COMPLETE_PACK.md",
    "README_REPOSITORY_SELFTEST_COMPLETE_PACK.md",
    "README_AGENT_OS.md",
    "README_RUNTIME_READINESS.md",
    "README_GOVERNANCE.md",
    "README_KNOWLEDGE_FACTORY.md",
}

ENTRYPOINT_DIRS = {"registry", "catalog", "docs", "contracts", "runbooks", "control"}

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
        text = read(p)
        if not text.lstrip().startswith("# "):
            results.append(issue("orphan/dead doc", r, "missing H1 title", "warning"))
        if p.name in ENTRYPOINT_NAMES:
            continue
        if is_template_or_report(p):
            continue
        if "INDEX" in p.name or "QUEUE" in p.name:
            continue
        if p.relative_to(ROOT).parts[0] in ENTRYPOINT_DIRS:
            # Many assets in these dirs are catalogued by convention, not markdown-linked.
            continue
        if referenced[r] == 0:
            results.append(issue("orphan/dead doc", r, "no inbound markdown reference", "warning"))

    if not results:
        results.append(pass_result("orphan/dead doc detection"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Orphan Dead Document Detection", run()))
