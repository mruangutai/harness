# Goal-check (validate c4): BUG-2565-digest-frontmatter-contract at dca6017d

**BLUF: PASS.** All three perspectives pass, all 11 SCs are met, and all 7 amend dispositions are met.

SC-07 is re-graded **met** with the generated-key lookalike shape included. F-2 is fixed under the same contract, not ruled away. The two lookalikes now exit 2 with their bytes unchanged. The same witnesses go red on the run-08 generator, on the guard-deleted mutant M2, and on a keys-only-guard mutant.

The round stayed inside the c3 ruling and inside T-03's files. One new advisory, A-1 (low, substance, T-03), is recorded below. It does not break SC-07's letter.

- Pin: `dca6017d59edf5222bbd41de08d2a8a2a0f74c51`.
- `git diff --quiet dca6017d -- .claude tests .omp .harness/harness/docs .harness/README.md` passed: TREE=PIN.
- Working-tree delta: `feature.json` plus the run-09 directory.
- `HARNESS_AGENT_TYPE` was unset for every gate run.

## Perspectives

- **operator: PASS.** Carried by SC-01, SC-02, SC-09, SC-10 and SC-11.
  - `git diff b9c98761 dca6017d -- .harness/harness/docs .omp .harness/README.md .claude/skills/harness-team` is empty, so the c3 hook, doc and probe evidence carries over unchanged.
  - `gen-decisions-index.py --stdout` is byte-equal to the pinned `DECISIONS-INDEX.md`.
- **orchestrator: PASS.** Carried by SC-03 and SC-05. The hook and `.omp/agents/` are unchanged since b9c98761, so the c3 evidence stands and the probe receipt's `agent_blob` still equals the pin blob.
- **code maintainer: PASS.** Carried by SC-04, SC-06, SC-07 and SC-08.
  - T-03 `verify` was taken verbatim from plan.yaml at the pin: exit 0, with 0 `^FAIL` lines and 16/16 `parity ok`.
  - `gen-agent-output.py --check` printed `agent output: ok`.
  - `check-omp-port.py` printed `OMP port surface: ok`.
  - `tests/integration/test-check-omp-port.py`: 39/39 (exit 0).
  - `tests/integration/test-check-plan-routes.py`: ALL PASS (exit 0). This test carries the canonical-reader classification, including the renamed `other_entries` row.

## SC-07 re-graded with the lookalike shape (BRIEF.md:29)

**Verdict: met.** The clause under grade is "leaves each agent's body and other frontmatter keys byte-for-byte unchanged". A run either writes the identical bytes, or it refuses with exit 2 and writes nothing.

### 1. F-2 premise re-measured (P-06, O-07)

I took a `git archive` of the pin and swapped in only `gen-agent-output.py`, then ran the pin's `tests/unit/test-digest-projection.py` against each version.

| Generator | Exit | FAIL lines | Which witnesses go red |
|---|---|---|---|
| pin | 0 | 0 | none |
| b9c98761 (run-08 generator) | 1 | 2 + summary | exactly the bare and escaped witnesses: "exit 0", the lossy write |
| M2 (pre-write guard deleted) | 1 | 2 + summary | the same two |
| keys-only guard (`other_entries` reverted to the key-set difference) | 1 | 2 + summary | the same two |

The witnesses discriminate the value comparison itself, not just the guard's presence. Each witness asserts all three of:
- exit 2;
- `qa.read_bytes() == before`;
- `"nothing written"` in stderr.

They live in `tests/unit/test-digest-projection.py` `refused`, `lookalike_in_description` and `case_generator_guard`.

### 2. Beyond the witnesses (P-19)

I called `render` directly at the pin on agent files built from `.omp/agents/harness-qa.md`. Each written case passes four checks: the other entries equal the input's, `output` equals the bundle, a second render is idempotent, and the kept lines are byte-equal.

**Refused, nothing written:**
- bare `output: middle` inside a single-quoted multiline description;
- escaped `"out\u0070ut": middle` in the same position;
- the same lookalike inside a double-quoted multiline description;
- a `structured: true` lookalike in a multiline description;
- an `output:` lookalike with an indented tail line;
- a lookalike when the generated keys are already fresh;
- a column-0 plain-scalar continuation (the current frontmatter has a duplicate key);
- a lookalike in a flow mapping continued at column 0 (the regenerated frontmatter does not parse).

**Written correctly:**
- a `''output'':` line inside a single-quoted string, which decodes to the empty key and is kept;
- a `- middle` line inside a quoted description;
- the c3 shapes: a dash-prefixed sibling (LF and CRLF), a comment and a blank line before the next key, the A-1 indented stale line, a comment on the `output:` line, a single-quoted `'output'` key, and a plain multiline sibling.

### 3. Run-08 advisories

The state of advisories 2-6 is unchanged.
- Advisory 2: the all-or-nothing write is still unwitnessed. `main` collects every persona before `report`.
- Advisory 3: a column-0 flow `}` still fails closed (measured above).

## New advisory A-1: block-scalar false refusal

- kind: substance
- severity: low
- task: T-03
- where: `gen-agent-output.py` `render` and `other_entries`, as the guard compares values

**What happens.** A sibling key holding a clip- or fold-chomped block scalar (`|` or `>`) is refused when it is the last line before the closing `---`. `artifact_accessors.load_frontmatter` reads that value without its final newline. After regeneration the generated keys follow it, and the same bytes read with a final newline. The regenerated value therefore "differs", and the run is refused.

**Measured with each generator:**

| Shape | b9c98761 | pin |
|---|---|---|
| `notes: \|` + `  x` | wrote | REFUSED |
| `notes: \|` + `  - x` + `  # y` | wrote | REFUSED |
| `notes: >` + `  x` + `  y` | wrote | REFUSED |
| `\|-` (strip chomping) | wrote | wrote |

The result is the same with the stale generated keys at the top and with no generated keys at all.

**Concrete failure.** Suppose someone adds a persona agent file whose frontmatter ends with a `description: |` block. `gen-agent-output.py` then exits 2 and prints "regeneration would change another frontmatter key or its value; nothing written". The bytes would not have changed, so the maintainer must reorder the keys by hand.

**Why it is not a finding against SC-07:**
- A refusal writes nothing, so the byte clause holds.
- No `.omp/agents/*.md` file at the pin uses a block scalar: `git grep` found 0 hits, and `--check` reports ok.
- It follows from the ruled "refuses on any difference" over parsed values. It is the c3 boundary observation turned from "written" to "refused".

**Route:** backlog or advisory only, outside the narrow F-2 ruling.

## Success criteria

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | met | `omp-hooks.test.ts` refusal classes; `.omp` unchanged since b9c98761 (c3/c2 evidence) |
| SC-02 | met | `omp-hooks.test.ts` contract-refusal case (unchanged) |
| SC-03 | met | `omp-hooks.test.ts` "neither refused nor revised" (unchanged) |
| SC-04 | met | `.omp` unchanged since b9c98761; c2/c3 symbol census stands |
| SC-05 | met | `notes/research-frontmatter-binding-probe.md`; agent file unchanged |
| SC-06 | met | port gate ok; `test-check-omp-port.py` 39/39 at the pin |
| SC-07 | met | the section above: 2 witnesses, 3 mutants red, 18-shape probe; `--check` ok |
| SC-08 | met | T-03 parity 16/16, exit 0 at the pin |
| SC-09 | met | docs unchanged since b9c98761; c2 evidence |
| SC-10 | met | dispositions below; index byte-equal |
| SC-11 | met | probe receipt and README/BUILD unchanged |

## Decision dispositions (`git show dca6017d:.harness/harness/docs/DECISIONS.md`)

For every row, the plan.yaml `decisions_affected` clause is present at 104252db and absent at the pin, and the section names BUG-2565.

| DEC | Disposition | Verdict | Heading line at the pin | BUG-2565 named at |
|---|---|---|---|---|
| DEC-100 | amend | met | 1336 | 1411 |
| DEC-126 | amend | met | 2676 | 2682 |
| DEC-127 | amend | met | 2692 | 2727 |
| DEC-202 | amend | met | 6287 | 6329, 6340 |
| DEC-206 | amend | met | 6766 | 6776 |
| DEC-208 | amend | met | 6811 | 6823 |
| DEC-237 | amend | met | 8048 | 8069, 8085 |

The keep rows (DEC-174, DEC-179, DEC-233, DEC-188, DEC-254) are not graded.

## Authorisation and scope

**Code delta.** `git diff --name-only b9c98761 dca6017d` outside the feature directory lists exactly three files: `gen-agent-output.py`, `tests/unit/test-digest-projection.py` and `tests/integration/canonical-reader-classification.json`. All three are in T-03 `files:`. plan.yaml is unchanged, with `approval.status` approved.

**Ruling items** (`notes/answers-2026-11-27-validate-c3.md`):
- **Key-and-value compare:** `other_entries` now returns a dict, and `render` compares it.
- **Nothing written on refusal:** `main` prints `; nothing written` and exits 2.
- **Bare and escaped RED witnesses, plus M2:** all present, and measured above.

**Beyond the literal ruling text:**
- the stderr wording change;
- the docstring update;
- the classification-row rename `other_keys` → `other_entries`, which the classification gate requires.

All three sit within T-03's files.

**feature.json:** the delta matches the ruling: `rework` is 4 rounds / 165 minutes, citing the c3 answers, plus the run-08 entry. The `review_sha` field inside the pin commit reads `26613408…`, the code-identical fix commit named in the dispatch.

## Executed vs reasoned

**Executed at the pin:**
- T-03 verify;
- `gen --check`;
- the port gate;
- `test-check-omp-port`;
- `test-check-plan-routes`;
- 3 generator mutants, plus the pin control;
- the 18-shape `render` probe;
- the A-1 probe against both generators;
- the clause checks for the 7 amend rows;
- the index regeneration diff.

**Not re-run:** the bun hook suite, which is unchanged since b9c98761 and is QA's to run.

## Principles applied
- Expertise P-06 / O-07: I closed F-2 by re-running the witnesses against the run-08 generator and against two mutants.
- Expertise P-19 / O-12: I probed lookalike variants beyond the two witnesses, and measured the side effect of the value comparison on block scalars (A-1).
- Expertise G-06: I graded A-1 against the byte contract. It is a false refusal, not a byte change.
