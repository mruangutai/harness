# FEAT-1559 pinned code review — cycle 1

**FAIL.** SC-04 has a missing-entry refusal gap in plan discovery. Mandatory Python grading independently fails nine gated functions. General Stage 2 is deferred because Stage 1 failed; grading is the explicitly required independent audit, not a claim that general quality review passed.

Reviewed `e8d868f78a6ec43880598af5c5873f5daa8ba985..0e8301a58a7de7dc23a067005c9aa8b3ee528de0`, using the persona-managed sparse pin. All affected execution lanes below are **main-session-direct**, as signed in the plan. No source changes or test/build/lint runs performed.

## Stage 1: specification

**MED, substance, must fix — SC-04 / D-03 / T-03:** `.claude/skills/harness/bin/check-plan-routes.py:790-795,809-824`. `discover_plans` checks checkout layout and obtains corpus roots, but enumerates only directories actually present. It never compares the owner corpus's reached names against expected tracked names. [INFERENCE from source] In an otherwise converged linked checkout, remove one required landed owner's feature directory while another remains: default discovery can audit the surviving plans and return clean, instead of refusing the missing feature by name before auditing. A full clone has the equivalent gap. This violates SC-04's explicit missing-expected-entry requirement. Use the population/name-set seam before the readability-aware walk; preserve local active-record precedence and existing permission semantics. Security independently confirmed this finding. No mutation probe was run by this reader.

Inspection criteria:
- **SC-11:** inspected `notes/non-regression-receipt.md` and `STATE.md` at the pin; immutable seam `69e3d81987b8a9d7676dbaf0f18674b8bf039579..0e8301a58a7de7dc23a067005c9aa8b3ee528de0` changes only five files inside this active feature directory. Receipt records frozen pre/main endpoints, identical 4635-entry main manifests, full-clone unit 54/0 and integration 86/0, and non-skipped real-owner proof. These are receipt observations, not reruns by this reader.
- **SC-14:** pinned `AGENTS.md:10`, `.claude/skills/harness/SKILL.md:12-20`, `.claude/skills/harness-verification-rules/SKILL.md:66-76`, `.harness/README.md:50-139` distinguish active writes/absolute landed-main reads; exclude siblings, symlink and git-content providers; document local hooksPath and preserve-work/repair/verify/retry/restore recovery.
- **SC-10:** deferred by operator ruling to post-merge issue #2101; not met here, not a defect. T-06 is abandoned. DEC-174 ownership and INV-17 handoff exemption are settled, not findings.

## Mandatory changed-Python grading

Ran the registered control-plane `code-grade.py --base e8d868f78a6ec43880598af5c5873f5daa8ba985 --head 0e8301a58a7de7dc23a067005c9aa8b3ee528de0` from the pin. Exit 1; output `artifact://1628`; 293 passing records. **code_grade: fail.** C/Cog/ABC below are tool measurements, not behavior claims.

Each row is a high substance finding requiring repair of the named gated function, then regrading. Production bar is 4, test bar 3. Production paths are relative to `.claude/skills/harness/bin/`; paths beginning `tests/` are relative to the repository root, not that bin directory. This path transcription correction changes no kind, severity, assessment or verification.

| Path:line function | C/Cog/ABC | Grade; driver | Task / SC |
|---|---|---|---|
| check-instruction-paths.py:99 `_classify` | 7/11/10.0 | 3; cognitive | T-05 / SC-14 |
| feature_corpus.py:152 `reached_feature_dirs` | 10/12/17.5 | 3; cyclomatic+cognitive | T-01 / SC-04 |
| feature_corpus.py:227 `population` | 9/4/19.7 | 3; cyclomatic | T-03 / SC-04 |
| feature_corpus.py:416 `identity` | 10/11/14.9 | 3; cyclomatic+cognitive | T-01 / SC-01,13 |
| feature_corpus.py:438 `claiming_segments` | 10/14/18.8 | 3; cyclomatic+cognitive | T-01 / SC-01,13 |
| feature_corpus.py:461 `derive_cone` | 10/2/15.7 | 3; cyclomatic | T-01 / SC-01,13 |
| worktree-state.py:287 `render` | 8/10/15.4 | 3; cognitive | T-01 / SC-07 |
| tests/integration/test-corpus-non-regression.py:128 `manifest_findings` | 24/40/59.1 | 1; all three | T-05 / SC-06,11 |
| tests/integration/test-feature-corpus-census.py:92 `glob_names` | 11/31/15.6 | 1; cognitive | T-03 / SC-04,13 |

### Nonblocking MED grade-2 findings and reasons

These reasons justify retaining coherent responsibilities rather than splitting solely to change a score. They do not override the high failures above. `grade_2_reasons` in the digest is empty because the aggregate grade is fail.

| Path:line function | C/Cog/ABC; driver | Task / written reason |
|---|---|---|
| check_state/corpus.py:102 `preflight` | 15/14/30.6; cyclomatic+ABC | T-02: one ordered pre-Ctx refusal boundary for identity, layout and selected subject; no mutation. |
| feature_corpus.py:300 `verify_report_findings` | 15/7/23.2; cyclomatic | T-03: one closed parser for known verification report categories, including invalid/unknown fail-closed cases. |
| feature_corpus.py:523 `select` | 10/12/32.0; ABC | T-01: one checkout classification/active-cone orchestration boundary. |
| worktree-state.py:155 `divergent_paths` | 20/20/34.6; all three | T-01: central content-safety classification of every status entry before any mutation. |
| worktree-state.py:197 `diagnose` | 13/12/36.4; cyclomatic+ABC | T-01: collect all independent diagnostic categories instead of hiding later defects behind the first exit. |
| worktree-state.py:311 `main` | 5/8/27.6; ABC | T-01: CLI mode dispatch and stable report output remain together at the entrypoint. |
| tests/integration/f58_sparse_fixture.py:237 `snapshot` | 6/10/27.1; ABC | T-01/T-05: whole filesystem/index/config witness is necessary to prove nonmutation. |
| tests/integration/test-feature-corpus-census.py:60 `Resolver.components` | 19/25/26.7; all three | T-03: the closed AST path-expression grammar is one resolver responsibility. |
| tests/integration/test-feature-corpus-census.py:107 `statement_lines` | 7/18/9.4; cognitive | T-03: nested statement mapping binds markers to their actual enumeration subject. |
| tests/integration/test-feature-corpus-census.py:130 `detected_sites` | 12/18/26.9; all three | T-03: alias resolution plus pattern/site identification forms the census enumeration boundary. |
| tests/integration/test-feature-corpus-census.py:167 `findings` | 8/19/15.6; cognitive | T-03: validates each detected site's closed scope vocabulary and owner-root seam. |
| tests/unit/test-corpus-regression.py:47 `tree_digest` | 11/10/25.8; cyclomatic | T-05: deterministic file/link/index byte witness is necessary for no-mutation assertions. |

No unbound scope changes or operator decisions requested. General Stage 2 and post-fix grading remain prerequisites for an eventual passing review; this report itself changes no source.
