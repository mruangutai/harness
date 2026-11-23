# T-02 red/green receipts (BuildC_T02, 2026-11-22)

Command: the literal plan.yaml tasks[1].verify (saved verbatim as /tmp/t02-verify.sh). Red runs executed only its inline CHECK heredoc with HARNESS_PROJECT_DIR=$PWD inside `git archive <sha>` extracts (no git writes), HARNESS_AGENT_TYPE unset.

## RED at 9eb07b4f (spec baseline 9eb07b4f; pre-change HEAD 2346a777)
```
FAIL Unit suite
FAIL Validate feature execution state
FAIL Plan-route gate
FAIL Canonical-reader audit
FAIL Instruction-path gate
FAIL Layout gate
FAIL Repository-state gate
FAIL Integration suite (shard ${{ matrix.shard }}/4)
FAIL Validate shard completeness
OK two guidance lines
FAIL echo "::error::check-plan-routes.py entered 0 feature directories, and this repository has features. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever, the exact trap issue #133 names. Check CLAUDE_PROJECT_DIR and .harness/*/features/." >&2
FAIL echo "::error::layout_migration.py examined 0 ${zero}. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever. Check CLAUDE_PROJECT_DIR and the feature/doc roots." >&2
FAIL tests/integration/test-harness-yaml.py
FAIL tests/integration/test-validate-feature-json.py
FAIL tests/unit/test-harness-yaml-corpus.py
FAIL tests/unit/test-team-catalog.py
FAIL tests/unit/test-plan-depends-on.py
Traceback (most recent call last):
  File "<stdin>", line 14, in <module>
AssertionError
exit=1
```

## RED at 2346a777 (spec baseline 9eb07b4f; pre-change HEAD 2346a777)
```
FAIL Unit suite
FAIL Validate feature execution state
FAIL Plan-route gate
FAIL Canonical-reader audit
FAIL Instruction-path gate
FAIL Layout gate
FAIL Repository-state gate
FAIL Integration suite (shard ${{ matrix.shard }}/4)
FAIL Validate shard completeness
OK two guidance lines
FAIL echo "::error::check-plan-routes.py entered 0 feature directories, and this repository has features. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever, the exact trap issue #133 names. Check CLAUDE_PROJECT_DIR and .harness/*/features/." >&2
FAIL echo "::error::layout_migration.py examined 0 ${zero}. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever. Check CLAUDE_PROJECT_DIR and the feature/doc roots." >&2
FAIL tests/integration/test-harness-yaml.py
FAIL tests/integration/test-validate-feature-json.py
FAIL tests/unit/test-harness-yaml-corpus.py
FAIL tests/unit/test-team-catalog.py
FAIL tests/unit/test-plan-depends-on.py
Traceback (most recent call last):
  File "<stdin>", line 14, in <module>
AssertionError
exit=1
```

## GREEN: full verify on the working tree after the change
```
OK Unit suite
OK Validate feature execution state
OK Plan-route gate
OK Canonical-reader audit
OK Instruction-path gate
OK Layout gate
OK Repository-state gate
OK Integration suite (shard ${{ matrix.shard }}/4)
OK Validate shard completeness
OK two guidance lines
OK echo "::error::check-plan-routes.py entered 0 feature directories, and this repository has features. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever, the exact trap issue #133 names. Check HARNESS_PROJECT_DIR and .harness/*/features/." >&2
OK echo "::error::layout_migration.py examined 0 ${zero}. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever. Check HARNESS_PROJECT_DIR and the feature/doc roots." >&2
OK tests/integration/test-harness-yaml.py
OK tests/integration/test-validate-feature-json.py
OK tests/unit/test-harness-yaml-corpus.py
OK tests/unit/test-team-catalog.py
OK tests/unit/test-plan-depends-on.py
16/16 checks passed.
10/10 checks passed.
13/13 checks passed.
exit=0
```

## Diff (HEAD 2346a777 -> working tree), reader assignments lose only the CLAUDE arm
```diff
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index e4b537f3..0f0e1de8 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -1,7 +1,7 @@
 name: tests
 
 # WHY THIS EXISTS (issue #161): nothing ran the suites mechanically. Not a git hook, not a
-# Claude Code hook, not check-state.py at /harness entry — the only path was harness-qa
+# session hook (.omp/extensions/harness-hooks.ts), not check-state.py at /harness entry — the only path was harness-qa
 # reading test_kinds during a team flow, or a human remembering. Every assertion added
 # across #149, #152 and #153 was dormant by default, which is issue #133's own shape
 # ("logic correct, nothing calls it") applied to the safety net itself.
@@ -115,7 +115,7 @@ jobs:
       # still does not cover.
       - name: Unit suite
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: .agents/skills/harness/bin/run-unit-tests.py --kind unit
 
       # VALIDATE EVERY FEATURE'S EXECUTION STATE (FEAT-14/T-03, REQ-06/REQ-07). No
@@ -124,12 +124,12 @@ jobs:
       # a session where check-domain.py's write-time gate is not registered at all.
       - name: Validate feature execution state
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: .agents/skills/harness/bin/validate-feature-json.py
 
       # THE ROUTE CHECK, PROMOTED (issue #133, DEC-183). `check-plan-routes.py` worked from the
       # day it shipped and NOTHING mechanical ran it: not this workflow, not check-state.py, not
-      # one of the 7 hook registrations in settings.json — `run-unit-tests.py` runs its TEST, never
+      # one of the session hooks in .omp/extensions/harness-hooks.ts — `run-unit-tests.py` runs its TEST, never
       # the checker. Its sole invocation was one sentence in harness-spec-driven/SKILL.md telling a
       # planner to remember. This step is the mechanism; the sentence stays, because plan time is
       # still when a violation is cheap to fix.
@@ -174,7 +174,7 @@ jobs:
       # on real plans. Collapsing them into one "failed" is how a broken gate hides behind a red X.
       - name: Plan-route gate
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: |
           rc=0
           out=$(python3 .agents/skills/harness/bin/check-plan-routes.py 2>&1) || rc=$?
@@ -212,7 +212,7 @@ jobs:
             exit 1
           fi
           if [ "$examined" -eq 0 ]; then
-            echo "::error::check-plan-routes.py entered 0 feature directories, and this repository has features. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever, the exact trap issue #133 names. Check CLAUDE_PROJECT_DIR and .harness/*/features/." >&2
+            echo "::error::check-plan-routes.py entered 0 feature directories, and this repository has features. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever, the exact trap issue #133 names. Check HARNESS_PROJECT_DIR and .harness/*/features/." >&2
             exit 1
           fi
 
@@ -236,7 +236,7 @@ jobs:
       # audit could not run; 0 Python files means discovery found nothing, never a clean tree.
       - name: Canonical-reader audit
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: |
           rc=0
           out=$(python3 .agents/skills/harness/bin/check-plan-routes.py --canonical-reader-audit 2>&1) || rc=$?
@@ -254,7 +254,7 @@ jobs:
 
       - name: Instruction-path gate
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: |
           rc=0
           out=$(python3 .agents/skills/harness/bin/check-instruction-paths.py 2>&1) || rc=$?
@@ -280,7 +280,7 @@ jobs:
       # deliberately unenforced, because the sole collaborator cannot approve their own PR.
       - name: Layout gate
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: |
           rc=0
           out=$(python3 .agents/skills/harness/bin/layout_migration.py . 2>&1) || rc=$?
@@ -321,7 +321,7 @@ jobs:
             zero="reader file(s)"
           fi
           if [ -n "$zero" ]; then
-            echo "::error::layout_migration.py examined 0 ${zero}. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever. Check CLAUDE_PROJECT_DIR and the feature/doc roots." >&2
+            echo "::error::layout_migration.py examined 0 ${zero}. Discovery did not run — an empty search is indistinguishable from a clean tree and would pass forever. Check HARNESS_PROJECT_DIR and the feature/doc roots." >&2
             exit 1
           fi
 
@@ -346,7 +346,7 @@ jobs:
       # checkout that blinds the checker cannot also silence the guard.
       - name: Repository-state gate
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: |
           git config core.hooksPath .claude/skills/harness/hooks
 
@@ -408,7 +408,7 @@ jobs:
       # shard leaves no manifest, and `integration` refuses on its absence.
       - name: Integration suite (shard ${{ matrix.shard }}/4)
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
         run: >-
           .agents/skills/harness/bin/run-unit-tests.py --kind integration
           --shard ${{ matrix.shard }}/4
@@ -461,7 +461,7 @@ jobs:
       - name: Validate shard completeness
         if: always()
         env:
-          CLAUDE_PROJECT_DIR: ${{ github.workspace }}
+          HARNESS_PROJECT_DIR: ${{ github.workspace }}
           CHECKS_RESULT: ${{ needs.checks.result }}
           MATRIX_RESULT: ${{ needs.integration-shards.result }}
           DOWNLOAD_OUTCOME: ${{ steps.download.outcome }}
diff --git a/tests/integration/check_domain_support.py b/tests/integration/check_domain_support.py
index e736ce8d..89d41691 100644
--- a/tests/integration/check_domain_support.py
+++ b/tests/integration/check_domain_support.py
@@ -34,21 +34,21 @@ ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
 
 
 def _env(root, **kw):
-    """The hook's environment for a fixture rooted at `root` — BOTH names, one value.
+    """The hook's environment for a fixture rooted at `root` — HARNESS_PROJECT_DIR only.
 
     FEAT-42 T-10. check-domain.py resolves its root through harness_boundary.resolve_root,
     which reads HARNESS_PROJECT_DIR and no other name. The reverted sha-3952814 copy this
-    suite is diffed against reads HARNESS_PROJECT_DIR first and CLAUDE_PROJECT_DIR second.
-    Setting both to the same value is therefore the ONE spelling under which the two copies
-    resolve the same root, which is what makes the identical-violation-set proof mean
-    anything. Setting only the host-owned name — what every call here did before — points
-    the new copy at the live checkout instead, and 20 cases failed exactly that way.
+    suite is diffed against reads HARNESS_PROJECT_DIR first, so that one name resolves the
+    same root in both copies, which is what makes the identical-violation-set proof mean
+    anything. Setting only the retired host-owned name (CLAUDE_PROJECT_DIR) — what every call
+    here once did — points the new copy at the live checkout instead, and 20 cases failed
+    exactly that way.
 
     resolve_root honours the override only when `.harness/team-config.yaml` is readable
     underneath it. A fixture without that marker gets the override discarded and falls back
     to the derived root, which is the same answer the deleted chain gave it.
     """
-    return dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root, **kw)
+    return dict(os.environ, HARNESS_PROJECT_DIR=root, **kw)
 
 
 FIXTURE_MANIFEST = """schema_version: 1
diff --git a/tests/integration/check_state_support.py b/tests/integration/check_state_support.py
index 027de63d..544bbb59 100644
--- a/tests/integration/check_state_support.py
+++ b/tests/integration/check_state_support.py
@@ -118,10 +118,10 @@ def _root_env(tmp, env=None, **extra):
     """The environment that points check-state.py at the fixture `tmp` — and the MARKER
     without which the pointer is discarded (FEAT-42 T-12).
 
-    BOTH NAMES. check-state.py now resolves through harness_boundary.resolve_root, which
-    reads HARNESS_PROJECT_DIR and no other name; the reverted sha-3952814 copy this suite is
-    diffed against read HARNESS first and the host-owned name second. Both set to one value
-    is the only spelling under which the two copies resolve the same root.
+    HARNESS_PROJECT_DIR ONLY. check-state.py resolves through harness_boundary.resolve_root,
+    which reads HARNESS_PROJECT_DIR and no other name; the reverted sha-3952814 copy this
+    suite is diffed against reads HARNESS first, so that one name resolves the same root in
+    both copies.
 
     AND THE MARKER. resolve_root honours the override only when .harness/team-config.yaml is
     readable underneath it. No builder in this file wrote one, so after the cutover every
@@ -133,7 +133,6 @@ def _root_env(tmp, env=None, **extra):
     reaching that branch, and INV-29's (e) and (f) write their own marker first.
     """
     env = dict(os.environ) if env is None else env
-    env["CLAUDE_PROJECT_DIR"] = tmp
     env["HARNESS_PROJECT_DIR"] = tmp
     _m = os.path.join(tmp, _hb.MARKER)
     if os.path.isdir(os.path.join(tmp, ".harness")) and not os.path.exists(_m):
diff --git a/tests/integration/test-harness-yaml.py b/tests/integration/test-harness-yaml.py
index 1bea15bf..93d38da6 100644
--- a/tests/integration/test-harness-yaml.py
+++ b/tests/integration/test-harness-yaml.py
@@ -25,9 +25,9 @@ if BIN_DIR not in sys.path:
     sys.path.insert(0, BIN_DIR)
 import artifact_accessors
 
-# Repo root: four levels above .agents/skills/harness/bin. CLAUDE_PROJECT_DIR
+# Repo root: four levels above .agents/skills/harness/bin. HARNESS_PROJECT_DIR
 # overrides when the caller has already resolved it (run-unit-tests.py does).
-REPO_ROOT = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.path.abspath(
+REPO_ROOT = os.environ.get("HARNESS_PROJECT_DIR") or os.path.abspath(
     os.path.join(BIN_DIR, "..", "..", "..", "..")
 )
 MANIFEST_PATH = os.path.join(REPO_ROOT, ".harness", "team-config.yaml")
diff --git a/tests/integration/test-validate-feature-json.py b/tests/integration/test-validate-feature-json.py
index d9ed8885..096d6a9a 100644
--- a/tests/integration/test-validate-feature-json.py
+++ b/tests/integration/test-validate-feature-json.py
@@ -26,7 +26,7 @@ BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
 if BIN_DIR not in sys.path:
     sys.path.insert(0, BIN_DIR)
 
-REPO_ROOT = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.path.abspath(
+REPO_ROOT = os.environ.get("HARNESS_PROJECT_DIR") or os.path.abspath(
     os.path.join(BIN_DIR, "..", "..", "..", "..")
 )
 
@@ -741,7 +741,8 @@ def case_749_schema_comes_from_the_written_tree():
     MEASURED LIVE 2026-08-23 during FEAT-26's ship. `check-domain.py --post` refused a
     legitimate write -- `undeclared key 'source_issues' at /github' -- because the key WAS
     declared in the worktree's own feature-schema.json and was NOT in main's, and the hook
-    imports this module from CLAUDE_PROJECT_DIR, the main checkout.
+    imports this module from the main checkout (then reached through CLAUDE_PROJECT_DIR,
+    now through HARNESS_PROJECT_DIR).
 
     THE GENERAL SHAPE: a feature that ADDS a schema key cannot write data using that key
     until it merges, and cannot demonstrate the key working before it merges. The schema and
diff --git a/tests/unit/test-harness-yaml-corpus.py b/tests/unit/test-harness-yaml-corpus.py
index 8edaf43f..49d3fa34 100644
--- a/tests/unit/test-harness-yaml-corpus.py
+++ b/tests/unit/test-harness-yaml-corpus.py
@@ -61,7 +61,7 @@ except ModuleNotFoundError:
           "fallback by design.", file=sys.stderr)
     sys.exit(1)
 
-REPO = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.getcwd()
+REPO = os.environ.get("HARNESS_PROJECT_DIR") or os.getcwd()
 
 
 def _rel(p, root):
diff --git a/tests/unit/test-plan-depends-on.py b/tests/unit/test-plan-depends-on.py
index 0450fbe4..efe8c5e1 100755
--- a/tests/unit/test-plan-depends-on.py
+++ b/tests/unit/test-plan-depends-on.py
@@ -236,9 +236,7 @@ with tempfile.TemporaryDirectory() as _tmp:
 # --- 9. THE LIVE CORPUS (D-04): every real plan.yaml loads ---------------------
 # Asserts integrity only, never a size: cases 7 and 8 carry the vacuity guard, so this holds
 # for however many features the corpus keeps.
-_REPO = (_anchor_os.environ.get("HARNESS_PROJECT_DIR")
-         or _anchor_os.environ.get("CLAUDE_PROJECT_DIR")
-         or _anchor_os.getcwd())
+_REPO = _anchor_os.environ.get("HARNESS_PROJECT_DIR") or _anchor_os.getcwd()
 _count_a, _failures_a = walk(_REPO)
 check(f"the live plan corpus loads cleanly ({_count_a} files found)",
       not _failures_a,
diff --git a/tests/unit/test-team-catalog.py b/tests/unit/test-team-catalog.py
index 20fccd69..643b3c8f 100755
--- a/tests/unit/test-team-catalog.py
+++ b/tests/unit/test-team-catalog.py
@@ -45,7 +45,7 @@ except ModuleNotFoundError:
               "  This is REQUIRED, not optional (DEC-171).", file=sys.stderr)
         sys.exit(1)
 
-REPO = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or _anchor_root
+REPO = os.environ.get("HARNESS_PROJECT_DIR") or _anchor_root
 TEAMS = os.path.join(REPO, ".claude", "skills", "harness", "teams")
 BIN = os.path.join(REPO, ".claude", "skills", "harness", "bin")
 SKILL_MD = os.path.join(REPO, ".claude", "skills", "harness", "SKILL.md")
```

## Root-negative + helper-consumer suites (exit, last summary line), CLAUDE_PROJECT_DIR unset
```
0 tests/integration/test-bash-write-guard.py :: 89/89 FEAT-2225 expertise CLI cases passed.
0 tests/integration/test-check-domain-approval.py :: 28/28 T-14 cases passed.
0 tests/integration/test-check-domain-artifact.py :: 10/10 BUG-1305 identity cases passed.
0 tests/integration/test-check-domain-claims.py :: 
0 tests/integration/test-check-domain-grant.py :: 21/21 FEAT-2337 receipt-grant cases passed.
0 tests/integration/test-check-domain-post.py :: 30/30 post-mode cases passed.
0 tests/integration/test-check-domain-worktree-parity.py :: 49/49 worktree grant-parity cases passed.
0 tests/integration/test-check-domain-worktree.py :: 12/12 b2 cwd-independence cases passed.
0 tests/integration/test-check-domain.py :: 29/29 T-06 check-domain cases passed.
0 tests/integration/test-check-state-entry.py :: 
0 tests/integration/test-check-state-feat59.py :: ok - case (47.b) member notes at PASS/n/a are silent; an earlier cycle's BLOCKED note belongs to that cycle's FAIL run, not this one
0 tests/integration/test-check-state-handoff.py :: 
0 tests/integration/test-check-state-inv26.py :: 
0 tests/integration/test-check-state-inv37-offline.py :: 
0 tests/integration/test-check-state-inv51.py :: all checks passed
0 tests/integration/test-check-state-plans.py :: 
0 tests/integration/test-check-state-records.py :: ok - INV-7 (SC-04): no cycle or FAIL-count violation for three FAILs against a total of 1
0 tests/integration/test-check-state-table.py :: 
0 tests/integration/test-check-state-worktrees.py :: 
0 tests/integration/test-check-state.py :: 3/3 T-07 undeclared step key cases passed.
1 tests/integration/test-harness-config-fixtures.py :: FAIL  tests/unit/omp-hooks.test.ts::writeFileSync#5: an inline TypeScript harness.json that is not read from the checked-in budget fixture
0 tests/integration/test-harness-config-readers.py :: 
0 tests/integration/test-plan-merge.py :: PASS  F-02 (a bare newline): approved_by round-trips as the exact string passed
0 tests/integration/test-validate-digest.py :: 4/4 member-expertise committed tamper checks passed.
0 tests/integration/test-gen-decisions-index.py :: 
```
test-harness-config-fixtures.py exit 1: finding in tests/unit/omp-hooks.test.ts (writeFileSync#5), a file last changed by T-01 8f373f76 and untouched by T-02; not caused by T-02.

## CI job `checks` run steps, local (env ${{ github.workspace }} -> $PWD, HARNESS_AGENT_TYPE unset)
```
STEP 2 Install TypeScript toolchain: exit=0
STEP 3 Typecheck: exit=0
STEP 4 Install PyYAML and jsonschema: exit=1
STEP 5 Precompile harness bin: exit=0
STEP 6 Unit suite: exit=1
STEP 7 Validate feature execution state: exit=0
STEP 8 Plan-route gate: exit=0
STEP 9 Canonical-reader audit: exit=0
STEP 10 Instruction-path gate: exit=0
STEP 11 Layout gate: exit=0
STEP 12 Repository-state gate: exit=0
```
- Step 4 ran with pip `--dry-run` (to avoid mutating the host Python); exit 1 = Homebrew externally-managed-environment refusal, local-only. PyYAML/jsonschema already importable.
- Step 6 exit 1: tests/unit/test-omp-hooks.py, 5 fails `distill-authority: REFUSED no live claim binds runtime Orch* to FEAT-9003-host-core`; identical 5 fails (242 pass) reproduce on the pristine 2346a777 extract, so pre-existing, not T-02.
- Step 12 runs `git config core.hooksPath .claude/skills/harness/hooks`; the value was already that, so it was a no-op.

Grades: no test functions added; changed helpers `_env` / `_root_env` are straight-line (CC 1), self-graded 4. No production files are in T-02.
