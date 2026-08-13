# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/2026-08-13-04-eng/state.yaml
- squad: eng
- status: building

**Four of six tasks done, and every team task in this feature is now finished.** T-01 and T-05 at
`1fd6f9a`, T-02 at `4755b6e`, T-03 at `7102d45`. Gates re-run by me at each commit rather than taken
from a digest: unit 0, integration 0, `check-state.sh` 0 with no FEAT-18 finding,
`check-plan-routes.py` 0 violations. **Two rework cycles of ten spent** — T-05's missing unit test,
and one send-back on T-03 for a docstring that documented D-02 while the code implemented T-03, plus
a no-board test block that could not discriminate an abandoned invocation from a completed one.

**Remaining: T-04 and T-06, both `main-session-direct`, both the main session's to execute.** T-04 is
marked `building` in `plan.yaml` and its card is in `Building` — that is live and truthful, not
drift, and **whoever finishes T-04 must mark it `done` before running `close-task`**, because the
parent station is derived from the plan and a status recorded after the subcommand leaves the parent
stuck in `Building` forever.

**LIVE EVIDENCE, measured not predicted, and it is the thing the BRIEF says nothing observes.**
`## Verification gaps` records that no criterion in this feature observes GitHub — every automated
criterion runs against a fake `gh`. I exercised the shipped code against the real board 3 and read
the stations back with `gh_board.board_stations`:

- `close-task T-03` closed #329, wrote no parent station (correct — `derive_station` returns `None`
  with tasks still pending), and #329 landed in `Done` via GitHub's own `Item closed` workflow,
  confirming D-03's measurement that closing is the already-automatic half.
- `start-task T-04` wrote **two** stations in one invocation: #330 to `Building` and parent #326 to
  `Building`, derived from task statuses alone.
- Read back: #326 `Building`, #327/#328/#329/#331 `Done`, #330 `Building`, #332 `Backlog`. Every card
  agrees with the plan.

**THE ONE THING THAT MUST BE SETTLED BEFORE T-06 IS WRITTEN.** D-02's signed text contradicts T-03's
signed intent in two clauses, and **T-06 step 2 inherits both**, so T-06 as signed would write a rule
into `SKILL.md` that the shipped code does not implement. Verified by me against both sources, not
relayed. Details in `## Open Questions`.

## Open Questions

- **Q6 (blocking for T-06 only, not for the build).** D-02 says an absent or incomplete
  `github.board` is an environmental precondition that abandons **the whole invocation**, and that
  "close-task's issue close joins the loud set". T-03 step 4 says the opposite on both: "Do NOT skip
  the whole invocation for it — the issue lifecycle still runs", and "close-task's issue close DOES
  stay on `gh()`, which is today's behaviour". The code follows T-03 and is pinned by T-03's own
  signed test case ("a feature whose `harness.json` carries no `github.board` runs open and
  close-task **unchanged**"). T-03 is also right on the merits: D-02's version would strip issue
  mirroring from every project that has no board, and the parent-before-close ordering is
  load-bearing precisely **because** the close can still terminate the process. So the code is right
  and the record is wrong — but D-02 is a signed decision and correcting it is the operator's, not
  mine. T-06 step 2 repeats both errors verbatim.
- Answered and closed, do not reopen: Q1 and Q3 at signature in `BRIEF.md` `## Approval`; Q2
  overtaken by the 2026-08-13 revision; Q4 settled by the operator with a re-signature at `3862a64`;
  Q5 moot — the advisor is unavailable this session, so judgement calls are made unreviewed and are
  said to be so.
