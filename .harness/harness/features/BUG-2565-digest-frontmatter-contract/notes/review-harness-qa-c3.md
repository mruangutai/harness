# QA gate — BUG-2565 — validate run 2026-11-27-08-validate-validator (c3)

**VERDICT: PASS.**
- At `b9c98761ff82c408a1c58a974cfd10d60eee31b1`, the required `unit` and `integration` kinds pass, each with `runner_exit 0`.
- All three new F-1 witnesses fail against ed064577's `gen-agent-output.py` and pass at the pin.
- Three of the four requested mutants are killed.
- **M2 survives.** Removing the pre-write key-set guard (`gen-agent-output.py:127-128`) leaves every test green. It is a coverage gap (finding 1), not a gate failure: I showed separately that the guard is live and that it discriminates.
- Parity is 16/16; `--check`, `check-omp-port.py` and the code grade of production functions all pass.

## Pin and policy
- **Repository and pin.** The repository is harness (an unbound feature). The pin is `b9c98761ff82c408a1c58a974cfd10d60eee31b1`, the worktree's `feature.json` `review_sha`.
- **Managed checkout.** I created it with `pinned-checkout.py add` (`…/.pins/BUG-2565-digest-frontmatter-contract--2026-11-27-08-validate-validator--harness-qa`).
  - `worktree-state.py --verify` reported "converged" (exit 0).
  - `bun install --frozen-lockfile` ran first.
  - I removed the checkout with `pinned-checkout.py remove` before writing this note.
- **Matrix source.** `git show b9c98761:.harness/harness.json`. `git diff --name-only 104252db b9c98761 -- .harness/harness.json` is empty, and no task's `change_type` changed in `ed064577..b9c98761`. The c1 resolution against the full feature diff therefore stands (P-13):

  | Task | change_type | Requires |
  |---|---|---|
  | T-02 | bugfix, touches_runtime_code | unit |
  | T-03 | logic | unit |
  | T-04 | config, touches_config_shape | integration |
  | T-01, T-05, T-06 | docs | nothing |

  **The floor is unit plus integration.** `component` and `ui` are unresolved, but no started task requires them. `typecheck` ran inside the integration kind (`test-typescript-typecheck.py` PASS) and has no receipt.

## Per-kind results (each kind run once from the pin; the runner wrote the receipts)

| Kind | Command | Result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/2026-11-27-08-validate-validator/qa/manifest-unit.json` | exit 0, 69 files, `OK`. `test-omp-hooks.py` 240 pass. `test-digest-projection.py` `PASS (0)`. Receipt: `tested_commit` b9c98761…, `runner_exit` 0 |
| integration | the same command with `--kind integration` and `manifest-integration.json` | exit 0, 95 files, `ALL PASSED`. `test-check-omp-port.py` 39/39. `test-check-plan-routes.py`, `test-gen-decisions-index.py` and `test-typescript-typecheck.py` PASS. Receipt: `tested_commit` b9c98761…, `runner_exit` 0 |

- The unit log's `FAIL BUG-1290 5a/5b/5c` lines come from the deliberate mutation proof in `test-factory-claim-mutation.py`, which exits 0 (repository G-09).
- Both kinds are graded on the runner's own exit code.
- The full runner output stays at `/tmp/bug2565-qa-c3/{unit,integration}.log`. The receipts are the durable record.

## (a) Fail-first for the three F-1 witnesses (SC-07 byte-preservation clause)
- **Method.** I built a scratch tree with `git archive b9c98761` (`.claude`, `.omp`, `tests/unit`). Only `gen-agent-output.py` was replaced, with its ed064577 blob. The pin's test file was then run whole in that tree (P-07). The driver is `/tmp/bug2565-qa-c3/driver.py`; its log is `driver.log`.
- **ed064577 generator: exit 1, `FAIL test-digest-projection.py (3)`.** Exactly the three new witnesses fail. All earlier cases, including c2's four witnesses, pass:
  - `test-digest-projection.py:256`, the dash-prefixed sibling key `-mode: keep`, is dropped.
  - `:260`, the commented indentationless sequence, leaves an orphan or loses the comment.
  - `:264`, the escaped quoted key `"struc\u0074ured"`, is duplicated.
- **Control.** The unmodified pin tree gives exit 0, `PASS (0)`.
- **Tier.** All three are natural, semantic reds: assertions on the old code's output bytes, not a missing signature.

## (b) Mutation probes at the pin (each in its own scratch tree under `/tmp`)

| Mutant | Edit to `gen-agent-output.py` | Result | Witness turned red |
|---|---|---|---|
| M1 | `SEQUENCE_ITEM = re.compile(r"-")` | **killed** | `:256` dash-prefixed sibling. The guard refuses with "would change the frontmatter's other keys", so the run exits 2 |
| M2 | the `if other_keys(...) != other_keys(...): raise` guard (`:127-128`) deleted | **SURVIVES** (exit 0, PASS 0) | none: coverage gap, finding 1 |
| M3 | `top_key` returns the raw quoted text (no `harness_yaml.load_str`) | **killed** | `:264` escaped quoted key. Refused with a duplicate key 'structured' |
| M4 | `value_end` adds `elif line.startswith('#'): end = index + 1` | **killed** | `:260`. The `# about mode` comment before `mode:` is lost |

- M1 and M3 are killed through the guard's refusal and the `returncode == 0` leg. The byte assertions would also catch them if the guard were gone, because the removed `-mode` key and the duplicate are visible in the bytes. I reasoned this and did not run the M1+M2 or M3+M2 combinations.
- **The M2 control shows the guard is live** (`/tmp/bug2565-qa-c3/probe.py`, P-09/P-11). I ran five inputs at the pin and under M2. The two c2-advisory-2 cases (a blank line and a column-0 comment inside a stale output) are now handled by both: exit 0, key set unchanged, `--check` 0. The three cases below show the guard deciding the outcome:

  | Input | At the pin | Under M2 |
  |---|---|---|
  | `? output` explicit-key syntax | exit 2, nothing written | exit 0, writes a duplicate `output` key that YAML silently shadows; `--check` 0 |
  | `!!str structured: true` | exit 2, nothing written | exit 0, writes a duplicate `structured` |
  | `output: &o` with `copy: *o` | exit 2, nothing written | exit 0, writes **unparseable** frontmatter (ComposerError); `--check` 0 |

## (c) Run-07 advisory 1, the all-or-nothing write
**State unchanged: no witness.** `ed064577..b9c98761 -- tests/` adds only the three edge rows. No case breaks a later persona's schema and asserts that an earlier stale agent's bytes are unchanged.

## (d) Parity and gates at the pin
- T-03 `verify`, verbatim from plan.yaml: exit 0, `test-digest-projection.py` PASS, and **16 `parity ok`**.
- `gen-agent-output.py --check`: `agent output: ok` (exit 0). Every shipped agent renders byte-identical, because `--check` compares rendered bytes to file bytes.
- `check-omp-port.py`: `OMP port surface: ok` (exit 0).
- **code-grade (production).** `code-grade.py gen-agent-output.py` gives 13/13 RESULT PASS. `--base ed064577 --head b9c98761` exits 0:

  | Function | Grade | Bar |
  |---|---|---|
  | `top_key` | 4 | 4 |
  | `interlude` | 5 | 4 |
  | `value_end` | 4 | 4 |
  | `other_keys` | 5 | 4 |

  The changed-function grader did not list the rewritten `continues`, `kept` or `render`. The whole-file grade covers them, and all PASS.
- **code-grade (test).** `case_generator_edges` (test, `:245`) is RESULT FAIL, grade 2 against bar 3, severity med, driver ABC 30.0. It is a test function and does not block (finding 3).

## fail_first per `verify: automated` SC
`ed064577..b9c98761` changes only `gen-agent-output.py` and the test file. SC-01, 02, 03 and 06 therefore keep their c1 evidence.

| SC | Covering test at the pin | Pre-fix evidence | Tier |
|---|---|---|---|
| SC-01 | `tests/unit/omp-hooks.test.ts:2357`, `:1807` | `notes/review-harness-qa-c1.md`: both cases `(fail)` against the 104252db hook | natural RED |
| SC-02 | `omp-hooks.test.ts:2385`, `:2357` | c1: `:2357` red under the old hook; the refusal-text mutant turns `:2385` red | natural + mutation |
| SC-03 | `omp-hooks.test.ts:1737` | c1: six `(fail) BUG-2565: … neither refused nor revised` at 104252db | natural RED |
| SC-06 | `tests/integration/test-check-omp-port.py:205`, `:254` | c1: the old check exits 0 on schema-edit drift; 31/39 against it | natural RED |
| SC-07 | `tests/unit/test-digest-projection.py:85,101,131,184,246,250,253,256,260,264` | c1/c2 for the earlier rows. **This round:** `:256,260,264` are red against the ed064577 generator and green at the pin (`/tmp/bug2565-qa-c3/driver.log`) | natural RED |

## Findings
1. **Coverage gap, substance, medium, T-03. `gen-agent-output.py:127-128`.** The pre-write key-set guard that the operator ruling required has no witness.
   - Deleting it (M2) keeps all of `test-digest-projection.py` green.
   - Failure scenario: an agent whose frontmatter uses `? output`, a tagged generated key, or an alias into `output:` would be rewritten with a silently shadowed duplicate key, or with unparseable YAML. The generator would exit 0 and `--check` would print `ok`.
   - Repair: add one edge row that expects exit 2 and unchanged bytes. For example, `output: &o` plus `copy: *o`, where the pin refuses and M2 writes ComposerError YAML.
2. **Coverage gap, substance, low, T-03, carried from run-07 advisory 1. `gen-agent-output.py:164-168`.** The all-or-nothing write still has no witness (see c above).
3. **Form, low, T-03. `tests/unit/test-digest-projection.py:245`.** `case_generator_edges` grades 2 against its bar of 3 (ABC 30.0), after growing by three rows. It is a test function, so it does not block.

## Executed vs reasoned
- Executed: everything above, except the matrix predicate carry-over (harness.json and the change types are unchanged; diff checked) and the M1+M2 and M3+M2 combinations (reasoned).
- My runtime hooks are main's installed copies. No candidate behaviour is attributed to them.
- O-07: the round-2 fix was examined only by this round's readers.

## Principles applied
- **Build the Lever:** the fail-first swap, all four mutants and the guard control ran from `/tmp/bug2565-qa-c3/driver.py` and `probe.py`, in scratch trees built from `git archive`. No repository file was authored.
