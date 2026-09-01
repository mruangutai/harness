# Receipt — harness-dev-ops — T-08 — run c1

## What landed

`.claude/skills/harness/bin/test-gen-decisions-index.py` (only file changed): added
`QUARANTINE_DEC = "DEC-210"`, module-level `_dec_region(text, dec)` (bounded both
sides, reuses the file's own fence-toggle rule), and three tests —
`test_dec_210_entry_names_both_enforcement_points`,
`test_dec_210_entry_states_the_bash_write_route_for_plan_yaml`,
`test_dec_210_index_row_names_the_compatibility_host_in_the_ruling` — all three
registered in `TESTS`. No other line touched; `plan.yaml`/`DECISIONS.md`/`DECISIONS-INDEX.md`
untouched by me (plan.yaml's dirty `status: building` in the worktree is the
orchestrator's own station update, confirmed via `git diff`, not mine).

## Final verify (verbatim command from plan, cross-checked byte-for-byte against `plan.yaml`)

```
$ grep -q 'def test_dec_210_entry_names_both_enforcement_points' .agents/skills/harness/bin/test-gen-decisions-index.py &&
  grep -q 'def test_dec_210_entry_states_the_bash_write_route_for_plan_yaml' .agents/skills/harness/bin/test-gen-decisions-index.py &&
  grep -q 'def test_dec_210_index_row_names_the_compatibility_host_in_the_ruling' .agents/skills/harness/bin/test-gen-decisions-index.py &&
  python3 .agents/skills/harness/bin/test-gen-decisions-index.py
ok - test_row_per_distinct_dec_matches_authority
... (9 more existing oks) ...
ok - test_dec_210_entry_names_both_enforcement_points
ok - test_dec_210_entry_states_the_bash_write_route_for_plan_yaml
ok - test_dec_210_index_row_names_the_compatibility_host_in_the_ruling
$ echo $?   # 0, 14 ok lines total
```

## Discrimination probes (rig: `mktemp -d` tree with copied `DECISIONS.md`/`DECISIONS-INDEX.md`/
test script; `GEN_DECISIONS_INDEX_BIN` and `PYTHONPATH` pointed at the real generator/`harness_boundary`
by absolute path; control run first confirmed 14 ok, matching live). Rig deleted after; worktree and
main-checkout status confirmed clean of it.

**Probe A — delete `plan-sign-gate.sh` from the DEC-210 region only:**
```
FAIL - test_dec_210_entry_names_both_enforcement_points: 'plan-sign-gate.sh' not found in the DEC-210 region of <rig>/.harness/harness/docs/DECISIONS.md
```
Test 1 red on that clause alone; tests 2 and 3 stayed `ok`.

**Probe B — split the plan.yaml/plan-merge.py sentence:** DEC-210 states this fact TWICE
(line 6539's "Adoption of `plan.yaml` ... put behind `plan-merge.py`." and line 6519-6520's
"**`plan.yaml` is covered by...** Its only write route is `plan-merge.py`..." — the latter's
`.**` immediately after the period, with no space, keeps my period+space split from cutting there,
so it reads as one chunk). Splitting only the first sentence left the test green (the second still
satisfied the clause) — a real finding, not a bug in the probe: the entry genuinely states the fact
twice. Splitting BOTH:
```
FAIL - test_dec_210_entry_states_the_bash_write_route_for_plan_yaml: no single sentence in the DEC-210 region of <rig>/.harness/harness/docs/DECISIONS.md names both 'plan.yaml' and 'plan-merge.py'
```
Test 2 red on the joint-sentence clause; the `Bash` whole-word clause stayed green (failure was on
the second check, not the first). Tests 1 and 3 stayed `ok`.

**Probe C1 — strip `Claude Code` from the index row's ruling half (group 2):**
```
FAIL - test_dec_210_index_row_names_the_compatibility_host_in_the_ruling: 'Claude Code' not found in the ruling half of the DEC-210 row in <rig>/.harness/harness/docs/DECISIONS-INDEX.md
```

**Probe C2 — move `Claude Code` into the row's generated left half only (a synthetic tag), leaving
the ruling stripped:**
```
FAIL - test_dec_210_index_row_names_the_compatibility_host_in_the_ruling: 'Claude Code' not found in the ruling half of the DEC-210 row in <rig>/.harness/harness/docs/DECISIONS-INDEX.md
```
Both C1 and C2 red on test 3 as required — a whole-row search would have missed C2.

**Probe D — remove the `## DEC-210` heading entirely:**
```
FAIL - test_dec_210_entry_names_both_enforcement_points: no '## DEC-210' heading found in <rig>/.harness/harness/docs/DECISIONS.md
FAIL - test_dec_210_entry_states_the_bash_write_route_for_plan_yaml: no '## DEC-210' heading found in <rig>/.harness/harness/docs/DECISIONS.md
```
Both region tests FAIL LOUDLY (no skip). Test 3 stayed `ok` — it reads `REAL_INDEX` independently
of the heading, by design; the DECISIONS-INDEX.md row was untouched in this probe.

Every probe's collateral state (unrelated existing tests) matched expectation; in C1/C2
`test_committed_index_matches_a_fresh_regeneration` also correctly reddened as a side effect of
mutating the index without regenerating — expected, not investigated further (out of scope).

## git status after edits

Worktree (`git -C <worktree> status --porcelain`):
```
 M .claude/skills/harness/bin/test-gen-decisions-index.py
 M .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/plan.yaml
```
The `plan.yaml` line is the orchestrator's own station bump (`status: ready` → `status: building`
on T-08), confirmed via `git diff` — not written by me, and I wrote no other file.

Main checkout (`git -C /Users/molchairuangutai/GitHub/harness status --porcelain`): dirty, but with
changes unrelated to this task (`run-unit-tests.sh`, `harness.json`, several other features' notes
and logs) — pre-existing from other concurrent work in that checkout, not touched by me; I performed
zero writes there. The rig lived entirely under `mktemp -d` (outside both trees) and was deleted.
