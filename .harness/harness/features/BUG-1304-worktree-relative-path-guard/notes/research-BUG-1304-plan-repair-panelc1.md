# Plan repair — BUG-1304 — panel cycle 1 — five findings

## BLUF

All five panel findings are repaired in the plan and the brief; `panel` is recorded with both
readers, the advisor's non-contract `FINDINGS` token, and five findings all `resolved`.
`approval.status` stays `pending`, `status: plan`. `check-plan-routes.py` exits 0 (10 DEC-174
deviation lines, 0 violations). The plan now carries **11 SCs, 10 decisions, 10 tasks** — nothing
renumbered.

## L-02 — the seam (the important one)

Advisor **RULING B** is the only answer used; **no third seam answer was invented.** T-09's intent
now states the seam before the sites: inside every pruning function the `_expire_where` list feeds
TWO uses — the file-content assignment `data["claims"] = live` and the caller's own answer — and
retention changes only what is WRITTEN. The suggested shape is a `(answer_live, retained)` pair, so
`retained` reaches the file and `answer_live` reaches every answer.

All six callers named, each with its duty (measured myself in the worktree copy,
`inflight_registry.py`): `orphan_write:297`, `live_claim:323-328`, `live_children:343-349`,
`claim_with_receipt:375`, `attach_runtime_identity:432`, `release:472`, plus `reconcile:519` and
`_all_live:593`. `orphan_write` and `release` are called out as previously unnamed and as deleting
today. `claim_with_receipt` is called out as the most dangerous site: admission must keep reading
the 1200s list or FEAT-37 stranding returns at 86400s.

Assertions: `case_bug1304_retention` now covers a previously omitted site (`orphan_write` or
`release`) and asserts each call's own return value is unchanged;
`case_bug1304_retention_admission` asserts single-flight ADMISSION still admits at 1200s with a
retained claim present. SC-11 binds both halves and is explicitly struck with T-09.

## L-01 — the corrupt registry

REQ-05 gains a third half: an existing-but-unreadable registry leaves the claim set INCOMPLETE and
is refused, never read as "no claims here". `_parse`'s treat-as-empty fallback
(`inflight_registry.py:56-65`) and its write-path pin `case_8_corrupt_registry`
(`tests/integration/test-inflight-registry.py:329`) are cited and left untouched. New
`UnreadableRegistry` is raised by `live_claims`, propagated by `claim_worktrees`, and the refusal
message is built ONCE in the seam (T-02); T-04/T-06 only catch and exit 2. D-10 flags it as the
Advisor's REQ-05 pattern **extended by pm, ratified at signature**.

**One deliberate departure from the dispatch's fixture wording, and why.** The dispatch's shape —
"a live claim in a linked worktree PLUS a corrupt registry among the roots" — is refused by the
ordinary claim-set rule anyway, so it discriminates nothing. SC-10 instead pins the agent whose
ONLY claim sits in the corrupt file (S would otherwise be empty → allowed, which is the measured
harm) and adds a **paired well-formed control** that must exit 0. That is the version that can fail.

## L-03 — the verify audit

`DECISIONS.md:5338` spells the clause with a capital `T`; T-07's negation never fired. Now
`! grep -qi "Bash route keeps DEC-153's blanket allow"`, proven red against the current file.

**Audited 10 verifies, changed 5** (T-03, T-05, T-07, T-08, T-09). Two more defects of the same
class found beyond L-03:

- **T-08**: `grep -q 'worktree_for_feature'` already matches `dispatch-guard.sh:174`. Replaced by
  `grep -q 'worktree_for_feature(owner_root, flow)'` plus `! grep -q 'os.path.basename(wt) == flow'`
  — both proven red today.
- **T-09**: `grep -q 'case_bug1304_retention()'` is satisfied by the `def` line; the file wires
  cases as bare names in `CASES` (`test-inflight-registry.py:1073-1094`). Now `…retention,`.
- T-03/T-05's `grep -c 'bug1304_pre_change_hook('` floor was replaced by a count of
  `bug1304_assert_pre_change_allows(` call sites, which is the thing actually being asserted.

Clean: T-01, T-02, T-04, T-06, T-10. `fails += run_bug1304_claim_set()` matches the suites' real
wiring (`test-check-domain.py:4419-4437`); T-07's four presence greps match 0 lines today.

## L-04 — fail-open satisfies the pre-change proof

SC-06 and SC-09 now require every pre-change call to prove the guard RAN: **no** `enforcement OFF`,
`was not enforced`, `passing through` on stderr, **and** a positive control refused with exit 2 at
the same frozen guard. T-03 and T-05 specify one helper, `bug1304_assert_pre_change_allows`, that
every refusal case must call. **The Bash route's fail-opens are silent** (`bash-write-guard.sh:78-80`
payload, `:267-269` manifest) — a marker check cannot see them, so the positive control is named
there as the load-bearing half (T-05 reuses the run-artifact refusal). Write route markers measured
at `check-domain.sh:1864-1869` and `:383-386`.

## L-05 — the asymmetric strike

T-09's opening and D-09's strike paragraph both now say the strike **overrides Advisor rulings A and
B**, is not symmetric with T-08's (T-02 already makes T-08 free), and leaves B-10 reachable on the
routine suspend path (`dispatch-guard.sh:197`, `validate-digest.py:1755-1760`). OC-1 asks where the
closure lands, not whether the hole may stay open. SC-11 supplies the missing criterion.

## Open questions

- **Q1 (non-blocking, operator):** D-10's refusal is fail-closed for the persona while any scanned
  registry file is unreadable. Strike or narrow it at signature if that trade is unwanted.
- **Q2 (non-blocking, harness):** `plan-merge.py set-panel` validates only `last_run/cycle/
  readers/findings` types. Finding ids are `PF-<hash>` from `panel_findings.py`, so the panel's
  `L-NN` labels are recorded as a sibling `label:` field, not as `id:`.
