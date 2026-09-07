# research — BUG-151 — panel goalcheck reader recorded (c1)

**BLUF.** `panel.readers` now records all three readers INV-32 expects. The `goalcheck` reader —
the plan-phase product segment that ran in cycle 0 — was appended as `persona: harness-pm`,
`status: ran`, `verdict: YES-WITH-FINDINGS`. Nothing else in `plan.yaml` changed: both finding ids
are character-identical, `approval:` is still `pending`, `status:` still `plan`, tasks still
`T-01, T-02`, decisions still `D-01, D-02`. INV-32 would have emitted a `bad` for the missing
reader the moment the operator signed; it no longer can.

## Why the entry has no artifact field

The reader-entry schema has none. `plan-merge.py:_load_panel_value` (line 1011) validates only
`last_run: str`, `cycle: int`, `readers: list`, `findings: list`; `check-state.sh:534-555` reads
only `reader`, `status`, and — for `skipped` — `persona` and `reason`. `verdict` is carried
because both sibling entries carry it. The segment's artifact is recorded here instead:
`notes/research-BUG-151-goalcheck-plan-c0.md` (YES-WITH-FINDINGS, two must_fix items, both since
applied).

## Finding ids — before and after, side by side

| # | before | after |
|---|---|---|
| 1 | `PF-cf17fd813d058340727a00b9a33886cd` (med, resolved, `resolved_by: T-01`) | `PF-cf17fd813d058340727a00b9a33886cd` (med, resolved, `resolved_by: T-01`) |
| 2 | `PF-009cd606d15c7da41e40a02e87ad8b39` (low, resolved, `resolved_by: T-02`) | `PF-009cd606d15c7da41e40a02e87ad8b39` (low, resolved, `resolved_by: T-02`) |

Ids are content hashes over `summary`, so identical ids are proof no summary was reworded and no
later operator risk acceptance was stranded.

## How identity was guaranteed, not merely intended

The value file was not retyped. `/tmp/build-panel-BUG-151.py` loaded the live `panel:` mapping,
asserted `goalcheck` was absent, appended the one reader entry, and dumped the same object —
so every other value (including the multi-line `transcription_rule`) is preserved by
construction rather than by transcription. `set-panel` then asserts the spliced file reloads
equal to the supplied value (`plan-merge.py:1063`), a second independent check.

## Verification

`set-panel`, exit 0:

```
PANEL cycle 0 -> .../BUG-151-check-domain-fail-aggregation/plan.yaml
APPLIED .../BUG-151-check-domain-fail-aggregation/plan.yaml
```

Mandated acceptance check, run from the worktree:

```
pending plan plan-validator 0 [('goalcheck', 'ran'), ('scope', 'ran'), ('should-not-exist', 'ran')] [('PF-cf17fd813d058340727a00b9a33886cd', 'med', 'resolved'), ('PF-009cd606d15c7da41e40a02e87ad8b39', 'low', 'resolved')]
```

Untouched-field check on the same load:

```
tasks ['T-01', 'T-02']
decisions ['D-01', 'D-02']
source_issues [151]
lanes_at 6d969ed3
rule_tail 'h ids computed from the digest headings.'
```

`git status --porcelain` reports only the (already untracked) feature directory — no other file
modified. No linter, formatter or test suite was run.

## Open questions

None. This was a single transcription correction with no residual scope.
