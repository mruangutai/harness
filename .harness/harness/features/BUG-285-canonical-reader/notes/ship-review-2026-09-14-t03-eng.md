# Ship review — BUG-285-canonical-reader — blocked at T-03

The feature is not ready to ship. T-09, T-01, and T-02 are complete, but T-03 stopped before source edits because the signed classification assigns `factory_config.product_config` to migration without naming a usable canonical accessor. The current public `load_harness_json(path)` cannot parse the remote in-memory `harness.json` body. No report round was spawned; this briefing was assembled from the six run digests named below and the committed direct-task record at `12c0171b`.

## Definition of done

| Perspective | Signed outcome | Verdict | SCs and evidence |
|---|---|---|---|
| operator | Every reader agrees while hooks, gates, and validators preserve violations, diagnostics, and exits. | unmet | SC-04/SC-05 remain incomplete: T-03 is blocked and T-04 through T-08 have not run. Evidence: `runs/2026-09-14-t03-eng/digest.md`; `plan.yaml` task stations. |
| code maintainer | One dependency-light reader module and one AST guard cover all Python entrypoints with named remedies. | unmet | T-01 built the AST inventory at `12c0171b` and T-02 built the accessor seam at `4c4b1a2f`, but one T-03 row names only `documented source route`, so SC-01/SC-02 are not yet closed. Evidence: `tests/integration/canonical-reader-classification.json`; `runs/2026-09-14-t03-eng/digest.md`. |
| reader (reviewer / qa) | Semantic and mechanical diffs are separately reviewable with fail-first evidence. | unmet | T-02 has fail-first evidence, but T-03/T-04 and validate have not completed, so SC-06 and final SC-07 grading remain open. Evidence: `runs/2026-09-14-t02-t04-eng/digest.md`; `notes/receipt-harness-backend-dev-T-02-c1.md`. |

## Blocking decision

Approve a narrow plan amendment or choose another disposition for `.claude/skills/harness/bin/factory_config.py::product_config::json_string#1`.

Recommendation: keep one public accessor and extend `load_harness_json` with an explicit keyword-only in-memory text source mode. Path and text inputs should be mutually exclusive and share duplicate-key, non-finite-constant, mapping, context, and typed-error behavior. Reopen T-02 only for this source mode and its tests, then re-run T-03. Exempting the remote reader would preserve the bypass class this feature exists to remove; routing it through generic `parse_gh_json` would classify artifact content as transport output.

## Run summaries

- Initial plan: signature-ready draft after reader application, later superseded by current-state planning — `runs/2026-09-13-plan-product/digest.md`.
- Deferred apply: blocked on a now-resolved source-issue interpretation — `runs/2026-09-13-plan-apply-c1-product/digest.md`.
- Current-state plan: all readers and goal-check passed; both approvals were subsequently signed — `runs/2026-09-14-plan-refresh-product/digest.md`.
- T-09: obsolete shell differential deleted and exact verify passed — `runs/2026-09-14-t09-eng/digest.md`.
- T-02: accessor seam and issue 1682 hardening passed after one internal send-back — `runs/2026-09-14-t02-t04-eng/digest.md`.
- T-03: blocked before source edits on the unresolved remote `harness.json` source contract — `runs/2026-09-14-t03-eng/digest.md`.
- T-01 was main-session-direct, so it has no team run digest; commit `12c0171b` and the Done task station are its record.

## Open questions

1. Should the signed plan add the recommended keyword-only text source mode to `load_harness_json`, or explicitly exempt/reassign the remote `harness.json` row?

## Resolved escalations

- The original issue provenance and issue 1682 placement were resolved at plan time: `source_issues` remains `[285, 1594]`, and issue 1682 remains within SC-03/SC-07.
- The obsolete shell exclusion was removed after PR 1688; all former shell entrypoints are now inside the AST surface.

## Spend and record

- `feature-record.py spend`: 6 runs, 172 recorded wall-clock minutes, build phase, tokens unmeasured, no validate rework window started.
- `feature.json`: 5 judgements, `cycles_used: 0`, hard ceiling 10, and 6 runs against the informational 20-run budget.
- The feature-level cycle record currently understates lead send-backs: the run digests report two in the initial plan, two in the refresh plan, and one in T-02. No authorized `feature-record.py` increment verb exists; this is disclosed rather than silently rewritten.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Make `observations-merge.py` create its parent directory or document/guarantee the directory precondition; T-09 initially failed until the directory was created. |
| B-2 | bug | Add an authorized feature-record verb that increments `cycles_used` from lead-reported send-backs; the current CLI can start/end runs and raise the ceiling but cannot record consumed cycles. |
| B-3 | bug | Repair the denied `xd://report_issue` route reported by the T-09 engineer so harness-tool inconsistencies can be filed through the required channel. |
