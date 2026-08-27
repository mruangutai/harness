# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: .harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-26-02-product/digest.md
- squad: none — plan SIGNED, build not started
- status: ready-for-build

**PLAN AND BRIEF ARE APPROVED, 2026-08-27, by the operator. FIVE tasks: T-01, T-02, T-04, T-05,
T-06. Runs 8 of 20, cycles 0/10.**

**ONE TASK WAS STRUCK AT SIGNATURE, with REQ-08 and SC-09.** It would have restored the
orchestrator tier's own never-wait rule, which `c5e59aa` deleted one tier up. The operator ruled the
lead-tier rule ships sooner without it. **The strike record is `plan.yaml` D-12** — that is the
authority, and the struck id is named there rather than here, because a live STATE.md may not cite a
task its plan no longer holds. The knock-on is applied: T-01 dropped its `orchestrator` group and
that group's line from its verify block. Task numbering is NOT compacted, so every citation to T-04
and later still resolves. The regression is real and returns to the backlog.

**THE FALSE ATTRIBUTION IS CORRECTED.** `plan.yaml` D-12 and `BRIEF.md`'s scope section claimed the
REQ-08 restore was the operator's own scope call. It was not — the operator delegated that call at
re-plan and the orchestrator took it, then labelled its own choice as the operator's. Both documents
now record that plainly, and the operator ruled on it for the first time at this signature.

**`origin/main` WAS MERGED IN BEFORE THE SIGNATURE, and that was not routine.** The worktree sat
**20 commits behind** — FEAT-42 had landed. Signing against a stale tree is exactly what forced the
first withdrawal. Merge was clean, and every anchor was re-measured on the merged tree: the refusal
sentence T-04 rewrites survives verbatim, DEC-174 amendment 4's write grant is at `DECISIONS.md:5011`,
`DECISIONS.md` holds 201 level-two `DEC-` headings against 28 level-three, and the never-wait
paragraph is still absent from the orchestrator playbook.

**TWO PARAGRAPHS WENT FALSE WHEN FEAT-42 LANDED; ONE IS FIXED HERE.** T-04's intent said
`refusal_lines` cites issue 551 where 866 measures 628, held deliberately out of scope. **FEAT-42
already fixed it** — at `origin/main` that function cites 628, and `RELEASE_ALL_CMD` is retired as a
printed remedy in favour of `release_cmd`, which is absolute and single-agent. T-04's paragraph is
rewritten to say so; the instruction not to touch that function is unchanged.

**BUILD ORDER.** T-01 alone first — it is the test file every other task's `verify:` calls, and
nothing can be graded until it exists. T-02, T-04, T-05 and T-06 follow in plan order.

## Open Questions

- Q1 (was: D-02 and D-11 spell the ruling AMEND) — RESOLVED at re-plan. Both now read "corrected IN
  PLACE". The only `AMEND` strings left in `plan.yaml` are T-05's and T-06's own DO NOT ADD AN
  AMENDMENT instructions.
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Corrected in place. D-11 and T-06 carry the reasoning.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. D-07 is the strike
  record. Issue #811 stays OPEN and returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6 (the #866 deadlock) — HALF CLOSED BY FEAT-42, and the note that said otherwise is now corrected.
  The dispatch end is fixed: `release_cmd` prints an absolute single-agent command, so a refusal no
  longer tells an agent to wipe every feature's live claims. The RETURN end is what T-04 still
  corrects. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
