# Source: the four-angle /simplify dispatch prompts, verbatim from this session's transcript
# (extracted from ~/.claude/projects/-Users-molchairuangutai-GitHub-harness/070b3f94-....jsonl)

## line 6997 · subagent=general-purpose · desc=Reuse review FEAT-22 plan
```
Read-only quality review, angle: REUSE. Repo: /Users/molchairuangutai/GitHub/harness. Target: the SIGNED planning artifacts of FEAT-22 (nothing is built): .harness/harness/features/FEAT-22-docs-layout-migration/plan.yaml (r10, 11 tasks with embedded shell/python/awk verify clauses) and BRIEF.md. These are signed — you flag, never edit.

Flag places where a verify clause or task intent RE-IMPLEMENTS something the codebase already has: e.g. hand-rolled greps where layout_migration.py's exported functions/regexes could be invoked; partition audits duplicating check-plan-routes/check-state discovery; boundary-capture steps duplicating FEAT-21's captured method where a reference would do; repeated awk/grep idioms across tasks that could cite one task's canonical form. Name the existing helper/file:line to use instead and the concrete cost (two spellings drifting). Compact list: file, line, summary, cost, existing-thing-to-use. Empty if clean.
```

## line 6999 · subagent=general-purpose · desc=Simplification review FEAT-22 plan
```
Read-only quality review, angle: SIMPLIFICATION. Repo: /Users/molchairuangutai/GitHub/harness. Target: SIGNED plan artifacts of FEAT-22: .harness/harness/features/FEAT-22-docs-layout-migration/plan.yaml (r10) and BRIEF.md. Flag only — no edits (signed text).

Flag unnecessary complexity: verify clauses with redundant conjuncts (asserting the same fact twice through different spellings), task intents restating what another task's intent already rules (drift risk between two statements of one rule), dead references to r7/r8/r9 shapes that no longer exist after the revisions, over-long RED-STATES enumerations where one rule would cover, awk/sed pipelines with simpler grep -qF equivalents THAT PRESERVE the anchoring semantics r10 fought for (do NOT propose weakening the clause-4 span anchor — it is the point). For each: file, line, summary, cost, simpler form. Empty if clean.
```

## line 7001 · subagent=general-purpose · desc=Efficiency review FEAT-22 plan
```
Read-only quality review, angle: EFFICIENCY. Repo: /Users/molchairuangutai/GitHub/harness. Target: SIGNED plan artifacts of FEAT-22: .harness/harness/features/FEAT-22-docs-layout-migration/plan.yaml (r10) and BRIEF.md. Flag only — no edits.

Flag wasted work the PLANNED execution would do: verify clauses that re-run whole suites where a targeted case would bind equally (note: full-suite runs at boundary tasks are deliberate — judge only obviously redundant repeats), the same file read/grepped N times across sequential tasks where one audit pass could feed several, boundary captures re-running expensive gates already run by an adjacent task's verify, any clause invoking network (gh) that could read disk state. Estimate real cost honestly (this is a one-shot build, so only flag things costing minutes, not milliseconds). For each: file, line, summary, cost, cheaper alternative. Empty if clean.
```

## line 7003 · subagent=general-purpose · desc=Altitude review FEAT-22 plan
```
Read-only quality review, angle: ALTITUDE. Repo: /Users/molchairuangutai/GitHub/harness. Target: SIGNED plan artifacts of FEAT-22: .harness/harness/features/FEAT-22-docs-layout-migration/plan.yaml (r10) and BRIEF.md. Flag only — no edits.

Judge depth: (1) the r10 clause-4 span anchor lives as a hand-built awk program inside one task's verify — is that the right home, or should the "assert this exact sentence exists in DECISIONS.md" capability be a tiny shared checker (note the counterweight: DEC-174 makes new gate code expensive, and this runs once); (2) the plan's survivor-partition rule is stated in prose across BRIEF and multiple task intents — is there one authoritative statement the others cite, or N restatements that can drift; (3) accepted residuals (clause-1 placement ceiling, interior-markup red) — right to accept, or is a one-line deeper fix available that does NOT reopen review scope; (4) per-task RED-STATES enumerations vs one detector-output table. For each: file, line, summary, deeper-or-cheaper mechanism, cost of current shape, and an explicit recommendation: fold-into-build (executor latitude), briefing-row, or leave. Empty if clean.
```

## line 7932 · subagent=general-purpose · desc=Reuse review FEAT-22 cluster
```
Read-only code review, angle: REUSE. Repo: /Users/molchairuangutai/GitHub/harness, branch feat/FEAT-22-docs-layout-migration. Scope: `git diff main...HEAD -- .claude .github .gitignore CLAUDE.md .harness/team-config.yaml .harness/expertise .harness/notes/audit-decisions.py` (24 files, ~131 insertions — the docs-migration cluster; IGNORE the feature bookkeeping dir and the moved docs files themselves). Context: FEAT-22 moved docs/harness/ to .harness/harness/docs/ and repointed 3 resolvers + 12 test files. The wildcard-vs-literal split (grants take `.harness/*/docs/**`, prose takes `.harness/harness/docs/`) is a signed decision — do not flag it.

Flag new code that re-implements an existing helper. Candidates: repeated fixture stub text for the docs probe across test files (test-factory-integration's make_root vs layout_fixtures patterns); repeated migrated-path literals that could read off gen-decisions-index's DOCS_DIR or layout_migration constants. For each: file, line, summary, cost, existing thing to use. No correctness hunting, no edits. Compact; empty if clean.
```

## line 7934 · subagent=general-purpose · desc=Simplification review FEAT-22 cluster
```
Read-only code review, angle: SIMPLIFICATION. Repo: /Users/molchairuangutai/GitHub/harness, branch feat/FEAT-22-docs-layout-migration. Scope: `git diff main...HEAD -- .claude .github .gitignore CLAUDE.md .harness/team-config.yaml .harness/expertise .harness/notes/audit-decisions.py`. IGNORE feature bookkeeping and the moved docs. Signed wildcard/literal split not flaggable.

Flag unnecessary complexity the diff adds: comments that now say something twice, stale references to the pre-move state left beside migrated code, redundant conjuncts in edited test assertions, the two-root docs walk in test-no-distribution (docs_dirs list + nested loop — is there residue), harness_boundary's expanded :84 redundancy comment (too long? contradictory?), gh-sync/factory_config docstring edits. For each: file, line, summary, cost, simpler form. No correctness hunting, no edits. Compact; empty if clean.
```

## line 7936 · subagent=general-purpose · desc=Efficiency review FEAT-22 cluster
```
Read-only code review, angle: EFFICIENCY. Repo: /Users/molchairuangutai/GitHub/harness, branch feat/FEAT-22-docs-layout-migration. Scope: `git diff main...HEAD -- .claude .github .gitignore CLAUDE.md .harness/team-config.yaml .harness/expertise .harness/notes/audit-decisions.py`. IGNORE feature bookkeeping and the moved docs.

Flag wasted work the diff introduces. check-state.sh and check-domain.sh run at session entry / every write — anything newly expensive there matters most (the diff should be one diagnostic string each; verify nothing else crept in). test-no-distribution now walks two roots — measure whether that meaningfully slows the suite. audit-decisions.py's module-scope reads — pre-existing shape, only the paths moved; confirm no new cost. Only flag things costing minutes or hot-path milliseconds. For each: file, line, summary, cost, cheaper alternative. No edits. Compact; empty if clean.
```

## line 7938 · subagent=general-purpose · desc=Altitude review FEAT-22 cluster
```
Read-only code review, angle: ALTITUDE. Repo: /Users/molchairuangutai/GitHub/harness, branch feat/FEAT-22-docs-layout-migration. Scope: `git diff main...HEAD -- .claude .github .gitignore CLAUDE.md .harness/team-config.yaml .harness/expertise .harness/notes/audit-decisions.py`. IGNORE feature bookkeeping and the moved docs. Context: units 5-8 follow (config split, expertise re-home, repo-aware grants, live kaya proof); a second repository segment arrives eventually.

Judge depth. Candidates: (1) test fixtures now hardcode the `harness` segment in migrated docs paths — right interim (one repo exists, matches FEAT-21's precedent) or should a shared segment constant land now; (2) the refused-direction case in test-check-domain asserts the OLD path is refused — does that case survive unit 5+ or rot; (3) harness_boundary's `.harness/*/docs/**` entry being logically redundant but kept — the comment explains it; is keeping it the right depth vs deleting with the detector pattern updated; (4) audit-decisions.py living in .harness/notes/ outside every suite — flag whether it should gain a smoke test or move to bin/ (a defect class T-06/MF-A just proved). For each: file, line, summary, deeper-or-cheaper mechanism, recommendation fold-into-this-branch vs briefing-row vs leave. No edits. Compact; empty if clean.
```
