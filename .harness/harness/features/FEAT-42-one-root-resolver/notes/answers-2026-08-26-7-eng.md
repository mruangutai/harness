# Answers — 2026-08-26-7-eng — FEAT-42

Written by harness-orchestrator, 2026-08-27, in reply to the questions raised from inside the
engineering run. Every answer here is my own measurement or my own execution-time ruling. None of
it is the operator's; where a question needs the operator, I say so and it travels up in my return.

## A1 — the baseline is not self-contradictory. Both numbers are mine and both turn on ONE variable.

The two statements describe the SAME suite under TWO states of `.harness/.inflight-claims.json`.

- **Registry empty.** `run-unit-tests.sh --kind all` at a1658c2: `SUITE_EXIT=0`, **zero** `FAIL`
  lines, 1013 result lines, 57 script verdicts. `test-validate-digest.py` reports `PASS` at output
  line 1482. I started that run with `cat .harness/.inflight-claims.json` showing `{}`, and the run
  reached `test-validate-digest.py` before my dispatch placed any claim.
- **Registry non-empty.** I wrote two claims through `inflight_registry.claim()` and re-ran
  `test-validate-digest.py` alone: exit 1, exactly **6** `FAIL  [hook]` lines. I then removed both
  claims with targeted per-agent releases and diffed the file byte-identical against a backup.

So the 6 failures are caused by a live claim, not by the tree. A suite run while an agent is in
flight carries them; a suite run with an empty registry does not. Nothing at HEAD is red.

**How to use this.** Any failure that is NOT one of those 6 `[hook]` cases is real. Record the
registry state at the moment a run starts and report it beside the result. Never clear the registry
to obtain a green — that destroys other agents' claims.

## A2 — CORRECTED. T-06's verify CAN reach green. My first answer here was wrong and I am replacing it.

**What I first wrote, and why it was wrong.** I accepted V-7's finding that T-06 reds both
`test-dispatch-guard.py:168` and `:170`, and I ruled that T-06 should proceed with a permanently red
verify. V-9 then showed V-7 was mistaken. I have re-derived V-9 myself rather than relaying it, and
V-9 is right:

- `inflight_registry.py:251` — `def refusal_lines(agent, existing, release_cmd)`. The function does
  not choose the command; it receives it.
- The only production caller is `dispatch-guard.sh:115`, which passes `reg.RELEASE_ALL_CMD`.
- T-06's `files:` are exactly `inflight_registry.py` and `test-inflight-registry.py`.
  `dispatch-guard.sh` is untouched by T-06 and is on this run's LEAVE list.

So after T-06 the refusal still prints `RELEASE_ALL_CMD`'s value and **`:168` stays GREEN**. Item
5's "never what a refusal prints" describes the end state after T-18, which owns the swap — T-18's
own verify greps `dispatch-guard.sh` for the constant and fails on any hit. The only assertion T-06
breaks is `:170`, and V-1's two-line citation split greens it while satisfying T-06's own `#551`
and `#628` grep clauses.

**The ruling that follows.** Implement T-06 in full and expect a GREEN verify. Specifically:

- Delete `CLI_REL_PATH`. Add `release_cmd(root, agent)`.
- **Keep `RELEASE_ALL_CMD` as a plain module literal**, and **keep `refusal_lines`' three-parameter
  signature.** V-9's warning is the sharpest thing in this file: a member that "helpfully" drops the
  third parameter and builds the command inside the function makes `dispatch-guard.sh:115` pass
  three arguments to a two-argument function. That `TypeError` is swallowed by the broad
  `except Exception` at `:124`, which prints "passing through, the dispatch is NOT blocked" and
  exits 0 — the single-flight guard fails OPEN, by a different route than the one V-2 found.
- Apply item 6's citation move with the split. Capture the verbatim `FAIL` for `:170` as red proof
  before the split lands.
- Do NOT edit `test-dispatch-guard.py` under any circumstance. If a green needs that file, stop and
  report instead.

The plan-ordering concern in V-1 is now advisory, not blocking, and I carry it up as such: the
sequencing is tight enough that one careless refactor turns it into a real inversion.

**Why this correction is stated instead of quietly replaced.** I restated a subordinate's finding in
my own voice and it became my ruling one step later. That is the exact failure my own notes warn
about — restating launders a report into a fact. The finding was decidable by reading two lines, and
I should have read them before ruling, not after.

## A3 — the freeze extends to every fixture in the three named files, including the site I did not name.

`test-check-state.py:2479-2488` is frozen on the same ground as `:2552-2577`. I named one site; the
rule was always the file. The freeze covers `test-check-state.py`, `test-post-merge-sweep.py` and
`test-worktree-terminal.py` entirely: **no fixture change, no assertion change, no env change.**
Those three are tests of the harness's own gate scripts and hooks, and under DEC-174 the harness
does not execute changes to them through the enforcement path being changed.

**Prose reword in those three files remains REQUIRED, not merely permitted.** T-04's first verify
clause greps the whole directory for the bare name and reds before any test runs. Reword the prose,
change nothing executable. That distinction is the whole of what is allowed there.

## A4 — `test-feature-worktree.py`: prose reword only. Do not change its fixture.

I previously left this to the member's judgement. I am narrowing it, because the argument I used was
wrong. I reasoned that `feature-worktree.py` is not a hook or a gate, so its test is not DEC-174
material. But widening a task beyond its approved `files:` to make a BEHAVIOURAL change is a plan
amendment, and plan amendments are pm's under the operator's approval — not mine and not the
member's. The prose sweep is defensible because T-04's intent states directory-wide removal in its
own words and the verify enforces it; a fixture rewrite has no such warrant.

If its redirect breaks, that is a finding to report, with the case named. It is not a thing to fix
inside this run.

## A5 — on the relay problem itself

The observation is correct and the failure was mine, not the lead's. I hold `Read, Glob, Grep,
Agent, Write, Bash` and no `SendMessage`, so there is no channel to a running member; my own attempt
to correct one spawned a second lead instead. Writing the correction to `correction-t04.md` and
binding it at assessment and at the next dispatch was the right recovery, and it is the pattern to
use again: **a correction that cannot be delivered becomes a file the assessor must read.**

No verdict may be asserted over a member still running. Refusing to give one was correct.
