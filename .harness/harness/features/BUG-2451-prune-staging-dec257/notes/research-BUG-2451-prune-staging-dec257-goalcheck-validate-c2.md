# Goal-check — BUG-2451 validate c2 (harness-pm)

**BLUF: PASS. At review_sha b7e1f26e both perspectives are discharged. SC-01..SC-04 are met, and MF-1 is fixed in the code itself, not only in the tests. `_unreadable_dirs` now walks every recorded run, ui/ included, and names every directory it cannot list, before any mutation, in both modes, and still follows no link. The shipped refusal sentence is now true of the code. D-01 / DEC-238 amend is met, and all five keep rows are untouched. There are no must-fix findings. There are four advisories. Two of them are boundary probes beyond SC-02's literal contract, and both show behaviour that predates this fix.**

Pin: b7e1f26ecfdff7683d25009435a30098c5580c52.
- Every read below is `git show b7e1f26e:<path>`, or a `git archive b7e1f26e` extracted to `/tmp/bug2451-c2-pm-arc`. I did not read the control-plane copy.
- `git diff --stat 10823d58 b7e1f26e` touches only FD (`feature.json` and `plan.yaml`).
- `git diff --stat e83c4e20 b7e1f26e` outside FD lists exactly T-01's five files.
- **fix-c1 changed no text surface.** `git diff --stat b2c1f55e b7e1f26e -- .harness/harness/docs .omp` is empty, so DECISIONS.md, DECISIONS-INDEX.md and harness-ship.md are byte-identical to the c1 pin. fix-c1 touched only the pruner (its docstring and `_unreadable_dirs`), the test and FD.
- Product docs/spec.md, decisions.md and architecture.md are absent; this is not a finding (BRIEF `## Constraints`).

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | pass | SC-02, SC-03 | `main` runs `_pre_mutation_refusal`, which exits 2. It then runs `_unreadable_records`, which exits 1. Only then does it call `_prune`, so both checks come before any mutation, with or without `--dry-run`. The walk covers ui/ (`_unreadable_dirs`). The DEC-238 bullet and the ship paragraph equal 5e51124e plus the one refusal sentence, and the sentence is now true of the code. |
| code maintainer | pass | SC-01, SC-04 | The regression reddens on assertions against both 47d6c54d (12 FAIL) and b2c1f55e (4 FAIL), and greens at the pin. No staging code remains. Retention, refusal, symlink and CLI coverage is kept. |

## Success criteria

All runs used HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR cleared. The test file's sha256 was 291b798e…931d, matching the fix record.

- **SC-01 met (automated).**
  - At the pin: rc 0, `all checks passed`, 52 PASS out of 52 checks. All three T-01 verify lines are present (`grep -Fx`), and `gen-decisions-index.py --stdout` equals DECISIONS-INDEX.md.
  - Against the 47d6c54d pruner (sha256 55df0581…a93ef) via PRUNE_RUN_EVIDENCE_BIN: rc 1, `12 failure(s)`. Every failure is an assertion. They include the audit-hooked `git add -f` Popen, the unhooked `prune leaves the real git index byte-identical` (`index 9148 -> 8663 bytes`), and the five-file check on the subject's own text.
- **SC-02 met (automated, grade taken from the code).**
  - **The code.** `_unreadable_dirs` is now `for _walked in os.walk(run_dir, onerror=note): pass`. The `dirs.remove("ui")` line is gone, so every directory `os.walk` fails to list under a recorded run is collected and named, ui/ included. `followlinks` stays False, and a linked run directory is skipped before the walk. Unchanged lines in `main` order the steps: `_pre_mutation_refusal` (exit 2), then `_unreadable_records` (exit 1), then `_prune`. That order is the same with or without `--dry-run`.
  - **The test.** `unreadable_ui_cases` covers three cases: chmod 000 on a kept lane's `ui/evidence`, on a pruned ui/ itself, and on a pruned lane's subdirectory. Checks:
    - each mode exits 1 with every directory named;
    - after each mode, the readable bytes and the index are unchanged;
    - after the permissions are restored, the whole feature tree is byte-identical.
  - **RED measured.** The b2c1f55e pruner (sha256 0237578f…ed) gives rc 1 with exactly these 4 FAILs: dry-run rc 0 naming nothing; prune deleting a lane and then crashing with a traceback; the two immutability checks. The other 48 PASS.
  - **pm probes.** P4: a recorded run directory at 000 is named in both modes and nothing changes. P1b: a recorded `ui/evidence` at 0o300 is named in both modes and nothing changes.
- **SC-03 met (inspection).**
  - The DEC-238 bullet at DECISIONS.md:8152 differs from 5e51124e by exactly one inserted sentence after `PLACEHOLDER_UNSET` value. I checked this with difflib on the literal text, with no whitespace folding.
  - The whole harness-ship.md differs from 5e51124e only by one sentence inserted after "empty or a placeholder." (lines 51-53).
  - The sentence occurs once on each surface.
  - The pruner docstring (lines 19-29) states deletion only, "never runs git or touches the index", both exit codes, "dry-run included" and "its ui/ included".
  - The index regenerates identically.
- **SC-04 met (inspection).** fix-c1's pruner diff is limited to the docstring and `_unreadable_dirs`, so argparse, `keep_set`, `_ui_targets` and the refusals are unchanged from c1. The test still holds the retention, --keep, review-pin, symlink and FEAT-2229 cases. harness-ship.md is byte-identical to the c1 pin, so the step order, both invocations and the commit name (`[harness:human] <flow-id>: prune run evidence at ship`) are unchanged.

## Decision dispositions (DECISIONS.md at b7e1f26e)

The only DECISIONS.md hunk between e83c4e20 and the pin is @@ -8156, inside DEC-238 (DEC-238 starts at line 8140; the next DEC starts after line 8156).

| Row | Verdict | Evidence |
|---|---|---|
| DEC-238 amend (D-01) | met | The `**Ship keeps the record and drops the rest.**` bullet at line 8152 equals the 5e51124e text plus exactly one sentence naming both refusals. The index regenerates identically. Owner: T-01. |
| DEC-174 keep | met | The clause is at line 4521 and the heading at line 4479, both outside the hunk. |
| DEC-179 keep | met | The clause is at line 4851, outside the hunk. |
| DEC-225 keep | met | The clause `with no panel and no goal-check run` is at line 7511, outside the hunk. |
| DEC-254 keep | met | The clause is at line 8423, outside the hunk. |
| DEC-257 keep | met | The clause is at line 8666, outside the hunk. The index row text is unchanged; only its anchor moved, from @8663 to @8661. |

## c1 findings — rulings

- **MF-1: resolved.** The code change and a test that reddens against b2c1f55e are both described above. The test asserts exit 1, every directory named, no file change and no index change in both modes.
- **MF-2: resolved.**
  - The restoration check is literal: `restored()` must equal the section exactly. My independent difflib comparison against 5e51124e agrees.
  - `pruner_claims` and the whole-file scan read TOOL. The 47d6c54d run flags the subject's own `force-stag` and `git add`.
  - The exclusions are the DEC-257 section, the DEC-257 index row and the test's `FORBIDDEN` literal. These are exactly T-01's carve-out: "unchanged historical DEC-257 text or tests that negatively assert absence". DEC-257 is unchanged at the pin.
- **QA-F1: resolved for normal mode, residual for dry-run.** The unhooked normal-mode leg has a natural RED (9148 → 8663 bytes). The dry-run leg still has none, because 47d6c54d's dry-run never wrote the index. That cannot be repaired by a test.
- **QA-F2: resolved.** The line always prints, and it printed FAIL against 47d6c54d.
- **QA-F3: resolved.** `dry_run_cases` and both dry-run legs compare `tree_bytes(feat)`, which covers the whole feature with feature.json included.

## Advisories (none must-fix; all bind T-01)

- **A-1 (substance, low; beyond SC-02's literal contract; behaviour predates fix-c1).** A recorded pruned `ui/evidence` set to 0o400 (readable but not traversable) or 0o500 (not writable) is not refused. Dry-run exits 0, and prune deletes part of the first lane and then crashes with a traceback (probes P1 and P6). Failure scenario: a mis-permissioned lane leaves a half-pruned ui/ and a traceback. SC-02 says "unreadable", so this is advisory.
- **A-2 (substance, low; outside "under recorded runs"; behaviour predates fix-c1).** An unreadable directory in an *unrecorded* run's ui/ is not walked. Prune removes earlier lanes and then crashes in `rmtree` (P2). The refusal sentence says "under a recorded run", so the docs stay true.
- **A-3 (form, low; introduced by fix-c1).** The forbidden-phrase scan now covers all of DECISIONS.md except DEC-257, and all of harness-ship.md. That is wider than intent's "changed current text". Failure scenario: a future, unrelated decision or ship step that writes "git add" turns this unit test red in another feature.
- **A-4 (form, low; record accuracy).** The fix record (red-first-T-01.md, `### GREEN`) claims 55 PASS at the fixed pruner. I measured 52, and 48 + 4 = 52 on the b2c1f55e run as well. Its RED counts (48/4 and 40/12) match my runs exactly.

## Prior open questions

- **OQ-1 (DEC-225 wording): still open, non-blocking.** DEC-225's text is unchanged at the pin. Its "no goal-check" and "execution_mode: team" wording still conflicts with this validate goal-check and with T-01 running main-session-direct. This is outside T-01's scope.
- **OQ-2 (hooked run without `--root`): behaviour resolved by pm measurement; coverage residual.** I ran P3: no `--root`, cwd inside the feature, under the audit hook, with no git repository. It gave rc 0 and started no subprocess in both modes. No test exercises this path.

## Principles applied

- harness-pm P-06: I re-measured MF-1's premise at the pin, both in the code and against the b2c1f55e pruner, without relying on the green suite.
- harness-pm P-19 / O-12: I ran boundary probes P1, P2, P4, P6 and P3 rather than reasoning about them; they produced A-1, A-2 and the OQ-2 closure.
- harness-pm P-16: I graded the shipped refusal sentence against measured behaviour. It is now true.
