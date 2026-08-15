# Code review — FEAT-04-decisions-index — c1

**Verdict: PASS with notes.** Stage 1 (spec compliance) is clean. Stage 2 surfaces three findings,
all `med` or lower — none fire on well-formed input, and one (finding 2) is guaranteed to fire on
the very next feature that appends a decision, which is the more urgent of the two code findings
despite the lower drama.

Reviewed: `f723194..363b539` (feature baseline per `feature.yaml baseline:`, to the pinned
`review_sha`). No `[harness:human]`-tagged commits in range; `363b539` itself is a main-session
hand-edit (T-09/T-10, no agent domain covers `CLAUDE.md` or `.claude/skills/harness-handoff/`) and
is in scope — reviewed below.

## Stage 1 — spec compliance

Clean. Independently re-verified rather than taken on report:

- `check-docs.sh` run directly: exit 0, `checked 45 superseded pattern(s) across 103 file(s)`
  (file count deliberately unpinned per BRIEF SC-07 — not a divergence).
- `run-unit-tests.sh` run directly: exit 0, all six `test-gen-decisions-index.py` cases `ok`, no
  `MISCONFIGURED`.
- `gen-decisions-index.py --stdout` diffed against the committed index at `363b539` (HEAD equals
  the pin, tree clean): byte-identical — SC-05 holds at the pinned SHA, not just against drift.
- SC-09's two absence greps run over the full surface set (`CLAUDE.md`, `.claude/skills`,
  `.claude/agents`, `.harness/expertise`) at `363b539`: 0 hits each, matching the claim. Presence
  grep: 2 hits (`CLAUDE.md:36`, `:43`).
- SC-10 grep pair on `.claude/skills/harness-handoff/SKILL.md` at `363b539`: trigger markers 4,
  `floor` 1 — matches the claim.
- Committed index measured directly: 170 rows (not 169 — DEC-170 landed mid-build at `bdfa3ab`,
  so the live-heading count genuinely grew; SC-01's own wording pins this as counted at run time,
  not a frozen number, so 170 is correct, not a miss). Min ruling 72 non-whitespace chars (floor is
  20); max ruling 30 words (cap is 30) — both hold.
- DEC-170's row carries a real ruling, not the sentinel — REQ-09's teeth exercised for real, not
  just asserted.

**DEC-169 lens on SC-02, SC-06, SC-09 — all three presence halves are real, not nominal:**
- SC-02: presence is a per-row ≥20-non-whitespace-char floor on stripped prose, independently
  measured by me over the committed file (min 72) and enforced by a passing automated test.
- SC-06: `test_checker_flags_planted_stale_phrase_in_index` asserts both directions in one test —
  unmarked plant → exit 1, then the same row re-marked `ok-stale` → exit 0.
- SC-09: presence grep is a genuine positive assertion (index pointer literally present at
  `CLAUDE.md:36,43`), not inferred from the absence pair.

**SC-08 audit (inspection-only, per dispatch — not reproduced):** receipt at
`.harness/features/FEAT-04-decisions-index/observations/harness-documentor.md:118-126`. Landing
line was bare (no `ok-stale`, no narration keyword — the marker shown in the observation's own
quote is the observer's self-escape, not present in the real planted line, matching how the
observer explains it). Attribution names `DEC-120` explicitly. Revert is byte-clean
(`git status --porcelain` empty, confirmed in the receipt). The cited `docs/harness/SPEC.md:2162`
is a genuine landing line, not inferred. Non-vacuous on all four questions.

**Already-on-record, not re-raised:** DEC-102's index row lacks its `— SUPERSEDED BY` clause
because DEC-120 declares the supersession in body prose rather than in its title — confirmed still
present (`- DEC-102 @1494 ...` carries no clause) — generator gap, backlog, not a FEAT-04 blocker.

No scope creep found: `TOPIC_VOCAB` matches D-05's 24-tag list exactly; no stray `--check` flag
(A-5 honored); T-09/T-10 diffs are each exactly the one instruction PLAN gave them, nothing more.

## Stage 2 — code quality

### 1. [med] Malformed or line-wrapped existing rows are silently dropped, discarding a hand-written ruling with no error

`gen-decisions-index.py:317-323` (`parse_existing_index`) matches each line against `ROW_RE`
(`gen-decisions-index.py:74`, `^- (DEC-\d+) .*? :: (.*)$`) and simply skips any line that doesn't
match (`if m:` — no `else`, no count check). A row for a still-live decision whose ` :: ` separator
gets corrupted by a hand-edit, or whose long ruling gets hard-wrapped across two physical lines by
an editor (rulings up to 302 chars exist in the committed file today — long enough to soft-wrap in
an editor and risk becoming a hard wrap on save), fails to parse. `build_index` then treats that DEC
as having "no prior row" (`gen-decisions-index.py:287-288`) and silently regenerates it as
`RULING PENDING` (or, in the wrap case, truncates it to whatever fragment stayed on the matching
line) — no stderr, no non-zero exit, nothing distinguishing this from a decision that genuinely
never had a ruling.

Verified the regex gap directly: a synthetic row with the same prefix/tags/refs but the ` :: `
separator replaced by `--` fails to match `ROW_RE` (checked in isolation, no file writes). Confirmed
independently that all 170 committed rows currently parse cleanly (`grep -cE` count matches
`grep -c '^- DEC'` exactly, 170 == 170).

**Why `med`, not `high`:** the defect does not fire on well-formed input — it requires a row that is
already malformed or already hard-wrapped, which is itself a violation of PLAN's explicit
"one physical line per decision" invariant, and which is verified absent today (170/170 clean). The
two fail-opens this project's history measures — a dangling reference resolving to valid, a partial
match returning a fabricated result — both fire on ordinary input; this one needs a precondition
that doesn't currently exist. It contradicts the feature's own explicit design principle, stated for
the sibling case: "a silently dropped hand-written ruling is the one failure that makes the whole
index untrustworthy, so it is a hard error rather than a warning" (PLAN T-02 merge bullets, MF-5).
That principle is enforced for a DEC whose *heading* vanishes from the authority (orphan detection,
`gen-decisions-index.py:263-274`) but not for a DEC whose *own row* fails to parse while its heading
is still live — the same class of loss, undefended on this path, and untested (none of the six tests
in `test-gen-decisions-index.py` exercise a malformed-row or wrapped-row fixture). If the corruption
does reach a committed index, `test_committed_index_is_complete_and_within_budget` (test 5) catches
the `RULING PENDING`-reversion variant on the next unit-test run before ship, but not the
line-wrap-truncation variant, since a truncated fragment can still clear the 20-character floor.

**Non-blocking open question:** should the generator hard-error on any `^- DEC-` line that fails
`ROW_RE`, the same way it hard-errors on an orphaned key — rather than silently treating it as
"no prior row"?

### 2. [med] Test 1's two hardcoded sanity counts are a landmine for the very next feature that appends a decision — unconditional, not requiring any precondition

`test-gen-decisions-index.py:115-119` hardcodes `171` (raw regex count) and `170` (fence-guarded
distinct count) as pass/fail conditions in `test_row_per_distinct_dec_matches_authority`. The test's
*primary* assertion (generator row count == computed distinct count) is correctly dynamic and
survives future decisions, matching PLAN's own instruction that this "survive[s] the next appended
decision." But REQ-09 (landed by this same feature) makes it a standing obligation on every future
feature that appends a decision to `docs/harness/DECISIONS.md`: the very next one bumps both raw and
distinct counts, and these two hardcoded checks will FAIL for a reason invisible to that feature's
own correctness — nothing in `feature.yaml`'s `pending`/REQ-09 narrative, nor anywhere in this diff,
documents that appending a decision also requires updating these two magic numbers. Unlike finding
1, this fires with certainty on the very next ordinary use of the feature, not on a precondition
that must first go wrong.

### 3. [low] Test 2's "byte-identical" claim is checked by substring containment, not equality

`test-gen-decisions-index.py:198-199` (`test_preserves_hand_written_rulings_by_dec_number`) —
PLAN's own description of this test says "assert: all 5 original rulings are present byte-identical"
and it is billed as covering "the only real logic in the feature." The actual check is
`if rulings[n] not in by_dec[dec]:` — substring containment, not `==`. Sibling test 3
(`test-gen-decisions-index.py:279`) does use exact equality for its own byte-identical claim. A
regression that prepends or appends stray characters to a preserved ruling while keeping the
original text intact as a substring would pass test 2 silently. Narrower than the other findings
here since it doesn't reflect a shipped defect (SC-05's idempotency held exactly at the pin), but it
is a real gap in the rigor this specific test claims for itself.

## Ranking

1. med — finding 2 (hardcoded 171/170 sanity counts — fires unconditionally on the next feature)
2. med — finding 1 (silent row-drop / truncation on malformed or wrapped rows — needs a precondition)
3. low — finding 3 (substring vs. equality in test 2)

None gate. `must_fix: []`, `severity_max: med`.
