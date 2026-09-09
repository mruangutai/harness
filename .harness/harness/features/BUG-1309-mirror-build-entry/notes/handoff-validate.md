# Handoff — BUG-1309-mirror-build-entry, validate → ship decision — written at b5eb8f8e, seq-1

## Next

Return SC-04's three evidence gaps to the operator and do NOT dispatch anything until they rule.
The parser remediation itself is graded clean at the pin; what is unresolved is whether SC-04 may be
signed off on inspected-correct behaviour with three of its ten clauses carried by no automated
case (`notes/research-BUG-1309-goalcheck-c17.md` "SC-04 — UNMET", gaps A/B/C). The operator's three
options, in the goal-check's own words: record a ruling accepting the gaps; carry them as a
follow-up bug; or authorise ONE additive test-only cycle on `tests/integration/test-merge-gate.py`
(which would take `cycles_used` to 16 of 16, the cap). Only after that ruling does the UAT Step 3b
amendment (one pm spawn, product lead) and then the operator's SC-10 hand test become the next
action. No fix is dispatchable inside this budget.

## Trust

- The parser fix is committed at `94b5e465`; the panel and the goal-check both graded that commit — `feature.json` runs c17 — verified-at 94b5e465
- `review_sha` was pinned to `94b5e465` before any validator ran, then moved to `b5eb8f8e` after the
  record commit for INV-33; the code diff between them is EMPTY — `git diff --name-only 94b5e465..b5eb8f8e -- ':!<feature-dir>'` — verified-at b5eb8f8e
- T-05 reads `status: done`, feature station reads `review`; the T-05 write was the main session's
  (main-session-direct), the feature station write mine — `plan.yaml:24`, `plan.yaml` T-05 — verified-at 94b5e465
- GitHub mirror is at review: parent #1407 and all nine sub-issues — `gh-sync.py status … review` output — verified-at 94b5e465
- Panel c17 PASS, `severity_max: low`, `must_fix: []`, `matrix_ok: true`, 0 send-backs — `runs/c17-validator/digest.md` — verified-at 94b5e465
- SC-11 MET; its three case names pass individually and each reddens at `e374c9a2` — `notes/qa-c17.md:50-63` — verified-at 94b5e465
- SC-04 gap C is real: the two "noise" cases use byte-identical `json.dump([])` fixtures, so only the
  non-object kind of four is exercised — `git show 94b5e465:tests/integration/test-merge-gate.py:128-135,163-170` — verified-at 94b5e465
- SC-04 gap B is real: neither duplicate claimant is in `BUILD_ENTRY_ERA_EXEMPT` (0 matches) — `feature_schema.py:226` — verified-at 94b5e465
- SC-04 gap A is real: no single-owner receipt deny asserts the feature id; `:65` asserts the state,
  `:67` the command, and the id assertion at `:126-127` is the fail-closed deny — verified-at 94b5e465

## Dead ends

- pm's rationale for gap B says `BUILD_ENTRY_ERA_EXEMPT` holds "only BUG-* ids"; it holds 54 FEAT-
  ids too. The GAP still stands on the fixture ids — do not re-litigate the gap, do not reuse the
  rationale — `feature_schema.py:226`, `grep -c FEAT-` → 54 — verified-at 94b5e465
- c15's SC-04 blocker (form 16, `git --exec-path <p> merge <branch>`) is CLOSED and must not be
  reopened: real git prints the exec path and never runs the subcommand — `notes/research-BUG-1309-goalcheck-c17.md` "The c15 residual" — verified-at 94b5e465
- `git merge` in any form cannot be probed from inside a run: `bash-write-guard.sh` refuses the
  command name outright, including in a throwaway `/tmp` repo — refusal text observed this run — verified-at 94b5e465

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/research-BUG-1309-goalcheck-c17.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/runs/c17-validator/digest.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/qa-c17.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`

## Done when

Scope: operator rules on SC-04's three evidence gaps, then SC-10 is hand-tested
Authority: brief-sc:SC-04
Authority: brief-sc:SC-10
