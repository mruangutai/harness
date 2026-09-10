# Plan panel 2 · scope · FEAT-58-corpus-outside-worktree · cycle 1

**FAIL, severity_max high.** The cycle-3 batch genuinely answered all six high findings from the
prior panel (F-01..F-06) plus F-07, F-08, F-09 — I re-verified each against the written plan.yaml
text and, for F-06, against the actual `merge-gate.py` source. But N-11 PART1's new hardlink-scan
refusal recreates a fail-open on the exact class this feature exists to close, and it is invisible
because nothing in N-11's own test list exercises the path that trips it. Four low/med findings
(F-10..F-13) were never in the operator's Q1-Q4 batch and remain genuinely unfixed; the plan is
honest about this (disposition stays `open`), so this is not the "told answered, wasn't" trap —
just work still owed before signature settles all thirteen.

Pinned to worktree HEAD `5dda443b13b2b02e21e629f95416e177ba2f1274` (matches `git rev-parse HEAD`).
This is a plan-phase read: `reviewed: plan:.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml`, `code_grade: n_a` (no code exists yet to grade).

## Must-fix

**NEW-01 (high) — N-11 PART1's hardlink-scan refusal is unspecified at the exact place it needs
specifying, and the surrounding code's own documented contract turns that gap into a fail-open.**

Lands on N-11 PART1 (`_hardlink_plan`), REQ-03/REQ-08, SC-15. Chain, each link read at source:

1. N-11 PART1 (plan.yaml) requires: "enumerate the candidate plan.yaml paths at the OWNER root
   through `feature_corpus`, and REFUSE when the corpus root cannot be resolved."
2. N-10 PART1 requires `feature_corpus.corpus_root()` to RAISE a named error when unresolvable —
   "Never return None, never fall back." There is no non-raising failure mode to check for.
3. `check-domain.sh`'s current `_hardlink_plan` (`:1907-1922`, read at HEAD) wraps only
   `os.stat(_claimed_abs(path))` in `try/except (OSError, ValueError)`. The `glob.glob(...)` line
   N-11 must rewrite to call `corpus_root()` sits **outside** that block, with no handler of its
   own.
4. `_plan_route`'s sole caller in the file is the bare module-level statement
   `_reached_plan = _plan_route(target) if target else None` (`:1949`, read at HEAD) — no
   `try/except` anywhere near it.
5. The file's own header, line 14 (read at HEAD): **"Only exit 2 blocks — exit 1 is a
   NON-blocking error and the write proceeds."** This is not incidental — the file elsewhere
   (`:195`, `:766`) explicitly reasons about this exact contract, once even naming the general
   shape as "the same failure direction as issue #103."

An unresolved corpus root during a hardlink-scan write therefore raises uncaught, Python exits 1
by default, and by this file's own documented rule that is non-blocking: **the write the guard
exists to deny goes through.** This is the identical fail-open shape SC-15 was written to close,
reintroduced at the one call site the plan never tests.

Confirm the gap is real, not hypothetical: N-11 PART4/PART5 name four test cases — hardlink denied,
positive control, branch-gate allows, branch-gate denies for a nonexistent flow. None exercises an
unresolvable corpus root against the hardlink scan. Contrast with the two sibling widenings, both of
which the plan **does** force through a named test: N-07 PART4(d) ("THE UNRESOLVABLE CORPUS ROOT ...
assert the gate emits the DENY payload") and N-10 PART5 ("THE REFUSAL CASE, once ... assert the
message, not only the status"). N-11's hardlink site is the one of the three genuinely-cross-feature
widenings this feature adds with no test forcing an implementer to catch the raise.

**Concrete change:** add a fifth case to `tests/integration/test-corpus-denials.py` — point the
worktree's `.git` at an unparseable pointer, send a hardlink-aliasing Write payload, and assert
`check-domain.sh` exits 2 with a message naming the unresolved corpus root (never exit 1, never a
traceback) — mirroring N-07 PART4(d) and N-10 PART5's refusal case. Pair it with an intent-text
instruction that `_hardlink_plan`'s (or its caller's) exception handling must be widened to catch
the named error `feature_corpus.corpus_root()` raises and turn it into `sys.exit(2)`, naming this
file's own exit-1-is-non-blocking contract as the reason it matters.

## Disposition of the prior panel's 13 findings

Verified against the written plan text at this pin (F-06 additionally against `merge-gate.py`
source), never against the digest's own summary of itself.

| id | sev | disposition | evidence |
|---|---|---|---|
| F-01 | high | **ANSWERED** | Q1 "bring all four in." N-10 widens all four read sites (`board_lifecycle.py:477`, `check-plan-routes.py:678,835`, `validate-feature-json.py:44`, `layout_migration.py:187-188`) through `feature_corpus.corpus_root()`; N-06 PART2 fixes the 9th choke point (`harness_boundary.py:151-174 linked_worktrees`). All nine choke points apply-batch-c3 tabulated now sit in a task. |
| F-02 | high | **ANSWERED** | D-01 rewritten per Q2: no `feature-index.json`/`.py`/`--check`/regen test anywhere; `feature_corpus.records()` computed on demand, 0.0023s/79-record cost recorded, 1.2s figure struck. |
| F-03 | high | **ANSWERED** | N-09's `verify:` block (read in full) contains no inline `git diff`; PART3 clause 3 is the single discharge site. |
| F-04 | high | **ANSWERED** | N-06 PART3(c) is explicitly "A ONE-TIME PROOF, NOT A COLLECTED TEST (D-13)," recorded under a `PRE-CHANGE REPRODUCTION` receipt heading, never in the test file. |
| F-05 | high | **ANSWERED** | N-09 PART3 clause 3 pins both endpoints to immutable literals (`pre_change_sha`, `review_sha`) and self-scopes with a named skip line when either is absent, per D-13. |
| F-06 | high | **ANSWERED**, re-verified at source | `grep -c sys.exit merge-gate.py` = 0 (confirmed live); `deny()` at `:144-145` prints exactly the claimed `permissionDecision: deny` JSON (confirmed live). D-01/N-07 now assert that payload, never an exit code. |
| F-07 | med | **ANSWERED** | N-09 PART1(b) demoted to a one-time proof under `AUDIT UNCHANGED` in `nonregression.md`, per D-13; clauses (a)(c)(d) stay standing. |
| F-08 | med | **ANSWERED (dissolved)** | D-01: no file is ever written anywhere, so the cone-materialization question has no subject. |
| F-09 | med | **ANSWERED** | N-06 `depends_on` now reads `[N-01, N-02]`. |
| F-10 | med | **NOT ANSWERED** | N-09 `change_type` is still `cross_module`, and PART5 still specifies the full 4-case `tests/unit/test-nonregression-notes.py` parser suite verbatim. The asked relabel-to-`scaffolding`-plus-delete never landed. Correctly still `open` in `plan.yaml`; non-blocking. |
| F-11 | low | **NOT ANSWERED** | N-01 EXCLUSION 1 still specifies the runtime list-equals-plan comparison ("the list EQUALS the set of ... paths this plan's tasks name ... enumerate the plan's task file lists, compare as sets") and the non-strict PENDING mode verbatim — exactly the machinery asked to be dropped. Correctly still `open`; non-blocking. |
| F-12 | low | **NOT ANSWERED** | The accepted residual ("QA probe and ad-hoc trees keep the full corpus") appears nowhere in D-10's `because` or N-02's scope-guard text — the only occurrence in `plan.yaml` is the panel's own verbatim transcription of the original finding. `grep` of `BRIEF.md` for "residual" returns nothing. Correctly still `open`; non-blocking. |
| F-13 | low | **NOT ANSWERED** | SC-01 ("demonstrated first"), SC-09 ("asserted by the invocation it records"), SC-11 ("reproduced in the same file"), SC-13 ("BOTH the stdout and the exit status asserted") all still carry the flagged construction-language verbatim in `BRIEF.md`. Correctly still `open`; non-blocking. |

**9 of 13 answered and verified; 4 of 13 (all med/low) genuinely unaddressed, and the plan says so
honestly — the "told answered, wasn't" trap does not fire here.** F-10..F-13 do not gate this
review but should be cleared before the batched signature closes all thirteen out.

## First-read material (N-10, N-11, N-12, SC-14, SC-15, D-06 Arm B)

- **N-12's census.** Confirmed it reddens on a new unresolved site (HALF 2's scratch-directory
  proof) and confirmed it does **not** recreate the standing-red-for-corpus-data shape the operator
  rejected — its subject is source text under `bin/`, with no mtime, git range, or pinned count,
  exactly as its own "WHY THIS IS NOT THE STANDING RED" section states. It measures 30 sites in 8
  files, and every one of those 8 files already sits under a task's `files:` per D-07 — residual
  zero, confirmed against `notes/research-FEAT-58-fix-goalcheck-c3.md`.
- **D-06 Arm B exemption.** Pins both halves and more: N-07 PART3 cases 5-8 and N-08 clauses 1-4
  together assert (5) exact pair → zero findings, (6) new duplicate → exactly one, (7) pair + a
  third id → returns, (8) reason emptied → returns. Exceeds the operator's two-case minimum.
- **The three weight-bearing proofs remain red-capable after both amendment rounds:** (a) N-04
  PART2's merge regression is still "kept in the file" with an explicit BLOCKED escalation if the
  fixture cannot reproduce the pre-change shape; (b) N-06's `test-check-state-equivalence.py`
  still excludes exit status from the comparison; (c) N-02's `test-worktree-state-norepair.py`
  still asserts manifest-plus-skip-bit-set equality, never a count. None was weakened by D-13's
  demotions, which touched different, adjacent tests.
- **Positive controls, a third instance?** Searched deliberately for another "central mechanism
  absent from its own control" gap (the GC-01/GC-02 shape). Found none beyond NEW-01 above, which
  is a different shape (a raise with no catch, not an omitted positive-control entry).

## Point 7 — the `check-domain.sh:1052-1062` `_SWEEP_PATTERNS` ruling pm invited

**Ruling: acceptable as scoped, but name the residual where the census lives, not only in a
research note.** `_SWEEP_PATTERNS` is a list of pattern *strings*, consumed later through a
for-loop variable; N-12's census resolves only one level of *assignment* indirection
(`pattern = ...`), never a for-loop binding or a list literal, so this site correctly falls outside
HALF 1's detection by construction — not a hole in today's coverage, since D-02 already rules this
site correctly checkout-scoped and untouched. The real cost is prospective: **any future site
written in that same list-plus-for-loop shape also escapes HALF 1**, silently, which is the one
authoring style the census cannot see. That is a known, accepted gap, not a defect — but right now
it is documented only in `notes/research-FEAT-58-fix-goalcheck-c3.md`'s "Open" section, not in
`plan.yaml`. **Low-severity, non-blocking:** add one sentence to N-12's intent (same shape as F-12's
ask) naming this as an accepted residual — list-valued/for-loop pattern indirection is out of
HALF 1's detection scope by design, and a future consumer proposing to widen it justifies that
then.

## Floor and structural checks — no findings

- No orphan `REQ`/`SC` id in any task's `traces:`; every `REQ-01..REQ-10` and `SC-01..SC-15` traces
  to at least one task; all fifteen SC declare `verify: automated` / `evidence: integration` —
  none of the seven binding items is graded by inspection.
- `depends_on` graph is acyclic and correctly ordered as a DAG (N-07→N-10, N-11→{N-06,N-10},
  N-12→{N-06,N-07,N-10,N-11}, N-09→everything but N-01 directly, reached transitively through
  N-02). File-listing order in `plan.yaml` is not execution order and need not match the graph.
- Every `verify:` line resolves to a path either in that task's own `files:` list or a
  pre-existing file (e.g. N-04's re-run of `tests/integration/test-post-merge-sweep.py`, which
  N-04 does not modify). No task's `verify:` targets a file a predecessor deletes.
- Each of the twelve tasks owns one coherent, nameable surface (N-06 and N-10's multi-part shape is
  the single-writer-per-shared-file device D-07 requires, not padding); none is a bare assertion
  standing in for a task.
- Constraints reconfirmed present and **not** re-litigated: `lanes:` stale key, D-06 settled as
  Arm B, all tasks `main-session-direct`, SC-12/SC-13 split, uniqueness computed on demand, D-06
  records left uncorrected. Filed items (#1595-1598, #1630-1631, FEAT-53, 597-omp-baseline)
  untouched.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "N-11's hardlink-scan refusal has no test forcing the exception feature_corpus.corpus_root() raises to be caught, and check-domain.sh's own documented contract (exit 1 is non-blocking, the write proceeds) turns that gap into a live fail-open on the exact class SC-15 exists to close; 9 of the prior panel's 13 findings are genuinely fixed and verified, 4 low/med ones remain honestly still open"
  severity_max: high
  findings: 2
  must_fix:
    - "NEW-01 (high): N-11 PART1's hardlink-scan refusal for an unresolvable corpus root is unspecified at check-domain.sh's _hardlink_plan/_plan_route call chain, which has no exception handling today; feature_corpus.corpus_root() is specified to RAISE (never return None), the raise propagates uncaught to the bare module-level `_reached_plan = _plan_route(target)` statement, Python exits 1, and check-domain.sh's own header states exit 1 is non-blocking and the write proceeds. No test in N-11 PART4/PART5 exercises this path, unlike N-07 PART4(d) and N-10 PART5 which both test it for their sites. Add a fifth test-corpus-denials.py case asserting exit 2 with a named-owner-root message, and widen the intent text to require catching the raise."
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:.harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "F-10, F-11, F-12, F-13 (med/low, never part of the operator's Q1-Q4 batch) remain unaddressed. Fold them into this same batched fix pass with NEW-01, or explicitly defer each by name at signature?", blocking: false }
  files_touched:
    - ".harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c1.md"
  expertise_update: []
artifact: .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/review-harness-code-reviewer-planpanel-c1.md
```
