# Goal-check — BUG-151 drafted plan vs issue #151

**DOES THIS PLAN DELIVER THE OPERATOR'S STATED INTENT? — YES-WITH-FINDINGS.** All four findings are
advisory; none means the plan as drafted fails to close the defect. Two are worth one edit each
before signature (F-1 med, F-2 low).

## 1. Intent coverage — complete, traced to task steps

The operator's defect is "delete the 9 chars `fails += ` from any one line → block prints FAIL, suite
exits 0". Closure is structural, not a REQ restatement:

- The deletable characters cease to exist: `plan.yaml:149` T-02 step 2 deletes all 21 sites — the 20
  statements at `test-check-domain.py:5211-5230` and the `+ run_bug1305_cases()` term at `:5231`.
- Reachability stops depending on a hand-written line: T-02 step 4 (`plan.yaml:158`) discovers
  `run_*` module globals in definition order.
- A print/return disagreement now trips: `_aggregation_verdict` (T-01 step 4, `plan.yaml:114`) plus
  T-02 steps 5-6, which also cover the CASES loop at `:5192-5206` — the same exposure, and the plan
  is the only document that noticed it.
- Step 6 returns `fails + len(problems)`, so a safeguard trip alone exits non-zero.

Residue: one, and it is REQ-02's, not the issue's — see F-3.

## 2. The operator's option analysis — the operator's premise fails; the orchestrator's holds

The issue says option 2 (assert the arithmetic) is the only option catching **both** directions.
Against the file, it catches only one. Every block couples its own print to its own return inside one
function (`:5176-5179`: `failures += 1`, `print("FAIL …")`, `return failures`); the defect lives at
the aggregation site, not in the block. A block that is **never called** prints nothing and returns
nothing — printed 0 == counted 0, the arithmetic agrees, and nothing fires. Catching that direction
needs an expected total the file does not derive from itself; a hardcoded one is exactly the
"remember to edit a second place" the goal forbids (BRIEF:23-24), and it would not rise for a block
nobody called. So D-02's discovery is not redundant and the plan is **not over-built** on this axis.

The plan therefore overturns the issue's stated conclusion — legitimately, but **the departure is
nowhere named for the signer**. `plan.yaml:36-38` (D-02 `because:`) states why enumeration cannot
notice an unenumerated block, which is the reason, but never says "issue #151 concluded option 2
alone suffices; it does not". BRIEF `## Constraints:40` cites #151 only as naming the suite. **F-2.**

## 3. Scope fidelity — faithful

The issue asks that other suites "should be checked before generalizing" — a precondition on
generalizing, not a deliverable. BRIEF:41-44 records the check and declines to generalize, which
satisfies the wording. Measured here: `grep -c '^    fails += run_'` = 13 in
`test-validate-digest.py`, 8 in `test-bash-write-guard.py` — so the BRIEF is right that the shape is
**identical**, and the issue's own guess ("other bin/ suites use different shapes") is falsified.
That contradiction is visible in the BRIEF; the propagation decision is out of scope by ruling.

## 4. Cost proportion — the "net deletion" claim is true only for T-02 in isolation

Deletion side verified by reading the file: 20 statements (`:5211-5230`), the return term (`:5231`),
the 6-line composite (`:5182-5187`), the false 4-line comment (`:5207-5210`) whose last sentence
claims an assertion that appears nowhere in `main()`, plus T-01's one added line ≈ **31 lines out**.
Added as specified: tee class, verdict helper, six-case synthetic block, discovery/capture/problems
loop ≈ **60-70 lines in** [INFERENCE — sized from the spec, not from code]. Honest net for the
ticket: an **addition of roughly +30 lines**. `plan.yaml:142` says "This task is a net DELETION" and
is scoped to T-02 (≈ -31/+12), which is defensible; the ticket-level framing is not. **F-4.**

## 5. Verifiability — every SC executable as written

- T-01 `verify:` (`plan.yaml:53`) runs and **discriminates**: on the current tree it exits 1 with
  `AttributeError: module 'tcd' has no attribute '_aggregation_verdict'`, in 1.18s, running no cases
  (the `__main__` guard at `:5234` holds).
- T-02 `verify:` (`plan.yaml:138`) costs 38s + ~1s, inside its 60s budget. `len(blocks)==24` alone is
  non-discriminating — the pre-change file already has 24 `^def run_` — but the conjunction
  `'run_bug1305_cases' not in blocks` and `398<=ok` cannot both hold pre-change, and deleting the
  composite without discovery drops the three sub-blocks' `ok` lines below 398. It discriminates.
- SC-02 `verify: inspection` is **honest, not an escape**. Any behavioural test would enumerate
  `run_*` globals and assert each ran — the same `vars(m)` scan as the implementation, i.e. the loop
  restated. The alternative is a source-text assertion, which is worse. T-02's verify incidentally
  supplies partial behavioural evidence: `ok>=398` with the composite gone means the three
  sub-blocks ran while named nowhere.
- SC-04 is genuinely automated: the diagnostic prints at column 0 with the FAIL prefix (T-02 step 6),
  so T-02's `bad==0` covers "no safeguard diagnostic on a green run".
- SC-03 is gradeable — the sha256 protocol (T-01 step 0, `plan.yaml:60-67`; T-02 step 8a,
  `plan.yaml:184-187`) is a real equality, and the exclusion key `[bug151-selfcheck]` matches the
  output format T-01 step 2 mandates (`plan.yaml:100`). **But there is a hole: F-1.**

## Findings

1. **F-1 · med · SC-03's baseline is unrecoverable if T-01 is retried.** T-01 step 0 says the
   baseline "is only obtainable now" (`plan.yaml:60-62`) but gives no recovery path. A second T-01
   spawn — a retry after a partial edit, the common case — measures the already-edited file, records
   a sha over a name set that includes `[bug151-selfcheck]` entries, and T-02 then compares against a
   corrupted baseline: SC-03 either fails spuriously or "passes" an equality that proves nothing.
   Recovery is also non-obvious because the module anchors `ROOT` off its own `__file__`
   (`plan.yaml:71-73`), so a `/tmp` copy does not resolve. Fix, one sentence in step 0: if the file
   is already modified, write `git show <base sha>:tests/integration/test-check-domain.py` to a
   sibling path **inside `tests/integration/`**, run that, then delete it.
2. **F-2 · low · the departure from the issue's conclusion is invisible where it is signed.** The
   plan adopts option 1 *and* option 2 where the issue concluded option 2 alone catches both
   directions. The reason is derivable from D-02 `because:` (`plan.yaml:36-38`) but never stated as a
   departure, and BRIEF:40 does not mention the option analysis. The operator signs a plan that
   overrules their own analysis without being told. Fix: one clause in D-02's `because:`.
3. **F-3 · low · REQ-02 is delivered only for blocks that honour the `run_` prefix.** Discovery keys
   off the name (`plan.yaml:158-164`), so a future block named `check_foo_cases` is defined, never
   run, and nothing notices — the mirror-image defect re-entering through a naming slip. The
   convention is load-bearing and recorded only as BRIEF prose (`BRIEF.md:51-53`); two non-underscore
   helpers already exist. Strictly weaker than today's failure mode, so accept-and-document is
   proportionate; do not add a gate.
4. **F-4 · info · "net DELETION" overstates the change at ticket level.** True for T-02 alone; the
   ticket is a net addition of ~30 lines. Only matters if the phrase is quoted at signature as a cost
   argument.

## Not re-raised (resolved by ruling)

`approval: {status: pending}` without `approved_by`/`date` is plan-merge.py's bootstrap shape.
Propagation to `test-validate-digest.py` / `test-bash-write-guard.py` is out of scope by decision.

## Advisory, no finding

T-01 step 1's red measurement (`plan.yaml:69-80`) serves no REQ or SC: D-01's default (agreement of
zeroness) already satisfies REQ-01 — the harmful form is print-FAIL/return-0 — and SC-01 case (f) is
written to assert whichever invariant is in force. It is the one place a ~30-line fix buys a probe it
does not need (rule 6). Harmless if kept, cheaper if dropped.
