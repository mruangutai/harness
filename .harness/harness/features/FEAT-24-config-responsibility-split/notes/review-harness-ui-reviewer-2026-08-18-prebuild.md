# ui-reviewer — FEAT-24 — Mode A pre-build — 2026-08-18

## Scope call: IN

There is no `DESIGN.md`, but `plan.yaml` itself carries an exhaustive, mostly-implementable text
contract for the surface this feature actually changes: **operator-facing CLI/gate stderr lines and
exit codes**, replacing today's silent `None` with a loud, named failure (REQ-03). That is squarely
the surface this role audits — see the dispatch's own framing and Expertise P-06 ("a handed-down
non-rendered surface turns a decline into a reviewed finding"). I read `plan.yaml` in full (all 1284
lines, two passes) and cross-checked its message-grammar claims directly against
`.claude/skills/harness/bin/factory_config.py`, `factory_cli.py`, `factory_gh.py`, `gh-sync.py` and
`board-station.py` at HEAD. That is the census: every new error-emitting state named in T-01, T-02,
T-04 and T-05 — the eight malformed-board shapes (SC-04) driven through both entry points, the
explicit-null non-error path, the remote-read failure, the memo-failure-not-cached case,
`board-station.py`'s split, `gh-sync.py`'s split, and INV-26's split — was traced to source and
checked for wording/exit-code completeness and cross-tool consistency.

**Counter-argument on the record — confirmed true, not just plausible.** `FleetError.__str__` and
`GhError.__str__` are both built by `factory_cli.body(what, value, next_step)` →
`"{what}: {value} — {next_step}"`, and `next_step` already threads `in {path}` (or an equivalent
named-value clause) through every existing raise I read: `_validate_board` and `load_fleet`
(`factory_config.py:65-165`), the `workspace_root` filesystem-root guard, `repo_entry` and
`board_station` (`factory_config.py:180-217`). New error paths inherit this style — verified at
source, not taken on trust. This closes most of the "would the operator have enough to act on"
question before it opens.

## Prototype gate: CONFIRM — no prototype needed

Every new state this feature introduces is a stderr line and a shell exit code; there is no rendered
screen, no interactive flow, no layout, and (per `SC-04`/`SC-06`/`D-07`) no colour-only state
encoding to prototype. This is exactly FEAT-19's own manifest classification
(`needs_prototype: false`) despite FEAT-19's designer scoping *in* for text-contract work — the two
questions are independent: whether a high-fidelity mock is needed (no, here or there) is not the same
question as whether the text contract needs review (yes, here and there). Confirming the
product-lead's call.

## Finding — gh-sync.py's new loud-failure exit code and prefix are unspecified, and board-station.py's parallel path pins both

**Where:** `plan.yaml` T-04 Part B item 4 (gh-sync.py `load_config`) vs. Part C item 7
(`board-station.py`'s no-board branch). Both react to the *same* new condition —
`factory_config.FleetError` raised by an unusable board declaration — through independent code paths
(P-10: cross-tool consistency for the same refusal condition through different call sites).

- **board-station.py side is fully pinned.** T-04 item 7: "prints one line on stderr, prefixed
  `board-station:` as every line in this tool is... and exits 2." Confirmed at source:
  `board-station.py:55-60` (`out()`/`err()`) already carries a uniform `"board-station: "` prefix,
  and `EXIT CONTRACT` documents 2 as the tool's one non-zero value.
- **gh-sync.py side is not.** T-04 item 4 says only: "one line on stderr naming the file and the
  key, and a non-zero exit. Do NOT route it through `skip()`, which exits 0." It never says which
  non-zero value, and never says what prefix the line carries.
- **`gh-sync.py`'s own two existing exit primitives are both a semantic mismatch for this state**
  (confirmed at `gh-sync.py:72-81`): `skip()` = "Environmental no-go... exit 0. The mirror never
  gates" — explicitly excluded by the task. `die()` = "Caller error: the dispatch itself is wrong.
  Visible, exit 1" — but a malformed board is a **config** defect, not a caller/dispatch mistake;
  reusing `die()` here would make its own docstring false the moment it is reused for a second class
  of problem.
- **The rest of the factory family already has a name for this class.** `factory_cli.run()`
  (`factory_cli.py:72-96`) catches exactly this kind of "expected" exception — the class every other
  `factory_*` CLI raises `FleetError`/`GhError` into — and exits `EXIT_REFUSED = 2`, the same value
  `board-station.py` independently pins for the identical condition. `gh-sync.py` is the one tool in
  this feature's surface that does **not** route through `factory_cli.run()` and has no `EXIT_REFUSED`
  of its own.

**Consequence if unaddressed:** two sibling CLI paths built from the same task, reacting to the same
misconfiguration, can legitimately ship with different exit codes (1 via `die()`, or a new ad hoc
value) and different stderr prefixes, because T-04's own verify only asserts "a non-zero exit"
(`hasin "an unusable board config is a loud failure, not a skipped station write"`) — it cannot catch
which non-zero value ships, so this divergence is invisible to the test that is supposed to prove the
task done. This is the same *class* of gap ui-reviewer caught on FEAT-19 (a refusal branch's exact
exit-code/output-slot contract left to the plan's silence — see
`FEAT-19-central-product-config/runs/plan-product/digest.md`, "The prototype gate" section) —
confirmed here by reading the actual `die()`/`skip()` docstrings and `factory_cli.run()`, not by
analogy alone.

**Recommendation, not a blocker:** add one clause to T-04 Part B item 4 pinning gh-sync's new failure
line to `"gh-sync: ERROR — {FleetError}"` (matching this file's own existing `die()`/parent-station
convention) and its exit code to `2` (matching `board-station.py`'s pinned value and the wider
`factory_cli.EXIT_REFUSED` convention), or state explicitly why gh-sync should diverge. This is a
one-line plan edit, not a redesign, and does not require another review cycle to land.

**Severity: med, not blocking.** The message content itself (file + offending key) is already fully
specified regardless of which exit code ships — an operator reading stderr is not short-changed. The
risk is confined to script/wrapper integration reading the exit code, which is a real but
lower-stakes consequence than an unreadable or missing message.

## Other states checked, no gap found

- The eight malformed-board shapes are driven through **both** `load_board` and `board_for` with
  identical ok-line texts (`SC-04`, T-02 and T-04) — cross-checked, consistent.
- The explicit-null non-error path (D-07) is asserted separately from the absent-key error path at
  every entry point checked (T-02, T-04, T-08 template, T-06 harness board) — no vacuous-truth risk;
  `_STATION_KEYS`/the five-key set is a fixed non-empty tuple, so an empty `stations` map fails the
  key-set-equality check before any `all()`-style short-circuit could apply (Expertise P-12 checked
  and cleared).
- T-01's `GhError` composition of repo+path+ref into one `value` slot is *not* pinned to an exact
  string template, only to "in that order" plus a three-assertion substring test — this looseness is
  appropriate (project rule 6, pin acceptance not implementation) and is not a finding, unlike the
  exit-code gap above where an existing, named semantic taxonomy (`die()`'s own docstring) would be
  falsified by the obvious implementation choice.
- T-05/INV-26's loud-failure path has no equivalent ambiguity: it already has one mechanism (append to
  `bad`, gate completes) with no exit-code choice to make.
- Docstring-rewrite instructions (T-04 item 3b, T-04 Part B item 5, T-05 item 3, T-06 `_note`, T-08
  `_board_note`) were spot-checked against current file content and are accurate descriptions of what
  exists today — none describes a state that isn't actually there.

## Accessibility / theme parity — not applicable, stated explicitly

This surface is batch/CLI stderr text and process exit codes with no colour-only state encoding and
no rendered screen. Both sections are explicitly not-applicable rather than omitted (Expertise G-02).

## Rendered-size / layout — not applicable

No layout or rendered surface exists in this diff; nothing here needs a human/UAT visual check.
