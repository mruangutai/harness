# qa segment — FEAT-06 (D-08 "two jobs, one persona") — cycle 0

**VERDICT: PASS.** The blocking `qa_gate` (`harness.json` `gates.qa_gate: blocking`) is satisfied:
`unit` is the only matrix-required kind across all ten PLAN tasks, it is fully present and green, and
`run-unit-tests.sh`'s own drift detector confirms the new script (`test-team-catalog.py`) is
registered, not orphaned.

## Anchor

```
$ git rev-parse HEAD
9f87c48dae0ced97e7655dffb9daddeba4708324
$ .claude/skills/harness/bin/run-unit-tests.sh; echo "exit=$?"
```
Ran from repo root in one invocation (issue #36 avoided). Full output, counted directly (`grep -c`
against the captured run, not eyeballed): **13** scripts (the `SCRIPTS` array at
`run-unit-tests.sh:6`), each printing `PASS <name>`; **281** individual `ok` case lines; **0** `FAIL`
lines anywhere; terminal line `exit=0`. `test-team-catalog.py`'s own
block: **10/10 checks passed**, one line per SC it covers (SC-01, SC-02, SC-04, SC-07 ×2, SC-08,
SC-09, SC-10, SC-14, SC-15). `test-harness-yaml-corpus.py`: **12/12**, including the SC-06
broken-fixture-under-`teams/` case and a scan confirmed non-vacuous on **both** roots (`.harness`=56
files, `.claude/skills/harness/teams`=2 files). `test-check-state.py`: cases (h)/(i)/(j) — the T-01
INV-6 fixtures — all `ok`.

## Phase 1 (BRIEF/PLAN only) vs Phase 2 (code) — the delta

Before reading any source, the 15 SCs implied: 3 fixture-driven unit assertions for INV-6 (SC-01);
one single-definition assertion (SC-02); 2 inspection SCs no runner can produce (SC-03, SC-12); one
uat (SC-13); one runner-exit assertion (SC-11); and 8 further unit assertions over team-file shape,
playbook text and SPEC agreement (SC-04–SC-10, SC-14, SC-15). One delta found on inspection — see
**SC-05 count conjunct** below; every other Phase-1-expected unit assertion has a named, behavioral
test in the diff, none satisfied by an unrelated pre-existing test.

**Coverage gap — SC-05's count conjunct is unasserted.** SC-05 has two halves: every `*.yaml` under
`teams/` loads, **and** the directory's contents are exactly **two** files. Only the first half is a
registered assertion. Checked directly, not assumed:
```
$ grep -n 'check(\|== *2\|len(' .claude/skills/harness/bin/test-harness-yaml-corpus.py
174:check(f"every shipped YAML parses ({total} files across {len(ROOTS)} roots: "…   # >=0 parse check
180:check(f"the corpus under {r} is not empty …")                                    # >=1, not ==2
```
The "2" that appears is inside a printed *label* (`"…teams=2"`), not an asserted equality — and
`test-team-catalog.py` never references `teams/` file counts either (`grep -n 'teams\b'` there hits
only comments and unrelated `team-config.yaml` teams). Nothing today fails the gate if a third file
lands under `.claude/skills/harness/teams/` — e.g. an accidental leftover fixture, or a future team
added without updating this test — SC-05's own equality clause has no floor. **What would need to
change:** `.claude/skills/harness/bin/test-harness-yaml-corpus.py`, adding a `check(...)` asserting
`counts[teams_root] == 2` (from the `scan_roots` return already computed at `:172`), or an equivalent
assertion added to `test-team-catalog.py`. Not a `must_fix` from me — routed to the validator-lead per
the dispatch instructions.

## Matrix disposition

| change_type | tasks | required kinds | state |
|---|---|---|---|
| `bugfix` | T-01 | `unit` (+ `when: match_bug_class`, see below) | satisfied — `test-check-state.py` cases (h)/(i)/(j) |
| `logic` | T-07 | `unit` | satisfied — `test-team-catalog.py`, 10/10 |
| `config` | T-02, T-04, T-05, T-10 | none | n/a by matrix (config.always: []); T-02/T-04/T-05/T-10 are nonetheless exercised by the same unit suite (checks 1,2,3,4,6, the corpus scan) as a byproduct of covering the artifacts they produce |
| `docs` | T-06, T-08, T-09, T-11 | none | n/a by matrix; T-06/T-11 exercised by checks 5,8; T-08 by checks 7,9 + `check-docs.sh` (run, exit 0, 45 patterns, 0 stale) |

**`bugfix.when: {kind: __bug_class__, if: match_bug_class}` — disposed, not silently dropped.**
T-01's diff (`check-state.sh`) is a pure string-comparison logic fix: `_sha = (val("review_sha") or
"").strip().lower()` then a membership test against `harness_yaml.PLACEHOLDER_UNSET`. No I/O,
concurrency, external system, or security boundary is touched — it is the same shape of defect as
the rest of the bash-heredoc/Python state-check surface already covered by `unit`. Evaluated against
the diff: no additional kind is warranted. `unit` is sufficient and the red-first receipt (below)
demonstrates the exact fixture the fix must flip.

**`matrix_ok: true`**

## Test-first audit (D-06)

T-01 carries an explicit red-first requirement with a verbatim receipt, not a prose claim. Verified
present at `notes/before-check-state-635ef14.txt:12-29` — invocation, HEAD `635ef14`, `check-state.sh`
stated UNMODIFIED, then case (h) printed `FAIL` with the exact violation text, terminal `exit: 1`.
This is the discriminating artifact D-06 required; it is not an assertion I am taking on trust.

## Adequacy — beyond the BRIEF's declared gaps

BRIEF `## Verification gaps` already names: no runner proves an orchestrator actually sequences the
qa segment or dispatches `build.yaml`; no runner executes `build.yaml` or a ship; SC-03's whole-repo
diff has no runner. Restating those is not a finding. One thing **not** already named there:

- **`test-team-catalog.py` check (8) (SC-14) and check (9) (SC-15) are read against the live
  `SKILL.md`/`SPEC.md` text, not fixtures** — this is correct per D-04 (presence, not a synthetic
  double), and I confirmed it discriminates: `git show 635ef14:.claude/skills/harness/SKILL.md | grep
  -c -e test_matrix -e loop_back -e '\bqa\b'` → **0**, checked directly, not taken from BRIEF's stated
  measurement. Check (9)'s `panel_set()` raises loudly (not a silent guess) on an ambiguous `{...}`
  row — read the function; it is not decoration. No gap here.
- **See coverage gap above (SC-05 count conjunct)** — the one adequacy question with a real answer.

**SC-03 — resolved, not left as ambient worry.** Re-running `check-state.sh` on the current tree
against the `635ef14` before-capture surfaces one extra line: `FEAT-06…: run dir qa-validator exists
on disk but feature.yaml does not record it — orphaned work`. This is **not** an INV-6 line. Settled
by checking, not assuming: `git diff 635ef14..9f87c48 -- .claude/skills/harness/bin/check-state.sh`
touches **only** the INV-6 hunk (one `if` replaced by a 4-line equivalent condition — see the diff
above); no other invariant's logic changed. The extra note is produced by an untouched code path
firing against `runs/qa-validator/`, a directory created *after* `635ef14` for this qa dispatch itself
— it would print for any feature mid-dispatch, regardless of this diff. SC-03's "no invariant other
than INV-6 changes" holds; the live artifact is a byproduct of when this check happened to run, not
of the code. Formal confirmation is still `verify: inspection` — a reviewer's job, not mine to sign —
but the discriminating check is done and does not point at a defect.

**The authoring half of this segment was structurally unavailable, as scoped.** `tests/` and `web/`
do not exist in this repo; every test lives under `.claude/skills/harness/bin/test-*.py`, outside my
domain and inside the DEC-174 carve-out (extended by D-05). I wrote no tests this cycle — the ten
`test-team-catalog.py` assertions and the T-01 fixtures were authored main-session-direct, per PLAN's
routing table. This is not a `BLOCKED`; it is the expected shape of this feature's own routing wall
(#20).

## SC evidence map

| SC | Test | Notes |
|---|---|---|
| SC-01 | `.claude/skills/harness/bin/test-check-state.py` cases (h)/(i)/(j), lines ~231-318 | red-first receipt at `notes/before-check-state-635ef14.txt:12-29` |
| SC-02 | `test-team-catalog.py` check (6) | needle constructed from `harness_yaml.PLACEHOLDER_UNSET`, not embedded |
| SC-03 | inspection — see Adequacy note above | not automated by design (BRIEF) |
| SC-04 | `test-team-catalog.py` check (1) | |
| SC-05 | `test-harness-yaml-corpus.py` (parse half only — both roots parse, non-vacuously) | **partial**: the "exactly two files" half is unasserted — see coverage gap above |
| SC-06 | `test-harness-yaml-corpus.py` "detects a broken team definition under .claude/skills/harness/teams" | |
| SC-07 | `test-team-catalog.py` checks (2),(3) | |
| SC-08 | `test-team-catalog.py` check (4) | |
| SC-09 | `test-team-catalog.py` check (5) | |
| SC-10 | `test-team-catalog.py` check (7) | |
| SC-11 | `run-unit-tests.sh` exit 0, `test-team-catalog.py` present in `SCRIPTS` and output | |
| SC-12 | inspection — main-session-direct execution reasons stated per-task in PLAN.md (`carve-out` T-01/T-05/T-07; `domain-ungranted` T-02/T-04/T-06/T-09/T-10/T-11; `squad-dispatched` T-08) — not my job to adjudicate, flagged for pm/validator-lead | |
| SC-13 | uat — not mine | |
| SC-14 | `test-team-catalog.py` check (8) | |
| SC-15 | `test-team-catalog.py` check (9) | |

No SC is marked met by me — that is pm's job. This table only names the test each SC's evidence
should point to.
