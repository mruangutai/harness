# Code Review — FEAT-41-one-station-vocabulary — c0

Both stages run unconditionally per dispatch. Baseline reproduced: unit exit 0, integration exit
0 (194s), `check-state.sh` exit 0 with 0 `VIOLATION` lines. `code-grade.py` run against the pin
(never HEAD): 9 gated HIGH records, 5 gated grade-2 (MED) records → `code_grade: fail`.

## MUST_FIX (blocks ship)

**F1 — stage 2, HIGH, blocks: yes.** `plan-merge.py:697-727` `cmd_sign_approval.transform`
interpolates `--by`/`--date` directly into the approval YAML with no escaping and — unlike
`apply`/`add-tasks` — never calls `_verify_spliced` before the write lands. Reproduced live: a
signer name containing `": "` (e.g. `O'Brien: The Great`) writes an approval block that
`yaml.safe_load` cannot parse (`ScannerError: mapping values are not allowed here`), and
`sign-approval` still prints `SIGNED ... / APPLIED ...` and exits 0. This is the exact defect
class Step 9 (`_verify_spliced`) exists to close — "1541 unparseable lines... exited 0" — on a
brand-new verb this feature adds, which skipped the protection its sibling verb got. No test in
`test-plan-merge.py` exercises a signer name with a colon or other YAML-significant character.
`set-task-station`/`set-feature-station` are safe (their values come only from the validated
station whitelist), so this is scoped to `sign-approval`'s free-text `--by`/`--date`.

**F2 — stage 2, HIGH, blocks: yes.** `gh-sync.py:598-624` `_record_station`'s two failure prints
("... is absent — station not recorded" / "... station not recorded — plan-merge.py
set-feature-station exited N: ...") never contain the literal `SKIP` or `FAILED`.
`cmd_ship`'s tail (`gh-sync.py:1613`) only calls `_commit_terminal_station` when
`_record_station` returns `True`, so a write failure correctly skips the commit — but
`post-merge-sweep.sh`'s positive-signal gate (`:186-195`) greps ship's combined output for
exactly those two literals to decide whether the terminal write is proof enough to remove the
worktree. A `_record_station` failure (lock contention, transient I/O, a corrupted plan.yaml)
prints neither literal, so if the worktree happens to be otherwise clean the gate sails through
and `feature-worktree.py remove`'s own dirty-check (which is what actually saves the
`_commit_terminal_station`-succeeds-but-git-commit-fails case) has nothing to catch — nothing was
written, so nothing is dirty. The worktree is deleted with the terminal station never recorded
anywhere. This reproduces the exact INV-26/uncommitted-station defect class SC-09/SC-10/REQ-07
and T-10 exist to close, through a path neither `test-gh-sync.py` nor `test-post-merge-sweep.py`
exercises (both test the `_commit_terminal_station` git-commit failure, never the upstream
`_record_station` write failure).

**F3 — stage 2, HIGH ×9, blocks: yes (code-grade, mechanical).** Every record below is NEW or
REGRESSED (the tool only gates those) and below its bar, not grade 2:
- `gh-sync.py:617 _commit_terminal_station` — cyclomatic 9, cognitive 12, abc 19.5, grade 3, bar 4, driver cyclomatic+cognitive
- `gh_board.py:205 _task_cards` — cyclomatic 7, cognitive 11, abc 12.4, grade 3, bar 4, driver cognitive
- `gh_board.py:257 board_stations` — cyclomatic 6, cognitive 11, abc 14.1, grade 3, bar 4, driver cognitive
- `plan-merge.py:122 _legal_stations` — cyclomatic 8, cognitive 11, abc 16.3, grade 3, bar 4, driver cognitive
- `plan-merge.py:680 cmd_set_feature_station.transform` — cyclomatic 6, cognitive 12, abc 17.6, grade 3, bar 4, driver cognitive
- `plan-merge.py:763 main` — cyclomatic 2, cognitive 1, abc 23.8, grade 3, bar 4, driver abc
- `test-check-domain.py:2529 run_t09` — cyclomatic 5, cognitive 4, abc 48.6, grade 1, bar 3, driver abc
- `worktree_terminal.py:178 _read_landed_plan_yaml` — cyclomatic 10, cognitive 13, abc 19.7, grade 3, bar 4, driver cyclomatic+cognitive
- `worktree_terminal.py:253 classify` — cyclomatic 16, cognitive 27, abc 47.4, grade 1, bar 4, driver abc

None of these read as accidental complexity — each is a single-purpose function enumerating a
closed set of failure/branch cases (classification records, station cases, splice-region cases)
— but the tool gates on the numbers, not on my read, per the review contract.

## SHOULD_FIX (non-blocking)

**F4 — stage 2, grade-2 (MED), reasoned acceptance, `code_grade: grade_2` component, non-gating:**
- `plan-merge.py:232 _verify_spliced` (grade2, cyclomatic+cognitive, abc 21.1) — accept: one
  cohesive "does the splice reload as the merge we reported" gate; splitting fragments the
  invariant across files.
- `plan-merge.py:597 _task_status_line` (grade2, cyclomatic+cognitive+abc, abc 33.8) — accept:
  must scope a task's own `status:` line against sibling tasks and nested `verify:` prose at
  arbitrary indent; the branching is the correctness requirement, not incidental.
- `plan-merge.py:720 cmd_sign_approval.transform` (grade2, cyclomatic+cognitive+abc, abc 31.3) —
  accept the grade; see F1 for the correctness gap this same function carries.
- `plan-sign-gate.py:103 denies` (grade2, cognitive, abc 15.0) — accept: recursive
  shell-command-boundary walk (subshell/eval/pipe, `MAX_DEPTH=3`) is inherently branchy
  security-matching logic.
- `test-plan-merge.py:625 case_set_task_station_one_line` (grade2, abc, abc 30.3) — accept: test
  function, ABC driven by assertion-call count, not real complexity.

**F5 — stage 1, omission, MED.** 9 files carry substantive, verified-correct content changes that
no task's `files:` list names and no `lanes:` row authorises: `test-feature-json-merge.py` (26
lines), `test-hooks-install.py` (10), `.claude/skills/harness/references/github-mirror.md` (2),
`.harness/harness/docs/SPEC.md` (16), `.harness/harness/docs/DECISIONS-INDEX.md` (40, regenerated
by T-15's own generator per its commit message), plus all four
`.claude/skills/harness/templates/{harness.json,plan.yaml,feature.json,settings.snippet.json}` —
a SECOND, hand-maintained mirror of the `.agents/skills/harness/templates/` tree that T-01/T-04/
T-07/T-08 do declare, kept byte-identical but never itself named. Content in every case checks out
against the commit narrative (T-07: "two [sites] the audit found beyond D-14"; T-15: "A
CONSEQUENCE THE TASK DID NOT NAME"), so this is a traceability gap, not a wrong-content defect —
but `harness-spec-driven`'s every-file-to-a-task discipline is the thing that makes a diff this
size auditable at all, and these 9 paths were not.

**F6 — stage 2, MED, non-blocking.** `check-domain.sh`'s `RE_PLAN_YAML` (`:1044`) and its four
pre-existing `SHAPE_PATTERNS` siblings all require exactly one path segment between `.harness/`
and `features/` (`^\.harness/[^/]+/features/[^/]+/plan\.yaml$`). `plan-merge.py`'s own `PLAN_TAIL`
(`:90`) documents a SHALLOWER legal destination as equally valid — its `require_destination`
refusal message reads "a legal path looks like `.harness/features/FEAT-NN-slug/plan.yaml` or
`.harness/<repo>/features/FEAT-NN-slug/plan.yaml`". An Edit/Write against the shallow form is NOT
matched by `RE_PLAN_YAML`, so the SHAPE-region denial this feature exists to add would not fire
for that layout — reopening the hand-edit route REQ-05/T-09 close, for one path shape. Not
reachable on this checkout (`find .harness -maxdepth 2` shows only `.harness/harness/features`,
no bare `.harness/features`), and the limitation is inherited verbatim from the four sibling
patterns (pre-existing convention, not a regression this diff introduces) — but it directly
undercuts REQ-05's "no route exists" claim the day any served repo uses the shallow layout.
Recommend a backlog item to widen all five `SHAPE_PATTERNS` together, not a fix here.

## Rulings on the two disclosed items

**(a) T-10 verify line 3 — AGREE, correct disposition (report, not self-amend).** Reproduced live:
running the verify's own one-liner throws `AssertionError` on every currently-placed card, because
`st[n]` (from `board_stations`, lowercased since T-02) is compared against
`fc.station_column(w)` (capitalised) — `'done' != 'Done'` for every correct card. The tooling this
feature just built cannot fix it: `apply`/`add-tasks` only add items and refuse (exit 7) on any
existing-item difference, none of the three new verbs touches `verify:` text, and hand-editing
`plan.yaml` — for ANY change, not only station edits — is now categorically denied by the SHAPE
gate T-09 adds. Manually running a corrected comparison against the same inputs confirmed the
underlying `project`/board-agreement logic is right; only the plan's own recorded verify text is
wrong. LOW, non-blocking, but worth tracking so a future automated replay of this plan's verify
block is not mistaken for a live regression.

**(b) T-15 execution-mode deviation — PARTIALLY AGREE, recommend operator ratification.** The
2026-08-30 signature approved 13 tasks with T-15 explicitly on the `harness-documentor` team lane
(the BRIEF's own Constraints section spends a full paragraph on why T-15 alone was pulled onto
that lane after Q1 stripped decisions-authority work from direct execution). The commit
(`f895c2b`) honestly discloses "DEVIATION, RECORDED: the plan marks this task execution_mode
`team`. I executed it directly," with a stated rationale (avoiding a lossy relay into the
repository's highest-consequence file against a character-exact verify) — content is verified
correct (T-15's own verify, `test-gen-decisions-index`, `test-check-decision-anchors` all green).
That instinct — record rather than hide — is right per PRINCIPLES rule 15. But this is the same
shape of thing the project's own convention (T-13's strike forcing a return-to-pending
re-signature) treats as requiring the operator's word, not merely a commit-message note: the
signature was given ON the documentor-lane allocation specifically. Silently reassigning a
team-lane task to the main session post-signature, however well-reasoned, sets a precedent that
the main session may do this unilaterally on future features too. Recommend: raise as an open
question for explicit operator ratification before the next pin, rather than treating disclosure
alone as closing it. Non-blocking on its own.

## Areas checked clean

- `gh_board.py:project` / `_task_cards` / `_parent_station` — terminal-first ordering, no
  ready→backlog exception, illegal station raises loud (not silent) naming task+value; matches
  D-11 exactly.
- The three deliberate `project` non-consumers — `cmd_ship`'s done pass, `_to_backlog`,
  `cmd_status`'s Review branch — each carries a probe-measured (#860) justification for bypassing
  `project`, and none silently disagrees with it; D-11's "no exception" scope is `project` itself,
  not every station write in the file.
- `check-plan-routes.py:_manifest_deviation`'s byte→parsed loosening: only comments/whitespace/key
  order are tolerated; a duplicate key still raises (`harness_yaml`'s strict loader) and any other
  parse failure is treated as a deviation, never a silent pass. Safe.
- D-05 (`TERMINAL_MARKER` in `factory_config`), D-06 (SHAPE not domain region — confirmed
  unconditional on `agent_type`), D-08 (`gh_board.py` sole case boundary), D-13
  (`feature_json_write.write_feature_json` used for both the T-07 migration and the PR/github
  writers — confirmed via commit `26a8365`'s own receipt), D-14 (both SKILL.md sites repointed,
  confirmed on disk) — all mechanically checked, all honoured.
- SC-01/SC-02/SC-04/SC-08 reproduced directly (grep + Python checks): 0 capitalised literals
  outside tests, 0 `feature.json` status keys, exactly 4 non-test `gh_board.set_station(` sites.
- Baseline suites reproduced at the pin: unit exit 0, integration exit 0 (194s), `check-state.sh`
  exit 0 / 0 `VIOLATION` lines — matches the claimed measurement, no disagreement.

## Not examined

Security-relevant surfaces (path-traversal on the SHAPE gate's regexes, identity spoofing on
`plan-sign-gate.py`) are SecReview41's lens, not re-derived here beyond F6's structural gap.
Visual/UX has no surface in this diff (D-12's re-trigger condition never fired — no UI-shaped file
landed). QA41 owns suite-flake reproducibility; I did not re-run suites beyond the single
reproduction above.

## Delivery note

This note is duplicated at the worktree path
`.claude/worktrees/harness/FEAT-41-one-station-vocabulary/.harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-code-reviewer-c0.md`
(the location my dispatch named). It is ALSO written here, at the main-checkout-relative path,
because `validate-digest.py`'s SEC-01 `code_grade` binding check resolves this session's checkout
root to the main checkout regardless of the worktree I was dispatched to review, and `feature.json`
does not exist at either location on the main checkout (FEAT-41 has never merged) — so the check
fails "feature.json could not be read" for every yield attempt, independent of content or format.
Raised to Feat41Panel and Main via hub; no reply as of this write. Treat this artifact as the
authoritative delivery of the review.
