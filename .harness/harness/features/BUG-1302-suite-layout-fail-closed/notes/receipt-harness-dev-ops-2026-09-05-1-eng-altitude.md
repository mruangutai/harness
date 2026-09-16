# ALTITUDE angle — BUG-1302 plan draft — receipt

BLUF: two real findings, both cheap to apply without reopening D-02: merge T-01/T-02 (identical
mechanical shape, chained only for an `import ast` reuse), and make the "demonstrate the red"
obligation durable for SC-02/04/06/07/08. The three remaining items (right-home, one-authority,
accepted-residual-control) checked out — either already correctly designed or out of scope by the
feature's own file-lock constraint — and are `leave`/`briefing-row`.

## 1. Decomposition (T-01..T-04 chained over one file)

T-01 and T-02 are the same operation on adjacent pure functions: strip a dead conjunct/comparison,
pin verdicts with a literal corpus, add an AST absence check (plan.yaml:34-134). T-02's
`depends_on: [T-01]` (plan.yaml:88) exists only because its intent says "the ast module imported by
T-01" (plan.yaml:122) — a reuse of one import line, not a data or ordering dependency between the
two fixes (they touch disjoint functions, `_is_inside_tests` vs `_literal_key_present`). That is a
merge candidate, not a real precedence.

T-03 and T-04 are a different shape each (case-11 fail-closed conversion; exception-guarded read
plus a new fixture case) and should stay separate — merging either into T-01/T-02 would put an
unrelated diagnostic burden on one verify command, working against the parallel simplify pass'
"one fix, one concern" instinct.

**Merge: T-01 + T-02 → T-01.** `traces: [REQ-01, REQ-02, REQ-06]`. `depends_on: []` (T-01's
original). T-03's `depends_on` becomes `[T-01]` in place of `[T-02]`; T-04 unchanged (`[T-03]`).
Merged `verify:`, every grep clause from both preserved, one `python3` run instead of two:

```
python3 tests/unit/test-suite-layout.py && grep -q "b5 corpus: _is_inside_tests verdicts unchanged" tests/unit/test-suite-layout.py && grep -q "b5 structural: no unreachable dotdot comparison" tests/unit/test-suite-layout.py && grep -q "b4 corpus: _literal_key_present verdicts unchanged" tests/unit/test-suite-layout.py && grep -q "b4 structural: the tautological conjunct is absent" tests/unit/test-suite-layout.py
```

Cost of leaving it split: one extra main-session dispatch (context load, file re-read, receipt) for
a task whose only reason to exist separately from T-02 is which of two adjacent functions it edits.
**fold-in**

## 2. Right home (corpora + AST self-inspection)

B4_CORPUS/B5_CORPUS and the three AST self-parses (T-01/T-02/T-03) pin invariants over
`_is_inside_tests`/`_literal_key_present` — functions that are private to the test file, not
exported from `suite_layout.py` (confirmed: neither name exists in `suite_layout.py`, checked by
grep-equivalent read of the module during BRIEF review). They aren't a capability bolted onto a
caller that belongs in the callee; they're a test file asserting invariants about its *own* helper
code. A shared-module home would need a third file, and the BRIEF's own constraint list closes that
door: "No file outside these two is edited ... read-only for this feature" (BRIEF.md:139-140). Given
that lock, self-parsing is the only altitude available, not a bolt-on. **leave**

## 3. One authority

Checked for a rule repeated across task intents that could drift. The plan already centralizes the
one repeatable mechanism correctly: T-01 introduces `import ast` and the `Path(__file__).read_text()`
parse; T-02 says "the ast module imported by T-01" (plan.yaml:122) and T-03 says "the ast parse
already present in the file" (plan.yaml:172) — neither re-states the setup. The one phrase every task
intent repeats is "before committing, demonstrate the red, then revert" — five near-identical
closings — but each names a *different* concrete mutation (restore a tuple, restore a conjunct,
patch a call site, revert a guard, retag a fixture), so this is task-specific instantiation of one
BRIEF-level rule (BRIEF.md:45-46: "each new assertion must be demonstrated failing"), not five
independent copies of the same fact free to drift apart. No consolidation needed beyond what item 5
proposes for the *evidence* that obligation leaves behind. **leave**

## 4. Accepted residual and its compensating control (B-6 / D-02)

Verified against the file, not just BRIEF prose: `hygiene_uncertified` (test-suite-layout.py:488-495,
called unconditionally at line 562) and `_certify_pattern` (471-485) do run every time case 11 runs,
independent of whether `select_control_candidate` returns a candidate — the BRIEF's claim that
coverage "does not rest on the positive control alone" (BRIEF.md:158-159) is true. But the two checks
prove different things: the positive control (line 553-557) exercises `offenders()` against a real
constructed path to show a live, counted-but-unrefused file is actually flagged; `hygiene_uncertified`
only certifies that each *configured detect pattern's text* is structurally safe (scoped inside
`tests/`, or carrying a literal key an adversarial-basename corpus can't defeat) — it never runs a
real path through `offenders()`. So it is a real, unconditional, complementary control, not a
redundant restatement of the same fact, but it would not by itself catch every regression class the
dynamic control catches (e.g., a config change that makes an already-certified-shaped pattern start
counting a directory that happens to contain a disguised non-test file — `hygiene_uncertified` is
blind to that because it certifies pattern shape, not live membership). The residual is real, correctly
named, and the control is genuinely unconditional — but the BRIEF's phrasing ("does not rest on the
positive control alone") could be read as stronger equivalence than the code delivers. Not a case for
reopening D-02's remedy choice — a one-clause precision fix to the accepted-risk paragraph, naming
what `hygiene_uncertified` does and does not prove, closes the gap without touching remedy or scope.
**fold-in**

## 5. The unrecorded red

Every task's falsifiability evidence for SC-02, SC-04, SC-06, SC-07 and SC-08 is a human-run mutate
→ observe-FAIL → revert cycle with no artifact — the record lives only in whoever ran it, at the
moment they ran it. Recommend: one durable file appended to as each task executes,
`notes/red-demonstration-2026-09-05.md` under this feature's directory, one dated section per task
(T-01 merged/T-02/T-03/T-04/T-05) pasting the literal mutated snippet and the FAIL line(s) it
produced before the revert. SC-02, SC-04, SC-06, SC-07 and SC-08 each already state "verify:
automated — ... exits 0; restoring/reverting X makes it exit 1" (BRIEF.md:66-67, 80-81, 93-94,
100-101, 111) with nothing citing where that exit-1 observation is kept; add one `evidence:` line to
each of those five criteria citing this file's path and dated section. This does not reopen scope —
it adds a record of an obligation the plan already imposes, on every task, without changing any
task's fix. **fold-in**

## Confirmations

Read-only run: wrote nothing under `tests/`, did not touch `plan.yaml` or `BRIEF.md`, ran no test
suite or formatter. All reads were `read`/`grep`-equivalent inspection of
`tests/unit/test-suite-layout.py` at the feature's checked-out HEAD.
