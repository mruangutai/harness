# UI Review — BUG-442-docs-grant-witness-test — validate (review_sha 9b3fde7e)

## Verdict: PASS (advisory only; no must_fix)

## 1. Measured file-set census

`git -C <worktree> diff --stat 6d969ed3 9b3fde7e`: **15 files, +1421/-0**. Exactly one is code:
`tests/integration/test-harness-yaml.py` (+182/0). The other 14 are this feature's own records under
`.harness/harness/features/BUG-442-docs-grant-witness-test/` (BRIEF.md, STATE.md, feature.json,
plan.yaml, and files under `notes/`/`observations/`). Matches the dispatch's stated census exactly —
no drift, no extra files, no files outside those two buckets.

## 2. Design-contract / UAT / accessibility check

- `DESIGN.md` at `9b3fde7e:.harness/harness/features/BUG-442-docs-grant-witness-test/DESIGN.md`:
  **confirmed absent** — `git cat-file -e` returns "does not exist in 9b3fde7e". This feature carries
  no Mode-A contract to audit.
- `BRIEF.md` (read via `git show 9b3fde7e:…/BRIEF.md`, full text inspected): all seven success
  criteria (SC-01…SC-07) are `verify: automated` / `evidence: integration` except SC-07
  (`verify: inspection`). **Zero criteria are `verify: uat`.** No user-facing surface, workflow, or
  screen is named anywhere in Problem/Goal/Requirements/Success Criteria/Constraints. No
  accessibility requirement of any kind appears. The Constraints section explicitly scopes the whole
  flow to a read-only manifest assertion in one test file.

## 3. UI-file census in the diff

Measured with `git diff --name-only 6d969ed3 9b3fde7e | grep -Ei '\.(tsx|jsx|css|scss|html|vue|svelte|less)$|/web/|template'`:
**0 matches.** No component, stylesheet, template, or `web/`-rooted file appears anywhere in the 15
changed files. This is a stated measurement, not an inferred absence (repo-tier P-01/expertise: this
repo is files-only with no rendered UI surface by default; confirmed again here rather than assumed).

## 4. The one human-facing surface: failure-message diagnostics

Per the dispatch, judged the operator-facing text a developer reads when the witness reddens
(`git show 9b3fde7e:tests/integration/test-harness-yaml.py`, lines 267–380).

**`test_docs_domain_grant_is_exhaustive_over_every_persona` (:267-288):**
- Census-mismatch path (:277-282): the message splits into `missing (deleted/renamed): {...}` and
  `unexpected (added): {...}` on separate labeled lines — a reader gets the exact persona names in
  each bucket, and the deletion/addition distinction the plan requires is explicit in the label text,
  not left to be inferred from set arithmetic. Satisfies the dispatch's diagnostic question directly.
- Per-persona mismatch path (:284-288): `f"{name}: docs grant mismatch\n  got: {...}\n  expected:
  {...}"` — names the specific persona and shows both sides of the diff. A reader never has to guess
  which of 16 personas broke.

**`test_docs_domain_witness_reddens_on_addition_removal_and_census_drift` (:292-380):**
- Every per-mutant assertion in the M1/M2/M3 loop (:363, :367, :373) is prefixed `f"{label}: …"` where
  `label` is one of the literal strings `"M1 addition"`, `"M2 removal"`, `"M3 census drift"` (:359-363
  tuple). A reader failing here knows immediately which point on the mutant ladder broke, plus gets
  `child.stdout`/`child.stderr` verbatim.
  - :363 — wrong-exit-code case names the label, expected/actual returncode, and both streams.
  - :367 — missing-FAIL case names the label and dumps `child.stdout` so the reader can see what the
    witness actually printed instead.
  - :373 — missing-anti-false-red-control case names the label and explains *why* the control
    matters (rules out an import/parse failure masking the real signal), not just that it's absent.
- The baseline (unmutated) control failure (:351-354) says `"control (unmutated manifest, repointed
  root) must exit 0"` — no `{label}` prefix, but it doesn't need one: it's a single, uniquely-named
  check outside the M1/M2/M3 loop, and the message already names itself as "control" distinctly from
  any mutant.
- The recursion-guard assertion (:307-312, `BUG442_MUTANT_CHILD leaked into the parent environment`)
  explains the specific env-var mismatch, states the consequence (why the negative control can't be
  trusted), and would let an operator diagnose an unexpected recursion rather than a bare
  `AssertionError`.

No message in either function would leave an operator unable to tell what broke. All are
diagnosable: which persona, which direction (missing vs. unexpected), which mutant label, and full
subprocess output are all present where relevant.

## 5. SIMPLIFY's `:373` fold-in — verified accurate

Diffed `f9f2d392` (pre-SIMPLIFY) against `9b3fde7e` directly
(`git diff f9f2d392 9b3fde7e -- tests/integration/test-harness-yaml.py`): the only change is
`test-harness-yaml.py:892-904` → `see main() at the foot of this file` inside the anti-false-red
control's failure message; the assertion expression is byte-identical, confirming the dispatch's
description. Checked the replacement's accuracy against the file it describes: `main()` is defined at
line 1074 of a 1090-line file (`TESTS = [` at :1041, `def main():` at :1074) — genuinely the last ~16
lines, i.e. "the foot of this file" is a true statement, and unlike the numeric pin it replaced, it
cannot go stale as the file grows above it. Also confirmed `main()`'s actual print format
(`f"FAIL {t.__name__}: {e}"` / `f"ok   {t.__name__}"`, :1074-1084) matches the substring checks the
test performs (`'FAIL test_docs_domain_grant_is_exhaustive_over_every_persona' in child.stdout`,
`'ok   test_bare_date_scalar_stays_str' in child.stdout`) — the diagnostic assertions are checking
against the real output shape, not a guessed one.

## Not applicable

Accessibility and theme-parity sections are explicitly N/A: the entire surface is batch CLI stdout
text with no colour-only state encoding and no themed rendering to check.

## Findings

None. `must_fix: []`.
