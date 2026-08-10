# Handoff — build phase — FEAT-10-software-factory

RECONSTRUCTED AT FEATURE CLOSE by the ship-phase orchestrator from the run digests. The build
predecessors wrote none, so that working memory WAS lost and every successor ran the disk-only
path DEC-159 supports. This records the crossing; it is not contemporaneous.

## Next

The ship decision — the operator's acceptance. Build is closed: all 12 T-NN carry a PASS run in
`feature.yaml`. It was re-entered ONCE after validate, for A1 alone, and that segment returned
PASS. Nothing in `plan.yaml` remains to build.

## Trust

- 12 of 12 tasks DONE; T-01 and T-08 landed main-session-direct under DEC-179 and the DEC-174
  carve-out — `feature.yaml` `tasks:` — verified-at b86565b
- Three build waves, eleven tasks, ZERO send-backs — `runs/w1-eng`, `w2-eng`, `w3-eng` digests —
  verified-at b86565b
- `run-unit-tests.sh` exit 0, 22 test files PASS, 0 FAIL — re-run by me — verified-at b86565b
- Every factory module has its own test file registered in `run-unit-tests.sh` —
  `runs/w3-eng/digest.md` — verified-at b86565b
- The suite is green against SCRIPTED RECORDERS, never against GitHub; no build run made a live
  `gh` call — `runs/qa2-validator/digest.md` — verified-at b86565b
- TEST-FIRST IS UNVERIFIABLE for every task: nothing was committed during the build, so git history
  proves nothing. 7 of 8 receipts self-report a named RED traceback; T-12's does not —
  `runs/qa-validator/digest.md` — UNVERIFIED
- `factory_land.py:77` still fails open on `gh pr create`, and no tool's `expected` tuple carries
  `YamlParseError` — both re-read by me — verified-at b86565b

## Dead ends

- Do not patch `factory_land.py:77`'s predicate in place — a `create_pull_request` helper behind
  `factory_gh` throws that patch away and closes the predicate divergence with it —
  `runs/qa-validator/digest.md`
- Do not add `YamlParseError` to five `expected` tuples — the fix is two raw call sites —
  `runs/panel-validator/digest.md`
- Do not re-add a live-API criterion — ruled under #194's one-in-flight cap —
  `notes/answers-plan-review.md`
- Do not carry a severity word into a reviewer dispatch — panel1 anchored its own panel and
  disclosed it — `runs/panel-validator/digest.md`
- Do not route `.claude/skills/harness/bin/**` by domain grant — backend-dev and dev-ops both hold
  it, so only `consult-when` discriminates — `runs/w2-eng/digest.md`

## Working set

- `.harness/features/FEAT-10-software-factory/feature.yaml`
- `.harness/features/FEAT-10-software-factory/STATE.md`
- `.harness/features/FEAT-10-software-factory/runs/w3-eng/digest.md`
- `.harness/features/FEAT-10-software-factory/runs/a1fix-eng/digest.md`
- `.claude/skills/harness/bin/factory_decompose.py`
