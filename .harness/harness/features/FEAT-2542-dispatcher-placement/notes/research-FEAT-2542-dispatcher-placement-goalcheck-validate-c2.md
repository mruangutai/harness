# Goal-check — FEAT-2542 validate c2 (run r-20261126-3-validate-validator), delta-scoped

**BLUF: PASS.** The goal-check is at pin `2ec0916f8bf6b5d10607e36486ccbeb959ca4822` (base `2e7a2c77`),
scoped by `notes/answers-2026-11-26-validate-c0.md`.

- **SC-02** moves from partial to **met**. An ok claim with a null or empty feature is now refused at exit 2 as `unreadable`, before the persona check. It no longer falls back to the declared feature.
- **SC-04 evidence is met.** DEC-258's `unreadable` bullet now covers the null/empty shape. The index is unchanged and regenerates with no drift, and the anchors check passes.
- The SC-03 seam exits 0.
- SC-01 and SC-05 stand on their c1 evidence.
- The T-01.intent amendment was recorded through `record-amendments`, and its text matches the ruling's OQ-1 rules 1–4 and the (i′) clause.

There are two low, non-gating advisories (A-3 and A-4).

**Pin method.** Worktree HEAD is `a69f1367`, which is a child of the pin. `git diff --stat 2ec0916f a69f1367` touches only `feature.json`, and `git diff --quiet 2ec0916f -- .harness/harness/docs .claude/skills/harness/bin` exits 0. Each source read used `git show 2ec0916f:<path>`. Each run used the worktree, whose source is byte-equal to the pin.

## Re-graded

| SC / item | Verdict | Method | Evidence at the pin |
|---|---|---|---|
| SC-02 | **met** (was partial) | automated | **Source.** In `dispatch-guard.py#_lookup_placement`, `feature = found["feature"]` (l.854) is followed by `if not (isinstance(feature, str) and feature)`, which calls `_refuse_placement(agent_id, "unreadable", "…names no feature (%r): a malformed claim row.", _LOOKUP_REMEDIES["unreadable"])` (l.855). This runs after the `not found["ok"]` branch and before the persona check (l.860). It returns `feature`, so the postcondition is "non-empty str or exit 2". There is no new sentinel.<br>**Rows.** `tests/integration/test-dispatch-guard.py#case_42_claim_naming_no_feature_is_unreadable` covers `c42/{null,empty}-feature/{bound,exploit}`: lineage rows (exit 2, no claim, cause `cannot be placed (unreadable)` and `names no feature`, remedy `never delete it` and `find-run --agent-id Orch.Lead`, no unavailable). It also has `c42/omitted-feature/exploit` (PROCEED, giving `"legacy"`; by ruling this is a valid PASS, not a gap). The ordering row is `#case_43_placement_refuses_before_the_run_preflight`.<br>**Measured.** The suite at pin-equal source gave 426 of 426 and exit 0. Every `c42`/`c43` check printed PASS.<br>**Mutant (O-07).** The same suite against the c0-pin guard (`git show bc937a94:` copied into a mktemp bin through `DISPATCH_GUARD_BIN`) gave 412 of 426 and exit 1, with exactly 14 FAILs, all in c42. They include `c42/null-feature/bound:exit` and `:claim`, which means the c0 guard proceeded and claimed on a null feature. That is the closed fail-open. The receipt is `characterization-pin.md` "Pin run (fix round c1)" (`tested_sha: b27cbcc6`, 426/426, all four suites exit 0), and the c1 predicted and observed red sets are equal at 13 lines. |
| SC-04 | **met** | inspection | **DEC-258 `unreadable` bullet** (`DECISIONS.md` l.8706–8707 at the pin) now reads: "an ok claim that names no feature (null or empty) is a malformed record, refused as unreadable too". The `DECISIONS.md` diff `bc937a94..2ec0916f` changes only this bullet.<br>**Index.** `git diff --quiet bc937a94 2ec0916f -- DECISIONS-INDEX.md` gave exit 0, so the post-`::` ruling is unchanged (DEC-258 is the last entry, `@8697`). `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` gave exit 0. `check-decision-anchors.py` reported 25 anchors, 0 failed, exit 0.<br>**Body vs code.** DEC-258's "placed only by its own runtime claim" and "None of the five is ever the declared feature" are now true for the null and empty shapes, as the SC-02 mutant run above shows. See A-3 on the wording. |
| SC-03 (seam) | met (stands) | inspection | `git diff --quiet b27cbcc6 2ec0916f -- .claude/skills/harness/bin/dispatch-guard.py tests/integration/test-dispatch-guard.py` gave **exit 0** (measured). `2ec0916f` changes only `characterization-pin.md`. |
| SC-01 | met (stands) | automated | The fix diff does not touch `_mission_scope`, `_placed_distill_feature` or the c38/c40 rows. `inflight_registry.py` is byte-identical to base: `git diff --quiet 2e7a2c77 2ec0916f`, exit 0. |
| SC-05 | met (stands) | inspection | `plan.yaml` `source_issues: [2542, 2532]` is unchanged by the fix diff. |

## Decision dispositions touched by the fix

- **DEC-258 amendment (T-02 owns `DECISIONS.md`): met, with A-3.** The ruled clause has landed in substance, but not verbatim.
- **T-01.intent amendment: met.**
  - **How it was recorded.** `feature.json` judgement `{by: harness-orchestrator, kind: amendment, decision: T-01.intent, at 2026-11-26T17:42:29}` has the shape `plan_merge/amendments.py#_amendment_judgement` emits. It sits beside `notes/amend-T-01-intent-c1-digest.md` (`amendments: [{task: T-01, field: intent, was, now, reason}]`), which is the record-amendments route, not `amend`.
  - **(i′).** The intent says "after the ok check and before the persona check" and requires `isinstance(feature, str) and feature`. It names cause unreadable and the unreadable remedy, adds no separate sentinel, and lets an omitted feature (LEGACY_FEATURE) pass. ✓
  - **Rule 1.** The ruling allowed `Path(__file__).resolve().parent`; the amendment uses `os.path.join(os.path.dirname(os.path.realpath(__file__)), 'inflight_registry.py')`, computed once. This is semantically equal (realpath = resolve). The code has `_REGISTRY_SCRIPT`. ✓
  - **Rule 2.** Commands are built with `shlex.quote` for agent_id, feature and root (`_registry_command`). ✓
  - **Rule 3.** Each command is on its own line, indented four spaces, and the prose before it ends with ':'. ✓
  - **Rule 4.** The narrowed sentence matches the ruling verbatim, in the plan "last, always" line and in `_PLACEMENT_CONTRACT`. ✓
- **The eight `keep` rows stand.** The DECISIONS diff touched only DEC-258.

## Perspectives (only the two c1 exceptions are re-graded)

| Perspective | Verdict | Basis |
|---|---|---|
| operator | **pass** | SC-02 is met: no ok claim of any feature shape is silently rebound, as measured above. SC-05 stands. |
| code maintainer | **pass** | SC-04 is met. DEC-258's body is accurate for the null shape, and the index has no drift. |
| orchestrator, reader | pass (stand) | SC-01 and SC-03 are unchanged. |

## Advisories (non-gating, not re-raising ruled items)

- **A-3 · form · low · T-02.** The DEC-258 clause narrows the ruled wording. The ruling read "an ok claim whose feature is not a non-empty string (a malformed claim row)"; the landed text says "names no feature (null or empty)". The code also refuses non-str features, for example `"feature": 42`, because `isinstance` fails. The body under-describes the refusal class, but it makes no false claim: every shape it names is refused. Failure scenario: a maintainer reads "null or empty" as the whole class and relaxes the check to `feature is None or feature == ""`. A non-str feature would then reach `shlex.quote` in the persona-mismatch remedy. That is a TypeError, and the hook fails open (DEC-100).
- **A-4 · substance · low · T-01.** The check-before-persona ordering is inspected, not executed. No row combines a null feature with a persona mismatch. If the two checks were swapped, `_refuse_persona_mismatch` would call `shlex.quote(None)`, which raises TypeError, so the hook fails open with no row reddening. This is the same O-14 class as c1's A-1. The ruling made the order mandatory but asked for no row, so this is recorded and not escalated.

## Measured vs reasoned

- **Measured:** HEAD-vs-pin equality; the SC-03 seam (exit 0); `inflight_registry.py` byte-identity (exit 0); the index has no drift and is unchanged; anchors 25/0; the dispatch-guard suite gave 426/426 at pin-equal source; the c0-guard mutant gave 14 FAILs, all in c42; the amendment judgement shape.
- **Reasoned:** the amendment text against rules 1–4 and (i′); A-3 and A-4. I did not run `test-lead-start-*`, the census or `test-gen-decisions-index.py`; those belong to QA. Scratch for the mutant run was in a mktemp dir outside the repo.

## Principles applied

- harness-pm P-06 / O-07: I re-measured c1's failed premise directly by running the current suite against the c0 guard as a free mutant. That turned SC-02 into a measured close, not one read off the receipt.
- harness-pm P-16 / P-19: I graded DEC-258's amended prose against the code, and probed one step past the "null or empty" class (a non-str feature). That produced A-3.
- harness-pm O-14: I separated the inspected order from executed coverage. That produced A-4.
