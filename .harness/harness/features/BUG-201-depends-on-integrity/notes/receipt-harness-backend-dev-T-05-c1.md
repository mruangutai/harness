# Receipt — harness-backend-dev — T-05 (BUG-201-depends-on-integrity)

## Task

T-05, `depends_on: [T-03]` (done). Files touched (exactly the two named): `tests/unit/test-factory-claim.py`, `tests/integration/test-gh-sync.py`. No production file touched — confirmed via `git status --porcelain` in the worktree, and independently the main checkout was checked clean before and after every write (one accidental leak into the main checkout was caught and reverted mid-task; see Incident below).

## `verify:` (verbatim from plan.yaml T-05)

```
python3 tests/unit/test-factory-claim.py &&
python3 tests/integration/test-gh-sync.py
```

Run as `env -u HARNESS_AGENT_TYPE python3 <path>` from the worktree root, per the dispatch. **Both commands FAIL today**, exactly as T-05's intent requires (T-06, a separate later dispatch, is what turns them green).

## RED run 1 — `tests/unit/test-factory-claim.py` (exit 1)

```
FAIL  (Da) blocker-gate reason a caller receives names BOTH T-02 and T-99
        issue #780 carries a feature: label that resolves, but no plan could be read at /var/folders/.../.harness/widget/features/FEAT-201-dangling/plan.yaml - the feature directory or its plan.yaml is missing or unparseable
FAIL  (Da) blocker-gate reason no longer carries the missing-or-unparseable wording (factory_claim.py:193-196)
        issue #780 carries a feature: label that resolves, but no plan could be read at /var/folders/.../.harness/widget/features/FEAT-201-dangling/plan.yaml - the feature directory or its plan.yaml is missing or unparseable

2 of 133 FAILING.
```

Both FAILs are case (a) — the diagnosis. Today `factory_claim.py`'s `_BlockerCache._plan` catches `PlanSchemaError` (a `YamlParseError` subclass) as a generic parse failure and reports the wrong cause; both assertions on the caller-received reason text fail for exactly that reason. Everything else in the file is green, in the SAME run:

- `(D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)` — **ok**
- `(D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, present)` — **ok**
- `(Db)` (paired correct plan, gate is `None`, exactly (B3)'s verdict) — **ok**
- `(Dc)` (not a crash, poll continues, #790 still claimed) — **ok**, including "no traceback"

## RED run 2 — `tests/integration/test-gh-sync.py` (exit 1)

```
FAIL  (d) start-task over the dangling fixture: exit status EXACTLY 2
      gh-sync: no station follows from the plan for #5501 (T-02) — card not moved

FAIL  (d) exactly one stderr line names BOTH T-02 and T-99
      gh-sync: no station follows from the plan for #5501 (T-02) — card not moved

FAIL  (f) stderr ALSO carries a line naming BOTH T-02 and T-99, additive to the above
      (empty)
```

Case (d) — `_projected_for` — exits 0 today (not 2) and prints the pre-existing silent "no station follows from the plan" line, never naming T-02/T-99: the exact swallow this task exists to red. Case (f) — `_status_plan_doc` — is red only on the additive new line; the two "unchanged from today" assertions pass in the SAME run:

- `(D0) load_plan RAISES on the dangling fixture` / `RETURNS on the paired legal fixture` — **ok**
- `(d) no Traceback anywhere in the output` — **ok**
- `(e)` start-task over the LEGAL fixture (paired allow, mirrors the file's plain `featN` start-task success case): exits 0, writes T-02's own card to Building — **ok**
- `(f) status Ready over the dangling fixture: exit status UNCHANGED from today (2)` — **ok**
- `(f) the existing refusal line is UNCHANGED from today (captured pair, additive)` — **ok** (captured first: today's pair is exit 2 + "station ready refused — plan.yaml's approval.status is not 'approved'"; asserted as still true in the same run the new-line assertion reddens on)
- `(g)` status Ready over the LEGAL fixture, approval approved (paired allow, mirrors the file's `featSt2` case): exits 0, both recorded sub-issues moved to Ready — **ok**

## Acceptance checklist

1. Both `verify:` commands observed FAILING — literal FAIL lines above, both exit 1.
2. In the SAME red runs, each file's `load_plan` raises-on-dangling / returns-on-legal assertions (`D0`) **PASS** — shown above for both files.
3. Case (d) drives `start-task`, never `status Ready` — confirmed (`run(["start-task", featDd, "T-02"], ...)`).
4. Case (f) captures today's exit code (2) and refusal line (`"station ready refused — plan.yaml's approval.status is not 'approved'"`) as its own passing assertions, and the new T-02/T-99 line is asserted additively (a separate, currently-red assertion) — never a replacement.
5. Paired-allow mirrors, named:
   - (b) mirrors (B3) "all blockers closed: candidate IS claimed" → gate is `None`.
   - (e) mirrors the file's plain `featN` start-task success case (`--id ITEM_<n> --single-select-option-id OPT_BUILDING`).
   - (g) mirrors the file's `featSt2` "status Ready … writes exactly the … sub-issues" case.
6. No case for self-dependency, cycles, or task ordering — none added.
7. Only the two `files:` are modified (`git status --porcelain` in the worktree shows exactly `tests/unit/test-factory-claim.py` and `tests/integration/test-gh-sync.py`, plus a pre-existing, not-mine `feature.json` change). No production file touched.
8. This receipt.
9. Nothing committed; no formatter/linter/project-wide suite run.

## Incident (self-caught, corrected)

Two edit calls used the file's path relative to the worktree root inside the edit tool's `[PATH#TAG]` header instead of the full absolute worktree path. Per the dispatch's own documented hazard, a relative path resolves against the process cwd (the MAIN checkout), and both edits landed there instead of in the worktree. Caught immediately via `git status --porcelain` in the main checkout before any further work; reverted with `git checkout -- tests/unit/test-factory-claim.py` in the main checkout (confirmed clean afterward), then redone correctly against the worktree's absolute path. The main checkout was re-verified clean after every subsequent edit in this task. No trace of the leak remains.

## Fixtures added (test-only, no production changes)

- `tests/unit/test-factory-claim.py`: `FEAT_DANGLING` / `FEAT_DANGLING_LEGAL`, a two-task plan pair (`T-01`, `T-02`) under REPO's own "widget" segment — `T-02 depends_on [T-99]` (T-99 absent from the plan, dangling) and `T-02 depends_on [T-01]` (present, legal) respectively. Section `D` (cases Da/Db/Dc) added after the existing `B7` case, before section `X`.
- `tests/integration/test-gh-sync.py`: `write_dangling_plan_yaml` / `stage_depends_on`, following `write_plan_yaml` / `stage_station`'s own shape (block-YAML, every `REQUIRED_TASK_FIELDS` key present including an explicit `status:` per task so `plan-merge.py set-task-station` can locate and update it). New section (D0, d, e, f, g) appended at the end of the file, before the final `sys.exit`.
