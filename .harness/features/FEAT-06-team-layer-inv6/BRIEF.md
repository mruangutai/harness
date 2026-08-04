# BRIEF — FEAT-06 team layer and INV-6

**Feature id ratified (DEC-133):** `FEAT-06-team-layer-inv6`, coined by the orchestrator at
dir-creation, immutable. pm has no objection to the slug.

**Re-scoped 2026-08-04 on the user's instruction** (`notes/answers-plan-eng.md`). `closes_issues`
is now **#8 #9 #16 #24**. #24 — the unowned qa gate — is the feature's centre of gravity.

## Problem

**Six** things in the harness are a **definition or a check that appears to exist but does
nothing** — the same class of defect FEAT-05 spent a day on, and the reason DEC-174 exists. The one
guarding the project's only blocking gate is issue **#24**, listed first below, and it is why this
feature was re-scoped.

1. **THE ONE THAT MATTERS — the qa gate has an obligation but no owner who reads it.** Issue
   **#24**. `docs/harness/SPEC.md:1978` assigns the job explicitly: "the orchestrator sequences the
   squad segments… qa gates (writes + runs tests, `test_matrix` hard gate) → `loop_back` → dev."
   But `.claude/skills/harness/SKILL.md` — the orchestrator playbook, and the only thing
   `harness-orchestrator` preloads (`.claude/agents/harness-orchestrator.md:8-12`) — contains
   **zero** occurrences of `qa` and **zero** of `test_matrix` (`grep -c -i`, verified at `635ef14`).
   SPEC is not preloaded by the orchestrator. **The obligation exists only where its owner never
   reads it.** The gate has nonetheless run on all three shipped features — because a *lead* added
   the step by hand each time (FEAT-03 `feature.yaml:62`; FEAT-04 `feature.yaml:144`; FEAT-05
   `notes/qa-c0.md`, `qa-c1.md`). `harness.json` sets `gates.qa_gate: blocking`. The only blocking
   gate in the project runs by habit.
2. **Three descriptions of where qa runs, no two agreeing.** `SPEC.md:1978` (ship-feature) has qa
   as an orchestrator-sequenced segment ahead of a **three**-wide panel `{code ∥ security ∥ ui}`;
   `SPEC.md:1980` (review) has a **four**-wide panel `{code ∥ qa ∥ security ∥ ui}`; the shipped
   `.claude/skills/harness/teams/review.yaml` declares `code`, `security`, `ui` and **no qa at
   all** (`:22`, `:36`, `:49`). Reconciling them is in scope and is **D-08** — the user's signature,
   not pm's.
3. **The shipped `review` team omits the qa step.** Issue **#8** — the same hole from the team-file
   side. FEAT-03's validator lead had to add the step by hand at run `2026-07-31-12-validator`
   (`state.yaml` records `code`/`security`/`qa` all at `dispatched_at: seq-1` against
   `team: review`). #8 remains **necessary and is no longer sufficient**: it fixes the panel path,
   not the ship sequencing where SPEC assigns the job.
4. **No `build` team definition exists.** `.claude/skills/harness/teams/` contains exactly
   `review.yaml` and `gate-probe.yaml` at `635ef14`. Every build run to date was dispatched with a
   step list composed at dispatch time — FEAT-03's three build runs (`…-09-eng` T-01, `…-10-eng`
   T-02..T-07, `…-11-product` T-08) all carry `team:` unset or `none`. Issue **#9**.
5. **INV-6 passes on an unpinned feature.** `check-state.sh:156` guards a validator run with
   `not val("review_sha")`, and `val()` (`:136-141`) returns `str(v)` — so the literal string
   `none` is truthy and only an **absent** key trips the invariant. Live on a real feature: this
   feature's own `feature.yaml` carries `review_sha: none` today, and FEAT-05's did for its whole
   plan phase. Issue **#16**.
6. **Both shipped team files fail `yaml.safe_load`** — unquoted `{{feat}}` opening a flow mapping
   inside a `[...]` sequence (`review.yaml:26`, `gate-probe.yaml:32`, re-verified at `635ef14`).
   The YAML validity gate cannot see them: `test-harness-yaml-corpus.py:56-58` globs `.harness/**`
   only. Their `.yaml` extension promises a machine can read them when it cannot.

**#8 and #9 are one original finding split into two tickets**, recorded together as **B-7** in
FEAT-03's ship review
(`.harness/features/FEAT-03-subissue-mirror/notes/ship-review-2026-07-31-16.md:198`). #24 is the
third face of the same finding, seen from the orchestrator's side.

## Goal

Make the blocking qa gate **owned by the agent the spec says owns it**, and make the
team-definition layer machine-readable and complete. After this feature: the orchestrator playbook
states, where the orchestrator actually reads it, that the `test_matrix` qa gate runs as a
validator-squad segment it sequences; every shipped description of where qa runs agrees with the
others and with the file on disk; a `build` team exists and is dispatched by name instead of
composed inline; every team file parses under a real YAML parser with an automated gate keeping it
that way; and a validator run recorded against `review_sha: none` is reported as the violation it
is. Issues **#8**, **#9**, **#16** and **#24** close as a consequence.

## Requirements

- REQ-01: A validator run recorded against an unpinned `review_sha` is reported as a violation by
  the state check, including when the field carries a placeholder the harness already treats as
  unset rather than being absent. *(closes #16)*
- REQ-02: The `review` team, as it ships, runs the project's only blocking gate. *(closes #8)*
- REQ-03: A build phase is dispatched from a named team definition that exists on disk, not from a
  step list composed at dispatch time. *(closes #9)*
- REQ-04: Every team definition the harness ships loads under a real YAML parser, and a future team
  file that does not is caught by an automated gate before anything machine-reads it.
- REQ-05: The "this placeholder means unset" vocabulary has exactly one definition in the tree.
- REQ-06: The shipped design docs describe the team catalog as it actually exists on disk.
- REQ-07: **The obligation to run the blocking `test_matrix` gate is stated where the agent that
  owns it reads it** — an orchestrator that loads only its own playbook knows the gate exists, who
  runs it, and what happens when it fails, without reading a document it never loads. *(closes #24)*
- REQ-08: **There is exactly one account of where the qa gate runs**, and the shipped team file,
  the orchestrator playbook and the design docs all state it compatibly.

## Constraints

- **`build.yaml` covering the eng half of a build is CORRECTLY BOUNDED, not a shortfall** (the
  user's re-scope, `answers-plan-eng.md`). qa was never `build.yaml`'s job: DEC-118 puts qa in the
  Validation squad and the orchestrator owns cross-squad sequencing. **No SC apologises for
  7-of-8, and `build.yaml` is not widened to reach qa.** Both were the wrong repair.
- **DEC-174 carve-out, extended.** The harness plans its own work but does not *execute* changes to
  its own enforcement layer. CLAUDE.md names `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py`, `check-state.sh`, `check-docs.sh`. The mission extends it to
  `bin/test-harness-yaml-corpus.py`; pm extended it further (D-05) to `bin/test-check-state.py`,
  `bin/run-unit-tests.sh` and the new `bin/test-team-catalog.py` — **the user KEPT that extension**
  (Q5). Not re-litigated.
- **The routing wall (measured at `635ef14`).** No agent domain grants write on
  `.claude/skills/harness/teams/**`, `.claude/skills/harness/SKILL.md` or
  `.claude/skills/harness-team/SKILL.md`. The only `.claude` write grant anywhere is
  `.claude/skills/harness/bin/**` (`team-config.yaml:155`, `:197`). So #8, #9, #24 and the
  `{{feat}}` quoting have **no eligible member** — they are main-session steps on *domain* grounds,
  which is a **different reason** from the carve-out. **`SKILL.md` is not one of CLAUDE.md's five
  enforcement files.** This is issue **#20** (routing wall) at recurrences 5 and 6; noted here,
  **not fixed here**.
- **#16 must reuse the existing placeholder vocabulary** at `validate-digest.py:472` —
  `("none", "null", "n/a")` — rather than inventing a second one. The mechanism is D-01.
- **`gate-probe.yaml` is DELETED, not quoted** (the user's Q3 answer). Verified a 1-file change:
  `check-docs.sh` carries no `gate-probe` reference and passes clean; the only references outside
  the file are `DECISIONS.md:2307-2325`, which record it historically. D-02 is **overridden**.
- **Making the runner machine-parse team files is out of scope.** They are read as prose by a lead
  today (`harness-team/SKILL.md:9`).
- **Out of scope:** #19 (no agent runs a PLAN task's `verify:` — filed, the user has been told, and
  this PLAN's own `verify:` lines are subject to it), #20, #21, #10, #7, #13, #14, #6, and the
  `bash-write-guard.sh` `FOO=bar python3 -` false positive.
- Budget **$160** (raised from $120 by the user on 2026-08-04, `notes/answers-replan-product.md`);
  **57–90 of 160** spent — 44.81 measured (18.90 plan-eng + 25.91 replan-product) plus a
  never-measured segment-1 band of 12–45. See `open_questions`.

## Success Criteria

- SC-01: A `feature.yaml` fixture carrying `review_sha: none` plus one `squad: validator` run makes
  `check-state.sh` report an INV-6 violation; the same fixture with a real 7-hex SHA reports none;
  and a **third** fixture with `review_sha: none` and **no validator run** also reports none — the
  precondition conjunct survives the rewrite. All three fixtures are asserted present, so a rewrite
  that never writes the red case cannot pass silently.
  verify: automated        evidence: unit
- SC-02: The placeholder vocabulary `("none", "null", "n/a")` appears as exactly **one** literal
  definition under `.claude/skills/harness/bin/`; both `check-state.sh` and `validate-digest.py`
  read it from that definition. Asserted by a registered unit test, not by a hand-run grep — a
  source reading is inspection, not automated evidence (P-03).
  verify: automated        evidence: unit
- SC-03: A reviewer confirms that `check-state.sh` run over the repo's real `.harness/` tree
  reports the **same violation set** after the fix as before it — no invariant other than INV-6
  changes, **and INV-6 itself fires on no existing feature**. Stated as the whole violation set on
  purpose: "unchanged except INV-6" would be satisfied while the fix turned a green gate red
  elsewhere. Evidence is a before-capture taken at `635ef14` **ahead of T-01** and diffed after,
  cited as a `file:line` finding. Precondition verified at `635ef14`: every `feature.yaml` except
  this one carries a real SHA (`FEAT-01` `a606d7a..9b07cfc`, `FEAT-02` `d9b16e5…`, `FEAT-03`
  `e68ba00`, `FEAT-04` `363b539`, `FEAT-05` `f0a3831`). `FEAT-06`'s is `none` and it **now carries
  two `runs:` entries** (`plan-product`, `plan-eng`) — **neither is `squad: validator`**, so INV-6's
  precondition is still unmet and nothing goes red. *(The earlier wording of this SC said the
  `runs:` list was empty; that was true when written and is false now. The conclusion is unchanged;
  the premise is corrected here rather than left standing.)* **`verify:` is `inspection`, not
  `automated`, because no runner can produce it**: `test-check-state.py` runs `check-state.sh`
  against `tempfile.TemporaryDirectory()` roots (`:160-167`) and cannot do a whole-repo before/after
  diff. See Verification gaps.
  verify: inspection
- SC-04: `.claude/skills/harness/teams/review.yaml` declares a step whose `id` is `qa` and whose
  `persona` is `qa`, and the parsed step id set equals `{code, qa, security, ui}`.
  **Contingent on D-08** (the three-descriptions reconciliation, **decided 2026-08-04 on the
  recommended branch**; alternative not taken): this wording assumes
  D-08's **recommended** branch — qa is a gate-only reviewer in the panel. If the user picks the
  alternative branch, this SC becomes `{code, security, ui}` and `SPEC.md:1980` is the thing that
  changes instead. Stated rather than left silent.
  verify: automated        evidence: unit
- SC-05: Every `*.yaml` under `.claude/skills/harness/teams/` loads under `harness_yaml.load_file`,
  and the directory's contents at completion are exactly **two** files — `review.yaml` (receiving
  the quoting fix) and `build.yaml` (born valid). **`gate-probe.yaml` is deleted (T-10), so the
  count is two, not three.**
  verify: automated        evidence: unit
- SC-06: The YAML-validity gate fails when a deliberately broken fixture is placed under a
  `teams/` directory — i.e. the widened glob is load-bearing and not vacuous.
  verify: automated        evidence: unit
- SC-07: `.claude/skills/harness/teams/build.yaml` exists, parses, declares `lead: eng-lead`, and
  its declared personas are a subset of the eng squad's members in `team-config.yaml` (DEC-118:
  a team is single-squad).
  verify: automated        evidence: unit
- SC-08: `build.yaml`'s declared persona set covers the personas that FEAT-03's eng-squad build
  runs actually used — `dev-ops` and `backend-dev`, read from `runs/2026-07-31-09-eng/state.yaml`
  and `runs/2026-07-31-10-eng/state.yaml`.
  verify: automated        evidence: unit
- SC-09: `.claude/skills/harness/SKILL.md` **names** the `build` team as the build-phase
  resolution path, in a line that also names DEC-118. This is a **presence** assertion on purpose:
  the mirror-image absence-grep ("SKILL.md no longer carries inline build step lists") **would
  already have passed before the change** — SKILL.md never carried such lists (P-01, D-04).
  verify: automated        evidence: unit
- SC-10: `docs/harness/SPEC.md` §13's team catalog contains a `build` row whose lead matches
  `build.yaml`'s, asserted by a registered unit test. (`check-docs.sh` exiting 0 is also required
  by T-08's verify, but it is not matched by `test_kinds.unit.detect` — `…/bin/test-*.py` — so it
  is not evidence the unit runner can produce.)
  verify: automated        evidence: unit
- SC-11: `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 across the full script list,
  including any test script this feature adds — the drift detector at `:9` sees no unregistered
  `test-*.py`.
  verify: automated        evidence: unit
- SC-12: A reviewer confirms that every task in PLAN.md that touched an enforcement script, a gate
  test, a team file or the playbook was executed **directly** (main session), not dispatched
  through a team run — the DEC-174 carve-out and the routing wall both held, and each task's stated
  reason matches which of the two applied.
  verify: inspection
- SC-13: The user reads the new `build.yaml` and the amended playbook passage and agrees they
  describe a build the way they want builds dispatched — the expansion rule (D-03) and the qa
  segment's placement (D-08) are judgements about how the org should work, and no test settles them.
  verify: uat
- **SC-14: `.claude/skills/harness/SKILL.md` names the blocking qa gate.** `grep -c -i 'test_matrix'`
  on that file returns **≥ 1**, and the same passage names `qa`, `validator` and `loop_back` — so
  the file states that the gate is a validator-squad segment the orchestrator sequences with a
  `loop_back` on failure. **"The same passage" means a window of 8 consecutive lines**, the budget
  T-11 has for the passage it adds; the three tokens must co-occur inside one such window anywhere
  in the file. It is deliberately **not** "the same physical line": that would test where markdown
  happens to wrap rather than what the playbook says, and the passage the PLAN prescribes renders
  as six lines with no single line carrying all three. **This SC is RED unless `SKILL.md` is
  edited** — it is the one criterion `review.yaml` alone cannot satisfy, and it is what makes the
  #24 re-scope falsifiable. Measured at `635ef14`: `test_matrix` occurs **0** times, and `qa` and
  `loop_back` each occur **0** times, so both halves are red today.
  verify: automated        evidence: unit
- **SC-15: the three-descriptions problem is closed by construction.** A registered unit test
  asserts that the panel step set stated in `SPEC.md`'s ship-feature row, the panel step set stated
  in `SPEC.md`'s review row, and the parsed step id set of the shipped `review.yaml` are **the same
  set**. Today they are three different sets; after this feature a future edit to any one of them
  turns the gate red.
  verify: automated        evidence: unit

## Verification gaps

Read from `.harness/harness.json` `test_kinds`: **`unit` is the only kind with a runner**
(`cmd: .claude/skills/harness/bin/run-unit-tests.sh`). `functional`, `integration`, `component`,
`ui`, `eval` and `typecheck` all carry `cmd: null`. No SC above rests on a null kind.

- **The whole-repo state-check diff has no runner.** SC-03 is `inspection` for that reason, not by
  preference: `test-check-state.py` only runs `check-state.sh` against throwaway temp roots
  (`:160-167`) and `run-unit-tests.sh` runs only the scripts listed at `:6`. **What is therefore
  NOT proven by a test: that the INV-6 rewrite leaves every other invariant's verdict unchanged on
  the real tree.** It is carried by a human-read before/after diff captured ahead of T-01.
- **Markdown behaviour has no runner.** SC-09, SC-10, SC-14 and SC-15 assert that `SKILL.md` and
  `SPEC.md` contain certain text. That is all a test can prove. **What is NOT proven: that an
  orchestrator reading the edited playbook actually sequences the qa segment, or resolves and
  dispatches the `build` team.** No automated kind can prove it. It is carried by SC-13 (uat) and
  by the first real ship run after this lands.
- **`build.yaml` is never executed by this feature**, and **no ship run exercises the new qa
  segment**. `build.yaml`'s correctness as a team rests on FEAT-03's recorded runs (SC-08) — n = 2
  eng runs on 1 feature. Nothing here runs a build or a ship through either.
- **`verify:` lines in PLAN.md are not executed by any agent** (issue #19, filed, out of scope).
  Every `verify:` in this feature's PLAN is a command a human or the main session must run.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-04

Signed by the user through the main session, together with PLAN.md, at
`notes/answers-arch-review-eng.md`'s terminus. The 15 success criteria are approved as written,
including SC-14's reshaped predicate — `grep -c -i 'test_matrix' >= 1` unchanged as the user
hand-verified it, and the co-occurrence half as an 8-consecutive-line sliding window, measured RED
at `635ef14` and GREEN against T-11's prescribed passage by pm and independently by the delta
reviewer.

Approved after a FULL pre-signature architecture review (the user's explicit override of a scoped
delta), which returned 6 blocking findings, plus a delta re-review that caught a 7th (DMF-1). Cost
of the plan phase: $170.17 measured against a $160 ceiling. **Build re-authorised at $100** — a new
allowance for the build and validate phases, not a raise of the $160 the plan phase consumed.
