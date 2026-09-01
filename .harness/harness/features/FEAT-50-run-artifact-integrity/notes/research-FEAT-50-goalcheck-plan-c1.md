# Goal-check — FEAT-50 amended plan vs the operator's stated intent (cycle 1)

**Does this plan, as amended, deliver the operator's stated intent?**

**Yes. All four rulings are carried without weakening, all six constraints hold, and the scope is
exactly the four authorized defects. One gap was found and closed in this run: SC-11's second
clause was RED for five reasons that a signer could not see from the criterion. It is REACHABLE,
and SC-11 now says by what act each of the five rows clears.** Graded against
`notes/answers-2026-08-31-plan.md` (the whole file, including the four `## Operator ruling`
sections), on the WORKING TREE at `5d12e68`. One file edited: `BRIEF.md`, SC-11 only.

## 1 — The mission

`delivered`. No production-implementation task exists: all 12 tasks are `status: pending` and the
only changed files in the worktree are `BRIEF.md`, `plan.yaml`, `feature.json`, the answers note,
the observations log and this cycle's notes (`git status --porcelain`). Nothing under
`.claude/skills/harness/bin/` is touched. `approval.status: pending`, `approved_by`/`date` still
placeholders, `approval.rulings` ABSENT (asserted through `harness_yaml.load_plan`).

Nothing is planned outside the four defects. T-06 (playbook), T-07 (decision record) and T-08
(the `worktree_for_feature` seam) each serve a named REQ; T-08 is the operator's own routing-table
shape (`answers-2026-08-31-plan.md:95`), already adjudicated in-scope at c0.

## 2 — The six constraints

| # | Constraint | Verdict | Evidence |
|---|---|---|---|
| 1 | FEAT-50; FEAT-46 never created or referenced | `delivered` | zero `FEAT-46` in `BRIEF.md`, `plan.yaml`, `feature.json`, `STATE.md` |
| 2 | No regression to FEAT-45's two fixes | `delivered` | REQ-05; SC-08 (INV-32 `case_inv32`, exit-status graded), SC-09 (zero-collection), SC-10 (both suites, `^FAIL ` counted separately from rc, floors 1463/1945 at `75daa3b`) |
| 3 | Deterministic regression for ALL FOUR issues | `delivered` | #1056 → T-02 `empty-red`/SC-02 · #1057 → T-05 `feature-checkout-red`/SC-04 AND T-10 `bash-feature-checkout-red`/SC-19 · #1058 → T-05 `digest-clobber-red`/SC-06 · 4th → T-12 `dec156-worktree-red`/SC-21. Every mutant name is unique-per-process (D-07, c0 F-05 applied) |
| 4 | Three canonical commands exit 0 | `delivered as a criterion, externally blocked as an outcome` | SC-10 pins the two suites; SC-11 requires `check-state.sh` exit 0 verbatim — form (c) refused as a weakening, per the ruling. See §3 and §5 |
| 5 | Scope bounded, no unrelated docs/enforcement change | `delivered` | 12 tasks, 9 REQs, all traced; `check-state.sh` is in NO task's `files:` (asserted programmatically); T-07 APPENDS one entry and regenerates a generated index |
| 6 | Stop conditions respected | `delivered` | no destructive/history change, no backfill of any signed plan, no scope outside the four defects. c0's F-01 (`rulings: []` written into `approval:`) is corrected — the key is now absent |

## 3 — The four rulings

**INV-32 `choice: d` — `carried, unweakened`.** SC-11 requires exit 0 (`test "$rc" -eq 0`), which
is stated-intent constraint 4 as written; the FEAT-50 clause is kept ALONGSIDE it, not instead of
it. No INV-32 work is planned: no task's `files:` names `check-state.sh`, the lane row is
declared-but-unedited with that reason written in it, and D-08/D-09 record the ruling rather than
a deferral. The external blocker is stated where a SIGNER sees it — `BRIEF.md`
`## The INV-32 ruling, and the external blocker it creates`, plus the first `## Verification gaps`
bullet and SC-11 itself — not only in a note.

**Both `high` findings — `fixed, not overruled`.** `approval.rulings` is absent and stays absent;
`BRIEF.md` explains why writing it would make the signature itself falsify SC-11
(`check-state.sh:189-204`). Each finding's CONSEQUENCE is closed, not merely mentioned:

- `PF-3d9ac1d0…` (Bash governed-write route) → REQ-08 · D-10 (one seam, both surfaces, plus the
  scope fence that REQ-04 is NOT extended) · T-09 narrows the allow-continue at
  `bash-write-guard.sh:747`, names the loop's ROOT-relative `rel` at `:706` and fences the
  `rel.startswith("..")` continue at `:744` as out of scope · T-10's five cases including the
  short-form clause and `bash-feature-checkout-red` · SC-18/SC-19 · two `lanes:` rows.
  Binding, regression and reachability proof are all present and distinct.
- `PF-964d6356…` (obsolete exit-0 expectation) → T-02 step 5 names the exact description string at
  `test-validate-digest.py:738-739`, rules for DELETION over rewrite and says why; T-02's `verify:`
  adds `grep -cF … -eq 0` with the two existing `-q` greps as its positive control; SC-17 grades
  the removal at `<review_sha>` so the instruction alone is not the evidence. It is reconciled in
  the task that owns the file.

**The fourth defect — `planned to the same standard`.** REQ-09 · D-11 (with the explicit
route-specificity argument that D-03's `harness_feature` ban does not reach the SubagentStop hook,
which already consumes the key at `:1514`/`:1598-1599`) · T-11 (fix, `depends_on: [T-08]` for a
real reason) · T-12 (four cases, including why `_dec156_case` at `:750-769` cannot see the defect)
· red-proof `dec156-worktree-red` · SC-20/SC-21. Its provenance is recorded beside `source_issues:`
because it carries no issue number. No lane row was needed — `validate-digest.py` and its test
already had one.

**Q4 (INV-6 vs a plan-phase validator run) — `genuinely absent`.** Read both documents end to end.
The only occurrence of `Q4` or `INV-6` in either file is `BRIEF.md:106`, inside `## Constraints`,
declaring it out of scope. No REQ, no SC, no task, no decision addresses it.

## 4 — Traceability

`harness_yaml.load_plan` over the working tree: 12 tasks (T-01…T-12), 11 decisions (D-01…D-11),
14 lane rows. Every task's `traces:` resolves to a real `REQ-NN`; the union is exactly REQ-01…09,
so no REQ is untraced and no trace is phantom. Every `files:` entry across all 12 tasks has a
`lanes:` row (checked programmatically — empty set). `depends_on` is acyclic: T-01, T-08 are
roots; T-07 is the sink depending on the other eleven.

`check-plan-routes.py <plan>` → exit 0, `0 violation(s) across 1 plan(s)`, 9 DEVIATION lines, all
DEC-174 carve-outs. Re-run after this cycle's edit (which touched only `BRIEF.md`), together with
`load_plan`: `approval.status: pending`, `rulings` absent, `panel:` byte-unchanged (`plan.yaml` is
not among the files this run modified).

## 5 — SC-11's FEAT-50 clause: ADJUDICATED **REACHABLE** — and now amended to say so

Measured myself in this worktree: `check-state.sh` exits 1, 37 VIOLATION rows, five naming
FEAT-50. The criterion said nothing about them. Each clears by a named act:

1. `BRIEF.md is NOT approved` — the operator's signature (already gated by D-09).
2. `a validator run exists but review_sha is not pinned` — the review segment pinning
   `feature.json review_sha`.
3–5. `runs/2026-08-31-{1-validator,2-validator,1-product}/digest.md` — each a real lead digest
   with intact prose and **no fenced `VERDICT:`/`DIGEST:` block**; `validate-digest.py lead`
   returns `BLOCKED (contract violation)` on all three (run and read, not inferred). Cleared by
   the AUTHORING lead re-emitting its own digest with the contract block — completing the record,
   not rewriting it. A third party editing another agent's digest would falsify it (rule 15) and
   is forbidden. They also cannot reach the default branch: `.gitignore:7` excludes
   `.harness/*/features/*/runs/**`, so no run artifact is ever committed and the worktree holding
   these three is removed post-merge.

Note what rows 3–5 ARE: the fourth defect's own footprint. The SubagentStop hook that should have
refused those three returns was inert for exactly the reason T-11 fixes.

**Edit made — `BRIEF.md` SC-11 only, inserted after the existing "NOT REACHABLE" paragraph.** It
enumerates the five rows and their clearing acts, and states that the criterion is graded from the
repository root of the checkout the feature LANDS in — which is what makes rows 3–5 absent by
construction there and present here until their authors re-emit. Neither graded clause changed:
`test "$rc" -eq 0` and `! … grep -qE '^  VIOLATION .*FEAT-50'` are byte-identical, so the
operator's restored exit-0 clause is untouched. Nothing was weakened; disclosure was added.

## Open question, with a recommendation

- **Q1 (non-blocking).** Rows 3–5 have no named OWNER anywhere actionable. Recommendation: before
  the review segment pins `review_sha`, the orchestrator dispatches each of the three authoring
  leads to re-emit its own `digest.md` with the fenced contract block, prose unchanged. If those
  contexts are gone, record the three as an accepted, gitignored, pre-fix residual in `STATE.md` —
  do NOT have a third party rewrite them.

## Advisory, not gating

- `panel:` is stale by construction (both `high` findings were reworded, so their content-hash ids
  no longer apply) and its two `high` entries still read `disposition: open` with no `resolved_by`.
  `harness-spec-driven` wants `resolved` + `resolved_by: T-NN`; that is the re-transcription
  dispatch's job, not this one's, and editing `panel:` was forbidden here.
- File-level ordering is pinned for `check-domain.sh` (T-04 `depends_on: [T-03]`) but not for the
  two other shared files: T-01/T-11 both edit `validate-digest.py`, and T-02/T-12 both edit
  `test-validate-digest.py`, with no edge between the pairs. Harmless in a serial main-session
  lane and no verify breaks in either order — recorded so a later reader does not read the
  asymmetry as an oversight.
