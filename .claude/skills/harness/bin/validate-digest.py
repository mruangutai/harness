#!/usr/bin/env python3
"""Validate an agent's three-part return against the NORMATIVE DIGEST schema.

WHY: SPEC 8.1 declares the schemas normative and the runner routes on exact field
names and enum values — but nothing validated them except the consuming LLM.
SPEC 8.3 catches MISSING returns, not DRIFTED ones. `severity_max: medium` instead
of `med`, `must-fix` instead of `must_fix`, `matrix_ok: "mostly"` — an LLM reader
charitably normalizes all of those, so drift is invisible by construction and the
system behaves correctly right up until one routing decision doesn't.

EVERY FIELD IS REQUIRED. An absent field is a violation, not a shortcut: silence
is ambiguous ("none found" or "forgot to collate?") while an explicit `[]` is a
positive assertion that the agent looked. Lists say nothing with `[]`; scalars
that can be genuinely inapplicable say it with `none`. This is stricter than the
first version, which skipped absent fields and therefore let a lead digest ship
missing `members:` — the field SPEC calls load-bearing — while reporting "ok".

Usage:  validate-digest.py <persona> [file]      (reads stdin if no file)
        validate-digest.py --hook                 (SubagentStop hook; exit 2 rejects)
Exit 0 = valid.  Exit 1 = contract violation (reasons on stdout).

A violation routes into the BLOCKED (contract violation) path SPEC 8.3 already
defines. Never guess a verdict — silent misrouting is worse than a halt.
"""
import sys, re, os, json

# Same directory as this script; sys.path[0] is that directory under `python3 <path>`.
# The placeholder vocabulary lives there so INV-6 and this check cannot drift (issue #16).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_yaml

VERDICTS = {"PASS", "FAIL", "BLOCKED", "ESCALATE"}
SEV      = ["info", "low", "med", "high", "critical"]

# Required of EVERY persona — the universal return contract (harness-handoff).
UNIVERSAL = {"open_questions": list, "files_touched": list, "expertise_update": list}

# Scalars where "not applicable" is a real answer. The key is still required; the
# value may be `none`/`null`, which asserts inapplicability rather than omitting it.
#
# DEC-173 widened this. An audit of every persona's did-nothing state found 6 of 7
# could not report it truthfully: the honest value was REJECTED while a false one
# was ACCEPTED. A dev refusing an under-specified task had to claim `suite: pass`;
# QA unable to run the suite at all had to claim `matrix_ok: true` — the project's
# only blocking gate, recorded as passed because "did not run" had no spelling.
# That is the fail-open shape this whole file exists to prevent.
#
# `dev-ops`'s `suite` already carried an `n/a` member (below): the vocabulary was
# extended once, where someone hit the wall, and never propagated. This generalises
# it through the mechanism that was already here rather than inventing a second one.
NULLABLE = {"branch", "blocked_on", "briefing",
            # DEC-173 additions — enum scalars whose personas have a legitimate
            # did-nothing state: refusing a task, being unable to run, or scoping
            # out of a diff that has nothing for this role to judge.
            "suite", "matrix_ok", "severity_max", "contract", "surface", "risk",
            # FEAT-07: a dev that refused or was blocked ran no verify command, and
            # `n/a` is its spelling (REQ-03). `task` is deliberately NOT here — its
            # `none` is a DECLARED answer, not a declined one, and NULLABLE would
            # route it into the placeholder branch and out of its own regex check.
            "task_verify"}

# ...but declining to REPORT a gate is not the same as passing it. This is keyed by
# PERSONA as well as field, because the same field means different things by role
# and a field-only rule gets it wrong:
#
#   dev      suite: n/a + PASS  -> REJECTED. It refused or could not run the tests;
#                                  the Iron Law says no production code without a
#                                  passing test, so PASS is unearned.
#   qa       suite/matrix_ok n/a + PASS -> REJECTED. The project's only blocking
#                                  gate did not run. This is the audit's worst row.
#   dev-ops  suite: n/a + PASS  -> ALLOWED. `test_matrix` maps config/scaffolding/
#                                  docs to [] (DEC-100), so "no tests apply" is the
#                                  correct outcome, not a dodge.
#   reviewer severity_max n/a + PASS -> ALLOWED. A ui-reviewer on a non-UI diff
#                                  reviewed nothing and blocks nothing.
#
# So: only the roles whose PASS is *earned by the gate* are bound by it.
#
# FEAT-07 added `task_verify` and with it a SECOND axis, so the exemption is no
# longer "this persona is exempt" but "this persona is exempt from THIS field by
# THIS mechanism". Both axes, stated rather than left to be rediscovered:
#
#   PER FIELD.     dev-ops `suite: n/a` + PASS stays ALLOWED (above), while
#                  dev-ops `task_verify: n/a` + PASS is REJECTED. Every PLAN task
#                  carries a `verify:`, so where a return DECLARES a task, `n/a`
#                  means refused or blocked. No task declared is CONDITIONAL, below.
#   PER MECHANISM. This dict gates only the DECLINED value (`n/a`). Reporting an
#                  outright FAILURE is the separate GATE_FAIL_VALUES table below.
#                  `dev-ops` is absent from `suite` in BOTH, so dev-ops
#                  `suite: fail` + PASS stays accepted — deliberate (D-03), and
#                  recorded as a residue in BRIEF `## Verification gaps`.
GATE_FIELDS = {"dev": {"suite", "task_verify"}, "qa": {"suite", "matrix_ok"},
               "dev-ops": {"task_verify"}}

# ...and declining to report is not the same as REPORTING A FAILURE. Measured at
# 3bfedc9, four rows were accepted that should not have been: dev `suite: fail`,
# qa `suite: fail` and qa `matrix_ok: false`, each alongside `VERDICT: PASS`, all
# returning `digest ok` exit 0. Cause: the GATE_FIELDS check below is nested INSIDE
# the `val in PLACEHOLDER_UNSET` branch, so it can only ever see a placeholder.
#
# Keyed persona -> field -> the value that counts as FAILURE for that field, NOT a
# set of field names, because the failing values differ in TYPE: `suite`/`task_verify`
# fail as the STRING "fail" while `matrix_ok` fails as the BOOLEAN False. A
# string-keyed table would silently never fire on matrix_ok.
#
# The fourth row stays open on purpose: `dev-ops` carries `task_verify` only and must
# NOT gain `suite` (D-03), so dev-ops `suite: fail` + PASS remains accepted.
GATE_FAIL_VALUES = {"dev": {"suite": "fail", "task_verify": "fail"},
                    "qa": {"suite": "fail", "matrix_ok": False},
                    "dev-ops": {"task_verify": "fail"}}

# A field whose obligation is GOVERNED by another field. A dispatch carrying no PLAN
# task has no `verify:` command, so `task_verify` cannot be required of it; `task` is
# what declares which case a return is. Chosen over a bare `no-task` enum value
# (D-07) because `task: none` is a task-id-shaped string that the lead's
# dispatch-carries-the-T-NN-id rule (T-05) gives a cross-reference to.
CONDITIONAL = {"task_verify": "task"}

# A field whose obligation is lifted by what the return BOTH DECLARED and DID.
# An ANALYSIS dispatch -- read this, report that -- writes no production code, so the
# Iron Law binds on nothing: there is no code owed a passing test, and `suite` has no
# gate to decline. Before this, such a return had NO truthful digest. MEASURED
# 2026-08-26: three of four member runs lost their report body to the re-prompt, and
# TWO agents reasoned themselves into a fabricated `suite: pass` to satisfy the schema.
# A schema that teaches agents to misreport the record is worse than no schema.
#
# BOTH CONDITIONS, NEVER ONE. Each closes the other's hole, and both holes were real:
#
#   `task: none` alone       a CLAIM about the dispatch. A return can write it and
#                            still edit ten files, and the Iron Law would be bypassed
#                            on code that exists.
#   `files_touched: []` alone a dev handed a REAL task that REFUSED it also touches
#                            nothing, and its PASS is unearned. The case
#                            "suite: n/a with VERDICT PASS is a fail-open" pins that
#                            exact return -- `task: T-01`, `files_touched: []` -- and
#                            it MUST stay rejected.
#
# Only the pair separates "had nothing to test" from "declined to test".
NOTHING_TO_GATE = {"dev": {"suite"}}


def _nothing_to_gate(field, persona, seen):
    """True when this return declared no task AND changed no file, so `field` would
    gate work that does not exist.

    FAILS CLOSED on anything unexpected -- a missing, unparsed or non-list
    `files_touched`, or any `task` value other than the literal `none`, leaves the
    gate BINDING. The default in the `task` read is load-bearing for the same reason
    `_unbound`'s is: `str(None).lower()` is `"none"` in Python, so a MISSING `task`
    written without it would switch the requirement off.
    """
    if field not in NOTHING_TO_GATE.get(persona, ()):
        return False
    if str(seen.get("task", "")).strip().lower() != "none":
        return False
    touched = seen.get("files_touched")
    return isinstance(touched, list) and not touched

def _unbound(field, seen):
    """True when `field`'s governor declares this dispatch carries no PLAN task.

    The `""` default is LOAD-BEARING: `str(None).lower()` is `"none"` in Python, so
    `seen.get(gov)` written without it would make a MISSING `task` switch the
    requirement off — the conditional mechanism failing open in its own first line.
    Fail closed: no governor value, or any value other than `none`, means it BINDS.
    """
    gov = CONDITIONAL.get(field)
    if gov is None:
        return False
    return str(seen.get(gov, "")).strip().lower() == "none"

# A task id, or the literal `none` for a dispatch that carries no PLAN task. The
# placeholder spelling `T-NN` is REJECTED on purpose — the same zero-placeholder
# discipline harness-tdd-enforcement already applies to task ids. `fullmatch`, never
# `search`: `search` would accept `not-T-01-really`.
TASK_ID_RE = re.compile(r"T-\d+|none")

# field -> (allowed values | type | compiled pattern). Enums are EXACT; near-misses
# are the whole point.
SCHEMAS = {
    "pm": {"feasibility": {"clear","risky","blocked"}, "surface": {"S","M","L"},
           "recommend": {"proceed","spike","reframe","halt"}, "risk": {"low","med","high"},
           "tasks": int, "decisions": int, "needs_approval": bool, "flags": list,
           "sc_status": list},
    # `task_verify` has no `n/a` member on purpose: NULLABLE short-circuits it before
    # the enum check, which is the one mechanism DEC-173 established for "did not
    # happen". There is no fourth member — D-07 rejected the `no-task` spelling.
    "dev": {"tests_added": int, "suite": {"pass","fail"}, "blocked_on": str,
            "task": TASK_ID_RE, "task_verify": {"pass","fail"}},
    "qa": {"suite": {"pass","fail"}, "failures": int, "coverage_gaps": list, "matrix_ok": bool},
    "reviewer": {"severity_max": set(SEV), "findings": int, "must_fix": list},
    "visual-designer": {"contract": {"written","updated"}, "mockups": list, "direction_choices": list},
    "documentor": {"docs_updated": list, "gaps": list},
    # `suite` was {"pass","fail","n/a"} here and {"pass","fail"} everywhere else —
    # the local fix that DEC-173 generalised. The `n/a` member is now redundant
    # (NULLABLE short-circuits before the enum check) and is removed so there is one
    # mechanism for "did not happen", not two that can drift apart.
    "dev-ops": {"change_type": {"config","scaffolding","infra","ci"},
                "applied": list, "suite": {"pass","fail"},
                "task": TASK_ID_RE, "task_verify": {"pass","fail"}},
    # SPEC 10.4 in full. `sc_status` is pm's field (11.6) riding up as a passthrough,
    # surfaced at team level so the orchestrator can read goal-check status without
    # opening member entries; `[]` when this team ran no goal-check.
    "lead": {"team": str, "steps_run": int, "cycles_used": int,
             "members": list, "must_fix": list, "branch": str,
             "escalations": list, "sc_status": list},
    # The main session's schema for harness-orchestrator (reconciled with BUILD task
    # 14, not derived from SPEC — SPEC 10.3 defines a *briefing artifact*, not a
    # digest block, for the orchestrator). These are exactly the fields the main
    # session routes on when the orchestrator returns: `status` decides relay vs.
    # done, `runs`/`cycles_used` are the budget accounting it logs, and
    # `briefing` is the path it presents to the user. Everything else stays on disk
    # in feature.json.
    #
    # The money field this schema used to require is GONE, and a return still
    # carrying it is IGNORED rather than rejected — unknown keys are ignored
    # (measured). Said here so the next reader does not re-add it "to be safe":
    # the harness no longer meters money, and `cycles_used` is the one budget
    # with teeth. Named without its literal spelling on purpose — this task's
    # `verify:` asserts that spelling appears nowhere in this file.
    "orchestrator": {"feature": str,
                      "status": {"in_progress", "in_review", "shipped", "blocked",
                                 "awaiting_user"},
                      "runs": list, "cycles_used": int,
                      "briefing": str},
}
ALIAS = {
    "harness-pm": "pm", "harness-qa": "qa", "harness-documentor": "documentor",
    "harness-dev-ops": "dev-ops", "harness-visual-designer": "visual-designer",
    "harness-frontend-dev": "dev", "harness-backend-dev": "dev",
    "harness-ai-dev": "dev", "harness-data-engineer": "dev",
    "harness-code-reviewer": "reviewer", "harness-security-reviewer": "reviewer",
    "harness-ui-reviewer": "reviewer",
    "harness-product-lead": "lead", "harness-eng-lead": "lead",
    "harness-validator-lead": "lead",
    "harness-orchestrator": "orchestrator",
}

def norm(p):
    return ALIAS.get(p, ALIAS.get("harness-" + p, p))

def strip_comment(v):
    """Drop a trailing YAML `# comment`, respecting quotes and brackets.

    Not cosmetic. SPEC 10.4 and the runner both annotate their templates inline, so
    an agent copying either writes `steps_run: 3   # …`. Without this, that parsed as
    the STRING "3   # …" and failed "must be an integer", and worse — `members:   # …`
    parsed as a scalar, so the block list under it was never seen. The validator
    rejected its own documented format.

    A `#` inside quotes or brackets is content: `headline: "fixes #42"`.
    """
    out, q, depth = [], None, 0
    for i, c in enumerate(v):
        if q:
            out.append(c)
            if c == q:
                q = None
            continue
        if c in "\"'":
            q = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth = max(0, depth - 1)
        elif c == "#" and depth == 0 and (i == 0 or v[i - 1] in " \t"):
            break
        out.append(c)
    return "".join(out).strip()


_QUOTE_STARTS_AFTER = set(",:[{ \t") | {None}

def split_items(s):
    """Split an inline YAML list on top-level commas only.

    A naive `s.split(",")` shreds structured entries: the members list is written
    `[{ step: s1, persona: qa, verdict: PASS }, ...]`, and splitting every comma
    turns one entry into three fragments — none of which carries a `verdict:`, so
    the roll-up check reported four bogus violations against a valid digest.

    Two hardenings (BUILD task 22, F1):

    - A quote only OPENS a quoted value when it starts a token — the char before it
      is a delimiter, bracket or whitespace (or nothing). An unescaped apostrophe
      mid-word (`didn't finish`) is real text, not a quote: it followed a letter.
      Treating every `'` as a toggle let one apostrophe swallow the rest of the
      list — including the next entry's `verdict:` — and fuse two entries into one,
      masking whichever verdict lost the fusion.
    - `depth` is now floored at 0, matching `strip_comment`. An unguarded `depth -= 1`
      lets a stray closing bracket drive depth negative, after which top-level commas
      never split again for the rest of the string — the same fusion failure as the
      apostrophe case, by a different route. Not in the panel's repro list; found
      while hardening the sibling function.
    """
    items, buf, depth, q, prev = [], [], 0, None, None
    for c in s:
        if q:
            buf.append(c)
            if c == q:
                q = None
            prev = c
            continue
        if c in "\"'" and prev in _QUOTE_STARTS_AFTER:
            q = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth = max(0, depth - 1)
        elif c == "," and depth == 0:
            items.append("".join(buf).strip())
            buf = []
            prev = c
            continue
        buf.append(c)
        prev = c
    if "".join(buf).strip():
        items.append("".join(buf).strip())
    return [i for i in items if i]


def top_level_colon(s):
    """Index of the first ':' at depth 0, outside quotes — or None.

    Splitting a member-entry field on the FIRST colon found anywhere (a bare
    `re.search`) is exactly the bug this validator exists to catch elsewhere: a
    quoted value that happens to contain `verdict: PASS` as TEXT (e.g. a headline
    reporting a retry) matches before the real `verdict:` key is ever reached.
    """
    depth, q, prev = 0, None, None
    for i, c in enumerate(s):
        if q:
            if c == q:
                q = None
            prev = c
            continue
        if c in "\"'" and prev in _QUOTE_STARTS_AFTER:
            q = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth = max(0, depth - 1)
        elif c == ":" and depth == 0:
            return i
        prev = c
    return None


def parse_member_entry(item):
    """A members-list entry (inline `{ ... }` or joined block-mapping lines) into
    {field: value}, keyed by NAME rather than by "first colon-like text anywhere"
    (F1) — the roll-up must read the `verdict:` KEY, never grep for the substring.
    """
    s = item.strip()
    if s.startswith("{"):
        s = s[1:]
        if s.endswith("}"):
            s = s[:-1]
    d = {}
    for part in split_items(s):
        idx = top_level_colon(part)
        if idx is None:
            continue
        d[part[:idx].strip()] = parse_scalar(part[idx + 1:])
    return d


def bracket_depth(s):
    """Net `[`/`{` depth of `s`, respecting quotes. Positive means unclosed.

    Uses the SAME quote-starts-after-a-delimiter heuristic as `split_items` — an
    earlier version toggled on every `'`/`"` unconditionally, so an unquoted
    apostrophe mid-word (`didn't`) opened a quote with no matching close, and
    everything after it (including the real closing brackets) was read as quoted
    content. That silently reported a well-formed inline list as `_UNPARSED`.
    """
    depth, q, prev = 0, None, None
    for c in s:
        if q:
            if c == q:
                q = None
            prev = c
            continue
        if c in "\"'" and prev in _QUOTE_STARTS_AFTER:
            q = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
        prev = c
    return depth


_UNPARSED = object()  # sentinel: an inline value whose brackets never balanced


def parse_scalar(v):
    v = v.strip().strip('"\'')
    if v.lower() in ("true", "false"): return v.lower() == "true"
    if re.fullmatch(r"-?\d+", v): return int(v)
    if v.startswith("["): return split_items(v[1:-1])
    return v

def parse_digest(text):
    """Read the DIGEST block into {field: value}, honouring BOTH YAML list styles.

    This replaced a one-line `re.findall(r"^\\s*(key):\\s*(.*)$")`, which had two
    defects that between them made a correct lead digest impossible to write:

    1. `\\s*` after the colon MATCHES NEWLINES. A key with a block-style value
       therefore swallowed the first line of that block as its own scalar, so
       `members:` parsed as the string "- { step: build, ... }" and was reported as
       "must be a list" — while `steps_run` and `cycles_used`, sitting on the same
       source line as `team:` in SPEC 10.4's own template, were never seen at all.
       The normative example in the spec could not pass the validator that enforces it.
    2. It harvested keys at EVERY depth. A `must_fix:` nested inside one member entry
       satisfied the top-level `must_fix` requirement — a false pass on exactly the
       roll-up field the lead digest exists to carry.

    So: values never cross a line, and only keys at the DIGEST block's own indent
    are digest fields. Deeper keys belong to a member entry and are that member's.

    Two BUILD-task-22 hardenings on top of the above:

    - `DIGEST:` may carry a trailing `# comment` (F4). SPEC 8's own template does —
      `DIGEST:                             # routing — orchestrator reads THIS…` —
      so requiring an exact end-of-line match rejected the format this validator's
      own docs teach agents to copy.
    - A block-list entry now absorbs CONTINUATION lines, not just its own `- ` line
      (F5): standard YAML block-mapping (`- step: s1` / newline / `  verdict: PASS`)
      is legal and SPEC 10.4's `escalations` example is written exactly that way.
      Discarding continuation lines silently dropped every field but the first.
    - A key's inline value may itself span multiple lines (`members: [` / entries /
      `]`) — legal YAML, and the multi-line members list is a real F1 repro. Rather
      than truncate at the first line (which silently produced `[]` and made the
      roll-up guard decorative), unclosed brackets/braces are followed across lines
      until they balance. If they never do, the field is `_UNPARSED` — reported as a
      violation, never silently coerced to an empty list.
    """
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if re.match(r"^\s*DIGEST:\s*(#.*)?$", l)), None)
    if start is None:
        return {}

    body = lines[start + 1:]
    # Base indent = the first real key under DIGEST:. Everything deeper is nested.
    base = next((len(l) - len(l.lstrip())
                 for l in body
                 if l.strip() and re.match(r"^\s*[a-z_][a-z0-9_-]*:", l)), None)
    if base is None:
        return {}

    out = {}
    n = len(body)
    i = 0
    while i < n:
        line = body[i]
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base:
            break                      # dedented out of the block (`artifact:`)
        if indent != base:
            i += 1
            continue                   # nested — belongs to a member, not to us
        # NOTE the hyphen in the class: a drifted key like `must-fix` must be PARSED
        # before it can be reported as drift. Omitting it made this validator blind
        # to exactly the defect class it exists to catch.
        m = re.match(r"^\s*([a-z_][a-z0-9_-]*):[ \t]*(.*)$", line)
        if not m:
            i += 1
            continue
        k, v = m.group(1), strip_comment(m.group(2))
        if v:
            if v[0] in "[{" and bracket_depth(v) > 0:
                # Unclosed on this line — an inline list/map spanning lines.
                joined = v
                j = i + 1
                while j < n and bracket_depth(joined) > 0:
                    joined += " " + strip_comment(body[j]).strip()
                    j += 1
                out[k] = parse_scalar(joined) if bracket_depth(joined) == 0 else _UNPARSED
                i = j
                continue
            out[k] = parse_scalar(v)
            i += 1
            continue
        # Empty value: a block list if the next non-blank deeper line is an item.
        # Each `- ` line starts a new entry; subsequent deeper lines that are NOT
        # a new `- ` are continuation lines of the entry just opened (F5) — joined
        # with ", " for block-mapping style (`step: s1` / `verdict: PASS`, no
        # existing separator) or with " " for an inline `{ ... }` still balancing
        # its own brackets across lines.
        items, cur, cur_is_brace = [], None, False
        j = i + 1
        while j < n:
            nxt = body[j]
            if not nxt.strip():
                j += 1
                continue
            nind = len(nxt) - len(nxt.lstrip())
            if nind <= base:
                break
            stripped = strip_comment(nxt.lstrip())
            if nxt.lstrip().startswith("- "):
                if cur is not None:
                    items.append(cur)
                cur = stripped[2:]
                cur_is_brace = cur.lstrip().startswith("{")
            elif cur is not None:
                if cur_is_brace:
                    if bracket_depth(cur) > 0:
                        cur += " " + stripped
                    # else: balanced already — stray deeper content, not ours.
                else:
                    cur += ", " + stripped
            j += 1
        if cur is not None:
            items.append(cur)
        # `key:` with nothing under it is an EMPTY LIST, not a missing field. Writing
        # a bare `escalations:` is the natural way to say "none" and must not read as
        # an omission — the point of requiring the key is that the agent asserted it.
        out[k] = items
        i = j
    return out


def validate(persona, text):
    err = []
    persona = norm(persona)
    schema = SCHEMAS.get(persona)
    if schema is None:
        return [f"unknown persona {persona!r} — cannot validate; refusing to pass it."]

    # Echo-shadowing fix (BUILD task 22 follow-up): agents sometimes echo the
    # harness-handoff template (a schema-valid VERDICT/DIGEST block) before their
    # real return. Every anchor below is first-match, so the echo used to shadow
    # the real block. The contract mandates the real return LAST, so slice from
    # the last line-start VERDICT: and validate only that. No anchor at all keeps
    # whole-text behavior — the "no VERDICT" path stays byte-identical.
    anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))
    if anchors:
        text = text[anchors[-1].start():]

    # --- VERDICT: exact token, exact spelling.
    m = re.search(r"^\s*VERDICT:\s*(\S+)", text, re.M)
    if not m:
        err.append("no VERDICT: line — this is a contract violation, not a verdict of any kind.")
    elif m.group(1) not in VERDICTS:
        err.append(f"VERDICT is {m.group(1)!r}; must be exactly one of {sorted(VERDICTS)}.")

    if not re.search(r"^\s*DIGEST:", text, re.M):
        err.append("no DIGEST: block.")
    if not re.search(r"^\s*artifact:\s*\S+", text, re.M):
        err.append("no artifact: path.")

    seen = parse_digest(text)

    # F7: `headline` must be at the DIGEST block's OWN level, read from `seen` (which
    # only holds base-indent keys) rather than matched anywhere in the text at any
    # depth. A lead digest with no top-level headline but a block-style member that
    # happens to carry its own `headline:` used to pass — the orchestrator routes on
    # the TOP-level headline and never opens member entries.
    hl = seen.get("headline")
    if not (isinstance(hl, str) and hl.strip()):
        err.append("DIGEST has no headline: — the orchestrator routes on this.")

    # --- catch DRIFTED key spellings before reporting them as merely missing.
    # F15: iterate the FULL field set (schema + universal), not schema alone — a
    # universal field like `files_touched` drifting to `files-touched` was reported
    # as merely missing rather than as the drift it is; fails closed either way, but
    # the wrong message.
    all_fields = {**schema, **UNIVERSAL}
    for k in list(seen):
        for want in all_fields:
            if k != want and k.replace("-", "_").lower() == want:
                err.append(f"key {k!r} is drifted spelling of {want!r} — the runner "
                           f"routes on the exact name and will not see it.")

    for field, allowed in all_fields.items():
        if field not in seen:
            # D-08(a): with `task: none` this dispatch carries no PLAN task, so a
            # governed field is not required of it at all.
            if _unbound(field, seen):
                continue
            # REQ-11: a hint must name a value that will actually VALIDATE. Before
            # this, `task_verify` inherited "write `none`" — which the gate above
            # then rejects alongside PASS — and `task` would have inherited "write
            # `[]`", which its own regex rejects. Four branches, most specific first.
            if isinstance(allowed, re.Pattern):
                hint = ("your task's `T-NN` id exactly as your dispatch carries it "
                        "(T-05), or `none` if this dispatch carries no PLAN task")
            elif field in GATE_FIELDS.get(persona, ()) and isinstance(allowed, set):
                # The isinstance guard is not decoration: qa's `matrix_ok` is in
                # GATE_FIELDS with `allowed is bool`, and sorted() over a type raises.
                #
                # WORDING: do NOT say a placeholder is disallowed. This branch also
                # fires on a missing `suite` for dev, and `suite: n/a` with BLOCKED is
                # LEGAL (REQ-03/SC-06). The gate is on the PAIRING, so the hint says so.
                vals = sorted(a for a in allowed if isinstance(a, str))
                hint = (f"one of {vals} — what gets rejected for this role is a "
                        f"placeholder ALONGSIDE `VERDICT: PASS`, never the placeholder "
                        f"itself (`n/a` with FAIL or BLOCKED is the honest refusal)")
                # JOINTLY FOLLOWABLE (SC-18c). Without this clause a return omitting
                # both fields gets hint (8a) offering `task: none` and this hint
                # demanding a real value — and `task: none` + `task_verify: pass` is
                # then rejected by the conditional. A hint routing an agent into a
                # second rejection is REQ-11's own defect class, re-created by its fix,
                # and the re-prompted return is NOT re-validated (see below).
                if field in CONDITIONAL:
                    hint += (f", or omit this field entirely if this dispatch carries "
                             f"no PLAN task and you wrote `{CONDITIONAL[field]}: none`")
            elif field in NULLABLE:
                hint = "`none` if genuinely not applicable"
            else:
                hint = "`[]` if there are none"
            # HONEST LIMIT: a re-prompted return is not re-validated —
            # `:845` is `if d.get("stop_hook_active"): return 0` — so a hint naming a rejectable
            # value ships the second attempt unvalidated. That passthrough is
            # pre-existing and deliberate; this edit stops the hint POINTING at it and
            # does not close it.
            err.append(f"missing {field!r} — every field is required; write {hint}. "
                       f"An absent field is ambiguous; an explicit empty one asserts you looked.")
            continue
        val = seen[field]
        if val is _UNPARSED:
            err.append(f"{field!r} could not be parsed — its brackets/quotes never "
                       f"balanced. Fix the YAML rather than resubmitting as-is.")
            continue
        # D-08(b)/(c). Placed BEFORE the NULLABLE branch on purpose: after it,
        # D-08(b) would be unreachable for a placeholder value.
        if _unbound(field, seen):
            if isinstance(val, str) and val.lower() in harness_yaml.PLACEHOLDER_UNSET:
                # D-08(b): `n/a` is the honest DEC-121 spelling for a field with no
                # answer, and the n/a-with-PASS gate does NOT bind here — there was no
                # gate to decline.
                continue
            # D-08(c): the `continue` below short-circuits both the enum check and the
            # fail gate, so this produces exactly ONE error, naming the actionable
            # field, rather than two that disagree about what is wrong.
            err.append(f"{field}={val!r} but {CONDITIONAL[field]}=none — a dispatch "
                       f"carrying no PLAN task has no verify: command to report on. "
                       f"Omit {field} or write `n/a`, or name the task's T-NN id in "
                       f"`{CONDITIONAL[field]}`.")
            continue
        if field in NULLABLE and isinstance(val, str) and val.lower() in harness_yaml.PLACEHOLDER_UNSET:
            # DEC-173: declining a GATE while claiming PASS is the fail-open the
            # widened NULLABLE would otherwise have created. Reported here rather
            # than as a separate pass so the message lands next to the field.
            if field in GATE_FIELDS.get(persona, ()) and m and m.group(1) == "PASS" \
                    and not _nothing_to_gate(field, persona, seen):
                err.append(f"{field}={val!r} declines to report a gate, but VERDICT is "
                           f"PASS — a gate that did not run cannot have passed. Return "
                           f"BLOCKED or FAIL, or report the real result.")
            continue
        # THE FAIL-VALUE GATE. Deliberately OUTSIDE the placeholder branch above —
        # nesting it inside is exactly why `suite: fail` + PASS was accepted for five
        # features. ADDITIVE: it appends and does not `continue`, so a value that is
        # both a gate failure and a schema violation still reports both.
        expected = GATE_FAIL_VALUES.get(persona, {})
        if field in expected and m and m.group(1) == "PASS":
            want = expected[field]
            # TYPE-STRICT, and the reason is not stylistic: `0 == False` is True in
            # Python, so a bare equality would fire on `matrix_ok: 0`.
            # `isinstance(0, bool)` is False, which is what makes this correct.
            if val == want and isinstance(val, type(want)):
                err.append(f"{field}={val!r} reports a gate as FAILED, but VERDICT is "
                           f"PASS — a gate that failed cannot have passed. Fix until it "
                           f"passes, or return FAIL or BLOCKED.")
        if isinstance(allowed, set):
            # F: fail-open crash. `val` can be a LIST (`severity_max: [low, med]`
            # parses via parse_scalar's `[...]` branch) while `allowed` is a set —
            # `val not in allowed` then raises TypeError on the unhashable list,
            # which propagated all the way out of `validate()` uncaught. In `--hook`
            # mode that meant exit 1, and only exit 2 blocks (DEC-100/DEC-122), so
            # the ENTIRE gate went dark for that return with no signal. Report it as
            # the real violation it is instead of crashing past it.
            if isinstance(val, list):
                err.append(f"{field}={val!r} must be a single value from "
                           f"{sorted(a for a in allowed if isinstance(a, str))}, not a list.")
            elif val not in allowed:
                extra = ""
                if isinstance(val, str):
                    near = [a for a in allowed if isinstance(a, str)
                            and (a.startswith(val[:3]) or val.startswith(a[:3]))]
                    if near: extra = f" (did you mean {near[0]!r}?)"
                err.append(f"{field}={val!r} is not in {sorted(allowed)}{extra}.")
        elif isinstance(allowed, re.Pattern):
            # LOAD-BEARING, not stylistic. Measured in the interpreter: a re.Pattern
            # is not a set and is none of bool/int/list/str, so WITHOUT this branch it
            # falls through the whole chain in SILENCE and `task: bogus` is ACCEPTED —
            # the "unknown key ignored" shape this file exists to remove.
            if not (isinstance(val, str) and allowed.fullmatch(val)):
                err.append(f"{field}={val!r} is not a task id — write your task's "
                           f"`T-NN` id exactly as your dispatch carries it (T-05), or "
                           f"`none` if this dispatch carries no PLAN task.")
        elif allowed is bool and not isinstance(val, bool):
            err.append(f"{field}={val!r} must be a bool, not {type(val).__name__} "
                       f"— a string like \"mostly\" silently soft-fails a hard gate.")
        elif allowed is int and (not isinstance(val, int) or isinstance(val, bool)):
            # F12/bool: `bool` is an `int` subclass in Python — `open_questions: true`
            # parsed by `parse_scalar` to `True` would otherwise pass an `int` field.
            err.append(f"{field}={val!r} must be an integer.")
        elif allowed is list and not isinstance(val, list):
            err.append(f"{field}={val!r} must be a list.")
        elif allowed is str and not (isinstance(val, str) and val.strip()):
            # F12: `str`-typed fields (`team`, `branch`, `blocked_on`,
            # `briefing`) hit no type branch at all before this — `team: 7` passed
            # as an int, and a bare `branch:` with nothing under it parsed to `[]`
            # and passed, though DEC-121 requires the literal `none` for an
            # inapplicable NULLABLE scalar, not silence.
            err.append(f"{field}={val!r} must be a non-empty string"
                       + (" (write the literal `none` if genuinely inapplicable)."
                          if field in NULLABLE else "."))

    # --- LEAD ROLL-UP: the top verdict must be the WORST member verdict (SPEC 10.4).
    #
    # This is the only part of collation that is arithmetic rather than judgement, and
    # it was the one thing stated in prose with a validator sitting next to it that
    # could check it and didn't — the DEC-19 / DEC-110 / DEC-119 shape exactly. A lead
    # reporting PASS over a failing member is the single most consequential digest
    # error possible: the orchestrator routes on VERDICT and never opens member
    # entries (SPEC 8), so a masked FAIL ships.
    #
    # ESCALATE outranks FAIL deliberately: a decision only the user can make must not
    # be hidden behind a failure the team could have fixed.
    if persona == "lead" and m:
        members = seen.get("members")
        steps_run = seen.get("steps_run")
        # F1 cross-check: `members: []` alongside `steps_run: 3` used to sail
        # through — SPEC 10.4 calls `members` "NOT optional", and a team that ran
        # steps but reported zero members is never legitimate. Checked whether or
        # not the roll-up itself can run, since an empty list makes the roll-up a
        # no-op (there is nothing to rank).
        if (isinstance(members, list) and isinstance(steps_run, int)
                and len(members) == 0 and steps_run > 0):
            err.append(f"members: [] but steps_run={steps_run} — a team that ran "
                       f"{steps_run} step(s) reported zero members; that is never "
                       f"legitimate (SPEC 10.4: members is NOT optional).")

        if isinstance(members, list) and members:
            RANK = {"PASS": 0, "FAIL": 1, "ESCALATE": 2, "BLOCKED": 3}
            top = m.group(1)
            worst, worst_src = None, None
            for item in members:
                fields = parse_member_entry(str(item))
                mv = fields.get("verdict")
                if not mv:
                    # Their data, not our bug — the normative template carries a
                    # verdict in every member entry, and without one the roll-up is
                    # undecidable. Looked up by KEY, never by matching `verdict:`
                    # as text anywhere in the entry (F1) — a quoted headline like
                    # `"verdict: PASS on retry"` must not satisfy this.
                    err.append(f"a members entry has no verdict: — {str(item)[:60]!r}. "
                               f"Every member entry needs one; the team verdict is the "
                               f"worst of them and cannot be computed otherwise.")
                    continue
                v = str(mv).upper()
                if v not in RANK:
                    err.append(f"member verdict {mv!r} is not one of "
                               f"{sorted(RANK)} — the roll-up cannot rank it.")
                    continue
                if worst is None or RANK[v] > RANK[worst]:
                    worst, worst_src = v, str(item)[:60]
            if worst and top in RANK and RANK[top] < RANK[worst]:
                err.append(f"VERDICT is {top} but a member returned {worst} "
                           f"({worst_src!r}). The team verdict is the WORST member verdict "
                           f"— BLOCKED > ESCALATE > FAIL > PASS. The orchestrator routes on "
                           f"your VERDICT and never opens member entries, so reporting "
                           f"{top} here hides the {worst}.")

    # --- open_questions is a LIST of structured items, never a count (SPEC 8).
    # F13: read from `seen` — the parsed, DIGEST's-own-level value — rather than a
    # whole-text regex. The old regex matched a NESTED `open_questions: 0` (e.g.
    # inside a member entry) appearing before the real top-level key, producing a
    # false positive on an otherwise valid digest — the exact nesting bug
    # `parse_digest` was written to fix, left live in this one check.
    oq_val = seen.get("open_questions")
    if isinstance(oq_val, int) and not isinstance(oq_val, bool):
        err.append("open_questions is a COUNT; it must be a list of structured items — "
                   "it is an active routing signal, not a tally.")
    return err


def _root_or_none():
    """This checkout's root, from harness_boundary — or None if there is not one (FEAT-42
    T-17).

    NONE RATHER THAN A RAISE. Every caller here treats an unresolvable root as "the errand
    could not be run", never as a verdict: this hook validates digests, and the registry and
    the artifact-shape check are side errands that may not change what it returns.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        import harness_boundary
        return harness_boundary.resolve_root(
            os.path.dirname(os.path.realpath(__file__)), strict=False)
    except Exception:
        return None


def check_artifact_file(agent, text, payload):
    """DEC-156: a lead's WRITTEN digest.md must carry the same §10.4 block.

    The FEAT-02 (kaya-ai) audit found all 14 run digest.md files were narrative
    markdown with no contract block — every in-message return had passed this
    hook, so nothing ever looked at the durable copy, which is the one a
    successor context actually reads. Validate the file at the return's
    `artifact:` path with the same schema, while the lead is still alive to fix
    it.

    FAIL OPEN, LOUDLY when the file cannot be located or read: a hook whose cwd
    drifts (worktrees, unset CLAUDE_PROJECT_DIR) must not block a legitimate
    lead on our own resolution bug. check-state.sh INV-15 is the deterministic
    backstop that runs from repo root and catches what this pass-through misses.
    Blocking is for THEIR contract violation, never our lookup failure.
    """
    # Same tail-anchor discipline as validate(): the real return is LAST, so an
    # echoed template's `artifact:` line must not win. Take the final match.
    tail = text
    anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))
    if anchors:
        tail = text[anchors[-1].start():]
    m = None
    for m in re.finditer(r"^\s*artifact:\s*(\S+)", tail, re.M):
        pass
    if not m:
        return 0  # validate() already required artifact:; nothing to resolve here.
    path = strip_comment(m.group(1)).strip("\"'")
    if not path.endswith("digest.md"):
        # The lead artifact contract is <run_dir>/digest.md; a differently-named
        # artifact is INV-15's finding (it can see the run dir), not this hook's.
        return 0

    # ONE ROOT, NOT A CANDIDATE WALK (FEAT-42 T-17). What stood here tried the payload cwd,
    # then the two-name environment chain, then os.getcwd(). Payload cwd is DELETED as a root
    # input and that is a ruling, not a preference: NOTHING sets where an agent stands — the
    # Agent tool has no cwd parameter, `cd` does not persist between Bash calls, and
    # bash-write-guard refuses it — so cwd stays inherited from the spawning session and
    # varies by accident.
    cands = ([path] if os.path.isabs(path) else [os.path.join(_root_or_none() or "", path)])
    found = next((p for p in cands if os.path.isfile(p)), None)
    if not found:
        print(f"check-digest: {agent}'s artifact {path} not found from the hook's vantage — "
              f"file-shape check skipped; check-state.sh INV-15 will audit it from repo root.",
              file=sys.stderr)
        return 0
    try:
        ferrs = validate(agent, open(found, encoding="utf-8").read())
    except Exception as e:
        print(f"check-digest: internal error validating {found} ({e!r}) — passing through; "
              f"this is our bug, not theirs.", file=sys.stderr)
        return 0
    if not ferrs:
        return 0
    print(f"Your return is valid, but the digest FILE you wrote ({path}) does not carry the "
          f"same contract block — and the file is what a successor context reads (DEC-156). "
          f"Rewrite it as the §10.4 return (VERDICT / DIGEST / artifact), prose assessment "
          f"below the block:", file=sys.stderr)
    for e in ferrs:
        print(f"  - {e}", file=sys.stderr)
    return 2


def hook_mode():
    """SubagentStop hook: reject a malformed digest at source.

    Exit 2 "prevents the subagent from stopping", so the agent must fix its return
    before it can finish — enforcement rather than a request. This is the same
    answer DEC-19 reached for domain enforcement: prose guarding a contract is
    unenforceable, so a script guards it instead.

    THREE PASS-THROUGHS, each deliberate:

    1. No `agent_type`, or a non-harness one. `Explore`, `general-purpose` and any
       other agent share this hook and have no digest contract. Governing them
       would break every unrelated subagent in the project.
    2. `stop_hook_active`. Set when we are already re-running because a stop hook
       blocked. Blocking again is an infinite loop with no operator escape.
    3. Our own failure — unreadable payload, unknown persona, an exception. We
       fail OPEN and say so on stderr. check-domain.sh set this precedent for the
       same reason: a hook that blocks on its own bug wedges every agent in every
       project the moment a payload shape changes. Blocking is for THEIR contract
       violation, never ours.
    """
    try:
        d = json.load(sys.stdin)
    except Exception as e:
        print(f"check-digest: unreadable hook payload ({e}) — passing through.", file=sys.stderr)
        return 0

    # F6: absent `agent_type` and a PRESENT non-harness one are different situations
    # and used to be silently identical. A present `Explore`/`general-purpose` value
    # is a correct, silent decline to govern — that agent has no digest contract. A
    # MISSING key is either the same thing, or the payload key was renamed and this
    # hook just went dark project-wide with no signal (the DEC-110 shape). Loud in
    # the second case, silent in the first.
    if "agent_type" not in d or not d.get("agent_type"):
        print("check-digest: hook payload has no agent_type — passing through. If this "
              "is unexpected, the payload key may have been renamed and this hook is "
              "silently no-oping project-wide.", file=sys.stderr)
        return 0
    agent = d["agent_type"]
    if not agent.startswith("harness-"):
        return 0
    if d.get("stop_hook_active"):
        return 0

    # -----------------------------------------------------------------------
    # T-09 — issue #551. TWO steps, in THIS order: release first, then the
    # return contract. Reversed, an agent refused at step two would never have
    # its own claim released and would leak it until the TTL.
    #
    # NEITHER STEP MAY EVER CHANGE THE VERDICT. This hook validates digests;
    # the registry is a side errand. Every failure below is swallowed and
    # reported, never raised, never returned.
    # -----------------------------------------------------------------------
    _reg = None
    try:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        import inflight_registry as _reg
    except Exception as _e:
        print(f"check-digest: inflight_registry unavailable ({_e!r}) — the #551 claim was "
              f"neither released nor checked. This is our gap, not theirs.", file=sys.stderr)

    if _reg is not None:
        # THE ROOT COMES FROM THE ONE RESOLVER (FEAT-42 T-17), not from a walk starting at
        # the payload cwd. The old note here said cwd had to come first so this released from
        # the same registry dispatch-guard.sh wrote to — but that guard now takes its root
        # from the DECLARED feature (T-18), not from where the dispatcher happened to stand,
        # so the two agree without either of them reading a cwd. Nothing sets an agent's cwd,
        # which is why it was never a root.
        _root = _root_or_none()

        if _root is None:
            print("check-digest: no checkout root from this vantage — the #551 claim was "
                  "neither released nor checked.", file=sys.stderr)
        else:
            # STEP ONE — THE RELEASE. OMP supplies feature and runtime identity, so its
            # idempotent yield path can release exactly one claim even when the same persona
            # is active in another feature. Claude Code retains the compatibility fallback.
            _feature = d.get("harness_feature")
            _agent_id = d.get("harness_agent_id")
            _job_id = d.get("harness_job_id")
            try:
                _released = _reg.release(
                    _root,
                    agent=agent,
                    feature=_feature,
                    agent_id=_agent_id,
                    job_id=_job_id,
                )
                if _released:
                    print(f"check-digest: released the #551 claim for {agent}.",
                          file=sys.stderr)
            except Exception as _e:
                print(f"check-digest: could not release {agent}'s claim ({_e!r}) — it will "
                      f"expire or reconcile on supervisor loss. Not blocking on our own errand.",
                      file=sys.stderr)

            # STEP TWO — THE D-09 RETURN CONTRACT. Fires AT MOST ONCE per return, which is
            # not a wait: a lead cannot be made to wait for its children, and D-09 records
            # that as an impossibility rather than working around it. What this catches is
            # FALSE REPORTING — occurrence 7 committed a verdict asserting a member's work
            # was empty and unrecoverable while that member was still running and later
            # returned PASS.
            if norm(agent) in ("lead", "orchestrator"):
                try:
                    # THE SESSION FILTER IS THE FIX FOR THE CASCADE (FEAT-42 T-17, #742/#866).
                    # A claim stranded by ANOTHER session is not a live child of THIS return.
                    # Measured 2026-08-26: one stranded pm claim refused the pm spawn at
                    # dispatch-guard, then refused the LEAD's return here, then refused the
                    # ORCHESTRATOR's return here again — three tiers locked out of reporting
                    # by one strand, each stranding creating the next.
                    _kids = _reg.live_children(
                        _root,
                        agent,
                        session=d.get("session_id"),
                        feature=_feature,
                    )
                except Exception as _e:
                    _kids = []
                    print(f"check-digest: could not read children of {agent} ({_e!r}) — the "
                          f"#551 return contract is not enforced for this return.",
                          file=sys.stderr)
                if _kids:
                    for _line in _reg.children_refusal_lines(agent, _kids):
                        print(_line, file=sys.stderr)
                    # AND THE PRECISE REMEDY, ONE COMMAND PER STRANDED CHILD. The refusal
                    # named the problem and no cure, so a reader reached for release-all —
                    # which sets the registry to {} and wipes every claim of every agent.
                    # On 2026-08-26 following that advice would have destroyed a live claim.
                    try:
                        print("  if one of these is stranded rather than running, release "
                              "exactly it:", file=sys.stderr)
                        for _persona, _c in _kids:
                            print(
                                "  %s" % _reg.release_cmd(
                                    _root, _persona, feature=_c.get("feature")
                                ),
                                file=sys.stderr,
                            )
                    except Exception as _e:
                        print(f"check-digest: could not compose the release command "
                              f"({_e!r}).", file=sys.stderr)
                    return 2

    text = d.get("last_assistant_message") or ""
    if not text.strip():
        print(f"check-digest: {agent} returned no final message to validate — passing through.",
              file=sys.stderr)
        return 0

    if norm(agent) not in SCHEMAS:
        print(f"check-digest: no schema for {agent} — passing through rather than "
              f"blocking on our own gap.", file=sys.stderr)
        return 0

    # Fail OPEN, LOUDLY on our own bug (check-domain.sh's precedent) — never crash
    # to an ambiguous exit. Before this, any exception raised inside `validate()`
    # (e.g. the enum/list TypeError above, pre-fix) propagated uncaught, exited 1,
    # and — because only exit 2 blocks (DEC-100/DEC-122) — the digest shipped
    # completely unvalidated with no signal at all. That is a worse outcome than
    # the "decline to govern" pass-throughs above, which at least say so.
    try:
        errs = validate(agent, text)
    except Exception as e:
        print(f"check-digest: internal error validating {agent}'s return ({e!r}) — "
              f"passing through; this is our bug, not theirs.", file=sys.stderr)
        return 0
    if not errs:
        # Message valid. For leads, the DURABLE copy must comply too (DEC-156) —
        # the orchestrator's successor reads runs/<id>/digest.md, never this message.
        if norm(agent) == "lead":
            return check_artifact_file(agent, text, d)
        return 0

    print(f"Your return does not satisfy the digest contract, so it cannot be accepted. "
          f"Fix these and return again — every field is required; say nothing with an "
          f"explicit `[]`, or `none` for a scalar that genuinely does not apply:",
          file=sys.stderr)
    for e in errs:
        print(f"  - {e}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    if "--hook" in sys.argv:
        sys.exit(hook_mode())
    # F14: CLI mode crashed with UnicodeEncodeError under an ASCII locale
    # (LC_ALL=C), truncating the printed reasons before the operator saw them.
    # Hook mode was already safe (stderr defaults to backslashreplace); make
    # stdout match it rather than raise on a non-ASCII byte in a digest value.
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except Exception:
        pass
    if len(sys.argv) < 2:
        print("usage: validate-digest.py <persona> [file]   |   --hook  (SubagentStop)"); sys.exit(2)
    text = open(sys.argv[2]).read() if len(sys.argv) > 2 else sys.stdin.read()
    errs = validate(sys.argv[1], text)
    if errs:
        print("VERDICT: BLOCKED (contract violation)")
        for e in errs: print(f"  - {e}")
        sys.exit(1)
    print("digest ok")
