# Reader fan-in — plan-product cycle 1

All three readers ran. Findings are transcribed at each reader's own severity and kind; the
`why` text lives in each reader's note (scope: notes/review-harness-code-reviewer-plan-c1.md;
design: notes/review-harness-ui-reviewer-plan-c1.md; should-not-exist: inline return, no write
grant — its `why` lines are carried below for apply). The code-reviewer and ui-reviewer
no-successor-reject findings are one defect reported by two readers; both are kept, since
identity is reader plus summary.

```yaml
VERDICT: FAIL
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "returned FAIL; note at notes/review-harness-code-reviewer-plan-c1.md"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "returned three findings inline (no write grant)"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "in scope (CLI reject/abandon states); returned FAIL; note at notes/review-harness-ui-reviewer-plan-c1.md"
  findings:
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-05/T-07 deletes evidence before terminal state on reject with no successor."
      why: "gh-sync.py:2093 leaves the station write to the caller when the successor is none; T-05 cleans first, so a refused later write loses evidence on a nonterminal feature."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-03/T-06/T-07 cannot reliably clean after ship or distill."
      why: "Ship writes the owner/plain-clone plan while clean reads the retained worktree plan; owner done/worktree review refuses the declined-distill and retry paths. A completed distill with no Expertise diff cannot reach merge-distill cleanup either."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-03's project-note cleanup can delete unclaimed files."
      why: "A valid flat project_notes path can name a directory; recursive deletion then removes unclaimed descendants. A symlinked parent is not constrained by checking the final target alone."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-06/T-07 does not stage D-04's durable distill ledger."
      why: "The instruction to commit only Expertise leaves feature.json dirty when runs are registered/closed, and merge-gate.py:414-420 refuses before local receipt replay."
    - reader: code-reviewer
      severity: high
      kind: substance
      summary: "T-01 changes T-03/T-06 fixture semantics before their gates are migrated; first landing and registry timing are unstated."
      why: "The old BUG-2399 tests derive behavior from the root ignore file and still require staging or the old refusal output; the main distill fixture stages via add -A before ignore rules. Intermediate fresh PR trees hit old check-state reads or stale CI registries; an ordinary hooked merge still invokes merge-gate.py. Explicit isolated verification is not equivalent to live enforcement."
    - reader: code-reviewer
      severity: med
      kind: substance
      summary: "T-08 misses live clauses in affected decisions."
      why: "DEC-46, DEC-150 and DEC-191 still prescribe or describe committed run history, archives, or retired readers; several listed amend entries also retain live obsolete clauses. DEC-257 alone is correctly struck."
    - reader: code-reviewer
      severity: low
      kind: form
      summary: "T-07's negative grep matches its own required documentation."
      why: "plan.yaml rejects runs/distill-*/digest.md in T-07's verify, which the T-07 intent explicitly requires."
    - reader: ui-reviewer
      severity: high
      kind: substance
      summary: "T-05 deletes local working files before writing the terminal station on reject --superseded-by none."
      why: "BRIEF.md SC-06 requires terminal recording before deletion and preservation on a refused station write; references/reject-path.md step 4 and gh-sync.py:2093-2115 leave the station write to the caller after exit 0 for none. If that write refuses, the files are already gone."
    - reader: ui-reviewer
      severity: med
      kind: substance
      summary: "T-05 does not specify what abandon or reject reports when the terminal operation succeeds but local cleanup fails."
      why: "T-03 propagates the cleanup error after any earlier removals and T-06 distinguishes post-merge cleanup failure from merge refusal; T-05 leaves the equivalent case unspecified as INV-51 retires, so an operator may retry the remote operation rather than only local cleanup."
    - reader: should-not-exist
      severity: low
      kind: proportionality
      scope: task
      summary: 'GATE 2b''s per-file "WOULD DISCARD WORKING FILE" listing turns every post-merge sweep into a wall of output for shipped-but-undistilled features'
      why: "post-merge-sweep.py:249-255 reprints feature-worktree.py remove output on decline; after D-08 every shipped feature refuses with exit 4 until distill or clean runs, burying the one actionable line (the clean command). Naming the three directories plus a file count carries the same remedy."
    - reader: should-not-exist
      severity: info
      kind: form
      summary: 'T-06''s induced-cleanup-failure integration fixture ("a directory the process cannot remove") is environment-dependent and should be a unit-level fake instead'
      why: "permission-based unremovable directories do not exist for root (some CI/container environments); the exit-4 contract is provable by faking the OSError at the working_files.clean seam. [reader: unverified whether CI runs as non-root]"
    - reader: should-not-exist
      severity: info
      kind: substance
      summary: "Everything of substance traces to an operator ruling or a grilling \"Not yet specified\" item; no task builds a thing the user does not need, and no task is obsoleted by another"
      why: "Stated agreement so the panel does not re-litigate it: D-01..D-08 map to settled grilling lines or delegated open questions; rejected alternatives are uniformly heavier; the mission is correctly plan-lane."
```
