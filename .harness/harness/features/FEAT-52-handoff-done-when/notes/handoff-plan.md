# Handoff — FEAT-52-handoff-done-when, plan → build — written at b7956fc4, seq-1

## Next

Do nothing until the operator signs. The plan is complete and pending signature: BRIEF.md
`## Approval` and plan.yaml `approval:` both read pending, and only the main session may sign
(`plan-merge.py sign-approval`). At signature the operator must also rule on two carried questions —
panel finding PF-4205e7e2 (whether INV-17 re-resolves pointers forever, or checks presence and shape
only) and D-04 (whether the persisted comprehension probe stays; striking it strikes T-09, T-12's
three cases and SC-09's registration clauses with it). After signature the build phase starts at
T-01, which is main-session-direct: 10 of 13 tasks are, under DEC-174.

## Trust

- BRIEF.md (10 REQ, 14 SC) and plan.yaml (13 tasks, 9 decisions) exist and are pending approval —
  `.harness/harness/features/FEAT-52-handoff-done-when/` — verified-at b7956fc4 by direct read.
- Routing is clean: `check-plan-routes.py` reports 0 violations; the DEVIATION lines are expected,
  a granted path declared main-session-direct under DEC-174 — verified-at b7956fc4 by running it.
- The panel ran with BOTH readers and is on the record: plan.yaml `panel:` carries readers
  should-not-exist and scope, five findings, severity_max med, all disposition open — verified-at
  b7956fc4 by reading the key back.
- No finding gates: nothing is high, critical or unrated, so signature is not withheld (DEC-176) —
  verified-at b7956fc4 from the panel digest and the transcribed severities.
- `check-state.sh` reports exactly one violation for this feature, the unapproved BRIEF, which IS
  the plan gate ("halt that flow and surface to the user", check-state.sh:301) — verified-at
  b7956fc4 by running it.
- SC-11 and SC-14 read not_met and that is correct: nothing is built. SC-11's control arm was
  observed discriminating on a stand-in range (control 4 lines, primary 0) and must be re-observed
  non-empty when `review_sha` is pinned — pm digest, run 2026-09-02-3-product — UNVERIFIED by me.
- feature.json references run `2026-09-02-goalcheck-c1-product`, which left no run dir; the c1
  goal-check's record is `notes/research-FEAT-52-goalcheck-plan-c1.md` — verified-at b7956fc4 by
  listing runs/. check-state emits a NOTE, not a violation.

## Dead ends

- Do not open a pre-signature fix dispatch for any panel finding: DEC-207 routes them into the one
  batched review at the signature gate — `.harness/harness/docs/DECISIONS.md` DEC-207 — verified-at
  b7956fc4.
- Do not route the gate scripts or their tests to a squad, whatever `check-domain.sh --resolve`
  grants: DEC-174's category governs — plan.yaml `lanes:` rows — verified-at b7956fc4.
- Do not write plan.yaml with an editor or a redirect, and do not reach for `apply` to CHANGE a
  value: it is add-only and exits 7 CONFLICT. `amend --show` then `--expect-sha256` is the route —
  pm digest, run 2026-09-02-2-product — verified-at b7956fc4.
- `.agents/skills/` is a symlink to `.claude/skills/`; grep -r does not follow it and the grants are
  written against the `.claude/` spelling — `readlink .agents/skills` — verified-at b7956fc4.

## Working set

- .harness/harness/features/FEAT-52-handoff-done-when/plan.yaml
- .harness/harness/features/FEAT-52-handoff-done-when/BRIEF.md
- .harness/notes/grilling-handoff-done-when-2026-09-02.md
- .harness/harness/features/FEAT-52-handoff-done-when/notes/research-FEAT-52-goalcheck-plan-c1.md
- .harness/harness/features/FEAT-52-handoff-done-when/runs/2026-09-02-4-validator/digest.md
