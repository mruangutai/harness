# Goal-check (validate c2): BUG-2565-digest-frontmatter-contract at ed064577

**BLUF: PASS. All three perspectives are met, SC-01 through SC-11 are met, and all 7 amend dispositions are met.** Two round-1 gaps are now closed:

- **Operator perspective, round-1 partial.** The SPEC.md refusal-table Unavailable row now says a yield is refused.
- **SC-07, round-1 partial.** A `$ref`-reached root anyOf is now refused, and the generator now preserves CRLF, quoted-key and indentationless-sequence bytes.

All four round-1 must_fix items were re-measured at the pin and hold. I found one new advisory (A-1, T-03, low). Nothing blocks.

Pin: `ed064577a769b853e291cd71117404cb5dfc3731`. The fix delta is `bb401aae..ed064577`. Before running anything I confirmed `git diff --quiet ed064577 -- .claude tests .omp .harness/harness/docs .harness/README.md` (TREE=PIN). The only working-tree change is `feature.json`'s run-07 entry. `HARNESS_AGENT_TYPE` was unset for every run. The product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent, so `.harness/harness/docs/` is the governing record.

## Perspectives

- **operator: PASS.** Carried by SC-01, SC-02, SC-09, SC-10 and SC-11.
  - SPEC.md:779 at the pin reads: "the call proceeds (pre, post, dispatch) … a yield is refused, never passed (BUG-2565)". This now agrees with the hook's `validatorUnavailableRefusal`, with SPEC :784-788 and with DEC-100. The round-1 F-1 premise no longer occurs.
  - README :182-189 and BUILD :58-63 now give the measured count ("after three refusals"). They also narrow D-03 to task data (OQ-4), which matches the probe receipt's correction line.
  - The hook and its tests are unchanged in the fix round (`git diff bb401aae..ed064577 -- .omp tests/unit/omp-hooks.test.ts` is empty), so the round-1 SC-01 and SC-02 evidence carries over unchanged.
- **orchestrator: PASS.** Carried by SC-03 and SC-05.
  - The fix round touched no `.omp/` file, so the hook and `harness-documentor.md` blob at the pin are byte-equal to bb401aae. The round-1 evidence stands: 0 schema keys in the hook, and agent_blob equal to the pin blob.
- **code maintainer: PASS.** Carried by SC-04, SC-06, SC-07 and SC-08.
  - At the pin:
    - `gen-agent-output.py --check` → `agent output: ok` (exit 0).
    - `check-omp-port.py` → `OMP port surface: ok` (exit 0).
    - T-03's verify, run verbatim from plan.yaml → `test-digest-projection.py (0)`, with 0 FAIL lines and 16/16 `parity ok` (exit 0).

## Round-1 must_fix: re-measured at the pin

| # | Item | Status | Measurement |
|---|---|---|---|
| 1 | T-03 code grade | fixed | `code-grade.py digest_projection.py gen-agent-output.py` printed `PASSING: 34` and exited 0. `_Loader.project` is now grade 4 (6/7/14.8) and `render` is grade 4 (6/1/12.2). |
| 1 | Four regression witnesses, red-first | fixed | O-07 free mutant: the pin's `test-digest-projection.py` run against bb401aae's two scripts, in a `git archive` copy, exits 1. It reddens exactly the 4 new cases: the `$ref` root anyOf, CRLF, the quoted `structured` key, and the indentationless `output` sequence. At the pin it shows 0 FAIL lines. |
| 1 | Agents regenerate byte-identical | fixed | `.omp/` has no diff in the fix round, and `--check` reports ok. |
| 2 | Reader classification | fixed | The JSON gains the `_Loader.document::load_json_mapping#1` row and both scripts in `scanned_files`. `test-check-plan-routes.py` reports ALL PASS (exit 0, 0 FAIL lines). |
| 3 | Index rulings within the 30-word cap | fixed | Rulings now run DEC-100 30, DEC-127 25, DEC-208 27 and DEC-237 30 words. None says "inject" or a passing yield. `test-gen-decisions-index.py` exits 0 with 0 fail lines. `gen-decisions-index.py --stdout` is byte-equal to the pinned index. |
| 4 | SPEC Unavailable row | fixed | See the operator perspective above. |
| adv | harness-team SKILL :146 | fixed | The text now reads "Your lead schema, carried by your agent definition". The round-1 advisory F-2 is closed. |

## Success criteria

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | met | `omp-hooks.test.ts` "a validator that could not run refuses the yield, class by class" and "a data-less result yield is refused". The file is unchanged since bb401aae, and QA's round-1 natural red was taken against the 104252db hook. |
| SC-02 | met | `omp-hooks.test.ts` "a contract refusal reaches the child with the validator's own reason…" (unchanged). The contract leg is mutation-witnessed (QA, c1). |
| SC-03 | met | `omp-hooks.test.ts` "is neither refused nor revised, for Main and a governed lead" (unchanged). Witnesses were red at base (QA, c1). |
| SC-04 | met | The hook at the pin has 0 hits for the seven symbols, and `.omp/extensions/digest-schema.ts` is absent. `.omp` is untouched in the fix round. |
| SC-05 | met | `notes/research-frontmatter-binding-probe.md` records three observations. `agent_blob` equals the pin blob, and `harness-documentor.md` is unchanged since bb401aae. |
| SC-06 | met | `check-omp-port.py` exits 0 at the pin. `test-check-omp-port.py` and `check-omp-port.py` are unchanged since bb401aae, where QA measured 39/39, and the receipt also reports 39/39 after the fix. |
| SC-07 | met | `test-digest-projection.py` exits 0 at the pin. The root anyOf is refused at the referenced pointer (`common.json#/$defs/r/anyOf`, case "…reached through $ref names the referenced pointer"). Each of the CRLF, quoted-key and sequence byte witnesses is red on bb401aae and green at the pin. `--check` exits 0 on the tree. Advisory A-1 is below. |
| SC-08 | met | T-03's parity command, run verbatim at the pin, prints 16/16 `parity ok` and exits 0. This re-measures parity after the refactor. Per OQ-3, QA's execution remains the panel evidence. |
| SC-09 | met | Round-1 evidence plus the fix: SPEC :779, README :182-189, BUILD :58-63, and harness-team SKILL :146 no longer says "injected". |
| SC-10 | met | All 7 amend clauses are present at 104252db and absent at the pin, and each section names BUG-2565. The index is regenerated byte-equal. The DEC-100, DEC-127, DEC-208 and DEC-237 rulings assert neither injection nor a passing yield. |
| SC-11 | met | The probe Result block is unchanged. README and BUILD now state the measured count (three) and that the outcome is `failed`. |

## Decision dispositions

Read from `git show ed064577:.harness/harness/docs/DECISIONS.md`. DECISIONS.md has no diff in `bb401aae..ed064577`.

| DEC | Verdict | Evidence (pin section line) |
|---|---|---|
| DEC-100 | met | :1336. The clause is gone and BUG-2565 is named. |
| DEC-126 | met | :2676 |
| DEC-127 | met | :2692 |
| DEC-202 | met | :6287 |
| DEC-206 | met | :6766 |
| DEC-208 | met | :6811 |
| DEC-237 | met | :8048 |

The keep rows (DEC-174, DEC-179, DEC-233, DEC-188, DEC-254) are present and unchanged. They are not graded.

## T-03 amendment record (OQ-1)

- **plan.yaml.** At the pin, T-03 `files:` lists `tests/integration/canonical-reader-classification.json`. That is the only plan.yaml change in the fix round. `approval.status` remains `approved`, which is correct: `plan-merge amend` ledgers the change and does not reset approval (`plan_merge/amend.py` `_ledgered_target`).
- **feature.json.** At the pin, `judgements[]` carries `kind: amendment`, `decision: T-03.files` (2026-11-27T18:23:40, reason citing OQ-1).
- **Signed hash.** T-03's current `signed_task_hash` is `149bfad80dee…`. That differs from the signed `5df484f46d5b…`. No other task differs.
- **Gate result.** INV-40(d) exempts a task named by an amendment judgement. `check-state.py` emits no INV-40 line for BUG-2565, only INV-32/INV-17 notes. `plan-merge.py check` resolves T-03's 4 anchors. The record is in a state the gates accept.

## Findings (new in the fix round)

- **A-1. advisory. kind: substance, severity: low. Owner: T-03 (`gen-agent-output.py`).**
  - **Where:** `gen-agent-output.py` `continues` / `kept`.
  - **Failure scenario:** a hand-edited stale `output:` block containing a blank line or an unindented `#` comment ends the dropped span early. The tail of the stale value is then kept as orphaned indented lines.
  - **Measured** in a `git archive` copy of the pin. I added `\n  x-stale: 1` after a blank line inside `harness-qa.md`'s output, then:
    - The generator wrote the file and exited 0.
    - Its own `--check` printed `agent output: ok` and exited 0.
    - The frontmatter no longer parses (ScannerError).
  - **Why advisory:** the drift gate catches it. `check-omp-port.py` exits 1, printing "invalid frontmatter … mapping values are not allowed here" and a roster mismatch. It fails closed, and it needs a hand edit that generator output never produces, because generated blank lines are indented.
  - **Repair:** treat blank and comment lines inside a dropped span as continuation until the next top-level key, plus one witness.
- **A-2. advisory, pre-existing, not a fix-round regression. kind: form, severity: low. Owner: T-06 (plan record).**
  - `plan-merge.py check` exits 1 with one FAIL: T-06's quote anchor `{path: .harness/harness/docs/org.html, quote: 'The OMP task hook refuses dispatcher-supplied'}` no longer resolves. T-06 removed that text as intended; the quote is present at 104252db and absent at bb401aae.
  - It does not affect T-03, INV-40 or `test-check-plan-routes.py` (ALL PASS).
  - I am reporting it only so that nobody cites `plan-merge check` as green for this plan.

## Boundary probe (P-19)

One step past the claimed byte-preservation class (CRLF, quoted, indentationless), I tried blank, comment, flow, tab-indented and no-trailing-newline inputs to `render`:

- Flow, tab and no-trailing-newline inputs are correct and idempotent.
- Blank and comment inputs produce A-1.

## Executed vs reasoned

**Executed:**
- code-grade.
- The projection test at the pin, and against the bb401aae scripts.
- `gen --check`.
- The port gate.
- T-03 verify (parity).
- `test-gen-decisions-index`.
- `test-check-plan-routes`.
- The index regeneration diff.
- Clause presence for the 12 `decisions_affected` rows.
- The signed-hash recomputation.
- check-state.
- `plan-merge check`.
- The A-1 probe.

**Not re-run:** the bun hook suite, which is unchanged since bb401aae; QA owns it.

## Principles applied
- Expertise P-06 / O-07: each round-1 premise was re-measured with the prior commit's scripts as a free mutant, not accepted from the receipt.
- Expertise P-19 / O-12: probed one boundary beyond the stated byte-preservation class and measured the result (A-1) before grading severity.
