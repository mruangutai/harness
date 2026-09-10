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

## Two corrections to the c1 packet, and what they mean for the build phase

The product lead completed its run correctly but could not write its own run directory: every
write after the first two was refused with
`harness-product-lead holds worktree claim(s): .../FEAT-57-review-latency`.

**Correction 1 — I told you that claim had cleared. It had not, and my evidence was worthless.**
I had run `inflight_registry.py list` from the main checkout and read `NO CLAIMS`. `REGISTRY_REL`
resolves `.harness/.inflight-claims.json` per ROOT, so that command reports on the main checkout
and says nothing whatever about another worktree's registry.

**Correction 2 — my replacement evidence was also too strong.** I then cited `ps` showing
`supervisor_pid 9988` alive with a start time matching `supervisor_started_at`, and concluded the
claim was live. That proves the SUPERVISOR lives. A claim is retained for that supervisor's whole
lifetime, so a claim leaked by an interrupted dispatch can never expire inside it, and `reconcile`
returns `RECONCILED 0` correctly. PID liveness and run liveness are separable.

**What actually discriminates, measured.** FEAT-57 holds two claims, both registered
2026-09-09T18:49:11Z. Its own run states show exactly one non-complete run —
`2026-09-09-02-validator`, step `q6-reachability` still `running`, touched 872s before I read it.
That backs the `harness-validator-lead` claim. There is **no** non-complete product run in FEAT-57,
so the `harness-product-lead` claim that blocked me has no run behind it that I can see, and may be
a leak.

**I released nothing, and am not asking you to.** An absent `state.yaml` is not proof of an absent
run — a lead blocked from writing its own run dir is precisely the failure I just experienced — it
is another flow's worktree, and you have stopped cross-worktree releases. The measurement is yours;
the decision is not mine. I landed the lead's digest from my own tier instead, carrying its fenced
contract block, and disclosed both corrections in the file rather than overwriting them.

**Why this bears on your signature rather than on my bookkeeping.** `check-domain.sh` enforces
single-flight by agent TYPE across every linked worktree, not per feature. So while another flow
holds `harness-product-lead` or `harness-eng-lead`, this feature's build-phase dispatches will hit
the same wall — mid-run, after earlier writes to the same path have succeeded, which is what makes
it read as a transient. The blast radius is run bookkeeping only: `notes/` paths are granted per
persona and are not what the claim blocks, so durable artifacts land fine and a lead can return its
digest inline for the tier above to write. The FEAT-56 flow has hit this seven times today and has
already escalated it to you as one structural finding; I am citing it rather than re-filing it, and
FEAT-104 is the second independent feature with the same failure and the same workaround.

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
- `runs/sigfix-c2-product/digest.md` — this pass's record, carrying both corrections
