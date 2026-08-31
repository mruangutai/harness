# QA Gate re-run — FEAT-38-decisions-current-knowledge — c0 (independent of qa-2026-08-29-10-validator)

**VERDICT: PASS.** Independent re-run of the full matrix at `3928c70` is green (exit 0, 0 FAIL,
1117 PASS, 0 KIND-DRIFT). Both new checkers and their test files, and the stripped generator's
test file, PASS. All three SC-07/SC-08/SC-09 mutation criteria were **measured live in this
session** (not merely asserted), against copies outside the worktree, and all discriminate
correctly. No `high` finding. One `low` documentation gap noted below.

## 1. Full-suite re-run — CONFIRMED, matches the prior qa note exactly

`.claude/skills/harness/bin/run-unit-tests.sh --kind all` from worktree root:
`EXIT:0`, `grep -c ^PASS` = 1117, `grep -c ^FAIL` = 0, `grep ^KIND-DRIFT:` = 0 lines. Full output
captured to a file (never piped through `tail`) and searched with `grep`. Lines
`PASS test-gen-decisions-index.py`, `PASS test-check-decision-anchors.py`,
`PASS test-check-decision-claims.py` all present.

## 2. Required kinds per change_type — `matrix_ok: true`

- `docs` (T-01,02,03,04,05,07,08,09,11,12,14,15,16,21): `always: []` — no required kind (LEAVE-LIST
  item 4, not re-litigated).
- `config` (T-13,18,19): `always: []` — same floor.
- `logic` (T-06,10,17,20): `always: [unit]`. All four logic tasks' files match `unit`'s detect glob
  (`test-*.py` under bin) AND are present as `PASS` lines in the run above — satisfied, not just
  glob-matched (P-14).
- No `api`/`cross_module`/`frontend`/`feature`/`bugfix`/`ai_behavior` change_type appears in this
  plan, so those kinds are not obligated.

## 3. Checker registration — CONFIRMED both places

`test-check-decision-anchors.py` and `test-check-decision-claims.py` are literal members of BOTH
`run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` array AND `harness.json`'s `integration.detect`
pipe-list (grepped/parsed directly, not inferred). The runner's own set-comparison cross-check
(`--check-kinds`) is part of the green run above — a mismatch would exit 2, not report FAIL.

## 4. Discovery counts (non-zero, real tree at the pin)

- Anchor checker against `.harness/harness/docs/DECISIONS.md` (worktree content verified byte-identical
  to `3928c70` via `git diff 3928c70 -- <path>` = empty): **20 anchors examined, 0 failed, exit 0**.
- Claim checker against the same file: **11 claims examined, 0 failed, exit 0**.
- Anchor checker against `git show 7ebfc9e:.../DECISIONS.md` (base): **32 anchors examined, 3
  failed, exit 1** — the exact three `feature.yaml` anchors named in SC-08 (`FEAT-03-subissue-mirror
  /feature.yaml:73`, `feature.yaml:63-64`, `FEAT-03-subissue-mirror/feature.yaml:97`).
  Both counts are non-zero: this rules out an empty-set false-positive exit 0/1.

## 5. Mutation observations — all three MEASURED this session, not asserted

All performed on throwaway copies under `/tmp` (now deleted) or in-memory monkeypatched
`REPO_ROOT`; never on any tracked path. `git status --porcelain` was clean before and after every
probe; the two untracked files present at the end (`notes/review-harness-ui-reviewer-c0.md`,
`.harness/notes/grilling-decisions-current-knowledge-2026-08-24.md`) are peer/pre-existing
artifacts, not mine.

- **SC-07** (T-10's amendment-construct guard, `test_no_amendment_construct_survives_in_the_authority`
  in `test-gen-decisions-index.py`): loaded the real module via `importlib`, monkeypatched
  `REPO_ROOT` to a scratch dir holding a copy of the pin's `DECISIONS.md` with
  `\n### DEC-99 amendment 1\n` appended, and **called the actual test function directly** (not a
  reimplementation of its regex). Result: `FAIL - ... heading found at ...:[6301]`, `False`.
  Re-ran against the unmutated pin copy: `ok - ...`, `True`. The case's `ok -`/`FAIL -` line is
  individually named, matching the runner's per-line PASS/FAIL accounting, so silently deleting the
  case would drop the PASS-line total below 1117 — detectable, not undetectable-by-suite-green as a
  literal reading of "cannot be deleted with the suite green" might imply; the count is the guard.
- **SC-08** (anchor checker): planted `` `nonexistent/fabricated_path_xyz.py:9999` `` onto a copy of
  the pin's `DECISIONS.md` and ran the checker directly: `1 failed`, exit 1, message names the
  fabricated path — reddens correctly. Combined with §4's exit-0-at-pin and exit-1-with-named-3-at-base,
  all three of SC-08's separate observations (exit 0 at pin / exit non-zero naming exactly the 3 at
  base / reddens on a fabricated anchor) are independently measured, not inferred from one exit code.
- **SC-09** (claims checker): copied the pin's `DECISIONS.md`, replaced the exact verbatim marker
  `grep -c -m 81 -e "" CLAUDE.md :: 12` with `:: 81`, ran the checker directly: exit 1, message is
  `DEC-181 — CLAUDE.md gets a line budget of 80: ... expected substring '81' not found in stdout:
  '12'` — names the marker by its owning heading exactly as SC-09 requires.

## 5b. The two new checkers' OWN test suites also guard the live authority

Beyond T-10's guard case, both `test-check-decision-anchors.py` (7 cases, incl.
`test_live_authority_anchors_all_resolve`) and `test-check-decision-claims.py` (8 cases, incl.
`test_live_authority_claims_all_hold`, plus `test_checker_source_never_uses_shell_true` asserting
the security boundary directly against source) run against the real `DECISIONS.md`, not only
synthetic fixtures — so a future edit that reintroduces a rotted anchor or a false claim reddens
these suites too, independent of the generator-side T-10 guard. Not mutation-probed further in this
session (T-10's guard already gave a direct measurement of live-authority sensitivity for the
amendment-construct class; the anchor/claim live-guards are structurally identical to the
already-measured SC-08/SC-09 probes above, just invoked from a second call site).

## Findings

- **[low, docs]** §5's literal SC-07 phrasing — "named so it cannot be deleted with the suite still
  green" — is satisfied only via the PASS-count-must-match-1117 mechanism (no per-test allowlist or
  count assertion exists that would fail loudly and *name* the missing case if deleted; a bare drop
  from 1117 to 1116 is the only signal, and nothing in the runner asserts the total against a
  baseline). Failure scenario: a future refactor deletes the test case; the suite still reports
  `EXIT:0`/`0 FAIL`, and only a PASS-count regression (which nothing currently gates) would catch
  it. Non-blocking — the LEAVE LIST already covers the broader "docs/config carry zero required
  kinds" floor question, and this is a variant of the same class, not a new gap.

No `high` finding. `matrix_ok: true`. `suite: pass`.

## SC evidence

- SC-07 → `.claude/skills/harness/bin/test-gen-decisions-index.py:829-869`
  (`test_no_amendment_construct_survives_in_the_authority`), mutation-measured §5.
- SC-08 → `.claude/skills/harness/bin/check-decision-anchors.py` run directly against
  `7ebfc9e`/pin/mutant copies, §4–§5.
- SC-09 → `.claude/skills/harness/bin/check-decision-claims.py` run directly against pin/mutant
  copies, §5.
- Registration (REQ-07/08 config half) → `run-unit-tests.sh:31` + `harness.json` `integration.detect`,
  §3.
