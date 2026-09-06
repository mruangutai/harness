# QA Gate — BUG-440 digest verdict reconciliation (c2, mutation re-probe)

review_sha: `a1a67956a5844c67ce098e9580ee6692a92f9a30` (prior pin `2964cddbbfe465d1268cb12a248861d8a28e31a6`).
`check-state.sh` is confirmed byte-identical to the prior pin (`diff` clean) — the remedy is
genuinely test-only, as claimed.

## BLUF

**V-02 RESOLVED. V-03 RESOLVED.** Both previously-escaping mutants now redden, and — critically — each
reddens through the *specific* sub-check its remedy targeted, not through an unrelated coincidence.
V-04 (SC-01 order-blindness) is confirmed to still ESCAPE exactly as cycle-1 predicted; it was never in
the cycle-1 must_fix list and remains an open, low-severity gap. Two new mutants (m4, m5) were run: m4
escapes (expected, not remediated), m5 reddens (REQ-03(e) is bound). **VERDICT: PASS**, with one
new low-severity finding on SC-05's verbatim-output claim (below) and the standing V-04/SC-01 gap
carried forward as advisory.

## Mutation table (isolated copy via a private `isolated_bin(tmp)` copy, `CHECK_STATE_BIN=` env var,
never touching the live tree; anchors matched exactly once each before mutating)

| Mutant | Change | Expected | Actual | Verdict |
|---|---|---|---|---|
| m1 (control) | `_dm.group(1) != _rv` → `False` (comparison never fires) | reddens | **reddens** (`mixed_ok=F, blocking_ok=F, clean_ok=T`) | case is non-vacuous |
| m2 (V-02) | move INV-37 finding `bad.append` → `warn.append` (non-blocking) | reddens | **reddens, via `blocking_ok` specifically** (`mixed_ok=True` — unchanged from cycle-1's vacuity; `blocking_ok=False` — the new isolated mismatch-only tree, `entries=("M",)`, sees `mismatch_code=0` since a warn-only run never sets exit 1) | **RESOLVED** — the isolated tree is what catches it, exactly as claimed |
| m3 (V-03) | hang reconciliation off the outer `if _errs:`'s implicit else, so it also runs on invalid digests | reddens | **reddens, via `mixed_ok` specifically**: `inv37_count=2` (fires for both run M and run X) — fails `len(inv37) == 1` AND the `not any("runs/X" ...)` clause. Run X's digest text is now `"VERDICT: FAIL\n"` (was `"# digest\n"`), which fails `validate("lead", ...)` (missing `DIGEST:` block) yet still carries a matchable `VERDICT:` line, so the reconciliation block — if wrongly hung on invalid digests — now has something to fire on | **RESOLVED** |
| m4 (V-04, new) | transpose the two `!r` interpolations (digest verdict ↔ feature.json verdict swap) | predicted to ESCAPE | **ESCAPES**: `mixed_ok=True, blocking_ok=True, clean_ok=True` — the message still contains literal `'FAIL'` and `'PASS'`, merely with the labels swapped (confirmed: mismatch line reads `digest verdict 'PASS' ... differs from feature.json verdict 'FAIL'`, i.e. backwards) | **confirmed, not remediated** — SC-01's six-substring `all(...)` is still order-blind on the two verdict tokens |
| m5 (REQ-03(e), new) | membership guard `if _rid in _recorded:` → unconditional entry, verdict list resolved via `_recorded.get(_rid) or [None]` so an unclaimed run (O) compares its digest against `None` | predicted to redden if bound | **reddens, via `mixed_ok`**: `inv37_count=2` — a spurious INV-37 line now fires for run `O` (`digest verdict 'FAIL' ... differs from feature.json verdict 'None'`), tripping `len(inv37)==1` and the `not any("runs/O"...)` clause | REQ-03(e) is genuinely bound by the mixed fixture — an earlier crude attempt (`if True:` with no `.get()`, still indexing `_recorded[_rid]`) instead raised an uncaught `KeyError` and crashed the whole gate to exit 1 with empty stdout; the graceful `.get()`-chain variant above is the correct probe and it reddens cleanly |

## Per-SC resolution at the new pin

| SC | State | Evidence |
|---|---|---|
| SC-01 | satisfied, with a **standing gap (V-04, not remediated, not in must_fix)** | 3 of 6 substring tokens (`"M"`, `"feature.json"`, `"digest.md"`) are structurally guaranteed by the pre-filter/literal filenames, not by correct code; `"FAIL"`/`"PASS"` are order-blind — confirmed live by m4 |
| SC-02 | satisfied | `clean_ok`: isolated all-agree fixture, exit 0, no `INV-37` line |
| SC-03 | satisfied, all five legs now individually pinned | (a) host `omp` not a lead — `not any("runs/N"...)`; (b) run `I` is `active` — `not any("runs/I"...)`; (c) run `G` missing digest.md — existing INV-15 violation, counted exactly once (`sum(...)==1`); (d) run `X` invalid digest (has `VERDICT:` but fails `validate`) — existing INV-15 violation, counted exactly once, **and m3 proves no second INV-37 line stacks**; (e) run `O` unclaimed by feature.json — `not any("runs/O"...)`, **and m5 proves a regression comparing it would be caught** |
| SC-04 | satisfied | before/after sha256 dict compare over `feature.json` + every `digest.md`, `unchanged=True` in the mixed fixture (the two new isolated fixtures discard the flag via `_`, but SC-04 only requires one fixture tree demonstrate it, which the mixed tree does); no `open(..., "w")` in the new region |
| SC-05 | satisfied on substance, **new low-severity finding on literal text** | note present at the pinned sha, heading/sha/`CHECK_STATE_BIN`/`RESULT: RED` all match the grep contract, and I independently reran the CURRENT (restructured) case against a private copy of the pre-change (`772790be`) script: it still exits 1 printing `FAIL - BUG-440 INV-37 reconciles digest verdicts without mutation` — non-vacuity genuinely reproduces today. **But** the note's *verbatim* captured text (`mixed=False; clean=True; output=...` three-violation-line dump) is a transcript of the OLD single-fixture case's own diagnostic print, which no longer exists — today's case prints only the one-line `FAIL - ...` on failure, and the note was never touched between the two pins (`git diff` on the note across both shas is empty). The note's RED *conclusion* still holds; its literal *output text* no longer matches what the current case would produce. Advisory, not blocking — SC-05's exit/heading/sha/RESULT gate is satisfied and does not require exact text reproduction |
| SC-06 | satisfied | `python3 tests/integration/test-check-state.py`: exit 0, 217 output lines, 0 `FAIL` lines, 71.6s. Identical to cycle-1's 217/0/exit-0 at the prior pin — the +1 over the 772790be baseline (216) is exactly `case_bug440_digest_verdict_reconciliation`'s own `ok -` print, and stayed at +1 (not +2 or more) despite the case being internally restructured into three fixture calls, because only one `print(...)` statement exists in the case regardless of how many fixture trees it builds |
| SC-07 | satisfied | `check-state.sh` unchanged since cycle-1 (byte-identical to prior pin, confirmed by diff); tail-anchor regexes remain byte-identical to `validate-digest.py:1155-1160`, `_dtext` is read once and reused, zero literal `PASS`/`FAIL`/`BLOCKED`/`ESCALATE` tokens in the new region (grep-confirmed) |

## Coverage gaps (carried forward / new)

1. **V-04 / SC-01 order-blindness — still open, not remediated, not cycle-1 must_fix.** A defect that
   swaps which verdict is reported as "digest" vs. "feature.json" ships green. Fix is cheap: replace
   the two bare `"FAIL"`/`"PASS"` substring checks with two *positional* assertions (e.g. `mismatch[0].index("digest verdict 'FAIL'") < mismatch[0].index("feature.json verdict 'PASS'")`), which is dev/qa test-only work, not a `check-state.sh` change.
2. **SC-05's recorded verbatim text is stale relative to the current case shape** (info/low). Not a
   remediation gap in the check itself — RED still reproduces — but the note over-claims exactness for
   an output format that no longer exists. If the note is ever re-read as literal proof of *today's*
   output shape rather than *that a RED occurred*, it will mislead. No build change owed; flagging so a
   future cycle does not treat the note's text as current documentation.

## Test matrix

Unchanged since cycle-1: `change_type: bugfix` (plan.yaml T-01, unchanged this cycle).
`test_matrix.bugfix`: `unit if touches_runtime_code` → true (check-state.sh is runtime code) → unit
required, satisfied by T-01's own verify. `integration if fix_confined_to_tests_and_contract_docs` →
false this cycle too (the remedy IS confined to `tests/integration/test-check-state.py`, but the
*original* T-01 diff touched `check-state.sh` itself — the leg is evaluated against the feature's
whole diff, not the c2 delta alone) → not obligated by this leg; `integration` is independently
satisfied regardless because the diff's own test file matches `test_kinds.integration.detect` and I ran
it directly (SC-06, the scoped proof required by this dispatch). `match_bug_class` remains inert
(repository Expertise G-08 — no taxonomy entry resolves for any diff yet). **matrix_ok: true.**

## Cleanup

All mutation probing ran inside `tempfile.TemporaryDirectory()` fixture trees and a private
`isolated_bin(tmp)` copy of the bin tree, per-probe, auto-cleaned on exit — nothing written to the live
tree or the worktree outside this note. `git status --porcelain` before and after probing: identical
set of pre-existing modifications (`feature.json`, `plan.yaml`) and peer-written `notes/*-c1.md`/`*-c2.md`
files from concurrent reviewers; no file this dispatch is scoped to touch was altered.
