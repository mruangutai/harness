# FEAT-70 plan scope and architecture review

## BLUF

PASS. The BRIEF and plan faithfully encode the complete settled grilling intent, the task graph is sufficient and correctly ordered, and the mission is proportionate. I found no blocking, advisory, form, or proportionality issue.

## Specification compliance

- All three success criteria are live and traced by both T-01 and T-02. There are no orphan SCs or unknown trace identifiers (`BRIEF.md:15-27`; `plan.yaml:33-36,80-83`).
- The exact quantities and exclusions are retained: the unchanged hyphenated entry is roughly 250 lines; the package is `__init__.py` plus exactly ten named implementation modules; all twelve named below-bar functions must reach grade 4; the existing suite has 107 subprocess cases; exactly 15 classification rows are re-keyed; FEAT-70 and `record-amendments` are excluded only from the baseline identity sweep for the stated reasons (`BRIEF.md:15-24,37-44`; `plan.yaml:45-76,92-108`).
- D-01 resolves the reset/resume family to `stations.py` and D-02 records the exact helper decompositions. T-01 carries those decisions without weakening their boundary behavior (`plan.yaml:22-31,56-66`). The ownership language matches the binding note rather than relying on near synonyms: the text primitives, guards and anchors, union operations, approval family, station/reset family, panel and key-validator binding, amendment atomic write, deletion, and check owner are all explicit (`plan.yaml:54-58`).
- The crash is fixed at the shared `_render_field` line-list contract rather than special-cased in `record-amendments`, and the regression is red-first and observes the atomic two-entry outcome (`plan.yaml:50,60`; SC-03).
- T-01 machine ownership uses the package-aware `.claude/skills/harness/bin/plan[-_]merge*` glob and four short `files` entries, satisfying the 50-line machine-field constraint without enumerating the package. T-02 owns only feature notes via a glob (`plan.yaml:41-45,88-89`). No line-number anchor appears; references use paths or symbols.
- Every task is `main-session-direct` with a DEC-174 reason; lane rows cover implementation, tests, and receipt evidence. `source_issues` is empty (`plan.yaml:6,11-20,37-39,84-86`).
- Topology is correct: T-01 produces and commits the implementation; T-02 depends on T-01, pins that commit, then creates scripts and receipts. No later task mutates production or tests, so T-02 cannot invalidate T-01's final gate (`plan.yaml:40,47-48,87,90-93,110`). Verification is bounded: T-01 grades the exact entry/package set and runs the owning behavioral/classification runners; T-02 validates the committed receipt chronology and reruns the pin-grade assertion while the one-execution identity measurement remains preserved as evidence (`plan.yaml:46-48,90-110`).
- Plan and BRIEF both remain in plan/pending approval state; tasks are ready, `needs_approval` is true, and the BRIEF records the pending—not signed—recommendation of 2 rounds and 480 wall-clock minutes (`BRIEF.md:45,53-54`; `plan.yaml:3-6,40,87,111`).
- Out-of-scope behavior and later long-file waves remain excluded; the plan adds no compatibility shim, second dispatcher, renamed command, extra normalization, or file-length ratchet (`BRIEF.md:47-51`; `plan.yaml:52,60,76,105`).

## Architecture and proportionality

The package boundary is justified by observed variation: verb families are adapters over shared text/guard seams, while the existing entry remains the single small interface. The plan concentrates generic mutation mechanics in `text.py`, enforcement/lifecycle behavior in `guards.py`, and each writer family in one owner, improving locality without adding a second dispatch layer or speculative seam. The two explicitly decomposed complex functions split independent search/reload/schema/order responsibilities while preserving their coordinator interfaces. Tests and mutation proofs move with the package seam rather than reaching past it through a monolith copy.

Mission proportionality: **proportionate**. A plan mission is warranted by the new importable package surface, twelve behavior-preserving grade repairs, the shared text-contract bug fix, package-aware mutation harness migration, canonical-reader re-keying, and immutable cross-checkout byte proof. T-01 and T-02 are both necessary to ship: T-01 makes the bounded implementation change; T-02 establishes the immutable pin and reproducible evidence. No task or mission lane exceeds a live requirement.

## Findings

None.

## Principles applied

- **Delete First** — judged the design against unnecessary dispatch layers, compatibility shims, and speculative modules; the draft keeps one entry/dispatch interface and only the settled ownership package.
- **harness-codebase-design** — assessed depth, seam placement, adapter variation, locality, and reader load; the package earns its interface through distinct verb-family behavior over shared primitives.

## Review record

```yaml
VERDICT: PASS
DIGEST:
  headline: Draft scope and architecture fully match the settled grilling intent and are proportionate.
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-70-long-file-plan-merge-package/.harness/harness/features/FEAT-70-long-file-plan-merge-package/notes/review-harness-code-reviewer-plan-c0.md
```
