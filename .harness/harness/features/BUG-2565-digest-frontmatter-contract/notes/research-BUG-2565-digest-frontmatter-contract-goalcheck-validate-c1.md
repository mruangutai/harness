# Goal-check (validate c1): BUG-2565-digest-frontmatter-contract at bb401aae

**BLUF: FAIL. One perspective is partial.** The orchestrator and code maintainer perspectives pass. All seven amend dispositions landed (met). SC-09, SC-10 and SC-11 (the doc half) are met. The operator perspective is **partial** because SPEC.md's `Refusal, unavailable, allow` table still says that when a gate is unavailable, the call proceeds in the `yield` phase too (finding F-1, owned by T-06). That contradicts the hook at the pin and also the SPEC paragraph and DEC-100 text directly below it. The fix is one table row in T-06's file.

Pin: `bb401aaea16b9b36a954daef3cebafb2401efe89`, base `104252db`. Everything below was read with `git show bb401aae:<path>`. Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` do not exist in the checkout. The governing record is `.harness/harness/docs/`.

## Perspectives (one line each)

- **operator: PARTIAL.** SC-01, SC-02, SC-09, SC-10 and SC-11 carry it.
  - **Code side holds.** In the yield branch of `harness-hooks.ts`, `result.unavailable` maps to `validatorUnavailableRefusal`, and `RETURN_THE_OBJECT` handles data-less yields. Tests in `omp-hooks.test.ts`:
    - "a validator that could not run refuses the yield, class by class": six process-end classes, each with exact D-02 text.
    - "an unavailable check-domain still lets a governed write proceed".
    - "a contract refusal reaches the child with the validator's own reason, never the could-not-run text".
    - "a data-less result yield is refused".
  - **Docs side holds for README, BUILD, DECISIONS and the index.**
  - **The gap:** the SPEC.md table row at line 779 still promises that a yield proceeds when its gate is unavailable (F-1). The perspective's second sentence, "SPEC … describe[s] the contract that actually runs", is therefore not fully discharged.
- **orchestrator: PASS.** SC-03 and SC-05 carry it.
  - The hook code at the pin contains no `outputSchema` or `schemaMode` (0 grep hits). The only hits in tracked `.ts`/`.py` files are in two test files: `tests/unit/omp-hooks.test.ts` and `tests/integration/test-dispatch-guard.py`.
  - The parameterised test "is neither refused nor revised, for Main and a governed lead" covers the nine flat and batch witnesses, including `probe-qa` and `probe-scout`.
  - `.omp/config.yml` sets no `task.structured` (BUG-2565 comment). The `harness-documentor.md` blob at the pin is `96f4332c…`, which equals `agent_blob` in the binding probe.
  - In the binding probe, `task_item_keys: agent, name, solutionSpace, task`, the off-schema yield was rejected and the conforming yield accepted.
- **code maintainer: PASS.** SC-04, SC-06, SC-07 and SC-08 carry it.
  - `.omp/extensions/` at the pin holds only `harness-hooks.ts`. `digest-schema.ts` is gone.
  - All 16 `harness-*.md` files carry exactly one `structured: true` and one `output:`.
  - I ran both checks against the working tree, which equals the pin for these paths. Both are read-only and exited 0:
    - `check-omp-port.py` printed `OMP port surface: ok`.
    - `gen-agent-output.py --check` printed `agent output: ok`.
  - Drift cases in `test-check-omp-port.py`: `case_task_structured_off` and `case_agent_output_drift`. Refusal, generator and idempotence cases are in `test-digest-projection.py`.
  - The build receipt records 16/16 `parity ok` for SC-08. I did not re-run any suite (qa owns that).

## Success criteria I graded from the pinned files

| SC | Verdict | Evidence |
|---|---|---|
| SC-09 | met | README.md:176-188 (paragraph rewritten). BUILD.md:55-62 and its failure-table rows. SPEC.md:784-788 and §8.3 at :1334-1343. harness-team SKILL.md:95. org.html:282-287. In the five files, `outputSchema`, `schemaMode` and `hook injects` each match 0 times. README, BUILD and SPEC each contain `gen-agent-output.py` and `refused, never passed`. README has 0 `feature.yaml`. See F-1 for the table contradiction and F-2 for a residual adjective. |
| SC-10 | met | All seven amend clauses are present at base and absent at the pin, and each entry names BUG-2565 (dispositions below). `gen-decisions-index.py --stdout` matches the pinned index byte-for-byte. Index rulings: DEC-100 at :109, DEC-127 at :132, DEC-208 at :206, DEC-237 at :231. Each changed from "pass visibly", "fails open visibly" and "hook injects" to "yield … refused (BUG-2565)" or "agent definitions carry the schema". |
| SC-11 | met | `research-yield-refusal-probe.md` Result block: `hook_refusal_consumes_schema_retry: no`, `refused_attempts_before_end: 3`, `parent_task_status: failed`, `parent_receives_refused_payload: no`. README.md:184-187 and BUILD.md:60-62 state the measured behaviour: no retry consumed, `failed`, the cause named, never the refused object. Advisory: neither doc gives the count 3; both say "after repeated refusals". |

## Decision dispositions (amend rows; DECISIONS.md at bb401aae)

Each row is met. The clause exists at base, is absent at the pin, and was replaced by text that states the D-xx contract and names BUG-2565. None was struck (DEC-188).

| DEC | Verdict | Pinned evidence (DECISIONS.md line) |
|---|---|---|
| DEC-100 | met | :1400-1418. The bullet now reads "write, Bash call and dispatch fail open, visibly; the yield is refused" and keeps the D-02 refusal text. "Failing … closed stays refused" is narrowed to those three gates. The phase tags drop `yield`. |
| DEC-126 | met | :2678 moves the directory to `schemas/digest/`. :2682-2684 now says `digest_projection.py` → `gen-agent-output.py` → `check-omp-port.py` (D-01). |
| DEC-127 | met | :2725-2728. Still returns 0 with the unavailable line, but "since BUG-2565 the yield carrying it is refused, never passed". |
| DEC-202 | met | :6328-6331: "`task` carries no schema … (BUG-2565)". :6340-6341: the port gate also fails on `output:` drift. "receives the persona's strict schema" is gone. |
| DEC-206 | met | :6775-6776: "only `harness-*` agent definitions carry a digest schema, in frontmatter (BUG-2565)". |
| DEC-208 | met | :6823-6826. The operator reversed the fail-closed rejection for the yield, with a reason. |
| DEC-237 | met | :8069-8078 adds the "Agent definitions own schema delivery (BUG-2565)" paragraph, including D-04 and the removal of the BUG-2305 exception. :8085-8087 adds the yield refusal to "Yield owns live validation". :8058 updates the directory. :8114's "injected strict schema" is in past-tense history ("The deletion gate was live") and is correct as record. |

Keep rows (DEC-174, DEC-179, DEC-233, DEC-188, DEC-254) are not graded. Their clauses are present unchanged at the pin.

## Findings

- **F-1.** SPEC.md:779 (`Refusal, unavailable, allow (DEC-100)` table, **Unavailable** row).
  - **What it says:** "the call proceeds … phase-tagged (pre, post, dispatch, yield)". The diff left this row byte-identical to base.
  - **Failure scenario:** an operator auditing SPEC reads that an unavailable `validate-digest` lets the yield proceed with a notice. The code does the opposite (`validatorUnavailableRefusal` in the yield branch). So do SPEC.md:784-788 five lines later and DEC-100:1411, which dropped `yield` from the tags.
  - **Repair:** reword the row's agent-sees cell to "the call proceeds (pre, post, dispatch) …; a yield is refused, never passed (BUG-2565)".
  - kind: substance (false runtime claim). Severity: low. Owner: **T-06** (`.harness/harness/docs/SPEC.md` is in its `files:`). This is the same class as the panel's open PF-dc87fd07 "stale sibling wording".
- **F-2.** harness-team SKILL.md:146: "Your injected lead schema owns the required fields".
  - **What's wrong:** the schema is no longer injected at dispatch. SC-09's literal forms (`hook injects`) do not match it, but the adjective restates the retired mechanism.
  - **Repair:** change "injected" to "agent-definition".
  - kind: form. Severity: low. Owner: **T-06**.
- **Out of scope (no task owns it):** SPEC §8.3 `Yield` cites `harness-hooks.ts:1108` and `validate-digest.py:2200`/`:1827`. These line numbers were already stale at base (base :1108 is `releaseClaims`). The diff did not cause this. Fixing it would be a scope change.

## Boundary probe (P-19), reasoned not executed

The yield branch runs only when a `currentAgent` is detected (`if (!currentAgent && !ompMainTask) return;` in `tool_call`). That detection comes from the agent body's `HARNESS_AGENT_ID` marker. A harness-named child with no marker would yield unchecked. The generator keeps bodies byte-identical (test-digest-projection "body byte-identical"), and this behaviour is unchanged from base. This is not a finding against this diff.

## What I executed vs reasoned

**Executed:**
- `git show`/`git diff` reads at the pin.
- Clause presence at base vs pin for all 12 `decisions_affected` rows (python).
- `gen-decisions-index.py --stdout` diffed against the pinned index (match).
- `check-omp-port.py` (exit 0).
- `gen-agent-output.py --check` (exit 0).
- Greps on the five SC-09 docs.
- Comparison of the agent blob to the probe receipt.

**Not re-run:** the bun and python suites. SC-01..08 test evidence comes from test names at the pin and from `receipt-main-session-build.md`.

## Principles applied
- The P-16 / P-19 expertise rules shaped two choices. I graded the SPEC prose beyond SC-09's literal grep, which produced F-1. I checked one boundary past the validator-unavailable class (an undetected agent).
