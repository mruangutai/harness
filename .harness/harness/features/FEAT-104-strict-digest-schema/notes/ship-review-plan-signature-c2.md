# FEAT-104 — corrected plan signature packet (c2)

**Supersedes `ship-review-plan-signature-c1.md`.** Your rulings are applied. Five of six landed;
**OD-5 has no legal write route and is the one thing still needing you.** Nothing was implemented,
nothing was signed, and all six proposed backlog rows are struck and appear nowhere.

## Your rulings, one line each

| Ruling | State | Where |
|---|---|---|
| OD-1 — apply the hermetic inert fixture remedy | **APPLIED** | `plan.yaml:108,120,255,563,577`; `BRIEF.md:74-88` |
| OD-2 — drop `failures`/`suite`/`kinds` | **APPLIED** | `plan.yaml:132-134` (5 rows); D-02's bar repaired |
| OD-3 — T-01 PART 1 precision correction | **APPLIED** | `plan.yaml:141-147` |
| OD-4 — SC-11 precision correction | **APPLIED** | `BRIEF.md:105-108` |
| OD-5 — strike T-02 | **BLOCKED — needs you** | no delete verb exists; T-02 untouched |
| OD-6 — correct DEC-126 | **VERIFIED, already carried** | `plan.yaml:645-653`, WRITE 2, one clause |
| B-1..B-6 backlog | **ALL STRUCK** | none appears as task, decision, issue or note |

I verified OD-1 through OD-4 on disk myself rather than accepting the report: the fixture path is
present, the passthrough table is five rows, the optional-when-present sentence names
`validate-digest.py:1190` and `:1197`, and SC-11 carries its qualifier. The only surviving
`git show` string in either artifact is inside the verbatim panel finding text at `plan.yaml:743`,
which must not be reworded because a `PF-` id is a content hash of it.

## The one thing still yours — OD-5

**There is no legal route to remove a task from a plan.** `plan-merge.py`'s verbs are
`apply | add-tasks | set-task-station | set-feature-station | set-panel | sign-approval | amend`;
`apply`'s own help string reads "adds, never deletes", and `amend` replaces one field of one named
task under compare-and-swap. pm confirmed this at source, the lead confirmed it independently, and
neither invented a route or hand-edited the file — which is the correct refusal.

T-02 therefore still sits at `status: abandoned`, subsumed into T-01. Two options:

1. **Amend T-02's `title`/`intent` to record the strike in place.** Legal today, one command,
   reversible. The entry stays in the file but says plainly that you struck it.
2. **Add a guarded delete verb to `plan-merge.py`** as its own feature. This weakens the add-only
   promise the tool is built on and needs its own guard, so it is not a side change.

My recommendation is (1). It costs one command, it makes the record say what you decided, and it
does not touch a tool that eight other flows write through.

## One judgement call you should see — the passthrough table

Your ruling named three rows to drop. pm dropped exactly those three, then hit a consequence: with
D-02's bar repaired to "documented in a lead block", **`matrix_ok` and `coverage_gaps` are grounded
in no lead block that exists today**. Rather than drop two rows you did not name, pm made T-01
PART 3's new commented passthrough line (`plan.yaml:205-213`) the documentation that grounds them.

That is in-pattern with D-09 and I judge it sound. But it means two of the five surviving rows
depend on that one line landing at build time. Accept it, or strike those two as well — either is
a one-line change and neither blocks the signature.

## What signing gets you

`BRIEF.md` — 9 requirements, 15 success criteria, every one with a verification method: 13
`automated` on the `integration` runner, 1 `inspection` (SC-12's sha256 manifest), 1 `uat`
(SC-13, you read the DEC-174 carve-out diff). `plan.yaml` — 12 decisions, 9 active tasks plus the
abandoned T-02, the `lanes:` routing table, and the `panel:` record with all four `PF-` findings
now at `disposition: resolved` and their ids, severities, readers and evidence unchanged.

Traceability verified mechanically after the edits: every REQ has at least one SC and one active
task, every active task traces at least one REQ, and no task cites a REQ that does not exist.

## Gate state at signature

- `check-state.sh` reports exactly **two** FEAT-104 violations. One is the signature gate itself
  ("BRIEF.md is NOT approved"), which is the gate working.
- The other is the INV-26 false positive: its not-started skip requires `all(status == "ready")`,
  so T-02's `abandoned` value alone makes it demand `gh-sync.py open` — a command the mirror
  reference forbids before signed approval. **You struck B-1, so this stays red.** Recording it
  because taking OD-5 option (1) leaves it red too, and option (2) or removing T-02 is what clears
  it. No action implied; you have the facts.
- `check-plan-routes.py` exits 1 on the same pre-existing manifest deviation (this worktree's
  `.harness/team-config.yaml` is behind the owner root by `4d81e460`). No task violation. You
  struck B-2, so this also stays as it is.
- `validate-digest.py lead` on the last run's digest: `digest ok`.

## One thing that went wrong in the machinery, recorded not proposed

The product lead completed this run correctly but could not write its own run directory: a stale
`harness-product-lead` worktree claim on `FEAT-57-review-latency`, registered against its persona
mid-run by a concurrent flow, refused every write after the first two succeeded. The claim had
expired by the time the run returned (`inflight_registry.py list` → `NO CLAIMS`), so I wrote the
digest from the lead's returned DIGEST and closed its `state.yaml`, disclosing that in the file
itself. You struck B-6, which covers the neighbouring transport defect; this one is recorded in
`runs/sigfix-c2-product/digest.md` and nowhere else.

## Budget

`cycles_used: 3` of 10. The third is this ruling-application pass, counted as rework because the
panel FAIL came back down to a squad. `runs: 7` of an informational 20. Both healthy.

## Artifacts

All under
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/`:

- `BRIEF.md` — approval `pending`
- `plan.yaml` — approval `pending`, feature station `plan`, `panel:` all four findings resolved
- `notes/research-FEAT-104-sigfix-c2.md` — what changed per ruling, and the OD-5 route finding
- `notes/research-FEAT-104-triage-c0.md` — the measurement and per-key triage
- `notes/research-FEAT-104-goalcheck-plan-c0.md` and `notes/research-FEAT-104-planfix-c1.md`
- `notes/review-harness-code-reviewer-planpanel-c1.md`
- `runs/sigfix-c2-product/digest.md` — this pass's record
