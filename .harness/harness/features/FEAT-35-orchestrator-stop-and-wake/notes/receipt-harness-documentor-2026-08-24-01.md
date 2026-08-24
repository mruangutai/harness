# Receipt — harness-documentor — FEAT-35 S1 — 2026-08-24-01

**DEC-201's index ruling is now 29 words and the suite is green.** One line changed:
`.harness/harness/docs/DECISIONS-INDEX.md` line 219, only the text right of ` :: `.

## What changed

New ruling: "An orchestrator never waits: every dispatch ends its turn and the platform wakes it;
on waking it verifies claims against disk and weighs its context against an advisory threshold."

29 words, counted the way the gate counts them — `len(stripped.split())` on whitespace
(`.claude/skills/harness/bin/test-gen-decisions-index.py:438`), cap `> 30` at line 439. Punctuation
rides along on its token, so `waits:` and `it;` are one word each.

All three mandated clauses survive, in the mandated order: never-waits/platform-wakes,
verify-against-disk, advisory-context-threshold. Cut was the provenance clause ("measured across
three probes against sub-agent documentation that says the opposite"), which the entry carries in
full at `.harness/harness/docs/DECISIONS.md` under "The evidence is MEASUREMENT" — DEC-158's
index-is-a-filter / entry-is-the-authority split.

"treats a reported completion as a claim … re-reads disk" compressed to "verifies claims against
disk". Faithful to the entry's (a)+(b): re-reading disk exists *so that* a reported completion can
be confirmed, so the compressed form asserts nothing the entry does not.

## Verification — actual output

- `python3 .claude/skills/harness/bin/test-gen-decisions-index.py` → exit 0, 9 `ok` lines, 9 lines
  total, zero `FAIL`. Includes `ok - test_committed_index_is_complete_and_within_budget`, the row
  that was red.
- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` → no output, exit 0. The generator
  reproduces the committed file byte-for-byte, confirming its docstring (lines 13-14): everything
  right of ` :: ` is hand-written and preserved verbatim. Editing in place was the right location.
- `git diff --stat` → 1 file, 1 insertion, 1 deletion; `git diff -U0` shows a single hunk `@@ -219 +219 @@`.
  Anchor `@6800`, tags, and the seven `refs:` are untouched — they are left of ` :: ` and the
  generator regenerates them identically.

Not committed, not pushed. `DECISIONS.md` and `.claude/skills/harness/SKILL.md` untouched.

## Open

None blocking. Advisory: the entry's own "open measurement" (does a stopped parent survive past the
600s watchdog while its child runs) is recorded as open in DECISIONS.md and is deliberately absent
from the row — a filter carries the ruling, not its caveats.
