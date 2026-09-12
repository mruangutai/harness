# The plan phase — one run, one signature

Read this when your mission is `plan` or `patch`, before the first dispatch. The rule in the
playbook is one line; this is the procedure. Evidence and history: DEC-225, DEC-228, DEC-229.

## Mission plan

ONE dispatch of the `plan` team to `harness-product-lead` — resolve it
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/teams/plan.yaml` before
`<HARNESS_CONTROL_PLANE_ROOT>/.claude/skills/harness/teams/plan.yaml`, as `harness-team` requires.
Pass the grilling artifact's path (its `## Mission` block reads `mission: plan`) and the BRIEF's.
The whole plan phase happens inside that run; you sequence nothing between its steps. Run-dir
slug: `plan-product`.

Inside the run:

- pm drafts BRIEF and `plan.yaml`; then, **in one turn**, three readers see the same draft:
  `scope` (code-reviewer — orphan SCs, traces to nonexistent SCs, non-topological deps,
  verify-vs-delete, and the architecture read per `harness-codebase-design`; there is no separate
  eng-lead review at plan time), `should-not-exist` (fable-advisor; if that persona does not
  resolve, the lead skips it and **records the skip** — never presents a skipped reader as one that
  ran and found nothing) and `design` (ui-reviewer, which self-scopes out on a non-UI plan).
- pm applies: every `form` finding is fixed in place, every `substance` finding is applied, then
  pm runs `plan-merge.py record-panel --file <plan.yaml> --digest <run_dir>/panel-c<N>.md --cycle N`
  over the lead's reader fan-in and `plan-merge.py check --file <plan.yaml> --root <worktree>`,
  which resolves every anchor, every `files:` path against the layout gate and every
  `execution_agent` route. Both verbs are pm's, inside the run; no run exists to transcribe.
- pm's goal-check, **once, at plan exit** (SC-09): one grade per perspective against the
  operator's STATED INTENT — the grilling or wayfinding artifact handed through the plan door, not
  the BRIEF derived from it. The question, verbatim: **does this plan deliver the operator's stated
  intent?** Written to `notes/research-<FEAT>-goalcheck-plan.md` — no cycle suffix; it does not
  re-run per cycle.

When the run returns, run
`plan-merge.py record-panel --file <plan.yaml> --digest <run_dir>/digest.md --cycle N` once
yourself: the lead's final digest carries every reader including `goalcheck`, which ran after pm's
apply, and INV-32 reads `panel.readers` for it. This is the one `plan.yaml` verb you hold beside
the station writes (DEC-229); `approval:` stays the main session's.

## Findings and the proportionality route

Every finding carries `kind` — `substance`, `form` or `proportionality` (SC-06); one without is
rejected at the digest. Only a `substance` finding re-panels, and only over the tasks it names, in
a new run directory; a `form` finding never buys a re-read.

**A `proportionality` finding no reader opposes** is the panel telling you the mission is too heavy
(SC-03). The lead's digest says `recommend: downgrade patch`, and you act on it yourself:
`feature-record.py set-mission --file <feature.json> --mission patch`, a `mission` judgement with
the reason, and the intake returned `pending` with the downgrade stated in your return — the
operator sees it at signature, not as a question. A re-cycle on a proportionality finding is a
defect.

## The signature

The run returns BRIEF and `plan.yaml` `pending`. You never mark them approved: the main session
signs with `plan-merge.py sign-approval --rework rounds=N,minutes=M --decision <path>`, and that one
signature is also the operator's one rework ruling for the build phase (DEC-226, SC-15). Findings
the operator accepts are `approval.rulings` entries from `--overrule PF-ID:<reason>`, written by
that same act and never by you or pm.

## Mission patch

`mission: patch` in the grilling artifact is the same single dispatch with a smaller deliverable
and no readers: a BRIEF in the by-perspective shape at ≤ 120 lines and a `plan.yaml` holding
exactly one task — `T-01`, `execution_mode: team`, `execution_agent` the owning dev, `files:` from
the grilling, `traces:` every SC, `change_type: bugfix` unless the grilling says otherwise. No
panel, no goal-check run: a patch is gated at qa and review on the diff, not at plan on a document
(DEC-225). After signature it runs exactly build → validate → ship.
