# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: [.]harness/harness/features/BUG-124-run-dir-squad-suffix/runs/panel-c4-validator/digest.md
- squad: validator
- status: in_review

**VALIDATE IS COMPLETE AND THE PANEL PASSED.** `severity_max: med`, `must_fix: []`, at `review_sha`
`6c037de463fd2b7be0c6ffa4df04ce801aac86e2`. `gates.review` is `advisory_unless_high`
(`.harness/harness.json`, read by me, not taken from the lead), so a med maximum with an empty
`must_fix` clears. Feature station `review`; T-01 and T-02 `done`; T-03 `ready` and correctly
undone. `cycles_used: 7` against budget 10 — SIMPLIFY and the panel each reported 0 send-backs, so
this phase added ZERO. 15 runs against budget 20, under the tripwire.

**Next: NOTHING IN THIS PHASE.** Ship is the main session's and this orchestrator stops here by its
own dispatch. Two things wait for the operator, both in my return: **T-03**
(`execution_mode: main-session-direct` — `check-domain --resolve` answers NOBODY for
`.claude/skills/harness/SKILL.md`; docs, traces REQ-02/REQ-06, phrase-exact `verify:` because it has
no reviewer) is a pre-ship main-session step, and until it lands `gh-sync.py status` refuses and the
goal-check cannot pass REQ-06; and **F-1's disposition** (Q7 below), which is scope and so not mine.

**THE PANEL (`runs/panel-c4-validator/digest.md`).** Four reviewers in one wave, each recording its
OWN verdict, none skipped pre-emptively. code PASS (6/6 REQ, 9/9 SC), qa PASS gate-only at the pin
(`matrix_ok: true`), security PASS in-scope with a six-boundary STRIDE table and no new finding, ui
PASS having judged the one surface in its lens. Three surviving findings, none gating; seven
dismissed WITH reasons, including SC-08 escape smuggling (the operator-signed PF-334e1b37) and the
SIMPLIFY nest-collapse (traced across all three input classes, behaviour-identical).

**Seven backlog rows for the ship briefing, none gating** — full text in the two run digests. F-1
(med, chore; ABSORBS SIMPLIFY's B-1 and the old Q6): `run_dir_grant_globs`'s `walk()` admits ANY
`/runs/` grant as a write grant, so a read-flagged `runs/*/**` grant makes the guard accept every
slug while `globs` is non-empty, no SKIPPED line prints and exit is 0 — **it looks like it ran**.
F-2 (med, chore): that same closure is grade 2; sequence it WITH F-1 or the second re-touches the
first. F-3 (low, enhancement): the refusal prints the `[.]harness/` path three lines before its
explanation. B-2 (chore): a fourth spelling of the run-dir path shape, fixable only by rewriting
three PRE-EXISTING regexes. B-3 (chore): a duplicated test fixture block, fixable only by editing
PRE-EXISTING `_checkout()`. B-4 (enhancement): the derivation subprocess runs unconditionally,
~64ms of ~105ms per governed dispatch — deliberately unapplied, since its alternative puts a SECOND
spelling of the pattern in bash and drift makes the guard fail OPEN. B-5 (chore, from the panel's
adequacy notes): the mandatory matrix floor is `unit` ALONE, and the only end-to-end proof of the
refusal is `integration`, added ABOVE the floor with nothing holding it there next cycle.

**THE MIRROR REFUSED THE REVIEW STATION, TRUTHFULLY, AND IT IS NEVER A GATE.** `gh-sync.py status
<feature-dir> review` → `REFUSED — station review refused — not every task in plan.yaml is done or
abandoned` (`gh-sync.py:1318-1319`; `finished_stations()` is `done`/`abandoned` only). T-03 is
`ready`, so the refusal is CORRECT about the plan. It refuses BEFORE `_record_station`, so the cards
stay at Building; plan.yaml on disk is the authority and already reads `review`. Re-run it once T-03
lands — idempotent. Do NOT falsify T-03's station to make the mirror pass.

Trust (claim — pointer — ORCHESTRATOR-MEASURED unless attributed):
- **F-1's premise, verified at source BY ME rather than accepted:** `walk()` at
  `harness_boundary.py:834-843` carries no read filter, while `harness_yaml.py:408` reads
  `... and "path" in entry and not entry.get("read")`. The docstring's own words — "Every
  write-grant glob" — are what the code no longer guarantees.
- **The SIMPLIFY apply is behaviour-identical — I read the diff, not the claim.** Every message
  string, the `sys.exit(2)` path, the `hb.*` call sites and the `try / except SystemExit: raise /
  except Exception` fail-open structure unchanged; `bash -n` clean; 24 insertions, 23 deletions.
- **The suite is green, re-measured BY ME, not tail-read:** `RUNNER_EXIT=0` captured into a
  variable, `grep -c '^FAIL '` = 0, 5403 output lines, pool `8 workers, 80 files`. **Discovery
  volume equals the pre-SIMPLIFY baseline**, so the green is not a gate that stopped discovering.
  qa reproduced all four numbers independently at the pin.
- **The pin satisfies INV-33, checked not assumed:** `git show <review_sha>:plan.yaml | cmp -`
  against disk is byte-equal. The pin moved ONCE, deliberately, after T-01/T-02's stations were
  corrected from `review` to `done` (D-23: `done` is a task's finished station, `review` is the
  FEATURE's); `git diff --stat 64924e19..6c037de4 -- .claude tests` is EMPTY.
- **The panel wrote no source and moved nothing:** `git status --porcelain` after it returned showed
  only its four untracked reviewer notes — no ` M` line — and `review_sha` unchanged.
- ATTRIBUTED, NOT re-measured because none of it gates: the four SIMPLIFY angle readers and their
  counts (`2026-09-08-1-eng`); the ~64ms/~105ms measurement; the panel's case counts (56 unit,
  69/69 integration).
- Earlier trust stands, NOT re-derived: the operator signature at `80ce35d1` (BRIEF and plan both
  `approved`, five `rulings` overruling R-1..R-5); the adequacy A/B proving `test-dispatch-guard.py`
  CAN report red (8 FAIL against the pre-change guard, md5 `ca904b2906ad8d44662db428cb2dbc89`).

Dead ends for the next phase:
- Do NOT re-run the panel or re-litigate its seven dismissals (D-a..D-g), R-1..R-5, the test-first
  ordering ruling, the `unit` kind ruling, the three `bugfix` predicate evaluations, or the four
  behavioural-equivalence rulings. All closed across cycles 1–4.
- Do NOT hand T-03 to a squad, and do NOT mark it `done` to satisfy the mirror.
- Do NOT rewrite `qa-c3.md`. The corrected attribution lives in the 3-eng digest and `qa-c4.md`.
- Do NOT `cp` a fixture into `/tmp` or a scratch worktree for an A/B — `bash-write-guard.sh` refuses
  it. Pointing `DISPATCH_GUARD_BIN` at the main checkout's pre-change guard is the working route.
- Do NOT re-pin `review_sha` unless a commit lands that touches a reviewed code path OR changes
  `plan.yaml`. A STATE.md or feature.json commit alone does not move it.
- Do NOT run the suites without `env -u HARNESS_AGENT_TYPE`.
- The handoff note still cannot be written (Q2a). This `## Current` is the supported disk-only
  substitute.

Working set: runs/panel-c4-validator/digest.md, notes/review-harness-code-reviewer-c4.md,
plan.yaml (T-03 at 491), .claude/skills/harness/bin/harness_boundary.py,
.claude/skills/harness/bin/dispatch-guard.sh

## Open Questions

- Q7 (SCOPE, for the operator, non-blocking, raised by the validator lead): F-1 is a silent
  fail-open in the very guard this bug adds, and the remedy — one `not entry.get("read")` conjunct
  plus a unit case for the class — is smaller than the backlog row describing it. The panel and I
  both rate it med and NON-gating (latent, no live trigger, write-time control intact), so no fix
  cycle is owed. Whether it lands inside BUG-124 or as backlog changes approved scope, so it is the
  operator's, not mine.
- Q2 (harness defect, one class, three symptoms, all for the harness owner): worktree-hosted
  features are graded against the OWNER checkout root. (a) `handoff_done_when.problems()` receives
  the owner root while the note's prefix comes from its own worktree-relative path
  (handoff_done_when.py:11,51-54) and an absolute pointer is refused as "is absolute" (:69-70), so
  there is NO legal spelling and no handoff note can be written at all. (b) `check-state.sh` globs
  the owner checkout's `.harness/*/features/*` (:118-120), so a full run from inside this worktree
  cannot grade this feature. (c) observed this cycle: `gh-sync.py` must be invoked from the WORKTREE
  for `status` and from the MAIN checkout for `ship`, so two subcommands disagree about the root.
- Q5 (harness defect, raised by qa at the c4 gate, non-blocking, NOT a BUG-124 fix cycle):
  `test_matrix.bugfix`'s third leg `{__bug_class__, if: match_bug_class}` is structurally
  unresolvable in this project — no bug-class taxonomy exists for the predicate to match against.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). Pasting one verbatim into a dispatch will be
  refused once the change reaches the main checkout. Left as-is on purpose.
- Q4 (operator, already accepted at signature): T-02's SECOND parse of `team-config.yaml` inside the
  derivation subprocess — what makes case 23 distinguishable from 21.
