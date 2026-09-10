# QA matrix gate — FEAT-104 strict-digest-schema — RE-GRADE at tip `1a66d2cc`

**Verdict: PASS.** The blocking `qa_gate` passes at `1a66d2cc`. Both prior-cycle `must_fix` items are
CLOSED on disk. No production defect, no coverage regression, no team-authored test edit survives.
This supersedes the prior cycle's FAIL record in full.

## 1. Tree under grade

```
git -C <worktree> rev-parse HEAD
```
→ `1a66d2cc1cb6cb753bae4a91b62df14b8a4bbf0a` — matches the pinned tip exactly.

```
git -C <worktree> status --porcelain -- tests/ .claude/skills/harness/bin/ .agents/skills/harness/bin/
```
→ empty output. **No uncommitted modification exists under `tests/` or either `bin/` tree** — the
graded tree carries only committed content, no live team-authored edit.

## 2. Full suite

```
env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh; echo "SUITE_EXIT=$?"
```
→ `pool: 8 workers, 106 files, 76.37s wall` · `ALL PASSED` · `SUITE_EXIT=0`.

Several `^FAIL ` lines appear inside `test-factory-claim-mutation.py`'s own BUG-1290 mutation-proof
output (lines ~140/199 of that file construct the literal prefix as proof text) — per the correction
above, this is NOT a red signal; graded on `SUITE_EXIT=0` alone, which is clean.

## 3. Per-kind commands (test_matrix floor for `change_type: logic`)

- `unit` (active): `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` → `pool: 8 workers, 36 files, 2.33s wall`, `UNIT_EXIT=0`. **satisfied** (regression gate; see coverage gap below).
- `integration` (active): `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` → `pool: 8 workers, 70 files, 75.89s wall`, `ALL PASSED`, `INTEGRATION_EXIT=0`. **satisfied** — every new automated criterion for T-01/T-04/T-05/T-06/T-07/T-08 lives here.
- `component`, `ui`, `typecheck`: `cmd: null`, status `unresolved` in `.harness/harness.json` — not obligated by `change_type: logic`, no predicate fires. **not applicable.**
- `functional`, `eval`: status `excluded`, signed DEC-187. **not applicable.**
- `omp_session_accessor`, `handoff_comprehension`, `issue_types_live`: `locally_run`. This diff does not touch any of these three kinds' `detect` surface (schema/digest/CLI code, not session-accessor/handoff-prompt/issue-type surfaces). **not applicable — no recorded run required.**

**Matrix floor for `change_type: logic` is MET**: `unit` + `integration` both satisfied, nothing else obligated.

## 4. must_fix #1 — DEC-174 authorship violation: **CLOSED**

```
git -C <worktree> log --oneline abff2a8444669cfabd01f2905c1de48595b7aa76..1a66d2cc -- tests/
```
→ `1a66d2cc test(feat-104): update strict schema compatibility cases`, `9fc8543f test(feat-104): lower schema test complexity`, `9be1d722 test(feat-104): simplify schema regression drivers`, plus the original T-01/T-04/T-06/T-07/T-08 production+test commits (`684d3ad2`…`d873a915`).

`git show --stat` on each of the three: all three are authored and committed by **Mike Ruangutai
<molchair@gmail.com>** (the human/main-session identity), touching only `tests/integration/test-check-domain.py`,
`tests/integration/test-validate-digest.py`, `tests/integration/test-check-domain-artifact.py`. None
carries `[harness:<step-id>]` (the `agent_prefix`) — consistent with these being main-session-direct
commits, not dispatched-agent commits; none carries the literal `[harness:human]` marker either
(`commit_attribution.human_prefix` — a naming-convention gap, not a routing defect, and outside this
dispatch's remit to fix). No commit under this range is authored by a `harness-qa`/team identity.
**On-disk: no team-authored edit survives; the landed repairs are the main session's own commits.**

## 5. must_fix #2 — red suite at `50c4bce9`: **CLOSED, both causes**

```
git -C <worktree> diff 50c4bce9 1a66d2cc -- tests/integration/test-check-domain-artifact.py tests/integration/test-validate-digest.py
```
- **(a) creation-floor fixtures** — all four cited sites now write `schema_version: 2`:
  `test-check-domain-artifact.py` `_bug1124_new_file_case` (state-new-file-allowed),
  `_bug1305_marker_recovery_cases` (absent-prior recovery), `_bug1305_marker_file_protection`
  (run_uid legality), `_bug1305_identity_allow_cases` (identity-absent case, via
  `.replace("schema_version: 1", "schema_version: 2", 1)`). Each carries an inline comment tying the
  bump to satisfying T-06's creation floor while preserving what the case actually isolates
  (run-id collision / recovery / run_uid legality / identity absence), not the floor itself.
  **Mechanism: fixture data updated to the new legal minimum; no production code touched.**
- **(b) live-checkout temp dir** — `test-validate-digest.py:_t08_revision_failures` (formerly
  line ~3231) dropped `dir=os.path.dirname(VALIDATE)` from `tempfile.TemporaryDirectory(...)`,
  defaulting to the system temp root. **Mechanism: the AST-scanned path is gone; nothing under
  `tests/integration/` is written outside the system temp dir for this case.**

Independent guard re-run: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-suite-independence.py`
→ `root <worktree>`, `discovered 106`, `ok no test mutates a path derived from the live checkout`,
`SUITE_INDEP_EXIT=0`. The specific scanner that raised (b) is clean at the tip.

## 6. Four discrimination checks — CARRIED FORWARD (verified previous cycle by harness-validator-lead, not re-derived)

- Pre-change red proof via `tests/integration/fixtures/pre-t04-validate-digest.py.fixture`: pre-change accepts rogue keys (exit 0), current refuses (exit 2, names them); 3 persona comparisons + 1 independent hand-run.
- Per-key coverage: `tests/integration/test-check-domain.py:121-124` set-equality `schema_keys == DECLARED` plus full-step accept.
- Refusal message (not just exit code): one-shot 3-key message asserts `digest contract is closed`, `PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`, and every offending key.
- `schema_version: 2` boundary both directions: creation accepted@2/refused@1/refused-absent/refused-as-string"2"; version-1 update still allowed; `test-check-state.py`'s version-1/version-2 pair.

Spot-check at the tip: the full-suite run above reports these same named case counts unchanged —
`55/55 T-01 schema cases passed`, `34/34 T-04 undeclared digest key cases passed`,
`10/10 T-08 revision and lead replay cases passed` — all inside `test-validate-digest.py`, which is
part of this diff and was touched by the landed repair commits. **Anchors resolve at `1a66d2cc`.**

## 7. Coverage gaps

- `unit` binds **zero new assertions** for this diff — every new automated criterion (T-01/T-04/T-05/T-06/T-07/T-08) rests on `tests/integration/`. **Advisory, not a gate failure** — `unit` ran clean as a regression floor per the repository's standing convention that hook/CLI subprocess behavior lives in `integration`, and the matrix does not require `unit` to carry new coverage, only to pass.
- T-07's evidence container has accept/refuse cases but **no pre-change comparison** (unlike T-08's vendored fixture) — nothing demonstrates the container's assertions could have been red before the change. **Advisory gap**, not a gate failure: T-07 is exercised functionally (accept+refuse both present, per-key granular per §6) and check-domain.sh's step-schema refusal did not exist pre-diff at all (no "revert to" state to fixture against), same reasoning the prior cycle applied to T-06/T-07 generally.

## 8. `check-state.sh`

```
bash .agents/skills/harness/bin/check-state.sh
```
→ exit 1 (project-wide, pre-existing violations, not caused by this diff). FEAT-104-scoped output:
10 `INV-26` card/plan-mismatch lines (T-01,T-03..T-10, parent) — **known class, not routed** (D-23:
cards move to done only at `gh-sync.py ship`, which has not run). `INV-29`'s `qa-bug440-c3-probe`
worktree ("terminal status could not be determined") **appears in this run's output** — **known
class, not routed** per dispatch. Two additional informational `note` lines (not `VIOLATION`) report
run dirs `2026-09-09-01-t09-product` and `2026-09-09-02-qa-gate-validator` unrecorded in
`feature.json` — informational orphan-run notes from this same resume flow, not a `VIOLATION`; not a
new defect class beyond the two named exemptions and not routed.

## must_fix

None. Both prior items are CLOSED on disk as shown above.

## Files touched

None. This dispatch is read-only over code and tests; only this note was written.
