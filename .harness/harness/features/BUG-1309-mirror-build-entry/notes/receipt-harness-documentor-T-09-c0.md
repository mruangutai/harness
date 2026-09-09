# Receipt — harness-documentor — BUG-1309 T-09 — c0

**DEC-220 is written and the index carries its row with a hand-written ruling. The task's
`verify:` string as signed cannot pass: it calls `gen-decisions-index.py --check`, a flag the
generator does not implement and rejects at exit 2.** Every semantic clause of that verify passes
under the generator's own documented drift check. The plan's verify string needs amending by a tier
that may edit `plan.yaml`; nothing about the documentation work is outstanding.

## What changed — exactly two files, pure addition, 0 deletions

- `.harness/harness/docs/DECISIONS.md` — one hunk, `@@ -6977,0 +6978,33 @@`. `## DEC-220 — Build
  entry opens the mirror and leaves a local receipt; Ship is post-merge terminal finalization only`
  appended at EOF in numeric order.
- `.harness/harness/docs/DECISIONS-INDEX.md` — one hunk, `@@ -219,0 +220 @@`. **One row added, no
  other row changed.** Appending at EOF left every existing `@line` anchor stable, so regeneration
  produced no churn (documentor P-02). The generator emitted `⚠ RULING PENDING`; the ` :: ` tail was
  hand-written after, and `grep -c "RULING PENDING"` is now `0`.

Nothing else was touched. `merge-gate.py`, `test-check-state.py` and `test-post-merge-sweep.py` —
held by the main session — were not read for edit and are not in the diff. No commit; HEAD is
`7519cb74`.

## Number allocation — confirmed free at the files, and on the integration branch

`grep "^## DEC-2"` topped out at `## DEC-219 @6946`, and the index's last row was `DEC-219 @6946`,
so the index was in sync before the edit. `git show main:.harness/harness/docs/DECISIONS.md` also
tops out at DEC-219, so 220 is free on the integration branch too, not merely on this branch
(documentor P-02 — a branch-local ceiling can hide numbers merged since the cut).

## Verification

The signed clause, run verbatim from the worktree root, **fails before reaching any assertion**:

```
gen-decisions-index: unrecognized argument(s): --check. Wrote nothing.
... There is no --check: to check for drift without writing, pipe the read-only mode into
diff — `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`.
exit=2
```

The generator's own help text names the substitute. Same three assertions, drift check swapped for
the documented form — final line `VERIFY-PASS`:

```
python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md \
  && grep -q "DEC-220" .harness/harness/docs/DECISIONS-INDEX.md \
  && python3 tests/integration/test-check-decision-anchors.py && echo VERIFY-PASS
→ ok - test_live_authority_anchors_all_resolve
  VERIFY-PASS
```

`tests/integration/test-gen-decisions-index.py` also passes at exit 0, including
`test_committed_index_matches_a_fresh_regeneration` and
`test_committed_index_is_complete_and_within_budget` — the only place the ruling's length band is
asserted (documentor G-03). The new ruling is 24 words.

## The entry's claims were checked against the landed code, not transcribed

The intent is signed prose, so its naming stands; each factual claim was still confirmed at the
implementation before being written (documentor P-07):

- outcome vocabulary `opened | recovery-required | not-applicable | recovered-terminal` —
  `gh-sync.py:625-626`; absence is the fifth state, `feature.json github.build_entry` unset.
- Build refusal on absence, notice-and-proceed on `recovery-required` — `gh-sync.py:1357-1389`,
  called from `cmd_start_task` at `gh-sync.py:1452`.
- merge gated by the registered PreToolUse Bash gate — `.claude/settings.json:48`.
- partial write / caller error record nothing — `_NO_RECORD` at `gh-sync.py:289`.
- `recover-terminal --yes` records `recovered-terminal` as its last statement —
  `gh-sync.py:1277-1323`.
- sweep keeps the worktree — `post-merge-sweep.sh:222-231`.
- INV-37 — `check-state.sh:1983-2018`.

**One correction to the intent's framing, made deliberately in the entry.** The intent attributes
the frozen era-exempt set to INV-37 alone. `feature_schema.BUILD_ENTRY_ERA_EXEMPT` in fact bounds
*three* things: INV-37, the Build refusal (`gh-sync.py:1361`) and the merge refusal
(`gh-sync.py:1380`). The entry states the wider, true scope. This narrows nothing the plan decided;
it records the mechanism as built.

## Open

- **Q1 (blocks acceptance, not the work): T-09's `verify:` in `plan.yaml` names a nonexistent
  flag.** Replace `gen-decisions-index.py --check` with
  `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`. I may not
  edit `plan.yaml`. No other BUG-1309 task carries the string — I grepped the feature tree.
- **Q2 (non-blocking, harness defect): this is the fourth feature to ship the same broken clause.**
  `FEAT-19-central-product-config/observations/harness-pm.md:13`,
  `FEAT-32-concurrent-write-merge/notes/handoff-build.md:14` (two occurrences, `plan.yaml:1587`
  and `:2219`), `FEAT-37-lead-stop-and-wake/plan.yaml:794`, and now this one. Four pms independently
  wrote `--check` because every other harness checker spells it that way and this one script alone
  does not. Another receipt will not stop the fifth. The fix is upstream and outside T-09's two
  declared files: teach `gen-decisions-index.py` to accept `--check` as an alias for its documented
  drift check, or lint `verify:` strings against each tool's `--help`.
