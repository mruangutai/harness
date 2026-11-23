# Security review c2 — BUG-2399

PASS: no security findings in `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd`. Owner: T-01. Inspection and historical-evidence audit only; no tests, probes, builds, linters or formatters executed.

## Scope and boundaries

- IN: pruner, regression tests, ship instructions, DEC-238 and regenerated index: local record identifiers/files become Git index entries and committed evidence. OUT as independent executable surfaces: BRIEF, plan, STATE, feature.json, observation log and all added answer/build/research/red-first/reviewer/simplify notes; these are specification or audit records. Full pinned diff credential screening found only token accounting, quoted prior screening prose and synthetic `secret.txt` containing `external`, not credentials. Prior c1 security review covered this surface; c2 independently inspected the full base-to-pin delta.
- Injection/Tampering: pruner:172–175 confines recorded ids to single directory entries; :209–210 uses argv without a shell, literal pathspecs and NUL-delimited stdin. Names cannot become Git options or wildcard/pathspec directives.
- Information disclosure/Tampering: :178–192 skips linked run directories and linked files, does not follow linked subdirectories, and excludes the immediate run `ui/` subtree. Only recorded-run paths reach staging. This is not a claim of protection against a concurrent actor already authorized to replace checkout files or control Git configuration/environment.
- Refusal/Tampering: :235–241 checks missing evidence and traversal errors before either mutation call at :242–243. Dry-run returns before Git at :207–208 and preserves existing deletion suppression. Git-add failure is exit 1, not a pre-mutation refusal or rollback guarantee.

## Previous must-fix disposition

- **MF-1 resolved, T-01 / SC-01:** :186–188 records `os.walk` errors; :196–200 aggregates errors across recorded runs; :238–241 exits 1 naming them before prune/stage. The pinned tests :271–296 exercise chmod-000 traversal, error-path identity, unchanged index and a prunable UI sentinel in both modes. `notes/red-first-T-01.md`, c1 fix section, records three genuine red assertions against c1 and 40 green checks without SKIP. Independently computed pinned SHA-256 values match that receipt: pruner `55df0581f38f88489e5ba876a617cd9f74bd245dfbd94972c3f3526e201a93ef`; tests `5431b50296c38aac81abf1971225fe54d3e9aa9e81eb18c3522c7df90bbaa05d`. Historical failures were not rerun.
- **MF-2 resolved by operator ruling, T-01 / SC-03:** pinned `notes/answers-2026-11-23-c1-ruling.md` explicitly accepts the historical removal clause as vacuously satisfied, with no amendment/reapproval. Remaining security-relevant SC-03 clauses pass inspection: existing keep/prune and deletion-symlink functions are unchanged; dry-run guards remain; ship diff retains the human prune commit and documents automatic staging; decision diff changes only DEC-238's ship bullet. No old must-fix remains open or regressed.

No new findings or scope changes. Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent in the pinned tree; approved BRIEF/plan and the explicit ruling supply this patch's acceptance guidance. Open questions: none.
