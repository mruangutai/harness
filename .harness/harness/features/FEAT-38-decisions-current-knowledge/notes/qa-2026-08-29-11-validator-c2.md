			# QA re-verification — FEAT-38 — cycle 2 — §2 reopened (115-line integration PASS drop)

**VERDICT: PASS.** The 115 lines are fully allocated to a **grep-pattern mismatch across two
independently-run gate cycles measuring byte-identical script content**, not to lost coverage,
skipped sub-cases, or tree-dependent census volume. Sections §0/§1/§3/§4/§5/§6 of
`notes/qa-2026-08-29-11-validator.md` stand unchanged and are not restated here.

## The mechanism (not the two anticipated in the dispatch — a third, confirmed by direct measurement)

Three of the 29 `INTEGRATION_SCRIPTS` — `test-worktree-terminal.py`, `test-post-merge-sweep.py`,
`test-hooks-install.py` — report their own sub-cases as `PASS: <name>` (**colon**, no space after
`PASS`). Every other script in both arrays that emits sub-case lines uses `PASS <name>` (**space**,
no colon) or `ok - <name>`/`ok    <name>`. `run-unit-tests.sh` itself (line 152) emits `PASS
<script>.py` (space) once per script.

- Cycle 1's `585` = `grep -c '^PASS '` (**space-anchored** — the runner's own convention). Verified
  by direct re-run: 556 sub-case `PASS ` lines summed over the 29 scripts + 29 runner markers = 585.
- The prior gate's `700` = `grep -c '^PASS'` (**unanchored trailing character** — matches `PASS `
  AND `PASS:`). `585 + 115 = 700`, and `115` is exactly the sum of the three colon-convention
  scripts' sub-case counts: `34 + 52 + 29 = 115`.
- This reproduces **identically at both trees** when measured with the *same* single expression
  (below), which is the direct proof that nothing about the tree changed — only which regex two
  different QA cycles happened to type.

This is the exact failure mode the ship-review already named at B-15 for the combined suite total
("Three agents reported three different `PASS` totals for one tree … counting-expression
divergence, not disagreement") — here isolated to the `integration` bucket and to the specific
regex boundary (`^PASS` vs `^PASS `) responsible.

## A. Per-script census at the pin (worktree HEAD `04d333d`, diffs from pin `48bbe7e` only by a
`feature.json` review_sha bump — confirmed `git diff --stat 48bbe7e HEAD`, 1 file, non-source)

All 29 scripts run individually from the worktree root, output captured to a variable (never
piped), exit status captured separately.

| script | exit | `^PASS ` (space) | `^PASS:` (colon) | `^FAIL` | `^ok ` |
|---|---|---|---|---|---|
| test-validate-digest.py | 0 | 0 | 0 | 0 | 106 |
| test-gh-sync.py | 0 | 0 | 0 | 0 | 273 |
| test-check-state.py | 0 | 0 | 0 | 0 | 145 |
| test-check-expertise.py | 0 | 0 | 0 | 0 | 32 |
| test-gen-decisions-index.py | 0 | 0 | 0 | 0 | 11 |
| test-bash-write-guard.py | 0 | 0 | 0 | 0 | 101 |
| test-check-domain.py | 0 | 0 | 0 | 0 | 203 |
| test-harness-yaml.py | 0 | 0 | 0 | 0 | 21 |
| test-upgrade-config.py | 0 | 0 | 0 | 0 | 10 |
| test-check-plan-routes.py | 0 | 82 | 0 | 0 | 6 |
| test-merge-settings.py | 0 | 0 | 0 | 0 | 22 |
| test-factory-integration.py | 0 | 0 | 0 | 0 | 131 |
| test-feature-worktree.py | 0 | 112 | 0 | 0 | 0 |
| test-expertise-merge.py | 0 | 39 | 0 | 0 | 0 |
| test-context-watch-cli.py | 0 | 0 | 0 | 0 | 10 |
| test-context-watch-hook.py | 0 | 0 | 0 | 0 | 22 |
| test-run-unit-tests-kinds.py | 0 | 0 | 0 | 0 | 23 |
| test-harness-merge.py | 0 | 19 | 0 | 0 | 0 |
| test-plan-merge.py | 0 | 110 | 0 | 0 | 0 |
| test-observations-merge.py | 0 | 33 | 0 | 0 | 0 |
| test-inflight-registry.py | 0 | 112 | 0 | 0 | 0 |
| test-dispatch-guard.py | 0 | 42 | 0 | 0 | 0 |
| test-merge-gitignore.py | 0 | 7 | 0 | 0 | 0 |
| **test-worktree-terminal.py** | 0 | 0 | **34** | 0 | 0 |
| **test-post-merge-sweep.py** | 0 | 0 | **52** | 0 | 0 |
| **test-hooks-install.py** | 0 | 0 | **29** | 0 | 0 |
| test-gh-close-gate.py | 0 | 0 | 0 | 0 | 48 |
| test-check-decision-anchors.py | 0 | 0 | 0 | 0 | 8 |
| test-check-decision-claims.py | 0 | 0 | 0 | 0 | 21 |

`^PASS ` column sums to **556**; `+ 29` runner markers (`PASS <script>.py`, one per script, all
exit 0) = **585**, matching cycle 1's reported integration PASS total exactly. `^PASS:` column
sums to **115**. `556 + 29 + 115 = 700`. `0` `FAIL` anywhere, `0` scripts missing, `0` non-zero
exits.

## B. Same census at the baseline tree (2557950), read-only

```
mkdir -p /tmp/feat38-base && git archive 2557950 | tar -x -C /tmp/feat38-base
```

`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays in `run-unit-tests.sh` are byte-identical to the pin
(confirmed by diff of the two array lines — expected, since neither the runner nor any test/source
file is in the delta, per §0).

**First attempt gave a false 6-`FAIL` reading on `test-check-decision-anchors.py`** — a methodology
artifact, not a tree difference: `check-decision-anchors.py` shells out to `git ls-files` against
its inherited cwd, and a plain `git archive | tar -x` extraction has no `.git`, so every subprocess
call failed with `returned non-zero exit status 128` and the checker exited 2 (misconfigured), not
1. Fixed by materializing a real (disposable, `/tmp`-local) git index over the extracted tree:
`git init -q && git add -A && git -c user.email=t@t -c user.name=t commit -q -m tmp`. Re-run: `0
FAIL`, `8 ok`, exit 0 — **identical to the pin.** Reported per rule 15 (record failures honestly)
even though the true cause was outside the diff under review.

The corrected per-script census at `/tmp/feat38-base` is **row-for-row identical to Table A above**
— same 29 scripts, same exit codes, same `^PASS `/`^PASS:`/`^FAIL`/`^ok ` counts per script,
including `34`/`52`/`29` for the three colon-convention scripts. `^PASS ` sum = 556 (+29 markers =
585); `^PASS:` sum = 115; combined `^PASS` (unanchored) = 700.

**Direct full-suite cross-check** (not just the per-script sum), `run-unit-tests.sh --kind
integration`, output captured to a file (never piped through `head`/`tail`), at both trees:

| tree | `grep -cE '^PASS '` | `grep -cE '^PASS:'` | `grep -cE '^PASS'` (unanchored) | `FAIL` | exit |
|---|---|---|---|---|---|
| pin (`04d333d`, = `48bbe7e` for source/tests) | 585 | 115 | **700** | 0 | 0 |
| baseline (`2557950`) | 585 | 115 | **700** | 0 | 0 |

**The baseline's `700` reproduces exactly — but only under the unanchored `^PASS` expression, the
same one that also matches the pin's `700`.** Under a single consistent expression the two trees
report identical numbers at every granularity. There is no drop to allocate under any one fixed
measurement; the appearance of a `700 → 585` drop came from comparing cycle 1's `^PASS ` figure
against an earlier cycle's `^PASS` figure for a different tree.

## C. Naming the "dropping" scripts

None. Every one of the 29 scripts has **identical** `PASS`/`FAIL`/`ok` line counts, by any single
grep convention, at both trees. The full 115 is the difference between two counting conventions
applied to the *same* set of three unchanged scripts, not a per-script regression:

| script | `^PASS:` count (both trees, identical) | share of 115 |
|---|---|---|
| test-post-merge-sweep.py | 52 | 45.2% |
| test-worktree-terminal.py | 34 | 29.6% |
| test-hooks-install.py | 29 | 25.2% |
| **total** | **115** | **100%** |

`52 + 34 + 29 = 115` — fully allocated, concentrated in exactly three scripts (not spread thinly
across many), and **none of the three is in the FEAT-38 delta** (§0: zero `.py` files touched).

## D. Why: mechanism is neither tree-dependent census volume nor a skip — it's the scripts' own
fixed sub-case-reporting convention, unrelated to both trees

`test-worktree-terminal.py`, `test-post-merge-sweep.py` all format their per-case result as
`print(f"{'PASS' if passed else 'FAIL'}: {name}" + ...)` (colon, `bin/test-worktree-terminal.py:814`,
`bin/test-post-merge-sweep.py:880`); `test-hooks-install.py` uses the same colon convention
(confirmed by direct run — 29 lines, 0 `FAIL`, exit 0, both trees). Contrast
`test-merge-gitignore.py:159`, `print("PASS %s" % name)` — no colon, space — which is why its 7
sub-cases *are* inside cycle 1's 585 and were never part of the 115.

This is **not** "it scans the tree" (the drop is not proportional to any counted entity — DECISIONS
citations, feature dirs, skill files — that differs between the two trees; §0 already established
`DECISIONS.md` is not in the delta and F below confirms its discovery volume is unchanged) and it
is **not** a short-circuit or skip (D and E below). It is a fixed, per-script string-formatting
choice, made once when each script was authored, invariant across both trees because neither
script's source changed between them.

## E. Guard against the silent-skip reading

For each of the three scripts, at both trees: exit `0`, `0` `FAIL`/`FAIL:` lines, and grepping their
own output for `skip|xfail|no such|not found` (case-insensitive) turns up only sub-case *names*
that are themselves about skip-handling correctness (e.g. `test-post-merge-sweep.py`: `"PASS: (g)
SKIP IS NOT SUCCESS: a feature whose ship exited 0 but printed 'gh-sync: SKIP' keeps its worktree
standing"`, `"PASS: (j)/(k) RED PROOF: a stub skipping every non-enumerable declared repo passes
(j) but fails (k)"`) — every one a `PASS:` line, none an actually-skipped case. `test-hooks-install.py`
has zero matches for those markers at all.

None of the three scripts prints an aggregate `N/N` self-count (they iterate `results` and print one
line per case, then `sys.exit(0 if all_ok else 1)` / `print(f"EXIT={0 if ok else 1}")`), so there is
no internal accounting line to compare — the per-line count (34/52/29, identical at both trees) *is*
the accounting, and it is self-consistent by construction (no case is silently dropped from the
`results` list without also dropping its `PASS:`/`FAIL:` print, and `0 FAIL:` at both trees confirms
none flipped).

Two scripts in the 29 that *do* print an aggregate line were checked for completeness and are
identical at both trees: `test-check-plan-routes.py` → `131/131 checks passed.`,
`test-observations-merge.py`-adjacent `test-inflight-registry.py` → `111/111 checks passed`,
`test-harness-merge.py` → `18/18 checks passed`. All three at the pin; re-run at
`/tmp/feat38-base` (post git-init fix) gave the identical `N/N` lines.

## F. Checker discovery volume, baseline vs pin

```
                              pin (48bbe7e-equiv)    baseline (2557950)
check-decision-anchors.py    examined 20 anchor(s), 0 failed   examined 20 anchor(s), 0 failed
check-decision-claims.py     examined 11 claim(s), 0 failed    examined 11 claim(s), 0 failed
```

Identical at both trees — expected and confirmed, since `.harness/harness/docs/DECISIONS.md` is not
in the delta (§0). Nothing moved here; no further investigation needed.

## Cleanup

`/tmp/feat38-base` and all `/tmp/pin_*`/`/tmp/base_*` scratch files removed.
`git -C <worktree> status --porcelain` shows only this artifact and cycle 1's (both untracked notes
files; no tracked file touched, no source/test edited, HEAD not moved, no worktree added/removed).

```yaml
VERDICT: PASS
DIGEST:
  headline: "115-line integration PASS gap fully allocated: it is a grep-pattern mismatch (`^PASS` unanchored vs `^PASS ` space-anchored) across two gate cycles, isolated to 3 unchanged scripts' colon (`PASS:`) sub-case convention — test-post-merge-sweep.py (52), test-worktree-terminal.py (34), test-hooks-install.py (29) — byte-identical PASS/FAIL/ok counts confirmed at both the pin and a read-only 2557950 archive; no coverage lost, no sub-case skipped."
  suite: pass
  suite_full: { exit: 0, fail: 0, pass: 1002, kind_drift: 0 }
  suite_unit: { exit: 0, fail: 0, pass: 417 }
  suite_integration: { exit: 0, fail: 0, pass: 585 }
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, required: false, state: not_applicable, cmd: none }
    - { kind: integration, required: false, state: not_applicable, cmd: none }
    - { kind: functional, required: false, state: not_applicable, signed: DEC-187 }
    - { kind: component, required: false, state: not_applicable, cmd: null }
    - { kind: ui, required: false, state: not_applicable, cmd: null }
    - { kind: eval, required: false, state: not_applicable, cmd: null }
  coverage_gaps: []
  sc_evidence: []
  cycles_used: 1
  open_questions:
    - { id: Q1, question: "run-unit-tests.sh's own printed PASS-line total is ambiguous across `^PASS`/`^PASS `/`^PASS:` conventions used by different test scripts (repo Expertise G-04 already flags this; ship-review B-15 independently hit it for the combined total). Should the runner print an unambiguous, single-convention aggregate (e.g. its own per-script marker count only, or a script-emitted `N passed` line normalized to one format) so future gate cycles stop producing apparent regressions that are really regex drift?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/qa-2026-08-29-11-validator-c2.md
```
