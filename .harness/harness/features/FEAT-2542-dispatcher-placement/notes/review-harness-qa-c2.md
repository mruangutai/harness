# QA gate — FEAT-2542 validate c2 (run r-20261126-3-validate-validator), gate-only after fix c1

**PASS.** At review_sha `2ec0916f8bf6b5d10607e36486ccbeb959ca4822` the fix closes my c1 F-1 and the
must_fix:

- Both plan verifies exit 0, and both kinds ran once, green, with receipts.
- `inflight_registry.py` is byte-identical to base. The seam is clean.
- Base-red reproduces as a set: 110 = 110.
- Mutant **g** now goes RED on `c43/not-found/run-preflight:cause`. n1 and n2 go RED on the
  intended rows.
- Two low coverage gaps remain. Neither is a code defect, because the pin behaves correctly in
  both probes:
  - **n3**, which moves the feature check after the persona check, survives 426/426.
  - **n5**, which drops `isinstance`, survives 426/426 and fails open.

## Pin, checkout, matrix

- Repository: mruangutai/harness, the unbound Harness feature. Commit `2ec0916f…`.
- The worktree HEAD is `a69f1367`, which is the pin plus a `feature.json` review_sha bump only
  (`git diff --stat 2ec0916f HEAD`).
- Everything was measured in the managed pin
  `.claude/worktrees/.pins/FEAT-2542-dispatcher-placement--r-20261126-3-validate-validator--harness-qa`.
  - HEAD = pin, and `git status` is clean.
  - `worktree-state.py --verify` exited 0 ("converged").
  - `bun install --frozen-lockfile` exited 0.
- Matrix: read with `git show 2ec0916f:.harness/harness.json`, and unchanged from c1.
  - T-01 `bugfix`: `unit` (touches_runtime_code = true).
  - `integration` is not required (the fix is not confined to tests and docs). QA adds it as
    warranted, because the SC evidence lives there. `__bug_class__` is the unresolvable
    placeholder.
  - T-02 `docs`: `always: []`.
- Candidate versus installed: the installed hook is the main checkout's `dispatch-guard.py` at
  2e7a2c77 (sha256 57fb0c65…). The candidate at the pin is sha256 a63b5f93…. Candidate behaviour
  is proven only from pin-tree runs.

## 1. Plan verifies (`bash -c <plan.yaml verify>` from the pin)

The env stripped PYTHONUNBUFFERED, NO_COLOR, FORCE_COLOR and HARNESS_AGENT_TYPE, with
TERM=xterm-256color. T-01's text in plan.yaml matches the dispatch's quoted text byte for byte
(`diff` was empty).

- **T-01 exit 0.**
  - dispatch-guard: 426 of 426.
  - lead-start-return: 60 of 60.
  - lead-start-preflight: 61 of 61.
  - census: ALL PASS.
- **T-02 exit 0.**
  - The index regenerates with no diff.
  - `check-decision-anchors`: "examined 25 anchor(s), 0 failed".
  - `test-gen-decisions-index`: 12 `ok` lines.
  - source_issues is [2532, 2542], and `(DEC-258)` is in the guard.
  - dispatch-guard: 426 of 426.

## 2. Kinds and receipts (DEC-255 production runner, from the pin)

| kind | cmd | files | exit | receipt sha256 |
|---|---|---|---|---|
| unit | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/r-20261126-3-validate-validator/qa/manifest-unit.json` | 68 / 68, all `tests/unit`, every returncode 0 | 0 | 87dc3747… |
| integration | same, with `--kind integration` and `manifest-integration.json` | 95 / 95, all `tests/integration`, every returncode 0 | 0 | 6f400d58… |

- Both receipts record `tested_commit` = 2ec0916f… and `runner_exit` 0.
- dispatch-guard and lead-start-return are in the integration receipt. lead-start-preflight and
  broad-catch-census are in the unit receipt.
- The unit log's four `^FAIL BUG-1290` lines (359–364) are test-factory-claim-mutation.py's own
  proof reprints, not failures. Grading uses the runner exit and the per-file returncodes.

## 3–4. Byte-identity and seam

- `git diff --quiet 2e7a2c77 2ec0916f -- inflight_registry.py` exited **0**.
- `b27cbcc6` resolves to `b27cbcc6e103f058e1e8e060893a5ecc74f9106b`. That equals the last
  `tested_sha` in characterization-pin.md, in the "Pin run (fix round c1)" block (line 278). It
  is an ancestor of the pin.
- `git diff --quiet b27cbcc6 2ec0916f -- dispatch-guard.py test-dispatch-guard.py` exited **0**.

## 5. Pin block and base-red

- The new block reads `tested_sha` b27cbcc6… and `pin_run_exit: 0`.
- The predicted set equals the observed set: 110 = 110, `diff` empty. That is the 97 original
  rows plus 13 new ones: c42 null/empty × bound {cause, remedy} and exploit {exit, claim,
  cause, remedy}, and c43/not-found/run-preflight:cause.
- **Base reproduction.** I made a /tmp `git archive` of the pin and replaced its guard with
  `git show 2e7a2c77:` (so the escaped-state fixtures' isolated_bin copies were base too). Result:
  exit 1, 316 of 426, 110 FAIL lines.
  - `sort`-ed, these `diff` against `predicted_red` with **no output (set-equal)**.
  - This is stronger than the fix author's own base run (89 FAILs). There, 21 escaped and
    run-reads assertions ran the live guard.
- **Omitted feature → "legacy".** `c42/omitted-feature/exploit` {exit, claim, receipt} is PASS at
  base and PASS at the pin. Mutant n4 refuses "legacy". Under n4 all three rows go red, so the
  row pins the producer default against "omitted = refuse".
- Pre-fix guard bc937a94 (the c1 pin) against the pin tests: 412/426, failing exactly the 14
  c42 null and empty assertions, including null/bound exit+claim (it proceeded). That is the
  must_fix fail-open, reproduced. c43 stays green there, because c1 already ordered placement
  first.

## 6. Mutants (pin tests, mutated pin guard, /tmp archive copies, deleted after)

The control (unmutated pin guard) gave 426/426. Each item gives the mutant and the suite result.

- **g** places `_dispatcher_placement()` after `_start_preflight()`: **RED**, 425/426, on
  `c43/not-found/run-preflight:cause`. This closes c1 F-1.
- **n1** deletes the feature check: **RED**, 412/426. All 14 null and empty rows fail: bound
  {exit, claim, cause, remedy} and exploit {exit, claim, cause, remedy}.
- **n2** weakens the check to `feature is not None`: **RED**, 420/426. The 6 empty-feature rows
  fail and null stays green, as intended.
- **n3** moves the feature check after the persona check: **GREEN, 426/426. It survives.**
  - Scratch probe: an eng-lead whose Orch.Lead claim belongs to harness-validator-lead with
    `feature: null`.
  - **At the pin:** exit 2, `cannot be placed (unreadable)`, "names no feature (None)", and the
    repair-in-place remedy. This is correct.
  - **Under n3:** exit 2, `(persona-mismatch)`, "feature None". It prints
    `inflight_registry.py release --agent-id Orch.Lead --feature '' --root …`, which is the
    broken printed command the ruling's ordering exists to prevent. `shlex.quote(None)` yields
    `''`.
- **n4** refuses "legacy": RED, 423/426, with the 3 omitted-feature rows failing.
- **n5** drops `isinstance` (`if not feature:`): **GREEN, 426/426. It survives.**
  - Probe: an ok, persona-matched claim with `feature: 123`.
  - **At the pin:** bound and exploit both exit 2 with `unreadable` and "names no feature (123)".
    This is correct.
  - **Under n5:** bound is refused by the distill-marker rule. Exploit **exits 0 and claims in the
    declared feature**, which is the must_fix fail-open class on a wrong-type shape.

## 7. Fail-first

Both SC rows are natural RED at the base guard, semantic and not merely signature-absent.

- **SC-01:** c38/distill/distill:{exit, claim, receipt} are FAIL at base. They sit in the 110-set,
  which matches `predicted_red`, `observed_red` and §5.
- **SC-02:** the c39/eng failure states, c39/validator/not-found and c40 are FAIL at base, as in
  c1. The new c42 null and empty assertions (12) are FAIL at base. The 14 null and empty
  assertions are FAIL at bc937a94, where null/bound exit and claim are semantic: it proceeded and
  claimed.
- **Ordering:** c43/not-found:cause is FAIL at base.

## Findings

- **F-1 (c1)** — closed. Mutant g now reddens.
- **Q2-1** — kind substance, low, bound to T-01. The ruled ordering (feature validity before
  persona) has no witness, and mutant n3 survives 426/426.
  - Failure scenario: a reorder ships green, and a malformed claim that also has a
    persona mismatch prints `release … --feature ''`.
  - The pin itself is correct, as measured. Fix: one c42 row with persona-mismatch plus
    null-feature that asserts `(unreadable)` and excludes `--feature`.
- **Q2-2** — kind substance, low, bound to T-01. The type leg of
  `isinstance(feature, str) and feature` is unpinned, and mutant n5 survives 426/426.
  - Under n5 a non-str truthy feature (123) fails open to the declared feature. The pin refuses
    it, as measured.
  - The ruling chose null and empty as the fixture set, so this is advisory, one boundary past
    the ruled shapes (P-05 and P-11). Fix: one c42 int-feature row.

Neither finding is a defect in the shipped code, and neither blocks.

## Measured vs reasoned

Every number above was measured. Reasoned: the operator impact in Q2-1 and Q2-2. The raw runner
and base or mutant logs are not retained under `runs/`, because QA's grant there is the receipts
only. The /tmp scratch was deleted afterwards.

## Principles applied

- Build the Lever: /tmp/qa2542c2 `drv.py`, `n3probe.py` and `n5probe.py` generated every base,
  pre-fix and mutant tree and both probes from the pin blobs, with no hand edits.
