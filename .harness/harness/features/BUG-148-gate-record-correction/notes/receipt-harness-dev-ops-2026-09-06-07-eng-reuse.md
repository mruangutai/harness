# REUSE angle — BUG-148 gate record correction

**BLUF: REUSE: no finding.** One candidate was investigated in depth (DEC-174/STATE.md's mechanism
prose vs. `gen-decisions-index.py`'s own docstrings) and declined — the duplication is real but the
concrete cost the angle exists to catch (two spellings that must be edited in lockstep, one going
stale) does not materialize here, for reasons below. No other candidate survived the settled
exclusions.

## What I read

- Skill `harness-simplify/SKILL.md` §REUSE and §Applying-what-comes-back (full file).
- `plan.yaml` (this worktree): `decisions:` D-01 through D-05, `tasks:` T-01/T-02 `intent:` and
  `verify:` in full (lines 1-237).
- Full diff, both hunks unelided, for all three product paths
  (`git diff 41c16c7..f60d5d2 -- DECISIONS.md DECISIONS-INDEX.md STATE.md`, via `artifact://626`).
- `grep -rn 'ffbdbfa1|never a supported mode|stdout_mode|--check'` over the whole worktree —
  285+ files matched (paginated at 20); scanned the first page for anything stating the same
  mechanism outside the two corrected records. No `DEC-140` heading exists in `DECISIONS.md`
  (`grep -n 'DEC-140 '` → 0 matches; the numbering has no entry by that id, only commit-message
  `perf(#140)`/`(#140)` references).
- `.agents/skills/harness/bin/gen-decisions-index.py:1-15` (module docstring) and `:240-259`
  (`parse_argv`, its docstring and body) — read in full, not summary form.
- `BRIEF.md:9-15,39-46,55-84` — REQ-01/02/03 and SC-01/02/04/05, to see whether the mechanism
  prose is BRIEF-only spec language echoed forward (expected, not flaggable) or something else.
- `features/BUG-148-.../notes/` directory listing — confirmed no research note is itself a
  reachable authority a reader would cite from DECISIONS.md or STATE.md.

## Candidate considered and declined

**Where it looked reusable:** `gen-decisions-index.py:9-10` (module docstring) already states "There
is no `--check`... pipe the read-only mode into diff — `gen-decisions-index.py --stdout | diff -
.harness/harness/docs/DECISIONS-INDEX.md`", and `:243-248` (`parse_argv`'s docstring) already states
the historical mechanism: "Unvalidated argv used to mean every unrecognized flag... fell through to
the WRITE path (#140)... An unknown flag must therefore refuse LOUDLY rather than default to the
only branch that touches the tree." DEC-174's new sentence (`DECISIONS.md:4308-4316`) and STATE.md's
new passage (`STATE.md:14-19`) both re-derive this same fact in prose: `--check` never supported,
`ffbdbfa1` argv validation, unrecognized flag fell to the write path, a regeneration overwrites
exactly the drift a check would report.

**Why it doesn't count as a finding, against the shared-contract invariants:**
1. Both settled exclusions apply and neither is what I'm describing — settled item 3 covers
   cross-record repetition (DECISIONS.md vs. STATE.md), settled item 2 covers the `--stdout | diff`
   string specifically. My candidate is a *third* location (the script's own docstrings), so it
   survives both exclusions as a *candidate*, but fails on its own footing next:
2. **The concrete cost the angle looks for — "two spellings edited in lockstep, one goes stale" —
   doesn't apply.** `gen-decisions-index.py`'s docstrings describe *current, live* script behavior
   and will be maintained forward with the code. DEC-174 and STATE.md's passages narrate a
   *historical* event (what was true on 2026-08-03, before `ffbdbfa1`) — DEC-205 makes
   `DECISIONS.md` a current-truth record of decisions, not of code, and this entry's evidence
   sentence is inherently a frozen historical account. If the script's docstring wording changes
   again tomorrow, neither corrected passage becomes false or needs a matching edit — they are not
   two spellings of one live fact, they are one live fact (in code) and one dead-frozen fact
   (in a decision record) that happen to overlap in content once (2026-08-03).
3. **A cross-reference in place of the restatement would break the task itself.** T-01's `verify`
   (`plan.yaml:110-119`) and T-02's (`plan.yaml:177-186`) mechanically grep for the literal
   contiguous phrases `never a supported mode`, `could not prove index drift`, `ffbdbfa1` inside
   the DECISIONS.md/STATE.md text itself. A reader-facing pointer to `gen-decisions-index.py:243-248`
   instead of carrying the phrases would fail both verifies — this is forced by the plan the task
   already executed under, not a style choice open to the record.
4. `BRIEF.md`'s REQ-01/02/03 and SC-01/02/04 (lines 39-84) restate the same mechanism a third time,
   but that is a planning artifact describing what the fix must contain, read by nobody once the
   feature ships — normal spec-vs-implementation echo, not the kind of reachable-authority
   restatement REUSE flags.

No plan-surface candidate found either: T-01's verify clause (`plan.yaml:110-119`) runs the real
`tests/integration/test-gen-decisions-index.py` rather than hand-rolling an index-consistency check,
and T-02's verify (`plan.yaml:177-186`) is a grep over its own file, not a re-implementation of
T-01's. No hand-rolled constant/fixture appears in either task.

## Verdict

**REUSE: no finding.**
