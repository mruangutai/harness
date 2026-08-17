# STATE

## Current

- feature: FEAT-22-docs-layout-migration
- run: close-out complete — 23 runs recorded, last is `2026-08-16-15-distill-*`
- squad: none
- status: **Review — every gate passed, briefing written, awaiting the operator's acceptance**

**12 of 12 SCs met at `b479afd`.** qa PASS (blocking) · panel PASS (advisory, `must_fix: []`) ·
goal-check FAIL → re-grade PASS on all seven stale criteria. No eleventh cycle fired.

**Briefing:** `notes/ship-review-2026-08-16.md` (+ rendered `.html` sibling, never hand-authored).
It is the artifact addressed to the operator: 24 backlog rows with IDs, all recorded deviations,
and my own errors.

**Seven commits, `0f12f14..1f4124e`. Nothing pushed. Zero tracked dirt** — the only remaining
working-tree entries are the held untracked FEAT-20/FEAT-21 review notes.
`e6e74c8` cluster · `1246b06` logs · `5faa832` boundary record · `0140dce` simplify ·
`e26e628` SHA line · `b479afd` the SC-10 fix · `1f4124e` the distillation (10 Expertise files).
Expertise is committed on the branch by precedent: FEAT-20, FEAT-21 and this feature's own cluster
all carried it, and two commits exist in this repo purely to recover lessons lost before a branch
was deleted.

**`review_sha` = `b479afd`.** Re-pinned after every commit; no validator ran on a stale tree.

**Close-out, verified rather than relayed.** Ship-refresh **SKIPPED** — measured: `.harness/codebase/`
does not exist. Distillation ran for all three squads; a spend limit killed two lead sessions, so
`distill-product` has a verdict-less digest and `distill-validator` has none. Both are recorded
**`INCOMPLETE`**, never as passes. **The work itself is durable and I checked it three ways:** no
wipe (all ten files GAINED entries, +25 net), no double-application (zero duplicate entry IDs across
all thirteen), and `check-expertise.sh` exits 0. **I deliberately did not re-dispatch** — the members
had already self-applied, so a re-dispatch risks double-applying entries into files injected into
every future spawn. A gap in the archive beats a permanent tax on every agent.

**Budget: cycles 10 of 10, fully consumed.** The last one bought the SC-10 fix, which closed four
findings in a single commit; the re-grade was its back half and did not increment.
**Runs 23 against an informational 20 — INV-22 now fires.** My read: they earned their place. Four
failures, each resolved by the run after it; a plan that converged over ten revisions before a line
was built; and all four final gates found something real.

**Two crash resumes this session** (API rate limit, then a spend limit). Both times the relay that
woke me carried stale state — once describing three already-run gates as still owed, and once the
cycle count. Disk won both times. That is the resume protocol working.

**My own errors, all in the briefing rather than smoothed away:** I asserted all 11 tasks were
`change_type: docs` (7/3/1 — the validation lead caught it); I cleared the simplify commit on
behaviour alone without checking whether a signed verify greps the words it changed (the panel found
one that did); and I found a **failed run recorded as passed**, reconciled all 17 runs against their
digests, corrected the single mismatch, and did **not** retro-adjust `cycles_used` because its basis
is unreconstructable — so the count may understate.

**No handoff note is owed:** `check-state.sh` INV-17 exempts this feature — every task is
`execution_mode: main-session-direct` under D-03, so no squad ran a build seam.

**Next, and it is the operator's:** accept and ship, or send back. On acceptance the main session
runs `gh-sync.py ship` and turns the unstruck backlog rows into issues.

## Open Questions

- Q1 — `plan.yaml:927` invokes `check-expertise.sh` with no argument; its usage gate exits 2 on empty
  argv, so that clause cannot pass on any tree (measured both ways). Signed text — **operator's
  call**. Does not gate shipping; T-07 was accepted on the intended invocation. Briefing row B-13.
- Q2 — DEC-189 amendment 1 states the control-plane list "is advertised in deny messages". Measured
  false: the constant appears twice in `harness_boundary.py` (membership test `:231`, filter `:345`)
  and is never printed. The amendment copied the wording verbatim from a code comment that the
  simplify pass has since corrected, leaving the signed text as the sole carrier. Signed text —
  **operator's call**. Briefing row B-14.
- Q3 — the panel's union finding: the docs grant is correct today and pinned by nothing. A witness
  needs BOTH a repointable root AND an exhaustive assertion, so fixing the hardcoded root alone
  would not close it. Recommended remedy is the witness test, not narrowing the grant. Row B-12.
- Q4 — the seven accepted residuals in `notes/rotation-carry-2026-08-16.md` stand. **Do not
  re-litigate.** `harness_boundary.py:223-224`'s "two of the four" left the blocking list by ruling,
  not by remedy — stated plainly in the briefing so the record is not flattering.
- Q5 — the harness defects are enumerated as briefing rows B-3, B-6, B-7, B-8, B-9, B-10, B-11,
  B-15, B-16, B-17, B-18, B-19. Two were hit by me live this session: the write-guard's
  redirect misparse, twice; and the playbook's stale "write-less reviewers" distillation clause,
  which I measured before dispatching and which would otherwise have stranded every reviewer's ops.
