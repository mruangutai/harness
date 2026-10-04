# Grilling — a reject verb: an orchestrator returns "superseded by #N" at cycle 0 instead of planning the wrong ticket (#1714) — 2026-09-15

## Destination
An orchestrator in a `plan` or `patch` mission that finds, on reading the source ticket, that it is
superseded or should not be planned can say so in one run: a recognised digest shape, a `reject`
judgement naming the superseding issue, the feature at a terminal `rejected` station with provenance
kept, the GitHub parent closed not-planned with the link — and zero cycles consumed, no panel, no
product run.

## Mission
mission: plan
reason: new schema surface on three gates (a digest verdict shape in validate-digest.py, a judgement kind, a plan station and INV trigger in check-state.py) plus a gh-sync path — fails rule 3 of the patch test; cause and files are known.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do all of them from plan (or patch) to ship")

## Settled
- Who judges → the orchestrator, at the start of its first run, before any lead is dispatched. The
  judgement is recorded like every other (DEC-230); the operator overrules from the return. This
  ticket gives the judgement a verb; it does not decide whether a ticket is wrong.
- Where the verdict lives → the orchestrator digest gains a `kind: reject` judgement entry with
  `superseded_by: <issue>` or `superseded_by: none` plus a one-line reason; the return `status` is
  `rejected`. `validate-digest.py` recognises it as terminal; it is not a `PASS` with prose.
- Judgement kind → `reject` joins `JUDGEMENT_KINDS` (`feature-record.py:59`). With #1716's
  `amendment` the enum becomes seven; whichever lands second amends DEC-230's count.
- Station → `rejected` joins `plan.yaml`'s station vocabulary (`backlog plan ready building review
  done abandoned`, `harness/SKILL.md:102`); `plan-merge.py set-feature-station --station rejected`
  writes it. It is terminal: `check-state.py` INV-29 treats it like `done`/`abandoned` (worktree
  must be removed).
- Record → a rejected feature keeps `source_issues` as provenance (#1683 ruling: provenance is not
  rewritten), keeps its BRIEF if one was drafted, and has no signature. `feature.json` carries the
  `reject` judgement and `runs` holds exactly the one orchestrator-owned run.
- GitHub mirror → `gh-sync.py reject <feature-dir> --superseded-by <n> --reason-file <path>`:
  closes the parent `not_planned` with a comment linking the superseding issue, labels it
  `superseded`, returns its card to backlog (the `_close_and_reseat` order from `cmd_abandon`),
  closes the milestone if one exists, and touches no sub-issues (a reject happens before `open`
  creates any). Report-and-ask like `abandon`: without `--yes` it prints and makes no write.
- Cost → INV: a feature at `rejected` has `cycles_used: 0` and no run whose agent is a lead. A
  reject that dispatched a panel is a violation.
- Build execution → `validate-digest.py`, `check-state.py`, `feature-record.py`, `plan-merge.py`
  are DEC-174 carve-out → `main-session-direct`. `gh-sync.py` is dispatchable (not a gate). Prose:
  DEC-230, `harness/SKILL.md`, `harness-handoff`, `templates/plan.yaml` station comment.

## Not yet specified
- none

## Out of scope
- Rejecting mid-build (a task found wrong after signature) — that is #1716's amendment or a
  DEC-32 ask.
- Auto-planning the superseding issue; the return names it, the operator decides.
- Retroactively marking BUG-285-yaml-loader-pin `rejected`; its record stays as committed.

## Facts I verified (so pm does not re-derive them)
- BUG-285: #285 was superseded by #1594 in writing on 2026-09-10; the pre-FEAT-59 plan ran 7 amend
  cycles (#1684). The post-FEAT-59 replan's first judgement (`feature.json` judgements[0], kind
  `mission`) reads "issue comment points to superseding canonical-reader scope in #1594" — the
  closest existing shape to a reject.
- `JUDGEMENT_KINDS` at `feature-record.py:59`; INV-40 at `check-state.py:2869-3000`.
- Station vocabulary at `harness/SKILL.md:100-103`; `set-feature-station` is the verb.
- `gh-sync.py cmd_abandon` (`:1676-1770`) is the model: report-and-ask, close `not_planned` first,
  reseat card to backlog after, label; `_abandon_plan` renders both paths.
- `validate-digest.py` orchestrator persona at `:394`; terminal statuses are enumerated in its
  SCHEMAS.
- Base: `origin/main` at 82c9d074.
