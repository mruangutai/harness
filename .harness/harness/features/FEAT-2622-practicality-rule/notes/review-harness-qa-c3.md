# QA gate: FEAT-2622 validate c3 (run 2026-11-28-04-validate-validator)

**BLUF: PASS, `matrix_ok: true`.** The floor is unit + integration. Both kinds ran once at `0ce1c841f4534e3720e95927d61f43a162aa6a13` and both were green: unit 74/74 files, integration 94/94. Both receipts return `evidence_defects == []`.

- **The fix-round-2 mutant table holds exactly.** Each of the 5 mutants turns exactly one case red, the case the receipt names. BUG-2582's rollup file stays 34/34 under every mutant.
- **MF-1 and MF-2 have natural reds.** At `edcda5be` the two new cases FAIL with "no errors", and those are the only two failures.
- **c2's M10 is now witnessed.**
- **One new advisory mutant is unwitnessed (QA-F4).** It is fail-open, but contrived and no worse than today.

Every probe below was EXECUTED. Mutants were applied in memory: a `/tmp` driver wrapped `harness_boundary.load_repo_module` and exec'd each mutant body into the loaded validate-digest module. A reached-marker fired for every mutant, and a control run gave 36/36 and 34/34. No file was edited. I took the in-memory route because of repo G-06: check-domain refuses QA source edits.

## Policy and pin
- **Policy:** `git show 0ce1c841…:.harness/harness.json` in the harness repo. The feature is unbound.
- **Kinds:**
  - T-01 is `cross_module`, which requires unit and integration.
  - T-02 is `logic`, which requires unit.
  - T-03..T-05 are `docs`, which require no kind.
  - No `when:` predicate applies.
  - typecheck is active but not required, and the diff touches no `.ts`.
- **Managed pin:** `.claude/worktrees/.pins/FEAT-2622-practicality-rule--2026-11-28-04-validate-validator--harness-qa`. HEAD is `0ce1c841`, the tree was clean, and `bun install --frozen-lockfile` ran first. The pin is removed on return.
- **Candidate vs installed:**
  - The candidate `validate-digest.py` at the pin has sha256 `eba413dec69e5506…`.
  - The installed control-plane copy (main `3e979ae3`) has sha256 `c843d51be8693503…`.
  - Every candidate claim here comes from runs in the pin.
- **Interpreter:** this host's Python 3.15.2 on darwin arm64. This is not CI.
- **Commits after the pin:** `git diff --stat 0ce1c841..HEAD` lists only this feature's `feature.json` and `plan.yaml`.

## Runner receipts (DEC-255)
`env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <run>/qa/manifest-<k>.json`, run from the pin.

|kind|receipt sha256|tested_commit|files|runner_exit|evidence_defects|
|---|---|---|---|---|---|
|unit|`86d202cf…`|0ce1c841f4534e3720e95927d61f43a162aa6a13|74/74 expected|0|[]|
|integration|`4fdf72dc…`|0ce1c841f4534e3720e95927d61f43a162aa6a13|94/94 expected|0|[]|

Full output:
- **Unit:** `/tmp/feat2622-c3-unit.log`, 4419 lines, sha256 `840b581d…`. Tail: `pool: 8 workers, 74 files, 82.50s wall` and `unit exit 0`. All 74 `----- test-*.py` headers read `exit 0`.
- **Integration:** `/tmp/feat2622-c3-int.log`, 8586 lines, sha256 `70599f0d…`. Tail: `ALL PASSED.`, `pool: 8 workers, 94 files, 341.88s wall` and `integration exit 0`. All 94 headers read `exit 0`.
- **Expected stderr:** the one `ERROR could not resolve scan root` line is a self-test's expected stderr, followed by `PASS self-test unresolved root refuses`.
- **Files of note:** test-practicality-rule, test-practicality-record-panel, test-validate-digest-plan-rollup, test-code-grade, test-digest-dev-skill, test-plan-merge, test-validate-digest and test-typescript-typecheck are all `exit 0`.

## Probe 1: the fix-round-2 mutant table, re-measured
`test-practicality-rule.py` has 36 checks. The carve-out cases live there (L239-262) and in `test-validate-digest-plan-rollup.py`, which has 34 checks.

|mutant (in `_open_row_reason`/`_carveout_inputs`)|red cases, practicality|rollup|receipt claim|
|---|---|---|---|
|Ma drop the row-discount conjunct|1: `row-plausible-current-discounted-denied`|34/34|matches|
|Mb current check on severity only|1: `current-plausible-med-denied`|34/34|matches|
|Mc current check on exposure only|1: `current-discounted-high-denied`|34/34|matches|
|Md drop the presence conjunct (`current and`)|1: `no-current-finding-denied`|34/34|matches|
|Me drop the `must_fix` check|1: `team-mustfix-denied`|34/34|matches|

No mutant stays green, and no count differs from the receipt.

## Probe 2: fail-first for the MF-1 and MF-2 closures (natural red)
I ran `git archive edcda5be…` (`.claude/skills/harness`, `tests`, `.harness/harness.json` and `team-config.yaml`) into `/tmp`, with the pin's `test-practicality-rule.py` placed over it (sha256 `de8e8f95…`).

Result: rc=1, `FAIL 2 of 36 checks failed: practicality-carveout-no-current-finding-denied, practicality-carveout-team-mustfix-denied`. Both reds are semantic (`no errors`), meaning edcda5be relieved both. The other three new cases pass at edcda5be. They are leg witnesses, not regression fixes, and Probe 1 proves they discriminate.

## Probe 3: c2's M10
**Now witnessed.** M10 is "current conjunct keeps severity, drops exposure", and this round's Mb is the same mutant. Under Mb, `practicality-carveout-current-plausible-med-denied` (L250) turns red.

I re-ran c2's relief probes, all executed:
- **At the pin:** P3 plausible-med, P4 unrated, P5 adversary-med and P6 malformed exposure are all denied. P7 disc-low and P8 both-discounted are relieved.
- **Under Mb:** P3, P4 and P5 flip to relieved. P6 stays refused by the schema.

## Probe 4: BUG-2582 and code-grade
Both files are green at the pin, run directly from the pin:
- `tests/unit/test-validate-digest-plan-rollup.py`: rc=0, 34/34.
- `tests/unit/test-code-grade.py`: rc=0, 1034/1034.

Both are also `exit 0` in the unit receipt run.

## Findings (advisory; QA's gate is green)
- **QA-F4: the `all()` quantifier over same-PF-id current findings is unwitnessed.** kind: substance; owner T-01; severity low.
  - Mutant Mf replaces `all(map(_discounted_non_gating, current))` with `any(...)`. Both test files stay green.
  - The fail-open probe: two current findings share one PF id (same reader and summary), one DISCOUNTED med and one PLAUSIBLE high. Under Mf they are relieved with zero errors, in either order (P1/P2). The pin denies them.
  - why: exposure {trigger: contrived (needs a future edit to the quantifier, plus a digest with duplicate-identity findings), vs_today: no_worse (the pin and edcda5be deny it), control: harness}.
  - Under the practicality rule this is at most med. It is not must_fix and not a reason for a new round (VAL-OQ-04).
- c2's QA-F2 (PF-id case) and QA-F3 (SC-15 text) are already ruled. They are not re-raised.

## Fail-first (`verify: automated` SCs)
|SC|test|pre-fix red|
|---|---|---|
|SC-01|tests/unit/test-practicality-rule.py:115-124|pin test over `git archive 3e979ae3`: 5 schema cases + wellformed FAIL (notes/review-harness-qa-c2.md, reproduced c2; L1-204 byte-unchanged since)|
|SC-02|:140-153|base: all 8 FAIL (qa-c2); medmax-capped isolated by c2 M2|
|SC-03|:167-170|base: all FAIL (qa-c2)|
|SC-04|:174-185|base: all 6 unrated cases FAIL (qa-c2)|
|SC-05|tests/unit/test-practicality-record-panel.py|base + pin test: 5 FAIL (qa-c2); file unchanged edcda5be→0ce1c841|
|SC-13|gen-agent-output.py --check; tests/unit/test-digest-dev-skill.py|c1 at `0daddfc4`: 6× DRIFT, 3/12 refused (notes/review-harness-qa-c1.md); subject unchanged|
|SC-14|tests/integration/test-plan-merge.py `case_f59_record_panel_writes_from_a_lead_digest`|notes/fail-first-T-02.md (rc=5 "missing exposure"); plan-merge unchanged|
|SC-15|test-practicality-rule.py:196-262|base: 6 FAIL (qa-c2). MF-1 (c2): stale-row-denied red at `d131c231`. **This round:** `no-current-finding-denied` + `team-mustfix-denied` red at `edcda5be` (Probe 2, this note)|

## Principles applied
- **Build the Lever:** one `/tmp` in-memory mutant driver covers 7 mutant configurations (control, Ma–Mf) across both test files and the probe script. It edited no source, and it was deleted on return.
