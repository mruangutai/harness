# Goal-check — BUG-1286 plan phase, cycle 5 (post second amendment)

**BLUF: yes — the twice-amended plan delivers the operator's stated intent; all eleven acceptance
criteria are delivered and both operator-selected fixes are CLOSED, with one surviving residual in
fix 1's new assertion (a directory-only `detect` glob rooted outside `tests/` is out of its partition
by construction, so one substitution widening stays green).**

Graded from the current text of `plan.yaml` (tag as read) and `BRIEF.md` at worktree HEAD, working
tree carrying only BRIEF/plan/observations edits plus the amend note (`git status --porcelain`) — no
implementation, test or config file touched.

## 1. Destination, both negatives — delivered, undrifted

- Every tracked test-shaped file made to obey `tests/**`: `BRIEF.md:18-21`, REQ-01 `:25-26`; clause
  `plan.yaml:326-340`, vocabulary `:286-288`, predicate `:296-300`.
- Product-checkout discovery unchanged: D-03 `plan.yaml:82-102`, self-ownership skip `:331-333`,
  SC-16 `BRIEF.md:141-147`, T-01 case 9 `plan.yaml:411-415`. No discovery surface in `lanes:` `:8-31`.
- Implementation not begun: `plan.yaml:3-5`, every task `status: ready`.

## 2. The four blocking questions — all still settled decisively

| Q | Settled at | Decisive |
|---|---|---|
| 1 vocabulary | D-01 `plan.yaml:34-70`; constants `:286-288`; predicate `:296-300`; "SOURCE_EXTENSIONS applies to RESTRICTED_NAME_PATTERNS ONLY" `:308-313`; census dispositions `:530-537`; DEC-213 text `:653-672` | yes — literal constants + one exported predicate, no improvisation left |
| 2 exception contract | D-02 `:72-81`, D-05 `:111-123`, policing `:341-348`, cases 6-7 `:398-407`, SC-10 `BRIEF.md:110-114` | yes |
| 3 tracked authority + failure semantics | D-03 `:82-102`, `tracked_paths` `:318-324`, LookupError branch `:328-330`, cases 4-5 `:394-397`, SC-05/SC-17 | yes |
| 4 DEC-213 amendment | D-06 `:124-132`, T-05 `:633-703`, SC-13 `BRIEF.md:129-133` | yes |

## 3. Eleven acceptance criteria — 11 delivered / 0 partially delivered / 0 not delivered

Table `BRIEF.md:182-202`. AC-01 SC-01/02/18/19 → T-01 clause `:334-340`, cases 1/10/11; AC-02 SC-03 →
`:339-340`, case 3 `:391-393`; AC-03 SC-04 → T-02 case 2 `:487-492`; AC-04 SC-05+17 → `:328-330`,
cases 4-5, T-02 case 4 `:495-497`; AC-05 SC-06+07 → exact-equality grader `:368-377`, pre-existing
assertion re-verified at `tests/unit/test-suite-layout.py:104-105`; AC-06 SC-08+09 → case 7 `:403-407`,
`import layout_fixtures as lf` verified at `tests/integration/test-layout-migration.py:62`; AC-07
SC-10 → `:341-348`, cases 6-7; AC-08 SC-11 → case 2 `:389-390`, T-02 case 5 `:498-499`; AC-09 SC-12 →
T-03 `:502-589`, T-04 `:590-632`; AC-10 SC-13 → T-05 `:633-703`; AC-11 SC-14/15/16 → `:462-463`,
SC-15's pin re-derived (`run_pool.py --mutation-check "$BIN_DIR"` is still the sole invocation and
still line 47 of `run-unit-tests.sh`). **11 + 0 + 0 = 11.**

## 4. FEAT-44 classification — carried through, not weakened

D-05 `plan.yaml:111-123` keeps the exact path, "is not relocated", the consumer reference at
`tests/manual/probe-omp-session-accessor.py:54-55` (re-verified: `PROBE` occupies those lines), and
the archival coupling with its consequence stated verbatim. Touching sites unchanged: registry seed
`:289-294`, case 1 rebinding rationale `:378-388`, case 7, T-04 `:624-628`, T-05 `:686-689`,
`BRIEF.md:84-88`.

## 5. Four out-of-scope entries — undrifted

Product-checkout redesign (`:331-333`, no discovery surface in `lanes:`); mutation snapshots
(`BRIEF.md:136-140`, `plan.yaml:462-463`); support-module renames (T-05 `:690-691` keeps "What this
does not do"); implementation during planning (`:3-5`, clean tree). **`harness.json` untouched:** no
task lists it in `files:`; T-01 explicitly "Case 11 READS `.harness/harness.json` and must not write
it" `:462`; SC-14 `BRIEF.md:134-135` still demands zero bytes changed.

## 6. Delivered but never asked for — nothing out of scope

REQ-09/SC-19 and T-01 case 11 are new this cycle but are the operator's own selected fix, not creep;
they add an assertion, no product surface. T-03's `--against` mode remains the mechanism SC-12 needs.

## Fix closures

**Fix 1 (PF-8de8d644…) — CLOSED, with one residual.** Case 11 `plan.yaml:424-461` derives globs at
runtime from `test_kinds.unit.detect` via `repo_cfg` and forbids a literal copy (`:426-428`); it
IMPORTS `is_test_shaped` and forbids re-spelling, `fnmatch`, or consulting the tuples (`:425`,
`:446-449`); the partition rule is computable from the glob string alone (`:429-433`). Applied to
today's four (emulated from the plan's literal spec, and matching `unit.detect` read from
`.harness/harness.json` = `tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py`): `tests/unit/**` →
`**` → `""` → OUT; `**/*.test.*` → `.test.` → IN → `.harness/tools/x.test.x` → shaped; `**/*_test.*`
→ `_test.` → IN → `x_test.x` → shaped; `**/test_*.py` → `test_*.py` **unchanged** → IN →
`test_x.py` → shaped. The corrected intermediate is in the plan (`:436-438`); **no stale `test_.py`
occurs anywhere in `plan.yaml` or `BRIEF.md`** (grep, 0 hits). Synthesised names are genuinely
evaluated: each is judged by the same predicate the clause itself calls, so a narrowing of the
tuples or `SOURCE_EXTENSIONS` reddens it (`test_x.py` depends on `.py ∈ SOURCE_EXTENSIONS`).

*The red set (not one example):* (a) any basename-constraining glob added or edited whose fixed-token
representative is not test-shaped — measured: `+**/*.spec.*` → `x.spec.x` RED, `+**/test_*` → RED,
`+**/*test*.md` → RED; (b) the out-of-scope glob count leaving exactly one — measured: `+bench/**`
RED; (c) any narrowing of `AGNOSTIC_NAME_PATTERNS`, `RESTRICTED_NAME_PATTERNS`, `SOURCE_EXTENSIONS`
or `is_test_shaped`; (d) `test_kinds.unit.detect` absent/renamed, so the read fails. **The
widen-both-files mutant is inside the set** — `**/*.spec.*` added to both `harness.json` and the
template goes RED on case 11 while `tests/unit/test-suite-layout.py:100-103` stays GREEN (verified:
that assertion compares the two files to each other).

*Adversarial construction, attempted and SUCCESSFUL:* substitute rather than add. Replace
`tests/unit/**` with `docs/**` (or bare `**`) in `unit.detect` — still exactly one out-of-scope glob,
three in-scope, all three representatives shaped, so **case 11 stays GREEN** (measured both). Every
tracked file under `docs/` is then counted a unit test by the kind map, sits outside `tests/`, is not
test-shaped by the guard, and no runner selects it — the counted-but-never-run defect re-created.
Cause: the partition treats a wildcard-only final segment as unable to produce a file outside
`tests/`, which holds only because today's one such glob is rooted *inside* `tests/`; the rule does
not test that prefix. Reported, not applied.

**Fix 2 (PF-8da87ee5…) — CLOSED.** Three sites, same contract, none ambiguous or plural:
T-03 `plan.yaml:557-572` (count before parsing; zero → named error, two or more → named error, both
exit 2 reserved; "REFUSING is the contract, NOT first-block-only"); T-04 `plan.yaml:610-623` ("the
ONLY fenced block", one opening and one closing, quoted commands inline or indented); SC-12
`BRIEF.md:118-128` ("EXACTLY ONE fenced block"; a second fence "is a failure of this criterion, not
merely of a command"). Failure mode named at all three (`:567-570`, `:615-619`, `BRIEF.md:125-127`).
No `verify:` depends on a changed ordering or exit rule: T-03's verify runs without `--against`
(`:513`) so the note contract is unreachable; T-04's (`:601`) already required exit 0, which the new
rule only narrows, and the unconditional block + `TOTAL` still print before the refusal (`:571-572`),
so the `probe-session-accessors\.ts.*documented-exception` anchor survives. The only plural-fence
prose left in either artifact is inside the frozen `panel:` block (`plan.yaml:176`, `:219`) — expected,
not drift.

## Stale-text check — four verdicts

1. **D-01 `because`** — CURRENT. `:62-68` reads "ASSERTED rather than argued from a snapshot" and
   cites case 11's runtime read and SC-19; the `c040c319` baseline `:68-70` still carries its sha and
   condition.
2. **BRIEF `unit.detect` closure bullet** — CURRENT. `BRIEF.md:213-225`: "asserted rather than
   assumed", names case 11 and SC-19; no surviving "disclosed residual" claim.
3. **T-05 DEC-213 bullets** — CURRENT. `:663-669` instructs the documentor to state the property is
   ENFORCED by the unit assertion, cite it, and not re-list globs or synthesised names.
4. **SC-06 / T-01 case 1 exact-equality fixture** — SAFE, by construction not by inspection alone.
   Case 11 "builds no fixture and plants no file" (`:424-425`) and is declared ADDITIVE with case 1
   explicitly untouched (`:459-461`); the two file-planting cases added earlier build their own
   fixtures (case 10 "Assert it in this case and not by widening case 1's fixture" `:419-421`; case 8
   `:408-410`), and every case cleans up its own temporary directory (`:352-353`). Nothing this
   amendment introduced can enter case 1's fixture, so the one-element list at `:371-372` still holds.

## Surviving gaps

1. **REQ-09's durability has a hole SC-19 cannot see: a directory-only `unit.detect` glob rooted
   outside `tests/`.** Case 11's partition (`plan.yaml:429-433`) puts any wildcard-only final segment
   out of scope, and the "exactly one out of scope" assertion (`:438-439`) catches *adding* one but
   not *substituting* the existing `tests/unit/**`. Concrete widening that stays green:
   `detect: docs/**|**/*.test.*|**/*_test.*|**/test_*.py` (measured GREEN). Cheapest remedy, for the
   orchestrator to route, not applied here: make out-of-scope conditional on the glob's literal
   directory prefix starting with `tests/`, and assert the one out-of-scope glob is that prefix.
