# Goal-check — BUG-1306, validate phase, pin `da05ea28`

## BLUF

**All five criteria MET.** SC-01/02/03 re-measured first-hand this run (two direct invocations,
~8.6s each, both exit 0, zero `^FAIL` lines). SC-04/05 graded by inspection at the pin; SC-04's
"near lines 305/309" parenthetical is **stale documentation, not a criterion failure** — the
substance (single module-import removal, lexically before every case body and both raw `Popen`
sites) holds at 41 < 165 < 315 < 319. REQ-01..03 all satisfied. One **emergent** criterion is
reported, not adopted: nothing standing keeps the pop honest (below).

## Per-criterion grades

| SC | verdict | method | evidence | provenance |
|---|---|---|---|---|
| SC-01 | **met** | automated | `HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py` → **exit 0, 0 `^FAIL` lines** (run under `pipefail`, from worktree root, ambient shell `HARNESS_AGENT_TYPE=harness-pm` overridden per-invocation, never unset) | measured-this-run |
| SC-02 | **met** | automated | same run's stdout contains, each checked separately: `PASS  a governed agent's sign-approval exits 10` — **present**; `PASS  the signature actually lands` — **present** | measured-this-run |
| SC-03 | **met** | automated | `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py` → **exit 0, 0 `^FAIL` lines** | measured-this-run |
| SC-04 | **met** (with a stale anchor, ruled below) | inspection | at `git show da05ea28:tests/integration/test-plan-merge.py`: pop at **:41**, the ONLY line matching `^os\.environ` in the file; first `def case_*` at **:165**; the two `subprocess.Popen` sites at **:315** and **:319** | measured-this-run (re-derived independently); corroborated cited-from `notes/review-harness-code-reviewer-c0.md:18-28` |
| SC-05 | **met** | inspection | `git diff --name-only $(git merge-base main da05ea28) da05ea28` returns 17 paths: `tests/integration/test-plan-merge.py` plus 16 under `.harness/harness/features/BUG-1306-agent-type-hermetic-tests/` (BRIEF.md, STATE.md, feature.json, plan.yaml, 9 `notes/*`, 2 `observations/*`). (a) **no** path under `.claude/skills/harness/bin/` or `.agents/skills/harness/bin/` — checked by name over the full list; (b) **no** second test file — `tests/` contributes exactly one path | measured-this-run; list matches cited-from `review-harness-code-reviewer-c0.md:41-57` verbatim |

## SC-04 — ruling on the line-anchor discrepancy

**Substance holds; the parenthetical is a drifted documentation anchor, not a failure.** SC-04's
binding clause is *"the removal … happens once at module import — before any case body and before
the two raw `Popen` call sites … so a future case written with a raw `subprocess.run` is covered
with no per-site edit."* Every conjunct is true at the pin: one statement, module scope (`:41`,
sole `^os\.environ` match), lexically before `:165` and before `:315`/`:319`. The `Popen` numbers
are inside a parenthetical whose grammatical job is to *locate* the sites, not to constrain them;
the +10 shift is caused by the fix's own 8-line insertion plus the 2-line net docstring growth,
both textually above the Popens — i.e. the criterion's own subject moved its own anchor.

**What should happen to the stale numbers:** nothing here. BRIEF is approval-gated and read-only to
this run, and rewording a criterion so it reads cleanly after the fact is deciding the verdict
first. Record it as a **ship-briefing note to the operator**: "SC-04 says 305/309; at
`review_sha` they are 315/319 — order unaffected." If the operator wants the text corrected, that
is a one-line BRIEF amendment under their signature, post-ship. It gates nothing. This is the same
item the code reviewer filed as `F-INFO-01` (severity `info`), and I concur with that severity.

## REQ coverage

- **REQ-01** (same verdict governed vs clean) — satisfied, by SC-01 ∧ SC-03 measured back to back
  this run: both exit 0 / 0 FAIL.
- **REQ-02** (#1103 refusal still proven) — satisfied by SC-02's two literal PASS lines, present in
  the governed run. Byte-identity of both `case_1103_*` bodies to the pre-fix file is
  cited-from `review-harness-code-reviewer-c0.md:98-112` (hunk-range analysis + region diff); I did
  not re-derive it, and SC-02's live PASS lines are the stronger evidence anyway.
- **REQ-03** (production guard unweakened, no other test file altered) — satisfied by SC-05's path
  list: `plan-merge.py` absent from the diff, exactly one test file present.

## Could the bug return unnoticed?

**Yes — and this is the one real gap.** SC-01 is a *manual* invocation. CI
(`.github/workflows/tests.yml` → `run-unit-tests.sh`) runs with no `HARNESS_AGENT_TYPE` set, so a
future edit deleting line 41 keeps CI green and reddens only for a governed agent — exactly the
pre-fix condition this bug describes. qa's governed full-kind runner sweep
(cited-from `notes/review-harness-qa-c0.md:61-79`) was a one-off measurement, not a standing gate.

## Emergent criterion — reported, NOT adopted

- **E-01: no standing gate exercises the suite under a governed ambient identity, so the pop's
  deletion is invisible.** Judged new against BRIEF's own `## Verification gaps`: gap 1 says a
  runner-level green does not *prove* hermeticity; gap 2 covers *future `bin/` readers*. Neither
  states that *this fix's own regression* has no automated guard. **Recommendation:** a separate
  dev-ops ticket to add one governed-identity leg to the integration CI job
  (`HARNESS_AGENT_TYPE=harness-orchestrator`), not scope for BUG-1306 — the Advisor ruling in
  `## Constraints` confines this feature to the one test file. Operator's call.

## Housekeeping

No source, test, BRIEF, or plan file touched; no commit; HEAD never moved; no GitHub call. Only
this note written. Commands run: the two direct invocations above plus `git show` / `git diff` /
`git merge-base` reads.
