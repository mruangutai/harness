# Receipt — harness-backend-dev — FEAT-2225 T-01 SIMPLIFY final (run r-20261121-5-simplify-eng)

**BLUF.** PASS. T-01 verify exit 0 (unit 0, integration 0); code-grade at `f06b2e57` reports 414 PASS, 0 FAIL, 0 REASON REQUIRED, 0 SEVERITY lines; audit 0 unresolved. One reader finding applied (REUSE F-1), the rest skipped with reasons. One run, zero correction cycles.

## Dispositions

|Finding|Disposition|Reason|
|---|---|---|
|REUSE F-1|APPLIED|`_EXPERTISE_REL` shared fragment; `EXPERTISE_TAIL = (?:^|/)` + frag + `$`, `EXPERTISE_PATH_RE = ^` + frag + `$`. Same regex text as before for TAIL; PATH_RE gains one unused capture group (only `.match` truthiness is used, line 1013). `require_destination` still gets the identical TAIL match/capture.|
|SIMPLIFICATION F6|SKIPPED|`_is_persona`/`_declared_segment` already share the persona/segment rules with `destination_rel`. Replacing `_destination_form_ok`'s `(.+)` + persona-equality form with `EXPERTISE_PATH_RE` would change receipt-header acceptance (receipt evidence contract); the dispatch forbids tightening it.|
|REUSE F-2/F-3, T-04 findings|SKIPPED|T-04 host/guards/schema/tests are main-session-direct, no grant.|
|SIMPLIFICATION F9|SKIPPED|Structured cap errors exceed the local interface.|
|REUSE F-4|SKIPPED|Optional cross-suite fixture cleanup, not needed for the grade lift.|
|Altitude F1|SKIPPED|Authority change is main-session-only, already routed.|
|Repeated check-expertise/authority check removals|SKIPPED|No assertion deletion/weakening/merging.|

## T-01 verify (plan.yaml:160, matches verbatim)

```
python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py
```
Run as `env -u HARNESS_AGENT_TYPE sh -c '<that string>'`: exit 0, 551 PASS lines, 0 FAIL (output /tmp/t01.out). Constituents run separately: unit exit 0, integration exit 0.

## AST fact comparison (same expression: ast.walk, Call with func Name `check`; ast.Assert)

|File|check calls fd8ffcdf → final|ast.Assert|
|---|---|---|
|tests/unit/test-expertise-ops.py|119 → 119|0 → 0|
|tests/integration/test-expertise-merge.py|255 → 255|0 → 0|

Fact set: multiset of first-arg labels is identical in both files. Multiset of full call args (label, condition, detail) is identical except two textual shape differences, both semantics-preserving:
- unit `u40: receipt failure is refusal 15`: `e.code == 15`/`e` → `refusal.code == 15`/`refusal` (variable renamed in the split phase).
- integration `supersession: historical receipt is immutable`: `open(...,'rb').read() == old_bytes` → `read_bytes(...) == old_bytes` (new helper doing the same read, now closing the handle).

## Runtime tallies (named scripts, HARNESS_AGENT_TYPE unset)

|Script|Exit|PASS check lines|FAIL|
|---|---|---|---|
|tests/unit/test-expertise-ops.py|0|194 (+1 trailer line)|0|
|tests/integration/test-expertise-merge.py|0|355 (+1 trailer line)|0|

Equal to the earlier T-01 receipt (194/355). Discovery: unit suite registers `LEGACY_CASES` + `GUARDED_CASES`, integration `SERIAL_CASES` (26) + `POOLED_CASES` (13); all checks ran through those registries, with no empty collection (counts above).

## Other gates (exit codes)

|#|Command|Exit|Notes|
|---|---|---|---|
|2|tests/integration/test-member-expertise.py|0|111 PASS, 0 FAIL|
|3|tests/integration/test-validate-digest.py|0|ALL PASSED (output has the word FAIL only inside passing test names)|
|4|tests/integration/test-merge-gate.py|0|ALL PASSED|
|5|code-grade.py --base 594af2a8 --head HEAD|0|414 PASS; no FAIL, REASON REQUIRED or SEVERITY lines; no grade-2 reasons owed|
|6a|check-plan-routes.py|0|0 violations across 2 plans|
|6b|check-plan-routes.py --canonical-reader-audit|0|0 unresolved reader sites across 100 Python files (`cmd_ops.transform` anchor resolves)|
|state|check-state.py (before commit)|0|only notes; LAYOUT dirty notes report 4 paths not to be touched by repair|

Grading-at SHA: `f06b2e57d1f6ee38ed901a66885a0f0cb29f0b8b` (the source commit, made after the suites and before code-grade). Outputs under /tmp/{t01,u,i,state,grade,r,ra}.out and /tmp/test-*.out.

## Commits

- Source (three owned paths by pathspec): `f06b2e57` `[harness:SIMPLIFY] FEAT-2225: lift T-01 functions to the code-grade bar; share the Expertise path fragment`.
- Receipts: this file (and the earlier lifts/reuse receipts) are left untracked for the lead/main bookkeeping; none were staged by me.

## Tree status

Source-only clean: yes (three owned paths committed). Total tree NOT clean. Dirty paths for lead/main: `.harness/harness/features/FEAT-2225-member-expertise-writes/feature.json` (modified, not mine), and untracked notes receipts: `receipt-harness-ai-dev-...-altitude.md`, `receipt-harness-backend-dev-...-lifts.md`, `...-reuse.md`, `...-final.md`, `receipt-harness-data-engineer-...-simplification.md`, `receipt-harness-dev-ops-...-efficiency.md`.

## Docs/changelog

Unchanged: behavior and interfaces are unchanged, so there is no semantic doc update.

## Principles applied

Delete First (`references/delete-first.md`, read): F-1 merges two copies of the path grammar into one fragment, removal before addition; F6 skipped because deduplicating it would alter receipt acceptance.
