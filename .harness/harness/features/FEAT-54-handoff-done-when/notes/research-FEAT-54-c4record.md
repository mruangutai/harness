# FEAT-54 c4 panel transcription assessment

## Conclusion

PASS. The canonical c4 validator result is now the top-level `panel` in `plan.yaml`, written only through `plan-merge.py set-panel`. Both configured readers ran and all four findings were copied with their canonical ids, readers, severities, summaries, and dispositions. The maximum severity is `med`; there is no `high`, `critical`, or unrated finding.

Canonical input: `.harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c4-validator/digest.md:21-41,86-88`.

Result: `.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml:12-56`.

## Recorded panel

- `last_run`: `2026-09-02-c4-validator`
- `cycle`: `4`
- `should-not-exist`: persona `fable-advisor`, status `ran`
- `scope`: persona `harness-code-reviewer`, status `ran`
- Findings in canonical order: `C4-SNE-01` (`med`), `C4-SCOPE-01` (`med`), `C4-SNE-02` (`low`), `C4-SNE-03` (`info`)

## Scoped proof

Mutation command (exit 0):

```text
python3 .agents/skills/harness/bin/plan-merge.py set-panel --file .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml --value-file /tmp/FEAT-54-c4-panel.yaml
PANEL cycle 4 -> .../plan.yaml
APPLIED .../plan.yaml
```

A scoped Python assertion loaded `plan.yaml` and the exact value file with `yaml.safe_load`, asserted `plan["panel"] == expected`, asserted the absence of high, critical, and unrated severities, and compared pre/post SHA-256 hashes of the raw non-panel bytes and raw approval block. It exited 0 with:

```text
panel_exact=True
reader_count=2 finding_count=4
high_critical_unrated=[]
plan_approval=approved
non_panel_sha256=1fa81ad486fd63e65e09960adfe9276bb2a5f6c966f48998eea198050640f054
approval_sha256=78d3e03863461971eb0d2e86159eb04f17312e2d7d6f73f458f27ff249c6ea3c
```

The matching pre/post non-panel hash proves tasks, decisions, lanes, and every other top-level plan surface were byte-identical. The matching approval hash separately proves the approval mapping was byte-identical. No BRIEF or implementation file was mutated.

## Protected approval seam

Current plan approval is `approved` by Mike Ruangutai on `2026-09-02` (`plan.yaml:3-6`). Current BRIEF approval is also `approved` by Mike Ruangutai on `2026-09-02` (`BRIEF.md:199-203`).

There is no authorized PM verb that can reset an approved plan to `pending`. `plan-merge.py --help` exposes `apply`, `add-tasks`, `set-task-station`, `set-feature-station`, `set-panel`, `sign-approval`, and `amend`; none is a reset verb. The source contract says every verb on an existing plan preserves approval bytes and that `sign-approval` is the only approval writer (`plan-merge.py:29-39,995-1033`). `sign-approval` writes only `status: approved` and refuses governed subagents through its in-command identity check (`plan-merge.py:1024-1039`). Therefore no legal pending-to-signature seam can be re-established with the current vocabulary. The exact mechanism blocker is the absence of a guarded main-session reset-approval verb; directly editing approval or evading the identity guard would violate the contract. A main session can legally invoke `sign-approval`, but on this already-approved mapping that is a re-sign, not the required reset to pending, so it does not restore the desired boundary.
