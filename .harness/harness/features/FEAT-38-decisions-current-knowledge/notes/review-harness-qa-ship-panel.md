# QA ship-panel review — FEAT-38-decisions-current-knowledge

review_sha `635cd3ba`. Working tree confirmed byte-identical to `635cd3ba` for every path in the
shared file set (`git diff 635cd3ba -- <path>` empty for each, checked individually — a
directory-wide `git diff --stat` with multiple pathspecs silently returns nothing useful and is
not admissible on its own). All commands below therefore ran against the pin, in place, read-only.

**Environment note for whoever reads this next:** the `read`/`grep` tools' default root for a
bare relative path is the OUTER repo checkout (`/Users/molchairuangutai/GitHub/harness`, sitting at
`7ebfc9e`), not this worktree. A bare-path `read` of `gen-decisions-index.py` returns the
pre-feature file with `AMEND_HEADING_RE` still live and a 3-tuple `parse_decisions` return —
which looks alarmingly like SC-06 is unmet. It is not: that content is the wrong tree. Every
finding below was re-derived after prefixing paths with the full worktree path or `cd`-ing there
in `bash`. Filed as an open question at the end because it cost a full detour here.

## Part 1 — SC-11 re-grade, five entries only

Per the corrected scope (DEC-205 excluded, coverage is SC-16's). For each: pre-fold text from
`git show 99bb52c:.harness/harness/docs/DECISIONS.md`, folded form from `git show 635cd3ba:` same
path. `diff` between the two extracted entries (full heading-to-heading span) shows, for all five,
**zero prose lines changed — the only deletions are the `<!-- claim: ... -->` marker lines (and
one adjacent blank line each)**. That is the whole story for this re-grade: T-27 touched nothing
but markers here, so the question reduces to whether the belief/falsification narrative already
lived in prose independent of the marker, or leaned on marker text for content.

| DEC | Markers removed (99bb52c→635cd3ba) | Belief/falsification survives as prose | Verdict |
|---|---|---|---|
| DEC-145 | 1 (`CRAFT_LINE_BUDGET = 150` grep) | `DECISIONS.md:3242-3244` (635cd3ba) — "**Deploying the checker is the control; authoring discipline is not.** Where the caps were authored but the checker was not yet deployed, 9 of 15 Expertise files failed it again within a day of being distilled." Prior belief (authoring discipline suffices) stated, falsification (9/15 failed again) stated, both untouched by the marker deletion which sat 13 lines earlier next to an unrelated enforcement sentence. | **met** |
| DEC-157 | 1 (`"max_total_cycles": 10` grep) | `DECISIONS.md:3551-3559` — "`max_total_cycles` kept exhausting on healthy features... The audit of those numbers says otherwise: FEAT-02's 19 'cycles' span 16 runs, of which only ~6 were rework." Prior belief (the counted unit was right) and its falsification (audit of real runs) both in prose; deleted marker was a bare config-value assertion two bullets later, no narrative content. | **met** |
| DEC-181 | 2 (`budget is 80` grep, `grep -c CLAUDE.md`) + the earlier `budget is 300` grep | `DECISIONS.md:4788-4793` — "**Issue #139 ruled out `check-domain.sh`'s shape gate**... Both clauses were true when written and neither is true now: the main session is bound on all four routes." Belief (issue #139's stated reason) and falsification (both clauses now false) survive; the three deleted markers sat elsewhere and asserted only numeric facts already stated in the adjacent prose (e.g. "feature.json 300" already appears in the sentence the third marker sat under). | **met** |
| DEC-183 | 3 (`name: Plan-route gate`, `violation(s) across`, CODEOWNERS grep) | `DECISIONS.md:4900-4901` — "`check-plan-routes.py` shipped working and nothing mechanical ran it (issue #133). DEC-179's clause 'nothing executes it automatically' is now false." A second, larger fold at `:4922-4936` — "THE STEP IS UNGUARDED, BY DECISION... All 39 of those assertions were deleted by owner decision" — states the prior design (a heavy assertion suite) and its falsification/replacement (owner decision to drop it). Both survive; none of the three deleted markers carried narrative, only checker-output-format and CODEOWNERS-line assertions. | **met** |
| DEC-193 | 1 (`WORKTREES_SEGMENT =` grep) | `DECISIONS.md:5349-5357` — "**The evidence, and the wording matters because half of the original evidence was overtaken.** Measured at `a29ad06`: a Write to `<root>/src/main.py` exited 2 while the same write via Bash exited 0... The other case — a session ROOTED in the sibling worktree — is NOT evidence of an enforcement hole." Belief (both cases were evidence of a hole) and falsification (one case reclassified) both present; the deleted marker was a code-constant assertion in an earlier paragraph, unrelated. | **met** |

**Result: 5/5 met.** The specific failure this re-grade watches for — a falsified claim deleted
along with its marker, leaving only the marker's absence to notice — did not occur in any of the
five. In every case the marker was a pure verification aside (a `grep`+expected-value pair over
code) bolted beside prose that already carried the belief/falsification content on its own; T-27's
edit is a clean structural excision, not a content edit, confirmed by `diff` showing zero non-marker
line changes per entry.

## Part 2 — Adequacy

### 2a. Which changed units does the green suite bind?

Ran the live suite in place (worktree = pin for every path checked): `bash
.claude/skills/harness/bin/run-unit-tests.sh`, `RC=0`. Counted in Python against the actual
`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` literals (not a bare `PASS ` regex — that overcounts: one
script, `test-inflight-registry.py`, prints an internal case line `PASS
case_floor_inflight_registry.py` that itself matches the naive per-script marker regex, inflating a
naive count to 56). Intersecting the regex hits against the declared 55-name set gives **55/55
matched, 0 missing, 0 FAIL lines** — the true, current discovery count at `635cd3ba` itself (the
qa-ship-gate record measured 55 at `8a7c75c`, a different, earlier commit; this run re-derives the
same number independently at the actual pin, after the SIMPLIFY dead-code apply landed).
`--check-kinds` also re-run standalone: `RC=0`, "the script arrays and test_kinds.integration.detect
agree."

Per changed file:

| File | Bound by | Evidence |
|---|---|---|
| `run-unit-tests.sh` (T-24 array edit) | `test-run-unit-tests-kinds.py` `case_1_green_on_the_real_tree` — invokes `--check-kinds` against the REAL config and REAL arrays and asserts zero KIND-DRIFT lines; this is the one case in the suite that exercises the actual current arrays, not a synthetic copy. Also self-checked by the runner's own inline drift detector (unmodified, confirmed at gate item 7 and re-read directly here at lines 60-74). | direct |
| `check-decision-claims.py` + test (T-24, deleted) | none, by design — Contract 3. Confirmed absent from the reviewed tree (`git ls-tree -r 635cd3ba \| grep check-decision-claims` → `[]`, re-derived independently of the gate record). | n/a, accepted |
| `gen-decisions-index.py` (dead-code apply + earlier T-06/T-10 work) | `test-gen-decisions-index.py`, run directly: `PASS`. SC-06's dead-code claim independently re-verified: no `AMEND_HEADING_RE`/`AMEND_BOLD_RE`/`SUPERSESSION_VERB_RE`/`BODY_SUPERSESSION_RE`/`compute_amendments`/`format_amendment_span`/`compute_supersession_target` anywhere in the file at the pin (grepped directly against the worktree copy, not the outer-repo trap above). | direct |
| `test-gen-decisions-index.py` SC-07 case | `test_no_amendment_construct_survives_in_the_authority` — see mutation proof below | direct, mutation-proved |
| `check-decision-anchors.py` + test (RETAINED, frozen) | `test-check-decision-anchors.py`, run directly: exit 0, 8 named `ok -` cases. SHA-256 independently re-verified against `git show 635cd3ba:` of both paths — `adb9a648...` and `7a4e0ba1...`, matching Contract 2 exactly (re-derived, not copied from the gate record). | direct |
| `.harness/harness.json` (T-25 `detect` edit) | `--check-kinds`, run standalone: agree. Also `test-run-unit-tests-kinds.py`'s `case_1` reads this exact file. | direct |
| `board_lifecycle.py`, `check-domain.sh`, `.github/workflows/tests.yml` (earlier tasks) | Diffed the full range (`7ebfc9e..635cd3ba`): all three changes are **comment-text only** — repointing stale citations `DEC-186`→`DEC-203`, `DEC-192`→`DEC-203` (×3), `DEC-171 am.1`→`DEC-171` (×2). Zero logic delta; nothing to bind behaviorally. Checked the citations themselves resolve: `## DEC-203` is a live heading at the pin (`DECISIONS.md:5982`); DEC-186/DEC-192/DEC-171-am.1 no longer appear anywhere in these three files. **Looked, nothing to report** — this is exactly REQ-04/SC-04's citation-repointing sweep working as intended, no residual dangling reference. | citation-resolution check, not a behavioral test (none needed — no behavior changed) |
| `DECISIONS.md`, `DECISIONS-INDEX.md` | No standing automated check binds prose truth. `gen-decisions-index.py --stdout` diff-clean against the committed index is the one mechanical tie (SC-05, part of the standing suite via `test_committed_index_matches_a_fresh_regeneration`); everything else is Part 3 below. | see Part 3 |

### 2b. Can the new/changed assertions actually fail? Mutation-proved.

**SC-07.** The discriminating case is `test_no_amendment_construct_survives_in_the_authority`
(`test-gen-decisions-index.py`, named `TESTS` entry, `ok -` line is its own function name — it
cannot be silently dropped without the suite's own test count changing). Unlike most of this
file's cases it is NOT a synthetic-fixture test — it reads the live `DECISIONS.md` directly and
regex-sweeps for `### DEC-N amendment`, `**Amendment`, and `am.\d`. Proved discriminating with a
mutation, run in a disposable copy **outside the repository** (`/tmp/feat38-mut2/`, plain
directory replica of the four files the test/module actually touch — `bash-write-guard` blocks
`git worktree add` outside `.claude/worktrees/` per DEC-193, so a real worktree was not an option;
a plain temp-dir copy was used instead, consistent with the constraint):
- Baseline (unmodified copy of the pin's `DECISIONS.md`): `ok -
  test_no_amendment_construct_survives_in_the_authority` / `RESULT: True`.
- Planted `### DEC-9999 amendment 1` at the tail: `FAIL - ...: '### DEC-N amendment' heading found
  at .../DECISIONS.md:[6274]` / `RESULT: False`.
- Restored the exact pin content: back to `ok -` / `RESULT: True`.
- `git status --porcelain .harness/harness/docs/DECISIONS.md` in the real worktree: empty, both
  before and after — nothing in the reviewed tree was touched.

**SC-08.** Ran `check-decision-anchors.py --file` directly against three targets:
- `git show 7ebfc9e:.harness/harness/docs/DECISIONS.md` (the brief's `base_sha` for this
  criterion): `examined 32 anchor(s), 3 failed`, naming exactly the three `feature.yaml` anchors
  (`FEAT-03-subissue-mirror/feature.yaml:73`, `feature.yaml:63-64`,
  `FEAT-03-subissue-mirror/feature.yaml:97`), `RC=1`.
- The pin's own `DECISIONS.md`: `examined 20 anchor(s), 0 failed`, `RC=0`.
- A temp copy of the pin's file with one fabricated anchor appended
  (`` `nonexistent-fabricated-file-xyz.py:9999` ``): `examined 21 anchor(s), 1 failed`, naming the
  planted anchor, `RC=1`.

All three SC-08 observations independently re-derived (not copied from the gate record), all
three pass.

### 2c. Discovery count re-derivation (`run-unit-tests.sh`'s own registration edit)

Covered in 2a: 55/55 against the literal `UNIT_SCRIPTS`+`INTEGRATION_SCRIPTS` union, non-zero,
matches `len(UNIT_SCRIPTS)=27 + len(INTEGRATION_SCRIPTS)=28`. Re-derived at `635cd3ba` directly
(the gate record's 55 was measured at `8a7c75c`, a different, earlier SHA in the same range —
this closes that gap).

### 2d. SIMPLIFY dead-code apply (landed after the gate record) — still green at `review_sha`

The apply is a five-line diff in `gen-decisions-index.py` between `99bb52c` and `635cd3ba`:
`parse_decisions` no longer returns the unused `lines` tuple member or sets a dead `"title"` key;
`build_index` unpacks two values instead of three-with-a-throwaway. The suite run in 2a (`RC=0`,
55/55, 0 FAIL) was executed against the actual pin content, i.e. **with this apply included** —
it is not stale evidence from before the apply landed. `test-gen-decisions-index.py` passing
confirms no caller regressed from the signature change.

## Part 3 — What no gate can tell this panel

Stated in the brief's own "What removal costs" section and independently confirmed by the marker
census above (11 markers, 6 entries, all removed, all replaced by nothing): **after this lands,
nothing in the tree detects semantic citation rot** — a `file:line` a decision cites that still
resolves and no longer says what the entry claims about it. `check-decision-anchors.py` proves
existence and range only (SC-08 above); it cannot and does not check content. Concretely
unprotected, by design, going forward:

- Every one of the 15 folded entries' claim that "what falsified the prior belief" is accurately
  restated — the exact content SC-11 exists to human-check, and which this re-grade found intact
  for its five, but which has no mechanical backstop for the other ten or for any future edit to
  these five. A future PR could quietly soften or drop the falsification clause from any of these
  entries and nothing in CI would object.
- SC-12/SC-13's semantic reading that a folded entry "reads as current truth, not merged history"
  — inherently a prose-quality judgment, not a predicate.
- REQ-09 itself — "a human has read each folded entry against its pre-fold form" — is a process
  attestation with no artifact enforcing it happened beyond the review record itself (this file,
  the earlier `review-harness-qa-c0.md`, and the UAT note).
- Any future entry that grows a NEW amendment block is caught mechanically (SC-06's dead-code
  removal notwithstanding — `test_no_amendment_construct_survives_in_the_authority` still sweeps
  the live authority text directly, independent of the generator's own amendment code, and is
  mutation-proved above), but a rewrite that keeps single-entry, non-amendment SHAPE while quietly
  reverting the CONTENT to something already disproved is invisible to every check in this tree.

## Verdicts on the full shared file set (Contract-aware, no pre-emptive skips)

- `run-unit-tests.sh` — looked, one array-line change, bound by `test-run-unit-tests-kinds.py`
  case_1 against the real tree. No finding.
- `check-decision-claims.py` + test — looked, confirmed deleted from the reviewed tree
  independently. No finding (Contract 3).
- `gen-decisions-index.py` + test — looked, SC-06 dead-code claim and SC-07 discriminating case
  both independently re-verified, including a live mutation proof. No finding.
- `check-decision-anchors.py` + test — looked, byte-identical to `99bb52c` (independently
  re-hashed), still named on both registration sides, SC-08's three observations all reproduced.
  No finding (Contract 2 — not re-reporting the known docstring issue).
- `.harness/harness.json` — looked, one `detect` string entry, `--check-kinds` agrees. No finding.
- `board_lifecycle.py`, `check-domain.sh`, `.github/workflows/tests.yml` — looked, comment-only
  citation repoints, all targets resolve to a live heading, no logic touched. No finding.
- `DECISIONS.md`, `DECISIONS-INDEX.md` — SC-11 graded above (5/5 met). SC-05 (index diffs clean)
  covered by the standing green suite. Everything else is Part 3's named, accepted, unprotected
  surface — not a finding, a scoped limitation the brief itself already prices in.

No tracked file was modified. All mutation probes ran against copies outside the repository
(`/tmp/`); the one attempted `git worktree add` outside `.claude/worktrees/` was correctly refused
by `bash-write-guard` per DEC-193 and abandoned in favor of a plain directory copy. HEAD was not
moved; `git status --porcelain` on the worktree shows no changes from this review.

## Part 4 — SC-11 inherited-coverage seam

**Target of this measurement:** the ten entries whose SC-11 grading was inherited via
byte-identity proof only up to `48bbe7e` (DEC-11, 138, 142, 149, 152, 158, 171, 174, 189, 194) —
never independently re-checked across `48bbe7e..635cd3ba`, the interval both T-27 and T-28 edit.

### Method

For each of `48bbe7e` and `635cd3ba`, pulled `.harness/harness/docs/DECISIONS.md` via `git show
<sha>:<path>` and split it in Python on `^## DEC-\d+` headings into heading-to-next-heading spans
(anchored on the heading text, never a line number — both T-27 and T-28 shorten the file, so line
numbers do not correspond across the two SHAs). Compared each of the ten named spans for exact
string equality between the two SHAs, then separately computed the full set of `DEC-NNN` ids whose
span differs at all between the two SHAs, over the complete heading set (188 headings present on
both sides — no entries added or removed in this interval).

### Per-entry byte-identity result — the ten

| DEC | 48bbe7e → 635cd3ba |
|---|---|
| DEC-11 | IDENTICAL |
| DEC-138 | IDENTICAL |
| DEC-142 | IDENTICAL |
| DEC-149 | IDENTICAL |
| DEC-152 | IDENTICAL |
| DEC-158 | IDENTICAL |
| DEC-171 | IDENTICAL |
| DEC-174 | IDENTICAL |
| DEC-189 | IDENTICAL |
| DEC-194 | IDENTICAL |

**Result: 10/10 byte-identical.** None of the ten entries whose SC-11 grading was carried forward
past `48bbe7e` moved again before `635cd3ba`. No stale grading among them; no real SC-11 read-back
against `7ebfc9e` is required for any of the ten (step 3 of the assignment is vacuous — nothing
triggered it).

### Full blast radius — every entry whose span changed at all, `48bbe7e..635cd3ba`

Computed directly from the heading split (not from a file-global `git diff`, which cannot localize
to individual entries): `['DEC-145', 'DEC-157', 'DEC-181', 'DEC-183', 'DEC-193', 'DEC-205']` — six
entries, all six from the expected T-27 marker-strip set (DEC-205 touched by both T-27 and T-28,
counted once). Cross-checked against `git diff --stat 48bbe7e 635cd3ba --
.harness/harness/docs/DECISIONS.md`: single file, `4 insertions, 31 deletions` — consistent with a
pure marker-line removal across six entries, no other file in the diff.

**The changed set does NOT exceed the expected T-27/T-28 set.** No finding beyond what was already
anticipated: exactly the six marker-strip entries, nothing else. DEC-205's own SC-11-vs-SC-16
scoping question is out of scope for this measurement (Part 1 already excluded it per corrected
scope) and is unaffected by this result either way.

### Bottom line

**SC-11's 15/15 coverage is sound at `review_sha` (`635cd3ba`).** All ten inherited entries are
byte-identical to their `48bbe7e` form (proven in Python here, not by trust), and the only entries
that moved in the interval are exactly the five already re-graded in Part 1 plus DEC-205, whose
coverage question belongs to SC-16, not SC-11. No entry's SC-11 grading is stale. Zero named
entries require rework.
