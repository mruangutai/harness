#!/usr/bin/env python3
"""Cases validate-digest.py must get right. Run it; it prints what failed.

WHY A TEST FILE AND NOT A HEREDOC: this validator is now a `SubagentStop` hook that
can BLOCK any agent in any project (DEC-122). A false negative silently accepts a
malformed digest; a false positive wedges a working agent. Both were live here —
the parser rejected SPEC 10.4's own normative template, and separately accepted a
`must_fix` nested inside a member entry as the top-level roll-up. Neither was
noticed because each was only ever exercised by the example that happened to pass.

FEAT-1928: every return is a digest OBJECT `{VERDICT, DIGEST, artifact}`. The fixtures
below are written in YAML notation because it is the readable way to spell a nested
mapping; `obj_of` turns each into the object, and the validator only ever receives that
object — as JSON on the CLI, as `digest_object` in a hook payload, or in-process.

    ./test-validate-digest.py     -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import contextlib, importlib.util, json, subprocess, sys, os, shutil, tempfile, time
import concurrent.futures
import copy
import re
import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)
from isolated_bin import isolated_bin
from check_domain_support import make_linked_worktree
# Overridable so the pre-fix binary can be run through the SAME suite to prove
# each new regression case actually fails against the old code (task 22).
VALIDATE = os.environ.get("VALIDATE_DIGEST_BIN") or os.path.join(HERE, "validate-digest.py")


def obj_of(text):
    """The digest object a fixture spells in YAML notation. The validator never parses this
    text; it receives the mapping."""
    return yaml.safe_load(text)


# FEAT-1928 operator ruling: every DIGEST field is required and a field that does not apply
# is spelled `none` (scalar) or `[]` (list). These are the fields that ruling made required;
# a fixture here names only the fields its case is about, so each one it leaves out is filled
# with that not-applicable spelling. A case that pins the omission itself passes
# `complete=False` and gets the object exactly as written.
_LEAD_NOT_APPLICABLE = {"adequacy_notes": [], "sc_status": [], "needs_approval": "none",
                        "severity_max": "none", "matrix_ok": "none", "coverage_gaps": [],
                        "findings": [], "readers": []}
_DEV_NOT_APPLICABLE = {"task_verify": "n/a"}
_NOT_APPLICABLE = {
    "harness-eng-lead": {**_LEAD_NOT_APPLICABLE, "amendments": []},
    "harness-product-lead": _LEAD_NOT_APPLICABLE,
    "harness-validator-lead": _LEAD_NOT_APPLICABLE,
    "harness-backend-dev": _DEV_NOT_APPLICABLE, "harness-frontend-dev": _DEV_NOT_APPLICABLE,
    "harness-ai-dev": _DEV_NOT_APPLICABLE, "harness-data-engineer": _DEV_NOT_APPLICABLE,
    "harness-dev-ops": {**_DEV_NOT_APPLICABLE, "test_kinds_written": []},
    "harness-qa": {"kinds": [], "sc_evidence": []},
    "harness-code-reviewer": {"spec_violations": [], "human_commits_in_scope": [],
                              "grade_2_reasons": []},
    "harness-security-reviewer": {"in_scope": "none", "scope_reason": "none",
                                  "threat_model": []},
    "harness-ui-reviewer": {"mode": "none", "in_scope": "none", "states_unspecified": [],
                            "contract_violations": [], "a11y": []},
    "harness-visual-designer": {"needs_prototype": "none", "why": "none", "prototype": "none"},
    "harness-documentor": {"stale_found": []},
    "harness-orchestrator": {"judgement": "none"},
}
_PERSONA_ALIASES = {"lead": "harness-eng-lead", "dev": "harness-backend-dev",
                    "reviewer": "harness-code-reviewer"}


def fixture(persona, text, complete=True):
    """`obj_of(text)` with every ruling-required field it omits spelled not-applicable."""
    obj = obj_of(text) if isinstance(text, str) else copy.deepcopy(text)
    digest = obj.get("DIGEST") if isinstance(obj, dict) else None
    if complete and isinstance(digest, dict):
        filler = _NOT_APPLICABLE.get(_PERSONA_ALIASES.get(persona, persona), {})
        for field, value in filler.items():
            digest.setdefault(field, list(value) if isinstance(value, list) else value)
    return obj
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# Vendored fixture data for check_prior_validator (Q11 cycle-27): the pre-FEAT-43 revision
# of validate-digest.py/harness_yaml.py, committed inert so the control needs no `git show`
# and no repository history to be hermetic in a shallow CI checkout.
FIXTURE_DIR = os.path.join(TESTS_DIR, "fixtures")
PRE_FEATURE_REVISION = "df63193f7ec9798d9660904e0e4e7c78d52358f5"


# (name, persona, digest text, expect_ok, must_mention)
CASES = []
# (name, payload carrying `digest_object` (any JSON value, as a yield sends it),
#  expect_exit, must_mention_on_stderr)
HOOK_CASES = []


def case(name, persona, text, ok, mentions=None, complete=True):
    CASES.append((name, persona, fixture(persona, text, complete), ok, mentions))


def hook_case(name, agent_type, text, expect_exit, mentions=None, complete=True, **overrides):
    payload = {"agent_type": agent_type,
               "digest_object": fixture(agent_type, text, complete) if isinstance(text, str)
               else text}
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
    - { step: qa, persona: qa, verdict: FAIL, headline: "refresh path untested", files_touched: [] }
  must_fix: ["refresh path untested"]
  branch: feat/auth
  files_touched: [src/auth.ts, test/auth.spec.ts]
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
  adequacy_notes: []
artifact: .harness/features/FEAT-01/runs/r1/digest.md
"""
case("lead, block-style members", "harness-eng-lead", LEAD_BLOCK, True)


# BUG-1716 T-02 (SC-01/SC-06, D-02): `amendments` — the eng-lead's optional list of in-build
# corrections to a signed task's HOW. Each entry is exactly {task, field, was, now, reason};
# task is T-NN, field is intent|files|verify, reason ≤240 one-liner, and was/now are strings
# for intent/verify, lists of legal anchored plan file entries for files. Declared for
# harness-eng-lead only: a product or validator lead amends nothing.
def _amended(entries, persona="harness-eng-lead"):
    return LEAD_BLOCK.replace("  adequacy_notes: []\n", f"  amendments: {entries}\n  adequacy_notes: []\n") \
        if isinstance(entries, str) and entries.startswith("[") \
        else LEAD_BLOCK.replace("  adequacy_notes: []\n", f"  amendments:\n{entries}  adequacy_notes: []\n")


# The three BUG-285 T-03 recommendations, as the amendments they would have been (SC-06).
BUG285_AMENDMENTS = """\
    - { task: T-03, field: intent, was: "Add a second text accessor with a compatibility exemption", now: "Keep the keyword-only text source; no second accessor and no exemption", reason: "the exemption would let a caller bypass the accessor the task exists to make canonical" }
    - { task: T-03, field: verify, was: "parse_gh_json accepts objects only", now: "parse_gh_json accepts any JSON value", reason: "gh api returns arrays for list endpoints; an object-only reader refuses real output" }
    - { task: T-03, field: files, was: [.claude/skills/harness/bin/check-domain.py#manifest_domains], now: [{ path: .claude/skills/harness/bin/check-domain.py, quote: "def manifest_domains(agent=None)" }], reason: "the symbol anchor moved to a content anchor once the signature gained agent=None" }
"""
case("amendments: the three BUG-285 recommendations are accepted eng-lead amendments",
     "harness-eng-lead", _amended(BUG285_AMENDMENTS), True)
case("amendments: absent is refused — every field is required, `[]` says none",
     "harness-eng-lead", LEAD_BLOCK, False, "missing 'amendments'", complete=False)
case("amendments: empty list is legal", "harness-eng-lead", _amended("[]"), True)
case("amendments: inline mappings for all three fields",
     "harness-eng-lead", _amended(
         '[{ task: T-01, field: intent, was: "a", now: "b", reason: "r" }, '
         '{ task: T-01, field: verify, was: "python3 x.py", now: "python3 y.py", reason: "r" }, '
         '{ task: T-02, field: files, was: [a.py], now: [a.py#f, { path: b.py, quote: "q" }], reason: "r" }]'),
     True)
case("amendments: block mapping entry", "harness-eng-lead", _amended(
    "    - task: T-04\n      field: intent\n      was: old text\n      now: new text\n      reason: shorter\n"), True)
case("amendments: unknown key is refused naming index and key", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "r", by: me }]'), False, "by")
case("amendments: missing key is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: "a", reason: "r" }]'), False, "now")
case("amendments: not a list is refused", "harness-eng-lead",
     LEAD_BLOCK.replace("  adequacy_notes: []\n", "  amendments: none\n  adequacy_notes: []\n"),
     False, "amendments")
case("amendments: entry that is not a mapping is refused", "harness-eng-lead",
     _amended("[T-01.intent]"), False, "amendments[0]")
case("amendments: SC id as task is refused", "harness-eng-lead",
     _amended('[{ task: SC-01, field: intent, was: "a", now: "b", reason: "r" }]'), False, "task")
case("amendments: decision id as task is refused", "harness-eng-lead",
     _amended('[{ task: D-01, field: intent, was: "a", now: "b", reason: "r" }]'), False, "task")
case("amendments: field outside intent/files/verify is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: title, was: "a", now: "b", reason: "r" }]'), False, "field")
case("amendments: empty reason is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "" }]'), False, "reason")
case("amendments: reason over 240 is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "' + "x" * 241 + '" }]'), False, "reason")
case("amendments: intent with a list value is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: [a], now: "b", reason: "r" }]'), False, "was")
case("amendments: files with a string value is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: files, was: [a.py], now: "b.py", reason: "r" }]'), False, "now")
case("amendments: files with a line-number anchor is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: files, was: [a.py], now: [a.py:12], reason: "r" }]'), False, "now")
case("amendments: files with a bad mapping entry is refused", "harness-eng-lead",
     _amended('[{ task: T-01, field: files, was: [a.py], now: [{ path: a.py, line: 3 }], reason: "r" }]'), False, "now")
case("amendments: second entry's fault is reported at its index", "harness-eng-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "r" }, '
              '{ task: T-02, field: intent, was: "a", now: "b" }]'), False, "amendments[1]")
case("amendments: a product lead may not carry the field", "harness-product-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "r" }]'), False, "amendments")
case("amendments: a validator lead may not carry the field", "harness-validator-lead",
     _amended('[{ task: T-01, field: intent, was: "a", now: "b", reason: "r" }]'), False, "amendments")

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
  members: [{ step: s1, persona: code-reviewer, verdict: PASS, headline: "s1 ran", files_touched: [] }, { step: s2, persona: qa, verdict: PASS, headline: "s2 ran", files_touched: [] }]
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

# The object counterpart of SPEC 10.4's old one-line packing (`team: build  steps_run: 3
# cycles_used: 0`, which lost two fields): a return missing them is refused, naming both.
case("a lead return missing steps_run and cycles_used is refused, naming both", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: done
  team: build
  members: []
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: x.md
""", False, ["missing 'steps_run'", "missing 'cycles_used'"])

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

# #1895: a run the MAIN SESSION wrote directly (DEC-174, `run-start --agent main-session`) is closed
# through the composed `close-run`, whose digest stage validates against the run's recorded agent.
# `main-session` is the dev contract -- the main session wrote the diff and owns the same
# task / task_verify / suite receipt -- so it validates as `dev`, gate fields included.
case("main-session (DEC-174 direct build) validates as dev", "main-session", """
VERDICT: PASS
DIGEST:
  headline: the eighteen scoped files carry zero broad catches
  tests_added: 60
  suite: pass
  blocked_on: none
  task: T-03
  task_verify: pass
  files_touched: [.claude/skills/harness/bin/board-station.py]
  open_questions: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-64-x/notes/red-first-receipts.md
""", True)

case("main-session with task_verify fail and VERDICT PASS is refused like any dev", "main-session", """
VERDICT: PASS
DIGEST:
  headline: built
  tests_added: 1
  suite: pass
  blocked_on: none
  task: T-01
  task_verify: fail
  files_touched: [x.py]
  open_questions: []
  expertise_update: []
artifact: notes/x.md
""", False, mentions=["task_verify"])

case("drifted key spelling is caught", "harness-code-reviewer", """
VERDICT: FAIL
DIGEST:
  headline: two blocking findings
  severity_max: high
  findings: [{ kind: substance, scope: none, severity: high, reader: code-reviewer, summary: "fail-open branch in auth", why: "the reader states its reason" }, { kind: substance, scope: none, severity: high, reader: code-reviewer, summary: "unhandled rejection", why: "the reader states its reason" }]
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
  findings: [{ kind: substance, scope: none, severity: med, reader: code-reviewer, summary: "off-by-one", why: "the reader states its reason" }]
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
""", False, "open_questions: 0 is not of type 'array'")

# A list field is a list: null (a bare `key:` in YAML) is not the empty list `[]` that
# asserts "none" — the object contract has one spelling for nothing, and it is explicit.
case("a null list field is refused — null is not an empty list", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: clean run
  team: build
  steps_run: 1
  cycles_used: 0
  members:
    - { step: build, persona: backend-dev, verdict: PASS, headline: "build ran", files_touched: [] }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: null
  expertise_update: []
  sc_status: []
artifact: x.md
""", False, "escalations: None is not of type 'array'")

case("no VERDICT at all", "harness-qa", """
DIGEST:
  headline: whatever
artifact: x.md
""", False, "missing 'VERDICT'")


# The roll-up is the only part of collation that is arithmetic. It was prose with a
# validator next to it that could check it and didn't — the shape of DEC-110/119.
case("PASS over a failing member is rejected", "harness-eng-lead", """
VERDICT: PASS
DIGEST:
  headline: two of three passed
  team: build
  steps_run: 3
  cycles_used: 0
  members:
    - { step: s1, persona: backend-dev, verdict: PASS, headline: "s1 ran", files_touched: [] }
    - { step: s2, persona: qa, verdict: FAIL, headline: "s2 ran", files_touched: [] }
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
    - { step: s1, persona: code-reviewer, verdict: FAIL, headline: "s1 ran", files_touched: [] }
    - { step: s2, persona: security-reviewer, verdict: ESCALATE, headline: "s2 ran", files_touched: [] }
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
    - { step: s1, persona: backend-dev, verdict: PASS, headline: "s1 ran", files_touched: [] }
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

# A team step that never ran has no verdict to roll up. The plan team's contract
# records the absence explicitly instead of manufacturing ESCALATE (which would
# contaminate worst-wins) or PASS (which would claim work happened).
case("a skipped member is explicit and excluded from worst-wins", "harness-product-lead", """
VERDICT: PASS
DIGEST:
  headline: scope review passed; optional advisor was unavailable
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
    - { step: scope, persona: code-reviewer, verdict: PASS, headline: "scope ran", files_touched: [] }
    - { step: should-not-exist, persona: fable-advisor, status: skipped, reason: persona unavailable }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", True)

case("all skipped members cannot support a lead verdict", "harness-product-lead", """
VERDICT: PASS
DIGEST:
  headline: nobody ran
  team: plan
  steps_run: 2
  cycles_used: 0
  members:
    - { step: should-not-exist, persona: fable-advisor, status: skipped, reason: persona unavailable }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "no member actually ran")

case("mandatory member cannot be laundered as skipped", "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: qa was omitted
  team: validate
  steps_run: 2
  cycles_used: 0
  members:
    - { step: code, persona: code-reviewer, verdict: PASS, headline: "code ran", files_touched: [] }
    - { step: qa, persona: qa, status: skipped, reason: environment unavailable }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "only the optional fable-advisor")


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
    - { step: qa, persona: qa, headline: "verdict: PASS on retry", verdict: FAIL, files_touched: [] }
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
# earlier, `verdict: PASS` first and never saw entry 3's real `verdict: FAIL`. As an
# object the three members are three mappings; the roll-up must still see entry 3's FAIL.
hook_case("F1.3 unquoted apostrophe must not fuse list entries",
          "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: panel ran
  team: review
  steps_run: 3
  cycles_used: 0
  members: [{ step: s1, persona: code-reviewer, verdict: PASS, headline: "s1 ran", files_touched: [] }, { step: s2, persona: qa, headline: didn't stop, verdict: PASS, files_touched: [] }, { step: s3, persona: security-reviewer, verdict: FAIL, headline: "s3 ran", files_touched: [] }]
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
  findings: [{ kind: form, scope: none, severity: low, reader: code-reviewer, summary: "a", why: "the reader states its reason" }, { kind: substance, scope: none, severity: med, reader: code-reviewer, summary: "b", why: "the reader states its reason" }]
  must_fix: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/review-code.md
""", 2, "must be a single value")

QA_REAL_FAIL_MISSING_MATRIX = """
VERDICT: FAIL
DIGEST:
  headline: refresh path fails under load
  suite: fail
  failures: 2
  coverage_gaps: ["refresh path"]
  fail_first: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/notes/qa.md
"""
QA_REAL_FAIL = QA_REAL_FAIL_MISSING_MATRIX.replace("  fail_first: []\n",
                                                   "  matrix_ok: false\n  fail_first: []\n")

# --- FEAT-1928 SC-02: the yield's `data` IS the digest, or there is none ---------------
# D-01 (#1056) told absent, null and blank TEXT apart so the platform's gap was not mistaken
# for the persona's violation. Under the object contract the host hands over `data` as the
# agent yielded it, so every one of these is the agent's to fix: the hook blocks (exit 2)
# with the one instruction, and nothing is read from anywhere else.
OBJECT_INSTRUCTION = "return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}})"

HOOK_CASES.append(("object [hook]: absent data is refused with the object instruction",
                   {"agent_type": "harness-qa"}, 2, (OBJECT_INSTRUCTION, "absent")))
hook_case("object [hook]: null data is refused with the object instruction",
          "harness-qa", None, 2, mentions=(OBJECT_INSTRUCTION, "NoneType"))
HOOK_CASES.append(("object [hook]: string data carrying digest TEXT is refused, never parsed",
                   {"agent_type": "harness-qa", "digest_object": QA_REAL_FAIL}, 2,
                   (OBJECT_INSTRUCTION, "a str")))
HOOK_CASES.append(("object [hook]: blank string data is refused",
                   {"agent_type": "harness-qa", "digest_object": "   \n"}, 2, OBJECT_INSTRUCTION))
HOOK_CASES.append(("object [hook]: a list is refused",
                   {"agent_type": "harness-qa", "digest_object": [fixture("harness-qa", QA_REAL_FAIL)]}, 2,
                   (OBJECT_INSTRUCTION, "a list")))

# --- The deliberate pass-throughs, each asserted at exit 0 — and each only for a mapping ---

hook_case("pass-through: non-harness agent_type is not governed",
          "Explore", "VERDICT: PASS\nDIGEST:\nartifact: x.md\n", 0)
HOOK_CASES.append(("pass-through: non-harness agent_type is not governed, whatever data it yields",
                   {"agent_type": "Explore", "digest_object": "not a digest"}, 0, None))
hook_case("pass-through: stop_hook_active passes a mapping unvalidated",
          "harness-qa", QA_REAL_FAIL_MISSING_MATRIX, 0, stop_hook_active=True)
HOOK_CASES.append(("stop_hook_active does not pass string data",
                   {"agent_type": "harness-qa", "digest_object": "done", "stop_hook_active": True},
                   2, OBJECT_INSTRUCTION))
# F6: an absent agent_type key is LOUD on stderr — distinguishable from a present
# non-harness value (silent, above) — and still refuses what cannot be a digest.
HOOK_CASES.append(("F6 missing agent_type key is loud, not silent",
                   {"digest_object": fixture("harness-qa", QA_REAL_FAIL)}, 0, "agent_type"))
HOOK_CASES.append(("F6 missing agent_type with string data is refused",
                   {"digest_object": "whatever"}, 2, OBJECT_INSTRUCTION))

# --- SC-07 (DEC-156, DEC-208): the lead's durable digest.md ends with its validated object ---
# The lead writes the human assessment; the validator appends the fenced YAML record. Only
# the file-resolution half is a HOOK_CASES row; the byte-level append rules are
# run_lead_append_cases, which reads the file back after each fire.
# Root and checkout must differ here. `_dec156_case` makes them coincide, so the old
# owner-root join and the corrected feature-checkout join name the same file and cannot
# distinguish the worktree-resolution defect.
def _linked_worktree_fixture(root, wt_id):
    worktree = os.path.join(root, ".claude", "worktrees", wt_id)
    make_linked_worktree(root, worktree, wt_id)
    os.makedirs(os.path.join(worktree, ".harness"), exist_ok=True)
    return worktree


def _write_optional_digest(worktree, rel, file_content):
    os.makedirs(os.path.dirname(os.path.join(worktree, rel)), exist_ok=True)
    if file_content is None:
        return
    with open(os.path.join(worktree, rel), "w", encoding="utf-8") as digest:
        digest.write(file_content)




def _dec156_worktree_case(name, file_content, expect_exit, mentions=None, feature=True):
    root = os.path.realpath(tempfile.mkdtemp(prefix="vd-dec156-worktree-"))
    worktree = _linked_worktree_fixture(root, HOOK_IDENTITY["harness_feature"])
    _append_registration(worktree)
    shutil.copytree(os.path.join(worktree, ".harness"), os.path.join(root, ".harness"),
                    ignore=shutil.ignore_patterns("features", "inflight.json", "inflight.json.lock"))
    rel = APPEND_REL
    _write_optional_digest(worktree, rel, file_content)
    payload = {"agent_type": "harness-eng-lead", "digest_object": _append_lead_object(),
               "_root": root, **HOOK_IDENTITY, "harness_parent_agent_id": "Test.Parent",
               "harness_digest_binding": _append_binding(worktree)}
    if not feature:
        payload["harness_feature"] = None
    HOOK_CASES.append((name, payload, expect_exit, mentions))
    return root, worktree, rel, payload




# --- Fold-ins (BUILD task 22) ---

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
""", False, "missing 'headline'")

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
    - { step: s1, persona: backend-dev, verdict: PASS, headline: "s1 ran", files_touched: [] }
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "team: 7 is not of type 'string'")

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
    - { step: s1, persona: backend-dev, verdict: PASS, headline: "s1 ran", files_touched: [] }
  must_fix: []
  branch:
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, "branch: None is not of type 'string'")

# F13 was a text-parser defect: a NESTED `open_questions: 0` inside a member entry tripped
# the top-level count check. As an object the member is its own mapping, and the FEAT-1928
# ruling closes it to {step, persona, verdict, headline, files_touched}: a member carrying
# any other key is refused at that member, and the top-level list is never confused with it.
case("a member entry carrying open_questions is refused at that member", "harness-eng-lead", """
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
      headline: "s1 ran"
      files_touched: []
      open_questions: 0
  must_fix: []
  branch: none
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
artifact: r/digest.md
""", False, ["members[0]", "!open_questions is a COUNT"])

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
  runs: [{ id: r1, squad: build, verdict: PASS }, { id: r2, squad: validate, verdict: PASS }]
  cycles_used: 2
  briefing: .harness/notes/ship-review-FEAT-01-r2.md
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/features/FEAT-01/feature.json
""", True)

case("orchestrator briefing is NULLABLE — `none` when nothing was written", "harness-orchestrator", """
VERDICT: PASS
DIGEST:
  headline: mid-flight, no briefing yet
  feature: FEAT-01
  status: in_progress
  runs: [{ id: r1, squad: build, verdict: PASS }]
  cycles_used: 1
  # THE NEW CONTRACT (SC-04): the money field this schema used to require is simply
  # absent. This case is the DETECTOR — at ae2443d it was REJECTED for a missing
  # required field, so it can only go green once the schema entry is gone. Named
  # without its literal spelling because SC-01's sweep asserts that spelling appears
  # in no file outside the four it enumerates.
  briefing: none
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/features/FEAT-01/feature.json
""", True)

# FEAT-1714 T-01 (SC-01): `status: rejected` is a terminal return an orchestrator makes at
# first-run intake — "this ticket is wrong, here is the right one" — and it carries exactly
# one `judgement:` mapping {kind: reject, superseded_by: <positive int | none>, reason: <one
# line, ≤240>} with `cycles_used: 0`. BUG-285 spent seven cycles amending a ticket its own
# comments said was superseded, because no such return existed (#1684, #1714).
def _reject_digest(judgement_yaml, cycles=0, status="rejected"):
    return f"""
VERDICT: PASS
DIGEST:
  headline: superseded by the canonical-reader ticket
  feature: BUG-285-yaml-loader-pin
  status: {status}
  runs: [{{ id: plan-product, squad: product, verdict: PASS }}]
  cycles_used: {cycles}
  briefing: none
{judgement_yaml}  files_touched: []
  open_questions: []
  expertise_update: []
artifact: .harness/features/BUG-285-yaml-loader-pin/feature.json
"""


case("rejected: reject judgement with a superseding issue is accepted", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"#285 superseded by #1594 on 2026-09-10\" }\n"),
     True)
case("rejected: superseded_by none (should not be planned) is accepted", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: none, reason: \"already fixed on main\" }\n"),
     True)
case("rejected: judgement none is refused, naming the mapping a rejection carries",
     "harness-orchestrator", _reject_digest("  judgement: none\n"), False,
     ["judgement='none' on status: rejected", "a rejection carries one mapping"])
case("rejected: kind other than reject is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: succession, superseded_by: 1594, reason: \"x\" }\n"),
     False, "kind")
case("rejected: superseded_by zero is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 0, reason: \"x\" }\n"),
     False, "superseded_by")
case("rejected: superseded_by negative is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: -3, reason: \"x\" }\n"),
     False, "superseded_by")
case("rejected: superseded_by boolean is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: true, reason: \"x\" }\n"),
     False, "superseded_by")
case("rejected: empty reason is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"\" }\n"),
     False, "reason")
case("rejected: reason over 240 characters is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"" + "x" * 241 + "\" }\n"),
     False, "reason")
case("rejected: multiline reason is refused", "harness-orchestrator",
     _reject_digest("  judgement:\n    kind: reject\n    superseded_by: 1594\n    reason: |\n      one\n      two\n"),
     False, "reason")
case("rejected: a missing key is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, reason: \"x\" }\n"), False, "superseded_by")
case("rejected: an extra key is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"x\", by: me }\n"),
     False, "by")
case("rejected: cycles_used must be integer zero", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"x\" }\n", cycles=1),
     False, ["cycles_used=1 on status: rejected", "write 0"])
case("a judgement mapping on any other status is refused", "harness-orchestrator",
     _reject_digest("  judgement: { kind: reject, superseded_by: 1594, reason: \"x\" }\n", status="shipped"),
     False, "judgement is `none` unless status is rejected")


# =====================================================================
# FEAT-1928: the return IS the object. There is no text to echo a template into and no
# "last block" to pick, so the FEAT-02 echo-shadow cases became these: a wrapped object,
# a JSON string and a list are not a digest, and a real object missing a field is refused
# for that field in both modes.
# =====================================================================

case("object: a real FAIL object validates", "harness-qa", QA_REAL_FAIL, True)
case("object: a real object missing matrix_ok is refused for that field",
     "harness-qa", QA_REAL_FAIL_MISSING_MATRIX, False, "missing 'matrix_ok'")
CASES.append(("object: a wrapped {data: ...} object is not a digest", "harness-qa",
              {"data": fixture("harness-qa", QA_REAL_FAIL)}, False,
              ["missing 'VERDICT'", "'data' was unexpected"]))
CASES.append(("object: a list is not a digest", "harness-qa", [fixture("harness-qa", QA_REAL_FAIL)], False,
              "neither one JSON digest object"))
CASES.append(("object: a JSON string is not a digest", "harness-qa", "VERDICT: FAIL", False,
              "neither one JSON digest object"))
hook_case("object [hook]: missing matrix_ok is exit 2, naming the field",
          "harness-qa", QA_REAL_FAIL_MISSING_MATRIX, 2, "missing 'matrix_ok'")
HOOK_CASES.append(("object [hook]: a wrapped {data: ...} object is exit 2",
                   {"agent_type": "harness-qa", "digest_object": {"data": fixture("harness-qa", QA_REAL_FAIL)}},
                   2, "missing 'VERDICT'"))


def _run_cli_case(cli_case):
    _name, persona, obj, _want_ok, _mentions = cli_case
    return subprocess.run([VALIDATE, persona], input=json.dumps(obj),
                          capture_output=True, text=True)


def run_cli_cases():
    fails = 0
    # Each case is one independent, read-only CLI spawn (_cli_never_writes): they spawn
    # concurrently and are judged and printed in CASES order, so the output is unchanged.
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
        runs = list(pool.map(_run_cli_case, CASES))
    for (name, persona, obj, want_ok, mentions), r in zip(CASES, runs):
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


# ---------------------------------------------------------------------------
# T-09's NINE MANDATED CASES (plan.yaml:1331-1362). MF-2: these were mandated by
# the approved intent and never written, and the panel proved the gap by
# neutering live_children and getting a green suite. Each drives the hook as a
# SUBPROCESS with its own throwaway checkout so no case can see another.
# ---------------------------------------------------------------------------

# BUG-1898: OMP is the only host (DEC-233) and its adapter sends every governed return with
# the run's exact feature and runtime id; the hook refuses a non-BLOCKED return without them.
# Cases about digest SHAPE carry this neutral identity (no worktree, no claim of that id);
# a case's own keys win, and a case about a missing value passes it as None.
HOOK_IDENTITY = {"harness_feature": "FEAT-01-hook-case", "harness_agent_id": "Test.Run"}


def _governed(payload):
    return {**HOOK_IDENTITY, **payload}


T09 = []


def t09(name, ok, detail=""):
    T09.append((name, ok, detail))


def _reg_module():
    import importlib.util
    sp = importlib.util.spec_from_file_location(
        "t09_ir", os.path.join(os.path.dirname(os.path.realpath(VALIDATE)),
                               "inflight_registry.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _t09_root():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"), exist_ok=True)
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("schema_version: 1\nteams: []\n")
    return d


def _t09_fire(root, agent, text, hook=None, governed=True, **extra):
    """Fire the hook as a governed return (HOOK_IDENTITY merged in), or with `governed`
    False, exactly the identity passed and nothing else."""
    payload = {"agent_type": agent, "digest_object": fixture(agent, text), "cwd": root}
    payload.update(extra)
    return subprocess.run([hook or VALIDATE, "--hook"],
                          input=json.dumps(_governed(payload) if governed else payload),
                          capture_output=True, text=True,
                          # BOTH NAMES, ONE VALUE (FEAT-42 T-17). The hook resolves through
                          # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR
                          # and no other name, and payload cwd is no longer a root input.
                          env=dict(os.environ, 
                                   HARNESS_PROJECT_DIR=root))


PM_OK = """
VERDICT: PASS
DIGEST:
  headline: scoped the surface and wrote the plan
  feasibility: clear
  surface: S
  recommend: proceed
  risk: low
  tasks: 3
  decisions: 1
  needs_approval: false
  flags: []
  open_questions: []
  files_touched: []
  expertise_update: []
  sc_status: []
artifact: .harness/features/FEAT-01/plan.yaml
"""

CHILD_MARK = "BLOCKED - returned with children in flight"
T09_FEATURE = "FEAT-09-exact-claims"


def run_t09():
    reg = _reg_module()

    def claims(root, agent):
        p = os.path.join(root, reg.REGISTRY_REL)
        if not os.path.exists(p):
            return []
        with open(p) as fh:
            data = json.load(fh) or {}
        return [claim for claim in data.get("claims", []) if claim.get("agent") == agent]

    def run(root, agent, agent_id, parent_id, dispatcher):
        """One live claim bound to OMP runtime id `agent_id` under `parent_id` (BUG-1898:
        the hook selects claims by exact feature and runtime id, never by persona)."""
        entry = reg.claim_with_receipt(root, agent, dispatcher, root, feature=T09_FEATURE)
        reg.attach_runtime_identity(root, agent, T09_FEATURE, agent_id=agent_id,
                                    claim_id=entry["claim_id"], parent_agent_id=parent_id)

    def fire(root, agent, agent_id, text, **extra):
        return _t09_fire(root, agent, text, harness_feature=T09_FEATURE,
                         harness_agent_id=agent_id, **extra)

    # 1. a valid pm return RELEASES its claim
    root = _t09_root()
    run(root, "harness-pm", "Lead.Pm", "Lead", "harness-product-lead")
    r = fire(root, "harness-pm", "Lead.Pm", PM_OK)
    t09("1: a valid pm return exits 0", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("1: and its claim is GONE from the registry", not claims(root, "harness-pm"),
        repr(claims(root, "harness-pm")))

    # A retryable contract rejection keeps this same live job's claim.
    root = _t09_root()
    run(root, "harness-pm", "Lead.Pm", "Lead", "harness-product-lead")
    r = fire(root, "harness-pm", "Lead.Pm", "VERDICT: PASS\nDIGEST:\n  headline: x\n")
    t09("2: an invalid digest still exits 2", r.returncode == 2, f"exit {r.returncode}")
    t09("2: the rejected job retains its claim for correction",
        len(claims(root, "harness-pm")) == 1, repr(claims(root, "harness-pm")))
    corrected = fire(root, "harness-pm", "Lead.Pm", PM_OK)
    t09("2: correction completes the same job and releases its claim",
        corrected.returncode == 0 and not claims(root, "harness-pm"),
        corrected.stderr + repr(claims(root, "harness-pm")))

    # 3. stop_hook_active short-circuits and does not raise, with a claim present
    root = _t09_root()
    run(root, "harness-pm", "Lead.Pm", "Lead", "harness-product-lead")
    r = fire(root, "harness-pm", "Lead.Pm", PM_OK, stop_hook_active=True)
    t09("3: stop_hook_active exits 0 with a claim present", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("3: and prints no traceback", "Traceback" not in r.stderr, r.stderr[:200])

    # 4. a persona releases its OWN claim and leaves an unrelated one alone. BOTH halves.
    root = _t09_root()
    run(root, "harness-documentor", "Lead.Doc", "Lead", "harness-product-lead")
    run(root, "harness-pm", "Lead.Pm", "Lead", "harness-product-lead")
    r = fire(root, "harness-documentor", "Lead.Doc", _t04_base_digest("harness-documentor"))
    t09("4: the returning persona's own claim is released",
        not claims(root, "harness-documentor"), repr(claims(root, "harness-documentor")))
    t09("4: and an UNRELATED harness-pm claim is untouched",
        len(claims(root, "harness-pm")) == 1, repr(claims(root, "harness-pm")))

    # 5. THE LIBRARY MISSING. Neither the release nor the children check may break validation.
    root = _t09_root()
    mbin = os.path.join(root, "bin")
    shutil.copytree(os.path.dirname(os.path.realpath(VALIDATE)), mbin)
    os.remove(os.path.join(mbin, "inflight_registry.py"))
    r = _t09_fire(root, "harness-pm", PM_OK, hook=os.path.join(mbin, "validate-digest.py"))
    t09("5: a valid digest still exits 0 with inflight_registry absent", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("5: and stderr NAMES the missing module", "inflight_registry" in r.stderr,
        r.stderr.strip()[:200])

    # 6. THE D-09 REFUSAL. Two live children of this exact lead run. Assert the exit, both
    #    children by name, the issue, AND that the lead keeps its own claim (DEC-233: a
    #    parent with a live child is still their only owner; BUG-1898 T-03).
    root = _t09_root()
    run(root, "harness-eng-lead", "Orch.Lead", "Orch", "harness-orchestrator")
    run(root, "harness-backend-dev", "Orch.Lead.Dev", "Orch.Lead", "harness-eng-lead")
    run(root, "harness-dev-ops", "Orch.Lead.Ops", "Orch.Lead", "harness-eng-lead")
    r = fire(root, "harness-eng-lead", "Orch.Lead", LEAD_BLOCK)
    t09("6: a lead returning with children in flight exits 2", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:240]!r}")
    t09("6: stderr carries the children-in-flight refusal", CHILD_MARK in r.stderr,
        r.stderr.strip()[:240])
    t09("6: stderr names BOTH children",
        "harness-backend-dev" in r.stderr and "harness-dev-ops" in r.stderr,
        r.stderr.strip()[:240])
    t09("6: stderr cites the issue", "#551" in r.stderr, r.stderr.strip()[:240])
    t09("6: the lead KEEPS its own claim while its children are live",
        len(claims(root, "harness-eng-lead")) == 1, repr(claims(root, "harness-eng-lead")))

    # 7. THE ALLOW HALF, asserting the ABSENCE of the marker so a refuse-every-lead build fails.
    #    A same-persona sibling lead's child is not this lead's child.
    root = _t09_root()
    run(root, "harness-eng-lead", "Orch.Lead", "Orch", "harness-orchestrator")
    run(root, "harness-eng-lead", "Orch.Lead-2", "Orch", "harness-orchestrator")
    run(root, "harness-backend-dev", "Orch.Lead-2.Dev", "Orch.Lead-2", "harness-eng-lead")
    r = fire(root, "harness-eng-lead", "Orch.Lead", LEAD_BLOCK)
    t09("7: a lead with NO children carries no children marker", CHILD_MARK not in r.stderr,
        r.stderr.strip()[:240])

    # 8. A MEMBER IS NEVER SUBJECT TO IT -- only a lead or the orchestrator dispatches.
    root = _t09_root()
    run(root, "harness-pm", "Lead.Pm", "Lead", "harness-product-lead")
    run(root, "harness-qa", "Lead.Pm.Qa", "Lead.Pm", "harness-pm")
    r = fire(root, "harness-pm", "Lead.Pm", PM_OK)
    t09("8: a member with a claim naming it as parent still exits 0", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("8: and no children marker", CHILD_MARK not in r.stderr, r.stderr.strip()[:200])

    # 9. THE ONE-SHOT BOUND, ASSERTED RATHER THAN HIDDEN. This records D-09's residual: a
    #    second refusal here would be the infinite stop loop the pass-through prevents.
    #    DO NOT "fix" this case.
    root = _t09_root()
    run(root, "harness-eng-lead", "Orch.Lead", "Orch", "harness-orchestrator")
    run(root, "harness-backend-dev", "Orch.Lead.Dev", "Orch.Lead", "harness-eng-lead")
    r = fire(root, "harness-eng-lead", "Orch.Lead", LEAD_BLOCK, stop_hook_active=True)
    t09("9: stop_hook_active exits 0 WITH children still on disk (D-09's residual)",
        r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("9: and the child claim is still there, so the bound is real",
        len(claims(root, "harness-backend-dev")) == 1,
        repr(claims(root, "harness-backend-dev")))

    # 10. A live child refuses the parent's return, and the refusal names the precise
    #     release command for that ONE claim — its runtime id — never a persona selector
    #     (which would match every same-persona run) and never release-all, which wipes
    #     every claim of every agent (following the old advice on 2026-08-26 would have
    #     destroyed a live one).
    root = _t09_root()
    run(root, "harness-eng-lead", "Orch.Lead", "Orch", "harness-orchestrator")
    run(root, "harness-backend-dev", "Orch.Lead.Dev", "Orch.Lead", "harness-eng-lead")
    r = fire(root, "harness-eng-lead", "Orch.Lead", LEAD_BLOCK)
    t09("10: a live child refuses the parent's return",
        r.returncode == 2 and CHILD_MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:240]!r}")
    t09("10: and the refusal names the exact release command for that child",
        "--agent-id Orch.Lead.Dev" in r.stderr and "--agent harness-backend-dev"
        not in r.stderr and "release-all" not in r.stderr,
        r.stderr.strip()[:400])

    fails = 0
    for name, ok, detail in T09:
        if ok:
            print("ok    %s" % (name,))
        else:
            fails += 1
            print("FAIL  %s" % (name,))
            print("      | %s" % (detail,))
    print("\n%d/%d T-09 cases passed." % (len(T09) - fails, len(T09)))
    return fails


T51_PARENT_ID = "Orch.Product"


def _t51_fixture(reg, parent="harness-product-lead", children=("harness-pm",)):
    root = _t09_root()
    session = "feat51-session"
    for agent, dispatcher, agent_id, parent_id in (
        [(parent, "harness-orchestrator", T51_PARENT_ID, "Orch")]
        + [(child, parent, "%s.%s" % (T51_PARENT_ID, child), T51_PARENT_ID)
           for child in children]
    ):
        entry = reg.claim_with_receipt(root, agent, dispatcher, root, feature=T09_FEATURE)
        reg.attach_runtime_identity(root, agent, T09_FEATURE, agent_id=agent_id,
                                    claim_id=entry["claim_id"], parent_agent_id=parent_id)
    return root, session


def _t51_result(name, result, expected):
    return name, result.returncode == expected, (
        f"exit {result.returncode}: {result.stderr}"
    )


def _t51_suspended_refused(reg):
    """DEC-233: under a blocking host a parent never yields with a live child, so the
    nonterminal SUSPENDED turn-end DEC-210 accepted is now refused like any other
    return with a live child, and the parent's claim is left in place."""
    root, session = _t51_fixture(reg)
    result = _t09_fire(
        root, "harness-product-lead",
        "VERDICT: SUSPENDED\nDIGEST:\n  awaiting:\n    - harness-pm\n",
        session_id=session,
        harness_feature=T09_FEATURE, harness_agent_id=T51_PARENT_ID,
    )
    parent, _ = reg.live_claim(root, "harness-product-lead")
    return [
        _t51_result("a SUSPENDED return with a live child is refused", result, 2),
        ("the refused SUSPENDED return leaves the parent claim live",
         parent is not None, repr(parent)),
    ]


def _t51_terminal(reg):
    root, session = _t51_fixture(reg)
    result = _t09_fire(
        root, "harness-product-lead",
        "VERDICT: PASS\nDIGEST:\n  headline: done\n", session_id=session,
        harness_feature=T09_FEATURE, harness_agent_id=T51_PARENT_ID,
    )
    return [_t51_result("a terminal PASS with a live child is refused", result, 2)]

def _t51_missing_message(reg):
    results = []
    for label, include_null in (("absent", False), ("null", True)):
        root, session = _t51_fixture(reg)
        payload = {
            "agent_type": "harness-product-lead",
            "cwd": root,
            "session_id": session,
            "harness_feature": T09_FEATURE,
            "harness_agent_id": T51_PARENT_ID,
        }
        if include_null:
            payload["digest_object"] = None
        result = subprocess.run(
            [VALIDATE, "--hook"], input=json.dumps(_governed(payload)),
            capture_output=True, text=True,
            env=dict(os.environ, 
                     HARNESS_PROJECT_DIR=root),
        )
        parent, _ = reg.live_claim(
            root, "harness-product-lead"
        )
        results.extend([
            _t51_result(
                f"a live child with {label} yield data is refused",
                result, 2,
            ),
            (f"the {label}-message refusal leaves the parent claim live",
             parent is not None, repr(parent)),
        ])
    return results


def run_t51_suspension_cases():
    reg = _reg_module()
    results = []
    for case in (
        _t51_suspended_refused(reg),
        _t51_terminal(reg),
        _t51_missing_message(reg),
    ):
        results.extend(case)
    fails = 0
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            fails += 1
            print("     ", detail[:500])
    return fails


_ISOLATED_ROOT = None


def _isolated_root():
    """A throwaway checkout every hook case that does not name its own root runs against.

    WITHOUT THIS THEY RUN AGAINST THE LIVE ONE. The hook releases and inspects the in-flight
    claim registry, and that registry lives under the resolved root — so a claim left behind
    by anything else in this repository refuses cases that have nothing to do with it. It
    happened during FEAT-42 T-18: a reverted-gate run stranded eight claims here, and three
    unrelated digest-shape cases then failed with a children-in-flight refusal. A suite whose
    verdict depends on what else touched the machine is not a suite.
    """
    global _ISOLATED_ROOT
    if _ISOLATED_ROOT is None:
        _ISOLATED_ROOT = tempfile.mkdtemp(prefix="vd-hookcases-")
        os.makedirs(os.path.join(_ISOLATED_ROOT, ".harness"), exist_ok=True)
        with open(os.path.join(_ISOLATED_ROOT, ".harness", "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        with open(os.path.join(_ISOLATED_ROOT, ".harness", "harness.json"), "w") as f:
            json.dump({"gates": {"review": "advisory"}}, f)
    return _ISOLATED_ROOT


def run_hook_cases():
    """Drive --hook mode directly: JSON payload on stdin, EXACT exit code
    asserted (2 reject / 0 pass — never just 'nonzero'), rejection text
    checked on STDERR (hook mode writes there, not stdout). Asserting only
    "nonzero == rejected" would let the fail-open crash (exit 1) masquerade
    as a correct rejection — exactly the bug this suite exists to catch.
    """
    fails = 0
    for name, payload, want_exit, mentions in HOOK_CASES:
        # `_root` is the test harness's own key, stripped before the payload is sent: it names
        # the root this case's artifact lives under, which the hook now takes from the
        # override rather than from the payload cwd (FEAT-42 T-17).
        payload = dict(payload)
        _root = payload.pop("_root", None) or _isolated_root()
        env = dict(os.environ)
        env["HARNESS_PROJECT_DIR"] = _root
        r = subprocess.run([VALIDATE, "--hook"], input=json.dumps(_governed(payload)),
                           capture_output=True, text=True, env=env)
        bad = []
        if r.returncode != want_exit:
            bad.append(f"expected exit {want_exit}, got {r.returncode}")
        # A case may require SEVERAL substrings. D-01's fail-open line has to carry both
        # the words that say the return went unvalidated AND the attribution of the gap to
        # us, and a single substring can assert only one of them: exit 0 is what the DEFECT
        # returned too, so the words are the whole discrimination.
        for _want in ((mentions,) if isinstance(mentions, str) else (mentions or ())):
            if _want.lower() not in r.stderr.lower():
                bad.append(f"stderr should mention {_want!r}")
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


# --- SC-07: the sanctioned append, read back byte for byte -------------------------------
APPEND_REL = os.path.join(".harness", "harness", "features", HOOK_IDENTITY["harness_feature"],
                          "runs", "r1-eng", "digest.md")
APPEND_PROSE = "# Team digest — T-01\n\nThe lead's human assessment, written by the lead.\n"


def _append_root():
    root = os.path.realpath(tempfile.mkdtemp(prefix="vd-append-"))
    _append_registration(root)
    return root, os.path.join(root, APPEND_REL)


def _append_registration(root, cwd=None, claim=True):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as marker:
        yaml.safe_dump({"leads": [{"name": "harness-eng-lead", "squad": "engineering", "domain": [
            {"path": ".harness/*/features/*/runs/*-eng/**", "upsert": True},
            {"path": ".", "read": True}]}]}, marker)
    path = os.path.join(root, APPEND_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    feature_dir = os.path.dirname(os.path.dirname(os.path.dirname(path)))
    with open(os.path.join(feature_dir, "feature.json"), "w") as record:
        json.dump({"feature_id": HOOK_IDENTITY["harness_feature"], "runs": [{
            "id": "r1-eng", "squad": "engineering", "agent": "harness-eng-lead",
            "verdict": "PENDING", "started_at": "2026-10-04T00:00:00+00:00"}]}, record)
    if claim:
        _reg_module().claim_run_start(root, "harness-eng-lead", HOOK_IDENTITY["harness_feature"],
                                     HOOK_IDENTITY["harness_agent_id"], "Test.Parent",
                                     supervisor_pid=os.getpid(), cwd=cwd or root)


def _append_binding(root):
    return {"root": root, "feature": HOOK_IDENTITY["harness_feature"],
            "agent": "harness-eng-lead", "agent_id": HOOK_IDENTITY["harness_agent_id"],
            "parent_agent_id": "Test.Parent", "run_id": "r1-eng",
            "artifact": os.path.join(root, APPEND_REL)}


def _append_lead_object(**digest):
    obj = fixture("harness-eng-lead", LEAD_BLOCK.replace("artifact: .harness/features/FEAT-01/runs/r1/digest.md",
                                    f"artifact: {APPEND_REL}"))
    obj["DIGEST"].update(digest)
    return obj
_dec156_worktree_case(
    "dec156-worktree-narrative: the bound worktree digest gains the validated block",
    "# narrative digest, no contract block\n", 0)
_dec156_worktree_case(
    "dec156-worktree-valid: an identical last object is left alone",
    "# narrative\n" + "\n```yaml\n" + yaml.safe_dump(_append_lead_object(), sort_keys=False) + "```\n", 0)
_dec156_worktree_case(
    "dec156-worktree-nofeature: missing feature identity refuses the return",
    "# narrative digest, no contract block\n", 2, feature=False)



def _fenced(obj):
    return "\n```yaml\n" + yaml.safe_dump(obj, sort_keys=False) + "```\n"


def _append_fire(root, obj, agent="harness-eng-lead"):
    payload = {"agent_type": agent, "digest_object": obj,
               "harness_parent_agent_id": "Test.Parent",
               "harness_digest_binding": _append_binding(root)}
    return subprocess.run([VALIDATE, "--hook"], input=json.dumps(_governed(payload)),
                          capture_output=True, text=True,
                          env=dict(os.environ, HARNESS_PROJECT_DIR=root))


def _read_bytes(path):
    """The file's bytes (through a symlink), or None when there is no file."""
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        return handle.read()


def _remove_append_root(root):
    for dirpath, _dirs, files in os.walk(root):
        for leaf in files:
            if not os.path.islink(os.path.join(dirpath, leaf)):
                os.chmod(os.path.join(dirpath, leaf), 0o644)
    shutil.rmtree(root, ignore_errors=True)


def _append_prepare(prior, prepare):
    """A fixture root with `prior` written (None = no file) and `prepare` applied; returns
    (root, path, skip-reason or None)."""
    root, path = _append_root()
    if prior is not None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(prior)
    return root, path, prepare(root, path) if prepare else None


def _append_case(name, prior, obj, want_exit, expect_bytes, agent="harness-eng-lead",
                 prepare=None):
    """Write `prior`, fire, and compare the file's bytes with `expect_bytes(prior_bytes)`
    — None meaning "unchanged"."""
    root, path, skip = _append_prepare(prior, prepare)
    try:
        if skip:
            return name, True, skip
        before = _read_bytes(path)
        result = _append_fire(root, obj, agent)
        after = _read_bytes(path)
        want = before if expect_bytes is None else expect_bytes(before)
        ok = result.returncode == want_exit and after == want
        return name, ok, f"exit={result.returncode} bytes-match={after == want} {result.stderr.strip()[:400]}"
    finally:
        _remove_append_root(root)


def _make_readonly(root, path):
    os.chmod(path, 0o444)
    if os.access(path, os.W_OK):
        return "skipped: running with privileges that ignore file modes"
    return None


def _make_symlink(root, path):
    target = os.path.join(root, "elsewhere.md")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(APPEND_PROSE)
    os.remove(path)
    os.symlink(target, path)
    return None


def _cli_never_writes():
    root, path = _append_root()
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(APPEND_PROSE)
        obj = _append_lead_object()
        obj["artifact"] = path
        result = subprocess.run([VALIDATE, "harness-eng-lead"], input=json.dumps(obj),
                                capture_output=True, text=True)
        with open(path, encoding="utf-8") as handle:
            unchanged = handle.read() == APPEND_PROSE
        return ("the direct CLI validates a lead object and never writes its digest",
                result.returncode == 0 and unchanged, f"exit={result.returncode} {result.stdout}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def run_lead_append_cases():
    """SC-07: after a lead object passes every live check the hook appends it to the
    registered digest.md as one fenced YAML block — never when it equals the last one,
    always after the existing bytes, refusing when the file cannot be resolved or written;
    a non-lead and the CLI never write."""
    obj = _append_lead_object()
    cases = _append_rule_cases(obj)
    cases += [_repeated_yield_appends_once(obj), _cli_never_writes()]
    cases += _append_authorization_cases()
    cases += [_hook_binding_refuses(kind) for kind in ("wrong-parent", "ambiguous-run")]
    cases += [_hook_binding_linked_worktree_binds(), _hook_binding_other_registry_refuses()]
    fails = 0
    for name, ok, detail in cases:
        print(f"ok    [append] {name}" if ok else f"FAIL  [append] {name}\n      | {detail}")
        fails += 0 if ok else 1
    print(f"\n{len(cases) - fails}/{len(cases)} SC-07 append cases passed.")
    return fails


def _append_rule_cases(obj):
    earlier = _append_lead_object(headline="an earlier assessment of the same run")
    historical = dict(earlier, DIGEST=dict(earlier["DIGEST"], legacy_field="kept as written"))
    doc_obj = fixture("harness-documentor", "VERDICT: PASS\nDIGEST:\n  headline: docs updated\n  docs_updated: []\n"
                     "  gaps: []\n  files_touched: []\n  open_questions: []\n"
                     f"  expertise_update: []\nartifact: {APPEND_REL}\n")
    bad_lead = _append_lead_object()
    bad_lead["VERDICT"] = "PASS"  # a FAIL member under a PASS lead: the roll-up refuses it
    appended = lambda before: before + _fenced(obj).encode("utf-8")
    return [
        _append_case("identical to the last fenced mapping: nothing is written",
                     APPEND_PROSE + _fenced(obj), obj, 0, None),
        _append_case("a changed object is appended as a correction, prior bytes intact",
                     APPEND_PROSE + _fenced(earlier), obj, 0, appended),
        _append_case("a historical block outside today's schema is compared, never validated",
                     APPEND_PROSE + _fenced(historical), obj, 0, appended),
        _append_case("prose with no fenced block gains the block after the prose",
                     APPEND_PROSE, obj, 0, appended),
        _append_case("prose with no trailing newline still gets a fence on its own line",
                     APPEND_PROSE.rstrip("\n"), obj, 0, appended),
        _append_case("an unfinished prose fence refuses before any bytes change",
                     APPEND_PROSE + "```text\nunfinished example\n", obj, 2, None),
        _append_case("an unfinished fence after an earlier record cannot hide a correction",
                     APPEND_PROSE + _fenced(earlier) + "```yaml\nunfinished: example\n",
                     obj, 2, None),
        _append_case("a closed prose fence still permits a readable record",
                     APPEND_PROSE + "```text\ncomplete example\n```\n", obj, 0, appended),
        _append_case("a missing digest in the resolved run directory is refused, nothing created",
                     None, obj, 2, None),
        _append_case("an unwritable digest is refused and left unchanged",
                     APPEND_PROSE, obj, 2, None,
                     prepare=_make_readonly),
        _append_case("a symlinked digest is not a safe target and is refused",
                     APPEND_PROSE, obj, 2, None,
                     prepare=_make_symlink),
        _append_case("an invalid lead object is refused before any write",
                     APPEND_PROSE, bad_lead, 2, None),
        _append_case("a non-lead return naming the same digest.md never writes it",
                     APPEND_PROSE, doc_obj, 0, None, agent="harness-documentor"),
    ]


def _repeated_yield_appends_once(obj):
    root, path = _append_root()
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(APPEND_PROSE)
        first, second = _append_fire(root, obj), _append_fire(root, obj)
        text = open(path, encoding="utf-8").read()
        return ("a repeated identical yield appends once, then nothing",
                first.returncode == 0 and second.returncode == 0
                and text == APPEND_PROSE + _fenced(obj), text[-200:])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _append_authorization_target(root, kind):
    own = os.path.join(root, APPEND_REL)
    if kind == "parent-symlink":
        external = os.path.realpath(tempfile.mkdtemp(prefix="vd-external-"))
        shutil.rmtree(os.path.dirname(own))
        os.symlink(external, os.path.dirname(own))
        return own, external
    relative = APPEND_REL
    if kind in ("product", "validator", "other-eng"):
        relative = relative.replace("r1-eng", f"victim-{kind}")
    elif kind == "other-feature":
        relative = relative.replace(HOOK_IDENTITY["harness_feature"], "FEAT-02-other")
    target = os.path.join(root, relative)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    return target, None


@contextlib.contextmanager
def _authorization_fixture(kind):
    root, own = _append_root()
    external = None
    try:
        with open(own, "w") as report:
            report.write(APPEND_PROSE)
        target, external = _append_authorization_target(root, kind)
        victim = _append_lead_object(headline="the victim's authoritative assessment")
        victim["artifact"] = target
        before = (APPEND_PROSE + _fenced(victim)).encode()
        with open(target, "wb") as report:
            report.write(before)
        yield root, target, victim, before
    finally:
        shutil.rmtree(root, ignore_errors=True)
        if external:
            shutil.rmtree(external, ignore_errors=True)


def _append_authorization_case(kind, absolute=False):
    import digest_record
    with _authorization_fixture(kind) as (root, target, victim, before):
        obj = _append_lead_object()
        obj["artifact"] = target if absolute else os.path.relpath(target, root)
        result = _append_fire(root, obj)
        after = _read_bytes(target)
        selected = digest_record.last_fenced_mapping(after.decode(), target)
        claims = _reg_module().live_claims(root, None)
        ok = (result.returncode == 2
              and before == after and selected == victim
              and any(row.get("agent_id") == HOOK_IDENTITY["harness_agent_id"]
                          for row in claims))
        return (f"unauthorized {kind} {'absolute' if absolute else 'relative'} target stays byte-identical",
                ok, f"exit={result.returncode} bytes-match={before == after} {result.stderr.strip()[:400]}")


def _append_authorization_cases():
    return [_append_authorization_case(kind, absolute)
            for kind, absolute in (
                ("product", False), ("validator", False), ("other-eng", False),
                ("other-feature", False), ("product", True),
                ("parent-symlink", False), ("parent-symlink", True))]


def _hook_binding_refuses(kind):
    root, path = _append_root()
    try:
        payload = _governed({"agent_type": "harness-eng-lead", "cwd": root,
                             "harness_parent_agent_id": "Test.Parent"})
        if kind == "wrong-parent":
            payload["harness_parent_agent_id"] = "Other.Parent"
        else:
            record_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(path))),
                                       "feature.json")
            with open(record_path) as source:
                record = json.load(source)
            record["runs"].append({"id": "r2-eng", "squad": "engineering",
                                   "agent": "harness-eng-lead", "verdict": "PENDING"})
            with open(record_path, "w") as target:
                json.dump(record, target)
        result = subprocess.run([os.path.join(os.path.dirname(VALIDATE), "digest_destination.py")],
                                input=json.dumps(payload), capture_output=True, text=True,
                                env=dict(os.environ, HARNESS_PROJECT_DIR=root))
        response = json.loads(result.stdout)
        ok = result.returncode == 2 and response.get("ok") is False and "binding" not in response
        return f"startup refuses {kind} without issuing digest authority", ok, result.stdout + result.stderr
    finally:
        _remove_append_root(root)


def _linked_worktree_bind(claim_in_feature):
    """#2063: a feature on a linked worktree. The session (and so every claim's recorded
    cwd) is the OWNER checkout; the claim lives in the feature worktree's registry, or —
    when `claim_in_feature` is false — only in the owner's. Answers the startup result."""
    owner = os.path.realpath(tempfile.mkdtemp(prefix="vd-bind-linked-"))
    try:
        worktree = _linked_worktree_fixture(owner, HOOK_IDENTITY["harness_feature"])
        _append_registration(worktree, cwd=owner, claim=claim_in_feature)
        shutil.copytree(os.path.join(worktree, ".harness"), os.path.join(owner, ".harness"),
                        ignore=shutil.ignore_patterns("features", "inflight.json", "inflight.json.lock"))
        if not claim_in_feature:
            _reg_module().claim_run_start(owner, "harness-eng-lead", HOOK_IDENTITY["harness_feature"],
                                         HOOK_IDENTITY["harness_agent_id"], "Test.Parent",
                                         supervisor_pid=os.getpid(), cwd=owner)
        payload = _governed({"agent_type": "harness-eng-lead", "cwd": owner,
                             "harness_parent_agent_id": "Test.Parent"})
        result = subprocess.run([os.path.join(os.path.dirname(VALIDATE), "digest_destination.py")],
                                input=json.dumps(payload), capture_output=True, text=True,
                                env=dict(os.environ, HARNESS_PROJECT_DIR=owner))
        return worktree, result, json.loads(result.stdout)
    finally:
        _remove_append_root(owner)


def _hook_binding_linked_worktree_binds():
    worktree, result, response = _linked_worktree_bind(True)
    binding = response.get("binding", {})
    ok = (result.returncode == 0 and binding.get("root") == worktree
          and binding.get("artifact") == os.path.join(worktree, APPEND_REL))
    return ("startup binds a linked-worktree feature whose claim cwd is the owner checkout",
            ok, result.stdout + result.stderr)


def _hook_binding_other_registry_refuses():
    _worktree, result, response = _linked_worktree_bind(False)
    ok = result.returncode == 2 and response.get("ok") is False and "binding" not in response
    return ("startup refuses a claim held only in another checkout's registry",
            ok, result.stdout + result.stderr)



QA_UNCONDITIONAL_PASS = """
VERDICT: PASS
DIGEST:
  headline: suite green
  suite: pass
  failures: 0
  coverage_gaps: []
  matrix_ok: true
  fail_first: [{ sc: SC-01, evidence: "notes/qa-r1/fail-first-SC-01.txt" }]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
"""


def _bug919_stub_script(root, exit_code):
    """A fast run-unit-tests.py stand-in for RUN_UNIT_TESTS_BIN — the real suite takes
    minutes; this proves the wiring (which script ran, with which argv, what its exit
    code did) instead. It is a PYTHON file, as the real runner has been since #1674
    (BUG-1756): a spawn that hands it to bash cannot run it, so the agree case goes red
    on the defect. Every invocation appends its argv to `<stub>.argv`, one line each."""
    path = os.path.join(root, "stub-run-unit-tests-%d.py" % exit_code)
    with open(path, "w") as f:
        f.write("#!/usr/bin/env python3\nimport sys\n"
                "open(sys.argv[0] + '.argv', 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
                "print('STUB_RAN')\nsys.exit(%d)\n" % exit_code)
    os.chmod(path, 0o755)
    return path


def _bug919_fire(stub_path, text=QA_UNCONDITIONAL_PASS, agent="harness-qa", extra_env=None):
    root = _isolated_root()
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root)
    if stub_path is not None:
        env["RUN_UNIT_TESTS_BIN"] = stub_path
    else:
        env.pop("RUN_UNIT_TESTS_BIN", None)
    if extra_env:
        env.update(extra_env)
    payload = {"agent_type": agent, "digest_object": fixture(agent, text)}
    return subprocess.run([VALIDATE, "--hook"], input=json.dumps(_governed(payload)),
                          capture_output=True, text=True, env=env)


def _bug919_agree_case(green):
    r = _bug919_fire(green)
    return ("independent re-run agrees (exit 0) — accepted", r.returncode == 0,
            f"exit={r.returncode} stderr={r.stderr!r}")


def _bug919_disagree_case(red):
    r = _bug919_fire(red)
    ok = (r.returncode == 2 and "919" in r.stderr
          and "independent re-run" in r.stderr.lower())
    return ("independent re-run disagrees (exit 1) — the false-PASS is refused",
            ok, f"exit={r.returncode} stderr={r.stderr!r}")


def _bug919_non_pass_case(green):
    text = QA_UNCONDITIONAL_PASS.replace(
        "VERDICT: PASS", "VERDICT: BLOCKED").replace(
        "matrix_ok: true", "matrix_ok: n/a").replace("suite: pass", "suite: n/a")
    r = _bug919_fire(green, text=text)
    ok = r.returncode == 0 and "STUB_RAN" not in (r.stdout + r.stderr)
    return ("a non-PASS verdict is never re-run — the stub was never asked to run",
            ok, f"exit={r.returncode} out={r.stdout!r} err={r.stderr!r}")


def _bug919_missing_script_case(tmp):
    missing = os.path.join(tmp, "does-not-exist.sh")
    r = _bug919_fire(missing)
    ok = r.returncode == 0 and "could not independently re-run" in r.stderr.lower()
    return ("a missing suite script fails OPEN, loudly — never blocks on our own gap",
            ok, f"exit={r.returncode} stderr={r.stderr!r}")


def _bug919_red_case(red):
    mutant_source = _bug919_red_mutant()
    if mutant_source is None:
        return ("RED proof: with the qa wiring removed, the same false PASS is accepted",
                False, "INCONCLUSIVE: the qa-wiring anchor was not found by its source text")
    iso_root = tempfile.mkdtemp()
    mutant = os.path.join(
        isolated_bin(iso_root), ".validate-digest-bug919-red-%d.py" % os.getpid())
    root = _isolated_root()
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root,
              RUN_UNIT_TESTS_BIN=red)
    payload = {"agent_type": "harness-qa", "digest_object": fixture("harness-qa", QA_UNCONDITIONAL_PASS)}
    try:
        _install_mutant(mutant, mutant_source)
        muted = subprocess.run([mutant, "--hook"], input=json.dumps(_governed(payload)),
                               capture_output=True, text=True, env=env)
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)
    real = _bug919_fire(red)
    ok = (real.returncode == 2 and muted.returncode == 0
          and "Traceback" not in muted.stderr)
    detail = f"real={real.returncode} mutant={muted.returncode}: {muted.stderr}"
    return ("RED proof: with the qa wiring removed, the same false PASS is accepted",
            ok, detail)


QA_PASS_WITH_KINDS = QA_UNCONDITIONAL_PASS.replace(
    "  matrix_ok: true\n",
    "  matrix_ok: true\n"
    "  kinds:\n"
    "    - { kind: unit, state: satisfied, cmd: \"python3 x --kind unit\", named_tests: 40 }\n"
    "    - { kind: integration, state: satisfied, cmd: \"python3 x --kind integration\", named_tests: 72 }\n")


def _bug1756_argv(stub):
    """The argv lines the Python stub recorded, one per invocation."""
    try:
        with open(stub + ".argv") as f:
            return [l.rstrip("\n") for l in f if l.strip() or l == "\n"]
    except FileNotFoundError:
        return []


def _bug1756_kinds_forwarded_case(green):
    """SC-01: each claimed kind is one `--kind <k>` run of the Python runner, in order."""
    r = _bug919_fire(green, text=QA_PASS_WITH_KINDS)
    argv = _bug1756_argv(green)
    ok = r.returncode == 0 and argv == ["--kind unit", "--kind integration"]
    return ("BUG-1756 SC-01: a claim naming unit+integration runs the Python runner once per kind",
            ok, f"exit={r.returncode} argv={argv!r} stderr={r.stderr!r}")


def _bug1756_first_failure_stops_case(tmp):
    """SC-02: a runner that fails on the FIRST kind stops the rerun there — the second kind
    never runs — and the refusal carries the runner's real tail."""
    stub = os.path.join(tmp, "stub-fails-on-unit.py")
    with open(stub, "w") as f:
        f.write("#!/usr/bin/env python3\nimport sys\n"
                "open(sys.argv[0] + '.argv', 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
                "print('UNIT_TAIL_LINE' if 'unit' in sys.argv else 'INTEGRATION_RAN')\n"
                "sys.exit(1 if 'unit' in sys.argv else 0)\n")
    os.chmod(stub, 0o755)
    r = _bug919_fire(stub, text=QA_PASS_WITH_KINDS)
    argv = _bug1756_argv(stub)
    ok = (r.returncode == 2 and argv == ["--kind unit"] and "UNIT_TAIL_LINE" in r.stderr
          and "INTEGRATION_RAN" not in r.stderr)
    return ("BUG-1756 SC-02: the first failing kind stops the rerun and its real tail is reported",
            ok, f"exit={r.returncode} argv={argv!r} stderr={r.stderr!r}")


def _bug1756_default_set_case(green):
    """SC-03: a claim naming no kinds runs the runner once, bare, so its default set governs."""
    r = _bug919_fire(green)
    argv = _bug1756_argv(green)
    ok = r.returncode == 0 and argv and argv[-1] == ""
    return ("BUG-1756 SC-03: a claim naming no kinds runs the Python runner once with no --kind",
            ok, f"exit={r.returncode} argv={argv!r} stderr={r.stderr!r}")


def _bug1756_in_process_reverify(green, raising):
    """SC-04 at the exact seam: load the validator, make `subprocess.run` raise `raising`
    when it is handed the runner, and call `check_qa_matrix_claim` directly. The directory
    fixture the c0 review struck never reached `subprocess.run` (os.path.isfile refused it
    first); this does. Returns (exit_code, stderr_text)."""
    import importlib.util
    import io
    import contextlib
    spec = importlib.util.spec_from_file_location("_bug1756_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    real_run = validator.subprocess.run

    def run_or_raise(argv, **kw):
        if len(argv) > 1 and argv[1] == green:
            raise raising
        return real_run(argv, **kw)

    validator.subprocess.run = run_or_raise
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            code = validator.check_qa_matrix_claim(
                "harness-qa", fixture("harness-qa", QA_PASS_WITH_KINDS), {"harness_feature": None})
        except Exception as exc:  # the fail-open contract broken: a crash, not a verdict
            return None, f"{err.getvalue()}RAISED {type(exc).__name__}: {exc}"
    return code, err.getvalue()


def _bug1756_spawn_error_case(green):
    """SC-04: an OSError raised BY the spawn (not by a missing file) fails OPEN with the
    'could not independently re-run' line and exit 0, never a block or a traceback."""
    os.environ["RUN_UNIT_TESTS_BIN"] = green
    try:
        code, err = _bug1756_in_process_reverify(green, OSError(8, "Exec format error"))
    finally:
        os.environ.pop("RUN_UNIT_TESTS_BIN", None)
    ok = code == 0 and "could not independently re-run" in err.lower()
    return ("BUG-1756 SC-04: a spawn OSError fails OPEN, loudly", ok, f"exit={code} stderr={err!r}")


def _bug1756_timeout_case(green):
    """SC-04: a runner that exceeds the re-run timeout (subprocess.TimeoutExpired) fails
    OPEN the same way — the gate never hangs the return and never blocks on its own gap."""
    os.environ["RUN_UNIT_TESTS_BIN"] = green
    try:
        code, err = _bug1756_in_process_reverify(
            green, subprocess.TimeoutExpired([sys.executable, green], 1800))
    finally:
        os.environ.pop("RUN_UNIT_TESTS_BIN", None)
    ok = code == 0 and "could not independently re-run" in err.lower()
    return ("BUG-1756 SC-04: a re-run timeout fails OPEN, loudly", ok, f"exit={code} stderr={err!r}")


def _report_bug919_results(cases):
    fails = 0
    for name, ok, detail in cases:
        if ok:
            print(f"ok    [bug919] {name}")
        else:
            fails += 1
            print(f"FAIL  [bug919] {name}\n      | {detail}")
    print(f"\n{len(cases) - fails}/{len(cases)} bug919 qa-matrix-reverify cases passed.")
    return fails


def run_bug919_qa_matrix_cases():
    """Issue #919: an unconditional qa PASS (VERDICT: PASS, suite: pass, matrix_ok:
    true) is independently re-verified against a real run of the suite, rather than
    trusted on the strength of the self-report alone."""
    tmp = tempfile.mkdtemp(prefix="vd-bug919-")
    os.makedirs(os.path.join(tmp, "k"))
    green = _bug919_stub_script(tmp, 0)
    red = _bug919_stub_script(tmp, 1)
    cases = [
        _bug919_agree_case(green),
        _bug919_disagree_case(red),
        _bug919_non_pass_case(green),
        _bug919_missing_script_case(tmp),
        _bug919_red_case(red),
        _bug1756_default_set_case(green),
        _bug1756_kinds_forwarded_case(_bug919_stub_script(os.path.join(tmp, "k"), 0)),
        _bug1756_first_failure_stops_case(tmp),
        _bug1756_spawn_error_case(green),
        _bug1756_timeout_case(green),
    ]
    return _report_bug919_results(cases)


def run_bug919_resolve_fallback_case():
    """Code review of #1185, Finding 1 (high): a named feature whose worktree lookup
    FAILS must resolve to None, never silently substitute owner_root — run-unit-tests.py
    is a static, always-present path, so a wrong-root substitution here never 404s; it
    just silently re-runs the suite against the wrong checkout and reports that
    mismatched result as though it verified the claim."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import inflight_registry
    spec = importlib.util.spec_from_file_location("_bug919_fallback_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)

    original_root_fn = validator._root_or_none
    original_feature_root = inflight_registry.feature_root
    validator._root_or_none = lambda: "/some/owner/root"
    # FEAT-65: the lookup's own boundary class, not an arbitrary one — the fallback is
    # typed now, and an unrelated exception is a defect that reaches hook_guard instead.
    def _raise(root, feature):
        raise OSError("no unambiguous worktree for %r" % feature)
    inflight_registry.feature_root = _raise
    saved_env = os.environ.pop("RUN_UNIT_TESTS_BIN", None)
    try:
        resolved = validator._resolve_run_unit_tests_bin(
            {"harness_feature": "some-ambiguous-feature"})
    finally:
        validator._root_or_none = original_root_fn
        inflight_registry.feature_root = original_feature_root
        if saved_env is not None:
            os.environ["RUN_UNIT_TESTS_BIN"] = saved_env
    ok = resolved is None
    if ok:
        print("ok    [bug919] a feature_root lookup failure resolves to None, "
              "never a silent owner_root substitution")
    else:
        print(f"FAIL  [bug919] a feature_root lookup failure resolves to None, "
              f"never a silent owner_root substitution\n      | got {resolved!r}")
    print("\n%d/1 bug919 fallback-resolution cases passed." % (1 if ok else 0,))
    return 0 if ok else 1


def run_bug919_resolve_by_artifact_case():
    """#1883, second site: the #919 re-run resolved the feature's checkout by WORKTREE NAME
    and `feature_root` substitutes the owner root when no worktree is named after the
    feature — the exact silent wrong-checkout re-run the docstring above refuses. Measured
    2026-09-22: a qa re-return for FEAT-63 from a branch worktree named `process-gaps` was
    re-run against the owner checkout on a stale branch and refused on THAT tree's failure.
    The digest's own artifact line names the checkout; when it lies inside a linked
    worktree, that worktree's runner is the one to re-run."""
    spec = importlib.util.spec_from_file_location("_bug919_artifact_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    owner = tempfile.mkdtemp(prefix="vd-919-owner-")
    os.makedirs(os.path.join(owner, ".harness"), exist_ok=True)
    worktree = _linked_worktree_fixture(owner, "process-gaps")
    artifact = (f"{worktree}/.harness/harness/features/FEAT-63-thing/notes/"
                f"review-harness-qa-c2.md")
    original_root_fn = validator._root_or_none
    validator._root_or_none = lambda: owner
    saved_env = os.environ.pop("RUN_UNIT_TESTS_BIN", None)
    try:
        resolved = validator._resolve_run_unit_tests_bin(
            {"harness_feature": "FEAT-63-thing"}, artifact)
    finally:
        validator._root_or_none = original_root_fn
        if saved_env is not None:
            os.environ["RUN_UNIT_TESTS_BIN"] = saved_env
        shutil.rmtree(owner, ignore_errors=True)
    expected = os.path.join(worktree, ".claude", "skills", "harness", "bin", "run-unit-tests.py")
    ok = resolved is not None and os.path.realpath(resolved) == os.path.realpath(expected)
    label = ("[bug919/#1883] the re-run resolves to the linked worktree holding the "
             "digest's artifact, not the owner root")
    print(f"ok    {label}" if ok else f"FAIL  {label}\n      | got {resolved!r}")
    return 0 if ok else 1


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

# --- 2026-08-26: an ANALYSIS dispatch owes no test result --------------------------
# A dev asked to READ and REPORT writes no production code, so the Iron Law binds on
# nothing: there is no code owed a passing test. Before this, such a return had NO
# truthful digest -- `suite: n/a` + PASS was rejected, it was re-prompted, and the
# re-emission dropped its report body. MEASURED on 2026-08-26: three of four member
# runs lost their report that way, and TWO agents reasoned themselves into a
# fabricated `suite: pass` to satisfy the schema.
#
# THE GATE OPENS ON BOTH CONDITIONS, NEVER ONE. `files_touched: []` alone is not
# enough -- DEV_NA above is `task: T-01` refused with nothing touched, and that must
# STAY rejected. `task: none` alone is not enough either: it is a CLAIM, and a return
# can write it while editing ten files. Only the pair -- no task declared AND nothing
# touched -- separates "had nothing to test" from "declined to test".
DEV_ANALYSIS = """
VERDICT: PASS
DIGEST:
  headline: censused 84 path-returning functions; harness_boundary.py is the candidate
  tests_added: 0
  suite: n/a
  blocked_on: none
  task: none
  task_verify: n/a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: none
"""
case("an analysis dev -- task: none AND files_touched: [] -- may say suite: n/a with PASS",
     "harness-backend-dev", DEV_ANALYSIS, True)

case("task: none but files WERE touched -- suite: n/a with PASS is still REJECTED, "
     "because `task: none` is a claim and the edit is the fact",
     "harness-backend-dev",
     DEV_ANALYSIS.replace("files_touched: []", "files_touched: [gh-sync.py]"),
     False, "pass")

# THE SUITE GATE, ISOLATED. Found by mutation on 2026-08-26: deleting the `task: none`
# half of `_nothing_to_gate` broke NO test, because the case above it -- DEV_NA with
# PASS -- is rejected over `task_verify: n/a`, never over `suite`. It asserts the right
# outcome for the wrong reason, so it could not pin this half.
#
# This return satisfies EVERY other gate: a real task, its verify PASSED, nothing
# touched. The ONLY thing wrong with it is `suite: n/a` alongside PASS. It must stay
# REJECTED -- a task was worked and the suite still did not run -- and it is the only
# case that can go red when the task half is removed.
DEV_REAL_TASK_NO_SUITE = """
VERDICT: PASS
DIGEST:
  headline: T-01 verified against its own command; the full suite was not run
  tests_added: 0
  suite: n/a
  blocked_on: none
  task: T-01
  task_verify: pass
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: none
"""
case("a REAL task whose verify passed still owes a suite result -- suite: n/a with "
     "PASS is REJECTED even with nothing touched",
     "harness-backend-dev", DEV_REAL_TASK_NO_SUITE, False, "pass")

QA_NA = """
VERDICT: BLOCKED
DIGEST:
  headline: the suite could not be run; no runner resolves in this project
  suite: n/a
  failures: 0
  coverage_gaps: []
  matrix_ok: n/a
  fail_first: []
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
  findings: []
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
  findings: [{ kind: substance, scope: none, severity: med, reader: ui-reviewer, summary: "focus ring lost", why: "the reader states its reason" }]
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
     "harness-backend-dev", _dev(tv=None), False, "missing 'task_verify'", complete=False)
# (b) DETECTOR — REQ-01's whole point.
case("dev task_verify: fail + PASS is rejected",
     "harness-backend-dev", _dev(tv="fail"), False, "task_verify")
# (c) DETECTOR.
case("dev task_verify: n/a + PASS is rejected",
     "harness-backend-dev", _dev(tv="n/a"), False, "task_verify")
# (d) DETECTOR — the no-carve-out ruling. dev-ops is NOT exempt from this field,
# though it stays exempt from `suite` (D-03, proven by the case further above).
# (d, second half) DETECTOR — SC-03 says BOTH rejections hold for dev-ops, and only
# the `n/a` one was fixtured. `fail` travels the GATE_FAIL_VALUES path, `n/a` the
# GATE_FIELDS path: two different mechanisms, so one case cannot vouch for the other.
case("dev-ops task_verify: fail + PASS is rejected — no carve-out on this value either",
     "harness-dev-ops", """
VERDICT: PASS
DIGEST:
  headline: x
  change_type: config
  applied: []
  suite: n/a
  task: T-01
  task_verify: fail
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, "task_verify")
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
  fail_first: [{ sc: SC-01, evidence: "notes/qa-r1/fail-first-SC-01.txt" }]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
# (g2) REGRESSION by construction — `task` is in no schema at 4091b36 and unknown
# keys are ignored, so this was green then too. It cannot show the field was ADDED;
# (h2) is what can. Kept because an acceptance clause with no rejection partner is
# the vacuous shape this feature exists to remove.
# FEAT-1928 ruling: D-07's escape hatch is now spelled, not omitted — `task_verify: n/a`
# under `task: none` (accepted below); omitting it is a missing required field.
case("dev task: none with task_verify omitted is refused — the hatch is `n/a` now",
     "harness-backend-dev", _dev(task="none", tv=None), False, "missing 'task_verify'",
     complete=False)
case("dev-ops task: none with task_verify omitted is refused",
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
""", False, "missing 'task_verify'", complete=False)
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
     "harness-backend-dev", _dev(task="none", tv="fail"), False,
     ["task_verify='fail' but task=none", "!does not match"])
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
  fail_first: [{ sc: SC-01, evidence: "notes/qa-r1/fail-first-SC-01.txt" }]
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
  fail_first: [{ sc: SC-01, evidence: "notes/qa-r1/fail-first-SC-01.txt" }]
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
# (f, documentor half) REGRESSION — SC-05 names five persona families and documentor
# was the one with no accepted case at any commit. Completes the leak check.
case("a documentor digest carries neither new field and is still accepted",
     "harness-documentor", """
VERDICT: PASS
DIGEST:
  headline: x
  docs_updated: [.harness/harness/docs/SPEC.md]
  gaps: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", True)
case("code reviewer omission of code_grade is rejected",
     "harness-code-reviewer", """
VERDICT: PASS
DIGEST:
  headline: x
  severity_max: low
  findings: []
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, "code_grade")
# SEC-01/SC-19 follow-on: the missing-`code_grade` hint must name the four legal
# enum values, not the generic "`[]` if there are none" — `code_grade` is a
# single-value scalar, and that hint sent a reviewer straight into a second,
# guaranteed rejection (REQ-11's own defect class, `_missing_field_default_hint`).
case("code_grade's missing-field hint names the four legal values, not the list wording",
     "harness-code-reviewer", """
VERDICT: PASS
DIGEST:
  headline: x
  severity_max: low
  findings: []
  must_fix: []
  reviewed: "HEAD..HEAD"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: a.md
""", False, ["code_grade", "grade_2", "n_a", "!if there are none"])
# (11)(i2) — the hint CONTENT, both fields, both polarities. Exit code alone cannot
# see these: before REQ-11, `task_verify`'s hint said "write `none`", which the gate
# then rejects, and `task` would have inherited "write `[]`", which its regex rejects.
# The "no other NULLABLE field omitted" condition is load-bearing — another missing
# NULLABLE field emits the old hint into the same error list and false-reds the
# negative assertion.
case("task_verify's missing-field hint names its real values, not the none wording",
     "harness-backend-dev", _dev(tv=None), False, complete=False, mentions=
     # SC-18a: the hint must say what is rejected is a placeholder ALONGSIDE
     # `VERDICT: PASS` — never that placeholders are disallowed. That distinction is
     # what keeps `suite: n/a` + BLOCKED legal (REQ-03/SC-06), and the hint already
     # said it while nothing asserted it.
     ["task_verify", "pass", "fail", "alongside", "VERDICT: PASS",
      "!genuinely not applicable"])
case("task's missing-field hint names a task id, not the list wording",
     "harness-backend-dev", _dev(task=None), False,
     ["task", "T-NN", "none", "!if there are none"])
# FEAT-1928 ruling (REQ-11): a field that does not apply is spelled `none`, never omitted,
# so a missing nullable field's hint names its real type AND the `none` spelling.
case("a lead missing needs_approval is told true, false or `none`",
     "harness-validator-lead", LEAD_BLOCK, False,
     ["missing 'needs_approval'", "true or false, or `none` if it does not apply"],
     complete=False)
case("an orchestrator missing judgement is told the mapping or `none`",
     "harness-orchestrator", _reject_digest("", status="in_progress"), False,
     ["missing 'judgement'", "every key present, or `none` if it does not apply"],
     complete=False)

# =====================================================================
# FEAT-59 SC-06 / C2 — every finding carries a KIND. `findings` was an INT count
# (`findings: 2`), which told the routing layer how many and nothing about what
# they were; BUG-285 measured 5 of 8 re-cycle triggers were about DOCUMENT FORM,
# not code, and each one cost a cold three-layer dispatch. The kind is what lets
# a `form` finding be fixed in-run without a re-read and a `substance` finding
# re-gate only the tasks it names. A finding without one is undecidable and is
# rejected at source.
# =====================================================================

def _ui_review(findings):
    return f"""
VERDICT: FAIL
DIGEST:
  headline: one blocking finding
  severity_max: high
  findings:
{findings}
  must_fix: ["fail-open branch in auth"]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: notes/ui-review.md
"""


case("FEAT-59 finding without kind is rejected, naming the entry",
     "harness-ui-reviewer", _ui_review(
         '    - { severity: high, reader: ui-reviewer, summary: "fail-open branch" }'),
     False, "findings[0]: 'kind' is a required property")
case("FEAT-59 finding with a kind outside the enum is rejected, naming the value",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: style, severity: high, reader: ui-reviewer, summary: "fail-open branch" }'),
     False, ["findings[0]", "style", "substance", "form", "proportionality"])
# A near-miss must not be charitably normalised — the whole point of this validator.
case("FEAT-59 kind: substantive (near-miss) is rejected, not normalised",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: substantive, severity: high, reader: ui-reviewer, summary: "x" }'),
     False, ["findings[0]", "substantive"])
case("FEAT-59 a bare-string finding has no kind and is rejected",
     "harness-ui-reviewer", _ui_review('    - "fail-open branch in auth"'),
     False, "findings[0]: 'fail-open branch in auth' is not of type 'object'")
# The index in the message is the SECOND entry when the first is fine.
case("FEAT-59 the error names the offending entry's index, not the first",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: substance, scope: none, severity: high, reader: ui-reviewer, summary: "a", why: "the reader states its reason" }\n'
         '    - { severity: low, reader: ui-reviewer, summary: "b" }'),
     False, ["findings[1]", "!findings[0]"])
# Each member of the enum is ACCEPTED — inline and block-mapping styles both.
case("FEAT-59 kind: substance is accepted (inline entry)",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: substance, scope: none, severity: high, reader: ui-reviewer, summary: "fail-open branch", why: "the reader states its reason" }'),
     True)
case("FEAT-59 kind: form is accepted (block-mapping entry)",
     "harness-ui-reviewer", _ui_review(
         '    - kind: form\n'
         '      scope: none\n'
         '      severity: high\n'
         '      reader: ui-reviewer\n'
         '      summary: "DESIGN.md table header drifted"\n'
         '      why: "the table no longer matches DESIGN.md"'),
     True)
case("FEAT-59 kind: proportionality with scope: mission is accepted",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: proportionality, scope: mission, severity: high, reader: ui-reviewer, '
         'summary: "a plan for a five-line fix", why: "no design surface changes" }'),
     True)
case("DEC-228 kind: proportionality with scope: task is accepted",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: proportionality, scope: task, severity: med, reader: ui-reviewer, '
         'summary: "T-03 ships one-shot scaffolding as a durable flag", why: "the flag outlives T-03" }'),
     True)
# The BUG-285-canonical-reader defect: four task-scope findings summed into a mission downgrade.
# Without scope the route is undecidable, so a scope-less proportionality finding is refused.
case("DEC-228 kind: proportionality without scope is rejected, naming the entry",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: proportionality, severity: high, reader: ui-reviewer, '
         'summary: "a plan for a five-line fix" }'),
     False, "findings[0]: 'scope' is a required property")
case("DEC-228 kind: proportionality with a scope outside task|mission is rejected",
     "harness-ui-reviewer", _ui_review(
         '    - { kind: proportionality, scope: whole, severity: high, reader: ui-reviewer, '
         'summary: "a plan for a five-line fix" }'),
     False, ["findings[0]", "whole"])
# `findings: []` is the positive assertion "looked, found nothing" and stays legal.
case("FEAT-59 findings: [] is accepted — an explicit empty list asserts you looked",
     "harness-security-reviewer", """
VERDICT: PASS
DIGEST:
  headline: nothing security-relevant in the diff
  severity_max: none
  findings: []
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: notes/sec.md
""", True)
# The pre-FEAT-59 spelling is a CONTRACT VIOLATION now, not a count.
case("FEAT-59 findings as an INT count is rejected — it is a list of kinded entries",
     "harness-security-reviewer", """
VERDICT: PASS
DIGEST:
  headline: nothing security-relevant in the diff
  severity_max: none
  findings: 0
  must_fix: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: notes/sec.md
""", False, "findings: 0 is not of type 'array'")
# A validator-lead digest may carry the consolidated panel findings and the readers
# roster (PlanMerge's `record-panel --digest` reads both); the same kind rule binds.
case("FEAT-59 lead findings passthrough: kinded entries are accepted alongside readers:",
     "harness-validator-lead", LEAD_BLOCK.replace(
         "\n  sc_status: []",
         "\n  sc_status: []\n"
         "  readers: [{ reader: scope, status: ran, persona: harness-pm, reason: none }, { reader: should-not-exist, status: skipped, persona: fable-advisor, reason: host refusal }]\n"
         "  findings: [{ kind: substance, scope: none, severity: high, reader: scope, summary: \"SC-03 has no task\", why: \"the reader states its reason\" }]"),
     True)
case("FEAT-59 lead findings passthrough: an entry without kind is rejected",
     "harness-validator-lead", LEAD_BLOCK.replace(
         "\n  sc_status: []",
         "\n  sc_status: []\n"
         "  findings: [{ severity: high, reader: scope, summary: \"SC-03 has no task\" }]"),
     False, ["findings[0]", "kind"])

# =====================================================================
# FEAT-59 SC-17 / C3 — qa PASS needs FAIL-FIRST evidence. A green suite proves the
# tests pass; it does not prove they ever failed, and a test that never failed
# constrains nothing (harness-tdd-enforcement's Iron Law, now enforced at the
# digest). Per `verify: automated` SC the qa digest names the evidence that the
# test FAILED before the fix. `matrix_ok: n/a` ran no gate and may carry `[]`.
# =====================================================================

def _qa(verdict="PASS", matrix_ok="true", fail_first="[]", suite="pass"):
    return f"""
VERDICT: {verdict}
DIGEST:
  headline: suite green
  suite: {suite}
  failures: 0
  coverage_gaps: []
  matrix_ok: {matrix_ok}
  fail_first: {fail_first}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: notes/qa.md
"""


FAIL_FIRST_ONE = ('[{ sc: SC-01, evidence: '
                  '"notes/qa-r1/fail-first-SC-01.txt: 1 failed before 3f2a9c1" }]')

case("FEAT-59 qa PASS + matrix_ok: true + fail_first: [] is REJECTED — a green suite "
     "with no fail-first evidence is not a pass",
     "harness-qa", _qa(), False, ["fail_first", "fail-first"])
case("FEAT-59 qa PASS with populated fail_first is accepted",
     "harness-qa", _qa(fail_first=FAIL_FIRST_ONE), True)
case("FEAT-59 qa matrix_ok: n/a with fail_first: [] is accepted — no gate ran",
     "harness-qa", _qa(verdict="BLOCKED", matrix_ok="n/a", suite="n/a"), True)
case("FEAT-59 qa FAIL with fail_first: [] is accepted — the gate is on PASS",
     "harness-qa", _qa(verdict="FAIL", matrix_ok="false", fail_first="[]"), True)
case("FEAT-59 qa omitting fail_first is rejected — every field is required",
     "harness-qa", _qa().replace("  fail_first: []\n", ""), False, "fail_first")
# Entry shape: `{sc: SC-NN, evidence: <non-empty>}`. A bare string is not evidence
# for any named SC; an SC without evidence is a claim, not a receipt.
case("FEAT-59 fail_first entry without sc is rejected, naming the index",
     "harness-qa", _qa(fail_first='[{ evidence: "x.txt" }]'), False,
     ["fail_first[0]", "sc"])
case("FEAT-59 fail_first entry with empty evidence is rejected, naming the index",
     "harness-qa", _qa(fail_first='[{ sc: SC-01, evidence: "" }]'), False,
     ["fail_first[0]", "evidence"])
case("FEAT-59 fail_first bare-string entry is rejected",
     "harness-qa", _qa(fail_first='["SC-01 failed first"]'), False, ["fail_first[0]"])
case("FEAT-59 fail_first sc must be an SC-NN id",
     "harness-qa", _qa(fail_first='[{ sc: T-01, evidence: "x.txt" }]'), False,
     ["fail_first[0].sc", "^SC-"])
case("FEAT-59 fail_first block-mapping entries are accepted",
     "harness-qa", _qa().replace(
         "  fail_first: []",
         "  fail_first:\n"
         "    - sc: SC-01\n"
         "      evidence: notes/qa-r1/fail-first-SC-01.txt\n"
         "    - sc: SC-02\n"
         "      evidence: \"receipt: 2 failed, 0 passed at 3f2a9c1~1\""),
     True)


# (11)(j2-ii) JOINT HINT FOLLOWABILITY. Not expressible as independent cases: the
# point is that the two hints emitted TOGETHER license two repairs that both
# validate. Two individually-correct hints can still contradict each other — an
# agent following both literally would write `task: none` + `task_verify: pass`,
# which the conditional then rejects. That is REQ-11's own defect class re-created
# by REQ-11's fix, and the re-prompted return is NOT re-validated (validate-digest
# passes through on `stop_hook_active`), so the second attempt would ship unchecked.
def run_joint_hint_case():
    def run(text):
        r = subprocess.run([VALIDATE, "harness-backend-dev"],
                           input=json.dumps(fixture("harness-backend-dev", text, complete=False)),
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
    if "`n/a` if this dispatch carries no plan task" not in low:
        bad.append("task_verify's hint must license `n/a` under task: none")
    for label, text in (("task: none + task_verify: n/a", _dev(task="none", tv="n/a")),
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


# SEC-01: `REVIEW_SHA` stands in for a feature's `feature.json` `review_sha` — a
# real, resolvable commit, deliberately NOT `HEAD` (which moves as this repo
# gains commits) so an honest range stays honest across test runs.
#
# SEC-01 wave 4 (Q8): this is now FEAT-43's own real `review_sha`
# (`.harness/harness/features/FEAT-43-code-risk-grading/feature.json`), not
# `PRE_FEATURE_REVISION` — deliberately, because `check_reviewed_range` below
# needs a review_sha whose TRUE, repository-derived range (`merge-base(main,
# REVIEW_SHA)..REVIEW_SHA`) genuinely changes Python TODAY, so a forged
# self-consistent no-op AT this pin has something real to be caught hiding.
# Send-back 1: `check_reviewed_range`'s ambient-repo assertions no longer pin
# WHICH wave-4 reason the claim is refused for (see N_A_REFUSAL_SUBSTRINGS) —
# only that it IS refused — because this constant's own derived range stops
# meaning "genuinely changes Python" the moment FEAT-43 lands on main
# (REVIEW_SHA becomes an ancestor of origin/main: the range goes degenerate)
# or the checkout has no `origin/HEAD` at all; the reason-level pin for each
# of those shapes lives hermetically in `check_derived_base_range` and
# `check_unresolvable_default_branch` instead, against purpose-built /tmp
# repos where the environment is controlled, not ambient.
# `PRE_FEATURE_REVISION` stays available on its own name below for the cases
# that want an honest, resolvable ancestor with no such requirement.
REVIEW_SHA = "94383e671e51f95d142f3220f97c8e453721d516"


def make_feature_dir(root, review_sha=None, feat="FEAT-TEST", branch=None):
    """A minimal on-disk feature.json fixture at
    `<root>/.harness/harness/features/<feat>/feature.json`, carrying just the
    fields SEC-01's binding reads. Returns the feature directory, which
    `validate()`'s `feature_dir` override seam (mirrors `config_path`) accepts
    directly — no environment variable, no subprocess mocking.

    `branch` mirrors feature.json's own field, omitted by default (the shape
    the many existing fixtures need — no branch recorded at all): pass a
    string, including the literal `"none"` (a real recorded state — FEAT-01,
    FEAT-15, FEAT-19), to exercise the wave 3 branch corroboration.
    """
    feature_dir = os.path.join(root, ".harness", "harness", "features", feat)
    os.makedirs(feature_dir, exist_ok=True)
    doc = {"feature_id": feat,
           "review_sha": REVIEW_SHA if review_sha is None else review_sha}
    if branch is not None:
        doc["branch"] = branch
    with open(os.path.join(feature_dir, "feature.json"), "w") as f:
        json.dump(doc, f)
    return feature_dir


def reviewer_digest(code_grade="pass", files="[]", must_fix="[]", severity_max="low",
                    reviewed=None, grade_2_reasons="[]", artifact="a.md"):
    # SEC-01: NOT a self-consistent no-op pair (base == head) — that shape is
    # the exact bypass this feature closes, and reviewer_digest()'s own default
    # used to BE it (base == head == PRE_FEATURE_REVISION), so every case that
    # relied on the default was only ever "accepted" because base and head
    # happened to be equal, never because head was checked against anything.
    # `HEAD` and `REVIEW_SHA` differ by construction (see above); head alone is
    # what SEC-01 binds, so an honest default needs no particular base.
    reviewed = reviewed or f"HEAD..{REVIEW_SHA}"
    return f"""VERDICT: PASS
DIGEST:
  headline: reviewer result
  severity_max: {severity_max}
  findings: []
  must_fix: {must_fix}
  code_grade: {code_grade}
  reviewed: "{reviewed}"
  grade_2_reasons: {grade_2_reasons}
  files_touched: {files}
  open_questions: []
  expertise_update: []
artifact: {artifact}
"""


def _write_plan_approval(plan_path, status):
    with open(plan_path, "w") as handle:
        handle.write(
            f"schema: plan/1\nfeature: FEAT-PLAN\napproval:\n  status: {status}\n"
            "tasks:\n"
            "  - id: T-01\n"
            "    title: fixture task\n"
            "    change_type: test\n"
            "    execution_mode: main-session-direct\n"
            "    files: [fixture.py]\n"
            "    verify: \"true\"\n"
            "    intent: exercise plan review validation\n"
        )


def _plan_review_fixture(root):
    feature_dir = os.path.join(root, ".harness", "harness", "features", "FEAT-PLAN")
    os.makedirs(os.path.join(feature_dir, "notes"), exist_ok=True)
    plan_path = os.path.join(feature_dir, "plan.yaml")
    _write_plan_approval(plan_path, "pending")
    artifact = os.path.join(feature_dir, "notes", "review-plan.md")
    digest = reviewer_digest("n_a", reviewed=f"plan:{plan_path}", artifact=artifact)
    return feature_dir, plan_path, artifact, digest


def _plan_review_errors(validator, config, feature_dir, digest, branch_override=None):
    return validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", digest), config, feature_dir, branch_override
    )


def _load_validator(tag):
    spec = importlib.util.spec_from_file_location(tag, VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator


def _write_verification_brief(path, brief):
    if brief is None:
        os.remove(path)
        return
    with open(path, "wb") as handle:
        handle.write(brief.encode("utf-8") if isinstance(brief, str) else brief)


def run_qa_verification_mode_cases():
    validator = _load_validator("_qa_verification_modes")
    cases = (
        ("inspection and UAT", "- SC-01: inspect\n  verify: inspection\n"
         "- SC-02: exercise\n  verify: uat\n", True),
        ("perspective-tagged criteria", "- SC-01 (operator): exercise\n  verify: uat\n"
         "- SC-02 (reader): inspect\n  verify: inspection\n", True),
        ("automated", "- SC-01: exercise\n  verify: automated\n", False),
        ("missing mode before UAT", "- SC-01: unknown\n"
         "- SC-02: exercise\n  verify: uat\n", False),
        ("unknown mode", "- SC-01: exercise\n  verify: manual\n", False),
        ("no criteria", "# BRIEF\n", False),
        ("missing brief", None, False),
        ("undecodable brief", b"\xff", False),
    )
    failures = []
    with tempfile.TemporaryDirectory(prefix="qa-modes-") as root:
        feature_dir = make_feature_dir(root)
        brief_path = os.path.join(feature_dir, "BRIEF.md")
        for label, brief, accepted in cases:
            _write_verification_brief(brief_path, brief)
            errors = validator._qa_errors(
                {"suite": "pass", "failures": 0, "matrix_ok": True,
                 "fail_first": [], "kinds": []}, "PASS", feature_dir)
            rejected = any("fail_first" in error for error in errors)
            valid = not errors if accepted else rejected
            if not valid:
                failures.append(f"{label}: {errors}")
    for failure in failures:
        print(f"FAIL: {failure}")
    return len(failures)


_T04_UNIVERSAL = "  files_touched: []\n  open_questions: []\n  expertise_update: []\n"
_T04_BASES = {
    "harness-dev-ops": "  change_type: ci\n  applied: []\n  suite: pass\n  task: T-01\n  task_verify: pass\n",
    "harness-security-reviewer": "  severity_max: none\n  findings: []\n  must_fix: []\n",
    "harness-ui-reviewer": "  severity_max: none\n  findings: []\n  must_fix: []\n",
    "harness-qa": ("  suite: pass\n  failures: 0\n  coverage_gaps: []\n  matrix_ok: n/a\n"
                   "  fail_first: []\n"),
    "harness-documentor": "  docs_updated: []\n  gaps: []\n",
    "harness-visual-designer": "  contract: written\n  mockups: []\n  direction_choices: []\n",
    "harness-orchestrator": ("  feature: FEAT-X\n  status: in_progress\n  runs: []\n"
                             "  cycles_used: 0\n  briefing: none\n"),
}


def _t04_base_digest(persona):
    """A minimal valid return for one persona, in fixture notation."""
    if persona == "harness-backend-dev":
        return _dev()
    if persona == "harness-eng-lead":
        return LEAD_BLOCK
    if persona == "harness-pm":
        return PM_OK
    return (f"VERDICT: BLOCKED\nDIGEST:\n  headline: base return\n{_T04_BASES[persona]}"
            f"{_T04_UNIVERSAL}artifact: a.md\n")


def _t04_with_fields(text, fields):
    lines = "\n".join(
        f"  {field}: {json.dumps(value)}" for field, value in fields.items())
    return text.replace("\nartifact:", "\n" + lines + "\nartifact:")


def _t04_canonical_failures(validator, probes):
    failures = []
    for canonical, persona in probes.items():
        base = fixture(persona, _t04_base_digest(persona))
        if validator.validate(persona, base):
            failures.append(f"{canonical}: the base return is not valid: "
                            f"{validator.validate(persona, base)}")
        rogue = f"rogue_{canonical.replace('-', '_')}"
        errors = validator.validate(persona, fixture(persona, _t04_with_fields(
            _t04_base_digest(persona), {rogue: 1})))
        if not any("undeclared digest key" in error and rogue in error for error in errors):
            failures.append(f"{canonical}: one undeclared key was accepted: {errors}")
    return failures


def _t04_three_key_failures(validator, digest):
    errors = [
        error for error in validator.validate("harness-eng-lead", fixture("harness-eng-lead", digest))
        if "undeclared digest key" in error
    ]
    if len(errors) != 1:
        return [f"three undeclared keys produced {len(errors)} messages"]
    message = errors[0]
    tokens = (
        "rogue_alpha", "rogue_beta", "rogue_gamma",
        "digest contract is closed", "digest-schemas/harness-eng-lead.json",
    )
    return [
        f"three-key message omitted {token}"
        for token in tokens if token not in message
    ]


def _t04_hook_failures(digest):
    failures = []
    base = {
        "agent_type": "harness-eng-lead",
        "digest_object": fixture("harness-eng-lead", digest),
    }
    # BUG-1898: every --hook fire names a throwaway root; unrooted, these resolved to the live
    # checkout and released a persona's real claim there.
    env = dict(os.environ, HARNESS_PROJECT_DIR=_isolated_root())
    rejected = subprocess.run(
        [sys.executable, VALIDATE, "--hook"], input=json.dumps(_governed(base)),
        capture_output=True, text=True, env=env)
    if rejected.returncode != 2:
        failures.append(f"hook returned {rejected.returncode}, not exit 2")
    bypassed = subprocess.run(
        [sys.executable, VALIDATE, "--hook"],
        input=json.dumps(_governed({**base, "stop_hook_active": True})),
        capture_output=True, text=True, env=env)
    if bypassed.returncode != 0:
        failures.append(
            f"stop_hook_active passthrough returned {bypassed.returncode}")
    return failures


def _t04_lead_field_failures(validator):
    """T-08's object half: every optional field a lead carries up from a member is accepted
    on a lead, and a member-only field (qa's) is refused there as undeclared."""
    failures = []
    carried = {"sc_status": [], "needs_approval": False, "severity_max": "none",
               "matrix_ok": True, "coverage_gaps": [], "readers": [], "findings": []}
    for field, value in carried.items():
        errors = validator.validate("harness-eng-lead", fixture("harness-eng-lead", _t04_with_fields(LEAD_BLOCK, {field: value})))
        if errors:
            failures.append(f"declared lead field {field} was rejected: {errors}")
    for field in ("failures", "suite", "kinds"):
        errors = validator.validate("harness-eng-lead", fixture("harness-eng-lead", _t04_with_fields(LEAD_BLOCK, {field: []})))
        if not any("undeclared digest key" in error for error in errors):
            failures.append(f"member-only field {field} was accepted on a lead")
    return failures


def run_t04_unknown_key_cases():
    """T-04: the digest key set is closed and one refusal is sufficient."""
    validator = _load_validator("_validator_t04")
    canonical_probes = {
        "pm": "harness-pm", "dev": "harness-backend-dev",
        "qa": "harness-qa", "reviewer": "harness-security-reviewer",
        "ui-reviewer": "harness-ui-reviewer",
        "visual-designer": "harness-visual-designer",
        "documentor": "harness-documentor", "dev-ops": "harness-dev-ops",
        "lead": "harness-eng-lead", "orchestrator": "harness-orchestrator",
    }
    three = _t04_with_fields(
        LEAD_BLOCK, {"rogue_alpha": 1, "rogue_beta": 2, "rogue_gamma": 3})
    failures = _t04_canonical_failures(validator, canonical_probes)
    failures.extend(_t04_three_key_failures(validator, three))
    failures.extend(_t04_hook_failures(three))
    failures.extend(_t04_lead_field_failures(validator))
    for failure in failures:
        print("FAIL  [T-04] " + failure)
    total = 2 * len(canonical_probes) + 7 + 10
    print(f"\n{total - len(failures)}/{total} T-04 undeclared digest key cases passed.")
    return len(failures)


def _check_plan_approval_states(
        validator, config, feature_dir, plan_path, artifact, digest, failures):
    errors = _plan_review_errors(validator, config, feature_dir, digest)
    if errors:
        failures.append(
            f"a pending plan review with no feature.json/review_sha must accept: {errors}"
        )

    _write_plan_approval(plan_path, "approved")
    errors = _plan_review_errors(validator, config, feature_dir, digest)
    if not any("pending" in error.lower() for error in errors):
        failures.append("plan review mode must reject an already-approved plan")

    _write_plan_approval(plan_path, "pending")
    wrong_grade = reviewer_digest(
        "pass", reviewed=f"plan:{plan_path}", artifact=artifact
    )
    errors = _plan_review_errors(validator, config, feature_dir, wrong_grade)
    if not any("n_a" in error for error in errors):
        failures.append("plan review mode must reject a code_grade other than n_a")


def _check_plan_feature_binding(validator, config, feature_dir, digest, failures):
    feature_json = os.path.join(feature_dir, "feature.json")
    with open(feature_json, "w") as handle:
        json.dump({"review_sha": REVIEW_SHA, "branch": "feat/FEAT-PLAN"}, handle)
    errors = _plan_review_errors(validator, config, feature_dir, digest)
    if not any("pre-signature" in error for error in errors):
        failures.append("plan review mode must reject a feature with a pinned review_sha")

    with open(feature_json, "w") as handle:
        json.dump({"review_sha": "none", "branch": "feat/FEAT-PLAN"}, handle)
    errors = _plan_review_errors(
        validator, config, feature_dir, digest, branch_override="feat/OTHER"
    )
    if not any("does not match" in error for error in errors):
        failures.append("plan review mode must reject a different current branch")


def check_pending_plan_review(validator, config, root, failures):
    """DEC-207: a pre-signature plan review has no review_sha or code diff."""
    feature_dir, plan_path, artifact, digest = _plan_review_fixture(root)
    _check_plan_approval_states(
        validator, config, feature_dir, plan_path, artifact, digest, failures
    )
    _check_plan_feature_binding(validator, config, feature_dir, digest, failures)


def check_review_policy(validator, config, feature_dir, failures):
    guarded = reviewer_digest("pass", must_fix="[needs repair]")
    if not any("review policy" in error for error in validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", guarded), config, feature_dir)):
        failures.append("advisory_unless_high must reject must_fix with PASS")
    if validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest(severity_max="none")), config, feature_dir):
        failures.append("none severity must be accepted by review policy")
    if not any("severity_max" in error for error in validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest(severity_max="info")),
            config, feature_dir)):
        failures.append("info severity must be rejected by the policy vocabulary")
    return guarded


def check_prior_validator(td, guarded, failures):
    """SC-20 clause 4: the PRIOR revision of the validator must accept the guarded digest too,
    proving the rejection this suite exercises is NEW rather than a hardcoded always-reject.

    Hermetic per the Q11 cycle-27 ruling: no `git show`, no repository history. The prior
    revision's bytes are committed as inert fixture data (non-`.py` suffix, so
    `code_grade._changed_python_files` never selects them) and written into a temp dir under
    their real module filenames, exactly as the git-backed version did.
    """
    prior_dir = os.path.join(td, "prior")
    os.makedirs(prior_dir)
    for name, fixture in (("validate-digest.py", "prior-validate-digest.py.fixture"),
                          ("harness_yaml.py", "prior-harness_yaml.py.fixture")):
        with open(os.path.join(FIXTURE_DIR, fixture), encoding="utf-8") as f:
            source = f.read()
        with open(os.path.join(prior_dir, name), "w") as f:
            f.write(source)
    prior = subprocess.run(
        [sys.executable, os.path.join(prior_dir, "validate-digest.py"),
         "harness-code-reviewer"],
        # FEAT-59 turned `findings` from an int count into a kinded list; the PRIOR
        # revision's contract spelled the empty case `findings: 0`, and this control is
        # about the review-policy rejection being new, not about the findings shape.
        input=guarded.replace("findings: []", "findings: 0"), capture_output=True, text=True)
    if prior.returncode != 0:
        failures.append("previous validator must accept the gated digest")


def write_review_config(config, review):
    with open(config, "w") as f:
        json.dump({"gates": {"review": review}}, f)


def check_code_grade_state(validator, config, feature_dir, failures):
    if not any("code_grade" in error for error in validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("fail")), config, feature_dir)):
        failures.append("fail-plus-PASS must reject")
    reasoned_grade_2 = reviewer_digest(
        "grade_2", grade_2_reasons="[one auditable reason]")
    if not any("expected 'pass'" in error for error in validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reasoned_grade_2), config, feature_dir)):
        failures.append("a reasoned grade_2 claim over a range that grades 'pass' must "
                        "still reject on the mechanical mismatch — a written reason "
                        "buys the VERDICT, never the grade")
    if not any("grade_2_reasons" in error for error in validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("grade_2")), config, feature_dir)):
        failures.append("grade_2 without written reasons must reject")


# Send-back 1 (sec01-derived-base-sendback): the three ambient-repo n_a cases
# in `check_reviewed_range` run against THIS repository's real, live state —
# exogenous to the defect they guard. Pinning a single wave-4 refusal reason
# (e.g. "only valid") there is a false failure waiting to happen: the moment
# FEAT-43 lands on main by a non-squash merge, REVIEW_SHA becomes an ancestor
# of origin/main and the SAME correct fix refuses with "already an ancestor"
# instead; a checkout with no `origin/HEAD` at all (a fresh `git init`, some
# CI checkouts) refuses with "default branch ... could not be resolved"
# instead. Neither is a regression. So here we assert only what the ambient
# cases CAN prove without depending on ambient repo state: `code_grade: n_a`
# is refused for one of wave-4's own named reasons — never that some
# unrelated schema error tripped instead (a bare `if errors:` would pass
# vacuously on that). The exact-reason discrimination is not lost: each
# reason is pinned precisely, hermetically, in `check_derived_base_range`
# ("only valid", "already an ancestor of the default branch") and
# `check_unresolvable_default_branch` ("default branch"), against
# purpose-built /tmp repos where the environment is controlled.
N_A_REFUSAL_SUBSTRINGS = (
    "disagrees with the mechanical result",  # BUG-1081: the computed result is not n_a
    "already an ancestor of the default",   # degenerate: review_sha merged in
    "default branch",                       # origin/HEAD unresolvable
    "no merge base",                        # merge-base could not be computed
)


def _assert_n_a_rejects(validator, config, feature_dir, reviewed, message, failures):
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("n_a", reviewed=reviewed)),
            config, feature_dir)
    if not any(substring in error for error in errors
               for substring in N_A_REFUSAL_SUBSTRINGS):
        failures.append(f"{message}: {errors}")


def _check_option_like_revisions(validator, config, feature_dir, td, failures):
    output_path = os.path.join(td, "must-not-exist")
    for revision in ("--no-patch..HEAD", f"--output={output_path}..HEAD"):
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("n_a", reviewed=revision)),
            config, feature_dir)
        if not any("reviewed range" in error for error in errors):
            failures.append(f"option-like revision {revision!r} must reject")
    if os.path.exists(output_path):
        failures.append("option-like review revision must not write an output file")


def check_reviewed_range(validator, config, feature_dir, td, failures):
    _assert_n_a_rejects(validator, config, feature_dir, f"{PRE_FEATURE_REVISION}..HEAD",
                        "n_a with a reviewed Python diff must reject", failures)
    # SEC-01 wave 4 (Q8): a self-consistent no-op AT the pin (base == head ==
    # review_sha) used to be the exact bypass this feature closes — a digest
    # that is BOTH an honest binding (head matches review_sha) and trivially
    # empty for the OLD digest-named diff check bought `code_grade: n_a` for
    # free. The n_a decision no longer reads `reviewed:` at all: it is
    # `merge-base(main, review_sha)..review_sha`, and REVIEW_SHA's true
    # derived range genuinely changes Python (chosen for exactly that reason
    # — see the constant's own comment), so this forged shape must now
    # REJECT, not accept — this is the case that never existed before this
    # fix, reproducing the live security-reviewer bypass at this feature's
    # own pin.
    _assert_n_a_rejects(validator, config, feature_dir, f"{REVIEW_SHA}..{REVIEW_SHA}",
                        "a forged no-op AT review_sha itself must reject — the "
                        "n_a decision must never read the digest's own reviewed:",
                        failures)
    # Q8 closes the whole class, not this one shape: an ancestor pair ending
    # at review_sha is exactly as forgeable as base == head and must reject
    # the same way (Q2, closed — not a backlog row).
    _assert_n_a_rejects(validator, config, feature_dir, f"{REVIEW_SHA}~1..{REVIEW_SHA}",
                        "<review_sha>~1..<review_sha> is inside the class Q8 "
                        "closes and must also reject", failures)
    _check_option_like_revisions(validator, config, feature_dir, td, failures)


# --- BUG-1081: the mechanical code-grade result is COMPUTED, never trusted -------
#
# FEAT-43 confirmed only that a reviewer's report ENDED at review_sha; for `pass`,
# `fail` and `grade_2` it never ran the grader, so a review passed when code-grade.py
# was skipped, crashed, or reported a blocking result as a clean one (issue #1081).
# Every case below drives the REAL `validate()` / `--hook` surfaces against a
# purpose-built repository — never a stub of the derivation under test.
#
# RED, MEASURED AGAINST THE PRE-FIX TREE before any of this was written. The pre-fix
# validator resolved every commit against the process cwd, which is how the hook ran in
# production (it fires inside the checkout under review), so the reproduction was run
# with cwd inside the fixture repo — running it from anywhere else would only have shown
# that unrelated OIDs do not resolve, which is a different failure and not this defect:
#
#   --- blocking production function (src/blocking.py, grade 1, bar 4)
#       canonical range : a77e55df096f..9a4fc0a7a211
#       digest claims   : code_grade: pass
#       validate()      : errors=[]
#       --hook exit     : 0
#       --hook stderr   : ''
#   --- committed syntax error (src/broken.py, `def broken(:`)
#       canonical range : a77e55df096f..c09ced91c984
#       digest claims   : code_grade: pass
#       validate()      : errors=[]
#       --hook exit     : 0
#       --hook stderr   : ''
#
# Both were ACCEPTED at exit 0 with the grader never invoked, which is issue #1081 in
# two lines. `check_hook_rejects_false_pass` and `check_committed_syntax_error` below
# are those two cases, now asserting exit 2 and a named reason.

HARNESS_JSON_FIXTURE = {
    "gates": {"review": "advisory_unless_high"},
    "test_kinds": {
        "unit": {"detect": "test_*.py|**/test-*.py", "exclude": "",
                 "cmd": "true", "status": "active"},
    },
}

# Grades below are MEASURED with `code_grade.grade_source`, not asserted from taste,
# and each function is NEW in the head commit so `gated_set()` gates it (no pre-image).
CLEAN_PY = "def add(a, b):\n    return a + b\n"                      # grade 5 -> pass

BLOCKING_PY = (                                                       # grade 1 -> fail
    "def blocking(values):\n"
    "    total = 0\n"
    + "".join(
        f"    if values.get({index!r}):\n"
        f"        for item in values[{index!r}]:\n"
        f"            if item:\n"
        f"                total += item\n"
        for index in range(8)
    )
    + "    return total\n"
)

GRADE_2_PY = (                                          # cyclomatic 12 -> grade exactly 2
    "def moderate(flags):\n"
    "    total = 0\n"
    + "".join(f"    if flags[{index}]:\n        total += {index}\n" for index in range(11))
    + "    return total\n"
)

SYNTAX_ERROR_PY = "def broken(:\n    return 1\n"


def _fresh_validator():
    """A freshly-imported validator module, so a case that monkeypatches one name
    cannot leak into another's run."""
    spec = importlib.util.spec_from_file_location("_bug1081_validator", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_repo_file(repo, relative, content):
    path = os.path.join(repo, *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(content)
    return path


def make_graded_repo(td, name, head_files, base_files=None, removals=()):
    """A purpose-built repo whose CANONICAL range — `merge-base(origin/HEAD, head)..head`,
    the range the repository derives and the digest cannot name — contains exactly
    `head_files` plus `removals`.

    Commit A carries `readme.txt`, `.harness/harness.json` and any `base_files`, and is
    mirrored as `origin/main` + `origin/HEAD`; the head commit is a sibling child of A, so
    the range is real and never degenerate. Returns `(repo, base_oid, head_oid)`.
    """
    repo = os.path.join(td, name)
    _init_test_repo(repo)
    for relative, content in (base_files or {}).items():
        _write_repo_file(repo, relative, content)
    base_oid = _commit_file(repo, "readme.txt", "a\n", "A")
    _git_quiet(repo, "update-ref", "refs/remotes/origin/main", base_oid)
    _git_quiet(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
               "refs/remotes/origin/main")
    for relative in removals:
        _git_quiet(repo, "rm", "-q", relative)
    for relative, content in head_files.items():
        _write_repo_file(repo, relative, content)
    head_oid = _commit_file(repo, "head.txt", "b\n", "head")
    return repo, base_oid, head_oid


def _reviewer_digest_for(result, base_oid, head_oid, artifact="a.md"):
    """A digest claiming `result` over `base..head`, carrying the VERDICT and the
    grade-2 reasons that result's OWN pre-existing rules already require — so a
    rejection below is the mechanical mismatch, never an unrelated schema error."""
    # The reason NAMES the graded function: a reason naming none is refused (consumer audit).
    extra = {"grade_2_reasons": "[moderate is a dispatch table]"} if result == "grade_2" else {}
    digest = reviewer_digest(result, reviewed=f"{base_oid}..{head_oid}",
                             artifact=artifact, **extra)
    if result == "fail":
        digest = digest.replace("VERDICT: PASS", "VERDICT: FAIL", 1)
    return digest


def _run_hook(root, agent_type, text):
    """Drive the REAL SubagentStop entry path: JSON on stdin, `root` as the resolved
    checkout. Returns `(exit_code, stderr)` — the exit code matters exactly, because
    only 2 rejects and a crash exits 1 while the digest ships unvalidated (DEC-127)."""
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = root
    payload = {"agent_type": agent_type, "digest_object": fixture(agent_type, text)}
    result = subprocess.run([VALIDATE, "--hook"], input=json.dumps(_governed(payload)),
                            capture_output=True, text=True, env=env)
    return result.returncode, result.stderr


def _hookable_repo(td, name, head_files, feat, base_files=None, removals=()):
    """`make_graded_repo` plus the two files hook mode itself reads, and a feature.json
    pinned at the head commit. Returns `(repo, base_oid, head_oid, artifact)`."""
    repo, base_oid, head_oid = make_graded_repo(td, name, head_files, base_files, removals)
    _write_repo_file(repo, ".harness/team-config.yaml", "agents: {}\n")
    make_feature_dir(repo, review_sha=head_oid, feat=feat)
    return repo, base_oid, head_oid, f".harness/harness/features/{feat}/notes/review.md"


# (name, head files, the result the repository computes, one wrong claim for it)
GRADE_FIXTURES = (
    ("pass", {"src/clean.py": CLEAN_PY}, "pass", "fail"),
    ("fail", {"src/blocking.py": BLOCKING_PY}, "fail", "pass"),
    ("grade2", {"src/moderate.py": GRADE_2_PY}, "grade_2", "pass"),
    ("na", {"docs/notes.md": "prose only\n"}, "n_a", "pass"),
)


def check_mechanical_result_discrimination(td, failures):
    """SC-01/SC-02/SC-03: every canonical range ACCEPTS the matching claim and REJECTS a
    wrong one, naming the expected value.

    The accept half is what makes this discrimination rather than a validator wired to
    refuse every graded code review — a rejection-only suite would pass against one.
    No `chdir`: the range is derived from the checkout that owns the feature directory,
    so a case that depended on the process cwd would fail here.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "bug1081-config.json")
    write_review_config(config, "advisory_unless_high")
    for name, head_files, expected, wrong in GRADE_FIXTURES:
        repo, base_oid, head_oid = make_graded_repo(td, f"grade-{name}", head_files)
        feature_dir = make_feature_dir(repo, review_sha=head_oid,
                                       feat=f"FEAT-GRADE-{name.upper()}")
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for(expected, base_oid, head_oid)),
            config, feature_dir)
        if errors:
            failures.append(f"a canonical range grading {expected!r} must ACCEPT the "
                            f"matching claim: {errors}")
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for(wrong, base_oid, head_oid)),
            config, feature_dir)
        if not any(f"expected {expected!r}" in error for error in errors):
            failures.append(f"code_grade={wrong!r} over a range grading {expected!r} "
                            f"must reject AND name the expected value: {errors}")


def check_hook_rejects_false_pass(td, failures):
    """SC-01 through the REAL hook path: a `code_grade: pass` claim over a canonical
    range that adds a blocking production function must exit exactly 2.

    Exit 2 exactly, because only 2 blocks (DEC-100/DEC-122) and a crash exits 1 — a
    validator that fell over here would look like a refusal while the digest shipped
    unvalidated. `SC-02`'s counterpart runs in the same repo: the HONEST `fail` claim
    with `VERDICT: FAIL` must be accepted at exit 0.
    """
    repo, base_oid, head_oid, artifact = _hookable_repo(
        td, "hook-blocking", {"src/blocking.py": BLOCKING_PY}, "FEAT-HOOK-BLOCKING")
    code, stderr = _run_hook(repo, "harness-code-reviewer",
                             _reviewer_digest_for("pass", base_oid, head_oid, artifact))
    if code != 2:
        failures.append(f"the hook must reject a false code_grade='pass' with exit 2, "
                        f"got {code}: {stderr}")
    if "expected 'fail'" not in stderr:
        failures.append(f"the hook's refusal must name the expected value: {stderr}")
    if "Traceback" in stderr:
        failures.append(f"the hook must refuse, not crash: {stderr}")
    code, stderr = _run_hook(repo, "harness-code-reviewer",
                             _reviewer_digest_for("fail", base_oid, head_oid, artifact))
    if code != 0:
        failures.append(f"the hook must ACCEPT the honest code_grade='fail' with "
                        f"VERDICT: FAIL, got exit {code}: {stderr}")


def check_committed_syntax_error(td, failures):
    """SC-04: a committed Python file in the canonical range that does not parse REFUSES
    the digest with a named grading error and NO traceback — through the real hook, at
    exit 2 rather than the crash-shaped exit 1. Before the fix the same digest was
    accepted at exit 0, having graded nothing at all.
    """
    repo, base_oid, head_oid, artifact = _hookable_repo(
        td, "hook-syntax", {"src/broken.py": SYNTAX_ERROR_PY}, "FEAT-HOOK-SYNTAX")
    code, stderr = _run_hook(repo, "harness-code-reviewer",
                             _reviewer_digest_for("pass", base_oid, head_oid, artifact))
    if code != 2:
        failures.append(f"a committed syntax error must refuse the digest at exit 2, "
                        f"got {code}: {stderr}")
    if "does not parse" not in stderr:
        failures.append(f"the grading failure must be NAMED, not generic: {stderr}")
    if "Traceback" in stderr:
        failures.append(f"a grading crash must be converted to a refusal: {stderr}")


def check_digest_base_cannot_move_result(td, failures):
    """SC-05: the digest's own base is a reported value that is cross-checked, never an
    input that decides.

    `A -> B (adds the blocking function) -> C`, with `review_sha` at C. A digest naming
    the canonical base A and one naming B — whose OWN range excludes the blocking
    function entirely — must produce the SAME `fail`; and a head that is not `review_sha`
    must still be refused by the binding.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "digest-base-config.json")
    write_review_config(config, "advisory_unless_high")
    repo = os.path.join(td, "digest-base-repo")
    _init_test_repo(repo)
    oid_a = _commit_file(repo, "readme.txt", "a\n", "A")
    _git_quiet(repo, "update-ref", "refs/remotes/origin/main", oid_a)
    _git_quiet(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
               "refs/remotes/origin/main")
    _write_repo_file(repo, "src/blocking.py", BLOCKING_PY)
    oid_b = _commit_file(repo, "b.txt", "b\n", "B adds the blocking function")
    oid_c = _commit_file(repo, "c.txt", "c\n", "C")
    feature_dir = make_feature_dir(repo, review_sha=oid_c, feat="FEAT-DIGEST-BASE")
    for base in (oid_a, oid_b):
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("pass", base, oid_c)),
            config, feature_dir)
        if not any("expected 'fail'" in error for error in errors):
            failures.append(f"a digest-supplied base ({base[:12]}) must not change the "
                            f"mechanical result: {errors}")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("fail", oid_a, oid_b)),
        config, feature_dir)
    if not any("review_sha" in error for error in errors):
        failures.append(f"the digest's HEAD must still be bound to review_sha: {errors}")


def check_deletion_only_range(td, failures):
    """D-04: a canonical range whose only Python change is a DELETION grades `pass`, not
    `n_a` — a Python path changed, there is simply no head-side function left to gate.
    Pinned in both directions so the boundary cannot drift to either neighbour.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "deletion-config.json")
    write_review_config(config, "advisory_unless_high")
    repo, base_oid, head_oid = make_graded_repo(
        td, "deletion-only", {}, base_files={"src/gone.py": CLEAN_PY},
        removals=("src/gone.py",))
    feature_dir = make_feature_dir(repo, review_sha=head_oid, feat="FEAT-DELETION")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("pass", base_oid, head_oid)),
        config, feature_dir)
    if errors:
        failures.append(f"a deletion-only Python range must accept 'pass': {errors}")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("n_a", base_oid, head_oid)),
        config, feature_dir)
    if not any("expected 'pass'" in error for error in errors):
        failures.append(f"a deletion-only Python range is not n_a: {errors}")


def check_missing_test_kinds(td, failures):
    """SC-11/D-05: a checkout whose harness.json carries no `test_kinds` cannot tell a
    production path from a test path, so no grade bar can be resolved. Refuse and name
    the repair — never fall back to an implicit production bar, and never to the
    digest's own claim.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "no-kinds-config.json")
    write_review_config(config, "advisory_unless_high")
    repo, base_oid, head_oid = make_graded_repo(
        td, "no-test-kinds", {"src/clean.py": CLEAN_PY})
    _write_repo_file(repo, ".harness/harness.json", json.dumps({"gates": {}}))
    feature_dir = make_feature_dir(repo, review_sha=head_oid, feat="FEAT-NO-KINDS")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("pass", base_oid, head_oid)),
        config, feature_dir)
    if not any("test_kinds" in error for error in errors):
        failures.append(f"a checkout with no test_kinds policy must refuse the code "
                        f"grade and name it: {errors}")


def check_malformed_test_kinds(td, failures):
    """SC-11/REQ-03: a MALFORMED `test_kinds` policy — well-shaped enough to load, but a
    kind with no `detect` — reaches the grader and raises there, and that exception must
    become a named refusal rather than an acceptance.

    This case exists because a mutation proved the need for it: converting the grading
    catch-all into `return "pass", None` reddened NOTHING, so the branch was unreachable
    from the suite and its greenness meant nothing. A missing `detect` is the reachable
    production shape of it — `_load_test_kinds` cannot see inside a kind, so the failure
    surfaces inside `classify`.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "malformed-kinds-config.json")
    write_review_config(config, "advisory_unless_high")
    repo, base_oid, head_oid = make_graded_repo(
        td, "malformed-test-kinds", {"src/clean.py": CLEAN_PY})
    _write_repo_file(repo, ".harness/harness.json", json.dumps(
        {"gates": {}, "test_kinds": {"unit": {"status": "active"}}}))
    feature_dir = make_feature_dir(repo, review_sha=head_oid, feat="FEAT-BAD-KINDS")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", _reviewer_digest_for("pass", base_oid, head_oid)),
        config, feature_dir)
    if not any("TestKindsError" in error for error in errors):
        failures.append(f"a grader exception must become a NAMED refusal, never an "
                        f"acceptance: {errors}")
    if not any(error.startswith("code_grade cannot be verified") for error in errors):
        failures.append(f"the grading failure must be reported as a code_grade "
                        f"verification failure: {errors}")


HOSTILE_ARTIFACT_PATHS = (
    ".harness/../features/../notes/fake.md",
    ".harness/./features/../notes/fake.md",
    ".harness/harness/features/../notes/fake.md",
    ".harness/../harness/features/FEAT-TRAVERSAL/notes/fake.md",
)


def _assert_honest_artifact_resolves(validator, repo, failures):
    """The accept half: a real artifact path still resolves, and the root it yields is
    the checkout it names. Without this, a validator wired to refuse every artifact path
    would pass the refusal cases below."""
    honest = ".harness/harness/features/FEAT-TRAVERSAL/notes/review.md"
    feature_dir, error = validator._feature_dir_from_artifact(honest, repo)
    expected = os.path.join(repo, ".harness", "harness", "features", "FEAT-TRAVERSAL")
    if error or feature_dir != expected:
        failures.append(f"an honest artifact path must still resolve: "
                        f"{feature_dir!r} {error!r}")
    elif validator._repo_root_for_feature(feature_dir) != os.path.realpath(repo):
        failures.append("an honest artifact path must resolve the root it names")


def check_artifact_path_traversal(td, failures):
    """The panel's critical finding, pinned: an `artifact:` line whose captured segments
    contain `.` or `..` must not be able to redirect the repository root.

    `FEATURE_DIR_IN_ARTIFACT_RE`'s `[^/\\s]+` matches `..`, so
    `.harness/../features/../notes/fake.md` satisfied the pattern; measured against the
    real checkout before the fix, `_repo_root_for_feature` then resolved the PARENT
    repository — a different git work tree sharing the same object store. That redirected
    the `review_sha` read and every grading `git -C` call at once, so both sides of the
    binding became digest-chosen, which is REQ-02 defeated from the inside.

    Asserted at both levels because they regress independently: the derivation must
    refuse the path, and `validate()` must refuse the digest carrying it.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "traversal-config.json")
    write_review_config(config, "advisory_unless_high")
    repo, base_oid, head_oid = make_graded_repo(
        td, "traversal-repo", {"src/clean.py": CLEAN_PY})
    make_feature_dir(repo, review_sha=head_oid, feat="FEAT-TRAVERSAL")

    _assert_honest_artifact_resolves(validator, repo, failures)

    for hostile in HOSTILE_ARTIFACT_PATHS:
        feature_dir, error = validator._feature_dir_from_artifact(hostile, repo)
        if feature_dir is not None or not error:
            failures.append(f"a traversing artifact path {hostile!r} must be refused, "
                            f"got {feature_dir!r}")

    hostile_digest = reviewer_digest(
        "pass", reviewed=f"{base_oid}..{head_oid}",
        artifact=HOSTILE_ARTIFACT_PATHS[0])
    original_root = validator._root_or_none
    validator._root_or_none = lambda: repo
    try:
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", hostile_digest), config)
    finally:
        validator._root_or_none = original_root
    if not any("relative segment" in error for error in errors):
        failures.append(f"validate() must refuse a digest whose artifact line traverses "
                        f"out of the checkout: {errors}")


def _assert_symlinked_component_refused(validator, root, link_name, target, failures,
                                       label):
    """One symlinked `<repo>` component pointing at `target`: every segment of the
    artifact path is a plain name, so the `.`/`..` token check cannot see it and only the
    realpath containment comparison can refuse it."""
    os.makedirs(os.path.join(target, "features", "FEAT-LINKED"), exist_ok=True)
    link = os.path.join(root, ".harness", link_name)
    if not os.path.lexists(link):
        os.symlink(target, link)
    feature_dir, error = validator._feature_dir_from_artifact(
        f".harness/{link_name}/features/FEAT-LINKED/notes/review.md", root)
    if feature_dir is not None or not error:
        failures.append(f"{label} must be refused by the realpath containment check, "
                        f"got {feature_dir!r}")
    elif "resolves outside this checkout" not in error:
        failures.append(f"{label}: the containment refusal must name its own cause, "
                        f"not the token check's: {error!r}")


def check_symlinked_feature_component(td, failures):
    """`_contained_feature_dir`'s SECOND defence, which the token check cannot reach.

    Panel cycle 2 measured with `sys.settrace` that the realpath containment line never
    executed in the committed suite: all four `HOSTILE_ARTIFACT_PATHS` trip the `.`/`..`
    token check first, so deleting the containment test left the suite fully green.
    Correct today and pinned against regression by nothing — the exact
    gate-that-cannot-report-red shape this whole feature exists to refuse. Both cases
    below were confirmed discriminating by mutation (M8 removes the check, M9 drops the
    `+ os.sep`; each reds here and nowhere else).
    """
    validator = _fresh_validator()
    root = os.path.join(td, "symlink-root")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)

    _assert_symlinked_component_refused(
        validator, root, "escaped", os.path.join(td, "outside-the-checkout"), failures,
        "a component symlinked out of the checkout")
    # The `+ os.sep` boundary specifically: a sibling whose path shares the root's string
    # prefix. A bare `startswith(real_root)` admits `<root>-evil`; only the separator
    # makes "descendant" mean descendant.
    _assert_symlinked_component_refused(
        validator, root, "sibling", root + "-evil", failures,
        "a component symlinked to a sibling sharing the root's prefix")

    inside = os.path.join(root, ".harness", "harness", "features", "FEAT-INSIDE")
    os.makedirs(inside, exist_ok=True)
    feature_dir, error = validator._feature_dir_from_artifact(
        ".harness/harness/features/FEAT-INSIDE/notes/review.md", root)
    if error or feature_dir != inside:
        failures.append(f"the containment check must still admit a real in-tree feature "
                        f"directory: {feature_dir!r} {error!r}")


def check_artifact_in_linked_worktree_binds_there(td, failures):
    """#1883: an ABSOLUTE artifact path inside one of the owner checkout's linked
    worktrees binds to THAT worktree's feature.json and grades `git -C <worktree>`.

    Three agents on 2026-09-22 (FEAT-63's delta reviewer, the distill's code-expertise
    member) returned valid digests and could not yield: the artifact named
    `<owner>/.claude/worktrees/harness/distill-FEAT-63/.harness/harness/features/FEAT-63-…`
    and the binding joined the suffix onto the OWNER root, where a worktree-only feature
    has no record. The worktree family SEC-01 trusts is the owner root plus
    `linked_worktrees(owner_root)` — nothing digest-chosen — so an absolute path inside
    one of them is the same trust the relative form already has. Anything outside the
    family is refused exactly as before."""
    validator = _fresh_validator()
    owner = os.path.join(td, "wt-owner")
    os.makedirs(os.path.join(owner, ".harness"), exist_ok=True)
    worktree = _linked_worktree_fixture(owner, "distill-FEAT-Z")
    feature_dir = os.path.join(worktree, ".harness", "harness", "features", "FEAT-Z-thing")
    os.makedirs(os.path.join(feature_dir, "notes"), exist_ok=True)
    artifact = f"{feature_dir}/notes/review-harness-code-reviewer-delta.md"
    resolved, error = validator._feature_dir_from_artifact(artifact, owner)
    if error or os.path.realpath(resolved or "") != os.path.realpath(feature_dir):
        failures.append(f"#1883: an absolute artifact inside a linked worktree must bind "
                        f"to that worktree's feature dir: {resolved!r} {error!r}")
    elif validator._repo_root_for_feature(resolved) != os.path.realpath(worktree):
        failures.append("#1883: the bound feature dir must grade against the worktree, "
                        "not the owner root")

    outside = os.path.join(td, "not-a-worktree", ".harness", "harness", "features", "FEAT-Z-thing")
    os.makedirs(outside, exist_ok=True)
    resolved, error = validator._feature_dir_from_artifact(
        f"{outside}/notes/review.md", owner)
    if resolved is not None or "resolves outside this checkout" not in (error or ""):
        failures.append(f"#1883: an absolute artifact outside the worktree family must "
                        f"still be refused: {resolved!r} {error!r}")


def check_judgment_outranks_clean_grade(td, failures):
    """SC-08/REQ-05: a mechanically CLEAN range cannot rescue a review whose own human
    judgment failed. The reviewer keeps `must_fix` and severity; recomputing the grade
    neither grants nor overrides them.
    """
    validator = _fresh_validator()
    config = os.path.join(td, "judgment-config.json")
    write_review_config(config, "advisory_unless_high")
    repo, base_oid, head_oid = make_graded_repo(
        td, "judgment-clean", {"src/clean.py": CLEAN_PY})
    feature_dir = make_feature_dir(repo, review_sha=head_oid, feat="FEAT-JUDGMENT")
    guarded = reviewer_digest("pass", reviewed=f"{base_oid}..{head_oid}",
                              must_fix="[needs repair]", artifact="a.md")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", guarded), config, feature_dir)
    if not any("review policy" in error for error in errors):
        failures.append(f"a clean mechanical grade must not override a failing "
                        f"must_fix: {errors}")
    high = reviewer_digest("pass", reviewed=f"{base_oid}..{head_oid}",
                           severity_max="high", artifact="a.md")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", high), config, feature_dir)
    if not any("review policy" in error for error in errors):
        failures.append(f"a clean mechanical grade must not override a high-severity "
                        f"review-policy result: {errors}")


def check_plan_review_never_grades(validator, config, td, failures):
    """SC-07/REQ-06/D-06: a pre-signature plan review still validates only as
    `plan:<path>` with `code_grade: n_a`, and the grading seam is NEVER invoked for it —
    a pending plan has no code diff and no review_sha to grade against.
    """
    calls = []
    original = getattr(validator, "gated_set", None)
    validator.gated_set = lambda *args, **kwargs: calls.append(args) or ([], [])
    try:
        feature_dir, _plan_path, _artifact, digest = _plan_review_fixture(
            os.path.join(td, "plan-no-grade"))
        errors = _plan_review_errors(validator, config, feature_dir, digest)
    finally:
        if original is None:
            del validator.gated_set
        else:
            validator.gated_set = original
    if errors:
        failures.append(f"a pending plan review must still validate: {errors}")
    if calls:
        failures.append(f"a plan review must never invoke the grading seam: {calls}")


def _check_bug1081_enforcement(validator, config, _feature_dir, td, failures):
    check_mechanical_result_discrimination(td, failures)
    check_hook_rejects_false_pass(td, failures)
    check_committed_syntax_error(td, failures)
    check_digest_base_cannot_move_result(td, failures)
    check_deletion_only_range(td, failures)
    check_missing_test_kinds(td, failures)
    check_malformed_test_kinds(td, failures)
    check_artifact_path_traversal(td, failures)
    check_symlinked_feature_component(td, failures)
    check_artifact_in_linked_worktree_binds_there(td, failures)
    check_judgment_outranks_clean_grade(td, failures)
    check_plan_review_never_grades(validator, config, td, failures)


def _git_quiet(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True,
                          capture_output=True, text=True).stdout


def _init_test_repo(repo):
    """A fixture checkout, complete enough to be GRADED: BUG-1081 reads `test_kinds`
    from the checkout under review, so every purpose-built repo needs its own
    `.harness/harness.json` exactly as a real one does."""
    os.makedirs(repo)
    _git_quiet(repo, "init", "-q", "-b", "main")
    _git_quiet(repo, "config", "user.email", "test@example.com")
    _git_quiet(repo, "config", "user.name", "test")
    os.makedirs(os.path.join(repo, ".harness"), exist_ok=True)
    with open(os.path.join(repo, ".harness", "harness.json"), "w") as handle:
        json.dump(HARNESS_JSON_FIXTURE, handle)


def _commit_file(repo, name, content, message):
    with open(os.path.join(repo, name), "w") as f:
        f.write(content)
    _git_quiet(repo, "add", ".")
    _git_quiet(repo, "commit", "-q", "-m", message)
    return _git_quiet(repo, "rev-parse", "HEAD").strip()


def make_derived_base_repo(td):
    """A purpose-built git repo under `/tmp` proving SEC-01 wave 4's derived
    range against REAL git plumbing — never a stub of the derivation
    function under test. `main` (mirrored as `origin/main`, this checkout's
    default branch) sits at commit A; `oid_no_py` is a sibling child of A
    touching only a non-`.py` file (the HONEST case: a real, non-degenerate
    range that genuinely changes no Python); `oid_with_py` is a sibling
    child of A touching a `.py` file (the ATTACK case: a self-consistent
    no-op AT this pin must still be caught, because the TRUE derived range
    changed Python); A itself is the DEGENERATE case (review_sha already an
    ancestor of the default branch). Returns `(repo, oid_a, oid_no_py,
    oid_with_py)`.
    """
    repo = os.path.join(td, "derived-base-repo")
    _init_test_repo(repo)
    oid_a = _commit_file(repo, "readme.txt", "a\n", "A")
    _git_quiet(repo, "update-ref", "refs/remotes/origin/main", oid_a)
    _git_quiet(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
               "refs/remotes/origin/main")
    oid_no_py = _commit_file(repo, "feature.txt", "b\n", "no-py-change")
    _git_quiet(repo, "checkout", "-q", oid_a)
    oid_with_py = _commit_file(repo, "feature.py", "x = 1\n", "with-py-change")
    return repo, oid_a, oid_no_py, oid_with_py


def make_review_sha_repo(td):
    """A purpose-built git repo under `/tmp` — hermetic stand-in for the
    ambient checkout `check_reviewed_range` and `check_review_sha_binding`
    used to run against (send-back 2, cycle 27: neither `PRE_FEATURE_REVISION`
    nor `REVIEW_SHA` resolves in a real shallow CI checkout — proven by a
    genuine `--depth 1` clone, which lacks both). `origin/main` (this
    checkout's default branch) sits at commit A; `review_sha` is a REAL
    child of A that touches a `.py` file, so its TRUE derived range
    (`merge-base(main, review_sha)..review_sha`) genuinely changes Python —
    the same property the module-level `REVIEW_SHA` docstring documents,
    now produced by real git plumbing instead of a hardcoded ambient commit.
    The repo's checked-out HEAD is a further, unrelated child of
    `review_sha`, so `HEAD` and `review_sha` differ by construction (SEC-01
    binds `head`, not `base` — a forged `HEAD..HEAD` range must still
    reject). Returns `(repo, oid_a, oid_review_sha, oid_head)`.
    """
    repo = os.path.join(td, "review-sha-repo")
    _init_test_repo(repo)
    oid_a = _commit_file(repo, "readme.txt", "a\n", "A")
    _git_quiet(repo, "update-ref", "refs/remotes/origin/main", oid_a)
    _git_quiet(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
               "refs/remotes/origin/main")
    oid_review_sha = _commit_file(repo, "feature.py", "x = 1\n",
                                  "review_sha: touches Python")
    oid_head = _commit_file(repo, "extra.txt", "b\n",
                            "HEAD: a further, unrelated commit")
    return repo, oid_a, oid_review_sha, oid_head


def _assert_derived_accepts(validator, config, feature_dir, reviewed, message, failures):
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("n_a", reviewed=reviewed, artifact="a.md")), config, feature_dir)
    if errors:
        failures.append(f"{message}: {errors}")


def _assert_derived_rejects(validator, config, feature_dir, reviewed, substring, message, failures):
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("n_a", reviewed=reviewed, artifact="a.md")), config, feature_dir)
    if not any(substring in error for error in errors):
        failures.append(f"{message}: {errors}")


def check_derived_base_range(td, failures):
    """SEC-01 wave 4 (Q8-sec01-remedy-ruling.md): the `code_grade: n_a`
    decision comes from `merge-base(default branch, review_sha)..
    review_sha`, a range the REPOSITORY derives — never from the digest's
    own `reviewed:` field. Proven against a real, purpose-built repo (not a
    stubbed derivation): an honest accept when the true range has no Python
    change, a rejection of the forged self-consistent no-op (and its `~1`
    ancestor variant) when the true range DOES, and a refusal, distinctly
    worded, when the range is degenerate.

    Uses its OWN freshly-imported validator module and NO `chdir`: every git
    operation is addressed at the checkout that owns the feature directory
    (`_repo_root_for_feature`), so a case still depending on the process cwd
    would fail here rather than pass by coincidence (BUG-1081).
    """
    validator = _fresh_validator()
    repo, oid_a, oid_no_py, oid_with_py = make_derived_base_repo(td)
    config = os.path.join(td, "derived-base-config.json")
    write_review_config(config, "advisory_unless_high")
    if True:
        feature_dir_ok = make_feature_dir(repo, review_sha=oid_no_py, feat="FEAT-DERIVED-OK")
        _assert_derived_accepts(
            validator, config, feature_dir_ok, f"{oid_no_py}..{oid_no_py}",
            "a review_sha whose TRUE derived range has no Python change must accept",
            failures)

        feature_dir_bad = make_feature_dir(repo, review_sha=oid_with_py, feat="FEAT-DERIVED-BAD")
        _assert_derived_rejects(
            validator, config, feature_dir_bad, f"{oid_with_py}..{oid_with_py}",
            "expected 'pass'",
            "a forged no-op AT review_sha whose TRUE derived range changed Python "
            "must still reject, now naming the computed result", failures)
        _assert_derived_rejects(
            validator, config, feature_dir_bad, f"{oid_with_py}~1..{oid_with_py}",
            "expected 'pass'",
            "<review_sha>~1..<review_sha> against a real repo must also reject", failures)

        feature_dir_degenerate = make_feature_dir(repo, review_sha=oid_a,
                                                   feat="FEAT-DERIVED-DEGENERATE")
        # SC-11 binds the degenerate refusal to an ORDINARY pass/fail/grade_2 claim, not
        # only to n_a. `_assert_derived_rejects` hardcodes an n_a digest, so sweeping all
        # four values needs `_assert_grade_refused` — the same helper the other two
        # availability conditions use. A criterion quantifying over four values is not
        # satisfied by a fixture that exercises one of them.
        for grade in ("n_a", "pass", "fail", "grade_2"):
            _assert_grade_refused(validator, config, feature_dir_degenerate, oid_a, grade,
                                  "already an ancestor of the default branch", failures)
        _assert_repair_named(validator, config, feature_dir_degenerate, oid_a,
                             "Re-pin review_sha", failures)


def _assert_repair_named(validator, config, feature_dir, oid, repair, failures):
    """SC-11 asks for a refusal that carries a REMEDIATION, not only a cause. A message
    naming what broke and not what to do about it leaves a reviewer with a red gate and
    no next step, which is how a fail-closed check gets worked around instead of fixed."""
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("pass", reviewed=f"{oid}..{oid}", artifact="a.md")),
        config, feature_dir)
    if not any(repair in error for error in errors):
        failures.append(f"the refusal must carry its repair ({repair!r}), not only its "
                        f"cause: {errors}")


def _assert_grade_refused(validator, config, feature_dir, oid, grade, substring,
                          failures, extra=None):
    """D-05: EVERY ordinary grade is refused, with `substring` named, when the
    repository-owned range cannot be derived. `fail` carries `VERDICT: FAIL` so the
    refusal under test is the derivation one and not the verdict rule."""
    digest = _reviewer_digest_for(grade, oid, oid) if grade in ("fail", "grade_2") \
        else reviewer_digest(grade, reviewed=f"{oid}..{oid}", artifact="a.md",
                             **(extra or {}))
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", digest), config, feature_dir)
    if not any(substring in error for error in errors):
        failures.append(f"code_grade={grade!r} must be REFUSED when the canonical range "
                        f"cannot be derived ({substring!r}): {errors}")


def check_unresolvable_default_branch(td, failures):
    """SC-11/D-05: an unresolvable default branch refuses EVERY ordinary grade, each
    with a specific remediation-bearing error.

    This deliberately reverses FEAT-43's carve-out, which exempted `pass`, `fail` and
    `grade_2` from base derivation so an unavailable default branch could not brick
    reviewer validation generally. That exemption IS the bypass BUG-1081 closes: a
    checkout that cannot derive the repository-owned range cannot prove any mechanical
    result, and falling back to the digest's own base would restore it. Proven against a
    REAL checkout that genuinely carries no `origin/HEAD` at all, never a stubbed
    argument.
    """
    validator = _fresh_validator()
    repo = os.path.join(td, "no-default-branch-repo")
    _init_test_repo(repo)
    oid = _commit_file(repo, "readme.txt", "a\n", "A")
    # Deliberately NO origin remote and no refs/remotes/origin/HEAD.
    config = os.path.join(td, "no-origin-config.json")
    write_review_config(config, "advisory_unless_high")
    feature_dir = make_feature_dir(repo, review_sha=oid, feat="FEAT-NO-ORIGIN")
    for grade in ("pass", "fail", "grade_2", "n_a"):
        _assert_grade_refused(validator, config, feature_dir, oid, grade,
                              "default branch", failures)
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", reviewer_digest("pass", reviewed=f"{oid}..{oid}", artifact="a.md")),
        config, feature_dir)
    if not any("repair origin/HEAD" in error for error in errors):
        failures.append(f"the refusal must carry its repair, not only its cause: {errors}")


def make_orphan_review_repo(td):
    """A purpose-built git repo under `/tmp` for SEC-01 wave 4's FOURTH
    fail-closed condition — distinct from `check_unresolvable_default_branch`
    (no `origin/HEAD` at all): here `origin/HEAD` resolves fine and `main`
    exists, but `review_sha` sits on a `git checkout --orphan` branch that
    shares NO commit history with it — `git merge-base` genuinely has
    nothing to return, against real plumbing, never a stub of
    `_merge_base_or_none`. Returns `(repo, oid_orphan)`.
    """
    repo = os.path.join(td, "orphan-review-repo")
    _init_test_repo(repo)
    oid_main = _commit_file(repo, "readme.txt", "a\n", "A")
    _git_quiet(repo, "update-ref", "refs/remotes/origin/main", oid_main)
    _git_quiet(repo, "symbolic-ref", "refs/remotes/origin/HEAD",
               "refs/remotes/origin/main")
    _git_quiet(repo, "checkout", "-q", "--orphan", "no-shared-history")
    _git_quiet(repo, "rm", "-rf", "-q", ".")
    oid_orphan = _commit_file(repo, "orphan.py", "y = 2\n",
                              "orphan root, shares no history with main")
    return repo, oid_orphan


def check_no_merge_base(td, failures):
    """SC-11/D-05's third availability refusal, pinned hermetically: an unresolvable
    MERGE BASE. Distinct from `check_unresolvable_default_branch` (no `origin/HEAD` at
    all) — here the default branch resolves fine, but `review_sha` is on a real orphan
    branch sharing no common ancestor with it, so `git merge-base` itself fails.

    EVERY ordinary grade must refuse for that pin, named distinctly ("no merge base") —
    `pass` included, where FEAT-43 accepted it. A range that cannot be derived proves no
    mechanical result at all, and falling back to the digest's own base would restore
    the bypass.
    """
    validator = _fresh_validator()
    repo, oid_orphan = make_orphan_review_repo(td)
    config = os.path.join(td, "no-merge-base-config.json")
    write_review_config(config, "advisory_unless_high")
    feature_dir = make_feature_dir(repo, review_sha=oid_orphan, feat="FEAT-NO-MERGE-BASE")
    for grade in ("n_a", "pass", "fail", "grade_2"):
        _assert_grade_refused(validator, config, feature_dir, oid_orphan, grade,
                              "no merge base", failures)
    _assert_repair_named(validator, config, feature_dir, oid_orphan,
                         "fetch the default branch", failures)


def check_resolve_reviewed_commit_guard(validator, td, failures):
    """An option-like revision must be rejected before Git is ever invoked.

    The existing `--end-of-options`-based rejection above proves the RESULT
    (None); it does not prove Git was never run. This pins the stronger claim
    the code_grade.commit_oid seam adds: the leading-`-` check runs first.
    """
    original_run = validator.subprocess.run
    calls = []

    def traced_run(args, *args_tail, **kwargs):
        calls.append(args)
        return original_run(args, *args_tail, **kwargs)

    validator.subprocess.run = traced_run
    try:
        result = validator.resolve_reviewed_commit(td, "--upload-pack=touch /tmp/pwned")
    finally:
        validator.subprocess.run = original_run
    if result is not None:
        failures.append("option-like revision must resolve to None")
    if calls:
        failures.append("option-like revision must not invoke Git at all")


def check_review_sha_binding(validator, config, feature_dir, td, failures):
    """SEC-01: `code_grade`'s claim is bound to feature.json's `review_sha`,
    read from the system of record — never to whatever range the digest itself
    names. Proves the discrimination BOTH ways: a validator wired to reject
    everything would still pass a rejection-only test.
    """
    honest = reviewer_digest("pass", reviewed=f"{PRE_FEATURE_REVISION}..{REVIEW_SHA}")
    if validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", honest), config, feature_dir):
        failures.append("an honest range whose head matches review_sha must accept")

    # The reproduction of the live bypass: a resolvable, self-consistent no-op
    # range whose head is simply not review_sha. Before SEC-01 this validated
    # for ANY resolvable commit; now only a head equal to review_sha does.
    forged = reviewer_digest("n_a", reviewed="HEAD..HEAD")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", forged), config, feature_dir)
    if not any("review_sha" in error for error in errors):
        failures.append("a resolvable no-op range whose head != review_sha must "
                        "reject, naming review_sha (the SEC-01 bypass)")

    check_review_sha_binding_unconditional(validator, config, feature_dir, failures)

    missing_feature_dir = os.path.join(td, "no-such-feature-anywhere")
    errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", honest), config,
                                missing_feature_dir)
    if not errors:
        failures.append("an unresolvable feature.json must fail closed, not "
                        "silently accept the code_grade claim")

    check_review_sha_binding_other_personas(validator, config, feature_dir, failures)


def _pin_errors(validator, config, feature_dir, digest, review_pin=None):
    return validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", digest), config, feature_dir,
                              review_pin=review_pin)


def check_dispatch_pin_stands_in_for_an_unpinned_feature(validator, config, feature_dir, failures):
    """#1677: an operator-supplied pin (`HARNESS-REVIEW-PIN:` in the dispatch, forwarded
    as `review_pin`) satisfies the binding when feature.json has none — a frozen
    `review_sha: none`, or no feature at all — without weakening it: `review_sha: none`
    alone still refuses, and the head must still equal the pin. Fixtures live in the
    hermetic repo `feature_dir` belongs to, so the pins resolve."""
    repo = validator._repo_root_for_feature(feature_dir)
    honest = reviewer_digest("pass", reviewed=f"{PRE_FEATURE_REVISION}..{REVIEW_SHA}")
    frozen = make_feature_dir(repo, review_sha="none", feat="FEAT-FROZEN")
    errors = _pin_errors(validator, config, frozen, honest)
    if not any("no pinned review_sha" in error for error in errors):
        failures.append(f"review_sha: none with no dispatch pin must still refuse: {errors}")
    errors = _pin_errors(validator, config, frozen, honest, REVIEW_SHA)
    if errors:
        failures.append(f"a dispatch pin must satisfy the binding on a frozen feature: {errors}")
    forged = reviewer_digest("n_a", reviewed="HEAD..HEAD")
    errors = _pin_errors(validator, config, frozen, forged, REVIEW_SHA)
    if not any("HARNESS-REVIEW-PIN" in error for error in errors):
        failures.append(f"a head that is not the dispatch pin must refuse, naming the pin "
                        f"source: {errors}")
    # No feature at all: the artifact resolves to no feature directory, so the checkout
    # root is the validator's own vantage — pointed at the hermetic repo here.
    original_root_fn = validator._root_or_none
    validator._root_or_none = lambda: repo
    try:
        errors = _pin_errors(validator, config, None, honest, REVIEW_SHA)
    finally:
        validator._root_or_none = original_root_fn
    if errors:
        failures.append(f"a dispatch pin must satisfy the binding with no feature at all "
                        f"(a DEC-174 direct patch): {errors}")


def check_dispatch_pin_never_overrides_a_recorded_one(validator, config, feature_dir, failures):
    """#1677's limit: feature.json's recorded review_sha stays authoritative. A dispatch pin
    equal to it is accepted; one that differs is refused naming both."""
    repo = validator._repo_root_for_feature(feature_dir)
    honest = reviewer_digest("pass", reviewed=f"{PRE_FEATURE_REVISION}..{REVIEW_SHA}")
    recorded = make_feature_dir(repo, review_sha=REVIEW_SHA, feat="FEAT-RECORDED")
    errors = _pin_errors(validator, config, recorded, honest, REVIEW_SHA)
    if errors:
        failures.append(f"a dispatch pin equal to the recorded one must accept: {errors}")
    errors = _pin_errors(validator, config, recorded, honest, PRE_FEATURE_REVISION)
    if not any("never overridden" in error for error in errors):
        failures.append(f"a dispatch pin disagreeing with the recorded one must refuse, "
                        f"naming both: {errors}")


def check_review_sha_binding_unconditional(validator, config, feature_dir, failures):
    """The forged no-op range must reject regardless of `code_grade`'s own
    value — UNCONDITIONAL, not only for `n_a` (the branch the live bypass
    happened to use)."""
    for grade, extra in (("pass", {}), ("fail", {}),
                         ("grade_2", {"grade_2_reasons": "[one reason]"})):
        forged_other = reviewer_digest(grade, reviewed="HEAD..HEAD", **extra)
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", forged_other),
                                    config, feature_dir)
        if not any("review_sha" in error for error in errors):
            failures.append(f"code_grade={grade!r} with a forged no-op range "
                            f"must still reject — the binding runs before the "
                            f"code_grade branch, not only inside it")


def check_review_sha_binding_other_personas(validator, config, feature_dir, failures):
    """`harness-security-reviewer` and `harness-ui-reviewer` normalise to the
    same `reviewer` schema but must NOT acquire the `code_grade`/`reviewed`
    requirement — SEC-01 binds `harness-code-reviewer` only."""
    other_reviewer_digest = """VERDICT: PASS
DIGEST:
  headline: ui pass
  severity_max: low
  findings: []
  must_fix: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: a.md
"""
    for persona in ("harness-ui-reviewer", "harness-security-reviewer"):
        if validator.validate(persona, fixture(persona, other_reviewer_digest), config, feature_dir):
            failures.append(f"{persona} must not require code_grade/reviewed — "
                            f"SEC-01 binds harness-code-reviewer only")


def _resolve_review_sha(validator, text, feature_dir=None):
    """The composition that replaced `resolve_review_sha`: derive the feature from the
    digest's own `artifact:` line, then read THAT feature's pinned review_sha. The
    wrapper went when BUG-1081's enforcement needed the directory as well as the SHA;
    both halves are unchanged production code and are what this covers."""
    feature_dir, error = validator._resolve_feature_dir(text, feature_dir)
    if error:
        return None, error
    return validator._read_review_sha(feature_dir)


def check_resolve_review_sha_artifact_path(validator, td, failures):
    """White-box coverage of the artifact-path +
    checkout-root derivation — the path `validate()` takes in production, when
    no `feature_dir` override is supplied. `_root_or_none` is monkeypatched on
    OUR OWN loaded module (not subprocess, not the environment) purely to
    stand in for a real checkout root without writing into one.
    """
    root = os.path.join(td, "prod-root")
    make_feature_dir(root, feat="FEAT-PROD")
    original_root_fn = validator._root_or_none
    validator._root_or_none = lambda: root
    try:
        text_ok = ("VERDICT: PASS\nDIGEST:\n  headline: x\nartifact: "
                   ".harness/harness/features/FEAT-PROD/notes/review.md\n")
        sha, err = _resolve_review_sha(validator, text_ok)
        if err or sha != REVIEW_SHA:
            failures.append("resolve_review_sha must derive the feature from "
                            f"the artifact: path and read its review_sha "
                            f"(got sha={sha!r} err={err!r})")

        _, err2 = _resolve_review_sha(validator, "VERDICT: PASS\nDIGEST:\n  headline: x\n")
        if not err2:
            failures.append("resolve_review_sha with no artifact: line must fail closed")

        _, err3 = _resolve_review_sha(validator, 
            "VERDICT: PASS\nDIGEST:\n  headline: x\nartifact: a.md\n")
        if not err3:
            failures.append("resolve_review_sha with a non-feature artifact "
                            "path must fail closed")

        validator._root_or_none = lambda: None
        _, err4 = _resolve_review_sha(validator, text_ok)
        if not err4:
            failures.append("resolve_review_sha with no checkout root must fail closed")
    finally:
        validator._root_or_none = original_root_fn


def check_resolve_review_sha_feature_json(validator, td, failures):
    """White-box coverage of `resolve_review_sha`'s READ half — an unpinned or
    absent feature.json, given directly via the `feature_dir` override so no
    artifact-path derivation is exercised here (that half is
    `check_resolve_review_sha_artifact_path`)."""
    unpinned_dir = make_feature_dir(td, review_sha="none", feat="FEAT-UNPINNED")
    _, err5 = _resolve_review_sha(validator, "irrelevant", feature_dir=unpinned_dir)
    if not err5:
        failures.append("resolve_review_sha with an unpinned (placeholder) "
                        "review_sha must fail closed")

    no_feature_json_dir = os.path.join(td, "empty-feature-dir")
    os.makedirs(no_feature_json_dir, exist_ok=True)
    _, err6 = _resolve_review_sha(validator, "irrelevant", feature_dir=no_feature_json_dir)
    if not err6:
        failures.append("resolve_review_sha with no feature.json at all must fail closed")


# Wave 3 hardening fixtures. The current checkout's branch is a value
# `branch_override` sets DIRECTLY — never through `subprocess` mocking (that
# seam is what makes the undeterminable-branch case testable at all).
CURRENT_CHECKOUT_BRANCH = "feat/checkout-under-test"
OTHER_FEATURE_BRANCH = "feat/other-shipped-feature"


def check_branch_corroboration(validator, config, td, failures):
    """Wave 3 hardening: even an HONEST head==review_sha binding still trusts
    the digest's OWN `artifact:` line to pick WHICH feature.json supplied
    that review_sha (SEC-01's residual hole) — a reviewer can point
    `artifact:` at a DIFFERENT shipped feature and reuse ITS OWN, perfectly
    honest review_sha. Proven as the CROSS-FEATURE case, not a shape case:
    two real `feature.json` fixtures, one genuinely under review on this
    checkout's branch, one not.
    """
    root, base_oid, head_oid = make_graded_repo(
        td, "branch-corrob-root", {"src/clean.py": CLEAN_PY})
    make_feature_dir(root, review_sha=head_oid, feat="FEAT-UNDER-REVIEW",
                     branch=CURRENT_CHECKOUT_BRANCH)
    make_feature_dir(root, review_sha=head_oid, feat="FEAT-OTHER-SHIPPED",
                     branch=OTHER_FEATURE_BRANCH)
    make_feature_dir(root, review_sha=head_oid, feat="FEAT-NO-BRANCH", branch="none")
    original_root_fn = validator._root_or_none
    validator._root_or_none = lambda: root
    try:
        # THE FINDING: artifact: names the OTHER feature; reviewed: names
        # THAT feature's own review_sha ("HEAD") twice — self-consistent,
        # honestly bound to FEAT-OTHER-SHIPPED. Accepted before this
        # hardening; must reject now. `code_grade="pass"`, deliberately not
        # `n_a`: this fixture's `review_sha` is the real worktree HEAD, whose
        # TRUE derived range (SEC-01 wave 4) genuinely changes Python, and
        # this test is about branch corroboration, not that decision.
        forged = reviewer_digest(
            "pass", reviewed=f"{base_oid}..{head_oid}",
            artifact=".harness/harness/features/FEAT-OTHER-SHIPPED/notes/review.md")
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", forged), config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if not any("does not match the current checkout" in error for error in errors):
            failures.append("cross-feature forgery (artifact: names a different "
                            "feature and reuses ITS OWN honest review_sha) must "
                            "reject, naming both branches (the SEC-01 residual hole)")

        # The honest counterpart: artifact: names the feature ACTUALLY under
        # review, whose recorded branch matches this checkout's.
        honest = reviewer_digest(
            "pass", reviewed=f"{base_oid}..{head_oid}",
            artifact=".harness/harness/features/FEAT-UNDER-REVIEW/notes/review.md")
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", honest), config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if errors:
            failures.append("the honest digest (artifact: names the feature "
                            f"actually under review) must accept: {errors}")

        # ADDITIVE GUARANTEE 1: current branch undeterminable -> behave
        # exactly as before (accept), never a NEW rejection.
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", forged), config,
                                    feature_dir=None, branch_override=None)
        if errors:
            failures.append("an undeterminable current checkout branch must not "
                            f"introduce a new rejection: {errors}")

        # ADDITIVE GUARANTEE 2: the resolved feature's branch is the literal
        # `none` (a real recorded state — FEAT-01/15/19) -> behave exactly as
        # before (accept), never a NEW rejection. `code_grade="pass"` for the
        # same reason as `forged` above.
        no_branch = reviewer_digest(
            "pass", reviewed=f"{base_oid}..{head_oid}",
            artifact=".harness/harness/features/FEAT-NO-BRANCH/notes/review.md")
        errors = validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", no_branch), config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if errors:
            failures.append("a feature.json with branch: none must not introduce "
                            f"a new rejection: {errors}")
    finally:
        validator._root_or_none = original_root_fn


def check_config_errors(validator, config, feature_dir, guarded, failures):
    write_review_config(config, "advisory")
    if validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", guarded), config, feature_dir):
        failures.append("advisory must accept the same digest")
    with open(config, "w") as f:
        json.dump({}, f)
    try:
        validator.validate("harness-code-reviewer", fixture("harness-code-reviewer", guarded), config, feature_dir)
        failures.append("missing gates must raise")
    except ValueError as error:
        if "gates" not in str(error):
            failures.append("missing gates error must name gates")


@contextlib.contextmanager
def _hermetic_review_sha_repo(td):
    """Send-back 2 (cycle 27): `PRE_FEATURE_REVISION`/`REVIEW_SHA` used to be
    fixed ambient commit hashes a real shallow CI checkout does not carry
    (proven: a genuine `--depth 1` clone lacks both). Builds
    `make_review_sha_repo`'s purpose-built repo, re-points both module-level
    names at it, and `chdir`s into it for the `with` block's duration —
    restoring both on exit. Isolated here, not inlined into
    `_run_code_grade_group`, so that function keeps its own flat shape: the
    ambient-repo swap is orthogonal to what each `check_*` call asserts.

    BUG-1081 dropped the `chdir`: every git operation is addressed at the checkout that
    owns the feature directory, so this yields that repo for the caller to put its
    fixture feature INSIDE, and a case that still depended on cwd would now fail.
    """
    global PRE_FEATURE_REVISION, REVIEW_SHA
    repo, oid_a, oid_review_sha, _oid_head = make_review_sha_repo(td)
    saved = (PRE_FEATURE_REVISION, REVIEW_SHA)
    PRE_FEATURE_REVISION, REVIEW_SHA = oid_a, oid_review_sha
    try:
        yield repo
    finally:
        PRE_FEATURE_REVISION, REVIEW_SHA = saved


def check_hook_feature_dir(validator, td, failures):
    """An installed validator resolves an unmerged feature in its linked worktree."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import inflight_registry
    owner_root = os.path.join(td, "owner")
    feature_root = os.path.join(td, "worktrees", "FEAT-INSTALLED")
    expected = os.path.join(
        feature_root, ".harness", "harness", "features", "FEAT-INSTALLED"
    )
    artifact = ".harness/harness/features/FEAT-INSTALLED/notes/review.md"
    os.makedirs(expected, exist_ok=True)

    original_root = validator._root_or_none
    original_feature_root = inflight_registry.feature_root
    validator._root_or_none = lambda: owner_root
    inflight_registry.feature_root = lambda root, feature: feature_root
    try:
        actual = validator._hook_feature_dir(f"artifact: {artifact}", "FEAT-INSTALLED")
        if actual != expected:
            failures.append(
                f"installed validator must bind to linked feature worktree: {actual!r}"
            )
    finally:
        validator._root_or_none = original_root
        inflight_registry.feature_root = original_feature_root


def check_skipped_member_errors(validator, failures):
    cases = (
        ({"status": "skipped", "persona": "fable-advisor", "reason": "host refusal",
          "verdict": "PASS"}, "verdict"),
        ({"status": "skipped", "reason": "host refusal"}, "persona"),
        ({"status": "skipped", "persona": "fable-advisor"}, "reason"),
        ({"status": "skipped", "persona": "qa", "reason": "host refusal"},
         "optional fable-advisor"),
    )
    for fields, expected in cases:
        skipped, error = validator._skipped_member_error(fields)
        if not skipped or not error or expected not in error:
            failures.append(
                f"skipped member {fields!r} must reject with {expected!r}: {error!r}"
            )


def _check_review_bindings(validator, config, feature_dir, td, failures):
    check_code_grade_state(validator, config, feature_dir, failures)
    check_reviewed_range(validator, config, feature_dir, td, failures)
    check_resolve_reviewed_commit_guard(validator, td, failures)
    check_review_sha_binding(validator, config, feature_dir, td, failures)
    check_dispatch_pin_stands_in_for_an_unpinned_feature(validator, config, feature_dir, failures)
    check_dispatch_pin_never_overrides_a_recorded_one(validator, config, feature_dir, failures)
    check_resolve_review_sha_artifact_path(validator, td, failures)
    check_resolve_review_sha_feature_json(validator, td, failures)
    check_pending_plan_review(validator, config, td, failures)
    check_hook_feature_dir(validator, td, failures)
    check_skipped_member_errors(validator, failures)
    check_branch_corroboration(validator, config, td, failures)


def _check_review_repository(_validator, _config, _feature_dir, td, failures):
    check_derived_base_range(td, failures)
    check_unresolvable_default_branch(td, failures)
    check_no_merge_base(td, failures)


def _check_review_policy_cases(validator, config, feature_dir, td, failures):
    guarded = check_review_policy(validator, config, feature_dir, failures)
    check_config_errors(validator, config, feature_dir, guarded, failures)
    check_prior_validator(td, guarded, failures)


def _run_code_grade_group(label, check):
    """One code-grade checker against its own fixture: a fresh validator module, hermetic
    review_sha repo, `advisory_unless_high` config and feature dir, exactly as the single
    group that used to run all four checkers serially built them once. No checker reads
    state another leaves behind, so each runs as its own concurrent `--only` group."""
    spec = importlib.util.spec_from_file_location("_validator_under_test", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    failures = []
    with tempfile.TemporaryDirectory() as td, _hermetic_review_sha_repo(td) as repo:
        config = os.path.join(td, "harness.json")
        write_review_config(config, "advisory_unless_high")
        feature_dir = make_feature_dir(repo)
        check(validator, config, feature_dir, td, failures)
    if failures:
        print(f"FAIL  code-grade and review-policy gates: {label}")
        for failure in failures:
            print(f"        {failure}")
        return 1
    print(f"ok    code-grade and review-policy gates: {label}")
    return 0


def run_code_grade_bindings_cases():
    return _run_code_grade_group("review bindings", _check_review_bindings)


def run_code_grade_repository_cases():
    return _run_code_grade_group("review repository", _check_review_repository)


def run_code_grade_bug1081_cases():
    return _run_code_grade_group("BUG-1081 enforcement", _check_bug1081_enforcement)


def run_code_grade_policy_cases():
    return _run_code_grade_group("review policy", _check_review_policy_cases)


def _red_failure(label, detail):
    print("FAIL  [%s] %s" % (label, detail))
    return 1


def _fire_hook_binary(binary, payload, env):
    return subprocess.run([sys.executable, binary, "--hook"],
                          input=json.dumps(_governed(payload)), capture_output=True,
                          text=True, env=env)


def _install_mutant(path, source):
    with open(path, "w", encoding="utf-8") as mutant_file:
        mutant_file.write(source)
    os.chmod(path, os.stat(VALIDATE).st_mode & 0o7777)


def _remove_mutant(path):
    try:
        os.remove(path)
    except OSError:
        pass


def _bug919_red_mutant():
    """Read VALIDATE's own source and remove the `if family == "qa":` dispatch to
    check_qa_matrix_claim, leaving everything else — including check_qa_matrix_claim
    itself, now simply unreachable — intact. Returns None if the anchor is absent."""
    with open(VALIDATE, encoding="utf-8") as source_file:
        source = source_file.read()
    anchor = '    if family == "qa":\n        return check_qa_matrix_claim(agent, obj, d)\n'
    if anchor not in source:
        return None
    mutant_source = source.replace(anchor, "", 1)
    if mutant_source == source:
        return None
    return mutant_source


def _dec156_owner_root_mutant(source):
    anchor = "    import digest_destination\n"
    if anchor not in source:
        return None
    # Regress the checkout binding, not a removed search-order implementation.
    return source.replace(anchor, anchor + (
        "    payload = dict(payload)\n"
        "    binding = dict(payload['harness_digest_binding'])\n"
        "    binding['root'] = _root_or_none()\n"
        "    payload['harness_digest_binding'] = binding\n"), 1)


def _dec156_red_is_green(real, old):
    """SC-07: the real validator finds the worktree digest and appends (0); the owner-root
    join finds no run directory and refuses (2)."""
    return (real.returncode == 0
            and old.returncode == 2
            and "Traceback (most recent call last)" not in old.stderr)


def run_dec156_worktree_red_case():
    """dec156-worktree-red: the worktree digest is found only by the feature-checkout join."""
    root, _worktree, _rel, payload = _dec156_worktree_case(
        "red-fixture", "# narrative digest, no contract block\n", 0)
    HOOK_CASES.pop()
    payload = dict(payload)
    payload.pop("_root", None)
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root)

    with open(VALIDATE, encoding="utf-8") as source_file:
        mutant_source = _dec156_owner_root_mutant(source_file.read())
    if mutant_source is None:
        return _red_failure(
            "dec156-worktree-red", "INCONCLUSIVE: resolution anchors absent")

    iso_root = tempfile.mkdtemp()
    mutant = os.path.join(
        isolated_bin(iso_root), ".validate-digest-dec156-red-%d.py" % os.getpid())
    try:
        _install_mutant(mutant, mutant_source)
        real = _fire_hook_binary(VALIDATE, payload, env)
        old = _fire_hook_binary(mutant, payload, env)
        if not _dec156_red_is_green(real, old):
            return _red_failure(
                "dec156-worktree-red", "real=%d mutant=%d\n      | %s"
                % (real.returncode, old.returncode, old.stderr.strip()))
        print("ok    [dec156-worktree-red] owner-root join misses the worktree digest")
        return 0
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)


def _strict_validator_module():
    spec = importlib.util.spec_from_file_location(
        "_strict_validator_under_test", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator


def _duplicate_harness_config_failures(validator, td):
    harness_json = os.path.join(td, ".harness", "harness.json")
    os.makedirs(os.path.dirname(harness_json), exist_ok=True)
    with open(harness_json, "w", encoding="utf-8") as handle:
        handle.write(
            '{"test_kinds": {"x": {}}, "test_kinds": {"x": {}}}')
    kinds, error = validator._load_test_kinds(td)
    if kinds is None and error and "duplicate key" in error:
        return []
    return ["duplicate harness.json keys were not refused"]


def _duplicate_feature_json_failures(validator, td):
    feature_dir = os.path.join(
        td, ".harness", "harness", "features", "FEAT-STRICT")
    os.makedirs(feature_dir, exist_ok=True)
    with open(os.path.join(feature_dir, "feature.json"), "w",
              encoding="utf-8") as handle:
        handle.write(
            '{"feature_id":"FEAT-STRICT","review_sha":"abc1234",'
            '"review_sha":"abc1234","branch":"feat/strict",'
            '"branch":"feat/strict"}')
    review_sha, error = validator._read_review_sha(feature_dir)
    pinned_error = validator._pinned_feature_review_error(feature_dir)
    checks = (
        (review_sha is None and error and "duplicate key" in error,
         "duplicate feature.json keys did not refuse review_sha"),
        (validator._read_feature_branch(feature_dir) is None,
         "duplicate feature.json keys supplied a branch"),
        (pinned_error and "duplicate key" in pinned_error,
         "duplicate feature.json keys did not refuse plan review"),
    )
    return [message for ok, message in checks if not ok]


def _duplicate_hook_payload_failures():
    payload = (
        '{"agent_type":"Explore","agent_type":"Explore",'
        '"digest_object":"not governed"}')
    hook = subprocess.run(
        [sys.executable, VALIDATE, "--hook"], input=payload,
        capture_output=True, text=True,
        env=dict(os.environ, HARNESS_PROJECT_DIR=_isolated_root()))
    # FEAT-65: the typed ArtifactAccessError reaches hook_guard and is named in its template.
    refused = (
        hook.returncode == 0
        and "duplicate key" in hook.stderr
        and "check-digest: the hook failed internally (ArtifactAccessError:" in hook.stderr
    )
    return [] if refused else [
        "duplicate hook payload did not take the typed fail-open path"]


def run_canonical_reader_strictness_cases():
    """Strict artifact seams reject duplicate keys without changing legacy cases."""
    validator = _strict_validator_module()
    with tempfile.TemporaryDirectory() as td:
        failures = _duplicate_harness_config_failures(validator, td)
        failures.extend(_duplicate_feature_json_failures(validator, td))
    failures.extend(_duplicate_hook_payload_failures())
    if not failures:
        return 0
    for failure in failures:
        print(f"FAIL  [canonical-reader audit] {failure}")
    return 1


# --- #1854: a member entry carrying a NESTED block list is ONE member -------------------
# Measured on FEAT-61's distill-validator digest: five members, each with a block-style
# `files_touched:` under it. Well-formed YAML (safe_load reads five members), but every
# nested `- /path` row was split off as a member of its own and reported as "has no
# verdict". The item indent under `members:` is what says which `- ` opens an entry.
LEAD_NESTED_LIST_MEMBERS = """
VERDICT: PASS
DIGEST:
  headline: distillation complete
  team: validate
  steps_run: 2
  cycles_used: 1
  members:
    - step: qa
      persona: harness-qa
      verdict: PASS
      headline: "accepted three lessons"
      files_touched:
        - /abs/.harness/expertise/harness-qa.md
        - /abs/.harness/harness/expertise/harness-qa.md
    - step: ui-reviewer
      persona: harness-ui-reviewer
      verdict: PASS
      headline: "accepted no entry"
      files_touched: []
  must_fix: []
  branch: none
  files_touched: [/abs/.harness/expertise/harness-qa.md]
  open_questions: []
  escalations: []
  expertise_update: []
artifact: .harness/features/FEAT-01/runs/distill-validator/digest.md
"""
case("#1854: a member's nested block list stays inside that member",
     "harness-validator-lead", LEAD_NESTED_LIST_MEMBERS, True)
case("#1854: a nested list does not hide a member that genuinely lacks a verdict",
     "harness-validator-lead",
     LEAD_NESTED_LIST_MEMBERS.replace("      verdict: PASS\n      headline: \"accepted no entry\"\n",
                                      "      headline: \"accepted no entry\"\n"),
     False, "no verdict")
case("#1854: a nested member verdict still rolls up worst-wins",
     "harness-validator-lead",
     LEAD_NESTED_LIST_MEMBERS.replace("      verdict: PASS\n      headline: \"accepted no entry\"",
                                      "      verdict: FAIL\n      headline: \"accepted no entry\""),
     False, "worst")


# --- #1855: a distill dispatch has NO gate subject ------------------------------------
# Feature-close distillation (DEC-145) runs after the merge: the readers judge Expertise
# candidates, touch Expertise files, and review no diff and run no suite. Under the
# build/validate schema qa could not return PASS without `suite: pass` (which then fired
# the #919 rerun) and the code-reviewer could not bind `code_grade` to a review_sha that
# is already an ancestor of main. The mission rides in the dispatch exactly as the
# review pin does (#1677) and reaches the validator as `harness_mission`.
QA_DISTILL = """
VERDICT: PASS
DIGEST:
  headline: accepted three lessons, displaced two weaker craft entries
  suite: n/a
  failures: 0
  coverage_gaps: []
  matrix_ok: n/a
  fail_first: []
  open_questions: []
  files_touched: [/abs/.harness/expertise/harness-qa.md]
  expertise_update: [{ op: add, target: /abs/.harness/expertise/harness-qa.md, section: Patterns, entry: "WHEN a suite is green DO record the fail-first receipt", why: "three runs lost it" }]
artifact: .harness/features/FEAT-01/runs/distill-validator/digest.md
"""
REVIEWER_DISTILL = """
VERDICT: PASS
DIGEST:
  headline: accepted three lessons across craft and repository layers
  severity_max: n/a
  findings: []
  must_fix: []
  code_grade: n_a
  reviewed: none
  files_touched: [/abs/.harness/expertise/harness-code-reviewer.md]
  open_questions: []
  expertise_update: [{ op: add, target: /abs/.harness/expertise/harness-code-reviewer.md, section: Gotchas, entry: "WHEN a grade is n_a DO name the range", why: "two reviews skipped it" }]
artifact: .harness/features/FEAT-01/runs/distill-validator/digest.md
"""
hook_case("#1855: qa on a distill dispatch may PASS with suite/matrix_ok n/a",
          "harness-qa", QA_DISTILL, 0, harness_mission="distill")
hook_case("#1855: the same qa return outside distill is still the fail-open it always was",
          "harness-qa", QA_DISTILL, 2, "gate")
hook_case("#1855: qa on a distill dispatch may not decorate the return with a suite it did not run",
          "harness-qa", QA_DISTILL.replace("suite: n/a", "suite: pass"), 2, "distill",
          harness_mission="distill")
hook_case("#1855: code-reviewer on a distill dispatch may PASS with code_grade n_a and no range",
          "harness-code-reviewer", REVIEWER_DISTILL, 0, harness_mission="distill")
hook_case("#1855: the same reviewer return outside distill is refused at the binding",
          "harness-code-reviewer", REVIEWER_DISTILL, 2, "cannot be bound")
hook_case("#1855: a distill reviewer claiming a grade is refused — there is no diff to grade",
          "harness-code-reviewer", REVIEWER_DISTILL.replace("code_grade: n_a", "code_grade: pass"),
          2, "distill", harness_mission="distill")
hook_case("#1855: an unknown mission changes nothing",
          "harness-qa", QA_DISTILL, 2, "gate", harness_mission="polish")


# --- FEAT-65: the hook's own failure is harness_boundary.hook_guard's ONE template -------
# Hook mode runs under `hook_guard(hook_mode, "check-digest")`. The two local "internal error
# … passing through" catches and the "unreadable hook payload" catch are gone: an unexpected
# defect anywhere in hook mode prints the template line and exits 0; process control escapes;
# and the direct CLI is NOT wrapped — its defects stay loud and nonzero.

GUARD_LINE = ("check-digest: the hook failed internally ({detail}) — passing through; "
              "this is not a pass, nothing was checked.\n")


def _feat65_fire(sibling, override, argv=("--hook",), payload=None, stdin=None):
    """Fire a copy of the validator whose `sibling` module ends with `override` (an appended
    def wins). `sibling` None fires the unmodified copy."""
    root = tempfile.mkdtemp(prefix="vd-feat65-")
    os.makedirs(os.path.join(root, ".harness"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as handle:
        handle.write("schema_version: 1\n")
    iso = isolated_bin(root)
    if sibling is not None:
        with open(os.path.join(iso, sibling), "a", encoding="utf-8") as handle:
            handle.write("\n\n" + override)
    if payload is None:
        payload = {"agent_type": "harness-qa", "digest_object": "VERDICT: PASS\n"}
    env = dict(os.environ, HARNESS_PROJECT_DIR=root)
    return subprocess.run([os.path.join(iso, "validate-digest.py"), *argv],
                          input=json.dumps(_governed(payload)) if stdin is None else stdin,
                          capture_output=True, text=True, env=env)


def _feat65_guarded(result, line):
    """Pass-through: exit 0, stderr ending in the template, and never the old sentences."""
    legacy = ("Not blocking on our own errand", "internal error validating", "unreadable hook payload")
    return (result.returncode == 0 and result.stderr.endswith(line)
            and not any(old in result.stderr for old in legacy))


def _feat65_escaped(result, code=None):
    """Process control escaped the guard: nonzero (or the named code) and no template."""
    exit_ok = result.returncode != 0 if code is None else result.returncode == code
    return exit_ok and "failed internally" not in result.stderr


def run_feat65_guard_cases():
    raise_rt = "    raise RuntimeError('FEAT-65 injected')\n"
    payload_defect = _feat65_fire(
        "artifact_accessors.py", "def read_hook_payload(text, context):\n" + raise_rt)
    unreadable_payload = _feat65_fire(None, "", stdin="{not json")
    registry_defect = _feat65_fire(
        "inflight_registry.py",
        "def live_claims(root, agent, now=None, agent_id=None, parent_agent_id=None):\n"
        + raise_rt)
    interrupt = _feat65_fire(
        "artifact_accessors.py",
        "def read_hook_payload(text, context):\n    raise KeyboardInterrupt()\n")
    deliberate_exit = _feat65_fire(
        "artifact_accessors.py", "def read_hook_payload(text, context):\n    raise SystemExit(7)\n")
    # The direct CLI reads its persona and text itself; a defect in the validator core must
    # stay a loud traceback, never a pass-through. The reviewer persona resolves the review
    # policy's root through harness_boundary on every validate() call.
    cli_defect = _feat65_fire(
        "harness_boundary.py", "def resolve_root(bin_dir, strict=True):\n" + raise_rt,
        argv=("harness-code-reviewer",),
        stdin=json.dumps({"VERDICT": "PASS", "DIGEST": {}, "artifact": "x.md"}))
    line = GUARD_LINE.format(detail="RuntimeError: FEAT-65 injected")
    unreadable_head = ("check-digest: the hook failed internally (ArtifactAccessError: "
                       "yield hook payload: invalid JSON: ")
    return _feat65_report([
        ("a defect reading the payload passes through with exactly the hook_guard line",
         payload_defect.stderr == line and payload_defect.stdout == ""
         and _feat65_guarded(payload_defect, line), payload_defect),
        ("an unreadable payload is the hook's own failure and takes the same template",
         unreadable_payload.stderr.startswith(unreadable_head)
         and _feat65_guarded(unreadable_payload, line[line.index(" — passing through"):]),
         unreadable_payload),
        ("a defect in the registry errand is no longer reported in its own sentence",
         _feat65_guarded(registry_defect, line), registry_defect),
        ("KeyboardInterrupt escapes the guard",
         _feat65_escaped(interrupt) and "KeyboardInterrupt" in interrupt.stderr, interrupt),
        ("a deliberate SystemExit keeps its own exit code",
         _feat65_escaped(deliberate_exit, 7), deliberate_exit),
        ("the direct CLI is not wrapped: a validator defect is loud and nonzero",
         _feat65_escaped(cli_defect) and cli_defect.returncode != 2
         and "FEAT-65 injected" in cli_defect.stderr, cli_defect),
    ])


def _feat65_report(cases):
    fails = 0
    for name, ok, result in cases:
        if ok:
            print(f"ok    [feat65] {name}")
        else:
            fails += 1
            print(f"FAIL  [feat65] {name}\n      | exit {result.returncode}: "
                  f"{result.stderr.strip()[:400]!r}")
    print(f"\n{len(cases) - fails}/{len(cases)} FEAT-65 guard cases passed.")
    return fails


# ---------------------------------------------------------------------------
# BUG-1898 T-03 — the digest hook releases EXACTLY one run's claim, in the registry the
# feature lives in, or nothing. Every case fires the real hook as a subprocess against its
# own throwaway checkout (HARNESS_PROJECT_DIR), seeds real registry rows supervised by this
# live process, and asserts the rows left behind.
# ---------------------------------------------------------------------------
B1898_FEATURE = "BUG-98-exact-release"
B1898 = []


def _b1898_check(name, ok, detail=""):
    B1898.append((name, ok, detail))


def _b1898_personas():
    return sorted(name[:-3] for name in os.listdir(os.path.join(ROOT, ".omp", "agents"))
                  if name.startswith("harness-") and name.endswith(".md"))


def _b1898_seed(root, rows):
    path = os.path.join(root, ".harness", ".inflight-claims.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    claims = []
    for index, row in enumerate(rows):
        claim = {"claim_id": "b1898-%d" % index, "started_at": time.time() - 60 + index, "cwd": root,
                 "dispatcher": "run-start", "runtime": "omp", "supervisor_pid": os.getpid(),
                 "feature": B1898_FEATURE}
        claim.update(row)
        claims.append(claim)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 2, "claims": claims}, handle)


def _b1898_rows(root):
    path = os.path.join(root, ".harness", ".inflight-claims.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return json.load(handle).get("claims", [])


def _b1898_one_claim_per_persona():
    root = _t09_root()
    _b1898_seed(root, [{"agent": persona, "agent_id": "Lead.%s" % persona,
                        "parent_agent_id": "Lead"} for persona in _b1898_personas()])
    return root


def _b1898_missing_identity_releases_nothing():
    """Seed one live exact-id claim for every governed persona, then fire each persona's
    return with the feature OR the runtime id missing. The pre-fix hook fell back to a
    persona-wide (or feature-wide) release and removed that persona's seeded claim."""
    for persona in _b1898_personas():
        for missing, identity in (
            ("runtime id", {"harness_feature": B1898_FEATURE}),
            ("feature", {"harness_agent_id": "Lead.%s" % persona}),
        ):
            root = _b1898_one_claim_per_persona()
            before = _b1898_rows(root)
            r = _t09_fire(root, persona, PM_OK, **identity, governed=False)
            _b1898_check("%s return missing its %s is refused" % (persona, missing),
                         r.returncode == 2 and "harness_agent_id" in r.stderr
                         and "harness_feature" in r.stderr,
                         "exit %d: %s" % (r.returncode, r.stderr.strip()[-240:]))
            _b1898_check("%s return missing its %s releases nothing" % (persona, missing),
                         _b1898_rows(root) == before, repr(_b1898_rows(root))[:240])


def _b1898_blocked_return_without_identity():
    """A run T-02 holds (no claim, often no feature) may still yield BLOCKED: that return
    touches no registry and is not refused for the identity it lacks."""
    root = _b1898_one_claim_per_persona()
    before = _b1898_rows(root)
    r = _t09_fire(root, "harness-qa", "VERDICT: BLOCKED\nDIGEST:\n  headline: held\n", governed=False)
    _b1898_check("a BLOCKED return without identity is not refused for identity",
                 "harness_agent_id" not in r.stderr, r.stderr.strip()[-240:])
    _b1898_check("and it releases nothing", _b1898_rows(root) == before,
                 repr(_b1898_rows(root))[:240])


def _b1898_qa_yields_while_pm_live():
    """Occurrence-1 invariant: QA's digest is validated while PM is live, and PM's row
    survives byte-for-byte. No historical cause is claimed by this case."""
    root = _t09_root()
    _b1898_seed(root, [
        {"agent": "harness-pm", "agent_id": "Lead.Pm", "parent_agent_id": "Lead"},
        {"agent": "harness-qa", "agent_id": "Lead.Qa", "parent_agent_id": "Lead"},
    ])
    pm_before = [row for row in _b1898_rows(root) if row["agent"] == "harness-pm"]
    _t09_fire(root, "harness-qa", _t04_base_digest("harness-qa"),
                harness_feature=B1898_FEATURE, harness_agent_id="Lead.Qa", governed=False)
    rows = _b1898_rows(root)
    _b1898_check("occurrence-1: QA's exact claim is released",
                 [row["agent"] for row in rows] == ["harness-pm"], repr(rows)[:240])
    _b1898_check("occurrence-1: PM's claim id, ids and timestamps survive unchanged",
                 [row for row in rows if row["agent"] == "harness-pm"] == pm_before,
                 repr(rows)[:240])


def _b1898_owner_and_worktree():
    owner = _t09_root()
    worktree = _linked_worktree_fixture(owner, "BUG-98")
    return owner, worktree


def _b1898_release_reads_the_feature_worktree():
    """Defect E: the guard claims in the feature worktree's registry; the hook released in
    the owner checkout's and left the real claim behind."""
    owner, worktree = _b1898_owner_and_worktree()
    _b1898_seed(worktree, [{"agent": "harness-qa", "agent_id": "Lead.Qa",
                            "parent_agent_id": "Lead"}])
    _b1898_seed(owner, [{"agent": "harness-qa", "agent_id": "Other.Qa",
                         "parent_agent_id": "Other", "feature": "FEAT-7-owner"}])
    owner_before = _b1898_rows(owner)
    _t09_fire(owner, "harness-qa", _t04_base_digest("harness-qa"),
                harness_feature=B1898_FEATURE, harness_agent_id="Lead.Qa", governed=False)
    _b1898_check("the claim is released from the feature worktree's registry",
                 _b1898_rows(worktree) == [], repr(_b1898_rows(worktree))[:240])
    _b1898_check("and the owner checkout's registry is untouched",
                 _b1898_rows(owner) == owner_before, repr(_b1898_rows(owner))[:240])


def _b1898_orchestrator_digest():
    return (
        "VERDICT: PASS\nDIGEST:\n  headline: %(f)s shipped\n  feature: %(f)s\n"
        "  status: shipped\n  runs: [{ id: r1, squad: build, verdict: PASS }]\n  cycles_used: 1\n  briefing: none\n"
        "  files_touched: []\n  open_questions: []\n  expertise_update: []\n"
        "artifact: .harness/features/%(f)s/feature.json\n" % {"f": B1898_FEATURE})


B1898_PARENT = {"harness_feature": B1898_FEATURE, "harness_agent_id": "Main.Orch"}


def _b1898_parent_with_live_child():
    """In the feature worktree: parent Main.Orch with live child Main.Orch.Lead, and a second
    parent Main.Orch-2 with its own child that no case may touch."""
    owner, worktree = _b1898_owner_and_worktree()
    _b1898_seed(worktree, [
        {"agent": "harness-orchestrator", "agent_id": "Main.Orch", "parent_agent_id": "Main"},
        {"agent": "harness-eng-lead", "agent_id": "Main.Orch.Lead",
         "parent_agent_id": "Main.Orch"},
        {"agent": "harness-orchestrator", "agent_id": "Main.Orch-2", "parent_agent_id": "Main"},
        {"agent": "harness-qa", "agent_id": "Main.Orch-2.Qa", "parent_agent_id": "Main.Orch-2"},
    ])
    return owner, worktree


def _b1898_ids(root):
    return sorted(row.get("agent_id") for row in _b1898_rows(root))


def _b1898_held_child_refuses_the_parent():
    """The held-child gate on exact ids: a parent with a live child is refused, keeps its
    own claim, and is told how to release exactly that child."""
    owner, worktree = _b1898_parent_with_live_child()
    r = _t09_fire(owner, "harness-orchestrator", _b1898_orchestrator_digest(), **B1898_PARENT, governed=False)
    _b1898_check("a parent with an exact live child is refused",
                 r.returncode == 2 and CHILD_MARK in r.stderr,
                 "exit %d: %s" % (r.returncode, r.stderr.strip()[-300:]))
    _b1898_check("and every claim, its own included, remains",
                 _b1898_ids(worktree) == ["Main.Orch", "Main.Orch-2", "Main.Orch-2.Qa",
                                          "Main.Orch.Lead"], _b1898_ids(worktree))
    _b1898_check("the recovery command targets the one child exactly",
                 "--agent-id Main.Orch.Lead" in r.stderr and "--feature " + B1898_FEATURE
                 in r.stderr and os.path.realpath(worktree) in r.stderr,
                 r.stderr.strip()[-400:])
    _b1898_check("and never a persona-wide or bulk release",
                 "--agent harness-eng-lead" not in r.stderr and "release-all" not in r.stderr
                 and "Main.Orch-2" not in r.stderr, r.stderr.strip()[-400:])


def _b1898_settled_child_frees_the_parent():
    """Once that child settles, the identical yield passes and releases only the parent."""
    owner, worktree = _b1898_parent_with_live_child()
    _t09_fire(owner, "harness-orchestrator", _b1898_orchestrator_digest(), **B1898_PARENT, governed=False)
    _reg_module().release(worktree, feature=B1898_FEATURE, agent_id="Main.Orch.Lead")
    r = _t09_fire(owner, "harness-orchestrator", _b1898_orchestrator_digest(), **B1898_PARENT, governed=False)
    _b1898_check("after the child settles the identical yield passes",
                 r.returncode == 0, "exit %d: %s" % (r.returncode, r.stderr.strip()[-300:]))
    _b1898_check("and releases only the parent",
                 _b1898_ids(worktree) == ["Main.Orch-2", "Main.Orch-2.Qa"], _b1898_ids(worktree))


B1898_UNREADABLE_MARK = "cannot tell whether it holds a live child"


def _b1898_unreadable_registry_holds_the_parent():
    """F-01: "cannot read" is never "no live child". An unreadable registry refuses a
    dispatch-capable parent's return, leaves the file as found, and lets only a BLOCKED
    return — the parent's one way out while the operator repairs it — go on. A leaf, which
    holds no children, is not held by it."""
    owner, worktree = _b1898_parent_with_live_child()
    path = os.path.join(worktree, ".harness", ".inflight-claims.json")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("{not json")
    r = _t09_fire(owner, "harness-orchestrator", _b1898_orchestrator_digest(), **B1898_PARENT,
                  governed=False)
    _b1898_check("an unreadable registry refuses a parent's PASS return",
                 r.returncode == 2 and B1898_UNREADABLE_MARK in r.stderr,
                 "exit %d: %s" % (r.returncode, r.stderr.strip()[-300:]))
    _b1898_check("and names the unreadable registry and the BLOCKED way out",
                 os.path.realpath(worktree) in r.stderr and "BLOCKED" in r.stderr,
                 r.stderr.strip()[-400:])
    blocked = _b1898_orchestrator_digest().replace("VERDICT: PASS", "VERDICT: BLOCKED", 1)
    r = _t09_fire(owner, "harness-orchestrator", blocked, **B1898_PARENT, governed=False)
    _b1898_check("a parent's BLOCKED return is not held by the unreadable registry",
                 B1898_UNREADABLE_MARK not in r.stderr, r.stderr.strip()[-300:])
    r = _t09_fire(owner, "harness-qa", "VERDICT: PASS\n", governed=False,
                  harness_feature=B1898_FEATURE, harness_agent_id="Main.Orch-2.Qa")
    _b1898_check("a leaf's return is not held by it",
                 B1898_UNREADABLE_MARK not in r.stderr, r.stderr.strip()[-300:])
    with open(path, encoding="utf-8") as handle:
        _b1898_check("the unreadable registry is left exactly as found",
                     handle.read() == "{not json", "registry rewritten")


def run_bug1898_exact_release_cases():
    for case_fn in (
        _b1898_missing_identity_releases_nothing,
        _b1898_blocked_return_without_identity,
        _b1898_qa_yields_while_pm_live,
        _b1898_release_reads_the_feature_worktree,
        _b1898_held_child_refuses_the_parent,
        _b1898_settled_child_frees_the_parent,
        _b1898_unreadable_registry_holds_the_parent,
    ):
        case_fn()
    fails = 0
    for name, ok, detail in B1898:
        print(("ok    " if ok else "FAIL  ") + "[bug1898] " + name)
        if not ok:
            fails += 1
            print("      | %s" % (detail,))
    print("\n%d/%d BUG-1898 exact-release checks passed." % (len(B1898) - fails, len(B1898)))
    return fails


# A `--only` child's closing line; the full run prints one line of its own over every group.
_GROUP_SUMMARY = re.compile(r"\n(?:ALL PASSED|(\d+) FAILING)\.\n\Z")


def _run_group(check):
    return subprocess.run([sys.executable, os.path.abspath(__file__), "--only", check.__name__],
                          capture_output=True, text=True)


def _run_groups(checks):
    """Every group as its own `--only` child, concurrently, each output replayed in group
    order without the child's closing line. The suite is spawn-bound, so this is where its
    wall time goes; returns the summed failure count, a child that crashed counting as one."""
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(len(checks), os.cpu_count() or 2)) as pool:
        runs = list(pool.map(_run_group, checks))
    fails = 0
    for run in runs:
        summary = _GROUP_SUMMARY.search(run.stdout)
        sys.stdout.write(run.stdout[:summary.start()] if summary else run.stdout)
        sys.stderr.write(run.stderr)
        group_fails = int(summary.group(1) or 0) if summary else 0
        fails += group_fails or int(run.returncode != 0)
    sys.stdout.flush()
    return fails


_SENTINEL_FEATURE = "BUG-1898-suite-sentinel-%d" % os.getpid()


def _sentinel_rows(registry):
    path = os.path.join(ROOT, registry.REGISTRY_REL)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as stream:
        return json.load(stream).get("claims", [])


def _governed_personas():
    return sorted(name[:-3] for name in os.listdir(os.path.join(ROOT, ".omp", "agents"))
                  if name.startswith("harness-") and name.endswith(".md"))


def _seed_sentinel(registry, persona, claim_ids):
    """One live claim for `persona`, bound to this run's own runtime id; its id joins
    `claim_ids` before anything else can fail, so cleanup always sees it."""
    entry = registry.claim_with_receipt(ROOT, persona, "suite-sentinel", ROOT,
                                        feature=_SENTINEL_FEATURE, supervisor_pid=os.getpid())
    if entry is None:
        return
    claim_ids.append(entry["claim_id"])
    registry.attach_runtime_identity(
        ROOT, persona, _SENTINEL_FEATURE, agent_id="Suite%d.%s" % (os.getpid(), persona),
        claim_id=entry["claim_id"], parent_agent_id="Suite%d" % os.getpid())


def _seeded_rows(registry, claim_ids):
    return [row for row in _sentinel_rows(registry) if row.get("claim_id") in claim_ids]


def _sentinel_verdict(label, ok, detail):
    print(f"ok    [sentinel] {label}" if ok else f"FAIL  [sentinel] {label}: {detail}")
    return 0 if ok else 1


def _run_groups_with_sentinels(checks):
    """BUG-1898 SC-01: a real full suite run releases no unrelated live claim. One live
    stranger per governed persona is seeded in this checkout's registry under this run's own
    feature and runtime id (so concurrent runs never collide); after every group has run each
    stranger must be byte-identical. Cleanup releases exactly the seeded claims. The mutant
    half of SC-01 lives in test-suite-claim-preservation.py."""
    import inflight_registry
    claim_ids = []
    try:
        personas = _governed_personas()
        for persona in personas:
            _seed_sentinel(inflight_registry, persona, claim_ids)
        sentinels = _seeded_rows(inflight_registry, claim_ids)
        fails = _sentinel_verdict("one live sentinel per governed persona was seeded",
                                  len(sentinels) == len(personas), len(sentinels))
        fails += _run_groups(checks)
        kept = _seeded_rows(inflight_registry, claim_ids)
        return fails + _sentinel_verdict(
            "every unrelated live claim is byte-identical after the suite", kept == sentinels,
            sorted({r["agent"] for r in sentinels} - {r["agent"] for r in kept}))
    finally:
        for claim_id in claim_ids:
            inflight_registry.release(ROOT, feature=_SENTINEL_FEATURE, claim_id=claim_id)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    checks = (
        run_canonical_reader_strictness_cases,
        run_feat65_guard_cases,
        run_cli_cases,
        run_dec156_worktree_red_case,
        run_bug919_qa_matrix_cases,
        run_qa_verification_mode_cases,
        run_bug919_resolve_fallback_case,
        run_bug919_resolve_by_artifact_case,
        run_joint_hint_case,
        run_code_grade_bindings_cases,
        run_code_grade_repository_cases,
        run_code_grade_bug1081_cases,
        run_code_grade_policy_cases,
        run_hook_cases,
        run_lead_append_cases,
        run_t09,
        run_t51_suspension_cases,
        run_bug1898_exact_release_cases,
        run_t04_unknown_key_cases,
    )
    # `--only <group>` runs one group by its function name. test-suite-claim-preservation.py's
    # mutant pass reads only the [bug1898] lines, and without this it paid for every group.
    if argv[:1] == ["--only"] and len(argv) == 2:
        by_name = {check.__name__: check for check in checks}
        if argv[1] not in by_name:
            print(f"unknown group {argv[1]!r}; groups: {', '.join(by_name)}", file=sys.stderr)
            return 2
        checks = (by_name[argv[1]],)
    elif argv:
        print(f"usage: {os.path.basename(__file__)} [--only <group>]", file=sys.stderr)
        return 2
    fails = (sum(check() for check in checks) if len(checks) == 1
             else _run_groups_with_sentinels(checks))
    print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILING'}.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
