# QA gate — FEAT-2206 T-01 — pin fe49c8df3807d875f2cd44410559966cc836b9ab (baseline b7af829c) — run c0

## BLUF — VERDICT: FAIL

Unit and integration kinds are green with real fail-first evidence for SC-01..04, but two things stop a PASS:

1. **New defect (kind: substance, severity: med, task T-01, SC-03).** A shipped record whose factory issue is a non-ASCII digit string (`"²"`) crashes the whole audit with a `ValueError` traceback, exit 1. SC-03 and DEC-252 say shipped fields are comparison data and never graded. Cause: `board.py:_inv24_issue_number` (line ~146) guards with `str(n).strip().isdigit()` but then calls `int(n)`. `"²".isdigit()` is True and `int("²")` raises. `_inv24_shipped_claims` (board.py:178) calls it unguarded. The baseline had the same predicate, so an active record would crash identically (a latent defect). The new shipped path makes it reachable for records the ruling says are never graded. No test covers a non-integer shipped issue value (see coverage_gaps).
2. **Literal T-01 verify exits 1 at the pin today (kind: environment drift, not a code defect).** Its first step passes. The standalone `check-state.py` then reports three INV-26 violations, all on FEAT-2206's own card: the pinned plan says `building` and the live board now reads `review`. This is the known gh-sync/#2201 seam-order drift. The builder's log shows exit 0 from when the board still read `building`. `&&` stopped the chain there, so I ran the other gates separately (below). All were green. I am not grading the literal verify as passed.

Pin check: the worktree HEAD is 1de2ebd6 (a notes/feature.json-only child of the pin). All reads and runs used a pinned checkout at fe49c8df. `plan.yaml` `tasks[0].verify` at the pin is byte-identical to the working copy's, and I ran it as written.

## Phase 1 (from BRIEF and DEC-252 only, before reading source)

- SC-01 (unit): lenient classification of exactly `done`; strict-invalid shipped plan excluded; missing, unreadable, non-mapping or nested status stays checked; shipped BRIEF, STATE and feature.json not opened up front; filter applies under a `keep` selector.
- SC-02 (integration): full audit, `--changed` audit and `--feature X` (one note, exit 0); open-log boundary; nonempty real-corpus.
- SC-03 (integration): INV-24 shipped/active and shipped/shipped; INV-52; INV-29; sparse and full populations; malformed shipped fields never graded (undeclared repo, bad container, bad issue values, within-record duplicates).
- SC-04 (integration): INV-28 and INV-30 retired in `--list`; `--only` follows retired behavior; no gh milestone query; abandoned/rejected, missing-selector and host/repo/layout controls preserved.

## Gate execution (pinned checkout, env `CLAUDE_PROJECT_DIR`, `HARNESS_PROJECT_DIR`, `HARNESS_AGENT_TYPE` unset)

Mechanical accommodation, stated once: the literal verify writes `notes/merge-$pin.log`, which would overwrite the builder's log. I ran the same verify with only the `evidence=` line pointed at `/private/tmp/f2206-qa-evidence`. The builder log is untouched.

- Verify step 1 (new unit, new integration, `--real-corpus /Users/molchairuangutai/GitHub/harness`): PASS. Unit 15 PASS lines, 0 failures. Integration 14 tests OK. Real corpus: 9 landed, 7 shipped (BUG-2141, BUG-2161, BUG-2169, BUG-2180, BUG-2190, FEAT-2037, FEAT-71), 21 PASS (3 claims x 7), 0 failures.
  - The corpus ref is the control plane's moving HEAD, not a pinned SHA.
- Standalone clone at `fe49c8df`: `check-state.py` exit 1, 3 x INV-26 (drift above).
- Same clone, run separately: `validate-feature-json.py` 0; `check-decision-anchors.py` 0; `check-plan-routes.py` 0; `gen-decisions-index.py --stdout | diff` clean; `run-unit-tests.py --kind all` exit 0 (146 files, 111.7s wall).
- Per-kind result from the `--kind all` output: 60 unit files (tests/unit) all exit 0; 86 integration files all exit 0. Both kinds are nonzero.
  - The 3508 `PASS` lines are runner and per-case lines, not a test count.
  - The 4 `FAIL BUG-1290 5a/5b/5c` lines and one `ERROR could not resolve scan root` line are deliberate output of `test-factory-claim-mutation.py` and its siblings. I graded on exit codes, not a `^FAIL` count.
- Matrix: `bugfix` resolves to unit (touches runtime code under check_state/) plus integration (explicit in BRIEF and DEC-217). Both satisfied by directly exercising tests; `functional` is excluded under DEC-187. `matrix_ok: true`.
- Code grade: `code-grade.py --base b7af829c --head fe49c8df` exit 0, 56 functions, 56 RESULT: PASS, none below bar. Output: `/private/tmp/f2206-qa-evidence/code-grade.txt`.

## Fail-first (reproduced, tier: natural RED at the baseline, semantic)

Baseline = a pinned checkout at b7af829c, with the new tests run from the pin via `CHECK_STATE_BIN_DIR` and `CHECK_STATE_BIN`.

- Unit: exit 1, **10 FAIL** and 5 PASS. All are assertion diffs, not import or setup errors:
  - `features=[...]` still includes shipped plans.
  - `shipped=None`.
  - Strict-parse findings `does not load, so INV-3/4/5...`.
  - `opened=['BRIEF.md','STATE.md','plan.yaml']`.
  - `keep={shipped}` still leaves a subject.
  - Population entries are not triples.
  - The 5 PASS are controls.
- Integration (`-v`): exit 1, **8 FAIL** and 6 ok.
  - FAIL: INV-24 shipped claim graded, retired INV-28/30, milestone query issued (`milestones?state=open`), `--only` retired runs the invariant, changed audit, full audit, open-confinement (`BRIEF.md, STATE.md, feature.json, plan.yaml, runs/r9/state.yaml`), and the explicit-select note (exit 1 with strict-parse violation).
  - ok (baseline-equivalent controls, not claimed red): INV-24 shipped/active, INV-24 shipped/shipped, INV-29, INV-52, missing selector, unreadable status.
- `--real-corpus` against the baseline checker: **21 FAIL, 0 PASS**. It names shipped features in the full audit, opens BRIEF, and `--feature` exits 1.
- `--only INV-28` and `--only INV-30` at the baseline run the check and emit INV-32/43 findings, exit 1. At the pin they print `INV-28 is retired — DEC-252 ... Nothing runs for it`, exit 0, in the same words as INV-9.

Saved baseline outputs are in `/private/tmp/f2206-qa-evidence/base-unit.txt`, `base-int.txt` and `base-real.txt`. They match the builder's `notes/red-first.md` (10 and 8).

## Mutation checks (monkeypatch wrappers, no source writes)

- Mutant "abandoned and rejected also count as shipped": the new unit and integration tests stay **green** (exit 0, 14 tests). The standing tests catch it: `test-check-state-inv51.py` exit 1 (2 FAILs); with a rejected-only mutant, `test-check-state-feat59.py` 44.b/44.c FAIL. Abandoned/rejected preservation (SC-04 clause) is therefore pinned only by pre-existing suites. The new file adds none. This is the gap behind the `coverage_gaps` entry below, not a failure.
- The `lenient_station` duplicate-status probe (`status: done` then `status: null`) returns `""`, so the feature is not shipped (OralHedgehog case 1: OK). Other probes: nested `x:\n  status: done` gives not shipped; trailing comment gives `done`; `status: done` plus later invalid YAML gives `done`. That last result follows DEC-252's one-line decision, even though the T-01 intent prose says "invalid YAML is not shipped". DEC-252 is the signed text. Flagged as a question below.
- Shipped `feature.json` in each shape below, run in full clone and sparse worktree: no traceback, no shipped-specific finding.
  - invalid JSON, JSON `null`, a JSON list
  - `factory` as a string
  - non-string repo
  - dict-valued issues or parent
  - `"abc"`, `None` and `1.5` issue values (these skip cleanly; `True` as parent is ignored)
- The `"²"` shipped issue crashes in the full audit: `Traceback ... board.py line 189 _inv24_shipped_claims -> line 146 int(n) -> ValueError`, exit 1. With `--feature FEAT-5-shipped` it exits 0, since that path never builds the population.

## Green-evidence adequacy

- SC-01: strong. Unit pins the classifier cases, ordering and open boundaries. The CLI (SC-02) also observes the opens.
- SC-02: strong. Open-log allowlist, one-note exact line, full and changed audits, and 7/7 real shipped records. The real-corpus mode is discriminating (21 red at baseline).
- SC-03: collisions are fine (the baseline was already correct, so not newly red). The malformed-field leg is incomplete: undeclared repo, `issues: 42` and a duplicate only. Not covered: non-ASCII or other non-integer issue values and a malformed `parent`, which is the leg that hides the new defect. INV-52 and shipped/shipped INV-24 run only in a full clone; INV-24 shipped/active also runs in a sparse worktree.
- SC-04: retirement, `--list`, `--only` and no-milestone are discriminating. The abandoned/rejected control lives in older suites (see mutation checks).

## Known items, not re-litigated

- DEC-252 disclosures: handoff-validate.md is now demanded nowhere; the FEAT-63 gh-auth-probed-once test was deleted with INV-30.
- INV-26 live drift (see BLUF 2): only FEAT-2206's own card, 3 lines, nothing else in the standalone output. The pinned `building` plan against a `review` board is the #2201 seam order.
- Product guidance is missing: `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent per the signed BRIEF. The operator-settled grilling note and DEC-252 govern. I substituted no other documents.

## Open questions

- Q1 (non-blocking for the verdict): the T-01 intent says a shipped decision is a lenient YAML mapping read and that invalid YAML is not shipped. DEC-252 and the code use a one-line text read, so `status: done` with otherwise invalid YAML counts as shipped. Recommendation: treat DEC-252 as the authority and word the intent to match, unless the operator wants YAML validity to gate it.
- Q2: the repair is the dev's (main-session-direct). Suggested: make `_inv24_issue_number` total, e.g. `try: return int(n)` or require `str(n).isascii() and isdigit()`. Add shipped cases `"²"`, a malformed parent and a list-of-dicts issues value. That changes behavior for active records too (non-ASCII digit becomes "not an integer" finding rather than a crash), which should be confirmed.
- Re-gate: rerun the literal verify once the board and plan agree (plan status `review` at the new pin). `check-state.py` clean of INV-26 is required for exit 0.

## Principles applied

- Build the Lever: the open-log, baseline-export and monkeypatch-wrapper mutants reuse the suite's own helpers (`F.sparse_fixture`, `CHECK_STATE_BIN`); no source or test was authored.
