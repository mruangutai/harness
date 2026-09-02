# FEAT-51 goal-check — the twelve success criteria

**Bottom line: the goal is delivered. Ten of twelve criteria are met, SC-12 is withdrawn, SC-10 is
the operator's hand-test and stays `not_met` until he runs it. One criterion, SC-07, is `not_met`
for a TEST-ONLY reason: the behaviour it grades is correct and I proved it, but the committed OMP
case cannot go red under the mutation SC-07 itself names.** No code defect was found on any
criterion.

Graded at **`4f97dfe5`** (working tree clean; no `review_sha` is pinned yet — the panel has not run).
The tip commit `4f97dfe5 [harness:main] defer orphan registry import` changed
`check-domain.sh` after the batch contract was measured, so both whole suites were re-measured here
rather than inherited (G-07). Nothing in this run wrote to either checkout outside `/tmp`.

## Per-criterion table

| SC | verify | command / read performed | observed | verdict |
|---|---|---|---|---|
| 01 | automated | `/tmp/gc51_probe_sc010203.py` — real `validate-digest.py --hook`, one fixture, `VERDICT: SUSPENDED` + `awaiting: harness-pm` vs the **byte-identical** payload with only the verdict token swapped to `PASS` | exit **0** / exit **2**, refusal carries `children in flight`. Suite: `test-validate-digest.py` `run_t51_suspension_cases` 6/6 PASS, whole file exit 0 | **met** |
| 02 | automated | same probe, three assertions run separately: no live child / `awaiting:` omits a live child / persona is a member (`harness-pm`); plus an orchestrator control | 2, 2, 2, and the orchestrator control **0** — so the persona gate is not a blanket refusal | **met** |
| 03 | automated | same probe: `reg.live_claim()` **read back from the registry file** after a SUSPENDED return, and after a terminal `PASS` | claim present after SUSPENDED; `None` after the terminal return (hook exit 0) | **met** |
| 04 | automated | `/tmp/gc51_probe_sc0405.py` — real `check-domain.sh`, real registry. (1) orphan `Write` of `BRIEF.md`; (2) same write with the writer's own claim live; (3) orphan `Write` of `plan.yaml` | (1) exit 2, stderr names the **exact** path `…/quarantine/harness-orchestrator-feat51-w/BRIEF.md`; (2) exit 0; (3) exit 2 carrying `exactly ONE writer` and **no** quarantine text | **met** |
| 05 | automated | same probe, same orphaned persona: `notes/report.txt`, the quarantine path, `BRIEF.md`; canonical sha256 before/after the refused call | 0, 0, 2; sha256 unchanged | **met** |
| 06 | automated | `test-quarantine.py` (26/26 PASS): canonical 14 tasks `T-01..T-14` + quarantined 1-task `T-15` → adopt yields **fifteen** ids and never the 1-task file; `discard` removes the named dir only; `list` sha256-identical before/after. Timer clause by `grep` for every `adopt`/`discard` caller across `bin/` | all PASS; the only callers of the two verbs are the CLI itself and the two gates' refusal text — no scheduler, no timer | **met** |
| 07 | automated | `/tmp/gc51_probe_sc07.py`; `check-omp-port.py`; per-file enumeration of `.omp/agents/harness-*.md`; both suites at HEAD | see below | **not_met** |
| 08 | inspection | `git show 4f97dfe5:.claude/skills/harness/SKILL.md` and `…harness-team/SKILL.md` | four clauses cited below, all four present in **both** files | **met** |
| 09 | automated | `git show 4f97dfe5:.harness/harness/docs/DECISIONS.md` `## DEC-210`; index row; `gen-decisions-index.py --stdout \| diff -`; `/tmp/gc51_probe_sc09.py` red proof | diff **exit 0**; entry names both `check-domain.sh` and `plan-sign-gate.sh`, `quarantine.py adopt`, the `plan.yaml`→`plan-merge.py`-through-`Bash` sentence, the OMP-unchanged clause; index ruling names "the Claude Code compatibility host". Red proof: replacing `plan-sign-gate.sh` in the entry reddens `test_dec_210_entry_names_both_enforcement_points` (suite exit 1) | **met** |
| 10 | uat | not run — not mine | pending the operator; script below | **not_met (pending uat)** |
| 11 | automated | `/tmp/gc51_probe_sc11.py` — real `plan-sign-gate.sh`, `agent_type: harness-pm` (the persona the criterion names; the suite uses `harness-orchestrator`), one live non-`omp` claim held by `harness-qa` in `other-session` | all three refusals exit **2** and each stderr names the **exact** path `…/quarantine/harness-pm-feat51-w/plan.yaml`; all three exit **0** with the persona's own claim live; all three exit **0** with `runtime: omp` + a live supervisor pid. **Red proof:** `plan-sign-gate.py` from `72ec341d^` → all three exit **0** | **met** |
| 12 | — | `BRIEF.md ## Verification gaps` | **withdrawn** by operator ruling: `bash-write-guard.sh` already permits a plain `rm -rf` of a quarantine directory (`PF-2b48984b50ff69c5dfdf8afa20c3956b`), so a rule covering only `quarantine.py discard` would have recorded a protection the tree does not have (D-18). Number left as a deliberate gap; not renumbered | **withdrawn** |
| 13 | automated | files read at the sha (`git show 4f97dfe5:…test-check-domain.py`, `…test-plan-sign-gate.py`); mutation (c) applied **at source** in `/tmp/gc51_probe_sc13b.py` | six items present and enumerated below; all four fail-open cases assert exact exit **0** AND `boundary was not enforced`; source mutation to a silent handler reddens **all four**; widening the handler reddens the negative control | **met** |

## SC-08 — the four clauses, cited

`.claude/skills/harness/SKILL.md` (step 4): suspension is the legal turn-end `:45`; no poll/sleep/
heartbeat/invented work `:46-47`; same parent resumed and the registry blocks a replacement while the
claim is live `:47-49`; resumed parent runs `quarantine.py list` then explicitly adopts or discards,
neither automatic nor timer-driven `:49-51`.
`.claude/skills/harness-team/SKILL.md` (step 3d): `:126-128`, `:128-129`, `:129-131`, `:131-134`
respectively.
**Why a parent reading only these four would not poll:** the turn-end it is given is *legal and
nonterminal*, and the clause that follows says the host — not the parent — resumes it, so waiting
buys nothing and the permitted count of such actions is stated as zero.

## SC-13 — the six items, enumerated at the sha

`test-check-domain.py`: raising registry (`os.mkdir(registry_path)` → `IsADirectoryError`) `:3463-3466`;
unimportable (`os.remove(<copytree>/inflight_registry.py)`) `:3468-3474`; negative control `:3459`.
`test-plan-sign-gate.py`: raising `:526-532`; unimportable `:534-544`; negative control `:521`.
Each fail-open case asserts `rc == 0` **and** `"boundary was not enforced" in stderr`; each negative
control asserts exit 2 with a live orphan claim held by another persona in another session.

> Method note for a successor: the two **unimportable** cases `copytree` the directory the *test
> file* lives in, so they ignore `CHECK_DOMAIN_BIN`/`PLAN_SIGN_GATE_BIN`. An override-based mutation
> reddens only two of the four; the mutation must be applied to a whole mutant checkout and the test
> run from inside it. Done that way, all four redden.

## SC-07 — why it is `not_met`, and what is actually wrong

Clause by clause:

- **`check-omp-port.py` exits 0.** ✅
- **`.omp/agents/harness-*.md`** — 16 files enumerated one by one; 15 declare `blocking: true`,
  the sixteenth is `harness-orchestrator.md`, the criterion's own exception. ✅
- **Both suites.** `run-unit-tests.sh --kind unit` → **exit 0**, no `FAIL` lines. `--kind integration`
  → **exit 1**, and the failure set is exactly `test-check-plan-routes.py`'s `6 FAILURE(S)`
  (`case_04`, `case_05`, `case_15`, `case_17`, `case_19d`, `case_19d2`) plus the one script-level
  `FAIL test-check-plan-routes.py` line = the contract's seven. `diff` of the two `team-config.yaml`
  copies returns **only** T-03's approved `.harness/*/features/*/quarantine/**` route plus its
  comment, which is the whole cause. Not a defect; this clause is satisfied by decomposition. ✅
- **OMP allow at registry AND hook level, with a live supervisor pid.** Behaviour ✅ — registry
  `orphan_write` returns `False` and `check-domain.sh` exits 0. Committed guard: registry side is
  covered properly (`test-inflight-registry.py` `case_33` spawns a real process for the pid). **Hook
  side is not:** `test-check-domain.py`'s `an omp-runtime writer is never quarantined` and
  `test-plan-sign-gate.py`'s `an omp-runtime writer is never quarantined on the Bash route` both
  claim with `runtime="omp"` and **no** `supervisor_pid`, so `_expire` (`inflight_registry.py:215-219`,
  `_omp_claim_live:183-185`) prunes the claim outright. With no claim left there is nothing for the
  runtime condition to decide, and the case would pass against the pre-change tree too. ❌
- **"Discrimination is demonstrated: removing the runtime condition turns the OMP case red."** I
  removed it (`claim.get("runtime") != "omp" for claim in feature_claims` → `True for …`) and the
  behaviour reddens: `orphan_write` → `True`, hook → exit 2. But the **shipped** case stays
  `ok    an omp-runtime writer is never quarantined`. As written against the suite, this clause is
  **false**. ❌

**Remedy: tests, not code.** Pass a live `supervisor_pid` into the two hook-level OMP fixtures
(`test-check-domain.py` `run_feat51_orphan_write` `root_with_claim(..., runtime="omp")`, and
`test-plan-sign-gate.py`'s `_omp`), exactly as `case_33` already does. **Lane: main-session-direct.**
Both files are DEC-174 enforcement-layer test files; no squad may take this.

## SC-10 — what the operator must do

From the **main checkout, after merge** (a spawned agent loads its skills from there, not from this
worktree — `BRIEF.md ## Verification gaps`): dispatch a real Claude Code lead, interrupt it while its
member is mid-run, then resume it, and confirm three things by hand — (1) a directory under
`.harness/harness/features/<FEAT>/quarantine/<agent>-<session8>/` holds the orphan's result;
(2) `git status` shows no canonical `plan.yaml`/`BRIEF.md`/`feature.json`/`STATE.md` overwritten by
the orphan; (3) nothing became canonical until he ran `quarantine.py adopt --file <path>` himself.
Not gradeable by code reading; it is the only evidence of a parent's actual conduct under
interruption.

## Advisory — guard gaps that did not change a verdict

Three committed cases assert a weaker string than their criterion states. Behaviour was confirmed by
completed runs of the real binaries, so the verdicts stand, but the guards are looser than the
criteria: SC-04's refusal case asserts the substring `quarantine` rather than the exact path
(`test-check-domain.py:3457`); SC-04's `plan.yaml` case does not assert the *absence* of quarantine
text; SC-05's "no canonical artifact is modified" clause has no committed before/after assertion.
Same lane as SC-07's remedy, same file.

## Open questions

- **Q1 (non-blocking):** should SC-07's remedy be a fix cycle now, or a follow-up? The behaviour ships
  correct; only the guard is vacuous. Two one-line fixture changes, main-session-direct.
- **Q2 (non-blocking):** nothing emergent surfaced. Every observation above is covered by an existing
  criterion; no new "done" condition was adopted.
