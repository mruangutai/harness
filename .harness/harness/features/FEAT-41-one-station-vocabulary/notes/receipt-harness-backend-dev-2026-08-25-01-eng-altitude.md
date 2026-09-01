# ALTITUDE angle — FEAT-41 plan.yaml, read-only

Two findings, both on the DAG leads named in the dispatch. Nothing else at this altitude: the
station-decision authority (`factory_config.py`, T-01) is genuinely single, `project()` (T-06) is
genuinely the one policy function, and the residuals I checked (T-08's shell-expansion gap, T-09's
"legal value via shell, unattributable" gap) each already name their own compensating-control
limits in the task text — no silent ones found beyond BRIEF.md:69-72.

## Finding 1 — T-12's `depends_on` (11 tasks) is wider than its own `traces`, and the excess
tasks are on a lane that could otherwise run in parallel

- **File/line**: `plan.yaml:668-674` (T-12, `execution_mode: team`, `execution_agent:
  harness-documentor`), `depends_on: [T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08, T-09, T-10,
  T-11]`.
- **Derivation**: T-12's own `traces: [REQ-01, REQ-02, REQ-05, REQ-06]` (line 670) and its intent
  text (lines 682-721) name a new DEC entry with exactly four content points — the six-name
  mandate (REQ-01, from T-01), lowercase-everywhere-plus-one-derivation (REQ-02, from T-02),
  plan.yaml's one-writer/shape-gate/identity-gate story (REQ-05, from T-03/T-05/T-08/T-09), and
  the `feature.json`→`plan.yaml` station move (REQ-06, from T-07) — plus three named amendments to
  DEC-203/DEC-191/DEC-182, which cite exactly those same tasks. REQ-04 (T-06's `project()`) is
  **not** in T-12's `traces` and does not appear among the four decision points. T-10 (ship
  commit/worktree-refusal bugfixes, REQ-07) and T-11 (deleting an unreachable renamed-board test,
  REQ-01-but-already-covered-by-T-01) appear nowhere in T-12's traces or intent text either. The
  real data dependency set, derived from T-12's own content, is {T-01, T-02, T-03, T-05, T-07,
  T-08, T-09} — 7 of the 11 listed, with T-04/T-06/T-08 additionally reachable transitively through
  T-07/T-09 so their direct edges are at worst redundant, not wrong. T-10 and T-11 are neither
  direct nor transitive requirements of anything T-12 reads or writes, and I confirmed no file
  overlap either (T-10 touches `gh-sync.py`/its tests/FEAT-40's `plan.yaml`; T-11 touches only
  `test-check-state.py`; T-12 touches only `DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`).
- **Concrete cost**: T-12 is the one task on the `team` lane (`harness-documentor`) in a plan where
  every other task is `main-session-direct` (DEC-174). That lane split is the plan's one point of
  real parallelism. As written, `harness-documentor` cannot start until a ship bugfix (T-10) and a
  test deletion (T-11) — work its own decision text never cites — have both landed, which forces
  the only parallel-capable seat in the plan back onto the single-actor critical path for no
  derivable reason.
- **Alternative**: prune T-12's `depends_on` to the tasks its `traces` and intent actually cite —
  {T-01, T-02, T-03, T-05, T-07, T-08, T-09} — dropping T-04, T-06, T-10, T-11. T-04 and T-06 stay
  reachable transitively through T-07 and T-09 so correctness is unaffected; only T-10 and T-11 are
  a net removal, and that is the whole gain.
- **Verdict: briefing-row.** Cheap and mechanical to apply, but it is pm's call whether the
  original 11-task list was intentional slack (a documentor that never starts until "everything
  else is basically done" as a simplicity/safety default) rather than an oversight — that trade
  is pm's to make, not mine to fold in silently.

## Finding 2 — T-09's `depends_on` orders the plan.yaml write-denial after the mechanism exists,
but not after the mechanism is proven against real data

- **File/line**: `plan.yaml:545-551` (T-09, `depends_on: [T-03, T-05, T-08]`) versus `plan.yaml:
  269-313` (T-04, `depends_on: [T-03]`, the only task whose verify actually exercises
  `set-task-station` against the 28 live `plan.yaml` files under
  `.harness/harness/features/` — its `intent` runs the migration through the tool "for every
  plan.yaml under .harness/harness/features/", and its `verify` block includes
  `check-plan-routes.py --all` plus a grep proving no `status: pending` survives).
- **Derivation**: D-03 (line 57-60) states the write-window intent in prose: "T-03 and T-05 close
  the plan.yaml write window and T-09 opens it, so no ordering exists in which plan.yaml has zero
  writers" — but that is a claim about the *Edit-route* window, not about correctness of the new
  verbs. T-09's own `verify` (line 557-558) runs only `test-check-domain.py` — mocked PreToolUse
  payloads exercising the *gate*, not `plan-write.py` against a real file. T-09's `depends_on` does
  not include T-04. Nothing in the encoded DAG requires T-04 to have run, or to have run
  successfully, before T-09 lands. The two tasks share only the common ancestor T-03; per the graph
  as written, a scheduler honoring `depends_on` alone could legally run T-09 immediately after
  T-03/T-05/T-08 and before T-04 ever touches a live plan.
- **Concrete cost**: if `set-task-station`/`set-feature-station` have a defect that only shows up
  against one of the 28 real `plan.yaml` files (variant task-id formats, an unusual line the splice
  doesn't anticipate, etc. — exactly the class of bug T-04's migration is positioned to catch, per
  its own verify), and T-09 has already landed first, the Edit/Write route is denied network-wide
  before the one task that stress-tests the verbs on production data has run. The plan's own DAG
  is where this would have to be caught, and it does not encode the requirement.
- **Alternative**: add T-04 to T-09's `depends_on` (`[T-03, T-04, T-05, T-08]`). This is what D-03's
  prose intent already implies — "no ordering exists in which plan.yaml has zero writers" reads
  naturally as "the writer must be proven, not merely coded" — the edge just isn't in the graph.
- **Verdict: fold-in.** One-line, no file-overlap risk (T-04 and T-09 touch disjoint file sets), and
  it makes the DAG say what D-03's own reasoning already asserts.

## Leave

Everything else scanned at this altitude — the station-vocabulary single-authority story
(`factory_config.py` per T-01/T-02/T-04, consistently cited rather than restated), `project()` as
the one station-decision function (T-06, and T-10/T-08's caller-side knowledge is inherent to being
a gate, not vocabulary knowledge), and the two residuals the plan itself discloses (T-08's
shell-expansion evasion, T-09's unattributable-legal-write gap) — is at the right depth or already
carries its named compensating control. No further findings.
