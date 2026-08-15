# Handoff — FEAT-09, validate → blocked on a user decision — written at 4918d06, seq-4

## Next

**Apply VF-1, then resume.** One line plus one test case on `check-domain.sh`, specified in full at
`notes/vf1-guard-bypass.md`; the panel's record is `runs/panel-validator/digest.md`. It is
**main-session-direct**: DEC-174 forbids dispatching a change to `check-domain.sh` through a team
run whose gates are the thing being changed, and the domain hook blocks the orchestrator from
writing it. No agent in this feature may do it.

After the fix lands, in this order:

1. Re-run `run-unit-tests.sh` (13 scripts) and `test-check-domain.py`.
2. **Re-pin `review_sha`** — the fix lands a new source commit, so the current pin `4918d06` goes
   stale the moment it does. One pin, taken after.
3. A DELTA review of the fix — ask the user whether a one-line change warrants the full four-wide
   panel again, rather than deciding it yourself.
4. pm goal-check on all 12 SCs. 5. Distillation. 6. CEO briefing.

## Trust

- VF-1 is REPRODUCED, not relayed. Same payload FILE three times, documentor writing `bin/`:
  clean env exits 2; `HARNESS_RESOLVE_PATH` set exits 0; empty string also exits 0 — my own
  probe — verified-at 4918d06
- SC-04 is FALSE AS WRITTEN, not under-tested. `BRIEF.md:48-49` states it in argv terms and the
  code never branches on argv — verified-at 4918d06
- The manifest DOES grant `check-domain.sh` to backend-dev and dev-ops; the block is DEC-174
  policy plus my own domain, not the manifest — `--resolve` run by me — verified-at 4918d06
- T-02 is green on its own terms: 17 distinct cases, suite 13/13, FEAT-09's own PLAN at zero
  violations and exactly one DEVIATION naming T-01 — my own re-run — verified-at ae28daf
- The SCRIPTS array hazard did NOT fire: the diff is one added element, 12 to 13, and
  `test-cost-report.py` appears nowhere — verified-at 4918d06
- `cycles_used: 2` was incremented PRE-EMPTIVELY for a fix cycle nobody has dispatched yet. Do
  not count it twice when re-delegating — my own bookkeeping — verified-at 4918d06

## Dead ends

- Do NOT restructure `--resolve` to branch on argv. `check-domain.sh:105` already consumes
  `sys.argv[2]` as `argv_agent`, so it touches the hook path's identity contract on a DEC-174
  file and drifts from the mechanism DEC-179 documents — panel finding — verified-at 4918d06
- Do NOT re-probe the hook with an inline escaped-quote payload: it yields a false exit 0 that
  looks like a regression. Build payload FILES — verified-at 4918d06
- Do NOT resume the cost reconciliation and write NO cost line; say once that the harness no
  longer meters spend (DEC-178) — verified-at 4918d06
- Do NOT treat the `:190-197` anchor in the new source comments as a builder defect —
  `PLAN.md:210` carries the same wrong anchor, so the approved plan is the origin — 4918d06
- Do NOT re-run the goal-check before the fix: SC-04 is known false and the fix touches the
  evidence path of SC-04, SC-08 and REQ-04, so every verdict is re-taken anyway
- Do NOT use base `ae2443d`. It still RESOLVES, returning 71 files against a true 14 — silent,
  not an error. Base is `47ed11f` — verified-at 4918d06

## Working set

- `notes/vf1-guard-bypass.md` — the blocking finding, in full
- `feature.yaml` — pin, gates, backlog
- `runs/panel-validator/digest.md` — the panel's own record
- `BRIEF.md` — the 12 SCs
