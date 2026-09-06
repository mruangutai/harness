# Goal-check — BUG-440 plan vs the operator's stated intent — c1

**Does this plan deliver the operator's stated intent? YES — after four defects this check found and
fixed.** Every line of the grilling is delivered; nothing is contradicted; two silences are delivered
by construction. Four findings were corrected in place (BRIEF ×3 clauses, plan T-01 `intent` ×2
clauses). **One item still needs the operator, and it is a ruling, not a defect:** whether `/harness`
entry may stay red with 4 blocking findings until the four live records are reconciled separately.

Grading source: `.harness/notes/grilling-digest-verdict-reconciliation-2026-09-06.md`. Where the
BRIEF and the grilling disagreed, the grilling won.

## 1. Intent coverage — every grilling line, one row

Line numbers are the grilling's. Plan cites are `plan.yaml:NN` / `BRIEF.md:NN` at post-correction
state.

| # | Grilling line | Verdict | Where |
|---|---|---|---|
| S1 (:7) | equal `VERDICT:` vs `runs[].verdict`; mismatch is a blocking state-check violation | delivers | `BRIEF.md:30-34` REQ-01 ("the violation list that fails the check"); `plan.yaml` T-01 intent, "append to `bad` - the BLOCKING list, never `warn`" |
| S2 (:8) | detect and report; no auto-repair of either record | delivers | `BRIEF.md:46-48` REQ-04; SC-04 hash-before/after; T-01 intent "Write NOTHING: no repair, no rewrite, no move" |
| S3 (:9) | scope is completed lead-hosted runs with durable digests; non-lead, incomplete, missing, legacy unchanged | delivers, with one reading to rule on (F-05) | `BRIEF.md:37-45` REQ-03(a)-(e); SC-03 pins each case separately |
| S4 (:10) | BUG-440, full BUG flow, known cause skips the debug segment | delivers **by construction** — no text says it | plan carries exactly one task and no investigation/debug task (`plan.yaml` `tasks:` = T-01). Informational (F-08); no change |
| S5 (:11) | `check-state.sh` and its test are main-session-direct | delivers | `plan.yaml:12-19` lanes rows; T-01 `execution_mode: main-session-direct` + `execution_reason` (DEC-174). Both grants re-measured — see §5 |
| O1 (:17) | no retroactive repair of historical records | delivers | REQ-04; `BRIEF.md:99-100` out-of-scope; disclosure at `BRIEF.md:101-114` states the consequence rather than quietly repairing |
| O2 (:18) | no change to cycle accounting, `feature.json` schema, digest-return semantics | delivers **by construction**, no criterion quantifies it (F-06) | T-01 `files:` names only `check-state.sh`, `test-check-state.py`, the red-proof note; D-04 forbids widening the `runs` 3-tuple; SC-06 catches behaviour drift |
| F1 (:21) | "FEAT-22 recorded one `digest.md` FAIL vs `feature.json` PASS mismatch" | **contradicted by disk — the grilling's fact is wrong** (F-02) | see §3; contract unchanged |
| F2 (:22) | `check-state.sh` validates the digest structurally but never compares its verdict | verified true, delivered | `check-state.sh:1516-1535` re-read: `validate("lead", ...)` at :1529, no comparison anywhere in the branch. T-01 hosts the check inside that branch |
| F3 (:23) | `runs[]` has `id`, `squad`, `verdict`; run id maps to `runs/<id>/` | verified true, delivered | `check-state.sh:643-652` (3-tuple), INV-15 glob `H + "/*/features/*/runs/*/state.yaml"`; D-04 builds its side dict from that same loop |

No grilling line is silent in the sense that matters — S4 and O2 are delivered by the shape of the
task list rather than by prose, which is the correct home for both.

## 2. The four required areas — and the criterion that goes red

| Area | REQ | SC that FAILS on regression | Can it go red? |
|---|---|---|---|
| (i) mismatch is BLOCKING and names five things | REQ-01 | SC-01 — exit non-zero **plus six separate substring assertions** (feature, run id, digest verdict, recorded verdict, both paths) | Yes, twice over: append to `warn` instead of `bad` and exit stays 0 → the exit clause reddens; drop any one of the five and its own substring reddens (no file-global match — P-04 satisfied) |
| (ii) equal values produce no finding | REQ-02 | SC-02 — second **clean** tree, exit 0 and no `INV-37` line; explicit "FAILS IF the check is satisfied by the mismatch fixture alone" | Yes. A check that fires on everything passes SC-01 and fails SC-02. This is the control, and it exists |
| (iii) preservation of non-lead / incomplete / missing-digest / invalid-digest / unclaimed-directory | REQ-03(a)-(e) | SC-03 — one assertion per case, runs N, I, G, X, O in one mixed tree; G and X also assert **exactly one** existing violation and no second line | Yes, per case. The stacked-finding regression (a second line on X) is the one a naive implementation causes, and X's "exactly ONE" clause is what catches it |
| (iv) no auto-repair | REQ-04 | SC-04 — sha256 of `feature.json` and of every `digest.md` taken on both sides of the invocation | Yes, though it is the least likely to fire. It is falsifiable and cheap; keep |

No area rests on a criterion that cannot go red. SC-06 (whole-file `test-check-state.py`, exit 0, no
`FAIL` line, baseline 216 lines / 51.9s at `772790be`) carries the cross-invariant regression risk,
and SC-07 pins the semantics to `validate-digest.py:1155-1160` — both re-read and accurate.

## 3. The two record items — independently re-measured

**Method**: for every `feature.json` `runs[]` entry whose `runs/<id>/state.yaml` is `complete` with
`host` in the three leads, digest present, `validate("lead", text) == []`, compare the tail-anchored
`VERDICT:` against the recorded `verdict` by exact string equality — i.e. the operator-approved
contract, executed. Run 2026-09-06 against `/Users/molchairuangutai/GitHub/harness/.harness`.

```
complete_lead 308  with_digest 308  valid 308  claimed 298  mismatch 4
```

**Item A — corpus figures: I agree with the orchestrator; the BRIEF was wrong.** 308 is the count of
completed lead-hosted runs (all 308 carry a digest, all 308 structurally valid); **298 is the
COMPARED count** — the ones a `feature.json` `runs[]` entry claims. The remaining 10 run directories
are unclaimed and out of scope by construction (REQ-03(e)). The BRIEF said "298 … carry a digest",
and the same wrong sentence had been copied into T-01's `intent`. **Both corrected** (F-01). The
baseline also now carries its condition: run directories are untracked and per-checkout, so the sha
pins the code that read the tree, not the tree.

**Item B — the four mismatches, reproduced verbatim, identical to the orchestrator's probe:**

| feature | run id | digest | feature.json |
|---|---|---|---|
| FEAT-07-verify-teeth-batch-probe | goalcheck-product | ESCALATE | FAIL |
| FEAT-22-docs-layout-migration | 2026-08-16-15-distill-product | PASS | INCOMPLETE |
| FEAT-22-docs-layout-migration | 2026-08-16-15-distill-validator | PASS | INCOMPLETE |
| FEAT-25-claim-feature-root | 2026-08-19-6-distill-validator | FAIL | PASS |

**Does the correction change the contract? No — explicitly no.** The contract quantifies over *every*
mismatch, in either direction, over any pair of token values, by exact string equality. It never
names FEAT-22, never names a direction, and never enumerates tokens. The grilling's F1 was
motivating evidence, not a requirement: it survives as "the class exists and was found by hand", and
that is still true. Nothing in REQ-01..04, SC-01..07, D-01..06 or T-01 keys on which feature carried
which direction. **No task changes, no criterion changes.** Two consequences that are *not* contract
changes and are now visible where the operator signs: the FEAT-22 rows are digest `PASS` over a
recorded `INCOMPLETE` — a value that is not a legal digest verdict at all, which is precisely what
exact equality (no aliasing, no normalisation) is for; and the sole PASS-over-FAIL record is
FEAT-25's, which the BRIEF already attributed correctly at `BRIEF.md:16-17`.

## 4. Scope discipline — both directions

**Specified but not asked for.** D-02 (INV-37 numbering), D-03 (no DECISIONS entry owed), D-04 (side
dict keyed on feature directory path), D-06 (accept `check-plan-routes.py` DEVIATION lines) are all
mechanism inside a surface the grilling put in scope — none creates work beyond the one task. The
BRIEF's disclosure is not scope: it adds no task and spends no cycle.

**Ruling 1 — the red proof (T-01 `files:` `notes/redproof-BUG-440.md`, SC-05): INTENT-FAITHFUL,
keep it.** Conclusion unchanged; its GROUND is corrected here after panel finding
PF-dcb6d405dd9dfba7c620224365930746 (should-not-exist, info, 2026-09-06). What the note witnesses
is **NON-VACUITY**: that `case_bug440_digest_verdict_reconciliation()` actually fails against the
pre-change `check-state.sh`, so the case cannot be an ever-green assertion. It does **not** witness
test-first ORDERING, and this note previously claimed it did ("the only evidence the ordering
happened"): `CHECK_STATE_BIN` pointed at a `git show 772790be` copy is reproducible at any time,
including after the check was written, so nothing in the artifact places it before the
implementation. The ruling stands on the corrected ground: the grilling bought the *full Harness
BUG flow* (S4), a case that has never been shown to fail proves nothing, and T-01 is
main-session-direct with test and implementation in one task (D-01) — so without this artifact the
only automated evidence of a discriminating test is the task's own `verify:`, which the case would
satisfy either way. SC-05 grades it `verify: inspection` read through
`git show <review_sha>:...`, so an uncommitted or absent note fails. One note file, zero extra
cycles. It would be scope creep only if the grilling had waived the BUG flow, and it did the
opposite.

**Ruling 2 — D-05's narrowed task verify: no REQ is left unverified at task-verify time.** The
single imported case `case_bug440_digest_verdict_reconciliation()` contains the whole mixed tree
(M, E, N, I, G, X, O), the sha256 before/after assertion, *and* the second clean tree — so REQ-01
(M), REQ-02 (E + clean tree), REQ-03 (N, I, G, X, O) and REQ-04 (hashes) all execute inside it. What
D-05 defers is **not a REQ but cross-invariant regression safety**, which is SC-06's job and the qa
gate's, and D-05 says so. The 60s ground is sound: 51.9s measured for the whole file leaves no
headroom under sibling load, and the exemplar `case_bug1305_run_identity_invariant()`
(`test-check-state.py:4560-4615`) is self-contained and returns a bool, so the import-and-call
invocation in T-01's `verify:` works — the `__main__` guard is at :4789, so `exec_module` runs no
tests. Verified, not assumed.

**Quietly widened or narrowed: none found.** REQ-03's five cases are a *superset* of the grilling's
"non-lead, incomplete, missing" — (d) invalid-digest and (e) unclaimed-directory are boundaries the
implementation must decide anyway, and deciding them in the BRIEF is the opposite of widening scope.
See F-05 for the one reading the operator should confirm.

## 5. The disclosure — graded (a)/(b)/(c)

- **(a) Accurate: yes on content, defective on presentation — fixed.** All four rows and the count
  matched my measurement. But the pairs were written unlabelled (`FEAT-25 PASS/FAIL`), so a reader
  could not tell which value came from which record — in a disclosure whose entire point is *which
  record is wrong*. Now written explicitly as *recorded → digest says*, per row, with the run ids.
- **(b) Placement: adequate, and now stronger.** It sits in `## Constraints`, roughly fifteen lines
  above `## Approval`, bolded, on the last screen an operator reads before signing. It does not need
  to move to `## Problem`: it is a consequence of the design, not the motivating defect.
- **(c) Consequence with a named owner: was a consequence, was not answerable — fixed.** The old text
  said "the operator rules on it at signature" while posing no question, and left the reconciliation
  ticket ownerless. It now carries an answerable ruling and names the operator as the owner of
  filing the reconciliation ticket. No apology in either version — correct tone throughout.
  **Amended 2026-09-06 after panel finding PF-3f3c8cbd75c6538ac820075bfc6efe9b:** this goal-check
  posed the ruling as a yes/no, which was a false dilemma — reconcile-first was never offered.
  `BRIEF.md` now offers three options and is the authoritative wording.

**The ruling the operator must answer at signature — one choice of three:**

> Which do you choose? **(A)** `/harness` entry stays red with 4 blocking INV-37 findings —
> FEAT-07, the two FEAT-22 rows recorded `INCOMPLETE`, and FEAT-25 — until you or a delegate
> reconciles those four records under a separate ticket you own filing. **(B)** Those four
> `feature.json` records are reconciled FIRST and this merges into a green gate: they are
> per-checkout data edits independent of this code change, so B adds no scope, no task and no
> criterion. **(C)** Neither, and the plan goes back before signature for repair or grandfathering
> scope it does not have today.

## 6. Findings — severity and disposition

| id | Sev | Finding | Disposition |
|---|---|---|---|
| F-01 | MED | 298 stated as the digest count in `BRIEF.md` Problem **and** copied into T-01 `intent`; baseline pinned to a sha over untracked run directories with no condition | **Corrected both** (G-13): `BRIEF.md:5-18` and `plan.yaml` T-01 `intent` para 1 — 308/308/298/4, dated observation, condition stated |
| F-02 | MED | Grilling fact F1 is false on disk: FEAT-22's mismatches are digest `PASS` over recorded `INCOMPLETE`; the PASS-over-FAIL record is FEAT-25's | **Contract unchanged** (§3). `BRIEF.md:5-7` reworded so it no longer locates the FAIL-over-PASS record in FEAT-22; the correction reaches the operator in the briefing |
| F-03 | MED | T-01 `intent` (b) said "the existing `else:` arm, where `_errs` is FALSY" — but the existing `else:` at `check-state.sh:1527` is entered for valid *and* invalid digests; a literal reading stacks a second finding on an invalid digest, regressing REQ-03(d) | **Corrected**: now "a NEW `else:` arm on the `if _errs:` test at :1532 … never the outer `else:` at :1527", citing REQ-03(d). SC-03 case X would have caught it, but at build cost |
| F-04 | MED | Disclosure pairs unlabelled and no answerable ruling; reconciliation ticket ownerless | **Corrected**: `BRIEF.md:101-114` — labelled *recorded → digest*, run ids, the `INCOMPLETE`-is-not-a-verdict note, and the yes/no ruling with a named owner |
| F-05 | LOW | The grilling says "legacy-run behavior remains unchanged"; a legacy record such as FEAT-22's `INCOMPLETE` *will* now fire. The operator-approved contract governs and admits no legacy exemption | **No change.** The tension is resolved by the later, explicit contract and is now visible in the disclosure the operator rules on. Do not add an exemption without that ruling |
| F-06 | LOW | Nothing quantifies "no `feature.json` schema or cycle-accounting change" | **No change.** Enforced by construction — T-01 `files:` names three files, none of them the schema — and SC-06 catches behavioural drift. A criterion here would be true by construction (P-03) |
| F-07 | LOW | SC-02's clean tree holds a *lead-hosted, complete* run and asserts exit 0, so unrelated invariants (e.g. INV-6's `review_sha` pin for a `squad: validator` run) must not fire on it | **No change; advisory to the builder** — run E is `harness-product-lead`, keep its squad non-validator, or SC-02 reddens for a reason that is not INV-37 |
| F-08 | INFO | S4 ("skips the debug segment") appears in no plan text | **No change** — delivered by the task list containing no investigation task |

## 7. Gates run here (plan-time only; no build, lint or suite)

- `check-plan-routes.py <this plan>` → `0 violation(s)`, exit 0. The one `DEVIATION` line for T-01 is
  the DEC-174 carve-out D-06 predicts and accepts.
- `check-domain.sh --resolve` on all three lanes paths (G-02, every path, not a sample):
  `check-state.sh` → backend-dev, dev-ops; `test-check-state.py` → backend-dev, dev-ops, qa;
  `notes/redproof-BUG-440.md` → orchestrator. **All three `resolve:` fields verbatim-accurate.**
- Post-amend reload **as observed by this goal-check on 2026-09-06, before the plan panel was
  transcribed**: `approval: {status: pending}`, no `panel` key, 1 task, 6 decisions, T-01 keys
  unchanged, `verify:` intact. The panel record (cycle 1, 2 readers, 5 findings) and D-07 landed
  after this observation, so the `panel`-absent and 6-decision figures are superseded by design,
  not by drift; `approval:` is still `pending`.
- `git -C <TREE> status --porcelain` → `?? .harness/harness/features/BUG-440-digest-verdict-reconciliation/`
  and nothing else.

## Open questions

- **Q1 (blocking, operator):** the ruling in §5, now widened by panel finding
  PF-3f3c8cbd75c6538ac820075bfc6efe9b to three options — A merge-and-accept-red, B reconcile-first
  then merge, C send the plan back. `BRIEF.md` carries the current wording. Everything else in this
  plan is settled.
