# Review — harness-code-reviewer — validate — BUG-442-docs-grant-witness-test — c0

## Reconcile

`git log --format='%h %s' 6d969ed3..9b3fde7e`: 6 commits, all authored `Mike Ruangutai`, none
`[harness:human]`. `git status --porcelain`: clean. HEAD is actually `c3a9d7b9` (one commit ahead
of the pin, touching `feature.json` only — `git diff 9b3fde7e c3a9d7b9 -- tests/…` is empty), so
the working tree at HEAD reproduces `9b3fde7e`'s bytes for every path graded below. No drift to
report, no human edits in scope.

**Gotcha logged for the next reader of this artifact**: relative `read`/`grep` paths on this host
resolve against the main checkout, not this worktree, and the main checkout carries a stale
908-line version of the test file with no BUG-442 code — it silently returns that instead of
erroring. Every citation below was taken from the absolute worktree path or `git show 9b3fde7e:…`.

## STAGE 1 — Spec compliance: **PASS**

Read `BRIEF.md` and `plan.yaml` at `9b3fde7e`. Diff scope check: 15 files, +1421/-0; 14 are the
feature's own records under `.harness/harness/features/BUG-442-docs-grant-witness-test/`, exactly
1 is code (`tests/integration/test-harness-yaml.py`, +182/-0, confirmed zero deletion lines via
`git diff 6d969ed3 9b3fde7e -- tests/integration/test-harness-yaml.py | grep -E '^-' | grep -v '^---'`
→ no output). No scope creep.

| REQ | Verdict | Anchor |
|---|---|---|
| REQ-01 (asserted against live manifest) | met | `_docs_domain_census` calls `hy.load_file`/`hy.manifest_domains` on `MANIFEST_PATH` at :237-263; no hand-copied grant text |
| REQ-02 (addition fails) | met | per-persona assert :283-286; demonstrated live by mutant M1 :318-326 |
| REQ-03 (removal fails) | met | same per-persona assert; demonstrated live by mutant M2 :328-334 |
| REQ-04 (census pinned, deletion can't shrink) | met | `DOCS_GRANT_CENSUS` frozenset :208-224, `personas == DOCS_GRANT_CENSUS` :279; mutant M3 :336-338 |
| REQ-05 (COLLECT_FIXTURE unweakened, manifest unchanged) | met | see SC-07 below |

### SC verification

- **SC-01** (subprocess repoint reddens witness, control stays ok) — `verify: automated`. Mapped
  to `test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`'s `_run_child` +
  per-mutant asserts :340-381. **Ran it myself**: `env -u HARNESS_AGENT_TYPE python3
  tests/integration/test-harness-yaml.py` → exit 0, both new tests print `ok`, all 24 lines `ok`,
  0 `FAIL`. The internal ladder (which is exactly SC-01's scenario, run 4× as real subprocesses)
  passed as part of that.
- **SC-02** (all 16 personas, not a subset) — `verify: automated`, mapped to `personas ==
  DOCS_GRANT_CENSUS` :279. Independently re-executed `_docs_domain_census(MANIFEST_PATH)` in a
  standalone interpreter: returned exactly 16 names, matching `DOCS_GRANT_CENSUS` verbatim
  (1 bare `harness-orchestrator`, dedup of the `lead: {name: …}` references against `leads:`
  confirmed — no double count).
  Docs grant returned: `{'harness-documentor': ['.harness/*/docs/**', 'docs/**']}`, all other 15
  personas empty — matches `EXPECTED_DOCS_GRANTS` exactly.
- **SC-03** (addition to `harness-qa` reddens) — mapped to mutant M1 :318-326. Confirmed
  `harness-qa` is genuinely absent from `COLLECT_FIXTURE` (only other occurrence of the string in
  the file is inside `DOCS_GRANT_CENSUS`), and confirmed the manifest has exactly one
  `      - name: harness-qa` line (`.harness/team-config.yaml:244`) with its own `domain:` key
  directly below at 8-space indent and no intervening line of that exact shape — M1's anchor
  search cannot land in the wrong block on the current manifest.
- **SC-04** (removal from documentor reddens) — mapped to mutant M2 :328-334. Confirmed
  `{ path: .harness/*/docs/**` occurs exactly once in the whole manifest
  (`.harness/team-config.yaml:144`), so the needle search is unambiguous.
- **SC-05** (persona deletion reddens rather than shrinking the domain) — mapped to mutant M3
  :336-338. Confirmed `- name: harness-ui-reviewer` occurs exactly once
  (`.harness/team-config.yaml:289`); the walk's `node.get("name")` collection means the rename to
  `nickname:` genuinely drops that one persona from the discovered set.
- **SC-06** (equivalence test still ok; both new tests registered) — confirmed by the run above
  (`ok   test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`) and by reading
  `TESTS` at `tests/integration/test-harness-yaml.py:1041-1074` (absolute path) — both new
  functions present at :1050-1051, in the position the task specified.
- **SC-07** (`verify: inspection` — graded here). `git diff 6d969ed3 9b3fde7e --
  .harness/team-config.yaml .claude/skills/harness/bin/harness_yaml.py` → empty. `git diff 6d969ed3
  9b3fde7e -- tests/integration/test-harness-yaml.py` → zero lines matching `^-` other than the
  `---` file header. **Both clauses hold exactly as worded. SC-07: met.**

No omissions, no mismatches, no scope creep. **Stage 1 verdict: PASS.**

## STAGE 2 — Code quality (on `tests/integration/test-harness-yaml.py` only): **PASS with notes**

Fail-open hunt on the `BUG442_MUTANT_CHILD` guard (:292-300, D-03/D-02-settled, not proposing
removal): traced both branches. The child branch fires only when the env value equals the
*current* `HARNESS_PROJECT_DIR`, and that pairing is set in exactly one place (`_run_child`'s
`env={…}` at :349), always to the same fresh `tempfile.TemporaryDirectory` path for both keys —
no other code path in the file sets `BUG442_MUTANT_CHILD`. A genuinely nested legitimate nested-run
scenario that reaches the parent `assert _child_token is None` and reddens the suite spuriously
would require an ancestor process to export that variable without it matching this run's
`HARNESS_PROJECT_DIR` — i.e. contamination from an unrelated process, which is exactly the
scenario the assert is designed to catch loudly rather than mask. No reachable false-positive path
found. All three mutant no-op guards (`assert m*_text != real_text`) and all three per-mutant
assertions execute for real — confirmed by actually running the file: the internal subprocess
calls happened (proven by the outer test's own `ok`, which is unreachable if any of the three
child-process comparisons had failed).

Anchor fragility (M1, M2, M3): re-verified concrete uniqueness against the real manifest for all
three anchors (see SC-03/04/05 above) — none currently finds the wrong occurrence. Census-walk
correctness (`docs` segment membership via `path.split("/")`, not substring) verified by direct
execution, not by reading the code alone.

### Findings

- **F-01 (med, code-grade)** — `tests/integration/test-harness-yaml.py:292`,
  `test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`.
  `code-grade.py --base 6d969ed3 --head 9b3fde7e` (== `merge-base(origin/main, 9b3fde7e)`, verified
  independently: `git merge-base origin/main 9b3fde7e` → `6d969ed3`) reports CYCLOMATIC 15,
  COGNITIVE 7, ABC 33.1 → **GRADE 2**, below the test-code grade-3 bar, `RESULT: FAIL`,
  `REASON REQUIRED`. No reasoned justification for this exists anywhere in the feature record
  (checked `receipt-harness-backend-dev-T-01-c0.md`, the SIMPLIFY apply receipt, `STATE.md`, the qa
  note — none mention it; this is the first code-quality pass over the actual diff, the plan-phase
  panel graded `BRIEF.md`/`plan.yaml` only). My own reasoned answer: the elevated cyclomatic/ABC is
  enumerative, not nested — three structurally-parallel, non-mergeable mutation recipes (each
  needs its own anchor-and-edit shape: indexed insert for M1, line-removal-by-scan for M2, a plain
  replace for M3) plus a shared recursion guard and a 3-item assertion loop already dedups the
  per-mutant verification. Cognitive score (7) stays well under the grade-4 nesting threshold (9),
  consistent with "long but flat" rather than "hard to follow." SIMPLIFY's REUSE angle already
  weighed extracting shared shape here (REU-F1, on `_run_child`) and declined it for the same
  different-subjects reason D-02 gives the fixture split. I accept grade 2 as justified by design,
  not as an oversight — **not must_fix**. Reported per policy: `code_grade: grade_2`, not `fail`
  (no grade-1 function and no gated production function below its bar exists in this diff — the
  other four graded functions, `_docs_domain_census`, its nested `walk`, `_run_child`, and
  `test_docs_domain_grant_is_exhaustive_over_every_persona`, are all grade 4, comfortably above the
  test-code bar).
- **F-02 (low, robustness, non-blocking)** — `tests/integration/test-harness-yaml.py:350-353`,
  `_run_child`. `subprocess.run([...])` carries no `timeout=`. Today the recursion guard is sound
  (F-01's fail-open trace above), so this is not a live hang; it is a hardening gap — a future edit
  that weakens the `BUG442_MUTANT_CHILD` pairing (e.g. changing one side to a constant instead of
  the shared temp path) would make the child re-enter the ladder and this call would block forever
  with no diagnostic, wedging whatever CI runner invoked it. Cheap to add; not required by any REQ
  or SC, so not must_fix.
- **F-03 (info, non-blocking)** — `tests/integration/test-harness-yaml.py:317-321`. M1's anchor
  search (`real_text.index('        domain:', qa_idx)`) depends on no other 8-space `domain:` line
  appearing between `harness-qa`'s `name:` and its own `domain:` key. True today (verified: the
  intervening `consult-when: >` folded block carries no such literal). The manifest is read-only
  for this flow (D-01) so this is not exploitable now; flagged only so a future manifest edit near
  `harness-qa`'s block is reviewed against this test's anchor assumption.

**must_fix: []** — F-01 is `grade_2` (does not block per the code-risk-grading policy), F-02/F-03
are advisory. **Stage 2 verdict: PASS with notes.**

## Combined

`severity_max: med` (F-01). No `must_fix`. Both stages PASS.
