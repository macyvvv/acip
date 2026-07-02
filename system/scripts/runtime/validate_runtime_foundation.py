import subprocess, sys

subprocess.check_call([sys.executable, "system/scripts/runtime/context_loader.py"])
subprocess.check_call([sys.executable, "system/scripts/runtime/dry_run_adapter.py"])
print("Runtime Foundation Validation passed.")
