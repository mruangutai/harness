#!/usr/bin/env python3
import sys

from unit_support import ROOT
from check_support import Checks

C = Checks()
check = C.check

SETUP = "git config core.hooksPath .claude/skills/harness/hooks"


def step(workflow, name):
    start = workflow.find(name)
    if start < 0:
        return None
    return workflow[start:workflow.find("\n      - name:", start + 1)]


def instruction_gate_is_enforced(workflow):
    gate = step(workflow, "name: Instruction-path gate")
    return gate is not None and "check-instruction-paths.py" in gate and 'exit "$rc"' in gate


def repository_state_gate_is_runnable(workflow):
    gate = step(workflow, "name: Repository-state gate")
    if gate is None:
        return False
    commands = [line.strip() for line in gate.splitlines()]
    try:
        setup_index = commands.index(SETUP)
        check_index = next(i for i, line in enumerate(commands) if "check-state.py" in line)
    except (ValueError, StopIteration):
        return False
    return setup_index < check_index and 'exit "$rc"' in gate


workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
check("workflow runs instruction gate and propagates its nonzero status",
      instruction_gate_is_enforced(workflow))
check("workflow mutant without instruction gate is refused",
      not instruction_gate_is_enforced(workflow.replace(
          "name: Instruction-path gate", "name: Removed instruction gate", 1)))
gate = step(workflow, "name: Instruction-path gate")
ignored = workflow.replace(gate, gate.replace('exit "$rc"', "exit 0", 1), 1)
check("workflow mutant that ignores gate status is refused",
      not instruction_gate_is_enforced(ignored))
check("repository-state gate installs tracked hooks before checking INV-31",
      repository_state_gate_is_runnable(workflow))
for label, replacement in (("without hook setup", ""),
                           ("with commented hook setup", "# " + SETUP),
                           ("that only echoes hook setup", "echo " + SETUP)):
    check(f"repository-state mutant {label} is refused",
          not repository_state_gate_is_runnable(workflow.replace(SETUP, replacement, 1)))

sys.exit(C.report())
