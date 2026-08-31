# Grilling — harness's own tests move to `tests/**` — 2026-08-31

Entered as `/harness-plan issue://979` ("verification that verifies nothing"). Grilling
found that #979's qa half is blocked by a layout property, and that property is the
feature. **#979 is re-planned afterwards, on the repaired foundation.**

## Destination

Harness's own tests live in `tests/unit/**` and `tests/integration/**` like any other
project's, `bin/` becomes provably test-free, and the directory a test sits in *is* its
kind. Consequence that motivated it: "may write a test" stops being inseparable from
"may write an enforcement script".

## Settled

- **Is `bin/` placement drift?** → No. It follows from the two-base model: in the harness
  base a match is accepted only for a control-plane *target*, and harness's tests are
  control-plane by sitting under `.agents/**`. Corrected mid-session — an earlier
  agreement that "the standard is broken" was made before checking the mechanism.
- **Do it anyway?** → Yes, as a deliberate architectural position, not a drift repair.
  Harness's product is Harness; its tests are product artifacts.
- **How does the harness base accept `tests/**`?** → Add `tests/**` to
  `HARNESS_CONTROL_PLANE`. Smallest change to a working model.
- **Who holds `tests/**` after the move?** → `harness-qa`, `harness-backend-dev`,
  `harness-dev-ops`. The three that build here; the other two Iron Law seats stay as
  blocked as they are today.
- **Accepted consequence, recorded so #979 inherits it rather than rediscovering it:**
  granting qa `tests/**` makes qa an author of tests it also grades. That is the
  author-is-checker shape one level up — #979's central finding. Accepted here because
  the alternative (qa may never author a test) contradicts nothing in this feature but
  puts a spawn round-trip inside every red-green cycle, and because qa's Phase 1
  blindness (`harness-verification-rules:15`) already separates *deriving expected
  coverage* from *reading the implementation*. **The residual question — who checks that
  qa's own tests bind — is #979's, not this feature's.**
- **How does the runner register tests?** → Directory-driven; the arrays and the
  KIND-DRIFT set comparison are deleted. Keep one guard: the two directories stay
  disjoint and non-empty, and `bin/` holds nothing test-shaped.
- **`probe-omp-session-accessor.py`?** → Moves too, to a location that never runs in CI
  (`tests/manual/` or similar), so the test-free invariant on `bin/` is exact. #979 may
  rename it when it defines the host kind.
- **Do onboarded projects change?** → No. Their `tests/**` already resolves in their own
  product base, in their own checkout. The template already ships the right layout.
- **Scope** → Migration only. The mutation gate, host kind, fixture provenance and
  measurement mode are #979's, re-planned after this lands.

## Not yet specified

**Both items below were RESOLVED by pm's research on 2026-08-31**
(`features/FEAT-47-tests-layout/notes/research-tests-layout.md`). Kept here with their
answers so the record shows what was fog at grilling time and what closed it.

- ~~The exact unit/integration split criterion per file.~~ **Resolved by measurement, not
  grep.** Two runtime probes — one counting `Popen`/`os.system`/`os.fork`/`posix_spawn`,
  one recording the child's argv head — reassign **10 files, all unit → integration**,
  giving **19/37** against today's 29/27. Grep would have lied both ways:
  `test-factory-gh.py` names `subprocess` 93 times and spawns nothing;
  `test-harness-merge.py` names it zero times and forks 43.
- ~~Whether `bin/fixtures/` and `feature-schema.json` are production or test support.~~
  **Resolved.** `bin/fixtures/` is test support with two consumers, both integration →
  `tests/integration/fixtures/`. `feature-schema.json` is production —
  `feature_schema.py:45` reads it at runtime and `check-domain.sh:1170` names it in a
  write denial. Residue stated at signature: `layout_fixtures.py` is test support that
  stays in `bin/`, so the guard is name-shaped, not purpose-shaped.

## Out of scope

- Everything settled about #979 itself (mutation trigger, proof owner, host-kind gating,
  recording, mutation target). Recorded in the issue and in this session; **not** part of
  this feature.
- Renaming `is_control_plane_target` to say what it means. Considered and declined —
  behaviour-identical, and it touches enforcement-layer code for no functional gain.
- A third "own-product" base for harness. Considered and declined as too much concept
  for one directory.

## Facts I verified (so pm does not re-derive them)

Measured at `ba338d8` unless noted.

- **Two bases.** `harness_boundary.py:501-506` and `select_base`: harness base accepts a
  match only for a control-plane *target* — "that is what stops a `src/**` grant from
  reaching this repository's own `src/`". Product base filters on the glob side instead.
- `is_control_plane_glob('tests/**')` → **False**;
  `is_control_plane_glob('.claude/skills/harness/bin/test-*.py')` → **True**.
  `HARNESS_CONTROL_PLANE` = `.harness/*/docs/**`, `docs/PRINCIPLES.md`, `README.md`,
  `AGENTS.md`, `.agents/**`, `.omp/**`, `.github/**`.
- **Nobody can write a repo-root `tests/` file here today.** Probed on the PreToolUse
  edit route: `backend-dev` BLOCKED, `dev-ops` BLOCKED, `qa` BLOCKED. Creating the
  directories does not change it — it is target-side, not existence-based.
- **Only `harness-qa` carries a `tests/**` glob.** `backend-dev` and `dev-ops` carry
  `.claude/skills/harness/bin/**`, which is how they write tests today — the same grant
  that lets them write gate scripts.
- **What moves** *(CORRECTED 2026-08-31 — figures below re-measured by pm at `ea6f51f`;
  the originals were taken against the stale main checkout at `ba338d8`)*: **56** Python
  tests, 1 TypeScript test (`omp-hooks.test.ts`) plus its two `.jsonl` fixtures resolved
  via `import.meta.dir`, and `probe-omp-session-accessor.py`. **42** non-test `.py`
  helpers stay. The unit/integration split is **not** today's array split: pm's runtime
  probe reassigns 10 files, all unit → integration, giving **19/37** against today's
  29/27. `bin/fixtures/` is test support and travels; `feature-schema.json` is
  production and stays.
- **Live references to `bin/test-` paths: 6**, not 3 *(corrected)* — the three named here
  (`test-code-grade-cli.py`, `test-no-distribution.py`'s `ALLOW_LIST`,
  `.harness/harness.json`) plus `test-check-plan-routes.py` `case_13`,
  `test-check-domain.py:1749-1757`, and `.github/CODEOWNERS:22-27`. The raw grep says
  3219; the rest are historical notes and receipts that must **not** be rewritten.
- **Every moved file is location-dependent** *(added by pm)* — 25 import a `bin` module by
  bare name via `sys.path[0]`, 51 derive paths from `__file__`, none are independent. The
  "~18 depth climbs" figure below understates it; each moved file needs an anchor edit.
- **~18 tests derive repo root from their own depth** (four-level climb from `bin/`);
  16 use a literal four-level `..` chain. All shift with the move.
- **CI is unaffected.** `tests.yml` invokes `run-unit-tests.sh --kind unit|integration`,
  never paths. It installs bun and system python3 plus pyyaml/jsonschema, and references
  **no `secrets.*`**.
- `.agents/skills` is a **symlink** to `.claude/skills` (same inode), so a repo-root
  `tests/` sits outside the skill tree — correct for a project artifact.
- **The template already ships the target layout**: `tests/unit/**`,
  `tests/integration/**`. This repo *appended* `bin/` paths to `unit.detect` and a
  literal file list to `integration.detect`. **No DEC signs the divergence.**
- **`fleet.yaml` deliberately omits `mruangutai/harness` (DEC-174)** — harness develops
  itself in the live checkout and worktrees, both resolving in the harness base.
- Distribution is **gone** (`deploy.sh` removed, gated by `test-no-distribution.py`), so
  "the skill ships with its tests" no longer argues for `bin/`.
- **Execution is main-session-direct.** AGENTS.md's DEC-174 carve-out: harness may plan
  its own enforcement-layer work but must not execute it through the enforcement path
  being changed. This touches `harness_boundary.py`, `run-unit-tests.sh`, `team-config.yaml`
  and `harness.json`.

## For pm

Adding `tests/**` to `HARNESS_CONTROL_PLANE` and widening three domains is an
architecture change: **propose a DEC, approval-gated, user signs.** The migration itself
is verifiable by the suite continuing to pass from its new location — 1049 checks either
run green or they do not.
