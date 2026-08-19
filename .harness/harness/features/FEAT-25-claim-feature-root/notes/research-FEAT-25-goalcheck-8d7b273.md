# Goal-check — FEAT-25 — 8d7b273

**PASS. Eight of eight success criteria met, six on evidence I produced myself.** The factory can
claim work at the migrated root, the pin is red against the pre-fix constant, and nothing outside
the plan's declared files changed. Three known findings are real but none falsifies an SC as
written; two are durability gaps worth a follow-up, not a fix cycle here.

**UAT: BRIEF declares no UAT criteria.** Read in full — the document's sections are Problem, Goal,
Requirements, Success Criteria, Verification gaps, Constraints, Approval. No `## UAT` section exists
and no SC carries `verify: uat` (seven `automated`, one `inspection` — SC-08). Nothing here waits on
the operator to execute.

## The gate — judged, not inherited

The orchestrator's attribution is **correct, and I confirmed it without a worktree**. Run from the
repository root, of the twelve scripts in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`, exactly one
exits nonzero: `test-gen-decisions-index.py`, whose only failure is
`test_committed_index_matches_a_fresh_regeneration` disagreeing about DEC-196's refs/tags row.
`.harness/harness/docs/DECISIONS.md` and `DECISIONS-INDEX.md` are both absent from
`git diff --name-only d1ffd7f...8d7b273` (six files, all under `.claude/skills/harness/bin/`), so the
red is held dirt from another workstream and not attributable to this branch. One caveat worth
recording: `test-bash-write-guard.py` and `test-check-domain.py` are cwd-sensitive — they exit 1 when
run with cwd inside `bin/` and 0 from the repository root. The runner inherits the caller's cwd, so a
future measurement taken from the wrong directory will read three reds, not one.

## The eight verdicts

| SC | Verdict | Evidence | Mine / inherited |
|---|---|---|---|
| SC-01 | met | `test-factory-claim.py:52-61` — two module-scope `check()` calls, after `check()` is defined (line 38) and before `build_features_root()` (line 372) and every save-patch-restore block; the expectation is built as `os.path.join(fc.harness_root(), ".harness", "harness", "features")`, never a literal; both cases print `ok` in a 120/120 run | **mine** (read + ran) |
| SC-02 | met | Evaluated both pin assertions against the pre-fix constant value `<root>/.harness/features`: equality `False`, `isdir` `False` — a pure value derivation, no tree mutation. The full pre-fix snapshot run is `notes/qa-c1.md` §6 | **mine**, corroborated by **inherited** (`notes/qa-c1.md`) |
| SC-03 | met | `test-factory-integration.py:715` and `:1079` plant the fixture at `os.path.join(root, ".harness", "harness", "features", feat)` under a redirected `harness_root()`; the tool runs as a subprocess so nothing monkeypatches `FEATURES_ROOT` — the constant itself is what resolves. `(F) claim exits 0` / `(F) claim: stdout is one JSON object` / `(F) claim: claimed the T-1 issue` all `ok`, 106/106, exit 0 | **mine** (read + ran) |
| SC-04 | met | `factory_claim.py` new `no_plan` branch returns two texts naming the absolute `plan_path()`, one for an absent root and one for a missing/unparseable plan; `test-factory-claim.py:863-868` asserts `absent_root in err` and `"no matching plan task" not in err`, and `:881` asserts the edge-(i) text still fires when the plan loads but the task id is absent. Both `ok` | **mine** |
| SC-05 | met | This feature adds **two** `no_plan` texts (root-absent, and plan missing/unparseable) and both are returned by `_blocker_reason_text` into the **one** print site at `factory_claim.py:386`, which is `file=sys.stderr` — so the second is proven by the first structurally, and the string "missing or unparseable" appears in no test assertion (grep of both suites: no hits). Stream evidence: `(B5-ter) ... stdout empty` asserts `out == ""` with the reason in `err`; `(X) sc13b` counts exactly eight skip lines on stderr; `(F) claim: stdout is one JSON object` on the integration side. `run_main` captures stdout and stderr as two separate `StringIO`s (`test-factory-claim.py:399-402`), so no case reads a merged stream | **mine** |
| SC-06 | met | `test-layout-migration.py` case 22 asserts `features: CLEAN — evidence migrated` at the real root. That is genuinely a per-file assertion: `layout_migration.scan` returns MIXED if any reader's form differs from the evidence shape (`layout_migration.py:252-254`). I proved the dependency by mutation — passing a `table` whose `factory_claim.py` row cannot match the migrated form flips the surface to `MIXED`. Direct read of the verdict list at the real root: `('.claude/skills/harness/bin/factory_claim.py', 'migrated')` | **mine** (mutation + direct scan) |
| SC-07 | met | Own AST set diff of `check()` first-argument literals per file, `d1ffd7f` vs HEAD, each baseline set non-empty (111 / 75 / 32): **exactly one removal**, `"(X) sc13b fixture: exactly seven skip lines fired..."` — the single authorised rename, replaced by the eight-reason form (`len(matches) == 8`, `range(901, 909)`), which strengthens rather than weakens. I also read every `-` line of all three test diffs: they are the docstring rewrites, the `.harness/features` → `.harness/harness/features` path-literal move, and that rename — no assertion loosened in place. Counts at HEAD, mine: claim 120 (`^ok    `), integration 106, layout 41 (`^ok` — that suite prints `ok   - `). Baselines 114/106/40 | counts and set diff **mine**; the 114/106/40 baselines **inherited** (`notes/qa-c1.md`) |
| SC-08 | met | Grading set = `git diff --name-only d1ffd7f...8d7b273` (six paths, none under the feature directory, so the R-6 exclusion removes nothing). (a) all six appear in the T-01/T-02/T-03 `files:` union, which is exactly those six. (b) six individually named verdicts, each its own check: `factory_config.py` absent; `.harness/factory/fleet.yaml` absent; `.harness/harness.json` absent; `gh_board.py` absent; `check-domain.sh` absent; `load_board` appears in zero added (`^+`) lines of the diff | **mine** |

## The three known findings — none falsifies an SC

- **F-1** (`test-layout-migration.py:416-418`, `fails += 1` inside `if not ok and detail:`). Pre-existing
  confirmed by my own read: the file's whole three-dot diff is one hunk, `@@ -399,6 +399,16 @@`, with
  zero deleted lines and the report block as unchanged context. It does not touch my SC-06 or SC-07
  verdicts, which rest on printed `ok` lines and an empty `^FAIL` grep, not on the exit code. Real
  defect, not this feature's.
- **F-2** (case 22 does not name `factory_claim.py`; deleting its `READER_TABLE` row with the paired
  `STUB` entry would evade the guard). SC-06 as written asks that the detector report the file
  `migrated` and the surface stay CLEAN — both are true today and both are automated. The gap is
  durability of the permanent suite, not the criterion. Worth one case asserting the reader tuple.
- **The `no_plan` texts are pinned by substring, not byte-exact.** SC-04 asks that the reason name the
  absolute path tried and that the two messages not be interchangeable; SC-05 asks for stream
  separation. Neither asks for byte-exactness. A wrapping slip would degrade the message with the gate
  green — a real durability note, not a falsification.

## Open questions

- Q1 (non-blocking): an assertion that `factory_claim.py` is in the layout detector's features reader
  set, and byte-exact pins on the two `no_plan` texts, would close F-2 and the wrapping gap. Both are
  new work BRIEF never stated — emergent, **covered in substance** by SC-04/SC-06 as written, so not
  adopted here. The second `no_plan` text ("missing or unparseable") is likewise unexercised by any
  assertion — its stderr routing is proven by the shared print site, its wording by nothing.
  Recommendation: backlog, not a fix cycle.
- Q2 (non-blocking): `test-bash-write-guard.py` and `test-check-domain.py` pass only when run from the
  repository root. A gate measurement taken from `bin/` reads three reds. Harness defect, not FEAT-25's.
