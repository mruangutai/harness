# Plan consolidation cycle 2 — 20 tasks folded into 13, zero supersession language

**The plan is now a set of standing instructions.** Every one of the nine superseding tasks has been
folded into the task whose clauses it retracted, so no `intent:` contains the word SUPERSEDES, no
"unchanged from T-NN", and no cross-task clause reference a member would have to resolve. The
regression the fold existed to remove — old `T-04`'s F3/F4 anchoring two WRITE families to the
control-plane root while old `T-13` re-anchored them, with `depends_on` putting `T-04` first — is
gone: consolidated `T-04` states the feature-tree anchor **as the instruction**, and the
control-plane spelling of a feature-directory path survives in exactly one place, the lint's own
negative fixture in `T-02`, where the rule requires it to be the wrong answer.

**Substance unchanged.** No REQ, SC, decision or surviving task clause was altered in meaning. Ids
were renumbered (nothing outside `plan.yaml` cites a `T-NN`) and `depends_on` was rebuilt from real
dependency instead of cycle order.

## Task crosswalk — all 20 prior tasks accounted for

| Prior | Carries into | What moved |
|---|---|---|
| T-01 inject root | **T-03** | steps 1–4 verbatim; its step-5 case list replaced by the final one |
| T-02 handoff section | **T-08** | the section and its read-only policy; its receipt-anchor clause replaced by the feature-tree spelling |
| T-03 the lint | **T-02** | ARGUMENTS, summary, empty-scope, exemptions, REGISTRATION verbatim; THE RULE, SCOPE, SCOPE-COMPLETENESS and RED PROOF replaced by the final versions |
| T-04 four families | **T-04** | F1/F2 as reads; F3/F4 restated as feature-tree writes; the two-anchor observations-merge command line |
| T-05 fifth family | **T-05** | whole; clause 1 now reads "must read" rather than "rewrite", since the sweep in T-04 may already have anchored it |
| T-06 twelve skills | **T-06** | whole, plus the direction split (old T-14 clause 2) stated as the rule rather than as a later correction; verify narrowed from whole-scope to these twelve files |
| T-07 CI step | **T-12** | the workflow step verbatim; its three text assertions refactored per old T-15 |
| T-08 DEC entry | **T-13** | structure, index-row instruction, DECISIONS.md:1503 bullet, three severities, issue 356/357 citations; its ruling paragraph replaced by the two-anchor ruling |
| T-09 drift assertion | **T-03** | clause 1 (cwd-differs correction) folded into the first test case; clause 2 as step 5; clause 3 cases appended |
| T-10 feature-root verb | **T-01** | whole, unchanged |
| T-11 lint rule/scope | **T-02** | clauses 1–6 folded in as the checker's rule, scope, canonical sites and fixtures |
| T-12 handoff two anchors | **T-08** | the correction and all three added rules |
| T-13 F3/F4 write anchor | **T-04** | now the instruction; the fenced line-37 hand-anchor kept |
| T-14 templates + write anchors | **T-07** (clause 1) and **T-06** (clause 2) | split along the seam the two clauses already had: templates, and the twelve swept skills |
| T-15 CI red proof | **T-12** | the one path-taking function and both mutants |
| T-16 corrected DEC ruling | **T-13** | the two-anchor ruling, the measurement, the rejected second-injection, the D-07 sentence |
| T-17 README figure + direction | **T-07** | "eight spans, not nine" and the `.gitignore` caveat stated as fact; the three-read/five-write split pinned |
| T-18 dispatch-guard | **T-09** | whole, unchanged |
| T-19 shell-less route in four skills | **T-08** (harness-handoff) and **T-10** (the other three) | split by file; T-12's superseded bullet no longer exists to supersede — T-08 states self-resolution plus the "holds no shell" exception in one place |
| T-20 emit duty in agent defs | **T-11** | whole, unchanged |

## Decisions — 8, same ids, same subjects

`choice:` is one sentence on one line in all eight; `because:` is one clause; no markdown, no
backticks, no embedded newline (asserted programmatically). Rejected alternatives were moved out of
`because:` into a `rejected:` list of one-line entries, which **preserves every load-bearing
rejection** — two under D-06, five under D-08, and the smaller ones under D-01/D-02/D-04/D-05/D-07 —
rather than compressing them away. `rejected: []` where there are none. `plan-merge.py` unions
decisions by `id` and neither it nor `check-plan-routes.py` validates decision fields, so the extra
key is inert.

- **D-08 is now a standing ruling**, not an amendment: "the anchor is resolved by whoever holds a
  shell", with the shell-holding and shell-less halves in one sentence and the tool-grant predicate
  named. It no longer opens "EXTENDS D-06 and supersedes nothing in it".
- **D-01 and D-02 reconciled with the two-anchor ruling.** D-01 now says the control-plane root is
  *the only value this feature injects*; D-02 now defines *two* placeholder tokens and which
  direction each takes. Nothing in the file now disagrees about what is injected and what an
  instruction cites.

## Coverage

- **REQ-01..REQ-06 all traced**, and every task traces to a REQ that exists: REQ-01 T-03/T-13 ·
  REQ-02 T-04,05,06,07,08,10,11,13 · REQ-03 T-05,08,13 · REQ-04 T-02,03,12 · REQ-05 T-03 ·
  REQ-06 T-01,02,04,06,07,08,09,10,11,13.
- **SC-01..SC-14 all carried**: SC-01 T-03 · SC-02 T-03 (see finding F-1) · SC-03 T-02 · SC-04
  T-12 (whole-scope run) with the per-site anchoring in T-04/06/07/08 · SC-05 T-02 · SC-06 T-05 ·
  SC-07 no-change criterion, inspection only — no task widens a grant and T-05 and T-11 forbid it
  explicitly · SC-08 T-12 · SC-09 T-08 + T-13 · SC-10 T-01 · SC-11 T-02 (rule) + T-04/06/07/08
  (instruction form) + T-12 (whole scope) · SC-12 T-03 · SC-13 T-09 · SC-14 T-11 + T-08.
- **BRIEF.md untouched.** No consolidated task needed a trace to a REQ that does not exist.

## Findings

- **F-1 (pre-existing, carried forward unchanged, NOT introduced here).** SC-02's second clause —
  "the committed test greps the shipped script for `^[[:space:]]*exit [1-9]` and asserts ZERO
  matches, and in the same case asserts the SAME pattern DOES match a one-line `exit 2` fixture" —
  **has no task carrier**, and had none in the 20-task plan either: measured, `exit [1-9]` appears
  zero times in both the old `plan.yaml` and the consolidated one. Cycle 1 closed finding L1 by
  amending the SC and never routed the assertion into `T-01`/`T-09`. Adding it now would be a
  substance change this batch is forbidden to make, so it is raised instead. As it stands SC-02's
  first clause is met by T-03's unresolved-branch case and its second clause is unverifiable.
- **F-2 (no clause lost).** Every clause of the 20 prior tasks landed in a consolidated task except
  the supersession bookkeeping itself — the "SUPERSEDES X, and only that step" sentences and the
  "everything else stands" carve-outs. Those describe the amendment mechanism, not the work.
- **F-3 (verify narrowed, deliberately, twice).** Old `T-06` and old `T-11` each ran the checker
  over the *whole* scope; a consolidated plan cannot have two such gates green at different times,
  and one of them was green only because unswept directories had not yet joined the scope. The
  whole-scope run is now a single gate, in `T-12`, whose `depends_on` names every anchoring task.
  Every earlier anchoring task verifies the checker over its own file list, so no task asserts a
  by-construction red.
- **F-4 (`lanes:` still incomplete, unchanged).** The four surfaces added in cycle 1
  (`inflight_registry.py`, `test-inflight-registry.py`, `dispatch-guard.sh`, `templates/*.md`) still
  have no `lanes:` row. This rewrite could have added them — the file is written whole — but
  `lanes.resolved_at` pins the resolution to sha `e8e1b78b` and adding rows now would assert a
  resolution nobody performed. `check-plan-routes.py` reads task fields, so nothing is unenforced.

## Verification observed

```
python3 -c "import yaml; yaml.safe_load(open(<plan.yaml>))"        -> loads; 13 tasks, 8 decisions
python3 .agents/skills/harness/bin/check-plan-routes.py <plan.yaml> -> exit 0, 0 violations
```
Field checks re-read from the written file: `feature: FEAT-52-factory-control-plane`,
`status: plan`, `source_issues: [356]`, `lanes.resolved_at: e8e1b78be3379d4a669aa7e28aef8f76eb942471`,
8 lane rows. No `approval:` key was written — `plan-merge.py:468-478` exits 8 on the create path if a
proposal carries one, and the missing block is the separately routed harness defect.

## Open questions

- **Q1 (non-blocking, unchanged from cycle 1)** — `lanes:` cannot be amended by any `plan-merge.py`
  verb, so a plan that grows a surface after its first write can never record that surface's lane.
- **Q2 (non-blocking, unchanged)** — `harness-pm` has no writable non-`.md` staging path inside a
  feature directory, so a `plan-merge.py` proposal has to be staged in `notes/research-*.md`.
- **Q3 (new, non-blocking)** — `plan-merge.py apply` cannot amend an existing id (exit 7), so the
  only route to a consolidated plan was `rm` plus a whole re-create. A `replace` verb, or an
  `--allow-replace` flag under the same lock, would make a re-expression a first-class operation
  instead of a delete-and-recreate that only works while `approval:` is absent.
- **Q4 (non-blocking, unchanged)** — `dispatch-guard.sh:115-126` resolves a checkout by basename
  equality while `harness_boundary.worktree_for_feature:193-229` resolves by prefix; `T-09`
  enforces against the prefix resolver so the disagreement is loud, and reconciling `_root_for` is
  a separate change.

## Lane resolution the `lanes:` block cannot carry — cycle 3

`lanes:` is a non-union key, so the four surfaces added in cycle 1 have no `lanes.rows` entry and no
`plan-merge.py` verb can add one (Q1). The resolution is recorded here instead, so the operator signs
with it visible. Each answer below is the verbatim stdout of
`bash .agents/skills/harness/bin/check-domain.sh --resolve <path>`, exit 0 in all four cases. The
dispatch spelled the command `python3 …check-domain.sh`; the file is a shell script, so it was run
with `bash` (lead-corrected).

`.claude/skills/harness/bin/inflight_registry.py`

```
harness-backend-dev
harness-dev-ops
```

`.claude/skills/harness/bin/test-inflight-registry.py`

```
harness-backend-dev
harness-dev-ops
```

`.claude/skills/harness/bin/dispatch-guard.sh`

```
harness-backend-dev
harness-dev-ops
```

`.claude/skills/harness/templates/*.md` — resolved on the concrete member
`.claude/skills/harness/templates/PLAN.md`:

```
NOBODY
```

The guard is the authority, and on the first three it disagrees with the lane the plan declares:
`team-config.yaml` grants `harness-backend-dev` and `harness-dev-ops`, while `T-01`, `T-09` and the
new `T-14` are declared `main-session-direct` under the DEC-174 carve-out, which the grant does not
encode — `check-plan-routes.py` prints exactly that as `DEVIATION` and still exits 0, so the carve-out
stands and the grant is recorded here rather than followed. The templates surface resolves to
`NOBODY`, which agrees with `T-07`'s `main-session-direct` declaration.

### T-14, the SC-02 carrier (cycle 3)

SC-02's second clause — the committed test greps the shipped script for `^[[:space:]]*exit [1-9]`,
asserts ZERO matches, and asserts the same pattern matches a one-line `exit 2` fixture — had no task
carrier. `T-06:527` is the anchor-sweep's own positive control and is unrelated; `T-03` carries the
unresolved-branch cases but not this grep. Added as `T-14`, `traces: [REQ-05]`, `depends_on: [T-03]`,
`files:` the test file only, `main-session-direct` per the same DEC-174 carve-out `lanes:` already
records for `inject-expertise.sh`. `T-12` is NOT amended to depend on it: `T-12` wires and runs the
instruction-path lint, its verify never runs `test-inject-expertise.py`, and it does not depend on
`T-03` either — so `T-14` is outside its ordering, and `apply` exits 7 on any amendment regardless.

- 2026-09-01 (cycle 4): `T-14`'s `change_type` corrected from `test` to `logic`. `test` is absent from `.harness/harness.json`'s `test_matrix` keys (`logic api cross_module frontend feature bugfix ai_behavior config scaffolding docs`), so the task had no matrix row and would have entered the project's only blocking gate (`qa_gate: blocking`) with nothing to check it against; `T-14`'s script-plus-test-file work shape matches `T-01`/`T-02`/`T-03`, which already carry `logic`. A value correction, not a new category — no `_matrix_provenance` entry and no operator ruling.
