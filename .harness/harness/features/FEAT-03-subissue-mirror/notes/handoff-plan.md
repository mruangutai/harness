# Handoff — FEAT-03-subissue-mirror, plan → build — written at a8fce12, seq-4 (supersedes seq-3)

## Next

**Wait for the user's signature, then start the build phase.** Fix cycle 3 is CLOSED (runs 07/08 PASS,
zero `must_fix`); both `## Approval` are `status: pending`, which stops a build mission at step 0. On
signature, build T-01..T-08 in PLAN order, reading PLAN `## Preconditions` FIRST — one is an outstanding
**main-session** edit (`SKILL.md:137,144`, SC-13) no agent domain covers, and **T-08's owner
harness-documentor is PRODUCT squad**, routed via product-lead (Q8). **SC-13's bar rose (Q13):** that
ship row must not assert an unconditional parent close either.

## Trust

- Both `## Approval` still `status: pending` — greped at BRIEF:233 / PLAN:653, NOT trusted from line
  numbers, which moved as SC-04 and T-06 grew — verified-at a8fce12
- **`ship` is now conditional, symmetric with `abandon`**: `created` → close `completed`, `adopted` →
  open, absent origin → open. **The milestone still closes unconditionally** — only the parent branches.
  Six sites changed, not the two Q15 named: BRIEF Goal prose, REQ-04, SC-04, **SC-13's second clause**,
  T-06 (heading/intent/verify), **T-08's am.7 instruction text** — greped pre-dispatch — verified-at a8fce12
- **eng-lead reproduced the absence-greps FIRST-HAND** (run 08, `must_fix: []`): all seven new T-06 labels
  and the retired `ship closes parent then milestone` count 0; `:185` is the retained `ship PATCHes
  milestone closed`, not `:186`; and both leave-open fixtures assert absence in BOTH close forms
  (`issue close 40` AND `PATCH repos/*/issues/40`), so the MF-1 one-form class did not recur — run 08 digest
- **A fourth T-06 label guards an over-correction:** `ship closes the milestone regardless of parent
  origin`, in the ADOPTED fixture — one `if origin == "created":` over both the parent close and the
  milestone PATCH would otherwise pass every other label. No new task, no new SC — run 08-eng digest
- **The comment step is UNCONDITIONAL by design** — `--body-file` posts on any recorded parent regardless
  of origin (T-05 step 1 is identical). Do not "fix" it — verified-at a8fce12
- **No new `D-NN`**; D-01 now governs BOTH terminal subcommands. D-NN 6, tasks 8, SC 13, and `f929d44`
  still the valid code anchor (`git diff --stat f929d44 HEAD -- .claude/skills/harness/bin` empty;
  `observed @` greps 27, `observed @f929d44` also 27) — all re-run — verified-at a8fce12
- **Cost OVER budget: ~$162 of $120, by ~$42** (DEC-134: never gates). This cycle $21 ($16 + $5) — run
  07/08 `cost.run_usd`, P-01 snapshot deltas; the rest is prior cycles plus orchestrator session share
- Mirror invariants hold only against the fake `gh`; the live API path rides on DEC-168's probe — UNVERIFIED

## Dead ends

- **Reopening Q15 or the grilling** — `ship`'s conditional is settled and re-verified; the close FORM for
  the `created` case stays `gh issue close <parent>`, not a PATCH — source: user, this cycle; run 08
- **Re-anchoring PLAN:20-24 to a live HEAD** — it names `1ce886a` as the PINNED review baseline on
  purpose; re-anchoring reproduces the rot next commit — source: orchestrator, this cycle
- **Editing `DECISIONS.md`** (historical record) **or `SKILL.md`** (the main session's step, SC-13), and
  **renaming the dir or slug** (DEC-133, breaks eight run dirs) — source: user, Q6
- **Fixing Q17** (four PLAN sites cite `feature.yaml:41` for `parent: none`; it is now `:61`) — the fact
  asserted is true everywhere, so it is cosmetic; cite the FIELD not a line, and only if a cycle opens
  anyway. **Changing the task count / merging T-05+T-06** — held at 8 through three cycles, and the
  decomposition is the premise of the signature. **The ~3 prose "mirror" survivors** — one is correctly
  the relationship claim — sources: eng-lead run 08; orchestrator cycles 1–3; user, this cycle
- **Path-level greps for SC-06** — self-voiding: retained list GETs and extracted writes build the
  identical endpoint string; payload/lookup only (MF-1). **Feature B** — extracting the `blocked_by`
  write and parent read is IN, `gh-sync.py` *calling* either is OUT (grilling, pinned by SC-06).
  **Re-probing closure semantics** / **asserting on `sub_issues_summary` post-write** — DEC-168.
  **Retrofitting FEAT-01/FEAT-02/kaya's FEAT-03** — new features only. **visual-designer / ui-reviewer**
  — no visual surface, no DESIGN.md — `skipped_segments`, Q4

## Working set

- `.harness/features/FEAT-03-subissue-mirror/PLAN.md` (`## Preconditions` first) and `BRIEF.md`
- `runs/2026-07-31-08-eng/digest.md` (cycle-3 receipts), `runs/2026-07-31-07-product/digest.md`, and
  `.claude/skills/harness/bin/{gh-sync.py,wayfind.py,test-gh-sync.py}`
