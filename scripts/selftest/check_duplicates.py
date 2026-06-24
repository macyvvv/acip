from collections import defaultdict
import re
from selftest_common import ROOT, iter_text_files, rel, read, markdown_h1, pass_result, fail, print_results

def run():
    results = []
    h1s = defaultdict(list)
    adr_nums = defaultdict(list)
    wbs_nums = defaultdict(list)

    for p in iter_text_files():
        if p.suffix == ".md":
            h1 = markdown_h1(read(p))
            if h1:
                h1s[h1.lower()].append(rel(p))
        m = re.search(r"ADR-(\d{4})", p.name)
        if m:
            adr_nums[m.group(1)].append(rel(p))
        m = re.search(r"WBS-(\d{4})", p.name)
        if m:
            wbs_nums[m.group(1)].append(rel(p))

    for title, paths in h1s.items():
        if len(paths) > 1:
            results.append(fail("duplicate h1", ", ".join(paths), title, "warning"))
    for num, paths in adr_nums.items():
        if len(paths) > 1:
            results.append(fail("duplicate ADR number", ", ".join(paths), num))
    for num, paths in wbs_nums.items():
        if len(paths) > 1:
            results.append(fail("duplicate WBS number", ", ".join(paths), num))

    if not results:
        results.append(pass_result("duplicate detection"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Duplicate Detection", run()))
