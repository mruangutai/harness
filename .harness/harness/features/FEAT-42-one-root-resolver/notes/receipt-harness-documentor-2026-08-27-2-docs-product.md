# Receipt — harness-documentor — FEAT-42 docs falsification sweep

**Analysis only. No documentation was edited.** Every candidate surface resolved `NOBODY`, and the
remaining stale prose lives inside DEC-174 enforcement-layer files. This receipt is the only write.

**BLUF — 12 findings.** The worst is `.claude/skills/harness-brief/SKILL.md:131`: it is a *naming
authority* that tells every brief author to spell the root `harness_root`, and at 9d12e3a the only
surviving occurrence of that identifier in the whole `bin/` tree is inside
`test-no-distribution.py:363`'s `DELETED_NAMES` tuple. It teaches a deleted name as the canonical one.
**No live code calls a deleted symbol** — no bug to escalate; every hit below is prose.

Ground truth read first: `.claude/skills/harness/bin/harness_boundary.py` — `MARKER` (`:41`),
`root_from_script` (`:44`), `resolve_root` (`:53`, reads `HARNESS_PROJECT_DIR` only, `:65`),
`root_above` (`:84`).

## Findings, worst first

**F1 · `.claude/skills/harness-brief/SKILL.md:131`** — the Do/Do-not naming table's Do column reads
``| `owner_root`, `workspace_root`, `harness_root` | ...``. **Truth:** `harness_root` no longer names
anything; `grep -rnw harness_root` across `bin/` returns exactly one line, `test-no-distribution.py:363`,
where it is listed as deleted. `owner_root` and `workspace_root` are still live
(`feature-worktree.py:56`, `resolve_fleet` → `fleet["workspace_root"]`). The skill's own rule two
paragraphs up is "before writing a path or identifier, grep for it" — so a brief author who obeys the
table without obeying the rule ships a deleted name into a spec agents build from. **Owner:** whoever
holds `.claude/skills/harness-brief/` (resolved `NOBODY` for me). Replacement spelling is
`harness_boundary.resolve_root` / the root it returns.

**F2 · `.harness/harness/docs/SPEC.md:2270`** — "the literal `harness` for this repository
(`owner_root` = `factory_config.harness_root()`, default branch `main`)". **Truth:**
`feature-worktree.py:64-68` — `resolve_repo("harness")` returns
`harness_boundary.resolve_root(_BIN_DIR), "harness", "main"`. `factory_config.harness_root` is gone
(T-04). **On the half-updated question — no.** SPEC.md:2276 cites
`harness_boundary.WORKTREES_SEGMENT`, but that constant predates FEAT-42 (it is FEAT-17/DEC-143 work,
`harness_boundary.py:33`), so 2276 is old-and-still-correct rather than a partial FEAT-42 edit. The
paragraph was never touched by this feature; one clause in it simply went false.
**Owner:** main session / doc owner of `.harness/harness/docs/**`.

**F3 · `.claude/skills/harness/bin/check-state.sh:1143`** — "`root` is CLAUDE_PROJECT_DIR or the cwd".
**Truth:** `check-state.sh:38` sets `root` from `harness_boundary.resolve_root(_selfdir)` and refuses
with exit 2 when it cannot resolve (`:39-40`); the file's own header at `:21-25` says so explicitly.
The comment survives *directly beneath* prose stating the opposite. The reasoning it carries (why the
base must come from the first porcelain entry, not `<root>/.claude/worktrees/`) is still sound — only
its premise is dead. **Owner:** DEC-174 carve-out — main-session-direct.

**F4 · `.claude/skills/harness/bin/check-plan-routes.py:475-478`** — "Root precedence follows
check-domain.sh (`:178-180` … `:276-281`) … CLAUDE_PROJECT_DIR if it holds a readable manifest, else
the root DERIVED from this file's location". **Truth:** both files now call
`harness_boundary.resolve_root`; the read name is `HARNESS_PROJECT_DIR` and the probe is
`MARKER` = `.harness/team-config.yaml`. The cited `check-domain.sh` line anchors no longer point at
any root-resolution code. **Owner:** DEC-174 carve-out.

**F5 · `.claude/skills/harness/bin/test-check-plan-routes.py:1133-1136`** — "check-state.sh is a NAMED
EXCEPTION … it has no derived fallback at all — `cd "$root"` with an invalid CLAUDE_PROJECT_DIR fails
and it silently reports on the cwd. That is a real defect". **Truth:** that defect is fixed
(`check-state.sh:38` resolves via `harness_boundary`, `:39-43` refuses with `exit 2`). This is the most *actionable* stale prose in the sweep: it
is a live docstring asserting a live defect, sitting on an assertion that still exempts
`check-state.sh` from the shared-probe check — so the one file the exemption was written for is now
the one file that would pass it. **Recommendation:** delete the exemption and the paragraph together;
do not edit one without the other. **Owner:** DEC-174 carve-out.

**F6 · `.claude/skills/harness/bin/test-dispatch-guard.py:365` and `:381`** — the docstring says "with
no cwd in its payload the root falls back to CLAUDE_PROJECT_DIR -- the real checkout", and `:381`
implements the run-wide fix as `os.environ["CLAUDE_PROJECT_DIR"] = _iso`. **Truth:**
`dispatch-guard.sh:141` calls `hb.resolve_root(HARNESS_GUARD_BIN_DIR or os.getcwd(), strict=False)`,
which reads `HARNESS_PROJECT_DIR` only — so that assignment is **inert**. Not a live leak today:
`case_2_governed_agent_no_model` (`:68-82`) sets both names on its own `fire(env=...)`. But the
run-wide safety net described in a 15-line docstring no longer exists, and the next case added
without its own `env=` will leak a claim into the live registry exactly as narrated. **Owner:**
DEC-174 carve-out (`dispatch-guard.sh`'s test).

**F7 · `.github/workflows/tests.yml:188` and `:251`** — the two `::error::` messages tell a CI
debugger to "Check CLAUDE_PROJECT_DIR and .harness/*/features/" / "…and the feature/doc roots".
**Truth:** `check-plan-routes.py` and `layout_migration.py` both resolve through
`harness_boundary`; `CLAUDE_PROJECT_DIR` cannot affect either. Error text is documentation a reader
acts on under time pressure, and this sends them to an inert variable. **Owner:** whoever holds
`.github/**`.

**F8 · `.github/workflows/tests.yml:85, 91, 100, 150, 210`** — five steps set
`CLAUDE_PROJECT_DIR: ${{ github.workspace }}` and the file sets `HARNESS_PROJECT_DIR` **nowhere**
(verified: `grep -n HARNESS_PROJECT_DIR` returns nothing). **Truth:** for the cut-over gate scripts
these env blocks are no-ops. CI is not broken — the derived root already equals `github.workspace` —
but the config *reads* as the thing pinning the root, and the next person who changes the checkout
path will trust it. Configuration-as-documentation defect, not a failure. **Owner:** `.github/**`.

**F9 · `.claude/skills/harness/bin/validate-digest.py:815`** — "a hook whose cwd drifts (worktrees,
unset CLAUDE_PROJECT_DIR) must not block a legitimate lead on our own resolution bug". **Truth:** the
named cause is retired; the fail-open-loudly posture it justifies is correct and unchanged. Lowest
harm of the four seeded leads — the rule survives its rationale. **Owner:** DEC-174 carve-out.

**F10 · `.claude/skills/harness/bin/test-check-state.py:3-4`** (module docstring) — "check-state.sh
is run with CLAUDE_PROJECT_DIR pointed at each". **Truth:** the file's own `_env` helper (`:66-67`)
sets **both** names and writes `MARKER` into the fixture, and its docstring there explains that
without the marker every case scanned the live repository. The module docstring contradicts the
helper 60 lines below it. A new case written from the module docstring alone silently scans the live
repo. **Owner:** DEC-174 carve-out.

**F11 · `.claude/skills/harness/bin/test-harness-yaml.py:20-22`** — "CLAUDE_PROJECT_DIR overrides when
the caller has already resolved it (run-unit-tests.sh does)". **Truth:** `run-unit-tests.sh` contains
no occurrence of `PROJECT_DIR` at all (verified). The parenthetical was already false before this
feature; FEAT-42 makes the whole sentence false. The same two-name `REPO_ROOT` chain survives in five
test harnesses — `test-harness-yaml.py:22`, `test-harness-yaml-corpus.py:59`,
`test-validate-feature-json.py:21`, `test-run-unit-tests-kinds.py:26`, `test-team-catalog.py:41` —
which is legal (SC-01 excludes `test-*`) but means the retired chain is still *live code* in test
scaffolding while doctrine says it is retired. **Owner:** DEC-174 carve-out for the gate tests;
`test-team-catalog.py` / `test-harness-yaml-corpus.py` are not on the amendment-4 list.

**F12 · `.harness/harness/docs/SPEC.md:2270`, the citation `(`resolve_repo`, `:62-85`)`** — **Truth:**
`resolve_repo` is at `feature-worktree.py:64-87` at 9d12e3a; FEAT-42's deletion shifted it two lines.
Low harm (the range still overlaps the function), reported because SPEC anchors are cited by line and
nothing checks them. Contrast `dest_for`, `:56-59` in the same paragraph, which is still exact.

## Not defects — checked and cleared

- `.claude/settings.json` and `templates/settings.snippet.json` `${CLAUDE_PROJECT_DIR}/...` command
  strings: host-owned shell expansion of the hook *path*, unrelated to the retired resolver chain.
  Still correct. Same for `SPEC.md:657` and `BUILD.md:44/49/54/405/408/411`.
- `check-domain.sh:1142` and `feature_schema.py:78` — "this module is imported through
  CLAUDE_PROJECT_DIR — the main checkout". Still **true**: the hook script is still launched by the
  host through that expansion, so `sys.path` still points at the main checkout. Matches the grep,
  is not a finding.
- `test-check-domain.py:22-36` and `test-bash-write-guard.py:22-35` — accurate at 9d12e3a and
  self-dating ("the reverted sha-3952814 copy this suite is diffed against"). Model entries.
- `SPEC.md:685-687` — "derives the project root from its own location, not from `pwd`" — more true
  now than when written.
- Frozen record (`features/*/BRIEF.md|PLAN.md|plan.yaml|notes/|observations/`, `.harness/logs/`,
  `.harness/notes/`, `DECISIONS.md` entries): historical-and-correct. Not inspected for defects and
  must not be edited (PRINCIPLES rule 15).

## Expertise — graded, not fixed. Two tiers, three files, be exact about which.

- **`.harness/harness/expertise/harness-dev-ops.md:8` (G-05, repository tier — the harness repo).**
  Worst of the three. It instructs the persona to *expect* `factory_config.harness_root()` to
  silently fall back when `CLAUDE_PROJECT_DIR` points at a tempdir lacking `SPEC.md`. Three separate
  falsehoods now: the function is deleted, the env name is inert, and the probe is `team-config.yaml`
  not `SPEC.md`. **How a spawn goes wrong concretely:** a dev-ops agent building a benchmark fixture
  sets `CLAUDE_PROJECT_DIR=$tmp`, writes `$tmp/.harness/SPEC.md` to satisfy the probe the entry
  names, asserts the resolved root, sees the *live checkout* returned, and concludes its harness is
  broken — because the entry told it the correct probe file and the correct variable, and both are
  wrong. The entry's advice ("assert the resolved root before any write") remains right; its entire
  mechanism is wrong.
- **`.harness/harness/expertise/harness-backend-dev.md:5` (G-02, repository tier).** Same dead
  function, framed as an active hazard: "`factory_config.harness_root()`'s `CLAUDE_PROJECT_DIR`
  fallback routes pre-existing tests into the real `.harness/logs/`". **How a spawn goes wrong:** a
  backend dev adding always-on instrumentation greps `factory_config` for `harness_root`, finds
  nothing, and either concludes the hazard is gone (it is not — an unmarked override is *discarded*
  and resolution falls through to the derived root, `harness_boundary.py:69-75`, which is the same
  write-into-the-real-tree outcome by a different route) or spends a run re-deriving it. Misleading
  in the direction of *false safety*, which is worse than F1's false name.
- **`.harness/expertise/harness-dev-ops.md:30` (G-14, craft tier — the same persona, the other
  file).** Mildest. It says "an env-var-redirected root (e.g. CLAUDE_PROJECT_DIR)" — the example is
  now wrong, the rule ("assert the resolved root equals the intended temp path before the first
  write") is exactly right and is *more* necessary after this feature, because an unmarked override
  is now discarded silently rather than honoured. Fix is one parenthetical.

**Flagged for the feature-close distillation.** Not written here — Expertise is written only under a
distillation dispatch.

## DEC-174 amendment 4 — reported, not edited

`.harness/harness/docs/DECISIONS.md:5006-5008` (the "So the enforcement layer is:" sentence, in
amendment 4 which opens at `:4983`) enumerates: `check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh`, **and the test
file of each** — 12 files.

**Accuracy at 9d12e3a: all 12 exist under those exact names.** No renames, no deletions. Verified by
`test -f` on each. FEAT-42 changed files on this list and added none to it — correct as far as it goes.

**But the list is incomplete against its own category** ("hooks, validators, gate scripts"), and the
amendment itself says a script joins the day it becomes a gate:

- **Registered hooks absent from the list** (`.claude/settings.json:12, 32, 40, 64`):
  `inject-expertise.sh`, `branch-create-gate.sh`, `gh-close-gate.sh`, `context-watch-hook.py`. Each
  fires on every session or every tool call; `gh-close-gate.sh` and `branch-create-gate.sh` *refuse*
  actions, which is the same evidence on which `dispatch-guard.sh` joined.
- **CI gate steps absent from the list** (`.github/workflows/tests.yml`): `validate-feature-json.py`,
  `layout_migration.py`. `check-plan-routes.py` joined on precisely the DEC-183-made-it-a-CI-step
  argument; these two are steps of the same required job.
- **`harness_boundary.py` and `test-no-distribution.py`.** Amendment 4 already rules on this shape —
  "a module a gate imports is not itself a gate … the cutover that makes a gate use it is
  main-session-direct". FEAT-42 is the first feature where *one* module is imported by every file on
  the list, so a squad-authored change to `harness_boundary.py` reaches all six gates at once without
  touching any of them. That is a question for the operator, not a documentation fix.

**Not edited. A decision is the operator's.**

## SC-01 — the invariant's blind spot, confirmed by reading it

`test-no-distribution.py:358`: `CHAIN_NAME = "HARNESS" + "_PROJECT_DIR"`. **It greps for the
SURVIVING name, not the retired one** — the absence half asserts that no non-test, non-resolver source
file names `HARNESS_PROJECT_DIR`, i.e. "only the resolver reads the environment". Coherent, and
narrower than "the chain is gone".

Its scan set (`:368-373`) excludes: any basename starting `test-`, `harness_boundary.py`, anything
ending `.md`, and the prefixes `.harness/logs/`, `.harness/notes/`, `.harness/harness/features/`
(`:93`). So it **structurally cannot see** F1, F2, F5, F6, F9, F10, F11, F12 — and cannot see
`CLAUDE_PROJECT_DIR` anywhere at all. The dispatch's reading is correct.

**Recommendation (not an edit), one assertion, cheapest useful shape:**

> Add `case6_absence_the_retired_name_in_live_doctrine`: over `git ls-files`, restricted to
> `.claude/skills/**/SKILL.md`, `.claude/commands/*.md`, `.harness/harness/docs/SPEC.md`,
> `.harness/harness/docs/BUILD.md`, `.harness/README.md`, `AGENTS.md`, `docs/PRINCIPLES.md` and
> `.github/workflows/*.yml` — and explicitly NOT the record prefixes at `:93` — fail on any line
> matching `\bCLAUDE_PROJECT_DIR\b` that is not inside a `${CLAUDE_PROJECT_DIR}/` hook-command
> substitution, and on any line matching `\bharness_root\b`. Allow-list by exact path, declared, so a
> new site fails rather than being absorbed — the same discipline `ALLOW_LIST` at `:98` already uses.

That one assertion would have caught F1, F2, F7 and F8 at build time. It would still miss F3–F6 and
F9–F11, which live in `test-*` and gate scripts; catching those needs the exclusion at `:369` relaxed
for comments only, which is a bigger change and is not recommended here.

## Open questions

- **Q1 (non-blocking):** who owns `.claude/skills/harness-brief/SKILL.md`? `--resolve` returned
  `NOBODY`, and F1 is the highest-harm finding.
- **Q2 (non-blocking):** should F5's `check-state.sh` exemption in `test-check-plan-routes.py` be
  deleted now that the defect it names is fixed? That is a gate-behaviour change, DEC-174.
