# Review — FEAT-40, Mode B (post-build) — harness-ui-reviewer

review_sha: 3a548fe8c3eb1905d5b1cb9936266a30bc9b7489
diff: cc84b29..3a548fe (68 files)

## BLUF

`PASS`. Zero rendered-UI file extensions across the whole diff (confirmed by census — see below),
so this is correctly a terminal-only surface, and `needs_prototype: false` holds up under challenge:
`grep -n 'input(' .claude/skills/harness/bin/*.py` at the pinned SHA returns exactly one hit, and
it is prose inside `gh-sync.py:1048`'s own docstring, not a call — DESIGN.md's "no script calls
`input()`" premise is still true, not stale. Contract 2's HELD/FAILED literals, Contract 4's gate
denial text, and Contract 5's INV-31 lines are **character-exact** against DESIGN.md, including the
U+2014 em dash (verified by codepoint, not eyeball) and the `(not at Done)` / `(not on the board)`
parenthetical logic. One real, non-blocking finding: DESIGN.md's own Contract 3 example and its
duplicate in `plan.yaml:693` are now stale against a same-diff decision (DEC-203 item 8, landed
*after* DESIGN.md was written) that the implementation correctly follows and DESIGN.md does not.

## Self-scope

IN, by dispatch instruction (P-06: an adjacent non-rendered surface named explicitly alongside a
no-UI diff is in-remit). Independently confirmed no-UI-by-default via extension census:

```
git diff --name-only cc84b29..3a548fe | grep -iE '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'
```
→ zero hits, 68 files touched, all `.py`/`.sh`/`.md`/`.json`/`.yaml`. Matches repository-tier
Expertise P-01.

## Contract 2 — `ship`'s HELD/FAILED (character-exact check)

- `gh-sync.py:1277` — `f"gh-sync: HELD — #{num} waiting on open child #{kid} ({note})"`, where
  `note` is `"not on the board"` (verbatim from `gh_board.read_station:167`) or `f"not at {done}"`
  (`gh-sync.py:1257`). Matches DESIGN.md Contract 2 and `plan.yaml:394-396` byte for byte, including
  which parenthetical fires for which of `read_station`'s two failure reasons.
- `gh-sync.py:1286,1289` — the two-line batch summary (`HELD k of n — ...` / `FAILED k of n — ...
  did not reach Done and nothing downstream reports it`) matches DESIGN.md's quoted example and
  `plan.yaml:406-407` verbatim. `FAILED` fires only when `write_done`'s `except gh_board.BoardError`
  branch appends to `failed` (`:1224`) — never for a held card, confirmed by reading both append
  sites.
- Em dash check: `python3` codepoint scan on both DESIGN.md's quoted lines and gh-sync.py's f-strings
  → `U+2014` in every instance, no en-dash/hyphen substitution.
- **Distinguishability (the dispatch's actual question):** `HELD` reads "waiting on open child
  #N" — a dependency, not a fault. `FAILED` reads "did not reach Done and nothing downstream
  reports it" — an explicit unresolved-state warning. Different token, different clause; a healthy
  run prints neither and instead the unchanged `gh-sync: every recorded card is at Done`
  (`:1291`). The taxonomy does its job.
- **Operator visibility, confirmed structurally:** `post-merge-sweep.sh:178` calls
  `_print_proc_output(ship)` (`:121-124`), which writes `ship`'s full captured stdout+stderr back
  to the sweep's own stdout unconditionally, before the gate logic runs. A `git merge` that fires
  the post-merge hook therefore surfaces every `HELD`/`FAILED` line to the operator's terminal, not
  just to the gate's internal decision.
- No ANSI colour anywhere in the four touched CLI files (`gh-sync.py`, `gh-close-gate.sh`,
  `post-merge-sweep.sh`, `check-state.sh` — grepped for escape sequences, zero real hits).
  Theme/colour-contrast is therefore **not applicable**, stated rather than silently skipped.

## Contract 3 — `abandon`'s dry run

- **Prefix and order:** every line in `_abandon_plan`'s dry-run branch (`gh-sync.py:1086-1088`) is
  printed `gh-sync: would {line}`, iterating the plan built in order comment → sub-issues (sorted)
  → milestone → parent (`:1018-1032`) — matches DESIGN.md Contract 3 item 1 and `plan.yaml`'s T-05
  ordering exactly.
- **Parent labelled as parent:** `_abandon_plan` tags the parent entry `("parent", ...)` and its
  line literally contains `close parent #{num}` (`:1032-1033`) — an operator cannot mistake it for
  one more child number.
- **One renderer, two callers — the safety-critical half holds and is machine-tested.** Both the
  dry run and the `--yes` path iterate the *same* `plan = _abandon_plan(rec)` list
  (`gh-sync.py:1086`, `:1095`), so the set and order of ticket numbers cannot drift between the two.
  `test-gh-sync.py`'s `dry_numbers == real_numbers` assertion (~line 2588) checks exactly this, by
  comparing the dry run's printed numbers against the real run's actual `gh api` call log — a
  stronger check than a text comparison would be.
- **Finding (medium, non-blocking) — "diffed by eye" is weaker than the contract's own framing.**
  The `--yes` loop explicitly discards the plan's line text: `for kind, num, _line in plan:`
  (`gh-sync.py:1095`, leading underscore = deliberately unused) and instead prints a different,
  more granular breakdown per ticket — e.g. for one sub-issue the dry run prints ONE line
  (`detach issue #N ... close it (not_planned), label it abandoned and return its card to the
  backlog`), while the real run prints THREE separately-worded lines (`detached #N from parent
  #P`, `closed issue #N (not_planned)`, `issue #N -> Backlog (abandoned, not done)`) with no
  visible confirmation of the label step at all. DESIGN.md's own rationale for this contract is
  "the drift is invisible until it destroys the wrong ticket" — the *numeric* invariant that
  actually prevents that is solid and tested, but the literal line-for-line eye-diff the design
  language promises does not exist: an operator can only verify by scanning for matching issue
  numbers across two differently-shaped transcripts, not by diffing text.
- **Finding (low-medium, non-blocking) — DESIGN.md's and plan.yaml's own Contract-3 literal has
  drifted, within this same diff, and nothing catches it.** DESIGN.md and `plan.yaml:693` both
  quote the parent "would" line as `gh-sync: would close parent #728 (not_planned) and label it
  abandoned`. The implementation prints `gh-sync: would close parent #{n} (not_planned), label it
  abandoned and return its card to the backlog` (`gh-sync.py:1032-1033`) — an added clause and a
  comma-for-"and" change. This is not a bug: `git log` on this diff shows DESIGN.md was authored in
  `00c5630`, DEC-203 (which mandates the backlog-return + detach, item 8) landed after it in
  `41f11ab`, and the implementing commit `8a96d9f` updated `gh-sync.py` and `DECISIONS.md` but not
  `DESIGN.md` or `plan.yaml`'s quoted literal. `test-gh-sync.py` only substring-checks
  ("detach", "parent #40", "not_planned", "abandoned", "backlog" individually) so the exact
  wording is unenforced and free to drift again. Not gating — the *operator-facing* text is correct
  and matches the signed authority (DEC-203); only the design contract's own illustrative quote is
  stale.
- **Confirmation is argv-only, confirmed:** grepped every non-test `.py` for `input(` — the one hit
  is prose inside a docstring (`:1048`), not a call. `--yes` is stripped by name-search before the
  positional parse (`:1388-1393`), so `abandon --yes <dir>` and `abandon <dir> --yes` both parse
  correctly — verified by reading the strip logic directly, not by trusting the docstring's claim.
- **Final "re-run with --yes" line** (`gh-sync.py:1089-1090`) matches DESIGN.md's quote verbatim,
  em dash included.

## Contract 4 — `gh-close-gate.sh` denial text

Character-exact match, confirmed by diff against DESIGN.md's quoted block — same three clauses
(do nothing if finished / run `abandon` if dropping / web UI if untracked), same wording, same
em dash. One `REASON` string used for both denial branches (`gh issue close` and the `gh api
... state=closed` shape) — verified by reading `deny "$REASON"` at both call sites.

- **Runnability, checked against the parser, not assumed:** the printed command is
  `python3 .claude/skills/harness/bin/gh-sync.py abandon <feature-dir> --reason-file <path> --yes`
  — exactly this three-flags-plus-two-positionals shape is what `main()`'s name-search stripping
  (`:1362-1393`) accepts regardless of flag position, so the command is copy-paste-correct once the
  two placeholders are filled in. Path, interpreter, subcommand and every mandatory flag are present.
- **Minor, not a finding — a UAT note per this role's stated limit on rendered output:** the
  command line is 96 characters and will visually wrap in an 80-column terminal. It contains no
  embedded newline, so this is unlikely to break copy-paste in a normal terminal, but I cannot
  observe actual rendering from source — flagging for a human/UAT check rather than asserting it
  is fine.

## Contract 5 — INV-31

`check-state.sh:1731` (git-config-unreadable, `CANNOT RUN`), `:1744` (`core.hooksPath` mismatch),
`:1753`/`:1756` (missing / non-executable `post-merge`) — two distinct subjects as DESIGN.md
requires (a misconfigured clone vs. a damaged checkout, each with its own `Fix:` clause), both
appended to `bad` (never `warn`), matching the contract's explicit, reasoned departure from INV-28's
posture. No finding.

## Accessibility

No colour-only state encoding anywhere (no colour emitted at all — N/A, not silently skipped).
Em dash (U+2014) used consistently, matching this codebase's pre-existing convention
(`ERROR — ` at `gh-sync.py:110`, Contract 1), so this feature does not introduce a new
restricted-terminal risk class, only extends an existing one. No state conveyed only by
indentation or alignment that I can find — every line is self-describing text, not columnar.

## Not reviewed / out of my lens

- Test-suite correctness (mutation coverage, fixture completeness) — QA's lens, not mine.
- Whether DEC-203's item 8 substance (backlog-not-Done, detach-before-close) is the *right* board
  behaviour — that is a signed decision; I only checked the operator-facing text against it.

## Verdict

PASS. No must_fix. `severity_max: medium` (the two Contract-3 findings above; neither is an
accessibility failure and neither misleads the operator at the terminal — both are contract-fidelity
gaps in DESIGN.md/plan.yaml's own literal quotes and in the dry-run/real-run text parity the
contract's prose promises but the code does not fully deliver).
