# Code review — FEAT-23 re-fix — `afc8cfd..78e87dc` — run 2026-08-17-15-refix-validator

**HEAD confirmed `78e87dc90cf5df07bfc4a440081edc412e712845`, matches the task's pin.** The range holds
**three** commits, not two: `1d49644` (the fix), `fd465e7` (records-only — pin/STATE/feature.json/
briefing reconciliation, 5 files, no `.py`/`.md`-skill touched), `78e87dc` (the simplify pass). All
read via `git show <sha>:<path>`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "78e87dc is proven behaviour-neutral by AST comparison and the four-site skip is correct — but board-station.py:69 still lets a >4300-ASCII-digit issue-number argument reach int() inside the gate itself and raise ValueError, exit 1 with a traceback, against T-05 intent item 1's and the docstring's absolute '2 is the ONLY non-zero exit', reproduced empirically and safely from outside the harness root"
  severity_max: high
  findings: 3
  must_fix:
    - "board-station.py:69 — `if not (issue_arg.isascii() and issue_arg.isdigit()) or int(issue_arg) <= 0:` calls `int(issue_arg)` INSIDE the gate condition itself. A >4300 ASCII-digit string (e.g. '9'*4301) passes `isascii()` and `isdigit()`, so Python evaluates `int(issue_arg) <= 0` next, which raises `ValueError: Exceeds the limit (4300 digits) for integer string conversion` (CPython's built-in int-str conversion DoS guard, default since 3.11, this env's `sys.get_int_max_str_digits()` = 4300) — before either `return 2` executes. Uncaught: propagates through `main()` to `sys.exit(main(...))`, traceback, exit 1. Reproduced live from /tmp (outside any harness root, so the crash is proven to occur before the harness-root walk and nowhere near `gh_board.set_station` — no real board write risk). This is the SAME defect class (`isdigit()` True, `int()` disagrees) that 1d49644 was written to close and that 78e87dc's rewritten comment re-asserts as closed ('and 2 is this tool's only non-zero exit') — a third failure mode neither commit addresses. Pre-existing since the original T-05 build (e50b8b4) and NOT newly introduced by this range, but 1d49644 is inside the reviewed delta and both it and 78e87dc restate the absolute claim the code does not meet, so this is in scope as a Stage-1 mismatch against plan.yaml T-05 intent item 1, not a pre-existing defect outside review. Fix: bound the digit-string length before calling `int()` (or catch `ValueError` alongside the existing usage-error path), plus one test case with a >4300-digit argument. OR an explicit operator ruling narrowing item 1's absolute claim and correcting the docstring — same shape as Q1 in runs/2026-08-17-14-finalpass-validator/digest.md, which the operator has not yet ruled on for this new case."
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/board-station.py, ref: "T-05 intent item 1" }
  reviewed: "afc8cfd..78e87dc"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Does the length-based ValueError crash in board-station.py's argument gate (>4300 ASCII-digit issue-number argument raises inside the gate, exit 1 not 2) get a code fix, or does the operator narrow T-05 intent item 1's absolute claim and correct the docstring — same shape as the still-open Q1 from runs/2026-08-17-14-finalpass-validator/digest.md for the superscript case, now recurring a third way", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-code-reviewer-2026-08-17-15-refix-validator.md
```

## Probe A — is 78e87dc prose-and-test only? YES, proven mechanically.

**`ast.dump(ast.parse(...))` of `board-station.py` at `1d49644` vs `78e87dc` is byte-identical** (read
via `git show <sha>:path`, no working-tree file touched). This settles it without reading hunks: zero
production behaviour change in that file for this commit. The visible diff confirms why — one comment
block rewritten from incident-narration ("Found by the final validator pass (FEAT-23), reproduced with
'²'") to rule-statement ("ASCII-ONLY, and both halves earn their place...").

Full characterisation, `78e87dc` alone (`git show 78e87dc --stat`):
- `.claude/skills/harness-simplify/SKILL.md` — prose only, `-2/+1`: removed one sentence from ALTITUDE
  ("A special case layered on shared infrastructure is a sign the fix is not deep enough.") as a
  duplicate of the same idea at `:94` ("a special case bolted onto shared infrastructure"). **Left a
  dangling anaphor**: the surviving sentence now reads "A methodology that lives only in one session's
  prompts is **the same smell**" — but "smell" occurs exactly once in the whole file (`grep -ni smell`
  confirms), so "the same smell" has no antecedent left in the text. Doc-quality defect, not an
  assertion — advisory, low, non-blocking.
- `.claude/skills/harness/bin/board-station.py` — one comment block, AST-identical, confirmed above.
- `.claude/skills/harness/bin/test-board-station.py` — `+9/-4`: one comment rewritten (r4, prose only,
  no assertion change), one comment+test case ADDED (r5, `٢` Arabic-Indic 2 — the case where
  `int()` **accepts** the Unicode digit and silently parses to `2`, moving the wrong card). `check(` count
  goes 9→10 in the file, confirming purely additive; no existing check's boolean expression or label
  changed.

`git diff --stat 1d49644 78e87dc` (the combined range including `fd465e7`, which the task did not
mention) also touches `STATE.md`, `feature.json`, `notes/handoff-build.md`,
`notes/ship-review-2026-08-17-13.{md,html}` — all from `fd465e7` (records/pin reconciliation), none
from `78e87dc`.

**Suite state at HEAD, re-run independently:**
- `python3 test-board-station.py` → rc 0, all 10 checks PASS including the new r5 case.
- `bash run-unit-tests.sh --kind unit` → `ALL PASSED`, rc 0.
- `bash run-unit-tests.sh --kind integration` → `106/106 checks passed`, `ALL PASSED`, rc 0.
- T-02, T-03, T-05 `verify:` clauses copied from `plan.yaml` and run against HEAD: all three print their
  own `*-GREEN` line and exit 0. (T-05's inline failure-echo strings were abbreviated for my own
  terminal legibility — the `grep -qF`/`test` logic itself is verbatim; this does not affect the
  pass/fail outcome, flagging so "verbatim" isn't overclaimed.)

## Probe B — the shared strict-decimal skip: CORRECT.

Four sites exist, exactly four, all bare `.isdigit()` immediately followed by `int(...)` with no
length/ASCII guard:
- `.claude/skills/harness/bin/upgrade-config.py:151` — `return int(s) if s.isdigit() else None`
- `.claude/skills/harness/bin/gh-sync.py:327` — `return int(s) if s.isdigit() else None` (byte-identical
  to the line above — a real, pre-existing REUSE duplication, not introduced by this range)
- `.claude/skills/harness/bin/gh_board.py:82` — `elif isinstance(number, str) and number.strip().isdigit(): number = int(number.strip())`
- `.claude/skills/harness/bin/factory_gh.py:136` — `if len(tail) != 2 or not tail[1].strip().isdigit(): raise GhError(...)` / `return int(tail[1].strip())`

**None fall inside the reviewed delta.** `git diff --stat afc8cfd 78e87dc` touches only `SKILL.md`,
`board-station.py`, `test-board-station.py`, and five record files (`STATE.md`, `feature.json`,
`handoff-build.md`, `ship-review-*`, plus the two new validator notes from run 14) — none of the four
sites above appear anywhere in that list. The skip's stated reason ("outside this delta") holds for
all four, with no exception.

Weighed against the skill's own skip rule (permits skipping a fix that would "reach well outside the
reviewed scope") and the one-fix ceiling: the ceiling text (`SKILL.md` "Applying what comes back") reads
as a bound on **retries after a reddened suite** ("If an apply reddens the suites and one fix does not
restore green, revert..."), not a cap on the count of findings applied per pass. Two findings WERE
applied in `78e87dc` (the untested-second-Unicode-class fix, and the ALTITUDE dedup) — consistent with
that reading, not a violation of it. **Ruling: correct skip.**

Advisory, not separately run: the length-crash class in my must_fix above (`.isdigit()` True, `int()`
disagrees — this time via CPython's digit-count limit rather than a Unicode-form mismatch) is
structurally present at all four skipped sites too, on the same shape of code. This is inference from
board-station.py's confirmed behaviour, not an executed reproduction against each of the four — flagging
it strengthens the backlog item's priority without claiming a fourth-site repro I did not run.

## Probe C — does the shipped gate meet T-05 intent item 1? NO — see must_fix above.

The docstring's absolute claim ("EXIT CONTRACT: 2 is the ONLY non-zero exit") is **not TRUE at HEAD**,
merely more true than at `afc8cfd` (the Unicode-mismatch case is now closed by `1d49644`, the
silent-wrong-target case is now tested by `78e87dc`'s r5). The length-based case above is a live
counterexample, empirically reproduced. Blocks operator acceptance for the same reason
`runs/2026-08-17-14-finalpass-validator/digest.md` Q1 blocked it for the superscript case: "a contract
stated and undelivered is the falsified-record shape." Checked `digest.md` directly (not a grep) —
Q1–Q6 there name the superscript case only; this length-based case is new, not a re-file.

## Dismissed, recorded per P-15

- Whether the SKILL.md "apply may not delete or weaken an assertion" bound was violated: no — both
  `SKILL.md` edits touch prose, never a test assertion; the removed ALTITUDE sentence and the three
  rewritten code/test comments are all non-assertion text.
- Whether applying two findings (test-coverage fix + ALTITUDE dedup) in one pass breaches "the apply has
  a ceiling of one fix": no — that ceiling is a retry-after-red bound, not a per-pass finding cap; see
  Probe B.
- Whether the four skipped strict-decimal sites should have been folded in: no — none are in the
  reviewed delta, correctly backlogged.

## Bounds

Read-only throughout. No commits, no `gh` calls, no board write — confirmed by running the sole
reproduction from `/tmp`, outside every harness root, and by tracing that the crash precedes the
harness-root walk in `main()`. `runs/2026-08-17-15-refix-validator/state.yaml` matches this dispatch.
Did not read `notes/qa-2026-08-17-15-refix-validator.md` (already existed on disk at review time) —
Probe C was run and confirmed independently per the task's instruction, not deferred to qa's parallel
finding.
