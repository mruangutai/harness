# receipt — harness-data-engineer — 2026-08-19-12-eng — distill

## Base

Read `.harness/expertise/harness-data-engineer.md` from disk (not the injected block) as base.
Counts before: Patterns 1, Gotchas 1, Outcomes 0, Open 0. 15 lines / 150-line budget.

## Accepted (5 add, 0 replace/merge/drop)

1. **P-02** — `source: own-artifact` (receipt-2026-08-18-1-eng-alt J2 table: per-item vs
   file-global vs absent verify classification, plus the SC-10 "no implementing verify anywhere"
   framing) merged with `source: lead-relay` candidate 1 (my SC-10 headline over-totalized; the
   lead's correction found two of eleven files did carry assertions). Merged into one entry rather
   than two near-duplicates — both taught the same workflow: classify per-file before writing a
   totalizing claim. Passes six-spawns: this is a repeatable analytical step for any verify-gap
   finding, in any repo.

2. **P-03** — `source: lead-relay` candidate 2 (my "19 files, matches `git diff --stat` exactly"
   bare assertion, resolved against two independent breakdowns arriving at 13). Accepted as
   written: attach the breakdown, not just the total. Six-spawns: applies to any scope-count claim
   I write, not specific to this feature's file count.

3. **G-02** — `source: lead-relay` candidate 3 (docstring said `gh_board.load_board` raises on
   github-block-absent; code returns `None`; I called the caller situation a discriminator I could
   not resolve; enumerating all callers showed both pre-filter the case, so it is a stale
   docstring, not a live hole). Accepted: the resolving move — enumerate callers before flagging —
   generalizes past this one function.

4. **G-03** — `source: own-artifact` (receipt-2026-08-19-8-eng-alt F2: the `gh` test fake matches
   argv text only, never HTTP verb or response shape, so a future read-flipped-to-write call would
   pass silently). Accepted: argv-text-only fakes for external CLIs are a general testing gotcha,
   not specific to `gh`.

## Rejected

- F1 from receipt-2026-08-19-8-eng-alt (github-block-absent silently returns `None`) — the
  underlying *mechanism* (docstring/raise vs silent return, resolved via caller enumeration) was
  promoted as G-02. The specific finding itself (which function, which repo) does not pass
  six-spawns on its own and is not craft — correctly a one-off finding, already delivered via that
  receipt's `open_questions`/briefing-row, not Expertise.
- F3 from the same receipt (duplicated `"github.board"` literal across two files) — a real
  finding but not a generalizable rule; "don't duplicate a string literal across files" is a
  restatement of DRY, not something that would change what I do differently six spawns from now
  in an unrelated repo. Left out.
- Lead-relay candidate 1 and my own P-02 material were not kept as two separate entries — see
  "Accepted" item 1. Two near-duplicate entries covering the same workflow is padding; merged to
  one, same length as the longer input, per the merge rule.
- No repository-tier candidate: nothing in either artifact turns on a path/decision/invariant
  unique to this one repository as opposed to the craft-level judgement it illustrates, and
  `.harness/harness/expertise/` does not exist per the dispatch — correctly nowhere to put one even if
  found.

## Counts before/after

| Section | Before | After |
|---|---|---|
| Patterns | 1 | 3 |
| Gotchas | 1 | 3 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

Total: 15 lines → 34 lines, well under the 150-line budget.

## check-expertise.sh output (raw)

```
OK   .harness/expertise/harness-data-engineer.md
```

```yaml
VERDICT: PASS
DIGEST:
  headline: "distilled harness-data-engineer Expertise from own artifacts + 3 lead-relayed corrections — 5 entries added (2 patterns, 2 gotchas merged from 3 candidates), 2 findings rejected as non-generalizable, no repository-tier file created"
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched: [".harness/expertise/harness-data-engineer.md"]
  expertise_update:
    - op: add
      section: Patterns
      entry: "WHEN grading whether a verify block proves its claimed guarantee DO check every named file individually and classify each as per-item, file-global, or absent before writing \"no verify anywhere\" — a partial gap reported as total is the error a reader remembers, not the finding."
      why: "own SC-10 finding (per-item/file-global/absent table) merged with lead's correction that my 'no verify anywhere' totalized a partial gap — same workflow, one entry."
    - op: add
      section: Patterns
      entry: "WHEN reporting a scope count (e.g. files changed) DO show the breakdown that produced it, not just the total — a bare number is indistinguishable from a lucky guess against an independent recount, and the breakdown is what lets a reviewer verify or refute it."
      why: "lead relay: my bare '19 files, matches git diff --stat' was resolved against two independent breakdowns landing on 13; nothing backed the number."
    - op: add
      section: Gotchas
      entry: "WHEN a docstring or spec claims a function raises but the code path returns silently DO enumerate every real caller before flagging it as a live risk — if every caller pre-filters the case, it is a stale docstring, not a runtime hole."
      why: "lead relay: I called the caller situation an unresolvable discriminator; enumerating all three callers showed each pre-filters the case, converting a live-hole claim into a docstring fix."
    - op: add
      section: Gotchas
      entry: "WHEN a test fake for an external CLI matches only argv text DO check whether it also enforces the semantic shape — verb, response structure — a text-only fake lets a call that flips read to write, or returns a malformed response, pass silently."
      why: "own F2 finding: the gh test fake's Result triple checks argv strings only, never HTTP verb or response shape."
artifact: .harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-data-engineer-2026-08-19-12-eng.md
```
