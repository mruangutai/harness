# FEAT-62 build divergences — check-state.py decomposition

Bar: every suite's exit status, stdout bytes and stderr bytes are identical to the baseline below,
except the rows enumerated under `## After T-03 — the feedback loop, measured

- The eight baseline suites re-run after T-02 and T-03: all `SAME` against the receipts
  above (exit, stdout, stderr). Ninth suite `test-check-state-table.py`: ALL PASSED.
- `tests/unit/test-harness-boundary.py` `case_changed_state_feedback`,
  `tests/integration/test-plan-merge.py` `case_feat62_changed_feedback_after_a_plan_write`,
  `tests/integration/test-feature-json-merge.py` `case_15_changed_feedback_after_a_write`:
  red against the pinned bin/ (`git archive 16ee44f0`, via `HARNESS_BOUNDARY_BIN` /
  `PLAN_MERGE_BIN` / `FEATURE_JSON_MERGE_BIN`), green on the build.
- Live: `plan-merge.py set-task-station … T-03 building` in this worktree relayed the real
  checker's `--changed` output on stderr (the four pre-existing INV-29 stale-worktree rows and
  INV-32's five resolved-finding notes); the stdout receipt and exit 0 unchanged.
- `check-plan-routes.py --consolidation-audit`: 0 findings. `code-grade.py --base 16ee44f0`:
  318 graded, 0 below bar.
- One shape decision inside T-03's brief: `record-amendments` writes the plan and the ledger
  under the plan's lock; the ledger write (feature_json_write) relays once with both files
  dirty, and the plan path does NOT relay a second time — one `--changed` run over one dirty
  tree says everything a second would.

## Validate c0 — an orphaned run, and what the loop caught

- The validate orchestrator started `validate-validator` at 16:48Z without recording the
  plan→validate `succession` judgement, its panel wrote five artifacts (qa PASS, security
  PASS, ui PASS, code review FAIL, goal-check FAIL — `notes/review-*-c0.md`,
  `notes/research-*-goalcheck-validate-c0.md`), and the process then died on a provider
  error before closing the run. Its `PENDING` run entry and a retrospective succession the
  main session first appended were REMOVED by operator ruling 2026-09-21: the entry was a
  dead process's unfinished write, and INV-43 grades a retrospective succession as a
  standing violation. The c0 artifacts stay; the fix round below answers them.
- Fix round 1 (main session, DEC-174): CR-02/GC-04's census (`_dirty_paths` catch narrowed;
  47 sites); GC-02 (resource-level reads lock, three misdeclared-resource mutants); GC-03
  (fixture checker probes the writer's lock and must see it FREE; red on a relay-inside-
  the-lock mutant of each writer). GC-01 and GC-04's spec contradictions were ruled by
  BRIEF amendment (SC-01 admits D-1/D-3; SC-09 admits extraction-compatible control flow)
  with the approval revoked and re-signed.
- The changed-state loop itself, on this feature's own record writes, surfaced the stale
  `review_sha`, the unbounded `cycles_used`, and the missing succession — three real
  findings from one `set-key`.

## Ruled divergences`, each proved red-first (a failing
expectation describing old and new order committed before the move) and ruled here.

## Baseline receipts — at 1b69f67f (pin), worktree clean, run from the worktree root

| suite | exit | stdout sha256[:16] | stderr sha256[:16] |
|---|---|---|---|
| `python3 tests/integration/test-check-state.py` | 0 | `8fb2fb685ce1ec93` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-entry.py` | 0 | `c1a7332f7b889f68` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-plans.py` | 0 | `bf722335294598a6` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-handoff.py` | 0 | `509f0d8ecf22dbca` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-worktrees.py` | 0 | `9be634f33e8e2f5a` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-inv26.py` | 0 | `be17fb78d64bdfe5` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-records.py` | 0 | `7d42d644edf28dc8` | `e3b0c44298fc1c14` |
| `python3 tests/integration/test-check-state-feat59.py` | 0 | `a7108ea889731b1d` | `e3b0c44298fc1c14` |

Digests were stable across two consecutive runs (test-check-state, test-check-state-records re-run).
`e3b0c442…` is the empty-string digest: every suite has empty stderr at the baseline.

## After T-01 — receipts

All eight suites: exit, stdout digest and stderr digest IDENTICAL to the baseline table above
(re-measured after the final runner change). The ninth suite, `test-check-state-table.py`,
covers what the move added; its 22 cases were run against the baseline copy
(`CHECK_STATE_BIN=<baseline>`) and all 22 FAILED there before passing on the new checker.

Live-tree evidence (this worktree at the pin, default run): baseline 1,760 rows, new 1,760
rows, identical as a multiset; the sequence of invariant CLASSES (which block prints when)
is identical; the only reordering is feature order INSIDE a block — see D-1.

## Ruled divergences

| id | what changed | where it is observable | why | ruling |
|---|---|---|---|---|
| D-1 | Features are iterated in SORTED name order. The baseline iterated `glob.glob` / dict order — filesystem order, which on this machine is not sorted and on ext4 is hash order. | Live tree: rows within INV-17, INV-22/INV-8, INV-32, INV-3 and the FEAT-59 family reorder across features; no suite receipt changes (fixtures carry one feature, or assert by content). | A gate whose row order depends on the filesystem prints a different report on CI than on the operator's machine. Determinism is the point of a runner owning iteration. | Accepted. Feature order is sorted everywhere; asserted by `test-check-state-table.py` ("features are iterated in SORTED order"). |
| D-2 | Family interleave: a block that judged several invariants per feature (INV-6/33/7/22/8/12; INV-16/36/15; INV-38/41; INV-39/40/43; INV-3/4/5) now runs row-by-row INSIDE its group (`for group: for feature: for row`). Per-feature order of a family's rows is preserved; only two rows of the same family firing on one feature could interleave differently — and they do not on the live tree or in any suite. | No suite receipt changes; no live-tree change measured. | The grilled shape: one row per INV number, family order kept by the group. | Accepted; recorded so a future fixture that trips two family rows on one feature is not read as a regression. |
| D-3 | Context-load findings (a plan.yaml that does not load; an invalid harness.json; an unresolvable panel/seam era; the SEAM_NOTES startup assertion; plan-merge failing to import for INV-40) print FIRST. The baseline printed each at the position of the block that first needed the source. | Only on a tree with such a defect AND earlier findings; none in the suites or on the live tree. | Shared sources are parsed once into `Ctx`; the findings are the context's own. | Accepted. |
| D-4 | INV-32's FEAT-45 T-07 mutation markers (`# INV-32 BEGIN/END`) now wrap the invariant's TABLE ROW, not its code. Removing the row unregisters the check, which is what the mutant needs; the function may stay defined. The ERA markers stay inside the function body. | `test-check-state-records.py` `inv32-red` case — receipt unchanged after the move. | The plan foresaw rewriting marker slices against the function (INV-26's); INV-32's is the one that actually slices. | Accepted. |

## Plan deviations, disclosed

- INV-26, INV-30, INV-24, INV-37 (build-entry) and INV-23 stay REPO-scoped and loop
  `ctx.features` themselves, instead of being hoisted into the runner: each does one-time
  work (an import whose failure is one finding, one `gh` call over a batched candidate set,
  cross-feature collision state, a CLAUDE.md check beside per-feature sweeps). `--feature`
  still narrows them because they loop `ctx.features`, which `--feature` narrows. The plan's
  "loop-order change for INV-26" therefore did not occur; there was no honest way to hoist a
  two-pass, one-network-read block without inventing a divergence.
- INV-15 IS hoisted (rows INV-16/INV-36/INV-15 per feature over that feature's runs); its
  interleave is D-2.

## Record anomalies — RULED 2026-09-21 (follow-up PR after ship)

- The unnumbered `OMP-PORT` row is **INV-45** (authority DEC-233 unchanged; finding bytes
  unchanged). INV-44 was already taken by the DEC-230 rejected-record row.
- The digest-verdict cross-check is **INV-46**, its own feature-scoped row after INV-15
  (reads: run state, digest.md, feature.json, validate-digest.py; authority DEC-156). INV-15
  keeps the contract check; the digest is validated once through `Ctx.lead_digest` and both
  rows read the result. Message text `INV-37:` -> `INV-46:` -- the ONE receipt divergence
  (`test-check-state-records.py` stdout; exit unchanged), red-first in that suite's BUG-440
  cases and in `test-check-state-table.py`. The other seven suites: SAME.

The original record, as parked:

## Record anomalies as first recorded

- The retired INV-9 slot still RUNS an unnumbered check (check-omp-port.py under
  `.omp/config.yml`). The table names it `OMP-PORT` with authority DEC-233. Minting an INV
  number for it is the operator's call.
- `INV-37` labels two different checks: the digest-verdict cross-check inside INV-15's
  success branch (`INV-37: <feat> run <id>: digest verdict ... differs`) and the build-entry
  receipt (BUG-1309). Both texts are preserved byte-for-byte; the row is the build-entry one.
