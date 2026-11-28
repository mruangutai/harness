# QA gate — BUG-2565 — validate run 2026-11-27-09-validate-validator (c4)

**VERDICT: PASS. `matrix_ok: true`.**
- At `dca6017d59edf5222bbd41de08d2a8a2a0f74c51`, `unit` and `integration` each pass with `runner_exit 0`. The runner wrote both receipts.
- **F-2 is closed and witnessed.** Both new lookalike witnesses are red against b9c98761's generator and green at the pin.
- Every requested mutant is killed: M1, M2, M2b, M2c (two variants), M3 and M4.
- **M2, which survived in c3, is now killed.**
- Parity is 16/16, and `gen-agent-output.py --check` and `check-omp-port.py` both print ok.
- No new substance finding.

## Pin and policy
- **Repository and pin.** The repository is harness, an unbound feature. The pin is `dca6017d59edf5222bbd41de08d2a8a2a0f74c51`. The dispatch says `feature.json` `review_sha` agrees. `b9c98761..dca6017d` changes only these code and test files:
  - `gen-agent-output.py`
  - `tests/unit/test-digest-projection.py`
  - `tests/integration/canonical-reader-classification.json` (rename of `other_keys` to `other_entries`)
- **Managed checkout.** Created with `pinned-checkout.py add` (`…/.pins/BUG-2565-digest-frontmatter-contract--2026-11-27-09-validate-validator--harness-qa`).
  - `worktree-state.py --verify` reported "converged" (exit 0).
  - `bun install --frozen-lockfile` ran first.
  - `git status --porcelain` was clean after every run.
  - The checkout is removed on return.
- **Matrix source.** `git show dca6017d:.harness/harness.json`.
  - `git diff --name-only 104252db dca6017d -- .harness/harness.json` is empty, and plan.yaml is unchanged in `b9c98761..dca6017d`.
  - The resolution against the full feature diff (P-13) therefore stands:

    | Task | change_type | Requires |
    |---|---|---|
    | T-02 | bugfix, touches_runtime_code | unit |
    | T-03 | logic | unit |
    | T-04 | config, touches_config_shape | integration |
    | T-01, T-05, T-06 | docs | nothing |

  - **The floor is unit plus integration.** `typecheck` ran inside the integration kind (`test-typescript-typecheck.py` PASS). `component` and `ui` are not required by any started task.

## Per-kind results (each kind run once from the pin)

| Kind | Command | Result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/2026-11-27-09-validate-validator/qa/manifest-unit.json` | exit 0, 69 files, `OK`, 25.5 s. `test-digest-projection.py` `PASS (0)`. Receipt: `tested_commit` dca6017d…, `runner_exit` 0 |
| integration | the same command with `--kind integration` and `manifest-integration.json` | exit 0, 95 files, `ALL PASSED`, 171.9 s. `test-check-omp-port.py` 39/39. `test-check-plan-routes.py` (which reads the renamed classification row) PASS. `test-typescript-typecheck.py` PASS. Receipt: `tested_commit` dca6017d…, `runner_exit` 0 |

- The unit log's `FAIL BUG-1290 5a/5b/5c` lines are the deliberate mutation proof in `test-factory-claim-mutation.py` (repository G-09).
- Both kinds are graded on the runner's exit code.
- The full output is in `/tmp/bug2565-qa-c4/unit.log` (3228 lines) and `integration.log` (8608 lines). The receipts are the durable record.

## Falsification probes
- **Method.** Each tree is a scratch tree built with `git archive dca6017d` (`.claude`, `.omp`, `tests/unit`). Only `gen-agent-output.py` is swapped or mutated, and the pin's `test-digest-projection.py` is run whole in that tree (P-07).
- **Files.** The driver is `/tmp/bug2565-qa-c4/driver.py`, with its log in `driver.log`.
- **Pin control.** Exit 0, with 78 PASS lines and 0 FAIL lines.

| # | Tree | Exit | Failing assertions (name, line in the pin's test file) |
|---|---|---|---|
| 1 | **RED-first**: b9c98761 `gen-agent-output.py` | 1 | `:293` bare `output: middle` "refused, never deleted": exit 0. `:295` escaped `"out\u0070ut": middle`: exit 0. Nothing else fails |
| 2 | **M2**: guard `:127-128` deleted | 1 | `:293` and `:295`, both exit 0. **KILLED** (c3: survived) |
| 3 | **M2b**: `other_entries` returns `set(parsed) - set(GENERATED)`, the c3 key-set guard | 1 | `:293` and `:295`, both exit 0. The value leg is witnessed |
| 4 | **M2c**: `other_entries` returns `len({...})` | 1 | `:293` and `:295`, both exit 0 |
| 4′ | **M2c′**: guard compares `set(other_entries(...))` | 1 | `:293` and `:295`, both exit 0 |
| 5 | **M1**: `SEQUENCE_ITEM = re.compile(r"-")` | 1 | `:256` dash-prefixed sibling. Refused with "would change another frontmatter key or its value; nothing written". Still killed |
| 5 | **M3**: `top_key` returns raw quoted text | 1 | `:264` escaped quoted `structured` (duplicate key refused) and `:295` (escaped lookalike not recognised, so exit 0). Still killed |
| 5 | **M4**: `value_end` absorbs a trailing `#` comment | 1 | `:260` commented indentationless sequence. Still killed |

- **The F-1 c2 cases stay green at the pin.** `:256`, `:260` and `:264` all print PASS (pin control and T-03 verify).
- **RED tier.** The reds in rows 1 to 4′ are natural and semantic: the old or mutated generator rewrites the description and exits 0. The `refused()` assertion that fails is `returncode == 2 and bytes unchanged and "nothing written" in stderr`.

## Boundary probes (P-11, `/tmp/bug2565-qa-c4/probe.py`, `probe.log`)
- **Setup.** Each probe ran against the pin and against M2b, both with a write and with `--check`.
- **At the pin, every lookalike probe exits 2 with nothing written, under both modes.**
  - a bare `structured: middle` lookalike (the other generated key, which has no witness);
  - a lookalike in a **double**-quoted multiline description;
  - a lookalike while `output:` is **not** stale. This is F-2's original `--check ok` symptom: the pin now exits 2, and M2b prints `DRIFT` (exit 1) and on write deletes the line;
  - a lookalike inside a multiline flow sequence.
- **Under M2b**, all four exit 0 on write (the line is deleted) or 1 on `--check`.
- **A multiline flow mapping** fails closed on both: the regenerated parse fails, exit 2.
- **Control** (a stale output with no lookalike): exit 0, writes the file; `--check` gives DRIFT, exit 1.
- The boundary checked is the other generated key, the other quote style, the non-stale route and flow collections. All of them hold.

## Parity and gates at the pin
- **T-03 verify.** Extracted from plan.yaml at dca6017d; it is identical to c3's apart from a trailing newline.
  - Exit 0, with `test-digest-projection.py` `PASS (0)`.
  - Sixteen `parity ok` lines: ai-dev through visual-designer.
- **The 16 shipped agents.** `gen-agent-output.py --check` prints `agent output: ok` (exit 0), so all 16 shipped agents render byte-identical.
- **Port gate.** `check-omp-port.py` prints `OMP port surface: ok` (exit 0).
- **Code grade.** `code-grade.py --base b9c98761… --head dca6017d…` gives PASSING 4 and exit 0. `other_entries`, `refused`, `lookalike_in_description` and `case_generator_guard` all pass; the new test functions grade 5.

## fail_first per `verify: automated` SC

`b9c98761..dca6017d` touches only `gen-agent-output.py` and its test. SC-01, 02, 03 and 06 therefore keep their c1 evidence.

| SC | Covering test at the pin | Pre-fix evidence | Tier |
|---|---|---|---|
| SC-01 | `tests/unit/omp-hooks.test.ts:2357`, `:1807` | `notes/review-harness-qa-c1.md`: both `(fail)` against the 104252db hook | natural RED |
| SC-02 | `omp-hooks.test.ts:2385`, `:2357` | c1: `:2357` red under the old hook; the refusal-text mutant turns `:2385` red | natural + mutation |
| SC-03 | `omp-hooks.test.ts:1737` | c1: six `(fail) BUG-2565: … neither refused nor revised` at 104252db | natural RED |
| SC-06 | `tests/integration/test-check-omp-port.py:205`, `:254` | c1: the old check exits 0 on schema-edit drift (31/39 against it) | natural RED |
| SC-07 | `tests/unit/test-digest-projection.py:85,101,131,184,246,250,253,256,260,264,293,295` | c1, c2 and c3 for the earlier rows. **This round:** `:293` and `:295` are red against the b9c98761 generator (exit 0, line deleted) and green at the pin (`/tmp/bug2565-qa-c4/driver.log`) | natural RED |

## Findings
None of kind substance. Advisories:
1. **Form, low, T-03. `tests/unit/test-digest-projection.py:270-281`.** `refused()` binds exit 2, unchanged bytes and the substring "nothing written". It does not bind the cause.
   - Failure scenario: a regression that refused these files for an unrelated reason would keep the witnesses green. One example is a parse refusal of every multiline quoted description.
   - Each witness is still a real behaviour check, and no measured mutant slips through it.
2. **The run 08 advisories are unchanged at this pin.** Advisories 2 to 6 still apply, including the unwitnessed all-or-nothing write (`refused()` exercises one agent only) and the `case_generator_edges` grade of 2.

## Executed vs reasoned
- Everything above was executed except the matrix carry-over. For that, I verified that harness.json and plan.yaml are unchanged, and kept the c1 resolution.
- My runtime hooks are main's installed copies. I attribute no candidate behaviour to them.
- O-07: the round-3 fix is examined only by this round's readers.

## Principles applied
- **Build the Lever:** the RED-first swap, seven mutants and the boundary probes ran from `/tmp/bug2565-qa-c4/driver.py` and `probe.py` in scratch trees built with `git archive`. No repository file was authored apart from this note and the runner's receipts.
