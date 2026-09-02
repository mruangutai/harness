# Receipt — harness-dev-ops — A3 placement/distribution/grant/test-ordering — FEAT-53

**BLUF.** Placement under `.claude/skills/harness/bin/dashboard/` is the only *reachable* home and
the note's routing conclusion re-derives clean — but the plan conflates "reachable" with "sound":
a `.tsx`+npm+node_modules+committed-`dist/` tree under `bin/` is a real, if survivable, new kind of
artifact this tree has never carried, and one real gap exists in what makes it survivable (A3b-4:
the prototype's own untracked node project, not what T-02 ignores). No unhandled breakage found in
the four existing consumers checked (test-no-distribution.py, check-state.sh, run-unit-tests.sh,
team-config.yaml). Test-registration ordering across T-03→T-06→T-10→T-12 is genuinely gap-free.

## A3a — placement — SOUND (with one gap named)

Re-derived independently via `check-domain.sh --resolve`:
- `web/src/App.tsx` → `NOBODY`
- `.claude/skills/harness/bin/dashboard/client/src/App.tsx` → `harness-backend-dev`, `harness-dev-ops`
- `.claude/skills/harness/bin/dashboard/client/package.json` → `harness-backend-dev`, `harness-dev-ops`

Note's structural conclusion holds exactly as stated: no product-side glob resolves an owner in
this checkout, so `bin/dashboard/` is the only grantable location. That answers *reachable*, not
*sound* — the two are different questions and the note (and D-01) only answers the first.

On soundness: given DEC-202 (skill tree *is* the distribution), a nested npm project under `bin/`
is defensible — it is control-plane source, same as any other authored tool, and D-04 already
elects to commit `dist/` rather than require a build step for every consumer. The alternative
(`web/src/**`) is not merely unsound, it's `NOBODY` — not a real option today. No sounder *granted*
alternative exists. Verdict: **accept the placement**, but it is accepted for lack of an
alternative, not because a `node_modules/`-bearing tree under `bin/` is an established pattern here
— nothing else in `bin/` has one. This is a **finding**, not a blocker:

- **F-A3a-1** (advisory, remedy_cost: n/a — no plan text to change, it's a residual risk to carry
  forward). Citation: D-01, T-04 intent (plan.yaml:201-218). Consequence: `bin/` becomes the first
  directory in this repo requiring `npm install` before some of its contents are usable/testable;
  any future generic "sweep every file under `bin/`" tool (none exists today, per A3b) will need to
  know to skip `client/node_modules/` and `client/dist/`. Alternative: none better than what's
  planned. Cost of doing nothing: low, contained by T-02's ignores and by run-unit-tests.sh's
  non-recursive scan (A3b).

## A3b — blast radius — consumer table

| consumer | sweeps `bin/**`? | effect of nested npm project | state |
|---|---|---|---|
| `test-no-distribution.py` (case1/2/6) | reads `git ls-files` (tracked only), case2 token-scans tracked files for `deploy.sh`/`harness-deploy`/`registry.json` tokens | node_modules is gitignored (T-02) → never tracked → invisible to `git ls-files`; committed `dist/` and `client/src/**` are tracked but contain none of the four tokens | **unaffected** |
| `check-state.sh` | globs only `.harness/*/features/*/{BRIEF.md,PLAN.md,plan.yaml,STATE.md,feature.json,runs/*}` — never touches `.claude/skills/harness/bin/**` at all (checked full grep) | n/a | **unaffected** |
| `run-unit-tests.sh` drift detector (line 61: `for f in "$BIN_DIR"/test-*.py`) | **non-recursive** shell glob, direct children of `BIN_DIR` only, no globstar | a `test-*.py` inside `dashboard/client/node_modules/**` (hypothetical — JS deps don't ship Python tests, but structurally) would **not** be discovered; a `test-*.py` placed directly in `bin/` still would | **unaffected**, confirmed by reading the exact glob, not inferred |
| `.harness/team-config.yaml` domain globs | `.claude/skills/harness/bin/**` already granted to `harness-backend-dev` and `harness-dev-ops` (lines 184, 225) before this plan | T-01 adds a third grantee scoped to `client/**` only | **affected, plan handles it** (T-01) |
| `post-merge-sweep.sh` | walks worktrees/runs, not `bin/**` contents | n/a | **unaffected** |
| gitignore completeness (T-02) | ignores `client/node_modules/`, `client/.vite/` only | vite/tsc write no other artifacts into the project dir under the planned scripts (`vite build`/`vite`, `tsc` never invoked standalone, `noEmit: true` so no `tsbuildinfo`); `dist/` deliberately tracked (D-04); `package-lock.json` deliberately tracked (T-04) | **complete for the planned toolchain** — advisory below for the untracked residual `npm-debug.log` class |
| **prototype's own `package.json`** (`FD/notes/prototypes/FEAT-53/`) | n/a — separate location entirely, outside `bin/**` | **YES, a second Node project exists in this repo today**, currently fully **untracked** (`git status --porcelain` → `??` for the whole dir). It carries its own `.gitignore` (node_modules/, dist/, .smoke/, **package-lock.json** — inconsistent with T-04's client, which commits its lockfile) and its own dependency pins (`@astryxdesign/core 0.5.2`, `react 19.2.8`) that need not match whatever T-04 resolves "at install time". Nothing in the checked consumer set (test-no-distribution.py, check-state.sh, run-unit-tests.sh) sweeps or tests it — it is invisible to all of them by construction (wrong path, and T-05's own verify only reads under its own dir). | **affected, unhandled by T-01–T-16**: T-05's `files:` names only `index.html` and `README.md`, not `package.json`/`vite.config.js`/`.gitignore`, so the plan gives no instruction on whether those three are meant to land tracked at all |

- **F-A3b-1** (advisory, remedy_cost: amend — T-05's `files:` is a list per plan.yaml's own
  schema... but T-05 is `harness-visual-designer`'s task already `status: building`, so this
  crosses into an already-known amendment (T-15/CAP-probe.md correction lands before signature per
  dispatch's already-known list); flagging as a *sibling* gap in the same task, not a duplicate of
  the known T-15 finding). Citation: plan.yaml:227-229 (T-05 `files:`) vs. on-disk
  `notes/prototypes/FEAT-53/package.json`, `vite.config.js`, `.gitignore` (confirmed present,
  confirmed untracked). Consequence: if T-05 lands with only `index.html`/`README.md` staged, the
  prototype's own `node_modules`/`dist`/`.smoke` ignore rules never get committed, and a later `git
  add -A` (or any tooling assuming a feature dir is fully tracked) either dirties the tree with a
  second uncommitted `node_modules/` or silently untracks a second package manifest this repo now
  depends on for provenance (README's "resolved from the registry at author time" claim). Alternative:
  T-05's `files:` should include the three untracked support files or explicitly say the prototype's
  toolchain files are intentionally left untracked and why.

## A3c — grant and ordering — SOUND

- **Ordering**: `grep depends_on:.*T-01` finds exactly one direct dependent, T-13
  (plan.yaml:544, `depends_on: [T-01, T-04, T-05]`). T-14 depends on T-13, T-15 depends on T-14 —
  both transitively downstream of T-01. No frontend-dev task reaches the client subtree ahead of
  the grant. **Verdict: correctly ordered.**
- **Overlap**: after T-01, three personas (`backend-dev`, `dev-ops`, `frontend-dev`) can write
  `client/**`. Checking actual scheduled writers per file: T-04 (dev-ops) writes
  `client/{package.json,tsconfig.json,vite.config.ts,index.html,package-lock.json}`, gated by
  `depends_on: [T-02]`; T-13/14/15 (frontend-dev) write `client/src/**`, gated behind
  `[T-01, T-04, T-05]` and the T-13→T-14→T-15 chain; T-16 (dev-ops) writes `client/dist/**`, gated
  behind `[T-12, T-15]`. **No two tasks in this plan target the same file**, so the DAG's
  `depends_on` — not the lane row — is what actually prevents a same-file race. **Verdict: no
  collision in the scheduled task set.**
- **Lane row as "adequate control"**: the row (plan.yaml:9-11, `agent: harness-backend-dev |
  harness-dev-ops | harness-frontend-dev after T-01`) is descriptive text, not an enforcement
  mechanism — it documents who *may* write, not who *will*, and covers the whole
  `.claude/skills/harness/bin/**` surface, wider than the actual overlap (`client/**` only). For
  the tasks as planned this is harmless because `depends_on` does the real serializing. It is not
  an "adequate control" in the sense of preventing a *future*, off-plan write from racing — nothing
  in the row or the grant enforces sequencing by itself.
  - **F-A3c-1** (advisory, remedy_cost: amend). Citation: plan.yaml:9-11. Consequence: none for
    this plan's own tasks (verified above); a risk only for work added after this plan without a
    fresh `depends_on` audit. Alternative: none required now; note it as a standing caveat rather
    than a plan defect.
- **T-01 verify clause**: `check-domain.sh --resolve <client/App.tsx> | grep -qx harness-frontend-dev`
  (plan.yaml:127). Read the resolver source (check-domain.sh:286-295): it prints **one grantee per
  line**, sorted, "NOBODY" only when the set is empty. Independently reproduced pre-grant state:
  the path today resolves to two lines (`harness-backend-dev`, `harness-dev-ops`). `grep -qx`
  matches a full line anywhere in multi-line stdin, so a third grantee added by T-01 is matched
  correctly regardless of the two pre-existing owners or their sort position. **Verdict: the verify
  clause is correct and will discriminate real success from failure.**

## A3d — test-registration ordering — GAP-FREE, confirmed against source

Read `run-unit-tests.sh` directly (not the note's paraphrase):
- **Unregistered on-disk `test-*.py`**: line 61 loop, line 72 `exit 2` — confirmed, exits 2.
- **Registered name whose file doesn't exist**: this is **not** caught by `--check-kinds`
  (line 142-145 returns before the execution loop) — it is only caught by an actual run, at
  line 148-150 (`python3 "$BIN_DIR/$s"`; a missing file makes `python3` exit 2, marked `FAIL`,
  and the suite as a whole exits **1** at line 159-160, not 2). The research note itself says
  "FAILS the suite" (line 84), not "exits 2" — accurate as written; the dispatch's paraphrase
  slightly overstates it, immaterial to the ordering conclusion since every task's `verify:` uses
  `--check-kinds` (which never runs this path) plus a direct `python3 <specific-file>` call, never
  the full suite.
- **Kind cross-check** (lines 96-140): compares `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` against
  `harness.json`'s `integration.detect` set. It only flags (a) an `INTEGRATION_SCRIPTS` entry
  *absent* from `detect`, or (b) a `UNIT_SCRIPTS` entry *present* in `detect` — an entry declared
  in `detect` with **no** matching bash-array entry is never flagged (confirmed: the loop at
  line 121 iterates `integ`/`unit`, never `declared`, so nothing in `declared` alone is visited).

Walking the four commit boundaries with this exact behavior:
- **After T-03** (declares `test-metrics-dashboard.py`/`test-metrics-trend.py` in `harness.json`
  only, explicitly not in either bash array, plan.yaml:179-182): drift detector sees no new files
  on disk → passes. Kind cross-check: the two new `detect` entries have no bash-array counterpart
  yet, which is the unflagged case above → passes. **Green.**
- **After T-06** (creates `test-metrics-kpi.py`, registers it in `UNIT_SCRIPTS`, plan.yaml:301 —
  correctly *not* added to `harness.json`, since it's a unit test): drift detector finds the file
  now listed → passes. Kind cross-check: a `UNIT_SCRIPTS` name must NOT be in `detect` — it isn't
  → passes. **Green.**
- **After T-10** (creates `test-metrics-trend.py`, registers in `INTEGRATION_SCRIPTS`,
  plan.yaml:451, already declared by T-03): both checks pass. **Green.**
- **After T-12** (creates `test-metrics-dashboard.py`, registers in `INTEGRATION_SCRIPTS`,
  plan.yaml:530, already declared by T-03): both checks pass. **Green.**

**Verdict: no red window at any of the four boundaries**, contingent on each task landing as one
atomic commit (file + its own array registration together), which is what each task's `files:`
list already scopes to.

## Findings summary

| id | severity | remedy_cost |
|---|---|---|
| F-A3a-1 | advisory | n/a (residual risk, no text to amend) |
| F-A3b-1 | advisory | amend (T-05 `files:` — visual-designer's task, flagged for pm to fold in alongside the already-known T-15 correction) |
| F-A3c-1 | advisory | amend (lane-row caveat, optional) |

No blocking findings. Placement, grant ordering, and test-registration ordering all hold under
direct measurement.

## Open questions
- none blocking. F-A3b-1 should reach harness-pm's batched amendment alongside the two
  already-known T-15/T-05 corrections, since it touches the same task.
