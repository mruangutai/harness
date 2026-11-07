# QA gate c1 — FEAT-71-corpus-independence, T-01, review_sha 3e6add2af05f5b801afec1ef69440fe54e1529a4 (pin unchanged)
Supersedes the disposition of `review-harness-qa-c0.md` (retained). No tests, builds, source edits or repro were run for c1; it re-reads c0 and the two prior logs only.

## BLUF
**BLOCKED (policy conflict, not a shipped-code defect).** The measured outcomes in c0 stand unchanged: unit 57 files exit 0, integration 84 files exit 0, fail-first reds for SC-02/SC-03 reproduced. c0's `PASS` is withdrawn because it rested on treating the BRIEF's "no fresh live run" acknowledgement as an exemption for the touched `locally_run` kind `omp_session_accessor`. I can cite no higher-priority exemption. `harness-verification-rules` says a touched `locally_run` detect surface with no recorded run under `notes/` is `BLOCKED — locally-run kind 'omp_session_accessor' has no recorded run`.

## Q-1 reconciled (blocking policy conflict)
- `.harness/harness.json` `test_kinds.omp_session_accessor`: status `locally_run`, `detect` = `tests/manual/probe-omp-session-accessor.py`, `cmd` = `tests/manual/probe-omp-session-accessor.py`.
- That detect file is changed by T-01 (PROBE path repointed; the `.ts` probe relocated). Recorded run under `notes/`: none (`notes/` listing checked: no probe-run note).
- User-approved scope (SC-04 static inspection, byte-preserving relocation, no fresh live claim) conflicts with the verification-rules requirement. Both are honoured as written: I do NOT reopen the approved product scope and do NOT invent an exemption. The static evidence stays as evidence, not as a run: moved `probe-session-accessors.ts` blob `e8df5c44b0ef8e3172e5c3055d6b0b6a2b26291d` equals the baseline evidence blob; `PROBE = ROOT / "tests/manual/probe-session-accessors.ts"` resolves.
- Resolution belongs above me: either (a) an operator records a live run of the cmd (needs host/credentials) in `notes/`, or (b) the tier above signs an explicit exemption/rule amendment for byte-preserving relocation of a locally_run probe. See open question Q-1.
- Classification: **evidence/policy qualification, not a shipped-code defect.** Nothing in the code fails.

## Matrix and fail-first (preserved from c0, unaltered)
- Clone: `git clone --no-local --no-hardlinks --revision=<full pin>` into real-.git `/private/tmp/feat71-qa.1XCu9VpK` (since removed); HEAD = pin, `.git` a directory, exactly five survivor folders, `refs/heads/main` = pin, `HARNESS_AGENT_TYPE` unset (G-07). Managed sparse pin deliberately not used (sparse masks the five-corpus owner reads).
- cross_module.always = [unit, integration]; plan change_type valid.
- unit: `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit`, 57 files, `exit=0`, 20.11s. integration: `--kind integration`, 84 files, `exit=0`, 131.63s. 57+84 = 141 = builder receipt `merge-3e6add2a….log`. `--kind all` not rerun.
- fail_first: SC-02 reds (feature_schema id tables, BE-02/10/31/32, discovery `exempt` key, handoff cases g.2/g.3/t14-g) and SC-03 reds (canonical-reader self-test, two floors via R2) as listed in c0, with builder receipts `red-first-S1a/S1b/S2/s3/s4.md`. Natural RED, semantic.
- Grade fix (CR-01) evidence is the builder's plus my suite rerun only; no second reviewer independence applied (O-07).

## Findings dispositions (c0 numbering; severities/kinds of classifiable findings NOT rewritten)
1. kind=form, sev=low — SC-02 `evidence: unit` is partly carried by integration tests. Retained as-is. Evidence qualification (matrix unaffected).
2. kind=substance, sev=low — **claim narrowed, overclaim withdrawn.** c0 said "no red is possible" and called INV-37, `test-check-domain-post.py` and the template `harness.json` half of the baseline assertion "evidence of intent, not discriminating tests". That was too strong. Correct statement: those assertions were green against the baseline, i.e. there was **no pre-change defect to red against**. That does not show they cannot catch a future regression. **No mutation proof was run** for INV-37, the domain assertion or the template half (`test-check-state-handoff.py:343`); I therefore make no claim, either way, about their discrimination. The only measured fact is the builder's converse run reddening the OLD INV-37 file against the new implementation (`red-first-S1b.md`). Residual: discrimination unproven. Evidence qualification, not a code defect.
3. kind=substance, sev=low — `test_an_empty_walk_is_rejected` name over-claims (mismatch check); `test_the_walk_reaches_every_fixture_directory` is the real non-vacuity guard. No mutation proof run on either. Retained as-is.
4. c0 "kind=text-vs-intent" — **withdrawn as a finding.** The token is not in the finding-kind vocabulary (substance|form|proportionality) and was recorded as a classifiable defect. Reason: the observed fact (SC-03 text "without live-corpus reads" vs retained integrity-only live-tree reads in `test-corpus-real-owner`, `test-plan-depends-on` case 9, `canonical_reader_live_*`) is covered by the BRIEF's own wording ("pass on the retained five-folder corpus"), so no actionable defect exists. Kept only as an informational note for the PM/goal-check that reads SC-03 literally. Not an open question: I have no unresolved classification need.
5. kind=proportionality, sev=info — **dismissed, no actionable finding.** `info` is not a legal severity token (none|low|med|high|critical) (G-09). Content: two removed behaviours (kaya under uniform INV-17/INV-37; `--conversion-manifest` removal with no reader at pin by grep) were checked by pin diff and the suites only, no kaya check rerun. This is a statement of scope of my evidence, not a defect; no scenario of harm is shown. Dismissed.

## Evidence durability
- Complete stdout/stderr remain only at `/private/tmp/feat71-qa-unit.log` (7439eef8843f9fb30128a094db2e76c0ccdfaa76b7298b3eac633793560d9a57, 2203 newline-terminated lines by `wc -l`) and `/private/tmp/feat71-qa-integration.log` (9807350f013ce6d0282718687504391f5f9b026b2c249a66d914ccf3133acada, 5836 lines; 130430 and 402119 bytes). c0's "2204/5837 lines" counts one more than `wc -l`; I did not reconcile it (likely trailing line without newline), it is a count discrepancy of 1, not a result change.
- **Durability limitation:** copying them into `notes/` was attempted with `cp` and denied by bash-write-guard (outside my domain), and re-emitting 532 KB through Write would be a retype, not a durable copy. They sit in volatile `/tmp`. The hashes above allow later verification if a copy is kept by someone with the path grant.

## Open questions
- Q-1 (BLOCKING): Record a live `tests/manual/probe-omp-session-accessor.py` run under `notes/`, or have the tier above sign an exemption for byte-preserving relocation of a touched `locally_run` probe. Recommendation: the latter is consistent with the approved SC-04 scope and costs no credentials, but only the lead/user may grant it.
- Q-2 (non-blocking): move the two `/private/tmp` logs into feature `notes/` through a path with write grant, if durable retention is wanted.

## Principles applied
None cited (no craft leaf read).
