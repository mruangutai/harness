# Apply — cycle 8 panel fixes PP-01..PP-06 — FEAT-58-corpus-outside-worktree

**All six landed, none declined, in the operator's ruled order (Q7). Two fields changed in the
whole plan and nothing else: `tasks[N-13].intent` and `tasks[N-06].intent`.** Proven field-by-field,
not by eye — every loaded value diffed against `HEAD:plan.yaml` reports exactly
`['.tasks[N-06].intent', '.tasks[N-13].intent']` changed, zero keys added, zero removed
(`/tmp/f58_fielddiff.py`). `status: plan`, `approval.status: pending`, the `panel:` block, all 17
decisions and both `verify:` strings are untouched. **`BRIEF.md` was not written at all this round**
— its only working-tree diff is the operator's own cycle-8 SC-16 amendment at `:299-304`.

## Per finding

| finding | verdict | landed as |
|---|---|---|
| PP-01 + PP-05 (one respelling) | **LANDED** | N-13 PART 1: by-absolute-path invocation of `<owner_root>/.claude/skills/harness/bin/check-state.sh`; override stripped from the child env + discard-notice assertion; read AS IT STANDS ON DISK |
| PP-03 | **LANDED** | N-13 PART 1 clause 1: no REFUSAL + missing set EMPTY, unexpected-only non-gating report TOLERATED with names printed; old clause 4 diagnostic folded in |
| PP-04 | **LANDED** | N-13 PART 1 `PART 1 RED PROOF` block, written against the post-PP-01/PP-03 assertions |
| PP-02 | **LANDED** | N-13 PART 2: fourth announced-skip condition on `core.hooksPath`, naming INV-31, plus its own discrimination |
| PP-06 | **LANDED** | N-06 PART 4: `THE ZERO-MATCH REFUSAL CASE, NAMED` in `test-check-state-expected-dirs.py`'s case list |
| reconcile | **LANDED** | no REQ/SC moved, so the BRIEF coverage table needed no edit; ledger unchanged at 45 |

## The three judgement calls, with the evidence

**1. The by-path spelling overrides the panel's PP-01 remedy, and the task says so.** PP-01
proposed running the *worktree's* copy under `HARNESS_PROJECT_DIR=<owner_root>` and declared the
by-path invocation forbidden; Q1 rules the opposite. N-13 now carries one clause naming the
cycle-8 ruling explicitly so a later reader cannot restore the panel's version.

**2. The hazard clause is required, not defensive.** `resolve_root` (`harness_boundary.py:66-78`)
prefers a `HARNESS_PROJECT_DIR` override *carrying MARKER* over the derived root, and a feature
worktree of this repo carries `MARKER` (`.harness/team-config.yaml`). So a stray override in the
ambient environment reinstates exactly PP-01's vacuity even under the by-path spelling. PART 1
therefore removes the variable from the child environment (removed, never emptied) and asserts the
resolver's discard notice is absent from stderr, which `check-state.sh:36-46` keeps and replays.

**3. I took the lead's staging spelling for the red proof unchanged, and it is the only survivor.**
In-place edit of the owner root's script is excluded by N-13's absolute read-only rule; a lone temp
copy re-resolves its own root from `_selfdir` and cannot import `harness_boundary` — the property
this plan already records about itself at N-06 PART 3(c). What remains: stage the pre-fix copy
*alongside the bin modules it imports* in a temp directory the task creates and removes, and point
it at the owner root with the MARKER-carrying `HARNESS_PROJECT_DIR` override, which is a read.
The task states the override is used **there and only there**, so it cannot be read as licence to
weaken the authoritative run.

**No `HARNESS_REVIEW_SHA` token survives in N-13** (asserted programmatically). The reason for
dropping the ref framing is stated inline without naming the variable, and the struck framing is
recorded as struck so it is not restored. The phrases "reviewed commit" and "cwd at the owner
root" appear in N-13 **only inside the sentences that strike them**.

## Counts and ledger

- tasks **12** (`N-01..N-10`, `N-12`, `N-13`; `N-11` retired, id left as a gap) · decisions **17** ·
  criteria **15** in `BRIEF.md` (`SC-16` present, `SC-15` struck, id left as a gap). No count moved.
- **Ledger 45, no row lost.** Counted by chaining the apply notes — `apply-consolidation` (36) →
  `apply-batch-c3` (42) → `apply-c5` (41, one row removed by name, SC-15's) → `fold-n11` (moved one
  row's owning task, removed none) → `apply-c6` (45, four added by name). This round adds no row and
  removes none: all four cycle-6 rows land on the same files as before
  (`test-check-state-realdata.py`, `test-check-state-verify-gate.py` case (d)) and this pass changes
  their **assertion wording and evidence machinery**, not their landing place.
- `check-plan-routes.py` on this plan: **0 violations, exit 0**. Every `DEVIATION` line is the
  DEC-174 carve-out working (D-07); the `MANIFEST` line is informational and uncounted.

## Undisturbed — verified after the edits, by field-level diff and by grep

- The three weight-bearing proofs: merge regression `MUST FAIL TODAY` (1 occurrence, N-04),
  equivalence `EXIT 0 IS EXPLICITLY NOT PROOF` with exit status excluded (1 occurrence, N-06 PART 4
  — inside the intent I amended; the line diff shows the only N-06 change is +11 lines after
  line 206), `--verify`-does-not-repair in its own file with its red proof (N-02, unchanged field).
- The two-route D-2 denial — recorded in `D-02`, carried by `N-03` (Write/Edit via
  `check-domain.sh`, Bash via `bash-write-guard.sh:855`, with its paired positive control) — and
  every cycle-3/5/6 operator ruling: unchanged fields, so
  byte-identical by construction — D-01, D-05, D-12 (exit 8 reported, non-gating), D-13, D-14,
  D-15, D-16, D-17, the remedy-(b) rejection in N-06 PART 1, the ten record-less directories /
  issue 1640 non-suppression, and N-06 PART 3's four cases (a)-(d).
- `BRIEF.md` `## Approval`, SC-09 (`:239-252`) and SC-16 (`:299-315`) re-read at final state and
  byte-identical to the state I found: `git diff` over `BRIEF.md` carries exactly one hunk, the
  operator's SC-16 amendment, and none near SC-09 or `## Approval`.

## Open — noticed, NOT edited (there is no round after this one)

1. The ledger is fixed at 45 by dispatch, but this round adds three genuinely new graded
   assertions: the zero-match refusal case, PART 1's red proof (a one-time proof, D-13 class, like
   N-06 PART 3(c)), and the hooksPath skip's discrimination. If the ledger is meant to enumerate
   *graded* assertions rather than the consolidated set's landing places, it is arguably 48. Left
   at 45 as instructed; a future pass may want the three rows named.
2. `N-13` PART 1 and the red proof both now depend on `harness_boundary`'s override-discard notice
   being written to **stderr** in a form a test can match. Nothing in the plan pins that string, and
   `harness_boundary.py` is not in any task's `files:`. If the notice's wording is not stable, the
   implementer will need a looser matcher — a build-phase discovery, not a plan defect.
3. The DoD note's `bash-write-guard.sh:512` anchor is still stale (creation door `:624-741`); N-13
   already carries the corrected anchor. The note is the operator's, unedited (repeat of c6 Q2).
