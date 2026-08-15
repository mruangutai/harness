# PLAN — FEAT-02 Fix VERDICT shadowing in validate-digest.py

## Decisions

- D-01: **Tail-anchor the whole validation, not just the VERDICT regex.** In
  `validate()`, find the LAST `^\s*VERDICT:` line and slice the text from that line to
  the end; run every existing check (verdict token at `:380`, `DIGEST:` presence at
  `:386`, `artifact:` at `:388`, `parse_digest`, lead roll-up) against the slice. If no
  `VERDICT:` line exists anywhere, validate the whole text unchanged (preserves the
  existing "no VERDICT" error path and digest-field errors).
  — rationale: the defect is not one regex — `parse_digest` takes the FIRST `DIGEST:`
  (`:283`) and the artifact check is first-match too, so an echo shadows all three.
  The real return is by contract the final thing an agent writes; one slice fixes all
  three anchors with no new parsing code, and hook mode inherits it for free.
  tradeoffs: an echo-only message whose placeholders happen to be schema-valid still
  passes (content, not format — the validator cannot decide it); a real return written
  ABOVE trailing prose containing a line-start `VERDICT:` would anchor wrong, but the
  contract mandates the return last and no such case exists in practice.
- D-02: **Test-first with pre-fix proof**, task-22 precedent: every new regression
  case is run against a saved copy of the pre-fix binary via the suite's existing
  `VALIDATE_DIGEST_BIN` override (`test-validate-digest.py:18`) and shown to fail
  there — rationale: proves the cases capture the defect rather than passing
  vacuously; tradeoffs: one extra manual step during T-01 verification.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-07-27

<!-- RE-PLANNING RESETS THIS. pm resets to pending on any task-set change. -->

## Features

- FEAT-02: Fix VERDICT shadowing in validate-digest.py
  traces: REQ-01, REQ-02
  tasks: T-01, T-02

## Tasks

- T-01: Add echo-shadowing regression cases (red first)
  files: .claude/skills/harness/bin/test-validate-digest.py
  intent: Append CLI cases via the existing `case(...)` helper and one hook case via
    `hook_case(...)`, all built as "echoed harness-handoff template block (containing
    `VERDICT: PASS | FAIL | BLOCKED | ESCALATE`, a placeholder `DIGEST:` block, and
    `artifact: <path>`) followed by a real return". Cases: (1) qa echo + real
    `VERDICT: FAIL` block that is fully valid → expect PASS-validation (exit 0) —
    pre-fix this passes trivially against the echo, so pair it with (2) qa echo + real
    block MISSING `matrix_ok` → expect REJECT mentioning `matrix_ok` (pre-fix: falsely
    exits 0 because the echoed block is validated); (3) lead echo (`VERDICT: PASS`
    template) + real lead block whose `members` carry a FAIL and whose top verdict is
    PASS → expect REJECT mentioning "worst" (pre-fix: the echoed block shadows and the
    roll-up never sees the real members); (4) hook-mode variant of (2) for
    `harness-qa` → expect exit 2 with stderr mentioning `matrix_ok`. Do not modify
    validate-digest.py in this task. Save the pre-fix binary first:
    `cp .claude/skills/harness/bin/validate-digest.py /tmp/validate-digest-prefix.py`.
  change_type: bugfix
  verify: .claude/skills/harness/bin/test-validate-digest.py; test $? -ne 0
    (suite must be RED — the new cases fail against the unmodified validator; each
    new case name appears in the FAIL output, none of the 36 existing cases fail)
  traces: REQ-01, SC-01, D-02
  feature: FEAT-02
  status: pending

- T-02: Tail-anchor validate() to the last VERDICT line
  files: .claude/skills/harness/bin/validate-digest.py
  intent: In `validate()`, before the checks at ~line 380, compute
    `anchors = list(re.finditer(r"^\s*VERDICT:", text, re.M))`; if non-empty, set
    `text = text[anchors[-1].start():]` and validate the slice with the existing
    logic unchanged (verdict token, DIGEST presence, artifact, parse_digest, lead
    roll-up all read the slice). If empty, keep whole-text behavior — the "no
    VERDICT" error and all field errors must be byte-identical to today. Add a short
    docstring/comment recording WHY (echo-shadowing, BUILD task 22 follow-up), in the
    file's established comment style. No change to hook_mode() pass-through
    semantics. Stdlib only.
  change_type: bugfix
  verify: .claude/skills/harness/bin/test-validate-digest.py
    (exit 0 — all pre-existing 36 cases plus the T-01 cases green; additionally
    VALIDATE_DIGEST_BIN=/tmp/validate-digest-prefix.py .claude/skills/harness/bin/test-validate-digest.py
    must exit non-zero with exactly the T-01 case names failing, proving the cases
    capture the defect)
  traces: REQ-01, REQ-02, SC-01, SC-02, D-01, D-02
  feature: FEAT-02
  status: pending
