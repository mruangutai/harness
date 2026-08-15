# UI Review — FEAT-11 DESIGN.md (Mode A, pre-build) — the operator-facing failure-message contract

**Self-scope: IN.** No graphical surface exists, but the dispatch names the operator-facing stderr
diagnostic as the designed surface, and Expertise P-06 (this role, this codebase) holds: when a
dispatch names an adjacent non-rendered surface alongside a no-UI diff, audit it rather than decline.
Subject: `## Contract 1/2/3` of `DESIGN.md`.

## Verdict: FAIL

`must_fix` has 2 items — both change what a builder would ship, not just what the document should
say.

## 1. Missing state, and no success criterion covers Contract 3 (HIGH, must_fix)

`DESIGN.md`'s mechanism section says the resolver "must distinguish 'gh failed' from 'GitHub returned
a diagnosable envelope'" — two classes of failure. `## Contract 2`'s five-row table covers only the
second (a parseable `data`+`errors` envelope). The first — non-zero exit, stdout not a diagnosable
envelope: real auth failure, network failure, malformed response — has **no row, no
`what`/`value`/`next_step`**.

Not hypothetical: `## Contract 3` forbids `value: api graphql` for **any** failure in this path,
"including a genuine transport or auth failure." But the fallback this new call would hit is
`run_gh`'s existing `_value_from_argv` (`factory_gh.py:48-63`), which matches only a literal
`"--owner"` token — the new call's argv carries `-f`, `"owner=" + owner` (plan.yaml PART A step 2),
which it does not match, so it falls through to `" ".join(argv[:2])` = `"api graphql"`, exactly what
Contract 3 forbids.

**It also isn't checkable.** Walking `BRIEF.md`'s success criteria: SC-01 is cost, SC-02/SC-03 are
call/query shape, SC-04 is field/option naming, SC-05/SC-06 are org vs. missing-board, SC-07 is
zero-`item-edit` (raises and writes nothing — says nothing about the *message*), SC-08 is signatures,
SC-09 is integration deletion. **None asserts the `value` slot is never `api graphql`.** A contract
with no covering success criterion fails Mode A's own "is it checkable?" test.

**Must fix:** (a) add a row/rule for the non-diagnosable-envelope case with a real
`what`/`value`/`next_step`, confirming what produces it (not the generic `_value_from_argv`
fallback); (b) add a success criterion asserting no `GhError` raised anywhere in this path carries
`value == "api graphql"`.

## 2. Q1 names the exit-code rework but not the query swap Contract 2 itself requires (HIGH, must_fix)

`## Contract 2` recommends replacing `user(login:)` with `repositoryOwner(login:)` + `__typename` to
get four-state discrimination (owner-not-found vs. organization vs. board-not-found). `plan.yaml`'s
T-01 intent (the literal GraphQL document handed to the builder, lines 90-103) still reads
`user(login: $owner)` — no `__typename`, no `repositoryOwner` — and D-02 branch (a) still collapses
`data.user is null` into the organization case, the exact collapse `DESIGN.md`'s BLUF calls out as
unable to distinguish an org from a misspelled owner. Built literally as `plan.yaml` specifies,
Contract 2's rows 1 and 2 cannot both be produced.

`Q1` (blocking) names the exit-code/fixture rework but never names this. D-01's resolver shape (one
private function returning `{project_id, field_id, options}`) is unaffected by the swap — the gap is
narrower than "the plan is stale": it is D-02's branch (a) and T-01 PART A step 1's query text
specifically.

**Must fix:** `Q1` (or a new item) must say explicitly that `plan.yaml` D-02 and T-01 PART A step 1's
query need to change to `repositoryOwner(login:)` + `__typename` before build — not only that the
fixtures need exit-1 envelopes.

## 3. Grammar rule (Contract 1) not held to by the table's own row 5 (reported, not must_fix)

Contract 1's rule: "Slot 3 is what the operator does next, never the cause" — the rule used to fault
D-02 branch (a). Checking the table's own rows: rows 1–3 are imperative (`check the owner login`,
`run against a user-owned board`, `check the board number`). Rows 4–5 are declarative statements of
fact — `field-list for <owner> project <number> does not offer it` <!-- ok-stale --> and `field
<field> on <owner> project <number> does not offer it` <!-- ok-stale --> — no verb, nothing the
operator *does*, structurally the same shape as the D-02 cause the document faults. `DESIGN.md`
defends row 4 explicitly (names a command, `gh project field-list`, a human can still run). **Row 5
gets no such defense and the row-4 argument doesn't transfer** — it names no runnable command.

Not `must_fix`: both rows are frozen byte-identical by REQ-02, so the remedy isn't a reword (that
breaks the freeze) — it's a paragraph in `DESIGN.md` owning the tension for row 5 the way it already
does for row 4. Nothing a builder does changes either way; this is a document-quality gap, not an
implementability one.

## 4. Open question — combined-query exit behaviour not verified (blocking open_question, not must_fix)

Contract 2's live-verification claim ("`repositoryOwner` discriminates all three at exit 0... a
nonexistent login → null, no errors array, exit 0") was measured for `repositoryOwner(login:)`
**alone**. The BLUF's exit-code table — the document's only live verification — was measured against
the **old** `user()`-shaped query. Whether the *combined* `repositoryOwner`→`projectV2(number:)`→
`field(name:)` query preserves exit-0-for-owner-states / exit-1-for-board-and-field-states, or
changes it, has not been shown live; "the `projectV2(number:)` selection is unchanged" is an
inference. This determines whether the resolver needs one branch path or two, and the mechanism
section delegates the mechanism while withholding the fact that picks it.

Not something I can settle, and not `must_fix`: `BRIEF.md` SC-01 already reserves live GraphQL
measurement to the operator pre-ship, and answering this spends the same budget this feature exists
to conserve. Raised as `Q2`, blocking, naming who measures.

## 5. Frozen-wording tension (Contract 2, row 4) — sound, narrowly

Keeping `field-list for <owner> project <number> does not offer it` byte-identical is defensible: `gh
project field-list` remains a real, runnable command a human can type even though the tree no longer
invokes it internally. Not misleading. Doesn't extend to row 5 (finding 3).

## 6. Terminal-surface parity — not blocking, fully auditable

No colour dependency — state is never colour-only. The em dash in `{what}: {value} — {next_step}` is
a pre-existing project-wide convention (`factory_cli.body`), not new here. No width/truncation risk
beyond the existing pattern. Unlike a rendered UI, this dimension needed no "human/UAT eyes" caveat —
a plain-text stderr line is fully readable from source.

## states_unspecified

- non-diagnosable-envelope / genuine transport-or-auth failure — no `what`/`value`/`next_step`, and no
  success criterion covering Contract 3's negative constraint
- exit-0/exit-1 split of the *combined* `repositoryOwner`+`projectV2`+`field` query for the
  board-not-found and field-not-found branches — asserted, not live-verified (Q2)
