# Receipt — harness-backend-dev — T-11 (BUG-1309-mirror-build-entry)

## Verify, verbatim, from the worktree root

```
out=$(python3 tests/unit/test-feature-schema-build-entry.py && python3 tests/unit/test-gh-sync-build-entry.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL '; then exit 1; fi
for n in 02 03 04 06 08 09 10 11 12 14 19 23 24 25 27 28 29 30; do
  printf '%s\n' "$out" | grep -qF "PASS BE-$n " || exit 1
done
echo VERIFY-PASS
```

Cross-checked against plan.yaml's T-11 `verify:` block (lines 1681-1687) — identical. Intent
also cross-checked against plan.yaml's T-11 `intent:` block (lines 1688-1854) — identical to the
dispatch's quoted text. No mismatch.

Final output: `VERIFY-PASS`, exit status `0`. Both files individually also exit 0 with all 18
lines printed `PASS`.

## Files touched (exactly two, both new; zero production files, zero existing test files)

- `tests/unit/test-feature-schema-build-entry.py` (new)
- `tests/unit/test-gh-sync-build-entry.py` (new)

`git status --porcelain` over the worktree:

```
?? tests/unit/test-feature-schema-build-entry.py
?? tests/unit/test-gh-sync-build-entry.py
```

Nothing else appears. `.claude/skills/harness/bin/feature_schema.py` and
`.claude/skills/harness/bin/gh-sync.py` were hashed before and after the mutation probes
(md5sum `c0a51042366ecd224137cdcfaffd3ee5` and `150c0862925064e24923f643cf3b7fe1` respectively,
both unchanged) — the mutation probes ran entirely against mutated-copy files under `/tmp` and
against in-process monkeypatched module objects, never against the real files on disk, and the
throwaway `/tmp` scripts were deleted after the run.

## Per-case discrimination (DEC-217 Over clause) — one line per id

FILE 1 (`tests/unit/test-feature-schema-build-entry.py`), all against
`tests/integration/test-check-state.py:4622-4699`'s fixture (always writes plan.yaml via
`os.path.join`, always exactly one task, four stations only):

- BE-02: reaches the era short-circuit with a **trailing slash** on `feat_dir` — the integration
  fixture's `os.path.join` never produces one.
- BE-03: reaches the **except leg via an absent plan.yaml** — the integration fixture always
  writes a plan.yaml.
- BE-04: reaches the **except leg via an unparseable plan.yaml** — same reason, a valid
  plan.yaml is always written there.
- BE-06: reaches the **plan-status-done trigger** — not among the integration fixture's four
  stations (building/no-status, era+building, non-era+review, non-era+building+one-task-done).
- BE-08: reaches a **multi-task plan** (three tasks) in both directions — the integration
  fixture writes exactly one task, so it can never distinguish "scans the first task" from
  "scans every task".
- BE-09: reaches an **empty `tasks: []` list** — the integration fixture's one task is never
  absent.
- BE-10: observes **exact-match set membership** (`FEAT-01` in, `FEAT-01-suffix`/`feat-01`/
  `FEAT-90-e-green-thing` out) as a property of the set — no integration assertion inspects
  `BUILD_ENTRY_ERA_EXEMPT` membership directly at all.

FILE 2 (`tests/unit/test-gh-sync-build-entry.py`), against the full T-02/T-03/T-04 blocks in
`tests/integration/test-gh-sync.py`:

- BE-11: hands `gh-sync.py` an **out-of-enum `build_entry` value ("reopened")** — grep for
  "reopened" across `tests/integration` returns nothing; no integration fixture supplies one.
- BE-12: observes that `save_recorded` **drops the `build_entry` key** from the written document
  after that same out-of-enum normalization — same absent-fixture reason as BE-11.
- BE-14: observes the **recovery-required → opened upgrade direction** — `test-gh-sync.py:3481`
  proves only the no-downgrade direction (opened never regresses); no integration case starts at
  recovery-required and then successfully opens.
- BE-19: reaches `skip()` with **feature.json absent** — every integration fixture reaching
  `skip()` goes through `stage()`, which always writes a feature.json first.
- BE-23: calls `_build_entry_preflight` directly with an era directory carrying a **trailing
  slash** and a recorded recovery-required — `test-gh-sync.py:3623` passes recovery-required
  with no trailing slash, and T-12's own new integration case passes an *absent* outcome, not
  recovery-required.
- BE-24: observes **zero output at all** for a recorded `opened` — no integration assertion
  inspects stdout/stderr emptiness for this state, only exit code/side effects.
- BE-25: coerces `--parent` through `int()` when it **matches** the recorded parent (as a
  string, the way `main()` passes it) — `test-gh-sync.py:3559` only exercises the mismatch case
  (999 against 1289).
- BE-27: observes conflict is `None` when **no parent is recorded at all** (second leg) — no
  integration case passes `--parent` to a feature with no recorded parent.
- BE-28: observes the exact **adoption-line pair** when both milestone and parent are recorded —
  `test-gh-sync.py:3540` asserts only the call count for that state, never the returned lines.
- BE-29: observes the exact **two-line `creates` list** when neither is recorded —
  `test-gh-sync.py:3524` asserts the resulting record, never the exact list.
- BE-30: observes the exact **one-line `creates` list** for a given `--parent`, plus the
  **zero-task-mention property across all four adoption states** — the integration bed grades
  this state at one point (a record), never as an exact list, and never sweeps all four states
  for the SC-05 no-task-sub-issues property.

## Mutation-to-reddened-ids table

Every mutation ran as a throwaway `/tmp` script (deleted after the run): FILE 1 mutations loaded
a **mutated copy** of `feature_schema.py`'s full source into a `/tmp` file via `importlib`
(`test-validate-feature-json.py:665-684`'s shape); FILE 2 mutations **monkeypatched one
collaborator at a time** on a freshly `importlib`-loaded, in-process `gh-sync.py` module object.
The real files on disk were never touched (hashes above are unchanged before/after). One
mutation at a time; baseline (unmutated) ran fully green in both scripts before any mutation.

FILE 1 — feature_schema.py:

| mutation | change | reddened |
|---|---|---|
| A | drop `.rstrip("/")` in the era-membership check | BE-02 |
| B | except-leg `return "recover-terminal"` → `return "open"` | BE-03, BE-04 |
| C | status trigger set `{"review", "done"}` → `{"review"}` | BE-06 |
| D | `any()` over every task → check only `tasks[0]` | BE-08 |
| E | `plan.get("tasks") or []` → `... or [{"status": "done"}]` | BE-09 |
| F | inject `"FEAT-01-suffix"`, `"feat-01"` into `BUILD_ENTRY_ERA_EXEMPT` | BE-10 |

All seven ids reddened by exactly one targeted mutation each, none by more than the mutations
listed; no id is vacuous.

FILE 2 — gh-sync.py:

| mutation | change | reddened |
|---|---|---|
| 11/12 | `load_recorded` skips the closed-enum normalization | BE-11, BE-12 |
| 14 | `record_build_entry`'s no-downgrade guard also blocks the recovery-required→opened upgrade | BE-14 |
| 19 | `skip()` drops the `os.path.isfile(feature.json)` conjunct | BE-19 |
| 23 | `_build_entry_preflight` reverts to `os.path.basename(feat_dir)` (T-12's own reverted line) | BE-23 |
| 24 | `_build_entry_preflight` prints an extra line when `entry == "opened"` | BE-24 |
| 25 | `_recover_terminal_conflict` compares `str(parent_arg) == rec["parent"]` (drops `int()`) | BE-25 |
| 27 | `_recover_terminal_conflict`'s guard drops the "no parent recorded" leg | BE-27 |
| 28 | `_recover_terminal_report` drops the recorded-milestone adoption line | BE-28 |
| 29 | `_recover_terminal_report` typos "create the milestone" | BE-29 |
| 30 | `_recover_terminal_report`'s given-`--parent` line adds the word "task" | BE-30 |

Mutations 23 and 24 both exercise `_build_entry_preflight` and were each checked against both
BE-23 and BE-24: 23 reddens only BE-23 (BE-24 stays green, since the reverted rstrip is a no-op
without a trailing slash), 24 reddens only BE-24 (BE-23's own state is untouched by the added
"opened" branch). Likewise mutations 25/27 were each checked against both BE-25 and BE-27, and
28/29/30 were each checked against all three of BE-28/BE-29/BE-30 — cross-checking every
mutation against every case in its function, not only its target, is what shows isolation rather
than assuming it. All eleven ids reddened; none is vacuous.

Combined with FILE 1's table, all eighteen ids (02 03 04 06 08 09 10 11 12 14 19 23 24 25 27 28
29 30) are proven non-vacuous.

## Notes

- BE-23 (`_build_entry_preflight` on an era-exempt trailing-slash directory) is expected to pass
  because T-12's fix is already landed (`gh-sync.py:1360` reads
  `os.path.basename(feat_dir.rstrip("/"))`, verified by reading the file directly before writing
  any test). It passed on the first run — no RED phase, as the task's own discrimination-proof
  clause directs for a dependency already satisfied.
- No production code was read, written, or run against — only imported in-process for assertion
  and, for the mutation probes, read into `/tmp` copies or monkeypatched on in-process module
  objects.
- No case from the eleven struck ids (BE-01, BE-05, BE-07, BE-13, BE-15, BE-16, BE-17, BE-18,
  BE-20, BE-21, BE-22, BE-26) was written or reconsidered; none of the eighteen surviving cases
  was found, while writing, to duplicate an assertion in any of the five named integration
  files — no finding to report there.
