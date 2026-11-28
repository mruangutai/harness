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
station and approval are in `plan.yaml`, its runs are in `feature.json`, and its open questions are in the latest run
digest. Nothing on main still tells anyone to keep a second copy.

**orchestrator** — Each cycle I read live state from records that already exist and are kept current by the verbs that
write them. After a close-run I have no status file to rewrite. When I resume, the disk-only path names those same
records.

**code maintainer** — No gate, test or template carries rules for a file nobody writes. Retired invariant numbers are
recorded as retired, not left dangling or reused. The checks behave the same whether or not a stray copy of the old
file is present.

**reader** — I can grade each changed decision against the pinned DECISIONS.md: the struck entry keeps a strike
record, the rewritten entries state current truth in place, and the index matches its generator.

## Success criteria

- SC-01 (operator): At `review_sha`, `git ls-tree -r --name-only <review_sha> -- .harness | grep -E '/features/[^/]+/STATE\.md$'` prints nothing, which covers all 39 `.harness/harness/features/*/STATE.md` files and the kaya one, and `git cat-file -e <review_sha>:.claude/skills/harness/templates/STATE.md` fails. If the operator rules at Q-03 to keep the kaya copy, the command prints exactly `.harness/kaya/features/FEAT-01-kaya-platform/STATE.md` and nothing else, and T-07's gate is amended to that same inventory.
  verify: inspection
- SC-02 (orchestrator): At `review_sha`, `.claude/skills/harness/SKILL.md` "The loop" step 1 tells the orchestrator to read each cycle `plan.yaml` (`status`, `approval.status`), `feature.json` (`runs`, where the open run is the entry whose `verdict` is `PENDING`) and the `open_questions` of the latest accepted run digest (the digest of the newest `runs` entry whose `verdict` is not `PENDING`), with only the `notes/answers-*.md` paths it was handed. It says that no accepted digest (a first entry, or no return accepted yet) is recorded as such, never as a digest with no open questions. On the first cycle it instantiates `feature.json` only. Step 4's wake re-read names `plan.yaml` and `feature.json` and reads the returned digest's `open_questions` only after its artifact is verified. Step 6's separate writes after close-run are the phase handoff note at a seam and the commit, with no status-file write. `references/succession.md`'s disk-only path names `plan.yaml`, `feature.json` and the cited run digests.
  verify: inspection
- SC-03 (code maintainer): At `review_sha`, `git grep -n -I -E 'STATE\.md|STATE_MD|state_md' <review_sha> -- .claude/skills .omp .harness/team-config.yaml` prints nothing, which covers skills, references, templates, bin modules, agent bodies and the team-config comment. `git grep -n -I -w STATE <review_sha> -- .claude/skills/harness/templates` also prints nothing. Under `tests/`, excluding the frozen `tests/integration/fixtures/prior-*` controls, the only lines that name the file are inside the SC-05 case function `case_stray_status_file_is_inert` in `tests/integration/test-check-state-table.py` and the SC-06 case function `run_retired_status_file_is_ungated` in `tests/integration/test-check-domain-post.py`.
  verify: inspection
- SC-04 (code maintainer): The checker's retired catalogue (`check_state/table.py#RETIRED`, which its list mode prints) carries INV-2 and INV-5, each with a DEC reason. Neither is a row in `check_state/table.py#INVARIANTS`. INV-23's row reads only `feature.json` and `CLAUDE.md`. Every number in `INVARIANTS` and `RETIRED` appears exactly once across the two. The case is in `tests/integration/test-check-state-table.py`, and qa shows it failing at the base commit first.
  verify: automated        evidence: integration
- SC-05 (code maintainer): With a stray old-style file present, check-state behaves as if it were absent. A fixture feature carrying a 200-line `STATE.md` with an illegal `##` section and a dangling `T-99` gets the same exit code and stdout as the same fixture after the file is deleted, and no output line names the file. The case is a retirement regression in `tests/integration/test-check-state-table.py`, and qa shows it failing at the base commit first.
  verify: automated        evidence: integration
- SC-06 (code maintainer): Check-domain no longer shape-gates the old file. A governed `harness-orchestrator` Write of that 200-line payload to `.harness/harness/features/<FEAT>/STATE.md` exits 0 with empty stderr, and the same file reached through the `PostToolUse` sweep exits 0. In the same case, over-budget `feature.json`, handoff-note and `CLAUDE.md` payloads still exit 2, and no denial carries a routing sentence that names the old file. The case is the retirement regression `run_retired_status_file_is_ungated` in the existing `tests/integration/test-check-domain-post.py`, which drives `check-domain.py` as a subprocess, and qa shows it failing at the base commit first.
  verify: automated        evidence: integration
- SC-07 (code maintainer): Every integration suite the change touches exits 0 with no `^FAIL` line at `review_sha`. These are `test-check-state-{plans,table,shipped,entry,records}.py`, `test-check-domain-{approval,post,worktree}.py`, `test-harness-yaml.py`, `test-validate-feature-json.py`, `test-checker-structure-locks.py`, `test-structure-audit-single-pass.py`, `test-merge-gitignore.py`, `test-check-plan-routes.py` and `test-check-skill-weight.py` under `tests/integration/`. Each case that used the old file as its vehicle is retargeted to a live rule and still proves the same property.
  verify: automated        evidence: integration
- SC-08 (code maintainer): Every unit suite the change touches exits 0 with no `^FAIL` line at `review_sha`. These are `test-check-state-shipped-ctx.py`, `test-answers-provenance.py`, `test-orchestrator-playbook.py`, `test-lead-stop-and-wake.py` and `test-check-skill-refs.py` under `tests/unit/`.
  verify: automated        evidence: unit
- SC-09 (reader): Read with `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, every amend and strike row in `plan.yaml decisions_affected` has landed. DEC-45 keeps its heading with a strike record naming DEC-188 and its successor. DEC-129 and DEC-150 are rewritten in place with no "Amended by" text. `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` is empty, every touched ruling is 30 words or fewer, and `check-decision-anchors.py` exits 0.
  verify: inspection
- SC-10 (operator): At `review_sha`, `git grep -n -I -w STATE <review_sha> -- .harness/README.md .harness/harness/docs/SPEC.md .harness/harness/docs/org.html` prints nothing. That covers both `STATE.md` and the bare `BRIEF`/`PLAN`/`STATE` shorthand. SPEC §2, §10 and §15 describe live state as `plan.yaml`, `feature.json` and run digests: §10 names the latest accepted run digest as the home of open questions, and §15 names the run digests among the per-feature records. The artifact table in `org.html` names `plan.yaml` for the station and approval, `feature.json` for the runs and the open run, and the latest accepted run digest for `open_questions`.
  verify: inspection

## Verification gaps

- `component` and `ui` are unresolved with null runners and `functional` and `eval` are excluded (DEC-187). None covers
  a surface this feature touches, and no SC rests on them.
- SC-01, SC-02, SC-03, SC-09 and SC-10 are inspection: each names a `git` command at `review_sha` that a reviewer runs and
  cites. No test guards against a later merge re-adding a `STATE.md`. After this ships, nothing mechanical flags one
  (see Q-02).
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
  `harness-validator-lead` G-01) are edited only by their own personas at distillation, never by a build task (Q-04).
- **SUPPLIES:** DEC-182 and DEC-191. The station lives only in `plan.yaml` and is what the orchestrator reads instead.
  DEC-156 supplies the run digest, whose `open_questions` carries what `## Open Questions` held. DEC-159 supplies the
  handoff note, which stays.
- **Stays byte-identical (historical record):** shipped `runs/` digests, `notes/` and `observations/` of every feature;
  the three shipped `plan.yaml` files that mention the file (BUG-2187, BUG-2239, BUG-2451); the kaya FEAT-01 notes and
  observations; `.harness/logs/`; `council/`; `.harness/harness/docs/BUILD.md` (completed build log);
  `tests/integration/fixtures/prior-*.fixture` (frozen prior-hook controls); and the dated narrative in kept
  decisions DEC-31, DEC-90 (struck), DEC-121, DEC-160, DEC-173 and DEC-180.
- **Overlap:** FEAT-2643, which is in flight, edits `check_state/ctx.py#is_shipped`, `check_state/plan.py#_inv32_shape`
  and `check_state/feature_record.py#inv_33`. Those are the same files this feature's T-01 edits, but different
  symbols (Q-01).
- **In-flight worktrees:** FEAT-2641, FEAT-2688 and BUG-2524 each keep a `STATE.md` in their worktree. If they merge
  after this feature, they re-add the file (Q-02).
- **Open at signature, each with pm's recommendation (also in the plan digest):**
  - Q-01: When should the build start relative to FEAT-2643? Recommendation: start after FEAT-2643 merges and rebase
    first. The two features share three files in different symbols, so starting first only buys a rebase conflict in
    gate code.
  - Q-02: FEAT-2641, FEAT-2688 and BUG-2524 each keep a `STATE.md`. Recommendation: this feature merges first, and
    each of them drops its file with `git rm` before it merges. No new gate is added, so a later re-add is caught by
    review, not by a check.
  - Q-03: `.harness/kaya/features/FEAT-01-kaya-platform/STATE.md` is a 40th tracked copy, in this repository's kaya
    segment. Recommendation: delete it here too. No reader remains, and the file sits in this repository, not in
    kaya's code checkout.
  - Q-04: The two Expertise entries that name the file sit outside every build task. Recommendation: this feature's
    distillation recommends `drop` for code-reviewer G-05 and validator-lead G-01 to their own personas.

## Out of scope

- Any replacement status document, or a status or phase field in `feature.json`. `plan.yaml` stays the only station
  authority (grilling, operator).
- `.harness/logs/` and the per-run digests. They are unchanged (grilling).
- Served repositories' feature trees, except where the same template and skill text is shared (grilling). Q-03 asks
  whether the one tracked kaya-segment file counts.

## Approval

status: pending
approved-by:
date:

<!-- pm authors the pending fields above; only the main session records the user's
     explicit signature. See harness-brief's Approval rule (DEC-120). -->
