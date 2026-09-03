# QA distillation — FEAT-52

**BLUF:** No candidate passes. The lead-relayed two-branch negative-proof lesson is already covered by craft P-06; adding or rewording it would duplicate a durable rule without changing future QA conduct.

## Sources inspected

- Primary QA evidence: control-plane `notes/qa-feat52-validation-c8.md` — targeted red fixtures distinguish inline/fenced and control-plane path violations (§B); stripped contract-block negative control proves `validate-digest.py` rejects missing required fields (§D).
- Available feature observations: `observations/harness-documentor.md`, `observations/harness-orchestrator.md`, and `observations/harness-pm.md`; no QA observation file exists.
- Independent survivor evidence: `notes/research-FEAT-52-factory-control-plane-panel-record-c5.md:130-138` and `notes/research-FEAT-52-factory-control-plane-plan-repair-fix-c5.md:42-47` establish the distinct wrong-anchor, no-occurrence, and count branches.
- Inspected Expertise: craft `.harness/expertise/harness-qa.md`; repository `.harness/harness/expertise/harness-qa.md`.

## Counts

| Tier | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft, before | 15 | 15 | 10 | 1 |
| Craft, after | 15 | 15 | 10 | 1 |
| Repository, before | 0 | 8 | 0 | 0 |
| Repository, after | 0 | 8 | 0 | 0 |

## Candidate decisions

- **Lead-relayed, survivor notes:** Reject. P-06 already requires a separate test for every distinct triggering leg. The wrong-present and no-occurrence fixtures are exactly distinct decision branches; a second rule would only restate P-06 with this feature's vocabulary.
- **Primary QA note §D:** Reject. Its lesson is already within P-07's requirement to assert verdict content rather than a pass token or exit status; the stripped contract block is an instance, not a broader rule.
- **Primary QA note §C:** Reject. The environment-specific full-suite/worktree manifest drift is not demonstrated as durable across future QA spawns and does not qualify for repository Expertise.

## Applied operations

None. `expertise-merge.py` was not invoked because no accepted operation exists.
