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
import json, re, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
# Overridable so the pre-fix binary can be run through the SAME suite to prove
# each new regression case actually fails against the old code (task 22).
VALIDATE = os.environ.get("VALIDATE_DIGEST_BIN") or os.path.join(HERE, "validate-digest.py")
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# The two normative templates (DEC-123) must validate — extracted from their
# SOURCE FILES and run through the validator, not eyeballed. (name, file, heading)
TEMPLATES = [
    ("SPEC §10.4", os.path.join(REPO_ROOT, "docs/harness/SPEC.md"),
     "### 10.4 The team digest"),
    ("harness-team \"Reporting up\"",
     os.path.join(REPO_ROOT, ".claude/skills/harness-team/SKILL.md"),
     "## Reporting up"),
]


def extract_fenced_block(path, anchor):
    """Pull the normative return template out of a doc, after `anchor`.

    Line-based on purpose. DEC-172 wrapped every template in a ```yaml fence, and
    that fence is itself DISPLAYED inside a four-backtick fence so the doc can show
    the backticks an agent must emit. Substring-scanning for "```" matches the first
    three characters of the outer ```` and captures nothing — which is exactly how
    this broke. Target the inner ```yaml line and stop at the next bare ```.
    """
    lines = open(path).read().split("\n")
    start = next(i for i, l in enumerate(lines) if anchor in l)
    open_at = next(i for i in range(start, len(lines))
                   if lines[i].strip() in ("```yaml", "```"))
    close_at = next(i for i in range(open_at + 1, len(lines))
                    if lines[i].strip() == "```")
    return "\n".join(lines[open_at + 1:close_at]) + "\n"


def fill_placeholders(text):
    """Fill a normative template's `<placeholder>` markers with concrete, valid
    values so it can be run through the validator as a real digest. Every
    substitution is mechanical — no restructuring, no correcting the template.
    """
    text = text.replace("<roll-up>", "FAIL")           # worst member below is FAIL
    text = re.sub(r"\[<[^\]\n]*>\]", "[]", text)        # `[<prose>]` list placeholders
    text = re.sub(r"\[\.\.\.\]", "[]", text)            # `[...]` list placeholders
    text = re.sub(r"\[\{[^\]\n]*\}\]", "[]", text)      # `[{ key, key, ... }]` shorthand
    text = text.replace('"..."', '"example"')
    text = (text.replace("<id>", "s1")
                .replace("<p>", "backend-dev")
                .replace("<v>", "PASS"))
    text = re.sub(r"<branch\s*\|\s*none>", "none", text)
    text = text.replace("<n>", "1").replace("<run_dir>", "r")
    text = re.sub(r"<[^>\n]*>", "example", text)        # anything else scalar
    return text


def run_template_cases():
    fails = 0
    for name, path, anchor in TEMPLATES:
        filled = fill_placeholders(extract_fenced_block(path, anchor))
        r = subprocess.run([VALIDATE, "lead"], input=filled,
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f"ok    [template] {name}")
        else:
            fails += 1
            print(f"FAIL  [template] {name}")
            for l in r.stdout.strip().splitlines():
                print(f"      | {l}")
    print(f"\n{len(TEMPLATES) - fails}/{len(TEMPLATES)} template cases passed.")
    return fails

# (name, persona, digest text, expect_ok, must_mention)
CASES = []
# (name, agent_type, last_assistant_message text or None, payload_overrides dict,
#  expect_exit, must_mention_on_stderr)
HOOK_CASES = []


def case(name, persona, text, ok, mentions=None):
    CASES.append((name, persona, text.strip() + "\n", ok, mentions))


def hook_case(name, agent_type, text, expect_exit, mentions=None, **overrides):
    payload = {"agent_type": agent_type, "last_assistant_message": text}
    payload.update(overrides)
    HOOK_CASES.append((name, payload, expect_exit, mentions))


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
  task: T-01
  task_verify: pass
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
""", False,
     # F11: `mentions="med"` used to pass vacuously — "med" is a substring of
     # "medium", the value the error message echoes back regardless of whether the
     # near-miss hint exists at all. Assert the actual hint text so deleting the
     # hint would fail this test.
     "mean 'med'")

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
  task: T-01
  task_verify: pass
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


# =====================================================================
# --hook mode (BUILD task 22 / F8): the ONLY mode DEC-122 makes mandatory had
# ZERO coverage in the 16 CLI-only cases above, which is why all five repros
# below shipped a masked FAIL at exit 0 and the fail-open crash went unnoticed.
# Every case here asserts the EXACT exit code (2 reject / 0 pass — never just
# "nonzero"), because a crash (old exit 1) must not be mistaken for a correct
# rejection: that confusion IS the fail-open bug.
# =====================================================================

# F1 repro 1 — quote-blind, first-match verdict regex. No unusual formatting:
# a member's own (quoted) headline contains the text "verdict: PASS", and the
# member's REAL verdict is FAIL. The old `re.search(r"\bverdict:...", str(item))`
# matched the quoted text first and masked the FAIL.
hook_case("F1.1 quoted headline text must not satisfy the verdict lookup",
          "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: retry needed
  team: build
  steps_run: 2
  cycles_used: 1
  members:
    - { step: qa, persona: qa, headline: "verdict: PASS on retry", verdict: FAIL }
  must_fix: ["fix it"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", 2, "worst member verdict")

# F1 repro 2 — multi-line inline `members: [` list. The old parser took only
# the FIRST line of an unclosed inline value, so `members: [` alone parsed to
# `[]` and the roll-up guard (gated on `isinstance(members, list)`) saw an
# empty list and emitted silence over a masked FAIL.
hook_case("F1.2 multi-line inline members list is followed to its close",
          "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: two ran
  team: build
  steps_run: 2
  cycles_used: 0
  members: [
    { step: build, persona: backend-dev, verdict: PASS },
    { step: qa, persona: qa, verdict: FAIL }
  ]
  must_fix: ["fix it"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", 2, "worst member verdict")

# F1 repro 3 — an unquoted apostrophe mid-word used to be treated as a quote
# OPEN by `split_items`, so once opened (in entry 2's headline) it swallowed
# every character until end-of-string with no closing match — fusing entry 2
# and entry 3 into one item. The OLD roll-up (a bare `re.search` for
# `verdict:` ANYWHERE in that fused string) then matched entry 2's own,
# earlier, `verdict: PASS` first and never saw entry 3's real `verdict: FAIL`.
hook_case("F1.3 unquoted apostrophe must not fuse list entries",
          "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: panel ran
  team: review
  steps_run: 3
  cycles_used: 0
  members: [{ step: s1, persona: code-reviewer, verdict: PASS }, { step: s2, persona: qa, headline: didn't stop, verdict: PASS }, { step: s3, persona: security-reviewer, verdict: FAIL }]
  must_fix: ["fix it"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", 2, "worst member verdict")

# F1 repro 4 — `members: []` alongside `steps_run: 3`: no cross-check existed,
# so a team that ran steps and reported zero members passed silently.
hook_case("F1.4 empty members against a nonzero steps_run is rejected",
          "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: nothing to report, apparently
  team: build
  steps_run: 3
  cycles_used: 0
  members: []
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", 2, "steps_run=3")

# Fail-open crash — `severity_max: [low, med]` (a LIST) against a set-typed
# schema field used to raise TypeError inside `validate()`, uncaught, which
# in --hook mode meant exit 1 — and only exit 2 blocks, so the digest shipped
# completely unvalidated with no signal. Must now be a normal exit-2 rejection.
hook_case("fail-open crash: list-valued enum is a reported violation, not a crash",
          "harness-code-reviewer", """
VERDICT: FAIL
DIGEST:
  headline: two findings
  severity_max: [low, med]
  findings: 2
  must_fix: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/review-code.md
""", 2, "must be a single value")

# --- The three deliberate pass-throughs (DEC-122), each asserted at exit 0 ---

hook_case("pass-through: non-harness agent_type is not governed",
          "Explore", "VERDICT: PASS\nDIGEST:\nartifact: x.md\n", 0)

hook_case("pass-through: stop_hook_active avoids the infinite-block loop",
          "harness-qa", "done", 0, stop_hook_active=True)

hook_case("pass-through: empty last_assistant_message passes with a stated reason",
          "harness-qa", "", 0, mentions="no final message")

# --- DEC-156: a lead's WRITTEN digest.md must carry the contract block too ---
# The kaya-ai FEAT-02 audit found every run digest.md was narrative markdown while
# every in-message return had passed this hook — the durable copy (the one a
# successor reads) was never looked at. These cases pin the file check: real files
# in a tempdir, artifact path resolved via the payload's `cwd`.
import tempfile
_D156 = tempfile.mkdtemp(prefix="vd-dec156-")

def _dec156_case(name, file_content, expect_exit, mentions=None,
                 agent="harness-eng-lead", fname="digest.md"):
    rd = tempfile.mkdtemp(dir=_D156)
    rel = os.path.join("runs", "r1", fname)
    os.makedirs(os.path.dirname(os.path.join(rd, rel)))
    if file_content is not None:
        with open(os.path.join(rd, rel), "w") as f:
            f.write(file_content)
    msg = LEAD_BLOCK.replace(
        "artifact: .harness/features/FEAT-01/runs/r1/digest.md", f"artifact: {rel}")
    HOOK_CASES.append((name,
                       {"agent_type": agent, "last_assistant_message": msg, "cwd": rd},
                       expect_exit, mentions))

_dec156_case("DEC-156: narrative digest.md with no contract block is exit 2",
             "# Team digest — T-01\n\n**PASS.** All gates green, see tables below.\n",
             2, mentions="digest FILE")
_dec156_case("DEC-156: digest.md carrying the same valid block is exit 0",
             LEAD_BLOCK, 0)
_dec156_case("DEC-156: missing file fails OPEN with the INV-15 pointer, not a block",
             None, 0, mentions="INV-15")
_dec156_case("DEC-156: file check governs leads only — a dev's artifact is not read",
             "# notes, not a digest\n", 0, agent="harness-backend-dev", fname="notes.md")
# The dev case needs a valid dev message, not a lead one — rebuild its payload.
_n, _p, _e, _m = HOOK_CASES.pop()
_p["last_assistant_message"] = (
    "VERDICT: PASS\nDIGEST:\n  headline: built\n  tests_added: 2\n  suite: pass\n"
    "  task: T-01\n  task_verify: pass\n"
    "  blocked_on: none\n  branch: none\n  files_touched: []\n  open_questions: []\n"
    "  expertise_update: []\nartifact: runs/r1/notes.md\n")
HOOK_CASES.append((_n, _p, _e, _m))


# F6: absent agent_type key must be LOUD on stderr — distinguishable from a
# present-but-non-harness value (which stays silent, asserted above).
def _missing_agent_type_case():
    payload = {"last_assistant_message": "whatever"}
    HOOK_CASES.append(("F6 missing agent_type key is loud, not silent",
                        payload, 0, "agent_type"))
_missing_agent_type_case()


# --- Fold-ins (BUILD task 22) ---

# F4: DIGEST: with a trailing comment must still be recognized — SPEC 8's own
# normative template writes it exactly this way, so the validator rejected the
# format it teaches agents to copy.
case("DIGEST: with a trailing comment is still recognized", "harness-backend-dev", """
VERDICT: PASS
DIGEST:                             # routing — orchestrator reads THIS
  headline: jwt middleware added, suite green
  tests_added: 4
  suite: pass
  blocked_on: none
  task: T-01
  task_verify: pass
  files_touched: [src/auth.ts]
  open_questions: []
  expertise_update: []
artifact: .harness/notes/impl-auth.md
""", True)

# F5: standard YAML block-mapping member entries (`- step: s1` / newline /
# `  verdict: PASS`) must be accepted — SPEC 10.4's own `escalations` example
# is written across lines, and it is legal YAML.
case("block-mapping member entries spanning lines are accepted", "harness-eng-lead", """
VERDICT: FAIL
DIGEST:
  headline: qa failed on the refresh path
  team: build
  steps_run: 2
  cycles_used: 0
  members:
    - step: build
      persona: backend-dev
      verdict: PASS
    - step: qa
      persona: qa
      verdict: FAIL
  must_fix: ["refresh path untested"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", True)

# F7: `headline` must be read at the DIGEST block's own level. No top-level
# headline, but a block-style member happens to carry its OWN `headline:` at a
# deeper level — that must not satisfy the top-level requirement.
case("a member's nested headline does not satisfy the top-level one", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - step: s1
      persona: backend-dev
      headline: "did the thing"
      verdict: PASS
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "no headline")

# F12: str-typed fields hit no type branch before this fix — an int silently
# satisfied a `str` field.
case("an int does not satisfy a str-typed field", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean
  team: 7
  steps_run: 1
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
""", False, "must be a non-empty string")

# F12: a bare `branch:` with nothing under it parses to `[]`, which is not the
# literal `none` DEC-121 requires for an inapplicable NULLABLE scalar.
case("a bare NULLABLE scalar key must not silently become an empty list", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - { step: s1, persona: backend-dev, verdict: PASS }
  must_fix: []
  branch:
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "must be a non-empty string")

# F13: the open_questions-is-a-count check must read the DIGEST's OWN top-level
# value from the parsed map, not a whole-text regex — a NESTED
# `open_questions: 0` inside a member entry, appearing before the real
# top-level list, must not produce a false positive on an otherwise-valid digest.
case("a nested open_questions count must not trip the top-level check", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - step: s1
      persona: backend-dev
      verdict: PASS
      open_questions: 0
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", True)

# F15: the drift-spelling check must cover UNIVERSAL fields too, not just the
# persona schema — `files-touched` (hyphenated) is drift of the universal
# `files_touched`, not merely an absent field.
case("drift in a UNIVERSAL field is caught, not just schema fields", "harness-backend-dev", """
VERDICT: PASS
DIGEST:
  headline: jwt middleware added, suite green
  tests_added: 4
  suite: pass
  blocked_on: none
  task: T-01
  task_verify: pass
  files-touched: [src/auth.ts]
  open_questions: []
  expertise_update: []
artifact: .harness/notes/impl-auth.md
""", False, "drifted")

# harness-orchestrator (reconciled schema, not the `lead` shape) — a positive
# case using the exact fields agreed for BUILD task 14.
case("orchestrator digest with the reconciled schema", "harness-orchestrator", """
VERDICT: PASS
DIGEST:
  headline: FEAT-01 shipped
  feature: FEAT-01
  status: shipped
  runs: [r1, r2]
  cycles_used: 2
  cost_usd: "12.83"
  briefing: .harness/notes/ship-review-FEAT-01-r2.md
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/features/FEAT-01/feature.yaml
""", True)

case("orchestrator briefing is NULLABLE — `none` when nothing was written", "harness-orchestrator", """
VERDICT: PASS
DIGEST:
  headline: mid-flight, no briefing yet
  feature: FEAT-01
  status: in_progress
  runs: [r1]
  cycles_used: 1
  cost_usd: "4.10"
  briefing: none
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/features/FEAT-01/feature.yaml
""", True)



# =====================================================================
# FEAT-02 T-01: echo shadowing. An agent that echoes the harness-handoff
# contract template before its real return gets the ECHO validated: the
# verdict regex (:380), parse_digest's DIGEST anchor (:283), and the
# artifact check (:388) are all first-match-wins, and the template line
# `VERDICT: PASS | FAIL | BLOCKED | ESCALATE` captures as a valid PASS.
# Per review advisory A-1 the echo blocks below are FILLED and
# schema-valid for their persona — a bare-placeholder echo is rejected
# on missing fields pre-fix, which would not reproduce the defect.
# =====================================================================

QA_ECHO = """
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: example headline copied from the contract
  suite: pass
  failures: 0
  coverage_gaps: []
  matrix_ok: true
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/example.md
"""

LEAD_ECHO = """
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: example headline copied from the contract
  team: build
  steps_run: 1
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
artifact: .harness/notes/example.md
"""

QA_REAL_FAIL_MISSING_MATRIX = """
VERDICT: FAIL
DIGEST:
  headline: refresh path fails under load
  suite: fail
  failures: 2
  coverage_gaps: ["refresh path"]
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/qa.md
"""

# (1) Echo + fully valid real FAIL: must exit 0 with the REAL block routed.
# Pre-fix this is green by coincidence (the echo validates too) — it exists
# to pin post-fix behaviour, paired with (2) which is red pre-fix.
case("echo shadow: valid real FAIL after a template echo still validates",
     "harness-qa", QA_ECHO + """
VERDICT: FAIL
DIGEST:
  headline: refresh path fails under load
  suite: fail
  failures: 2
  coverage_gaps: ["refresh path"]
  matrix_ok: true
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/qa.md
""", True)

# (2) Echo + real block MISSING matrix_ok: must be REJECTED for the missing
# field. Pre-fix it falsely exits 0 — the echoed (complete) block is the one
# validated and the real return is never examined.
case("echo shadow: missing matrix_ok in the real block is not masked by the echo",
     "harness-qa", QA_ECHO + QA_REAL_FAIL_MISSING_MATRIX, False, "matrix_ok")

# (3) Lead echo + real lead block whose members carry a FAIL under a top-level
# PASS: the roll-up must see the REAL members and reject. Pre-fix the echoed
# all-PASS block shadows and the roll-up never runs on the real one.
case("echo shadow: lead roll-up must read the real members, not the echo",
     "harness-eng-lead", LEAD_ECHO + """
VERDICT: PASS
DIGEST:
  headline: two ran, one failed
  team: build
  steps_run: 2
  cycles_used: 0
  members:
    - { step: build, persona: backend-dev, verdict: PASS }
    - { step: qa, persona: qa, verdict: FAIL }
  must_fix: ["refresh path untested"]
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "worst")

# (4) Hook-mode variant of (2): the SubagentStop hook is the mandatory mode
# (DEC-122), so the shadowing must be caught there too — exit 2, matrix_ok
# named on stderr. Pre-fix: exit 0, the masked return ships.
hook_case("echo shadow [hook]: missing matrix_ok behind an echo is exit 2",
          "harness-qa", QA_ECHO + QA_REAL_FAIL_MISSING_MATRIX, 2, "matrix_ok")


def run_cli_cases():
    fails = 0
    for name, persona, text, want_ok, mentions in CASES:
        r = subprocess.run([VALIDATE, persona], input=text,
                           capture_output=True, text=True)
        got_ok = r.returncode == 0
        bad = []
        if got_ok != want_ok:
            bad.append(f"expected {'PASS' if want_ok else 'REJECT'}, "
                       f"got {'PASS' if got_ok else 'REJECT'}")
        # `mentions` is a plain substring (the original contract) OR a list of
        # them, where a leading "!" means MUST NOT appear. REQ-11's hint fixtures
        # need both polarities: a hint is wrong not only for omitting the right
        # words but for carrying the wrong ones — `task_verify`'s hint naming
        # "genuinely not applicable" would route an agent into a second rejection.
        for want in ([mentions] if isinstance(mentions, str) else (mentions or [])):
            neg = want.startswith("!")
            needle = want[1:] if neg else want
            present = needle.lower() in r.stdout.lower()
            if neg and present:
                bad.append(f"reason must NOT mention {needle!r}")
            elif not neg and not present:
                bad.append(f"reason should mention {needle!r}")
        if bad:
            fails += 1
            print(f"FAIL  {name}")
            for b in bad:
                print(f"        {b}")
            for l in r.stdout.strip().splitlines():
                print(f"      | {l}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} CLI cases passed.")
    return fails


def run_hook_cases():
    """Drive --hook mode directly: JSON payload on stdin, EXACT exit code
    asserted (2 reject / 0 pass — never just 'nonzero'), rejection text
    checked on STDERR (hook mode writes there, not stdout). Asserting only
    "nonzero == rejected" would let the fail-open crash (exit 1) masquerade
    as a correct rejection — exactly the bug this suite exists to catch.
    """
    fails = 0
    for name, payload, want_exit, mentions in HOOK_CASES:
        r = subprocess.run([VALIDATE, "--hook"], input=json.dumps(payload),
                           capture_output=True, text=True)
        bad = []
        if r.returncode != want_exit:
            bad.append(f"expected exit {want_exit}, got {r.returncode}")
        if mentions and mentions.lower() not in r.stderr.lower():
            bad.append(f"stderr should mention {mentions!r}")
        if bad:
            fails += 1
            print(f"FAIL  [hook] {name}")
            for b in bad:
                print(f"        {b}")
            for l in r.stderr.strip().splitlines():
                print(f"      | {l}")
        else:
            print(f"ok    [hook] {name}")
    print(f"\n{len(HOOK_CASES) - fails}/{len(HOOK_CASES)} hook cases passed.")
    return fails


# --- DEC-173: "nothing happened" must have a truthful encoding -----------------
# The audit found 6 of 7 personas could not report a did-nothing state honestly:
# the truthful value was REJECTED while a false one was ACCEPTED, which is the
# fail-open shape (`matrix_ok: true` recorded QA's inability to run the suite as
# the blocking gate having passed). These pin BOTH directions — the honest value
# is accepted, AND the near-miss junk that DEC-121 rejects still fails.

DEV_NA = """
VERDICT: BLOCKED
DIGEST:
  headline: T-01 is under-specified and was not executed
  tests_added: 0
  suite: n/a
  blocked_on: "T-01 contains a placeholder at line 4; needs pm revision"
  task: T-01
  task_verify: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: none
"""
case("dev refusing an under-specified task can say suite: n/a", "harness-backend-dev",
     DEV_NA, True)

case("suite: n/a with VERDICT PASS is a fail-open and is REJECTED", "harness-backend-dev",
     DEV_NA.replace("VERDICT: BLOCKED", "VERDICT: PASS"), False, "pass")

QA_NA = """
VERDICT: BLOCKED
DIGEST:
  headline: the suite could not be run; no runner resolves in this project
  suite: n/a
  failures: 0
  coverage_gaps: []
  matrix_ok: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-01/notes/qa.md
"""
case("qa that cannot run the suite can say matrix_ok: n/a", "harness-qa", QA_NA, True)

case("matrix_ok: n/a with VERDICT PASS is REJECTED — the gate did not run",
     "harness-qa", QA_NA.replace("VERDICT: BLOCKED", "VERDICT: PASS"), False, "pass")

# Scope-out is a LEGITIMATE pass: ui-reviewer on a non-UI diff reviewed nothing and
# blocks nothing. This is why the gate rule is scoped to suite/matrix_ok and not
# applied to every nullable field.
case("reviewer scoping out of a non-UI diff may PASS with severity_max: n/a",
     "harness-ui-reviewer", """
VERDICT: PASS
DIGEST:
  headline: diff touches no user-facing surface; nothing to review
  severity_max: n/a
  findings: 0
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-01/notes/ui-review.md
""", True)

case("visual-designer deciding no DESIGN.md is needed may say contract: n/a",
     "harness-visual-designer", """
VERDICT: PASS
DIGEST:
  headline: surface is bin/ scripts and config; no end-user visual surface
  contract: n/a
  mockups: []
  direction_choices: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-01/notes/design-scope.md
""", True)

case("pm blocked before sizing may say surface: n/a and risk: n/a", "harness-pm", """
VERDICT: BLOCKED
DIGEST:
  headline: cannot scope — the brief's destination contradicts the codebase map
  feasibility: blocked
  surface: n/a
  recommend: halt
  risk: n/a
  tasks: 0
  decisions: 0
  needs_approval: false
  flags: []
  sc_status: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-01/notes/pm-block.md
""", True)

# REGRESSIONS — the near-miss vocabulary DEC-121 exists to catch must still fail.
case("matrix_ok: mostly is STILL rejected after n/a became legal", "harness-qa",
     QA_NA.replace("matrix_ok: n/a", 'matrix_ok: "mostly"'), False, "bool")

case("severity_max: medium is STILL rejected after n/a became legal",
     "harness-ui-reviewer", """
VERDICT: PASS
DIGEST:
  headline: reviewed
  severity_max: medium
  findings: 1
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: notes/x.md
""", False, "med")

case("dev-ops suite: n/a still accepted (it had the value before DEC-173)",
     "harness-dev-ops", """
VERDICT: PASS
DIGEST:
  headline: gitignore merged; nothing to test
  change_type: config
  applied: [.gitignore]
  suite: n/a
  task: T-01
  task_verify: pass
  open_questions: []
  files_touched: [.gitignore]
  expertise_update: []
artifact: notes/devops.md
""", True)


# --- FEAT-07: the `task`/`task_verify` pair, the conditional behind it, and the
# fail-value gate. Every case below returned `digest ok` exit 0 at 4091b36, so each
# labelled DETECTOR can only go green once the change lands; the ones labelled
# REGRESSION were green then and must stay green.
_DEV = """
VERDICT: {v}
DIGEST:
  headline: x
  tests_added: 1
  suite: {suite}
  blocked_on: none
{task}{tv}  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
"""


def _dev(v="PASS", suite="pass", task="T-01", tv="pass"):
    return _DEV.format(v=v, suite=suite,
                       task=f"  task: {task}\n" if task is not None else "",
                       tv=f"  task_verify: {tv}\n" if tv is not None else "")


# (a) DETECTOR — the requirement binds only because `task` names a real id.
case("dev missing task_verify under a real task is rejected",
     "harness-backend-dev", _dev(tv=None), False, "task_verify")
# (b) DETECTOR — REQ-01's whole point.
case("dev task_verify: fail + PASS is rejected",
     "harness-backend-dev", _dev(tv="fail"), False, "task_verify")
# (c) DETECTOR.
case("dev task_verify: n/a + PASS is rejected",
     "harness-backend-dev", _dev(tv="n/a"), False, "task_verify")
# (d) DETECTOR — the no-carve-out ruling. dev-ops is NOT exempt from this field,
# though it stays exempt from `suite` (D-03, proven by the case further above).
case("dev-ops task_verify: n/a + PASS is rejected — no carve-out",
     "harness-dev-ops", """
VERDICT: PASS
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: n/a
  task: T-01
  task_verify: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, "task_verify")
# (e) REGRESSION — REQ-03/SC-06. A task that EXISTED and was refused. SC-06 names
# FOUR accepted shapes, not one: dev and dev-ops, each with BLOCKED and with FAIL.
# It is `verify: automated  evidence: unit`, so hand-reasoning satisfies it neither
# way — all four are fixtured. `task` keeps the REAL id in every one: a refusal HAD
# a task, and `task: none` would silently move these onto the conditional branch and
# leave REQ-03 unproven.
case("dev task_verify: n/a + BLOCKED is the honest refusal, accepted",
     "harness-backend-dev", _dev(v="BLOCKED", tv="n/a"), True)
case("dev task_verify: n/a + FAIL is accepted — the same refusal, other verdict",
     "harness-backend-dev", _dev(v="FAIL", tv="n/a"), True)
case("dev-ops task_verify: n/a + BLOCKED is accepted — refusal, not the carve-out",
     "harness-dev-ops", """
VERDICT: BLOCKED
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: n/a
  task: T-01
  task_verify: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
case("dev-ops task_verify: n/a + FAIL is accepted",
     "harness-dev-ops", """
VERDICT: FAIL
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: n/a
  task: T-01
  task_verify: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (f) REGRESSION — the leak check. Neither field belongs to qa or a reviewer, and a
# leak is invisible otherwise: an extra required field only ever makes returns FAIL.
case("qa carries neither new field and is still accepted",
     "harness-qa", """
VERDICT: PASS
DIGEST:
  headline: x
  suite: pass
  failures: 0
  coverage_gaps: []
  matrix_ok: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (g2) REGRESSION by construction — `task` is in no schema at 4091b36 and unknown
# keys are ignored, so this was green then too. It cannot show the field was ADDED;
# (h2) is what can. Kept because an acceptance clause with no rejection partner is
# the vacuous shape this feature exists to remove.
case("dev task: none with task_verify omitted is accepted — D-07's escape hatch",
     "harness-backend-dev", _dev(task="none", tv=None), True)
case("dev-ops task: none with task_verify omitted is accepted",
     "harness-dev-ops", """
VERDICT: PASS
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: n/a
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (h2) DETECTOR PAIR. The first shows `task` is CONSTRAINED, the second that it is
# REQUIRED. A field that is required but unconstrained is precisely the "unknown key
# ignored" shape — measured: a re.Pattern falls through every other branch in silence.
case("dev task: bogus is rejected — the field is constrained",
     "harness-backend-dev", _dev(task="bogus"), False, "task")
case("dev omitting task entirely is rejected — the field is required",
     "harness-backend-dev", _dev(task=None), False, "task")
# (j2-i) DETECTOR — the contradiction gate (D-08c). One error, naming the actionable
# field, rather than two that disagree.
case("dev task: none + task_verify: fail is rejected as a contradiction",
     "harness-backend-dev", _dev(task="none", tv="fail"), False, "task")
# (j2-i, second half) REGRESSION — this is what proves the rejection above is about
# the CONTRADICTION and not about `task: none` refusing every value (D-08b).
case("dev task: none + task_verify: n/a is accepted — the honest DEC-121 spelling",
     "harness-backend-dev", _dev(task="none", tv="n/a"), True)
# (g) DETECTOR — the Q2 fold. Carries `task`/`task_verify` deliberately: without them
# this would be rejected by the missing-field check ALONE and would pass even if the
# fail gate were never written, which is the vacuous shape again.
case("dev suite: fail + PASS is rejected — the fail-value gate",
     "harness-backend-dev", _dev(suite="fail"), False, "suite")
# (h) DETECTOR PAIR — different value TYPES. A string-keyed gate would catch the
# first and silently miss the second, because parse_scalar renders `false` as the
# BOOLEAN False.
case("qa suite: fail + PASS is rejected",
     "harness-qa", """
VERDICT: PASS
DIGEST:
  headline: x
  suite: fail
  failures: 1
  coverage_gaps: []
  matrix_ok: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, "suite")
case("qa matrix_ok: false + PASS is rejected — the BOOLEAN half",
     "harness-qa", """
VERDICT: PASS
DIGEST:
  headline: x
  suite: pass
  failures: 0
  coverage_gaps: []
  matrix_ok: false
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, "matrix_ok")
# (i) THE RESIDUE GUARD. dev-ops `suite: fail` + PASS stays accepted — that is the
# D-03 ruling, NOT a claim it is correct. Recorded in BRIEF `## Verification gaps`.
# This case goes red if a later edit tidies dev-ops into symmetry with dev.
case("dev-ops suite: fail + PASS stays accepted — D-03 ruling, not a claim it is right",
     "harness-dev-ops", """
VERDICT: PASS
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: fail
  task: T-01
  task_verify: pass
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (11)(f) reviewer half — the leak check is not complete with qa alone. Neither new
# field belongs to a reviewer either, and an extra required field only ever makes
# returns FAIL, so nothing else would notice a leak into this schema.
case("a reviewer digest carries neither new field and is still accepted",
     "harness-code-reviewer", """
VERDICT: PASS
DIGEST:
  headline: x
  severity_max: low
  findings: 0
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (11)(i2) — the hint CONTENT, both fields, both polarities. Exit code alone cannot
# see these: before REQ-11, `task_verify`'s hint said "write `none`", which the gate
# then rejects, and `task` would have inherited "write `[]`", which its regex rejects.
# The "no other NULLABLE field omitted" condition is load-bearing — another missing
# NULLABLE field emits the old hint into the same error list and false-reds the
# negative assertion.
case("task_verify's missing-field hint names its real values, not the none wording",
     "harness-backend-dev", _dev(tv=None), False,
     ["task_verify", "pass", "fail", "!genuinely not applicable"])
case("task's missing-field hint names a task id, not the list wording",
     "harness-backend-dev", _dev(task=None), False,
     ["task", "T-NN", "none", "!if there are none"])


# (11)(j2-ii) JOINT HINT FOLLOWABILITY. Not expressible as independent cases: the
# point is that the two hints emitted TOGETHER license two repairs that both
# validate. Two individually-correct hints can still contradict each other — an
# agent following both literally would write `task: none` + `task_verify: pass`,
# which the conditional then rejects. That is REQ-11's own defect class re-created
# by REQ-11's fix, and the re-prompted return is NOT re-validated (validate-digest
# passes through on `stop_hook_active`), so the second attempt would ship unchecked.
def run_joint_hint_case():
    def run(text):
        r = subprocess.run([VALIDATE, "harness-backend-dev"], input=text.strip() + "\n",
                           capture_output=True, text=True)
        return r.returncode, r.stdout

    name = "joint hint followability — both licensed repairs validate"
    bad = []
    rc, out = run(_dev(task=None, tv=None))
    if rc == 0:
        bad.append("omitting BOTH fields should be rejected, was accepted")
    low = out.lower()
    # The hints must LICENSE the two repairs, or the repairs below prove nothing
    # about the hints — they would just be two more acceptance cases.
    if "none" not in low:
        bad.append("task's hint must license `none`")
    if "omit this field entirely" not in low:
        bad.append("task_verify's hint must license omitting it under task: none")
    for label, text in (("task: none + task_verify omitted", _dev(task="none", tv=None)),
                        ("task: T-01 + task_verify: pass", _dev(task="T-01", tv="pass"))):
        rc2, out2 = run(text)
        if rc2 != 0:
            bad.append(f"licensed repair ({label}) must validate, was rejected: "
                       f"{out2.strip().splitlines()[-1] if out2.strip() else 'no output'}")
    if bad:
        print(f"FAIL  {name}")
        for b in bad:
            print(f"        {b}")
        return 1
    print(f"ok    {name}")
    return 0


def main():
    fails = run_cli_cases()
    fails += run_joint_hint_case()
    fails += run_hook_cases()
    fails += run_template_cases()
    print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILING'}.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
