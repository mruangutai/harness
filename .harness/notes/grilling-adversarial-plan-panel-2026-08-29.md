# Grilling — a standing adversarial panel for /harness-plan — 2026-08-29

Origin: run once by hand against FEAT-38's SIGNED plan. Three readers found what two prior review
rounds did not, including one high-severity defect that would have burned a build cycle. The operator
asked how to make the panel standing rather than ad hoc.

## Destination

`/harness-plan` gains a standing adversarial panel that runs against the DRAFTED plan before the
operator's signature. Its readers ask whether the work should be done at all — not whether it
conforms to the brief it was written from, which the existing simplify pass and architecture review
already cover. Reaching the end is: a team file the runner resolves, a named step in the plan door,
the routing and grants it needs, and a recorded decision for the two structural carve-outs it forces.

## Settled

- **Does an independent-model advisor participate at all, given its return is structurally
  unvalidated?** → **Yes, WRAPPED.** A harness agent dispatches it and normalizes its return into a
  compliant digest. Rejected: leaving it outside the contract as a pure advisory step; adding it as a
  17th agent; and dropping it, which would have cost the reader that found the high defect.
- **Where does the wrapper sit, given members are always leaves?** → **`harness-validator-lead`
  wraps it.** The lead dispatches the advisor as a step and normalizes its findings into its own
  collated digest. This is the only wrapper position the tier structure allows without a fourth
  layer, and the lead is already the collator. Rejected: carving out a member permitted to spawn,
  which breaks "specialist members are always leaves".
- **Who hosts the panel, given pm and the reviewers are in different squads?** → **TWO squad
  segments, sequenced by the orchestrator.** `harness-product-lead` hosts the goal-check;
  `harness-validator-lead` hosts the adversarial readers. Rejected: one host with pm loaned
  cross-squad, which `consult-when` routing does not permit; and product-lead hosting everything,
  which would have the authoring squad grade whether its own plan should exist.
- **Which persona takes the scope hunt** (orphan traces, dependency shape, unreachable verifies)?
  → **`harness-code-reviewer`.** Validation squad, already owns
  `notes/review-harness-code-reviewer-*.md`, and spec-compliance reading is its existing job, so no
  new grant is needed. Rejected: `harness-qa`; and `harness-pm`, which authored the plan and would be
  grading its own traceability.
- **When does the panel run?** → **EVERY plan, before the signature.** The cost on a small plan is
  accepted deliberately: a threshold has to be written down or it becomes an unrecorded judgement
  call, and opt-in gets skipped exactly when someone is in a hurry, which is when the panel pays.
- **Can the panel block a signature?** → **YES — a high-severity finding gates.** It must be resolved
  or **explicitly overruled by the operator** before the plan is presented for signature. Chosen over
  inform-only in full knowledge that it can trap a plan behind a reader that is simply wrong; the
  override path is what makes that survivable, and it must be part of the design rather than an
  informal habit.

## Not yet specified

- Whether the wrapped-advisor pattern generalizes to other outside models, or is a single carve-out
  for one reader. The question is not sharp until there is a second candidate.
- What the panel does on a `resume`-phase re-plan of an already-signed feature, where most tasks are
  `done` and only a few are new. FEAT-38 is exactly this shape and the hand-run panel had to be
  pointed at it manually.

## Out of scope

- The `/harness-ship` review panel. That panel grades a diff against a pinned SHA and already exists;
  this feature is about the plan, before any code is written.
- Fixing `check-domain.sh`'s fail-open approval guard. Same class of problem — convention where
  enforcement was assumed — and it is the next feature after FEAT-38 ships, not this one.
- Re-litigating FEAT-38's own findings. Those are ruled in that feature's
  `notes/answers-2026-08-29-panel.md` and a revision is in flight.

## Facts I verified (so pm does not re-derive them)

- **Teams are data, and there is no plan-phase team today.** `.claude/skills/harness/teams/` holds
  exactly `build.yaml` and `review.yaml`. Project overrides resolve from `.harness/teams/<name>.yaml`
  first (DEC-113). The plan sequence is currently PROSE in
  `.claude/commands/harness-plan.md`'s `**Target state:**` bullet, which is why nothing enforces its
  composition.
- **The step vocabulary is fixed and sufficient:** `id`, `persona`, `depends_on`, `inputs`,
  `outputs`, `mutates_repo`, `prompt`, `on_fail` (observed across both team files). `review.yaml`'s
  four reviewers are the exact precedent for a parallel read-only panel whose fan-in is deliberately
  NOT a step.
- **`on_fail: continue` already exists** for advisory steps that must not gate — `build.yaml` uses
  `loop_back`, and `harness-team/SKILL.md` documents `continue`.
- **A non-harness return is UNVALIDATED, not leniently validated.**
  `.claude/skills/harness/bin/validate-digest.py:906-907`: `if not agent.startswith("harness-"):
  return 0`. Measured consequence in the hand-run: the advisor returned a JSON object with
  `verdict`/`findings` keys, not `VERDICT:`/`DIGEST:`, and nothing objected.
- **A read-only persona cannot satisfy an `outputs:` path.** Measured: the scope-hunt reader was
  given an output path and no write tool, so its required note was NEVER created and its findings
  came back only in its return payload. Any team step pairing a read-only persona with `outputs:` is
  broken by construction.
- **Members are leaves.** `AGENTS.md`: "specialist members (layer 3, always leaves)". This is what
  forces the wrapper to the lead tier.
- **`harness-code-reviewer` needs no new grant** — `.harness/team-config.yaml` already gives it
  `.harness/*/features/*/notes/review-harness-code-reviewer-*.md`.
- **A grant mismatch is a real failure mode, observed in the hand-run.** The goal-check was asked for
  `notes/goalcheck-plan-*.md`; `check-domain.sh` denied it because pm owns
  `notes/research-*.md`, and the agent wrote the owned spelling instead and reported the deviation.
  The team file's `outputs:` templates must match existing grants or add them deliberately.
- **The hand-run's own process deviation, for the record:** the three readers were dispatched
  DIRECTLY from the main session, bypassing the orchestrator, which is a DEC-120 deviation. It is
  precisely the shortcut the standing version cannot take, and it is why the hosting question above
  had to be settled rather than assumed.
