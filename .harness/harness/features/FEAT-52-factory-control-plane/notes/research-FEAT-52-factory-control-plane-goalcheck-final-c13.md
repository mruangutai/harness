# Goal-check (final) — FEAT-52 — all 15 criteria at `review_sha 72a6a757` (HEAD `7ca27941`)

## BLUF

**FAIL — 14 of 15 met; one criterion, SC-08, carries a false `evidence:` label and cannot be
discharged as signed.** B1 (the DEC-213 layout violation) is **CLOSED**: `72a6a757` deletes the two
stale `bin/` carriers (168 deletions, deletions only), `run-unit-tests.sh --check-layout` exits **0**,
and `git diff --stat 72a6a757 -- . ':(exclude).harness'` is empty, so the tracked source I graded IS
the pinned tree. The user's amendment `7ca27941` is BRIEF-only and changes exactly the eight
`evidence: unit` → `integration` lines plus the approval date to 2026-09-02.

**The one gap is the same defect class the amendment fixed, on a criterion the amendment did not
list.** SC-08 declares `evidence: unit`; its only carrier is
`tests/integration/test-check-instruction-paths.py:79-86` (`case_workflow_gate`). `run-unit-tests.sh:27`
selects `tests/unit/test-*.py` for `--kind unit`, and `harness.json` `unit.detect` is
`tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py` — the hyphenated name matches none of the
non-directory globs. **The `unit` kind never executes SC-08's assertions.** No `tests/unit/` file
reads `.github/workflows/tests.yml` (grep: zero hits). Substance is proven; the declared method is not.

## Verdicts

| SC | Verdict | Method | Evidence at `72a6a757` |
|---|---|---|---|
| SC-01 | met | automated/integration | `tests/integration/test-inject-expertise.py` case4 (`:180-182`, no Expertise at any tier) + case4b (`:201`, `injected == root and injected != product_cwd`) — 21 ok, exit 0 |
| SC-02 | met | automated/integration | case4c `:221` (UNRESOLVED + `VERDICT: BLOCKED`, exit 0) and case14 `:401-404` (`^[ \t]*exit [1-9]` zero matches + positive control on `"  exit 2"`) |
| SC-03 | met | automated/integration | five separate `scope contains …` assertions, `test-check-instruction-paths.py:61-62`; all PASS |
| SC-04 | met | automated/integration | `test-anchor-directions.py` 7/7 exit 0 run with `HARNESS_REVIEW_SHA=72a6a757`; rows S1-S5 each read via `git show <ref>:<path>`, plus `reviewed-sha whole scope` |
| SC-05 | met | automated/integration | `:42` — exit 1, `:1:` inline, `:3:` fenced, `2 violation(s)`. `TOKEN` (`check-instruction-paths.py:17`) and `_tokens` (`:60-67`) are prefix-agnostic, so the fenced fixture exercises the same code path a fenced `.harness/` span would |
| SC-06 | met | automated/integration | `:71-76` conjoins `isfile(debug_path)`, `not os.path.exists(product_path)` and a content read — the discriminating half is present |
| SC-07 | met | inspection | `.harness/team-config.yaml` zero-line diff `origin/main..72a6a757`; `check-domain.sh` **unchanged**; no `tools:` line changed in any `.omp/agents/*.md`; the two writable claims naming a control-plane path (`harness-dev-ops.md`, `harness-documentor.md`) are re-anchorings of pre-existing claims, no new path |
| SC-08 | **partial** | automated/unit | Substance green: `case_workflow_gate` asserts real `tests.yml` enforced (`:200-216`, `exit "$rc"`) and both mutants refused (`:82`, `:86`). Two deviations: (a) declared kind `unit`, carrier under `tests/integration/` — the `unit` runner never runs it; (b) mutants are in-memory `str.replace`, not "materialised into a temporary path" as the criterion states |
| SC-09 | met | inspection | `harness-handoff/SKILL.md:62-66` at the pin — both placeholders, the `inflight_registry.py feature-root` command, the read-only policy; `DECISIONS.md:6689` DEC-214; `DECISIONS-INDEX.md:214` ruling written; `test-gen-decisions-index.py` 14 ok, exit 0 |
| SC-10 | met | automated/integration | `test-inflight-registry.py` 126 ok, exit 0 (`feature-root` CLI, worktree-differs and owner-root halves) |
| SC-11 | met | automated/integration | `test-check-instruction-paths.py:47-52` (control-plane-anchored feature path refused, named reason) + `test-anchor-directions.py` row `SC-11 S2 write observations` and whole-scope row, both green at the pin |
| SC-12 | met | automated/integration | `test-inject-expertise.py:249-252` asserts `none`, `1 unanchored path(s)` AND `.omp/agents/harness-qa.md:1`; `inject-expertise.sh:75` invokes the real checker over exactly the four files; both branches exit 0 |
| SC-13 | met | automated/integration | `test-dispatch-guard.py` 48 ok, exit 0; `dispatch-guard.sh` is +48 lines with no other guard changed |
| SC-14 | met | inspection | four per-file findings at the pin: `harness-product-lead.md:92`, `harness-eng-lead.md:110`, `harness-validator-lead.md:138`, `harness-orchestrator.md:157` (emit duty), plus `harness-handoff/SKILL.md:66` |
| SC-15 | met | automated/integration | `test-check-domain.py` 301 ok, exit 0 (`SC-15 PAIR`); guard script itself unchanged, so the allow/refuse pair measures shipped behaviour |

Suites I ran at the pin (tracked source identical to `72a6a757`): `test-check-instruction-paths.py`
16 PASS, `test-anchor-directions.py` 7 PASS, `test-inject-expertise.py` 21 ok,
`test-inflight-registry.py` 126 ok, `test-dispatch-guard.py` 48 ok, `test-check-domain.py` 301 ok,
`test-gen-decisions-index.py` 14 ok — every one exit 0, zero `FAIL`/`not ok` lines.
`run-unit-tests.sh --check-layout` exit 0. Each runner's failure accounting checked before citing its
exit code (e.g. `test-check-instruction-paths.py:92-93` raises on any false row).

## REQ coverage — complete

REQ-01 → T-03, T-13. REQ-02 → T-04..T-08, T-10, T-11, T-13, T-15. REQ-03 → T-05, T-08, T-13.
REQ-04 → T-02, T-03, T-12, T-15. REQ-05 → T-03, T-14. REQ-06 → T-01, T-02, T-04, T-06..T-11, T-13,
T-15. Every REQ is traced by at least two tasks; nothing is unimplemented. All five blockers of the
last three cycles (B1-B5) are closed.

## The one gap, and the two routes out — operator's choice, not mine

SC-08 needs ONE of:

1. **BRIEF amendment** — `evidence: unit` → `integration`, identical in kind to the eight already
   amended in `7ca27941`. Zero code change; the criterion is then met on the evidence above.
2. **Relocate the assertion** — `case_workflow_gate` spawns no subprocess (it reads `tests.yml` and
   mutates a string), so it is a genuine unit test and could move to a `tests/unit/` carrier, making
   the signed label true. Costs a commit and a `review_sha` re-pin.

Re-labelling a signed criterion is not a pm write, so I record it unmet rather than reading `unit`
loosely. Deviation (b) — in-memory mutants versus "materialised into a temporary path" — is
measurement-equivalent (both mutants ARE asserted red) and would not gate on its own.

## Advisory, non-gating

- `test-anchor-directions.py:14` defaults `REF` to `HEAD`, not to `feature.json review_sha`. Content
  coincides today, so no grade turns on it; a qa run without `HARNESS_REVIEW_SHA` grades HEAD while
  SC-04/SC-11 mandate the pin.
- `.github/workflows/tests.yml:50` is a bare `actions/checkout@v4` (depth 1). Harmless only because
  of the default above — a CI run that DID export the pin could not reach the blob.
- SC-06's `product_cwd` is a temp dir joined with the relative path rather than a `chdir`; the
  criterion says "process working directory set to". Equivalent measurement, looser mechanism.
- SC-05's fenced fixture span is `.claude/agents/harness-pm.md`, not a `.harness/` path as the
  criterion words it. Non-discriminating: one prefix-agnostic regex serves both.
- `plan.yaml` carries no `station` on the feature or on any of its 15 tasks. No criterion covers it;
  raised for the state check, not as a FEAT-52 defect.

## Open questions

- **Q1 (blocking the ship decision, operator)** — SC-08: amend the label to `integration`, or move
  `case_workflow_gate` to `tests/unit/`? See the two routes above.
- **Q2 (non-blocking, harness owner)** — third cycle running in which a criterion's `evidence:` kind
  was falsified by where its carrier lives. Nothing in the plan or qa path cross-checks a declared
  kind against the carrier's directory, so it is found only at goal-check. A `check-state.sh`
  invariant over BRIEF `evidence:` versus carrier path would close it.
- **Q3 (non-blocking, harness owner)** — carried from c11/c12: a rebase or a later commit can falsify
  criteria already graded met, and nothing re-takes grades after history moves.
