# Plan fix cycle 4 — BUG-1305 — every cycle-3 finding closed

**All ten findings in `notes/research-BUG-1305-goalcheck-plan-c3.md` are closed in the artifacts; one
half of F-05 is declined with evidence.** The three high findings are closed exactly as the
orchestrator ruled. `check-plan-routes.py` exits 0 (13 DEVIATION/OK lines, all the expected DEC-174
shape); `check-instruction-paths.py` exits 0 over 62 files. `approval.status` is `pending`, top-level
`status: plan`, no `panel:` key, both retired tasks still `abandoned` in place.

**Every anchor written into a task was verified at source in THIS run**, reading the worktree copies
of `check-domain.sh` and `check-state.sh` at HEAD `c369fb1f` with no tracked modification, so the
worktree text IS the pinned text: `if absolute_path is not None:` `:1508`; prior read and
`prior_unreadable` refusal `:1509-1529` (`if prior_unreadable:` `:1526`, `return out` `:1529`);
`if prior_state:` ladder `:1530`; unparseable-prior refusal head `:1542` (branch `:1539-1545`);
Issue-1124 compare `:1567-1574`; shape phase `:1581-1582`; `ALLOWED` `:1450-1453`; Edit
reconstruction `:1905-1923`; POST `elif target:` `:1930-1950`; `check-state.sh` `CHECKPOINT_KEYS`
`:1390-1405` and the run-directory loop `:1426`.

## Disposition by finding

| id | disposition | where |
|---|---|---|
| F-01 | closed — ONE insertion point: the witness compare goes inside `if absolute_path is not None:`, after the `prior_unreadable` refusal, before the ladder; SKIPPED when the prior parses to a mapping with a non-empty `run_uid`; prior parsed ONCE above the check and consumed by the ladder so every existing message/exit is byte-identical | plan T-02 §3, T-09 PRECEDENCE, D-01, BRIEF REQ-01 two-refusals bullets, SC-01(a)(f) |
| F-02 | closed — `conflict()`'s `run_id` row carries the recorded-non-None guard; two cases, one naming `run_id` explicitly and built through `record_seed` so it is the born-null witness the write-once path really produces, one on `squad` | plan T-01 |
| F-03 | closed — "truncated" struck from every no-refusal promise; the truncated case is disclosed at the signature as pre-existing #1106 gap-(b) fail-closed behaviour repaired by a human outside the guards, out of scope BY NATURE | BRIEF REQ-01 (new bullet), plan T-02, T-09 |
| F-04 | closed — D-01 now says the witness has TWO consumers (seed fields = PRE denial input, `run_uid` = detection input) and that only the recorded SESSION identity is a denial input nowhere | plan D-01 |
| F-05 | closed for SC-09 — the criterion now names the real limit (a witness beside the checkpoint) and all three reported paths, pinned five ways incl. unreadable-witness and seed-disagreement. **DECLINED half:** D-13's summary sentence keeps the narrow `run_uid` phrasing; the dispatch lists D-13 as DO-NOT-TOUCH, so SC-09 reconciles it in prose instead (Q1) | BRIEF SC-09 |
| F-06 | closed — FAILS-if now names (a) with its own failure condition, plus (f) | BRIEF SC-01 |
| F-07 | closed by the stronger route, priced below — SC-10 states plainly that the direct `--post` invocation IS its evidence and names what that leaves unmeasured; new **SC-12** and new **T-12** observe ONE real end-to-end mint | BRIEF SC-10/SC-12, plan T-12 |
| F-08 | closed — the first-write window is named as the residual instance of the modal collision, in the operator-facing bullet and in the builder's comment instruction | BRIEF REQ-01 legacy bullet, plan T-02 |
| F-09 | closed — `traces: []` on T-04 and T-10, each body saying coverage moved and where; `check-plan-routes.py` accepts it (exit 0) and `traces` is not in `REQUIRED_TASK_FIELDS` | plan T-04, T-10 |
| F-10 | closed — REQ-01 now says the forgery case IS an accepted residual and marks the earlier claim as corrected rather than dropped | BRIEF REQ-01 residual bullet |
| Q1 (c3) | closed by the F-01 ruling: before the ladder, deferring when the prior carries a `run_uid` | — |
| Q2 (c3) | closed by the F-03 ruling: narrow REQ-01 to zeroed/absent | — |

**Price of the F-07 choice:** one extra `main-session-direct` task (T-12), one live Write tool call
and a cleanup, against leaving the load-bearing assumption of the whole feature — that the host
delivers PostToolUse — asserted by nothing. The direct-invocation disclosure alone would have been
honest and unmeasured; the measurement is one tool call.

**Precedence consequence, checked across the whole case list before writing it:** a directory holding
a witness AND a prior that parses with NO `run_uid` now answers with the Issue-1305 witness wording
rather than Issue-1124. No case in T-02, T-09 or SC-01 asserted otherwise (T-02's Issue-1124 case is
the NO-witness directory; T-09's two legacy cases both exit 0). It is now pinned positively by a new
T-02 case and by SC-01(f).

## The four properties, walked against the plan as it now stands

1. **A resumed owner is never refused.** Prior parses with U1 → witness compare deferred (T-02 §3) →
   ladder: run_id equal, `uid_conflict` equal → exit 0. Proven: plan T-09 case "THE RESUMED OWNER"
   (session S2), BRIEF SC-01(e), T-08 direction-two pair 2.
2. **An owner recovering a zeroed or absent checkpoint is never refused.** Prior empty → no
   `run_uid` → witness compare runs and its seed fields AGREE with the owner's own witness → None;
   ladder not entered. The born-null witness cannot refuse it either (F-02 guard). Proven: plan T-02
   case "THE RECOVERING OWNER, both forms", T-09 same two cases, BRIEF SC-01(d), T-08 pair 2.
3. **A foreign run colliding on a slug IS refused, Write and Edit.** Prior present with U1 → ladder →
   `uid_conflict` missing-value row. Prior absent/zero-byte/unparseable → witness compare. Proven:
   plan T-09 cases MODAL COLLISION Write and Edit (BRIEF SC-01(b)(c)); plan T-02 cases 1, 2 and 3
   (BRIEF SC-01(a)); Edit reached because `check-domain.sh:1905-1923` reconstructs `RE_STATE_YAML`.
4. **No historical directory, sibling worktree or control-plane root can redden the new invariant.**
   Every reported path in T-03 requires a witness; witness-absent appends nothing, permanently. On
   PRE, `read_marker` returns None for a witness-less directory so `conflict()` returns None, and
   `uid_conflict`'s legacy row keeps a `run_uid`-less prior quiet. Proven: plan T-03 fixture rows Z
   and L plus the exit-0 tree assertion, BRIEF SC-09 (five pins, incl. the recorded run over this
   machine's control-plane root), T-08 direction-two pair 4.

## REQ → task → SC

- **Mode A.** REQ-01 → T-01, T-02, T-09, T-11, T-12 → SC-01, SC-10, SC-11, SC-12. REQ-02 → T-01,
  T-03 → SC-02, SC-09. REQ-03 → T-03 → SC-03.
- **Mode B.** REQ-04 → T-05 → SC-04. REQ-05 → T-06 → SC-05. REQ-06 → T-06 → SC-06.
- **Doctrine.** REQ-08 → T-07 → SC-08. **Both modes.** REQ-07 → T-02, T-05, T-06, T-08, T-09 → SC-07.
- Live tasks, all station `ready`: T-01, T-02, T-03, T-05, T-06, T-07, T-08, T-09, T-11, T-12.
  Retired in place, station `abandoned`, `traces: []`: T-04, T-10.

## Writes

`plan-merge.py amend` (compare-and-swap, no failure): `D-01.choice`, `T-01.intent`, `T-02.intent`,
`T-09.intent`, `T-04.traces` and `T-10.traces` (`--yaml-value`), `T-04.intent`, `T-10.intent`.
`plan-merge.py apply`: added `T-12`. `BRIEF.md` edited directly (pm's own file; `## Approval`
untouched).

## Open questions

- **Q1 (non-blocking):** D-13's `choice` still reads "judges a run directory only when its witness AND
  its checkpoint both carry a run_uid", which is narrower than the three paths T-03 reports. The
  dispatch lists D-13 as DO-NOT-TOUCH, so it is unamended; SC-09 and T-03's body carry the correct
  set. A one-clause D-13 amendment would remove the last inconsistency.
- **Q2 (non-blocking):** SC-12 and T-12 are new scope added in this pass to close F-07. If the
  operator prefers the cheaper disclosure-only route, strike both and SC-10's unmeasured-delivery
  paragraph stands alone.

## Send-back 1 — arity sweep

**SC-01's opening count was false after this pass's own additions and is corrected; a full sweep of
every counting claim in `BRIEF.md` and `plan.yaml` found five more falsified claims, all corrected,
and thirteen already correct. `check-plan-routes.py` exit 0 (0 violations, 1 plan);
`check-instruction-paths.py` exit 0 (62 files, 0 violations). No finding disposition, no mechanism,
no ruling and no case list moved.**

### Corrected — the number was re-derived from the thing it counts

| Claim | Location | Was | Now, and how re-derived |
|---|---|---|---|
| SC-01 opening arity | `BRIEF.md` SC-01 first sentence | "Six lettered cases and seven tests, because (d) is two" | Total dropped, multi-case letters named: "(d) is two cases and (f) is two". Re-derived from the enumeration (a)–(f) and the FAILS-if, which gates "either half of (f)". Survives a letter (g) |
| ordering-case pointer | `plan.yaml` T-02 case list, deferral bullet | "that case and the two above are the three" | "that case, the UNPARSEABLE-prior case and the PRECEDENCE PINNED case above" — the positional "two above" pointed at the no-witness and unreadable-witness bullets after this pass inserted the PRECEDENCE PINNED case. Named, not positioned |
| branches added | `plan.yaml` T-08 direction two | "adds three refusing or reporting branches" | "EVERY refusing or reporting branch … the pairs are the four below". Re-derived from the bullets (4) and from the branch set (T-02 seed-field, T-09 identity, T-03 invariant, T-05 fail-closed = 4); "three" agreed with neither |
| red-proof refusal cases | `plan.yaml` T-09 RED PROOF | "The two refusal cases exit 0 on that tree" | "The THREE refusal cases this branch adds — both MODAL COLLISION routes and the different-run_uid Write". Re-derived from T-09's own case list; the PRECEDENCE case exits 2 on both trees by the Issue 1124 branch and is now placed rather than left unaccounted |
| notes not written | `plan.yaml` T-10 last line | "The two notes this task would have produced" | "The seeding note … the one note in its `files:` list". Re-derived from T-10's `files:` (one path) and its `verify:` (asserts that one). No second note is named anywhere in the plan or the c1–c3 notes |
| minting evidence scope | `plan.yaml` T-12 WHY IT EXISTS | "Every other criterion in this plan invokes check-domain.sh --post directly" | "The only other criterion that evidences minting — SC-10 —". Re-derived from the SC list: SC-02/04/05/07/08/09/11 invoke no `--post` |

### Checked and left alone — each re-derived, each already true

| Claim | Location | Derivation |
|---|---|---|
| "four named pairs" / "four permitted-write cases" | `BRIEF.md` SC-07 | T-08 lists exactly 4 pair bullets |
| "Pinned five ways" / "any of the four tests" | `BRIEF.md` SC-09 | T-03 supplies all 4 (Z, L, W, X) + the control-plane run recorded in `regression-delta` = 5 |
| "the three paths above" | `BRIEF.md` SC-09 | T-03 reports exactly 3: unreadable witness, seed-field disagreement, run_uid disagreement |
| "A test asserts all four" / "four assertions" | `BRIEF.md` SC-10, `plan.yaml` T-02 | T-02's case family lists 4: mint+witness, second POST unchanged, payload-carrying byte-identical, non-parsing untouched |
| "(d) … two cases" | `BRIEF.md` SC-01(d) | zero-byte prior and absent prior |
| "bounded three ways" | `BRIEF.md` REQ-01 | message, re-injection, seed doctrine |
| "Two refusals" / "exactly two compares" | `BRIEF.md` REQ-01, `plan.yaml` T-09 | witness seed-field compare + prior-checkpoint uid compare |
| "all four cases" | `plan.yaml` T-06 | 4 case bullets; first and fourth green pre-change, as the text says |
| "exactly these nine names" / "seven keys" | `plan.yaml` T-01 | 9 public names listed; `record_seed` writes run_id, feature, squad, host, identity, run_uid, created_at |
| "TWO distinct code paths" | `plan.yaml` T-09 fail-open row b | FileNotFoundError branch + zero-byte read at `check-domain.sh:1508-1518` |
| REQ→task coverage sentences | `plan.yaml` T-04, T-10 | Loaded the plan: REQ-01 → T-01, T-02, T-09, T-11, T-12 (all live); REQ-02 → T-01, T-03; REQ-03 → T-03 |
| "the existing two clauses" | `plan.yaml` T-07 | `.claude/skills/harness/SKILL.md:272-274` carries exactly 2: squad suffix keys the glob; never embed the feature id |
| "Keep the existing two sentences" | `plan.yaml` T-06 | the quoted denial message is 2 sentences |

No claim states how many tasks or criteria the plan carries, so T-12 and SC-12 falsified no total.

### Noted, not acted on (out of this send-back's scope)

T-05's new fail-closed refusal in `validate-digest.py` is a refusing branch that T-08's four pairs
do not name; its permitted side (no root resolves → exit 0) is pinned inside T-05's own case list.
The T-08 sentence now quantifies over every added branch, so the omission is visible rather than
contradicted. Raising it as a finding is the panel's call, not this pass's.

### Writes

`plan-merge.py amend` (compare-and-swap with `--expect-sha256`, all exit 0, no CAS failure):
`T-02.intent`, `T-08.intent`, `T-09.intent`, `T-10.intent`, `T-12.intent`. `BRIEF.md` edited
directly (pm's own file; `## Approval` untouched). `git status --porcelain` reports one line,
`?? .harness/harness/features/BUG-1305-run-state-clobber/` — no tracked file modified.
