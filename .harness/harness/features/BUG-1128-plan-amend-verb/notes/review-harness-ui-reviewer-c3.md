# UI/operator-surface review — BUG-1128 panel c3 — review_sha 20775866

## Verdict: PASS — the round trip holds, N1's comment-deletion closure reproduces, and the
three previously-open message gaps remain byte-identical (advisory only, unchanged)

## Measured census

`git diff --name-only 08dd66bb..20775866`: 15 files. Extension census for
`html|css|scss|tsx|jsx|vue|svelte|less`: **zero matches**. Non-bookkeeping content: only
`plan-merge.py` (+261/-…) and `test-plan-merge.py` (+240/-…). No `DESIGN.md` at this pin (unchanged
from c1/c2). Zero rendered UI in this diff, again. The sole operator surface remains
`plan-merge.py`'s `amend` CLI, per the dispatch's explicit adjacent-surface instruction — same
scope call as c1 and c2, on fresh measurement, not inherited by assumption.

All experiments ran against fixtures under `/tmp/uirev-bug1128-c3/`, built with the `write` tool
(bash `cp`/`rm`/redirection is blocked for this role even to `/tmp` — confirmed by the guard, see
Open Questions). Nothing in any worktree was touched; `git status --porcelain` on the BUG-1128
worktree is empty after this review, and the FEAT-46 worktree's real `plan.yaml` was read-only
(`--show` and structural greps), never opened for write.

## Item 1 — the `--show` → `--value-file` round trip

Six identity replaces run against a fresh fixture (`.harness/features/FEAT-99-test/plan.yaml`):
plain scalar (T-01), a genuine multi-line **plain** scalar with continuation lines and no `|`/`>`
indicator (T-02), a `|` block (T-03), two adversarial `|` blocks whose own last line begins
literally with `sha256:` (T-04 loose match, T-05 exact-format collision), and a `decisions:`
`because:` field (D-01). Procedure: `--show`, strip exactly the printed **last** line, feed the
rest back via `--value-file` with the printed hash.

| id | shape | exit | whole-file sha256 after vs before |
|---|---|---|---|
| T-01 | plain, one line | 0, AMENDED | **identical** |
| T-02 | plain, 3 continuation lines | 0, AMENDED | **differs** — see below |
| T-03 | `\|` block | 0, AMENDED | **identical** |
| T-04 | `\|`, own last line starts `sha256:deadbeef…` (no space) | 0, AMENDED | **identical** |
| T-05 | `\|`, own last line is `sha256: ` + 64 hex chars (exact trailer format) | 0, AMENDED | **identical** |
| D-01 | `decisions:because`, one line | 0, AMENDED | **identical** |

**T-02 is genuinely not byte-identical**, and this is worth stating precisely against the
dispatch's literal ask: the *value* round-trips exactly (`yaml.safe_load` before/after matches,
confirmed), but the *on-disk form* does not — a plain scalar spanning 3 physical lines collapses
to 1 physical line, because `_render_field`'s plain-scalar path always routes through
`yaml.safe_dump` (width `10**9`, no wrap) and only a **block** scalar's header/body shape is
reused verbatim. This is consistent with `_render_field`'s own docstring, which promises form
preservation for block scalars only, and with SPEC.md:1813's byte-exact requirement, which is
scoped to `|`. Not a defect — a precise clarification of what "round trip" means per shape:
**semantic identity always; byte identity only for a single-line plain scalar or a `|` block.**

**The confirmed-live real case.** Also ran the identity round trip against the exact `D-05.because`
and `D-14.because` text from FEAT-46's real `plan.yaml` (copied verbatim into a fixture, per the
dispatch — the two fields the plan's next cycle will actually amend): both are single-line plain
scalars, both round-tripped **whole-file byte-identical** (`sha256sum` before/after equal). The
tool's round trip is safe for the two fields this feature exists to unblock.

**The ambiguity the dispatch asked to find.** YES, it exists, and I demonstrated its consequence.
`--show`'s output is `<value>\nsha256: <hash>\n` — the trailer is identified by **position** (it
is always literally the last printed line), never by content pattern. Positional stripping
(remove exactly the last line) is unambiguous and correct in every case tested, including T-04
and T-05. But T-05's construction — a value whose own last line is itself
`sha256: <64 lowercase hex chars>` — makes **content-based** stripping (e.g. "remove the line
that looks like a sha256 trailer") genuinely undecidable: two lines are format-identical. I
reproduced the failure this invites: fed back T-05's first line plus the *real* trailer's hash
(as if an operator had mis-picked which of the two "sha256:"-shaped lines to discard) with the
current `--expect-sha256`. Result: **exit 0, `AMENDED tasks:T-05.verify`**, and the field now
reads `the check documents its own expected digest below\nsha256: 2093cf…\n` — the operator's own
prior read-hash spliced into the document as if it were the value's second line, silently
replacing the real `sha256: 0000…0000` content line. Nothing catches this in principle: the
identity check compares the reloaded value against what was asked for, and the corrupted text is
exactly what was asked for — same shape `N4` (cycle 2, now closed for the general case) described,
surviving in this one narrow corner. **Rated low, not must-fix**: the trigger requires a value
that independently contains a line matching the trailer's exact `sha256: [0-9a-f]{64}` format —
not observed anywhere in FEAT-46's real plan — and only misfires under content-based stripping;
the natural, always-correct convention is positional (strip the last line), which this review's
own T-04/T-05 identity replays both confirm works. Worth a one-line help-text clarification
("the last line only, however it reads") rather than a code change.

## Item 2 — receipts

Format confirmed unchanged across all six replaces above plus D-05/D-14: `AMENDED
<key>:<id>.<field>` then `APPLIED <resolved path>`, exit 0 — never a diff, line count, or
boundary marker. This gives the operator no way to notice a boundary error from the receipt
alone; that has been true every cycle and remains true.

**N1 closure, reproduced directly.** Built a fixture with a `# NOTE` comment immediately
preceding `verify:` and a blank-line-then-comment immediately after it, before the next item.
Replaced `T-01.verify` with its own identity value. Result: **both comments and the blank line
survive byte-for-byte** — confirmed by re-reading the file after the write. N1 holds at this pin,
directly reproduced rather than inherited from the record.

**A residual, previously-known gap, re-confirmed still open.** Cycle 1's UI note (Q2) flagged
that a **nested mapping** sharing a field's name (`checks: {verify: …}` beside a top-level
`verify:`) makes `_find_field_line` bind to the nested occurrence, because `SIBLING_KEY_RE`
matches the first hit deeper than the item indent with no depth ceiling. Reproduced today,
unchanged: `--show --field verify` against `{checks: {verify: "nested value…"}, verify: "the real
top-level verify"}` returns `nested value, not the real field` at **exit 0**, silently. This was
never promoted to must-fix in cycle 1 or 2 (fail-closed on a subsequent *replace*, since the
identity check refuses when the reloaded field doesn't match what was asked; only `--show`, the
read path, is misled) and it still isn't reproduced anywhere real: I grepped FEAT-46's actual
`plan.yaml` for any nested-mapping-valued field under a task or decision (only `files:`, a list,
appears at that shape) and found none. **Rated med, not must-fix** — matching this exact finding's
rating in the cycle-2 UI note it carries forward from, and non-gating because it is confirmed
absent from the real consumer this panel is judging safety for.

## Item 3 — refusal messages, closure status of the three named gaps

`git diff 08dd66bb..20775866` on `plan-merge.py`, filtered to every refusal string cycle 1/2
tracked: **byte-identical in all three cases** — the amend block was refactored (a new
`_amend_locate` helper extracted, `_die` collapsing print/exit pairs) but no message text
changed.

| refusal | exit | names the document | pasteable next command | status |
|---|---|---|---|---|
| `_amend_preconditions`, missing hash/value-file | 2 | no (not yet resolved at this point) | no — says "Run --show first" without reconstructing the flags | **STILL OPEN, byte-identical** |
| `_amend_preconditions`, pre-lock hash mismatch | 6 | n/a | names BOTH hashes + "Re-run --show" | unchanged, good, not a gap |
| `transform`, under-lock hash mismatch | 6 | no | no — "changed between the read and the lock," no hash, no remedy | **STILL OPEN, byte-identical** |
| `transform`, base doesn't parse | 8 | no — "the plan on disk" + PyYAML's own anonymous `in "<unicode string>"` | no | **STILL OPEN, byte-identical** |
| `_amend_locate`, id not found | 3 | yes, `in {resolved}` | n/a (lists ids present) | fine |
| `_amend_locate`, field not found | 4 | no | n/a (explains why by design) | not previously flagged; consistent low, not new |
| `transform`, id vanished under lock | 3 | no | n/a | not previously flagged; consistent low, not new |
| `transform`, field vanished under lock | 4 | no | n/a | not previously flagged; consistent low, not new |
| `_verify_amend`, wrong-field write | 5 | no (states asked-for/reloads-as values instead) | n/a | unchanged, adequate |
| `_sole_item`, duplicate id | 5 | no | no | unchanged, low (cycle-2's own rating) |
| `harness_merge`, lock timeout | 6 | yes, names the `.lock` path | n/a | fine, outside plan-merge.py |
| `_resolve_plan`, exit 9 (bad path) | 9 | yes — shows both the given and resolved path, plus legal-shape examples | n/a | fine |

One correction to the prior cycle's framing, found while building this table: the c2 UI note
described exit-8's "siblings in the same function" (`transform`'s own exit-3/exit-4, the
under-lock recheck) as interpolating `{resolved}`. At this pin **neither does** — both are
`{id}`/`{id}.{field}`-only, same as exit-8. I cannot confirm from the diff whether that
characterization was ever true (the 08dd66bb→20775866 diff shows these three lines untouched, so
if it was true then it is equally untrue now, not a regression). Not re-filed as a new item —
noted so the pattern in the table above (no exit inside `transform` names the document) is read
correctly, and all three of exit-3/4/6/8 under the lock share the same gap, not just exit-8.

All of these remain advisory per this role's own contract (message wording is low/info) and per
the panel's standing decision across two cycles to keep them out of must_fix.

## Item 4 — help text

`amend --help`'s own summary is unambiguous: "replace ONE field of ONE named task or decision,
compare-and-swap on its sha256" — REPLACE, never ADD, stated plainly. `--field`'s help says "the
field to replace"; `--value-file`'s help says "replacement value." Good on the REPLACE-not-ADD
axis the dispatch asked about.

**One stale line, found by comparing help text against the current implementation.** `--show`'s
help reads: `"print the current field block and its sha256, and write nothing"`. That was accurate
before N3; it is not accurate now — N3's own remedy (docstring at `_amend_show`) deliberately
changed the emission from the field **block** (including the `field:` key line) to the bare
**value**, specifically so the round trip in item 1 would hold. The help text was never updated to
say "value" instead of "block." **Low, wording-only**, but a real drift between what the flag now
does and what `--help` says it does.

**Undocumented, confirmed live**: passing `--show` together with `--expect-sha256`/`--value-file`
silently ignores the latter two — `cmd_amend` branches to `_amend_show` and exits before
`_amend_preconditions` ever runs. Verified: `--show --expect-sha256 bogus --value-file
/nonexistent` still printed the value and exited 0, no complaint about the bogus/missing files.
Help text doesn't say `--show` is exclusive of the other two. **Low**, and arguably correct
behavior (an operator combining flags in one command line is unusual), just unstated.

## Item 5 — accessibility / terminal-only concerns

Applicable dimensions, measured: no ANSI escape sequences or color library anywhere in
`plan-merge.py` (`grep` for `\x1b[`, `colorama`, `termcolor` returns nothing) — every state is
conveyed by exit code plus stderr/stdout text, never by color, which is the correct default for a
surface that is piped, logged, and read by both humans and scripts. Non-ASCII use in the amend
block is limited to em-dashes in docstrings/messages, standard UTF-8, no rendering risk. Line
width: refusal messages wrap across Python string-literal continuations but each still prints as
one long stdout/stderr line — acceptable for a CLI whose output is typically captured or piped,
not scrolled by a human reading a fixed-width terminal, and consistent with every other verb's
messages in this file. **No accessibility gap found on this surface.**

## Open questions

- Q1 (harness process observation, not a code finding): the bash tool's write-guard for this role
  blocks `cp`/`rm`/redirection unconditionally, including to `/tmp`, even though the dispatch's
  constraint section explicitly authorizes `/tmp` scratch experiments. I worked around this by
  using the `write` tool for every fixture and value file (permitted) and running the real binary
  read-only via `bash` (permitted), which fully covered the assignment — but a successor role
  told to "experiment in /tmp" should know bash alone cannot do it; `write` must build the
  fixtures. Non-blocking, and it did not narrow anything I could test.
- Q2 (non-blocking, carried from cycle 1, still genuinely open): is the nested-mapping mis-bind
  (item 2) worth a future fix, or is "confirmed absent from every plan.yaml in this checkout"
  sufficient grounds to leave it? Not this panel's call; flagging again because it is the one
  finding in this note that touches the tool's *correctness*, not just its wording.

## Files touched
None in either worktree — read-only. Fixtures and value files under `/tmp/uirev-bug1128-c3/`.
