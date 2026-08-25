#!/usr/bin/env python3
"""Tests that the orchestrator playbook (SKILL.md) never returns to the receive-and-wait
loop it replaced (FEAT-35).

The positive `NEVER WAIT FOR A LEAD` assertion was retired when that block left the
playbook: FEAT-35 REQ-07 puts the rule and its reason in DECISIONS.md (DEC-201), and
REQ-02 is met by the loop's own "There is no waiting anywhere in this loop". The
retired-wording absences below are what still guards the direction of travel.

Stdlib only, no subprocess: reads the playbook text straight off disk from PLAYBOOK_PATH
(default .claude/skills/harness/SKILL.md), so the same seven assertions can be pointed at
an older copy (e.g. a `git show <rev>:...SKILL.md` extract) to prove they discriminate.

Case 6 is worded as a PRESENCE assertion, not a pure negative, on purpose. The intent's
literal wording ("no single line contains orchestrator_context_warn_tokens together with
refuse/refused/blocked/prevented") is vacuously true the moment the token is simply absent
from the file — which is exactly the state at 569d417 (measured: 0 occurrences there,
1 at current SKILL.md). Pairing the clean-line requirement with a presence requirement is
what keeps the case a real discriminator rather than a check that could never have failed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DEFAULT_PLAYBOOK = os.path.join(ROOT, ".claude", "skills", "harness", "SKILL.md")

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def read_playbook():
    path = os.environ.get("PLAYBOOK_PATH", DEFAULT_PLAYBOOK)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read(), path


REFUSAL_WORDS_RE = re.compile(r"refuse|refused|blocked|prevented", re.IGNORECASE)
CONTEXT_WARN_TOKEN = "orchestrator_context_warn_tokens"


def case1_absence_receive_team_digest(text):
    literal = "Receive the team digest"
    check("case1_absence_receive_the_team_digest", literal not in text,
          f"found the retired literal {literal!r}")


def case2_absence_loop_until_done(text):
    literal = "Loop until DONE"
    check("case2_absence_loop_until_done", literal not in text,
          f"found the retired literal {literal!r}")


def case4_presence_context_watch(text):
    literal = "context-watch.py"
    check("case4_presence_context_watch_py", literal in text,
          f"literal {literal!r} not found")


def case5_presence_context_warn_tokens(text):
    check("case5_presence_orchestrator_context_warn_tokens",
          CONTEXT_WARN_TOKEN in text,
          f"literal {CONTEXT_WARN_TOKEN!r} not found")


def case6_context_warn_tokens_never_paired_with_refusal(text):
    # A presence requirement paired with the clean-line requirement — see module
    # docstring on why a pure negative cannot discriminate here.
    present = CONTEXT_WARN_TOKEN in text
    check("case6_presence_orchestrator_context_warn_tokens_exists_at_all",
          present, f"literal {CONTEXT_WARN_TOKEN!r} not found, so the clean-line "
          "half below cannot mean anything")

    tainted_lines = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if CONTEXT_WARN_TOKEN in line and REFUSAL_WORDS_RE.search(line):
            tainted_lines.append(lineno)
    check("case6_absence_context_warn_tokens_never_reads_as_a_refusal_trigger",
          present and tainted_lines == [],
          f"lines pairing {CONTEXT_WARN_TOKEN!r} with a refusal word: {tainted_lines}")


def case7_absence_record_your_phase_in(text):
    literal = "Record your phase in"
    check("case7_absence_record_your_phase_in", literal not in text,
          f"found the retired literal {literal!r}")


def case8_presence_record_your_status_in(text):
    literal = "Record your status in"
    check("case8_presence_record_your_status_in", literal in text,
          f"literal {literal!r} not found")


def main():
    text, path = read_playbook()
    print(f"reading playbook from {path}")

    case1_absence_receive_team_digest(text)
    case2_absence_loop_until_done(text)
    case4_presence_context_watch(text)
    case5_presence_context_warn_tokens(text)
    case6_context_warn_tokens_never_paired_with_refusal(text)
    case7_absence_record_your_phase_in(text)
    case8_presence_record_your_status_in(text)

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
