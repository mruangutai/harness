# Probe — Projects v2 limits and field shapes, measured

Run by harness-orchestrator, 2026-08-08, against the live `mruangutai` account.
Part 1 settles Q-C from the contract-validator digest and re-grades MF-5.
Part 2 settles eng-lead's first-pass Q2 (`field-list` shape, never run) and converts the
riskiest half of Q1 from a typing question into a pick-from-list.

**Conclusion, BLUF: MF-5 was worse than graded — 50 items away, not months. And board 3 is
the only one of the two boards whose existing Status options can satisfy the one-word
station rule; board 2 cannot, as it stands.**

## Part 1 — item-list

| Question | Answer | Command |
|---|---|---|
| Boards that exist | `3 Harness` (`PVT_kwHOAAases4BfZ9Z`), `2 kaya-ai` (`PVT_kwHOAAases4Bc7h3`) | `gh project list --owner mruangutai` |
| Items on board 3 today | **150**, `totalCount: 150` | `gh project item-list 3 --owner mruangutai --format json --limit 200` |
| Do CLOSED issues stay as items | **YES** — #181, #182, #183, #197 are all closed and all still on the board | same, membership test over `content.number` |
| Item status spread | Done 80, Backlog 69, Ready 1 | same |
| Does the item JSON expose issue state | **NO** — `content` has no `state` key; item keys are `content, id, labels, repository, status, title` | same |
| Token scopes | `gist, project, read:org, repo, workflow` | `gh auth status` |

### What part 1 changed

1. The 200-item ceiling is **lifetime-total, not concurrent-open** — the worse of the two
   branches the reviewer named. Board 3 stands at 150 with 80 already Done.
2. A tool **cannot filter closed items out of the item list**, because the payload carries no
   state field. Filtering needs a second call per item, or the board's own station field, or
   an archive step.
3. This drove the fix away from pagination and onto a server-side query filter (D-10).

## Part 2 — field-list

`gh project field-list <n> --owner mruangutai --format json`. Single-select fields only:

| Board | Field | Existing options |
|---|---|---|
| 3 Harness | `Status` | Backlog, Ready, **In progress**, **In review**, Done |
| 3 Harness | `Priority` | P0, P1, P2 |
| 3 Harness | `Size` | XS, S, M, L, XL |
| 2 kaya-ai | `Status` | Todo, **In Progress**, Done |
| 2 kaya-ai | `Priority` | Urgent, High, Medium, Low |

Every other field on both boards is a plain `ProjectV2Field`, not a single-select.

### What part 2 changes — read this before answering Q1

`DESIGN.md:40-47` makes **one word** a load-bearing rule, not a style note: the option name is
interpolated into a board query string and no tool quotes it, so **a name containing a space
silently matches nothing** — and a query naming an absent option returns zero items and exit 0,
which is indistinguishable from an empty queue forever. `T-05` validates board *existence* only,
so nothing machine-checks this (Q-G).

1. **Board 3 has exactly three one-word Status options — Backlog, Ready, Done** — and the
   increment needs exactly three stations. `In progress` and `In review` are two words and are
   unusable as station names without renaming them.
2. **Board 2 has only two one-word options** (Todo, Done). It cannot carry three stations
   without editing its Status field first.
3. Board 3 already carries `Priority` and `Size` as single-selects, which is the field set
   effort ticket #186 decided on. **Neither board has a `Kind` field.**
4. The field is named `Status` on both boards — so the station field's name is not an open
   question, only the option words are.

## Not probed

Whether `gh issue edit --add-label` rejects an undefined label. It needs a write to a live
repo, and the mitigation is cheap either way: every factory label is in the ensured set. Left
unverified deliberately, not assumed.
