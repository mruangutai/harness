# BRIEF — FEAT-23 Ship-flow fixes

## Problem

**Three things go wrong in the ship-and-plan sequence. Two are at the end of every feature and have
now happened three times each; the third is at the very start, and the operator has been papering
over it by hand.**

*Shipping leaves the record wrong.* `gh-sync.py ship` closes the parent issue and the milestone, so
the board card lands in Done — while `feature.json` still reads a pre-terminal status. INV-26 then
compares a board that says Done against a plan that derives Review, and the first gate run on merged
`main` is red. Measured on FEAT-20, FEAT-21 and FEAT-22; each needed a one-field follow-up pull
request to clear it (FEAT-22's was PR #452, commit `6f7a5fd`, `"status": "Review"` → `"Done"`).
The same gap exists on the abandon path: nothing in the repository writes `"Abandoned"` at all,
though the invariant exempts it. Issue #417.

*The quality pass arrives too late to change anything.* The four-angle simplify pass has been run
twice at the wrong point in the sequence, and each time its findings could not be applied. On
FEAT-20 it ran after the validator's PASS at `6296149`; the apply commit moved the tip, invalidated
the pinned verdict, and cost a third validator round. On FEAT-22 it ran after the operator's
signature; **zero** of its findings could be applied, and four binding notes now ride beside the
signed text instead of inside it (`notes/simplify-pass-2026-08-16.md`). The methodology itself lives
only in one session's dispatch prompts — nothing in the repository carries it, so it cannot be run
without the operator reconstructing it. Issue #430.

*The board never shows that planning is happening.* A ticket sits in `Backlog` while its feature is
actively being planned; the move to `Plan` was done by hand for #417 and #430 in one session. Two
independent causes were suspected — an unmapped station and a missing writer — and **only the second
survives measurement.** The `Plan` column exists on board 3, DEC-192 already prescribes `Plan` as a
lifecycle value, and `gh_board.set_station` passes a station name straight through for the board to
resolve, so nothing has to be declared for the write to land. What is genuinely missing is a writer
that runs that early: `gh_board.derive_station` reads `plan.yaml` task statuses alone, and at
`/harness-plan` kickoff there is neither a `plan.yaml` nor a feature directory, so `gh-sync open`
cannot run either. **The ticket being planned FROM is usually a wayfinding ticket, not the feature's
own card** — the feature's parent issue is created later by `open`. So the write is not
`derive_station`'s job; it is a kickoff act on a named source ticket, and today nothing performs it.
Issue #453.

## Goal

End both feature-close defects. A feature that ships records itself as shipped without a follow-up
commit, and a feature that is abandoned records itself as abandoned. The four-angle simplify pass
becomes a standing, repository-native step that runs while its findings can still be applied — after
the qa gate and before `review_sha` pins on the build side, and after the plan draft and before the
reviews and the signature on the plan side. Neither change alters what the factory verifies; both
change **when** and **whether** the record and the polish actually land. And the board stops lying
about the start of a feature as well as its end: when the operator names the ticket a feature is
being planned from, that ticket's card moves to `Plan` at kickoff without anyone doing it by hand.

## Requirements

- REQ-01: After `gh-sync.py ship` runs, the feature's recorded execution state reads terminal, with
  no further human or agent action.
- REQ-02: After `gh-sync.py abandon` runs, the feature's recorded execution state reads terminal.
- REQ-03: The four-angle simplify pass is a standing step of the build flow, positioned after the qa
  gate and before `review_sha` is pinned.
- REQ-04: The four-angle simplify pass is a standing step of the plan flow, positioned after the plan
  draft and before the architecture and design reviews and the operator's signature.
- REQ-05: The simplify methodology ships inside this repository and can be run without any file,
  command or plugin that lives outside it.
- REQ-06: The simplify step is never assigned to the validator lead.
- REQ-07: The decision behind the simplify step's ownership and position is recorded where the
  factory reads decisions, and the decisions index reflects it.
- REQ-08: When a feature's planning begins from a source ticket the operator names, that ticket's
  board card reads `Plan` with no manual move; when no source ticket is named, no card is written.
- REQ-09: The ruling on which tickets the harness may move, and why no station map is declared for
  its own board, is recorded where the factory reads decisions.

## Success Criteria

- SC-01: With a feature staged at a pre-terminal status, running `ship` leaves its recorded status
  reading `Done`.
  verify: automated      evidence: integration
- SC-02: With a feature staged at a pre-terminal status, running `abandon` leaves its recorded status
  reading `Abandoned`.
  verify: automated      evidence: integration
- SC-03: The existing `gh-sync` behaviours are unchanged by the status write — the milestone still
  closes, an adopted parent is still left open, a created parent still closes, and `--body-file`
  still posts exactly once.
  verify: automated      evidence: integration
- SC-04: The next feature to ship needs no follow-up commit to clear INV-26 on merged `main`.
  verify: uat
- SC-05: The four angles — reuse, simplification, efficiency and altitude — are each present in the
  shipped skill, in both their plan-surface and code-surface forms, and the skill cites the in-repo
  note holding the source prompts.
  verify: inspection
- SC-06: The shipped skill and both playbook steps name no file, command or plugin outside this
  repository, and in particular neither the `code-simplifier` plugin nor a `/simplify` user command.
  verify: inspection
- SC-07: In the build playbook the simplify step appears after the qa-gate sentence and before the
  `review_sha` pin sentence; in the plan playbook it appears after the plan draft and before the
  architecture review.
  verify: inspection
- SC-08: No step in either playbook, and no line in the skill, assigns the simplify pass to
  `harness-validator-lead` or to any validator-squad member.
  verify: inspection
- SC-09: **Both** decisions — the simplify step, and the station-write boundary — are recorded in
  `DECISIONS.md` and the generated index is in sync with it: regenerating the index produces no diff.
  verify: inspection
- SC-10: The kickoff writer moves a named issue to a named station when a board is configured, writes
  nothing when no board is configured, when it is run outside a harness root, or when `github.sync`
  is false, and reports a failure of the board write without stopping its caller — **for every
  failure class, not only the one the board library declares.** A wrong invocation is its only
  non-zero exit.
  verify: automated      evidence: unit
- SC-11: `/harness-plan` carries the kickoff step before its plan sequence, names the writer by path,
  and states the branch where no source ticket is named. The existing plan-sequence wording is
  unchanged apart from the simplify insertion of SC-07.
  verify: inspection
- SC-12: The recorded station ruling states the boundary the tree actually enforces — the harness
  moves any card it is pointed at and closes only cards it created — and states why no `stations`
  map is added to `harness.json`, naming the closed ruling that owns that restructure.
  verify: inspection
- SC-13: The next feature planned from a named source ticket lands that ticket in `Plan` on board 3
  with no manual move.
  verify: uat

## Verification gaps

Read before signing. `test_kinds` in `.harness/harness.json` was checked entry by entry (DEC-163).

- **No runner covers markdown behaviour.** `change_type: docs` and `change_type: config` both carry
  `always: []` in the test matrix, and no active kind's `detect` glob matches
  `.claude/skills/**/SKILL.md` or `.claude/commands/*.md`. So **the ordering of the simplify step in
  either playbook is not protected by any standing regression gate.** It is asserted once, by the
  task's own `verify:` clause at build time, and thereafter by a reader. If someone later rewords the
  qa-gate sentence or moves the pin, nothing goes red. What carries it instead: the task clauses
  assert each anchor occurs exactly once and report anchor drift distinctly from work failure, so the
  build-time check cannot pass on a rotted pointer. **A standing playbook-ordering checker is worth a
  backlog item; it is deliberately not in this feature's scope**, because it is new gate-adjacent
  code and this feature is three small fixes.
- **`component`, `ui`, `eval` and `typecheck` all have `cmd: null`.** None of them touches a surface
  this feature changes, so no criterion here rests on one.
- **The `/harness-plan` kickoff step's placement is not protected either.** It is the same class as
  the playbook gap above: `.claude/commands/*.md` matches no active kind's `detect` glob, so the step
  is asserted once by T-06's clause at build time and thereafter by a reader. What carries it: T-06's
  clause asserts each anchor occurs exactly once and re-asserts T-03's clause on the same file, so a
  collision between the two edits reddens rather than passing silently.
- **The kickoff writer's message shapes are structurally ungated, not merely currently ungated.** No
  active `test_kinds` `detect` glob covers the operator-facing text surfaces, and the writer's own
  cases assert behaviour (`writes nothing`, `exits 0`) rather than stdout wording. So nothing will
  ever catch a line printed without the `board-station: ` prefix, or a usage line that omits the
  repository binding — only a reader will. What carries it instead: the prefix is required of every
  output line in the task's own intent, and its divergence from the sibling tool's exit code for the
  same failure class is recorded there as deliberate rather than left to be rediscovered.
- **No test writes to the real board.** `test-board-station.py` drives the tool against a fake `gh`.
  That the card on board 3 actually reads `Plan` afterwards is therefore SC-13's business, and SC-13
  is `uat` for that reason, not as a shortcut.
- **SC-04 and SC-13 cannot be met at ship time.** They are the two criteria that prove a defect is
  actually gone in the real sequence rather than in a fixture — SC-04 on the next feature the
  operator ships, SC-13 on the next feature the operator plans from a named ticket. Both stay
  `not_met` until then. That is deliberate, not an oversight.

## Constraints

- The three fixed points on the simplify step are the operator's ruling on issue #430 and are not
  open: it is the **last build step**, owned by the build side, applied **before `review_sha` pins**;
  it is **never the validator lead**; and it is **harness-native**, with no dependency on the
  `code-simplifier` plugin or any `/simplify` user command.
- **On surfaces no specialist owns, the simplify pass is flag-only.** Under `.claude/` the domain
  guard grants exactly one path — `skills/harness/bin/**` — and every other path there resolves to no
  owner at all. That is not a corner case for a self-hosted feature: three of this feature's six
  tasks (T-02, T-03, T-06) write `.claude/skills/**/SKILL.md` or `.claude/commands/**`, surfaces the
  guard resolves to NOBODY, against two that write the granted `bin/**`. A build-side apply on such
  a surface is refused mid-run and the findings are lost, so those findings return to the
  orchestrator instead.
  **This is an implementation gap in the ruling that the pass is the last build step, owned by the
  build side and applied before `review_sha` pins — not a weakening of it.** The step's position and
  ownership are unchanged.
- The four angles are ported verbatim in substance from
  `notes/research-FEAT-23-simplify-angles-source.md`. No new angle is invented.
- `.claude/skills/harness/bin/gh-sync.py` is **not** one of the four DEC-174 files, so it is ordinary
  team work. Nothing in this feature touches `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py` or `check-state.sh`.
- INV-26's terminal exemption is case-sensitive on purpose (DEC-192): `Done` is not `done`. The
  status written must match the board's own column spelling exactly.
- `derive_station()` returning `Review` when all tasks are done is deliberate and is not changed —
  its docstring states the Done exemption is the caller's. The exemption's precondition is the only
  fix surface.
- The three fixes need not share a commit. Nothing here is atomically coupled.
- The kickoff station write bypasses `derive_station` entirely, and that is the point: the ticket a
  feature is planned FROM is usually a wayfinding ticket, not the feature's own parent card, and at
  kickoff neither a `plan.yaml` nor a feature directory exists for `derive_station` to read.
  `derive_station` is not changed by this feature.
- **No `stations` map is added to `.harness/harness.json`, and no `plan:` key to `fleet.yaml`.**
  `gh_board.set_station` passes the station name straight through and the board resolves it by name,
  so declaring it would buy nothing on board 3. The restructure that would declare stations for every
  board is a separate, already-closed ruling that nothing currently implements.
- `.harness/harness.json` and `.harness/factory/fleet.yaml` had their lanes resolved and were then
  ruled out of scope — not assumed untouched.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-17
notes: Signed as-is. Arch finding G left unapplied by the operator's ruling — the reviewer
  routed it rather than fixing it, and its deeper remedy would edit a file D-05 scopes as
  called-not-edited; the gap is recorded in the run digests. Every verify clause was
  executed red before signature.
