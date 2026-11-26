# Goal-check — FEAT-2542 validate c1 (run r-20261126-2-validate-validator)

**BLUF: PASS.** At pin `bc937a947fc8716c6cf1b171f05ad24d5e019747` (base `2e7a2c77`), all four
declared perspectives are discharged. The diff's own records support SC-03, SC-04 and SC-05, which
are `met`. SC-01 and SC-02 are covered on their test rows, but their verdicts wait on QA's runner
receipts at the pin. All eight `keep` decision dispositions are `met`. There are two advisory
notes, both low, and neither is blocking. Every read used `git show bc937a94:<path>`.

## Perspectives

| Perspective | Verdict | SCs | Evidence at the pin |
|---|---|---|---|
| operator | pass | SC-02, SC-05 | `dispatch-guard.py#_lookup_placement` / `#_refuse_placement` / `#_dispatcher_placement` exit 2 on every non-ok `find_run_claim` cause and on persona mismatch; the module sequence is `_direct_orchestration_refusal(); _dispatcher_placement(); _start_preflight(); _distill_preflight()`, ahead of the claim `try`. Rows: `c38/fail-*` (all 7 states, product lead), `c39/eng/<8 states>/{bound,exploit}`, `c39/validator/{ok,not-found}/bound`, `c40/*`, `c41/{main,orchestrator-id,orchestrator-no-id,lead-no-id}/{unreadable-owner,escaped-oserror}`. `source_issues: [2542, 2532]`. Closure is observable only at ship (signed gap). |
| orchestrator | pass | SC-01 | `_mission_scope` adds `and _placed_distill_feature() is None` to `plan_route`. `c38/distill/distill` (labelled "the FEAT-2489 payload") was observed red at base on exit/claim/receipt and is green at `tested_sha`. No relabel works: `c38/distill/plan` and `c38/distill-pending/plan` are refused, and the plan, norun and no-id rows keep their outcomes. `c38/distill/run-reads` asserts exactly one `registered_destination` read. |
| reader | pass | SC-03 | The research note at the pin carries the Contract table (planned), the condensed class tables with branch witness, planned outcome and delta, and Appendix A (98 measured rows at `2e7a2c77`). It is unchanged since the signature commit `8e05046b`. `notes/characterization-pin.md` has `base_sha`, `dec_number: DEC-258`, 97 `predicted_red` = 97 `observed_red` (set-equal, **measured**), the base run, and one Pin run (`tested_sha: d23f3728…`, `pin_run_exit: 0`, 397 of 397). |
| code maintainer | pass | SC-04 | `DECISIONS.md` `## DEC-258` (the only one, line 8697) records every SC-04 element. Its code-checkable claims match `dispatch-guard.py` (table below). Its lineage to DEC-100, DEC-218, DEC-250 and DEC-253 is stated, and it amends none of them. The index row has a hand-written ruling, and regeneration shows no drift (**measured**). |

## SC status

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met on rows, pending QA receipt | automated | `tests/integration/test-dispatch-guard.py#case_38_product_reader_route_keys_on_trusted_placement`, `#_c38_run_reads`, `#case_40_…`. Fail-first: `characterization-pin.md` `observed_red: c38/distill/distill:{exit,claim,receipt}`. LEAVE: `test-lead-start-return.py` and `inflight_registry.py` are byte-identical to base (**measured**, `git diff --quiet` exit 0). The final verdict rests on QA's runner receipt at the pin. |
| SC-02 | met on rows, pending QA receipt | automated | `#case_39_governed_lead_placement_is_bind_or_refuse`, `#case_41_main_and_non_lead_keep_prior_outcomes` (the lead-no-id signpost comment is present: SQ-2 and constraint 7). Fault injection goes through `_f2542_bin` copies (SQ-3). Only the typed tuple `except (reg.UnreadableRegistry, OSError)` is used, with no broad catch (constraint 4). `_dispatcher_feature` is deleted and has no straggler in `.claude` or `tests` (`git grep` at the pin returned nothing; constraint 8). |
| SC-03 | met | inspection | Seam `git diff --quiet d23f3728… bc937a94 -- dispatch-guard.py test-dispatch-guard.py` gave **exit 0 (measured)**. `d23f3728` is an ancestor of the pin, and the guard differs from base at it. Files changed after `tested_sha` are DECISIONS.md, the index, feature.json, plan.yaml and notes only. After T-02's last content commit `0d910f03`, only plan.yaml changed (constraint 9). |
| SC-04 | met | inspection | `DECISIONS.md` DEC-258 at line 8697. `gen-decisions-index.py --stdout` against a `git archive` of the pin gave diff exit 0. `check-decision-anchors.py` reported 25 anchors and 0 failed; I ran it in the worktree, whose `.harness/harness/docs` and `bin` are byte-equal to the pin. I did not run `test-gen-decisions-index.py`; it is QA's. |
| SC-05 | met | inspection | `plan.yaml` `source_issues: [2542, 2532]`, which sorts to `[2532, 2542]`. |

## DEC-258 claims vs code (SC-04 accuracy)

- Placement comes only from `find_run_claim`, persona-matched: `_lookup_placement` checks `found["claim"].get("agent") != agent`. ✓
- It runs once, after the direct-orchestration refusal and before the start and distill preflights and the claim: the `_placement` sentinel memo and the module order confirm it. ✓ (See A-2 for wording.)
- Five causes, each naming the cause token, the runtime id, a cause-specific remedy and `find-run`. `find_run_claim` can return only the causes `unreadable`, `not-found` and `ambiguous` (`inflight_registry.py#find_run_claim`), so `_LOOKUP_REMEDIES` has no missing key. `_registry_error_remedy` has a named-file branch and a no-file branch. ✓
- None of the five yields the declared feature or `emit_unavailable`: `_refuse` calls `sys.exit(2)`. The unreadable registry is left as found because the denial comes before the claim step and `find_run_claim` is read-only. ✓
- Main, non-lead and no-id dispatches are unchanged: `governed = agent in LEADS and non-empty id`, and the `_bound_distill_feature` else-branch uses `declared`. ✓
- The id-less nested Task is refused by the host: DEC-218's text ("refuses every governed Write, Edit, Bash, or nested Task when a Harness persona lacks … its child id") supports it. ✓
- Rule 2 is matched via `registered_destination` (`_registered_run_id`) and `DISTILL_RUN_RE` (`_is_distill_run_id`). One memoized `_placed_distill_feature` is consumed by both `_mission_scope` and `_bound_distill_feature`. The distill preflight and its `_require_*` helpers are untouched in the diff. ✓
- "The hook lets a governed lead dispatch only from a ready, claimed run": this cannot be checked in this file. The grilling's section e verified it at `harness-hooks.ts` (not re-read here).

## Decision dispositions (all `keep`)

The DECISIONS.md diff base..pin is **74 insertions and 0 deletions**, and the base text is a
byte-prefix of the pin text (**measured**). Each clause is present verbatim in its own section at
the pin:

| DEC | Verdict | Clause at pin |
|---|---|---|
| DEC-100 | met | line 1411 |
| DEC-174 | met | line 4521 |
| DEC-204 | met | line 6587 |
| DEC-214 | met | line 7091 |
| DEC-218 | met | line 7224 |
| DEC-228 | met | line 7649 |
| DEC-250 | met | line 8208 |
| DEC-253 | met | line 8363 |

Nothing is `not_met` or `partial`, so no remediation is routed to T-02.

## Ledgered amendment (T-02.intent, 32→30 words)

The amendment is recorded as a `feature.json` judgement (`kind: amendment`, `T-02.intent`, commit
`0d910f03`). It changed only the post-`::` prose of the index row: "named" and "product-lead" were
dropped. The amended ruling still carries both rules:

- Rule 1: bind to the own runtime claim, or refuse at exit 2 in five states.
- Rule 2: the scope-reader rule yields only to a placed `distill-*` run.

The "scope-reader rule" is singular in the record (DEC-228's `scope` reader is `harness-code-reviewer`
under the product lead), and the denial naming lives in the DEC body. **It carries the decision.**

## Advisory notes (non-blocking)

- **A-1 · kind substance · low · T-01.** Lead × cause coverage is partly executed and partly
  inferred:
  - Executed: product lead (7 failure states plus ok) and eng lead (all 8).
  - Inferred: validator lead in 5 failure states (persona-mismatch, ambiguous, unreadable ×2,
    escaped ×2). These pass through the shared, `agent`-independent `_lookup_placement`; only `ok`
    and `not-found` are executed.

  Failure scenario: a later edit special-cases `harness-validator-lead` inside `_lookup_placement`,
  for example by passing its ambiguous answer through. No row reddens. This is the signed T-01
  (c) design. It is recorded per O-14 and not re-raised.
- **A-2 · kind form · low · T-02.** DEC-258 says `_dispatcher_placement` runs "before any other
  preflight". That is true of the named preflights (`_start_preflight`, `_distill_preflight` and
  their callees). Module-level checks still precede it: the `name:` refusal, the
  feature/repository lines, the T-09 shell-less tree-root block and the runtime/pid check.

  Failure scenario: a shell-less child dispatched with no tree root by an unplaceable lead gets
  the T-09 refusal, not the lineage denial. A maintainer reading "before any other preflight" could
  expect the opposite. This does not fail SC-04, because the file's own vocabulary reserves
  "preflight" for the named functions and the plan's signed text uses the same words.

## Measured vs reasoned

- **Measured:**
  - predicted/observed set equality;
  - the seam diff, ancestry, and LEAVE byte-identity;
  - index regeneration with no drift;
  - the anchors check;
  - the DEC-258 heading count (1);
  - keep-clause presence and the append-only DECISIONS diff;
  - `source_issues`;
  - the `_dispatcher_feature` straggler grep.
- **Reasoned (code reading):** the claim-vs-code table and perspective coverage.
- **Not run:** the four test suites and `test-gen-decisions-index.py`. These are QA's; SC-01 and
  SC-02 rest on its receipts. My tools refused nothing I needed.

## Principles applied

- harness-pm P-16 (grade the signed prose against behaviour): I checked DEC-258 claim by claim
  against `dispatch-guard.py`, which produced A-2.
- harness-pm O-14 (separate inspected generalization from executed coverage): this produced A-1.
