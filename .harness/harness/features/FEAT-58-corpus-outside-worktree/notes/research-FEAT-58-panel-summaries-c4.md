# Panel 2 transcription — PF- identity record — FEAT-58 (planpanel4-validator, cycle 0)

**The identities below were computed once and are reproducible from `plan.yaml` alone.** Each id is
`panel_findings.py id --reader <row.reader> --summary <row.summary>` over the row as recorded in
`plan.yaml`'s `panel.findings` — no normalization, no stripping. Re-running the command over the
plan's own values reproduces all nine (verified after the merge).

```
python3 .claude/skills/harness/bin/panel_findings.py id --reader <reader> --summary <summary>
```

| label | reader | PF- id |
|---|---|---|
| VL-01 | scope | PF-f0281057320f2984492f8fba14508156 |
| VL-02 | should-not-exist | PF-9e4a874e461968f2eb1d6be6e7f759b5 |
| VL-03 | should-not-exist | PF-06cff062432fa2a378c86f484546aa67 |
| VL-04 | both | PF-5d6b94e681529c8c10a29ace089faf1b |
| VL-05 | should-not-exist | PF-20fa406d84f713a4a16e046acaa5180f |
| VL-06 | should-not-exist | PF-e73f4795ba116f730872c14a973d41d8 |
| VL-07 | should-not-exist | PF-f0a7225dad2cb03b19e82094f4e51448 |
| VL-08 | should-not-exist | PF-f7a5ff34454ade8140ab5219a5b26687 |
| VL-09 | should-not-exist | PF-00b183e742cf12a05cc19b0c25adce83 |

`VL-04` carries `reader: both` because both readers reported it independently and the lead
deduplicated it; that string is part of its identity.

Source of every severity, reporter, summary and disposition:
`runs/planpanel4-validator/digest.md`. Merge value staged at
`notes/research-FEAT-58-panel-value-c4.md` and applied with
`plan-merge.py set-panel` (the only write route).
