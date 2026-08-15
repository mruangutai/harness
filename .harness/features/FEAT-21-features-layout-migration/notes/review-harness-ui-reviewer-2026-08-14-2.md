# Review — harness-ui-reviewer — FEAT-21-features-layout-migration (Mode A, s6 re-check)

BLUF: PASS. The original must_fix (Finding 1, 2026-08-14-1) is closed — not a repeat hold. Two
new, non-blocking items surfaced while sweeping the revision for the same defect class; neither
risks a wrong message shipping to an operator, so neither gates.

## 1. Original finding — closed

`plan.yaml:405-425` (T-04's verify) now discriminates correctly:

- `stale = [l for l in lines if 'print(' in l and '.harness/features/' in l]` fails the build if
  either message site still carries the pre-move literal.
- `shown = [l for l in lines if 'print(' in l and '.harness/*/features/' in l]` requires exactly 2.

Confirmed against the real file at HEAD (`check-plan-routes.py:632,651`): both message sites carry
`print(` and the target literal on the same physical line, so the checks fire correctly. Confirmed
the substring non-overlap: `.harness/*/features/` does not contain the substring `.harness/features/`
(the `*/` breaks it), so a correctly-migrated line does not also trip the stale check. Confirmed via
direct grep that the four narrative comments the intent exempts (lines 15, 225, 430, 462) carry no
`print(` on their line, so they cannot false-red the verify — matches pm's report exactly, including
that the send-back's stale 475/504 line numbers are now superseded by content-anchored quotes in the
intent (`plan.yaml:450-457`).

`SC-14` (`BRIEF.md:143-156`) now covers the messages with named backing cases and a split evidence
tag (`integration` for the two `check-plan-routes.py` messages, `unit` for
`validate-feature-json.py`'s scan line) — matches pm's report. The detector's own row for this file
(`plan.yaml:431-437`) stays narrow (join-shape only) by design; that's fine now because T-04's verify
and SC-14 are independent, redundant enforcement of the message text, which is what was missing
before.

**Consequence check**: an operator debugging a zero-plans incident can no longer be misdirected by a
stale scan message — T-04's verify makes that unshippable. Original finding closed on primary
evidence, not on the plan's narration of itself.

## 2. Same defect class swept into the revision's new surfaces — clean

- **T-10 GROUP 2** (`validate-feature-json.py`, `plan.yaml:938-966`): the docstring, the glob and
  the scanning line are ALL swept by `stale = [l for l in vf.splitlines() if '.harness/features/' in
  l or ...]` (`plan.yaml:869-872`) — a whole-file literal check, not a narrow join-pattern, so the
  docstring migration the intent requires is enforced, not merely requested. Confirmed at HEAD
  (`validate-feature-json.py:12,41,51`) only three sites exist, all normative (no exempt narrative
  comments in this file), and all three fall inside the swept set — no residual gap.
- **`.github/workflows/tests.yml`'s operator error string** (line 171, "Check CLAUDE_PROJECT_DIR and
  `.harness/features/`.") IS migrated — it's one of the three pairs T-10's verify checks explicitly
  (`plan.yaml:882-889`, third tuple). This is the one site in the file that a CI operator actually
  reads on a failed run; it does not survive.

## 3. New finding — non-blocking. SC-14's "test-backed" claim is unenforced for two of its three conjuncts

SC-14 states the unreadable-path message and `validate-feature-json.py`'s scan line are each
"test-backed" by an *existing* case gaining a *new* stderr-path-text assertion:

- `plan.yaml:654-658` (T-06 intent): `case_22a_unreadable_feature_dir_exits_2` is to gain "one
  conjunct requiring the migrated path shape `.harness/*/features/` to appear in stderr."
- `plan.yaml:962-966` (T-10 intent): the added `migrated_depth` case for
  `test-validate-feature-json.py` is to gain "ONE MORE CONJUNCT" asserting the same shape in stderr.

Neither conjunct is enforced by any verify in the plan:

- T-06's verify (`plan.yaml:594-613`) checks only whole-file literal absence and generic `/features/`
  presence — nothing that names `case_22a` or confirms it gained a new assertion. Since `case_22a`
  already exists and already passes today without that conjunct (asserting only exit code and
  feature name), a build that skips adding it still shows `PASS test-check-plan-routes.py` at T-09
  (`plan.yaml:1026`) — the per-file suite result, not a per-case one.
- T-10's verify greps the test source for the case *label* (`'migrated_depth' in tv`,
  `plan.yaml:881`) — stronger than T-06's, but still only forces the case to exist, not that its
  added stderr conjunct is present inside it.

**Why this doesn't gate**: the operator-facing outcome is already double-locked independent of these
tests — T-04's exact-count verify and T-10's stale-sweep-plus-`any()` check the message *source text*
directly at build time, so a wrong or reverted message cannot ship regardless of whether the test
conjuncts land. What's at risk is only SC-14's own claim of being "test-backed" for two of its three
messages, which a reviewer trusting the plan's narrative (rather than reading the test file) would
believe is true when it may not be. That is a completeness gap in the contract's self-description,
not a shipped-defect risk — `severity: med`, non-blocking.

**One trap for whoever remedies this**: a whole-file grep for `.harness/*/features/` in
`test-check-plan-routes.py` will NOT discriminate, because `case_19a5`'s already-required rewritten
expected string alone satisfies it — the check needs to be region-anchored to `case_22a` or
count-based (e.g., the migrated literal present on 2+ distinct lines in that file), the same
exactly-2 shape T-04's own verify already uses successfully.

## 4. Advisory — tests.yml's "M IS ASSERTED" comment block

`plan.yaml:983-988` classifies three occurrences (`tests.yml:119` once, `:125` twice) as "knowing
survivors," a dated measurement record. Confirmed correct on the operator-facing test specifically
asked: all three are `#`-prefixed YAML comments, stripped before any job log — none reaches an
operator, so "knowing survivor" is the right call.

Worth naming for whoever owns this text: the block asserts present-tense, reproducible claims
("not a live hole *today*... `git ls-files ... returns 8`, `git check-ignore ... exits 1`") with no
date or commit anchor. Post-move, re-running the quoted commands against the literal paths they name
returns different numbers (the files are no longer at that path), so a future reader who takes the
comment's "today" literally and re-runs it will see a contradiction the comment doesn't explain. This
differs from T-04's four exempted comments, which are illustrative past-tense examples, not
falsifiable present-tense measurements. Advisory remedy: anchor the block with "measured at
\<sha\>, pre-move." Non-blocking — comment-only, never printed, no operator ever sees it.

One more clause for completeness: `tests.yml:126`'s `` `.harness/features` `` (no trailing slash) is
invisible to every literal sweep in this plan, T-04's and T-10's included, because they all match on
`.harness/features/` (with slash). It is inside the same exempted comment block, so nothing turns on
it here — noted only so a future slash-sensitive sweep isn't surprised by it.

## Mode A checklist

- Implementable: n/a — code, not a design contract.
- Complete for what's being built: closed for Finding 1; one new completeness gap noted (§3),
  non-blocking.
- Internally consistent: yes.
- Both themes: n/a.
- Checkable: SC-14 is checkable as an operator-facing-text contract (T-04 + T-10 verify it directly);
  its own "test-backed" self-description is not fully checkable for two of three messages (§3).
