# Review — FEAT-40, implemented code at pinned SHA 3a548fe (Mode B) — harness-ui-reviewer

## Correction notice

This supersedes the prior version of this artifact, which graded DESIGN.md as a pre-build contract
(Mode A) at base commit `cc84b29` and filed a `must_fix` claiming `plan.yaml` had no task touching
`post-merge-sweep.sh` and DESIGN.md permitted shipping the terminal write with no downstream gate.
**That claim is refuted at the pinned SHA, verified directly:**

- `plan.yaml:324` lists `.claude/skills/harness/bin/post-merge-sweep.sh` in T-04's `files:` block;
  `plan.yaml:430` is step 7b, "TEACH THE SWEEP TO READ THE FAILED LINE"; `plan.yaml:332`'s verify
  greps `grep -q 'gh-sync: FAILED' .claude/skills/harness/bin/post-merge-sweep.sh`.
- `post-merge-sweep.sh:206` (pinned SHA): `if "gh-sync: FAILED" in combined:` declines the worktree
  removal and prints the reason. The machine reader Q1 asked for exists and is wired.

The prior `must_fix` is withdrawn. This is a re-grade in Mode B against the implemented strings.

## BLUF

**PASS.** Contract 2's per-card and batch-summary literals are byte-exact against DESIGN.md,
including the em dash (verified via `xxd`, U+2014 in both). Contract 4's refusal text is
character-identical, used verbatim for both denial sites, and its `abandon` command line is
runnable (the interpreter, path, feature-dir placeholder, `--reason-file`, and `--yes` all resolve
against real `argv` handling in `gh-sync.py`). One real, non-gating finding: the new board-audit
`ERROR - ` line at `gh-sync.py:1321` falls outside DESIGN.md Contract 1's stated taxonomy for that
token — a documentation-precision gap, not an operator-facing hazard, because no downstream reader
greps `ERROR - ` and the pattern already existed pre-feature for non-write read failures.

## Self-scope

IN. Batch CLI text surface, explicitly handed down by the dispatch (`gh-sync.py`, `gh-close-gate.sh`),
consistent with this repo's established scope (repository Expertise P-01): no rendered UI, the
markdown/CLI-message surface is what this role audits here.

## Findings, against the pinned SHA (`git show 3a548fe...:<path>`)

### 1. Contract 2 literals — byte-exact

- Per-card HELD (`gh-sync.py:1277`, built from `gh-sync.py:1254-1258`) vs DESIGN.md:62:
  `gh-sync: HELD — #{num} waiting on open child #{kid} ({note})`. `note` is `"not on the board"`
  (verified verbatim in `gh_board.py:167`) or `f"not at {done}"` where `done = board["stations"]["done"]`
  — the FEAT-33-established convention capitalizes station names (`stations["plan"] == "Plan"`
  precedent, `plan.yaml:178` FEAT-33), so `not at Done` matches DESIGN.md:62 in form; not re-verified
  against a live `harness.json` at this SHA, flagged as inference from convention, not a literal read.
- Batch summary (`gh-sync.py:1286,1289`) vs DESIGN.md:72-73:
  `gh-sync: HELD {n} of {total} — {pairs}` and `gh-sync: FAILED {n} of {total} — {names} did not
  reach Done and nothing downstream reports it`. **Byte-level diff of the em dash**: both DESIGN.md
  and `gh-sync.py` encode `e2 80 94` (U+2014), confirmed via `xxd`, not a double-hyphen or en-dash
  substitute.
- `(not at Done)` vs `(not on the board)` — both parentheticals reproduced verbatim; ternary at
  `gh-sync.py:1257`.

### 2. Batch-summary stream — resolved, non-gating doc gap remains

Measured: `gh-sync.py:1286` and `:1289` are both plain `print(...)` — stdout, no `file=sys.stderr`.
This matches the per-card HELD line's stated stream (DESIGN.md:59, "printed on stdout") and every
other non-`ERROR -` shape in Contract 1's table. **DESIGN.md itself never states a stream for the
two new batch-summary lines** (Contract 1 pins a stream for `SKIP`/`REFUSED`/`ERROR -`/bare, but
Contract 2's summary block, DESIGN.md:68-84, states no stream at all). The implementation is
internally consistent with the rest of the taxonomy, so this is not a shipped defect — it is a
completeness gap in the contract text, unchanged from my prior advisory note, now confirmed
resolved-by-implementation rather than merely inferable. `low`, non-gating.

### 3. Contract 4 refusal text — character-identical, one text, runnable

`gh-close-gate.sh:49-56` (`REASON` heredoc) reproduces DESIGN.md's quoted block
(DESIGN.md:134-140) verbatim, line for line, including "do nothing here", the em dash, and the
untracked-issue closing sentence. **One text used for both denials**: both call sites (`:73` for
`gh issue close`, `:81` for `gh api ... state=closed`) call `deny "$REASON"` — the same variable,
confirmed by direct read, not by the file's own comment claiming it (`gh-close-gate.sh:47-48`
narrates "ONE refusal text... used verbatim for BOTH denials"; the code at `:72-82` bears it out).
The printed `abandon` command —
`python3 .claude/skills/harness/bin/gh-sync.py abandon <feature-dir> --reason-file <path> --yes` —
is runnable as printed once `<feature-dir>` and `<path>` are substituted: `gh-sync.py:1357-1362`
parses `--reason-file` by name-search, `:1392-1393` parses `--yes`, `:1451` wires both into
`cmd_abandon`.

### 4. Operator legibility across healthy / HELD / FAILED

Distinguishable by literal, confirmed at the pinned SHA (`gh-sync.py:1282-1291`): three mutually
exclusive prefixes — `gh-sync: every recorded card is at Done` (only when neither `held` nor
`failed` is non-empty), `gh-sync: HELD n of m — ...` (whenever anything is held, independent of
`failed`), `gh-sync: FAILED n of m — ...` (only when something failed). The `if held:` / `if
failed:` blocks are independent, not `elif`, so a mixed run correctly prints both lines rather than
picking one — matching DESIGN.md's own table row ("the HELD line is printed whenever anything is
held, even if nothing failed"). All `gh-sync:`-prefixed lines are distinguishable from
`post-merge-sweep:`-prefixed lines and from git's own merge output by that fixed prefix. No
ambiguity found in source; this is a source-level read of distinct string literals and control
flow, not a rendered-terminal check — genuinely low-risk here since the discriminator is a grep-able
prefix, not layout or color.

### 5. `ERROR - ` taxonomy overload — real, non-gating

DESIGN.md's Contract 1 table (DESIGN.md:46) pins `ERROR - ` (hyphen), stderr, to "one card's write
failed, run continues," citing `:245, :838, :941, :953, :959` as precedent. The module's own
docstring (`gh-sync.py:53-55`, pre-existing) defines it more precisely as "a failure of a STATION
WRITE while gh itself works." The new `_ship_audit` function — confirmed new in this feature's diff
(`git diff cc84b29..3a548fe -- gh-sync.py`, hunk at old-file line 597-612) — prints
`gh-sync: ERROR - the board audit could not run: {e}` at `gh-sync.py:1321` for a **read** failure of
the post-hoc audit, which its own adjacent comment (`gh-sync.py:1317-1319`) explicitly says "is not
a failed write." This does not match DESIGN.md's stated definition of the token.

**Judgment: real but non-gating.** Two mitigants, both measured, not assumed:
- No downstream machine reader greps `ERROR - `. `post-merge-sweep.sh`'s gate (the only consumer
  checked in this review) greps only `gh-sync: SKIP` and `gh-sync: FAILED` (`post-merge-sweep.sh:192,
  206`) — the audit's `ERROR - ` line cannot trip worktree-removal behavior.
- The token was already broader than DESIGN.md's narrow table description before this feature: other
  pre-existing `ERROR - ` lines (`gh-sync.py:856` guard-read failure, `:1208` board-read failure,
  `:1265` "not evaluated, the board read failed", `:1272` "child list unreadable") are also not
  literally station-write failures. DESIGN.md's Contract 1 table was already an incomplete
  characterization of an established, broader convention; the new audit line extends an existing
  pattern rather than introducing a new deviation.

DESIGN.md never mentions the board audit at all (`grep -i audit DESIGN.md` — zero hits), so this is
scoped as a documentation gap in Contract 1's completeness, not a code deviation from an explicit
rule. `medium`, non-gating — worth tightening DESIGN.md's taxonomy row to "at least one write or
read this run failed to complete" if the contract is meant to be exhaustive, but it does not mislead
any measured consumer today.

## Accessibility / theme parity

Not applicable — batch CLI stderr/stdout text, no rendered surface, no colour-only state encoding.
Stated explicitly per this role's own gotcha (G-02) rather than left as a silent omission.

## Open questions

None blocking. The doc-completeness gaps in findings 2 and 5 are candidates for a DESIGN.md
follow-up edit but do not gate this implementation review.

## Verdict

PASS. `severity_max: medium` (finding 5, non-gating). No `must_fix`. The prior FAIL/must_fix is
withdrawn as refuted by direct measurement at the pinned SHA.
