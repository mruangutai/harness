# Receipt — T-17 red proof, 2026-08-27

Main session, main-session-direct lane. The two cases below were written FIRST and run against
the untouched `validate-digest.py` at `8439002`. Both failed. The verbatim lines:

```
FAIL  10: children_in_flight_stale_claim — a FOREIGN session's claim does not refuse this return
      | exit 2, stderr='check-digest: released the #551 claim for harness-eng-lead.\ncheck-digest: BLOCKED - returned with children in flight (harness-eng-lead)\n  - harness-backend-dev started 2026-08-27T17:12:11.527662+00:00\n  this is issue #551: a verdict about a'
FAIL  10: children_in_flight_stale_claim — and no children marker is printed
FAIL  11: and the refusal names the single-agent release command for that child
```

Case 11's first half — that a SAME-session child still refuses — passed before the fix and must
keep passing after it. It is there so case 10 cannot be satisfied by a build that refuses
nobody.

## What the red state means

`live_children` accepts a `session` filter and `validate-digest.py` never passed one, so a claim
stranded by ANOTHER session counted as a live child of this return. Measured 2026-08-26 and
written up in `runs/2026-08-26-2-plan-product/digest.md`: one stranded `harness-pm` claim
refused the pm spawn at `dispatch-guard.sh`, then refused the LEAD's return here, then refused
the ORCHESTRATOR's return here again. Three tiers locked out of reporting by one strand, and
each stranding created the next.

Case 11's second half records the other half of that day: the refusal printed no remedy at all,
and the advice a reader would reach for — `release-all` — sets the registry to `{}` and wipes
every claim of every agent. Following it on 2026-08-26 would have destroyed a live claim.
