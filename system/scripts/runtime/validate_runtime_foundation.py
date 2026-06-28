import subprocess,sys
subprocess.check_call([sys.executable,'system/scripts/system/runtime/context_loader.py']);subprocess.check_call([sys.executable,'system/scripts/system/runtime/dry_run_adapter.py']);print('Runtime Foundation Validation passed.')
