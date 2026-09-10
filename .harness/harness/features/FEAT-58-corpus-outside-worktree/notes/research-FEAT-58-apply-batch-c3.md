# FEAT-58 — cycle-3 batch applied to BRIEF.md and plan.yaml

**The whole batch landed. Plan 9 → 12 tasks, 12 → 13 decisions; BRIEF 13 → 15 criteria; the
assertion ledger goes 36 in → 42 out with no row dropped and three whose evidence form changed,
each named below.** `plan.yaml` `status: plan`, `approval.status: pending`, `panel` and `lanes`
untouched; `BRIEF.md ## Approval` still `status: pending`.
`check-plan-routes.py <plan>` → **0 violations, exit 0** (12 TASK `DEVIATION` lines, the DEC-174
carve-out working; no MANIFEST deviation).

## What drove the task increase (Q1 + lead ruling 1)

Engineering's shape landed unchanged: **N-10** four-site owner-root read widening, **N-11**
two-gate denial widening, **N-12** source-text census. Not one task, because a *report widening*
and a *write denial* share no change and no test, and the census cannot be authored until every
site carries its marker. All **nine** choke points are named by anchor with their shape stated:

| # | anchor | shape | task |
|---|---|---|---|
| 1 | `check-state.sh:118-120` + `:127-131` | (a)+(b) | N-06 |
| 2 | `merge-gate.py:132-142` (glob `:134`) | (c)+(b) | N-07 |
| 3 | `board_lifecycle.py:472-477` | (c)+(b) | N-10 |
| 4 | `check-plan-routes.py:665` + `:835` | (c)+(b) | N-10 |
| 5 | `validate-feature-json.py:40-55` | (c)+(b) | N-10 |
| 6 | `layout_migration.py:187-188` | (c)+(b) | N-10 |
| 7 | `check-domain.sh:1907-1922` (glob `:1916`) | (c)+(b) | N-11 |
| 8 | `branch-create-gate.sh:89` | (c) only | N-11 |
| 9 | `harness_boundary.py:151-174` `linked_worktrees` | (a)+(b) | N-06 |

Site 8's task asserts the **allow path still allows** (N-11 PART 5 case (c), before the deny
case (d)) — narrowed, it falsely denies a legal branch. Graph: N-10 `[N-01]`, N-07 `[N-01,N-10]`,
N-11 `[N-06,N-10]`, N-12 `[N-06,N-07,N-10,N-11]`, N-09 `[N-02..N-08,N-10,N-11,N-12]`, N-06 gains
N-02 (F-09). D-07 carries the amended single-writer table: `check-domain.sh` → N-06 **then** N-11,
serialised by the edge; `feature_corpus.py` → N-10 then N-07; new rows for
`branch-create-gate.sh` and `layout_migration.py`.

## The two deletions, recorded as deletions

- **The persisted index (Q2).** `feature-index.py`, `feature-index.json`, `--check`,
  `test-feature-index-regen.py` and every regeneration/staleness assertion are gone. Reasoning is
  in `plan.yaml` D-01 `because` so a later scan cannot re-propose it: a tracked file needs a
  writer on every `feature.json` creation, has none under D-10, goes stale between writes, and its
  own `--check` reddens for the whole team at the next feature created. Cost is the **measured
  0.0023 s median over 79 records, 5 runs** — ~520× under the 1.2 s the question assumed; the
  1.2 s figure is explicitly struck.
- **F-08 is DISSOLVED, not renamed** (D-01 `because`): with no file written anywhere, the
  cone question has no subject. **F-06's D-01 half dissolves with it**; the surviving refusal is
  the deny payload (`merge-gate.py:144-145`, `grep -c sys.exit` = 0, no exit invented).

## Ledger arithmetic — 36 in, 42 out

All 36 keep a landing place. Restated (subject moved, not dropped): the `feature-index.json`
regeneration row → the exemption's both-halves real-data run (N-08); **A-13**'s `--check` clause →
the real-data run alone; **A-04/A-03/C-01** → "the records" and "emits the deny payload";
**ALT-F3** simplifies to an ordinary import; **ALT-F2** keeps a corrected anchor.
Added, 6: per-site count equivalence ×4 sites (N-10); `corpus_root` refusal (N-10); hardlink deny
+ positive control (N-11); branch-gate allow + deny (N-11); census both halves (N-12); the
exemption's three cases (N-07).

**Evidence form changed — a real reduction in STANDING coverage, not absorbed:**

| row | old form | new form |
|---|---|---|
| **A-14 clause (b)** (`test-nonworktree-unchanged.py`, audit-unchanged vs merge-base copy) | standing integration assertion | **one-time proof**, verdict under `## AUDIT UNCHANGED` in `notes/nonregression.md`; (a)(c)(d) stay standing |
| **N-06 PART 3 case (c)** (verify-gate pre-change reproduction, D-12's test; no lettered ledger row) | standing integration assertion | **one-time red proof** under `PRE-CHANGE REPRODUCTION` in N-06's receipt |
| **A-23** (nothing lost, strong form) | asserted **twice** — inline `git diff` in N-09 `verify:` **and** PART 3 clause 3, both over a moving merge-base | the `verify:` copy **deleted** (F-03); one standing assertion **pinned** to `pre_change_sha..review_sha` and **self-scoped**, skipping with a named line when either literal is absent |

**Correction to engineering's naming, and it favours coverage:** the digest listed **A-15** among
the three. It is not demoted. A-15 is the failing-set equality (N-01 records, N-09 PART 3
clause 2) and nothing in Q4 touches it; the demoted clause is N-09 **PART 1 (b)**, which belongs
to **A-14**. A-15 stays a standing assertion.

## Arm B (Q3) and the criteria

D-06 now reads **DECIDED — Arm B**, citing `notes/answers-operator-c3.md:43-60`; no open operator
choice remains in `decisions:`. Records uncorrected; `BRANCH_ERA_EXEMPT` keyed on the exact
frozenset lives in `feature_corpus.py` immediately above the predicate (precedent
`feature_schema.py:226`). Every Arm A carve-out is struck from SC-13, N-08, N-09 and D-06.
Tests pin four cases: exact pair → none; new duplicate → one; pair **plus a third id** → returns;
reason emptied → returns.

13 → **15 criteria**, engineering's recommended count and shape: **SC-14** no scan site under
`bin/` silently narrows (per-site count equivalence + census both halves) and **SC-15** the
hardlink-alias write is denied with the own-feature write still allowed. The demotions are
disclosed in `BRIEF.md ## Verification gaps`, where the operator signs.

## Coverage table, verbatim as it now stands in BRIEF.md

| Item | What | REQ | SC |
|---|---|---|---|
| **D-1 (DoD)** | Exactly one feature directory materialised | REQ-01 | SC-01 |
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06, SC-14 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03, SC-15 |
| — | The live FEAT-02 / FEAT-03 collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

## Open questions for the next segment

- **Q1 (non-blocking).** `N-08` lost its production surface under Arm B — it is now a single
  real-data test — so its `change_type` moved `config` → `scaffolding`. If the goal-check wants a
  required kind on it, `logic`/`feature` would demand a unit test that would be padding.
- **Q2 (non-blocking).** D-02's corrected fix lands in `harness_boundary.py`, which is now in
  N-06's `files:`. N-06 therefore writes three production files; if the panel calls that too wide,
  the `harness_boundary.py` edit splits cleanly, but it is one line serving two sweeps.
