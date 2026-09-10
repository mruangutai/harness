# Panel record — FEAT-58 — transcription of planpanel3-validator into plan.yaml `panel` (cycle 0)

**All 13 findings from `runs/planpanel3-validator/digest.md` are now in `plan.yaml`'s top-level
`panel` key — 6 high / 4 med / 3 low, every one `disposition: open`, none merged, none re-ranked,
none re-worded in severity, none risk-accepted.** The block was landed with
`plan-merge.py set-panel --value-file` (the only write route), which reported `APPLIED`; nothing
else in the plan was touched. This was a transcription, not an adjudication: no finding was fixed
and no disposition was decided here. The six highs reach the operator's batched signature review
unresolved (DEC-207).

## What landed

`panel.last_run: planpanel3-validator`, `cycle: 0`, `severity_max: high`, a `note` carrying the
FAIL, the no-reader-was-skipped-by-the-panel fact, the nothing-dismissed-on-merit fact, the
fix-order set and a pointer back to the digest for each finding's concrete change. Read back out of
the file after the write: `status: plan` and `approval.status: pending` unchanged, 9 tasks,
12 decisions, `lanes:` present, BRIEF.md untouched.

## Readers as written

| reader | status | persona | note |
|---|---|---|---|
| `scope` | `ran` | `harness-code-reviewer` | verdict FAIL, artifact `notes/review-harness-code-reviewer-planpanel-c0.md` |
| `should-not-exist` | `ran` | `fable-advisor` | verdict FAIL; no write grant, so its 9 findings exist only as transcribed |
| `goalcheck` | `skipped` | `harness-pm` | reason recorded in full in the block |

**The goalcheck decision (step 3), on evidence.** `teams/plan-panel.yaml` declares two steps, so
this panel produced no `goalcheck` reader. The feature's own goal-check graded a **pre-amendment**
draft: `runs/goalcheck3-product/digest.md` returned **FAIL** on GC-01 (D-08's cone strips six
tracked `.harness` subtrees) and GC-02, and `runs/amend3-product/digest.md` then records both as
LANDED after rewriting D-08 (`plan.yaml:239-306`), the fixture, N-05 and the BRIEF criteria set —
i.e. the amendment landed *after* the goal-check and changed exactly what it graded. The panel
digest agrees ("The amended plan fixes the derivation defect that failed goal-check"). No `ran` row
could be written honestly, so the reader is `skipped` with persona and the true reason.
`check-state.sh:551-558` grades a persona+reason skip as a **warn**, not a hard violation.

## Reader spelling for F-08 / F-09

Recorded as `reader: validator-lead`, per the lead's ruling — the digest attributes both to the
lead's union of the two readers' scopes and the enum has no term for it. **Verified this is not
rejected by any gate:** `check-state.sh:537-558` enum-validates only `readers[].reader`; the
finding loop (`:523-536`) reads `id`, `severity` and `disposition` and never `finding.reader`, and
`panel_findings.py` hashes the reader string without validating it. No open question needed.

## PF- id ↔ F-NN (computed by `panel_findings.py id`, never hand-written)

| label | sev | reader | id |
|---|---|---|---|
| F-01 | high | scope | `PF-4d938148443822e5d3d4a020757860bd` |
| F-02 | high | should-not-exist | `PF-8019985f6fc823ea262687e75108a1ba` |
| F-03 | high | should-not-exist | `PF-3919d144f94d57e0a246cf07b725097a` |
| F-04 | high | should-not-exist | `PF-49f508cf67c2d323f34c01aee70018a5` |
| F-05 | high | should-not-exist | `PF-22bd35b4cacca449abbc47a68fa7c71e` |
| F-06 | high | scope | `PF-f4b099518d765cc4f64ee8c7a65d7f5f` |
| F-07 | med | should-not-exist | `PF-799f9a68e4f57013272935518ced6d18` |
| F-08 | med | validator-lead | `PF-04bc7911c9b0158d77f90444f4485e77` |
| F-09 | med | validator-lead | `PF-801a7c02ad05c2c597d943ec97d46ada` |
| F-10 | med | should-not-exist | `PF-e02f536cdb50c8430c6ebf1571937755` |
| F-11 | low | should-not-exist | `PF-963e772d0924678051dc6b3bde3bd3f0` |
| F-12 | low | should-not-exist | `PF-5f866179428bb5a60faa08b0740f7d88` |
| F-13 | low | should-not-exist | `PF-55f4f7e86fb614cc7c9f51920834ccbe` |

Each id is the hash of the **exact** `reader` + `summary` recorded in the plan. Re-wording any
summary changes its id and silently invalidates a later operator ruling on it
(`check-state.sh:517-520`, STALE RISK ACCEPTANCE).

## Fix-order relationships — kept, in two places

The schema has no dedicated home, so each row carries a `fix_order:` string (the loader permits
extra keys) **and** the whole set is restated in `panel.note`: F-02 dropping the persisted index
also deletes F-08 and F-06's D-01 half; F-01 adding a task changes the graph and subsumes F-09;
F-03 + F-05 are ONE arm-aware, review-sha-gated edit; F-04 + F-07 are ONE rule (a standing test
never compares against a moving merge-base); the rest are independent. The findings list is in the
digest's own rank order, which the digest states IS the fix order.

## Blast radius of the write

`plan.yaml` mtime is the only one that moved (10:36:28); BRIEF.md 09:59, STATE.md 07:22,
feature.json 10:30, `observations/harness-pm.md` 10:02 all predate this segment. `panel:` still
begins at line 358 with lines 352-357 byte-identical to the pre-write read, and `tasks:` / `- id:
N-01` resume immediately after the block (now 358-576, was 358-373). `git diff --stat` shows five
files, all of them pre-existing uncommitted work from earlier segments of this run — the whole plan
was rewritten by `amend3-product` before I was dispatched, so the diff-vs-HEAD cannot isolate this
write and the mtime + boundary evidence above is what does.

## Open questions

- **Q1 (non-blocking, operator-visible residual).** No goal-check has read this draft; the
  `goalcheck` reader is recorded `skipped`. At signature `check-state.sh:551-558` emits
  `INV-32: ... reader goalcheck skipped persona harness-pm: ...` as a **warn**. If the operator
  wants a graded goal-check on the amended draft, it is a run, not a record edit.
- **Q2 (blocking at signature, by design).** INV-32 grades approved plans only, so today (approval
  `pending`) it emits nothing. The moment the plan is approved, `check-state.sh:534-536` appends a
  **hard violation per open high** — six of them — unless each is fixed or the operator records
  `approval.rulings` via `sign-approval --overrule`. That is the intended gate, not a defect, but
  it means signature cannot be a silent step.
- **Q3 (non-blocking).** The digest's Q1/Q2 remain the substance the operator must decide: F-02
  (does the DoD's uniqueness index mean a persisted file, and which writer regenerates it?) and
  F-01 (fix the four remaining cross-feature scan sites in this feature, or defer each by name).
