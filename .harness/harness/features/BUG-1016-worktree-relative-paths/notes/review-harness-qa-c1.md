# QA gate — BUG-1016, pin 8211687f (cycle 1)

**BLUF: PASS.** Matrix floor met (`unit` satisfied), both task verifies green on my own run, every automated SC-01..06 maps to a named red-first case in the retained receipt. Only my own evidence plus the receipt; the red-first run itself is the main-session's retained capture, not reproduced by me (assurance: receipt-tier, O-03).

## Identity
Worktree HEAD fe8c50ea. `git diff 8211687f..HEAD` (tests, .omp, docs, .claude/skills, harness.json) empty and status clean for those paths; only feature.json re-pin differs plus untracked notes/handoff-build.md. Files I ran are byte-equal to pin. No checkout, no source changes.

## Phase 1 (from BRIEF/plan only)
Expected: per-tool relative rooting (6 tools), list entries, edit section/MV, omitted/null default for grep/glob/ast_grep with blank passthrough, resolver authority (unique/no-match/ambiguous/error/unusable/spoof/cache), absolute/~/scheme untouched + BUG-2003 URI pre/post incl. mixed edit, silent success + main/Bash untouched. All have a test (below). No Phase 1 gaps.

## Matrix (harness.json)
- T-01 `bugfix`: always `[]`; `unit` when `touches_runtime_code` (diff touches `.omp/extensions/harness-hooks.ts`, runtime) → **required, true**. `integration` when `fix_confined_to_tests_and_contract_docs` → false (production adapter changed). `__bug_class__`/`match_bug_class`: unresolved placeholder (repo G-08), fires nothing.
- T-02 `docs`: always `[]` → no kind.
- Required kinds: `unit` only. Others: functional excluded (DEC-187), eval excluded, integration not triggered, component/ui unresolved but not in matrix, locally_run probes' detect surface (tests/manual/**) untouched, `typecheck` unresolved (cmd null) and not in matrix.
- Gap stated honestly: **no TypeScript typecheck runner exists**; BRIEF Verification gaps sanctions it. SC-07 for TS is inspection, not a typechecked proof.
- `matrix_ok: true`.

## Gate execution (mine, once, `env -u HARNESS_AGENT_TYPE`)
- T-01 `python3 tests/unit/test-omp-hooks.py`: exit 0, **123 pass / 0 fail**, 545 expects, 4.9s (<60s). Same count as the orchestrator receipt (not relabelled; that was at c2d4d7b6/10f38a42).
- T-02 `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`: diff exit 0, no output.
- Standing kind cmd `.agents/skills/harness/bin/run-unit-tests.py --kind unit`: exit 0, 44 files, 11.6s; `PASS test-omp-hooks.py` is inside it (P-14 membership confirmed, line 1893). The `FAIL BUG-1290 5a/5b/5c` lines are the known deliberate mutation-proof prints (repo G-09), not failures; graded on exit code.

## Fail-first audit (receipt: notes/t01-receipts-main-session.md:8-24; 109 pass / 14 fail against the unmodified adapter, fixture-only extended)
Receipt lines name the 14 red cases; test line numbers verified at pin in tests/unit/omp-hooks.test.ts.
| SC | covering cases (line) | red-first receipt line |
|---|---|---|
| SC-01 | 1320, 1338, 1347 | receipt :8, :9, :10 |
| SC-02 | 1400, 1505 | :13, :20 |
| SC-03 | 1357, 1369 | :11, :12 |
| SC-04 | 1432, 1448, 1455, 1477, 1488, 1495 | :14-:19 |
| SC-05 | 1529, 1505 | :21, :20 |
| SC-06 | 1382, 1545 (controls); governed rewrite path red via 1320..1495 | controls :26; rewrite red :8-:21 |

Supporting: mutation checks (receipt :30: 7 mutants each reddening ≥1 case, no-match-rewrites 12) and real-resolver smoke (:34). Controls 1382 and 1545 passed pre-change and are correctly labelled controls (:26), not red-first.

## Findings
- F1 · kind **substance** · severity **low** · T-01 · SC-06 has no dedicated red-first case. Its two named cases (1382, 1545) are controls that passed before the change; BRIEF asks to "demonstrate the new governed rewrite path failing first", which is carried by the shared rewrite cases. 1545 asserts only that `post` returns undefined for a rooted write/edit; the pre-hook return shape is pinned by the `toEqual` revised-input assertions elsewhere, so silence is bounded, not absent. Intent met; accepting as advisory.
- F2 · kind **form** · severity **low** · T-01 · receipt shows red-first counts and case names but not the command/exit line (e.g. `bun test` invocation) beside them; the retained capture is a pasted excerpt. Names are matchable to the 14 test titles at pin, so the binding is checkable.
- Not mine, per assignment: pre-existing `ast_edit` omission from the mutation set (receipt :39) and simplify F1 fixture reuse (flag-only). Not re-raised as defects.

## Principles applied
None cited from leaves (none read).

## Residual
SC-07 is inspection, owned by other readers. I did not perturb tests myself; mutation evidence is the receipt's.
