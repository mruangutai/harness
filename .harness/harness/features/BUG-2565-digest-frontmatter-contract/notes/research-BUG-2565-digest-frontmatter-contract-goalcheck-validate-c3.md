# Goal-check (validate c3): BUG-2565-digest-frontmatter-contract at b9c98761

**BLUF: PASS.** All three perspectives pass. SC-01 through SC-11 are met, and SC-07 is now met **on its full letter**. Round 2's F-1 is fixed, not ruled away: the three failing scenarios no longer occur under the same contract. All 7 amend dispositions are met. The round stayed inside the operator's narrow authorisation and inside T-03's files. There are no new findings. One boundary observation is recorded below, and it is not a finding.

Pin: `b9c98761ff82c408a1c58a974cfd10d60eee31b1`. I measured `git diff --quiet b9c98761 -- .claude tests .omp .harness/harness/docs .harness/README.md` (TREE=PIN). The only working-tree change is `feature.json` plus the run-08 directory. `HARNESS_AGENT_TYPE` was unset for every gate run.

## Perspectives

- **operator: PASS.** Carried by SC-01, SC-02, SC-09, SC-10 and SC-11. Round 3 touched no `.omp/`, hook, test-ts or doc file: `git diff ed064577 b9c98761 -- .harness/harness/docs` is empty, and so is the diff for `.omp`. The c2 evidence therefore carries over unchanged. `gen-decisions-index.py --stdout` is byte-equal to the pinned index (exit 0).
- **orchestrator: PASS.** Carried by SC-03 and SC-05. The hook and `harness-documentor.md` are unchanged since bb401aae. The probe receipt's `agent_blob` still equals the pin blob.
- **code maintainer: PASS.** Carried by SC-04, SC-06, SC-07 and SC-08.
  - T-03 verify run verbatim from plan.yaml: exit 0, 0 FAIL lines, 16/16 `parity ok`.
  - `gen-agent-output.py --check` printed `agent output: ok` (exit 0).
  - `check-omp-port.py` printed `OMP port surface: ok` (exit 0).
  - `test-check-omp-port.py`: 39/39.
  - `test-check-plan-routes.py`: ALL PASS.
  - `code-grade.py gen-agent-output.py`: RESULT PASS (13 functions, bar 4).

## SC-07 on its full letter (BRIEF.md:29, "other frontmatter keys byte-for-byte unchanged")

**Verdict: met.** Round 2's lead graded it partial on F-1. The round-3 repair discharges the clause, on the following evidence.

1. **F-1's three scenarios, re-measured (P-06, O-07).** I took a `git archive` of the pin and overlaid only ed064577's `gen-agent-output.py`. The pin's `test-digest-projection.py` exits 1 and reddens exactly the three new witnesses:
   - the dash-prefixed sibling key;
   - the commented indentationless sequence, including its comment before the next key;
   - the escaped quoted key.

   At the pin all three pass. These are raw-byte assertions: `"\n-mode: keep\n" in` the frontmatter, `"\n# about mode\nmode: keep\n" in after`, and exactly one `\nstructured: true\n`.
2. **The clause beyond the witnesses (P-19).** I drove `render` at the pin over 16 hand-edited shapes derived from `.omp/agents/harness-qa.md`. In every written case the frontmatter parses, the non-generated keys equal the input's, the generated `output` equals the bundle, and a second render is idempotent. Results by shape:
   - **c2 A-1** (blank line, then an indented stale line) and a comment between indented stale lines: both absorbed, no orphan. A-1 is closed.
   - **Trailing comment and blank line before the next key:** both kept.
   - **Dash-prefixed sibling keys:** `-mode`, `-x-y`, and `-mode` after a sequence are all kept, in LF and in CRLF.
   - **A comment on the `output:` line:** written correctly.
   - **A single-quoted `'output'` key:** written correctly.
   - **A plain scalar running over several lines, and a literal block, in a sibling key:** their lines are kept byte-identical.
   - **Fail closed, nothing written:** `-\t` sequence items (the current frontmatter does not parse strictly), a flow mapping continued at column 0 (the key set would change), and a tagged `!!str structured` (the regenerated frontmatter has a duplicate key). A refusal leaves every key unchanged, so it satisfies the clause.
3. **Pre-write guard.** `render` refuses through `other_keys` when the current or the regenerated frontmatter fails `artifact_accessors.load_frontmatter`, or when the non-generated key sets differ (`gen-agent-output.py` `render`/`other_keys`). The three probe refusals above exercised it.

**Boundary observation (not a finding).** The guard compares key sets, not values. Byte preservation therefore rests on `kept()` dropping only the generated spans, which the probes confirm. A literal block in a sibling key that ends the frontmatter loads through `load_frontmatter` as `'- x\n# y'` before regeneration and `'- x\n# y\n'` after. The cause is that `load_frontmatter` joins lines without a final newline, and the generated keys are appended after that block, as designed since round 1. The bytes are identical, and the BRIEF contracts bytes (G-06).

## Success criteria

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | met | `omp-hooks.test.ts` class-by-class refusal cases; the file is unchanged since bb401aae; QA's c1 natural red |
| SC-02 | met | `omp-hooks.test.ts` contract-refusal case (unchanged) |
| SC-03 | met | `omp-hooks.test.ts` "neither refused nor revised" (unchanged) |
| SC-04 | met | `.omp` unchanged since bb401aae; 0 symbol hits; `digest-schema.ts` absent (c2 measurement, same bytes) |
| SC-05 | met | `notes/research-frontmatter-binding-probe.md`; `agent_blob` equals the pin blob (unchanged) |
| SC-06 | met | port gate exits 0; `test-check-omp-port.py` 39/39 at the pin |
| SC-07 | met | F-1 mutant measurement (3 red on ed064577's generator, green at the pin) plus the 16-shape probe above; `--check` ok |
| SC-08 | met | T-03 parity, 16/16, exit 0 at the pin |
| SC-09 | met | docs unchanged in round 3; c2 evidence (SPEC :779, README :182-189, BUILD :58-63) |
| SC-10 | met | dispositions below; index regenerated byte-equal |
| SC-11 | met | probe receipt and README/BUILD unchanged since c2 |

## Decision dispositions

Each amend row's quoted `clause` was read from plan.yaml `decisions_affected` and checked in `git show 104252db:` and `git show b9c98761:.harness/harness/docs/DECISIONS.md`. Every clause is present at base, absent at the pin, and its section names BUG-2565.

| DEC | Verdict | Heading at the pin | BUG-2565 named at |
|---|---|---|---|
| DEC-100 | met | :1336 | :1411 |
| DEC-126 | met | :2676 | in section |
| DEC-127 | met | :2692 | :2727 |
| DEC-202 | met | :6287 | in section |
| DEC-206 | met | :6766 | in section |
| DEC-208 | met | :6811 | in section |
| DEC-237 | met | :8048 | in section |

The keep rows (DEC-174, DEC-179, DEC-233, DEC-188, DEC-254) are present and are not graded.

## Authorisation and scope

- **Within T-03's files.** The round-3 code delta, `ed064577..b9c98761`, touches exactly three files: `.claude/skills/harness/bin/gen-agent-output.py`, `tests/unit/test-digest-projection.py` and `tests/integration/canonical-reader-classification.json`. All three are in T-03 `files:` at the pin. plan.yaml is unchanged in round 3, and `approval.status` is `approved`.
- **Ruling items** (`notes/answers-2026-11-27-validate-c2.md`):
  - The `^-(\s|$)` dash rule is `SEQUENCE_ITEM`.
  - Comment and blank lines are handled by `interlude` and `value_end`.
  - The strict pre-write parse and key-set refusal are `other_keys` and `render`.
  - The three witnesses were RED first; I measured this above.
- **Beyond the literal ruling text:**
  - The `top_key` quoted-key decode. It is F-1's third case, so it is inside "narrow to F-1".
  - Two reader-classification rows, which the classification gate requires for the new reader calls. They are in T-03's files.
- **Out of scope, and untouched:** round-2 advisories 1-5 are in the same state. In particular, there is still no witness for the "a persona failure writes nothing" rule (advisory 1), and DECISIONS-INDEX :109 is unchanged (advisory 2). Their state is unchanged, so I do not re-raise them.
- **feature.json delta.** `review_sha`, the run-07 entry, and `rework` raised to 3 rounds / 135 minutes citing the c2 answers. This matches the ruling.

## Executed vs reasoned

**Executed at the pin:**
- T-03 verify.
- `gen --check`.
- The port gate.
- `test-check-omp-port`.
- `test-check-plan-routes`.
- `code-grade`.
- The O-07 mutant run.
- The 16-shape `render` probe.
- Clause presence for the 12 `decisions_affected` rows.
- The index regeneration diff.

**Not re-run:** the bun hook suite, which is unchanged since bb401aae and is QA's to run, and `plan-merge check`, whose A-2 state is unchanged because plan.yaml is unchanged.

## Principles applied
- Expertise P-06 / O-07: I closed F-1 by re-measuring its premise with ed064577's generator as a free mutant, not by reading the receipt.
- Expertise P-19 / O-12: I probed shapes beyond the three witnesses (tab, flow, tag, CRLF, block scalars) and measured each one before grading SC-07's full clause.
- Expertise G-06: the BRIEF contracts bytes, so I kept the parsed-value difference in the boundary observation as a reader normalization, not a finding.
