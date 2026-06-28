import re
from selftest_common import ROOT, read, rel, pass_result, fail, print_results

def run():
    results = []
    workflows = ROOT / ".github" / "workflows"
    for wf in workflows.glob("*.yml"):
        text = read(wf)
        for script in re.findall(r"python\s+([A-Za-z0-9_./-]+\.py)", text):
            if not (ROOT / script).exists():
                results.append(fail("workflow-script consistency", rel(wf), f"missing script: {script}"))
    if not results:
        results.append(pass_result("workflow-script consistency"))
    return results

if __name__ == "__main__":
    raise SystemExit(print_results("Workflow Script Consistency", run()))
