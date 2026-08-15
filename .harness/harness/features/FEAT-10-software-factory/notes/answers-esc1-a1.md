# Operator answers — ESC-1, A-1, and the signature, 2026-08-08

## ESC-1 — ENFORCE NOW. Deferral is rejected.

`factory_claim` must not take an issue whose `blocked_by` blockers are unfinished. Encoded-but-
unenforced edges are not acceptable for increment 1: a queue that renders a block marker and then
hands the work out anyway is worse than no marker, because the operator reads the board and
believes ordering holds.

This is the decision amendment eng-lead named, taken deliberately:
- Widen D-01's read-back bound to permit reading blocker COMPLETION (neither a claim nor a station).
- Record the widening as an amended decision with its reason, not as a bug fix.
- The DEC-138 write-only baseline is the thing being amended; say so explicitly in the decision text
  so a later reader sees a ruling, not a drift.

The stderr "N edges drawn, 0 enforced" line is moot under this ruling and must not ship as a
substitute for enforcement.

## A-1 — FOLD IN NOW.

Widen T-08's `INV-24` duplicate check to collect `factory.parent` alongside `factory.issues`.
D-12's recorded hazard is exactly a container published beside one the factory creates, and T-08 is
the only place it becomes detectable. T-08 stays `main-session-direct` under DEC-174.

## Signature

APPROVED IN INTENT, pending this amendment. The operator has approved BRIEF.md and plan.yaml
subject to the two changes above landing. Do NOT self-approve: return the amended plan and the main
session writes the signature. Present only the delta — the operator has read everything else.

## Not to be re-litigated (already settled)

- Q7 dependency edges: encoded (done) AND now enforced (this ruling).
- Q8 criteria rework: accepted as delivered — 20 SCs, 17 automated, all REQ-traced, SC-19 the
  end-to-end happy path.
- E-1, E-2 ledger fixes: accepted.
- N-1, N-2, N-3 disclosures: read and accepted; N-3's receipt-path recurrence is filed as #199,
  and the missing `depends_on` referential-integrity check is a NEW backlog item, not this
  feature's work.
- Board rename (Building, Review) and workspace_root: the operator's, before T-01 runs.

## LATE RULING — SC-07 is DROPPED ENTIRELY (2026-08-08, after the amendment dispatch)

Delete SC-07. Do not keep a reduced version.

Reason, in the operator's own framing: with the #194 cap at ONE issue in flight factory-wide, one
issue per scheduled wake, a single credential and push-first dispatch, two concurrent claims against
the same issue cannot arise in normal use. A criterion that requires the operator to stage that race
by hand is anticipation, and the constitution is explicit that structure must be earned by a real
bottleneck rather than designed in advance of one.

What does NOT change:
- The git-ref claim mechanism STAYS. It is not what was over-built: it costs nothing over any other
  marker and it fails loudly instead of silently, which is why the assignee scheme was rejected.
  D-05 and REQ-03 stand.
- SC-19 remains the end-to-end proof.

Accepted consequence, stated at the time of the ruling: with SC-07 gone, NO success criterion
exercises the live GitHub API before ship. The first real dispatch is the live verification. The
operator accepts this.

Housekeeping for pm: SC-07 traced REQ-01..REQ-05. Re-verify that every one of those requirements
still has at least one criterion after the deletion, and that no remaining criterion or DESIGN.md
row cites SC-07. UAT: if SC-07 was the only `verify: uat` criterion, the feature now has no UAT
script and the ship gate must say so explicitly rather than silently skipping it.

## FOURTH RULING — plain English across the BRIEF (2026-08-08)

Rewrite every REQUIREMENT and every SUCCESS CRITERION in plain, simple English. Same cycle.

**What must not change:** the meaning, the count, the ids, the `verify:` methods, the `evidence:`
kinds, and the REQ traces. This is a rewrite of the PROSE only. A criterion that changes what it
asserts has been re-authored, not rewritten, and that is out of scope here.

**What plain means, concretely:**
- Say what must be true, in the order a reader needs it. Lead with the outcome, not the mechanism.
- One idea per sentence. Short sentences.
- No scope caveats folded into the criterion text ("this proves X, not Y — the Z case is SC-NN's").
  If a boundary genuinely needs stating, it goes in a separate line, not inside the assertion.
- No cross-references to other criteria inside a criterion. SC-12 currently cites SC-07, which the
  operator has deleted — that dangling pointer is exactly the shape being removed.
- Keep exact data exact: ids, file paths, command names, exit codes, field names, `verify:` values.
  These are not prose and must be carried over unchanged.

Worked example the operator approved, for SC-12:

  SC-12: The claim tool must handle both answers it can get. If the marker is created, it proceeds
  and reports success. If the marker already exists, it stops, exits with code 3, and writes
  nothing — no label, no assignee, no card move.

pm owns the wording (DEC-132); this is the instruction, not the text.

## FIFTH RULING — plain English becomes standing policy

Add the rule above to the `harness-brief` skill, so every future BRIEF is written this way and no
future feature needs this instruction. This is an ordinary skill edit, NOT an enforcement-layer file,
so it is inside the carve-out and may be executed normally.

State it in the skill as a rule with one clause of why (the skill's own house style): requirements
and criteria are read by the person who signs them and by every agent that plans against them, so
they are written to be understood on one reading.
