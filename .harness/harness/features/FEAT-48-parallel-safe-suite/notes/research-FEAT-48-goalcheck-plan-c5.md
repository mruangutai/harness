# Goal-check — FEAT-48 plan, cycle 5 (fresh grade)

**Does this plan deliver the operator's stated intent? YES.** #1053's two commitments — remove the
sibling that mutates shared state, and unlock the parallel runner — are each owned by tasks with
discriminating verify blocks, every REQ traces to a task and every task to a live REQ. The
census-shape change WORKED: a fifth rot needs no new task and falsifies no numeral. Nine findings,
**0 high/critical/unrated, so nothing gating**: 2 med, 7 low. I would hand this to the panel as
SIGNABLE, with F-01 as a one-field pre-signature repair I recommend but do not gate on.

All anchors below re-derived at the tip (uncommitted cycle-5 diff over `2a5cbada`); every dispatch
anchor was dated and none was copied.

## 1. Did the census-shape change work? VERDICT: YES

D-10 as amended defines scope by a five-step procedure (`plan.yaml:159-171`) and states no
scope-defining count; its EIGHT-sites/FOUR-files figure is explicitly a dated non-binding
observation (`:172-186`). I re-derived it at source: 8 sites, 4 files — `test-check-state.py:2241`,
`:2377`, `:3286`, `:3591` (the era mutant, from `case_inv32_era_guard_is_load_bearing:3584`, called
unconditionally at `:4317`), `test-feature-worktree.py:583`, `test-bash-write-guard.py:898`,
`test-check-domain.py:1473` and `:3285`. The figure is true.

**Fourth-rot simulation, performed.** A sibling merges `test-new-thing.py` under
`.claude/skills/harness/bin` tomorrow, writing `.mutant-new-thing.sh` into live bin.
(a) **T-02 fixes it, with no plan edit**: `plan.yaml:503-508` authorises the doer to fix a site in a
THIRD file under the lanes glob "in the same shape" and name the addition in the receipt; the glob
`.claude/skills/harness/bin/**` already lane-resolves it (`:14`, `:200-206`), so no `lanes:` row and
no new task. (b) **T-03's live half goes red** — `live.returncode == 0` at `:601`, the only
whole-tree assertion in the plan — and after T-03 lands, so does CI's unit step on every PR.
(c) **No numeral or basename becomes false**: D-10's EIGHT/FOUR is dated and sha'd; T-02's "five
sites in these two files" (`:497`) is scoped to two named files; T-03's `discovered 59` (`:659`) is
dated and the verify floor is `>= 50` (`:602`) — I re-derived 59 at the tip, so a 60th file cannot
move it; the ten `want` entries are pinned at `ea6f51f`; D-09's census contract (`:130-137`) counts
only what FEAT-48 adds. A list was not relabelled: the scope is genuinely derived.

- **F-02 (low)** D-10 claims the census is "deterministic on a given tree" (`:167`), but two of the
  eight mutants embed `os.getpid()`, so two doers print textually different SITE lines. Consequence:
  a reviewer comparing two receipts sees `.feat50-check-domain-12345.sh` vs `-67890.sh` and reads
  drift where there is none. The (file, shape) pair converges; the line does not.
- **F-03 (low)** The derivation instrument and the completeness gate are different instruments. The
  census watches `(size, st_mtime_ns)` of files *directly* under bin (`:161-165`); T-03's scan is
  repo-wide, static and taint-based. A `chmod`/`utime`-only site, or one under a subdirectory, is
  census-invisible and scan-visible. Consequence: T-03 returns BLOCKED on a site no task owns →
  re-plan. Latent, not live: all 8 sites today create or rewrite a top-level bin file.
- **F-04 (low)** The census is a ~250s pass over the live tree (`:170`). A sibling agent editing any
  file in bin/ during it fabricates a SITE line attributed to whichever test happened to be running.
  Consequence: the doer hunts a site that does not exist. D-11 asserts no agent writes bin during a
  run (`:283-287`); nothing enforces it.

## 2. Is PF-58719ff7b430616b91b5a7cfe49bde10 closed? VERDICT: CLOSED, all three groups

| group (re-derived at tip) | owner | verdict |
|---|---|---|
| `test-bash-write-guard.py:891,:898,:901,:906` | T-07 `files:` (`plan.yaml:1240`) | CLOSED |
| `test-check-domain.py:3275,:3285,:3288,:3293,:3367` | T-01 `files:` + SITE B intent (`:358-364`) | CLOSED |
| `test-check-state.py:2241,:2377,:3286,:3591` | T-02 `files:` + intent naming all four (`:498-503`) | CLOSED |

T-02's verify (`:456-489`) is satisfiable on faithful execution: its run set is read from its own
`files:` list (I loaded the plan with `safe_load` — it parses, and the two paths resolve), it
asserts `appeared` and `moved` both empty, and both files are in `INTEGRATION_SCRIPTS`
(`run-unit-tests.sh:31`) so they are green at the tip. T-03's `live.returncode == 0` is **reachable**
by the chain T-01 → T-02 → T-07 → T-03: the eight sites are the whole static set, and my independent
sink×taint sweep over all 59 discovered test files found no ninth candidate (every other
`shutil.copy`/`copytree` writes an `args[1]` tempdir, which the rule does not flag). The chain's last
edge is prose, not `depends_on` — §3.

## 3. The T-03/T-07 ordering hole — VERDICT: **med, not gating; signable**

Confirmed at source: `T-03.depends_on: [T-01, T-02]`, `T-07.depends_on: [T-02]` (`:559`, `:1233`),
and `teams/build.yaml:83` reads `depends_on: from_task_depends_on` with `mutates_repo: true` at `:78`
forcing one-at-a-time dispatch. So T-03 and T-07 are one ready wave, serialised in *some* order —
and **both id order and file order put T-07 last** (file order is T-01,02,03,04,06,05,07). The
failure is therefore near-certain, not a coin flip: T-03 dispatches first and its verify reddens on
`test-bash-write-guard.py`'s live site.

Why it is nonetheless **med**: the failure cannot pass silently. T-03's verify *is* the guard the
doer cannot bypass — `live.returncode == 0` is unsatisfiable while the site stands, the intent
instructs BLOCKED (`:621-625`), and the lead cross-checks the verify string verbatim. The cost is one
wasted wave plus one `on_fail: loop_back` cycle (`build.yaml:89`), with a residual risk that a lead
loops back onto T-03 instead of reading the BLOCKED reason.

**(i) Could T-07's work be ordered without `depends_on`? Yes, and the minimum repair needs no new
tool capability.** Renumbering fails: `apply` can add a new id, so T-03 could be re-issued as T-08
with `depends_on: [T-01, T-02, T-07]` and T-03 stationed `abandoned` — but T-04, T-06 and T-05 all
chain off T-03, so that cascades to four re-issued tasks and litters the plan with abandoned ids.
There is no free id below T-03, so id-ordering cannot be exploited. The cheap repair is the one the
plan already half-wrote: **`amend --key tasks --id T-02 --field intent` is a TEXT field, which
`amend` accepts** — strike `:509` ("The test-bash-write-guard.py site is NOT yours: T-07 owns it")
so T-02 absorbs the third file under its own already-written widening clause (`:503-508`), and
station T-07 `abandoned`. One field, one station splice, no cascade. It costs the file T-07's
ownership check; T-03's live zero still covers it.
**(ii) Is hand-sequencing by the orchestrator adequate? No.** `steps_from: plan_tasks` expands waves
off `depends_on` and nothing else; an ordering held only in an orchestrator's context is not in the
artifact the operator signs, is not reproducible by a fresh orchestrator context that reads
`plan.yaml`, and disappears on any re-dispatch or loop_back. It is a same-run stopgap, not a
substitute for a DAG edge.

- **F-01 (med)** — the above. Consequence: one build wave and one loop-back cycle burned, on a
  feature whose whole subject is gates that report unreliably.

## 4. Intent coverage, re-derived — VERDICT: complete, two gaps

Every #1053 commitment traces: the sibling mutating shared state → REQ-01 → T-01/T-02/T-07 (+ T-04's
runtime check); "a green serial run is not evidence of independence" → REQ-02 → T-03; parallelise the
runner → REQ-03/04/05/06 → T-04/T-06; "not done here: bisecting" → honoured, the plan bisects
nothing. Task→REQ: T-01 [01], T-02 [01], T-03 [02,07], T-04 [01,03,04,05,07], T-06 [03,05,06], T-05
[08], **T-07 [REQ-01] — a live REQ**. No orphan task; REQ-01..08 all owned. D-04 stays honest: D-10
refuses an allowlist in terms (`:207-212`), T-03 carries no pragma and no allowlist file (`:744-746`),
and the derived set makes membership open, not optional. The escalation boundary (`:200-206`) is
vacuous today — I re-derived that all 59 discovered test files sit under the lanes glob.

- **F-07 (med)** No criterion would fail if #1053's own symptom persisted. SC-05's ten `--kind all`
  runs are declared non-probative by the BRIEF itself (`BRIEF.md:127-131`), and nothing asserts
  `test-gh-sync.py` (`run-unit-tests.sh:31`, integration) passes N consecutive 8-worker runs.
  Consequence: if the real collision partner is a class neither half covers (D-11's third and fourth
  uncovered classes, `:262-272`), FEAT-48 ships all-green and #1053 stays reproducible. See Q1.
- **F-08 (low)** #1053's `## Scope` still reads "Folded into FEAT-47" (verified via `gh issue view
  1053`); no task updates the issue body. BRIEF's half of cycle-4's PF-04e9 *is* fixed
  (`BRIEF.md:213-224` now states the boundary as settled).
- **F-09 (low, info-adjacent)** #1053 headlines 5.3x; SC-06 accepts <=120s against a 247s baseline,
  i.e. 2.06x. A 119s outcome passes every criterion while delivering ~40% of the advertised win.
  BRIEF `:139-146` argues 120s as noise tolerance, which is reasonable — but the *speed* commitment
  is graded by nothing tighter.

## 5. Satisfiability of all seven verify blocks at the tip — VERDICT: yield ZERO unsatisfiable, one under-specified

Swept for the cycle-1..4 class (a block that greps a moved line, counts a moved set, or asserts a
changed value). Confirmed at the tip: `"${SCRIPTS[@]}"` occurs **only** at `run-unit-tests.sh:148`,
so T-06's `not serial` leg is both satisfiable and discriminating (`${SCRIPTS[@]/#/$BIN_DIR/}` does
not contain it, and `"${UNIT_SCRIPTS[@]}"` does not either); `--check-kinds` exits 0 printing zero
`PASS`/`FAIL` lines and `--kind nope` exits 2 (both run, both as asserted); T-07's `red` grep target
`bash-feature-checkout-red` exists at `test-bash-write-guard.py:916` and is printed as `ok    {name}`
at `:924`; T-01's `crash_case` grep target exists at `test-check-domain.py:1482`; T-05's
`gen-decisions-index.py --stdout` is byte-identical to the committed index today (rc=0), so the drift
leg is satisfiable and the 18 needles are each instructed in the intent; T-04's asserted `pool: 3
workers, 3 files` matches the mandated summary spelling.

**T-06's `int(ctrl[0]) > 0` — cycle 4's unroutable leg — is ROUTED, and I measured it.** Built an
isolated bin copy in a tempdir, wrote `git show ea6f51f:.claude/skills/harness/bin/
test-check-domain.py` into it, polled the copy's `feature_schema.py`: **4,764 broken reads of 491,176
polls**, while the live module stayed byte- and mtime-identical. So the amendment routed it by the
mechanism named at `plan.yaml:1085-1099` (isolated bin copy), and `control method: isolated bin copy`
plus a non-zero control are both obtainable without reopening the hazard on the live tree. The
`len(runs) == 10` and `set(runs) == {"0"}` legs are ordinary instructed output (`:1116-1120`).

- **F-09b/F-05 (low)** T-03's verify requires exactly one `discovered ` line (`len(disc) == 1`,
  `:601`) while the intent says to print root/discovered "in both modes" (`:667`) and the live
  invocation also scans fixture tempdirs as cases (`:749-786`). A faithful doer printing the pair per
  scan reddens a correct implementation. One-line repair: say the pair is printed only for the
  top-level invocation's own scan.
- **F-06 (low)** The `ea6f51f` copy run inside an isolated root exits 1 with a `FileNotFoundError`
  traceback (`test-check-domain.py:1770`, reading `<iso-root>/.harness/team-config.yaml`) *after* the
  schema case has produced the window. T-06 asserts no exit code for the control, so the leg holds —
  but the doer pasting verbatim output will paste a traceback and may read it as a failed control.

## 6. Residual staleness — VERDICT: 30 anchors/numerals checked, 1 finding

Re-derived at the tip and **true**: `AGENTS.md:8` (exact phrase), `check-domain.sh:102` (PYTHONPATH
export) and `:125` (`sys.path.insert`), `run-unit-tests.sh:147-157` (serial loop) and `:60`
("Drift detector:"), `harness_boundary.py:44`/`:53`/`:84` (the three resolvers, all three ranges),
`test-check-domain.py` SITE A 1470-1492 and SITE B 3275-3289 with callers `:3293`/`:3367`,
`test-bash-write-guard.py` 891-915, `discovered 59`, DECISIONS.md `192 of 192` em-dash headings with
last `DEC-209`, D-10's EIGHT-in-FOUR, all four `test-check-state.py` mutant basenames, the era case's
unconditional call at `:4317`, `test-feature-worktree.py:583`, D-11's `117 files at ccf674a`
(sha-carrying; 120 today), and the two verify grep targets above. Dated-and-labelled but drifted:
`test-check-domain.py:1772`/`:1778` (now `:1770`; the plan already states these drift by two lines
and marks them illustration, `:611-616`).

- **F-10 (low)** `plan.yaml:382` — "Measured cost: 48ms for 111 files" carries **no sha and no date**,
  and bin holds 120 files today (I measured `copytree` at 44ms for 122 entries). It is the only
  unlabelled numeral left. Consequence: unfalsifiable, so a later reader cannot tell drift from
  error. D-01's twin figure at `:44` is correctly sha'd.

**Excluded, as instructed and as re-checked:** T-03's ten `want` entries (`:590-594`) are read from
`git show ea6f51f:...` and cannot rot. Also excluded the `panel:` block's cycle-4 pointers — that is
cycle 4's historical record, out of scope, untouched.

## 7. SC linkage — VERDICT: all ten reachable, no BLOCKING question

SC-01 → T-01 verify (evidence `integration` is correct: `test-check-domain.py` is in
`INTEGRATION_SCRIPTS`, `run-unit-tests.sh:31`). SC-02 → T-06's note, empirically demonstrated
reachable above. SC-03/SC-04 → T-03 verify + `UNIT_SCRIPTS` registration (`:788-792`). SC-05/SC-06 →
T-06's note, whose shape T-06's verify enforces including `tree condition:`. SC-07 → T-06 verify plus
`test-run-unit-tests-kinds.py` (integration, `:31`). SC-08/SC-10 → T-04 verify + `test-run-pool.py`
cases (e) and (g), registered integration in the same task (`:955-968`). SC-09 → T-05 verify, drift
leg confirmed satisfiable today. No SC is graded by nothing, none has become unmeetable, and no SC
needs to change — so nothing here is raised as blocking.

## Open questions

- **Q1 (non-blocking)** Does the operator expect #1053 to *close* on FEAT-48? No criterion asserts
  its symptom is gone (F-07). If closure is expected, the cheapest addition is an SC asserting
  `test-gh-sync.py` passes K consecutive 8-worker runs — a BRIEF change, so it is the operator's.
- **Q2 (non-blocking)** F-01's repair (amend T-02's intent, abandon T-07) is a scope-shaping edit to
  an approved-pending plan; I recommend it but it is not mine to make.
