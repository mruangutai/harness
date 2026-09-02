# STATE

## Current

- feature: FEAT-53-metrics-dashboard
- run: .harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-02-09-product/digest.md
- squad: none
- status: awaiting-user

Plan phase, fifth signature pass, at the operator's gate — and the plan is READY TO SIGN. The
cycle-4 budget question is closed: `max_total_cycles` is 20 in feature.json per the 2026-09-02
ruling (DEC-157), 11 used, so the build phase starts with 9 rework cycles rather than 1. All five
ordered fixes are applied and verified at source by me, not merely reported: B-19 — T-19's
simulated ship now git-inits the copytree copy, makes a baseline commit and asserts the copy's tree
clean with trend.jsonl TRACKED, keeping the non-git case as the labelled failure branch, so
record_ship's commit is observed SUCCEEDING and not only failing; B-20 — T-10 defines the week as
UTC ISO-8601 (Monday 00:00:00Z to next Monday exclusive, label = that Monday), 30d/90d derived from
resolve_window and `all` anchored at the earliest record's week; B-21 — the record no longer
presents two settled rulings as open, D-08 records the alpha ACCEPTED (operator 2026-09-01) with a
three-part rollback NAMED for the first time (exact version pin plus committed bundle; DESIGN C-2's
per-capability `If absent` workaround applied in place, enumerated; hard-requirement capabilities
→ T-18 records STOP and a replacement library becomes an operator decision taken then), D-20 records
the client build KEPT, both BRIEF `## Constraints` bullets agree, and DESIGN's dead react-charts
reference is gone at zero occurrences file-wide; B-22 — new decision D-23 is the single carrier for
all fourteen accepted backlog rows with a one-line subject for the six that carry no panel
disposition; B-24 — the false evidence is corrected in BRIEF `## Verification gaps` and T-07.intent,
`1024` and `ES2022` deleted as carriers of the token `12` and the true carriers `127.0.0.1`, `122`,
`3x3` and `python3` named, with the conclusion unchanged. B-23 and B-25 are accepted as backlog
labelled Dashboard, carried by D-23 and by dispositions C4-05 and C4-07.

The cycle-5 panel (2026-09-02-08-validator) returned PASS, severity_max med, must_fix EMPTY, both
readers ran and neither was skipped — the second consecutive panel that gates nothing. It raised
three new single-clause findings, ALL THREE residue of the cycle-5 fix pass itself: T-19's new case
could not pass as written (git init leaves the fixture tree untracked, so the clean-tree assertion
fails on `??` lines — I measured this directly rather than inferring it), D-23 and C4-04's note both
asserted something this plan contradicts, and T-10's week definition left the window-boundary bucket
undefined between two readings that disagree. All three are closed in
runs/2026-09-02-09-product: T-10 now pins the windowed reading REQ-15 forces, with the
bucket-sum-equals-headline invariant asserted as its own case and a distinct verbatim reason for a
partial bucket so no sentence asserts something false; T-19's setup makes one baseline commit; the
D-23/C4-04 clause is true. plan.yaml's panel key reads cycle 5, last_run 2026-09-02-08-validator,
28 findings, the three new ones resolved with citations and the 25 earlier ones carried.
plan.yaml and BRIEF.md both still read approval pending; only the main session signs, including
BRIEF.md's date field, which is load-bearing for cycle time.

Fifth signature briefing at notes/ship-review-2026-09-02-plan-c5.md. Phase handoff at
notes/handoff-plan.md.

## Open Questions

- The three cycle-5 findings were closed WITHOUT a sixth panel read. Each is a one-clause factual
  correction inside a field the panel had just named, and I verified each at source myself, but the
  operator should know the closure is orchestrator-verified rather than panel-verified. A sixth
  panel is available for the cost of one run if wanted; my read is that it would find the residue of
  this fix pass and the sequence does not obviously terminate.
- Harness defects, non-blocking, both second-occurrence: (1) `validate-digest.py` rejects a
  plan-phase code-review digest on the YIELD path — `code_grade cannot be bound to review_sha ...
  unpinned feature (INV-6)` for every value tried — so DEC-207's plan-phase exemption exists on the
  input path and is missing on the yield path, and the host returns exit 1 on a well-formed
  `VERDICT: PASS`; the verdict and artifact were recovered from disk both times. (2)
  `check-domain.sh` refuses any Write that replaces an existing `<run_dir>/digest.md` while
  `validate-digest.py` (DEC-156) requires the file at `artifact:` to carry the §10.4 block, so a
  lead that writes prose first cannot then add the block; resolved here by a companion
  `digest-corrigendum.md`. Neither is fixable by a squad — both edit the harness skill `bin/` tree.
- Line anchors inside the 25 carried panel findings shifted when T-10, T-19 and D-23 were amended.
  A rotted anchor asserts nothing false and the summaries are immutable by design; a refresh is
  available if the operator wants them re-pinned before signature.
