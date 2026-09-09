# Research — FEAT-56 · issue #206 re-graded at HEAD

**BLUF: about half of #206 is still live.** Its *diagnosis* holds — `harness-init` is still written to
run inside a product repo and to `cp` templates into it (`SKILL.md:141-147`). Its *table* is not
usable: one of its nine rows names a step that no longer exists (the codebase map, tier retired
2026-08-24, BUILD.md:208), three of its "Dead" grades are wrong at HEAD, and its **replacement item 2
(`.harness/products/<name>/harness.json`) was STRUCK by the operator on 2026-08-18** (#336 body,
"PLACEMENT: IN THE PRODUCT'S OWN REPO", on #493). Its stated "conflict this resolves" (DEC-187
aspirational) was closed by FEAT-24. What survives is the re-homing work #336 put out of scope
("Re-homing the onboarding interview, `dev-ops` detection, domain seeding and the BRIEF … past this
destination") — i.e. #206 is still the only ticket for onboarding, on a changed tree.

All line anchors below are HEAD of `feat/FEAT-56-central-onboarding-model` (cut from `4b5dbb23`).
`.agents/skills/X` and `.claude/skills/X` are ONE file — see item 6, the mechanism is not what the
dispatch says.

## 1. The nine steps, re-graded at HEAD

`SKILL.md` is 370 lines. The nine numbered steps at HEAD are not #206's nine.

| # | Step at HEAD | Lines | Grade | Mechanical reason |
|---|---|---|---|---|
| 1 | Install the eight prerequisites + the per-clone `core.hooksPath` step | 39-140 | **NARROW** | #206 says Dead. **Disagree.** Dead for a *served* product (item 4), but this block is also how the CONTROL-PLANE clone gets installed, and `check-state.sh` grades that clone against it every run: INV-9 (`:844`) on the settings entries, INV-31 (`:2431-2489`) on `core.hooksPath`/`post-merge`. `test-hooks-install.py:265 case_commands_verbatim_in_skill` asserts the step-1/step-2 command strings **verbatim out of `SKILL.md`**. Narrow to "this clone", never delete. |
| 2 | Scaffold `.harness/` from templates (`cp` ×2) | 141-157 | **RE-HOME** (harness.json) / **DELETE** (team-config) | #206 says Dead. **Half wrong.** `team-config.yaml`'s copy is dead: `check-domain.sh:189`/`:331` read `<control-plane>/.harness/team-config.yaml` only. But a product's `harness.json` MUST exist on its default branch or `factory_config.product_config` raises with no fallback (`factory_config.py:279-324`) — so a creation step still exists; only its destination changes (item 5). This is the `cp` #168 was about (`:145-146`). |
| 3 | Interview — technical | 158-165 | **KEEP-AS-IS** | Main-session `AskUserQuestion` + `harness-grilling` (DEC-164). Nothing in it is position-dependent; only where its answers land moves (step 4). |
| 4 | Delegate detection to `dev-ops` (`test_kinds`) | 166-193 | **RE-HOME** | Agrees with #206. Its write target is spelled as the control plane's own file in both agent copies (`.claude/agents/harness-dev-ops.md:53`, `.omp/agents/harness-dev-ops.md:54`); for a product it is that product's `.harness/harness.json` at its `default_branch`. Also DEC-187 closure is now ruled to happen at the first factory run, not at onboarding (#336, salvaged D-03). |
| 5 | Seed the domain manifest (`# SEED` globs) | 194-214 | **NARROW** | #206 says Re-homes. **Disagree — it cannot re-home today.** `team-config.yaml` is ruled forced-global (#346, carried in #336), the live grants are repo-agnostic globs (`.harness/*/features/**`, team-config.yaml:45,108-122) and the source globs are harness's own (`web/src/**` :173, `tests/**` :187,229). `harness_boundary.glob_to_re` supports only `**`, `*`, `?` and literals, so `.harness/${repo}/**` is inexpressible; per-repo isolation is unit 7 / **#495, unbuilt**. Narrow to seeding the control plane's own globs. |
| 6 | Interview — product, then the BRIEF | 215-224 | **RE-HOME** | Agrees. Destination is now `factory_config.features_root()` → `<cp>/.harness/<segment>/features` (`factory_config.py:402-408`), and `plan.yaml` not `PLAN.md` (DEC-182). Measured: `/Users/molchairuangutai/GitHub/harness/.harness/kaya-ai/` **does not exist** (`os.path.isdir` False), matching #498 DC-4 "layout exists, no kaya dir". |
| 7 | Approval gate, + GitHub mirror (`:240`) + board provisioning (`:252`) | 225-295 | **RE-HOME** | The approval write is main-session-only and already repo-scoped (`team-config.yaml:19-34`). The mirror/board writes are now *product config*: `fleet.yaml` REJECTS a board at any level (`fleet.yaml:3-5`) and `board_for` reads it from the product's own `harness.json` (`factory_config.py:327-347`). #206 folds this into "6-7 Re-homes"; at HEAD it is two sub-sections of real size (56 lines) that #206 never saw. |
| 8 | Design pass — UI projects only | 296-304 | **KEEP-AS-IS** | **#206's row 8 is void.** Its row 8 was "Map the codebase :179"; that step is gone — the map tier, both doors, INV-14, INV-20, the spawn injection and the renderer were all retired 2026-08-24 (`BUILD.md:208`; `check-state.sh:1562` "the map precondition went with the map tier"). HEAD's step 8 is the design pass, whose grant is already repo-scoped (`team-config.yaml:131`). |
| 9 | Verify (`check-state.sh`, `merge-settings --check`), then the restart warning | 305-326 | **NARROW** | #206 says "Dead with 1 and 2". **Disagree.** `check-state.sh` requires `.harness/` to exist (`:110-111`) and grades the clone it runs in; there is no product-side state to check. It survives as the control-plane verification, narrowed to that clone. The DEC-100a restart caveat is position-independent. |

Not one of the nine, but in the blast radius: **`--upgrade` (`:327-355`)** — `upgrade-config.py` merges
*a project root's* `harness.json` and refuses to rewrite `team-config.yaml` (`upgrade-config.py:2,187-188,229-230`).
Under the central model its subject is either this clone or a product repo; #206 does not mention it.

## 2. What the central model actually is today (from source)

| Artifact | Lives | Written centrally? |
|---|---|---|
| a product's `harness.json` | **the product repo**, read from the REMOTE at `default_branch`, never from disk, no fallback, memoised per `(repo, ref)` — `factory_config.py:279-324` | no — product-repo-resident |
| fleet declaration | `<cp>/.harness/factory/fleet.yaml`: `repos[].name`, `default_branch`, `workspace_root` only; a board at ANY level is rejected by `load_fleet` (`fleet.yaml:1-19`, `factory_config.py:159`) | central |
| `team-config` policy | `<cp>/.harness/team-config.yaml` **only** — `check-domain.sh:189` and `:331` join `harness_boundary.resolve_root(...)` with it; product paths are classified by `select_base` with control-plane globs filtered out (`harness_boundary.py:376-386`) | central |
| features tree | `<cp>/.harness/<segment>/features` — `factory_config.features_root` (`:402-408`); `<cp>/.harness/harness/features` is that tree for harness itself | central |
| expertise | `<cp>/.harness/expertise/<agent>.md` (craft) + `<cp>/.harness/<segment>/expertise/<agent>.md` (repo tier), globbed by `inject-expertise.sh:64,103-156` | central |
| codebase map | **nowhere — the tier does not exist.** `BUILD.md:208`; no reader in `bin/` (grepped); `<cp>/.harness/harness/codebase/` absent; #498 DC-7 | n/a |

`factory_workspace.py` writes **no** `.harness/` artifact into a checkout — it only prepares the
checkout and refuses on identity/dirty (`factory_workspace.py:1-38`).

**What the central model makes stale in `/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.harness/`:**

- `team-config.yaml` (16.4 KB) — **no reader**: policy resolution never opens a product's copy.
- `expertise/*.md` (14 files) — **never injected**: the injector globs `<cp>/.harness/*/expertise/` only.
- `features/FEAT-01…FEAT-03/` — pre-migration layout; the live path is `<cp>/.harness/kaya-ai/features/`, which does not exist, so these are unreachable by every feature reader.
- `codebase/` (11 files, incl. `map.html` 389.8 KB) — the tier is retired; no reader, no writer, no invariant.
- `.claude/settings.json` — **not the harness eight**: it registers kaya's own hooks (`work-tracking-nudge.sh`, `pre-commit-tests.sh`, `branch-issue-gate.sh`), and `.claude/skills/` does not exist in that checkout at all.
- `harness.json` (13.1 KB) — the *location* is live (read from `master`), but the on-disk copy is never read, and #336 records its content as pre-FEAT-18 stale (flat `project_id`/`status_field`/`in_progress_option`).

## 3. Reachability — every referencing site, with INVALIDATES

`INV = yes` means rewriting `harness-init` falsifies the cited assertion or sentence.

**Executable (a test or gate reads the skill / its behaviour):**

| Site | INV | Assertion at risk |
|---|---|---|
| `tests/integration/test-hooks-install.py:52-53,62-64,265` | **yes** | `case_commands_verbatim_in_skill` opens `SKILL.md` and asserts the literal strings `git config --get core.hooksPath \|\| echo "(unset)"` and `git config core.hooksPath .claude/skills/harness/hooks` are present |
| `tests/integration/test-merge-settings.py:13-14,143-145` | no | comment-level: "`--check` fail[s] a gate harness-init calls HARD"; behaviour unchanged if the gate narrows |
| `tests/integration/test-layout-migration.py:250-254` | **yes** | fixture premise "harness-init installs the whole bin/ into products, so every reader file EXISTS here" — the onboarded-product shape the NOT-APPLICABLE case is built on |
| `tests/integration/test-post-merge-sweep.py:783-785` | no | cites `SKILL.md:73/:78` for relative-`hooksPath`-per-worktree; a line anchor, not an assertion |
| `tests/integration/test-check-state.py:3889-3890` | no | comment premise "a literal compiled into a file that /harness-init copies everywhere" — INV-32's per-project boundary; the *value* stays per-project either way |
| `tests/fixtures/prior-check-domain.sh.fixture:384` | **no — do not touch** | frozen prior-copy of `check-domain.sh`; editing it defeats the fixture |
| `bin/check-instruction-paths.py:12-16` | **yes** | `MAIN_SESSION_ONLY` lists `harness-init`; a rewrite that dispatches it to an agent breaks this classification |
| `bin/check-state.sh:110-111, 286-287, 405-407, 2371-2372, 2431-2436` | **yes** | four user-facing remedies name `/harness-init` (`--upgrade` twice); `:2433` asserts the per-clone step "lives in `.claude/skills/harness-init/SKILL.md`" |
| `bin/check-domain.sh:375-376, 383-384` | **yes** | fail-open message "enforcement OFF (run /harness-init)" — false for a product path once products are governed centrally |
| `bin/upgrade-config.py:2, 187-188, 229-230` | **yes** | docstring "`/harness-init --upgrade`" plus two remedies telling the user to run init in *this project root* |
| `bin/merge-settings.py:35-36, 164-165` | no | comments about prose counts in `SKILL.md` and the HARD-GATE consequence |
| `bin/gh-sync.py:254-255` | **yes** | skip message "run /harness-init --upgrade to record it" (`github.repo` unpinned) — a product's repo pin now lives in the product's config |
| `bin/layout_migration.py:121-125` | **yes** | the APPLICABLE marker's rationale: "harness-init installs the whole bin/ into product repos" |
| `bin/post-merge-sweep.sh:68-69` | no | cites `harness-init SKILL.md:73/:78` as the reason a relative `hooksPath` resolves per-worktree |

**Instructional (routes a session into init):** `.claude/commands/harness.md:12` (**yes** — "BRIEF.md
missing" routes to `/harness-init`); `.claude/commands/harness-plan.md:18` (**yes** — routes when a
project "has no `.harness/` at all", a condition that stops existing); `.claude/commands/harness-grilling.md:7,12`
(**yes** — "the answers seed `harness.json`, the domain description, and the first glossary terms");
`.claude/skills/harness-grilling/SKILL.md:23` (no — one clause); `.claude/agents/harness-dev-ops.md:52-53`
+ `.omp/agents/harness-dev-ops.md:53-54` (**yes** — both name the write target as the control plane's
own `harness.json`; **two separate files**, see item 6); `.claude/agents/harness-visual-designer.md:41`
+ `.omp/agents/harness-visual-designer.md:42` (no).

**Docs:** `README.md:192` (**yes** — "`/harness-init` creates that repository's state");
`.harness/README.md:6,16,17,82` (**yes** — "Written by `/harness-init` … It writes this directory
once"; the `team-config.yaml`/`harness.json` owner rows; "BRIEF.md missing means … run
`/harness-init`"); `.harness/harness/docs/SPEC.md:84,134,144,151,404-405,418-419,450-453,473-474,1353-1354`
(**yes** — §2.2 routing table, §3.3 "instantiated at onboarding time", the five-step interview list);
`.harness/harness/docs/BUILD.md:104,199,369-393,779-780,803-804,814-818,826,839-841,943-944` (**yes** —
task 12's shipped spec, incl. ":388 `/harness-init` writes every project artifact");
`.harness/harness/docs/DECISIONS.md` DEC-13 (`:171-172`), DEC-14 (`:178`), DEC-111 (`:1698`), DEC-112
(`:1732-1734`), DEC-163 (`:3854`), DEC-164 (`:3883`), DEC-171 (`:4171-4172`), DEC-190 (`:5271-5274`),
DEC-194-era (`:5499-5500`) (**yes, by amendment not edit** — DEC-190 cites `SKILL.md:47` (still
correct) and install commands at `:61-65` (now `:112-116`, **already stale**));
`DECISIONS-INDEX.md:29,30,117,118,167,190` (no — index rows, regenerate);
`.agents/skills/harness/references/github-mirror.md:15,18` (**yes** — bounds two read-backs to
"`/harness-init`, and `ship`"); `.harness/harness/docs/org.html:286` (**yes** — owner column
"`/harness-init`" for `team-config.yaml`).

**Templates (enumerated):** `templates/README.md:3,8-12,25,29,35` (**yes** — the whole
Template→Instantiated-to→By table, incl. `BRIEF.md` → the pre-migration `.harness/features/<FEAT>/`);
`templates/harness.json:2` `_template` string and `:167` `github._note` (**yes**);
`templates/team-config.yaml:3` (**yes** — "copies this to `.harness/team-config.yaml`");
`templates/BRIEF.md:1` (**yes**); `templates/DESIGN.md:5-6` (no); `templates/PLAN.md:2` (no —
already superseded by DEC-182). `templates/settings.snippet.json` and `templates/gitignore.snippet`
carry no mention.

**Not in the dispatch's list, found by grep:** `references/github-mirror.md`, `docs/SPEC.md`,
`docs/BUILD.md`, `docs/DECISIONS.md`, `DECISIONS-INDEX.md`, `docs/org.html`,
`tests/fixtures/prior-check-domain.sh.fixture`, `tests/integration/test-check-state.py`, plus ~30
historical `features/**` plans and notes (FEAT-04, FEAT-05, BUG-1071 …) which are **record, not to be
edited** (DEC-188 striking rules). `CLAUDE.md` carries **no** mention.

## 4. The eight prerequisites — CONDITIONALLY LIVE, conditioned on *which clone*

Independently measured (run from `/Users/molchairuangutai/GitHub/harness`):

```
$ .claude/skills/harness/bin/check-domain.sh --resolve \
    /Users/molchairuangutai/GitHub/harness-factories/kaya-ai/src/foo.py
harness-backend-dev            exit=0
$ ... --resolve .../kaya-ai/.harness/harness.json   -> NOBODY   exit=0
$ ... --resolve .../kaya-ai/.harness/team-config.yaml -> NOBODY exit=0
```

And in the kaya checkout: `.claude/skills/` **absent**, `.claude/skills/harness/hooks` **absent**,
`git config --get core.hooksPath` → **exit 1, empty**, `.claude/settings.json` present but holding
kaya's OWN hooks. So the served product is governed today **with none of the eight installed and no
hooks path set**, because the enforcing hooks are registered in the control plane's
`.claude/settings.json` and resolve the control plane's manifest.

- **Installing the eight + `core.hooksPath` into a product repo: DEAD.** Nothing reads them there.
- **Into the control-plane clone: LIVE**, and gated — `check-state.sh` INV-9 (`:844`) and INV-31 (`:2431-2489`).
- **Into a repo a human clones and runs `/harness` inside, outside the workspace: has no mechanism.**
  `deploy.sh` is deleted (#203, DEC-113) and nothing distributes `bin/`, so there is no route by
  which such a clone gets the scripts the eight point at. Treat it as a **question for item 5's
  ruling**, not as a live case.

Tests asserting the install behaviour that must change or be deleted:
`tests/integration/test-hooks-install.py` — `case_commands_verbatim_in_skill`, `case_sc08_before_and_after`,
`case_sc13_idempotence`, `case_sc13_reporting_and_red_proof`, `case_sc14_end_to_end_and_red_proof`;
`tests/integration/test-merge-settings.py` — `case_matchers`, `case_agent_specs`, `case_no_duplicate_write`;
`tests/integration/test-merge-gitignore.py` — `case_preserves_existing_content`, `case_check_complete_is_read_only`,
`case_check_incomplete_reports_missing_and_is_read_only`, `case_absent_target_receives_each_rule_once`,
`case_partial_target_retains_present_rule_and_adds_missing_once`, `case_second_merge_is_byte_identical`,
`case_explicit_project_root_ignores_caller_cwd`; `tests/integration/test-upgrade-config.py` (cases
appended inline into `CASES`, `:51`); `tests/integration/test-check-state.py` —
`case_inv32_era_comes_from_project_config`.

## 5. The open scope question — both branches, no pick

**Branch A — central: `.harness/products/<name>/harness.json` (#206 item 2).** The plan would need:
a new central config reader (or a `product_config` rewrite) replacing the remote read at
`factory_config.py:279-324`; a decision to reverse DEC-174's no-disk-fallback rule; the `.harness/products/`
level added to `is_control_plane_glob`'s reasoning and to the write grants (no agent holds that path
today — `--resolve` on `templates/harness.json` and on `fleet.yaml` both return NOBODY, so a
main-session lane); migration of kaya's `harness.json` off `master` into the control plane, with the
old copy struck so two records cannot disagree; and a reversal record against the operator's
2026-08-18 ruling on #493, which struck exactly this placement (#336 body). **It also reopens what
#336 recorded as FORCED:** `repos[].name` and `workspace_root` cannot move, because
`resolve_fleet` computes a base for every declared repo including uncloned ones.

**Branch B — product-resident (DEC-174, as built).** The plan would need: a step that **commits** a
product's `harness.json` to its default branch (a PR/push against the product repo — a write route
onboarding does not have today, since `factory_workspace.py` writes no artifact and no agent domain
covers a product's `.harness/`); a decision on what happens between fleet registration and that
first commit, when `product_config` raises rather than defaulting; where the interview's answers are
staged meanwhile; and `--upgrade`'s subject (this clone, a product repo, or both). The template
`harness.json` stays the schema source, but its `_template` line and `templates/README.md`'s
destination column both become wrong as written.

**Shared by both branches, whichever wins:** items 1/5/9's narrowing, the `team-config` copy's
deletion, the features/BRIEF destination move to `features_root()`, and the item-3 doc sweep.

Nothing above picks a branch. **The one fact the advisor should weigh:** the tree records a signed
operator ruling for B and a struck ruling for A (#336 body, 2026-08-18), which is evidence, not a
decision — and #206 has not been amended since 2026-08-10.

## 6. Risk register

1. **The `.claude` / `.agents` link is a SYMLINK, not a hardlink — the dispatch's premise is wrong.**
   Measured: `os.path.islink('.agents/skills')` → `True`, target `../.claude/skills`;
   `st_nlink` of `harness-init/SKILL.md` is **1** (a hardlink would be ≥2). Consequence flips: a
   whole-file `Write` through either prefix is **safe** and cannot desynchronize the trees. (Inode
   178989343 is the *main* checkout's; this worktree's is 221227775 — a per-checkout file either way.)
2. **The mechanism has a name, and it is `bin/check-omp-port.py`.** `:126-133` asserts
   `.claude/skills` is the real directory and **`.agents/skills` must be a symlink to it**, and
   `:156-166` runs `bin/sync-agent-adapters.py --check`. Verified: `python3 check-omp-port.py` →
   `OMP port surface: ok`. Its test is `tests/integration/test-check-omp-port.py`.
3. **Agent files are NOT linked and DO differ.** `.omp/agents/harness-dev-ops.md` (inode 199528265)
   and `.claude/agents/harness-dev-ops.md` (199528179) are distinct files and `diff -q` reports them
   **different** (adapter format). Both mention `/harness-init`. Editing one and not regenerating via
   `sync-agent-adapters.py` fails `check-omp-port.py` — this is the real desync risk, in the agent
   tree, not the skill tree.
4. **No writer owns the skill.** `--resolve` on `.claude/skills/harness-init/SKILL.md` → `NOBODY`
   (exit 0), as on `fleet.yaml` and `templates/harness.json`. Every one of those edits is a declared
   main-session step; a task routed to `dev-ops` will stall (the FEAT-05 routing wall, third
   recurrence, `FEAT-05/PLAN.md:1047-1062`).
5. **Migration of the served checkout is unowned work.** `<cp>/.harness/kaya-ai/` does not exist;
   kaya's four stale `.harness/` subtrees (item 2) sit in a repo no harness domain grants. Deleting
   them is a write into a product repo, which is the same missing route as branch B's commit step.
6. **`harness_boundary.MARKER` is `.harness/team-config.yaml`** (`harness_boundary.py:54`), and
   `root_above` uses it to decide "which checkout is this path in". Kaya's stale copy is therefore
   not purely inert — removing it changes what `root_above` answers inside that checkout. Any task
   that deletes it must state which resolution paths depend on the marker.
7. **Doc drift is already present and will be blamed on this feature.** DEC-190's `:61-65` anchor is
   stale (install commands are at `:112-116`); `templates/README.md:11` still names the pre-migration
   `.harness/features/<FEAT>/`; `harness-brief/SKILL.md:95` still cites the retired INV-20. Fix these
   in the same pass or a reviewer will read them as regressions.
8. **Line-anchored citations into `SKILL.md` rot on the first edit** — `test-post-merge-sweep.py:784`
   and `post-merge-sweep.sh:69` both cite `SKILL.md:73/:78`. Prefer re-anchoring them to a stable
   heading over re-numbering.

## Open questions

- **Q1 (blocking):** branch A or B (item 5). Held for the concurrent advisor ruling.
- **Q2 (non-blocking):** does the "human clones a repo and runs `/harness` inside it" case survive at
  all, given `deploy.sh` is deleted and nothing distributes `bin/`? If not, `harness-init`'s
  `--upgrade` path and step 1 lose their last non-control-plane subject.
- **Q3 (non-blocking):** who deletes kaya's four stale `.harness/` subtrees, and by what write route
  into a product repo? No agent domain covers it today.
