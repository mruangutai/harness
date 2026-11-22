# QA gate — BUG-2294 T-01, cycle c2 (review_sha 88bf039f, base c1724230)

**BLUF: PASS.** unit (the only kind the bugfix row can require) is satisfied at the pin. The literal T-01 verify ran green: 25 PASS, 0 FAIL, rc 0, 0.93 s. SC-01 and SC-02 keep their natural-RED receipts. The c1 SEC-01 symlink fix has a receipt-audited natural RED against 70981edd (4 assertion failures, no import error) and is green at the pin. No findings.

## Phase 1 (BRIEF/plan only)
Expected tests: the c1 list (a–g) plus the SEC-01 delta. SEC-01 needs: a run symlink to a kept run, a run symlink to an outside dir, a ui/ symlink to an outside dir, dry-run naming no target through a link, prune deleting nothing through a link while still pruning the real run, and link-destination bytes unchanged. All are present, so no Phase 1 gap.

## Pin identity
Pin 88bf039f6ff31edbb1d5a4b2f6620762e3cc095a (commit; e51277a4 is its ancestor; the checkout HEAD equals the pin). The pinned checkout was created with pinned-checkout.py, and I removed it on return. Environment: CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR and HARNESS_AGENT_TYPE were unset.
- At 88bf039f, `prune-run-evidence.py` sha256 is 3ce3bb40…2af9, which matches the red-first "c1 fix GREEN" subject.
- At 88bf039f, `tests/unit/test-prune-run-evidence.py` sha256 is 7f4274f8…cdd22, which matches the red-first c1 test identity.
- At 70981edd, `prune-run-evidence.py` sha256 is d3f2c38e…2fe9, which matches the c1 RED subject.
- At 70981edd, the test file sha256 is f6cfe5ea…ad0b, which matches the first red record.
- At c1724230, `prune-run-evidence.py` sha256 is cd58e0b9…8c0, which matches the base RED subject.
- The remediation delta 70981edd..88bf039f is confined to those two code files, about 84 insertions and 7 deletions.

## Matrix
change_type is bugfix. `always` is `[]`. `when` unit applies if touches_runtime_code, which is true because the bin script changed. `when` integration applies if the fix is confined to tests and contract docs, which is false. `__bug_class__` is an unresolvable placeholder (repo G-08). The floor is therefore unit, and I raised no extra requirement. This was resolved against the full feature diff (P-13).

| kind | required | executed | outcome |
|---|---|---|---|
| unit | yes (touches_runtime_code) | task verify and kind cmd | satisfied |
| integration | no | not run | not required (fix not confined to tests/docs) |
| component, ui, typecheck | no | not run | unresolved runners, surfaces unchanged |
| functional, eval | no | not run | excluded (DEC-187), no criterion |
| omp_session_accessor, handoff_comprehension, issue_types_live | no | not run | locally_run, detect surface untouched |

## Runs at the pin
- Literal verify: `python3 tests/unit/test-prune-run-evidence.py` returned rc 0 in 0.93 s with 25 PASS, 0 FAIL and "all checks passed". The 20 prior checks and the 5 symlink checks all pass. The output was captured to /tmp/qa-c2-verify.txt, which is ephemeral.
- Kind cmd: `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` returned rc 0, 63 files, 22.94 s wall. It includes `PASS test-prune-run-evidence.py` (exit 0, 1.22 s), so list membership is confirmed (P-14). Other tests deliberately print ERROR or Traceback text. I graded on the runner's rc, not on grep (G-08/G-09). The output was captured to /tmp/qa-c2-kind.txt, which is ephemeral.
- The detected unit coverage of this change is the one file tests/unit/test-prune-run-evidence.py, with 25 named checks.

## fail_first (tier: natural RED, retained receipts; I did not rerun the known reds, per assignment)
Receipt: notes/red-first-T-01.md. I audited command, subject sha and test sha against the git objects above.
- SC-01 against the c1724230 pruner: 7 assertion failures, no setup or import error. SC-01 reds are the three whole-record byte-identity checks at test lines 119, 123 and 135, plus the dry-run and exit messages. They are semantic: the changed-file lists name digest.md, state.yaml and .run-identity.json.
- SC-02 against c1724230: the reds are "every cycle_evidence digest survives prune at its recorded hash" (line 250; all ten validate-c0..c9 lost) and "check-state is still clean after prune" (line 252; VIOLATION ... No such file digest.md). The precondition is sound because "check-state is clean before prune" and "empty keep set still exits 0" pass on the base (G-13).
- c1 SEC-01 symlink fix against 70981edd (pruner sha d3f2c38e, test sha 7f4274f8): 4 assertion failures. These are the dry-run line, the prune line, the skipped-names line and the bytes line, at test lines 170, 177, 181 and 183. All 20 earlier checks pass, so the red is not a setup, import or collection error. The dry-run printed `would remove runs/build-alias/ui`, `runs/evil-alias/ui` and `runs/ui-link-run/ui`. The prune run raised an OSError from the subject's own rmtree on the ui symlink. The bytes check read `[[], [], [...]]`, so the kept run's ui/ and the outside run's ui/ were actually deleted. This is signature-present semantic RED, not signature-only. One red (check at line 172) passes on base because dry-run writes nothing. That is expected and not a gap.

## Symlink coverage (symlink_cases, test lines ~138-196)
- A kept-run link: `build-alias -> validate-c2-validator`. It is asserted through dry-run and prune, with the destination bytes compared.
- An outside-run link: `evil-alias -> <tmp>/outside-run`, which holds a ui/.
- An outside-ui link: `ui-link-run/ui -> <tmp>/outside-ui/ui`.
- Dry-run (lines 170, 172) asserts that no `would remove` line mentions the three link names, that the real `build-c0-eng/ui` is still listed, and that all three destination trees are byte-identical.
- Prune (lines 177, 181, 183) asserts rc 0, no `removed` line through a link, and that the real run was pruned. It also asserts that the exact skip lines `skipped runs/build-alias (symlink)`, `skipped runs/evil-alias (symlink)` and `skipped runs/ui-link-run/ui (symlink)` are printed. It compares destination bytes (dict path -> bytes) and requires each to be non-empty, which guards against a vacuous empty comparison (P-08).
- The fix source matches the receipt. `_ui_targets` uses os.path.islink for the run and for ui before isdir. The keep set, --keep, the refusals and the CLI are untouched in the diff (SC-03 is inspection and outside this gate).

## Findings
None.

## coverage_gaps (advisory, none blocking)
- A symlink named in `--keep` is not exercised.
- A symlinked `runs/` parent is not exercised. It is outside the fix's stated scope, so I did not raise it as a finding.
- The `ui-link-run` digest.md bytes are not asserted after the prune. The all-records check in the earlier checks covers the real fixtures, not this one.
- SC-03 is inspection, outside this gate.

## Limits
- I ran the c2 green only, at the pin. I did not rerun the base or c1 reds. I audited their receipts and identities, so the red evidence is retained narrative plus matching hashes, not a fresh reproduction (O-03 tier: natural RED, receipt-based).
- I ran no perturbation or mutation proof beyond the base-versus-fix natural reds.
- The SEC-01 fix landed after the round that raised it. Only my own evidence plus the retained receipt have examined it, so no second reviewer's independence was applied (O-07).
- Product docs/spec.md, decisions.md and architecture.md are absent, and I did not substitute any.
- `check-state --only INV-7` scoping is the settled decision, and I did not relitigate it.
- The pin was removed on return.
