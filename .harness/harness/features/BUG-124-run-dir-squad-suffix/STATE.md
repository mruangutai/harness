# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: [.]harness/harness/features/BUG-124-run-dir-squad-suffix/runs/2026-09-08-1-eng/digest.md
- squad: eng
- status: in_progress

**THE BUILD IS CLOSED AND THE SEAM IS CROSSED.** The qa gate PASSed (`matrix_ok: true`,
`must_fix: []`); SIMPLIFY ran and landed one behaviour-identical apply; the feature station is
`review` and T-01 and T-02 are `done` (D-23: a task's station is `done` in the same act as its
commit — `review` is the FEATURE's station, never a task's). T-03 stays `ready` and correctly
undone: `execution_mode: main-session-direct`, `check-domain --resolve` answers NOBODY for
`.claude/skills/harness/SKILL.md`. `cycles_used: 7` against budget 10 (SIMPLIFY reported 0
send-backs). Twelve runs against budget 20.

**Next (cited to plan.yaml):** the validation panel, dispatched to `harness-validator-lead` against
the pinned `review_sha`. After the panel: `must_fix` resolution, then STOP — ship is the main
session's, and T-03 is a named pre-ship main-session step, not a matrix gap and not squad work.

**THE MIRROR REFUSED THE REVIEW STATION, TRUTHFULLY, AND IT IS NEVER A GATE.**
`gh-sync.py status <feature-dir> review` → `REFUSED — station review refused — not every task in
plan.yaml is done or abandoned` (`gh-sync.py:1318-1319`; `finished_stations()` is `done` and
`abandoned` only). T-03 is `ready`, so the refusal is CORRECT about the plan and is not a defect to
route. It refuses BEFORE `_record_station`, so the parent and sub-issue cards stay at Building until
T-03 lands; plan.yaml on disk is the authority and already reads `review`. Re-run the same command
once T-03 is done — it is idempotent. Do NOT falsify T-03's station to make the mirror pass.

**SIMPLIFY, complete (`runs/2026-09-08-1-eng/digest.md`).** All four angles ran as separate
parallel read-only spawns; none returned empty. Six findings, deduplicated. ONE apply, by
`harness-backend-dev` (picked over `harness-dev-ops` — both hold `bin/**`; the author keeps the
write, and dev-ops read the finding, so reader and fixer stay separate). The apply collapsed
`dispatch-guard.sh`'s `if refs and not globs: / elif refs and globs:` into a single nest on `refs`,
inner bodies byte-identical apart from indentation.

**Four SIMPLIFY skips, none gating, all four needed by the ship briefing as backlog rows** —
reasons in the run digest: B-1 (chore) `run_dir_grant_globs`'s walker re-implements
`harness_yaml.manifest_domains`' walk and drops its `not entry.get("read")` filter, two readers,
deduplicated, carries Q6; B-2 (chore) `_RUN_DIR_REF_RE` spells the run-dir path shape a fourth time
and the fix rewrites three PRE-EXISTING anchored regexes the diff never touched; B-3 (chore) the
`test-dispatch-guard.py` persona-copy block duplicates `_checkout`'s and the fix edits PRE-EXISTING
`_checkout()`, on which every other integration case depends; B-4 (enhancement) `dispatch-guard.sh`
spawns the run-dir derivation subprocess unconditionally, measured ~64ms of ~105ms on every governed
dispatch — highest value, deliberately unapplied because its alternative puts a SECOND spelling of
the run-dir pattern in bash and drift from `hb.run_dir_refs` makes the guard fail OPEN.

Trust (claim — pointer — verified-at the pinned `review_sha` unless restated; ORCHESTRATOR-MEASURED
unless attributed):
- **The apply is behaviour-identical — I read the diff myself, not the claim.** Every message
  string, the `sys.exit(2)` path, the `hb.*` call sites and the
  `try / except SystemExit: raise / except Exception` fail-open structure are unchanged;
  `refs and not globs` / `elif refs and globs` over a list is exactly `if refs:` + `if not globs:` /
  `else:`. `bash -n` clean. 24 insertions, 23 deletions, one file.
- **The suite is green at the apply, re-measured BY ME, not tail-read:**
  `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh` from the worktree
  root → `RUNNER_EXIT=0` (captured into a variable), `grep -c '^FAIL '` = 0, 5403 output lines,
  pool `8 workers, 80 files`. **Discovery volume equals the pre-SIMPLIFY baseline** — 5403 lines,
  80 files — so the green is not a gate that stopped discovering.
- **The pin satisfies INV-33, checked not assumed:** `git show <review_sha>:plan.yaml | cmp -` against
  disk is byte-equal. The pin was moved once, deliberately, after T-01/T-02's stations were corrected
  from `review` to `done`; the code paths between the two commits are identical.
- Earlier trust stands unchanged and is NOT re-derived here: the qa gate at `418a9eb6`
  (`notes/qa-c4.md`, all four cycle-3-red files individually green, 80/80 discovered); the
  adequacy A/B proving `test-dispatch-guard.py` CAN report red (8 FAIL against the main checkout's
  pre-change guard, md5 `ca904b2906ad8d44662db428cb2dbc89`); T-01/T-02 `verify:` both exit 0; the
  operator signature at `80ce35d1` (BRIEF `approved`, plan `approval.status: approved`, five
  `rulings` overruling R-1..R-5).
- ATTRIBUTED (eng lead, `2026-09-08-1-eng`), NOT independently re-measured because none of it
  gates: the four angle readers and their finding counts; the ~64ms/~105ms EFFICIENCY measurement.

Dead ends for the next phase:
- Do NOT re-litigate R-1..R-5 (operator `approval.rulings`), the Q1 test-first ordering ruling, the
  `unit` kind ruling, the three `bugfix` predicate evaluations, the assertion-strength review, or
  the four behavioural-equivalence rulings. All closed across cycles 1–4.
- Do NOT re-flag B-1..B-4 as simplification findings. They were read, costed and deliberately
  deferred; a panel may still rule on their CORRECTNESS.
- Do NOT rewrite `qa-c3.md`. The corrected attribution lives in the 3-eng digest and `qa-c4.md`;
  rewriting a recorded artifact to look better falsifies the record.
- Do NOT hand T-03 to a squad, and do NOT mark it `done` to satisfy the mirror.
- Do NOT `cp` a fixture into `/tmp` or a scratch worktree for an A/B — `bash-write-guard.sh` refuses
  it. Pointing `DISPATCH_GUARD_BIN` at the main checkout's pre-change guard is the working route.
- Do NOT re-pin `review_sha` unless a commit lands that touches a reviewed code path OR changes
  `plan.yaml` (INV-33 is a byte comparison over plan.yaml, not a commit comparison).
- Do NOT run the suites without `env -u HARNESS_AGENT_TYPE`.
- The handoff note still cannot be written (Q2a). This `## Current` is the supported disk-only
  substitute.

Working set: plan.yaml (tasks at 231; T-03 at 491), runs/2026-09-08-1-eng/digest.md,
notes/qa-c4.md, .claude/skills/harness/bin/harness_boundary.py,
.claude/skills/harness/bin/dispatch-guard.sh

## Open Questions

- Q2 (harness defect, one class, two symptoms, both diagnosed, both for the harness owner):
  worktree-hosted features are graded against the OWNER checkout root. (a)
  `handoff_done_when.problems()` receives the owner root while the note's feature-dir prefix comes
  from its own worktree-relative path (handoff_done_when.py:11,51-54), and an absolute pointer is
  separately refused as "is absolute" (:69-70), so there is NO legal spelling and no handoff note
  can be written at all. (b) `check-state.sh` globs the owner checkout's `.harness/*/features/*`
  (:118-120), so a full run from inside this worktree cannot grade this feature. (c) same class,
  observed this cycle: `gh-sync.py` must be invoked from the WORKTREE for `status`, and from the
  MAIN checkout for `ship` (it refuses a feature dir under `.claude/worktrees/`), so the two
  subcommands of one tool disagree about which root to stand in.
- Q5 (harness defect, raised by qa at the c4 gate, non-blocking, NOT a BUG-124 fix cycle):
  `test_matrix.bugfix`'s third leg `{__bug_class__, if: match_bug_class}` is structurally
  unresolvable in this project — no bug-class taxonomy exists for the predicate to match against.
  Pre-existing harness-config condition; belongs to the harness owner.
- Q6 (raised by the eng lead at SIMPLIFY, non-blocking, ROUTED BY ME to the panel as in-scope):
  `run_dir_grant_globs` counts any `/runs/` grant as a WRITE grant, so a future read-only `/runs/`
  grant would let the guard accept a slug that squad cannot write. Latent, not live — no such grant
  exists in `team-config.yaml` today. It stays backlog row B-1 unless the panel judges it gating.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). Pasting one verbatim into a dispatch will be
  refused once the change reaches the main checkout. Left as-is on purpose.
- Q4 (operator, already accepted at signature): T-02's SECOND parse of `team-config.yaml` inside the
  derivation subprocess. It shipped as designed and is what makes case 23 distinguishable from 21.
- CLOSED this cycle: the eng lead's SIMPLIFY Q1 — answered by me at rung 1 (see Q6): backlog row,
  and named to the panel rather than suppressed.
