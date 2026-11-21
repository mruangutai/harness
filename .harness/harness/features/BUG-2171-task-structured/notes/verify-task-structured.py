#!/usr/bin/env python3
"""BUG-2171 T-01 verify proofs, moved verbatim out of plan.yaml for the DEC-182 budget.

Each body below is byte-identical to the heredoc it replaces in the signed verify block;
run from the worktree root: `python3 <this file> <step>`.
"""
import sys

BODIES = {
    'port-red-green': r'''import os, subprocess, sys, tempfile
from pathlib import Path
root = Path.cwd(); bin_dir = root / ".claude/skills/harness/bin"
test = root / "tests/integration/test-check-omp-port.py"
ns = {"__file__": str(test), "__name__": "bug2171_red_green"}
exec(compile(test.read_text(), str(test), "exec"), ns)
case = ns["case_task_structured_required"]; fixed = ns["CHECK"]
os.environ["PYTHONPATH"] = str(bin_dir)
with tempfile.TemporaryDirectory() as td:
    base = Path(td) / "check-omp-port.py"
    base.write_bytes(subprocess.check_output(["git", "show", "b7af829c0207522b43f978b5275a2ebdc96b3210:.claude/skills/harness/bin/check-omp-port.py"]))
    ns["CHECK"] = base
    red = [label for label, ok, detail in case() if not ok]
    assert red, "Base unexpectedly satisfies the new structured-return regression"
    print("RED b7af829c:", red)
    ns["CHECK"] = fixed
    green = list(case()); assert green and all(ok for label, ok, detail in green), green
    print("GREEN fixed gate:", [label for label, ok, detail in green])
''',
    'hook-red-green': r'''import subprocess, tempfile
from pathlib import Path
root = Path.cwd()
with tempfile.TemporaryDirectory() as td:
    tree = Path(td) / "proof"
    subprocess.run(["git", "clone", "--shared", "--no-hardlinks", str(root), str(tree)], check=True)
    for rel in ["tests/unit/omp-hooks.test.ts", ".omp/extensions/harness-hooks.ts"]:
        (tree / rel).write_bytes((root / rel).read_bytes())
    hook = tree / ".omp/extensions/harness-hooks.ts"
    fixed = hook.read_bytes()
    hook.write_bytes(subprocess.check_output(["git", "show", "b7af829c0207522b43f978b5275a2ebdc96b3210:.omp/extensions/harness-hooks.ts"], cwd=root))
    command = ["bun", "test", "tests/unit/omp-hooks.test.ts", "--test-name-pattern", "BUG-2171 string-serialized PASS digest"]
    red = subprocess.run(command, cwd=tree, text=True, capture_output=True)
    print("RED b7af829c hook assertion output:", red.stdout, red.stderr, flush=True)
    assert red.returncode != 0 and "expect(" in red.stderr and "fail" in red.stderr, "Need actual new assertion failure, not invocation failure"
    hook.write_bytes(fixed)
    green = subprocess.run(command, cwd=tree, text=True, capture_output=True)
    print("GREEN fixed hook assertion output:", green.stdout, green.stderr, flush=True)
    assert green.returncode == 0 and "1 pass" in green.stderr, "Need actual new assertion pass"
''',
    'append-check': r'''import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / ".claude/skills/harness/bin"))
from digest_record import last_fenced_mapping
run = Path(".harness/harness/features/BUG-2171-task-structured/runs/2026-11-08-02-smoke-product")
before = (run / "before.md").read_text(); after = (run / "digest.md").read_text()
assert before and chr(96)*3 not in before and after.startswith(before) and len(before) < len(after)
record = last_fenced_mapping(after); assert set(record) == {"VERDICT", "DIGEST", "artifact"} and record["VERDICT"] == "PASS"
assert Path(record["artifact"]).resolve() == (run / "digest.md").resolve()
print("PASS hook-owned append: human-only prefix preserved; canonical reader selects lead record")
''',
}

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) == 2 else ""
    if step not in BODIES:
        sys.exit(f"usage: {sys.argv[0]} {{{'|'.join(BODIES)}}}")
    exec(compile(BODIES[step], f"<BUG-2171 {step}>", "exec"), {"__name__": "__main__"})
