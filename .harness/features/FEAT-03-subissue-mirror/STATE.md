# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-08-eng/state.yaml
- squad: eng
- status: awaiting-user
- phase: plan — at the approval gate, this phase's exit predicate (DEC-148). Fix cycle 3 closed PASS;
  BRIEF and PLAN are repaired, re-verified and sign-ready.
- note: **Fix cycle 3 (`cycles_used: 3`, DEC-157)** — the user authorized the Q15 fix the previous cycle
  raised and deliberately left unfixed. pm applied it (run 07-product PASS, no send-back); eng-lead
  re-verified per-item (run 08-eng PASS, `must_fix: []`, no send-back, no member spawn).
  **THE CHANGE — `ship`'s parent close was the mirror image of the abandon defect cycle 2 fixed.** T-06
  and SC-04 closed the parent unconditionally as `completed`; for an ADOPTED parent that asserts the
  user's live backlog item is done, exactly as false as closing it `not_planned` would have been. Now
  conditional on `github.parent_origin` (D-01), symmetric with `abandon`: `created` -> close `completed`,
  `adopted` -> leave OPEN, absent/`none` -> leave OPEN (the specified default, for abandon's stated
  reason — SC-10 bars editing existing `github:` blocks so pre-existing features carry no marker, and the
  false assertion is the strictly worse error). **The milestone still closes unconditionally; only the
  parent's fate branches.**
  **Six sites carried the unconditional claim, not the two Q15 named** — greped before dispatch: BRIEF
  Goal prose, **REQ-04** (falsified as written by the adopted case), SC-04, **SC-13's second clause**
  (the criterion telling the main session what to write into `SKILL.md` — it would otherwise have gone
  green on prose asserting the unconditional close), T-06 (heading + intent + `verify:` labels), and
  **T-08's DECISIONS am.7 instruction text**, which would have written the old behaviour into the
  permanent record. SC-11 was checked and is clean: it enumerates only the am.1 reversal.
  **The test assertion split, which was the reason for the cycle.** The single label "ship closes parent
  then milestone" is retired; three fixtures now, mirroring T-05: `ship closes a created parent
  completed` / `ship leaves an adopted parent open` / `ship leaves a parent with no recorded origin open`.
  The two leave-open fixtures assert absence in **both** close shapes (`issue close 40` AND
  `PATCH repos/*/issues/40`) — the MF-1 one-form class, which already burned this feature once.
  **pm caught an over-correction the brief did not name, and eng-lead confirmed the guard discriminates.**
  One `if origin == "created":` wrapping both the parent close and the milestone PATCH would pass all
  three parent labels and the retained `ship PATCHes milestone closed`, and nothing else would catch it.
  pm added a fourth label — `ship closes the milestone regardless of parent origin`, emitted inside the
  ADOPTED fixture, so the over-scoped guard suppresses the PATCH in exactly the fixture that asserts it.
  Adds no task and no SC; admitted as blocking-and-introduced-by-this-repair. The comment step correctly
  stayed **unconditional**: `--body-file` posts on any recorded parent, because commenting on an adopted
  issue asserts nothing false (T-05 step 1 has the identical shape).
  **No new `D-NN`** — D-01's note was extended to say the recorded origin governs BOTH terminal
  subcommands, using cycle 2's precedent sentence ("D-01's recorded-never-discovered applied to a field
  D-01 already owns"). eng-lead upheld it: a D-07 would split one rule across two decisions and make the
  symmetry easier to break. D-NN 6, tasks 8, SC 13 — all re-greped.
  **eng-lead reproduced the absence-greps FIRST-HAND** rather than relaying pm's, as in run 06: `ship`
  greps exactly 3 lines in `test-gh-sync.py` (`:181`, `:183`, `:185` the retained milestone assertion),
  all seven new T-06 labels count 0 and the retired label counts 0; `parent_origin` counts 0 in
  `gh-sync.py` with no `def cmd_abandon`, so no code could compose those strings. It also verified the
  absent-origin fixture's premise itself — `save_recorded` is called only at `gh-sync.py:208,228,230`,
  all inside `cmd_open`, none at or after `cmd_ship:267` — so pm's claim is its own, not T-05's copied
  blind. Receipts were taken via `python3 test-gh-sync.py`; `run-unit-tests.sh` lands with T-01.
  **Q16 closed:** PLAN:20-24 names `1ce886a` the **pinned review baseline** rather than "the current
  HEAD" — pinned, not re-anchored, so the rot does not reproduce on the next commit. Byte-identity
  stands: `git diff --stat f929d44 HEAD -- .claude/skills/harness/bin` empty at HEAD `a8fce12`, and
  `observed @` greps 27 with `observed @f929d44` also 27, so no receipt moved.
  Both `## Approval` blocks still `status: pending` (BRIEF:233, PLAN:653 — greped, not trusted from the
  moved line numbers); only the main session signs. `DECISIONS.md` has 0 `amendment 7`, `SKILL.md:137,144`
  still carry the superseded wording (1 match each, SC-13's subject), everything under `bin/` untouched,
  no existing feature's `github:` block edited (SC-10).
  **Cost is OVER budget: ~$162 of $120, by roughly $42.** Reported, never gated (DEC-134). This cycle
  cost $21 ($16 product + $5 eng); the overrun is dominated by prior cycles and this orchestrator's own
  session share, approximate because a second depth-1 orchestrator shares the transcript. Segments 1b
  and 3 remain skipped. Q15 and Q16 are CLOSED — recorded in `feature.yaml resolved:`.

## Open Questions

- Q17 (NEW, eng-lead, non-blocking, cosmetic) — **four PLAN sites cite `feature.yaml:41` for
  `parent: none` and the line has moved twice** (to `:54` during this cycle's review, then to `:61` when
  the orchestrator recorded run 08 — proof the anchor class is inherently unstable, not that one number
  is stale). Sites: PLAN `:88`, `:464`, `:479`, `:529`; three pre-date this repair, one rode in with it.
  The asserted FACT is true in every case (this feature has no recorded parent), so nothing is falsified
  and it failed the blocking-and-introduced bar. Fix by citing the field (`feature.yaml github.parent`)
  rather than a line, in one pass, if a cycle opens anyway.
- Q13 (for the user at signature) — **SC-13 is a success criterion only the user can satisfy.** Its
  subject (`.claude/skills/harness/SKILL.md:137,144`) is covered by no agent domain; MF-5's remedy rests
  entirely on that edit, eng-lead having accepted a softening of its run-02 wording (the
  `<!-- stale: -->` marker became optional, with SC-13's ship-gate grep substituted as the detection
  mechanism). **Fix cycle 3 raised this clause's bar:** SC-13 now also requires that the `SKILL.md` ship
  row NOT assert an unconditional parent close, so the pending edit's wording must carry the conditional.
  If the edit is not made before ship, SC-13 is unmet at goal-check, the gap can be routed to no lead,
  and the feature goes BLOCKED on a criterion the plan always knew was un-owned. Named at PLAN
  `## Preconditions`. Distinct from Q1, which predates SC-13's existence.
- Q14 (orchestrator, harness defect) — `bash-write-guard.sh` scans the WHOLE bash command string,
  including quoted and heredoc CONTENT, and reads any `>` in it as a shell redirect. Three distinct hits:
  the mandated `Co-Authored-By: ... <noreply@anthropic.com>` trailer in `git commit -m`; an arrow inside
  heredoc PROSE; and a third heredoc that reported "targets GitHub". The workaround is not "avoid one
  trailer" but "avoid `>` in ANY bash prose": commit messages get written to a file and passed via
  `git commit -F`, and edit scripts must not carry arrows in their text. A rule backfiring on content it
  should not be parsing, not a workaround to keep.
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
- Q8 (eng-lead) — T-08's owner harness-documentor is in the Product squad; the build segment needs
  lateral routing through product-lead, eng-lead cannot spawn it.
- Q9 (eng-lead) — no `build` team yaml exists (only gate-probe.yaml, review.yaml); pre-existing gap
  that the build phase hits.
- Q10 (orchestrator, harness defect) — check-state.sh infers a cycle from any FAIL run, so it fired
  a VIOLATION on the legitimate "FAIL held at the user gate" state DEC-157 defines as zero cycles.
  Moot now `cycles_used: 3`; the over-approximation is still a defect. Also asymmetric: a pending
  PLAN is a `note`, a pending BRIEF is a VIOLATION — yet a plan mission ends with both pending.
- Q11 (orchestrator, harness defect) — the playbook's `cost-report.py --yaml >> <run_dir>/state.yaml`
  append produces a duplicate top-level `cost:` key beside the lead's `cost: pending_orchestrator`,
  which check-state.sh rejects per DEC-156. The obvious fix (renaming the placeholder to
  `run_cost_usd:`) is ALSO rejected — `CHECKPOINT_KEYS` (check-state.sh:258-268) admits only `cost`,
  so the metered figure must nest as `cost.run_usd`. Hand-resolved that way in all eight run dirs;
  the playbook instruction and the invariant still disagree.
