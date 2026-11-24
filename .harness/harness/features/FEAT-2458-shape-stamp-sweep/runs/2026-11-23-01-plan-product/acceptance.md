# Send-back criteria — written before any return (cycle 1)

draft / apply (pm) are sent back if any holds:
- `plan-merge.py check --root <worktree>` not reported exit 0.
- Any task not `execution_mode: main-session-direct`.
- An SC permits a stamp deletion on anything but the existing landed rule, or the hook carries its own copy of the rule (D-02).
- `classify_feature` not three results with reasons; absent not folded into unresolved with a distinguishing reason; fleet (kaya) segment lookup not required.
- No SC for: plain stamp untouched, `--dry-run` deletes nothing, one line per kept unresolved stamp and none for live.
- `_repo_arg_for_segment` removal or `T07_TERMINAL_REMEDIES` key retirement missing.
- Anchors cite grilling line numbers without re-checking at worktree tip b788e9da.
- `panel:` or `approval:` written at draft; `approval:` written at apply.

Readers: a FAIL with no finding, or findings lacking `kind` (and `scope` for proportionality), is re-prompted once.
