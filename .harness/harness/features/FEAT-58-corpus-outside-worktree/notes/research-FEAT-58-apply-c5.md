# Apply — operator cycle-5 answers — FEAT-58-corpus-outside-worktree

**All seven answers landed. Criteria 15 → 14, tasks 12 (unchanged), decisions 13 → 15, assertion
ledger 42 → 41 with ONE removal, named.** `plan.yaml` written only through `plan-merge.py`
(`apply` for D-14/D-15, `amend` for every revised field); `status: plan`, `approval.status:
pending`, `panel` and `lanes` untouched — the diff has no hunk in `plan.yaml`'s panel region.
`BRIEF.md ## Approval` still `status: pending`. `check-plan-routes.py plan.yaml` → **0 violations,
exit 0** (12 TASK `DEVIATION` lines, the DEC-174 carve-out working).

## One ruling I had to take, and it is the only place I departed from the dispatch text

The dispatch says "the two-gate denial widening … STAY". The authority says the opposite about the
first gate: Q1 orders **"no `_hardlink_plan` change"** and "the code the finding was against no
longer exists in the plan" (`notes/answers-operator-c5.md:29-38`), and Q6's heading is "STRIKE the
hardlink half". Keeping the `_hardlink_plan` widening while striking SC-15 and PART 4/5(a)(b)
would have left either (i) the uncaught `corpus_root()` raise VL-01 measured — exit 1, and
`check-domain.sh:14` says exit 1 is non-blocking and the write proceeds — or (ii) the error
conversion Q1 forbids; and it would have left a widened security guard with no criterion and no
test, which is the exact shape Q6 reason (iii) rejects. **I followed the authority: N-11's
check-domain.sh half is struck.** Reconciling reading: the "two-gate/two-route denial" that
survives is D-02's Write/Edit + Bash pair, which N-03 carries and SC-03 grades — untouched. Raised
as an open question rather than decided silently.

## Per answer

| answer | disposition | where |
|---|---|---|
| **Q6** strike the hardlink half | **landed** | new **D-14** (three reasons verbatim in substance, D-2-still-delivered, #1638); SC-15 deleted; N-11 reduced; D-02 `because` tail corrected (it claimed "N-11 closes it and SC-15 grades it") |
| **Q1** VL-01 dissolved | **landed as dissolved-by-Q6** | D-14 `because` closes: "DISSOLVED BY THIS DECISION - NOT FIXED, AND NOT MISTAKEN", with `check-domain.sh:14` quoted and the operator's own verification named. No fifth case, no error conversion, no `_hardlink_plan` change |
| **Q2** VL-02, skip announced | **landed** | D-13 `choice` gains the resolvability arm, the announced skip, the once-local-full-clone rule and the rejected `fetch-depth: 0` with its measured premise; N-09 PART 3 clause 3 SELF-SCOPE now two conditions, `git cat-file -e` per endpoint, the skip **prints its reason and names the endpoint** and the test asserts the line; a new discrimination case proves the announce fires |
| **Q3** VL-03 | **landed** | new **D-15**; `MARK THE SITE` struck from N-06 PART 2 (`plan.yaml:1604`, now "DO NOT MARK THIS SITE"); **both** N-12 assertions quantify over DETECTED sites (`:2347-2350`) |
| **Q4 / VL-05** | **landed** | N-09 `cross_module → scaffolding` with the in-task justification; `tests/unit/test-nonregression-notes.py` struck from `files:` and `verify:`; its four behavioural cases moved into PART 3 clauses 4-7, beside their one consumer |
| **Q4 / VL-06** | **landed** | N-01 EXCLUSION 1 keeps the literal list, `--strict` existence failure and both greps with the shown-to-fire proof; the runtime list-equals-plan comparison and the non-strict PENDING accounting are struck, and N-09's `--strict` run is named as the sole discharge site so a zero-file run cannot read as discharged |
| **Q4 / VL-07** | **dissolved, no residual added** | verified at source: the withdrawn claim occurs **only** inside the frozen `panel` record (`plan.yaml:731-736`, left alone). D-10 `because` and N-02's scope guard carry no probe-stripping language — N-02 says the guard exists so "the hook tier does not start refusing trees this feature never claimed", which already matches the amended note (`dod-worktree-corpus-2026-09-10.md:136-143`). Nothing to correct, nothing added |
| **Q4 / VL-08** | **landed** | construction clauses struck from SC-01, SC-09, SC-11, SC-13, SC-14; each survivor re-verified in the CURRENT text (table below). No `approval.rulings` entry; nothing accepted or deferred |
| **VL-04** | **recorded, not fixed** | the `_SWEEP_PATTERNS` blind class is now a named block in N-12's intent (`:2304-2314`): list-of-strings via a for-loop binding, one-level *assignment* resolution cannot see it, D-02 forbids the change, the resolver is not to be built, and the prospective cost is stated |

## VL-08 — every struck clause, and where it survives now

| criterion | clause struck | survives at |
|---|---|---|
| SC-01 | "asserted individually, never as one aggregate clause" | N-05 group 2, `plan.yaml:1460` |
| SC-01 | "its own clause and never a bare existence check" | N-05 group 2, `:1467-1470` |
| SC-01 | "the failing state … is demonstrated first" | N-05 group 1, `:1420-1423` |
| SC-09 | "asserted by the invocation it records, never by exit 0" | N-06 PART 3 (a), `:1647-1649` |
| SC-11 | "the pre-change shape is reproduced in the same file" | N-04 PART 2 step 4, `:1330-1333` (and PART 3 step 4, `:1350-1351`) |
| SC-13 | "with BOTH the stdout and the exit status asserted …" | N-09 PART 3 clause 3, `:2036-2040` |
| SC-14 | "asserted per site with its own named case and never as one aggregate" | N-10 PART 5, `:2175-2177` |

SC-11 keeps "The merge case must FAIL today" (an outcome, and `IT MUST FAIL TODAY` at `:1311`
carries it) and the host baseline figures, which are the operator's measurement, not construction.

## The ledger — 42 in, 41 out, one removal

**Removed, by name: `hardlink deny + positive control (N-11)`** — one of the six rows added at
cycle 3 (`notes/research-FEAT-58-apply-batch-c3.md:55-57`). Reason: Q6's deliberate strike. Its
positive-control half is not lost as a claim — A-07 already asserts a write to the active feature's
own directory succeeds through both registered entrypoints (N-03, SC-03).

Nothing else fell, and two candidates were checked rather than assumed:
- the struck `test-nonregression-notes.py` is **not** a ledger row (it was GC-06's remedy for the
  `cross_module` label); its four assertions moved into `test-nonregression-baseline.py`.
- N-01's list-equals-plan comparison is **not** a ledger row either (GC-03's remedy); X-1 and X-2
  stand, with `--strict` as their discharge.

## Consistency check worth keeping

The marker instructions now cover the detected set **exactly**: N-06 21 (`check-state.sh`) + 1
(`check-domain.sh`, comment only) · N-07 1 (`merge-gate.py`) · N-10 6 · N-11 1
(`branch-create-gate.sh`) = **30**, the measured in-subject census. Before this pass N-06 PART 2
instructed a 31st marker on a site the detector cannot see, which is what made N-12 unpassable.

## Open questions for the tier above

1. **N-11's test kind.** Post-strike N-11 holds one production file and one *integration* test; its
   unit half was PART 4. `cross_module` (and `logic`/`feature`/`bugfix`) all require `unit`, so the
   qa matrix has no satisfied unit kind for it, and the only labels that avoid `unit` —
   `scaffolding`, `docs`, `config` — would be dishonest for a gate-behaviour change. I left
   `change_type: cross_module` and said so inside the task rather than relabelling. The clean
   answer is probably to fold the branch-gate work into **N-10** (already unit + integration, same
   "widen to the owner root behind `feature_corpus`" subject; its separation rationale was the
   security-hole failure mode Q6 removed) — but that merges a task the dispatch told me to keep.
2. **The dispatch/authority conflict** recorded above, in case the lead meant `_hardlink_plan`'s
   widening to survive on its own. If so, it needs an answer to VL-01 that Q1 forbids.
