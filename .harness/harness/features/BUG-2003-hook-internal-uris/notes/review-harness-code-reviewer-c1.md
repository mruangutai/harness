# BUG-2003 c1 — pinned code review

PASS: V1 is closed by exact SC-03 assertions; Stage 1 passes and the subsequent full production/test quality review finds no actionable defect. This is a read-only inspection verdict, not a new test-run claim.

Reviewed committed bytes at `c2170e265c30e36d6252668775ee41a8ebc93fb6`, against implementation baseline `7fba7e1d`; authoritative merge-base range is `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..c2170e265c30e36d6252668775ee41a8ebc93fb6`. Full commit history inspected: no human-tagged commits. Only tracked dirt is feature.json; its review pin agrees. Inherited FEAT-495 changes are PR/status station bookkeeping, not implementation. Actual `git diff --stat f9e23bcb c2170e26 -- .omp`: **empty output**. Production has not changed since f9e23bcb.

## Stage 1 — PASS; V1 closed (T-01, SC-03)

All references below are pinned `tests/unit/omp-hooks.test.ts`:
- Forbidden real-file write, :1134-1156: pre result equals `{ block: true, reason: "/repo/forbidden.ts is outside your domain" }`; post asserts `isError: true` and exact texts `["ok", "Harness post-write check: /repo/forbidden.ts is outside your domain"]`. Gate array equality pins exactly `[]/Write/{file_path: FORBIDDEN, content: "x"}` and `["--post"]/Write/same input`; pre feature identity is also asserted. Removing the write gate or altering its refusal/content/name/arguments violates these assertions.
- Mixed allowed URI/forbidden file edit, :1093-1111: exact pre refusal, post error flag and the same literal composed texts; gate array equality pins exactly two calls, `[]/Edit/{file_path: FORBIDDEN}` and `["--post"]/Edit/same input`. Skipping a sibling file, forwarding the allowed URI, changing Edit payloads, or dropping original post content violates these assertions.
- Main session, :1159-1170: `conflict://1` and `/repo/src/a.ts` each exercise write AND edit, tool_call AND tool_result; every callback must return undefined, with no check-domain call across the matrix. Applying governed scheme refusal or file gating to Main violates these assertions.

SC-01/02 coverage: allowed URI write/edit pre/post at :1055; refused device/scheme matrix and exact-xd suffix at :1067; MV destination at :1083. SC-04 **inspection PASS**: `.omp/extensions/harness-hooks.ts:272-284` is the sole classifier; :289-313 independently judges write.path and each extracted section/MV destination; preDomain :325-328 and postDomain :339-340 share it. Lineage authorization, main-session early returns, Bash checks and malformed-edit behavior remain unchanged. SC-05: registered production callbacks are exercised, not a replacement classifier. Committed fail-first/pass receipts name the four discriminating cases (102/4 then 106/0 and literal verify exit 0); these historical receipts do not claim the additional c1 controls were red or executed at c1. No developer amendment/principle-claim receipt is present in the pinned change.

## Stage 2 — PASS

Reviewed the full production/test delta after Stage 1. Recognized non-allowlisted schemes, including unknown schemes, produce a nonempty blocking reason before any file-domain runner; allowed decisions skip only their own target, not siblings. Ordinary-file payload/base/cwd and pre/post argument construction preserve baseline behavior. Refusals reach the unchanged pre block and post error composition. Tests inject only the established policy-runner seam and call real registered handlers; refused and file-preservation assertions would fail if registration or imported behavior became inert. Paired positive refusal/payload controls keep URI absence assertions from being the suite's sole proof. No new resource lifetime, exception swallowing, independent permissive branch, compatibility shim, or speculative interface was introduced. Existing malformed-edit zero-target behavior and runPolicy nonblocking error policy are unchanged, explicitly outside this patch's cutover.

Python grading: `n_a` — no Python path changes in the authoritative range. No execution, tests, mutants, builds, linters, formatters or grading commands run. Final `python3 tests/unit/test-omp-hooks.py` execution belongs to the authorized QA/main gate; this note supplies inspection only. Open questions: none. Findings/must-fix/spec violations: none.

## Principles applied

- Model the Domain: the discriminated DomainTarget union localizes the one scheme decision rather than synchronizing pre/post booleans.
- Delete First: shared fileDomain replaces duplicated write/edit gate construction; its two stage callers retain necessary event/base distinctions.

```yaml
VERDICT: PASS
DIGEST:
  headline: "V1 closed; both spec and full code-quality stages pass at c2170e26."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..c2170e265c30e36d6252668775ee41a8ebc93fb6"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2003-hook-internal-uris/.harness/harness/features/BUG-2003-hook-internal-uris/notes/review-harness-code-reviewer-c1.md
```
