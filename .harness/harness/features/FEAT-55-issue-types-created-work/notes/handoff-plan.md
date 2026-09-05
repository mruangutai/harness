# Handoff — FEAT-55, plan → signature — written at c76da3b6, seq-4

## Next

Take ONE batched operator signature over the plan package — BRIEF.md (11 REQ, 12 SC), plan.yaml
(12 tasks, 20 decisions) and plan.yaml's `panel:` key, whose 7 findings are that pass's agenda.
PF-f1031f76b4537f1cd9b60ddc0559b7d1 (high, `disposition: awaiting_user`) gates it: the operator
either directs the fix or accepts the risk via `plan-merge.py sign-approval --overrule <PF-id>:<why>`.
No fix goes out while they are still reading (DEC-176); collect every request from that one pass into
one `notes/answers-<runid>.md` and dispatch exactly ONE consolidated revision to product-lead. A
revision resets approval to pending and re-runs the panel over unfinished tasks in a new run dir.

## Trust

- Plan loads, 12 tasks / 20 decisions, `check-plan-routes.py` 0 violations — plan.yaml sha256
  04f45dbe36fe3482dc900da6f694b5a67efcba18b27a3dc2a0a146307af81277 — verified-at c76da3b6
- Neither approval fragment carries a half-signature: plan.yaml `approval: {status: pending}` and
  BRIEF.md `## Approval` `status: pending` — both re-read after the panel write — verified-at c76da3b6
- All 7 findings transcribed at the reader's own severity, none dismissed, every `PF-` id
  re-derives from its stored reader+summary — plan.yaml `panel:` re-hashed with
  `bin/panel_findings.py` — verified-at c76da3b6
- Both panel readers RAN — no finding is missing to an unresolved persona —
  `runs/2026-09-04-11-validator/digest.md` `readers:` — verified-at c76da3b6
- Plan delivers the operator's stated intent; F-01..F-09, N-01, N-02 all CLOSED —
  `notes/research-FEAT-55-goalcheck-plan-c2.md` — verified-at c76da3b6
- Panel `must_fix` (2) and `fix_order` (4) are the panel's own, re-ranked by nobody —
  plan.yaml `panel.must_fix` / `panel.fix_order` — verified-at c76da3b6

## Dead ends

- No pre-signature fix dispatch for any panel finding, gating or not — DECISIONS.md DEC-207,
  "never open a separate pre-signature fix dispatch" — verified-at c76da3b6
- Do not pin `review_sha`: the panel graded a specification, so its run record carries
  `code_grade: n_a` — feature.json `runs[-1]`, BUG-1080 — verified-at c76da3b6
- Do not re-run the product goal-check before signature; segment 1 closed at YES and its note is a
  panel INPUT, not a subject — `notes/research-FEAT-55-goalcheck-plan-c2.md` — verified-at c76da3b6
- Do not mirror to GitHub yet; `gh-sync.py` writes the `review` station at the Building→Review seam
  and this plan is unsigned — `.agents/skills/harness/references/github-mirror.md` — verified-at c76da3b6

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/plan.yaml
- .harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-04-11-validator/digest.md
- .harness/harness/features/FEAT-55-issue-types-created-work/notes/research-FEAT-55-goalcheck-plan-c2.md
- .harness/notes/grilling-issue-types-2026-09-04.md

## Done when

Scope: the operator's one batched signature pass over FEAT-55's plan package
Authority: approval:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/BRIEF.md#Approval
