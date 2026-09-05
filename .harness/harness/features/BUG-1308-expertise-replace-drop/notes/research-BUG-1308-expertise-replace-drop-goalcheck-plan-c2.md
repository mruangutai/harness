# Goal-check — BUG-1308 revised plan (cycle 2, plan panel product segment)

PASS — the plan as committed delivers the operator's stated intent and all four of his cycle-1 rulings.

Graded read-only from `BRIEF.md` and `plan.yaml` on disk in the worktree, against
`.harness/notes/grilling-six-residual-bugs-2026-09-05.md` and issue #1308. The revision note and the
c1 validator digest were read as context only; no claim below rests on them.

## Part A — the operator's four rulings

| Ruling | Status | Evidence |
|---|---|---|
| R1 stable-identity application + composition regression | **MET** | see A1 |
| R2 `section` required on every op | **MET** | see A2 |
| R3 A3 merge-as-authoring kept | **MET** | see A3 |
| R4 concurrency determinism + T-03/T-04 verify coverage | **MET** | see A4 |

### A1 — stable target identity and the composition regression

T-01 intent, Step D, states the invariant VERBATIM (`plan.yaml`, T-01 `intent`):
`no index resolved against the base snapshot is ever used to address the mutated list.`
It is not left as a bare invariant: Step B fixes the key — `Resolution yields a STABLE TARGET
IDENTITY, the (section, id) KEY, and never an index: no op carries, stores or computes a position in
any list` — and Step D mandates the mechanism — `Application is a SINGLE PASS that REBUILDS each
affected section from the base snapshot`, walking base entries in original order, plus the closing
prohibition `Never delete from, or assign into, a list you are also iterating by index.`
**A builder reading only this intent cannot write index arithmetic against a mutated list**: the only
addressing vocabulary offered is the `(section, id)` key, and the reconstruction is a rebuild, not an
in-place edit. Answer to the c1 high finding: the "given order vs original snapshot" reconciliation
is now stated (order-independence for replace/drop falls out of the base-order walk; only adds are
order-sensitive, and only relative to each other).

Composition regression exists at BOTH levels, low-index drop plus higher-index replace/drop:

| Level | Case | Shape | Asserts id sequence | Asserts replaced text |
|---|---|---|---|---|
| unit | `u11` (T-01 intent) | drop `P-01` (idx 0) + replace `P-05` (idx 4), then the same two ops reversed | `EXACTLY [P-02, P-03, P-04, P-05]` | `P-05` carries marker text, no other entry does |
| unit | `u12` (T-01 intent) | two drops, `P-01` and `P-04` | `EXACTLY [P-02, P-03, P-05]`, length 3 | n/a (drop-only shape) |
| integration | `case19` (T-02 intent) | drop `P-01` + replace `P-05` through the CLI, then reversed, byte-identical | `EXACTLY P-02, P-03, P-04, P-05 IN FILE ORDER` | marker text on `P-05` only |

Criteria and verify strings carrying them: **SC-12** (`evidence: integration`, naming `case19` with
`u11`/`u12` as the unit half); **T-01** `verify: python3 "$(git rev-parse --show-toplevel)/tests/unit/test-expertise-ops.py"`;
**T-02** `verify: python3 "$(git rev-parse --show-toplevel)/tests/integration/test-expertise-merge.py"`.
**SC-07** carries the unit suite's own gate. See finding B-6.2 on the discriminating power of those
two verify strings.

### A2 — `section` required on every op

Stated consistently and with no surviving optional affordance:
- **D-02**: `target and section are BOTH required on every op ... There is no optional-section
  affordance and no whole-file id resolution.`
- **D-05**: exit 12 covers `a missing required key including a missing section on any op of any verb`.
- **D-03**: `Exactly two conditions are ambiguous` — (a) duplicate id inside one base section,
  (b) two ops resolving to the same section and id — each `exits 11 with AMBIGUOUS TARGET naming
  section, id and reason`; the cross-section third condition is argued out as unreachable.
- **T-01 intent** Step A (`a missing or empty section on an op of ANY verb, since D-02 makes section
  required everywhere` -> exit 12) and Step B (`there is no whole-file resolution (D-02)`).
- **SC-04** carries both retained conditions and states `There is no third condition`.
- **T-03 intent** propagates it to the contract text: `There is no whole-file id resolution and no way
  to omit section.`

Token grep over `BRIEF.md` + `plan.yaml`: `u4` and `case14(a)` still occur, at exactly three sites,
none of them a live requirement — (i) `plan.yaml` `panel.findings` PF-3f8a11143ba40f67b0f326d532381d5e
`summary`, which is a verbatim reader record pm must not alter; (ii) T-01 intent `There is no u4: the
cross-section ambiguity case it held is unrepresentable`; (iii) T-02 intent `The former sub-case (a)
... is DELETED, not renamed`. Both (ii) and (iii) assert non-existence. No site anywhere describes an
optional section or whole-file id resolution as live behaviour.

Both retained refusals survive with code and message shape: exit `11` /
`AMBIGUOUS TARGET section=<section> id=<target> reason=the id appears N times in section <section>`
and `AMBIGUOUS TARGET section=<n> id=<id> reason=two ops in one proposal name this target`
(T-01 intent Steps B and C; D-03; SC-04; integration `case14` sub-cases (b) and (c)).

### A3 — merge as authoring

Intact. **D-10**: `merge stays an authoring concept and is not a mechanism op; the tool refuses op
merge at exit 12 with a message naming the rewrite, a replace on the surviving id plus a drop of the
absorbed id.` The tool-side refusal is pinned character for character in T-01 intent Step A
(`MALFORMED OPS op=merge is not a mechanism op; express it as a replace on the surviving id plus a
drop of the absorbed id`), asserted by `u7`, cross-checked by `case17` and SC-09, and required of the
contract text by T-03.

### A4 — concurrency determinism and verify coverage

Mechanism (SC-11 / T-02 `case18`): the **test process itself** takes the production lock —
`with harness_merge.acquire(str(file_path) + ".lock"):` — and spawns both writers with
`subprocess.Popen` inside that block. Verified against source: `harness_merge.locked_update` derives
`lock_path = path + ".lock"` (`harness_merge.py:132`) and calls the same `acquire`
(`harness_merge.py:105-118`, flock branch, `USE_FLOCK = True` at `:35`), so the test holds the very
lock both children must take.
- **RED condition**: either child `.poll()`s non-None during the hold window (it did not take the
  shared lock, the D-09 regression); plus two further REDs — a writer's ids missing from the final
  Patterns census, and `P-07` still carrying its old text.
- **Polling interval**: 0.05s. **Hold duration**: 2.0s. Sits below
  `harness_merge.LOCK_TIMEOUT_SECONDS` = 10.0 (`harness_merge.py:36`, confirmed), so a correctly
  locking child is waiting, not refused at exit 6.
- **Worst case including the fail path**: 2.0s hold + two 20s `communicate(timeout=20)` waits, under
  45 seconds. `TimeoutExpired` is a FAIL, not a skip.
- **No production bypass**: read `expertise-merge.py` and `harness_merge.py` — the only module-level
  switches are `UNION_APPLY` (`expertise-merge.py:50`) and `USE_FLOCK` (`harness_merge.py:35`), both
  documented as selected by nothing at runtime, no flag and no environment variable. `case18`
  presupposes neither, and it needs no injected sleep or test-only flag; SC-11 and case18 both state
  `no edit of any kind to expertise-merge.py or harness_merge.py`.

T-03 verify greps: `expertise-merge.py ops --file`, `replace on the surviving id`,
`drop of the absorbed id`, `7 CONFLICT`, `8 CAP EXCEEDED`, `9 not an Expertise file`,
`10 MISSING TARGET`, `11 AMBIGUOUS TARGET`, `12 MALFORMED OPS`, `apply --entries` — the c1 gap
(exit tokens 7/8/9/12 and the apply-unchanged sentence) is closed.
T-04 verify greps: in the DEC-216 region `Chose:`, `Over:`, `Because:`, `Tradeoff accepted:`,
`DEC-66`, `DEC-95`, `DEC-145`; in SPEC.md `expertise-merge.py ops`, `10 MISSING TARGET`,
`11 AMBIGUOUS TARGET`, `12 MALFORMED OPS`; plus the index ruling grep and
`tests/integration/test-gen-decisions-index.py` — the c1 gap is closed.

Promised-by-intent but still unchecked by those two verify blocks (residual, none named by the c1
finding, and the first is covered elsewhere):
- T-03: the ops vocabulary line naming exactly `add, replace, merge, drop` — **covered** by `case17`'s
  two-directional CONTRACT/ACCEPTED assertion; the section-required prose; the two ambiguity
  conditions; the retained "nonexistent target is a contract violation" sentence — **unchecked**.
- T-04: SPEC's "both required on every op", replace-does-not-move, one-base-snapshot /
  order-independence, caps-evaluated-once, and "point at CAPS" — **unchecked**; DEC-216's body
  content beyond the four labels and three DEC references — **unchecked**.

## Part B — full re-grade of the current artifacts

**B-1. Issue Requirement clauses -> REQ.** No unmapped clause.

| Clause | REQ |
|---|---|
| explicit, deterministic operation keyed to an existing entry | REQ-01, REQ-02 |
| replace an existing entry atomically | REQ-01 |
| drop an obsolete entry | REQ-02 |
| preserve section caps | REQ-03 |
| reject missing targets | REQ-04 |
| reject ambiguous targets | REQ-05 |
| fail closed without partially rewriting | REQ-06 |
| compatible with concurrent union-merge behavior | REQ-07 |
| focused regression coverage (the list) | REQ-09 |
| the issue's Alternative (contract must not promise an unappliable op) | REQ-08 |

**B-2. Regression-sentence cases -> criterion, behaviourally exercised.** Every one runs the CLI, not
a source grep: replacement at capacity -> SC-01 (`case11`); removal -> SC-02 (`case12`); missing
target -> SC-03 (`case13`); ambiguous target -> SC-04 (`case14` b, c); atomic failure -> SC-05
(`case15`). REQ-09's two-ops-one-section clause -> SC-12 (`case19`, `u11`, `u12`). Gaps: none.

**B-3. Traceability, both directions.** SC -> T: SC-01..05 -> T-02; SC-06 -> T-02 `case16`; SC-07 ->
T-01; SC-08 -> T-02 `case11`/`case12`; SC-09 -> T-02 `case17` + T-03; SC-10 -> T-04; SC-11 -> T-02
`case18`; SC-12 -> T-02 `case19` + T-01 `u11`/`u12`. T -> REQ: T-01 [REQ-01..07], T-02 [REQ-01..09],
T-03 [REQ-08], T-04 [REQ-08]; every REQ-01..09 is traced. Orphans: `[]` both directions.

**B-4. Determinism of criteria.** Every SC names an observable — an exit code, an exact stdout token,
a sha256 comparison, an id sequence, or a named RED demonstration. Violators: `none`.

**B-5. Verifiability.** Confirmed on disk: `tests/integration/test-expertise-merge.py`,
`tests/integration/test-gen-decisions-index.py`, `.claude/skills/harness/bin/check-expertise.sh`,
`.claude/skills/harness/bin/gen-decisions-index.py`, `.claude/skills/harness-distill/SKILL.md` all
exist; `tests/unit/test-expertise-ops.py` does not and is created by T-01, which is correct. All four
verify blocks are targeted single-suite or grep invocations, no project-wide suite. Gaps: `none`.

**B-6. Internal consistency.** Cross-checked every D against every task intent and every citing SC.
Exit-code semantics are single-valued throughout (6 lock, 7 CONFLICT, 8 CAP EXCEEDED, 9 destination,
10 MISSING TARGET, 11 AMBIGUOUS TARGET, 12 MALFORMED OPS); D-12's drop+add-same-target is a strict
subset of D-03(b), not a third condition; SC-01's "7th ordinal" matches D-06 and `u1` index 6;
SC-11's timings match `case18` exactly; SC-04's two conditions match D-03 and `case14`. Two findings:

- **B-6.1 (record inconsistency, pre-signature fix).** D-15 states the high finding
  `PF-f4d258f365f54f04d9cc976baf0ad981 is resolved before signature`, yet `panel.findings` still
  carries `disposition: open` with no `resolved_by:` for it, and likewise for the two mediums the
  operator ruled on (`PF-3f8a11143ba40f67b0f326d532381d5e`, `PF-21e98fb21fbbe9fefe7c47cc9784c99b`)
  and `PF-0fd81890be0279f72e1fd44bc27f9828`. `harness-spec-driven` requires a finding pm believes
  fixed to read `disposition: resolved` with `resolved_by: T-NN`. The plan therefore asserts
  resolution in prose and non-resolution in the field the operator reads at signature. Cannot change
  what gets built; must be corrected before the signature. (`plan.yaml` `panel.findings`.)
- **B-6.2 (verify discrimination, advisory).** T-01's and T-02's verify strings run whole suites, so
  neither can detect an omitted case: if a builder never writes `u11`, `u12` or `case19`, both verifies
  still exit 0 and SC-12's evidence is unfalsifiable by the verify alone. T-03 and T-04 solved the
  same problem with token greps. Grading SC-12 will require reading the suites for those case names.
- Advisory, not a disagreement: **SC-12** declares `evidence: integration` while naming `u11`/`u12`
  (unit-kind assertions) as half its evidence; the unit half is nevertheless gated by SC-07's
  `tests/unit/test-expertise-ops.py` invocation, so nothing is ungated.

**B-7. Scope.** Inside the grilling note's allowed set (implementation, focused tests, governing
decisions/docs, lifecycle artifacts): T-01 the mechanism, T-02 focused tests, T-03 contract text,
T-04 SPEC + DEC-216 + index. Nothing touches the out-of-scope list (no unrelated cleanup, no
redesign, no compatibility shim). No risk acceptance, no scope reduction, no waiver — the three
remaining low/info findings are recorded, not waived, and the operator ruled only on the substantive
mediums. Structurally finishable inside 8 cycles: four tasks, one main-session barrier (T-03) already
priced in D-13. Uncovered-by-design, noted not waived: `PF-f9161ebeb204bb05a72667ebc1f7df84` (info) —
exit-12 byte-identity has no integration case.

**B-8. Dependency shape.** `T-01 -> T-03 -> T-02`, `T-01 -> T-04`. Acyclic and topological. No task's
verify asserts anything a predecessor deletes: T-02's `case17` reads the SKILL.md text T-03 writes,
which is precisely why T-02 `depends_on: [T-01, T-03]`; T-01 is forbidden from touching
`compute_union`/`cmd_apply`, so T-02's `case16` add-only assertions cannot be undermined. Gaps:
`none`.

## Open questions

- Q1 (non-blocking, for the main session at signature): B-6.1 — should the four addressed findings be
  flipped to `disposition: resolved` with `resolved_by:` before the operator signs, or left `open`
  for the cycle-2 panel to re-adjudicate and re-transcribe? Either is defensible; the plan currently
  contradicts itself.
