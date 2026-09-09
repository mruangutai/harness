# Review C2 — code review at review_sha cf8a9e4c

**Headline: FAIL — one gated test function is code-grade 1 (blocks build per code-risk-grading);
spec compliance (SC-03, SC-04, the split read-through, T-10/T-11 exclusions) is clean.**

Note on the pin: the dispatch named `9768681c`, but `feature.json`'s own `review_sha` field is
`cf8a9e4c0aaad87901e5cc68443aa011513ff00c`, and `9768681c` is one commit later
("re-pin past the station write"). `git diff --stat cf8a9e4c 9768681c` touches only `feature.json`
itself (a station bookkeeping write) — no source, doc, test, or skill file differs between the two
commits. Every `git show <sha>:<path>` read below was taken at `9768681c` but is byte-identical to
the same read at `cf8a9e4c` for every file in this review's scope; the code-grade numbers were
re-run directly against `cf8a9e4c` and match exactly (reported below). All findings and citations
are unaffected by the correction; only the recorded range changes.

All reads done via `git show <sha>:<path>` (per instruction). Diff range `4b5dbb23..cf8a9e4c`
(`4b5dbb23` = `git merge-base origin/main cf8a9e4c`, confirmed).

## Stage 1 — Spec compliance

### SC-03 — six executable sites: **MET**

- `bin/check-instruction-paths.py:18` — `MAIN_SESSION_ONLY` lists `harness-add-repo` (with
  `harness-init` at :17, rationale-commented for the anchor-rule exemption). Names both artifacts
  correctly.
- `bin/check-state.sh` — all FOUR `/harness-init` remedies graded, none registration-scoped:
  `:111` ("no `.harness/` here ... Run `/harness-init` in the control-plane clone"),
  `:287` (".harness/harness.json missing — not onboarded ... Run `/harness-init`, in this clone"),
  `:408` ("Run `/harness-init --upgrade`"), `:2375` ("`/harness-init --upgrade` to decide the
  Issues mirror once"). All four are checkout-configuration or `--upgrade` conditions.
- `bin/check-domain.sh:384-386` — fail-open message: "That path is the control plane's own
  manifest; a product repository never carries one. Run `/harness-init` in the control-plane
  clone." States the central model and names the right artifact.
- `bin/upgrade-config.py:2-6` (docstring) + `:192`, `:236` (remedies) — docstring states the
  central model ("upgrades the control-plane clone's own harness.json ... For a fleet member ...
  committed to the repository's default branch"); both remedies say `/harness-init`, correctly,
  because this script is only ever invoked against the control-plane's own config (confirmed:
  neither `harness-add-repo/SKILL.md` nor `harness-init/SKILL.md` calls `upgrade-config.py` from a
  fleet-member context).
- `bin/gh-sync.py:255` — skip message states the central model correctly ("for a fleet member,
  that file lives in the member's own repository on its default branch") but does **not** name
  `harness-add-repo` as the artifact that lands it — unlike the other five sites, which all name
  an artifact explicitly. Low-severity observation (below), not treated as a miss for SC-03's
  verdict since the model statement itself is accurate and no false claim is made.
- `bin/layout_migration.py:119-127` — `MARKER` rationale states the central model at length ("The
  fleet declaration is the one file only the control plane carries: products are DECLARED IN it,
  never holders OF it"). No remedy to name an artifact for; MET.

### SC-04 — ~23 files (union of task `files:`): **MET**

All 23 files checked one at a time at the pin (commands ×4, `harness-grilling/SKILL.md`,
templates ×6, `references/github-mirror.md`, docs ×5, `README.md`, `.harness/README.md`, agents
×4). Every occurrence of onboarding language names the correct artifact:
`.claude/commands/harness.md:14-18` (router splits the four stale conditions correctly between
`harness-init` and `harness-add-repo`), `harness-plan.md:18` and `harness-grilling.md:7/:13` now
route to `/harness-plan`, `harness-grilling/SKILL.md:23`, `templates/README.md:3,8-12,21,25,35`,
`templates/harness.json:2,166`, `templates/team-config.yaml:3` (correctly **keeps** `harness-init`
— its one deliberate non-move, T-12's verify asserts this), `templates/BRIEF.md:1`,
`PLAN.md:2`, `DESIGN.md:6` (all now `/harness-plan`, none mention `harness-init`),
`references/github-mirror.md:15,18,23`, `SPEC.md:134-155,409-489,1369`,
`BUILD.md:106,202,372-403,795,959-960`, `DECISIONS.md:7023` (DEC-221 entry, states all four
required elements), `DECISIONS-INDEX.md:221`, `org.html:286,328-329`, `README.md:192`,
`.harness/README.md:6-19,86-87`, `.omp/agents/harness-dev-ops.md:53-55` and
`.claude/agents/harness-dev-ops.md:52-54` (both name `harness-init` bare, never `/harness-init`,
and both name `harness-add-repo`), `.omp/agents/harness-visual-designer.md:42` and
`.claude/agents/harness-visual-designer.md:41` (routed to `/harness-plan`, no mention of
`harness-init` at all — the file's sole prior occurrence is gone). No partial or missing citation.

### B. Split read-through (pre-split `12f74ea8:.claude/skills/harness-init/SKILL.md`, 434 lines,
read straight through against both current skills at the pin)

**Census: 0 orphans, 0 unintended duplicates.** Every unit in the pre-split file has an accounted
disposition:

| Unit | Disposition |
|---|---|
| Frontmatter | rewritten independently in both files |
| 3-things intro paragraph, one-file rule (:8-17) | moved to `harness-add-repo` |
| "This harness checkout" definition (:19-20) | stays `harness-init` only |
| Main-session note (:22-23) | duplicated, legitimately (both run in main session) |
| Grilling note (:25-28) | **split**: control-plane clause stays `harness-init`, registration clause moves to `harness-add-repo`, verified no cross-contamination (grep below) |
| Preflight (:30-46) | stays `harness-init`, minus `claude --version` + CLI-floor bullet (D-12); `harness-add-repo` gets an entirely new 5-item registration preflight |
| Track A/B headings (:48, :239-243) | deleted, both |
| Step 1 prereqs (:53-160) | stays `harness-init` step 1, two dangling refs reworded (`:65→"before you go on"`, `:83→"Do not skip the hooks configuration"`) |
| Step 5 seed manifest (:161-184) | stays `harness-init`, renumbered step 5 |
| Step 9 verify+restart (:185-208) | stays `harness-init` renumbered step 6; "brief is pending (step 7)" clause **deleted** (not reworded — correct, D-09 removed the referent) |
| `--upgrade` (:209-238) | stays `harness-init`, fleet-member clause repointed to name `harness-add-repo` (not "step 2") |
| Step 2 land+register (:245-278) | moved to `harness-add-repo` step 1, ordering `default_branch` < `factory/fleet.yaml` < segment path confirmed |
| Split sentence pair (:279-282) | first sentence ("no team-config anywhere but...") → `harness-add-repo` only (grepped, present at `:78`, absent from `harness-init`); second sentence ("instantiate its own...") → `harness-init` step 2 only (grepped, absent from `harness-add-repo`) |
| Step 3 interview (:284-291) | **deliberately present in both** — `harness-init` step 3 (control-plane's own project type, UI clause reworded per D-09) and `harness-add-repo` step 2 (fleet member's); not a defect, both artifacts configure a distinct project's `harness.json` |
| Step 4 dev-ops detection (:292-323) | `harness-init` step 4 keeps the full 8-bullet contract, restricted to the control-plane half only (fleet-member half of bullet 1 removed, confirmed absent); `harness-add-repo` step 2 references it by name ("follows the same dev-ops contract as harness-init's ... section") rather than re-copying it — this is the case that could have been a verbatim duplicate and was not |
| Steps 6/7/8 (BRIEF, approval, design) | deleted from both, per D-09, confirmed absent |
| GitHub mirror + board subsections | moved to `harness-add-repo` step 3 |
| Red flags table (12 rows) | **7 rows** → `harness-init` (prereq-install, script-denied, must-restart, no-evals, agent-blocked, team-config, can-run-a-team); **3 rows** → `harness-add-repo` (dev-ops-cmd-reason, npm-test, repo-in-fleet.yaml); **2 rows** dropped from both (describing≠approving, check-state-pending) — all 12 accounted, confirmed by direct read of both tables |

Grep-confirmed no banned phrase crossed into the wrong file (`instantiate its own`, `into the
control plane's`, `claude --version`, `2.1.217`, `Design pass`, `harness-visual-designer`, `The
approval gate`, `then the BRIEF` all absent from `harness-init`; only the one intended phrase
`anywhere but the control plane` appears in `harness-add-repo`, none of the others).

### C. T-10/T-11 exclusion cross-check: all three honoured bidirectionally

1. Control-plane team-config sentence (:280-282) — IN `harness-init` (step 2), OUT of
   `harness-add-repo` (confirmed absent).
2. Control-plane half of detection bullet (:296-298) — IN `harness-init` step 4 ("into the control
   plane's `.harness/harness.json`", fleet-member half removed), OUT of `harness-add-repo` (which
   instead carries only the fleet-member destination, "the fleet member's own harness.json ...
   lands that file through step 1").
3. Control-plane clause of grilling note (:25-28) — IN `harness-init` ("seed the control plane's
   domain description and first `.harness/glossary.md` terms"), OUT of `harness-add-repo`
   ("seed the repository's own `harness.json`" only).

No hole in either direction.

## Stage 2 — Code quality

### Code-risk grading (`code-grade.py --base 4b5dbb23 --head cf8a9e4c`, matches the earlier
`--head 9768681c` run exactly — expected, since no graded file differs between the two)

| File:line | Qualname | Cyclo | Cog | ABC | Grade | Bar | Result |
|---|---|---:|---:|---:|---:|---:|---|
| `factory_config.py:328` | `product_config_report` | 3 | 3 | 9.7 | 4 | 4 | PASS |
| `factory_config.py:448` | `_check_product_configs` | 8 | 7 | 15.3 | 4 | 4 | PASS |
| `sync-command-adapters.py:18` | `canonical_paths` | 3 | 0 | 4.6 | 5 | 4 | PASS |
| `sync-command-adapters.py:24` | `expected_adapters` | 2 | 1 | 3.7 | 5 | 4 | PASS |
| `sync-command-adapters.py:31` | `sync` | 10 | 15 | 27.9 | **2** | 4 | **FAIL** |
| `sync-command-adapters.py:59` | `main` | 2 | 1 | 12.1 | 4 | 4 | PASS |
| `tests/integration/test-sync-command-adapters.py:46` | `main` | 1 | 1 | **50.2** | **1** | 3 | **FAIL** |
| `tests/unit/test-no-distribution.py:66` | `case1` | 9 | 2 | 30.5 | **2** | 3 | **FAIL** |
| `tests/integration/test-onboarding-split.py` (11 functions) | — | — | — | — | 4-5 | 3 | all PASS |
| `tests/integration/test-check-omp-port.py` | — | no graded record in this diff (unchanged/unworsened) | | | | | |

`code_grade: fail` — one gated function (`test-sync-command-adapters.py:46`) is **grade 1**, which
blocks the build regardless of file kind ("grade 1 anywhere" per `harness-code-risk-grading`).

**MUST_FIX — HIGH — `tests/integration/test-sync-command-adapters.py:46` `main()` — code grade 1**
(T-14). Cyclomatic 1 / cognitive 1 but ABC 50.2 — a single 60-line function running five
sequential `tempfile.TemporaryDirectory()` blocks, each doing setup + subprocess call + 2-3
`check()` assertions (12 checks total), with no per-case decomposition. Concrete cost: a future
6th case (there will be one — SC-13/REQ-10 is exactly the surface most likely to grow a case) has
no natural extension point and will only add to this one function's ABC, and the file's own sibling
convention (`test-sync-agent-adapters.py`, `tests/integration/test-onboarding-split.py`'s
`case_*()` pattern used a few files over) demonstrates the alternative: one function per case. This
gates the review per `harness-code-risk-grading` ("below its bar and not grade 2 ... blocks the
build"). Writability: `tests/**` is squad-writable.

**MED — `sync-command-adapters.py:31` `sync()` — code grade 2** (T-14). REASON REQUIRED: the
function combines four responsibilities sharing local state (`drift`, `check`) — compute expected
adapters, compute actual adapter names, reconcile+write/report for the expected set, reconcile
orphans for the actual-only set. Grade 2 does not block the build; flagged with the required
reason. Writability: squad-writable (`.claude/skills/harness/bin/**`).

**MED — `tests/unit/test-no-distribution.py:66` `case1()` — code grade 2** (T-17). REASON
REQUIRED: seven independent `check()` calls in one straight-line body (cyclomatic 9 from list
comprehensions and boolean conditions, not real branching — cognitive is only 2). It is a checklist
function, not an algorithm; splitting it into seven single-assertion functions would add navigation
cost disproportionate to its review difficulty. Grade 2 does not block the build; flagged with the
required reason. Writability: squad-writable.

### Fail-open hunt

**MED — `sync-command-adapters.py` `sync()` (T-14) — `--check` is vacuously green when a
canonical door is deleted together with its adapter.** Traced: `canonical_paths()` builds its
result set entirely from what currently exists under `.omp/commands/` (`{canonical_dir /
"harness.md"}` filtered by `.is_file()`, plus a `glob()` that silently returns `[]` against a
missing directory — confirmed with a live interpreter test, no exception). `expected_adapters()`
therefore only ever describes files that exist; the tool detects **drift between two present
sets**, never the **absence of an expected set member**. Concrete scenario: delete
`.omp/commands/harness-ship.md` and `.claude/commands/harness-ship.md` together (or wipe both
directories), and `sync-command-adapters.py --check` reports `0 drift`, exit 0 — a false-clean
signal for a door that no longer exists under either provider, which is precisely the state REQ-10
exists to catch. SC-13's first clause grades this script standalone ("`sync-command-adapters.py
--check` exits 0" is one of its four independent assertions), so an operator or reviewer running
just that command gets a false "OK". **Mitigated, not closed, by `check-omp-port.py`'s own
door-existence loop** (`:169-171`, asserts each of the four names exists at `.omp/commands/NAME.md`
directly, independent of adapter state) — I confirmed `test-check-omp-port.py:156-163` builds
exactly this fixture (`shutil.rmtree(root/".omp"/"commands")`) and asserts all four are reported
missing, so the composite gate (`check()` in `check-omp-port.py`, which SC-08 and SC-13's fourth
clause depend on) is fail-closed. Rated MED rather than HIGH because the actual shipped gate does
not sail through; the isolated tool that SC-13 also names standalone does. Writability:
squad-writable (`.claude/skills/harness/bin/**` / `tests/**`).

**No finding** — root resolution: `sync-command-adapters.py` uses the identical pattern to its
sibling (`--root` default `Path(__file__).resolve().parents[4]`, then `.resolve()`) — confirmed by
diffing both files' argument definitions. No second root resolver introduced (T-14's intent
explicitly forbids this).

**No finding** — `factory_config.py`'s `product_config_report()` catches only `FleetError`, letting
any other exception propagate (documented and confirmed); `_check_product_configs` exits
`EXIT_REFUSED` (2) on `unreachable_count or len(report) != len(fleet["repos"])`, correctly
fail-closed, including the defensive short-report branch.

**No finding** — `check-omp-port.py`'s door-existence loop and `sync-command-adapters.py --check`
subprocess call both use `Path.is_file()` / subprocess return-code checks that behave correctly
(report an error) when `.omp/commands` is missing entirely — confirmed by the fixture above.

## Disposition of the SETTLED list

Not re-raised: D-14 owner-manifest deviation, D-13 `cli_min_version` removal, D-10/DEC-06
`harness-add-repo` as a skill, D-12 CLI floor removal, D-07 in-place revision, issue #206 item 2.
The known-red 6-case integration failure is the accepted D-14 condition, not reported as a finding.

## Verdict rationale

`must_fix` is non-empty (the grade-1 test function) → **FAIL**, independent of spec compliance,
which is clean. Nothing here re-litigates a settled decision; nothing here is a spec violation —
Stage 1 is fully MET. The gate is a Stage-2 code-quality bar this feature's own diff crosses.
