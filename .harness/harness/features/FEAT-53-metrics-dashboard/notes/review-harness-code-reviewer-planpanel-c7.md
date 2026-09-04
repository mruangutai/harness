# Plan-panel c7 — independent read, plan-as-spec — e6b93643

Read at `e6b93643` (`git rev-parse HEAD` confirmed), the same commit c6 reviewed — no commit has
landed since c6, confirmed by `git log` and by c6's note being the newest file in `notes/`. Read in
full: `plan.yaml` (2184 lines, all of D-01..D-23, T-01..T-22, the plan-cycle-3 RECORD comment block,
and every `panel.findings` entry through cycle 5 plus c6's un-merged F-1..F-5), `BRIEF.md` (all
REQ/SC/Coverage), `DESIGN.md` (all of Substrate/Palette/Type/Spacing/C-1..C-4/prototype
gate/Q1-Q4), `.harness/harness.json`, `.harness/team-config.yaml` and `check-domain.sh --resolve`
against a dozen representative task files.

## Prior-cycle findings re-verified as closed (not re-raised)

Checked against current plan.yaml text, not against summaries: PF-328f8f3c (D-21 predicate),
PF-7408d83a (T-21 mount+gate), PF-45518258 (T-16 depends_on T-21), PF-3b85f18/D-22, V-1..V-5 (D-14
one-authority, T-06 four-branch fixtures, T-11 copy-to-temp discipline, D-21 day-granularity),
C4-01..C4-07 (T-19 git-init commit case, T-10 week definition, D-08/D-20 no-longer-open, D-23
backlog carrier, T-07/BRIEF `12`/`3` carriers), PF-0f13227f/PF-1b818430/PF-804ec98d (T-10 boundary
bucket, T-19 baseline commit, D-23/C4-04 self-reference). All read as implemented exactly as their
`resolved_by`/`note` fields claim; none disputed.

Backlogged and correctly left alone (accepted, not fixed): PF-04c95fd6/B-1, PF-3713534d/B-2,
PF-55e28a6e/B-3, PF-d2fc9563/B-4, PF-ce8b018f/B-5, PF-0f3f4101/B-12, PF-aa9c41f6/B-13,
PF-ed0712ea/B-14, C4-05/B-23, C4-07/B-25, D-23's B-7..B-10.

**c6's F-1 through F-5 (`notes/review-harness-code-reviewer-planpanel-c6.md`) are NOT yet
dispositioned** — no commit has landed since c6 ran, and none of the five is reflected in
`panel.findings`. I re-verified F-1 independently (below) and it is confirmed still live. F-2..F-5
stand as c6 left them (notes/low, non-blocking) and I did not find grounds to change their rating.

## Findings

### G1 (= c6's F-1, still live) · `npm ci` cannot succeed on a clean checkout of T-05's own committed tree — **high, must_fix**

`plan.yaml:355-361` (T-05 `files:`) omits `package-lock.json`; `plan.yaml:363` T-05's `verify` runs
`npm ci` first. `git ls-files` under `notes/prototypes/FEAT-53/` at HEAD confirms no
`package-lock.json` is tracked, while the working tree carries an untracked one (confirmed via
`find`). `npm ci` requires a committed lockfile and fails immediately without one — this is not
carried over from an older cycle, c6 already traced it to this same amendment. Sibling task T-04
shows the plan author knows the fix (`package-lock.json` in `files:`, intent says "COMMIT the
resulting package-lock.json") — T-05 does neither. Failure scenario unchanged from c6: a fresh
clone of this commit's tree running T-05's own literal verify hits `npm ci` failing at the first
step, so the task can never mechanically re-verify itself, which is the exact thing adding `npm ci`
was meant to prove. Remedy: add `package-lock.json` to T-05's `files:` and its intent's own
"COMMIT" instruction, matching T-04's pattern.

### G2 (new) · `change_type: frontend`'s mandatory `component` test kind is `unresolved`/`cmd: null`, so every frontend task in this plan BLOCKS the (blocking) QA gate — **high, must_fix**

`.harness/harness.json:30-34` — `test_matrix.frontend.always` is `[unit, component]`. This is the
committed, per-project matrix (`_test_matrix_note`, `plan.yaml` untouched by this feature) and is a
FLOOR qa may not drop below. `.harness/harness.json:146-150` — `test_kinds.component` carries
`cmd: null` and `status: "unresolved"` (not `"excluded"`, no `_matrix_provenance` entry for
`frontend` — checked `harness.json:87-118`, entries exist only for `api`, `cross_module`,
`feature`, `config`).

`.agents/skills/harness-qa-gate/SKILL.md:85` states plainly: `cmd` is `null`/absent → `BLOCKED`,
never a pass, never a soft skip; and separately, "no test files matched" is *also* `BLOCKED`, not a
soft skip — the soft-skip row is reserved for tooling that is "genuinely not present," which does
not describe this project once T-04 installs vitest/jsdom/`@testing-library/react` (the toolchain
the render gate uses). `component`'s own `detect` glob (`**/*.spec.tsx|**/*.stories.tsx|**/*.stories.ts`)
matches none of the files this plan creates — T-04/T-21 use `.test.tsx`, not `.spec.tsx` — so it is
BLOCKED on both counts (`cmd: null` and, independently, zero matched files).

Four tasks declare `change_type: frontend`: T-13 (`plan.yaml:1030`), T-14 (`:1072`), T-15
(`:1138`), T-21 (`:1393`). The plan is well aware `component`'s `cmd` is `null` — it says so twice,
verbatim, as the *motivation* for building the vitest render gate under the `integration` kind
instead (`plan.yaml:328`, `:1536`) — but that routing closes only the functional gap (an executing
render assertion exists); it does not touch `test_kinds.component`'s status, and nothing in T-01..T-22
sets it to `excluded` (which the note says requires "a human's recorded call, never inferred at gate
time") or points its `cmd`/`detect` at the same toolchain. `qa_gate` is `"blocking"` per
`harness.json:203`, not advisory.

I grepped every note under this feature's `notes/` (all six prior panel cycles, all ship-reviews, all
research files) for `test_matrix`, `component.*BLOCKED`, `frontend.*component` and `qa_gate.*block`:
zero hits. This gap predates FEAT-53 in `harness.json` (DEC-187's original matrix), but FEAT-53 is
the first feature in this repository to introduce `change_type: frontend` work at all (BRIEF's own
"## Verification gaps" says this feature "introduces the first `.tsx` and `.ts` application code in
the repo"), so it is the first plan to actually trip it — and none of the six prior cycles caught it.

**Failure scenario:** T-13 (or any of T-13/T-14/T-15/T-21) lands, and the run proceeds to the QA
gate. QA evaluates the diff's `change_type`s against `test_matrix`, finds `frontend` requiring
`component`, looks up `test_kinds.component`, finds `cmd: null` / `status: unresolved` → returns
`VERDICT: BLOCKED — test command misconfigured for kind 'component'` per the gate's own stated rule.
This halts the build at the first frontend task, contradicting BRIEF `## Verification gaps`'s framing
of the component/typecheck gap as merely "unproven" (an evidentiary weakness) rather than a hard
stop the blocking gate will actually enforce.

**Remedy, smallest sufficient:** add one `test_kinds.component` resolution to this plan — either (a)
extend `component.detect` to include the render-gate's own `src/**/*.test.tsx` and point its `cmd`
at the same `npm --prefix .../client run test` T-21/T-22 already stand up (making it redundant with,
not separate from, the `integration`-kind gate), or (b) add a `_matrix_provenance.frontend` entry
with a signed decision explaining that `component` is excluded because its render-behaviour
obligation is discharged under `integration` via T-21/T-22, and set `test_kinds.component.status` to
`"excluded"` accordingly. `harness.json` is already a T-03 file (`plan.yaml:290`, dev-ops lane,
confirmed by `check-domain.sh --resolve`), so extending T-03 (or adding one clause to T-22, which
already edits the CI/test wiring) is in-lane and does not need a new task.

## Traceability, executability, lanes, decision integrity — no new findings

- **REQ↔SC coverage table** (`BRIEF.md` "### Coverage"): verified both directions by hand for all 15
  REQs and all 20 SCs — every `REQ | covered by` list and every `SC | traces` list cross-references
  consistently; no REQ is uncovered, no SC is untraced, no asymmetry between the two halves.
- **DAG ordering** (task executability #2): walked every task's `depends_on` against what its own
  `verify:` reads or invokes. No verify references an artifact a later task creates — the two
  apparent risks (T-16's bundle build needing T-21's chart mount; T-12's serve.py needing T-08/T-10/
  T-11's KPI wiring) are both explicit `depends_on` edges. T-13's `npm run build` needs T-04's
  installed toolchain, present via its own `depends_on: [T-01, T-04, T-05, T-18]`.
- **Lanes** (`check-domain.sh --resolve`, sampled T-04, T-06, T-09, T-11, T-12, T-16, T-17, T-18,
  T-19, T-20, T-22, T-02, plus T-05's prototype path): every task's `execution_agent` is among the
  resolved owners for its `files:`; T-01's widening of `harness-frontend-dev` onto the client
  subtree is correctly sequenced before every task that needs it; T-20/T-02/T-01's
  `main-session-direct` classification is correct (`check-domain.sh` returns `NOBODY` for their
  files). No task mixes lanes.
- **D-01..D-23 integrity:** no internal contradiction found. One cosmetic note, not raised as a
  finding: the "RECORD — what changed in plan cycle 3" comment block (`plan.yaml` between T-22 and
  `panel:`) restates the KPI-4 predicate using "the feature's plan.yaml approval.date" — the
  pre-D-14 formulation — while the live `D-21.choice` (`plan.yaml:125`) and `D-14.choice`
  (`plan.yaml:96`) both correctly cite the BRIEF.md approval date. The comment is explicitly
  historical ("what changed in cycle 3") and drives no verify or task, so this is not a build-time
  risk; flagging only so a future reader does not mistake it for the live rule.
- **REQ-11/D-19 unavailable-vs-zero, D-21/D-22 touchpoints epoch, T-19's non-fatal ship wrap:** all
  three read as solidly specified. D-19's null-plus-specific-reason contract is enforced
  consistently across T-06, T-10, T-11, T-19 and DESIGN S-4. D-21's four-branch ladder and D-22's
  commit-ownership assignment (T-20 for the two touchpoints files, T-19 for trend.jsonl) leave no
  gap I could find. T-19's non-fatal commit wrap is tested on both branches (the git-init'd
  succeeding case per C4-01/PF-1b818430's fix, and the explicit non-git failure-branch case) — no
  fail-open: the commit failure path prints and continues without ever silently substituting a
  fabricated success.

## Verdict basis

`must_fix` = [G1, G2]. `severity_max` = high. Both are build-time blockers with concrete failure
scenarios; neither is a re-litigation of a disposed finding. G1 is a live carry-forward of c6's own
must_fix (unaddressed since, no new commit); G2 is new to this cycle.
