# Handoff — FEAT-03-subissue-mirror, plan → build — written at 65e8cc7, seq-3 (supersedes seq-2)

## Next

**Wait for the user's signature, then start the build phase.** Fix cycle 2 is CLOSED: pm repaired both
changes (run 05-product PASS) and eng-lead re-verified them per-item (run 06-eng PASS, zero `must_fix`).
Both `## Approval` blocks are `status: pending`, which stops a build mission at step 0 until signed.
On signature, build T-01..T-08 in PLAN order; read PLAN `## Preconditions` FIRST — one is an outstanding
**main-session** edit (`.claude/skills/harness/SKILL.md:137,144`, SC-13) no agent domain covers, and
**T-08's owner harness-documentor is PRODUCT squad** — route laterally via product-lead (Q8).

## Trust

- Cycle 2 applied by pm (run 05-product PASS, no send-back); both `## Approval` still `status: pending`
  — one grep match each at BRIEF:214 / PLAN:599 — verified-at 65e8cc7
- **Abandon is now conditional**: adopted → open, created → close `not_planned`, absent origin → open.
  Receipt `  parent_origin: created|adopted|none`, two-space sibling key before `  issues:`; 20× PLAN,
  3× BRIEF — `grep -c` — verified-at 65e8cc7
- **eng-lead re-verified cycle 2 per-item and reproduced the absence-greps FIRST-HAND** (run 06-eng PASS,
  zero `must_fix`): in `bin/`, `parent_origin` and `abandon` both count ZERO, so all nine T-05 labels are
  provably absent from today's output — the MF-1 void-grep class did not recur — its digest, run 06-eng
- **Four unconditional-claim sites changed, not the two the task named** — BRIEF SC-03, T-05 step 4,
  T-05's `ok` label, **and T-08's DECISIONS am.7 instruction text** — grepped pre-dispatch — verified-at 65e8cc7
- Retired label `"abandon leaves the parent open"` greps **1** in PLAN (`:491`) — prose documenting its own
  retirement, not a live label. Read it before filing a defect — verified-at 65e8cc7
- Task count held at **8**; T-06/SC-04 unchanged, still the unconditional `completed` close — verified-at 65e8cc7
- Rename: BRIEF 19 → **9** `mirror`, PLAN 11 → **7** (`grep -o|wc -l`); 3 survivors are immutable slug
  occurrences (DEC-133). Handed-down "17 and 10" were approximate — the RULE governs — verified-at 65e8cc7
- `f929d44` still the valid code anchor: `git diff --stat f929d44..HEAD -- ':!.harness/'` empty, so no
  `observed @` receipt moved — ran it — verified-at 65e8cc7
- **Cost OVER budget: ~$141 of $120, by ~$21** (DEC-134: never gates). Runs 05/06 were $24 and $7 by P-01
  snapshot delta; the rest is orchestrator session share, not separable from a second depth-1 orchestrator
- Mirror invariants hold only against the fake `gh`; the live API path rides on DEC-168's probe — UNVERIFIED

## Dead ends

- **Reopening the grilling** (`.harness/notes/grilling-subissue-mirror-2026-07-31.md`) — cycle 2
  PRESERVES "leave the adopted parent open" and only ADDS the created case; root cause was D-01 adding a
  third origin after the grilling settled two — source: user, this cycle
- **Editing `docs/harness/DECISIONS.md` or `.claude/skills/harness/SKILL.md` for the rename** — first is
  historical record and defines "mirror" at DEC-138; second rides with SC-13. **Renaming the dir or
  slug** — DEC-133 immutability, breaks four run dirs — source: user, Q6
- **Fixing T-06/`ship`'s unconditional parent close** — the symmetric defect (closing an ADOPTED parent
  `completed`). Real, recorded as **Q15**, NOT authorized — source: user's two-change scope
- **Merging T-05+T-06 / changing the task count** — held at 8; the decomposition is the premise of the
  signature — source: orchestrator, cycles 1 and 2
- **Path-level greps for SC-06** — self-voiding: the retained list GETs (`wayfind.py:113`, `:117`) and the
  extracted writes build the identical endpoint string. Payload/lookup only; `grep -- '--jq .id'` passes
  vacuously (source carries the two-argv form) — source: MF-1
- **Feature B, both halves** — extracting the `blocked_by` write and parent read is IN, `gh-sync.py`
  *calling* either is OUT — source: grilling, pinned by SC-06
- **Re-probing closure semantics** / **asserting on `sub_issues_summary` post-write** — DEC-168.
  **Retrofitting FEAT-01/FEAT-02/kaya's FEAT-03** — new features only — BRIEF `## Constraints`.
  **visual-designer / ui-reviewer** — no visual surface, no DESIGN.md — `skipped_segments`, Q4

## Working set

- `.harness/features/FEAT-03-subissue-mirror/PLAN.md` (`## Preconditions` first) and `BRIEF.md`
- `runs/2026-07-31-06-eng/digest.md` (cycle-2 receipts) and `runs/2026-07-31-05-product/digest.md`
- `.claude/skills/harness/bin/{gh-sync.py,wayfind.py,test-gh-sync.py}`
