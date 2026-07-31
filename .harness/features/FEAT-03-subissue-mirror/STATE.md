# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-06-eng/state.yaml
- squad: eng
- status: awaiting-user
- phase: plan — at the approval gate, this phase's exit predicate (DEC-148). Fix cycle 2 closed PASS;
  BRIEF and PLAN are repaired, re-verified and sign-ready.
- note: **Fix cycle 2 (`cycles_used: 2`, DEC-157)** — the user read the sign-ready BRIEF/PLAN and found
  a defect the architecture review missed, plus ordered a terminology rename. pm applied both changes
  (run 05-product PASS, no send-back) and eng-lead re-verified them per-item (run 06-eng PASS, zero
  `must_fix`, no send-back, reviewed directly with no member spawn).
  eng-lead reproduced the discriminating greps FIRST-HAND rather than relaying pm's: over
  `.claude/skills/harness/bin/`, `parent_origin` and `abandon` both count ZERO, so all nine T-05 labels
  and the retired label are provably absent from today's suite output — the MF-1 void-absence-grep class
  did not recur. It also confirmed `^\s*parent:\s*(\d+)` cannot false-match `parent_origin:` (the
  `\s*` sits after the colon literal and is never reached; `_` is not whitespace), closing the
  silent-corruption path, and upheld pm's one judgment call on D-05 ("never a gate" is failure
  semantics, not the derivation claim, so the noun was correctly renamed there).
  **CHANGE 1 — parent-on-abandon was wrong for one of D-01's three origins.** SC-03 and T-05 step 4
  said `abandon` leaves the parent OPEN unconditionally. True for the two adopted origins; false for
  a parent `open` CREATED, which exists only to hold this feature's tasks and would be orphaned open
  with every child closed `not_planned`. Root cause: the grilling settled "leave the adopted parent
  open" when adoption was the only origin under discussion; D-01 later added the created case and
  SC-03 inherited the unconditional wording. Now conditional: adopted -> open, created -> close
  `state_reason: not_planned`, **absent origin -> open** (the specified default — closing an adopted
  issue asserts something false, strictly worse than orphaning a created one, and SC-10 bars editing
  existing `feature.yaml` `github:` blocks so pre-existing features carry no marker).
  The receipt is a T-03 change: `  parent_origin: created|adopted|none`, a two-space-indent sibling
  key written before `  issues:` at the moment `open` writes `github.parent` — without it the
  distinction is undecidable at abandon time and re-deriving it would need a GitHub read (DEC-138
  forbids). Chosen to leave the `parent:` line shape alone so T-07's INV-21 needs no edit.
  **Four sites carried the unconditional claim, not the two the task named** — I grepped: BRIEF SC-03,
  T-05 step 4's intent, T-05's `verify:` `ok` label, and T-08's DECISIONS am.7 instruction text. The
  single label "abandon leaves the parent open" split into three (adopted / created / no-origin), each
  with its own fixture; one prose mention survives at PLAN:491 documenting the retirement, by design.
  **CHANGE 2 — "mirror" is no longer the noun; "GitHub Issues" is.** The word stays only where the
  relationship is the assertion (write-only, never-composes, "a mirror of PLAN, never a source").
  BRIEF 19 -> 9 occurrences, PLAN 11 -> 7 (measured with `grep -o`; the task's handed-down 17/10 were
  approximate — the rule governs, not the count). Three are immutable slug occurrences: DEC-133 makes
  `subissue-mirror` unrenameable. `docs/harness/DECISIONS.md` and `.claude/skills/harness/SKILL.md`
  deliberately untouched.
  Decomposition held at T-01..T-08 (8 headings, verified) — the task count is the premise of the
  signature. T-06/SC-04 byte-unchanged. Both `## Approval` blocks `status: pending` (BRIEF:214,
  PLAN:599); only the main session signs. `review_sha` stays `1ce886a`; `f929d44` remains the valid
  code anchor (`git diff --stat f929d44..HEAD -- ':!.harness/'` is empty), so no receipt moved.
  **Cost is OVER budget: ~$141 of $120, by roughly $21.** Reported, never gated (DEC-134). Runs 05 and
  06 cost $24 and $7; the rest is this orchestrator's own session share, which is approximate because a
  second depth-1 orchestrator shares the transcript. Segments 1b and 3 remain skipped.
  One non-blocking spec tension eng-lead recorded for the implementing specialist rather than filing:
  PLAN:278 emits `parent_origin` unconditionally while PLAN:303-305 describes an unmarked parent. Both
  readings degrade to leave-open, since the reader recognises only `created`/`adopted`, so no state is
  corrupted either way.

## Open Questions

- Q15 (NEW, pm, non-blocking) — **T-06/`ship` closes the parent unconditionally as `completed`**
  (PLAN:499-522, SC-04) — the mirror image of the defect just fixed. Closing an ADOPTED backlog issue
  as `completed` asserts the user's live item is done, as false as closing it `not_planned` would have
  been. The `parent_origin` receipt this cycle adds makes the symmetric fix nearly free. Deliberately
  NOT authorized and not edited: the user's instruction scoped this cycle to two changes. Either a
  follow-up feature, or ship's unconditional close is intended and should be recorded as such.
- Q16 (NEW, pm, non-blocking, cosmetic) — PLAN:20 still names `1ce886a` as "the current HEAD" and it
  no longer is. The load-bearing byte-identity claim is still true, so no receipt is invalidated.
  Best fixed by the main session in the same pass that writes `## Approval`, not a member spawn.
- Q13 (for the user at signature) — **SC-13 is a success criterion only the user can satisfy.**
  BRIEF grew 12 SC -> 13 at cycle 1; SC-13 is the checkable form of REQ-09's second clause, and its
  subject (`.claude/skills/harness/SKILL.md:137,144`) is covered by no agent domain. MF-5's remedy
  rests entirely on that edit: eng-lead accepted a softening of its own run-02 wording (the
  `<!-- stale: -->` marker became optional, with SC-13's ship-gate grep substituted as the detection
  mechanism). Consequence if the edit is not made before ship: SC-13 is unmet at goal-check, the gap
  can be routed to no lead, and the feature goes BLOCKED on a criterion the plan always knew was
  un-owned. Named at PLAN `## Preconditions`. Distinct from Q1, which predates SC-13's existence.
- Q14 (orchestrator, harness defect, SCOPE WIDENED this cycle) — `bash-write-guard.sh` scans the
  WHOLE bash command string, including quoted and heredoc CONTENT, and reads any `>` in it as a
  shell redirect. Three distinct hits so far: the mandated `Co-Authored-By: ... <noreply@anthropic.com>`
  trailer in `git commit -m` ("redirect targets 1,"); an arrow `-> 0` inside heredoc PROSE
  ("redirect targets 0"); and a third heredoc that reported "targets GitHub". So the workaround is not
  "avoid one trailer" but "avoid `>` in ANY bash prose": commit messages get written to a file with
  the Write tool and passed via `git commit -F`, and edit scripts must not carry arrows in their text.
  A rule backfiring on content it should not be parsing, not a workaround to keep.
- Q1 (pm) — `.claude/skills/harness/SKILL.md:137,144` state the contract this feature reverses; no
  agent domain covers that file. ANSWERED IN PLAN, not closed: pm kept REQ-09 whole and named the
  SKILL.md edit as a main-session pre-ship step (PLAN `## Preconditions`, T-08), with SC-13 as its
  checkable form and the `check-docs.sh` consequence stated both ways. See Q13.
- Q2 (pm) — the BRIEF-H1 parent-title contract needs `.claude/skills/harness-brief/SKILL.md`;
  same uncovered-domain problem.
- Q3 (pm) — freezing an adopted wayfinding map issue's body at hand-off is settled in the grilling
  but scoped out of this BRIEF; nobody owns it.
- Q4 (pm) — prototype gate: pm judged NO prototype required (re-confirmed at cycle 1 — the surface
  is `gh-sync.py`/`wayfind.py`/`check-state.sh` behaviour plus a DECISIONS.md amendment, no
  end-user interactive surface), substituting for visual-designer, which never ran. Overridable.
- Q5 (pm) — PLAN adds an `attached:` receipt list to `feature.yaml github:`, a local-state schema
  addition the grilling did not name. eng-lead judged it safely writable under the regex constraint,
  with one sharp edge: the issues reader `^\s{4}(T-\d+):\s*(\d+)` would misread a nested form. Fix
  cycle 2's `parent_origin` key rides the same constraint and was shaped to clear it.
- Q6 (pm) — pm judges the slug `subissue-mirror` narrower than the feature; id not renamed, and
  DEC-133 makes it immutable now (re-confirmed at cycle 2 when the rename was scoped to prose only).
- Q7 (RESOLVED at 1ce886a) — budget raised 40 -> 120 by the user; now ~$111+ spent, see `## Current`.
- Q8 (eng-lead) — T-08's owner harness-documentor is in the Product squad; the build segment needs
  lateral routing through product-lead, eng-lead cannot spawn it.
- Q9 (eng-lead) — no `build` team yaml exists (only gate-probe.yaml, review.yaml); pre-existing gap
  that the build phase hits.
- Q10 (orchestrator, harness defect) — check-state.sh infers a cycle from any FAIL run, so it fired
  a VIOLATION on the legitimate "FAIL held at the user gate" state DEC-157 defines as zero cycles.
  Moot now `cycles_used: 2`; the over-approximation is still a defect. Also asymmetric: a pending
  PLAN is a `note`, a pending BRIEF is a VIOLATION — yet a plan mission ends with both pending.
- Q11 (orchestrator, harness defect) — the playbook's `cost-report.py --yaml >> <run_dir>/state.yaml`
  append produces a duplicate top-level `cost:` key beside the lead's `cost: pending_orchestrator`,
  which check-state.sh rejects per DEC-156. Refinement: the obvious fix (rename the placeholder to
  `run_cost_usd:`) is ALSO rejected — `CHECKPOINT_KEYS` (check-state.sh:258-268) admits only `cost`,
  so the metered figure must nest as `cost.run_usd`. Hand-resolved that way in all five run dirs;
  the playbook instruction and the invariant still disagree.
- Q12 (orchestrator, tree dirt) — RESOLVED at f929d44: `__pycache__/` and `*.pyc` ignored in both
  `.gitignore` and `templates/gitignore.snippet`, the tracked `.pyc` untracked, tree clean.
  This also discharges MF-6.
