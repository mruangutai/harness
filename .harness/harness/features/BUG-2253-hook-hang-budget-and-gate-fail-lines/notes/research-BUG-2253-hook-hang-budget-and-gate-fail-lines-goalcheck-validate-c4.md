# BUG-2253 goalcheck — FAIL

SC-01 remains partial: a captured same-name PASS can still hide a genuine failing file. SC-02 meets its bounded acceptance contract. Read-only assessment of base 3dd8bb677bb2936361e3952030fc24f15bf9afc6 through pin 645febc89615f9a508a5cc66122a02a80ddabaac, run 2026-11-21-04-validate-validator; no production, test, plan or approval edits.

## Perspectives

- **operator — PARTIAL (T-01 / SC-01).** Buried files, names with spaces, and the prior unmatched-header counterexample have discriminating red/green evidence. However, a captured `PASS outer.py` consumes the enclosing failing file's header, so its genuine `FAIL outer.py` is omitted. Pinned gate `.claude/skills/harness/bin/validate-digest.py:2512–2525`; producer `.claude/skills/harness/bin/run_pool.py:107–113`; regressions `tests/integration/test-validate-digest.py:6415–6459` omit this case.
- **code maintainer — PASS (T-01 / SC-02).** Six actual enclosing call sites observe 30, 0.05 and 0.10; six real helper/subprocess probes require readiness, TimeoutExpired and call time below 1.5s. The watchdog now enumerates and kills direct children from its 2s deadline independently of readiness; subprocess.run owns reaping. Delayed/never-ready containment rows require SIGKILL, no readiness and elapsed below 5s. Pinned tests `:6495–6550`, `:6570–6675`; supplied `notes/receipts/red-c3.stdout:40–65` and `green-c3.stdout:4–17` carry behavioral evidence, not source-count assertions.

## Ranked findings

1. **kind: substance; severity: high; scope: T-01 / SC-01.** A file can echo its own name in a passing verdict before its real failing verdict. Exact combined output: `----- outer.py (exit 1, 0.30s) -----`, then captured `PASS outer.py`, then producer `FAIL outer.py`, followed by more than 20 passing/tail lines. `_closes_failed_block` pushes outer.py, pops it on the captured PASS without consulting the header's exit status, and ignores the genuine FAIL because no matching header remains. `_run_pool_file_lines` therefore omits the failing file from the diagnosis; the tail buries it. run_pool prints captured output verbatim, so this input requires no producer-format change. This is a pinned-source deduction, not an executed probe. The exact earlier unmatched-header scenario is repaired; general diagnostic acceptance is not. No remedy or additional rework round is authorized by this note.

## Evidence and limits

- Literal T-01 verify: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`. PM executed no tests, probes, lint, grading or builds.
- `red-c3.txt` records exact-base production with final regressions carried back and the six base call expressions restored: exit 1 / 14 failures. `red-c3.stdout:1–38` exposes buried/echoed diagnoses; `:40–63` separately exposes all six budget and block rows. Some block rows fail with downstream exceptions after watchdog termination; the independently recorded `[3, 3, 3]` observations are the unambiguous base budget discrimination.
- `discriminate-c3.txt/stdout` records final tests against cycle-1 gate 6cbdc417: only the echoed-header case fails. This discriminates the production parser repair, NOT the earlier watchdog: the transplanted test file already carries the repaired watchdog.
- `green-c3.txt/stdout` records b228c3a225fd2baaf5e2a12ec704a5b7f2aeb276: selected 17 rows, exit 0 / 10.89s. `green-c3-full.stdout:485–504` includes all 17 rows and ALL PASSED; full-file exit 0 / 22.59s. A read-only immutable comparison shows b228c3a2 to the review pin changes only feature receipts and simplify-pass.md, permitting evidence transfer without claiming re-execution. Neither selected group nor full integration file is the complete integration kind.
- `_print_independent_run` retains ordered/duplicate source rows, conditional heading and the original last-20 lines; refusal remains return 2 and launch/timeout policy is unchanged (`validate-digest.py:2475–2492,2499–2552`). Existing buried/fallback tests cover those paths but not the finding above.
- **Advisory; kind: substance; out of scope:** unit-kind coverage is separately filed as #2281 by operator decision. No new blocker or scope request. **Advisory; kind: substance; out of scope:** unchanged runner-launch fail-open policy remains outside this patch.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md were recorded absent. No guidance was invented. Operator rework extension remains authoritative; no BRIEF or plan amendment is proposed.

## Principles applied

- **Attack the Premise:** do not equate header-shaped text with producer authority; following the prior counterexample through a same-name captured PASS reveals a remaining diagnostic failure rather than inheriting suite-green assurance.
- **harness-verification-rules:** grade each clause using discriminating behavioral evidence; distinguish supplied execution from PM inspection and gate-repair discrimination from transplanted-test behavior.

Open questions: none. Disposition: SC-01 partial / SC-02 met; return the concrete in-scope diagnosis gap to the validator lead for operator disposition, without reopening settled unit scope.
