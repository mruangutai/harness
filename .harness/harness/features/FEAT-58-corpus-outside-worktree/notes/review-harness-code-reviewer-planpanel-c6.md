# Plan-panel review (scope / harness-code-reviewer) — cycle 6 — FEAT-58-corpus-outside-worktree

**VERDICT: PASS, with 3 non-blocking findings (2 med, 1 high).** No `must_fix`. The severity_max
of `high` is a single finding about the new N-13 surface's own rigor, not about incorrect
behaviour it delivers — see finding 2. Three prior operator review passes and five amendment
rounds show; the plan is in materially sound shape. `code_grade: n_a` (no committed code in this
range; `reviewed: plan:.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml`).

## Reviewed as plan-phase (DEC-207)

`plan.yaml` + `BRIEF.md` graded as the specification. `approval.status: pending`, no `review_sha`.
Read in full: `plan.yaml` (2915 lines), `BRIEF.md` (410 lines), the DoD note's amended `:136-153`,
`answers-operator-c6.md`, `answers-operator-c3.md`/`c5.md` (via plan.yaml's D-06/D-14 quotes),
`notes/research-FEAT-58-apply-c6.md`, `notes/research-FEAT-58-apply-batch-c3.md`,
`notes/research-FEAT-58-apply-c5.md`. Source-verified at the checkout: `branch-create-gate.sh`
(deny/allow exit-0 pair), `merge-gate.py` (`sys.exit` count = 0), `bash-write-guard.sh:855`
(`wrong_checkout`), `check-state.sh` (header `:24` canonical-gate claim, `H=`/`_feat_dirs`/preflight
refusal region).

## The nine probes, each with an explicit verdict

**1. PL-01..PL-04 disposition — all four CLEAN.**
- **PL-04/Q4 (the class):** N-13 satisfies all three operator constraints. (i) read-only —
  "nothing mutates the owner root's working tree, its index or its records, and nothing touches a
  LIVE worktree" (N-13 intent, verbatim); PART 1 never writes; PART 2 only touches a probe it
  creates. (ii) dirty case is a disposable probe (`git worktree add --detach <probe>`), never a
  live tree. (iii) fixture keeps every assertion — D-11 states "EXTENDED, NEVER REPLACED... ADDITION,
  NEVER SUBSTITUTION." Cost rule intact — N-13 never `git init`s a copy; it reads the real owner
  root via `feature_corpus.corpus_root` and runs the shipped `check-state.sh` there.
- **PL-01/Q1:** confirmed remedy (a) taken — "ONE DERIVATION, USED TWICE" from `git ls-files` over
  `.harness/*/features/`. No feature.json-carrying restriction anywhere; N-06 PART 1 says so
  explicitly ("Add NO suppression, no allow-list, no exemption and no feature.json-carrying filter
  anywhere"), and N-13 repeats the non-suppression for the ten record-less directories.
- **PL-02/Q2:** D-12 and N-06 PART 3 verbatim-match the operator's amended `SC-09` (`BRIEF.md:239-252`,
  read at source): gate on structural exits 3–7 only, exit 8 reported and non-gating, `--verify`
  still reports (never repairs) the dirty tree, N-02 check 5 unchanged.
- **PL-03/Q3:** N-10 PART 7(c) reworded to assert absence of a `permissionDecision: deny` payload
  and explicitly "NEVER ASSERT AN EXIT STATUS AS THE GATE'S DECISION"; D-17 records the payload-not-
  exit convention, cross-checked against `branch-create-gate.sh` and `merge-gate.py` at source
  (both confirmed: `deny()` prints then `exit 0`; `merge-gate.py` has zero `sys.exit` calls).

**2. The new surface (N-13, D-16, D-17, SC-16, GC6 fixes) — mostly clean, one real gap (finding 2).**
- N-13 distinguishes a real audit defect from a benign transient: PART 1 clause 4 requires the
  failure message to print the missing/unexpected NAMES. No standing-red risk — N-13 pins no
  census figure ("no census figure — not 89, not 79 — is a passing condition anywhere").
- GC6-01 deadlock fix: N-06 PART 1's asymmetry confirmed verbatim — "GATE ON THE MISSING SIDE
  ALWAYS; GATE ON THE UNEXPECTED SIDE ONLY INSIDE A LINKED WORKTREE"; SC-06 mirrors it exactly. No
  third site in this plan performs the same expected-vs-reached gating (N-10's four read sites are
  shape (c)+(b) only — refuse-on-unresolvable, never a set-mismatch gate).
- GC6-02 non-emptiness clause: exists in prose ("If the derivation returns zero names, the audit
  REFUSES... naming the pathspec") but **no named test case in N-06 PART 4 exercises it** — see
  finding 1.

**3. Three weight-bearing proofs can still report RED — CONFIRMED for all three.** (a) N-04 PART 2
step 4 keeps "THE PRE-CHANGE REPRODUCTION... assert the two runs DIFFER" in the collected file. (b)
`test-check-state-equivalence.py` step 4 perturbs X's record and asserts the sets go UNEQUAL. (c)
`test-worktree-state-norepair.py`'s "RED PROOF... temporarily route one break's `--verify` through
the `--repair` code path... reddens for that case."

**4. Two-route D-2 denial — UNDISTURBED.** N-03 part (c) still requires both the Write/Edit route
(`check-domain.sh`) and the Bash route (`bash-write-guard.sh:855`, confirmed at source), each with
its own paired positive control. D-14's text states this explicitly survives the hardlink strike.

**5. Positive controls / fourth blind instance — ONE FOUND, it is finding 2.** `.agents`/`.claude`
and `.harness/corpus` are asserted per-path via `islink`+`realpath`, never exit status (N-05 GROUP
2, confirmed); the include list has its own DERIVED discrimination (N-05 GROUP 3, deletes the
literal-list stand-in and reddens). The fourth instance the probe asks to hunt for is real: **N-13
PART 1's own four assertions carry no red-proof/discrimination requirement**, unlike every other
consequential assertion in this plan (N-01, N-02, N-04, N-05 ×3, N-07 case (c), N-08 clauses 2–4,
N-09, N-12 HALF 2). See finding 2.

**6. Seven binding items — CLEAN.** BRIEF's coverage table (and `apply-c6.md`'s re-stated copy)
maps D-1..D-5, M-1, M-2 each to its own REQ and at least one SC; none merged, none deferred. Read
the REQ text directly (not the table): REQ-01..REQ-10 each traced by at least one task; all
`verify: automated` (I re-read all fifteen SC blocks in `BRIEF.md` — none says `inspection`).

**7. Shape rule — CLEAN**, with one adjacent gap folded into finding 3. Every `change_type` with
zero production `files:` is `scaffolding` (N-01, N-05, N-08, N-09, N-12, N-13) — the VL-05/VL-06
shape is not repeated elsewhere. N-13 is coherent: one test file discharging SC-16's compound
(owner-root clean + dirty-worktree non-gating) criterion, not a leftover bag.

**8. Coverage — CROSS-VALIDATED by a different method than the goal-check (which reads the plan's
own ledger claim).** I independently read the three historical apply notes rather than trusting
`apply-c6.md`'s arithmetic alone: `apply-batch-c3.md` records 36→42 (cycle 3, three evidence-form
changes named); `apply-c5.md` records 42→41 with one named removal (`hardlink deny + positive
control (N-11)`); `apply-c6.md` records 41→45 (four rows added, none removed, one row's evidence
form changed: N-10 PART 7(c)). The chain is arithmetically and narratively consistent across three
independently-written notes. Spot-checked all four new rows against N-13/N-06 PART 3 text directly
— each exists as described. Demotions (N-06 PART 3 case (c), N-09 PART 1 clause (b)) remain named,
not silently dropped, per D-13's text and `apply-batch-c3.md`'s named-demotion table.

**9. Executability — CLEAN**, with one drafting inconsistency (finding 3). `depends_on` graph is
acyclic with a valid topological order (`N-01, N-02, N-10, N-03, N-04, N-07, N-05, N-06, N-08,
N-12, N-13, N-09` satisfies every edge). Every `verify:` block names files the same task creates,
except N-04's `test-post-merge-sweep.py`, which the intent explicitly documents as a pre-existing
FEAT-34 file being re-run, not created — legitimate. No live task, trace, or `depends_on` edge
references retired N-11 or struck SC-15; every occurrence is inside a historical/mapping sentence
(`grep` over the whole file confirms this).

## Findings

1. **severity: med** — `lands_on: N-06 PART 1, SC-06`. The non-emptiness floor ("the derivation
   must yield a non-empty set... if it returns zero names, the audit REFUSES, naming the pathspec")
   is specified in N-06 PART 1's prose but no case in `test-check-state-expected-dirs.py` or
   `test-check-state-scope.py` (the two files PART 4 enumerates) exercises it — both files' listed
   cases cover the mismatch-message and one-derivation-property, never an empty-derivation input.
   **Why it matters:** a future re-spelling of the `git ls-files` pathspec that silently matches
   nothing (exactly the `.harness/*/features` vs `.harness/*/features/*` bug this cycle already
   found once) would pass N-06's own test suite even though the audit's expected set would then be
   empty and every downstream comparison vacuous — the fail-open GC6-02 exists to close.
   **Change asked:** add a named case to `test-check-state-expected-dirs.py` feeding a canned
   zero-match derivation and asserting refusal naming the pathspec, before N-06 is signed off as
   discharged.

2. **severity: high** — `lands_on: N-13, SC-16, D-16`. N-13 PART 1's four real-owner-root
   assertions (no-mismatch-refusal, past-the-choke-point, non-vacuity floor >70, diagnostic
   message) carry no RED PROOF / DISCRIMINATION instruction proving the test can actually go red —
   every other consequential assertion in this plan does (N-01 self-check exclusions, N-02
   norepair, N-04 merge/rebase pre-change reproduction, N-05's three separate discrimination
   proofs, N-07 case (c)'s pinned pre-change reproduction, N-08 clauses 2–4, N-09's discrimination
   clauses, N-12's HALF 2 red-capability proof). PART 2 of the same task already has this property
   internally (clause 3 report-only paired against clause 4's structural refuse), so the gap is
   specific to PART 1.
   **Why it matters:** this is exactly the defect class the whole cycle-6 engagement exists to
   close — "a control found blind to the thing it existed to catch" — and N-13 is the panel's own
   named remedy for it (D-16/PL-04). Without a demonstrated red state, an implementation that
   mis-parses `check-state.sh`'s stderr (matches the wrong marker, or a pattern that is vacuously
   satisfied) would pass clause 1 while never having exercised the claim it makes, and nothing in
   this task or its `verify:` block would catch that before signature. This would be the fourth
   instance of the exact pattern PL-04 was raised to stop.
   **Change asked:** add an explicit red-proof step to N-13 PART 1 — e.g. run the same four
   assertions once against a copy of `check-state.sh` predating N-06 PART 1's fix (or against the
   real owner root with the pre-fix `feature.json`-keyed derivation reinstated in a temp copy), and
   record in the receipt that clause 1 reddens naming the 89-vs-79 mismatch, then revert — matching
   the discipline required everywhere else in this plan.

3. **severity: med** — `lands_on: N-13 PART 1`. PART 1 instructs resolving `HARNESS_REVIEW_SHA`
   ("DEFAULTING TO HEAD when unset, exactly as N-08 does") for `check-state.sh`, but
   `check-state.sh` has no such mechanism at all (`grep HARNESS_REVIEW_SHA` over the file: zero
   matches) — it is a pure filesystem scan of whatever is actually checked out at `cwd`, unlike
   N-08, which reads records purely via `git show <ref>:<path>` and never runs a script against a
   live checkout. **Why it matters:** taken literally, honoring "reading records at the reviewed
   commit" for a live subprocess would require checking the owner root out to that ref — which
   directly contradicts the same task's absolute rule two paragraphs later ("nothing mutates the
   owner root's working tree, its index or its records"). Taken loosely, the `HARNESS_REVIEW_SHA`
   framing is dead prose and the test silently audits whatever happens to be on disk regardless of
   the env var, which is a materially weaker claim than "at the reviewed commit" advertises.
   **Change asked:** either drop the `HARNESS_REVIEW_SHA` framing from PART 1 and state plainly that
   the audit runs against whatever is checked out at the owner root when the test executes, or add
   an explicit precondition that fails/skips loudly (in the same announced-skip style as PART 2)
   when the owner root's checked-out `HEAD` does not equal the resolved ref.

## Not re-reported (checked, confirmed already discharged)

GC5-01/02/03, VL-01..VL-09 all show `disposition: resolved` verified per-clause at source per
`plan.yaml`'s own transcription; I did not re-litigate any of them, only cross-checked PL-01..PL-04
per the dispatch's explicit requirement.
