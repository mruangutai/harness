# Receipt — harness-backend-dev — BUG-1016 plan-simplify, SIMPLIFICATION angle

**Angle result: 5 findings (all advisory, none substance, none blocking).** Plan-surface only; every finding is a duplicated statement of one fact that can drift. No settled item reopened (blank-entry preservation, node:fs fixture removal, permitted success cache, D-01, DEC-174/250, BUG-2003 are all kept; only their repeated *wording* is flagged). No edits made.

Paths below: `plan.yaml` and `BRIEF.md` under the feature dir. Line numbers are the raw file lines.

## Findings

### S-1 — T-02 re-lists the whole T-01 contract (kind: form)
- File/line: plan.yaml:124 (T-02 intent, second paragraph); sources BRIEF.md:41-44, plan.yaml:98-106.
- Summary: DEC-251's content is specified a third time, clause by clause (seven tools, six fields, entries, defaults, predicate, tilde/scheme, lexical, silent, authority, no-match, pre/post, URI policy, cache).
- Cost: three lists (BRIEF constraints, T-01, T-02) must change in lockstep. If T-01 tightens a clause, T-02 silently documents the old one. The documentor also gets nothing a reader of SC-07 lacks.
- Alternative: T-02 says "DEC-251 records the contract exactly as landed by T-01 (the BRIEF SC-07 list and Constraints)" and keeps only what is new to a decision record: origins #1016/#1570, lineage DEC-174/250/233, the two rejected alternatives, and the unchanged hosts/Bash/OMP statement.

### S-2 — Blank-entry/byte-for-byte rule restated three times inside T-01 (kind: form)
- File/line: plan.yaml:101 ("Preserve every excluded entry byte-for-byte, including empty and whitespace-only…"), plan.yaml:102 ("Explicit empty or whitespace-only … remain byte-for-byte unchanged"), plus BRIEF.md:19, 23, 41 and plan.yaml:124.
- Summary: the preserve-excluded-entries rule is already part of the predicate paragraph (101); 102 repeats it for the default-path case.
- Cost: two spellings of the same invariant in adjacent paragraphs ("excluded entry" vs "explicit empty/whitespace entry"); a later edit to one leaves the other contradicting it.
- Alternative: keep the preservation sentence only in 101; shrink 102 to the omitted/undefined/null default for grep/glob/ast_grep, "no required path invented", and non-path fields preserved. The test paragraph (105) is a distinct artifact and stays.

### S-3 — Duplicate "no node:fs fixture" instruction (kind: form)
- File/line: plan.yaml:97 ("do not add a redundant node:fs main/worktree read/write fixture") and plan.yaml:107 (last sentence, "…without exercising Node's filesystem separately").
- Cost: the same prohibition is spelled twice, once with a named API and once without. The PF-167168 resolution already records it.
- Alternative: delete the 107 sentence; 97 states it and it is the only spelling that names the thing excluded.

### S-4 — "Cache permitted, not mandatory" disclaimer repeated across four places (kind: form)
- File/line: BRIEF.md:43, plan.yaml:100 (last sentence: "A success cache is permitted, not a new mandatory caching subsystem"), plan.yaml:106 ("If caching … Whether caching or not"), plan.yaml:124 ("without claiming caching is mandatory").
- Cost: the permission is settled; restating the disclaimer in T-01 and T-02 adds no constraint beyond BRIEF.md:43 ("may be cached") and creates a place for the wording to diverge (e.g. one saying "run" and another "session").
- Alternative: BRIEF.md:43 is the single authority. Drop the disclaimer sentence from plan.yaml:100; in T-02 replace the sentence with "describe the cache only as implemented". Keep the conditional assertions at 106; they are tests, not restated policy.

### S-5 — Main-session-direct rationale stated in four spellings (kind: form)
- File/line: plan.yaml `lanes.rows` reasons (~lines 59-65), T-01 `execution_reason` (~line 93), plan.yaml:96 ("Execute directly in the main session under DEC-174, never through a governed team build. Own only …"), BRIEF.md constraint 1.
- Cost: `execution_mode: main-session-direct`, the lanes row and `files:` already carry this; the intent sentences (plus the "Own only X and Y" that duplicates `files:`) restate it and can drift if a surface is added to `files:` but not the prose.
- Alternative: keep `execution_mode`/`execution_reason`/lanes as the record; cut the first two intent sentences' direct-execution clause and the file list from 96, retaining only "Work only in <worktree>" and the do-not-change list (a real constraint not stated elsewhere). Same trim for the "Own only …" sentence at plan.yaml:123.

## Not flagged (checked, earned their place)
- Test paragraphs 105-107 re-touch behaviors named in 98-104 but each is the oracle for a distinct SC; merging would weaken assertions.
- D-01 vs DEC-251 pointer: single decision, one reference.
- Cache conditionals at 106: settled, kept.

```yaml
VERDICT: PASS
DIGEST:
  headline: Simplification found 5 advisory plan-surface duplications (T-02 re-lists T-01 contract, repeated blank/byte-for-byte, node:fs and cache disclaimers, DEC-174 rationale) and no structural complexity.
  tests_added: 0
  suite: n/a
  task: none
  blocked_on: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/receipt-harness-backend-dev-plan-simplify-eng-simplification.md
```
