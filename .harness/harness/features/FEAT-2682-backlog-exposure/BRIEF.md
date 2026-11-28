# BRIEF — FEAT-2682-backlog-exposure Rate every ship-briefing backlog issue under DEC-260

## Problem

At ship acceptance the main session files the briefing's unstruck residual findings through
`gh-sync.py backlog`, one `nature:title` argument per row. Neither the briefing's proposed-backlog
table nor the verb has a slot for a DEC-260 exposure, so every backlog issue carries only the fixed
body "Residual finding from <FEAT>, accepted at the ship briefing." The operator triaging the
backlog later cannot tell a regression from a contrived no-worse finding, and a finding the
practicality rule discounts (contrived, no worse than today, not adversary-controlled) is filed as
work exactly like a real one (#2682).

## Done when — by perspective

**operator** — Every backlog issue the ship briefing files states its exposure, or why the row has
none. A row with no exposure, a malformed one, or one the practicality rule discounts never becomes
an issue, and nothing reaches GitHub when I pass one. The briefing still shows me every residual,
discounted ones included, so nothing dies silently. Issues and receipts filed before this ships
stay as they are.

**code maintainer** — The exposure values and the discount predicate stay defined once, in
`bin/panel_findings.py`. The verb's existing behaviour (labels, issue types, no milestone, the
`backlog-issues.json` receipt and its rerun suppression) is unchanged, and its existing tests still
pass, moved to the new item form.

## Success criteria

Terms. **Item form:** `nature:<exposure>:title`, where `<exposure>` is `trigger/vs_today/control`
in DEC-260's closed values, or `unrated=<reason>` with a non-blank reason. **Discounted:**
`panel_findings.is_discounted` is true (contrived, no_worse, control not adversary). **Pre-change
verb:** `gh-sync.py` at `git merge-base HEAD main` on the build branch.

- SC-01 (operator): `gh-sync.py backlog` exits 2, invokes `gh` zero times (not even
  `gh auth status`) and writes no `backlog-issues.json`, for an item with no exposure
  (`bug:a defect`); for each malformed exposure: an off-enum value, two or four slash-separated
  parts, bare `unrated`, and `unrated=` with a blank reason; and for a list where one malformed
  item follows a valid one, which is not filed either. qa must show each case fails against the
  pre-change verb first.
  verify: automated        evidence: integration
- SC-02 (operator): the verb exits 2 with a message naming DEC-260, invokes `gh` zero times and
  writes no receipt for a discounted item with control `harness`, `chance` and `user` each. It
  files a contrived, no_worse, adversary-controlled item (exit 0). No argument or flag admits a
  discounted item. qa must show the refusals fail against the pre-change verb first.
  verify: automated        evidence: integration
- SC-03 (operator): each filed issue's body states the item's rating as
  `Exposure (DEC-260): trigger <t>, vs_today <v>, control <c>`, or its reason as
  `Exposure (DEC-260): unrated - <reason>`, in place of the fixed line alone, on both the
  native-issue-type path and the labels-only path. qa must show this fails against the
  pre-change verb first.
  verify: automated        evidence: integration
- SC-04 (code maintainer): `backlog-issues.json` keeps its shape: entries keyed `nature:title`,
  each holding exactly `number` and `typed`; an entry an earlier run wrote under that key still
  suppresses re-creating its item. Every pre-existing case of
  `tests/integration/test-gh-sync-open.py` and `tests/integration/test-gh-backlog-issue-types.py`
  passes with its items moved to the item form, a colon-less item still exits 1, and
  `tests/unit/test-issue-types.py` passes unchanged.
  verify: automated        evidence: integration
- SC-05 (code maintainer): at the review_sha, `gh-sync.py` imports `panel_findings` and decides
  well-formedness with `panel_findings.exposure_faults` and the discount with
  `panel_findings.is_discounted`; it holds no literal copy of the trigger, vs_today or control
  value sets. The reviewer cites the symbols from `git show <review_sha>:.claude/skills/harness/bin/gh-sync.py`.
  verify: inspection
- SC-06 (operator): read with `git show <review_sha>:<path>`,
  `.claude/skills/harness/references/briefing.md`'s proposed-backlog table instructs an exposure
  per row in the item form's values, lists a discounted row with its exposure cell marked struck by
  DEC-260 and says it is never passed to the verb; `.omp/commands/harness.md`'s shipped row states
  the item form `nature:<exposure>:title`.
  verify: inspection

## Verification gaps

- `issue_types_live` is `locally_run` (needs authenticated `gh`). This feature leaves issue-type
  resolution (`type_for_nature`, `_backlog_apply_type`) untouched; SC-04's fake-`gh` integration
  cases carry the typed path, and no live probe is required for ship.
- No SC rests on a null or excluded kind; `integration` and `unit` are active runners.

## Constraints

- **Sequencing (BLOCKS the build).** The build starts only after FEAT-2643-ship-before-merge merges
  to main, and is based on that main: FEAT-2643 rewrites the ship order in the same `gh-sync.py`,
  `.omp/commands/harness.md` and `references/github-mirror.md`. This feature plans no FEAT-2643
  surface; T-01's verify refuses to pass on a base that lacks it.
- **DEC-174 (BLOCKS team execution).** T-01 adds a refusal to a Harness gate script, so it runs
  main-session-direct with its tests, like FEAT-2622; planning through Harness stays fine.
- **DEC-260 (SUPPLIES).** The closed values and the discount predicate live once in
  `bin/panel_findings.py`; the verb imports them, never copies them.
- **DEC-138 (binds).** Residuals become plain backlog issues only through the briefing and
  `gh-sync.py backlog`: labeled `harness` plus `bug`/`chore` by nature, unlabeled for enhancements,
  no milestone. All of it stays unchanged; a discounted row is struck by the rule, so "unstruck
  rows become issues" still holds.
- **Receipt.** `backlog-issues.json` gains no key and changes no shape (operator ruling).
- **Forward only.** Existing issues and receipts are never rewritten or backfilled.

## Out of scope

- Gating other issue-creating routes (factory decompose, `gh-sync.py open`, wayfind maps): ruled
  out by scope, since none of them files findings.
- Backfilling ratings onto open backlog issues: ruled forward only.
- Changing the digest gate: findings already carry an enforced exposure (FEAT-2622).
- Any change to `backlog-issues.json`: ruled out with the receipt key.

## Approval

status: approved
approved-by: operator
date: 2026-11-28
