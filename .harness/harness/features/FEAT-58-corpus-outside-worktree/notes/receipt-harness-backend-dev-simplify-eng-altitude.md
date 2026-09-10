# Altitude angle — FEAT-58-corpus-outside-worktree plan draft

BLUF: two real depth/authority gaps, both concrete and fixable without reopening settled scope.
The one that matters most: **SC-14 (D-5's negative half) has no task that actually discharges
it** — T-19's own intent falsely claims T-01 already holds it. The second: **T-10 risks a second,
independent implementation of T-09's "what counts as a branch claim" predicate** inside
`merge-gate.py`. Everything else examined (T-03/T-07/T-11/T-16's task depth, the five
repeated-rule candidates, T-12/T-03's placement of the sweep call and the scope guard, and three
of the four named residuals) is correctly scoped. Four findings total.

## Q1 — task depth

- **T-03** (worktree-state.py: five checks, six exits, two modes, scope guard, two test files):
  right depth. The five checks share one exit-code namespace that must stay pairwise-distinct
  (SC-15) and one mode-branch contract (SC-16); splitting them across tasks would fragment that
  single allocation and reopen the coordination D-10 already resolved. `leave`.
- **T-07** (.gitignore line + three-clause corpus-readable test): right depth. Byte-identity,
  cost/dirt, and refusal are three properties of one seam (the corpus read path), tested together
  against the same fixture. `leave`.
- **T-08**: see finding F2 below — not a depth problem in the sense of "should be split," but the
  bundled one-line `check-domain.sh:2150` fix ships with no test of its own. `briefing-row`.
- **T-11** (record correction + real-data test, two arms): right depth. The test's three clauses
  are direct consequences of the one correction it verifies; the arm-conditional third clause is
  already handled as a documented branch, not silent divergence. `leave`.
- **T-16** (unit half + integration half in one task): right depth. The plan already surfaces the
  BRIEF SC-21 `evidence: unit` vs. built-both-halves mismatch as an explicit open question in its
  own intent rather than silently reinterpreting the criterion — that is the correct handling of
  a decision that isn't the task-writer's to make. `leave`.

## Q2 — verify: pinning implementation over observable

Walked all 19 `verify:` lines and their intent-level assertions against the DoD's fixed
measurement modes (`ls | wc -l`, `find -type f | wc -l`, `git status --porcelain | wc -l`) and the
no-byte-figure/no-`du`/no-worktree-size rule. No task's `verify:` or intent rests on a byte
figure, a `du` value, or a worktree size — the only places those numbers appear (D-01's "5848
bytes", BRIEF's "168 MB", T-14's "3337/3807") are cited as evidentiary context in decision/intent
prose, never as an assertion. Message-content pins (T-08's "N of M", T-12/T-16's shared diagnostic
wording) are required by their own SC text and are the observable, not a substitute for one.
T-16 Part 1's static parse of a shim's own source text is appropriate for a five-line static shim
where the dynamic half (Part 2) is the actual behavioural proof. **Finding F1** is the one place a
`traces:` claim is not actually discharged by any verify at all, which is the "gone so abstract it
would pass for a wrong implementation" failure mode in its most literal form: the claim resolves
to nothing rather than to a weak assertion.

## Q3 — one authoritative statement per rule

- **Derived-not-literal include list** (D-08 authority; used by T-03/T-05/T-06): one authority.
  T-03 is the sole code home of the derivation; T-05/T-06 are tests against that one function, not
  competing restatements. `leave`.
- **`--verify` never repairs** (D-10; T-03/T-04/T-19c): one authority — the mode branch in
  `worktree-state.py`. Each citing site quotes it to pin the task's own contract, not to redefine
  it. `leave`.
- **Destroy-from-outside-the-worktree** (T-02/T-13/T-15): the mechanism is code (`destroy()` in
  the fixture module); the repeated prose is a warning restated at each site where an implementer
  could independently bypass it by hand-rolling teardown. That is load-bearing repetition, not
  drift risk — there is no independent spelling to diverge, only a reminder not to route around
  the one function that does it correctly. `leave`.
- **Fixture-is-synthetic** (D-11; T-02/T-14): same shape as above — T-14's restatement sits at the
  exact point (host-scale reproduction) where the temptation to violate D-11 is highest. `leave`.
- **Claim rule for the literal `none`** (D-06/T-09/T-10/T-11): this is the model case in the plan.
  T-09 states the rule once ("a row is a CLAIM only when..."); D-06, T-10 and T-11 all cite it back
  by name ("T-09's own claim rule", "T-09's claim rule does not treat as a claim") rather than
  restating an independent definition. Correct as drafted. `leave` — but see F3, which is about
  the rule's *code*-level authority in T-10, not its prose statement.

## Q4 — capability in the caller vs. the module it calls

- **T-12's `--repair` call in `post-merge-sweep.sh`'s body**: correct placement. The repair logic
  itself lives entirely in `worktree-state.py`; the body gains one delegating line to that
  module's own `--repair` interface, sequenced ahead of an unrelated pre-existing sweep. Deleting
  the added line removes only the call, not any hidden reimplementation — it was a pure
  delegation, not a bolted-on capability. `leave`.
- **T-03's SCOPE GUARD living inside `worktree-state.py`, not the three shims**: correct
  placement, and the deletion test argues for it directly. The guard must hold for all three shims
  *and* any bare invocation (a fresh clone, a CI runner, a manual `--verify`) — moving it into the
  shims multiplies it into three independent copies of a `harness_boundary.worktree_owner()` check
  that must all agree, which is exactly the drift risk D-03's "no shared body" already sidesteps
  differently (thin shims, deep module). `leave`.
- **T-10's index read inside `merge-gate.py`'s `feature_for`** — **F3**, below. `fold-in`.
- **`worktree-state.py` as a whole** (deletion test applied to the new module): passes. Deleting
  it returns the "at most one row" glob-blindness D-01's own rationale describes, and the module
  already has three concrete callers (the three shims) plus direct invocation — this is the "two
  adapters is real" bar cleared with margin, not a hypothetical seam. `leave`.

## Q5 — accepted residuals and their compensating controls

| Residual | Control named | Real? |
|---|---|---|
| D-01's new tracked index artifact | T-10 Part 3's regen-is-a-no-op + injected-drift test | Yes — concrete file, concrete assertion. `leave` |
| T-16's SC-21 `evidence: unit` vs. built-both-halves | Raised explicitly as an open question in T-16's own intent | Yes — correctly escalated rather than silently resolved. `leave` |
| SC-22 has no fixture | T-20's own `verify:` runs the real `git diff` and checks the artifact | Yes — T-20 *is* the control, not just a description of one. `leave` |
| Host-scale merge behaviour (3337/3807) proven by one manual run | "recorded" in T-14's intent / BRIEF's Verification gaps, with no file, heading or verify naming where | **No** — see F4. `briefing-row` |
| SC-14 (D-5 negative half: post-change failing set = baseline) | None named at all; T-19's intent asserts T-01 already covers it | **No** — see F1, the most serious finding in this angle. `fold-in` |

## Findings

**F1** — id `SC-14` (also touches T-01, T-19), severity **high**.
Summary: SC-14 ("run in a plain clone, the existing suites show no new failure — the failing set
equals the baseline set") traces only to T-01 in the `traces:` field, but T-01 runs "BEFORE ANY
BUILD TASK LANDS" (plan.yaml:287) and only *records* the pre-change baseline; it structurally
cannot compare anything. No other task re-runs `run-unit-tests.sh --kind unit`/`--kind
integration` after the change and diffs the extracted failing set against
`suite-baseline.md`. T-19's own intent (plan.yaml:1169) states "T-01 holds the negative half - the
suite's failing set unchanged" — which is not true of what T-01 does.
Cost: one of the DoD's seven binding items (D-5/REQ-05), which the BRIEF says "none may be folded
into another or deferred," ships with zero automated coverage of its actual claim, while the plan
narrates it as already covered — the worst version of an authority gap, a false attribution rather
than a silent omission.
Alternative: add the post-change comparison as its own checkable step — either a small new task
mirroring T-01's own extraction method (same failure-prefix matching, same set-equality
assertion, printing the symmetric difference on mismatch), or fold it into T-20 since T-20 already
"RUNS LAST" and grades the whole commit range. Also correct T-19's intent text, which currently
misdescribes what T-01 discharges.
Recommendation: `fold-in`.

**F2** — id `T-08`, severity **med**.
Summary: T-08 Part 2 (`check-domain.sh:2150`'s one-line `linked_worktrees()` fix) has no test of
its own; both of T-08's test files (`test-check-state-expected-dirs.py`,
`test-check-state-scope.py`) target Part 1 only (`check-state.sh`'s audit choke point).
Cost: a real defect fix (D-02's own text: "the :2150 defect is nonetheless real") ships with no
automated proof it works, and a future edit could reintroduce the bare `except: pass` with
nothing red to catch it.
Alternative: add one case — either its own tiny unit test or a fourth case in
`test-check-state-scope.py` — asserting `linked_worktrees(worktree_owner(root)[1] or root)`
returns the worktree in the STATE.md-budget sweep for a fixture whose `.git` is a file.
Recommendation: `briefing-row`.

**F3** — id `T-10`, severity **med**.
Summary: T-09 defines the branch-claim predicate once, as part of `collisions(rows)`. T-10 needs a
different query over the same rows — owners for one specific branch — and its intent ("populate
owners from the index rows using T-09's own claim rule") does not require importing a shared
predicate from `feature-index.py`; it can be satisfied by `merge-gate.py` re-implementing the
same "non-empty and not the literal `none`" check inline.
Cost: the one semantic rule D-04's whole mechanism depends on (what counts as a claim) would then
have two independent implementations that must be kept in lockstep by hand; a future refinement
(e.g., a second non-claim sentinel) edited in `feature-index.py` and missed in `merge-gate.py`
silently reopens exactly the enforcement gap D-01 exists to close, at the one place — the merge
gate — where it matters.
Alternative: `feature-index.py` exports a small pure predicate (`is_claim(branch)` or
`owners_for(rows, branch)`), imported into `merge-gate.py` by the same import-by-path precedent
already used for `worktree_terminal.py`'s import of `feature-worktree.py`'s helpers. Seam: "what
counts as a branch claim over an index row." Interface: a pure function, no state, no adapter
lifetime to name — it is a stateless predicate, not a constructed adapter.
Recommendation: `fold-in`.

**F4** — id `T-14` (D-01/host-scale residual), severity **med**.
Summary: unlike every other named residual in this plan, the compensating control for "host-scale
merge behaviour is proven by one manual run, not a runner" is not anchored to any file, heading,
or verify clause — T-14's intent and BRIEF's Verification gaps both say only that the command is
"recorded," without naming where.
Cost: nothing in the plan can notice if that manual run is skipped; every other accepted residual
in this plan (the index's staleness class, SC-22's inspection status) has a concrete, checkable
sink and this one does not.
Alternative: name the sink explicitly — e.g. "record the command and its verbatim output in this
task's own B-7 receipt under a fixed heading" (the receipt convention T-14 already produces per
`harness-tdd-enforcement`), or a small committed note mirroring T-01/T-20's `key: value` shape.
Recommendation: `briefing-row`.

## Empty ground covered

T-12's placement of the `--repair` call, T-03's scope guard placement, and the `worktree-state.py`
module's existence as a whole all pass the deletion test cleanly and needed no finding. The four
repeated-rule candidates in Q3 that are pure warning-prose (destroy-from-outside,
fixture-is-synthetic) are load-bearing repetition, not drift risk, and needed no finding either.
