# Goal-check — FEAT-104 drafted plan vs the operator's stated intent — cycle 0

**Does this plan deliver the operator's stated intent? NO — qualified.** Seven of the eight intake
clauses are carried by a REQ/SC/T-NN. Two defects block: (1) **T-04's legal key set, as specified,
rejects 15 fields that 7 personas' own documented DIGEST blocks instruct** — the strictness that is
supposed to protect the contract would refuse every conforming reviewer, qa, documentor,
visual-designer and dev-ops return, and no criterion catches it because the triage corpus was
lead-only; (2) **nothing makes step enforcement bind** — D-06 gates it on `schema_version: 2`, only
prose asks a new run to seed 2, and SC-11 pins the version-1 escape as *intended*. Both are one-edit
fixes at plan time. Plus one hard contradiction: **T-01's `verify:` cannot pass given T-01's own
`intent:`**.

## Findings

- **F1 critical — REQ-04 fails as specified.** T-04's set is `UNIVERSAL + headline +
  SCHEMAS[persona] + PASSTHROUGH + {code_grade, reviewed, grade_2_reasons}` (plan.yaml T-04
  `intent:`). None of these 15 documented fields is in it, and none appears anywhere in
  `validate-digest.py` (grepped, 0 hits each): code-reviewer `spec_violations`,
  `human_commits_in_scope` (`.claude/agents/harness-code-reviewer.md:89,93`); security-reviewer
  `in_scope`, `scope_reason`, `threat_model` (`:91,92,98`); ui-reviewer `mode`, `in_scope`,
  `states_unspecified`, `contract_violations` (`:101,102,108,109`); qa `kinds`, `sc_evidence`
  (`harness-qa.md:90,92`); documentor `stale_found` (`:60`); visual-designer `needs_prototype`,
  `why`, `prototype` (`:78,79,81`); dev-ops `test_kinds_written` (`:98`). Clean: `pm`, `dev`
  (`harness-digest-dev/SKILL.md:16-32`), `lead`, `orchestrator`. **Why nothing catches it:** the
  triage measured run `digest.md` artifacts and *all 319 infer as `lead`*
  (`notes/research-FEAT-104-triage-c0.md:37`), so 8 of 9 personas' live returns were never in the
  corpus; SC-05 then grades "every key the triage declared legitimate" — a set derived from the
  artifact under grading. DEC-216's contract test checks required→documented only, never
  documented→schema, which is the same blind spot one direction over.
- **F2 high — T-01's `verify:` is unsatisfiable.** `intent:` says "Expect
  `run_documented_contract_cases` to FAIL at the end of this task"; that function's failures feed
  `fails`, which makes the runner print `N FAILING.` and `return 1`
  (`tests/integration/test-validate-digest.py:4292-4294`). T-01's `verify:` does
  `out=$(...) || exit 1` and `grep -q 'ALL PASSED'` — both clauses red. Fix: land T-01+T-02 as one
  task, or have T-01 assert the single expected failure by name.
- **F3 high — step enforcement never binds.** T-06/T-07 run only at `schema_version >= 2`; the only
  surface that names the seed is `harness-team/SKILL.md:54` ("Seed `state.yaml` with
  `schema_version`, …" — no value), which T-05 edits to say `2`. No gate refuses a *new* run seeded
  at 1, and SC-11 asserts version-1 undeclared keys are **accepted**. So REQ-02 ("a new write … is
  rejected") holds only for runs that opt in, decided by the same agents whose drift it governs.
- **F4 med — T-08/SC-06's base revision is under-pinned.** The copy must be a commit containing
  T-01 but not T-04. T-01 makes `adequacy_notes` required; if T-01 and T-04 land in one commit (same
  two files), "the commit before T-04" lacks it and the unknown-key payloads exit 2 there for the
  wrong reason, so the case reddens on ordering, not on behaviour. Name the required base explicitly.
- **F5 med — D-02's 3+ bar rejects a real qa field.** `coverage_gaps` is a **required** member of
  `SCHEMAS["qa"]` (`validate-digest.py:193`) and appears on 2 lead roll-ups, so the triage files it
  as drift (`triage-c0.md:55,62`). REQ-04 reads "no legitimate return … becomes newly rejected"; a
  lower tier's required field riding up is exactly what PASSTHROUGH exists for. Operator item 2.
- **F6 med — one uncovered D-03 surface.** DEC-126's Applied record names `adequacy_notes` as the
  *validator-lead's* per-role extra (`DECISIONS.md:2612-2613`). D-03 makes it required of all three
  leads. No task's `files:` includes that entry, and T-09 forbids amending an existing one.
- **F7 low — T-07's verify grep is generic.** It greps the suite's output for `schema_version`, not
  for the new behaviour's own vocabulary; a case merely *named* for the version satisfies it.
  Contrast T-06's `undeclared step key` (0 occurrences today) and T-08's `pre-change validator` (0).
  All of T-03's six per-file greps are 0 today and each file is asserted separately — correct shape.
- **F8 low — SC-12's comparator default path is worktree-scoped** (T-10 `verify:` line 431). Graded
  at ship while the worktree exists, so it holds; a post-merge re-run needs the explicit argument.
  Note the manifest is taken at the **owner root**, and this feature's own runs live in the
  **worktree** (2 present) — so the feature cannot redden its own criterion.
- **F9 low — SC-14 is near-unfailable.** No task writes a historical file and SC-12 already grades
  content. Keep as a cheap parse guard; do not count it as independent evidence.
- **F10 info — anchors.** Verified correct: `SCHEMAS` 183-229, `check-state.sh` `CHECKPOINT_KEYS`
  1394 / report 1473, `stop_hook_active` 1744. Drifted: the lead digest block is
  `harness-team/SKILL.md:237-258`, T-02 cites 238-249. T-02's `^  adequacy_notes:` anchor matches the
  block's two-space indent.
- **F11 info — the manifest deviation bears on no declared lane.** The missing line is pm's
  `receipt-*.md` grant; no task writes a receipt, and T-09 is the only `team` task (DECISIONS.md +
  -INDEX.md, documentor).

## A. The eight intake clauses

| # | Clause | Verdict | Carrier / gap |
|---|---|---|---|
| 1 | Digest strictness, actionable repair naming key + route | **MET** | REQ-01/05, SC-01/02/07/08, T-04 |
| 2 | Step-level strictness where nothing governs today | **GAP** | Mechanism T-05/06/07, SC-03; **F3** — no gate makes a new run declare 2 |
| 3 | Declared free-form evidence container | **MET** | REQ-03, D-05, SC-04, T-05/T-06 (nested values refused, stated) |
| 4 | Historical readable; binds new returns/writes | **MET** | REQ-08, D-06, SC-11/12/14, T-10 |
| 5 | Both regressions; #37/#44 get a real boundary | **MET** | SC-05 + SC-06, T-08; #44 named unblocked only |
| 6 | Every measured key dispositioned | **GAP** | Partition closes arithmetically (65 = 3+1+61; 202 = 21+30+7+144, `triage-c0.md:43-137`) and D-01/02/04/05/09 + T-03/T-05 carry it. The leak is not in the measured set — it is the **unmeasured** one: **F1**, 15 documented keys on 7 personas the corpus never contained. Secondary: `coverage_gaps` (**F5**) |
| 7 | No historical rewrite, no FEAT-08 fold | **MET** | D-06 + SC-11/12; no FEAT-08 path in any `files:` |
| 8 | #37 resolved in this feature | **MET** | REQ-07, D-03, T-01+T-02 as step 1, SC-10 |

## B. SC-01..SC-14 — would a wrong implementation go RED?

| SC | Discriminating? | Reason |
|---|---|---|
| 01 | yes | positive+negative on one payload; a no-op exits 0 and fails it |
| 02 | yes, per persona | one case each, asserted separately (P-04). Blind to F1: minimal valid payloads omit the 15 fields |
| 03 | yes | refusal + key named at v2 |
| 04 | yes | both directions inside `evidence:` |
| 05 | **weak** | form is right (one assertion per key), but the grading SET is the plan's own triage — cannot fail on a key never measured (F1) |
| 06 | yes — strongest | red against a pinned pre-change copy; the only criterion that falsifies "rejects nothing". Base-pin risk = F4 |
| 07 | yes | one message naming all three; naming the first fails |
| 08 | yes | substring assertion on file+symbol, not non-emptiness |
| 09 | **pin, not proof** | already true today (`validate-digest.py:1744`); it fixes the property as deliberate. Correct, but no new behaviour |
| 10 | yes | schema requiredness AND the DEC-216 documented case; omission reddens (`test-validate-digest.py:311-313, 4292`) |
| 11 | yes | v1 accept / v2 refuse, both asserted — and it is what makes F3 invisible |
| 12 | yes | replacement checked against T-10's actual `verify:` body: content sha256 over a tracked manifest, `assert 726 <= n` truncation guard, `argv[1]` override, exit 1 on changed/vanished, discrimination demonstrated not asserted (`triage-c0.md:189-194`). The cycle-0 vacuity is genuinely gone. Residual = F8 |
| 13 | n/a (uat) | correct method; DEC-174 admits no substitute |
| 14 | **weak** | near-unfailable (F9); decidable, cheap, redundant with SC-12 |

## C. Traceability — closed, both directions

| REQ | SCs | Tasks | Orphan |
|---|---|---|---|
| REQ-01 | 01,02,06,07,08 | T-03, T-04, T-08, T-09 | none |
| REQ-02 | 03, 11 | T-05, T-06, T-07, T-09 | none |
| REQ-03 | 04 | T-03, T-05, T-06, T-09 | none |
| REQ-04 | 05 | T-01, T-08 | none |
| REQ-05 | 08 (01/03 name the key) | T-04, T-06 | none |
| REQ-06 | 09 | T-04, T-09 | none |
| REQ-07 | 10 | T-01, T-02, T-09 | none |
| REQ-08 | 11, 12, 14 | T-05, T-06, T-07, T-10 | none |

| Task | REQs | Orphan |
|---|---|---|
| T-01 | 04, 07 | none |
| T-02 | 07 | none |
| T-03 | 01, 03 | none |
| T-04 | 01, 05, 06 | none |
| T-05 | 02, 03, 08 | none |
| T-06 | 02, 03, 05, 08 | none |
| T-07 | 02, 08 | none |
| T-08 | 01, 04 | none |
| T-09 | 01, 02, 03, 06, 07 | none |
| T-10 | 08 | none |

No orphan in either direction. SC-13 traces to no task by construction (uat, operator-executed).

## D. `depends_on` — acyclic, and the ordering holds

Edges: T-10 ← nothing; T-01←[T-10]; T-02←[T-01]; T-03←[T-02]; T-04←[T-01,T-03]; T-05←[T-03];
T-06←[T-05]; T-07←[T-05]; T-08←[T-04,T-06]; T-09←[T-04,T-06,T-07,T-08]. **Acyclic**; valid
topological order `T-10, T-01, T-02, T-03, T-05, T-04, T-06, T-07, T-08, T-09`.

**T-10/T-01 adjudicated: honest as written.** T-10's `intent:` prose "must land before T-01" is
*declared* on the consumer side — `T-01.depends_on: [T-10]` — which is the only side
`teams/build.yaml` reads (`from_task_depends_on`). `T-10.depends_on: []` is correct, not a
contradiction; a reverse edge would be the bug.

**T-01's `verify:` vs its own `intent:` adjudicated: NOT satisfiable.** See F2 — the documented-
contract failure the intent predicts makes the suite exit 1 and print `N FAILING.`, so both of
T-01's `verify:` clauses fail. This is the one intra-task contradiction in the plan.

Other silent-artifact assumptions checked: T-06 and T-07 both read `run-state-schema.json` and both
declare `depends_on: [T-05]` — sound. T-08's base revision is the F4 gap. T-09's
`gen-decisions-index.py --stdout` exists (`gen-decisions-index.py:6,253-259`) and both index files
are in `files:` (G-04 satisfied).

## E. D-01..D-09 — all are decisions, none restates a requirement

Every one survives the swap test and clears the DEC-149 bar (hard to reverse, surprising without
context, a real trade-off). Two narrow the intake's promise and the operator should see it:
**D-02** narrows REQ-04's "every key in legitimate use" to "3+ occurrences in a lead-only corpus"
(F1, F5); **D-06** narrows REQ-02's "a new write is rejected" to "a new write that opts in" (F3).

**D-03 blast radius vs the plan's `files:`**

| Surface | Covered |
|---|---|
| `validate-digest.py` `SCHEMAS["lead"]` | T-01 ✓ |
| `tests/integration/test-validate-digest.py` (`_required_contracts`, :385) | T-01, T-08 ✓ |
| `harness-team/SKILL.md` lead block — the DEC-216 source for **all three** leads (:311-313) | T-02 ✓ |
| `.claude/agents/harness-validator-lead.md` (:130) + `.omp/agents/` twin | T-02 ✓ |
| `.claude/agents/harness-{product,eng}-lead.md` + `.omp/` twins | in T-03's `files:`, but T-03's `intent:` adds only the drift phrase. Acceptable — both point at the canonical block (DEC-126) and product-lead's own extra is `needs_approval` (:86) |
| `DECISIONS.md:2612-2613` DEC-126 Applied record | **no task** — F6 |
| Every live lead return from T-01 onward (a lead omitting the field exits 2, including this feature's own build runs) | not a file; no task or SC names it |

**D-06 blast radius vs the plan's `files:`**

| Surface | Covered |
|---|---|
| `run-state-schema.json` (new, the key set) | T-05 ✓ |
| `check-domain.sh` write-payload path | T-06 ✓ |
| `check-state.sh` sweep (`CHECKPOINT_KEYS` :1394, report :1473) | T-07 ✓ |
| `harness-team/SKILL.md:54` — the only seed instruction | T-05 ✓ |
| Top-level whitelists already carrying `schema_version` (`check-domain.sh:1535`, `check-state.sh:1396`) | no change needed ✓ |
| Anything that *enforces* the seeded value | **nothing** — F3 |
| Other `schema_version` readers checked and unaffected: `inflight_registry.py` (own file), `upgrade-config.py` / `check-plan-routes.py:728` (harness.json, feature dirs) | n/a ✓ |

## F. Operator-only decisions

1. **F1's remedy shape.** Add the 15 documented fields to each persona's `SCHEMAS` (DEC-121 makes
   them REQUIRED, and DEC-216 then binds each documented block), or declare a per-persona
   **optional typed** table beside `PASSTHROUGH`. *Recommend:* the optional table — requiredness
   would force 15 new mandatory fields on 7 personas in one step, none of which the corpus measured.
2. **D-02's 3+ bar over `coverage_gaps`.** *Recommend:* add it to `PASSTHROUGH["lead"]` as
   `list`. It is qa's own required field (`validate-digest.py:193`), not invented vocabulary; the
   bar was written against one-off inventions.
3. **F3 — whether a floor is in scope.** *Recommend:* yes, one clause in T-06 — `check-domain.sh`
   refuses the **creation** of a run `state.yaml` declaring `schema_version` below 2 — plus an SC.
   Without it REQ-02 is satisfied by prose.
4. **D-03's requiredness (lead-only, required list).** *Recommend:* proceed as drafted; it is the
   whole fix for #37. Consequence to accept: from T-01 onward every lead return omitting it exits
   2, including this feature's own build runs — which argues for landing T-01+T-02 as one commit
   (also closes F2).
5. **SC-13's UAT.** DEC-174 requires the operator personally to read the four-file diff. Not
   delegable, not automatable. *Recommend:* keep as `verify: uat`, unchanged.
6. **F6 — DEC-126's stale Applied record.** Amending a shipped entry is the operator's call.
   *Recommend:* widen T-09's `intent:` to correct that one clause, since D-03 falsifies it.

`BRIEF.md` and `plan.yaml` are byte-unchanged by this run.
