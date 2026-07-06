from collections import defaultdict
import re
from selftest_common import iter_text_files, rel, read, markdown_h1, pass_result, issue, print_results

# Deprecated skeleton files are handled by cleanup_selftest_skeleton.py and reported as warnings here.
KNOWN_DEPRECATED_DUPLICATE_FILES = {
    "archive/selftest_skeleton/adr/ADR-0016-repository-self-test.md",
    "archive/selftest_skeleton/wbs/WBS-0011-repository-selftest.md",
    "archive/selftest_skeleton/README_SELFTEST_PACK.md",
    "archive/selftest_skeleton/README_REPOSITORY_SELFTEST_PACK.md",
}

def run():
    results = []
    h1s = defaultdict(list)
    adr_nums = defaultdict(list)
    wbs_nums = defaultdict(list)

    for p in iter_text_files():
        r = rel(p)
        if p.suffix == ".md":
            h1 = markdown_h1(read(p))
            if h1:
                h1s[h1.lower()].append(r)
        m = re.search(r"ADR-(\d{4})", p.name)
        if m:
            adr_nums[m.group(1)].append(r)
        m = re.search(r"WBS-(\d{4})", p.name)
        if m:
            wbs_nums[m.group(1)].append(r)

    for title, paths in h1s.items():
        canonical_paths = [p for p in paths if p not in KNOWN_DEPRECATED_DUPLICATE_FILES]
        if len(canonical_paths) > 1:
            results.append(issue("duplicate h1", ", ".join(canonical_paths), title, "warning"))

    for num, paths in adr_nums.items():
        active = [p for p in paths if p not in KNOWN_DEPRECATED_DUPLICATE_FILES]
        deprecated = [p for p in paths if p in KNOWN_DEPRECATED_DUPLICATE_FILES]
        if len(active) > 1:
            results.append(issue("duplicate ADR number", ", ".join(active), num))
        elif deprecated:
            results.append(issue("deprecated duplicate ADR number", ", ".join(deprecated), num, "warning"))

    for num, paths in wbs_nums.items():
        active = [p for p in paths if p not in KNOWN_DEPRECATED_DUPLICATE_FILES]
        deprecated = [p for p in paths if p in KNOWN_DEPRECATED_DUPLICATE_FILES]
        if len(active) > 1:
            results.append(issue("duplicate WBS number", ", ".join(active), num))
        elif deprecated:
            results.append(issue("deprecated duplicate WBS number", ", ".join(deprecated), num, "warning"))

    if not results:
        results.append(pass_result("duplicate detection"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Duplicate Detection", run()))
