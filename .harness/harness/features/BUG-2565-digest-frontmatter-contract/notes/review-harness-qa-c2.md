# QA gate — BUG-2565 — validate run 2026-11-27-07-validate-validator (c2)

**VERDICT: PASS.** At `ed064577a769b853e291cd71117404cb5dfc3731`, the required `unit` and `integration`
kinds are green, `runner_exit 0` each, and both round-1 reds (`test-gen-decisions-index.py`,
`test-check-plan-routes.py`) now pass. All four new regression witnesses fail against bb401aae's
production files and pass at the pin. code-grade shows no production function below its bar.
Parity is 16/16. The fix round weakened no test. Two low advisory items are listed below; neither blocks.

## Pin and policy
- Repository: harness (unbound feature). The pin is `ed064577a769b853e291cd71117404cb5dfc3731`,
  equal to the worktree's `feature.json` `review_sha`.
- Managed checkout:
  `.claude/worktrees/.pins/BUG-2565-digest-frontmatter-contract--2026-11-27-07-validate-validator--harness-qa`.
  `worktree-state.py --verify` reported "converged" (exit 0). `bun install --frozen-lockfile` ran first.
- Matrix: `git show ed064577:.harness/harness.json`. `bb401aae..ed064577` does not touch
  harness.json or any task's `change_type`, so the c1 resolution stands:
  - T-02 bugfix → unit
  - T-03 logic → unit
  - T-04 config, with touches_config_shape → integration
  - T-01, T-05 and T-06 are docs and require nothing

  **The required floor is unit plus integration.** `typecheck` was also run (`bun run typecheck`, exit 0), but no receipt applies to it.

## Per-kind results (each run once from the pin, receipts written by the runner)
| Kind | Command | Result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/2026-11-27-07-validate-validator/qa/manifest-unit.json` | exit 0, 69 files. `test-omp-hooks.py`: 240 pass, 0 fail. `test-digest-projection.py`: PASS (0). Receipt: `tested_commit` ed064577…, `runner_exit` 0 |
| integration | same command with `--kind integration` and `manifest-integration.json` | exit 0, 95 files, ALL PASSED. `test-check-omp-port.py`: 39/39. `test-gen-decisions-index.py`: PASS. `test-check-plan-routes.py`: PASS. `test-typescript-typecheck.py`: PASS. Receipt: `tested_commit` ed064577…, `runner_exit` 0 |

The `FAIL BUG-1290 5a/5b/5c` lines in the unit output belong to the deliberate mutation proof in
`test-factory-claim-mutation.py` (exit 0). They are not failures. The full logs were kept in
`/tmp/bug2565-qa-c2/{unit,integration}.log` during the run; the runner's own receipts are the
durable record.

## Measurements requested by the lead
**(a) code-grade.py**
- `code-grade.py digest_projection.py gen-agent-output.py tests/unit/test-digest-projection.py` exits 0 ("PASSING: 51").
- Every production function in both scripts is RESULT PASS, at grade 4 or 5 against bar 4.
- Two test functions grade below their bar (2 against bar 3), both severity med:
  - `walk` (test-digest-projection.py:38)
  - `case_generator` (:189)

  Neither function changed in this round. `--base bb401aae --head ed064577` (only the functions the fix round changed) exits 0, with all 26 PASS.
- The fix round changed no other Python file (`git diff --name-only bb401aae ed064577 -- '*.py'` lists only these three).

**(b) T-03 parity, verbatim from plan.yaml, run at the pin:** exit 0, **16 `parity ok`**. A typed
rerun comparing sorted `json.dumps` output finds no persona that differs.

**(c)** `gen-agent-output.py --check` exits 0 (`agent output: ok`). `check-omp-port.py` exits 0 (`OMP port surface: ok`).

**(d) Fail-first for the four new witnesses.**
- Method: a scratch tree from `git archive ed064577`, with only `digest_projection.py` and
  `gen-agent-output.py` replaced by their bb401aae blobs. The pin's test file was run whole in that
  tree (P-07).
- Result there: exit 1, `FAIL test-digest-projection.py (4)`. Exactly the four witnesses fail, and every pre-existing case passes:
  - `:131` "an anyOf at the schema root reached through $ref…" fails with "no ProjectionError"
  - `:246` "CRLF … keep their CRLF bytes when stale output is rewritten"
  - `:250` "a quoted structured key is replaced, never duplicated"
  - `:253` "an indentationless output sequence is replaced whole, never orphaned"
- Control: the same file at the pin gives PASS (0), with all four PASS.
- All four are semantic reds from assertions on the old code's output, not missing-signature reds.

**(e)** `test-check-plan-routes.py` and `test-gen-decisions-index.py` were red in c1. Both are now PASS in the integration run above.

**Weakened tests: none.**
- `git diff bb401aae ed064577 -- tests/` is purely additive:
  - the `re` import
  - one refusal row
  - the `edge`, `front_keys` and `case_generator_edges` helpers, plus one entry in `main`'s case list
  - 15 lines of classification JSON
- No assertion was removed or loosened.
- `harness-hooks.ts`, `omp-hooks.test.ts`, `check-omp-port.py` and `test-check-omp-port.py` are unchanged in this round.

## fail_first per `verify: automated` SC
SC-01, 02, 03 and 06 rest on code and tests that the fix round left unchanged (diff above). Their c1
reproductions stand; this note adds no new evidence for them.

| SC | Covering test at the pin | Pre-fix evidence | Tier |
|---|---|---|---|
| SC-01 | `tests/unit/omp-hooks.test.ts:2357`, `:1807` | c1 note `review-harness-qa-c1.md`: `(fail)` both cases against the 104252db hook | natural RED |
| SC-02 | `omp-hooks.test.ts:2385`, `:2357` | c1: `:2357` is red under the old hook. Mutant `reason = validatorUnavailableRefusal(...)` turns `:2385` red | natural plus mutation |
| SC-03 | `omp-hooks.test.ts:1737` | c1: all six `(fail) BUG-2565: <label> is neither refused nor revised` at 104252db | natural RED |
| SC-06 | `tests/integration/test-check-omp-port.py:205`, `:254` | c1: at 104252db the schema-edit drift exits 0, and the new test against the old check gives 31/39 | natural RED |
| SC-07 | `tests/unit/test-digest-projection.py:85,101,131,184,246,250,253` | c1: signature-absent red plus per-class mutants. This round: the four witnesses are red against bb401aae's production files, green at the pin | natural RED (new witnesses) |

## Findings (all advisory; none blocks)
1. **coverage gap, low, T-03.** In `.claude/skills/harness/bin/gen-agent-output.py:118-122`, "writes
   nothing if any persona fails" is new behaviour, and no test pins it.
   - Measured on a probe with harness-ai-dev stale and harness-visual-designer.json malformed:
     - at the pin: exit 2, ai-dev untouched
     - at bb401aae: exit 2, `wrote .omp/agents/harness-ai-dev.md`
   - A revert to the per-file write would stay green.
   - Repair: in `test-digest-projection.py`, add a case that makes one agent stale, breaks a later persona's schema, and asserts exit 2 with the stale file's bytes unchanged.
2. **form/robustness, low, T-03, pre-existing (not a regression).** `gen-agent-output.py:50-64`
   (`continues`/`kept`) ends the generated value at a blank line, or at a column-0 comment, inside a
   hand-edited `output:` block. The rest of the stale block is kept and attached to the
   preceding key, so the frontmatter becomes unparseable YAML.
   - The generator exits 0, and its `--check` then prints `agent output: ok`.
   - bb401aae behaves the same way.
   - The drift gate does catch it: `check-omp-port.py <fixture>` exits 1 (YAML ScannerError plus a roster mismatch). The gate fails closed and only the generator's self-check is fooled.
   - Repair (optional): treat blank and comment lines as continuation while dropping, or have `--check` parse the frontmatter it rendered.

## Adequacy probes beyond the class (P-11)
- The new generator was probed on seven mutated harness-qa.md inputs. Five held: frontmatter parses equal to the original, the body is unchanged, and `--check` gives 0:
  - a trailing comment on `structured: true # x`
  - a single-quoted `'output':`
  - stale output plus CRLF
  - a flow-style `output: {type: object}`
  - a stale `output` placed before `name`
- The other two (a blank line or a column-0 comment inside output) are finding 2.
- In the projection, the `root` flag survives `follow`. A two-hop `$ref` reuses the same recursion and was reasoned, not executed.

## Executed vs reasoned
- Everything above was executed except the matrix predicate resolution, which was carried from c1 because harness.json and the task change types are unchanged, and the two-hop `$ref` remark.
- My own runtime hooks are main's installed copies; none of them is cited as candidate behaviour.

## Principles applied
- Build the Lever: the parity, the fail-first swap and both probe sets ran from scratch drivers under
  `/tmp` (`/tmp/bug2565-qa-c2/*.py`). No repository file was authored.
