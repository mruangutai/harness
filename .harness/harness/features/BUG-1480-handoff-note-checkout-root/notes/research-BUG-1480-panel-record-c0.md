# Panel record — c0 transcription and remedies — BUG-1480

**BLUF: the c0 plan panel is recorded in `plan.yaml`'s top-level `panel:` key and both actionable
remedies are applied. The plan is ready for the operator's signature — `approval:` is untouched at
`{status: pending}`, the task set is still exactly T-01/T-02, and T-02's `verify:` and `intent:` are
byte-identical to their pre-write state.** One deviation from the dispatch, taken deliberately and
recorded below: the finding ids are the canonical `panel_findings.py` ids, not the ad-hoc
8-hex-of-summary ids the dispatch specified.

## What was written

- `plan.yaml` `panel:` — `last_run: 2026-09-07-01-validator`, `cycle: 0`, three readers all
  `status: ran` (`should-not-exist`/`fable-advisor`, `scope`/`harness-code-reviewer`,
  `goalcheck`/`harness-pm`), three findings. Route: `plan-merge.py set-panel`.
- `plan.yaml` `T-02.traces` — `[REQ-01, REQ-02, REQ-03, REQ-04]` → `[REQ-01, REQ-02, REQ-03, REQ-04,
  REQ-06]`. Route: `plan-merge.py amend --field traces --yaml-value --expect-sha256
  c7d747aa…474b`. T-01.traces untouched. This discharges the `med` finding; `resolved_by: T-02`.
- `BRIEF.md` `## Constraints`, third bullet — the six numeric anchors (`:1906`, `:1912`,
  `:2042-2048`, `:2073`, `:2077`, `:2089-2090`) replaced by the by-name citations SC-05 already uses
  (`_resolved_rel`, `_plan_route`, the Edit/Write target-assembly block in `__main__`, the sweep's
  `targets.append`). The claim is unchanged; only the citation form is. **This edit — not any task —
  discharges the `low` finding, which is why that finding carries no `resolved_by`.**
- `notes/research-BUG-1480-goalcheck-plan-c0.md` — appended `## Reconciliation — F-id mapping across
  the two c0 notes`. Add-only; nothing renumbered in either note.

## Findings, at the readers' own severities

| id | sev | reader | disposition |
|---|---|---|---|
| `PF-880e7f88ebb96fb0dc3a4f07f32fcd32` | med | scope | resolved, `resolved_by: T-02` |
| `PF-bc6a76a833e3d2f5f991cf9a205b621c` | low | scope | resolved (BRIEF.md's own edit) |
| `PF-7b29d51a6c8f4b6dbdcba528ca92d5ff` | info | should-not-exist | open — advisory, no resolution invented |

`should-not-exist`'s four KEEP verdicts and the lead's POST-route observation at
`check-domain.sh:2092-2094` are dismissed in the digest and are deliberately absent from `findings:`.

## The id-scheme deviation — read this before comparing against the dispatch

The dispatch specified `PF-` + first 8 hex of `sha256(summary)`, which would have given
`PF-0c83a5c1` / `PF-5f6dd88c` / `PF-4b0ffe2c`. I used `panel_findings.py id --reader <r> --summary
<s>` instead — `PF-` + first 32 hex of `sha256(reader + "\n" + normalize(summary))`
(`panel_findings.py:28-33`). Reasons, in order of weight:

1. `harness-spec-driven` mandates it verbatim: "Compute every id with … `panel_findings.py`; never
   type it." The script's own docstring is the reason — it is the ONE place identity is computed so
   the lead, pm and `check-state.sh` cannot disagree.
2. `check-state.sh` INV-32 (`:514-517`) reports STALE RISK ACCEPTANCE when an `approval.rulings`
   entry names an id absent from `panel.findings`. An operator ruling on the open `info` finding will
   compute the id with the mandated tool, so a non-canonical id in the plan is a latent hard fail.
3. Every other recorded panel in this tree uses the 32-hex form (FEAT-55, BUG-1303, BUG-1290,
   BUG-1306 in `check-state.sh` output). The 8-hex form would have been unique in the record.
4. The dispatch's preimage omits the reader, so two readers reporting identical text would collide —
   the exact property `test-panel-findings.py` case4 defends.

The summaries are byte-identical to the dispatch's preimages, so the lead can re-derive either form.

## Open questions

- Q1 (non-blocking, not mine): `check-state.sh` reports
  `runs/2026-09-07-01-validator/digest.md: does not satisfy the lead digest contract … Run
  bin/validate-digest.py lead on it for reasons.` The run dir is the validator lead's write grant,
  not the pm's. Flagged for the lead before the ship review reads it.
- Q2 (non-blocking): the dispatch's finding-id formula contradicts `harness-spec-driven` and
  `panel_findings.py`. If the dispatcher intended the short form, the doctrine and the tool need to
  change together — not this one plan.
