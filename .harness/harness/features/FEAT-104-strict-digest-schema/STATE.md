# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- runs: `2026-09-09-05-qa-gate-validator`, `2026-09-09-06-simplify-eng` (round 1, graded the
  amended-away `99035a9c`), then `2026-09-09-07-qa-gate-validator`, `2026-09-09-09-simplify-eng`
  (round 2, graded the real tip `168f875f`)
- squads: validator (QA gate) and eng (harness-simplify), sequenced as two segments, run twice
- status: validate — **the code at `168f875f` is READY for a new review pin.** The reviewer panel
  has NOT re-run; no goal-check, no UAT, no briefing. `review_sha` re-pinned to `168f875f`.

**The commit under assessment moved mid-cycle and that is the headline for the record.** Round 1
graded `99035a9c`. The main session then amended it away; `168f875f` is its SIBLING, not its
descendant, and is the branch tip. Round 1's `MF-1` — "an unattributed commit reverted the F2 fix"
— is therefore RETRACTED: the missing F2 hunk is the main session's deliberate declination, not a
revert. Round 2 re-graded everything at the real tip. Both rounds are preserved.

**File-by-file at the tip, measured, not inferred.** `check-domain.sh`, `test-check-domain.py` and
`test-validate-digest.py` are byte-identical to `99035a9c` (F1 and F3 assertions present).
`validate-digest.py` carries only the F3 message line adding the by-file declaration route; the
comment reword that existed at `99035a9c` is reverted to the original archive-reader wording.
`check-state.sh` and `test-check-state.py` are byte-identical to the old pin `6126ac07` — F2 is not
in the tree.

**QA PASSES at the tip, blocking gate satisfied.** `matrix_ok: true`. unit exit 0 (36 files),
integration exit 0 (70 files), full canonical suite exit 0 (106 files); all four `^FAIL ` lines
attributed to `tests/unit/test-factory-claim-mutation.py`'s own mutation proof. F1 CLOSED — T-06
12/12, the downgrade case now refuses at exit 2 with the message substring, where the pre-fix
witness was 11/12 with the downgrade ACCEPTED. F3 CLOSED — T-04 34/34, and the tip's emitted
rejection text was re-read verbatim rather than inherited from round 1.

**F2 is DECLINED with evidence, and the evidence corrects an error in this cycle's own record.**
Round 1's census swept from the MAIN CHECKOUT and reported `discovery 309 / strict_count 0`,
concluding F2 was "a measured no-op". FEAT-104's `runs/` tree is gitignored and exists only in the
worktree, so that sweep was structurally blind to every strict record this feature produced. Round
2 re-took it from the worktree: `discovery 324 / strict_count 4`, and **1 of the 4 — this feature's
own `runs/2026-09-09-02-qa-gate-validator/digest.md`, on keys `failures`/`kinds`/`suite` — fails
under its raw host persona and passes only under generic `lead`.** The corrected measurement
supports the declination rather than merely permitting it. The round-1 premise is retracted on the
record; round 1's `matrix_ok` verdict survives the retraction.

**SIMPLIFY: tip READY, one surviving residual, two findings withdrawn.** Zero simplification
findings survive — the reworded comment is gone at the tip and the `test-check-state.py` refactor is
absent. Efficiency stays EMPTY (measured, not assumed: the guard reuses an already-parsed
`prior_doc`, no new read). Altitude: `leave`, `leave`. REUSE survives, corrected at the tip: **3
complete strict-`schema_version` predicates** (`check-domain.sh:1594-1597`, `check-domain.sh:1761-1764`,
`check-state.sh:1487-1489`) plus 2 partial type-half restatements (`check-domain.sh:1601`,
`:1767-1768`), with no shared home — a backlog-grade maintainability residual, not a pin blocker.
The pass was FLAG-ONLY throughout: every touched path is inside the DEC-174 carve-out, so no agent
applied anything and no code or test file was edited in either round.

**Two run digests are contract-INVALID on disk and no persona can repair them.**
`runs/2026-09-09-06-simplify-eng/digest.md` is missing the required `adequacy_notes`;
`runs/2026-09-09-08-simplify-eng/digest.md` (round 2's superseded draft, preserved untouched)
declares `VERDICT: PASS` beside a `FAIL` member step. `check-domain.sh:1327` refused both in-place
corrections: its correction channel demands a strict textual prefix-append, and
`validate-digest.py`'s parser stops at the indent-0 `artifact:` line, so appended text is never
parsed. The guard refused the owning lead twice, which is why `2026-09-09-09-simplify-eng`
supersedes `-08` rather than correcting it. Both blockers are inside DEC-174.

`cycles_used` 7 → **8**. Both leads reported ZERO send-backs. The round-2 re-dispatch is counted
inside the same cycle deliberately: no gate FAILed, no SC went unmet, no lead sent anything back —
the base commit moved, which is none of DEC-157's three triggers. Runs 14 → 18 of 20; the budget is
informational and each of the four earns its place (round 1 established the F1/F3 closure method and
surfaced the commit divergence; round 2 corrected the census and the tip grading). One cycle of
rework remains before the hard bound, and the re-panel is the natural claimant.

## Open Questions

- Q1 (blocking, main session only, DEC-174): `check-domain.sh:1327`'s append-only correction channel
  cannot repair a run digest, because `validate-digest.py`'s parser stops at the indent-0 `artifact:`
  line and never sees appended text. Two invalid digests are stranded by it (runs `-06`, `-08`). A
  harness defect, not a finding about this diff. Remedy: allow an in-place correction for a digest
  that fails its own contract, or make the parser read past `artifact:`.
- Q2 (not blocking, main session only, DEC-174): with F2 declined, the generic-`lead` exemption
  (`validate-digest.py:1407`, `check-state.sh:1590`) is now a LOAD-BEARING invariant — a decision was
  just made on the strength of its behaviour — and NO test can report red on it;
  `test-check-state.py` carries no digest or persona-selection case at all. Add one, or accept the
  gap explicitly. Rated `med` by the validator lead, non-gating: no defect exists at the tip.
- Q3 (not blocking): the 3 complete + 2 partial strict-version predicate spellings above want one
  `is_strict_schema_version()` home beside the schema loader. Main-session only. Backlog row or
  fold-in before the pin?
- Q4 (retired, recorded so it is not re-asked): the panel's Q2 — order F1 against SIMPLIFY's S2 —
  is retired, not answered. At the tip only `check-domain.sh` carries the remedy and that is
  sufficient: a version-2 run's declared version can no longer decrease through the write-time gate,
  so the at-rest sweep's self-declared key is not reachable by the downgrade route the panel
  described.
- Residue of Q4, not gating: `check-domain.sh` governs Write/Edit-tool payloads only, so a
  Bash-authored `state.yaml` bypasses it (DEC-85's acknowledged sharp edge) and the at-rest sweep
  still keys on the self-declared value. Same F1 class, already with the main session.
- SC-12 (`verify: inspection`) and SC-13 (`verify: uat`) remain unexercised. SC-13 gates
  (`gates.uat` is `blocking_when_uat_criteria_exist`) and no harness run can close it.
- Unchanged and still unanswered: whether the INV-26 card/plan mismatch is a harness defect rather
  than drift; and `check-domain.sh`'s worktree-claim guard being keyed per persona with no
  per-session identity, so a live claim on another feature refuses this feature's same-persona agent
  its own writes.
