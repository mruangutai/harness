#!/usr/bin/env python3
"""Tests that the orchestrator playbook (SKILL.md) never returns to the receive-and-wait
loop it replaced (FEAT-35).

The positive `NEVER WAIT FOR A LEAD` assertion was retired when that block left the
playbook: FEAT-35 REQ-07 puts the rule and its reason in DECISIONS.md (DEC-201), and
REQ-02 is met by the loop's own "There is no waiting anywhere in this loop". The
retired-wording absences below are what still guards the direction of travel.

Stdlib only, no subprocess: reads the playbook text straight off disk from PLAYBOOK_PATH
(default .agents/skills/harness/SKILL.md), so the same seven assertions can be pointed at
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
DEFAULT_PLAYBOOK = os.path.join(ROOT, ".agents", "skills", "harness", "SKILL.md")

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


def case4_host_neutral_context_signal(text):
    """FEAT-44: the playbook must describe the mechanism that EXISTS.

    Retargeted. The old presence half asserted the wording "host's current-session context
    signal", which PR #922 introduced and issue #923 then measured as naming nothing: the
    signal it pointed at returns `undefined` in exactly the session type an orchestrator runs
    in. A test that asserts a sentence passes because the sentence was written, which is how
    a green suite coexisted with a capability that had gone inert.

    These assert the shape of the mechanism now in place: the figure ARRIVES, unrequested, on
    the wake; the orchestrator never goes looking for it.
    """
    # Whitespace-tolerant: SKILL.md hard-wraps, so any of these phrases can straddle a line
    # break. A plain substring test would fail on reflow rather than on substance.
    for phrase, why in (
        ("reads your own OMP transcript off disk",
         "step 5 no longer describes the hook reading the transcript"),
        ("appends one advisory line",
         "step 5 no longer says the advisory arrives unrequested on the wake"),
    ):
        pattern = re.compile(r"\s+".join(re.escape(word) for word in phrase.split()))
        check(f"case4_presence_{phrase.split()[0]}_{phrase.split()[1]}",
              bool(pattern.search(text)), f"{why} (looked for {phrase!r})")
    check("case4_absence_claude_sidecar_probe", "context-watch.py" not in text,
          "Claude-only context-watch.py still appears in the canonical OMP playbook")
    # The numeral must live in harness.json alone. Prose carrying it goes stale on the next
    # budget change with every gate still green, which is the DEC-198 half of the same defect.
    check("case4_absence_hardcoded_threshold_numeral", "200000" not in text,
          "step 5 restates the threshold numeral; it must name the key and let the runtime "
          "advisory carry the resolved value")


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
    literal = "Record your station in"
    check("case8_presence_record_your_status_in", literal in text,
          f"literal {literal!r} not found")


def case9_plan_yaml_write_is_a_verb_not_an_edit(text):
    """(9) The playbook names `set-task-station` and never sends the orchestrator to an editor.

    PAIRED, for the reason case 6 records: a pure absence assertion goes vacuously true the
    moment the subject leaves the file, so "does not say Edit plan.yaml" alone would pass a
    playbook that says nothing about writing plan.yaml at all — which is exactly the state
    this task found (measured: 0 occurrences of `set-task-station`, and the only `plan.yaml`
    mention was a READ). The presence half is what makes the pair discriminate.

    This is T-05's half of closing the write window. It must hold before T-09 denies the
    editor route, because an agent denied a route it was never told to replace has no legal
    way to record a task status — the failure this playbook's own history records, five task
    statuses lost.
    """
    check("case9a_playbook_names_set_task_station",
          "set-task-station" in text,
          "the playbook does not name the verb that writes a task station")

    # The absence half is a LINE-LEVEL scan, not a document-level one. "Edit" and "plan.yaml"
    # both occur legitimately and far apart — the file forbids editing the plan at all, which
    # is the same instruction stated as a prohibition. Only the two together on one line is
    # the editor route being prescribed.
    offenders = [l.strip() for l in text.splitlines()
                 if "plan.yaml" in l and re.search(r"\bEdit\b", l)
                 and not re.search(r"never|not|no\s+`?Edit|denies|refus", l, re.I)]
    check("case9b_playbook_never_prescribes_an_Edit_of_plan_yaml",
          not offenders, f"lines prescribing an Edit of plan.yaml: {offenders}")


def case10_claude_code_suspension(text):
    start = text.find("Under the Claude Code compatibility host")
    region = text[start:start + 1200] if start >= 0 else ""
    checks = (
        ("suspended awaiting",
         re.search(r"VERDICT:?\s*`?\s*SUSPENDED.*awaiting", region, re.I | re.S)),
        ("zero polling",
         re.search(r"Do not poll.*sleep.*heartbeat.*invent.*zero", region, re.I | re.S)),
        ("same parent registry",
         re.search(r"same parent.*registry.*replacement parent", region, re.I | re.S)),
        ("explicit quarantine adoption",
         re.search(r"quarantine\.py list.*adopt.*discard.*automatic.*timer.*non-canonical",
                   region, re.I | re.S)),
    )
    for clause, match in checks:
        check(f"case10_claude_code_suspension_{clause.replace(' ', '_')}",
              bool(match), f"compatibility region misses {clause}")


def main():
    text, path = read_playbook()
    print(f"reading playbook from {path}")

    case1_absence_receive_team_digest(text)
    case2_absence_loop_until_done(text)
    case4_host_neutral_context_signal(text)
    case5_presence_context_warn_tokens(text)
    case6_context_warn_tokens_never_paired_with_refusal(text)
    case7_absence_record_your_phase_in(text)
    case8_presence_record_your_status_in(text)
    case9_plan_yaml_write_is_a_verb_not_an_edit(text)
    case10_claude_code_suspension(text)

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
