# Applying the operator's shape correction — FEAT-58, cycle 0 re-plan, 2026-09-10

**Applied in full. 19 tasks → 9 (N-01…N-09); 22 criteria → 12 (SC-01…SC-12); nine decisions
re-authored, two untouched. No ledger assertion lost — every row has a named landing place below.
One decision, D-06, stays open for the operator's pick at signature.** Nothing is signed;
`approval.status` and BRIEF `## Approval` are `pending`, `status: plan`, `panel.last_run: none`.

## What merged into what

| New | Surface it owns | From |
|---|---|---|
| N-01 | synthetic fixture + pre-change baseline | T-02, T-01 |
| N-02 | `worktree-state.py`, all M-1 (DoD) proofs | T-03, T-04 |
| N-03 | `.gitignore` + corpus read and refusal | T-07 |
| N-04 | three shims + merge, rebase, integrity | T-12, T-14, T-15, T-16 |
| N-05 | creation surface, both routes | T-05, T-06, T-13 |
| N-06 | `check-state.sh` + `check-domain.sh` + audit scope and equivalence | T-08, T-18 |
| N-07 | `feature-index.py` + `merge-gate.py` | T-09, T-10 |
| N-08 | live FEAT-02 / FEAT-03 correction | T-11 |
| N-09 | non-regression closeout | T-19, T-20 |

Tasks merged; **test files did not.** The three weight-bearing proofs keep their own files inside
their merged tasks — `test-check-state-equivalence.py` (N-06), `test-worktree-state-norepair.py`
(N-02), `test-merge-skipbits.py` (N-04) — so a chained red stays attributable by filename.

## Ledger row → landing place

`A-01` N-01 self-check · `A-02` N-05 grp 1 · `A-03` N-05 grp 2 (`REQUIRED_PATHS`, both `.agents`
and `.claude` spellings, delete-one red proof) · `A-04` N-05 grp 3 · `A-05` N-03 (a) · `A-06` N-03
(b) + the `.gitignore` grep in verify · `A-07` N-03 (c) + positive control · `A-08` N-06
`test-check-state-equivalence.py`, exit status excluded · `A-09` N-06 scope case 1 + instrument
positive control · `A-10` N-06 scope case 2 · `A-11` N-07 unit cases 1–3 + mixed · `A-12` N-07
integration (a)(b) · `A-13` N-08 real-data · `A-14` N-09 part 1 (a)–(d) · `A-15` **split**: record
N-01 part 2, compare N-09 part 3 clause 2 · `A-16` N-02 six cases · `A-17` N-02
`test-worktree-state-norepair.py`, manifest comparison · `A-18` N-02 idempotence · `A-19` N-04
`test-merge-skipbits.py`, pre-change reproduction, 3337/3807 as the operator's host measurement and
never a fixture expectation, BLOCKED rather than weakened · `A-20` N-05 grp 1b · `A-21` N-04
`test-rebase-state.py` · `A-22` N-04 unit + integration (a) · `A-23` N-09 part 3 clause 3 ·
`X-1`/`X-2` N-01 self-check as **assertions**, re-run from N-09's verify once every test file
exists.

Finding-derived: `F-01` N-02 per-case remedy · `F-02` N-02 no repair-completed verb · `F-03` N-02
announce-per-repair · `F-06` N-02 + N-06 remedy tail, shim tier exempt · `F-04`/`C-03` N-04 shim
rule 5 and case (b), D-03 re-authored · `VL-01` N-02 dirty-tree asymmetry (`--verify` 8, `--repair`
0) + N-04 · `C-01` N-07 parts 1/3 and case (c), D-01 and D-08 re-authored · `ALT-F2` N-06 scope
case 3 · `ALT-F3` N-07 same-function-object assertion · `C-04` N-08 regenerate-and-commit,
`--check` in verify, `HARNESS_REVIEW_SHA` defaulting to `HEAD` · `A-06` (finding) N-02 three
scope-guard conditions, N-04 re-runs `test-post-merge-sweep.py` · `C-02` N-09 parts 2–3, the false
"N-01 holds it" prose deleted · REUSE `F-01` N-01 exports `add_worktree`, the four existing copies
left alone.

## Decisions I took rather than asked

1. **Old SC-21 declared `evidence: unit`; the consolidated SC-11 declares `integration`.** Its
   decisive clause — the effect *absent* when a delegate fails — needs a real worktree, a real
   merge and a real rebase, none of which can live under `tests/unit/`. Nothing is signed, so the
   wrong declaration is corrected before signature rather than carried into it.
2. **SC-12's nothing-altered clause moved from `inspection` to an assertion in
   `tests/integration/test-nonregression-baseline.py`** (N-09 part 3 clause 3), reading
   `HARNESS_REVIEW_SHA` with a `HEAD` default. A criterion declaring `integration` whose decisive
   clause lived only in a shell string would not be discharged by the kind it declares.
3. **Twelve, not fewer.** 10 REQs × ≥1 SC, REQ-03 at three and REQ-06 at two, is 13; SC-12 carrying
   both REQ-05 and REQ-10 brings it to 12. Going to 11 deletes a REQ, and each of the seven binding
   items keeps its own REQ and SC.
4. **Decision ids reused, not renumbered.** D-01…D-08 and D-11 were deleted and re-authored under
   the same ids; D-09 and D-10 needed no change. Renumbering would have broken every recorded
   citation for no gain.

## Open

- **D-06 is the operator's pick at signature and no agent may take it.** Arm A (correct
  `FEAT-03-subissue-mirror`'s record) conflicts with SC-12 **by construction**: picking Arm A also
  signs one named pathspec exclusion, for
  `.harness/harness/features/FEAT-03-subissue-mirror/feature.json` and nothing else. Arm B
  (era-exempt the pair) needs no exclusion but leaves a permanent exemption surface. Both arms are
  stated in D-06 with the recommendation (Arm A) intact.
- `plan.yaml`'s top-level `lanes:` block still describes the halted plan and is unwritable by any
  route; **D-07 carries the live lane table.** Known, already reported, not re-raised.

## Counts I actually observed, and the gate I actually ran

`plan.yaml`: 9 occurrences of `- id: N-`, **0** of `- id: T-`. `BRIEF.md`: 12 `SC-NN` definitions
(SC-01…SC-12), 12 `verify:` lines, 12 `evidence: integration`. `status: plan`,
`approval.status: pending`, BRIEF `## Approval` `status: pending`, `panel.last_run: none`.
`check-plan-routes.py` on this plan: **0 violation(s) across 1 plan(s)**, exit 0 — the six
TASK-level `DEVIATION` lines are the expected DEC-174 carve-out output. `safe_load` round-trips;
every task's `traces:` resolve to a live REQ/SC; `depends_on` is acyclic and matches eng-lead's
graph in file order; every REQ and every SC is traced by at least one task.

**Not verified by me:** no `verify:` string was executed — none of the test files this plan names
exists yet. The claim here is coverage mapping and plan shape, never green tests.

## Coverage table as written into BRIEF.md

| Item | REQ | SC |
|---|---|---|
| D-1 (DoD) | REQ-01 | SC-01 |
| D-2 (DoD) | REQ-02 | SC-02 |
| D-3 (DoD) | REQ-03 | SC-04, SC-05, SC-06 |
| D-4 (DoD) | REQ-04 | SC-07 |
| D-5 (DoD) | REQ-05 | SC-12 |
| M-1 (DoD) | REQ-06 | SC-09, SC-10 |
| M-2 (DoD) | REQ-07 | SC-11 |
| corpus gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| the live FEAT-02 / FEAT-03 collision | REQ-09 | SC-08 |
| nothing altered outside the active feature | REQ-10 | SC-12 |
