# Panel record repair — the goalcheck reader row (BUG-1309)

**Done. `panel.readers` now carries three rows and INV-32 no longer blocks this feature.** The
plan's substance is byte-for-byte what the operator signed: findings, ids, dispositions, rulings,
tasks, decisions and station are unchanged, verified against `HEAD` by parsed comparison.

## What changed — two lines

```yaml
  - reader: goalcheck
    status: ran
```

Appended to `panel.readers` in
`.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml`. Nothing else in the file was
authored by this run.

**Fields: `reader` and `status` only.** `set-panel`'s validator (`plan-merge.py:1017-1037`) checks
only that `readers` is a list — it never inspects a row. The consumer that does is
`check-state.sh:542-555`: it requires `persona` and `reason` **only on the `skipped` branch**
(`:548-552`); a `ran` row is accepted on `status` alone and no code path reads a `persona` there.
The template's `persona:`/`reason:` comments say "required when skipped"
(`templates/plan.yaml:70-74`), i.e. admitted-when-skipped, not admitted-on-`ran`. Unread fields on
a `ran` row are unverifiable assertion, so both were omitted.

## How it was written — no retyping

A throwaway script `yaml.safe_load`ed the plan, took `plan['panel']` as an object, appended the one
dict, and `safe_dump`ed that mapping alone to `/tmp` (deleted after). The seven summaries were
never re-keyed, so no content-hash id could rehash and no operator ruling could go stale — the
failure mode `panel.transcription_rule` in the plan itself warns about. Write route was
`plan-merge.py set-panel --file <plan.yaml> --value-file <tmp>`, which exited 0 with
`PANEL cycle 0 -> …` / `APPLIED …`. No Edit, no Write, no redirect touched plan.yaml.

## Read-back — every acceptance item

- Loads under `yaml.safe_load`. ✅
- `panel.readers`: should-not-exist/ran, scope/ran, goalcheck/ran — exactly three rows, each with
  keys `['reader','status']`. ✅
- `panel.findings`: seven, ids unchanged — `PF-f1684ee3…` med/T-05, `PF-1aa3b36c…` med/open,
  `PF-a882c9b8…` med/T-02, `PF-6030c547…` low/open, `PF-8bfef7ee…` low/open, `PF-23f51fd8…`
  low/open, `PF-da04a39f…` low/T-02 → 3 resolved, 4 open. ✅
- `last_run: 2026-09-06-01-validator`, `cycle: 0`, `transcription_rule` (518 chars) unchanged;
  `panel` minus `readers` compares equal to `HEAD`'s. ✅
- `approval`: `approved`, Mike Ruangutai, 2026-09-06, four rulings naming `PF-1aa3b36c…`,
  `PF-8bfef7ee…`, `PF-23f51fd8…`, `PF-6030c547…`. The diff against `HEAD` shows an approval hunk —
  that is the **pre-existing uncommitted signature** (`HEAD` still reads `status: pending`), not
  this run: `git diff` attributes only the two goalcheck lines to the panel hunk. ✅
- `tasks: 9`, `decisions: 9`, `status: plan` — all identical to `HEAD`. ✅

## Gate evidence

`check-state.sh` **from the worktree copy** (it resolves its root from its own location, so the
main-root copy grades the main root's tree and says nothing about this feature). Every BUG-1309
INV-32 line is now a `note`: three `disposition resolved`, four `operator accepted risk`. **No
blocking line, and no stale risk acceptance.** The script's overall exit 1 is other features'
findings plus a pre-existing unrelated note here — run dir `2026-09-06-02-validator` exists on
disk but `feature.json` does not record it (orphaned work, for whoever resumes).

## Open questions

None blocking. The orphaned run-dir note above is out of scope for this repair and is left for the
orchestrator.
