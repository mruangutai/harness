# UI Review — BUG-1286-test-tree-enforcement — Mode B — c1

## Verdict
PASS. No rendered UI surface in this diff. Advisory-only findings on the one adjacent
operator-facing text surface named in the dispatch (stdout/stderr messages from
`suite_layout.py` and `tests/manual/suite-census.py`). Nothing gates.

## 1. DESIGN.md — measured absence
`find .harness/harness/features/BUG-1286-test-tree-enforcement -iname 'DESIGN*'` → no hits.
Repo-wide `find . -iname DESIGN.md` returns only the template
(`.claude/skills/harness/templates/DESIGN.md`) and four unrelated features (FEAT-19, FEAT-40,
FEAT-11, FEAT-10). None reference BUG-1286. Correct state for a filesystem-invariant/CLI feature,
not a gap — Mode A doesn't apply here (repository-tier Expertise P-01 for this repo: expect zero
rendered UI by default).

## 2. File enumeration — full 70-file diff (merge-base `1977ebd6` → `9adbce6b`)
`git diff --stat` over the pinned range: 70 files, +8928/-113. Extension census: zero
html/css/scss/tsx/jsx/vue/svelte/less files. Breakdown:
- 1 guard module: `.claude/skills/harness/bin/suite_layout.py` (+116) — text-only, stdout/stderr strings.
- 1 manual instrument: `tests/manual/suite-census.py` (+108, adds `tree-audit`) — same, text-only.
- 1 integration test: `tests/integration/test-run-unit-tests-layout.py` (+89) — asserts on those strings, doesn't render.
- 1 unit test: `tests/unit/test-suite-layout.py` (+391) — same.
- 2 decision docs: `DECISIONS.md`/`DECISIONS-INDEX.md` — internal governance record, not a runtime operator surface a user reads during normal operation; out of my remit (documentation, not product/CLI UI).
- ~63 feature-process artifacts under `.harness/harness/features/BUG-1286-test-tree-enforcement/` (BRIEF, STATE, plan.yaml, receipts, research/review notes) — process paperwork, not a UI contract.
- 1 deletion: `.harness/notes/audit-decisions.py` (-110) — unrelated tool removal, no message-surface overlap with this feature.

No candidate for graphical UI (colour, layout, contrast, theme, focus) exists anywhere in the diff.
The only candidate is the operator-facing TEXT emitted by the two Python tools, which the dispatch
named explicitly.

## 3. Text-surface audit (the one in-remit item)
Diffed the six new message forms against merge-base (pre-existing forms — `"{unit} contains no
test-*.py"`, `"{name} appears in both..."`, `"test file is not selected by the runner: {path}"`,
`"test-shaped file remains under bin: {path}"` — are untouched by this diff and out of scope per
P-11/dispatch item 2).

New in this diff, verified by direct execution against the live worktree
(`suite_layout.violations('.')` → `[]`; `suite-census.py tree-audit --ref 9adbce6b…` →
`TOTAL 85 OUTSIDE 9 VIOLATIONS 0`, matching the orchestrator's stated measurement) and by reading
`run-unit-tests.sh:33-40`, which prefixes every `violations()` line with `MISCONFIGURED: ` on stderr
before any test sentinel runs:

| Message | Names path? | Names rule? | Names remedy? |
|---|---|---|---|
| `cannot enumerate tracked files under {root}: {error}` | yes (`{root}`) | yes, via wrapped git error (not-toplevel / timeout / git-missing) | implicit in the wrapped reason |
| `tracked test-shaped file outside tests/: {rel}` | yes | yes ("outside tests/") | **no** |
| `documented exception is not an exact path: {rel}` | yes | yes | implicit (fix the registry entry) |
| `documented exception is listed twice: {rel}` | yes | yes | implicit |
| `documented exception is unnecessary: {rel}` | yes | yes | implicit |
| `documented exception is no longer tracked: {rel}` | yes | yes | implicit |

Phrasing is internally consistent: all six are `<subject-phrase>: {value}`, and the four
`documented exception is …` forms share identical lead vocabulary. No inconsistency finding.

**Advisory (non-gating): `tracked test-shaped file outside tests/: {rel}` is the primary,
most-tripped message** — the one an engineer sees the first time they commit a stray `test_*.py`
outside `tests/`, rendered on stderr as `MISCONFIGURED: tracked test-shaped file outside tests/:
.harness/tools/test_rogue.py` (confirmed via `tests/integration/test-run-unit-tests-layout.py`
case 2 and via `run-unit-tests.sh:33-40`). It states the fact and the path but not the remedy —
contrast with sibling refusal messages in the SAME `.claude/skills/harness/bin/` directory
(`bash-write-guard.sh:233-234` "Work in the worktree cut for this feature and address it with
git's -C option rather than moving to it.", `check-domain.sh:207-209` "Restore
.agents/skills/harness/bin/harness_boundary.py, then retry.", `check-plan-routes.py:639-644`
"Point the override at a harness checkout, or pass PLAN.md paths explicitly."), which pair the
fact with an explicit next action. This message does not.

I am **not** filing this as a defect: the exact string is a signed contract, not this code's
choice — `plan.yaml:559` pins it verbatim, and `plan.yaml:591-599`/BRIEF.md SC-06 grade it by
literal list-equality, so a wording change is a plan amendment, not a code fix, and the spec is
explicitly not on trial here (dispatch constraint). Recording it as an open, non-blocking
observation for a future decision, not a `must_fix`.

**Advisory (non-gating): `tree-audit`'s summary line has no legend.** `TOTAL 85 OUTSIDE 9
VIOLATIONS 0` (verified live) is preceded by one `{path}\t{disposition}` row per matched file, so
the three counts ARE derivable from the full output (`OUTSIDE` = everything not `in-tests-tree`;
`VIOLATIONS` = the strict subset flagged `violation`, excluding `documented-exception` and
`out-of-vocabulary`). But the final line alone — e.g. if only the summary is captured or grepped —
does not say that `OUTSIDE` includes legitimate exceptions, so `OUTSIDE 9 VIOLATIONS 0` could be
misread as "9 anomalies" rather than "9 accounted-for, 0 unaccounted-for." This is a manual/review
instrument (`tests/manual/`), not a CI gate consumed line-by-line, so severity is low.

## Accessibility / theme parity / contrast
Not applicable and confirmed rather than assumed: grepped both files for ANSI escapes / colour —
zero hits. Both tools are plain stdout/stderr text with no colour-only state encoding, so
contrast, dark/light parity, and colour-alone-conveys-state do not apply to this surface.

## Not verifiable from this lens
Rendered layout/pixel concerns are moot — there is no rendered surface in this diff to fail to
verify.

## Scope declined
DECISIONS.md/DECISIONS-INDEX.md prose (the DEC-213 amendment) — internal governance record read by
maintainers doing archaeology, not a product or CLI operator surface; leaving wording/consistency
judgment on that document to code-reviewer, whose lens is decision-graph correctness.
