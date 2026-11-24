# Reader fan-in — FEAT-2458, cycle 1

All three readers ran. Scope returned FAIL with two substance findings (one high, one med), two form findings and one task-proportionality finding; should-not-exist returned PASS with three low findings and judged the plan lane proportionate; design self-scoped out (no user-facing surface). No `scope: mission` finding exists, so no downgrade recommendation. PM applies every finding below in the planned apply step; the scope FAIL is routed to apply, not a send-back of the reader.

Lead check of the high finding's premise: `worktree_terminal.py::_match_landed_id` does prefix matching (`prefix_matches = [n for n in names if n.startswith(wt_id)]`), and plan.yaml T-01 step 2e routes `classify_feature` through it, so an absent id that is a prefix of a landed terminal id would resolve terminal and its stamp be deleted. Confirmed at the worktree.

Two readers converge on `FEATURE_CLASSES` (scope: proportionality/task; should-not-exist: substance) — both say do not publish it; pm resolves them as one change.

No prototype is required: the plan changes a hook body and gate-imported modules with plain-text diagnostics, no end-user interaction (ui-reviewer, in_scope false). Operator may override in either direction.

Inputs: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`, and the external reader return `agent://Feat2458Plan3.KindBoar.BigEarthworm` (its fenced findings block transcribed below; it has no write grant).

```yaml
DIGEST:
  severity_max: high
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending-plan scope and architecture review completed with FAIL; two substance, two form, one task-proportionality finding.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent necessity challenge completed with PASS; three low findings, mission lane judged proportionate.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A completed with PASS; self-scoped out because the plan touches no user-facing surface.
  findings:
    - kind: substance
      severity: high
      reader: scope
      summary: T-01/T-02 can delete an absent feature's stamp by matching a different landed ID.
      why: "plan.yaml:72,74 calls the worktree prefix matcher: absent FEAT-912-stamp-absent becomes terminal when FEAT-912-stamp-absent-longer is the unique landed match at done. A Harness prefix can also suppress an exact fleet match. Resolve stamp IDs exactly across segments; retain worktree prefix semantics and share the landed station rule."
    - kind: substance
      severity: med
      reader: scope
      summary: T-01/T-02 let undecodable landed records abort the stamp sweep.
      why: "Invalid UTF-8 in a landed feature.json raises UnicodeDecodeError from worktree_terminal.py:49-54 before JSON parse handling; the planned OSError catch does not intercept it, so the stamp gets no unresolved line and subsequent stamps are unprocessed."
    - kind: form
      severity: med
      reader: scope
      summary: SC-11 requires a post-merge observation as a pre-ship UAT gate.
      why: "BRIEF.md:86-89 requires the feature to have merged before the operator checks it, but DEC-74 requires UAT to pass before ship. Preserve the live check as a post-merge operational check, or stage an equivalent disposable-checkout UAT before merge."
    - kind: form
      severity: low
      reader: scope
      summary: The decision dispositions omit three governing keep rows.
      why: "DEC-221 governs the central fleet segment lookup, DEC-191 governs station ownership in landed plan.yaml, and DEC-252 governs the shared INV-29 reader's comparison-only use of shipped records. The plan keeps those rules unchanged; no amend or strike is warranted. Record DEC-74 as keep if retaining a UAT criterion."
    - kind: proportionality
      scope: task
      severity: low
      reader: scope
      summary: T-01 publishes a result vocabulary with no production caller.
      why: "FEATURE_CLASSES is only needed for the proposed membership assertion; the literal class/reason assertions already pin the interface, and the hook does not read the tuple."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "T-01's mandated extraction of a shared _landed_names helper out of _resolve_landed is an optional refactor of a gate-critical path; classify_feature can carry the ~6-line segment lookup privately instead"
      why: "D-02 governs the landed rule (_landed_classification), which is shared either way; the lookup steps b-d are not the predicate. Refactoring _resolve_landed, the chain check-state.py's INV-29 and worktree reclamation run, buys removal of a small duplication at the price of regression surface in a DEC-174 human-read diff: a slip there mis-classifies standing worktrees fleet-wide, and the reviewer must now also prove classify/classify_all unchanged."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "SC-06's inspection clauses that re-check what T-02's verify line already greps should be dropped, keeping only the reads-no-records clause"
      why: "T-02 verify machine-proves the three symbol facts (no def _repo_arg_for_segment; worktree_terminal.repo_arg_for_segment( present; worktree_terminal.classify_feature( present) on every run; requiring the reviewer to cite each again spends human review attention, the scarce resource under DEC-174, and dilutes the one clause only a human can judge: that the stamp sweep reads no plan.yaml/feature.json/BRIEF.md/station itself."
    - kind: substance
      severity: low
      reader: should-not-exist
      summary: "The new public FEATURE_CLASSES constant (T-01 step 1, named in SC-08's docstring surface) was not asked for by grilling R3 and should not be public surface; its only planned consumer is a test membership assertion a literal tuple serves"
      why: "CLASSES = (terminal, exempt_absent, unresolved) in worktree_terminal.py; FEATURE_CLASSES = (terminal, unresolved, not_terminal) shares two members but encodes the opposite treatment of absence. Publishing both tuples side by side in the gate-imported module invites a future check-state.py or hook maintainer to reach for the wrong vocabulary, and permanently widens the public surface the docstring polices."
```
