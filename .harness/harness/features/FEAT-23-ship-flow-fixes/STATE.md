# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: .harness/harness/features/FEAT-23-ship-flow-fixes/runs/2026-08-17-5-foldin2-product/state.yaml
- squad: product
- status: awaiting-user

Mission `plan`, resumed after a 529 killed the predecessor. **Complete — the plan is signature-ready.**
Scope is THREE tickets, all absorbed: #417 (`ship`/`abandon` leave `feature.json` pre-terminal),
#430 (the four-angle simplify pass becomes a standing harness-native build and plan step), #453 (the
board never shows `Plan`). Plan is 6 tasks, 5 decisions, 10 lane rows; BRIEF is 9 REQs and 13 SCs.
Both approval blocks read `pending`; only the operator signs.

#453 took option (a) narrowed, recorded as D-05 → DEC-196: the tree's real boundary is **move any
card it is pointed at, close only cards it created**, so option (b) as worded is falsified by
`gh-sync.py:631`. It adds T-05 (`board-station.py` + test) and T-06 (a `/harness-plan` kickoff step).

Both plan-flow reviews PASSED. Two eng-lead architecture passes ran concurrently, both digests real
(`runs/2026-08-17-2-archreview-eng/digest.md`, findings A–K, and its sibling
`digest-eng-lead-arch-b.md`, MF-1..MF-3 and A-01..A-07). The ui-reviewer cleared the design contract
by measured census, scoping IN on 2 of 10 surfaces. **19 of 20 findings are folded** across two
fold-in runs. **The exception is arch finding G**, which the reviewer itself routed as the
operator's call rather than a fix: D-05's `because:` and DEC-196's prescribed body both name "a
second board-writing entry point, and one more call site", but neither names the duplicated
`load_config` github-block precondition policy nor `gh_board.py` as its eventual home.

Verified at HEAD `b7ae135` by this orchestrator, independently of every squad: all six `verify:`
clauses execute and exit 1 with distinct discriminating messages; T-02's new dispatch-discipline
conjunct is TWO-WAY proved — green on a complete fixture, red on a paraphrase, red on a case-flip —
and its grep literal is byte-identical to the literal its intent pins; 19 of the 20 findings are
present by content grep and G is absent; `--kind unit` exits 0 in 2.5s; case_20 is real and sits in
`INTEGRATION_SCRIPTS`; `cmd_abandon`'s guard is a conjunction while `cmd_ship`'s is not;
`github.attached` is array-of-string; no DEC-174 file is touched.

Next: the operator signs BRIEF + PLAN as one, then the build phase begins. See
`notes/handoff-plan.md`.

## Open Questions

- Harness defect, the significant one: **lead spawns are intermittently provisioned without the
  `Agent` tool their agent files grant.** Both review leads and three `harness-product-lead` spawns
  hit it. It is intermittent, not absent — the same dispatch succeeded on retry, and all work
  eventually landed.
- Harness defect: **lead returns went false about the disk four times.** `3-revise`, `4-revise` and
  `5-revise` report that pm never ran, and the ui run returned BLOCKED, while the work had in fact
  landed. A successor trusting a return over disk would redo completed work. The cause is named in
  `runs/2026-08-17-5-foldin2-product/digest.md` Q3: `validate-digest.py --hook` fires on a lead's
  turn-end while its dispatched member is still in flight and extracts a premature verdict.
- **CORRECTION, this orchestrator's own error — NOT a harness defect.** An earlier entry here
  recorded "two orchestrator contexts ran this feature concurrently" as a defect. The truth: this
  orchestrator accidentally spawned a `fork` subagent with a placeholder prompt while trying to
  redirect a running agent. A `fork` inherits the parent's full context, so it acted as a second
  orchestrator and duplicated the whole phase — that is why `feature.json` was overwritten
  repeatedly and why a second `STATE.md` account appeared. The tooling behaved as documented. It did
  net good (it preserved the first product lead's digest at
  `runs/2026-08-17-1-product/digest-first-return.md`, which a duplicate lead had overwritten, and it
  caught finding G), but it was unintended and roughly doubled this phase's spend.
- Non-blocking, raised by pm: `bash-write-guard.sh` denies writes to the session scratchpad the
  harness itself designates for temp files.
- Non-blocking, raised by the ui reviewer: how is "the operator names the ticket" recognised during a
  live `/harness-plan` session? No seat owns dialog semantics.
- Backlog: #350 is CLOSED carrying two unimplemented rulings with no open implementing ticket.
- Backlog: the two accepted costs in DEC-196 — a second board-writing entry point, and a fourth
  copy of the root probe with no importable `harness_root()`.
