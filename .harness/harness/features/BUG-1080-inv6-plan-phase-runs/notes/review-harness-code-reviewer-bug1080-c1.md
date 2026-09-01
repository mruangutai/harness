# Code review — BUG-1080, cycle 1 — review_sha e9b11035 (base 9f2a0702)

Delta reviewed: `a2fb6c0b..e9b11035` (the remedy for cycle 0's HIGH), read against the whole
range `9f2a0702..e9b11035` for context. Worktree: `.claude/worktrees/harness/BUG-1080-inv6-plan-phase-runs`,
`git branch --show-current` = `feat/BUG-1080-inv6-plan-phase-runs`, matching `feature.json`'s
`branch` field exactly. Live: `test-check-state.py` 164 ok / 0 FAIL (26s); `test-validate-feature-json.py`
64 PASS / 0 FAIL; `check-state.sh` on the real worktree exits 0, 0 violation lines (grep -ci
"violation" = 0; the ~200 `note`-severity lines are pre-existing repo-wide advisories unrelated
to this feature). `code-grade.py --base 9f2a0702.. --head e9b11035` over the changed-Python range:
13 functions graded, all PASS (grades 4-5, no function below its bar, 0 `SEVERITY:` lines) —
`code_grade: pass`. Author's claimed evidence stands.

## Q-A — Is the HIGH genuinely closed? REAL, not merely ASSERTS-ONLY.

Traced every writer of `feature.json`'s `runs[]`: `feature-json-merge.py append-run` takes a
free-form JSON entry and appends it via `feature_json_write.write_feature_json`, which
schema-validates the candidate document against `feature-schema.json` under a **monotonic
non-regression policy** (`feature_json_write.py:84-171`) — any NEW schema problem not already
present in the baseline REFUSES the write. Confirmed live: mutating a candidate to
`code_grade: "N_A"` or `code_grade: " n_a "` is unwriteable through the CLI (§Q-C). So once the
orchestrator, following the new SKILL.md step 6 sentence, constructs its JSON entry with
`"code_grade": "n_a"`, the sanctioned writer lands it correctly and INV-6 reads it correctly
(verified: `case_inv6_plan_run_is_exempt` and my own live probe both confirm exemption). If the
orchestrator forgets, INV-6 fails closed (absence = code review) and the whole feature blocks at
the gate — a loud, re-triable failure, not a silent one.

The remaining risk — a documented procedure with no code-level default is only as reliable as the
orchestrator actually reading and following it — is not new here. It is the standing property of
**every** field this playbook instructs the orchestrator to write (`cycles_used`, `runs[]` itself,
`STATE.md`'s `## Current`): none of them have a dedicated stamping tool; all are prose-instructed
and gate-verified. This remedy fits that existing convention exactly, and cycle 0's own digest
explicitly named this fix ("stamp `code_grade: n_a` in step 6") as the remedy — it did not ask for
a tool-level affordance. **Verdict: REAL.** No must_fix.

Also confirmed: step 6 ("Adjust and record") is genuinely where a plan-panel run lands in
`runs[]` — "The plan phase" step 3 is a *different* record (pm transcribes panel findings into
`plan.yaml`'s `panel` key), never `feature.json`. Every lead dispatch, including the plan-panel
team dispatch, is one iteration of the outer loop, so step 6 governs its `runs[]` entry too — this
cycle's own validator run entry (`squad: validator`, `agent: harness-validator-lead`) is that same
shape. The remedy is in the right step, not a misfire.

## Q-B — Does `case_inv6_producer_is_documented` discriminate? Weakly — location- and
polarity-blind.

The assertion is `"code_grade: n_a" in text` against the whole shipped `SKILL.md` (one
occurrence, confirmed by grep: line 65 only). Built two live mutants against the real file:

- **Negated the instruction** — replaced the sentence with "A validator run must NEVER carry
  `code_grade: n_a` under any circumstance whatsoever." — literal substring still present →
  test still passes.
- **Relocated the sentence** verbatim into the unrelated "Mission debug" section, away from step
  6 — literal substring still present → test still passes.

So it catches only outright *deletion* of the phrase from the file; it proves nothing about
placement (is it actually in step 6, the load-bearing spot?) or polarity (does it *instruct*, or
could a future edit invert it while keeping the words?). This is a real gap in the test's own
docstring claim ("the key must be named **there**" — step 6 — which the code never checks). Not a
production defect today (the shipped sentence is correct and well-placed); flagged as a
maintainability/fragile-test finding, **med, no must_fix**.

## Q-C — Schema vs. gate divergence, direction by direction (empirically verified, both layers)

check-state.sh's loader is `harness_yaml.load_file` (PyYAML `safe_load`-class, whitespace-trims
unquoted scalars, preserves quoted scalars verbatim). The schema checker
(`feature_schema.problems_for_text` / `validate-feature-json.py`) uses strict `json.loads`. The
**sanctioned writer** (`feature-json-merge.py` → `feature_json_write.write_feature_json`) always
serializes with `json.dumps(doc, indent=2)` and schema-validates before any write lands
(monotonic non-regression — new violations refused; `check-domain.sh` also runs
`feature_schema.problems_for_text` at write time per `check-domain.sh:1133-1150`). Live probe
(isolated fixture, `CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR` + marker, confirmed fast/isolated
after an initial mistaken run against the live repo):

| Value written | check-state.sh (exact match) | Schema (enum `["n_a"]`) | Divergent? | Reachable via sanctioned CLI? |
|---|---|---|---|---|
| `n_a` unquoted, unpadded | exempt | valid | no | yes — canonical form |
| `n_a` unquoted, padded (YAML bareword) | exempt | **N/A — not valid JSON at all** (bareword) | yes, in the safe direction (schema can't even parse it; gate is lenient) | **no** — `json.dumps` always quotes; only a raw hand-edit bypassing the CLI produces bareword YAML |
| `"n_a"` quoted, unpadded | exempt | valid | no | yes — canonical form |
| `" n_a "` quoted, padded | **liable** (fires INV-6) | invalid | no — both reject | writer refuses it (new violation vs. baseline) |
| `"N_A"` / `N_A` case variant | **liable** | invalid | no — both reject | writer refuses it |
| `null` | **liable** | invalid (type) | no — both reject | writer refuses it |
| `true` | **liable** | invalid (type) | no — both reject | writer refuses it |
| `0` | **liable** (int `0 != "n_a"` is always True — no truthiness bug) | invalid (type) | no — both reject | writer refuses it |
| `""` | **liable** | invalid (not in enum) | no — both reject | writer refuses it |
| absent key | **liable** (designed default — "absence means code review") | valid (optional key) | intentional asymmetry, not a bug — matches every pre-existing `runs[]` entry | n/a, this is the baseline state |

**Only one direction diverges** (unquoted-padded YAML bareword: schema-can't-parse yet
gate-exempt), and it is unreachable through the sanctioned writer — same bypass class cycle 0
already ruled low/advisory for case-folding (finding #4: "only a raw Bash write bypassing the CLI
can seat the divergent value, and that actor already has the strictly easier bypass of forging
`review_sha` itself"). Dropping `.strip()`/`.lower()` (Q2) closed every OTHER direction cleanly;
it did not introduce a new divergence. No schema-valid-and-gate-liable case exists in any
direction tested. **No must_fix.**

**Cross-checked with `Bug1080ReviewC1.QaGateC1`**, run independently against 10 real
`feature.json` fixtures across both validators: full agreement, no disagreement in either
direction. QA independently reached the same conclusion on the one real divergent cell
(schema-can't-parse-JSON yet gate-exempt via the YAML-tolerant reader) — same root cause,
same "unreachable through the guarded write path" scoping, same low/non-blocking severity, same
cycle-0 finding #4 lineage. Their matrix is in `notes/qa-bug1080-c1.md`.

## Q-D — Are the three new schema cases non-vacuous? NO — 2 of 3 are vacuous re: `code_grade`.

`case_accepted_runs_item_code_grade_n_a` is a real discriminator (asserts `problems == []`, which
requires everything about the fixture to be correct, `code_grade` included).

`case_rejected_runs_item_code_grade_other_value` and `case_rejected_runs_item_code_grade_case_variant`
are **vacuous**. Both fixtures omit `agent` from their single `runs[]` entry, which — independent
of `code_grade` — always trips the FEAT-31 positional-`agent` rule for a feature not in
`RUNS_AGENT_EXEMPT`. Their assertion is only `problems != []`, so the pre-existing unrelated
violation alone satisfies it. Proved live: patched the in-process schema to drop the `code_grade`
enum entirely (`{"type": "string"}`, no enum) and re-ran both fixtures — `problems` was still
non-empty (the `agent` complaint alone), so both cases still "pass" with the enum gone. The
production code itself is unaffected (independently confirmed correct via §Q-C); this is a test-
suite gap that reproduces cycle 0's own finding #2 ("the enum could be widened and no test would
fail") one level down — the widening-detection tests now exist but don't actually detect it.
**Med, no must_fix** — not wrong production behavior, but should_fix before the next `code_grade`
schema edit ships unnoticed. Fix: give the rejected-case fixtures an `agent` field (matching the
accepted case) so the sole surviving problem is `code_grade`. QA independently reproduced the same
vacuity via the same mechanism (see cross-check note above) — no disagreement.

## Q-E — Regressions: none found.

`runs` stays a documented 3-tuple for INV-7/INV-22 (`check-state.sh` comment, unchanged;
`code_reviewing_runs` is deliberately a separate list). All INV-7/INV-22 cases in the 164-case
suite pass. The rewritten INV-6 message still contains `"review_sha is not pinned"` — grepped the
whole `.claude/` tree; every substring assertion elsewhere (`test-check-state.py` cases e/h/i/j,
`_PIN_MSG`) matches only that unchanged fragment, none reference the removed "a validator run
exists but" wording (cycle 0 finding #5, already correctly left as the sole historical artifact
untouched).

## Branch field: feature.json is correct; cycle 0's own digest had the typo, not a defect.

`feature.json`'s `branch: feat/BUG-1080-inv6-plan-phase-runs` matches
`git branch --show-current` exactly. Cycle 0's digest.md wrote its own `branch:` DIGEST field as
`bug/BUG-1080-inv6-plan-phase-runs` — a typo in that digest's self-reported text, not a claim
about `feature.json`. `validate-digest.py`'s `code_grade`-to-`review_sha` branch corroboration
(`_branch_corroboration_error`) compares `feature.json`'s `branch` to the checkout's *actual* git
branch, never to a digest's own `branch:` field — so this typo has zero effect on that binding.
Nothing to fix.

## Cycle-0 validator run recorded without `code_grade`, `review_sha` pinned: self-consistent.

That run genuinely reviewed code (the SKILL.md/check-state.sh/test diff at `a2fb6c0b`) and pinned
a real commit — the correct shape under the new rule ("absence means code review", and code
review happened). Not an oversight.

## Ranked findings

| # | sev | gates | finding |
|---|---|---|---|
| 1 | med | no | `case_rejected_runs_item_code_grade_other_value` / `case_rejected_runs_item_code_grade_case_variant` (`test-validate-feature-json.py`) don't discriminate on `code_grade` — both fixtures' missing `agent` field alone satisfies `problems != []`. Proved live by deleting the enum in-process; both still "pass". Reproduces cycle 0 finding #2 one level down. Cross-confirmed by QA. |
| 2 | med | no | `case_inv6_producer_is_documented` is a whole-file substring test with no location or polarity check — a verified mutant that negates the instruction, or relocates it out of step 6, still passes. |

## Verdict

Both cycle-0 open questions (Q2 schema/gate reconciliation, Q3 message names the remedy) are
correctly closed — confirmed at source and empirically, and cross-checked with QA's independent
mutation run (full agreement, no disagreement). The HIGH is genuinely closed (Q-A: REAL). No
must_fix. `severity_max: med`. **PASS with notes.**
