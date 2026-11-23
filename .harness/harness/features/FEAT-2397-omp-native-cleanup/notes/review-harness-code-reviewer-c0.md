# FEAT-2397 code review c0 — FAIL

SC-12's changed-function bar and SC-08's current index rulings remain unmet. Stage 2 is not cleared while Stage 1 fails; runtime inspection found no additional defect.

**Reviewed:** `522c94b2b79e5e2021cb670910772428c17914b0..53a89eb70251d1529dbffd8e50959c4590a032f7`, actual merge-base(origin/main, pin). Build baseline `bdb1c2f68c63bdc7a2b8ba2203db72da80a2abe0`; merge `3912d98a` included. No human-tagged commits or initially modified tracked source. Requirements/evidence read using git show at pin.

## Findings by owner

1. **med / substance / T-03 / SC-12:** `tests/integration/test-check-domain.py:111::_feat2274_cases` grades **2** (CC 8, cognitive 6, ABC 33.5); `tests/integration/test-layout-migration.py:357::_parity` grades **2** (CC 12, cognitive 10, ABC 30.8). Both change executable environment construction. The canonical new-or-worsened gate passes because both grades equal base, but SC-12 explicitly requires every changed test function >=3. Decompose these two scenarios. This is an explicit acceptance obligation, not a generic touch-it-fix-it ratchet or mechanical grade-2 finding.
2. **med / substance / T-05 / SC-08:** `.harness/harness/docs/DECISIONS-INDEX.md:28,72,76-77,93,116-117,158-159,214` retains obsolete ruling tails: Claude `skills:` injection, envelope response, concurrency 20, live settings/INV-9 provisioning, Harness model refusal and compatibility TTLs. DEC-111's row does not identify its strike. Readers selecting affected entries see contracts contradicting rewritten authority. The generator preserves text after ` :: `; regeneration cannot repair it. Rewrite affected <=30-word tails with required durable successors. `notes/t05-doctrine.md` claims this already happened; pinned bytes disprove that claim.

## Inspection criteria

- **SC-04:** `.github/workflows/tests.yml:119` and `tests/integration/test-harness-yaml.py:30` exemplify inspected nine export/two guidance/five reader changes. `notes/T-02-red-green.md:1` records individual red/green targets; HARNESS and existing script/cwd fallbacks survive. Final production-runner receipts remain QA-owned.
- **SC-08:** `.harness/harness/docs/DECISIONS.md:722,3654,5936,6190,7933` reconciles direct context, native model policy, native usage and retained ABI; SPEC §§3–5/7 and native command/rule/org changes agree. Index exception above. Delegated team-config and BUILD historical rulings respected.
- **SC-09:** `.claude/skills/harness/bin/check-domain.py:1818,2598` and the five other named comment-only modules have only comment/docstring baseline diffs. `.claude/skills/harness/bin/inject-expertise.py:12-35` copied bootstrap remains unchanged. `.harness/harness/docs/DECISIONS.md:7933` documents retained request/tool/decision ABI; `.claude/skills/harness/bin/harness_yaml.py:781` retains the live systemMessage branch. Frozen prior fixtures, historical context fixtures and Expertise data have no baseline diff; authored .claude directories, caps, precedence, DEC-108/109 and BUILD history survive. Model helper/call and JSONL fallback are deleted, not shimmed.
- **SC-12:** `notes/t05-verify-literal.txt:1` records cumulative gates, positive discovery of 31 tracked feature records and typecheck. Actual grading below finds two exceptions. Authorized one-line stale allowlist removal is documented in `notes/answers-2026-11-22-allowlist.md:1`.

## Grading and regression evidence

Actually ran `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 522c94b2b79e5e2021cb670910772428c17914b0 --head 53a89eb70251d1529dbffd8e50959c4590a032f7`: **PASSING: 80**, no severity/reason records; canonical **code_grade: pass**. Also compared pinned function executable-body hashes (`code_grade._body_hashes`) and ran `grade_source` on every changed Python path: **155 changed functions**; all eight production functions >=4, including validate-digest `hook_mode` 4 and `_pass_through` 4; exactly the two tests above below 3.

SC-01/02/03/05/06/07 witnesses inspected separately from source: complete frozen context parity and Unicode mutants; in-process four-file drift/error outcomes; carried decoded context/retry/hidden delivery; schema/semantic/held-child refusal and claim retention; unchanged root-negative assertions; config-accessor string-off regression; finite native usage, custom/default strict thresholds, exclusions, repeated wakes and post-domain continuation.

SC-10/11: `notes/research-omp1910-observation.md:1` is Main's credentialled 19.1.0 observation (7/7 exit 0, #2194 CLOSED), not my UAT. Probe blob `81a28131c1e233c415aacdf6162faa9583344236` and companion `8c3e9153faf876d97e3ef4c0c25f6c03a54c1e6d` match the pin exactly. Offline scenario assertions and committed mutants bind identity and numeric acceptance; missing-helper baseline failures alone were not treated as behavioral proof.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** coordinated caller migration has no compatibility shim; retained Python ABI is intentionally not host wiring.
- **Type System Discipline:** inspected host-boundary numeric narrowing and carried decoded context rather than a second response parser.

**Open questions:** none. **Next:** Main resolves T-03/T-05 findings; QA owns final runner receipts. No suites/builds/linters/formatters/live probes run, known failures not rerun, no source edits or pin checkout created.
