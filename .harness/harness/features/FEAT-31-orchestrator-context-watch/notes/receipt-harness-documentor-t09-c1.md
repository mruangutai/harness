# T-09 receipt — DEC-198 recorded, index regenerated

**PASS.** `DEC-198` appended to `.harness/harness/docs/DECISIONS.md` (heading at line 6398, 57 added
lines) and `.harness/harness/docs/DECISIONS-INDEX.md` regenerated with the script; its DEC-198 row is
at index line 216. Full `verify:` block green.

## The decision number, re-derived (not adopted)
`grep -o '^## DEC-[0-9]*' .harness/harness/docs/DECISIONS.md | sed 's/## DEC-//' | sort -n | tail -3`
→ `195 196 197`. Highest **entry** at HEAD `0901c23` is `## DEC-197` (line 6362, last entry; file was
6396 lines). So **198** is next; no gap backfilled.
Reconciliation of the two conflicting numbers in the dispatch: `grep -c '^### DEC-'` returns **25** —
those are amendment sub-headings, not entries, which is why an h3 grep produced 194. And DEC-197
landed after `6f651f1`, which is why the intent's "196 was highest" is stale rather than wrong.

## Facts verified at source before writing (both check out, with one precision caveat)
- **Default 200000 when absent:** `context-watch.py:56` `DEFAULT_CONTEXT_WARN_TOKENS = 200000`,
  returned on every miss path — file missing/unreadable/not JSON (`:96-102`), no `budgets` dict or key
  absent (`:104-109`), value not a number or a bool (`:111-116`).
- **DEC-148 names the figure — as "200k", for a different metric.** DECISIONS.md line 3563 reads
  `budgets.context_per_turn_tokens` (default 200k), an **average cache-read-per-turn** threshold.
  200k = 200000, so the figure checks out; the *metric* differs from an orchestrator context size.
  Not a FAIL — a notation/metric distinction, and DEC-198 states it explicitly rather than claiming a
  like-for-like carry-over.
- **`budgets` is NOT new** — `.harness/harness.json:165-166` and template `:139-140` already hold
  `max_total_cycles`/`max_total_runs`. Only the leaf is new (project `:169`, template `:143`, each
  with a `_..._rationale` sibling). The entry says so.
- **`upgrade-config.py` byte-unchanged:** `git diff --stat` on it is empty; **zero** occurrences of
  `budgets` in the file. Anchors re-derived by grep: `PRESERVE_ALWAYS:47`, `NEVER_ADD:53`,
  `TEMPLATE_ONLY:56`, `def merge:64`, add branch `:79-83`, recursion `:87`.
- **Only one propagation path is tested:** `test-upgrade-config.py:215` fixture carries
  `budgets: {}`, so case 8 exercises the recursion branch only. The add branch (no `budgets` block at
  all) is untested for this key. The entry says "proven for the first shape, inferred for the second".
- **Not guarded:** no assertion anywhere in `test-upgrade-config.py` that an operator's existing value
  survives. Recorded in the entry as resting on `merge()`'s contract, not on a test.

## verify: block — each line, exit status and actual count
The string was cross-checked against plan.yaml lines 657-662: identical.
1. `grep -c orchestrator_context_warn_tokens .harness/harness/docs/DECISIONS.md` → **3**, exit **0**.
2. `grep -c ... DECISIONS-INDEX.md` → **1**, exit **0**.
3. `python3 .claude/skills/harness/bin/test-gen-decisions-index.py` → exit **0**, all cases `ok`.
Also: `run-unit-tests.sh --check-kinds` exit **0**; `gen-decisions-index.py --stdout | diff -` clean
(index is a mechanical regeneration, DEC-141's law).

## Two things the next reader needs
1. **The index row had to be hand-authored, and it has a 30-word cap.** A fresh entry regenerates as
   `⚠ RULING PENDING`; the ruling after ` :: ` is hand-written and preserved. My first ruling was 51
   words and `test-gen-decisions-index.py` FAILED on the cap. Final ruling is 27 words and names the
   key literally, which is what makes verify line 2 non-zero.
2. **`check-state.sh` exits 1, and none of it is mine:** FEAT-26's BRIEF not approved, and INV-26
   board drift on FEAT-31 T-01/T-02 (plan says done, board reads Building). Pre-existing; no
   DECISIONS-related violation. Tree left dirty, nothing staged, nothing committed, HEAD unmoved.
Dispatch said the tree carried uncommitted user edits to plan.yaml/feature.json/STATE.md/
test-upgrade-config.py — at spawn `git status --short` was **clean**; those had already landed. I
reverted nothing.
