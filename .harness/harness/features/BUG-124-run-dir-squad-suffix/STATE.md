# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: .harness/harness/features/BUG-124-run-dir-squad-suffix/runs/panel-record-c1-product/state.yaml
- squad: product
- status: awaiting-user

**PLAN PHASE COMPLETE, CYCLE 1.** Station `plan`, approval `pending`, `cycles_used: 1`, seven runs
(budget 10 and 20). Everything is committed at `24aec95c` on `feat/BUG-124-run-dir-squad-suffix`.
The cycle-1 panel PASSED at `severity_max: med` with `must_fix: []`, and its record is transcribed
into plan.yaml's `panel:`. **The only thing this feature now waits on is the operator's signature.**
After `approval.status: approved`, T-01 dispatches to `harness-eng-lead`. Nothing is built; no
`review_sha` exists and none is owed until the Building -> Review seam.

**Do NOT fix R-1..R-5 before signature.** They are advisory med/low/info; `gates.review` is
`advisory_unless_high`, so none gates, and DEC-176 puts them in the operator's ONE batched signature
review. Amending the plan's substance now would also unbind the c1 panel verdict from the plan the
readers read and force a cycle-2 panel for four one-clause remedies. Only an `approval.rulings`
entry, written by the main session's `sign-approval --overrule PF-ID:<reason>`, records acceptance.

Trust (claim — pointer — verified-at 24aec95c, orchestrator-measured unless attributed):
- All EIGHT cycle-0 findings are recorded `resolved` except the info clean bill, which the panel
  never adjudicated and which stays `open`. The seven were re-derived independently by the c1
  panel, not taken on pm's word — `runs/planpanel-c1-validator/digest.md`.
- The three cycle-0 `high` findings were one class — a gate that scans free prose whose own refusal
  output re-triggers it. Closed by D-05: a QUOTED or illustrated run-dir path is spelled
  `[.]harness/`, invisible to a detector anchored on the literal `.harness/` segment.
- ZERO refusable run-dir references survive in plan.yaml or BRIEF.md, measured twice by two methods:
  by me (simulating the specified `run_dir_refs`) and by the `scope` reader, which rebuilt the
  detector from the plan's own spec and ran a positive control.
- Panel Q1 (blocking at cycle 0) is ANSWERED in D-03: `import yaml` succeeds under
  `/opt/homebrew/bin/python3`, `/usr/bin/python3` and `PATH=/usr/bin:/bin python3`, while
  `python3 -I -c "import yaml"` fails. Q2 is RULED in D-05 (state the convention in SKILL.md, T-03).
- D-01 carries the operator-accepted callee-INDEPENDENT rule; BRIEF's requirements section carries
  its `detected by nothing` disclosure naming the wrong-squad-slug case.
- The record diff is confined to `panel:`: 9 hunks, every header inside `panel:`, old spans 93-159
  within the 92-160 block. `approval: pending` and `status: plan` unchanged.
- `check-plan-routes.py`: 0 violations. REQ-01..06 all traced; SC-01..09 all have producing cases.
- Disposition vocabulary is `open|resolved` (templates/plan.yaml:80); `closed` reads as still-open
  to check-state.sh:526-533 and would have made the three `high` entries a hard INV-32 bad.

Dead ends for the next phase:
- Do NOT re-derive whether issue #124 is real, do NOT re-measure the PyYAML question, do NOT
  re-check the eight cycle-0 findings. All settled above.
- Do NOT amend plan.yaml's substance before signature (see the DEC-176 paragraph above).
- Do NOT edit `plan.yaml` by hand: `plan-merge.py` is the only write route, and `approval:` is the
  main session's `sign-approval` alone.
- Do NOT rewrite the pre-D-05 run digests and the c0 goal-check note to carry the escape spelling
  (Q3 below): rewriting a recorded artifact to look better falsifies the record.

Working set: plan.yaml, BRIEF.md, runs/planpanel-c1-validator/digest.md,
notes/review-harness-code-reviewer-planpanel-c1.md, notes/research-BUG-124-goalcheck-plan-c1.md

## Open Questions

- Q1 (harness defect, one class, two symptoms, both diagnosed and both for the harness owner):
  worktree-hosted features are graded against the OWNER checkout root. (a)
  `handoff_done_when.problems()` receives the owner root while the note's feature-dir prefix comes
  from its own worktree-relative path (handoff_done_when.py:11,51-54), and an absolute pointer is
  separately refused as "is absolute" (:69-70), so there is NO legal spelling and the plan-phase
  handoff note cannot be written at all. (b) `check-state.sh` globs the owner checkout's
  `.harness/*/features/*` (:118-120), so a full run from inside this worktree printed 867 lines,
  none mentioning BUG-124 — it cannot grade this feature. This STATE.md section is the supported
  disk-only substitute for the missing handoff note.
- Q2 (operator, at signature): the five surviving panel findings, all advisory, none gating.
  R-1 `PF-334e1b370c596f88c39730bf43579f13` med — D-05's escape is a SPELLING, so it is typable into
  a DIRECTED path, the same objection D-05 raises against a NOSCAN token, and the refusal teaches it
  to every refused dispatcher including a true positive; detection then moves from dispatch time to
  write time, where check-domain.sh still refuses, so no bypass but the mid-run cost BUG-124 exists
  to remove returns. BRIEF discloses the D-01 narrowing and not this.
  R-2 `PF-c996440943e296d047bc8707c587ad89` med — `[.]` is the literal dot in grep BRE/ERE, in a
  Python character class and in fnmatch, so an auditor grepping for the convention's own spelling
  matches every REAL anchor and no escaped site, silently.
  R-3 `PF-4ed20fe501059b1b0507f9eccfdc2fb7` med — `[` is a YAML flow indicator, so an unquoted
  `[.]harness/...` at a plain-scalar head raises ParserError; the plan's own text survives only
  because every `verify:`/`intent:` is a block scalar, which the convention never states.
  R-4 `PF-20b1d027656f333f87b7c54ddf742281` info — the refusal's convention-teaching final line is
  mandated in T-02's intent but pinned by no case; deleting it leaves the red proof green.
  R-5 `PF-fb7141e87d0ab54cb511a4c0dddcf184` low — the stale dispositions, now transcribed; recorded
  `open` deliberately so the operator rules rather than the record pre-empting it.
  Each of R-1..R-4 has a one-clause or one-assertion remedy named by its reader.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). After T-02 lands, pasting one verbatim into a
  dispatch is refused, recoverable in one re-spelling. Left as-is on purpose.
- Q4 (operator, at signature): T-02 specifies a SECOND parse of `team-config.yaml` inside the
  derivation subprocess — one small file read per governed dispatch — because it is the only source
  of the derivation's failability. Both c1 readers dismissed it as over-build; accepted as designed
  unless the operator objects.
