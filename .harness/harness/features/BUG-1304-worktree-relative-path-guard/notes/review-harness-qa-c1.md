# QA gate — panel-c1 (independent re-run) — BUG-1304 @ af5ddd7a

**matrix_ok: true.** Both `unit` and `integration` re-ran clean at `af5ddd7a`: exit 0, 0 `^FAIL `
lines, 27 unit files / 46 integration files (73 total, matching the pre-build baseline). The pin is
confirmed byte-identical to the build tip. One genuine disagreement with the prior gate's digest is
recorded below (discovery-count figure) — everything else this run checked independently agrees.

## Pin audit

`git diff --stat af5ddd7a 6dd081a1 -- <all 8 code+test paths>` → empty output, exit 0. The eight
files are byte-identical at the pin and at the build tip; the panel is reviewing what was built.

## Required-kind derivation

Every substantive task (T-01, T-02, T-03, T-04, T-05, T-06, T-09) carries `change_type: logic` in
`plan.yaml`. The matrix's `logic` entry is `always: [unit]`, no `when` clause — **the floor is `unit`
only.** T-07 is `docs` (`always: []`), T-10 is `scaffolding` (`always: []`), T-08 is `abandoned`.

The floor understates what the change needs: two gate scripts (`check-domain.sh`,
`bash-write-guard.sh`) and two shared libraries (`harness_boundary.py`, `inflight_registry.py`) all
move together, and REQ-04 explicitly requires both write routes to refuse identically — textbook
`cross_module` shape (`always: [unit, integration]`), not `logic`. This was reviewed and signed
through three plan-panel cycles (L-01/L-02/F1/F2 all resolved) without anyone flagging the
`change_type` label itself, so I am **not** re-litigating a settled plan question — but I am adding
`integration` to the floor myself, per the matrix's own "floor not ceiling" rule, because the diff
plainly warrants it and in fact delivers it (every SC-01–SC-12 verify block already reads
`evidence: integration`).

**Required kinds this run enforces: `unit` + `integration`.**

## Per-kind results

| kind | required by | cmd | result | files | notes |
|---|---|---|---|---|---|
| unit | matrix floor (`logic.always`) | `run-unit-tests.sh --kind unit` | **satisfied**, exit 0, 0 FAIL | 27 | `test-harness-boundary.py` present and passes; binds `claim_worktrees`/`claim_set_refusal` directly (`case_bug1304_claim_set`, 16 refs) |
| integration | added by qa (diff-warranted, cross-module shape + REQ-04 both-routes) | `run-unit-tests.sh --kind integration` | **satisfied**, exit 0, 0 FAIL | 46 | `test-check-domain.py` (44.1s), `test-bash-write-guard.py` (16.1s), `test-inflight-registry.py` (1.7s) all individually exit 0 |
| component/ui/typecheck | not touched by this diff (no `.tsx`/e2e paths in the 8-file set) | — | not applicable | — | correctly out of scope |

Both commands run with `env -u HARNESS_AGENT_TYPE` per instruction; no phantom `test-plan-merge.py`
regression observed.

## Agree / disagree with `runs/qa-gate-validator/digest.md`

**Agree:**
- `matrix_ok: true`, unit satisfied, 0 FAIL — same as this run.
- SC-06 helper conjunction: I independently read both helpers
  (`test-check-domain.py:4429-4443`, `test-bash-write-guard.py:986-1001`) and confirm each asserts
  all three of (a) `allowed.returncode == 0`, (b) stderr carries none of `enforcement OFF` / `was
  not enforced` / `passing through`, (c) a positive control still exits 2 at the same frozen guard.
  Call-site census matches exactly: 10 on the check-domain route (lines 4475, 4477, 4481, 4512,
  4527, 4546, 4558, 4567, 4584, 4612), 12 on the bash-write-guard route (1044, 1048, 1052, 1056,
  1090, 1108, 1127, 1142, 1157, 1181, 1200, 1228).
- FEAT-51 narrowing: `_feat51_fail_open_cases` (`test-check-domain.py:3953-3976`) narrows only the
  `raising` (directory-at-registry-path) case to exit 2; the `unimportable`
  (missing-`inflight_registry.py`) case still asserts exit 0 with `"boundary was not enforced"`
  (line 3975) — confirmed at source, matches the prior gate's claim exactly.

**Disagree (FINDING):** the prior digest's headline reads *"unit suite rc=0 ... and **20/20**
discovery against the **20 baseline**."* My own run of the identical command
(`run-unit-tests.sh --kind unit`) reports **27 files discovered**, and `--kind integration` reports
**46**, for 73 total — matching the shared context's own baseline claim of 73. I cannot locate any
"20" total anywhere in this tree (27 unit + 46 integration = 73; no kind or subset sums to 20). This
looks like a transcription error in the prior digest rather than a real regression — my own recount
is internally consistent with the independently-stated 73-file baseline — but it is reported as a
disagreement per instruction, not silently reconciled.

## Adequacy assessment (not just green)

- **Binding breadth:** the two new core functions (`harness_boundary.claim_worktrees`,
  `claim_set_refusal`) are exercised directly at the unit level (`test-harness-boundary.py`,
  `case_bug1304_claim_set`), not only indirectly through the two guard scripts' subprocess
  integration tests — so a regression in the shared library itself, not just in a guard's wiring to
  it, is caught at the cheaper unit layer.
- **SC-06 discrimination machinery genuinely discriminates by SC-06's own wording:** confirmed
  above — every pre-change call in both suites carries the full three-part conjunction, not an
  exit-code-only check. This is a **reasoned** (source-read) conclusion, not a mutation-proven one:
  I read the helper and its call sites; I did not flip a guard branch to watch a specific case go
  red. That gap — shape proven, discriminating power against a live mutant not independently
  reconfirmed by me — is the same gap the prior gate's `adequacy_notes` already disclosed, and I
  have not closed it either.
- **Discovery count is non-zero and matches the pre-build 73-file baseline** (27 unit + 46
  integration), so this is not a sweep over an empty set exiting 0 for the wrong reason.
- Not independently re-verified in this pass: no mutation/fault-injection against the 22 new
  claim-set assertions, and SC-07's `DECISIONS.md` five-answer completeness was not re-audited here
  (out of this gate's required scope; it is an `inspection`-verified criterion, not `automated`).

## Verdict basis

`matrix_ok: true`. Suite green at the pin with the derivation above. One genuine, unresolved
disagreement (discovery-count figure) is surfaced as a finding rather than reconciled away, per
instruction — it does not itself block, since my own count is corroborated by the shared context's
independently-stated baseline and by two separately-run commands.
