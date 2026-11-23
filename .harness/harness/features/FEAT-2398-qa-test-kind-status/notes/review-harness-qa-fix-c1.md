# QA fix-c1 — FEAT-2398 at 2f50e8bb1f5e6442742c53e1e2997a8be341d58b — evidence green, unconditional PASS REFUSED by the hook: ESCALATE

**Hook refusal (not a test failure).** The PASS yield was refused: `no trusted receipt location: the registered run fix-c1-validator is a fix run but the dispatch's harness_mission is None`. A fix run needs both the `fix-c<N>-validator` id and a dispatch-forwarded `harness_mission: fix`; the hook saw no mission. Re-running the printed repair commands (from the feature worktree, HEAD 9a975551, not the pin) cannot change the mission and would replace the pin-tested receipts with a different tested_commit, so I did not run them. Receipts at the pin stay as the runner wrote them. Lead/Main must re-dispatch QA with `harness_mission: fix`; then the evidence below supports PASS. No PASS is claimed from this refused return.

**All four prior must-fix are resolved at the pin; the focused verify, unit and integration are green; runner receipts for this live run are recorded.** Run `fix-c1-validator` (mission fix). Author nothing; one environment preparation (`bun install --frozen-lockfile` in the pin, installs ignored `node_modules`, tracked tree stayed clean).

## Phase 1 (from BRIEF/plan only) — expected coverage
SC-01 unresolved / active-null: only misconfigured+BLOCKED accepted, other states and omission refused, naming both repairs. SC-02 excluded / locally_run controls + disclosure no-op. SC-03 pinned policy for product and Harness features; refusals without fallback; empty-kind must not bypass pin. SC-04 omission refusal under every verdict x matrix_ok; full floor only at PASS/true; BLOCKED kind-free allowed when no policy. SC-05 inspection of prose. Phase-2 gap check: none left uncovered by a named case (see below).

## Candidate vs installed
Candidate behavior is proved only by tests run from the pin checkout `.claude/worktrees/.pins/FEAT-2398-qa-test-kind-status--fix-c1-validator--harness-qa` (HEAD 2f50e8bb). Installed control-plane hook `.claude/skills/harness/bin/validate-digest.py` sha256 `ecd7c09f…81b4`; candidate at pin `7e0feb6d…a2a3` (different bytes). Nothing here claims the installed hook behaves as the candidate.

## Runs (exact commands, this run)
- Focused T-01 verify at pin: `python3 tests/integration/test-validate-digest.py --only run_feat2398_qa_policy_cases` → **69/69 ok, exit 0** (0 FAIL lines).
- `run-unit-tests.py --kind unit --shard 1/1 --manifest <abs>/runs/fix-c1-validator/qa/manifest-unit.json` → exit 0, **66 files selected / 66 completed**, runner_exit 0, tested_commit 2f50e8bb.
- `... --kind integration ...manifest-integration.json` → exit 0, **95 selected / 95 completed**, "ALL PASSED", includes `PASS test-validate-digest.py`; tested_commit 2f50e8bb. (Prior red was missing `tsc` + fixture audit; both gone — tsc present after install, fixture audit passes inside the integration bucket.)
- Receipts: `.harness/harness/features/FEAT-2398-qa-test-kind-status/runs/fix-c1-validator/qa/manifest-{unit,integration}.json` (runner-written, unedited). Each kind run once; full output retained at `/tmp/fix-c1-{unit,integration}.txt`. Main must force-add them (DEC-255).
- Required active kinds from `.harness/harness.json`: unit, integration (T-01 change_type cross_module → both always). Others: component/ui unresolved but not on this floor; functional/eval excluded (DEC-187 signed); omp_session_accessor/handoff_comprehension/issue_types_live locally_run, detect surfaces untouched; typecheck active but `classifies_tests: false`, not a matrix kind.

## Prior findings
1. **High empty-kind CLI bypass — RESOLVED.** `_qa_claims_need_policy` (validate-digest.py) now requires policy when kinds, started tasks, or PASS+matrix_ok; `_qa_unestablished` lets only kind-free BLOCKED/ESCALATE stand. Cases: CLI empty-kind PASS refused (exit 1, "review pin…no fallback"); CLI kind-free BLOCKED accepted; real hook unpinned kind-free BLOCKED accepted (`test-validate-digest.py` `_kp_sc03_harness_cases`). Natural red at the failed pin 685e861a: exactly those 2 cases FAIL (`t01-fix-c1-red.txt` §685e861a: 67 ok / 2 FAIL).
2. **Medium fixture audit — RESOLVED.** `_kp_write_policy`/`_kp_pin_policy` route through `write_config`; P3 truncates `build_config()` (deliberately invalid JSON kept). Integration runner and its audit are green (95/95).
3. **Medium omission proof — RESOLVED (coverage), discrimination vs 685e861a unshown.** `KP_OMISSIONS` = BLOCKED/ESCALATE/FAIL x matrix_ok true/false/n/a + PASS/true, for both unresolved and active-null (20 "omitting the required kind" cases in green receipt), refusal asserts kind name plus both repairs. Against baseline 9eb07b4f all 18+ are natural-red; against 685e861a they were already green (the implementation was unconditional), so these cases close the missing automated proof but do not by themselves redden against 685e861a. I could not run a mutation proof: the bash-write-guard denies in-place edits of pinned source for QA (DEC-151/153). Reported as unshown, not as non-discriminating.
4. **Low false INV-49 instruction — RESOLVED.** Skill line 38 now says INV-49 only requires BRIEF `## Verification gaps` disclosure, never a waiver; skill, SPEC §9 and DEC-256 D01 agree on the missing-pin path. Advisory: the skill says stop with `BLOCKED`, SPEC/DEC say BLOCKED or ESCALATE (validator accepts both) — consistent, not contradictory.

## Moved acceptance cases
Diff 685e861a..2f50e8bb of the test file: the three PASS-acceptance cases ("neither new field", "populated fail_first", "fail_first block-mapping") moved from `case(...)` to `qa_pinned_case(...)` with bodies and assertion (accepted → no errors) unchanged; `run_qa_pinned_cases` validates them in-process over a real committed repo with `review_sha` pinned (`_qa_pinned_feature`), registered in `main`. `run_qa_verification_mode_cases` uses the same pinned feature. Real CLI and real hook coverage live in the feat2398 cases above, not in the moved set. Note: these three now have no unpinned-refusal twin in that block; the refusal is covered by `SC-03 ... CLI/unpinned` cases.

## fail_first (natural red, retained commands in receipts)
SC-01..04: `notes/receipts/t01-red.txt` (39/52 FAIL at baseline 9eb07b4f) and `notes/receipts/t01-fix-c1-red.txt` (54 FAIL/15 ok at 9eb07b4f over the 69-case file; 2 FAIL at 685e861a). Green: `t01-green.txt` (52/52), `t01-fix-c1-green.txt` (69/69) and my own rerun 69/69. Tier: natural red (signature-bearing: assertion diffs naming missing refusal text). I did not re-reproduce reds; receipts are Main-captured, their green side reproduced here.

## Verdict inputs
suite pass, failures 0, matrix_ok true, kinds unit+integration satisfied. SC-05 is `verify: inspection` (pinned prose confirmed above; no automated claim). Product docs/spec.md, decisions.md, architecture.md absent per BRIEF; not invented.

## Open / gaps
- Omission matrix not mutation-proved against 685e861a (guard-denied); reds exist only against baseline.
- Only my own evidence has examined this fix after the review round that raised it (no second independent QA).
