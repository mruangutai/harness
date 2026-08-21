# STATE

## Current

- feature: FEAT-30-worktree-per-feature · phase **validate** (recorded here; the shape gate denies a
  `phase` key in feature.json) · status Review / in_review
- cycles_used: **7 of 13**, six remaining. qa, simplify and docs each reported ZERO send-backs, so the
  validate phase has added none. Runs 10 of 20, informational.
- review_sha: pinned at the validate commit (feature.json). **I ran the qa segment BEFORE pinning,
  contrary to INV-6** — `check-state.sh` caught it. No harm materialised: the dispatch carried the
  explicit range `49c528a..fbb3bc0` and qa's numbers match mine exactly. The ordering was still wrong.
- All ten tasks read `status: done`, verified. Both approvals read `approved` (`BRIEF.md:275-279`,
  `plan.yaml:4-5`). Surface `49c528a..fbb3bc0`, sixteen source/config files.

**Three segments complete, all PASS, all zero send-backs.** qa gate PASSES
(`runs/2026-08-21-01-validator/`): `matrix_ok: true` per task for all ten, 12 SCs `met` at that tier;
the lead returned PASS with `severity_max: high` and `must_fix: []`, overriding its own gate-on-high
rule because DEC-174 bars every agent from remediating F-1/F-2 — **I accepted that**, since FAIL is for
when looping back is meaningful. Simplify: **EMPTY apply set** (`runs/2026-08-21-02-eng/`), four angles
parallel, five candidates all declined, nothing touched the enforcement layer. Docs: **SPEC.md +120/-9**
(`runs/2026-08-21-03-product/`), both tools previously undocumented; `BUILD.md` earns no row.

**Suites, my own measurement:** unit exit 0 **179/0**; integration exit 0 **213/0**. Reproduces qa.

**Live-instance gap — the weakest point.** `git worktree list` shows two checkouts: this one (the MAIN
checkout, on the feature branch) and `.claude/worktrees/FEAT-31`, a legacy ONE-segment tree. **The
two-level `<segment>/<repo>/<id>` layout T-04 exists to serve has zero live instances**, only fixtures.
FEAT-30 was built in the main checkout, so it did not dogfood the isolation it delivers.

**No governance regression on the live tree, both directions.** Inside `.claude/worktrees/FEAT-31`,
`check-domain.sh --resolve` returns `harness-documentor` for a SPEC path and `harness-backend-dev
harness-dev-ops` for a `bin/` path — identical to root. T-04's resolution is depth-agnostic in practice.

**My own measurements, not relayed:**

- **SC-01b PASSES.** Exit 0, 14 assertions: four worktrees at once, two per repository via a real
  `fleet.yaml` (repoB's default branch is `master`), four concurrent committers on a barrier, six
  pairwise write-window overlaps asserted, no outside branch advancing. **Its predicate is proven able
  to redden:** 5 trials against a shared checkout, 4/4 committers succeeded each time, zero index-lock
  failures, `IsolationViolation` raised all 5 — so case B's `committer_failed` short-circuit
  (`test-feature-worktree.py:806`) never fired.
- **T-05's red proof is EXACT:** against `4792cd1`'s guard, exit 1 with **exactly 10 FAILs**, all new
  refuse cases, zero pre-existing breakage. At HEAD exit 0, 99 cases green.
- **T-03's recorded red proof is INERT at HEAD.** Its `verify:` mutates `WORKTREES_SEGMENT` and asserts
  only a non-zero exit; that leaves **38/38 grant-parity cases green**, the exit coming from 5
  collateral reds. The 32 agent assertions are SOUND regardless: mutating T-04's real mechanism
  (`checkout_relative` → `return None`) reddens **33 of 38** and 5 of 8 deep-layout, 45 FAILs. That is
  the mutation the verify should carry.
- **F-ALT-1, the simplify pass's only HIGH, is REFUTED.** The switch names are absent from both test
  files (0 occurrences), but flipping `REFUSE_ON_DIRTY`, `REQUIRE_LANDED` and `UNION_APPLY` to `False`
  reddens each suite — 4, 13 and 12 FAILs, 94/104/82 lines reported, exit 1 all three. Coverage is
  behavioural, not by-name. **Do not carry as high.**
- **The real defect behind qa's F-5:** `test-feature-worktree.py` reports NOTHING when it crashes.
  `create_four` carries `dest: None` when a create fails, `case_isolation:196` raises `TypeError`, and
  the exception escapes `main()`'s `try/finally` (cleanup only) — **all 88 results discarded, 13 of 17
  cases never run, exit 1.** Three CLI mutations reproduced it. Any red proof here asserting only a
  non-zero exit cannot tell a reddened assertion from a crashed harness. `test-expertise-merge.py` does
  NOT share it (broken tool → exit 1, 98 reported lines).
- **qa's F-6 is a coverage hole, not a bug.** I ran the missing case: a sibling at
  `.claude/worktrees-old/FEAT-77` is correctly excluded by `list`. `startswith` would include it,
  `commonpath` excludes it. Code right, case absent, ~10 lines.
- **The write guard is a literal-token parser, verified.** `checkout`/`reset --hard`/`rebase` BLOCKED
  for `harness-backend-dev` and `harness-orchestrator` alike (D-04 holds), and `git -C <path> checkout`
  blocked. But `python3 -c "...subprocess.run(['git','checkout',...])"`, a heredoc equivalent, and
  `g=git; $g checkout main` are ALLOWED. The undecidable rule fires for `git --git-dir=/tmp/x` but not
  for a subcommand or command head behind a variable.
- The CLI has **four** subcommands (`create list path remove`), so D-01's record of three undercounts
  the code and matches the intent. SC-04/SC-07 covered both directions with named paths and exits 4/5.
  SC-08's red proof is case1 plus 20 concurrent trials. SC-06 corroborated: `grep -c` = 2 and 6, and
  `harness-orchestrator.md:23-33` is imperative rule text.

**Still to run:** review panel, pm's goal-check, CEO briefing.

## Open Questions

- **Q-V1, OPERATOR, blocking the feature not the gate.** Two high findings inside the blocking gate,
  barred to every agent by DEC-174. **F-1:** `test_kinds.unit.detect`'s glob claims all 32 `bin/`
  scripts while `--kind unit` runs only the 18 in `UNIT_SCRIPTS`, so the unit leg **cannot fail**; eight
  of ten `matrix_ok` verdicts rest on it. **F-2:** `integration.detect` names 6 where
  `run-unit-tests.sh:18` runs 14 — B-1's gap was 8 and is still 8, so this diff MOVED B-1. **Fix F-1's
  consistency check FIRST**; it turns F-2's hand-maintained list into a loud failure.
- **Q-V2, OPERATOR.** Mirror unsynced: 11 FEAT-30 INV-26 rows — sub-issues #616-#625 OPEN against a
  plan reading `done`, parent #572 at `Building` where the plan derives `Review`. Ordering is already
  satisfied, so the remedy is ten `gh-sync.py close-task` runs. My attempt was **denied by the
  permission classifier** as outward-facing — a correct denial, not to be worked around.
- **Q-V3, OPERATOR, verified twice.** `BUILD.md:147-148` claims "the hook cannot see writes made via
  Bash", falsified by `settings.json:28,36` registering `bash-write-guard.sh` as a `PreToolUse` Bash
  hook. The claim is restated in the **preloaded** `harness-team` and `harness-zero-micro-management`
  skills as the rationale for serialization, so every lead reasons from it at spawn. My own probe
  independently confirms the hook fires on Bash. No propagation checker exists. Needs its own flow.
- **Q-V4, plan-level.** T-03's `verify:` mutation target is stale, so future re-verification gets false
  assurance. One line: target `checkout_relative`. `plan.yaml` carries the operator's signature.
- **Q-V5.** Issue #626's scope may be one entry short: `DECISIONS-INDEX.md:114` has DEC-95 asserting
  `.harness/` is per-worktree state — a fourth falsified spelling beyond the three named.
- **L-1 (med), real.** `expertise-merge.py:37` accepts `[A-Za-z]{1,3}` ids where
  `check-expertise.sh:44` accepts `[A-Z]{1,3}`: a lowercase id is accepted, cap-counted and written,
  then FAILed by the checker. Narrowing the tool is a REGRESSION (silent drop vs loud reject); the
  remedy is an `ENTRY_RE` drift detector mirroring case 8's treatment of `CAPS`.
- **Harness defect, second recurrence.** The member digest schema has no shape for a read-only review
  dispatch and differs BY ROLE: one instruction `suite: none` produced `pass`, `none` and `n/a` from
  three personas, each citing its own schema, all validated.
- **T-05's signed intent was internally contradictory** and was not papered over. The DEC-153 carve-out
  is `if re.match(r"^\.claude/worktrees/", rel): continue` at `bash-write-guard.sh:688`, running BEFORE
  `classify` — blanket and depth-agnostic, so the intent's refuse-half is unreachable by construction.
  The comment states why that is deliberate. **For the panel to affirm or contest.**
- Backlog: efficiency F-1 (GATE 3 spawns two git subprocesses per artifact file, ~1.3s over 83 files vs
  ~10ms via one `ls-tree` plus local hashing; `git hash-object` without `--path` applies no
  `.gitattributes` filters, so local hashing reproduces it exactly); F-A (`create_four` could reuse
  `create_one`, low); F-ALT-4 (`.claude/commands/harness.md` restates a worked path as unchecked prose,
  guard resolves to nobody, recommendation *leave*); `.harness/README.md` contradicts disk on three
  counts (belongs to the FEAT-21/22 + DEC-182 migration); SPEC.md's Index `Cost` column has no
  documented formula and two figures are disclosed estimates; `test-expertise-merge.py` labels its
  seventh case group "case8" with no case7 — all seven ARE invoked, cosmetic.
- SC-06 named by no task (W3/Q27, accepted with the signature); Q11, Q12, Q14, Q15, Q16 carried; D-09
  unchanged. Q21's recorded subject is **T-10, not T-04**; my qa dispatch's T-04 premise was
  **inverted** — both its test files are integration-runner scripts and neither runs under `--kind
  unit`, so the leg lacking execution evidence is unit.
- Issue #626 is filed, unblocked, and OUT OF SCOPE here. `check-state.sh`'s other rows are FEAT-26,
  FEAT-28 and FEAT-29 board drift; the count is a shared mutable global, so scope by name never count.
