# BUG-285 · S-01 retarget — plan and brief moved off the deleted monolith

**The plan executes again.** 29 surfaces across `plan.yaml` and `BRIEF.md` named a file commit
`efcebe2d` (issue #1527) deleted, or a line number the same merge moved, or a baseline the split
killed. All retargeted onto measured anchors at `6cb113f4`. Five tasks in, five tasks out; no
task's goal changed. Two new decisions: **D-12** (where T-01's fixture lands) and **D-13** (the
ordering that keeps T-01 out of T-04's and T-05's verify).

**The unit-suite FAIL trap is closed.** `run-unit-tests.sh --kind unit` prints **four** lines
beginning `FAIL ` on a **green** run — a test's own live-mutant proof. SC-10 asserted zero, so it
was false at baseline and would have failed a correct build. SC-10 now grades exit status only and
says why the count is not the measure; T-03, T-04 and T-05 carry the same correction, and each now
requires the status be captured into a shell variable rather than read from `$?` after a pipe.

## The pole-file decision (D-12) — evidence, then ruling

`test-gh-sync-open.py` is the **only** pole file holding reader-level cases. `grep load_recorded`
across the five poles hits `-open` alone: the whole `T-06 Part C` block (`:350-399`) and the whole
`fix1 Part B` block (`:401-474`) sit there, zero-byte fixture at `:426-442` included. `-record`,
`-ship`, `-abandon` hold none; `-start-task` binds `_ghs` for other functions. The split's own
support module endorses it: `gh_sync_support.load_gh_sync` (`:844-846`) documents itself as *"Used
by the cases that assert a function's own contract rather than a subcommand's."* So the fixture
goes beside its old neighbours — its subject is `load_recorded`'s parser, not the `open`
subcommand — and no new test file is created. The product lead's grep is confirmed, not overturned.

**One thing the retarget uncovered that the sweep list did not name:** `test-gh-sync-open.py` does
**not** import `harness_yaml`, so T-01's YAML-side assertion needs one added import line
(precedent: `test-gh-sync-start-task.py:25`). That line falls outside SC-05's region clause, so
SC-05 now permits it explicitly — otherwise a correct build fails SC-05.

## OLD → NEW

| Surface | OLD | NEW |
|---|---|---|
| T-01 `files:` | `tests/integration/test-gh-sync.py` | `tests/integration/test-gh-sync-open.py` |
| T-01 `verify:` | `… test-gh-sync.py` | `… test-gh-sync-open.py` |
| T-01 insertion point | monolith `:1442` / `:1444` | `-open:399` (check opens `:396`) / `:401` |
| T-01 `nested_feature_dir` | "line 144" (monolith) | imported name; def `gh_sync_support.py:144` |
| T-01 `check` | "line 769" | imported name; def `gh_sync_support.py:830` |
| T-01 `_ghs` handle | "BIN_DIR at lines 1406-1410" | already bound `-open:361` via `load_gh_sync()` (def `:844`) |
| T-01 `harness_yaml` | "imported at line 25" | **not imported** — add `import harness_yaml` at `-open:16-20` |
| T-01 `json`/`os` | "lines 17-18" | `-open:16` / `:17` |
| T-01 `load_recorded` | `gh-sync.py:484` | `:527` |
| T-01 parse call | `:523` | `:566` |
| T-01 SystemExit | `:524-531` | `except` `:567`, raise `:572-574` |
| T-01 isinstance guard | `:535` | `:578` |
| T-01 zero-byte fixture | monolith `:1470-1480` | `-open:426-442` |
| T-01 failing-check shape | "lines 1474-1480" | `-open:436-442` |
| T-01 baseline | `exit 0, 318 ok, 0 FAIL, 36.9s @ 7e0c2ec` | `exit 0, 79 ok, 0 FAIL, 10.6s @ 6cb113f4` |
| T-04 `verify:` | one `test-gh-sync.py` | `-open` + `-record` |
| T-04 baselines | `36 files 3.5s` / `318 ok 36.9s` | `36 files 2.4s (exit-status only)` / `79 ok 10.6s` / `56 ok 8.8s` |
| T-04 `depends_on` | `[]` | `[T-01]` (D-13) |
| T-05 `verify:` | one `test-gh-sync.py` | `-open` + `-record` |
| T-05 baselines | same two dead numbers, "more than 318 ok" | as T-04; "above 79 ok once T-01 lands" |
| T-05 module-loading cite | "the way `test-gh-sync.py` does" | `gh_sync_support.py:844-850` (read, do not import) |
| T-03/T-04/T-05 unit FAIL count | "assert the FAIL count DIRECTLY" for every command | exit-status only for the unit runner; direct count kept for the poles |
| D-01 `because` | isinstance guard "`gh-sync.py` line 535" | `gh-sync.py:578` |
| D-07 `because` | "running `test-gh-sync.py` … is 36.9s" | the two poles, `10.6s` / `8.8s`, unit `2.4s`; DEC-217 derivation intact |
| BRIEF Problem | `test-gh-sync.py (:1415-1512)`, fixture `:1470-1480` | `-open (:350-474)`, fixture `:426-442` |
| BRIEF REQ-01, SC-01 | `test-gh-sync.py` | `-open` |
| BRIEF SC-04 | `318 ok @ 7e0c2ec, 36.9s` | `-open ≥79 ok` **and** `-record ≥56 ok`, both `0 FAIL @ 6cb113f4` |
| BRIEF SC-05 | pathspec `test-gh-sync.py`; region by block names | pathspec `-open`; region by the two literal strings (`:399`–`:401`) **plus** the added import line |
| BRIEF SC-10 | "exits 0 and prints zero lines beginning FAIL" | exit status only, with the four-baseline-FAIL reason recorded so it is not restored |

## Ordering (D-13)

`T-01 → T-04 → T-05`; `T-02 → T-03` parallel. T-01 **edits** `-open`; T-04 and T-05 only **run**
it. Direction is forced — T-01 runs nothing they edit. Cost is parallelism; the alternative is a
verify whose baseline nobody can pin. Each of T-01/T-04/T-05 now states in `intent:` which file it
edits and which it only runs.

## Verification performed

**1. Loader.** `harness_yaml.load_plan(plan.yaml)` → loads. Keys: `approval decisions feature
lanes panel schema source_issues status tasks`. Decisions `D-01…D-13`.

**2. `files:` entries, one by one.**

| Task | Entry | State |
|---|---|---|
| T-01 | `tests/integration/test-gh-sync-open.py` | EXISTS |
| T-02 | `.claude/skills/harness/bin/factory_decompose.py` | EXISTS |
| T-03 | `tests/unit/test-factory-decompose-loader.py` | ABSENT — **created by T-03** |
| T-04 | `.claude/skills/harness/bin/gh-sync.py` | EXISTS |
| T-05 | `tests/unit/test-feature-json-readers.py` | ABSENT — **created by T-05** |

**3. Stale-reference search.** Run in the feature dir:

```
grep -n 'tests/integration/test-gh-sync\.py\|318 ok\|318 "ok"\|318-.ok\|36\.9\|7e0c2ec\|gh-sync\.py:484\|gh-sync\.py:523\|gh-sync\.py:535\|gh-sync\.py line 535\|:524-531\|:1470\|:1442\|:1474\|1406-1410\|1415-1512' plan.yaml BRIEF.md
plan.yaml:11:  resolved_at: 7e0c2ec148c05786d2cbbc1bf1f352c3e0403738
plan.yaml:193:      \ is analytically entailed by SC-01 plus gh-sync.py:523-554, and its delivery\
BRIEF.md:170:  command and its 318-`ok` baseline no longer exist. The `FAIL`-line count is
```

Three hits, all accounted for, **no live target among them**:
- `plan.yaml:11` — `lanes.resolved_at`. No verb writes `lanes:`; accepted as recorded in D-05.
- `plan.yaml:193` — inside `panel.findings[].summary`, a verbatim transcription of what a cycle-2
  reader said. `panel:` is a non-goal here and only `set-panel` writes it; a reader's own words are
  not re-anchored. **This is the one surviving stale `gh-sync.py` anchor in the file.**
- `BRIEF.md:170` — my own sentence saying that baseline no longer exists. A negative reference.

Every `gh-sync.py` anchor now cited anywhere: `plan.yaml:20 → :578`, `:277 → :527`, `:323 → :578`,
`BRIEF.md:14 → :527` (plus the panel line above). All four verified at source.

**4. `approval:` / `panel:` / `lanes:` byte-identity** vs `git show HEAD:<plan>`:
`approval IDENTICAL` (sha256 `6f59dc09…`, unchanged from the pre-start snapshot),
`panel IDENTICAL`, `lanes IDENTICAL`. No `panel:` write occurred.

**5. `check-plan-routes.py`, cwd `/Users/molchairuangutai/GitHub/harness`** (the main checkout):

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-04 granted to harness-backend-dev, harness-dev-ops
OK T-05 granted to harness-backend-dev, harness-dev-ops, harness-qa
0 violation(s) across 1 plan(s)
exit=0
```

**Nothing new appears, and PF-142f3a51's DEVIATION does not reproduce today** — not from the main
checkout and not from the worktree (re-run from cwd `…/BUG-285-yaml-loader-pin`: byte-identical
output, exit 0). Reported as observed rather than worked around; the team-config skew that finding
named is no longer measurable at `6cb113f4` with main merged in.

**6. Baselines re-measured myself** (worktree, `6cb113f4`, `env -u HARNESS_AGENT_TYPE`):
`test-gh-sync-open.py` exit 0, **79 ok**, 0 FAIL, **10.6s**; `test-gh-sync-record.py` exit 0,
**56 ok**, 0 FAIL, **8.8s**; `run-unit-tests.sh --kind unit` exit 0, 36 files, **2.40s wall**, and
**4 lines beginning `FAIL `** (`MUTANT ACTIVE` … `MUTATION PROOF: 3/3 cases reddened`). The `ok`
counts match the orchestrator's measurement exactly; wall times differ by <1s (10.6 vs 11.2, 8.8
vs 9.1) — two runs of one command, not drift. The plan records my measured values.

**7. `plan-merge.py` stdout, every invocation** — 15 writes, all rc=0:
`AMENDED tasks:T-01.files`, `tasks:T-01.verify`, `tasks:T-01.intent` (twice — second pass removed
the deleted path's spelling), `tasks:T-03.intent`, `tasks:T-04.verify`, `tasks:T-04.intent`,
`tasks:T-04.depends_on`, `tasks:T-05.verify`, `tasks:T-05.intent`, `decisions:D-07.because`
(twice), `decisions:D-01.because`, `decisions:D-12.because`; `ADDED D-12`, `ADDED D-13`. Each
followed by `APPLIED <plan path>`. Every `amend` carried `--expect-sha256`; no exit 7, no exit 4
after the two list fields were re-shown with `--yaml-value`.

## Open

- **T-01's survival is the operator's call, not mine** (out of scope by dispatch). Retargeted as it
  stands. For the record: after the retarget T-01 and T-05 both assert the YAML-only input against
  `load_recorded`, T-05 as one row of a six-input parity table. T-01 is not redundant — it is the
  only assertion on the *refusal message wording* (`does not parse`), which D-11 deliberately keeps
  out of T-05 — but its two-directional fixture checks do duplicate T-05's input 5.
- `plan.yaml:193`'s stale `gh-sync.py:523-554` sits inside a panel finding summary. If the
  orchestrator wants it re-anchored, that is a `set-panel` write and not a pm one.
