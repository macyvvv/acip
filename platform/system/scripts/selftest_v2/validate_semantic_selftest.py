#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

SELFTEST_DIR = Path(__file__).resolve().parent
if str(SELFTEST_DIR) not in sys.path:
    sys.path.insert(0, str(SELFTEST_DIR))

from semantic_common import load_config, iter_docs, print_results
from semantic_checks import (
    check_required,
    check_runtime_boundary,
    check_human_boundary,
    check_current_objective,
    check_duplicates,
    check_links,
    check_orphans,
    check_workflows,
    check_secrets,
    build_graph_summary,
)

def main() -> int:
    config = load_config()
    docs = iter_docs(config)
    results = []
    results.extend(check_required())
    results.extend(build_graph_summary(docs, config))
    results.extend(check_runtime_boundary(docs, config))
    results.extend(check_human_boundary(docs, config))
    results.extend(check_current_objective(docs, config))
    results.extend(check_duplicates(docs, config))
    results.extend(check_links(docs, config))
    results.extend(check_orphans(docs, config))
    results.extend(check_workflows(docs, config))
    results.extend(check_secrets(docs, config))
    return print_results("Repository Semantic SelfTest v2", results)

if __name__ == "__main__":
    raise SystemExit(main())
