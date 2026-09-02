# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: 2026-09-02-16-validator (FAIL), 2026-09-02-17-product (FAIL) — validate phase COMPLETE
- squad: validator, then product
- status: in_review — **not shippable**, one bounded main-session-direct fix outstanding

Station `review`. Validate ran to completion and reached a defensible verdict: **the feature is
nine-tenths done and the missing tenth is a test that was specified, approved, and not written.**

**The blocking result: SC-03 is `unmet`.** `test-suite-independence.py` ships as scanner only —
180 lines, zero case machinery, `tempfile` imported at :9 and never used, which is the fingerprint
of dropped fixtures. `plan.yaml` T-03's signed intent block mandates "ITS OWN RED PROOF, in the
file, so CI keeps proving the guard can fail", enumerating six cases. None was delivered. **The
scanner itself works** — T-03's verify block re-executed finds all ten `ea6f51f` sites, missing 0,
extra 0 — so this is a *test-only* remedy, not a code defect, and it is **approved-but-unmet**:
the signed plan already requires it, so it is a fix cycle and needs no new operator ruling.
Two independent agents reached this separately (`notes/qa-c7.md`,
`notes/review-harness-code-reviewer-c7.md`, `notes/research-FEAT-48-goalcheck-validate.md`), and
I confirmed the absence at source myself.

**The `qa_gate` PASSES** — `matrix_ok: true`, unit 33/33, integration 30/30, both required kinds
satisfied. It had never run against this feature's code before now: the build was
main-session-direct, so no build run exists in `runs:`.

**The review gate is `high`** (`gates.review: advisory_unless_high`), on findings I verified rather
than relayed:
- `run_pool.py --mutation-check` **fails open on symlink-shaped new entries**. My own tempdir probe:
  a dangling symlink plus a symlinked subdirectory appear under the watched directory and the pool
  exits **0** with no `MUTATED` line; the control, an ordinary new file, correctly exits 1 with
  `MUTATED .mutant-x.sh`. T-04's approved intent requires catching a path that "APPEARED, which is
  the vector the static scan and a git-based watched set both miss" — so this too is
  approved-but-unmet, not a beyond-spec nicety. SC-10's three enumerated vectors all pass.
- `code_grade: fail` is the **mechanical** DEC-209 result, not a reviewer opinion:
  `code-grade.py --base d135364e --head 8e7f56dc` → 18 passing, 7 FAIL (5 grade-1). Both flagged
  pre-existing functions (`test-check-domain.py:1432 run_schema`,
  `test-check-fixture-secrets.py:171`) were **modified by this diff**, which is what pulled them
  into the gated set — the feature did not author their complexity but did touch them.
- `test-run-pool.py` omits the `__pycache__`-exclusion leg T-04 requires. `run_pool.py:32` excludes
  it correctly, so this is unpinned behaviour rather than a live defect.
- `snapshot()` records only `(st_size, st_mtime_ns)`, so a size-preserving overwrite with an exact
  `os.utime` restore is invisible. A deliberate forge; its remedy is the same disclosure edit.

**`review_sha` re-pinned `b86ce66a` → `8e7f56dc`, and the review target did not move.**
`check-state.sh` raised INV-33 against the inherited pin: the seam commit rewrote `plan.yaml`
(`status: ready` → `review`) *after* `b86ce66a` was pinned. Measured: `git diff --stat b86ce66a
8e7f56dc -- .claude .github` is **empty** and the whole `plan.yaml` delta is that one status line,
so `8e7f56dc` is a strict superset carrying byte-identical code. INV-6 and INV-33 are now satisfied
together and FEAT-48 carries **zero** `check-state.sh` findings. This also closed the standing
SEC-01 blocker, which bound only while no `review_sha` was pinned.

**Budget, and I got this wrong before a gate corrected me.** `cycles_used` is **8 of 10**. I first
recorded 6, reasoning that no rework had happened *inside* this phase — both leads reported zero
send-backs and I was returning the FAIL upward rather than routing it back. `check-state.sh`
refused: seven FAIL runs are recorded and a FAIL run **is** a rework loop, whoever executes the
remedy. The honest count is the prior 6 plus this phase's two FAIL runs. That leaves **2 cycles of
headroom**, which is the real signal: the SC-03 fix plus its re-validation is roughly the entire
remaining budget, and a second failed attempt exhausts it. 17 runs against an informational
`max_total_runs` of 20 — the count is a floor, since the whole main-session-direct build appears in
it nowhere.

## Open Questions

- **Answered, not escalated.** Both the panel and pm raised SC-03's reading (literal `evidence:
  unit` vs the build-time verify block). It needs no operator ruling: `plan.yaml` T-03's signed text
  mandates the in-file proof "asserted as a case rather than only as the exit code".
- **Needs an operator call.** The symlink fail-open has two remedies: harden `snapshot()`
  (`os.lstat`, record symlinks, decide `followlinks`), or amend D-11/DEC-211 to disclose the
  boundary honestly. The default under approved-but-unmet is to deliver what T-04 approved — harden
  the code — because the alternative edits a signed decision. The `(size, mtime_ns)` forge folds
  into whichever is chosen.
- **Needs an operator call.** Whether `code_grade: fail`'s five grade-1 records are remediated
  inside this feature or split out. Three sit in files the SC-03 fix must edit anyway; two are
  independent decomposition work.
- **Backlog, not a gate.** The suite is not independent of the ambient environment: with
  `HARNESS_AGENT_TYPE` set, `test-plan-merge.py` fails 11 `sign-approval` checks and the whole suite
  exits 1. Out of FEAT-48's stated scope — REQ-01 covers shared-state *mutation*, REQ-07 covers
  *order*, neither covers ambient env — and the file is untouched by the diff. It matters
  operationally: every agent that runs the suite carries that variable.
- **Backlog, not a gate.** `PASS <file>.py` is not a runner-reserved line shape: six test files
  print their own summary and the runner prints another, so 63 files yield 69 file-level lines.
  Pre-existing — `main`'s runner printed `PASS $s` per script identically.
- **Advisory.** SC-07's failing-file clause is established by composition, not by a gate; no test
  drives `run-unit-tests.sh` end-to-end with a deliberately failing file.
- Whether issue #1053 CLOSES on ship remains the operator's call; the Advisor recommended
  close-on-ship. Issue #1053's `## Scope` still reads "Folded into FEAT-47" and only the operator's
  hand fixes an issue body.
- `plan-sign-gate.py` does not read the `panel:` key, so a signature can land on a plan whose last
  panel word is FAIL. Moot here; the guard gap is untracked.
