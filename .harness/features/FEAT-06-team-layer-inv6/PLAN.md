# PLAN — FEAT-06 team layer and INV-6

**Rewritten 2026-08-04** against the user's answers (`notes/answers-plan-eng.md`) and eng-lead's six
`must_fix` (`runs/plan-eng/digest.md`). Per-item dispositions:
`notes/research-replan-dispositions.md`. **Approval is reset to pending** — the task set changed.

## Execution shape — the routing reason is PER TASK, and there are two different reasons

This feature has **one** member-executable task (T-08). Every other task is `main-session-direct`,
for one of two **distinct** causes, and each task states which. Confusing them corrupts issue #20's
evidence base.

| Reason | Meaning | Tasks |
|---|---|---|
| `carve-out` | DEC-174 — the harness never *executes* changes to its own enforcement/gate layer. Domain **is** granted here (`bin/**` → dev-ops, backend-dev), so the carve-out is the binding reason. Extended by D-05, which the user KEPT (Q5) | T-01, T-05, T-07 |
| `domain-ungranted` | **The routing wall, issue #20.** No agent domain grants write on `.claude/skills/harness/teams/**`, `.claude/skills/harness/SKILL.md` or `.claude/skills/harness-team/SKILL.md` (measured at `635ef14`; `team-config.yaml`'s only `.claude` grants are `.claude/skills/harness/bin/**` at `:155` and `:197`). **These are NOT enforcement files** — `SKILL.md` is not one of CLAUDE.md's five — they are simply unroutable | T-02, T-04, T-06, T-09, T-10, T-11 |
| `squad-dispatched` | `docs/**` is granted to `harness-documentor` (`team-config.yaml:116`) | T-08 |

Assigning a `domain-ungranted` task to a member would be recurrence #7 of the routing wall. Do not.

## Execution order — topological, verified against every declared `depends_on` (EMF-1)

**T-01 → T-02 → T-04 → T-10 → T-05 → T-06 → T-09 → T-11 → T-08 → T-07.**

Apply it verbatim; PLAN file order is **not** a topological order and must not be used as one.
Checked: T-05 after {T-02, T-04, T-10}; T-06 after T-04; T-09 after T-04; T-11 after T-06; T-08
after {T-04, T-06, T-10, T-11}; T-07 after {T-02, T-04, T-06, T-08, T-11}. **The build interleaves
main-session and member execution** — T-07 (main-session) depends on T-08 (documentor-dispatched),
so direct tasks cannot all be run before the one dispatch.

## Decisions

- **D-01: the placeholder vocabulary gets one home — a module-level constant in
  `bin/harness_yaml.py` — and both consumers import it.**
  Rationale: the user's constraint is "reuse the existing vocabulary, do not invent a second one",
  and the two consumers sit on opposite sides of a bash/python boundary. `check-state.sh` already
  runs `PYTHONPATH="$_selfdir…" python3 - <<'PY'` at `:24` and `import harness_yaml` at `:27`, so
  the import mechanism FEAT-05 established is already wired. `validate-digest.py` is import-safe
  (`if __name__ == "__main__":` at `:728`) and sits in the same directory; `settings.json:56`
  invokes it by absolute path, so `sys.path[0]` is `bin/` and a bare `import harness_yaml`
  resolves (confirmed by eng-lead). `harness_yaml.py` guards its own PyYAML import (`:17-20`), so
  this adds **no new hard PyYAML dependency**.
  Rejected — **importing from `validate-digest.py` itself**: the filename is hyphenated, so the
  only route is `importlib.util.spec_from_file_location` — a fragile dependency from a gate script
  onto a hook script's path.
  Rejected — **duplicating the tuple with a comment**: literally the second vocabulary the user
  forbade, and this feature's own through-line is definitions that drift out of agreement.
  Tradeoff accepted: a cohesion cost (`harness_yaml.py` is nominally a YAML module), taken to avoid
  a new module. Named `PLACEHOLDER_UNSET` so the mismatch is legible.

- **D-02: ~~`gate-probe.yaml` is fixed in place, not deleted.~~ OVERRIDDEN BY THE USER (Q3).**
  The user ruled `gate-probe.yaml` is **DELETED**. Verified a 1-file change: `check-docs.sh`
  contains no `gate-probe` reference and passes clean, and the only references outside the file are
  `DECISIONS.md:2307-2325`, which record it as the historical proof of loop-back semantics —
  deleting orphans no live consumer and the decision record keeps the story. **Consequences
  carried:** T-03 is **dropped from this PLAN** and replaced by **T-10** (the deletion); T-05's
  widened gate covers **two** files, not three; **SC-05 is the SC whose count was wrong and it is
  reworded to two** — an SC asserting a count that cannot be met is exactly the defect this feature
  exists to remove; T-08 adds a one-line amendment to DECISIONS.md so the record does not describe
  a file that no longer exists.

- **D-03: `build.yaml` is eng-squad-scoped and declares an expansion rule over PLAN tasks, not a
  literal step list.** *(User Q8: KEPT as an expansion rule. EMF-1, EMF-2 and EMF-3 are therefore
  live defects inside a form that definitely exists, and are fixed below.)*
  Rationale, two halves. **(a) Single-squad, by DEC-118** — which is exactly why `plan-feature` and
  `ship-feature` are orchestrator playbooks and not teams. FEAT-03's build spanned eng (`…-09-eng`
  dev-ops, `…-10-eng` backend-dev) **and** product (`…-11-product` documentor). A legal `build`
  team reaches the eng half only. **This is a correct bound, not a shortfall** — the qa gate and
  the documentation step were never a build team's to contain. **(b) Variable step set** —
  `review.yaml` has three fixed steps; a build has as many steps as the PLAN has eng tasks.
  Amended by the eng review, all three touching `steps_from:`:
  - **`prompt: from_task_intent` is added (EMF-3).** Without it the file retires the hand-composed
    step LIST while keeping the hand-composed step PROMPT — #9's defect moved down one level, not
    closed. The PLAN task's `intent:` block already *is* the fully specified dispatch text.
  - **`depends_on: from_task_depends_on` replaces `from_plan_order` (EMF-1).** PLAN order is
    demonstrably not a topological order — on this very PLAN. The token reads each task's own
    `depends_on:` and falls back to file order only where a task declares none.
  - **The task-selection key is REMOVED from `steps_from:` — EMF-2, completed.** The finding was
    that its value, `squad == eng`, named a `squad:` field PLAN tasks do not carry: a predicate over
    a field that does not exist, so nothing could ever evaluate it. Renaming it to an honest token
    was one way to close that; deleting it is the one taken. A key no runtime evaluates, whose only
    content is a decision made elsewhere, is a comment wearing a key — so the selection is recorded
    where it belongs, in a comment (`build.yaml:46-50`), and the key is gone. **This CLOSES the
    finding, it does not reverse it:** the finding was that the predicate was not evaluable; the
    resolution is that it is not needed. *(Amended 2026-08-04; this bullet previously prescribed
    renaming the selection key rather than removing it.)*
    The coordination obligation survives the deletion, re-anchored on the distinction that outlives
    the key — **two different decisions, each owned by a different tier**: **WHICH tasks** go to
    `eng-lead` is the **orchestrator's**, decided before dispatch and handed over as a list; **WHICH
    specialist** owns each of those tasks is the **lead's**, a real decision it makes by
    `consult-when`. The lead routes; it does not revisit the selection. T-06 and T-09 are worded to
    agree on that split.
  Tradeoff accepted, load-bearing: **`build.yaml` is a different KIND of object from `review.yaml`**
  — a rule to expand rather than a DAG to walk. Any future runner must handle both forms. Recorded
  so a future scan does not re-suggest "just write literal steps" without knowing the task set is
  variable.
  **Consequence that must not stay silent:** `harness-team/SKILL.md` step 2 says "one `steps:` entry
  per team step" and step 3a computes the ready set from `depends_on`. A lead handed a file with
  `steps_from:` and no `steps:` is running an algorithm with no branch for it — this feature's own
  through-line. **T-09 closes that. Without T-09, `build.yaml` is prose only.**

- **D-04: SC-09 asserts presence, not absence.**
  Rationale: the natural verify for "retire the hand-written step lists" — a grep asserting
  `SKILL.md` no longer carries inline build step lists — **would have passed before the change**.
  SKILL.md never carried such lists; the hand-written lists are what the **lead composed at
  dispatch**, visible as `team: none` in FEAT-03's build `state.yaml` files. The discriminating
  assertion is that SKILL.md now **names** the `build` team as the build-phase resolution path.
  Confirmed still discriminating at `635ef14`: no line in `harness/SKILL.md` matches both `build`
  and `DEC-118` (`build` at `:155`, `:205`, `:211`; `DEC-118` at `:38`).
  Tradeoff accepted: "retired" is proven only for the eng half and only as text. Stated in the
  BRIEF's Verification gaps rather than papered over.

- **D-05: the DEC-174 carve-out is extended to `bin/test-check-state.py`, `bin/run-unit-tests.sh`
  and the new `bin/test-team-catalog.py`. THE USER KEPT THIS (Q5) — not re-litigated.**
  Rationale accepted by the user: a test *for* `check-state.sh` is part of what makes that gate
  green, and the carve-out exists because green gates cannot vouch for the code that produces them
  — verbatim the 2026-08-03 failure. Cost accepted: more of the build sits in main-session context
  with no lead assessing it.

- **D-06: TDD order on T-01, with a verbatim red-first receipt.** The regression test for #16 is
  written **red first** into `bin/test-check-state.py`, beside its existing INV-6 case at `:152-172`
  (the *absent*-key case).
  Rationale: this is a fail-open — a fix that silently does nothing looks identical to a fix that
  works. Only a test that fails before the change can tell them apart.
  **Amended per EMF-5:** the red-first receipt must be recorded as the **verbatim failing output
  plus the exact invocation**, pasted into `notes/`, not asserted in prose. Prose that a test failed
  is unfalsifiable, which is the defect class this feature is about.

- **D-07: `harness-team/SKILL.md` is amended rather than `build.yaml` being forced into the literal
  `steps:` shape.**
  Rationale: forcing literal steps means the file is rewritten for every feature — a step list
  composed at dispatch wearing a filename, the exact thing #9 asks to retire (the user's Q8
  reasoning, verbatim). Amending the runner skill costs ~12 lines in a file preloaded by every lead.
  Tradeoff accepted: a second execution shape in the team runner, and a third unrouted `.claude`
  path, so T-09 is `main-session-direct` too.

- **D-08 (DECIDED 2026-08-04): reconcile the three descriptions of where the qa gate runs by naming
  TWO jobs, not one.**
  **Signed by the user on 2026-08-04 on pm's RECOMMENDED branch — "two jobs, one persona"
  (`notes/answers-replan-product.md`). The flip-delta below is therefore NOT applied: T-02, SC-04,
  T-07(1) and T-08 stand exactly as written. The cost was accepted explicitly: qa is spawned twice
  in a full ship. The alternative branch and its delta are retained below as the record of what was
  weighed and rejected, not as work to do.**

  The four sources, laid side by side:

  | Source | Says |
  |---|---|
  | `SPEC.md:1978` ship-feature DAG | `… → qa → {code ∥ security ∥ ui} → …`, "the orchestrator sequences the squad segments… qa gates (writes + runs tests, `test_matrix` hard gate) → `loop_back` → dev" |
  | `SPEC.md:1980` review DAG | `{code ∥ qa ∥ security ∥ ui} → validator-lead assesses` |
  | shipped `review.yaml` (`:22`, `:36`, `:49`) | `code`, `security`, `ui` — **no qa** |
  | FEAT-03 run `2026-07-31-12-validator` `state.yaml` | `team: review` with `id: qa`, `persona: harness-qa`, `dispatched_at: seq-1` — a lead put qa **in the panel**, at run time |

  **Recommended branch — "two jobs, one persona."** The contradiction is a vocabulary collapse:
  `qa` names two different jobs and no document distinguishes them.
  - The **qa segment** (`SPEC.md:1978`): validator-squad, orchestrator-sequenced, runs after the
    build team returns. It **writes** missing tests, runs the `test_matrix` hard gate, `mutates_repo`,
    and `loop_back`s to the dev that owns the task. This is the job **#24** says `SKILL.md` never
    mentions.
  - The **qa panel step** (`SPEC.md:1980`, `#8`): the same persona in **gate-only** mode — it
    re-runs the matrix over the pinned `review_sha`, writes one note, authors nothing,
    `mutates_repo: false`, dispatches in the same turn as the other three reviewers. This is what
    FEAT-03's lead actually ran, and it is what this feature's own cycle-1 send-back already
    adjudicated against three sources.
  Under this branch **every source is right except the shipped `review.yaml`** (which is #8) and
  `SPEC.md:1978`'s panel cell, which must widen from `{code ∥ security ∥ ui}` to
  `{code ∥ qa ∥ security ∥ ui}` so the two SPEC rows agree (T-08).

  **The alternative branch — "one job, segment only."** qa is *only* the orchestrator-sequenced
  segment; `review.yaml` correctly has three steps; `SPEC.md:1980`'s review row is the error and is
  narrowed to `{code ∥ security ∥ ui}`.
  Honest case for it: `harness-qa` holds `Write` and its own agent file says "You are a doer, not a
  reviewer" — a `mutates_repo` doer in a parallel read-only panel is odd; and `review.yaml`'s header
  calls the panel "the independence layer over qa", which reads as qa having already run.

  **Why the recommendation goes the other way — the check that settled it.** Standalone review is a
  real dispatch path: `SPEC.md:1980` names it explicitly ("standalone, the orchestrator delegates a
  fix") and `harness/SKILL.md:66` lets the orchestrator "insert a review" as an execution-time
  adjustment. **On that path nothing else runs the matrix.** The alternative branch would close
  #24's hole in ship-feature while opening the identical hole in standalone review — in the feature
  whose charter is "a definition or check that appears to exist but does nothing." The `Write`-tool
  objection is answered by the two-jobs split: the panel step does not author.

  **Flip-delta if the user picks the alternative — stated so the change is one edit pass, not a
  re-plan:** T-02 loses the qa step and becomes quoting-only; **SC-04** becomes
  `{code, security, ui}`; T-07's assertion (1) changes to match; T-08 narrows `SPEC.md:1980`
  instead of widening `:1978`; **SC-15 and SC-14 are unaffected**, and #24's fix (T-11) is
  unaffected — which is the point: the reconciliation moves #8, never #24.
  Tradeoff accepted under the recommended branch: qa is spawned twice in a full ship (once
  authoring, once gate-only over the pinned SHA). That is a real cost in spawns, bought for the
  independence property the panel exists to provide and for standalone-review coverage.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-04

Signed by the user through the main session, together with BRIEF.md. All 10 tasks and all 8
decisions are approved as written, D-08 included (qa in BOTH places — the orchestrator-sequenced
build segment that writes and runs tests, and the gate-only panel step that re-runs the matrix over
the pinned `review_sha`; the double qa spawn was accepted explicitly).

**Build re-authorised at $100.** This is a new allowance for the build and validate phases, NOT a
raise of the $160 the plan phase consumed at $170.17 measured. Report actual-vs-$100 at every gate.

**Known residual, accepted with the signature, not fixed:** MF-1 — T-02's `verify:` asserts the
step-id set, qa's persona, `mutates_repo` and `outputs`, but NOT the count-bearing comment sweep
that DMF-1 added. That sweep is prose-enforced at execution and asserted by nothing. The
orchestrator declined to buy a third pm run for it and said so; the user signed with it open. If
T-02's execution is the moment it can be closed cheaply, close it there.

---

## Re-signature — 2026-08-04, after the post-signature amendment

status: approved
approved-by: Mike Ruangutai
date: 2026-08-04

**"All 10 tasks approved as written" no longer holds for T-04, T-06 and D-03**, which were amended
after the signature above on the user's ruling at the ship gate. Re-approved as amended.

- **`personas:` and `filter: eng_squad_tasks` are both DELETED from `build.yaml`.** Neither was read
  by any runtime: `personas` was a copy of a roster `team-config.yaml` owns, and `filter` was
  explicitly a token no lead evaluates. Their only mechanical consumer was T-04's own `verify:`.
- **T-04's `verify:` was RED on two keys in succession** — `KeyError: 'personas'`, then
  `KeyError: 'filter'`. A signed check that crashes is the defect class this feature exists to
  close, sitting inside this feature's own plan. It now **asserts their ABSENCE**
  (`'personas' not in d and 'filter' not in sf`), so re-introduction reddens it. Executed at
  re-signature: **exit 0**.
- **EMF-2 is recorded as COMPLETED, not reversed.** The architecture review's finding was that
  `filter: squad == eng` named a field PLAN tasks do not carry — the predicate was fake. The first
  remedy made it an honest token; the user's ruling is that an honest token nobody evaluates is
  still dead weight. Same finding, cleaner resolution.
- **The lead's routing role is now stated as a real decision it owns.** The prior wording ("the lead
  does not re-evaluate it") could be read as the lead doing no routing at all. WHICH tasks reach
  `eng-lead` is the orchestrator's decision; WHICH specialist gets each one is the lead's, by
  `consult-when`. Corrected in `harness/SKILL.md` and `harness-team/SKILL.md`.

**Two things accepted WITHOUT change, so they are not re-litigated later:** the `build`-team
dispatch has no mechanical way to select eng-squad task ids — that is issue **#20**, the routing
wall, and not this feature's business; and `build.yaml` has never been dispatched, including by this
feature, whose eng-squad task list was empty. Both were put to the user explicitly and accepted.

**Site lists were short three times on this feature** — two `personas` sites handed over against
five actually present, four `filter` sites against six, and an earlier comment sweep that named four
sites against five. The layer a site list forgets is the verification criterion itself. Recorded
here because it is a pattern, not an incident.

**Cost at re-signature: $252.63 measured against the $100 build-and-validate allowance — 2.5x.**
The orchestrator's own session is 55% of it. Reported, not hidden (DEC-134).

## Features

- FEAT-06: team layer and INV-6
  traces: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08
  tasks: T-01, T-02, T-04, T-05, T-06, T-07, T-08, T-09, T-10, T-11
  note: >
    T-03 (quote `gate-probe.yaml`) is DROPPED — the user ruled the file deleted (Q3). T-10 is the
    deletion. The id T-03 is retired, not reused. Execute in the topological order stated above,
    not in file order.

## Tasks

- T-01: Close INV-6's truthy hole and give the placeholder vocabulary one home
  execution_mode: main-session-direct — reason: carve-out (`check-state.sh` and
    `validate-digest.py` are both named in CLAUDE.md; `test-check-state.py` and `harness_yaml.py`
    by D-05, which the user kept)
  depends_on: none
  files:
    - .claude/skills/harness/bin/test-check-state.py
    - .claude/skills/harness/bin/harness_yaml.py
    - .claude/skills/harness/bin/check-state.sh
    - .claude/skills/harness/bin/validate-digest.py
    - .harness/features/FEAT-06-team-layer-inv6/notes/before-check-state-635ef14.txt
  intent: >
    Step 0 (PRECONDITION for SC-03, and it must happen FIRST — an after-only run cannot assert
    sameness). Run `.claude/skills/harness/bin/check-state.sh` over the real repo tree at the
    current HEAD and capture its complete stdout+stderr verbatim to
    `.harness/features/FEAT-06-team-layer-inv6/notes/before-check-state-635ef14.txt`, with the exact
    invocation and the `git rev-parse HEAD` output as the first two lines of the file. After Step 3,
    re-run the same invocation and `diff` against this capture; the only permitted difference is an
    INV-6 line, and at `635ef14` there should be none at all (no `feature.yaml` meets INV-6's
    precondition — see BRIEF SC-03).
    Step 1 (red first, D-06). In `test-check-state.py`, beside the existing INV-6 case at `:152-172`
    (which covers an ABSENT `review_sha`), add THREE fixtures:
    (a) `review_sha: none` + one `runs:` entry with `squad: validator` → output MUST contain
    `review_sha is not pinned`;
    (b) `review_sha: 1ce886a` + the same validator run → NO INV-6 line (the value axis);
    (c) `review_sha: none` + a `runs:` entry that is NOT `squad: validator` → NO INV-6 line (the
    PRECONDITION axis — this is the guard against an over-scoped rewrite that drops the
    `any(sq == "validator")` conjunct, and it is live: this feature's own `feature.yaml` is exactly
    that shape). Run the file and confirm (a) FAILS and (b), (c) pass.
    Record the red-first receipt as the VERBATIM failing output plus the exact invocation, appended
    to `notes/before-check-state-635ef14.txt` under a `## red-first receipt` heading. Prose that it
    failed is not a receipt (D-06, EMF-5).
    Step 2. In `harness_yaml.py`, add a module-level constant
    `PLACEHOLDER_UNSET = ("none", "null", "n/a")` with a one-line comment naming it as the single
    definition of "this field is declining to answer" (DEC-121). Place it near the other
    module-level constants (e.g. beside `INSTALL_COMMAND` at `:293`).
    Step 3. In `check-state.sh`, replace the INV-6 condition at `:156`. It currently reads
    `if any(sq == "validator" for _, sq, _ in runs) and not val("review_sha"):`. It must become
    equivalent to: compute `_sha = (val("review_sha") or "").strip().lower()`, then fire when a
    validator run exists AND (`_sha == ""` OR `_sha in harness_yaml.PLACEHOLDER_UNSET`). **Keep the
    `any(sq == "validator" …)` conjunct** — fixture (c) exists to catch its removal. The heredoc
    already imports `harness_yaml` (`:27`) under `PYTHONPATH` set at `:24`, so no new plumbing. Do
    NOT change the violation message text — `test-check-state.py` matches on it. Do NOT touch the
    `cycles_used` consumer; it is already guarded by `.isdigit()`.
    Step 4. In `validate-digest.py`, add `import harness_yaml` and replace the inline literal at
    `:472` — `val.lower() in ("none", "null", "n/a")` — with
    `val.lower() in harness_yaml.PLACEHOLDER_UNSET`. Behaviour must be byte-identical; this is a
    de-duplication, not a semantic change. Leave `NULLABLE` (`:46`) and the DEC-173 gate branch
    untouched.
  change_type: bugfix
  verify: >
    `.claude/skills/harness/bin/run-unit-tests.sh` exits 0, AND
    `grep -rn '"none", "null", "n/a"' .claude/skills/harness/bin/ | wc -l` returns exactly `1`
    (the definition in `harness_yaml.py`) — and it must STILL return `1` after T-07 lands a new file
    in that same directory, which is true **only because** T-07 check (6) constructs its search
    needle from `harness_yaml.PLACEHOLDER_UNSET` instead of embedding the literal (AMF-6). The two
    sites are coupled: embed the literal in `test-team-catalog.py` and this conjunct silently goes
    from true to false after it was signed off — a verify that passes and then goes stale, this
    feature's own charter defect. AND
    `grep -c 'PLACEHOLDER_UNSET' .claude/skills/harness/bin/check-state.sh
    .claude/skills/harness/bin/validate-digest.py` returns 1 for each, AND — the assertion that
    makes the deliverable itself non-optional (EMF-5) —
    `grep -c 'review_sha: none' .claude/skills/harness/bin/test-check-state.py` returns `>= 2` and
    `grep -c 'review_sha: 1ce886a' .claude/skills/harness/bin/test-check-state.py` returns `>= 1`.
    Without those two greps the runner exits 0 whether or not the red case was ever written.
  traces: REQ-01, REQ-05, D-01, D-06
  feature: FEAT-06
  status: pending

- T-02: Add the gate-only qa step to the shipped `review` team and quote its templates
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
    (`.claude/skills/harness/teams/**` has no write grant in `team-config.yaml`; it is NOT an
    enforcement file)
  depends_on: none
  intent_is_contingent_on: D-08 (recommended branch). If the user picks the alternative branch,
    this task drops its qa step and becomes quoting-only — see D-08's flip-delta.
  files:
    - .claude/skills/harness/teams/review.yaml
  intent: >
    Add a fourth step with `id: qa`, `persona: qa`, `depends_on: []`, `inputs: []`,
    `outputs: [".harness/features/{{feat}}/notes/review-harness-qa-c{{cycle}}.md"]`,
    `mutates_repo: false`, and a
    prompt instructing qa to run the `test_matrix` gate over the diff at `{{review_sha}}` and
    return `matrix_ok` plus the per-kind results. Place it so the parsed step-id set is
    `{code, qa, security, ui}`.
    The prompt and an adjacent comment must state, in D-08's vocabulary, that this step is qa in
    **gate-only mode**: it re-runs the existing matrix over the pinned SHA and authors NOTHING —
    test authoring belongs to the orchestrator-sequenced qa segment that runs before the panel
    (`SPEC.md:1978`, T-11). That is why it is `mutates_repo: false` and dispatches in the SAME turn
    as the other three, consistent with the header at `review.yaml:8-10` ("serial dispatch looks
    correct while running 3× slower") and with `2026-07-31-12-validator/state.yaml`, where `code`
    (`:26`), `security` (`:35`) and `qa` (`:43`) all carry `dispatched_at: seq-1`.
    **The two jobs must be distinguishable on disk, not only in prose (AMF-2).** The
    orchestrator-sequenced qa SEGMENT keeps the historical name `notes/qa-c{{cycle}}.md` — that is
    what is on disk today (`FEAT-05/notes/qa-c0.md`, `qa-c1.md`) — and this PANEL step takes the
    reviewer-style name `notes/review-harness-qa-c{{cycle}}.md`, matching the other three steps
    (`:26`, `:40`, `:53`) and the grant `team-config.yaml:227` already carries for exactly this
    spelling (`# Q6`). Without the rename, at cycle N of a full ship the panel's gate-only note
    overwrites the segment's test-authoring receipt — same persona, same domain, same filename — and
    the two jobs D-08 separated collide on one file. State this in the adjacent comment.
    **Also correct `review.yaml`'s own comments, which after this task contradict its step count
    (AMF-3, DMF-1)** — in the feature whose REQ-08 is that shipped accounts agree. Sweep the whole
    file, first line to last, and bring every comment into agreement with the four-step file. The
    sweep's predicate — its only object — is comment text stating how many steps or reviewers the
    panel dispatches, or any number derived from that count, including phrases this task quotes
    elsewhere as citations of the file's current state. Numbers inside prompt bodies that describe a
    reviewer's own method (its review stages, an audit standard's name) do not derive from the
    dispatch count and are out of scope. Either action closes a site and both satisfy REQ-08 —
    correct the number, or reword so the sentence no longer states one — so pick whichever leaves
    the surrounding reasoning intact. Matching sites are not location-bounded and a count is not
    always a cardinal: the footer's "merge the three panels into ONE actionable set" matches, and so
    does the "3× slower" tail of the dispatch sentence, which is the panel count as a multiplier.
    Before finishing, re-grep the file case-insensitively for `three`, `3`, `four` and `4` and
    confirm no surviving hit disagrees with the four-step file. Change only the matching phrases —
    the surrounding reasoning is unaffected and stays verbatim.
    Separately, quote the `outputs:` entries of ALL steps so the file loads under a real parser:
    each `[.harness/…/{{feat}}/…]` becomes `[".harness/…/{{feat}}/…"]`. The value must be
    byte-identical once parsed; only the parser's reading changes. The current failure is at
    `review.yaml:26:14`, "while parsing a flow sequence" — verified at `635ef14`.
    Do not change `name`, `purpose`, `lead`, `inputs`, `max_cost_usd`, or any existing prompt text.
    **That protect list does NOT extend to comments** — a comment is unprotected wherever it carries
    the panel-count statement the sweep above defines, and must be brought into agreement. Every
    other comment stays verbatim.
  change_type: config
  verify: >
    `python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin'); import harness_yaml;
    d=harness_yaml.load_file('.claude/skills/harness/teams/review.yaml');
    ids={s['id'] for s in d['steps']};
    sys.exit(0 if ids=={'code','qa','security','ui'} and any(s['id']=='qa' and s['persona']=='qa'
    and s['mutates_repo'] is False
    and s['outputs']==['.harness/features/{{feat}}/notes/review-harness-qa-c{{cycle}}.md']
    for s in d['steps']) else 1)"` exits 0. (The templates are compared UN-rendered — the parsed
    file still carries the literal `{{feat}}`/`{{cycle}}` text.)
    **`harness_yaml.load_file`, not `yaml.safe_load`** (eng advisory 2): `load_file` also rejects
    duplicate keys, and a verify more permissive than the gate it feeds is not a gate. The
    `mutates_repo is False` conjunct closes MF-1 — the field the cycle-1 send-back corrected was
    previously invisible to its own gate. **The `outputs` conjunct is there for the same reason**
    (AMF-2): the panel/segment filename split is the one fix in this task whose failure is silent —
    a wrong receipt path in `build.yaml` is BLOCKED by `check-domain.sh` at exit 2, but writing the
    old `qa-c{{cycle}}.md` here would pass every other check in this PLAN and surface only as an
    overwritten qa note at cycle N of a real ship.
  traces: REQ-02, REQ-04, REQ-08, D-08
  feature: FEAT-06
  status: pending

- T-04: Write `build.yaml` — the eng-squad build team, born valid
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
  depends_on: none
  files:
    - .claude/skills/harness/teams/build.yaml
  intent: >
    Create the file. It must load under `harness_yaml.load_file` on first write (every templated
    path quoted — it is born valid, it receives no quoting fix). Contents:
    `name: build`; `lead: eng-lead`; `inputs: [feat, tasks]`; `max_cost_usd: 60`.
    `purpose:` — use THIS wording, and T-11 must use the same vocabulary for the same object
    (EMF-4; the two are one fix seen from two sides):
    "Run the approved PLAN's eng-squad tasks in dependency order, one step per T-NN. **The
    `test_matrix` qa gate is NOT a step this team contains** — it runs as an orchestrator-sequenced
    **validator-squad segment** after this team returns, because a team is single-squad (DEC-118)."
    This is a statement of correct bounds, not an apology: qa was never a build team's to contain.
    Instead of a literal `steps:` list, declare an expansion rule (D-03) under a `steps_from:` key
    with these fields:
    `source: plan_tasks` (the host reads `## Tasks` from `.harness/features/{{feat}}/PLAN.md`);
    **no task-selection key at all** (EMF-2): a key no runtime evaluates, recording a decision made
    before dispatch, is a comment wearing a key — so write it as a comment and not as config.
    *(Amended 2026-08-04; this instruction previously prescribed a selection key holding a token
    rather than a predicate.)* Above `persona:`, carry a comment stating the two decisions and their two
    owners: **WHICH tasks** arrive here is the ORCHESTRATOR's decision, made before dispatch and
    handed over as a list; **WHICH specialist** gets each of them is the LEAD's decision, and a
    real one. Same comment states that a non-eng task is not dropped here — it was never in the
    set, and it stays for the orchestrator to sequence as its own squad segment (DEC-118);
    `persona: by_consult_when` — the lead routes each T-NN to a member by that member's
    `consult-when`, which is what `…-09-eng` and `…-10-eng` actually did; it routes, it does not
    revisit the orchestrator's selection;
    `prompt: from_task_intent` — **required** (EMF-3): the PLAN task's `intent:` block IS the
    dispatch text. Without this the file retires the hand-composed step LIST while keeping the
    hand-composed step PROMPT, which is #9's defect moved down one level rather than closed;
    `id: "{{task_id}}"`;
    `outputs: [".harness/features/{{feat}}/notes/receipt-harness-{{persona}}-{{task_id}}-c{{cycle}}.md"]`
    — with a comment stating BOTH reasons this exact shape is required, because each is independently
    fatal (AMF-1): (i) the `harness-` prefix is what makes the rendered path match a receipt grant —
    all five grants in `team-config.yaml` (`:144`, `:158`, `:171`, `:184`, `:199`) require
    `receipt-harness-`, and `check-domain.sh:242-248` **BLOCKS** an unmatched path at exit 2 rather
    than warning. So the `harness-` prefix must be a LITERAL in the template while `{{persona}}`
    substitutes the SHORT resolved name (`dev-ops`) that `persona: by_consult_when` yields — short
    resolution, full rendered path. This is exactly the mixed convention `review.yaml` already uses
    (`persona: code-reviewer` at `review.yaml:23`, `outputs:
    review-harness-code-reviewer-c{{cycle}}.md` at `:26`); (ii) `c{{cycle}}` is what preserves the
    loop-back record — this step carries `on_fail: loop_back`, and `harness-team/SKILL.md` step 3.5
    (DEC-117) requires cycle-namespaced outputs on anything that re-runs, because a PASS on cycle 2
    otherwise overwrites the FAIL report that justified the cycle;
    `mutates_repo: true` with a comment that this forces one-at-a-time dispatch even where the DAG
    would allow parallelism (`harness-team/SKILL.md` step (c), DEC-85);
    `depends_on: from_task_depends_on` — **not `from_plan_order`** (EMF-1): read each task's own
    `depends_on:` field, falling back to PLAN file order ONLY for a task that declares none. PLAN
    file order is demonstrably not a topological order — on this very PLAN;
    `on_fail: loop_back` with a one-line comment that this restates eng-lead's existing build
    fix-loop rule rather than inventing a new one (eng advisory 1 — `review.yaml`'s steps carry no
    `on_fail:` and are legal, but build is where it matters and a future runner will look here).
    **Do NOT add a `personas:` key.** *(Amended 2026-08-04; this instruction previously read "Add
    `personas: [frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops]` — the Engineering
    squad's full roster as read from `team-config.yaml`".)* The roster lives in
    `.harness/team-config.yaml` and nothing here reads a copy of it: the expansion routes each task
    by `consult-when` at dispatch, so a second copy is data no runtime consults, going stale the day
    a member is added. `bin/test-team-catalog.py` asserts the DEC-118 bound and the recorded floor
    against `team-config.yaml` directly, which is the only file that can be right about them.
    Add a header comment block stating, in prose a lead reads: (a) this team is **eng-squad only**
    by DEC-118 and cannot reach documentor, pm, reviewer or qa steps — a correct bound; (b) it is
    an expansion rule, not a DAG, and why; (c) that this file **deliberately does not list its
    personas** and why — the roster lives in `team-config.yaml`, a second copy is data no runtime
    consults — while stating that the evidence for what a build actually uses is FEAT-03's recorded
    eng build runs `2026-07-31-09-eng` (dev-ops) and `2026-07-31-10-eng` (backend-dev),
    n = **2 eng runs on 1 feature** (Q1), so that is a floor, not a closed set. *(Amended
    2026-08-04: (c)'s first half previously read "that its persona set was derived from" those runs
    — a property of a key that no longer exists. The floor-not-a-closed-set half is unchanged and
    still required.)*; (d) that this file
    **prescribes one run per build covering all eng tasks, a shape the recorded runs did NOT use**
    — they used one lead-owned run per contiguous persona block. Say "prescribes a shape the
    recorded runs did not use", not "derived from" (eng-lead's Q2); (e) that the receipt path
    convention is **introduced here and has no precedent to match** — the two recorded eng
    `state.yaml` files record no artifact path at all (verified at `635ef14`), so there is nothing to
    compare against and the header must not imply there is. This is stated as fact rather than left
    as an execution-time check, because the check has already been run and its answer is "no
    precedent exists" (AMF-1).
  change_type: config
  verify: >
    `python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin'); import harness_yaml;
    d=harness_yaml.load_file('.claude/skills/harness/teams/build.yaml');
    sf=d['steps_from'];
    assert d['name']=='build' and d['lead']=='eng-lead';
    assert sf['prompt']=='from_task_intent' and sf['depends_on']=='from_task_depends_on';
    assert sf['persona']=='by_consult_when' and 'personas' not in d and 'filter' not in sf"`
    exits 0. Executed against the shipped file on 2026-08-04: **exit 0**.
    (`load_file`, not `yaml.safe_load` — eng advisory 2. The `steps_from` assertions are what make
    EMF-1/2/3 non-optional: EMF-1 and EMF-3 as presence, EMF-2 as absence.
    *(Amended 2026-08-04; the final assertion previously read `assert {'dev-ops','backend-dev'} <=
    set(d['personas'])`, and a further clause asserted a task-selection key on `steps_from:`.)*
    Both were red against the shipped file, each raising a `KeyError` on the key it named — i.e. a
    signed `verify:` that appears to check something and cannot run, this feature's charter defect
    inside its own PLAN. The roster clause is replaced by the mechanism that DISPLACED the roster
    copy, `persona: by_consult_when`, plus a regression guard that the copy has not come back; the
    selection clause is replaced by the same shape of guard, since EMF-2 now ships as a deletion.
    Both absence guards are discriminating, not vacuous (P-01): each key was present and non-empty
    before this change.)
  traces: REQ-03, D-03
  feature: FEAT-06
  status: pending

- T-05: Widen the YAML-validity gate to cover the shipped team definitions
  execution_mode: main-session-direct — reason: carve-out (mission extension, the user's explicit
    instruction — `bin/test-harness-yaml-corpus.py` is NOT in CLAUDE.md's list)
  depends_on: T-02, T-04, T-10
  files:
    - .claude/skills/harness/bin/test-harness-yaml-corpus.py
  intent: >
    `scan(root)` at `:56-58` globs `<root>/.harness/**/*.yaml` and `*.yml` only. Change it to scan
    a **list of roots**: `.harness` and `.claude/skills/harness/teams`.
    **State the return-shape contract explicitly** (eng advisory 3): six existing call sites unpack
    `_, nb = scan(d)`. Keep that two-value shape — `scan(root)` continues to return
    `(errors, n_files)` for a SINGLE root — and add a separate `scan_roots(roots)` that calls it
    once per root and returns `(errors, {root: n_files})`, so a per-root non-empty assertion has
    per-root counts to assert on. Do not change `scan`'s signature; a hand executor must not be
    able to pick the other implementation.
    Keep the existing per-file error handling verbatim (`DuplicateKeyError`, `YamlParseError` with
    the `file:line:col` mark, `OSError`) — the diagnostics are the whole point of the script.
    Report relpaths from the repo root as today, so a failure names which tree it came from.
    Update the two `check(...)` calls at `:111` and `:113-114` so the scanned-file count covers both
    roots and the "corpus is not empty" assertion is made **per root** — a second root matching zero
    files must FAIL, not pass vacuously. That is the whole reason the first assertion exists.
    Add a self-test using the existing `_fixture` helper pattern (`:83-86`): build a throwaway root
    containing `<root>/.claude/skills/harness/teams/broken.yaml` whose body is a deliberately
    unquoted `outputs: [a/{{x}}/b]`, and assert `scan` reports it. That is SC-06.
    Run T-02, T-04 and T-10 first: at `635ef14` both existing team files fail to parse, so this
    task turns the gate red on arrival if it lands before them. After T-10 the directory holds
    exactly `review.yaml` and `build.yaml` — **two** files (SC-05).
  change_type: config
  verify: >
    `python3 .claude/skills/harness/bin/test-harness-yaml-corpus.py` exits 0, its output includes a
    passing line for the broken-fixture-under-`teams/` self-test, AND
    `ls .claude/skills/harness/teams/ | wc -l` returns exactly `2`. Do NOT verify by writing a
    temporary broken file into the real `.claude/skills/harness/teams/` — the throwaway-root
    `_fixture` helper covers the same assertion without mutating the shipped tree.
  traces: REQ-04, D-02
  feature: FEAT-06
  status: pending

- T-06: Make the orchestrator playbook dispatch the named `build` team
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
    (`.claude/skills/harness/SKILL.md` has no write grant in `team-config.yaml`, and it is NOT one
    of CLAUDE.md's five enforcement files — this is the routing wall, not the carve-out)
  depends_on: T-04
  files:
    - .claude/skills/harness/SKILL.md
  intent: >
    In `## The loop`, step 3 ("Delegate to a lead, never a member", `:32-39`), the current text
    routes single tasks to "the lead that owns the relevant persona, which routes it by
    `consult-when`" and says nothing about a build team. Amend step 3 so that in the **build** phase
    the orchestrator (a) resolves the `build` team (`.harness/teams/build.yaml` first, then
    `.claude/skills/harness/teams/build.yaml`, per `harness-team/SKILL.md` step 1), (b) **selects
    the eng-squad task ids itself** and hands that list to `eng-lead`, which then routes each one to
    the specialist that owns it by `consult-when` — **two different decisions**: WHICH tasks is the
    orchestrator's, WHICH specialist is the lead's; it routes, it does not revisit the selection
    (EMF-2; T-09 must say the same and not contradict this split) — instead of composing a step list
    at dispatch. State in the same
    passage that non-eng tasks (documentation, goal-check, review, **and the qa gate**) remain
    orchestrator-sequenced squad segments because a team is single-squad by construction (DEC-118)
    — so `build` is not the whole build phase, only its eng segment.
    Also amend the `## You are a PHASE` build-exit sentence at `:211` **only if it names a
    build-phase dispatch mechanism other than the `build` team** — that is the criterion for
    "contradicts", stated so a hand executor does not have to judge (eng advisory 4). Do not
    restructure the section.
    Keep this task's edit to **at most 12 added lines**: SKILL.md is orchestrator-preloaded and
    every line costs context at each spawn. T-11 adds its own budget on top; the combined cap is in
    T-11's verify.
    Do NOT write a criterion of the form "the orchestrator then dispatches the named team" —
    unverifiable by the agent doing the editing (D-04).
  change_type: docs
  verify: >
    `grep -n 'build' .claude/skills/harness/SKILL.md` shows a line naming the `build` team as the
    build-phase resolution path AND naming DEC-118 (asserted mechanically by T-07's test), AND
    `git diff --numstat 635ef14 -- .claude/skills/harness/SKILL.md` shows **at most 12 added lines
    in total** (not "attributable to this task" — no command can make that attribution; T-06 runs
    before T-11, so at this point the total IS this task's).
  traces: REQ-03, D-03, D-04
  feature: FEAT-06
  status: pending

- T-07: Add `bin/test-team-catalog.py` and register it in the unit runner
  execution_mode: main-session-direct — reason: carve-out (D-05, kept by the user — a new gate test
    plus the runner that executes it)
  depends_on: T-02, T-04, T-06, T-08, T-11
  files:
    - .claude/skills/harness/bin/test-team-catalog.py
    - .claude/skills/harness/bin/run-unit-tests.sh
  intent: >
    New script following the same shape as the other `bin/test-*.py` (a `check(name, cond, detail)`
    helper, a `fails`/`ran` counter, exit 1 on any failure), parsing every YAML with
    `harness_yaml.load_file`. It asserts, against the real repo tree at
    `CLAUDE_PROJECT_DIR or os.getcwd()`:
    (1) `teams/review.yaml` parses and its step-id set is exactly `{code, qa, security, ui}`, with
    the `qa` step carrying `persona: qa` and `mutates_repo: false` — SC-04 (and MF-1). **Contingent
    on D-08's recommended branch**; under the alternative branch this becomes
    `{code, security, ui}`;
    (2) `teams/build.yaml` parses, has `name: build` and `lead: eng-lead` — SC-07;
    (3) `build.yaml`'s declared `lead:` is recorded in `.harness/team-config.yaml`'s `leads:` with
    `squad: eng`, so the team is single-squad **by construction** — SC-07, the DEC-118 assertion.
    Match the lead record on either the bare or the `harness-`-prefixed name;
    (4) the **Engineering** team as read from `.harness/team-config.yaml` (`d['teams']` → the entry
    whose `team-name` is `Engineering` → `members[*].name`) covers the recorded floor, i.e.
    `{harness-dev-ops, harness-backend-dev}` is a subset of that member set — SC-08. Compare against
    the full `harness-`-prefixed names as `team-config.yaml` records them, not a short form
    normalised up from `build.yaml`;
    *(Both amended 2026-08-04: (3) and (4) previously read `build.yaml`'s `personas:` key, which is
    deleted. The old (3) — `listed ⊆ Engineering` — could catch a persona that should not be there
    and structurally could NOT catch a member added to the squad, the direction a copy actually
    rots. As shipped they read `team-config.yaml` directly: check (3) at
    `bin/test-team-catalog.py:103-116`, check (4) at `:122-129`. Still exactly TEN checks, as this
    task's signed `verify:` requires.)*
    (5) `.claude/skills/harness/SKILL.md` contains a line matching both `build` and `DEC-118`
    — SC-09, a PRESENCE assertion (D-04);
    (6) the literal `"none", "null", "n/a"` occurs exactly **once** across
    `.claude/skills/harness/bin/*.py` and `*.sh`, and both `check-state.sh` and
    `validate-digest.py` contain the token `PLACEHOLDER_UNSET` — SC-02 (P-03).
    **The search needle must be CONSTRUCTED, never embedded (AMF-6).** This checker lives in the
    directory it scans, so a plain string literal of the needle takes the count 1 → 2 the moment
    this file lands and the assertion breaks itself by existing. Build it from the constant:
    `import json` and `needle = ", ".join(json.dumps(x) for x in harness_yaml.PLACEHOLDER_UNSET)`.
    **`json.dumps`, not `repr`** — verified at `635ef14`: `repr` emits SINGLE quotes
    (`'none', 'null', 'n/a'`), which matches **0** occurrences in `bin/`, while `json.dumps` emits
    the DOUBLE-quoted form that matches the **1** occurrence actually in the tree. Getting this
    wrong fails the check for the opposite reason and hands the executor the same undefined choice.
    Constructing the needle is also the D-01-consistent choice: it makes the checker read the single
    definition rather than restate it. Do NOT instead loosen the assertion to "exactly two" or
    special-case this filename out of the scanned set — that hard-codes the checker's own presence
    into the criterion the user signed;
    (7) `docs/harness/SPEC.md` contains a §13 table row for `build` whose "conducted by" cell names
    the same lead as `build.yaml`'s `lead:` — SC-10, since `check-docs.sh` is not matched by
    `test_kinds.unit.detect` and so cannot supply unit evidence;
    (8) **SC-14, the #24 assertion:** `.claude/skills/harness/SKILL.md` contains at least one
    occurrence of `test_matrix`, AND all three of `qa`, `validator` and `loop_back` occur **within
    one window of 8 consecutive lines** of that file. Implement as an anchor-free sliding window:
    join `lines[i:i+8]` and test that all three tokens are present, for every `i`. **The window is
    8 lines, and 8 is the ONLY number any site may name** — it is T-11's own added-line budget for
    the passage, so the predicate says "the three tokens occur inside the one passage T-11 adds"
    and nothing wider. Do NOT assert a single physical LINE and do NOT try to detect paragraphs:
    the prescribed passage is a quoted block whose blank-line structure is not fixed, and measured
    at `SKILL.md`'s own ~95-col house style it renders as six lines carrying `qa`+`validator`,
    `qa`+`test_matrix`, `qa`, `loop_back`, nothing, `validator` — so no single line carries all
    three and a one-line predicate would fail the plan's own prescribed text while a later harmless
    reflow could turn the gate red with content unchanged.
    **Still fully discriminating at `635ef14`, measured not assumed:** `SKILL.md` contains `qa` 0
    times, `loop_back` 0 times and `test_matrix` 0 times, so the windowed predicate is RED at any
    window size and only T-11 can turn it green. **This is the assertion that makes the #24 re-scope
    falsifiable — no other check in this feature fails if `SKILL.md` is never touched for qa;**
    (9) **SC-15, the reconciliation:** assert that the panel step set stated in `SPEC.md`'s
    ship-feature row, the panel step set stated in its review row, and the parsed step-id set of the
    shipped `review.yaml` are all the SAME SET (set equality, not literal text, so a harmless
    re-ordering does not fail).
    **The panel-group selection rule, stated because the cell is ambiguous without it:** a §13 DAG
    cell may contain several `{...}` groups — the ship-feature cell at `:1978` contains
    `{specialist devs, matched by consult-when}` as well as the panel. **The panel group is the
    `{...}` group that contains `∥`.** If a row contains **zero** such groups or **more than one**,
    the check FAILS with a diagnostic naming the row — it does not guess. Split the selected group
    on `∥` and strip each element. An ambiguous parse must be a loud failure, not a silent wrong
    answer; a gate that guesses is the defect class this feature exists to close.
    (10) **the T-01 fixture-presence assertion, registered durably (EMF-5's "eighth check"):**
    `.claude/skills/harness/bin/test-check-state.py` contains `review_sha: none` at least twice and
    `review_sha: 1ce886a` at least once — so T-01's deliverable cannot be silently omitted by a
    later edit, not just by the original executor.
    Then add `"test-team-catalog.py"` to the `SCRIPTS` array at `run-unit-tests.sh:6`. The drift
    detector at `:9` fails the runner on any `test-*.py` not in that list, so this is mandatory.
    All ten assertions run against the real repo tree, as the other catalog-style tests in `bin/`
    do; use the `_fixture` helper only if the SPEC parsing needs a negative case.
  change_type: logic
  verify: >
    `python3 .claude/skills/harness/bin/test-team-catalog.py` exits 0 and its output names **ten**
    checks, AND `.claude/skills/harness/bin/run-unit-tests.sh` exits 0 with `test-team-catalog.py`
    named in its output.
  traces: REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, D-03, D-04, D-08
  feature: FEAT-06
  status: pending

- T-08: Propagate the team catalog and the qa reconciliation into the design docs
  execution_mode: squad-dispatched — product squad, `harness-documentor`
    (`docs/**` granted at `team-config.yaml:116`)
  depends_on: T-04, T-06, T-10, T-11
  files:
    - docs/harness/SPEC.md
    - docs/harness/DECISIONS.md
  intent: >
    (a) Add one row to the §13 team catalog table (`docs/harness/SPEC.md:1974-1982`) for **build**:
    conducted by `eng-lead`; DAG column states it is an expansion over the approved PLAN's
    eng-squad tasks rather than a literal step list, one step per T-NN, personas routed by
    `consult-when`, `depends_on` read from each task's own field; notes column states it is
    **eng-squad only** by DEC-118 — a correct bound, not a gap — and that documentation, goal-check,
    review **and the `test_matrix` qa gate** remain orchestrator-sequenced segments, and that
    `mutates_repo: true` serializes the steps. Do not mark it ★ (it is not one of the four v1 core
    teams).
    (b) **The D-08 reconciliation, recommended branch.** Amend the ship-feature row's DAG cell at
    `:1978` so its panel group reads `{code ∥ qa ∥ security ∥ ui}`, matching the review row at
    `:1980` and the shipped `review.yaml` after T-02. In the same cell, keep the preceding
    `qa →` segment and add a clause distinguishing the two jobs in D-08's exact vocabulary: the
    segment **writes and runs tests** and enforces the `test_matrix` hard gate with `loop_back` to
    dev; the panel step is the same persona in **gate-only** mode, re-running the matrix over the
    pinned `review_sha` and authoring nothing. Keep the cell to one added clause — this table is
    already dense.
    (c) Add one line to `docs/harness/DECISIONS.md` at the `gate-probe` entry (`:2307-2325`) noting
    that the file was **deleted** by FEAT-06 and that the entry is retained as the historical record
    of loop-back semantics. Do not delete or rewrite the entry — a decision record that describes a
    file which no longer exists, with no note saying so, is this feature's own through-line.
    Do not restructure any table. Do not add a `<!-- stale: … -->` marker for (a): no prior wording
    is superseded, only a missing row added. (b) DOES supersede wording — mark it per whatever
    `check-docs.sh` requires and re-run the checker until clean.
  change_type: docs
  verify: >
    `.claude/skills/harness/bin/check-docs.sh` exits 0, AND
    `grep -c '^| .*\*\*build\*\*' docs/harness/SPEC.md` returns 1, AND
    `grep -c 'gate-probe' docs/harness/DECISIONS.md` is unchanged or higher AND the entry contains
    the word `deleted`, AND T-07's check (9) passes.
  traces: REQ-06, REQ-08, D-08
  feature: FEAT-06
  status: pending

- T-09: Teach the team runner the expansion form, so `build.yaml` is hostable
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
    (`.claude/skills/harness-team/SKILL.md` has no write grant; `team-config.yaml`'s only `.claude`
    grants are `.claude/skills/harness/bin/**` at `:155` and `:197`, verified at `635ef14`)
  depends_on: T-04
  files:
    - .claude/skills/harness-team/SKILL.md
  intent: >
    Step 2 of `## Process` currently says the host seeds `state.yaml` with "one `steps:` entry per
    team step", and step 3a computes the ready set from `depends_on`. Neither has a branch for a
    team file that declares `steps_from:` instead of `steps:`. Add a short subsection (target ≤ 12
    lines, this file is preloaded by every lead) stating: a team file carries EITHER a literal
    `steps:` DAG OR a `steps_from:` expansion rule; when it carries the latter, the host first
    expands it into concrete steps —
    read the source named by `steps_from.source` (for `plan_tasks`, the `## Tasks` of
    `.harness/features/<feat>/PLAN.md`);
    take the task ids **the caller handed you** — the expansion rule carries no selection key and
    the host evaluates no predicate to choose tasks; WHICH tasks arrive is the orchestrator's
    decision, already made (EMF-2; this must not contradict T-06's wording);
    resolve `persona` by `consult-when` — WHICH specialist owns each task is the lead's own
    decision, and the one real routing choice this expansion makes;
    take each step's prompt from the task's own `intent:` block when `prompt: from_task_intent`
    (EMF-3);
    build `depends_on` from each task's own `depends_on:` field when
    `depends_on: from_task_depends_on`, falling back to PLAN file order only for tasks that declare
    none — **PLAN file order is not a topological order** (EMF-1);
    substitute `{{task_id}}`/`{{persona}}` into the `id` and `outputs` templates
    — and from that point the algorithm is unchanged: expanded steps are written into `state.yaml`
    exactly as literal steps would be, and steps 3a-3d proceed as written. State explicitly that a
    task the caller did not hand you is NOT silently dropped: it stays for the orchestrator to
    sequence as its own squad segment (DEC-118).
    Do not change steps 1, 3b, 3c, 3d, or the two rules at the top of the file.
  change_type: docs
  verify: >
    `python3 -c "import sys; t=open('.claude/skills/harness-team/SKILL.md').read();
    sys.exit(0 if all(k in t for k in ('steps_from','from_task_intent','from_task_depends_on',
    'DEC-118')) else 1)"` exits 0, AND
    `wc -l < .claude/skills/harness-team/SKILL.md` has grown by no more than 14 lines versus
    `git show 635ef14:.claude/skills/harness-team/SKILL.md | wc -l`.
    Discriminating: `harness-team/SKILL.md` contains none of those three tokens today.
  traces: REQ-03, D-03, D-07
  feature: FEAT-06
  status: pending

- T-10: Delete `gate-probe.yaml`
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
    (`.claude/skills/harness/teams/**` has no write grant)
  depends_on: none
  files:
    - .claude/skills/harness/teams/gate-probe.yaml
  intent: >
    `git rm .claude/skills/harness/teams/gate-probe.yaml`. The user ruled deletion over quoting
    (Q3), overriding D-02. Verified a 1-file change: nothing executes it, `check-docs.sh` contains
    no `gate-probe` reference and passes clean, and the only references outside the file itself are
    `docs/harness/DECISIONS.md:2307-2325`, which record it as the historical proof of loop-back
    semantics. The DECISIONS.md note that the file is gone is T-08(c), not this task — `docs/**` is
    documentor's domain and this path is not.
    Delete only. Do not touch `review.yaml`, and do not "tidy" the directory further.
  change_type: config
  verify: >
    `test ! -e .claude/skills/harness/teams/gate-probe.yaml`, AND
    `ls .claude/skills/harness/teams/ | wc -l` returns `2` after T-04 (`review.yaml`, `build.yaml`),
    AND `.claude/skills/harness/bin/check-docs.sh` still exits 0, AND
    `grep -rn 'gate-probe' .claude/ | wc -l` returns `0`. That last one is passable, checked rather
    than assumed: at `635ef14` it returns **3**, and all three are inside `gate-probe.yaml` itself
    (`grep -rln` names only that file), so deleting the file takes it to 0. If a future edit adds a
    reference elsewhere under `.claude/`, this verify fails loudly instead of the deletion
    orphaning it.
  traces: REQ-04, D-02
  feature: FEAT-06
  status: pending

- T-11: Name the blocking qa gate in the orchestrator playbook — the #24 fix
  execution_mode: main-session-direct — reason: domain-ungranted, issue #20
    (`.claude/skills/harness/SKILL.md` has no write grant in `team-config.yaml`. **It is NOT one of
    CLAUDE.md's five enforcement files**, so this is the routing wall and not the DEC-174
    carve-out. Getting that reason right is what keeps #20's evidence base clean)
  depends_on: T-06
  files:
    - .claude/skills/harness/SKILL.md
  intent: >
    THE CENTRE OF THE RE-SCOPE. `SKILL.md` is the only thing `harness-orchestrator` preloads
    (`.claude/agents/harness-orchestrator.md:8-12`) and `grep -c -i` returns **0** for both `qa` and
    `test_matrix` at `635ef14`, while `SPEC.md:1978` assigns the sequencing to the orchestrator.
    Add to `## The loop` — immediately after step 3's build-team passage from T-06, so the two read
    as one sequence — a passage of **at most 8 added lines** stating, in the SAME vocabulary
    `build.yaml`'s `purpose:` uses (EMF-4; the two are one fix seen from two sides):
    "**After the build team returns, sequence the qa segment.** It is a **validator-squad** segment <!-- ok-stale --> historical: quotes the pre-DEC-180 playbook
    you sequence yourself — `harness-qa` writes and runs the tests and enforces the `test_matrix`
    hard gate (`harness.json` `gates.qa_gate: blocking`, the project's only blocking gate). On
    failure, `loop_back` to the dev that owns the task; the build is not done until the matrix
    passes. It is not a step the `build` team contains, because a team is single-squad (DEC-118).
    Pin `review_sha` before any validator run (INV-6)."
    The `loop_back`, `validator`, `test_matrix` and `qa` tokens must all appear **inside this one
    passage, not scattered across the file.** T-07 check (8) and this task's verify test a window of
    **8 consecutive lines** — T-11's own added-line budget — so tokens spread across the document
    satisfy the letter and still fail the check. Write the passage as one contiguous block, with the
    `loop_back` sentence and the `validator-squad` sentence in the same block rather than separated
    by other content. This also means the passage must stand on its own tokens: T-06's build-team
    text lands immediately before it and itself contains `qa`, but `loop_back` and `test_matrix`
    occur **0** times in `SKILL.md` at `635ef14` and only this task adds them, so SC-14 stays red
    until this task lands.
    Do NOT restructure the loop, do NOT duplicate the INV-6 sentence already at `:38` (reference it
    rather than repeating it if that is shorter), and do NOT write a criterion of the form "the
    orchestrator then runs the gate" — unverifiable by the agent doing the editing (D-04).
    Combined budget check: T-06 + T-11 together add at most **20** lines to `SKILL.md`.
  change_type: docs
  verify: >
    `grep -c -i 'test_matrix' .claude/skills/harness/SKILL.md` returns `>= 1` (it returns `0` at
    `635ef14` — the change is the only thing that can produce it), AND
    `python3 -c "import sys; ls=open('.claude/skills/harness/SKILL.md').read().splitlines(); W=8;
    sys.exit(0 if any(all(k in '\n'.join(ls[i:i+W]) for k in ('qa','validator','loop_back'))
    for i in range(len(ls))) else 1)"` exits 0 — the **8-consecutive-line window**, the same and only
    window number T-07 check (8) and SC-14 name. Measured at `635ef14`: this command exits **1**
    (`qa` and `loop_back` each occur 0 times), and it exits **0** against a copy of `SKILL.md` with
    the passage above inserted. It is a window and not a single line because the passage renders as
    six lines at this file's house style with no line carrying all three tokens, AND
    `git diff --numstat 635ef14 -- .claude/skills/harness/SKILL.md` shows **at most 20 added lines
    in total** — T-06's 12 plus this task's 8, measured against the same base so no attribution
    judgement is needed.
  traces: REQ-07, REQ-08, D-08
  feature: FEAT-06
  status: pending

## Verify receipts — commands whose result only this change can produce

| SC | Discriminating command | Why it was not already true |
|---|---|---|
| SC-01 | the three new INV-6 fixtures in `test-check-state.py`, plus presence greps on each | fixture (a) fails at `635ef14`; the presence greps stop a rewrite that never writes it (EMF-5) |
| SC-02 | `grep -rn '"none", "null", "n/a"' bin/ \| wc -l` → `1` | returns `1` today too, but at `validate-digest.py:472`; paired with `grep -c PLACEHOLDER_UNSET` on both consumers, which returns 0/0 today |
| SC-04 | parsed step-id set `== {code,qa,security,ui}` with `mutates_repo is False` | today the file does not parse at all, and its ids are `{code,security,ui}` |
| SC-05 | `load_file` over `teams/` + `ls teams/ \| wc -l` → `2` | today the glob cannot see `teams/`, both files there fail to parse, and there are two files of which one is being deleted |
| SC-06 | broken fixture under a `teams/` root makes the gate fail | today no fixture placed there is scanned; the assertion is vacuous |
| SC-09 | `grep` for a SKILL.md line naming both `build` and `DEC-118` | **absent today.** The mirror-image absence-grep would already have passed — D-04 |
| **SC-14** | `grep -c -i 'test_matrix' .claude/skills/harness/SKILL.md` → `>= 1` | **returns `0` at `635ef14`.** Nothing but editing `SKILL.md` can move it — `review.yaml` alone cannot satisfy this SC |
| **SC-15** | SPEC ship-row panel set == SPEC review-row panel set == parsed `review.yaml` step ids | today these are three different sets, which is issue #24's three-descriptions problem stated as a test |

## Open questions

- **Q8 — ANSWERED 2026-08-04. NOT BLOCKING. Settled in place; kept as the record.** D-08, the
  three-descriptions reconciliation, was signed by the user on pm's recommended branch
  (`notes/answers-replan-product.md`). Nothing about the plan shifts. The reasoning as it stood at
  the time, retained: three shipped sources disagree about where the blocking qa gate runs and no two
  agree. pm recommended the **"two jobs, one persona"** branch: an orchestrator-sequenced qa
  *segment* that writes and runs tests (`SPEC.md:1978`, the #24 fix, T-11) plus a gate-only qa
  *panel step* that re-runs the matrix over the pinned SHA and authors nothing (`SPEC.md:1980`, #8,
  T-02). The check that settled it: **standalone review is a real dispatch path** (`SPEC.md:1980`
  names it; `harness/SKILL.md:66` lets the orchestrator "insert a review") and **nothing else runs
  the matrix on it** — the alternative branch closes #24's hole and opens the identical one there.
  Cost of the recommendation, stated plainly: qa is spawned twice in a full ship — **the user
  accepted that cost explicitly.** The flip-delta written into D-08 touches T-02, SC-04, T-07(1)
  **and T-08**; **#24's fix is unaffected either way.** **It was NOT applied** — the user took the
  recommended branch. This was a scope-and-approved-artifact decision, so it was not pm's.
- **Q9 (ANSWERED 2026-08-04, informational) — the budget, RAISED to $160.** The user authorised
  **+$40**: `max_cost_usd` moves from 120 to **160** (`notes/answers-replan-product.md`, the
  orchestrator's Q10). Honest carry: **57–90 of 160 spent** — 44.81 measured (18.90 plan-eng +
  25.91 replan-product) plus a never-measured segment-1 band of 12–45. The re-scope adds two tasks
  (T-10, T-11), two REQs, two SCs and one decision. Honest read: **it fits with the raise; the
  margin is the review-and-loop-back tail, as it always was.** The
  remaining **70–103** buys the build (10 tasks, 9 of them main-session-direct so they cost
  main-session turns rather than spawns), one documentor dispatch, one qa segment, the
  pre-signature architecture review and one review panel. The
  exposure is the review-and-loop-back tail, not the build. If the user wants a hard guarantee
  rather than an estimate, the lever is dropping T-09 — which would leave `build.yaml` prose only
  (D-03's own note) and is not recommended. Cost never stops work (DEC-134); this is stated, not
  a request.
  **Recorded here because it is what the raise buys: the orchestrator's own Q9 — how much
  architecture review this rewritten PLAN gets — was ANSWERED AGAINST ITS RECOMMENDATION.** The
  orchestrator recommended a scoped delta review after signature (est. 10–19). **The user overrode
  it and chose a FULL architecture review of the rewritten PLAN, run BEFORE they sign** — the
  standing instruction is that the user signs a plan an architect has already passed end to end,
  and this rewrite has had none. The staleness objection behind the delta recommendation does not
  apply: D-08 came back on the recommended branch, so the PLAN does not shift underneath the
  reviewer. Scope: the re-scope and its D-NN decisions, the 15 SCs, retired T-03, added T-10/T-11,
  the qa two-places shape now that D-08 is settled, and confirmation the six EMF remedies landed as
  eng-lead specified.
- **Q1 (non-blocking) — the #9 evidence base is thinner than every prior statement of it.** The
  grilling says "five real build runs"; issue #9's title says "four"; disk at `635ef14` shows
  **three**, of which only **two** are eng-squad and therefore inside a legal `build` team. So
  `build.yaml` derives from **n = 2 eng runs on 1 feature**. A floor, not a generalisation, and
  T-04 says so in the file's header comment.
- **Q2 (non-blocking, REWRITTEN per the user's re-scope) — `build.yaml` covering the eng half is
  a correct bound, not a shortfall.** DEC-118 makes a team single-squad, so `build.yaml` covers
  FEAT-03's 7 eng tasks and not the product-squad documentation step, and it never covers qa. That
  is the design working, not a gap: the qa gate and the documentation step are orchestrator-
  sequenced segments and this feature now makes the qa one explicit (T-11). **No SC apologises for
  7-of-8 and `build.yaml` is not widened to reach qa.** If the user ever wants the whole build
  phase to come from one definition, that is a *playbook* object like `ship-feature`, and a
  different feature.
- **Q4 (non-blocking) — the routing wall, recurrences 5 and 6, belongs to issue #20.** Six of this
  PLAN's ten tasks are `main-session-direct` on domain grounds alone. `visual-designer` having no
  legal path for a design ruling is the sixth instance. Noted for #20, **not fixed here** on the
  user's instruction (Q10).
- **Q6 (non-blocking) — T-01 turns no existing gate red, checked rather than assumed.** Every
  `feature.yaml` at `635ef14` except this one carries a real SHA. `FEAT-06`'s own is `none`, and it
  now carries **two** `runs:` entries — `plan-product` and `plan-eng` — **neither `squad: validator`**,
  so INV-6's precondition is still unmet. (The earlier statement that `runs:` was empty is now
  false; the conclusion is unchanged. Corrected in BRIEF SC-03 rather than left standing.) The
  first thing the fixed invariant polices is this feature's own validate phase: the orchestrator
  must pin `review_sha` before recording a validator run. Intended behaviour, not a collision.
- **Q7 (non-blocking) — T-07 carries `change_type: logic`**, live in `harness.json` `test_matrix`
  (`logic.always: [unit]`) but missing from `validate-digest.py:85`'s per-persona change-type
  vocabulary — issue #10, out of scope. `check-state.sh:99` only checks presence, so INV-4 is
  satisfied and the qa gate resolves to `unit`. T-07 is `main-session-direct` and returns no digest,
  so the exposure is nil for this feature. Flagged so nobody re-diagnoses it mid-build.
- **Q11 (non-blocking, known and filed — NOT re-derived) — issue #19: no agent ever runs a PLAN
  task's `verify:` command.** Every `verify:` above is a command a human or the main session must
  run. The user has been told; it is filed and out of scope. Recorded here only so the build does
  not assume the verifies self-execute.
