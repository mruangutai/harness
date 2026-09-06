# Plan-panel review — scope reader — BUG-1304 — cycle 1

Bound to `plan:.../BUG-1304-worktree-relative-path-guard/plan.yaml` (DEC-207, no review_sha).

## BLUF

Traceability and DAG are clean; the vendored SC-06 fixture route is sound and matches existing
convention; the DEC-153/DEC-193 doctrine anchors are byte-accurate. But two fail-open gaps survive
the two prior Advisor rulings, both in the *same* module the plan already trusts:

1. **HIGH — corrupt registry file silently empties S.** `harness_boundary.claim_worktrees` fans out
   over every candidate root and calls `inflight_registry.live_claims(root, agent)`; `live_claims`
   is spec'd (T-01/T-02 intent) to return `[]` on an unparseable registry, inheriting
   `_parse`'s existing "corrupt → treat as empty" behaviour
   (`.claude/skills/harness/bin/inflight_registry.py:56-58`). This is not hypothetical: the module
   already carries a named, deliberate test for it, `case_8_corrupt_registry`
   (`tests/integration/test-inflight-registry.py:329-350`), which asserts exactly this fallback for
   the *claim/write* path. Nobody re-examined it for the *read/refusal* path BUG-1304 adds. If an
   agent's only live claim sits in a registry file that is corrupted (partial write, crash mid
   `harness_merge.locked_update`, external edit), `live_claims` for that root returns `[]`, that
   worktree contributes nothing to S, and if it was the agent's only claim S is empty — the agent
   reads fully unbound and every governed main-checkout write is **allowed**, silently (a stderr
   line from `_parse`, not a refusal). This reopens B-10 verbatim under a failure mode the codebase
   already names and tests elsewhere. Neither REQ-05 (which only names an unparsed *destination*
   `.git` pointer and claim ambiguity as refusal cases) nor T-01's four `live_claims` cases (only
   "missing registry file returns empty" is tested, never "corrupt/malformed JSON") cover it.

2. **HIGH — T-09's named "pruning sites" leave the single-flight check silently regressed if the
   fix lands at its only sensible choke point.** T-09's retention-rule intent names exactly four
   sites — `_expire_where`'s own delegation to `_expire` (`inflight_registry.py:234`, verified),
   `live_claim` (`:323-328`, verified), `live_children` (`:343-349`, verified), `reconcile` (`:519`,
   verified), `_all_live` (`:593`, verified) — all anchors check out exactly. But `_expire_where` has
   four *other* callers that reuse its returned `live` list for BOTH the file-content assignment
   (`data["claims"] = live`) AND their own answer computation, and T-09 never names them:
   `orphan_write` (`:297`), `claim_with_receipt` (`:375`), `attach_runtime_identity` (`:432`),
   `release` (`:472`). The only architecturally sensible place to implement "retain in file, exclude
   from returned answer" is inside the shared `_expire`/`_expire_where` primitive — but if that is
   where it lands, ALL eight callers inherit the new meaning of `live`, not just the four named ones.
   Concrete failure: `claim_with_receipt`'s single-flight admission
   (`any(_matches(c, agent=agent, feature=feature) for c in live)`, single-flight scoped to
   `harness-pm`) would then see a dispatch-expired-but-backstop-retained non-OMP claim as still
   "live," refusing a fresh `harness-pm` dispatch for the same feature for up to 86400s instead of
   the mandated 1200s — exactly the FEAT-37 stranding regression D-09 states must not happen
   ("Every dispatch-side ANSWER... keeps CLAIM_TTL_SECONDS at 1200s unchanged"). T-09's own verify
   (`case_bug1304_retention` plus the two guard suites) never exercises `claim_with_receipt`'s
   single-flight path, so this would ship silently. T-09 is STRIKEABLE; if struck this is moot, but
   as drafted it is a real gap the operator should see before deciding.

3. **low** — T-03/T-05 intent cites "`prior-validate-digest.py.fixture` and its three siblings";
   only two other `prior-*.fixture` files exist today (`prior-harness_yaml.py.fixture`,
   `prior-check-plan-routes.py.fixture`). Cosmetic — the convention itself (directory, spelling,
   hermetic-for-shallow-CI rationale) is correctly identified and does exist.

## Traceability result: none — no orphan REQs, no orphan SCs, no dangling `traces:`

REQ-01..REQ-07 each trace to at least one task (`T-01/02/03/04/05/06/09` for REQ-01/02/05/06,
`T-03..T-06` for REQ-03/04, `T-07` for REQ-07, `T-08` traces REQ-01 alone as its own strikeable
scope question, `T-10` traces REQ-03/04 as the broad-verification task). SC-01..SC-09 (post cycle-2
repair) each have a named producing task: SC-01 T-03c1/T-04; SC-02 T-05c1-2/T-06; SC-03 T-03c2/T-05c3;
SC-04 T-03c4-7/T-05c5-8; SC-05 T-03c9-10/T-05c10-11; SC-06 the `bug1304_pre_change_hook`/
`bug1304_pre_change_guard` mechanism added in the cycle-2 repair; SC-07 D-01/D-02/D-05/D-06/D-08 (all
present in `decisions:`) plus T-07's DECISIONS.md landing; SC-08 T-03c11/T-05c12; SC-09 T-03c13/T-05c15.
Every task's `traces:` names a REQ that exists in BRIEF.md.

## DAG result: acyclic, topologically consistent with sequential main-session-direct execution

`depends_on` forms a valid partial order (T-01→T-02→{T-03,T-05,T-08,T-09 in parallel}→T-04→T-06→
T-07→T-10, with T-08/T-09 depending only on T-02). The plan's own listed order (T-01..T-10) is itself
a valid topological sort, so straight-line main-session-direct execution never violates an edge.
T-03/T-05's `verify:` require `test $? -eq 1` (RED) at their own landing — correct, since the live
guard is byte-identical to what T-03/T-05 will freeze as "pre-change" at that moment, so only the
new "assert exit 2 against the live hook" half of each case fails, while the "assert exit 0 against
frozen pre-change" half trivially passes (same bytes). At T-04/T-06 the same suite goes GREEN because
the live hook is now patched while the frozen fixture is immutable — internally consistent, and it
is exactly the mechanism that makes SC-06 durable at signature time rather than a transient
red-to-green artifact. T-08/T-09's re-run of both guard suites holds regardless of interleaving with
T-03/T-05, since T-02's additions are purely additive to the library surface.

## Route asymmetry, doctrine anchors — confirmed accurate, no finding

`check-domain.sh:917,922` are exactly the two `feature_checkout_guard(...)` calls (allow/shared
verdict branches); `bash-write-guard.sh:794` is exactly the DEC-153 `continue`, `:841,:845` are
exactly the two `feature_checkout_guard(...)` calls sitting under the `:840`
`verdict["outcome"] in ("allow", "not_a_domain_question")` branch — confirming T-06's "IN-REPO
DESTINATIONS ONLY" clause is load-bearing exactly where the plan says (Write route returns early on
`not_a_domain_question` at check-domain.sh:902-908, before 917/922; Bash route's :840 catches both
outcomes at the same call site), and T-05 case 14 / SC-04 case 4 test it. DEC-193's first
divergence bullet is at DECISIONS.md:5338-5339 verbatim as the plan cites (the Advisor's own
5334-5335 citation was the stale one — the plan's cycle-2 repair already re-verified and corrected
it). DEC-153's carve-out clause text matches T-07's rewrite target exactly. `DEC-215` is confirmed
the current highest entry in `DECISIONS-INDEX.md`, matching T-07's citation. T-07's `verify:` grep
targets (`CLAIM-SET MEMBERSHIP`, `the assigned worktree`, `OMP_UNVERIFIED_TTL_SECONDS`,
`inflight_registry.py:30-35`) do not currently appear anywhere in DECISIONS.md, so the presence
checks are not vacuously satisfiable by pre-existing text.

## SC-06 vendored-fixture judgment: sound, matches established convention

pm's stated reason for rejecting `CHECK_DOMAIN_BIN`/`BASH_WRITE_GUARD_BIN` (env var resolves once
at module import, so it cannot select two binaries within one test run) is accurate as a
description of *that* mechanism, but the chosen alternative is not novel: `isolated_bin()` +
byte-copy-with-overlay + an explicit `hook=`/`guard=` parameter on the fire helper is the exact
pattern already used repeatedly in both files for "red case" proofs
(`_bug895_mutant_hook`/`_bug895_red_case`, `_feat50_mutant_between`/`_feat50_binding_red_case`,
`_feat50_bash_mutant`/`_feat50_bash_red_case`), and `test-validate-digest.py`'s
`check_prior_validator` (`:2477-2496`) is the direct precedent for vendoring an entire prior-revision
file inert specifically because CI's shallow clone cannot `git show` a historical sha. Frozen bytes
cannot "rot into false-green" for SC-06's actual claim (a historical fact about the pre-change
guard, immutable regardless of later edits); the only forward risk is the same one every existing
mutant/red-case fixture in this suite already carries (a future `isolated_bin`/bin-layout change
breaking an old byte copy's ability to resolve its own libraries), which is pre-existing risk, not
new risk this plan introduces.

## Task completeness

Every reviewed task's `intent` is an executable instruction, not a summary — function signatures,
exact case enumerations, and line anchors are spelled out to the point a main-session executor does
not need to re-derive Advisor reasoning, with two exceptions already covered above: T-09's retention
rule states the desired *outcome* precisely but is silent on *which* of the eight `_expire_where`
callers must be touched to achieve it without side effects (finding 2), and neither T-01 nor T-02
name the corrupt-registry case at all (finding 1).
