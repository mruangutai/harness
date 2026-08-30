# Receipt — harness-backend-dev — simplify/simplification — FEAT-45

BLUF: the plan is close to the smallest set. One real finding (D-10 misclassified as a
decision when it's a measurement); everything else I hunted for either doesn't reduce the
set or is defended load-bearing repetition. No dead references found.

## Finding 1 — D-10 records a measurement, not a choice

**Acts on:** D-10 (decisions count), REQ-09.

D-10's body is "measured with check-domain.sh --resolve at 7ebfc9e", listing four already-true
resolutions. Nothing was chosen among alternatives — it's an audit record that REQ-09 is
already satisfied, which is exactly what `dec: none` on it already concedes. The `lanes:` block
directly above already carries the identical methodology statement ("Every row below was
produced by `check-domain.sh --resolve <path>` at this sha, not read off team-config.yaml"),
so D-10 duplicates that block's authority for a set of paths (`lanes:` covers only repo-source
surfaces, D-10 covers per-feature `notes/` paths) that could just as easily be a second `lanes:`-
style comment block rather than a numbered decision.

**Cost of leaving it:** none functional — but it inflates "13 decisions" with an entry that
isn't a decision, which is the exact property this pass is checking for, and a future reader
skimming `decisions:` for things the operator actually chose has to filter it out by hand.

**Alternative:** move D-10's body into a comment on the `lanes:` block (or a T-01 receipt note)
and drop it from `decisions:`, dropping the count to 12. Low value, not blocking — flagging
because the prompt asked me to adjudicate it directly.

## Non-findings — defended explicitly

**T-07/T-08 merge:** wrong to merge. T-08's `inv32-red` case (D-13) requires T-07's BEGIN/END
markers to already exist on disk before it can build the mutant; the split also gives each task
its own file and its own verify (T-07: does INV-32 exist and register; T-08: does the fixture
suite, including the failing-first proof, pass). This is exactly the test-first-discipline
shape the assignment flagged as the likely reason — confirmed, leave split.

**T-09/T-10 shared file (`run-unit-tests.sh`):** not a finding. Same agent
(`harness-dev-ops`), sequenced (T-10 depends on T-09 among others), and the two files being
registered (`panel_findings.py`'s content-hash helper vs. `test-plan-panel.py`'s wiring
assertions) are genuinely different subject matter, not an artificial split of one concern.
Merging would force the identity-helper work to wait on T-02/T-03/T-04/T-06 (T-10's other
deps) for no benefit — that's an efficiency-angle cost, not mine, but it's also not a
simplification win: task count drops by one while losing schedule freedom.

**T-03/T-04 merge:** wrong to merge. Different documents serving different readers (T-03's
playbook section is the orchestrator's full three-segment procedure; T-04's edit is the
one-bullet doctrine-door pointer that REQ-10's machine check greps), different files, different
verify shapes (grep+script vs. regex-sliced bullet assertion). No token or step is saved by
merging two single-file, single-purpose edits into one multi-file task.

**Repetition of "unrated == high", "then: escalate never halt", "panel key outside approval",
and "reworded finding gets a new id":** traced every cited site (D-06/T-01/T-02/T-05/T-06/T-07;
D-11/T-02/T-06/T-10; D-07/T-03/T-05; D-05/T-05/T-07/T-09/SC-13). All four are load-bearing, not
drift-prone duplication with one available authority. Each site is read by a different,
independent consumer that cannot be pointed at a shared source instead: an LLM reader's prompt
(T-02), an LLM lead's agent-definition instructions (T-06), a python enforcement script
(T-07), a decision archive entry (D-05/D-06/D-07/D-11), a template comment for future plan
editors (T-05), a module docstring for a future maintainer reading the file cold (T-09), and a
BRIEF success criterion (SC-13). There's no shared-constant mechanism across an LLM prompt, an
agent-definition file, a shell/python gate, and a decision log — each has to carry its own copy
or the rule silently stops applying somewhere. No finding.

**D-12 (run-unit-tests.sh not enforcement-path):** not redundant with T-09/T-10's intents.
It's a DEC-174 lane classification — the actual answer to "does touching run-unit-tests.sh's
UNIT_SCRIPTS array require main-session-direct treatment like check-state.sh does?" The `lanes:`
rows confirm the answer it records (run-unit-tests.sh is `team`/`harness-dev-ops`, not a
DEC-174 carve-out) but D-12 is the one place that states *why*, which a DEC-174 reviewer would
otherwise have to re-derive. Keep.

**SC-04 vs SC-07:** different falsification directions, not double-grading. SC-04 covers
"panel exists, has a high finding, not resolved/overruled" (T-07 check 2 — severity gating).
SC-07 covers "no panel result recorded at all" (T-07 check 1 — REQ-10's specific ask that a
removed panel step is detectable). Distinct code paths, distinct failure modes. Keep both.

**SC-02 vs SC-14:** different properties, not double-grading. SC-02 grades grant-coverage for
every step that actually writes something (non-empty `outputs:`), explicitly excluding the
empty-outputs case. SC-14 grades a structural identity assertion on one specific step (non-
harness persona AND zero declared outputs), which is a different question (independence of
that one reader) than "is every real output path granted." Keep both.

**Dead references:** checked and found none. `resolved_at: 7ebfc9e` is the direct parent of the
pinned `review_sha` (1d3e5db is the plan-authoring commit built straight on 7ebfc9e, `git
merge-base --is-ancestor` confirms, no intervening commits) — no drift. FEAT-44 appears once
in BRIEF.md, correctly describing the retracted-id incident as an out-of-scope backlog pointer,
not a leftover self-reference. All scripts and helpers T-01/T-03/T-06/T-07/T-08/T-10 cite by
name exist on disk (`gen-decisions-index.py`, `test-gen-decisions-index.py`,
`test-orchestrator-playbook.py`, `sync-agent-adapters.py`, `test-sync-agent-adapters.py`,
`test-team-catalog.py`, `live_invariant_numbers` in `check-plan-routes.py`), and the
`T14_MARKER`/`T10_MARKER` idiom D-13 cites as precedent is present in `test-check-state.py`.

## Verification

`git status --porcelain` over `plan.yaml`, `BRIEF.md`, and `.claude/` in this worktree: empty.
No files under my domain guard were touched; read-only pass, as required.
