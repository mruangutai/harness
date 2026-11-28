# BRIEF — FEAT-2423 Retire STATE.md

## Problem

Every feature directory is supposed to carry a `STATE.md` that the orchestrator reads each cycle and rewrites after each
close-run, yet the file is written and then abandoned. Of the 20 newest features on main, 15 have one and 12 of those
still say the feature is in progress (`awaiting-user`, `station: plan`, `station: review`) while `plan.yaml` says `done`
(grilling probe 1, main `36ee67e5`). On main-session-direct features (DEC-174) no orchestrator runs, so nothing reads it
(probe 2). The cost is a second, stale status channel beside `plan.yaml` and `feature.json`. Anyone resuming a feature
can trust the wrong one. Keeping it also costs three check-state invariants, a check-domain budget, a template, and
instructions in skills, agents and decisions.

## Done when — by perspective

**operator** — No feature directory holds a status file that can disagree with `plan.yaml`. When I open a feature, its
station and approval are in `plan.yaml`, its runs are in `feature.json`, and its open questions are in the latest accepted
run digest. Nothing on main still tells anyone to keep a second copy.

**orchestrator** — Each cycle I read live state from records that already exist and are kept current by the verbs that
write them. After a close-run I have no status file to rewrite. When I resume, the disk-only path names those same
records.

**code maintainer** — No gate, test or template carries rules for a file nobody writes. Retired invariant numbers are
recorded as retired, not left dangling or reused. The checks behave the same whether or not a stray copy of the old
file is present.

**reader** — I can grade each changed decision against the pinned DECISIONS.md: the struck entry keeps a strike
record, the rewritten entries state current truth in place, and the index matches its generator.

## Success criteria

- SC-01 (operator): At `review_sha`, `git ls-tree -r --name-only <review_sha> -- .harness | grep -E '/features/[^/]+/STATE\.md$'` prints nothing, which covers all 39 `.harness/harness/features/*/STATE.md` files and the kaya one (`.harness/kaya/features/FEAT-01-kaya-platform/STATE.md`, deleted by operator ruling Q-03), and `git cat-file -e <review_sha>:.claude/skills/harness/templates/STATE.md` fails.
  verify: inspection
- SC-02 (orchestrator): At `review_sha`, `.claude/skills/harness/SKILL.md` "The loop" step 1 tells the orchestrator to read each cycle `plan.yaml` (`status`, `approval.status`), `feature.json` (`runs`, where the open run is the entry whose `verdict` is `PENDING`) and the `open_questions` of the latest accepted run digest, with only the `notes/answers-*.md` paths it was handed, and carries this feature's one definition of that digest verbatim (plan D-01): "The latest accepted run digest is runs/<run-id>/digest.md of the last feature.json runs entry that is closed (its verdict is not PENDING) and not refused (it carries no refusal mapping and no legacy return_disposition: refused); a BLOCKED verdict without either marker is accepted. When no entry qualifies, no digest has been accepted: record that as none accepted, never as an accepted digest with no open questions." A refused return is skipped by its refusal marker, never by its `BLOCKED` verdict, so an older accepted digest is still found, and none accepted stays distinct from an accepted digest whose `open_questions` is empty. On the first cycle it instantiates `feature.json` only. Step 4's wake re-read names `plan.yaml` and `feature.json` and reads the returned digest's `open_questions` only after its artifact is verified. Step 6's separate writes after close-run are the phase handoff note at a seam and the commit, with no status-file write. `references/succession.md`'s disk-only path names `plan.yaml`, `feature.json` and the cited run digests.
  verify: inspection
- SC-03 (code maintainer): At `review_sha`, `git grep -n -I -E 'STATE\.md|STATE_MD|state_md' <review_sha> -- .claude/skills .omp .harness/team-config.yaml` prints nothing, which covers skills, references, templates, bin modules, agent bodies and the team-config comment. `git grep -n -I -w STATE <review_sha> -- .claude/skills/harness/templates` also prints nothing. Under `tests/`, no test, fixture or test data names the file, including by string construction or split literals (operator ruling Q-06): `git grep -n -I -E 'STATE\.md|STATE_MD|state_md' <review_sha> -- tests` and `git grep -n -I -E "[\"']STATE[\"']" <review_sha> -- tests` each exit 1 with no output, and the reviewer finds no other construction of the name. No path under `tests/` is excluded: the two prior-revision controls that named the file, `tests/integration/fixtures/prior-check-domain.fixture` and `tests/integration/fixtures/prior-check-plan-routes.py.fixture`, drop the name while `test-check-domain-claims.py` and `test-check-plan-routes.py` still pass on them unchanged (T-02).
  verify: inspection
- SC-04 (code maintainer): The checker's retired catalogue (`check_state/table.py#RETIRED`, which its list mode prints) carries INV-2 and INV-5, each with a DEC reason. Neither is a row in `check_state/table.py#INVARIANTS`. INV-23's row reads only `feature.json` and `CLAUDE.md`. Every number in `INVARIANTS` and `RETIRED` appears exactly once across the two. The case is in `tests/integration/test-check-state-table.py`, and qa shows it failing at the base commit first.
  verify: automated        evidence: integration
- SC-05 (code maintainer): Neither gate keeps a rule that names the retired file, and that removal is the proof that a stray copy is unread; no test writes one (operator ruling Q-06). At `review_sha`, SC-03's grep over `.claude/skills` prints nothing, so no check-state or check-domain module spells the name. In the `check-domain.py` source as committed at `review_sha` (read with `git show`), `RE_STATE_MD` and `_rule_state_md` are gone, and every entry of `SHAPE_PATTERNS`, `SHAPE_RULES` and `_SWEEP_PATTERNS` names one specific other file: `feature.json`, a run `state.yaml`, a handoff note, `CLAUDE.md`, `plan.yaml`, a run identity or a run digest (the reviewer cites each entry). The checker's list mode at `review_sha` names the file in no row; SC-04 owns the retired catalogue and INV-23's two sources.
  verify: inspection
- SC-06 (code maintainer): Check-domain's surviving budget rules still deny and now route to the live records. A governed `harness-orchestrator` Write of an over-budget, otherwise valid `feature.json` exits 2 with the feature.json budget diagnostic (`It is data a script parses, not a journal.`) in stderr, and one stderr line, stripped of indentation, is exactly `Routing: the station lives in plan.yaml; per-run findings and open questions go in that run's digest.md; rationale goes in notes/. State files carry no history.` In the same fixture, a 70-line handoff note that carries every required section and a valid `## Done when` exits 2 with `handoff note is 70 lines — cap is 60.` in stderr and no section or Done when problem, and an 81-line `CLAUDE.md` exits 2 with `CLAUDE.md is 81 lines — budget is 80 (DEC-181).` in stderr, so each exit is bound to its own budget, not to exit 2 alone. Every stderr line of the three that, stripped of surrounding whitespace, starts with `Routing:` equals that sentence. The case is `run_budget_denials_route_to_live_records` in the existing `tests/integration/test-check-domain-post.py`, which drives `check-domain.py` as a subprocess and names no retired file. qa shows it failing at the base commit first, where the `feature.json` denial carries the old routing sentence.
  verify: automated        evidence: integration
- SC-07 (code maintainer): Every integration suite the change touches exits 0 with no `^FAIL` line at `review_sha`. These are `test-check-state-{plans,table,shipped,entry,records}.py`, `test-check-domain-{approval,post,worktree,claims}.py`, `test-harness-yaml.py`, `test-validate-feature-json.py`, `test-checker-structure-locks.py`, `test-structure-audit-single-pass.py`, `test-merge-gitignore.py`, `test-check-plan-routes.py` and `test-check-skill-weight.py` under `tests/integration/`. Each case that used the old file as its vehicle is retargeted to a live rule and still proves the same property.
  verify: automated        evidence: integration
- SC-08 (code maintainer): Every unit suite the change touches exits 0 with no `^FAIL` line at `review_sha`. These are `test-check-state-shipped-ctx.py`, `test-answers-provenance.py`, `test-orchestrator-playbook.py`, `test-lead-stop-and-wake.py` and `test-check-skill-refs.py` under `tests/unit/`.
  verify: automated        evidence: unit
- SC-09 (reader): Read with `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, every amend and strike row in `plan.yaml decisions_affected` has landed. DEC-45 keeps its heading with a strike record naming DEC-188 and its successor. DEC-129 and DEC-150 are rewritten in place with no "Amended by" text. `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` is empty, every touched ruling is 30 words or fewer, and `check-decision-anchors.py` exits 0.
  verify: inspection
- SC-10 (operator): At `review_sha`, `git grep -n -I -w STATE <review_sha> -- .harness/README.md .harness/harness/docs/SPEC.md` prints nothing. That covers both `STATE.md` and the bare `BRIEF`/`PLAN`/`STATE` shorthand. SPEC §2, §10 and §15 describe live state as `plan.yaml`, `feature.json` and run digests: §10 names the latest accepted run digest as the home of open questions and carries the same definition verbatim (plan D-01): "The latest accepted run digest is runs/<run-id>/digest.md of the last feature.json runs entry that is closed (its verdict is not PENDING) and not refused (it carries no refusal mapping and no legacy return_disposition: refused); a BLOCKED verdict without either marker is accepted. When no entry qualifies, no digest has been accepted: record that as none accepted, never as an accepted digest with no open questions." §15 names the run digests among the per-feature records. The retired reference page is deleted, not rewritten (operator direction): `git cat-file -e <review_sha>:.harness/harness/docs/org.html` fails.
  verify: inspection
- SC-11 (operator): Before this feature ships, the two Expertise entries that still tell agents to keep the file are dropped: `harness-validator-lead` G-01 and `harness-code-reviewer` G-05. At the ship commit, `git show <ship_sha>:.harness/harness/expertise/harness-validator-lead.md` and `git show <ship_sha>:.harness/harness/expertise/harness-code-reviewer.md` each exit 0, and piped through `grep -n -E 'STATE\.md'` each print nothing. By operator ruling Q-04 this SC is traced by this feature's distillation, not by a task: each persona drops its own entry at distillation, and no build task edits Expertise (DEC-145, DEC-253). It is a ship condition.
  verify: inspection

## Verification gaps

- `component` and `ui` are unresolved with null runners and `functional` and `eval` are excluded (DEC-187). None covers
  a surface this feature touches, and no SC rests on them.
- SC-01, SC-02, SC-03, SC-05, SC-09, SC-10 and SC-11 are inspection: each names a `git` command at `review_sha` (SC-11 at
  the ship commit) that a reviewer runs and cites. No test guards against a later merge re-adding a `STATE.md`, and by
  operator ruling Q-02 no gate is added: whichever of FEAT-2641, FEAT-2688 or BUG-2524 merges after this feature runs
  `git rm` on its own copy, and review catches any leftover. After this ships, nothing mechanical flags one.
- No test writes a stray copy of the old file (operator ruling Q-06), so SC-05 proves only that every rule naming it is
  gone. It does not prove that the generic feature-directory reads (INV-7, INV-15, INV-37 and INV-46 list
  `.harness/*/features/*/**`) ignore a stray copy.
- Integration suite durations at the base go up to 58 s per file (`test-check-state-plans.py`, 3c490116), so a task's
  verify block takes longer than 60 s in total, though each command stays under it.

## Constraints

- **BLOCKS:** DEC-174. Every task changes or tests a gate (check-state, check-domain, check-plan-routes, the plan
  loader, the feature-record validator), so every task is `main-session-direct`.
- **BLOCKS:** DEC-205. DEC-129 and DEC-150 are rewritten in place, never with an "Amended by" line, and a retired INV
  number is never reused.
- **BLOCKS:** DEC-188. DEC-45 is struck, not marked stale. Its heading and strike record stay (operator ruling).
- **BLOCKS:** DEC-191. `feature.json` keeps its closed key set, so no status field is added.
- **BLOCKS:** DEC-145 and DEC-253. The two Expertise entries naming the file (`harness-code-reviewer` G-05,
  `harness-validator-lead` G-01) are edited only by their own personas at distillation, never by a build task. SC-11
  makes their drop a ship condition (operator ruling Q-04).
- **SUPPLIES:** DEC-182 and DEC-191. The station lives only in `plan.yaml` and is what the orchestrator reads instead.
  DEC-156 supplies the run digest, whose `open_questions` carries what `## Open Questions` held. DEC-159 supplies the
  handoff note, which stays.
- **Stays byte-identical (historical record):** shipped `runs/` digests, `notes/` and `observations/` of every feature;
  the three shipped `plan.yaml` files that mention the file (BUG-2187, BUG-2239, BUG-2451); the kaya FEAT-01 notes and
  observations; `.harness/logs/`; `council/`; `.harness/harness/docs/BUILD.md` (completed build log); and the dated
  narrative in kept decisions DEC-31, DEC-90 (struck), DEC-121, DEC-160, DEC-173 and DEC-180.
- **Overlap:** FEAT-2643, which is in flight, edits `check_state/ctx.py#is_shipped`, `check_state/plan.py#_inv32_shape`
  and `check_state/feature_record.py#inv_33`. Those are the same files this feature's T-01 edits, but different
  symbols (ruled below, Q-01).
- **In-flight worktrees:** FEAT-2641, FEAT-2688 and BUG-2524 each keep a `STATE.md` in their worktree. Whichever merges
  after this feature drops its own copy (ruled below, Q-02).
- **Ruled** (operator, `notes/answers-2026-11-28-plan-c1.md`):
  - Q-01: The build starts after FEAT-2643 merges, and it is rebased onto main first.
  - Q-02: No re-add gate. Whichever of FEAT-2641, FEAT-2688 or BUG-2524 merges after this feature runs `git rm` on its
    own `STATE.md`; review catches any leftover.
  - Q-03: The kaya-segment copy is deleted in T-07 (SC-01).
  - Q-04: Dropping code-reviewer G-05 and validator-lead G-01 is a ship condition, delivered by this feature's
    distillation (SC-11).
  - Q-05: The plan is checked with `plan-merge.py check --root` set to the main checkout. The worktree's sparse cone is
    not widened (FEAT-1559); the gap is filed as #2701.
  - Q-06: No test exceptions. No test, fixture or test data names the file (SC-03, SC-05, SC-06).
  - Q-07: `plan-merge.py apply` accepting an empty proposal is filed as #2702; the plan does not change for it.
  - GC-03: Historical mentions stay (DEC-205): old decision narrative, shipped runs, notes and plans, and BUILD.md. The
    destination means no live mention.
  - org.html (operator direction): `.harness/harness/docs/org.html` is deleted in T-04, not rewritten; nothing live
    links to it.

## Out of scope

- Any replacement status document, or a status or phase field in `feature.json`. `plan.yaml` stays the only station
  authority (grilling, operator).
- `.harness/logs/` and the per-run digests. They are unchanged (grilling).
- Served repositories' feature trees, except where the same template and skill text is shared (grilling). The one
  tracked kaya-segment file is in scope and deleted (Q-03).

## Approval

status: approved
approved-by: operator
date: 2026-11-28

<!-- pm authors the pending fields above; only the main session records the user's
     explicit signature. See harness-brief's Approval rule (DEC-120). -->
