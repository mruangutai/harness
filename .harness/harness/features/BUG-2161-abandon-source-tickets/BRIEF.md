# BRIEF — BUG-2161 Abandon source tickets

## Problem

An operator dropping FEAT-1774 cannot dispose of source #1774 through Harness: its mirror never opened, so abandon skips before recording the abandoned station or pruning runs/. Sources are also absent from abandonment when a mirror exists. The supported disposal command therefore leaves dropped work open and can retain evidence that INV-51 rejects.

## Done when — by perspective

**operator** — I can see and explicitly authorize the complete disposal of a dropped feature's source tickets, or leave every source untouched. This works even when its mirror never opened or the feature was already abandoned, including the archived FEAT-1774 record.

**code maintainer** — I can rely on one reported disposal matching what executes, the signed explanation reaching every opted-in source unchanged, and the existing rejection, shipping and close guard remaining intact. The governing decision explains the new contract and its operator-owned shared-ticket risk.

## Success criteria

- SC-01 (operator): Only abandon --close-sources together with --yes can write to sources. Without --close-sources, even --yes makes zero source comments, closes, label writes or board writes; --close-sources without --yes reports but writes nothing remotely or locally. Other subcommands refuse --close-sources before mutation. QA demonstrates a failing new opt-in case before the fix and pairs no-write assertions with the opted-in positive case.
  verify: automated evidence: integration
- SC-02 (operator): For each opted-in source from plan.yaml, the executed operations close not_planned, reseat Backlog after its close, label abandoned, and comment using the exact parent --reason-file contents, without generated wording. Dry run identifies each source and every intended write, including label setup and local station/pruning effects. Separate assertions cover each source and order; failure of one source's write does not prevent later sources or local finalization. QA captures the new source-disposal cases failing before the fix.
  verify: automated evidence: integration
- SC-03 (operator): With no recorded milestone, parent or task issues, abandon --yes still records abandoned and then prunes runs/, preserving other artifacts; sources remain untouched unless opted in. Dry run leaves plan and runs/ unchanged. Fixtures include a source present only in plan.yaml, an empty source list, and a stale feature.json source mirror. QA captures the unopened-mirror cases failing before the fix.
  verify: automated evidence: integration
- SC-04 (operator): Re-entering an already-abandoned feature can dispose of sources with --close-sources --yes. An already-abandoned station is not rewritten, absent runs/ is a no-op, and retained runs/ is still pruned after confirming the abandoned station; dry run changes neither. QA demonstrates this source-disposal case failing before the fix. Existing parent/task disposal, reject source behavior and ship's Done projection remain covered by the abandonment and shipping suites.
  verify: automated evidence: integration
- SC-05 (code maintainer): Unit cases prove that the reported source operations and executed source operations derive from the same abandonment plan, source inclusion depends on explicit opt-in, and every source comment passes the unchanged reason-file path rather than assembled text. A fixture with a second active feature referencing the source still disposes only the explicitly confirmed feature's authoritative plan.yaml source list. No shared-ticket corpus check is permitted; SC-06's decision and code inspection carry that constraint, not a speculative lookup detector. QA captures failing new planner cases.
  verify: automated evidence: unit
- SC-06 (code maintainer): Inspection of git show <review_sha>:.harness/harness/docs/DECISIONS.md at DEC-203 section 8 and git show <review_sha>:.harness/harness/docs/DECISIONS-INDEX.md confirms opt-in source disposal, close-before-Backlog, verbatim reason provenance, unopened/already-abandoned behavior, and operator confirmation instead of a shared-ticket corpus check. The documented amendment does not authorize changes to gh-close-gate.py or reject source behavior; inspection of git show <review_sha>:.claude/skills/harness/bin/gh-sync.py confirms no shared-ticket corpus check was introduced and CLI usage documents the new flag.
  verify: inspection
- SC-07 (operator): After merge, I use the merged gh-sync.py executable against the archived FEAT-1774 record materialized from feat/FEAT-1774-observations-hindsight in an operator-selected archive checkout, already at abandoned; I do not use the archive branch's old executable or require the BUG-2161 worktree to survive. I review the abandon --close-sources dry run with my signed --reason-file, then explicitly rerun with --close-sources --yes and that same reason file. Source #1774 is closed not_planned, its card is Backlog, it is labelled abandoned, and its comment is my exact reason; the local feature remains abandoned without runs/. The acceptance receipt identifies the merged executable and archived record revisions.
  verify: uat

## Verification gaps

No applicable null-runner kind: unit and integration are active with configured runners in .harness/harness.json; browser/component/typecheck surfaces are not touched. Fake-gh tests cannot prove real GitHub automation ordering or the live archived record: SC-07 carries that gap and remains not met until the operator's post-merge acceptance. Per the settled grilling, this live acceptance happens after merge, never during planning or as a fabricated pre-merge pass.

## Constraints

- SUPPLIES: operator-confirmed mission plan in /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-abandon-source-tickets-2026-11-02.md; source_issues is [2161].
- BLOCKS: DEC-138 reason provenance — posting text takes only --reason-file; source comments reuse the exact parent reason without additions.
- SUPPLIES: DEC-203 section 8's abandonment close, label and close-before-Backlog sequence. Plan decision D-01 proposes its bounded source-disposal amendment; no gh-close-gate.py change and no reject source-behavior change.
- SUPPLIES: DEC-238 and INV-51 require station-before-prune even for an unopened mirror; D-02 proposes already-abandoned local idempotence without refusing source disposal.
- BLOCKS: no shared-ticket corpus check. Issue #2161's Constraint is overruled by settled grilling: --close-sources --yes and the complete dry run are the operator's guard, including sources cited by another active feature.
- BLOCKS: no source writes of any kind without explicit --close-sources --yes. No comment-only disposal without the flag; no additional source detach or dependency-discovery behavior is requested.
- SUPPLIES: PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets; its AGENTS.md maps product guidance to .harness/harness/docs/SPEC.md, .harness/harness/docs/DECISIONS.md and docs/PRINCIPLES.md. Generic docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no substitute architecture contract is invented.
- BLOCKS: no live #1774 disposal before the shipped command is merged. The archived branch supplies the record, not an older executable.

## Out of scope

- Any change to gh-close-gate.py or to how agents may close issues.
- A shared-ticket corpus check (ruled: operator confirmation is the guard).
- Comment-only disposal of sources without the flag.
- reject's source-ticket behaviour; it is unchanged.
- Closing #1774 by hand before this ships.

## Approval

status: approved
approved-by: operator
date: 2026-11-03
