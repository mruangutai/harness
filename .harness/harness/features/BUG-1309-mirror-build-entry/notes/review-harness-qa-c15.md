# QA gate — c15 — BUG-1309-mirror-build-entry — e374c9a2

**matrix_ok: true.** All 5 required/standing suites green at the pin; the delta's own
discrimination proof holds full-pipeline; two coverage gaps remain (advisory, not gating this
cycle — DEC-174 reserves `tests/**` to the operator).

## Matrix requirement (from `.harness/harness.json`, `bugfix` entry)
`always: []`; `when`: `unit` if `touches_runtime_code` (**fires** — `merge-gate.py` is runtime
Python) → **unit required**. `integration` if `fix_confined_to_tests_and_contract_docs` (**does
not fire** — the delta edits runtime code, not only tests/docs) → integration not obligated by
this predicate. `__bug_class__` if `match_bug_class` — repo Expertise G-08: no bug-class taxonomy
entry resolves for any diff yet, unresolvable placeholder, contributes nothing.
**Strict floor: `unit` only.** Per dispatch instruction and the standing bed, `integration` was
run anyway as the suite directly exercising this fix; it is reported as run, not as
matrix-required.

## Suite results (`env -u HARNESS_AGENT_TYPE python3 <path>`, from worktree root)
| suite | kind | exit | cases |
|---|---|---|---|
| tests/integration/test-merge-gate.py | integration (bed) | 0 | 27 `ok`, 0 FAIL |
| tests/integration/test-gh-sync.py | integration (bed) | 0 | 323 `ok`, 0 FAIL |
| tests/unit/test-gh-sync-build-entry.py | unit (required) | 0 | 11 `PASS`, 0 FAIL |
| tests/unit/test-feature-schema-build-entry.py | unit (required) | 0 | 7 `PASS`, 0 FAIL |
| tests/unit/test-omp-hooks.py | unit (required) | 0 | 56 pass / 0 fail (bun test) |

None of the five exits with a load/import/collection error; all real named-case runs. `unit`
required by the matrix: **satisfied** (test-gh-sync-build-entry, test-feature-schema-build-entry,
test-omp-hooks all pass, all touch runtime code adjacent to the delta's domain).
`integration`: not matrix-required this cycle, but exercised and green.

## Adequacy Q1 — do the three added cases discriminate?
**Yes, proven full-pipeline, not just at the parser function.** Built a disposable copy of
`.claude/skills/harness/bin/` at `/tmp/old-parser-bin/` with `merge-gate.py` replaced by
`git show da6da610:.claude/skills/harness/bin/merge-gate.py`, wrapper (`merge-gate.sh`) untouched.
Ran the real fixture (non-era feature, `build_entry` absent → must DENY) through both
`merge-gate.sh` copies for all three added commands:

| command | NEW (e374c9a2) | OLD (da6da610) |
|---|---|---|
| `git merge --no-ff feature/test` | `deny` (build_entry=absent reason) | `None` — no permission decision (silent allow) |
| `git merge --squash feature/test` | `deny` | `None` |
| `git merge -m message feature/test` | `deny` | `None` |

Also confirmed at the `git_merge()` function level directly: OLD returns `('git', '--no-ff')` /
`('git', '--squash')` / `('git', '-m')` (the option token itself, never resolving to a real
branch); NEW returns `('git', 'feature/test')` in all three. All three cases fail-red against the
old parser and pass against the new — they discriminate exactly the defect the fix targets, not a
vacuous pin.

## Adequacy Q2 — fixture coverage for named shapes (not covered, none added — read-only per DEC-174)
Ran each shape directly against the new `git_merge()` to characterize behavior; no fixture in the
bed exercises any of them:

- **`git merge --abort`** — **not covered.** `git_merge` returns `('git', None)`; no test asserts
  this yields no-permission-decision-on-abort (plausible-correct today, unpinned).
- **`-F <file>`** (value-taking `merge` option, absent from `merge_values`) — **not covered, and
  live defect of the same class the fix exists to close.** `git merge -F msgfile feature/test` →
  `git_merge` returns `('git', 'msgfile')` — the file argument, not the branch — silently
  reproducing the exact fail-open shape VP-01 fixed for `-m`. `--cleanup <mode>` behaves
  identically: `git merge --cleanup scissors feature/test` → `('git', 'scissors')`.
- **`--attr-source <tree>`** (value-taking GLOBAL option, absent from `global_values`) — **not
  covered, and a live defect strictly worse than the branch-substitution case.**
  `git --attr-source refs/heads/attrs merge --no-ff feature/test` → `git_merge` returns `None`
  outright: the unrecognized global option is skipped by only one index instead of two, so the
  next token (`refs/heads/attrs`) is compared against `"merge"`, fails the match, and the whole
  command evades merge detection — total bypass, not merely a wrong branch.

These are carried-forward instances of VP-02 (the value-taking sets are non-exhaustive against
real git option surfaces) and are real, current, reproduced-today gaps, not history. Not authored
here per the read-only mandate — reported for a dev cycle.

## VERDICT basis
`matrix_ok: true` — the strict matrix floor (`unit`) is satisfied with real named passing cases,
and the standing integration bed run alongside it is green with a proven-discriminating delta.
Two advisory findings (fixture gaps for `-F`/`--cleanup`/`--attr-source`) are reasoned-and-measured
live defects of the same silent-allow/total-bypass class the fix targets, but they sit outside this
cycle's diff and outside a gate-only dispatch's authoring mandate.
