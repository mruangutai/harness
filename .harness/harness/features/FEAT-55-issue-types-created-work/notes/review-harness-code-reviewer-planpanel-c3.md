# Plan-panel c3 — scope reader — FEAT-55-issue-types-created-work

## BLUF
Edits 2 and 3 are sound. **Edit 1 (the must_fix that "closed" PF-60f3544b) is NOT sound: the
assertion it adds can never fail, in any of the three sibling test files, because the fixture it
was added to cannot produce the state the assertion exists to catch.** The operator should not
treat PF-60f3544b as closed by this edit. Two further NEW findings below (traces gap, T-10 §6
ambiguity). All six carried findings independently re-confirmed unchanged; no refutations.

## Scope hunt (topology, traces, verify/deletion, SC decidability)
- `depends_on` is a valid topological order (also matches file order here, contra the generic
  warning): T-01→T-02→T-03→T-04, T-02→T-05→T-06(needs T-04+T-05), T-02→T-07→T-08, T-09(∅),
  T-02+T-09→T-10, T-11(∅)→T-12. No forward reference found.
- Every REQ-01..REQ-11 is traced by ≥1 task; every task's `traces:` cites an existing REQ. No
  orphan, no dangling REQ id.
- **New finding — traceability gap, not a functional defect (severity: low).** T-07
  (`plan.yaml:869`) and T-08 (`plan.yaml:988`) both implement and test adopted-parent-never-typed
  behaviour on the factory route (T-08 §8 "THE ADOPTED PARENT"; T-07 cases F/H) — squarely REQ-10
  territory, and BRIEF SC-12 explicitly says REQ-10's only falsifiable grading runs "on both the
  gh-sync and the factory route." Yet only T-03/T-04 (gh-sync route) list `REQ-10` in `traces:`;
  T-07/T-08 do not. Nothing breaks, but an REQ-10 audit that trusts `traces:` metadata alone misses
  half the implementation.
- No `verify:` block found asserting content a predecessor task deletes; no SC verify method is
  structurally undecidable (SC-04/SC-11 inspection citations are file:line-anchored; SC-10's
  `automated`/`issue_types_live` pairing matches the two pre-existing `locally_run` kinds and is
  not new to this delta).

## Grading the three c5 edits

### Edit 1 — T-03 case F, `plan.yaml:528-545` — **UNSOUND, must_fix not actually discharged**
The added clause ("ZERO argv containing updateIssue") textually mirrors T-05 case G (`:785`) and
T-07 case I (`:969`) as claimed. But **all three sibling fixtures are explicitly "fresh"** — T-03
case F: "fresh fixture" (`:532`); T-05 case G: "fresh feature directory" (`:787`); T-07 case I:
"fresh fixture" (`:971`) — i.e. no task or parent is already recorded when the case runs.
PF-60f3544b's defect is specifically a **backfill-before-refusal-check** ordering bug: an
already-recorded key with provenance `"created"` (from a prior run whose type-apply crashed) gets
its `updateIssue` sent before a *different, newly-discovered* missing type causes the run to
refuse. T-04 §4 (`plan.yaml:663-682`) is explicit that the required set for the missing-types
check must include backfill candidates — but in a fresh fixture there are zero backfill
candidates by construction, so **no implementation, buggy or correct, can produce an `updateIssue`
call in any of these three cases**: the assertion passes identically whether the ordering is right
or wrong. Naming a mutant: swap T-04 §4's check-then-backfill order for backfill-then-check in the
implementation — none of case F/G/I redden, because none has a pre-recorded "created" key to
backfill against. The must_fix (`plan.yaml` panel `must_fix: F1`) is satisfied by the letter of the
fix request but leaves the underlying high-severity risk PF-60f3544b described completely
untested, in all three files, before and after this edit.
**Severity: high** (this is the same consequence class as PF-60f3544b — a live issue's native type
can still be silently mutated on a run specified to refuse cleanly, and nothing added by this
revision would catch it).

### Edit 2 — T-03 verify string loop, `plan.yaml:470` — **sound as a uniformity fix, pre-existing weakness inherited, not worsened**
`partial` and `github.issue_types` are now required file-wide, matching T-05 (`:719`)/T-07
(`:882`). But neither this loop nor the sibling `for c in A B C D E F G H H2 I J` case-marker loop
(`:463-466`) scopes matching to lines *within* case F — both are whole-file `grep -qF`. A test
file that labels `CASE F:` (satisfying the marker loop) with materially weaker assertions than
case F's intent describes, while the literal substrings `partial`/`github.issue_types` occur
anywhere else in the ~380-line file (they trivially do, since other cases also reference
`FAKE_TYPES=partial`-shaped fixtures and `github.issue_types` config), still satisfies the gate.
This is a real gap, but it is the same gap the finding's own disposition already named — "Gate
uniformity, not coverage" (panel `PF-8b5853…` `why:`) — so the operator was not misled about scope
here; the edit does exactly what it was asked to do and no more.
**Severity: med** (real, but disclosed; does not gate on its own).

### Edit 3 — T-10 §6, `plan.yaml:1177-1216` — **sound; safety property intact; one spec ambiguity**
Repair note's claims verified directly, not taken on trust: (a) T-10's `verify:` block
(`plan.yaml:1126-1146` region) truly never invokes `--create-in` — confirmed by reading the whole
block; only the default read-only path and the no-`gh` SKIP are exercised. (b) Grepped D-01..D-20
for `EQUAL`/`create-in`/`configured` myself — the only hits are the panel finding's own prose
(pre-fix state) and §6 itself; no decision still asserts the removed equality. (c) BRIEF SC-10
reworded consistently — verified by reading BRIEF.md directly.
All three new failure shapes route to a **non-creating** outcome (`CAPABILITY ABSENT`, or one of
two `SKIP` variants) before reaching the create step, so the safety invariant (nothing is created
in the TARGET without a confirmed-declared type) holds regardless of which shape fires.
**New finding — spec ambiguity, not a safety hole (severity: med).** §6 distinguishes "the
capability query on the TARGET fails (state `query_failed`)" from "gh cannot reach the TARGET - gh
auth status fails for its host, **or the query comes back with an authorisation or not-found
error**" as two different SKIP messages. But `classify_capability` (T-02, `plan.yaml`) has exactly
three states — `absent`/`available`/`query_failed` — with no sub-classification of *why* a query
failed; an authorisation/not-found error and any other query failure both land in the single
`query_failed` state with only a raw `message` string. Nothing in T-02 or T-10 gives the
implementer a rule (substring match, exit code, a separate pre-flight `gh auth status --hostname`
check) for choosing between "SKIP capability query failed on {target}" and "SKIP gh cannot reach
{target}". Two different implementers can reasonably pick differently, and T-10's own `verify:`
never exercises the `--create-in` path at all (correctly, since it's plan-time), so this is
permanently unverified by any automated gate. It does not compromise safety (both outcomes create
nothing) — it only means the *wording* of the SKIP the operator sees on a live run is
underdetermined by the plan.

## Corroborations
All six carried findings independently re-derived against the current (post-c5) plan text; none
were incidentally touched or fixed by this revision.
- `PF-1286544c197d1b0eb4a9b0dc8e1234dc` — T-06 §5 (`plan.yaml:858`) still reads "Write it with a
  plain json.dump of the whole document after every state change," unchanged, confirmed against
  `load_recorded`/`save_recorded`'s locked-atomic-writer pattern already used elsewhere in the same
  file per T-04 §6's own description.
- `PF-452948136bf467869d223e027191ae49` — T-06's `verify:` (`plan.yaml:809-811`) runs only
  `test-gh-backlog-issue-types.py` and `test-gh-sync.py`; T-06's own intent (`plan.yaml:813-815`)
  says to "run test-gh-issue-types.py too and report" — report-only, not gated. Confirmed
  unchanged.
- `PF-e27f1c3018b6b8477547a1b028607f96` — T-05 case F (`plan.yaml:780`) still asserts the rerun
  "makes three MORE 'issue create' argv" as a positive, permanent compat-mode contract. Confirmed
  unchanged.
- `PF-0c12a033f69bb6bc60b8f96134f94fd0` — `adopted` remains behaviourally inert under
  absent-means-never-typed in T-04 §7/T-08 §8; both still spell out that `"adopted"` and ABSENT
  are both never-typed, so the marker's only observable effect is on the receipt file itself, not
  on any created call. Confirmed unchanged.
- `PF-56a2ce7a053111a3aff62a4b97c5902e` — BRIEF SC-12 still carries the adopted-marker language
  verbatim (`"the provenance record reads adopted on both"`) while PF-0c12a033 remains unruled.
  Confirmed unchanged, both riding to the same signature pass.
- `PF-9a71cb9a0c590b06b890ff1517b80385` — T-11/T-12 `verify:` blocks (`plan.yaml:1224-1229`,
  `1289-1300`) still only diff the pinned wording at this feature's own gate; nothing protects the
  duplicated 511-char row after `review_sha` pins. Confirmed unchanged.

## Refutations
None. No carried finding is refuted by the c5 revision.

## Explicit one-line verdicts
1. T-03 case F zero-`updateIssue` assertion (edit 1): **unsound as a remedy — never exercises the
   route it names, in any of the three sibling files.**
2. T-03 verify string loop (edit 2): **sound as the disclosed uniformity fix it was asked to be.**
3. T-10 §6 TARGET semantics (edit 3): **sound — safety invariant intact — with one new,
   non-gating spec ambiguity (SKIP-message choice) left for the operator to note.**
