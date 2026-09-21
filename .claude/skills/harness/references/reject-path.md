# The reject path — the source ticket was wrong

Read this on the first cycle of a `plan` or `patch` mission, when the ticket you inspected before
any dispatch is wrong. The playbook carries the rule; this is the procedure and the return shape.
Evidence and history: FEAT-1714, INV-44.

The ticket is the one the grilling artifact names (mirrored as `plan.yaml`'s `source_issues` once a
plan exists); read it and its comments. It is wrong when it is already fixed, superseded by another
issue, or asks for what a later ruling refused. The honest return is `rejected`, at the cost of this
one run and zero cycles. This path never applies once build has begun, and a signed plan is never
rejected — that is `abandoned`.

## The procedure

1. **The record needs a plan to hold its station.** When no `plan.yaml` exists yet, write the
   station-only one — `schema: plan/1`, `feature:`, `status: plan`, `station_only: true`,
   `source_issues: [<ticket>]`, `tasks: []` — never a task.
2. **Record the judgement:**
   `feature-record.py judgement --file <feature.json> --by harness-orchestrator --kind reject --decision <superseding issue number | none> --reason "<one line>"`.
3. **Close your one run** (playbook step 6).
4. **Run `gh-sync.py reject <feature-dir> --superseded-by <n | none> --reason-file <path>`.** It
   reports and asks first, and executes exactly the list it printed. Nothing harness-created exists
   on GitHub yet (the parent is `open`'s, at build entry), so its disposition is the reason posted
   on each source ticket and that card returned to backlog — the ticket is never closed or
   labelled; the harness closes only cards it created. On a record that already carries a parent
   (a reject after build entry never applies, but the verb is one) it closes that parent
   `not_planned` with the comment, labels it `superseded` for a numeric successor, reseats it, and
   closes the milestone.
   - With `--yes` and a **superseding issue number** it **writes the plan station `rejected`
     itself as its last mutation, only after every GitHub write landed — do not also call
     `set-feature-station`**.
   - With `--yes` and **`none`** (the ticket should not be planned at all) it leaves the station
     to you: **only after it exits 0**, write `rejected` once with
     `plan-merge.py set-feature-station`.
   - A failed GitHub write exits 1 naming what landed and what did not, and no station is written
     on either path — fix the named step and re-run.
5. **Return `status: rejected`** with the digest's one inline
   `judgement: { kind: reject, superseded_by: <n | none>, reason: "<one line>" }`, `runs` holding
   only that run, `cycles_used: 0` and `briefing: none`. The validator refuses any other shape, and
   INV-44 grades the record: one orchestrator run, zero cycles, a reject judgement, nothing signed,
   no panel.

The operator overrules from that return; you never auto-plan the successor.
