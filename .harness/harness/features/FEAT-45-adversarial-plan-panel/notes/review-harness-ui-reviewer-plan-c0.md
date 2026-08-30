# UI Reviewer — Mode A design-contract review — FEAT-45-adversarial-plan-panel — cycle 0

review_sha: 1d3e5db5d17d9e7cf484b38e3796cf8ed5468bb1

## Scope

No graphical surface exists in this plan (team YAML, playbook prose, a template key, an invariant,
test scripts — confirmed by reading T-01..T-10 and BRIEF REQ/SC in full). The candidate surfaces are
operator-facing text: the panel gate message, the overrule act, and the two `verify: uat` criteria.
Per dispatch these are explicitly handed down as in-remit; judged on their own evidence below, not
accepted as framed.

## PASS, with two `med` completeness findings (neither gates)

### F1 — gate message: the operator cannot tell HOW to proceed without already knowing D-05, and the
stale-override case is undocumented anywhere operator-facing — `med`

T-03's spec for the live block is exactly: "return `awaiting_user` with the finding in
`open_questions`." The panel finding's own schema (T-05: `id`, `severity`, `reader`, `summary`,
`disposition`, `resolved_by`) gives WHAT and WHICH reader for free, but carries no field and no
instruction that the `awaiting_user` message state the remedy — that resolving means the finding's
`disposition` becomes `resolved` via a build task, or that overruling means a main-session write to
`approval.rulings` with `finding`/`ruling`/`who`/`date`/`reason` (D-07). Neither T-07's INV-32 message
spec ("each producing its own message naming the feature and the offending id") nor any REQ/SC
requires this. No SC checks operator-legibility of the block message at all.

The gap sharpens on the stale-override path. D-05 mints a reworded finding a NEW content-hash id by
design, so an operator who already overruled a concern on cycle 0 will, after a re-plan reruns the
panel and a reader rewords the same substantive point, see the SAME finding block signature AGAIN
under a different `PF-` id. T-07's message spec for that path is "append to bad as a STALE OVERRIDE
naming the id" — it does not require the message to say the id changed because the wording changed,
or that this is the same concern the operator already ruled on. That explanation exists only as a
template comment in T-05 (`.claude/skills/harness/templates/plan.yaml`, read by pm/developers) and as
task-intent prose (T-07) — never in `.claude/commands/harness-plan.md` or the new
`## The plan phase` section of `SKILL.md` (T-03/T-04), the two places an operator's own reading would
land. Concrete scenario: operator overrules `PF-a1b2c3d4` on cycle 0 with a stated reason; cycle 1's
`should-not-exist` reader rewords the same objection, minting `PF-e5f6a7b8`; the plan blocks again
citing only the new id, with nothing operator-facing distinguishing "new issue" from "the one you
already settled, reworded." Mitigated by the fact the orchestrator (the main session, an LLM with
`SKILL.md`/`harness-plan.md` in context) will very plausibly explain this in conversation even absent
an explicit spec line — which is why this is `med` and not `high`.

### F2 — SC-11's pass/fail line is undefined for the very outcome the design instructs readers to
produce — `med`

BRIEF SC-11: "the operator judges each of the three readers to have earned its spawn — findings of
substance, not padding to justify the run." T-02's own reader-prompt spec, twice, makes an empty
findings list the CORRECT outcome on a clean plan: "an empty list is a valid result" and "padding the
list to justify the spawn is worse than returning an empty findings list." SC-11 gives no rule for
that case — with zero findings there is nothing "of substance" to judge, and the wording does not say
whether a reader that (correctly) found nothing "earned its spawn" or failed to. A UAT executor
running SC-11 against a genuinely clean plan has no defined pass/fail line for the outcome the design
itself calls the good one. SC-12, by contrast, IS reasonably executable as written (act: read the
panel's rolled-up result; observation: any step beyond that before signing; pass/fail: extra step or
not) — no finding there.

## Not filed as findings

- The overrule ACT itself (operator states intent, main session performs the `approval.rulings`
  write, D-07) follows the same established convention already used for `approval.status` at
  signature (`harness-plan.md` Terminus: "ONE approval, taken by you") — extending a precedent the
  operator already relies on, not a new unspecified interaction. No finding.
- INV-32 (T-07/T-08) is a post-approval integrity net, not the live operator-facing block — its
  message-content spec was read for F1 but the live gate is T-03's `awaiting_user`, which is where
  F1 is anchored.

## Verdict basis

`must_fix: []`, `severity_max: med` — below the `>= high` gate threshold, so `VERDICT: PASS`. Both
findings are contract-completeness gaps a pm/main-session prose addition can close before build; they
do not require touching `.claude/`, `plan.yaml`, or `BRIEF.md` themselves — that edit is pm's under
D-03, not mine.
