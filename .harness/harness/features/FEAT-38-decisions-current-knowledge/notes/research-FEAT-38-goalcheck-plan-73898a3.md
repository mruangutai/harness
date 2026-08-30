# Goal-check — FEAT-38 signed plan vs. the operator's stated goal — pin 73898a3

> Dispatch named `notes/goalcheck-plan-73898a3.md`. `check-domain.sh` denied it — `harness-pm` owns
> `notes/research-*.md`, not `notes/goalcheck-*.md`. Written here instead (harness-handoff, #216).

**VERDICT: PARTLY SERVES.** The operator's stated goal is **already fully discharged by landed
work at the pin**, with a standing regression guard. Four of the five remaining tasks contribute
nothing to that goal but are **mandatory** — they remove an execution surface this feature itself
introduced and that is live at the pin. The fifth, **T-29 / SC-17, is a second mission** and is the
one thing here that should leave FEAT-38.

Recommendation: proceed with T-24, T-25, T-27, T-28. Move T-29 and SC-17 out of the feature.
Correct one arithmetic error in the signature line before validate runs.

All measurements below are at base `7ebfc9e` (merge-base with `main`) → pin `73898a3`, via
`git show <sha>:.harness/harness/docs/DECISIONS.md`.

## Q1 — the goal is already met. Numbers.

| Measure | command | 7ebfc9e | 73898a3 |
|---|---|---|---|
| amendment headings | `grep -cE '^###\s+DEC-[0-9]+\s+amendment'` | 25 | **0** |
| bold amendment blocks | `grep -cE '^\*\*Amendment'` | 13 | **0** |
| `am.N` tokens | `grep -coE 'am\.[0-9]+'` | 18 | **0** |
| struck-in-place entries | `grep -cE '^## DEC-[0-9]+ .*STRUCK'` | 8 | **1** (DEC-90, the recorded exception) |
| superseded entries present | per-id `grep -cE '^## DEC-<id> '` over the 15 | 15 | **0** |
| `SUPERSEDED BY` index rows | `grep -cE 'SUPERSEDED BY' DECISIONS-INDEX.md` | — | **0** |
| near-duplicate entry titles | Jaccard >= 0.40 over content words, all pairs | **5** | **0** |
| entries / lines | `grep -cE '^## DEC-'` / `wc -l` | 202 / 7414 | 188 / 6299 |

The five near-duplicate title pairs at base were exactly the struck pairs the feature deleted:
DEC-103/104, DEC-137/140, DEC-186/192, DEC-186/196, DEC-192/196 — all Jaccard 1.0.

Durable half also landed: `test_no_amendment_construct_survives_in_the_authority`
(`test-gen-decisions-index.py:829`), and all seven generator machinery symbols return 0 at the pin
(`AMEND_HEADING_RE`, `AMEND_BOLD_RE`, `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE`,
`compute_amendments`, `format_amendment_span`, `compute_supersession_target`).

**Correction to the shared contract:** T-01..T-23 are not "mostly" done — **all 23 carry
`status: done`**; the only `pending` statuses in `plan.yaml` are the five new tasks
(plan.yaml:1805, 1910, 1961, 2017, 2126).

**But "risk without product" is the wrong frame for four of the five.** At the pin,
`check-decision-claims.py` and `test-check-decision-claims.py` are still tracked
(`git ls-tree -r 73898a3 -- .claude/skills/harness/bin`) and all 11 markers are still live
(`grep -c '<!-- claim:'` = 11). Not shipping T-24/25/27/28 merges the execution surface. They are
self-remediation, not product — and not optional.

## Q2 — yes, a second mission, and it is bounded to one task

- **In scope by the "do not merge a defect you created" rule:** T-24, T-25, T-27, T-28 and
  SC-14/15/16. Every one of them removes something T-20/T-21 added inside this same plan.
- **A different mission:** **T-29 / SC-17 / REQ-10's class clause.** It audits scripts this feature
  never touched — `git grep -lE 'subprocess|shlex|shell=|Popen|os\.system|eval\('
  -- .claude/skills/harness/bin` returns **72** at the pin, **70** after T-24's two deletions —
  **explicitly forbids remediating anything it finds** (plan.yaml:2190-2192 / BRIEF.md:190-192), and
  delivers a note that becomes a backlog row.

**Concrete cost, high:** SC-17 is a ship gate, so a 70-row per-file judgement table sits on the path
*between* T-24 (the execution surface is deleted) and merge. The branch holding that surface stays
unmerged while read-only work this feature is barred from acting on is written. Budget at the pin is
`cycles_used: 14` of 30 and 24 runs against an informational 20 (`feature.json`).

The requirement text concedes the point itself: REQ-10 states a non-empty result is *"a finding this
feature delivers, not a failure of it"* (BRIEF.md:192). A requirement whose outcome cannot fail the
feature is not a requirement of this feature.

## Q3 — SC-14..SC-18: three earn their keep, one is droppable, one was green before the work

- **SC-14 — keep.** Its third clause (`git grep -l check-decision-claims` with the three dated-record
  pathspecs excluded) is the *only* thing in the plan proving no sixth reference site exists.
  Measured at the pin: exactly 5 tracked files, matching the recorded blast radius.
- **SC-15 — keep.** Not a restatement. `run-unit-tests.sh` exits 2 when its `INTEGRATION_SCRIPTS`
  array and `harness.json`'s `integration` detect disagree, and a one-sided deregistration is
  invisible to a single-file absence search.
- **SC-16 — keep; the only one of the five that serves the stated goal.** Without it the feature
  ships `DECISIONS.md:6240` heading *"two mechanical checks guard it"* and `:6272` *"Two mechanical
  checks guard this file, and only two"* with one check left — precisely the stale-truth defect
  FEAT-38 exists to remove. It asserts the corrected counts **positively**, so deleting a count
  sentence does not satisfy it.
- **SC-17 — DROPPABLE.** Nothing that ships depends on it; the one criterion whose failure changes
  nothing about the product. Move it with T-29.
- **SC-18 — keep, but record that it never had a failing state.** Measured: the anchor checker and
  its test are byte-identical between `99bb52c` and the pin (blobs `bc072f7` / `34f19b8`). Green
  before the work; it can only redden if a doer edits a file no task names. Non-discriminating by
  P-01 — kept only because it is two commands and adjacent-filename over-deletion is the likely error.

So the 13 -> 18 growth is not bloat: 3 of 5 additions carry real, distinct failure modes.

## Q4 — the SC-11 / SC-13 ruling holds for T-27, but its count is wrong

**T-27 cannot touch prose, verified at source.** All 11 markers sit on their own line, blank-line
delimited *between* paragraphs — checked line-by-line at `DECISIONS.md:3229, 3582, 4775, 4776, 4782,
4912, 4933, 4977, 5310, 6290, 6291`. Deleting the 11 lines plus a collapsed blank touches zero prose
characters. **SC-13's condition is not tripped; the operator's ruling stands and needs no reopening
on that point.**

The ruling is load-bearing rather than ceremonial: T-27's verify guards only that the six
`## DEC-NNN` headings survive (plan.yaml:1970-1972). A documentor who deletes a marker *and the
paragraph above it* passes T-27's verify. The SC-11 re-run is the only thing that catches it.

**DEFECT, med — the signature line's count is wrong.** BRIEF.md:389 reads *"SC-11 re-runs at
validate over the six entries T-27 touches."* T-27's six are DEC-145, 157, 181, 183, 193 and
**DEC-205**. SC-11's own set (BRIEF.md:277-279) is DEC-11, 138, 142, 145, 149, 152, 157, 158, 171,
174, 183, 189, 193, 194, 181 — **DEC-205 is not in it.** DEC-205 was authored by this feature (id-diff
7ebfc9e -> 73898a3: added = `[DEC-205]` only), so it has no pre-fold form and
`git show <base_sha>:` yields nothing to cite. SC-11 can re-run over **five** of the six.

Consequence, a real gap rather than a wording nit: the prose beside DEC-205's two markers is
`DECISIONS.md:6293-6299`, the M3/M4 considered-and-refused paragraph. SC-11 does not reach it, and
SC-16 asserts only the three count sentences, rule 1 unchanged, and the absence of a second numbered
item — none of which guards that paragraph. It is the one prose block in T-27's blast radius with no
read-back. T-28 also rewrites its last sentence, which is why nobody noticed. **Tell the operator
before validate looks for a DEC-205 read-back that cannot be produced.**

## Two low findings

- **`traces:` carries SC ids.** T-24 `[REQ-10, SC-14]`, T-28 `[REQ-05, REQ-10, SC-16]`, T-29
  `[REQ-10, SC-17]` (plan.yaml:1800, 2012, 2121). `traces:` is the REQ link; the intents say *"the
  grader looks for the id here"*. Any REQ-coverage count derived from `traces:` must now filter SC
  ids, and a tool treating the field as a REQ set reports REQ ids that do not exist.
- **T-28's region anchor is unbounded.** `sed -n '/^## DEC-205 /,/^## DEC-206 /p'` (plan.yaml:2025) —
  zero `## DEC-206` headings exist at the pin, so the region runs to EOF. Correct only because
  DEC-205 is the last entry (starts 6240, file ends 6299). Any entry appended after it before T-28
  runs joins the region, and the `^2\. ` negative clause would then fire on that entry's list. No
  task in this plan adds one.

## Observation, not a finding

The sole new decision this feature contributes to `DECISIONS.md` is DEC-205, and T-28 rewrites its
heading, its enumeration intro and its closing paragraph and deletes one of its two numbered items —
the exact shape the feature exists to abolish. It costs a reader nothing **because it happens
pre-merge on an unmerged branch**: `main`'s history will show one coherent entry. Recorded so nobody
mistakes it for a live back-and-forth.

## Checked and clean

- No surface outside `DECISIONS.md`, the two deleted files and the DEC-205 index row asserts the
  claim mechanism: `git grep -niE 'two mechanical check|executable claim|claim marker|claim:.*::'
  73898a3 -- . ':!.harness/harness/features' ':!.harness/notes' ':!.harness/logs'` returns only those.
  No unowned stale-truth site exists.
- T-29's note is not line-budgeted. `check-domain.sh` budgets `notes/handoff-*.md` only
  (check-domain.sh:924, 1035); a 70-row table in `notes/research-*.md` is permitted.
- T-27's positive control is sound: `git show 48bbe7e:...DECISIONS.md | grep -c '<!-- claim:'` = 11.
- T-29's count floor of 60 survives T-24: candidates drop 72 -> 70.

## Open questions for the operator

- Q1 (blocks the ship gate, not the build): move T-29 and SC-17 to their own backlog row so the
  execution-surface removal can merge on SC-14/15/16 alone?
- Q2 (blocks validate): BRIEF.md:389 says SC-11 re-runs over six entries; it reaches five. Accept
  DEC-205's marker-adjacent paragraph (`DECISIONS.md:6293-6299`) as ungraded, or extend SC-16?
