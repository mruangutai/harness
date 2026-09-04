# Goal-check (confirm) — FEAT-52 — all 15 criteria at `review_sha 1d93c727`

## BLUF

**PASS — 15 of 15 criteria met, all six REQs traced.** The one gap c13 recorded (SC-08's
`evidence: unit` label falsified by a `tests/integration/` carrier) is **CLOSED by route 2**:
`1d93c727` moves `case_workflow_gate` out of `tests/integration/test-check-instruction-paths.py`
into `tests/unit/test-instruction-workflow-gate.py`, and the declared kind now genuinely executes
its assertions — `run-unit-tests.sh --kind unit` exit **0**, 24 files, and the run names
`test-instruction-workflow-gate.py (exit 0)` explicitly, not by count.

Delta since the graded pin is exactly three things: the BRIEF's eight evidence-kind lines
(`7ca27941`), the `feature.json` repin, and the SC-08 relocation. `git diff 72a6a757 1d93c727 --
. ':(exclude).harness'` touches **only the two test files**, so no previously-met verdict rests on
changed source — and I re-ran every carrier at the pin regardless. `52375c9c` is `feature.json`
`review_sha` only; tracked source at HEAD is byte-identical to `1d93c727` outside `.harness`.

## Verdicts

| SC | Verdict | Method | Evidence at `1d93c727` |
|---|---|---|---|
| SC-01 | met | automated/integration | `tests/integration/test-inject-expertise.py` (case4 no-Expertise, case4b `injected != product_cwd`) — suite green in the `--kind integration` run |
| SC-02 | met | automated/integration | same suite, case4c (UNRESOLVED + `VERDICT: BLOCKED`, exit 0) and case14 (`^[ \t]*exit [1-9]` zero matches + `exit 2` positive control) |
| SC-03 | met | automated/integration | five separate `scope contains …` PASS lines, run verbatim: S1–S5 each named individually |
| SC-04 | met | automated/integration | `HARNESS_REVIEW_SHA=1d93c727 tests/integration/test-anchor-directions.py` — 7 PASS, exit 0; rows S1–S5 + `reviewed-sha whole scope` |
| SC-05 | met | automated/integration | `test-check-instruction-paths.py` `inline and fenced relative paths are both violations` PASS |
| SC-06 | met | automated/integration | same suite, `product clone can read anchored systematic-debugging skill` PASS (conjoins the exists/not-exists halves) |
| SC-07 | met | inspection | `git diff origin/main 1d93c727 -- .harness/team-config.yaml` → **0 lines**; zero `tools:` lines changed across `.omp/agents` + `.claude/agents` |
| SC-08 | **met** | automated/unit | `tests/unit/test-instruction-workflow-gate.py` 3/3 PASS: gate enforced, and BOTH mutants (step deleted, `exit "$rc"` → `exit 0`) refused. Substance re-confirmed at source: `tests.yml:32` is the sole job `integration:`, gate step at `:200`, `exit "$rc"` at `:216`. Kind now true: `harness.json unit.detect` includes `tests/unit/**`, and the runner globs `tests/unit/test-*.py` |
| SC-09 | met | inspection | `harness-handoff/SKILL.md:62-65` (both placeholders, the `feature-root` command, read-only policy); `DECISIONS.md:6689` DEC-214; `DECISIONS-INDEX.md:214` ruling row present |
| SC-10 | met | automated/integration | `test-inflight-registry.py` PASS in the pinned integration run |
| SC-11 | met | automated/integration | `control-plane feature path is refused` + `both feature path shapes are accepted` PASS; `test-anchor-directions.py` row `SC-11 S2 write observations` PASS |
| SC-12 | met | automated/integration | `test-inject-expertise.py` drift cases (`none` / `1 unanchored path(s)` naming file AND line), both exit 0 |
| SC-13 | met | automated/integration | `test-dispatch-guard.py` PASS (four payloads incl. the `bash`-holding discriminator) |
| SC-14 | met | inspection | four per-file findings at the pin: `harness-product-lead.md:92`, `harness-eng-lead.md:110`, `harness-validator-lead.md:138`, `harness-orchestrator.md:157` (emit duty) + `harness-handoff/SKILL.md:63,65` |
| SC-15 | met | automated/integration | `test-check-domain.py` PASS (`SC-15 PAIR`); guard script unchanged since the graded pin |

Suite runs at the pin, failure prefixes checked before citing exit codes:
`--kind unit` exit 0 (24 files, 243 PASS, zero `FAIL`/`not ok`/`MISCONFIGURED`);
`--kind integration` exit 0 (45 files, 51s) — including `test-check-plan-routes.py`, which was the
pre-rebase red in the c8 qa note and is now green; `--check-layout` exit 0.

## REQ coverage — complete

Re-derived from `plan.yaml` at the pin, not from the prior note: REQ-01 → T-03, T-13. REQ-02 →
T-04..T-08, T-10, T-11, T-13, T-15. REQ-03 → T-05, T-08, T-13. REQ-04 → T-02, T-03, T-12, T-15.
REQ-05 → T-03, T-14. REQ-06 → T-01, T-02, T-04, T-06..T-11, T-13, T-15. Every REQ traced by ≥2
tasks; all 15 tasks carry `change_type:` and `verify:`.

## Findings no criterion covers — operator's, not mine to absorb

- **F1 (real, non-gating).** Ten of fifteen `verify:` clauses in the signed `plan.yaml` name
  `.agents/skills/harness/bin/test-*.py` carriers that `72a6a757` deleted — T-01, T-02, T-03, T-05,
  T-09, T-12, T-13, T-14, T-15. Run verbatim, `python3 .agents/skills/harness/bin/test-check-instruction-paths.py`
  exits **2** (`No such file or directory`). No criterion rests on those clauses — every SC above is
  discharged from the relocated `tests/**` carriers, which I ran green — and the failure mode is a
  **false red, never a false green**, so it masks nothing. But a post-ship re-verification of this
  plan is unrunnable as written. Route: `plan-merge.py amend` the ten `verify:` values to the
  `tests/{unit,integration}/` paths; that resets approval, so it is the operator's call, not a pm write.
- **F2 (bookkeeping).** `plan.yaml` carries no `station:` on the feature or on any of its 15 tasks
  (carried from c13, still true at the pin). Raised for the state check / ship decision.
- **Deviation on SC-08, measurement-equivalent.** The criterion words the mutants as "materialised
  into a temporary path"; the new carrier mutates the workflow text in memory. The asserted outcome
  — the assertion FAILS on each mutant — is met, and since the thing under assertion
  (`instruction_gate_is_enforced`) is a pure string predicate, an on-disk mutant would measure the
  same. Recorded, not softened; it would not gate on its own.
- **Advisories carried unchanged from c13:** `test-anchor-directions.py:14` defaults `REF` to `HEAD`
  rather than `feature.json review_sha`; `.github/workflows/tests.yml:50` is a depth-1
  `actions/checkout@v4`, so a CI run that DID export the pin could not reach the blob; SC-06 joins a
  temp dir rather than `chdir`-ing; SC-05's fenced fixture span is a `.claude/agents/` path rather
  than a `.harness/` one (one prefix-agnostic regex serves both).

## Verification gap, as signed

The BRIEF's own gap stands: **no real factory worker has run.** SC-06 and SC-15 prove the read and
the write from a *simulated* product-shaped cwd. End-to-end factory behaviour is #496's, and this
feature is its precondition, not its substitute.

## Open questions

- **Q1 (non-blocking, operator)** — F1: amend the ten stale `verify:` clauses and re-sign, or ship
  with the plan's clauses known-stale and the criterion evidence carried by this note?
- **Q2 (non-blocking, harness owner)** — carried from c13 and now demonstrated a fourth time: nothing
  between plan and qa cross-checks a BRIEF `evidence:` kind against its carrier's directory, nor a
  task `verify:` path against the tree. Both were found only at goal-check. One `check-state.sh`
  invariant over BRIEF `evidence:` versus carrier path, plus a path-existence check on every
  `verify:` token, would close both.
