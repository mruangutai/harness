# The ledger — feature.json is the record of judgement, not a summary of it

Read this on your first cycle, and again before any raise, stop or succession. The playbook
carries the verbs and the five kinds; this is what each means and why. Evidence and history:
DEC-227, DEC-230, DEC-157.

Every write goes through `feature-record.py`; you never edit `feature.json` by hand.

## Runs

Before every dispatch:
`feature-record.py run-start --file <feature.json> --id <run-id> --squad <squad> --agent <lead>`.
After every return: `run-end --file <feature.json> --id <run-id> --verdict <V> [--tokens N]`, where
`N` is `details.results[<i>].tokens` from the `task` tool result when it is present — blocking
dispatches carry it — and omitted otherwise. **Never estimated**: the tool writes `null` for a run
you did not measure, so a reader can tell unmeasured from zero (SC-18). Every return of yours
carries the feature-level sum from `feature-record.py spend --file <feature.json>`.

The `plan` run graded a document and no code: close it with `run-end --code-grade n_a`. Omitting
the flag declares the run reviewed code, and INV-6 then demands a `review_sha` that cannot exist
before the Building → Review seam (BUG-1080). Every other run omits it.

## Judgements

Every autonomous judgement is one line in `judgements[]`:
`feature-record.py judgement --file <feature.json> --by harness-orchestrator --kind <kind> --decision <text> --reason <one line>`.

| `--kind` | Written when |
|---|---|
| `mission` | you record the grilling's `patch`/`plan` on the first cycle, and again on a SC-03 downgrade |
| `finding_kind` | you, not a reader, settle a finding's `substance`/`form`/`proportionality` |
| `regate` | a FAIL is followed by another run — every `fix` round, every substance re-panel |
| `continue` | you decide to keep going or to stop — `--decision continue` or `--decision stop` — at a budget line, a new finding class, or exhaustion |
| `succession` | your first act on waking as a successor — `continue`, `downgrade` or `stop` |

**A judgement not written is a judgement not made.** `check-state.sh` INV-40 refuses a `mission`
with no `mission` entry, a FAIL run followed by another with no `regate`, and a handoff note with
runs after its `seq-N` and no `succession`. The ledger is the whole basis of the operator's trust:
they verify after the fact, from the reason line, never by ruling in-flight (SC-21).

## Spend

On your wake the harness hook runs `feature-record.py spend` and appends one `SPEND:` advisory
line when the plan phase has run past `budgets.plan_phase_warn_minutes` in
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`, or the **rework window** — every run from
the first `validate-*` onward, `spend`'s `rework_minutes` — past the ruling's
`rework.wall_clock_minutes`. The ruling is a budget for rework, so plan and build minutes never
count against it. The line names the measured minutes and tokens, the key and the ratio;
the key is named here and the numeral never is. It ADVISES and never refuses (DEC-198): whether you
continue, downgrade or stop is a `continue` judgement, and a handoff belongs at a seam (DEC-201).
If no line arrives there is nothing to weigh.

## The cycle budget

| | Teeth | On crossing |
|---|---|---|
| `cycles_used` / `max_total_cycles` | **HARD** — kills runaway fix loops; `check-state.sh` INV-39 enforces the bound | stop the branch, preserve everything, `status: blocked`, return `BLOCKED`. Never silently continue |
| `rework.rounds` / `rework.wall_clock_minutes` | **THE RULING** — the operator's one answer to "how much rework", given at signature | a `continue` judgement with `--decision stop`, then return with the unmet findings named |
| `len(runs)` / `max_total_runs` | **INFORMATIONAL** — notices a long feature, never stops one | INV-22 emits a NOTE. Keep going; a high count is not a defect |

**What counts as rework** (DEC-157): a FAIL routed back, an unmet-SC re-dispatch, or a send-back a
lead reports from inside a run. A clean first-pass run adds ZERO cycles. Counting forward runs
instead is how a healthy feature goes BLOCKED with nothing wrong. The defaults are
`budgets.max_total_cycles` and `budgets.max_total_runs` in harness.json, never a figure in prose.
A main-session-direct segment is not a run and never appears in `runs:`.

**A raise is a recorded decision** —
`feature-record.py raise-cycles --file <feature.json> --to N --decision <path>` — the path an
existing file under the feature directory, or the verb refuses — writes the bound
and the `budget_decisions[]` record together, and INV-39 refuses a bound above the default with no
record of the current value. A ceiling that moves when reached is not one.

**Surface a crossing where a human sees it**, not only at `/harness` entry, which is retrospective.
When `len(runs)` passes `max_total_runs`, say so in your return and in the CEO briefing: the count,
the budget, and your one-line read on whether the runs still earn their place. Never as an apology.
