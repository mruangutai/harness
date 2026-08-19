# STATE

## Current

- feature: FEAT-25-claim-feature-root
- run: .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-19-7-distill2-validator/state.yaml
- squad: validator
- status: ship decision returned to the operator; awaiting acceptance

Phase: ship, at its terminus. Branch `feat/FEAT-25-claim-feature-root`, HEAD `8d7b273`, base
`d1ffd7f`. `review_sha` pinned at `8d7b273`, which contains all the work. Two source commits:
`76d01ce` `[harness:t-01] [harness:t-02]` and `8d7b273` `[harness:t-03]` — the first covers two
tasks because T-02 edits the same two files T-01 does and no honest hunk split exists; the message
says so rather than faking attribution.

**All eight SCs met** (`runs/2026-08-19-5-goalcheck-product/digest.md`), six on pm's own
measurements. **No UAT criteria exist.** Panel PASS, `severity_max: med`, `must_fix: []`, nothing at
`high`, so the advisory review gate does not gate. Simplify applied nothing and left the tree
byte-identical to the commit.

**The blocking qa gate is GREEN at the commit it grades** — measured by me in a clean worktree at
`8d7b273`: `--kind integration` exit 0, all 12 scripts PASS; `--kind unit` exit 0. In the working
tree the same command exits 1 solely because the uncommitted `.harness/harness/docs/DECISIONS.md`
(held dirt, another workstream) disagrees with a fresh decisions-index regeneration. Method and
repro: `notes/gate-measurement-2026-08-19.md`.

The panel's signed R-1 claim of "four sites, two files" is **retracted**: the validator lead
falsified its own claim during distillation and I confirmed by direct read — `test-check-state.py`
keeps `allok = allok and ok` outside the guard and holds zero `fails += 1`. One site, one file
(`test-layout-migration.py:416-418`). The correction is APPENDED to the panel digest; the original
text is untouched.

Close-out done. Ship-refresh SKIPPED with cause: no `INDEX.md` exists anywhere in the repo, so there
is no codebase map to intersect. Distillation ran for all three squads; I applied the write-less
tier's ops myself (three reviewers, two leads) and my own single op. `check-expertise.sh` exits 0
across all 15 files with per-section counts held — no wipe.

Budgets: `cycles_used: 4` of 10, `len(runs): 14` of 20 — both under. The 4th cycle bought nothing: I
re-dispatched a distillation run I judged incomplete and it had in fact completed. Counted anyway.

Briefing: `notes/ship-review-2026-08-19-ship.md` (+ rendered `.html`), 17 backlog rows, B-1 the only
one blocking other work.

Post-briefing: the redundant distillation pass (`2026-08-19-7-distill2-validator`) returned after the
briefing was written. Its ops are reconciled, not applied blind — `harness-code-reviewer`'s two are
DROPPED (both lessons already on disk as G-15/O-05, and its Gotchas is at 15/15 so an add would be a
cap violation), `harness-validator-lead`'s two are APPLIED (distinct, and room existed). Every count
re-grepped rather than trusted; `check-expertise.sh` exits 0 across all 15 files. That pass also
exposed a real hazard, now backlog row B-19: nothing serialises Expertise writes against an open
distillation run, and caps are computed from a spawn-time snapshot. The six graded source files are
byte-identical to `review_sha` — nothing about the ship recommendation, the SCs or the gate moved.

Next: the operator's ship decision. I have opened no PR and merged nothing. On acceptance the main
session runs `gh-sync.py ship` and `gh-sync.py backlog` for the unstruck rows.

## Open Questions

These ids are STATE's own; the run digest each item came from is cited so nothing is renamed
silently.

- S1 (non-blocking, the most consequential; run 2's Q2): #500 alone may not unblock unit 8 (#496).
  `factory_decompose.py:276-283` labels every sub-issue `feature:<id>` and `:360` labels an adopted
  parent the same way, so a decomposed kaya issue always resolves a feature id; under a fixed
  `harness` segment a kaya feature directory at `.harness/kaya-ai/features/` is still unreadable
  and still refused — with a correct message after T-02, but still refused. Operator's choice:
  place kaya's first feature dir under the harness segment, use an unlabelled first proof issue,
  or pull unit 7 forward.
- S2 (downgraded from blocking, with the disproof; run 3's Q1): SC-08's allowlist clause (a) would
  flag `.harness/expertise/*.md` if it were graded after feature-close distillation. The lead
  marked it blocking on that premise. It does not hold: goal-check precedes distillation and
  ship-refresh, so those writes are outside the graded set. The residual is one clarifying sentence
  pinning the grading moment, which the operator may request at signature.
- S3 (non-blocking; run 3's Q3): cut the implementation branch from `d1ffd7f` or later. SC-08's
  three-dot diff takes a merge-base, so a branch cut earlier fails clause (a) on unrelated files.
- S4 (non-blocking, harness defect, not this feature's; run 3's Q4): two directories still share
  the id FEAT-25 (`claim-feature-root`, `expertise-repository-tier`). Mechanically safe — lookups
  use the full slug — but every human "FEAT-25" reference is ambiguous. Nothing allocates ids (#323).
- S5 (non-blocking, deferred by design; run 2 validator's Q1): the two new stderr texts pinned in
  T-02 are the only human-facing artifact this feature produces, and ui-reviewer correctly declined
  them as out-of-lens. Their wording is judged by the post-build panel, nobody earlier.
