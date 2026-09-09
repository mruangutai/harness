# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c17 validate — `runs/c17-validator/` (validator lead, qa matrix + review panel, **PASS**) and
  `runs/c17gc-product/` (product lead, pm goal-check of SC-04 and SC-11, **ESCALATE**).
- squad: validator, then product. No source, test, `BRIEF.md` or approval file changed by either.
- station: **review** (`plan.yaml` `status:`), T-05 `done`. T-05's `done` was written by the main
  session (it is `execution_mode: main-session-direct`); the feature station and the mirror write
  were mine, as the phase owner.
- `review_sha`: **re-pinned to `94b5e465d498a9943890734223e69c390b0a77ad`** before any validator ran
  (INV-6) — that is the commit carrying the parser fix, and it is what the panel and the goal-check
  graded. **Moved forward to `b5eb8f8e95bfa2d6d3bbf664a07fe70cdd9ed3d7`** after this round's record
  commit, because that commit writes the feature station into `plan.yaml` and INV-33 compares the
  plan at the pin against the plan on disk. The move is free and changes nothing that was reviewed:
  `git diff --name-only 94b5e465..b5eb8f8e -- ':!<feature-dir>'` is EMPTY — every path in that range
  is this feature's own record.
- mirror: `gh-sync.py status <feature-dir> review` ran — parent #1407 and all nine sub-issues
  (#1408-#1416) are at review.
- budget: **`cycles_used` 15 of `max_total_cycles` 16 — NOT incremented.** Both leads reported ZERO
  send-backs, no FAIL was routed back and no unmet SC was re-dispatched (DEC-157: cycles count
  rework, and a goal-check that reports a gap it is forbidden to fix is not rework). `len(runs)` 50
  of `max_total_runs` 20 — INFORMATIONAL (INV-22). The count is high because this feature has run
  fourteen remediation and grading cycles; the recent ones each closed a named defect, and this one
  closed the c15 parser blocker.

### The c17 result — the fix is clean, one criterion is short of EVIDENCE

- **Panel c17: PASS.** `severity_max: low`, `must_fix: []`, `matrix_ok: true`, all four reviewers ran
  (ui scoped out on a measured census, and said so). 39/39 end-to-end probe forms deny on an owing
  fixture; a 27-case adversarial sweep found no surviving bypass; the four graded helpers score
  `git_merge` 4, `option_end` 5, `first_subcommand` 5, `merge_target` 4.
- **SC-11: MET.** Its three case names pass individually (run lines 32/33/34) and each reddens
  individually against `git show e374c9a2:.claude/skills/harness/bin/merge-gate.py`
  (`notes/qa-c17.md:50-63`).
- **SC-04: UNMET on EVIDENCE, not on behaviour.** Three of its ten clauses are carried by no
  automated case, and SC-04's declared method is `automated`. All three verified on disk by the
  orchestrator at the pin, not taken on the digest's word:
  - **Gap A** — no single-owner receipt deny asserts the feature id. `:65` asserts the state, `:67`
    the re-run command; the id assertion at `:126-127` belongs to the fail-closed deny, a different
    string that carries no command. The conjunction SC-04 states is unasserted.
  - **Gap B** — the ambiguity-before-era-gate ordering has no case: neither duplicate claimant
    (`FEAT-9001-fixture-non-era`, `FEAT-9002-fixture-duplicate`) is in `BUILD_ENTRY_ERA_EXEMPT`
    (0 matches). The ordering holds in source (`merge-gate.py:172` before `:179`) — that is
    inspection.
  - **Gap C** — of the four noise kinds the clause enumerates, only *non-object* is exercised: the
    two "noise" cases use byte-identical `json.dump([])` fixtures
    (`test-merge-gate.py:128-135` and `:163-170`). No unreadable record (the `OSError` arm), no
    malformed JSON text (the `JSONDecodeError` arm), no different-branch record beside a live owner.
- **The c15 SC-04 blocker is CLOSED**: `--attr-source` now denies, and `git --exec-path <p> merge`
  is unreachable because real git prints the exec path and never runs the subcommand.
- **UAT Step 3b was NOT amended** — correctly gated off by its own precondition, since SC-04 came
  back unmet. The script is byte-unchanged.

### Next, in order — the operator decides the first step

1. **Operator ruling on SC-04's three gaps** (blocking). Three options, none of them the
   orchestrator's: accept the gaps with a recorded ruling on inspected-correct behaviour; carry them
   as a follow-up bug; or authorise ONE additive test-only cycle on
   `tests/integration/test-merge-gate.py` — which takes `cycles_used` to 16 of 16, the cap, and
   touches no production source.
2. Then the UAT Step 3b amendment — one pm spawn through product lead, adding the `-F`,
   `--cleanup strip` and global `--attr-source` forms measured as denies at this pin
   (`notes/qa-c17.md:66-73`), and moving its PASS rule from three lines to six.
3. Then the operator's SC-10 hand test of `notes/uat-BUG-1309-mirror-build-entry.md`.
4. Then the rewritten briefing, then the ship decision. The stale briefing at
   `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still await disposition.

## Open Questions

- Q1 (blocking, operator) — **SC-04's three evidence gaps at an exhausted budget.** Behaviour is
  inspected-correct at `merge-gate.py:138/172/179/192`; the gap is that no automated case asserts
  clause g, three of clause h's four noise kinds, or clause a's feature-id half. Accept, defer, or
  spend the last cycle test-only.
- Q2 (non-blocking, backlog) — T-05's `verify:` grade assertion takes `min(grade)` over
  `git_merge`/`words`/`direct_merge`/`gh_merge` and never names `option_end`, `first_subcommand` or
  `merge_target`, the three helpers this delta introduced. Satisfied in fact (5/5/4); the mechanical
  assertion would not catch a future regression of those three. The remedy edits approval-gated
  `plan.yaml`.
- Q3 (non-blocking, backlog) — `merge_target` matches `--abort`/`--continue`/`--quit` by exact token
  equality, while git's parse-options accepts unambiguous long-option abbreviation, so
  `git merge --abo` would be classified as a merge and DENIED. Direction is over-deny, never a
  bypass, and SC-11 pins the three literal spellings. **Partly measured**: `git tag --lis` succeeds
  in this repo's git, so parse-options abbreviation is real; `git merge --abo` itself is
  unmeasurable from inside a run because `bash-write-guard.sh` refuses the command name.
- Q4 (non-blocking, harness defect, third sighting) — a member spawn returned a complete, well-formed
  fenced digest as its final assistant text while the host recorded `failed (exit 1) — subagent
  called yield with null data`. Seen on the c17 panel qa step, the c15 ui step and two pm runs. A
  lead routing on the exit code alone discards a PASS carrying 39 measurements.
- Q5 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21 names
  while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration.
- SC-10 UAT is still NOT requested and still blocks the ship.
