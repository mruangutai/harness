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
import contextlib, importlib.util, json, re, subprocess, sys, os, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Overridable so the pre-fix binary can be run through the SAME suite to prove
# each new regression case actually fails against the old code (task 22).
VALIDATE = os.environ.get("VALIDATE_DIGEST_BIN") or os.path.join(HERE, "validate-digest.py")
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# Vendored fixture data for check_prior_validator (Q11 cycle-27): the pre-FEAT-43 revision
# of validate-digest.py/harness_yaml.py, committed inert so the control needs no `git show`
# and no repository history to be hermetic in a shallow CI checkout.
FIXTURE_DIR = os.path.join(HERE, "fixtures")
PRE_FEATURE_REVISION = "df63193f7ec9798d9660904e0e4e7c78d52358f5"

# The two normative templates (DEC-123) must validate — extracted from their
# SOURCE FILES and run through the validator, not eyeballed. (name, file, heading)
TEMPLATES = [
    ("SPEC §10.4", os.path.join(REPO_ROOT, ".harness/harness/docs/SPEC.md"),
     "### 10.4 The team digest"),
    ("harness-team \"Reporting up\"",
     os.path.join(REPO_ROOT, ".agents/skills/harness-team/SKILL.md"),
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


# Matches only the template's `severity_max: a|b|c` instruction line, never
# prose like "severity_max >= high" (no `|`-joined alternatives after the
# colon) — confirmed against all six reviewer files before this landed.
_SEVERITY_LINE_RE = re.compile(r"^\s*severity_max:\s*([A-Za-z0-9_/]+(?:\|[A-Za-z0-9_/]+)+)\s*$")


def _reviewer_severity_expected(validator):
    """Expected `severity_max` vocabulary, derived from the validator's own
    `SEV`/`NULLABLE` — never a retyped literal, which is exactly how this
    drifted one narrowing ago."""
    expected = set(validator.SEV)
    if "severity_max" in validator.NULLABLE:
        expected.add("n/a")
    return expected


def _reviewer_template_paths(validator):
    """(path, persona) for every reviewer-schema agent template in BOTH
    trees, discovered MECHANICALLY via the validator's own `norm()`/`ALIAS`
    so a fourth reviewer persona cannot silently escape this check.

    A missing `agents_dir` yields zero paths from that tree rather than
    raising — `_report_missing_templates` is what turns that into a loud,
    named failure instead of a silent empty discovery (c22 send-back).
    """
    paths = []
    for agents_dir in (os.path.join(REPO_ROOT, ".claude", "agents"),
                        os.path.join(REPO_ROOT, ".omp", "agents")):
        try:
            fnames = sorted(os.listdir(agents_dir))
        except FileNotFoundError:
            continue
        for fname in fnames:
            if fname.endswith(".md") and validator.norm(fname[:-3]) == "reviewer":
                paths.append((os.path.join(agents_dir, fname), fname[:-3]))
    return paths


# The reviewer personas already shipped in BOTH trees — the floor
# `_reviewer_template_paths`'s discovery must clear. Not an equality: a
# legitimately-added fourth persona is still picked up by that mechanical
# discovery and never fails this check; it only catches discovery finding
# FEWER than these.
_EXPECTED_REVIEWER_PERSONAS = ("code", "security", "ui")


def _expected_reviewer_template_paths():
    """Every (tree, persona) path discovery must find at minimum."""
    return [
        os.path.join(REPO_ROOT, tree, "agents", f"harness-{persona}-reviewer.md")
        for tree in (".claude", ".omp")
        for persona in _EXPECTED_REVIEWER_PERSONAS
    ]


def _report_missing_templates(discovered_paths):
    """FAIL, naming it, for every expected reviewer template discovery did
    not find. Discovery breaking (renamed persona, missing agents_dir) must
    read as a named failure, never as a smaller-but-still-passing count."""
    fails = 0
    for expected_path in _expected_reviewer_template_paths():
        if expected_path not in discovered_paths:
            fails += 1
            print(f"FAIL  [severity_max enum] expected reviewer template missing: {expected_path}")
    return fails


def _severity_line_values(path):
    """Every `severity_max: a|b|c` alternative-set instructed by `path`."""
    with open(path) as f:
        lines = f.read().split("\n")
    return [set(m.group(1).split("|"))
            for m in map(_SEVERITY_LINE_RE.match, lines) if m]


def _report_template_has_lines(path, count):
    """FAIL, naming it, if a discovered reviewer template yielded zero
    `severity_max` lines — a regex/format failure on that file, never a
    silent zero that drops out of the checked total."""
    if count:
        return 0
    print(f"FAIL  [severity_max enum] {path} — no severity_max line found")
    return 1


def _report_severity_drift(path, instructed, expected):
    """Print and count the drift (if any) between one instructed set and the
    validator's expected vocabulary. Both directions count as drift: a value
    the template offers that the validator rejects, and a value the
    validator accepts that the template never offers."""
    only_template = instructed - expected
    only_validator = expected - instructed
    if not (only_template or only_validator):
        print(f"ok    [severity_max enum] {path}")
        return 0
    print(f"FAIL  [severity_max enum] {path}")
    if only_template:
        print(f"      | instructs {sorted(only_template)} — validator REJECTS these")
    if only_validator:
        print(f"      | validator accepts {sorted(only_validator)} — template never offers these")
    return 1


def run_reviewer_severity_enum_cases():
    """Guard against `severity_max` enum drift between the validator's own
    vocabulary and the reviewer agent templates that instruct agents what to
    write (BUILD task 22 / c22).

    FEAT-43 narrowed `SEV` (dropped `info`) inside its own reviewed range and
    only harness-code-reviewer.md followed; harness-security-reviewer.md and
    harness-ui-reviewer.md (both `.claude/agents` and `.omp/agents`) kept
    instructing the old vocabulary, which the validator then rejects as a
    contract violation the moment a reviewer's worst finding is `info`.

    Zero discovered templates used to read as zero checks and zero
    failures — a pass, indistinguishable from health, the moment either
    discovery seam (the regex, `_reviewer_template_paths`) broke silently
    (c22 send-back). `checked` now starts at the floor's size, so it can
    never reach zero, and both seams are asserted explicitly below.
    """
    spec = importlib.util.spec_from_file_location("_validator_severity_guard", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    expected = _reviewer_severity_expected(validator)

    discovered = _reviewer_template_paths(validator)
    discovered_paths = {path for path, _ in discovered}
    fails = _report_missing_templates(discovered_paths)
    checked = len(_expected_reviewer_template_paths())

    for path, _persona in discovered:
        values = _severity_line_values(path)
        checked += 1
        fails += _report_template_has_lines(path, len(values))
        for instructed in values:
            checked += 1
            fails += _report_severity_drift(path, instructed, expected)

    print(f"\n{checked - fails}/{checked} reviewer severity_max enum checks passed.")
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
# validator next to it that could check it and didn't — the shape of DEC-110/119.
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

# A team step that never ran has no verdict to roll up. The plan-panel contract
# records the absence explicitly instead of manufacturing ESCALATE (which would
# contaminate worst-wins) or PASS (which would claim work happened).
case("a skipped member is explicit and excluded from worst-wins", "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: scope review passed; optional advisor was unavailable
  team: plan-panel
  steps_run: 1
  cycles_used: 0
  members:
    - { step: scope, persona: code-reviewer, verdict: PASS }
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

case("all skipped members cannot support a lead verdict", "harness-validator-lead", """
VERDICT: PASS
DIGEST:
  headline: nobody ran
  team: plan-panel
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
  team: review
  steps_run: 2
  cycles_used: 0
  members:
    - { step: code, persona: code-reviewer, verdict: PASS }
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

# --- D-01 (issue #1056): PRESENCE, not truthiness -----------------------------
# Absent, null and empty-string were ONE branch, so the platform's gap and the persona's
# contract violation were indistinguishable and both exited 0. Five FEAT-45 returns were
# empty and nothing in the record said so. Each case asserts the EXIT CODE and the stderr
# TEXT, because exit 0 alone is what the defect also returned.

hook_case("empty-string: a present but blank final message is the persona's violation",
          "harness-qa", "   \n", 2, mentions="harness-qa")

def _absent_key_case():
    # The key omitted ENTIRELY — hook_case always sets it, so the payload is built here.
    HOOK_CASES.append((
        "absent-key: nothing supplied to validate is OUR gap, and is said so",
        {"agent_type": "harness-qa"}, 0,
        ("not validated", "our", "harness-qa")))
_absent_key_case()

hook_case("null-passthrough: an explicitly null final message is the same our-gap branch",
          "harness-qa", None, 0, mentions=("not validated", "our", "harness-qa"))

# --- The two deliberate pass-throughs (DEC-122), each asserted at exit 0 ---

hook_case("pass-through: non-harness agent_type is not governed",
          "Explore", "VERDICT: PASS\nDIGEST:\nartifact: x.md\n", 0)

hook_case("pass-through: stop_hook_active avoids the infinite-block loop",
          "harness-qa", "done", 0, stop_hook_active=True)

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
    # THE ROOT IS THE OVERRIDE NOW, NOT THE PAYLOAD cwd (FEAT-42 T-17). These fixtures used
    # to be found by joining the artifact path onto payload["cwd"]; cwd was deleted as a root
    # input because nothing SETS where an agent stands. The tmpdir therefore has to be a real
    # harness root — resolve_root honours the override only when the marker is under it — and
    # the runner has to hand it over per case.
    os.makedirs(os.path.join(rd, ".harness"), exist_ok=True)
    with open(os.path.join(rd, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    if file_content is not None:
        with open(os.path.join(rd, rel), "w") as f:
            f.write(file_content)
    msg = LEAD_BLOCK.replace(
        "artifact: .harness/features/FEAT-01/runs/r1/digest.md", f"artifact: {rel}")
    HOOK_CASES.append((name,
                       {"agent_type": agent, "last_assistant_message": msg, "cwd": rd,
                        "_root": rd},
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

# Root and checkout must differ here. `_dec156_case` makes them coincide, so the old
# owner-root join and the corrected feature-checkout join name the same file and cannot
# distinguish the worktree-resolution defect.
def _dec156_worktree_case(name, file_content, expect_exit, mentions=None, feature=True):
    root = tempfile.mkdtemp(prefix="vd-dec156-worktree-")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as marker:
        marker.write("agents: {}\n")
    wt_id = "FEAT-X"
    worktree = os.path.join(root, ".claude", "worktrees", wt_id)
    entry = os.path.join(root, ".git", "worktrees", wt_id)
    os.makedirs(entry, exist_ok=True)
    os.makedirs(os.path.join(worktree, ".harness"), exist_ok=True)
    with open(os.path.join(worktree, ".git"), "w") as pointer:
        pointer.write("gitdir: %s\n" % entry)
    with open(os.path.join(entry, "gitdir"), "w") as pointer:
        pointer.write("%s\n" % os.path.join(worktree, ".git"))
    rel = os.path.join("runs", "r1", "digest.md")
    os.makedirs(os.path.dirname(os.path.join(worktree, rel)), exist_ok=True)
    if file_content is not None:
        with open(os.path.join(worktree, rel), "w", encoding="utf-8") as digest:
            digest.write(file_content)
    msg = LEAD_BLOCK.replace(
        "artifact: .harness/features/FEAT-01/runs/r1/digest.md", f"artifact: {rel}")
    payload = {"agent_type": "harness-eng-lead", "last_assistant_message": msg,
               "_root": root}
    if feature:
        payload["harness_feature"] = "FEAT-X-thing"
    HOOK_CASES.append((name, payload, expect_exit, mentions))
    return root, worktree, rel, payload


_dec156_worktree_case(
    "dec156-worktree-narrative: worktree narrative digest is rejected",
    "# narrative digest, no contract block\n", 2, mentions="digest FILE")
_dec156_worktree_case(
    "dec156-worktree-valid: valid worktree digest passes",
    LEAD_BLOCK, 0)
_dec156_worktree_case(
    "dec156-worktree-nofeature: absent feature preserves fail-open fallback",
    "# narrative digest, no contract block\n", 0, mentions="INV-15", feature=False)


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
  runs: [r1]
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


# ---------------------------------------------------------------------------
# T-09's NINE MANDATED CASES (plan.yaml:1331-1362). MF-2: these were mandated by
# the approved intent and never written, and the panel proved the gap by
# neutering live_children and getting a green suite. Each drives the hook as a
# SUBPROCESS with its own throwaway checkout so no case can see another.
# ---------------------------------------------------------------------------

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


def _t09_fire(root, agent, text, hook=None, **extra):
    payload = {"agent_type": agent, "last_assistant_message": text, "cwd": root}
    payload.update(extra)
    return subprocess.run([hook or VALIDATE, "--hook"], input=json.dumps(payload),
                          capture_output=True, text=True,
                          # BOTH NAMES, ONE VALUE (FEAT-42 T-17). The hook resolves through
                          # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR
                          # and no other name, and payload cwd is no longer a root input.
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=root,
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


def run_t09():
    reg = _reg_module()

    def claims(root, agent):
        p = os.path.join(root, reg.REGISTRY_REL)
        if not os.path.exists(p):
            return []
        with open(p) as fh:
            data = json.load(fh) or {}
        return [claim for claim in data.get("claims", []) if claim.get("agent") == agent]

    # 1. a valid pm return RELEASES its claim
    root = _t09_root()
    reg.claim(root, "harness-pm", "harness-product-lead", root)
    r = _t09_fire(root, "harness-pm", PM_OK)
    t09("1: a valid pm return exits 0", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("1: and its claim is GONE from the registry", not claims(root, "harness-pm"),
        repr(claims(root, "harness-pm")))

    # 2. an INVALID digest still exits 2 for the contract AND still releases. A blocked
    #    return that leaks its claim can never be re-dispatched.
    root = _t09_root()
    reg.claim(root, "harness-pm", "harness-product-lead", root)
    r = _t09_fire(root, "harness-pm", "VERDICT: PASS\nDIGEST:\n  headline: x\n")
    t09("2: an invalid digest still exits 2", r.returncode == 2, f"exit {r.returncode}")
    t09("2: and the claim is STILL released, so a re-prompt can be re-dispatched",
        not claims(root, "harness-pm"), repr(claims(root, "harness-pm")))

    # 3. stop_hook_active short-circuits and does not raise, with a claim present
    root = _t09_root()
    reg.claim(root, "harness-pm", "harness-product-lead", root)
    r = _t09_fire(root, "harness-pm", PM_OK, stop_hook_active=True)
    t09("3: stop_hook_active exits 0 with a claim present", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("3: and prints no traceback", "Traceback" not in r.stderr, r.stderr[:200])

    # 4. a persona releases its OWN claim and leaves an unrelated one alone. BOTH halves.
    root = _t09_root()
    reg.claim(root, "harness-documentor", "harness-product-lead", root)
    reg.claim(root, "harness-pm", "harness-product-lead", root)
    r = _t09_fire(root, "harness-documentor", PM_OK.replace("VERDICT: PASS", "VERDICT: PASS"))
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

    # 6. THE D-09 REFUSAL. Two live children, a lead returning. Assert the exit, both children
    #    by name, the issue, AND that the lead's own claim was released first.
    root = _t09_root()
    reg.claim(root, "harness-eng-lead", "harness-orchestrator", root)
    reg.claim(root, "harness-backend-dev", "harness-eng-lead", root)
    reg.claim(root, "harness-dev-ops", "harness-eng-lead", root)
    r = _t09_fire(root, "harness-eng-lead", LEAD_BLOCK)
    t09("6: a lead returning with children in flight exits 2", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:240]!r}")
    t09("6: stderr carries the children-in-flight refusal", CHILD_MARK in r.stderr,
        r.stderr.strip()[:240])
    t09("6: stderr names BOTH children",
        "harness-backend-dev" in r.stderr and "harness-dev-ops" in r.stderr,
        r.stderr.strip()[:240])
    t09("6: stderr cites the issue", "#551" in r.stderr, r.stderr.strip()[:240])
    t09("6: the lead's OWN claim was released first",
        not claims(root, "harness-eng-lead"), repr(claims(root, "harness-eng-lead")))

    # 7. THE ALLOW HALF, asserting the ABSENCE of the marker so a refuse-every-lead build fails.
    root = _t09_root()
    reg.claim(root, "harness-eng-lead", "harness-orchestrator", root)
    r = _t09_fire(root, "harness-eng-lead", LEAD_BLOCK)
    t09("7: a lead with NO children carries no children marker", CHILD_MARK not in r.stderr,
        r.stderr.strip()[:240])

    # 8. A MEMBER IS NEVER SUBJECT TO IT -- only a lead or the orchestrator dispatches.
    root = _t09_root()
    reg.claim(root, "harness-pm", "harness-pm", root)
    r = _t09_fire(root, "harness-pm", PM_OK)
    t09("8: a member with a claim dispatched by itself still exits 0", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("8: and no children marker", CHILD_MARK not in r.stderr, r.stderr.strip()[:200])

    # 9. THE ONE-SHOT BOUND, ASSERTED RATHER THAN HIDDEN. This records D-09's residual: a
    #    second refusal here would be the infinite stop loop the pass-through prevents.
    #    DO NOT "fix" this case.
    root = _t09_root()
    reg.claim(root, "harness-eng-lead", "harness-orchestrator", root)
    reg.claim(root, "harness-backend-dev", "harness-eng-lead", root)
    r = _t09_fire(root, "harness-eng-lead", LEAD_BLOCK, stop_hook_active=True)
    t09("9: stop_hook_active exits 0 WITH children still on disk (D-09's residual)",
        r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t09("9: and the child claim is still there, so the bound is real",
        len(claims(root, "harness-backend-dev")) == 1,
        repr(claims(root, "harness-backend-dev")))

    # 10. children_in_flight_stale_claim — THE CASCADE (FEAT-42 T-17, issue #742/#866).
    #     A claim left behind by a DIFFERENT session is not a live child of this return.
    #     MEASURED 2026-08-26 and written up in
    #     runs/2026-08-26-2-plan-product/digest.md: one stranded pm claim refused the pm
    #     spawn at dispatch-guard, then refused the LEAD's return here, then refused the
    #     ORCHESTRATOR's return here again — three tiers locked out of reporting by one
    #     strand, each stranding creating the next. The payload carries session_id; the
    #     registry entry carries the session that made the claim; a mismatch means the
    #     claim belongs to somebody else's run and this return must be ADMITTED.
    root = _t09_root()
    reg.claim(root, "harness-eng-lead", "harness-orchestrator", root, session="THIS-SESSION")
    reg.claim(root, "harness-backend-dev", "harness-eng-lead", root, session="OTHER-SESSION")
    r = _t09_fire(root, "harness-eng-lead", LEAD_BLOCK, session_id="THIS-SESSION")
    t09("10: children_in_flight_stale_claim — a FOREIGN session's claim does not refuse "
        "this return", r.returncode == 0,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:240]!r}")
    t09("10: children_in_flight_stale_claim — and no children marker is printed",
        CHILD_MARK not in r.stderr, r.stderr.strip()[:240])

    # 11. THE OTHER HALF, so 10 cannot pass by never refusing anyone. Same shape, same
    #     session on both claims: this one MUST still refuse, and the refusal must name the
    #     precise single-agent release command rather than release-all, which wipes every
    #     claim of every agent (following the old advice on 2026-08-26 would have destroyed
    #     a live one).
    root = _t09_root()
    reg.claim(root, "harness-eng-lead", "harness-orchestrator", root, session="THIS-SESSION")
    reg.claim(root, "harness-backend-dev", "harness-eng-lead", root, session="THIS-SESSION")
    r = _t09_fire(root, "harness-eng-lead", LEAD_BLOCK, session_id="THIS-SESSION")
    t09("11: a SAME-session child still refuses, so case 10 is not a blanket pass",
        r.returncode == 2 and CHILD_MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:240]!r}")
    t09("11: and the refusal names the single-agent release command for that child",
        "--agent harness-backend-dev" in r.stderr and "release-all" not in r.stderr,
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
            json.dump({"gates": {"qa_gate": "blocking", "review": "advisory",
                                 "uat": "advisory", "merge": "autonomous"}}, f)
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
        env["CLAUDE_PROJECT_DIR"] = _root
        r = subprocess.run([VALIDATE, "--hook"], input=json.dumps(payload),
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
  findings: 0
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
  findings: 0
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
     "harness-backend-dev", _dev(tv=None), False,
     # SC-18a: the hint must say what is rejected is a placeholder ALONGSIDE
     # `VERDICT: PASS` — never that placeholders are disallowed. That distinction is
     # what keeps `suite: n/a` + BLOCKED legal (REQ-03/SC-06), and the hint already
     # said it while nothing asserted it.
     ["task_verify", "pass", "fail", "alongside", "VERDICT: PASS",
      "!genuinely not applicable"])
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
  findings: 0
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
    return validator.validate(
        "harness-code-reviewer", digest, config, feature_dir, branch_override
    )


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
    if not any("review policy" in error for error in validator.validate(
            "harness-code-reviewer", guarded, config, feature_dir)):
        failures.append("advisory_unless_high must reject must_fix with PASS")
    if validator.validate("harness-code-reviewer",
                          reviewer_digest(severity_max="none"), config, feature_dir):
        failures.append("none severity must be accepted by review policy")
    if not any("severity_max" in error for error in validator.validate(
            "harness-code-reviewer", reviewer_digest(severity_max="info"),
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
        input=guarded, capture_output=True, text=True)
    if prior.returncode != 0:
        failures.append("previous validator must accept the gated digest")


def write_review_config(config, review):
    with open(config, "w") as f:
        json.dump({"gates": {"qa_gate": "blocking", "review": review,
                             "uat": "advisory", "merge": "autonomous"}}, f)


def check_code_grade_state(validator, config, feature_dir, failures):
    if not any("code_grade" in error for error in validator.validate(
            "harness-code-reviewer", reviewer_digest("fail"), config, feature_dir)):
        failures.append("fail-plus-PASS must reject")
    reasoned_grade_2 = reviewer_digest(
        "grade_2", grade_2_reasons="[one auditable reason]")
    if validator.validate("harness-code-reviewer", reasoned_grade_2, config, feature_dir):
        failures.append("grade_2 with a written reason must permit PASS")
    if not any("grade_2_reasons" in error for error in validator.validate(
            "harness-code-reviewer", reviewer_digest("grade_2"), config, feature_dir)):
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
    "only valid",                           # reviewed diff genuinely has Python
    "already an ancestor of the default",   # degenerate: review_sha merged in
    "default branch",                       # origin/HEAD unresolvable
    "no merge base",                        # merge-base could not be computed
)


def _assert_n_a_rejects(validator, config, feature_dir, reviewed, message, failures):
    errors = validator.validate(
            "harness-code-reviewer", reviewer_digest("n_a", reviewed=reviewed),
            config, feature_dir)
    if not any(substring in error for error in errors
               for substring in N_A_REFUSAL_SUBSTRINGS):
        failures.append(f"{message}: {errors}")


def _check_option_like_revisions(validator, config, feature_dir, td, failures):
    output_path = os.path.join(td, "must-not-exist")
    for revision in ("--no-patch..HEAD", f"--output={output_path}..HEAD"):
        errors = validator.validate(
            "harness-code-reviewer", reviewer_digest("n_a", reviewed=revision),
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


def _git_quiet(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True,
                          capture_output=True, text=True).stdout


def _init_test_repo(repo):
    os.makedirs(repo)
    _git_quiet(repo, "init", "-q", "-b", "main")
    _git_quiet(repo, "config", "user.email", "test@example.com")
    _git_quiet(repo, "config", "user.name", "test")


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
    errors = validator.validate(
        "harness-code-reviewer",
        reviewer_digest("n_a", reviewed=reviewed, artifact="a.md"), config, feature_dir)
    if errors:
        failures.append(f"{message}: {errors}")


def _assert_derived_rejects(validator, config, feature_dir, reviewed, substring, message, failures):
    errors = validator.validate(
        "harness-code-reviewer",
        reviewer_digest("n_a", reviewed=reviewed, artifact="a.md"), config, feature_dir)
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

    Uses its OWN freshly-imported validator module + `os.chdir` into the
    fixture repo (restored in `finally`): `resolve_reviewed_commit` and the
    new derived-base helpers are bare `git` (no `-C`), so they resolve
    against the process cwd — the same basis this file already uses
    throughout (`resolve_reviewed_commit`'s `commit_oid(".", ...)`).
    """
    spec = importlib.util.spec_from_file_location("_derived_base_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    repo, oid_a, oid_no_py, oid_with_py = make_derived_base_repo(td)
    config = os.path.join(td, "derived-base-config.json")
    write_review_config(config, "advisory_unless_high")
    original_cwd = os.getcwd()
    os.chdir(repo)
    try:
        feature_dir_ok = make_feature_dir(repo, review_sha=oid_no_py, feat="FEAT-DERIVED-OK")
        _assert_derived_accepts(
            validator, config, feature_dir_ok, f"{oid_no_py}..{oid_no_py}",
            "a review_sha whose TRUE derived range has no Python change must accept",
            failures)

        feature_dir_bad = make_feature_dir(repo, review_sha=oid_with_py, feat="FEAT-DERIVED-BAD")
        _assert_derived_rejects(
            validator, config, feature_dir_bad, f"{oid_with_py}..{oid_with_py}", "only valid",
            "a forged no-op AT review_sha whose TRUE derived range changed Python "
            "must still reject", failures)
        _assert_derived_rejects(
            validator, config, feature_dir_bad, f"{oid_with_py}~1..{oid_with_py}", "only valid",
            "<review_sha>~1..<review_sha> against a real repo must also reject", failures)

        feature_dir_degenerate = make_feature_dir(repo, review_sha=oid_a,
                                                   feat="FEAT-DERIVED-DEGENERATE")
        _assert_derived_rejects(
            validator, config, feature_dir_degenerate, f"{oid_a}..{oid_a}",
            "already an ancestor of the default branch",
            "a review_sha already merged into the default branch must refuse "
            "with its own named error", failures)
    finally:
        os.chdir(original_cwd)


def _assert_ungated_grade(validator, config, feature_dir, oid, grade, extra, failures):
    digest = reviewer_digest(grade, reviewed=f"{oid}..{oid}", artifact="a.md", **extra)
    errors = validator.validate("harness-code-reviewer", digest, config, feature_dir)
    if errors:
        failures.append(f"code_grade={grade!r} must not be gated on an "
                        f"unresolvable default branch: {errors}")


def _assert_fail_ungated(validator, config, feature_dir, oid, failures):
    fail_digest = reviewer_digest("fail", reviewed=f"{oid}..{oid}", artifact="a.md").replace(
        "VERDICT: PASS", "VERDICT: FAIL", 1)
    errors = validator.validate("harness-code-reviewer", fail_digest, config, feature_dir)
    if errors:
        failures.append("code_grade='fail' must not be gated on an unresolvable "
                        f"default branch: {errors}")


def check_unresolvable_default_branch(td, failures):
    """SEC-01 wave 4: `pass`/`fail`/`grade_2` must never be gated on base
    derivation — an unresolvable default branch must not brick reviewer
    validation generally. Proven with a REAL checkout that genuinely carries
    no `origin/HEAD` symbolic ref at all, not a stubbed argument; `n_a`, in
    contrast, MUST refuse in the very same checkout, since the derivation it
    alone depends on genuinely cannot run there.
    """
    spec = importlib.util.spec_from_file_location("_no_origin_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    repo = os.path.join(td, "no-default-branch-repo")
    _init_test_repo(repo)
    oid = _commit_file(repo, "readme.txt", "a\n", "A")
    # Deliberately NO origin remote and no refs/remotes/origin/HEAD.
    config = os.path.join(td, "no-origin-config.json")
    write_review_config(config, "advisory_unless_high")
    original_cwd = os.getcwd()
    os.chdir(repo)
    try:
        feature_dir = make_feature_dir(repo, review_sha=oid, feat="FEAT-NO-ORIGIN")
        _assert_ungated_grade(validator, config, feature_dir, oid, "pass", {}, failures)
        _assert_ungated_grade(validator, config, feature_dir, oid, "grade_2",
                              {"grade_2_reasons": "[one reason]"}, failures)
        _assert_fail_ungated(validator, config, feature_dir, oid, failures)

        digest_na = reviewer_digest("n_a", reviewed=f"{oid}..{oid}", artifact="a.md")
        errors = validator.validate("harness-code-reviewer", digest_na, config, feature_dir)
        if not any("default branch" in error for error in errors):
            failures.append(f"n_a with an unresolvable default branch must refuse: {errors}")
    finally:
        os.chdir(original_cwd)


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
    """SEC-01 wave 4's fourth and last `n_a` refusal reason, pinned
    hermetically: an unresolvable MERGE BASE. Distinct from
    `check_unresolvable_default_branch` (no `origin/HEAD` at all) — here the
    default branch resolves fine, but `review_sha` is on a real orphan
    branch sharing no common ancestor with it, so `git merge-base` itself
    fails. `code_grade: n_a` for that pin must REFUSE, named distinctly
    ("no merge base"); `code_grade: pass` for the SAME pin in the SAME repo
    must still be ACCEPTED — proving the refusal is narrow to `n_a`'s own
    derivation and does not brick reviewer validation generally, the same
    ungated property `check_unresolvable_default_branch` already proves for
    the sibling branch.
    """
    spec = importlib.util.spec_from_file_location("_no_merge_base_validator", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    repo, oid_orphan = make_orphan_review_repo(td)
    config = os.path.join(td, "no-merge-base-config.json")
    write_review_config(config, "advisory_unless_high")
    original_cwd = os.getcwd()
    os.chdir(repo)
    try:
        feature_dir = make_feature_dir(repo, review_sha=oid_orphan, feat="FEAT-NO-MERGE-BASE")
        _assert_derived_rejects(
            validator, config, feature_dir, f"{oid_orphan}..{oid_orphan}", "no merge base",
            "n_a on an orphan review_sha with no merge base to the default "
            "branch must refuse", failures)

        pass_digest = reviewer_digest("pass", reviewed=f"{oid_orphan}..{oid_orphan}",
                                      artifact="a.md")
        errors = validator.validate("harness-code-reviewer", pass_digest, config, feature_dir)
        if errors:
            failures.append("code_grade='pass' for the same orphan pin must not be "
                            f"gated on an unresolvable merge base: {errors}")
    finally:
        os.chdir(original_cwd)


def check_resolve_reviewed_commit_guard(validator, failures):
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
        result = validator.resolve_reviewed_commit("--upload-pack=touch /tmp/pwned")
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
    if validator.validate("harness-code-reviewer", honest, config, feature_dir):
        failures.append("an honest range whose head matches review_sha must accept")

    # The reproduction of the live bypass: a resolvable, self-consistent no-op
    # range whose head is simply not review_sha. Before SEC-01 this validated
    # for ANY resolvable commit; now only a head equal to review_sha does.
    forged = reviewer_digest("n_a", reviewed="HEAD..HEAD")
    errors = validator.validate("harness-code-reviewer", forged, config, feature_dir)
    if not any("review_sha" in error for error in errors):
        failures.append("a resolvable no-op range whose head != review_sha must "
                        "reject, naming review_sha (the SEC-01 bypass)")

    check_review_sha_binding_unconditional(validator, config, feature_dir, failures)

    missing_feature_dir = os.path.join(td, "no-such-feature-anywhere")
    errors = validator.validate("harness-code-reviewer", honest, config,
                                missing_feature_dir)
    if not errors:
        failures.append("an unresolvable feature.json must fail closed, not "
                        "silently accept the code_grade claim")

    check_review_sha_binding_other_personas(validator, config, feature_dir, failures)


def check_review_sha_binding_unconditional(validator, config, feature_dir, failures):
    """The forged no-op range must reject regardless of `code_grade`'s own
    value — UNCONDITIONAL, not only for `n_a` (the branch the live bypass
    happened to use)."""
    for grade, extra in (("pass", {}), ("fail", {}),
                         ("grade_2", {"grade_2_reasons": "[one reason]"})):
        forged_other = reviewer_digest(grade, reviewed="HEAD..HEAD", **extra)
        errors = validator.validate("harness-code-reviewer", forged_other,
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
  findings: 0
  must_fix: []
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: a.md
"""
    for persona in ("harness-ui-reviewer", "harness-security-reviewer"):
        if validator.validate(persona, other_reviewer_digest, config, feature_dir):
            failures.append(f"{persona} must not require code_grade/reviewed — "
                            f"SEC-01 binds harness-code-reviewer only")


def check_resolve_review_sha_artifact_path(validator, td, failures):
    """White-box coverage of `resolve_review_sha`'s OWN artifact-path +
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
        sha, err = validator.resolve_review_sha(text_ok)
        if err or sha != REVIEW_SHA:
            failures.append("resolve_review_sha must derive the feature from "
                            f"the artifact: path and read its review_sha "
                            f"(got sha={sha!r} err={err!r})")

        _, err2 = validator.resolve_review_sha("VERDICT: PASS\nDIGEST:\n  headline: x\n")
        if not err2:
            failures.append("resolve_review_sha with no artifact: line must fail closed")

        _, err3 = validator.resolve_review_sha(
            "VERDICT: PASS\nDIGEST:\n  headline: x\nartifact: a.md\n")
        if not err3:
            failures.append("resolve_review_sha with a non-feature artifact "
                            "path must fail closed")

        validator._root_or_none = lambda: None
        _, err4 = validator.resolve_review_sha(text_ok)
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
    _, err5 = validator.resolve_review_sha("irrelevant", feature_dir=unpinned_dir)
    if not err5:
        failures.append("resolve_review_sha with an unpinned (placeholder) "
                        "review_sha must fail closed")

    no_feature_json_dir = os.path.join(td, "empty-feature-dir")
    os.makedirs(no_feature_json_dir, exist_ok=True)
    _, err6 = validator.resolve_review_sha("irrelevant", feature_dir=no_feature_json_dir)
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
    root = os.path.join(td, "branch-corrob-root")
    make_feature_dir(root, review_sha=REVIEW_SHA, feat="FEAT-UNDER-REVIEW",
                     branch=CURRENT_CHECKOUT_BRANCH)
    make_feature_dir(root, review_sha="HEAD", feat="FEAT-OTHER-SHIPPED",
                     branch=OTHER_FEATURE_BRANCH)
    make_feature_dir(root, review_sha="HEAD", feat="FEAT-NO-BRANCH", branch="none")
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
            "pass", reviewed="HEAD..HEAD",
            artifact=".harness/harness/features/FEAT-OTHER-SHIPPED/notes/review.md")
        errors = validator.validate("harness-code-reviewer", forged, config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if not any("does not match the current checkout" in error for error in errors):
            failures.append("cross-feature forgery (artifact: names a different "
                            "feature and reuses ITS OWN honest review_sha) must "
                            "reject, naming both branches (the SEC-01 residual hole)")

        # The honest counterpart: artifact: names the feature ACTUALLY under
        # review, whose recorded branch matches this checkout's.
        honest = reviewer_digest(
            "pass", reviewed=f"HEAD..{REVIEW_SHA}",
            artifact=".harness/harness/features/FEAT-UNDER-REVIEW/notes/review.md")
        errors = validator.validate("harness-code-reviewer", honest, config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if errors:
            failures.append("the honest digest (artifact: names the feature "
                            f"actually under review) must accept: {errors}")

        # ADDITIVE GUARANTEE 1: current branch undeterminable -> behave
        # exactly as before (accept), never a NEW rejection.
        errors = validator.validate("harness-code-reviewer", forged, config,
                                    feature_dir=None, branch_override=None)
        if errors:
            failures.append("an undeterminable current checkout branch must not "
                            f"introduce a new rejection: {errors}")

        # ADDITIVE GUARANTEE 2: the resolved feature's branch is the literal
        # `none` (a real recorded state — FEAT-01/15/19) -> behave exactly as
        # before (accept), never a NEW rejection. `code_grade="pass"` for the
        # same reason as `forged` above.
        no_branch = reviewer_digest(
            "pass", reviewed="HEAD..HEAD",
            artifact=".harness/harness/features/FEAT-NO-BRANCH/notes/review.md")
        errors = validator.validate("harness-code-reviewer", no_branch, config,
                                    feature_dir=None,
                                    branch_override=CURRENT_CHECKOUT_BRANCH)
        if errors:
            failures.append("a feature.json with branch: none must not introduce "
                            f"a new rejection: {errors}")
    finally:
        validator._root_or_none = original_root_fn


def check_config_errors(validator, config, feature_dir, guarded, failures):
    write_review_config(config, "advisory")
    if validator.validate("harness-code-reviewer", guarded, config, feature_dir):
        failures.append("advisory must accept the same digest")
    with open(config, "w") as f:
        json.dump({}, f)
    try:
        validator.validate("harness-code-reviewer", guarded, config, feature_dir)
        failures.append("missing gates must raise")
    except ValueError as error:
        if "gates" not in str(error):
            failures.append("missing gates error must name gates")


@contextlib.contextmanager
def _hermetic_review_sha_cwd(td):
    """Send-back 2 (cycle 27): `PRE_FEATURE_REVISION`/`REVIEW_SHA` used to be
    fixed ambient commit hashes a real shallow CI checkout does not carry
    (proven: a genuine `--depth 1` clone lacks both). Builds
    `make_review_sha_repo`'s purpose-built repo, re-points both module-level
    names at it, and `chdir`s into it for the `with` block's duration —
    restoring both on exit. Isolated here, not inlined into
    `run_code_grade_cases`, so that function keeps its own flat shape: the
    ambient-repo swap is orthogonal to what each `check_*` call asserts.
    """
    global PRE_FEATURE_REVISION, REVIEW_SHA
    repo, oid_a, oid_review_sha, _oid_head = make_review_sha_repo(td)
    saved = (PRE_FEATURE_REVISION, REVIEW_SHA)
    PRE_FEATURE_REVISION, REVIEW_SHA = oid_a, oid_review_sha
    original_cwd = os.getcwd()
    os.chdir(repo)
    try:
        yield
    finally:
        os.chdir(original_cwd)
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
    check_resolve_reviewed_commit_guard(validator, failures)
    check_review_sha_binding(validator, config, feature_dir, td, failures)
    check_resolve_review_sha_artifact_path(validator, td, failures)
    check_resolve_review_sha_feature_json(validator, td, failures)
    check_pending_plan_review(validator, config, td, failures)
    check_hook_feature_dir(validator, td, failures)
    check_skipped_member_errors(validator, failures)
    check_branch_corroboration(validator, config, td, failures)


def _check_review_repository(td, failures):
    check_derived_base_range(td, failures)
    check_unresolvable_default_branch(td, failures)
    check_no_merge_base(td, failures)


def _check_review_policy_cases(validator, config, feature_dir, td, failures):
    guarded = check_review_policy(validator, config, feature_dir, failures)
    check_config_errors(validator, config, feature_dir, guarded, failures)
    check_prior_validator(td, guarded, failures)


def run_code_grade_cases():
    spec = importlib.util.spec_from_file_location("_validator_under_test", VALIDATE)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    failures = []
    with tempfile.TemporaryDirectory() as td, _hermetic_review_sha_cwd(td) as _cwd_marker:
        config = os.path.join(td, "harness.json")
        write_review_config(config, "advisory_unless_high")
        feature_dir = make_feature_dir(td)
        _check_review_bindings(validator, config, feature_dir, td, failures)
        _check_review_repository(td, failures)
        _check_review_policy_cases(validator, config, feature_dir, td, failures)
    if failures:
        print("FAIL  code-grade and review-policy gates")
        for failure in failures:
            print(f"        {failure}")
        return 1
    print("ok    code-grade and review-policy gates")
    return 0


def run_empty_red_case():
    """empty-red — proof the empty-string case CAN report red (REQ-05/REQ-06).

    Reverts hook_mode()'s presence branch to the truthiness form it replaced and runs BOTH
    binaries over the SAME payload as the empty-string case. The mutant lives in the
    script's OWN directory because validate-digest.py imports sibling modules from it, so a
    copy in a tmpdir dies at import and the case would pass while measuring nothing. The
    name carries os.getpid() (D-07): that directory is shared and tracked, and two features
    running in parallel under one fixed name means one run's `finally` deletes the other's
    copy mid-read.
    """
    fails = 0

    def bad(detail):
        print("FAIL  [empty-red] %s" % detail)
        return 1

    with open(VALIDATE, encoding="utf-8") as fh:
        source = fh.read()

    # Located by its OWN SOURCE TEXT — never a line number and never a commit ref, both of
    # which go stale silently and turn this proof into a pass that measured nothing.
    head = '    raw = d.get("last_assistant_message", _ABSENT)'
    start = source.find(head)
    end = source.find("\n        return 2\n", start) + len("\n        return 2\n") if start >= 0 else -1
    if start < 0 or end <= start:
        print("FAIL  [empty-red] INCONCLUSIVE: the presence branch was not found by its "
              "source text in %s — the anchor is stale, nothing was measured." % VALIDATE)
        return 1

    truthiness = (
        '    text = d.get("last_assistant_message") or ""\n'
        '    if not text.strip():\n'
        '        print(f"check-digest: {agent} returned no final message to validate.",\n'
        '              file=sys.stderr)\n'
        '        return 0\n')
    mutant_src = source[:start] + truthiness + source[end:]

    mutant = os.path.join(os.path.dirname(os.path.realpath(VALIDATE)),
                          ".validate-digest-empty-red-%d.py" % os.getpid())
    payload = {"agent_type": "harness-qa", "last_assistant_message": "   \n"}
    root = _isolated_root()
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root)
    try:
        with open(mutant, "w", encoding="utf-8") as fh:
            fh.write(mutant_src)
        os.chmod(mutant, os.stat(VALIDATE).st_mode & 0o7777)

        if mutant_src == source:
            return bad("INCONCLUSIVE: the copy is byte-identical to the original, so the "
                       "revert changed nothing and the comparison below is vacuous.")

        def fire(binary):
            return subprocess.run([sys.executable, binary, "--hook"],
                                  input=json.dumps(payload), capture_output=True,
                                  text=True, env=env)

        real = fire(VALIDATE)
        old = fire(mutant)

        # A SyntaxError or NameError exits nonzero with a traceback and would otherwise be
        # indistinguishable from a real verdict, so the mutant's health is asserted first.
        if old.returncode not in (0, 2) or "Traceback (most recent call last)" in old.stderr:
            fails += bad("INCONCLUSIVE: the mutant crashed (exit %d) rather than returning "
                         "a verdict:\n      | %s"
                         % (old.returncode, old.stderr.strip().replace("\n", "\n      | ")))
        if real.returncode != 2:
            fails += bad("the real validator must exit 2 on a blank final message, got %d"
                         % real.returncode)
        if old.returncode != 0:
            fails += bad("the truthiness revert must exit 0 — if it does not, the "
                         "empty-string case is not what proves the fix, got %d"
                         % old.returncode)
    finally:
        try:
            os.remove(mutant)
        except OSError:
            pass

    if not fails:
        print("ok    [empty-red] the empty-string refusal fails against the truthiness revert")
    print("\n%d/1 empty-red cases passed." % (0 if fails else 1,))
    return 1 if fails else 0


def run_dec156_worktree_red_case():
    """dec156-worktree-red: the narrative case fails against the owner-root join."""
    root, _worktree, _rel, payload = _dec156_worktree_case(
        "red-fixture", "# narrative digest, no contract block\n", 2)
    HOOK_CASES.pop()
    payload = dict(payload)
    payload.pop("_root", None)
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root)

    with open(VALIDATE, encoding="utf-8") as source_file:
        source = source_file.read()
    function = source.find("def check_artifact_file(")
    start = source.find("    if os.path.isabs(path):\n", function)
    end = source.find("    found = next(", start)
    if function < 0 or start < 0 or end <= start:
        print("FAIL  [dec156-worktree-red] INCONCLUSIVE: resolution anchors absent")
        return 1
    old_join = ('    cands = ([path] if os.path.isabs(path) else '
                '[os.path.join(_root_or_none() or "", path)])\n')
    mutant_source = source[:start] + old_join + source[end:]
    if mutant_source == source:
        print("FAIL  [dec156-worktree-red] INCONCLUSIVE: mutant is byte-identical")
        return 1

    mutant = os.path.join(os.path.dirname(os.path.realpath(VALIDATE)),
                          ".validate-digest-dec156-red-%d.py" % os.getpid())
    try:
        with open(mutant, "w", encoding="utf-8") as mutant_file:
            mutant_file.write(mutant_source)
        os.chmod(mutant, os.stat(VALIDATE).st_mode & 0o7777)

        def fire(binary):
            return subprocess.run([sys.executable, binary, "--hook"],
                                  input=json.dumps(payload), capture_output=True,
                                  text=True, env=env)

        real = fire(VALIDATE)
        old = fire(mutant)
        ok = (real.returncode == 2 and old.returncode == 0
              and "Traceback (most recent call last)" not in old.stderr)
        if not ok:
            print("FAIL  [dec156-worktree-red] real=%d mutant=%d\n      | %s"
                  % (real.returncode, old.returncode, old.stderr.strip()))
            return 1
        print("ok    [dec156-worktree-red] owner-root join misses the worktree digest")
        return 0
    finally:
        try:
            os.remove(mutant)
        except OSError:
            pass


def main():
    fails = run_cli_cases()
    fails += run_empty_red_case()
    fails += run_dec156_worktree_red_case()
    fails += run_joint_hint_case()
    fails += run_code_grade_cases()
    fails += run_hook_cases()
    fails += run_t09()
    fails += run_template_cases()
    fails += run_reviewer_severity_enum_cases()
    print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILING'}.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
