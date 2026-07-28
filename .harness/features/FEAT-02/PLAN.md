# PLAN — FEAT-02

## Decisions

- D-01 — **Template-echo lines are not verdicts.** A `VERDICT:` line whose remainder after the
  first token contains `|`-separated alternatives (e.g. `VERDICT: PASS | FAIL | BLOCKED |
  ESCALATE`) is a template echo and is excluded from verdict matching. Rationale: this is the
  exact line the handoff rule teaches agents, and `(\S+)` currently captures `PASS` from it.
- D-02 — **Ambiguity is a violation, never a guess.** After excluding template echoes: exactly one
  remaining `VERDICT:` line (or several carrying the *same* token) yields that token; several
  carrying *different* tokens yields a new violation ("multiple differing VERDICT lines —
  ambiguous; remove the echo/quote"). Fail-closed via the existing violation path (CLI exit 1,
  hook exit 2), consistent with the file's own "never guess a verdict" rule (validate-digest.py:23).
- D-03 — **Digest parsing anchors to the accepted verdict.** `parse_digest` currently takes the
  FIRST `DIGEST:` block (validate-digest.py:283), so an echoed template shadows the digest too —
  same defect class, same repro. When a verdict line is selected, search for `DIGEST:` from that
  line forward; fall back to whole-text search when no verdict line exists, preserving current
  behaviour for all existing cases.
- D-04 — **Hook semantics untouched.** The three pass-throughs and fail-open-loudly on internal
  failure (DEC-122) are not modified. The new rejections are *their* contract violations riding
  the existing exit-2 path. No decision here weakens DEC-122/DEC-124.
- D-05 — **Echo classification runs on the comment-stripped, whitespace-stripped remainder.** The
  lead template line (`harness-team` "Reporting up") carries a trailing
  `# worst member verdict: BLOCKED > ESCALATE > FAIL > PASS` comment that defeats a raw
  `fullmatch`; apply the existing `strip_comment()` and `.strip()` to the `VERDICT:` remainder
  before the echo-shape match, so both the harness-handoff and harness-team template forms are
  excluded.
- D-06 — **Known limitation (accepted, no task):** an echoed template `artifact:` line can still be
  first-matched, but nothing routes mechanically on the artifact value — its consumer is an LLM
  reading the whole return, and the `<path ...>` placeholder is distinguishable — so this is
  deliberately out of scope for FEAT-02.

## Approval

status: pending
approved_by:
approved_on:

## Features

- FEAT-02: fix the VERDICT-shadowing defect in `.claude/skills/harness/bin/validate-digest.py`.

## Tasks

### T-01 — Repro tests, proven red pre-fix
- change_type: bugfix
- traces: REQ-01, REQ-02, D-05, SC-1
- files: `.claude/skills/harness/bin/test-validate-digest.py` (edit; save a pre-fix copy of
  `validate-digest.py` to the scratchpad to prove redness — do not commit the copy)
- intent: Add cases via the existing `case(...)` / `hook_case(...)` helpers:
  1. **Echo-shadow, differing verdicts** (CLI + hook): the harness-handoff template block —
     including its `VERDICT: PASS | FAIL | BLOCKED | ESCALATE` line and placeholder DIGEST —
     followed by a complete, valid pm return with `VERDICT: FAIL`. Expect: accepted with the
     REAL verdict routed (no violation), i.e. `ok=True` — and specifically NOT accepted-as-PASS;
     assert via a lead-roll-up variant or the ambiguity message absence per implementation. Hook
     variant: exit 0.
  1b. **Echo-shadow, comment-bearing lead template** (CLI + hook): same as case 1 but the echoed
     line is the harness-team form verbatim —
     `VERDICT: PASS | FAIL | BLOCKED | ESCALATE     # worst member verdict: BLOCKED > ESCALATE > FAIL > PASS`
     — followed by a real `VERDICT: FAIL` return. Expect: real verdict routed, `ok=True`, NOT
     accepted-as-PASS. Pre-fix this must be red (D-05: raw fullmatch fails on the comment).
  2. **Echo-shadow, digest** : echoed template DIGEST with placeholder `headline: <one line>`
     before a real, valid DIGEST. Expect the real digest's fields to be the ones validated
     (pre-fix this fails because the placeholder block is parsed instead).
  3. **Genuine ambiguity**: two non-template `VERDICT:` lines, `PASS` then `FAIL`, mentions
     "ambiguous"/"multiple" in the violation text. Expect `ok=False` (hook: exit 2).
  4. **Agreeing duplicates**: two non-template `VERDICT: PASS` lines plus a valid digest —
     `ok=True`.
- verify: `python3 .claude/skills/harness/bin/test-validate-digest.py` — new cases FAIL against
  the saved pre-fix binary (repro red), existing 36 still pass against it.

### T-02 — Fix validate-digest.py per D-01..D-03
- change_type: bugfix
- traces: REQ-01, REQ-02, REQ-03, REQ-04, D-01, D-02, D-03, D-04, D-05, SC-1, SC-2, SC-3
- files: `.claude/skills/harness/bin/validate-digest.py` (edit)
- intent: Replace the single `re.search` at line 380 with a verdict-selection step: collect all
  `^\s*VERDICT:\s*(.*)$` lines; for each, apply the existing `strip_comment()` and `.strip()` to
  the captured remainder (D-05), then drop lines whose stripped value matches a template-echo
  shape (first token followed by `|` alternatives, e.g.
  `re.fullmatch(r"\S+(\s*\|\s*\S+)+", value)`); apply D-02
  (none → existing "no VERDICT" error; one token or agreeing tokens → that token, still checked
  against `VERDICTS`; differing tokens → new "ambiguous verdict" error). Thread the selected
  line's index into `parse_digest` (new optional `start=` parameter or pre-sliced text) so the
  `DIGEST:` search begins at the accepted verdict line, falling back to the whole text if no
  `DIGEST:` follows it (D-03). Do not touch `hook_mode()` control flow (D-04). stdlib only.
- verify: `python3 .claude/skills/harness/bin/test-validate-digest.py` — full suite passes
  (36 existing + T-01 cases), exit 0.
