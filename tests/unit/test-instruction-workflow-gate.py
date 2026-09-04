#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAILURES = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL") + " - " + name
          + (f" ({detail})" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


def instruction_gate_is_enforced(workflow):
    start = workflow.find("name: Instruction-path gate")
    if start < 0:
        return False
    gate = workflow[start:workflow.find("\n      - name:", start + 1)]
    return "check-instruction-paths.py" in gate and 'exit "$rc"' in gate

def repository_state_gate_is_runnable(workflow):
    start = workflow.find("name: Repository-state gate")
    if start < 0:
        return False
    gate = workflow[start:workflow.find("\n      - name:", start + 1)]
    setup = "git config core.hooksPath .claude/skills/harness/hooks"
    commands = [line.strip() for line in gate.splitlines()]
    try:
        setup_index = commands.index(setup)
        check_index = next(i for i, line in enumerate(commands) if "check-state.sh" in line)
    except (ValueError, StopIteration):
        return False
    return setup_index < check_index and 'exit "$rc"' in gate


workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
check("workflow runs instruction gate and propagates its nonzero status",
      instruction_gate_is_enforced(workflow))
check("workflow mutant without instruction gate is refused",
      not instruction_gate_is_enforced(workflow.replace(
          "name: Instruction-path gate", "name: Removed instruction gate", 1)))
start = workflow.find("name: Instruction-path gate")
end = workflow.find("\n      - name:", start + 1)
ignored = workflow[:start] + workflow[start:end].replace('exit "$rc"', "exit 0", 1) + workflow[end:]
check("workflow mutant that ignores gate status is refused",
      not instruction_gate_is_enforced(ignored))
check("repository-state gate installs tracked hooks before checking INV-31",
      repository_state_gate_is_runnable(workflow))
check("repository-state mutant without hook setup is refused",
      not repository_state_gate_is_runnable(workflow.replace(
          "git config core.hooksPath .claude/skills/harness/hooks", "", 1)))
check("repository-state mutant with commented hook setup is refused",
      not repository_state_gate_is_runnable(workflow.replace(
          "git config core.hooksPath .claude/skills/harness/hooks",
          "# git config core.hooksPath .claude/skills/harness/hooks", 1)))
check("repository-state mutant that only echoes hook setup is refused",
      not repository_state_gate_is_runnable(workflow.replace(
          "git config core.hooksPath .claude/skills/harness/hooks",
          "echo git config core.hooksPath .claude/skills/harness/hooks", 1)))

if FAILURES:
    raise SystemExit(1)
