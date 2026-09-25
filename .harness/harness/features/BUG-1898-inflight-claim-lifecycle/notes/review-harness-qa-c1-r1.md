# QA gate rework — BUG-1898 c1-r1

**BLUF: FAIL.** The requested baseline-suite overlay demonstrates the exact preservation discriminator: a persona-release validator leaves the baseline suite green while releasing four unrelated live sentinel claims; the pinned validator releases none. F-QA-01 remains a high finding because the repository wrapper's earlier baseline run was non-discriminating, and F-QA-02 remains: the required unit kind fails its grade assertion.

## Immutable overlay and command

Temporary detached worktree: `0aa337f1`; all baseline test material came from that immutable tree.

- **Baseline:** `tests/integration/test-validate-digest.py`; all other support/fixture/contract files used by it, including `.claude/skills/harness/bin/{artifact_accessors,harness_boundary,harness_yaml,amendment_contract,code_grade,gate_policy,harness_merge}.py`, the baseline `.omp/agents/` roster, and fixture data.
- **Pin overlay:** only `.claude/skills/harness/bin/validate-digest.py` and `.claude/skills/harness/bin/inflight_registry.py` from `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`.

Command (twice, substituting the two validator/registry blobs for the mutant run):

```sh
python3 /tmp/bug1898-sentinel-driver.py \
  <baseline-tree>/tests/integration/test-validate-digest.py <report.jsonl>
```

The temporary driver injected `sitecustomize` only into child hook processes. When a real baseline `HARNESS_PROJECT_DIR` resolved to the baseline suite's shared `vd-hookcases-*` root, it seeded one OMP-live row for every governed persona: 16 distinct `claim_id`s (`sentinel-<persona>`) and 16 distinct runtime ids (`Sentinel.<persona>`). Each row used the suite process as live supervisor. It recorded the entire selected set before and after every real hook process, then removed only the remaining sentinel ids. No repository test, fixture, plan, or source was edited.

## Root resolution and measured result

The overlay cannot use one disconnected registry: execution observed **33 distinct `HARNESS_PROJECT_DIR` roots**, including 13 plain temporary roots, two graded-repository subroots, five `vd-dec156` roots, six `vd-feat65` roots, one `vd-bug1305` root, and `vd-hookcases-*`. The sentinel was intentionally placed in the latter because `run_hook_cases()` reuses it and its actual hook children resolve their registry there; its output is therefore a real hook-registry measurement, not a checkout-root probe.

| validator / registry | suite exit | sentinel before | sentinel after | released / changed |
|---|---:|---:|---:|---|
| pin `81dbd81d…` overlay | 1 (53 baseline-expectation failures) | 16 rows / 16 personas | same 16 byte-identical selected rows | **0** |
| baseline `0aa337f1` release-by-persona mutant | 0 | 16 rows / 16 personas | 12 rows | **4 released:** `harness-code-reviewer`, `harness-eng-lead`, `harness-qa`, `harness-validator-lead` |

The pin-overlay suite failure is expected incompatibility between the old suite's 0aa contracts and the review validator, not a preservation failure; its tail reported `53 FAILING`, including three T-08 probe mismatches. The preservation measurement itself passes at the pin (16/16 unchanged). The release-by-persona run's baseline suite exited **0** despite the four lost sentinels; the temporary driver therefore turns the loss into the required red discrimination. This is a true red reproduction of the release-by-persona wrong behavior, not an inference from a green wrapper.

Cleanup was exact: the pin runs removed the 16 retained `sentinel-*` claim ids each; the persona-release run removed its 12 retained ids after observing the four releases; the aborted first pin run also removed its 16 seeded ids. No non-sentinel claim was selected. All sentinel directories, reports, and driver files were removed. The temporary worktree remains for the main session/harness cleanup rule.

## Retained gate evidence

- **F-QA-01** — kind: substance; severity: high; reader: harness-qa; owner: T-03/T-04. The new overlay proves the regression is detectable, but the repository wrapper cited in c1 did not itself reproduce the wrong release: its baseline attempt had 0/16 changed sentinel rows. If a future suite changes identities or roots so that the wrapper again observes only green preservation, it can pass while a persona-release hook deletes live claims. The wrapper needs its own red proof bound to a release-by-persona mutant; this external rework does not retroactively make the wrapper discriminating.
- **F-QA-02** — kind: substance; severity: high; reader: harness-qa; owner: T-03. Retained established matrix result: `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` exited 1 at the pin because `tests/unit/test-code-grade.py` measured `_registry_errand` grade 3, below required 4. Thus `suite: fail`, `matrix_ok: false`.
- Retained established pin result: `python3 tests/integration/test-validate-digest.py` exited 0 with **81/81** BUG-1898 exact-release checks. The existing integration runner passed; SC-07 remains operator-only locally-run and has no fabricated receipt.

## SC evidence and fail-first

| SC | evidence | fail-first |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:5712-5760`; this overlay's 16-row preservation measurement | retained direct red in `notes/review-harness-qa-c0.md:23`; this rework's baseline persona-release run is a second red discriminator |
| SC-02 | `tests/unit/omp-hooks.test.ts:1875-2001` | `notes/review-harness-qa-c0.md:25` |
| SC-03 | `tests/integration/test-inflight-registry.py:1238-1410` | `notes/review-harness-qa-c0.md:25` |
| SC-04 | `tests/unit/omp-hooks.test.ts:2003-2113` | `notes/review-harness-qa-c0.md:26` |
| SC-05 | `tests/integration/test-check-omp-port.py:194-214` | `notes/review-harness-qa-c0.md:27` |
| SC-06 | `tests/integration/test-validate-digest.py:5769-5844` | `notes/review-harness-qa-c0.md:28` |

## Principles applied

- **Build the Lever** — used one temporary sentinel driver to seed, measure, and exact-clean every distinct-persona row across both immutable overlay runs.

```yaml
VERDICT: FAIL
DIGEST:
  headline: The overlay supplies a red suite-preservation discriminator, but the established required unit grade fails and the repository wrapper remains non-discriminating.
  suite: fail
  failures: 2
  matrix_ok: false
  kinds:
    - { kind: unit, state: missing, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 0 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-validate-digest.py", named_tests: 81 }
    - { kind: inflight_claim_lifecycle_live, state: locally_run, cmd: "operator-only live OMP probe", named_tests: 0 }
  coverage_gaps:
    - repository wrapper lacks a retained red release-by-persona proof bound to its own suite-preservation path
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py:5712-5760" }
    - { id: SC-02, test: "tests/unit/omp-hooks.test.ts:1875-2001" }
    - { id: SC-03, test: "tests/integration/test-inflight-registry.py:1238-1410" }
    - { id: SC-04, test: "tests/unit/omp-hooks.test.ts:2003-2113" }
    - { id: SC-05, test: "tests/integration/test-check-omp-port.py:194-214" }
    - { id: SC-06, test: "tests/integration/test-validate-digest.py:5769-5844" }
  fail_first:
    - { sc: SC-01, evidence: "notes/review-harness-qa-c0.md:23; this rework's baseline persona-release run" }
    - { sc: SC-02, evidence: "notes/review-harness-qa-c0.md:25" }
    - { sc: SC-03, evidence: "notes/review-harness-qa-c0.md:25" }
    - { sc: SC-04, evidence: "notes/review-harness-qa-c0.md:26" }
    - { sc: SC-05, evidence: "notes/review-harness-qa-c0.md:27" }
    - { sc: SC-06, evidence: "notes/review-harness-qa-c0.md:28" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-qa-c1-r1.md"]
  expertise_update: []
artifact: .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-qa-c1-r1.md
```
