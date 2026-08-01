chore(expertise): the three domain leads' close-out distillation (13 ops)

FEAT-03-subissue-mirror's feature-close distillation never applied the leads'
own Expertise ops. The dispatch that ran it told each lead not to self-apply,
generalizing from a rule that governs only the orchestrator: check-domain.sh
blocks the orchestrator tier from writing another agent's Expertise file, but
team-config.yaml grants each lead its own file with upsert: true. The result
was a deadlock with no owner — 13 ops stranded in three run digests and three
lead Expertise files that did not exist at all.

Each lead re-dispatched to apply its own recorded ops verbatim to its own file.
Nothing was re-adjudicated and no op was dropped.

  harness-eng-lead        4 ops   Patterns 3, Gotchas 1
  harness-product-lead    6 ops   Patterns 3, Gotchas 2, Outcomes 1
  harness-validator-lead  3 ops   Patterns 2, Open 1

check-expertise.sh over .harness/expertise/ reports OK for all 11 files, exit 0
— including the title rule added at 99dd80a, which postdates every one of these
leads' runs and was passed down in the dispatch.

Two leads needed a second, one-field pass because the dispatch prescribed an
encoding validate-digest.py:493-497 rejects: members: [] alongside a non-zero
steps_run. That is a defect in the contract as much as in the dispatch — a
lead's self-distillation is a step with no member, and the digest schema has no
way to say so. Both digest files now validate. Raised as a backlog candidate in
STATE.md; the run dirs holding the evidence are gitignored, so this message and
STATE.md are its only committed trace.

Feature state is unchanged: status in_review, cycles_used 6 (this repairs a
botched close-out step, it does not rework a member's product), and the user's
ship decision on notes/ship-review-2026-07-31-16.md is still open.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014eZMX1bCGRrL71dpHXwYCj
