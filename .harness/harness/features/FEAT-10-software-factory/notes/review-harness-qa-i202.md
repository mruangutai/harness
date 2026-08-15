# QA review — issue #202, SHA 835b2976 (base c4fea5d)

## BLUF

**FAIL. The ticket's own change list is not fully executed: DEC-165's required passage strike
never happened, and the passage it left standing is now demonstrably false.** The five
commit-message claims are separately all VERIFIED as literally stated (see Part A) — the suite is
green and the four listed decisions were struck correctly. That is not the same thing as the
change being complete; Finding 1 is a genuine gap against the ticket's own table, not against the
five claims. Two secondary, non-blocking findings: M2/M3 mutants show the automated unit suite has
zero test that diffs the committed `DECISIONS-INDEX.md` against a fresh regeneration (pre-existing,
not introduced by this diff); Part C's residual `ok-stale` emitter is confirmed a live revival
vector — a planted marker propagates through regeneration and no gate objects.

## Part A — the five claims

**1. `check-state.sh` reports no INV-10 — VERIFIED.**
Ran `.claude/skills/harness/bin/check-state.sh`. Exit 1, with 3 VIOLATION lines, all under
`FEAT-11-graphql-field-resolve/` and `FEAT-12-end-copy-distribution/` (unrelated in-flight flows,
matching the expected caveat exactly). `grep -i "INV-10\|check-docs"` over the full output: zero
matches. No error invoking the deleted `check-docs.sh`.

**2. `run-unit-tests.sh` — 97/97, every suite PASS — VERIFIED, with one clarification.**
Exit 0, zero `FAIL` lines. **"97/97" is `test-factory-integration.py`'s own internal check count**
(its last line reads `97/97 checks passed.`), not a grand total across all 22 suites — the runner
itself never emits an aggregate total. Confirmed this is not a fresh coincidence:
`git log -S"97/97"` shows the same number pre-dates this diff (test-factory-integration.py's check
count is stable). "Every suite PASS": confirmed 22 suites registered
(`diff <(ls .claude/skills/harness/bin/test-*.py | xargs -n1 basename | sort) <(python3 -c '...'
parse `UNIT_SCRIPTS`+`INTEGRATION_SCRIPTS` from the script text)` — empty diff, exit 0), and each
one's own `PASS <script>` line present with none missing and no `FAIL` anywhere in the transcript —
no vanished suite, no unlisted stray. `test-check-docs.py` does not exist and is not referenced
anywhere in the runner.

**3. `gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md` — VERIFIED.**
Ran literally. Exit 0, empty stderr, empty diff.

**4. Zero stale markers — VERIFIED for the propagation-relevant scope.**
`git grep -c -- '<!-- stale' 835b297`: 11 hits, all under `.harness/features/**` or
`.harness/logs/**` — historical artifacts and daily logs, not live scan-root docs (per the ticket's
"leave alone" carve-out). Zero hits in `docs/harness/DECISIONS.md`, `SPEC.md`, `BUILD.md`,
`CLAUDE.md`, or any `.claude/skills/**`.
`git grep -c -- 'ok-stale' 835b297`: hits split into (a) `.harness/features/**` and
`.harness/logs/**` artifacts (leave alone, per ticket), (b) narrative prose in
`docs/harness/DECISIONS.md:1568,3099` and in `test-bash-write-guard.py`/`test-render-brief.py`
using the string as unrelated test fixture data — not functional markers, and (c) the one live,
intentional residual the ticket names in Part C: `gen-decisions-index.py:340` (the emitter) and its
test `test-gen-decisions-index.py` (6 hits, its own test file). No actual `<!-- ok-stale -->`
marker syntax remains in `SPEC.md`, `BUILD.md`, `.claude/skills/harness/SKILL.md`, or
`harness-handoff/SKILL.md` — confirmed via direct grep for the marker syntax, zero hits in all
four.

**5. `CLAUDE.md` within budget — VERIFIED.** `wc -l CLAUDE.md` = 73. Budget enforced independently
of the deleted `check-docs.sh`, at `check-domain.sh:779-780` (`if len(lines) > 80: ... budget is 80
(DEC-181)`), under DEC-181's surviving budget half. Matches the commit's "73 of 80 lines" and
confirms DEC-181 was correctly struck IN PART (not whole) — its entry at DECISIONS.md:5096
explicitly records the budget half as standing and cites the same `check-domain.sh:779-780` line.

## Additional checks run before the verdict (beyond the five claims)

- **`check-state.sh`'s INV-10 removal hunk, read directly** (DEC-169 presence-beside-absence):
  `git diff c4fea5d..835b297 -- .claude/skills/harness/bin/check-state.sh` shows the entire ~28-line
  INV-10 block (the `docs`/`check-docs.sh` subprocess call and its three `bad.append` branches)
  replaced with a comment explaining the retirement. Nothing adjacent was removed with it.
- **`check-docs` repo-wide** (`git grep -n -- 'check-docs' 835b297`): every remaining hit is either
  the retirement comment in `check-state.sh`, an index row/refs-graph entry for the struck DEC-103,
  or historical narrative inside `DECISIONS.md`'s own entries (DEC-108's incident record, DEC-181's
  history, etc.) — none of it is a live instruction to run a binary that no longer exists.
- **`DEC-103`/`DEC-104` repo-wide** (`git grep -n -- 'DEC-103\|DEC-104' 835b297 -- .claude docs`):
  every hit outside `DECISIONS.md`/`DECISIONS-INDEX.md` themselves is `test-gen-decisions-index.py`'s
  own comment explaining why a fixture changed, and `docs/harness/SPEC.md:45`, which the diff
  correctly re-annotated — `"(The ruling came from DEC-104, since struck on other grounds under
  DEC-188; this half of it was never what was contradicted.)"` — exactly the provenance correction
  the commit message describes, not a dangling live citation.

## Finding 1 — DEC-165's required passage strike was never executed [BLOCKING]

**Failure scenario: a future agent or human reads DEC-165 at DECISIONS.md:4142-4144, still reading
"fits one conversation → `/harness-grilling`", and either re-adds `/harness-grill.md` believing it
is restoring a documented interface, or cites the passage as current truth in a digest or a
BRIEF — exactly the falsified-statement-survives-an-audit-free-stretch failure mode DEC-103 exists
to warn about, now with the one detector that used to catch it deleted.**

The ticket's "Decisions to strike" table (issue #202) is explicit: *"DEC-165 — Created wayfinding —
Strike the contradicted passage ONLY — `DECISIONS.md:4222-4226`, the 'entry test keeps the two
doors honest' paragraph."* That paragraph is still live, word for word, at DECISIONS.md:4142-4144
(line numbers shifted because earlier struck entries shortened the file, but the text is
untouched):

> The entry test keeps the two doors honest: fits one conversation → `/harness-grilling`; the
> destination itself is fuzzy or decisions wait on facts and prototypes → `/harness-wayfinding`...

Verified this is genuinely false under current state: `.claude/commands/` no longer contains
`harness-wayfind.md` or `harness-grill.md` (confirmed by `ls`), and
`.claude/skills/harness-grilling/SKILL.md:3` declares `user-invocable: false` — `/harness-grilling`
is not a live entry point the way the passage claims. `git diff c4fea5d..835b297 -- docs/harness/DECISIONS.md | grep "DEC-165"` shows zero touch to this entry in the whole diff — only two
unrelated mentions of DEC-165 inside DEC-188's own new prose.

This is the exact class of defect DEC-188/DEC-103 exist to prevent, present in the same commit that
records the new no-mechanical-check trade-off. Not a re-litigation of the ruling — a completeness
gap in executing it. Belongs to a dev to fix (add the strike), not to QA.

## Part B — mutant testing on `test_row_per_distinct_dec_matches_authority`

Baseline confirmed GREEN in a disposable worktree at 835b297 (`git worktree add`), all mutants
applied and reverted there; main checkout untouched throughout (`git status --porcelain` clean
before/after — confirmed).

- **M1a (plant only)** — inserted a fenced ``` `## DEC-999 — synthetic` ``` block inside DEC-188's
  body in `docs/harness/DECISIONS.md`. Test stayed **GREEN**. Expected: correct code should ignore
  a fenced heading, so this alone does not discriminate — consistent with the ticket's own
  prediction.
- **M1b (plant + generator mutation)** — with the plant still in place, disabled the fence toggle
  in `gen-decisions-index.py`'s `defenced_lines()` (`infence = not infence` → `continue`, a no-op).
  Test went **RED**: `expected 187 rows (distinct DEC count), got 188`. **The rewritten test does
  discriminate a real fence-skip regression**, when combined with a live plant. The test's own
  built-in synthetic fixture (`DEC-9999` planted inside the test function itself) independently
  proves the same guard in isolation, without needing a plant in the real file at all — this is
  the mechanism the commit message describes as "stronger, because it fails when the guard breaks
  rather than when someone edits an unrelated decision," and that claim held up under the mutant.
  **Verdict: not weaker on this specific dimension. Arguably better isolated than the old
  frozen-count fixture.**
- **M2 (delete a row from the committed `DECISIONS-INDEX.md`)** — deleted the `DEC-01` row. Ran
  the full suite: `test_row_per_distinct_dec_matches_authority` and
  `test_committed_index_is_complete_and_within_budget` both stayed **GREEN**. Neither test compares
  the committed index's row set against a fresh regeneration; the row-count test only regenerates
  into a fresh tmp dir and compares against `distinct` computed from `DECISIONS.md`, never against
  the file on disk at `REAL_INDEX`.
- **M3 (spurious row for a nonexistent DEC-9998)** — added an orphan row to the committed index.
  Ran the full suite: stayed **GREEN**, including `test_orphaned_ruling_is_reported_not_silently_
  dropped` (which only exercises orphan detection against a synthetic tmp fixture, never the real
  file).

**M2/M3 verdict: this IS a real gap in the automated suite — a missing or spurious row in the
committed index is currently invisible to `run-unit-tests.sh`.** But it is **pre-existing, not
introduced by this diff**: I pulled the pre-change test at `c4fea5d` and it had exactly the same
shape — regenerate into tmp, compare row *count* to `distinct`, never diff against `REAL_INDEX`
content. The manual command in claim 3
(`gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md`) *does* catch both:
confirmed live — running the real generator against my M3-mutated worktree produced
`ORPHAN: DEC-9998 ... has a ruling in the index but no live heading` on stderr, exit 1. So the gap
is real but only in the *automated, unattended* suite; a human running the documented manual
command would catch it. Flagging as `coverage_gaps` per O-01 (visibility costs nothing) — not a
regression to gate on.

All worktrees created for these probes were removed after use; `git status --porcelain` on the
main checkout confirmed clean before and after every mutant.

## Part C — the residual `<!-- ok-stale -->` emitter (real revival vector, confirmed live)

Planted `<!-- ok-stale -->` on `DEC-01`'s row in `DECISIONS-INDEX.md` in a disposable worktree.

- `gen-decisions-index.py --stdout` **faithfully propagated** the marker into the regenerated row.
- `check-state.sh` run against the mutated tree: **silent** — no mention of `ok-stale` or `DEC-01`
  anywhere in its output.
- Full unit suite (`test-gen-decisions-index.py` and the rest): **zero FAIL lines** — nothing
  objects to a live, functionally meaningless `ok-stale` marker.

**Confirmed, not opinion: this is a real revival vector.** With `check-docs.sh` deleted, nothing in
the current gate set would ever flag a future author writing `<!-- ok-stale -->` into a decision —
the generator preserves it silently forever, and every gate that ran (check-state.sh, the full
unit suite) stayed green. This matches Part C's framing exactly: not "dead code that should have
gone," but a mechanism that still fires and whose output nothing checks the meaning of.

## SC evidence

No BRIEF/SC exists for this ticket (`.harness/features/FEAT-10-software-factory` does not own
issue #202 — the ticket explicitly names no feature dir; per the dispatch, this note lives under
FEAT-10's notes/ by exception). Evidence is the direct command verification above, not an SC table.

## Coverage gaps

- `test-gen-decisions-index.py` has no test (pre-existing, not introduced here) that diffs the
  committed `DECISIONS-INDEX.md` against a fresh `gen-decisions-index.py --stdout` regeneration —
  M2/M3 both went undetected by the automated suite. Only the documented manual command catches it.
- No automated gate detects a live, meaningless `<!-- ok-stale -->` marker (Part C) — confirmed via
  a live plant that propagated silently through every gate that ran.

## Open questions

- DEC-165's required passage strike (issue #202's own table) was not executed — a dev fix, not a
  re-litigation of DEC-188's ruling.
