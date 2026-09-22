# FEAT-63 final goal-check — validate c0

Reviewed SHA: `4066581f6cec2d6eab1fc5094740c13a8d144d7f`  
Comparison baseline for SC-01/SC-06: `950b2f04ae9d73c6ed2bf5fee261287b396c761f`

## Verdict

**FAIL.** SC-01 through SC-05 are met at the pinned SHA. SC-06 is not met: two pre-existing quiet-behavior rationales were rewritten rather than moved byte-for-byte. Because the approved Brief requires every SC to be met, the feature has not delivered its reader perspective.

The disclosed behavior in `notes/build-divergences.md:48-90` was treated as authoritative: eleven post-bootstrap launches use `Ctx.spawn`; the bootstrap probe remains direct because it precedes `Ctx`; `RepoModuleError` covers load, by-name import, and call boundaries; INV-17/21/28/44 use `Ctx.record_error`; `harness_boundary.py` is frozen at six; D-1 is accepted.

## Perspective coverage

- **operator — pass — SC-01, SC-02:** all eight pinned checker suites passed; the only visible divergence is the accepted INV-23 CANNOT RUN behavior, and the subprocess/cache behavior is implemented at the accepted eleven-plus-bootstrap split.
- **code maintainer — pass — SC-03, SC-04:** the typed repository-module boundary and zero checker broad-catch state are exercised, while one AST census enforces the per-file ceilings and permits reductions.
- **reader — fail — SC-05, SC-06:** the shared-source audit is complete and discriminating, but the signed byte-preservation promise for silence rationales is false at two inspected sites.

## Success-criterion outcomes

| SC | Verdict | Method | Exact pinned evidence |
|---|---|---|---|
| SC-01 | met | automated | QA's scoped receipt records exit 0 for all eight suites at `notes/review-harness-qa-c0.md:11-18`. The discriminating accepted case is `4066581f:tests/integration/test-check-state-feat59.py:1027-1043`, which requires one NOTE-level INV-23 CANNOT RUN line and rejects the 300 fallback. Baseline and post-task stream receipts, with D-1 as the only ruled divergence, are recorded at `notes/build-divergences.md:7-46`. |
| SC-02 | met | automated | QA records all eight checker suites green at `notes/review-harness-qa-c0.md:11-18`; missing `gh` and unauthenticated `gh` remain quiet in `4066581f:tests/integration/test-check-state-inv26.py:225-232` and `4066581f:tests/integration/test-check-state-entry.py:703-715`. Source inspection confirms the accepted bootstrap exception at `4066581f:.claude/skills/harness/bin/check-state.py:42-54`, the sole `Ctx.spawn` boundary and cached `gh_ok` at `:546-583`, shared cache use at `:3385-3392,3528-3537`, and runner reuse of `ctx.git_top` at `:4608-4612`. `Ctx.spawn` returns `None` only from `except (OSError, subprocess.SubprocessError)` at `:570-575`. |
| SC-03 | met | automated | QA records `python3 tests/unit/test-harness-boundary.py` green at `notes/review-harness-qa-c0.md:21`. The behavioral cases at `4066581f:tests/unit/test-harness-boundary.py:518-599` cover structured/chained causes, registered and unregistered execution, absent loader/path, registration restoration, by-name load, call failure, success, `KeyboardInterrupt`, and `SystemExit`. The implementation wraps all `Exception` from spec/import/exec at `4066581f:.claude/skills/harness/bin/harness_boundary.py:369-427`, restores registration on `BaseException` at `:418-425`, and wraps call failures while allowing process control through at `:430-441`. QA's live census found zero checker broad catches (`notes/review-harness-qa-c0.md:22-25`). |
| SC-04 | met | automated | QA records `test-check-plan-routes.py`, `test-check-state-table.py`, and the live audit green, with `0 consolidation finding(s) under bin/`, at `notes/review-harness-qa-c0.md:19-25`. The one AST count path, checker ceiling 0, `harness_boundary.py` ceiling 6, per-file comparison, reduction acceptance, and increase rejection are at `4066581f:.claude/skills/harness/bin/check-plan-routes.py:2144-2221`; discriminating checker +1, legacy +1/-1, non-transfer, and new-file mutants are at `4066581f:tests/integration/test-check-plan-routes.py:2755-2802`. |
| SC-05 | met | automated | QA records the integration audit green at `notes/review-harness-qa-c0.md:20,22`. Both loaders are in the shared-source set at `4066581f:.claude/skills/harness/bin/check-plan-routes.py:1788-1795`, and isolated `load_feature_json`/`load_harness_json` reparses must produce named findings at `4066581f:tests/integration/test-check-plan-routes.py:2741-2752`. The accepted one-parse exception reuse is implemented by `Ctx.record_error` and consumed by INV-17/21/28/44 at `4066581f:.claude/skills/harness/bin/check-state.py:774-778,1879,2403,2626,4366`. |
| SC-06 | not_met | inspection | The comparison below found two non-byte-identical rewrites at `4066581f:.claude/skills/harness/bin/check-state.py:702-705,2458-2460` versus baseline `950b2f04:.claude/skills/harness/bin/check-state.py:669-674,2412-2415`. Adjacency remains, but byte preservation does not. |

## SC-06 source-inspection ledger

| Quiet behavior | Baseline source | Pinned source | Result |
|---|---|---|---|
| GitHub authentication unavailable/unauthenticated records nothing | `950b2f04:check-state.py:3086-3095` — “gh absent or unauthenticated … records nothing. Same posture as INV-25's git-absent branch.” | `4066581f:check-state.py:562-575` — the same rationale is adjacent to the narrowed `Ctx.spawn` handler | pass |
| INV-26 board read failure records nothing because the network is not the tree | `950b2f04:check-state.py:3146-3161` | `4066581f:check-state.py:3159-3174` — unchanged rationale remains immediately above `except _gb.BoardError` | pass |
| INV-30 does not double-report an unparseable feature record | `950b2f04:check-state.py:3449-3457` | `4066581f:check-state.py:3454-3459` — unchanged two-line rationale remains adjacent to the `ctx.record` guard | pass |
| INV-24 does not double-report a feature-record parse failure | `950b2f04:check-state.py:2412-2415` — `the parse failure is already a violation elsewhere; do not double-report` | `4066581f:check-state.py:2458-2460` — rewritten as `absent, or the parse failure is already ...` | **fail: not byte-for-byte** |
| Era lookup stays quiet when harness configuration is invalid because `cj` owns the finding | `950b2f04:check-state.py:669-674` — `The JSON-validity violation is raised on its own merit further down (`cj`).` | `4066581f:check-state.py:702-705` — replaced with two new lines beginning `No config, or one that does not parse...` | **fail: not byte-for-byte** |

## Findings

| id | severity | kind | reader | task/location | concrete failure scenario |
|---|---|---|---|---|---|
| PM-63-01 | med | spec-compliance | harness-pm | T-02 / `.claude/skills/harness/bin/check-state.py:702-705,2458-2460` | A maintainer comparing the narrowed quiet paths with the signed baseline sees newly broadened/reworded explanations rather than the promised preserved rationale, so source inspection cannot establish that only the handler boundary changed. Restore the original rationale bytes beside each replacement guard; any new absent-case explanation can remain as separate prose. |

## Evidence qualification

QA's current scoped gates are green, so SC-01 through SC-05 have direct present-state behavioral evidence. QA separately reports an unconfigured `refactor` matrix entry and missing retained fail-first receipts at `notes/review-harness-qa-c0.md:27-57`; those release-process findings do not falsify the exercised SC outcomes and remain owned by the QA reader.

Open questions: `[]`
