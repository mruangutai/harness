# ui-reviewer — FEAT-24 — Mode B post-build — pinned SHA `14994b3`

Diff audited: `ada8e99..14994b3`. All reads are against pinned git objects
(`git show 14994b3:<path>`) plus one live probe of `gh_board.load_board` executed inside the
detached-HEAD worktree at `.claude/worktrees/review-14994b3` (the main checkout sits ahead, at
`efaddcf`, on `feat/FEAT-24-config-responsibility-split` — reads were never taken from there).

## Verdict: FAIL — one must_fix

A regression this diff itself introduces: `factory_config.load_fleet`'s top-level `board`-key
refusal now gives **stale, self-contradicting advice**.

## must_fix — stale next_step in the top-level `board` rejection

**Where:** `.claude/skills/harness/bin/factory_config.py:163-167` (unchanged text, present
already at `ada8e99`) vs. `:189-194` (new in this diff, part of T-02's `load_fleet` repo-entry
check).

- Line 165's message, for a fleet file carrying a top-level `board:` key: *"the board is
  per-repository now — move it under each repos entry as `repos[].board` in {path}"*.
- Line 191's message, new in this diff, for a `repos[<name>].board` key: *"the board is no
  longer declared in fleet.yaml — {name} declares its own board remotely, in its own
  `.harness/harness.json` under `github.board`. Remove `repos[{name}].board` from {path}"*.

At `ada8e99` line 165's advice was correct — `repos[].board` was where the board lived. This
diff's own T-02 change (line 191, confirmed added by `git log -p ada8e99..14994b3 --
factory_config.py`) makes that destination a second rejection. An operator who reads the
top-level error, follows it literally, and re-runs hits a second wall telling them the first
message's own remedy is wrong. The correct destination — the product's own `harness.json` under
`github.board` — is never named on the path an operator following line 165 actually takes.

This sits inside the exact surface this feature exists to build correctly: REQ-03's "a message
naming the file and the offending key" is checkable, but the standard this review applies is
whether the *next step* the message gives is actionable — SC-01 pins that same bar for the
sibling `repos[].board` case ("naming that key **and where the board moved to**"), and the
top-level case fails it after this diff where it did not before.

Invisible to the gate: `test-factory-config.py:184`/`:209-218` (`(8b) a leftover top-level board
key raises FleetError`) asserts only that the raise happens, never the content of `next_step` —
so nothing in the suite can see this go stale, and nothing did.

**Remedy is one line inside a file this diff already edits** — point line 165's next_step at the
product's own `harness.json` (or simply delete the now-wrong `repos[].board` clause) — no
DEC-174 carve-out, no redesign, no second review cycle required to land.

## Item 1 — gh-sync.py's `skip()`/`die()` stream: confirmed still true, not a regression

`skip()` (`gh-sync.py:79-80`) and `die()` (`:85-86`) both `print()` with no `file=sys.stderr` —
confirmed unchanged at both `ada8e99` and `14994b3` (`git show <sha>:...gh-sync.py | sed -n
'/^def skip/,/^def die/p'` identical both revisions). An operator who captures stdout separately
from stderr (a normal split: log stdout, alert on stderr) sees `die()`'s "Caller error... Visible,
exit 1" message nowhere, despite the docstring's own claim of visibility — mixed in with ordinary
progress lines instead. `board-station.py`'s parallel `out()`/`err()` split (`:55-61`) does this
correctly, so the family is inconsistent, but only on this axis and only in pre-existing code.

**Not gating.** This diff's own new failure mode — the malformed-board refusal (REQ-03's actual
target) — deliberately bypasses both `skip()` and `die()`: the new `except FleetError` block added
at `gh-sync.py`'s `main()` (confirmed in the `ada8e99..14994b3` diff) writes directly to stderr
with `print(f"gh-sync: {e}", file=sys.stderr)` and `sys.exit(2)`. No board-declaration message
rides the wrong stream. Recorded as a low-severity, non-gating note on a sibling this diff never
touched (Expertise P-11).

## Item 2 — FleetError / board-validator messages: PASS

Every `FleetError` raised by `factory_config.py`'s `validate_board`, `load_fleet`, `product_config`
and `board_for` is built through `factory_cli.body(what, value, next_step)` →
`"{what}: {value} — {next_step}"`, and every `next_step` I read names both the file (`in {path}`
or the composed `{repo}@{ref}:{path}` form) and the offending key. Spot-checked exhaustively
against `factory_config.py:62-330` — every raise site read, all consistent except the one flagged
above. `gh_board.py`'s `load_board` raise for a missing `board` key (`:75-78`, `"declare
github.board in {path}"`) matches the same grammar.

`GhError` (`factory_gh.py:37-51`) composes the same way; `file_at_ref` (`:428-460`) sets
`value = f"{repo} {path}@{ref}"`, so SC-06's "naming the repository, the path and the ref" is
satisfied at the point the message is built, not just asserted by docstring. `product_config`
(`factory_config.py:279-291`) wraps the caught `GhError` into a `FleetError` whose `next_step`
embeds `str(e)` verbatim — the composed operator-facing line is the actionable form, not a raw
`gh` dump. Confirmed by reading both functions, not by trusting either docstring (G-01).

## Item 3 — `templates/harness.json`'s `_board_note`: PASS

Read at the pin: `owner, number, station_field, and a stations mapping with exactly the five keys
backlog, ready, building, review and done... null = this project has no board and no station is
ever written. A board that is present but incomplete is a loud error naming the offending key,
never a silently disabled feature.` Every clause checked against `validate_board` and `load_board`
directly — accurate. `.harness/harness.json`'s own `github.board._note` (the harness's live
config) makes the same claims and is likewise accurate against the code that reads it.

## Item 4 — exit codes: PASS, verified end-to-end not from docstring

- `board-station.py`: `except factory_config.FleetError` → `err(str(exc)); return 2`
  (`:141-146`), and the module tail is `sys.exit(main(sys.argv[1:]))` (confirmed by reading the
  literal last line, not the EXIT CONTRACT docstring alone — a bare `main(...)` call would have
  exited 0 regardless of the return value, and did not need to be taken on trust here).
- `gh-sync.py`'s new `main()` catch: `print(..., file=sys.stderr); sys.exit(2)`.
- `factory_land.py`, `factory_claim.py`, `factory_workspace.py`, `factory_decompose.py` all route
  `FleetError`/`GhError` through `factory_cli.run(..., expected=(...))`, which exits
  `EXIT_REFUSED = 2` uniformly (`factory_cli.py:72-96`).

All five tools agree on exit 2 for this refusal class. Consistent.

## Item 5 — accessibility analogue (colour/symbol-only state): N/A, confirmed by search

Grepped `board-station.py`, `gh-sync.py`, `factory_cli.py`, `factory_config.py`, `gh_board.py` for
ANSI escapes and status glyphs (`\033`, `\x1b`, `✓ ✗ ⚠ ❌ ✅`) — zero matches. Every state is plain
text. No dimension in this diff needs eyes: there is no rendered surface at all, so this is not a
source-only blind spot (unlike a shrunk diagram) — there is nothing to render.

## Record correction, not a re-report — `gh_board.load_board`'s already-dispositioned finding

The prior finding ("`load_board` returns `None` for an absent `github` block **and for a present
block with no `board` key**") is only half right, checked empirically at the pin (temp-dir probe,
`gh_board.load_board`, 3 cells):

- `github` block absent entirely → returns `None` (confirmed).
- `github` present, `board` key absent → **raises** `FleetError` (confirmed by direct probe; this
  contradicts the prior finding's second clause). Covered by SC-04/T-02's eight-shape sweep as
  `"no board key"`, and `test-gh-sync.py:55-56`'s own comment states the raise directly: "an
  absent board key now raises FleetError from `gh_board.load_board`."
- `github.board` explicit `null` → returns `None` (D-07, correct).

So the docstring's own claim — "Every other unusable shape RAISES... the `github` block absent,
the `board` key absent" (`gh_board.py:51-52`) — is itself wrong about one of its two named cells:
`github` block absent does not raise, contradicting the docstring's own text. This is a smaller,
more precisely-scoped gap than the disposition recorded, not a new defect and not grounds to
reopen the compatibility-decision call — the disposition's conclusion (not an unmet criterion,
routes to the operator) stands. Additionally: all three real call sites in `bin/` —
`board-station.py:172-174`, `gh-sync.py`'s `load_config` (gated on `g.get("sync")` before ever
calling `load_board`), and `check-state.sh`'s INV-26 block (gated on `isinstance(_g26, dict) and
_g26.get("sync") is True`) — each independently check `github`-block-presence/`sync` before
calling `load_board`, so none of the three reaches the silent-`None` branch on that cell today.
That is what the `bin/*.py`/`bin/*.sh` grep supports; it does not establish the branch is
unreachable from every possible caller, only from these three.

## Accessibility / theme parity

Not applicable — no rendered UI, no colour, confirmed by search above (G-02: stated explicitly,
not omitted).

## Rendered-size / layout

Not applicable — no rendered surface exists in this diff.
