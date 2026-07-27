#!/usr/bin/env python3
"""Cases validate-digest.py must get right. Run it; it prints what failed.

WHY A TEST FILE AND NOT A HEREDOC: this validator is now a `SubagentStop` hook that
can BLOCK any agent in any project (DEC-122). A false negative silently accepts a
malformed digest; a false positive wedges a working agent. Both were live here —
the parser rejected SPEC 10.4's own normative template, and separately accepted a
`must_fix` nested inside a member entry as the top-level roll-up. Neither was
noticed because each was only ever exercised by the example that happened to pass.

    ./test-validate-digest.py     -> exit 0 all pass, 1 otherwise
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATE = os.path.join(HERE, "validate-digest.py")

# (name, persona, digest text, expect_ok, must_mention)
CASES = []


def case(name, persona, text, ok, mentions=None):
    CASES.append((name, persona, text.strip() + "\n", ok, mentions))


LEAD_BLOCK = """
VERDICT: FAIL
DIGEST:
  headline: auth endpoints built; qa found a missing refresh-token path
  team: build
  steps_run: 3
  cycles_used: 1
  members:
    - { step: build, persona: backend-dev, verdict: PASS, headline: "jwt mw", files_touched: [src/auth.ts] }
    - { step: qa, persona: qa, verdict: FAIL, severity_max: high, must_fix: ["refresh path untested"] }
  must_fix: ["refresh path untested"]
  branch: feat/auth
  files_touched: [src/auth.ts, test/auth.spec.ts]
  open_questions: []
  escalations:
  expertise_update: []
  sc_status: []
artifact: .harness/features/FEAT-01/runs/r1/digest.md
"""
case("lead, block-style members + bare empty key", "harness-eng-lead", LEAD_BLOCK, True)

# Every list inline. Both styles are legal YAML and agents write both.
#
# NOTE the members entries are still STRUCTURED. An earlier version of this case used
# bare strings (`[code-reviewer PASS, qa PASS]`) and the roll-up check rejected it —
# correctly. That shorthand is not a format SPEC 10.4 sanctions: it drops `step` and
# `files_touched`, which are the per-member granularity the field exists to carry, and
# it leaves the team verdict underivable. The test was wrong, not the validator.
case("lead, fully inline lists", "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: panel clean across four reviewers
  team: review
  steps_run: 5
  cycles_used: 0
  members: [{ step: s1, persona: code-reviewer, verdict: PASS }, { step: s2, persona: qa, verdict: PASS }]
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/features/FEAT-01/runs/r2/digest.md
""", True)

# THE FALSE PASS. `must_fix` appears ONLY inside a member entry. The old parser
# harvested keys at every depth and accepted this as the top-level roll-up — the
# one field whose whole purpose is to be the union across members.
case("nested must_fix must NOT satisfy the top-level one", "harness-eng-lead", """
VERDICT: FAIL
DIGEST:
  headline: qa failed
  team: build
  steps_run: 2
  cycles_used: 0
  members:
    - { step: qa, persona: qa, verdict: FAIL, must_fix: ["refresh path untested"] }
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: .harness/features/FEAT-01/runs/r3/digest.md
""", False, "must_fix")

# SPEC 10.4 packed three fields onto one source line for compactness. That is not
# YAML, and a lead copying it verbatim loses two required fields silently.
case("three fields on one line loses two", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: done
  team: build            steps_run: 3   cycles_used: 0
  members: []
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: x.md
""", False, "steps_run")

case("doer, inline — unchanged behaviour", "harness-backend-dev", """
VERDICT: PASS
DIGEST:
  headline: jwt middleware added, suite green
  tests_added: 4
  suite: pass
  blocked_on: none
  files_touched: [src/auth.ts]
  open_questions: []
  expertise_update: []
artifact: .harness/notes/impl-auth.md
""", True)

case("drifted key spelling is caught", "harness-code-reviewer", """
VERDICT: FAIL
DIGEST:
  headline: two blocking findings
  severity_max: high
  findings: 2
  must-fix: ["fail-open branch in auth"]
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/review-code.md
""", False, "drifted")

case("enum near-miss is caught, not normalized", "harness-code-reviewer", """
VERDICT: FAIL
DIGEST:
  headline: one finding
  severity_max: medium
  findings: 1
  must_fix: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/review-code.md
""", False, "med")

case("open_questions as a count, not a list", "harness-qa", """
VERDICT: PASS
DIGEST:
  headline: suite green
  suite: pass
  failures: 0
  coverage_gaps: []
  matrix_ok: true
  files_touched: []
  open_questions: 0
  expertise_update: []
artifact: .harness/notes/qa.md
""", False, "COUNT")

# A bare `escalations:` with a DEEPER KEY under it is a mapping, not a list, and the
# lead almost certainly meant a list. It parses to [] — which is a legitimate "none".
# Recorded as accepted so the behaviour is a decision rather than an accident.
case("bare key followed by nothing is an empty list", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean run
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - { step: build, persona: backend-dev, verdict: PASS }
  must_fix:
  branch: none
  files_touched: []
  open_questions:
  escalations:
  expertise_update:
  sc_status:
artifact: x.md
""", True)

# SPEC 10.4 and the runner both annotate their templates inline, so agents copy the
# comments too. `steps_run: 3  # …` parsed as a string; `members:  # …` parsed as a
# scalar and hid the block under it. The validator rejected its own documented format.
case("inline # comments are stripped, not parsed", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean
  team: build                     # one key per line
  steps_run: 3                    # not a string
  cycles_used: 0
  members:                        # per-member roll-up — NOT optional
    - { step: s1, persona: backend-dev, verdict: PASS }
  must_fix: []
  branch: none                    # `none` if nothing was mutated
  files_touched: [src/auth.ts]    # union across members
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []                   # [] if no goal-check ran
artifact: r/digest.md             # not state.yaml
""", True)

# A `#` inside quotes or brackets is content, not a comment.
case("# inside a quoted value survives", "harness-backend-dev", """
VERDICT: PASS
DIGEST:
  headline: "closes #42 — token refresh"
  tests_added: 2
  suite: pass
  blocked_on: none
  files_touched: [src/a.ts]
  open_questions: []
  expertise_update: []
artifact: x.md
""", True)

case("no VERDICT at all", "harness-qa", """
DIGEST:
  headline: whatever
artifact: x.md
""", False, "no VERDICT")


# The roll-up is the only part of collation that is arithmetic. It was prose with a
# validator next to it that could check it and didn't — the shape of DEC-19/110/119.
case("PASS over a failing member is rejected", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: two of three passed
  team: build
  steps_run: 3
  cycles_used: 0
  members:
    - { step: s1, persona: backend-dev, verdict: PASS }
    - { step: s2, persona: qa, verdict: FAIL }
  must_fix: ["refresh path untested"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "worst member verdict")

# ESCALATE outranks FAIL: a decision only the user can make must not be masked by a
# failure the team could have fixed.
case("FAIL over an escalating member is rejected", "harness-validator-lead", """
VERDICT: FAIL
DIGEST:
  headline: panel found issues and one open decision
  team: review
  steps_run: 4
  cycles_used: 0
  members:
    - { step: s1, persona: code-reviewer, verdict: FAIL }
    - { step: s2, persona: security-reviewer, verdict: ESCALATE }
  must_fix: ["fail-open branch"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "ESCALATE")

# Reporting WORSE than the members is allowed — a lead may have its own reason.
case("lead may report worse than its members", "harness-eng-lead", """
VERDICT: BLOCKED
DIGEST:
  headline: members passed but the branch will not build
  team: build
  steps_run: 2
  cycles_used: 0
  members:
    - { step: s1, persona: backend-dev, verdict: PASS }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", True)

case("a members entry with no verdict is rejected", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - { step: s1, persona: backend-dev, headline: "did the thing" }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "no verdict")


def main():
    fails = 0
    for name, persona, text, want_ok, mentions in CASES:
        r = subprocess.run([VALIDATE, persona], input=text,
                           capture_output=True, text=True)
        got_ok = r.returncode == 0
        bad = []
        if got_ok != want_ok:
            bad.append(f"expected {'PASS' if want_ok else 'REJECT'}, "
                       f"got {'PASS' if got_ok else 'REJECT'}")
        if mentions and mentions.lower() not in r.stdout.lower():
            bad.append(f"reason should mention {mentions!r}")
        if bad:
            fails += 1
            print(f"FAIL  {name}")
            for b in bad:
                print(f"        {b}")
            for l in r.stdout.strip().splitlines():
                print(f"      | {l}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
