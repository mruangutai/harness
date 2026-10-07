# The ledger — feature.json is the record of judgement, not a summary of it

Read this on your first cycle, and again before any raise, stop or succession. The playbook
carries the verbs and the seven kinds; this is what each means and why. Evidence and history:
DEC-227, DEC-229, DEC-230, DEC-157.

Every write goes through `feature-record.py`; you never edit `feature.json` by hand.

## Runs

Before every dispatch:
`feature-record.py run-start --file <feature.json> --id <run-id> --squad <squad> --agent <lead> [--by harness-orchestrator --reason <one line> --regate <decision>] [--by harness-orchestrator --reason <one line> --succession continue|downgrade|stop]`.
For lead runs, `<squad>` is the canonical identity: `engineering` for `harness-eng-lead`,
`product` for `harness-product-lead`, and `validator` for `harness-validator-lead`. A mismatched
registration is refused before dispatch; an `eng` label cannot obtain the engineering digest binding.
The open is composed like the close (#1881): `run-start` derives what the new run owes from the
record — a FAIL run it follows owes a `regate`; a handoff note at `seq-N` it succeeds owes a
`succession` — and **refuses** unless you supply the matching decision and reason, in which case the run and
the judgement land in one write. A reason for a judgement the open does not owe is refused too.
You never write those two kinds with `judgement` after the fact; INV-43 grades a late succession
as retrospective forever.
After every return, ONE command:
`feature-record.py close-run --file <feature.json> --id <run-id> --digest <digest.md> --verdict <V> --cycles-used <C> [--task T-NN --station <s>] [--judgement kind=<k>,decision=<d>,reason=<r>] [--code-grade n_a] [--refused-return]`
— in order: the digest is validated against the run's recorded persona; `run-end`; the task
station when `--task`/`--station` are paired; the judgement, recorded as you; `spend`. **The first
refusal stops it, names its stage, and keeps every earlier durable write** — fix what the named
stage refused; never re-issue the later stages by hand (BUG-1723). On success it prints one line
carrying the spend figure, which every return of yours reports. `C` is the non-negative
`cycles_used` the lead DIGEST reports, **never estimated**: run-end writes the run's cycle
attribution and adjusts the feature total so repeating the same report leaves it unchanged.
Tokens are the host's: the hook stamps the measured figure onto the open run on your wake
(BUG-1724) and a bare close-out preserves it; only a run whose entry still carries none may take
`run-end --tokens N` from `details.results[i].tokens`, never an estimate — `null` when unmeasured,
so a reader can tell unmeasured from zero (SC-18).

When the host **refused** the lead's final return, its `digest.md` never received a valid record
and the digest stage can never pass. Close that run with `--refused-return --verdict BLOCKED`: the
digest stage is inverted — it refuses if the digest *does* validate, because then the return
landed and closes normally under its own verdict — and every later stage runs as usual (#2068).
Only this validated close-out creates `return_disposition: refused`; `run-end` has no
`--refused-return` option and can only replay a disposition already recorded. The inverted
stage requests deliberate contract-refusal status 65 from the validator: argument-parser
errors (2), input-read errors and internal failures (1) stop closure rather than providing
refusal evidence. Positional inputs follow `--`, including dash-leading digest filenames.
The closure records that disposition with the terminal BLOCKED entry. INV-15
recognizes only that exact closed run and matching lead; it does not accept the prose as a digest
or turn the refused result into PASS. Ordinary completed runs still require their durable record.
Reapplying that refused closure to an already BLOCKED run preserves its original `ended_at`;
ordinary run-end also preserves that timestamp once refusal is recorded. Neither path can
rewrite the refused terminal verdict or erase its disposition.
Historical refused annotation and replay also preserve the recorded cycle attribution, feature
cycle total, and measured tokens; conflicting explicit accounting is refused without writing.
A prior non-BLOCKED terminal verdict cannot be annotated as refused even when a legacy record
has no timing fields.
Retryable yield refusals retain the same live job's claim until its corrected return is accepted;
host terminal cleanup still releases jobs that actually end without an accepted return.

The `plan` run graded a document and no code: close it with `--code-grade n_a`. Omitting the flag
declares the run reviewed code, and INV-6 then demands a `review_sha` that cannot exist before the
Building → Review seam (BUG-1080). Every other run omits it.

**Three writes are yours and stay separate from close-run:** `STATE.md`'s `## Current` (DEC-150),
the phase handoff note, and the commit.

## Judgements

Every autonomous judgement is one line in `judgements[]`:
`feature-record.py judgement --file <feature.json> --by harness-orchestrator --kind <kind> --decision <text> --reason <one line>`.

| `--kind` | Written when |
|---|---|
| `mission` | you record the grilling's `patch`/`plan` on the first cycle, and again on a SC-03 downgrade |
| `finding_kind` | you, not a reader, settle a finding's `substance`/`form`/`proportionality` |
| `regate` | a FAIL is followed by another run — every `fix` round, every substance re-panel |
| `continue` | you decide to keep going or to stop — `--decision continue` or `--decision stop` — at a budget line, a new finding class, or exhaustion |
| `succession` | your first act on waking as a successor — `continue`, `downgrade` or `stop` — and **no later than your first run** |
| `amendment` | the engineering lead changed a signed task's `intent`, `files` or `verify` inside the same build run (DEC-32/DEC-229) — written FOR you by `plan-merge.py record-amendments`, one entry per changed field, never by hand |
| `reject` | the source ticket was wrong at first-run intake — already fixed, superseded, or refused by a later ruling; `--decision <superseding issue number \| none>`, one run, zero cycles, then `gh-sync.py reject` (FEAT-1714) |

**An amendment's identity is its `decision`: `T-NN.intent`, `T-NN.files` or `T-NN.verify`.**
`record-amendments` writes each entry from the lead's digest (`by: harness-orchestrator`, the
digest's one-line reason) in the same act that splices the text, at a distinct microsecond `at`,
so a field amended twice is two entries the operator can tell apart. **Overruling is by that exact
`at`:** at ship, the operator reads the amendment table in the briefing and, for any departure
they reject, the main session runs `feature-record.py overrule-amendment --file <feature.json>
--at <the entry's at>`; the verb selects the one live amendment at that instant and adds
`overruled: true`, refusing zero matches, two matches, a non-amendment, or a repeat. `overruled`
is ABSENT on an amendment that stands and `true` on one the operator rejected — never `false`,
never on any other kind (the schema refuses both). The operator's trust rate in builder-side
amendments is derived from the ledger, never recorded separately: `overruled / total` over all
`amendment` entries, `0/0` when there were none.

**A judgement not written is a judgement not made.** `check-state.py` INV-40 refuses a `mission`
with no `mission` entry, a FAIL run followed by another with no `regate`, a handoff note with
runs after its `seq-N` and no `succession`, and — on a signed plan — a task whose current
`intent`/`files`/`verify` no longer hash to the `signed_task_hashes` `sign-approval` wrote to
`feature.json` (SHA-256 over canonical JSON of the three fields, DEC-229) with no `amendment`
entry naming that task. The remedy it prints is the route: `plan-merge.py record-amendments
--file <plan.yaml> --digest <engineering-lead digest>`, or restore the signed text. The signed
hashes are never revised by an amendment; that is what lets the gate tell a ledgered departure
from an unrecorded edit. The ledger is the whole basis of the operator's trust: they verify after
the fact, from the reason line, never by ruling in-flight (SC-21).

**The seam has an order (DEC-159, BUG-1723).** The outgoing orchestrator writes the handoff note
BEFORE any run of the later phase exists; the successor appends its `succession` judgement before
or with its first run. INV-43 reports a `succession` whose `at` is later than the `started_at` of
the first run after that handoff's `seq-N` — a retrospective correction — at every station, `done`
included. It grades only successions after harness.json `seam_era_start`; earlier ones report as
notes (DEC-227). An unreadable `at` or `started_at` is CANNOT VERIFY, never a pass.

## Spend

On your wake the harness hook runs `feature-record.py spend` and appends one `SPEND:` advisory
line when the plan phase has run past `budgets.plan_phase_warn_minutes` in
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`, or the **rework window** — every run from
the first `validate-*` onward except feature-close `distill-*` runs, `spend`'s `rework_minutes` —
past the ruling's `rework.wall_clock_minutes`. The ruling is a budget for rework, so plan, build and
distill minutes never count against it. The line names the measured minutes and tokens, the key and the ratio;
the key is named here and the numeral never is. It ADVISES and never refuses (DEC-198): whether you
continue, downgrade or stop is a `continue` judgement, and a handoff belongs at a seam (DEC-201).
If no line arrives there is nothing to weigh.

## The cycle budget

The three lines and their teeth are the playbook's table; this is what counts against them.

**What counts as rework** (DEC-157): a FAIL routed back, an unmet-SC re-dispatch, or a send-back a
lead reports from inside a run. A clean first-pass run adds ZERO cycles. **Continuing a task after
an eligible amendment is the same run, not a cycle**: no gate failed and nothing was routed
back — the lead corrected the task's HOW and the owning specialist carried on; `record-amendments`
is transcription, and `cycles_used` does not move for it. Counting forward runs
instead is how a healthy feature goes BLOCKED with nothing wrong. The defaults are
`budgets.max_total_cycles` and `budgets.max_total_runs` in harness.json, never a figure in prose.
A main-session-direct segment is not a run and never appears in `runs:`.

**A raise is a recorded decision** —
`feature-record.py raise-cycles --file <feature.json> --to N --decision <path>` — the path an
existing file under the feature directory, or the verb refuses — writes the bound
and the `budget_decisions[]` record together, and INV-39 refuses a bound above the default with no
record of the current value. A ceiling that moves when reached is not one.
