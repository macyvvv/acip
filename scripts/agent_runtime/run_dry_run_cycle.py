#!/usr/bin/env python3
from agent_runtime.cycle import run_dry_run_cycle

if __name__ == "__main__":
    result = run_dry_run_cycle()
    print("# Agent Runtime MVP Dry Run")
    print(f"status={result['status']}")
    print(f"output_dir={result['output_dir']}")
