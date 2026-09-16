# REUSE angle — BUG-1290 B-3 fixture diff (`tests/unit/test-factory-claim.py`)

**BLUF: declined. No reuse violation found.** Every new call in the diff goes through helpers
and constants the file already defines and uses dozens of times elsewhere; nothing is
re-implemented.

## Commands run

```
git -C <worktree> diff -- tests/unit/test-factory-claim.py
git -C <worktree> diff -U6 -- tests/unit/test-factory-claim.py
grep -n "SEG_FEATURE" tests/unit/test-factory-claim.py
```
(plus `grep`/`glob` tool calls listed below — no shell `grep`/`rg` used for the search itself.)

## What I read looking for an existing spelling

- `tests/unit/test-factory-claim.py` in full for helper defs: `write_yaml` (L274),
  `write_json` (L281), `issue_data` (L301), `task_dict` (L311), `plan_dict` (L327), and the
  `SEG_FEATURE` constant (L71).
- Every `rec.issue_data[N] = issue_data(...)` registration site in the same file (~35 call
  sites from L448 through L1100) to establish the file's existing idiom for registering a
  mock issue.
- `tests/**/*.py` glob to confirm whether a shared test-helper module exists across
  `tests/unit/` and `tests/integration/` — none does; each unit test file is self-contained
  with its own inline helper defs (confirmed by the directory listing; no `helpers.py` /
  `fixtures.py` under `tests/`).
- `tests/integration/test-factory-integration.py` for literal reuse of `T-77`/`T-88`/`T-99`,
  `850`, `954` — no matches.
- Whole-tree `grep` for `T-88` / `850` / `954` — the only `T-88` hit outside the diff itself is
  an unrelated `T-88` feature-dir name in `test-feature-json-merge.py` (a different domain,
  coincidental digits, not a shared constant).

## Findings, five-part form

None qualify as findings. What was checked and why each clears:

1. **`write_json`/`write_yaml` calls** (L375, L382 area) — file, line: already-defined helpers
   at L274/L281, called the same way at dozens of other sites in this file. The diff changes
   only the *dict payload* passed in, not the calling convention. No restatement.
2. **`plan_dict(SEG_FEATURE, [task_dict(...)])` calls** (L377, L382) — `SEG_FEATURE` is a
   module-level constant at L71, already reused at L1169/L1195/L1198 for the same segment
   feature id; the diff's new `depends_on=["T-88"]` / `depends_on=["T-99"]` arguments use the
   existing `task_dict(tid, depends_on=None, ...)` signature (L311) as designed. No new
   parallel constant introduced.
3. **`rec.issue_data[954] = issue_data(954, "T-99 do the thing", state="CLOSED")`** — matches
   the file's established idiom (identical shape at, e.g., L674, L730, L1059, L1100): direct
   dict assignment via the existing `issue_data()` factory. This is not a duplicate
   registration path; it is the only registration mechanism the file has, used correctly.
4. **New literals `850`, `954`, `T-77`, `T-88`, `T-99`** — none collide with an existing named
   constant. `T-77`/`T-88`/`T-99` are task ids scoped to this fixture's local DAG, not module
   constants elsewhere; `850`/`954` are arbitrary mock issue numbers, a pattern the file
   already uses freely (`700`, `701`, `900`s, `940`, etc. — no numbering scheme to violate).
   No lockstep-edit risk: these numbers are used within this single test file, not mirrored in
   `test-factory-integration.py` or elsewhere.
5. **Shared helper module** — checked via `glob tests/**/*.py` and the integration test
   directory: no `tests/helpers.py`, no `tests/fixtures/` shared module used by
   `test-factory-claim.py`. Each unit test file, including this one, is deliberately
   self-contained; this is the tree's existing convention, not something this diff should
   change.

## Trap-rule note (batch context)

Per the dispatch's trap warning, I did not propose collapsing the two segment `write_json`/
`write_yaml` pairs into a parameterised helper — their differing dep ids (`T-88` vs `T-99`) and
differing issue-map contents are exactly what makes case 5b discriminate, and REUSE found no
independent existing helper that already does this parameterised job, so there is nothing to
point to as a duplicate. Recording per the trap rule rather than silently omitting it.

## Post-pass tree state (2026-09-06-04-eng)

`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root status --porcelain`
```
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/observations/harness-backend-dev.md
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b3.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/qa-2026-09-06-02-validator.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/qa-2026-09-06-03-validator.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-01-eng-b3.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-04-eng-altitude.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-04-eng-simplification.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-01-eng-b3-remeasure.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-04-eng-efficiency.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-04-eng-reuse.md
```

`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root diff --stat -- tests/unit/test-factory-claim.py`
```
 tests/unit/test-factory-claim.py | 23 ++++++++++++++---------
 1 file changed, 14 insertions(+), 9 deletions(-)
```

`cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && python3 tests/unit/test-factory-claim.py | tail -3`
```
ok    BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py

124/124 checks passed.
```

**Verdicts:**
1. Status confined to `tests/` and the feature directory and nothing else — **holds.** Every
   modified/untracked path is either `tests/unit/test-factory-claim.py` or under
   `.harness/harness/features/BUG-1290-factory-claim-repo-root/`; no other path appears.
2. `diff --stat` still shows `+14/-9` on that one test file — **holds**, exactly
   `14 insertions(+), 9 deletions(-)`, matching the pre-pass figure; no angle reader touched
   the subject file.
3. Suite prints `124/124 checks passed` — **holds**, verbatim.
