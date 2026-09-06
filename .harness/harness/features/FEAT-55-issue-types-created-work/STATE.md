# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-32-validator/digest.md
- squad: validator
- status: in_review
- station: review (plan.yaml `status: review`; plan `approval.status: approved`, BRIEF `## Approval`
  approved — both fragments signed 2026-09-05 by molchairuangutai and byte-intact after the
  amendment, re-verified by me on disk)
- mission: validate — COMPLETE. Ready for the operator's ship decision; nothing waits on me.

- all four operator rulings (`notes/answers-build-blockers-20260905.md`) are applied, none costing a
  cycle. F-04: budget raised by me to 13/40. F-01+F-02 plan half, run `2026-09-05-29-product` PASS:
  pm amended T-04's `files:` to `[gh-sync.py, feature-schema.json, tests/integration/test-gh-sync.py]`
  and its `intent`, and added D-21/D-22. `plan-merge.py amend`/`apply` preserve approval bytes by
  construction (BUG-1128), so NO re-signature was required and none was taken. F-01+F-02 code half,
  run `2026-09-05-02-eng` PASS: both `typed` mappings declared on the closed `github` and `factory`
  schema objects; `+ ["--repo", repo]` and its false comment removed from the capability query;
  test-gh-sync.py's assertion now accepts an `api graphql` line only with the exact `owner=implentio`
  AND `name=fake` values. F-03: SC-10 graded MET on the ruling; the optional live probe is backlog
  row B-1 in the briefing and nowhere else.

- gates, all green, measured by me per file with its own exit code and `^FAIL ` count — never a tail
  read, because a truncated capture already produced one false green here. The ten FEAT-55 suites
  (test-anchor-directions, test-issue-types-pin, test-issue-types, test-gh-issue-types, test-gh-sync,
  test-gh-backlog-issue-types, test-factory-issue-types, test-factory-decompose, test-factory-gh,
  test-factory-integration) every one exit 0 / FAIL 0; `.claude/skills/harness/bin/run-unit-tests.sh`
  exit 0 / FAIL 0 with the status captured in a variable; `code-grade.py --base eb9d044e --head
  76ba5f41` zero `SEVERITY: high`.

- qa, run `2026-09-05-01-validator`, FAIL → resolved, 1 cycle. The blocking matrix was red on
  test-anchor-directions.py: T-12's new prose in `.claude/skills/harness/references/github-mirror.md`
  carried unanchored instruction paths at :19 and :24. I confirmed it (exit 1, two violations) and
  `check-domain.sh --resolve` answered NOBODY — no squad, not me. The main session landed the fix;
  I committed it and the gate went green.

- SIMPLIFY, run `2026-09-05-03-eng`, PASS, 0 cycles. Reuse 0 findings (the D-11 extraction held
  across all three callers), efficiency 0 apply-worthy, 4 low from the other two angles, one
  behaviour-preserving fold-in applied to `gh_issue_types.py`.

- panel, run `2026-09-05-30-validator` at pin `cd6a3c0d`, FAIL — ONE gating finding, and it was
  real: `factory_decompose.write_factory.transform` graded 3 (ABC 20.5) in a bar-4 zone because THIS
  diff's `"typed"` serialization line carried ABC past 20. I checked the premise with the repo's own
  grader before spending the last cycle; it held. qa PASS, security PASS (one low in T-10's probe),
  ui PASS after looking rather than declining blind.

- fix, run `2026-09-05-1-eng`, PASS, the 13th and last cycle. `_factory_block` extracted; `transform`
  now GRADE 4 / ABC 9.0 and the helper GRADE 4 / ABC 14.1 — it did not merely move the mass, which
  is the specific way that remedy fails. Also corrected `probe-issue-types.py`'s comment asserting
  gh-sync still appends `--repo` — falsified by D-22, twin of the one F-02 ordered deleted.

- re-check, run `2026-09-05-32-validator`, PASS. Scoped to the two-file delta, routed to the reviewer
  that raised the finding. Its own measurement: must_fix closed, extraction key-for-key
  behaviour-preserving, comment accurate, suites green, nothing new. qa/security/ui verdicts are
  INHERITED across that delta and the lead said so rather than hiding it.

- goal-check, run `2026-09-05-31-product`, PASS. Twelve of twelve SCs MET at the pin, REQ-01..REQ-11
  all traced to verified tasks, nothing routed to a fix cycle.

- budget: `cycles_used` 13 of 13 — SPENT. `runs` 40 of 40 — at the informational bound (INV-22),
  high because this plan was signed through five rounds of rulings instead of one. This session's
  eight runs closed two rulings, four quality angles, a four-reviewer panel and the goal-check.

- committed on `feat/issue-1289-issue-types` at `73ec0c64`; `review_sha` pinned at `76ba5f41`, and
  `git diff 76ba5f41..HEAD -- .claude tests` is EMPTY, so the pin holds every reviewed line and the
  commits after it are feature-record only. No merge, no PR.
- briefing: `notes/ship-review-2026-09-05-02-eng.md` (+ rendered `.html`), sixteen-row proposed
  backlog. SUPERSEDES `notes/ship-review-2026-09-05-01-eng.md`.
- handoff: `notes/handoff-validate.md`; `notes/handoff-build.md` superseded.
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)

## Open Questions

No blocking questions. One refusal I chose not to work around, harness defects raised rather than
worked around, and one non-gating ratification.

- Q14 (harness defect, why the mirror is behind) — `gh-sync.py status <dir> review` REFUSED: "not
  every task in plan.yaml is done or abandoned". Correct that none reads done — this plan's tasks
  carry no `status:` key and `set-task-station` only SPLICES an existing line (Q5). I did NOT work
  around it: writing plan content outside `plan-merge.py` is what D-04 forbids. Never a gate.
- Q17 (NEW; the concrete instance of the unrepairable-digest defect) — FIVE FEAT-55 run digests fail
  the lead contract and `check-state.sh` reports each as a VIOLATION: `2026-09-04-03-product`,
  `2026-09-04-11-validator`, `2026-09-05-c5-validator`, `2026-09-05-26-validator` (all pre-existing,
  plan phase) and `2026-09-05-30-validator` — the review panel's own run, whose lead emitted a valid
  fenced contract in its RETURN and wrote a file without one. That file's prose record is complete
  and honest; only the machine fence is absent. I did not repair it: a digest cannot be repaired in
  place, the budget is spent, and retyping 6.7 KB of another agent's record to satisfy a parser
  risks corrupting a good one. The runs tree is gitignored, so all five die with this worktree at
  merge, and the panel's verdict is preserved above and in the briefing.
- Q3 (operator, non-blocking) — T-06 §5 specifies the backlog receipt nested under `items`, but
  T-05's red test seeds and reads those keys at the top level and T-06 had to make it green
  unedited, so the on-disk receipt is FLAT. Ratify it or correct the prose; behaviour is unaffected.
- Q4 — `bash-write-guard.sh` blocked `cp` onto a file outside my domain but NOT `python3 -c` writing
  the identical path in the identical call. It reads the command line for write verbs, not syscalls.
- Q5 — `set-task-station` records no station on a status-less plan, and misreports the cause as
  `T-01 is not in <file> — it carries: T-01, T-02`, naming the task it just called absent.
- Q6 — a truncated capture of the unit driver produced a FALSE GREEN. Captured output cannot be read
  for absence of failure.
- Q7 — the documentor's `Edit` resolved a relative path against the process cwd, not the dispatch
  worktree, briefly writing into the MAIN checkout. Detected, reverted, confirmed clean twice.
- Q12 — backend-dev's `Edit` on `tests/integration/test-gh-sync.py` reported success and issued a new
  snapshot tag while never reaching disk; a re-read returned pre-edit content and an identical retry
  was rejected as byte-identical. It landed by another route; I verified the content at source.
- Q13 — TWO agents wrote their checkpoint into `runs/2026-09-05-01-product/`, an older run's
  directory, because the runs tree is gitignored so a `Glob` returns nothing and a live directory
  reads as free. `check-domain` refused the `digest.md` write both times and allowed `state.yaml`
  both times. Unrecoverable; spent archive artifacts only, and both runs' digests survived.
- Q15 — the handoff shape gate resolves a `## Done when` authority pointer's relative path against
  the MAIN checkout root, not the worktree the note is written in, so `brief-sc:` and `plan-task:`
  cannot resolve from inside a worktree and every `finding:`/`approval:` pointer needs a
  `.claude/worktrees/<...>/` prefix duplicating the feature path.
- Q16 (advisory, non-gating) — `probe-issue-types.py:97-101` `_read_back_issue_type` `%`-formats
  owner and name into GraphQL query TEXT rather than passing `-f owner=`/`-f name=` as every other
  call site does. Reachable only behind the operator's `--create-in` flag on a host-only probe, so
  nothing crosses a boundary; unsafe the moment it gets an externally-sourced caller. Backlog B-9.
- Q8, Q10, Q11 (carried from the plan phase) — `validate-digest.py` rejecting `code_grade: n_a` on a
  plan review; the `harness-spec-driven` verb list omitting `amend`; `amend --key` accepting only
  `tasks|decisions`.
