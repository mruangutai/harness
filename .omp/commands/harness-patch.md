# /harness-patch — take a known-cause, bounded change to a signed intake in one run

Read `.omp/commands/harness.md` and follow it with **mission: patch**. The differences:

- **Step zero, BLOCKING:** load the `harness-grilling` skill and run it first — the same dialog
  `/harness-plan` opens with, and usually a short one: the cause is known and the grilling can name
  the files. Hand pm the artifact **path** as the BRIEF input (DEC-164). Already have the artifact?
  Cite it and move on. Skipping it is the user's explicit call, never your assumption.
- **Refuse without a mission.** The artifact's `## Mission` block must read `mission: patch`, with
  its `reason:` and the operator's `confirmed-by:` or `overridden-by:` line (SC-01). The judgement
  is `patch` when the cause is known, the diff is bounded and no new public interface, schema or
  enforcement surface is created; anything else is `plan`. No block → back to step zero;
  `mission: plan` → this is `/harness-plan`'s feature, not yours. You do not re-derive the
  judgement here, and you never upgrade to `plan` because it feels safer (SC-22): a known-cause
  bug reaches a signed intake in one run and ships in about four.
- **KICKOFF: the source ticket moves to Plan** — before the BRIEF work begins, run
  `python3 .claude/skills/harness/bin/board-station.py <issue-number> plan` from the repo root.
  The ticket is the issue the user names in the opening ask or in answer to step zero; no separate
  question is asked for it. When **no ticket is named**, write nothing and ask nothing.
  Best-effort: a board failure prints one line and the intake continues.
- **Target state:** BRIEF and `plan.yaml` `pending`, produced by ONE product run and nothing else
  (SC-02). The orchestrator dispatches product-lead once; pm writes a BRIEF in the by-perspective
  shape at no more than 120 lines — `## Problem`, `## Done when — by perspective`, the SCs each
  tagged with the perspective they discharge — and a `plan.yaml` holding exactly one task: `T-01`,
  `execution_mode: team`, `execution_agent` the dev who owns the files, `files:` from the grilling,
  `traces:` every SC, `change_type: bugfix` unless the grilling says otherwise. The orchestrator
  records `mission: patch` in `feature.json` with its `mission` judgement. **No readers, no panel,
  no goal-check run** — a patch is gated at qa and review on the diff, not at plan on a document
  (DEC-139 as amended by FEAT-59). Ids are `BUG-NN-<slug>` for a bug and `FEAT-NN-<slug>`
  otherwise; the lane does not change the id.
- **Terminus:** ONE approval, taken by you, and **the same signature carries the rework ruling**:
  `plan-merge.py sign-approval --file <plan.yaml> --by <you> --date <YYYY-MM-DD> --rework rounds=N,minutes=M --decision <path>`
  writes `approval.status: approved` and `feature.json` `rework` in one act (SC-15). Completing
  the intake is NOT a briefing (§10.3).
  **The signature is immediately followed by** this receipt-driven transaction:
  ```bash
  approval_receipt="$(
    python3 .claude/skills/harness/bin/plan-merge.py sign-approval \
      --file <plan.yaml> --by <you> --date <YYYY-MM-DD> \
      --rework rounds=N,minutes=M --decision <path>
  )"
  printf '%s\n' "$approval_receipt"
  resume_station="$(printf '%s\n' "$approval_receipt" | sed -n 's/^RESUME: //p')"
  case "$resume_station" in
    ready|building|review) ;;
    *) printf 'invalid or missing RESUME station\n' >&2; exit 2 ;;
  esac
  python3 .claude/skills/harness/bin/gh-sync.py open <feature-dir>
  python3 .claude/skills/harness/bin/gh-sync.py status <feature-dir> "$resume_station"
  ```
  `sign-approval` emits `RESUME: ready` for initial approval and the saved Ready, Building, or
  Review station for reapproval. Validate that machine-readable value; never replace it with a
  literal. `open` is idempotent and must precede `status`, so newly added task cards exist before
  the complete card set is projected.
- **After signature the flow is exactly build → validate → ship**: the `build` team for `T-01`,
  SIMPLIFY, one pinned `review_sha`, one `validate` run (qa with fail-first evidence, code,
  security, ui if the diff has one, pm's goal-check by perspective), `fix` rounds inside the
  rework ruling, then the CEO briefing. Offer `/harness-ship` — do not start it unasked.
