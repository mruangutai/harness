# Plan-contract review — FEAT-11 GraphQL field resolve

review_sha 835b2976abd649fb814385d7d9b5b19fb7e1431a == `git rev-parse HEAD`. `git diff --stat` over
factory_gh.py / test-factory-gh.py / test-factory-integration.py between the pinned SHA and HEAD is
empty — all three SHAs in play (review_sha, plan.yaml:10 resolved_at, HEAD) agree.
`git log --grep '\[harness:human\]' 835b2976..HEAD` over the three surfaces plus the feature dir
returns nothing — no human-edit drift since the pin.

## A. Anchor audit — clean

Every anchor listed in the dispatch resolves to what the plan claims, checked by direct read at HEAD:
factory_gh.py `:41-44,48-63,105-114,196-198,206-210,251-256,257-262,263-271`; test-factory-gh.py
`:78-87,255-267,269-279,282-306,309-328,446-463,571-573,594-597`; test-factory-integration.py
`:178-188,190-191,196-199,200-202,205,227`; factory_decompose.py `:255-268,444-458`; run-unit-tests.sh
`:17,18,42-55`. No class of drift found — no off-by-N, no stale target.

**D-04 byte-identity confirmed.** factory_gh.py:209 and :255 are both exactly
`f"field-list for {owner} project {number} does not offer it"` — identical text, different
indentation only. D-04's freeze claim holds.

## B. Fail-open surface of intent step 3 (plan.yaml:171-213) — both notes, not gating

- **B-1 (unmeasured hypothesis).** No measured row nor Part B fixture covers a top-level
  `{"data": null, ...}` envelope, only `data.repositoryOwner: null`. If reachable, walking
  `env["data"]["repositoryOwner"]` raises `TypeError`, not `GhError`, which `factory_decompose.py`'s
  `run()` doesn't catch (`expected=(FleetError, GhError)`, test-factory-decompose.py:270). But branch
  (a) already treats `repositoryOwner` as nullable-not-erroring, which is evidence it sits at the
  first nullable ancestor in the schema — so a deeper error would likely null out `repositoryOwner`
  (matching branch a) or `projectV2` (branch c), not `data` itself. I have not measured this and
  cannot confirm the shape is reachable for this query. Forwarding as an open question, not a finding.
- **B-2 (unmeasured hypothesis).** Branch (d) tests only `field is None OR field == {}`. A `field`
  dict present, non-empty, but missing `options` (absent key, or explicit `null`) isn't explicitly
  ruled out by the pseudocode (`field.get("options", [])`'s default only fires on an absent key).
  Given the schema likely returns `id`/`options` together or not at all under the same inline
  fragment, this is likely schema-impossible, same disposition as B-1.
- **B-3 — closed.** Step 6 (plan.yaml:223-233) confirmed: item-edit runs only in the success branch;
  every raise propagates with zero item-edit calls, no fallback.

## C. SC-08's evidence base — BRIEF misattributes it, but REQ-05 is not actually unguarded (low)

`patch_gh` in test-factory-decompose.py:128-132, test-factory-claim.py:127-131 and
test-factory-land.py (`PATCHED_GH` at :123) replace `factory_gh.project_field_options`/
`project_field_set` with `Recorder` stand-ins at the module-attribute level before any call — the real,
T-01-rewritten implementations are **never invoked** by these three suites. Their green result proves
only that the callers' positional-arg shape is unchanged, not that the real implementation still
accepts that call. **BRIEF.md:88-92's evidence citation is wrong.**

The actual proof is elsewhere and does exist: **test-factory-integration.py** (plan.yaml:330-336, run
explicitly by T-01's verify at plan.yaml:66) drives the real `factory_decompose.py`/`factory_claim.py`
as **separate subprocesses** (test-factory-integration.py:12, `subprocess.run([sys.executable, ...])`),
with only the `gh` binary faked via `FACTORY_GH` (:309) — nothing python-level is monkeypatched.
`factory_decompose.py:458`'s unedited call to `project_field_set` therefore runs the real, rewritten
implementation for real; a signature break there raises inside that subprocess and reddens the suite.
So REQ-05 is genuinely guarded — just not by the three suites BRIEF names. **spec_violations: mismatch**
(BRIEF.md:88-92 vs. the actual mechanism) — cheap fix, reword the citation to name
test-factory-integration.py instead of/alongside the three sentinel suites.

**Redy typo case — the grilling artifact's dependency claim is wrong, confirming the eng-lead's Q4.**
Direct read: test-factory-decompose.py:1040-1047 asserts on `_validate_stations`' own
`factory_cli.refuse(...)` message (factory_decompose.py:264-268), built from the option-name list
`project_field_options` returns — never on text `factory_gh.py` raises. `_validate_stations` never
calls `project_field_set`, so it cannot depend on factory_gh.py:251-262 as plan.yaml:44-46's `because`
clause states. **spec_violations: mismatch** (plan.yaml D-04 `because` vs. measured call graph).
Tied to what qa already found (the freeze has no automated check anywhere): between the two of us, the
freeze is enforced by nothing and read by neither cited consumer — `_validate_stations` only
propagates the field-not-found exception unread, and the Redy case never reaches factory_gh's text at
all. D-04's real support is its own "operators learn the string" clause, which is legitimate on its
own — but that isn't what the plan currently says. Info, not blocking; D-04's freeze itself is still
the right call.

## D. Eng-lead's four must_fix — re-checked from outside, all closed

- **M-1 closed.** plan.yaml:315-328 now uses the three regexes recommended (field-by-name present,
  `fields(` absent, `first:`/`last:` absent).
- **M-2 closed.** The measured table (plan.yaml:106-113) and D-03 (plan.yaml:41-43) cover both the
  exit-0 null-owner and exit-1 organization envelopes live.
- **M-3 closed.** D-02 (plan.yaml:36-39) roots at `repositoryOwner(login:)` with `__typename`,
  confirmed in the query text at plan.yaml:126-142.
- **M-4 closed.** Part B adds the `field: {}` fixture (plan.yaml:273) and a dedicated case for it
  (plan.yaml:308-309), "the one that catches `if field is None`".

**The qa-flagged gap, confirmed correct (low, no guard change recommended).** The over-scope regex
guard (plan.yaml:315-328) runs only inside `project_field_set`'s success-case test, inspecting that
call's argv. `project_field_options`'s rewritten test (plan.yaml:291-293) asserts only behavior, never
the emitted query text — nothing stops a second, separately-written query serving
`project_field_options` while `project_field_set` stays clean; D-01's "ONE resolver" is unenforced
prose. Severity stays low: `project_field_options` runs once per invocation, not in the per-task loop
(factory_decompose.py:261, factory_claim.py:214 confirmed single calls) — the loop-bound cost REQ-01
targets is `project_field_set`'s alone. **Sub-question answer:** the emitted-argv assertion closes
call-time query mutation only for `project_field_set`, not for `project_field_options`.

## Out of bounds

No finding here requires reopening the grilling `## Settled` section.
