# T-05 amended for operator ruling R-4 — BUG-1309-mirror-build-entry — 2026-09-08

**The signed plan now SPECIFIES all four ruled clauses, and T-05's `verify:` GATES them.** Two of
the four (fail-closed on an unresolvable ref; the merge control operations) appeared nowhere in the
plan text before this edit, so the operator's DEC-174 implementation round had nothing to build
against. It does now. **One thing the operator must still decide: R-4 clause 3 traces to NO success
criterion, and SC-04 as written is not merely silent about it — it is contrary.** See the last
section.

`plan.yaml` was written only through `plan-merge.py`. `approval:` is byte-identical (the plan's first
changed line is 263; `approval:` is lines 3-24) and its 2026-09-08 signature is now stale over
amended text — expected, and the main session's `sign-approval` to repair before ship.

## Exactly what changed

| field | change |
|---|---|
| `tasks[T-05].intent` | step 2's class clause REPLACED: the class rule now binds BOTH positions (git globals before the subcommand, `git merge`'s own options after it) in BOTH spellings, names the three measured escapes as evidence, and states the implementation freedom explicitly — behaviour pinned, mechanism free |
| `tasks[T-05].intent` | step 2, NEW clause `MERGE CONTROL OPERATIONS ARE NOT MERGES, AND THEY ALLOW` — `--abort`/`--continue`/`--quit` exit 0 with no permissionDecision on an owing branch, decided BEFORE the fail-closed fallback, with VF-03 named as the `e374c9a2` regression |
| `tasks[T-05].intent` | step 2, NEW clause `FAIL CLOSED WHEN THE MERGE IS IDENTIFIED AND ITS REF IS NOT` — local-branch fallback, receipt rule decides; restates the `894adc0f`/`473d82cb` attribution bound verbatim from step 4 so a doer cannot read it as licence to deny on a malformed RECORD |
| `tasks[T-05].intent` | NEW clause `THE GRADE BAR` before the registration section — grade 4 or better, the pin's measurement (CYC 8, COG 15, ABC 16.1, GRADE 3, BAR 4, FAIL), remedy is decomposition, `main` explicitly pre-existing and out |
| `tasks[T-05].intent` | seven case names appended to the enumerated contract, plus the fixture rule (all seven on `FEAT-9001-fixture-non-era` owing a receipt, `github.repo` pinned to `acme/widgets`) and the R-4 discrimination requirement (each RED against `e374c9a2` first) |
| `tasks[T-05].verify` | `for n in …` extended 19 → **26** names; grade assertion appended immediately before `echo VERIFY-PASS`, transcribed, qualname set `git_merge, words, direct_merge, gh_merge` — `main` deliberately absent or the verify is permanently unpassable |
| `decisions` | **D-16** (class in both positions + fail closed + control-operation exemption; R-4 clauses 1-3), **D-17** (grade-4 bar in T-05's own verify, `main` excluded; R-4 clause 4). Both `dec: DEC-174` |

Untouched and proven so: every other task, `approval:`, `panel:`, `lanes:`, every code and test file.
`check-plan-routes.py` on this plan: **0 violations, exit 0** (the six `DEVIATION` lines are the
expected DEC-174 carve-out output). `feature.json`'s `cycles_used 15 / max_total_cycles 16` in the
worktree diff is the orchestrator's R-5 write, not this dispatch's.

## SC-04 traceability — a RECOMMENDATION; `BRIEF.md` was not edited

**Clauses 1 and 2 are INSIDE SC-04.** `git merge -F <file> <ref>`, `--cleanup <mode>`,
`--attr-source` and a ref-less `git merge` are each "a merge command issued for a feature … whose
Build-entry outcome … is absent under enabled sync" (BRIEF.md:108-110). They need no brief change;
they are the already-recorded unmet clause (a).

**Clause 3 is a NEW criterion, and it is worse than uncovered.** Read `git merge --abort` as a merge
command and SC-04's first clause MANDATES A DENY — precisely the behaviour R-4 reverses; read it
narrowly and SC-04 is silent. Under either reading the shipped allow is not graded by any criterion,
and under the literal one it CONTRADICTS a signed one. This cannot be fixed by wording it away.

**What the operator would have to sign** — one of these two, both `BRIEF.md` edits, both resetting
the brief's approval:

- *Recommended* — a new criterion, provenance stays clean and SC-04's already-graded text is not
  reopened mid-flight:
  `SC-11: git merge --abort, --continue and --quit, issued on a branch whose feature owes a
  Build-entry receipt (github.build_entry absent or recovery-required, not era-exempt), each exit 0
  with NO permissionDecision object on stdout. Each assertion is DISCRIMINATING at review_sha:
  against the pre-change copy recovered with git show
  e374c9a2:.claude/skills/harness/bin/merge-gate.py, each case FAILS.
  verify: automated  evidence: integration`
- *Or* — an exclusion sentence inside SC-04 saying merge control operations are not merge commands
  for its purposes. Cheaper, but it edits a criterion three cycles of digests already grade.

**Clause 4 is NOT a success criterion and should not become one.** A code-grade bar is a quality
gate, not an outcome the feature delivers; it traces to no REQ and needs none. It is gated where it
belongs — T-05's own `verify:` — and recorded as D-17. If the operator wants it visible at
signature, `## Constraints` is its home. Consequence of leaving it out of the SCs: the goal-check
will never report the grade; only T-05's verify and the panel's code-grade reader will.

**If the operator declines both options for clause 3**, the honest record is a DISCLOSED
VERIFICATION GAP: three integration cases and T-05's verify gate the behaviour, no criterion claims
it, and the goal-check reports it under none.

## Open, for the next context

- T-05's enumerated case-name contract lists **21** names while `verify:` gates **26**. The five
  missing (`duplicate valid records …`, `single owner plus unrelated malformed record …`, and the
  three `git -C`/`-c`/`--work-tree` globals) predate this dispatch: they entered `verify:` with the
  D-13/D-14 amendments and were never appended to the enumeration. Harmless today — those five cases
  already exist and pass — but the list is no longer the contract it claims to be.
