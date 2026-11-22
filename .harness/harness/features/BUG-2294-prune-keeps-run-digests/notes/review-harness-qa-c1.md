# QA gate — BUG-2294 T-01, cycle c1 (review_sha 70981edd, base c1724230)

**BLUF: PASS.** unit (the only kind the bugfix row can require) is satisfied; SC-01 and SC-02 have independently reproduced natural RED (assertion failures, no setup/import error) against the exact base pruner and GREEN at the pin. No findings.

## Phase 1 (from BRIEF/plan only)
Expected tests: (a) non-kept run loses only ui/; digest.md/state.yaml/.run-identity.json/non-UI sibling bytes unchanged, run dir kept; (b) kept-run ui/ survives; (c) dry-run writes nothing; (d) absent ui/ ok; (e) repeat prune ok; (f) FEAT-2229 shape: 10 runs, hash-bound cycle_evidence digests, final BLOCKED, no UI, empty keep: digests survive, check-state exit 0 before and after; (g) refusals unchanged. All present in the test file; no Phase 1 gap.

## Matrix
change_type bugfix: always `[]`; when unit if touches_runtime_code (true: bin/prune-run-evidence.py changed); integration only if fix confined to tests/docs (false); `__bug_class__` placeholder unresolved (repo G-08). Floor = unit. Environment: CLAUDE_PROJECT_DIR/HARNESS_PROJECT_DIR/HARNESS_AGENT_TYPE unset.

## Runs (pinned checkouts, detached, HEAD never moved)
- Pin 70981edd (persona harness-qa); base pin c1724230 (persona harness-qa-base).
- Task verify `python3 tests/unit/test-prune-run-evidence.py` -> rc=0, 20 PASS, 0 FAIL, "all checks passed".
- Kind cmd `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` -> rc=0, 63 files, 22.8s; includes `PASS test-prune-run-evidence.py` (list membership confirmed, repo P-14).

## fail_first (own reproduction, tier: natural RED, same test file sha256 f6cfe5ea…ad0b as red-first-T-01.md)
Command: `PRUNE_RUN_EVIDENCE_BIN=<base-pin>/.claude/skills/harness/bin/prune-run-evidence.py python3 tests/unit/test-prune-run-evidence.py` (base pruner sha256 cd58e0b9…8c0, matches note) -> rc=1, "7 failure(s)", no Traceback/ImportError. Matches red-first-T-01.md lines 6-67.
- SC-01 reds (assertion diffs on destructive scope): "every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune" (test:119), "a repeated prune still leaves every run record byte-identical" (:123), "an explicit --keep prune leaves every run record byte-identical" (:135), plus message assertions "dry-run names exactly the ui/ lanes…" (:105) and "exit 0 and names the ui/ it removed". Semantic, not signature-only: base deleted whole run dirs, changed-file lists name digest.md/state.yaml/.run-identity.json.
- SC-02 reds: "FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash" (:191; all ten validate-c0..c9 lost) and "FEAT-2229 shape: check-state is still clean after prune" (:193; VIOLATION ... No such file digest.md). Precondition sound: "check-state is clean before prune" and "empty keep set still exits 0" PASS on base (G-13 satisfied, red is the actual regression not an empty state).
- Evidence: this note; red-first-T-01.md; own captures /tmp/qa-c1-red.txt, /tmp/qa-c1-green.txt (ephemeral).

## Notes
- check-state scoped `--only INV-7` is the settled decision; not relitigated.
- Absence/mutant: byte-hash comparisons over named sentinels, not counts, bind the subject (P-08). Perturbation proof beyond base-vs-fix not run; gate-only dispatch.
- SC-03 is inspection; outside this gate.
- Product docs/spec.md, decisions.md, architecture.md: not consulted as guidance (absent at intake; `docs/` holds only unrelated files).
- Pins removed on return.
