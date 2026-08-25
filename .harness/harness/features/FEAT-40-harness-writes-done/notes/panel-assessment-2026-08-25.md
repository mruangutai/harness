# Validator panel — assessment and disposition — 2026-08-25

Panel verdict FAIL, severity critical, three `must_fix` and six open questions. Every finding was
**re-measured in this worktree before being acted on**; the panel's own numbers were not taken on
trust. One finding it did not report was found while checking its SC-05 claim, and is the more
serious of the two.

## Fixed

### F-01 — the close gate was bypassed by ordinary shell forms (critical, CONFIRMED)

Reproduced against the pinned SHA. Ten of eleven probe forms reached `gh issue close` straight
through: `gh "issue" close`, `/opt/homebrew/bin/gh issue close`, `\gh issue close`, `eval "..."`,
`bash -c '...'`, `x=$(gh issue close 5)`, `$(echo gh) issue close`, `-f state="closed"`, a JSON body
on `--input -`, and the GraphQL `closeIssue` mutation. The script's own header claimed a quoted close
DENIES; it ALLOWED. A character class is not a shell lexer.

**Fixed by tokenizing rather than grepping.** The decision moved into `gh-close-gate.py`: `shlex`
resolves the quoting and the backslash, `basename` resolves the path, each token is re-scanned as a
command line so `eval` and `bash -c` are read, an issue-path `gh api` with a mutating method or an
`--input` body denies without needing to see `state=closed`, and an unlexable line denies. Measured
after: **13 deny forms, 8 allow forms, one blind spot.**

The blind spot is `G=gh; $G issue close 5` and it is **asserted as a test**, so it cannot be lost or
silently closed. Catching it needs the shell's own expansion, which a `PreToolUse` hook does not
have. DEC-203 item 8 now records this: **the gate is a guardrail against habit, not a security
boundary.** What bounds the harness is structural — no harness command closes an issue but `abandon`.

Two secondary corrections came with it. The three `python3` spawns per Bash call became one, which is
a cost this hook pays ahead of EVERY Bash call in the session. And the detector lives in a file rather
than a heredoc: `python3 - <<'PY'` feeds the SCRIPT on stdin, the same stdin the hook's JSON arrives
on, so a heredoc reader finds it already consumed and allows everything. That was caught before the
first test ran, not after.

### F-02 — a card that missed Done was silent, and the sweep removed the worktree (high, CONFIRMED)

`cmd_ship`'s unreadable-child-list branch printed one stderr line and continued **without** appending
to `failed`, while the board-read branch four lines above did. So no `gh-sync: FAILED` line fired, and
`post-merge-sweep.sh` gates worktree removal on exactly three things — non-zero exit, `SKIP`, `FAILED`
— so a network blip on one child read left the ticket open, said nothing, and had its evidence swept
away with the tree.

**Fixed in one line: the miss is recorded like every other one.** No new taxonomy was needed, contrary
to the panel's note — an unreadable child list is a card that did not reach done, which is precisely
what `FAILED` already means, and the sibling branch already bucketed environmental misses there. The
test that enshrined the old behaviour (`ship UNKNOWN:` asserting no FAILED line) was retargeted to
assert the report instead. Exit 0 is unchanged and still asserted.

### F-03 — `abandon --yes` could abort mid-batch and leave a card at Done (high, CONFIRMED)

Every write went through `gh()`, which calls `skip()` — print `gh-sync: SKIP`, `sys.exit(0)` — on any
non-zero return. So a failed `--add-label` after a SUCCESSFUL close ended the run: the backlog write
never ran, and probe #860 measured that a close moves the card to the DONE station at t+0s. The
dropped ticket came to rest at Done, the exact state the operator's backlog ruling exists to prevent,
reached by the command that implements the ruling. `_record_status` never ran, and every later issue
in the batch was left untouched with no report.

**Fixed by making the loop unable to exit.** One `_close_and_reseat` helper orders the writes by what
they cost: the close is the single irreversible act so it goes first and its failure costs nothing;
the backlog write is the state CORRECTION and follows immediately; the label is cosmetic and comes
last, where its failure can cost only itself. Every call is `gh_try`. Close failures accumulate and
are reported on a `gh-sync: FAILED` line at the end.

### F-04 — `factory_decompose.py` wrote a `feature.json` the schema REJECTS (critical, not reported by the panel)

Found while checking the panel's SC-05 claim, and worse than the claim. T-05 removed `parent_origin`
from **both** blocks of `feature-schema.json`, which carries `additionalProperties: false`. It did not
remove `factory_decompose.py`'s six writes of that field. Measured:

```
WITH    parent_origin: "undeclared key 'parent_origin' at /factory"
WITHOUT parent_origin: (that problem absent)
```

So every feature.json the factory touched from the merge onward would have failed validation. The
panel saw `parent_origin` surviving in `test-gh-sync.py` and stopped there; the production writer was
two files further on.

**Fixed by removing the field and its six sites.** Nothing read it for a decision — DEC-203 item 4
made origin stop mattering — so it was dead data that broke a live gate. The tests were retargeted to
assert its ABSENCE rather than deleted, which is a stronger assertion than the one they replaced, and
the fixture that carries it on the way IN was kept deliberately: it now proves `load_factory`
normalises a legacy file rather than round-tripping it.

### F-05 — `abandon`'s backlog write had NO test (not reported by the panel)

The operator's own ruling — an abandoned card returns to the Backlog, detached from its parent — was
implemented with no board-backed test anywhere in the suite. Added: the Backlog write for both the
sub-issue and the parent, the absence of any Done write, and **the ordering asserted by position in
the call log** (close before backlog), because probe #860 measured that the reverse order is silently
overwritten by GitHub's own workflow.

## Assessed and NOT fixed, with the reasoning

**Q2 — `reconcile --apply` as a second done-station writer: not a defect.** The panel is right that it
writes the done station with no open-child check, and right that nothing binds it. But a `STATION`
finding fires only on **an issue that is already closed** (`board_lifecycle.py:137`), and probe #860
measured that closing an issue moves its card to the done station at t+0s. So a STATION fix completes
a move GitHub's own workflow already attempted and failed at; it cannot reach a board state that
workflow does not already produce. A `Done`-status STATUS finding is separately excluded from
auto-fix (`:972-975`). Recorded rather than changed.

**Q3 — nothing reads an audit finding: real, and a follow-up.** DEC-203 item 9 makes the audit's
WORKFLOW class the only reader of the Auto-close dependency, and the sweep greps only `SKIP` and
`FAILED`, which audit lines are forbidden to carry. If Auto-close is disabled, tickets stop closing
quietly. That is a new surface, not a defect in this diff, and widening the feature to build a
finding-reader would be scope the plan did not take.

**Q5 — `wayfind.py:318`'s `gh issue close`: stays out.** The BRIEF scopes it out explicitly and #846
already carries it.

**Q6 — the dispatch template named artifact paths outside members' write domains.** Both members used
their granted paths and flagged it, so nothing was lost. A template correction, not a code change.

## Success criteria, re-measured after the fixes

- **SC-07 — now TRUE.** It was false as measured (`eval "gh issue close 5"` contains the literal
  substring and was allowed). The gate fix makes it true rather than the wording being amended.
- **SC-05 — now true of production code.** `parent_origin` is gone from `factory_decompose.py`. It
  survives in `test-gh-sync.py` **by T-05's own requirement**, which asks the suite to assert the
  field's absence and therefore has to name it. The SC's literal reading and its own plan contradict
  each other; the plan is what was built.
- **SC-16's last clause — the assertion count did fall,** 18 to 15, when `close-task` was deleted and
  its behaviours were retargeted through `start-task`. The three lost are cases `start-task` cannot
  reach, not coverage that went missing. Net across this assessment the suite GAINED assertions.

Both SC readings are the operator's to amend or accept; neither blocks the merge, and neither is a
defect in the delivered behaviour.
