# QA c3 — FEAT-2206 T-01 — classification, F-2 end-to-end probe, real-corpus reconciliation (pin 688c5ef5e3b6e0dd694afb3d6476c915934501d4)

**BLUF: VERDICT stays FAIL (F-1 unchanged). c3 corrects c2's finding form and closes F-2 with an end-to-end run.**
c2 (`review-harness-qa-c2.md`) is preserved unedited as historical evidence; this note supersedes only its
classification and its F-2 / real-corpus wording. No source or test edited; no commit. The 60 unit / 86
integration / real-corpus results in c2 are carried, not rerun.

QA's digest schema has no `findings` field, so the findings below also appear in the digest as `coverage_gaps`;
this note is the durable prose.

## Corrected classification (kind = substance | form | proportionality; severity explicit)

c2 used the non-schema label `defect`. Actual kinds, my own judgment:

- **F-1 · kind: substance · severity: med · T-01 · SC-03.** A shipped record's 4301-digit `factory.parent`
  or issue string makes `board._inv24_issue_number` (`check_state/board.py:153`, `int(s)` behind only
  `isascii() and isdigit()`) raise ValueError (Python 4300-digit int limit); the full audit aborts with a
  traceback and the usable 11 collision is lost. This breaks SC-03's text (malformed shipped fields never
  graded, never break the comparison). It is the same crash class as c0's `"²"` must-fix, in a new shape.
  c2 omitted the severity word; it is `med` (code reviewer and PM also read it med). c2's "must-fix" was the
  blocking call; blocking is the lead's contract determination, not mine. Evidence unchanged from c2: probe
  `_inv24_issue_number('9'*4301)` raises, CLI fixture exit 1 with `board.py:153 <- _inv24_shipped_claims
  board.py:196 <- inv_24 board.py:255`. No test covers it. Proportionality: small repair (make the function
  total).
- **F-2 · kind: substance · severity: low · T-01 · SC-03 and task text "Keep active-record validation
  unchanged".** Retained (not retracted); see probe below. Proportionality: narrow trigger (an active record
  with a non-ASCII digit string), narrow cost.
- No form or proportionality findings; c2's Q-01 (intent prose vs DEC-252) is unchanged and still open, not
  a finding.

## F-2 end-to-end probe (authorized probe execution; not authored source or tests)

Task binding: plan.yaml `tasks[0]` (T-01) text, line 71: "Keep active-record validation unchanged." The
change to `_inv24_issue_number` (ASCII-only gate, shared by shipped and active paths) alters what an active
record produces for a digit string `int()` reads.

Method: disposable pins from `pinned-checkout.py` (both removed on return): pin 688c5ef5 and baseline
b7af829c (HEAD verified for each). Probe script `/tmp/qa-c3/probe.py` (volatile, outside the repo) reuses the
pin test module's own helpers (`feature_files`, `check`, the FEAT-1559 `sparse_fixture`) and runs the CLI
once per code tree via `CHECK_STATE_BIN`. Env: HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR
unset. Fixture: fleet declaring acme/widget, plus TWO ACTIVE `building` features FEAT-7-a and FEAT-8-b, each
with `factory: {repo: acme/widget, issues: {T-01: <value>}}`. Full audit, exit code 1 in every case because
of unrelated fixture findings (BRIEF approval, handoff, INV-37 gh, INV-27); only INV-24 lines compared.

|case (FEAT-7-a vs FEAT-8-b)|baseline b7af829c INV-24|pin 688c5ef5 INV-24|
|---|---|---|
|A: `"٣"` (Arabic-Indic) vs `3`|`INV-24: FEAT-7-a and FEAT-8-b both record acme/widget issue 3` (collision)|**no collision.** Instead `INV-24 FEAT-7-a: records issue number '٣' for acme/widget, which is not an integer — re-run factory publish...`|
|B control: `"3"` vs `3`|collision on issue 3|collision on issue 3 (identical)|
|C control: `3` vs `3`|collision on issue 3|collision on issue 3 (identical)|
|D: `"٣"` vs `4`|no INV-24 line|`INV-24 FEAT-7-a: records issue number '٣' ... not an integer`|

No Traceback in any of the 8 runs. Exact outcome: baseline reports the collision; the pin loses the collision
**and emits a new malformed-number INV-24 finding against the active record**, which baseline did not emit
(case D shows it on a lone value). So the pin is NOT silent: c2's wording "pin silent" was wrong in that
respect and is corrected here. The strict loader accepts `"٣"` as 3 (per the lead's statement; the probe's
fixture was not rejected by it, since INV-24 ran on both records rather than stopping at a load finding).

Decision: **keep F-2, low, reworded**: for an active record, the real-world collision between `"٣"` and `3`
is no longer reported and a different, arguably more accurate "not an integer" finding replaces it. That is
a behavior change on the active-record path that T-01 says must be unchanged. It is also a deliberate trade
recorded in the code comment at `board.py:143-149`. Whether the trade is acceptable is the lead's call from
the contract; my own judgment stays low severity. Not blocking by my reading.

## Real-corpus discrimination — reconciliation (correcting c2:54-55)

c2 wrote "real-corpus discrimination is therefore unshown". That was true only of my c2 attempt (the
real-corpus mode at the baseline with the 688c5ef5 tests raised ImportError, `lenient_station` absent:
signature-absent, a failed attempt, proves no behavior) and is withdrawn as a statement about the feature.
Older valid evidence exists and I had it:

- c0 (`review-harness-qa-c0.md:48`): `--real-corpus` against the baseline checker b7af829c yielded **21 FAIL,
  0 PASS** (names shipped features in the full audit, opens BRIEF, `--feature` exits 1), with the c0 pin's
  tests run from fe49c8df via `CHECK_STATE_BIN`.
- Retained capture `/private/tmp/f2206-qa-evidence/base-real.txt` (read this run): header "9 landed, 7 shipped"
  (BUG-2141, BUG-2161, BUG-2169, BUG-2180, BUG-2190, FEAT-2037, FEAT-71); `grep -c '^FAIL'` = 21,
  `grep -c '^PASS'` = 0. Natural RED, semantic (behavioral assertion failures), tier: natural RED at baseline.
- Qualification only: that run used the fe49c8df test file, not the 688c5ef5 one. The rework's later changes
  touched INV-24/INV-52 number handling and `lenient_station`; I did not rerun, and did not need to for
  fail-first, because the c0 red is valid for the shipped-skipping behavior SC-02 names. The capture lives in
  volatile `/private/tmp`, not under the feature tree; it is cited by path, not tracked.

So real-corpus discrimination **is shown** (21 red at baseline, 21 green at the pin per c2). The c2
ImportError remains a failed attempt, not evidence either way.

## Fail-first and matrix — carried by path (not rerun)

- fail_first: `notes/review-harness-qa-c2.md` (rework reds at fe49c8df; original baseline b7af829c: unit 10 FAIL,
  integration 9 of 16 FAIL), `notes/review-harness-qa-c0.md` (unit 10 FAIL, integration 8 FAIL, real-corpus 21
  FAIL), `notes/red-first.md` (builder receipts). SC-03's INV-24 collision cases were green at baseline by
  design (already correct), so SC-03 red evidence rests on the malformed-shipped-field and INV-52 census
  tests (c2:46-47). F-1 (oversized number) has no test and no red.
- matrix: unit satisfied (`run-unit-tests.py --kind unit` exit 0, 60 files), integration satisfied (`--kind
  integration` exit 0, 86 files) per c2:60-62. `matrix_ok: true`. F-1 and F-2 are not matrix gaps; they are
  uncovered-behavior gaps.

## Open questions

- Q-01 (c0/c2, unchanged): intent-YAML prose vs DEC-252 one-line classifier; non-blocking.
- Q-02: F-2 acceptability against "Keep active-record validation unchanged" is a contract call for the lead.

## Cleanup

Pins `FEAT-2206-skip-shipped-features--c3--qa-pin` and `--qa-base` removed (verified absent from `.pins/`).

## Principles applied

None cited from craft leaves this run.
