# FEAT-58 — final apply: dispositions for the four rulings and four gaps

**All eight applied; two with a stated variance, none rejected. One item added beyond the eight
(SC-11's glob), because G-4 is unclosable without it.** `plan.yaml` written only through
`plan-merge.py amend` (8 field amends, 2 of them list fields), re-loads under `safe_load`,
`check-plan-routes.py` exits 0 with 0 violations. `approval: {status: pending}` and `status: plan`
untouched; no task carries a station key.

## Dispositions

| # | Item | Disposition |
|---|---|---|
| 1 | F-1 two frame lines → T-03, T-04 | **applied-with-variance** — wording transcribed sentence-for-sentence from the receipt's paste-ready block; the markdown decoration (blockquote `>` markers, backticks) is stripped, because DEC-182 forbids markdown in a `plan.yaml` value and the surrounding intents carry none. T-04's copy substitutes "Each module records" for "Record". T-05 and T-12 untouched, asserted |
| 2 | F-2 `REQ-05` → T-04 `traces:` | **applied** — now `[REQ-03, REQ-04, REQ-05, SC-04, SC-05, SC-09]` |
| 3 | F-3 `SWEEP_GLOBS` conversion → T-06 | **applied** — one shared `corpus_features(corpus_root(root), provider="path")` per invocation, five suffixes joined per enumerated name, `CLAUDE.md` literal, inner `runs/*`/`handoff-*` retained, worktree tier survives, no T-13 allow-list entry. Measurement carried verbatim: **-0.1751 ms/checkout, N=100, corpus 88 features** |
| 4 | F-4 `linked_worktrees(corpus_root(root))` → T-06 | **applied** — stated as a live latent defect with the reason (`.git` is a FILE in a linked worktree → the `listdir` of `<owner_root>/.git/worktrees` raises → `[]` on OSError → the tier reaches nothing whenever the hook fires from inside a worktree, the common case under DEC-143) |
| 5 | G-2 FEAT-57 freeze → T-01 | **applied** — hard execution precondition at the head of T-01's intent, the sole `depends_on: []` root (verified by topological sort). T-15's own in-file gate unchanged and explicitly additional |
| 6 | G-3 owner-root exclusion → T-09 | **applied** — added as a *guard* in the script plus its own assertion in `tests/unit/test-corpus-migration-order.py` (already in T-09's `files:`), with a red proof. A test asserting refusal needs the behaviour to exist, so both halves are specified |
| 7 | G-4 widen T-14 | **applied** — sweep scope now globs `.claude/commands/*.md` too; `.claude/commands/harness.md` added to `files:`; the `:45` bullet is rewritten by the task. Scope stays glob-based. `execution_reason` widened: `--resolve` returns NOBODY for that path too, measured this run |
| 8 | BRIEF REQ-05 strengthening | **applied** — receipt's sentence appended verbatim. SC-05 unchanged, as ruled |

## Added beyond the eight — one item, flagged

**SC-11's glob list in `BRIEF.md` now names `.claude/commands/*.md`.** Widening only T-14 would
have left the criterion stating a scope that excludes the one live violating artifact, so SC-11
could never redden on it — the criterion's grading set would be narrower than the work it grades.
No new SC id, no verify-method change.

## Two decisions taken locally (reversible, recorded here)

- **T-06's sweep path REPORTS a `CorpusIncomplete` refusal on stderr rather than letting
  `except Exception` at `:2152-2153` absorb it.** A PostToolUse sweep cannot deny after the fact, so
  an absorbed refusal is a clean report over a partial view — this feature's own defect. The
  deliberate absorb for a genuinely unimportable module (`:2141-2143`) stays and is distinguished.
- **T-06's title** now reads "Repoint both check-domain.sh corpus enumerations at the corpus root".
  The old title named `_hardlink_plan` alone and would have misdescribed the task's own scope.

## How the acceptance was checked

- `safe_load` over the amended file: 16 tasks, 12 decisions, every scalar tail intact.
- Traceability against `BRIEF.md`'s 11 REQ / 14 SC: **0 untraced REQ, 0 untraced SC, 0 traces citing
  a nonexistent id**, 0 tasks missing `change_type`.
- `graphlib.TopologicalSorter` over `depends_on`: acyclic, single root `T-01`.
- `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0. The 11 `DEVIATION` lines are the expected
  DEC-174 carve-out output; T-14 now reports `OK … main-session-direct` with the command file named
  as ungranted, which confirms the lane rather than contradicting it.
- Anchors re-derived this run, not trusted: `_SWEEP_PATTERNS` `:1052-1062`, `SWEEP_GLOBS` `:1069`,
  consumption `:2147` / `:2150-2151`, and `.claude/commands/harness.md:45` — all present as recorded.

## Open

Nothing blocking. `lanes:` still carries no row for `.claude/commands/**`; `plan-merge.py` has no
verb that reaches a top-level key (D-10 records the same limitation), so the routing fact lives in
T-14's `execution_reason`. If the operator wants the row itself, that is a main-session write.
