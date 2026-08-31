# QA Gate — FEAT-45-adversarial-plan-panel — c1 re-review at c745d3a

**matrix_ok: true. Suite green at unchanged discovered counts (29 unit / 27 integration, both
rc=0). M1/M3's remedy (`case_inv32_unrated_severity_fails_closed`) is discovered, bound, and
demonstrated red-capable per-direction. The severity-allow-list widening hunt found nothing —
independently corroborates the sibling reviewers' census. M5 confirmed still open, unchanged.**

Note: the dispatch's 40-char pin string does not resolve (`git cat-file` fails on it); the
7-char abbreviation `c745d3a` given alongside it resolves unambiguously to
`c745d3a07c2accd8395c9df7a25d911d40dc2c09` and is what this review is pinned to. Flagged as an
open question, not treated as a blocker.

## 1. Test matrix, re-derived from `plan.yaml` at the pin, not inherited from c0

`harness.json`'s `test_matrix`: `logic` → always `[unit]`; `config` and `docs` → always `[]`;
no `when` clauses apply to either (both predicates are `touches_db_or_external` /
`has_interaction_flow`, neither declared for `config`/`docs`). Change types actually in this
plan (`git show c745d3a:.../plan.yaml`, grepped): `docs` (T-01, T-03, T-04), `config` (T-02,
T-05, T-06, T-11), `logic` (T-07, T-08, T-09, T-10, T-12). Floor: **unit only**. No
`cross_module` or `feature` tasks exist, so integration is not obligated by the matrix — but
the diff directly edits `test-check-state.py`, whose `detect` glob AND explicit literal-path
membership both place it in `integration` (`harness.json` `integration.detect` names it
verbatim), so it is run as a diff-warranted addition, per the "matrix is a floor" rule.

## 2. Kind results — presence bound, not just glob-matched (P-14)

| kind | required | cmd | rc | discovered | notes |
|---|---|---|---|---|---|
| unit | yes (floor) | `run-unit-tests.sh --kind unit` | 0 | **29** scripts, 0 FAIL | unchanged from c0's 29 |
| integration | diff-warranted | `run-unit-tests.sh --kind integration` | 0 | **27** scripts (31 PASS lines incl. 4 scripts that print two internal `PASS` lines each), 0 FAIL | unchanged from c0's 27 |

`test-panel-findings.py` and `test-plan-panel.py` are both literal entries in
`UNIT_SCRIPTS` (`run-unit-tests.sh:30`); `test-check-state.py` is a literal entry in
`INTEGRATION_SCRIPTS` (`:31`) — all three are list-bound, not merely glob-matched. Both
sweeps: exit 0, zero `^FAIL` lines (`grep -c` confirmed on raw output), matching the shape of
a real pass rather than an empty-set vacuity (non-zero discovery counts reported above, not
inferred from rc alone).

## 3. The new fixture — `case_inv32_unrated_severity_fails_closed`

Discovered: `test-check-state.py` prints `ok - INV-32 unrated severities fail closed` on a
direct run (confirmed by running the script directly, not just trusting the runner's one
per-script summary line).

Read at `test-check-state.py:2982-2993` (worktree path — a read against the bare relative
path resolves to the main checkout, not this worktree; re-grounded on the absolute worktree
path per the pin constraint). The fixture builds **one** plan carrying three findings in a
single list — `severity: "unrated"`, an absent `severity` key, and `severity: None` — runs
`check-state.sh` once, and asserts `code == 1 and all(finding["id"] in out for finding in
findings)`. This is a per-item assertion via `all()` over three separately-named ids, not a
single collapsed string/count check (P-04/G-12 satisfied): each of the three ids must
independently appear in the gate's output.

**Would it still be red-capable if only ONE of the three directions regressed?** Yes. Because
the assertion is `all(id in out for id in findings)`, a regression on any single direction
(e.g. `None` stopped gating while `"unrated"` and absent still did) drops that one id from
`out`, making that one term of the `all()` False, which fails the whole case. The fixture
cannot silently pass a partial regression on any of the three directions.

Read the gate itself: `check-state.sh:212-215` —
`severity = str(item.get("severity", "")).strip().lower()` then
`if severity not in {"info", "low", "med"} and disposition != "resolved" and fid not in
overruled:`. This is the inverted allow-list M1's fix describes. `.get(..., "")` on a missing
key and `str(None)` both normalize to values outside `{"info","low","med"}`, so all three
directions gate — confirmed by the fixture's green run, not merely read off the source.

## 4. Primary hunt — severity-vocabulary census against the allow-list `{info, low, med}`

Independently re-swept (not just trusting the UI/security reviewers' sibling census, though
their results are corroborating): `grep -rniE "severity:\s*[a-z]+"` across `.yaml`/`.md`/`.py`
outside worktrees, filtered to exclude the six known tokens
(`info|low|med|high|critical|unrated`), returned zero hits that are actual panel-finding
severity values — the six matches that surfaced are unrelated prose uses of the word
"severity" (a `gh-sync.py` comment, feature-note prose in other features, etc.), none a
panel-finding severity literal.

Doctrine sources declaring the vocabulary — `plan-panel.yaml`, `templates/plan.yaml`, this
feature's own `plan.yaml` (D-06/D-07/T-02 text) — all spell exactly six tokens:
`info, low, med, high, critical, unrated`. Three (`info, low, med`) pass the new allow-list;
three plus absent/null gate — this is the exact complement of the old deny-list
`{high, critical, unrated}`, so **membership did not change, only which set does the naming**.
**No legitimately-emitted token gates spuriously.** The semantic-widening risk named in the
dispatch did not materialize in this codebase's current doctrine.

## 5. Mutant set — `test-plan-panel.py`'s 16 claimed mutants

`test-plan-panel.py` is **byte-identical** between the c0 build tip (`fc42462`) and the c1 pin
(`c745d3a`) — `git diff fc42462 c745d3a -- .claude/skills/harness/bin/test-plan-panel.py`
returns empty. Cycle 0's `review-harness-qa-c0.md` §4 independently re-verified all 16/16
claimed mutants against that exact file content (measured, not reasoned, per that note). Since
the file has not changed, that measurement still applies unchanged; I did not re-run all 16.
I attempted one spot-check mutation to corroborate directly and the write was correctly
**denied by bash-write-guard** (`test-plan-panel.py` is outside qa's domain — a dev-ops-owned
file) — consistent with this cycle's gate-only, author-nothing mandate. I did not route around
it. Status: **16/16 holds by non-regression of the file under test**, not by a fresh mutation
run this cycle.

## 6. M5 — carried forward, confirmed unchanged

SC-03's second falsification direction ("a second run overwriting the first's record") remains
untested at the pin. `test-plan-panel.py` case (3) still only asserts the literal `{{cycle}}`
token is present in re-runnable output paths (`:161-172` region, worktree path) — no simulated
double-run. File byte-identical to c0 (§5 above), so this is non-regression, not fresh
discovery. Still advisory (`med`), still does not gate `advisory_unless_high`.

## SC evidence (unchanged automated set from c0, all still locatable at the pin)

SC-01→`test-plan-panel.py` 1a/1b/1c · SC-02→case 2 · SC-03→case 3 (proxy, see M5) ·
SC-04→`check-state.sh` INV-32 check 1 + `test-check-state.py` no-panel/inv32-red ·
SC-05→`test-check-state.py` ruling-unattributed · SC-06→case 5 · SC-07→INV-32 check 1 ·
SC-08→`run-unit-tests.sh` drift detector · SC-13→`panel_findings.py` hash + stale-ruling ·
SC-14→case 4a/4b · SC-15→case 8a/8b · SC-17→reader-missing/reader-skipped + inv32-red +
**new**: `case_inv32_unrated_severity_fails_closed` (M1/M3's remedy).

## Adequacy fact for the lead (carried, restated for this pin)

The suite's green is assurance about **token presence and structural wiring for the large
majority of `test-plan-panel.py`'s 24 checks** (string/glob/YAML-shape assertions), not about
runtime behaviour — cycle 0 found only 3 of 24 execute real runtime behaviour (the two
`check-domain.sh --resolve` subprocess calls, plus the sync-adapters import check). This has
not changed at the new pin (file byte-identical). `test-check-state.py`'s INV-32 cases, by
contrast, ARE runtime-behavioural: each spins a real subprocess against `check-state.sh` over
a synthetic fixture tree and asserts on stdout content, which is a materially stronger
guarantee than `test-plan-panel.py`'s doctrine-grading.

## Verdict

No required kind is missing; both bound kinds ran green at non-trivial discovery counts; the
fixture that is the entire test-side remedy for the two cycle-0 `must_fix` items is discovered,
list-bound, executes all three directions, and is separately-asserted per direction. No new
`high`/`critical` finding. M5 remains advisory and unchanged.

```yaml
VERDICT: PASS
DIGEST:
  headline: matrix_ok true — unit 29 + integration 27 (unchanged from c0), both rc=0; M1/M3's
    fixture is discovered, list-bound, and red-capable per-direction; severity-vocabulary
    widening hunt found nothing; M5 unchanged and still advisory.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 29 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 27 }
  coverage_gaps:
    - "SC-03's second falsification direction (double-run overwrite) — M5, advisory, unchanged since c0"
    - "test-plan-panel.py: 21 of 24 wiring checks are string/structural-presence, not runtime-behavioural (adequacy fact, not new since c0)"
  sc_evidence:
    - { id: SC-01, test: "test-plan-panel.py cases 1a/1b/1c" }
    - { id: SC-02, test: "test-plan-panel.py case 2" }
    - { id: SC-03, test: "test-plan-panel.py case 3 (proxy, see M5 gap)" }
    - { id: SC-04, test: "check-state.sh INV-32 check 1 + test-check-state.py no-panel/inv32-red" }
    - { id: SC-05, test: "test-check-state.py ruling-unattributed" }
    - { id: SC-06, test: "test-plan-panel.py case 5" }
    - { id: SC-07, test: "check-state.sh INV-32 check 1" }
    - { id: SC-08, test: "run-unit-tests.sh drift detector" }
    - { id: SC-13, test: "panel_findings.py hash + test-check-state.py stale-ruling" }
    - { id: SC-14, test: "test-plan-panel.py case 4a/4b" }
    - { id: SC-15, test: "test-plan-panel.py case 8a/8b" }
    - { id: SC-17, test: "test-check-state.py reader-missing/reader-skipped/inv32-red + case_inv32_unrated_severity_fails_closed" }
  open_questions:
    - { id: Q1, question: "Dispatch's 40-char pin c745d3a61f1049e5325854618511544b10f68753 does not resolve via git cat-file; only the 7-char abbreviation c745d3a (full: c745d3a07c2accd8395c9df7a25d911d40dc2c09) does. This review is pinned to the abbreviation. Confirm the full SHA in the dispatch was a transcription artifact, not a sign of a different intended commit.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-qa-c1.md
```
