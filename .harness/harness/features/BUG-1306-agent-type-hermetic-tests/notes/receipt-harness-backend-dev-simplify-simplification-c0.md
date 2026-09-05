# SIMPLIFICATION angle — BUG-1306 hermeticity diff (c0)

**Verdict: two findings, both applyable, neither blocking.** All factual claims in the added
comment and docstring hold against the code — no dead or wrong claims found.

## Fact-check (criterion c)

- Module comment (lines 35-41) claims `cmd_sign_approval` reads `HARNESS_AGENT_TYPE` at
  `plan-merge.py` line 1188 and exits 10 for any non-empty value: **verified true**
  (`plan-merge.py:1188-1189`).
- Comment claims the pop covers `run_apply`, `run_verb`, and raw `Popen` sites with no
  per-call-site rule: **verified true** — `run_apply` (line 138) and the two `Popen` calls
  (lines 315, 319) pass no `env=` kwarg, so all inherit `os.environ` post-pop; `run_verb`
  defaults `env=None` (line 145), same inheritance. One process-wide pop at import (line 41)
  covers all four call shapes.
- `run_verb` docstring claims `env=None` is "hermetic on its own": **verified true** — the pop
  already ran at import before any case executes.
- Docstring claims an explicit mapping is needed only when a case wants a specific identity:
  **verified true** against the two cases that pass one — `case_1103_sign_approval_...` (line
  1117) injects `HARNESS_AGENT_TYPE="harness-pm"` to test the positive-refusal path; its
  negative control (line 1140) explicitly filters the key out (redundant given the global pop,
  but harmless and self-documenting for that specific test's intent). Both match the docstring.

No clause found dead or incorrect.

## Findings

**F1 — narration instead of present fact.**
`tests/integration/test-plan-merge.py:37-38`: "a Harness agent's own shell carries that
variable, so without this pop 13 checks across six cases fail for the agent and pass for a
human" narrates the counterfactual (what breaks if you undo this change) rather than stating
the present invariant the tests rely on. Cost: the "13 checks / six cases" figure is not tied
to any assertion or count — as cases are added or removed the number silently goes stale with
nothing to catch it, and a future reader can't tell if it's still accurate. Alternative: state
the fact the pop guarantees present-tense, e.g. "removed here so `cmd_sign_approval`'s identity
check never fires against this process's own ambient identity, regardless of who is running the
suite" — drop the specific pass/fail tally. Comment-only, same file, no assertion touched:
**apply candidate**, not a backlog item.

**F2 — one invariant asserted twice through different spellings (criterion a).**
`tests/integration/test-plan-merge.py:41` (the pop) and `:148-151` (`run_verb`'s docstring)
both assert "the ambient `HARNESS_AGENT_TYPE` is already gone by the time any subprocess
runs" — the module comment states it as the reason for the pop, the docstring restates it
locally as the reason `env=None` is safe. Cost: two independent spellings of one fact that can
drift apart — if the pop is later narrowed (moved into a function, made conditional, scoped to
one call site) nothing forces the docstring's "already removed at module import" to be
revisited, and it would then quietly overclaim. Alternative: have the docstring cross-reference
the module-level pop instead of restating its conclusion, e.g. "an explicit mapping is needed
only when a case wants a specific identity — see the module-level pop above for why `env=None`
is otherwise safe" in place of re-deriving "hermetic on its own" from scratch. Comment-only,
same file, no assertion touched: **apply candidate**.

## Not raised (per contract)

- The `plan-merge.py` line-1188 citation is on the LEAVE list — not re-raised.
- No new test proposed (D-05 declined this already).
- No change to `plan-merge.py` or any second file proposed (D-01, D-03).

## Scope discipline

Read-only on source; no repo file edited. Read only `test-plan-merge.py` (module header,
`run_verb`, two `Popen` sites) and `plan-merge.py:1158-1191` to verify the line-1188 claim —
nothing else opened.
