# Simplify pass — REUSE angle — FEAT-38 amendment (2026-08-29)

Scope: `plan.yaml` T-24..T-29 (`:1733-2091`) and `BRIEF.md` as amended. Read-only, flag-only.

## Q1 — Do T-24..T-29 duplicate T-01..T-23 or an existing checker?

**No.** Checked by `files:`/`verify:`, not titles.

- T-24/T-25 deregister; T-18/T-19 (`plan.yaml:1348-1484`) registered the same two strings.
  Opposite net state on the same two files, and T-18/T-19's own `verify:` blocks were rewritten
  in this amendment into two-sided reversal checks — the two pairs are deliberately paired
  register/deregister tasks, not duplicate work.
- T-26 deletes what T-20 (`plan.yaml:1485-1565`) built; T-20's `verify:` is likewise rewritten
  into a reversal check (`plan.yaml:1496-1504`) that already asserts non-tracked at final state —
  T-26 is what makes that assertion true, not a second implementation of it.
- T-27/T-28 remove what T-21 (`plan.yaml:1567-1641`) added; same reversal-pair shape.
- T-29 is new work with no existing counterpart (see Q3).

No existing checker under `.claude/skills/harness/bin/` performs any of T-24..T-29's checks —
confirmed against `test-check-decision-anchors.py` (retained, unrelated: fixed `git ls-files`
argv only), `test-dispatch-guard.py`, `test-post-merge-sweep.py`, `test-bash-write-guard.py`,
`test-no-distribution.py` (deploy-mechanism removal, a different feature's surface entirely —
`test-no-distribution.py:1-11`).

## Q2 — Is `git rm` reinvented in T-26's `verify:`?

**No.** T-26's `verify:` (`plan.yaml:1846-1854`) checks absence with
`git ls-files --error-unmatch` + `test -e`. That is the *same idiom* already established in this
same plan by T-20's own reversal-check `verify:` (`plan.yaml:1500-1503`), not a second
invention. No standalone "assert file deleted" utility exists under `bin/` to point to instead
(searched; none found) — the two-line idiom is the plainest available check and it is already
the plan's convention.

## Q3 — Does T-29's enumeration (`git grep -lE '...' -- .claude/skills/harness/bin`) duplicate an existing sweep?

**No.** Searched `.claude/skills/harness/bin/` for any existing bin/ auditor, argv-class sweep,
or classification tool:
- `bash-write-guard.sh` (`bash-write-guard.sh:1-42`) parses Bash *tool-call payloads* for
  in-place-editor/redirect patterns for domain enforcement — a different input class (agent
  commands, not this repo's own scripts) and a different question (write-target domain, not
  argv provenance).
- `post-merge-sweep.sh` sweeps worktrees for post-merge repair actions — unrelated concern.
- `test-no-distribution.py` sweeps for the deleted deploy mechanism — unrelated surface.
No script anywhere under `bin/` classifies call sites by FIXED-LITERAL-ARGV vs
TEXT-DERIVED-ARGV. T-29 is genuinely new.

## Q4 — Do new `verify:` blocks hand-roll checks existing scripts already perform?

**T-25 vs `run-unit-tests.sh --check-kinds`: no duplication — the two check different halves.**
`--check-kinds` (`run-unit-tests.sh:94-131` in the worktree) only cross-checks one direction:
every `INTEGRATION_SCRIPTS` name must appear in `detect` (flags `KIND-DRIFT` if absent), and
every `UNIT_SCRIPTS` name must be *absent* from `detect`. There is no rule flagging a `detect`
entry with **no** array entry — T-24's own `intent:` (`plan.yaml:1758-1770`) states this
asymmetry explicitly and uses it to justify task ordering. T-25's inline python
(`plan.yaml:1798-1809`) is exactly the check `--check-kinds` structurally cannot make: that the
removed literal string is actually gone from `detect`, not merely consistent with an
already-shrunk array. Legitimate, non-duplicative.

**T-28's index-regeneration diff vs `test-gen-decisions-index.py`: DUPLICATION — see finding
F-1 below.**

## Q5 — Does any `intent:` restate a procedure another task already owns?

**Yes, one instance — see finding F-2 below** (T-25's intent re-derives T-24's ordering
rationale, including independent line-number citations into `run-unit-tests.sh`).

## Findings

```yaml
findings:
  - id: F-1
    lines: "plan.yaml:1968-1969 (T-28 verify) vs .claude/skills/harness/bin/test-gen-decisions-index.py:332-380, assertion at 359-368"
    problem: >-
      T-28's verify ends with `python3 gen-decisions-index.py --stdout | diff -q -
      DECISIONS-INDEX.md`. This is byte-for-byte the same assertion as
      test_committed_index_matches_a_fresh_regeneration in test-gen-decisions-index.py
      (subprocess GEN --stdout compared against REAL_INDEX's content, same two files,
      same generator invocation), which is already registered in the integration suite
      (T-18/T-19 register test-gen-decisions-index.py; it is the suite referenced in
      T-24's and T-19's own intent text as running "after both documentation edits have
      landed"). The task's own verify re-implements a check the suite already re-runs on
      every subsequent integration run.
    recommendation: >-
      Backlog only — this is a plan-surface finding and the pass is flag-only here. When
      pm applies: either drop T-28's diff line and let the task rely on the already-
      registered suite test for freshness (the rest of T-28's verify already independently
      confirms the DEC-205 text edits), or, if a same-task freshness gate is wanted
      immediately rather than at suite time, note in the intent that it deliberately
      duplicates the suite's check rather than leaving it silent. Either way, two
      independent spellings of "regenerated stdout == committed index" (a shell diff here,
      a python line-list diff there) must be kept in agreement if gen-decisions-index.py's
      CLI or output framing ever changes; today only one of the two need be touched to fix
      that, and it will be easy to forget the other exists.
    severity: low
  - id: F-2
    lines: "plan.yaml:1758-1770 (T-24 intent) vs plan.yaml:1821-1831 (T-25 intent)"
    problem: >-
      Both intents independently derive and restate the same fact — that run-unit-tests.sh's
      KIND-DRIFT check is asymmetric, so T-24 must land before T-25 — each with its own
      citation into run-unit-tests.sh's line numbers. T-24 cites lines 121-130 and separately
      94-96; T-25 cites lines 121-125 for what is presented as the same rule. The two
      citations already disagree by five lines, which is the concrete symptom of the drift
      this creates: a task's `intent:` prose is never re-verified by any gate, so a citation
      here can go stale silently the next time run-unit-tests.sh is edited, and nothing
      catches the two intents diverging further.
    recommendation: >-
      Backlog only. T-25's intent could point at T-24's intent for the asymmetry rationale
      ("see T-24: the drift check is one-sided") rather than re-deriving and re-citing it
      independently. Not blocking: `depends_on: [T-24]` already enforces the real ordering
      mechanically: the prose duplication is a maintainability cost on the plan text, not a
      gap in what gets enforced.
    severity: low
```

## Verdict

PASS. Both findings are advisory (plan-surface, flag-only per the simplify skill); neither
changes behaviour, weakens a gate, or blocks the operator's signature. No writes made to
`plan.yaml` or `BRIEF.md`.
