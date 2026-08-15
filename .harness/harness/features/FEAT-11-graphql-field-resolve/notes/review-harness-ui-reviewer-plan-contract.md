# UI Review — FEAT-11 graphql-field-resolve — plan-contract (Mode A)

**Surface: the one stderr line an operator reads, grammar centralized in `factory_cli.body`.**
Read-only, no writes. `review_sha` 835b2976abd649fb814385d7d9b5b19fb7e1431a.

## BLUF

Contract holds. Byte-diff across DESIGN.md / plan.yaml / factory_gh.py found **no divergence** in
any of the five message rows. The transport column matches the probe's six measured cases exactly,
and both `<!-- ok-stale -->` markers correctly cover the retracted claim with nothing left uncovered
that still asserts it. The three new messages render as instructions and comply with Contract 1. The
one real gap: the contract's exact wording for the three NEW rows is not pinned by any automated
check — SC-04/SC-10 verify only that the *value* is named, never the literal `what`/`next_step`
text — so a future edit could silently drift from DESIGN.md's table with green tests. That gap
predates this feature (the two pre-existing frozen strings aren't byte-tested today either), so it
is not new here and does not gate.

## 1. Byte-consistency, all three documents, all five rows — verified, no mismatch

Compared literal `what`/`next_step` English text (placeholder style `<owner>` vs `{owner}` is just
doc-convention vs f-string syntax, not a byte question — the words match):

| Row | DESIGN.md:70-76 | plan.yaml (3a-d:186-202, step 6:223-233) | factory_gh.py |
|---|---|---|---|
| owner not found | `project owner not found` / `check the owner login` | identical (line 186-188) | new — matches plan.yaml |
| org | `organization-owned board not supported` / `run against a user-owned board` | identical (189-192) | new — matches plan.yaml |
| project not found | `project not found` / `check the board number` | identical (193-195) | new — matches plan.yaml |
| field not found | `project field not found` / `field-list for <owner> project <number> does not offer it` | identical (196-202) | `factory_gh.py:206-210` and `:251-256`, both `f"field-list for {owner} project {number} does not offer it"` — byte-identical to each other and to the doc pair |
| option not found | `project field option not found` / `field <field> on <owner> project <number> does not offer it` | identical (225-228) | `factory_gh.py:257-262`, `f"field {field} on {owner} project {number} does not offer it"` — matches |

No comma, capitalisation, or trailing-punctuation drift found anywhere in the five rows.

## 2. Transport column vs the probe — verified, no mismatch

Every DESIGN.md Contract 2 transport cell matches `research-FEAT-11-combined-query-probe.md:41-48`
case-for-case (owner-null → exit 0 no errors key = probe case 2; org → exit 1 + errors[] in the
probed case, with the same † caveat about the unreachable-board measurement = case 4; projectV2 null
→ exit 1 + errors[] = case 5; field null → exit 1 + errors[] = case 6; field `{}` → exit 0 = case 3).

Both `<!-- ok-stale -->` markers (DESIGN.md:59, 119) sit directly after the retracted sentence they
cover, and I found no other location in DESIGN.md, plan.yaml, or BRIEF.md that still asserts
"`repositoryOwner` discriminates all three at exit 0" uncorrected — BRIEF.md's SC-05/SC-11 already
state the split (exit 1 for the org/board-absent case, exit 0 for owner-not-found) without needing a
marker of their own.

## 3. Grammar compliance, the four new messages — compliant

Rendered in full (`factory: {tool}: {what}: {value} — {next_step}`):

- `factory: <tool>: project owner not found: <owner> — check the owner login` — instruction.
- `factory: <tool>: organization-owned board not supported: <owner> — run against a user-owned board`
  — instruction. On the value slot specifically: `<owner>` here echoes the operator's own input back
  (same pattern as the other four rows and required by Contract 3), so it is useful — it lets the
  operator confirm which login was rejected rather than just "an org was rejected somewhere."
- `factory: <tool>: project not found: <owner> project <number> — check the board number` —
  instruction.
- `factory: <tool>: gh graphql call failed: <owner> project <number> — re-run after checking gh auth
  status and network access` (plan.yaml:176-181) — instruction, and its value is the operator's own
  owner/number, never `api graphql` — Contract 3 and SC-10's negative clause are honoured explicitly
  by design.

All four obey "slot 3 is an action, never the cause." The two frozen rows that state a fact in slot 3
are D-04's accepted tension, not re-raised here per the dispatch.

## 4. Completeness and enforceability

**Two operator-facing states the table doesn't name**, both low severity, neither blocking:
- `data` key present but `repositoryOwner` entirely absent (vs explicitly `null`) — plan.yaml's walk
  ("repositoryOwner is null") doesn't specify `.get()` vs direct indexing; a direct-index
  implementation hits an unhandled `KeyError`, trapped by `factory_cli.run`'s generic "unexpected
  failure" path (`factory_cli.py:88-96`) instead of the designed message. Realistically unreachable
  against GitHub's actual GraphQL behaviour (the probe shows the key always present, null or
  populated), but the design text doesn't foreclose it.
- A `field` value that is neither `null`, `{}`, nor a populated single-select object (e.g. a list or
  scalar from a future schema change) — folds into branch (d) only if the implementation's falsy
  check is broad; not explicitly stated.

**The enforceability question (item 4, second half).** SC-04 (BRIEF.md:59-62) and SC-10
(BRIEF.md:102-111) both assert only that the message *names the value* and that it never contains
`api graphql` — neither asserts the literal `what`/`next_step` text against DESIGN.md's table. So a
build that typed slightly different English for one of the three NEW rows (e.g. "board owner not
found" instead of "project owner not found") would still pass every SC. This is a real gap between
DESIGN.md's message table and what the test suite actually pins — but it is not new to this feature:
grepping the current tree shows neither of the two *pre-existing* frozen strings is asserted
byte-for-byte in `test-factory-gh.py` today either (only a comment references the phrase). SC-04/
SC-10 are consistent with the existing project convention (test the actionable value, not the prose),
so I read this as a pre-existing pattern the contract inherits rather than a fresh defect it
introduces. Flagging it because Contract 2 markets the five rows as tightly specified prose, and
"prose nobody checks" is exactly the failure mode Mode A exists to catch — but it does not gate.

## Accessibility

Not applicable in the conventional sense — this surface is a single plain-text stderr line with no
markup, colour, or interactive element. Nothing here to audit for contrast, labels, or reading order.

## Out of scope, not touched

D-04's accepted tension (frozen `field-list` next_step naming a removed subcommand) — per dispatch,
not returned as a finding.
