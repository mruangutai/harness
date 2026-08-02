# Handoff — <FEAT-NN>, <ending phase> → <next phase> — written at <sha>, seq-<N>

<!-- Working memory for your successor, NOT a summary — disk already has the history
     (DEC-159). Four sections, all required, ~60 lines total; check-domain denies the
     Write otherwise. Entry grammar for Trust and Dead ends:
       claim — evidence pointer — verified-at <sha> | UNVERIFIED
     No pointer, no entry. Superseded, never appended. -->

## Next

<one action: what to dispatch, to which lead, with which input paths — cited to a
PLAN task/SC id. The successor validates this against PLAN/STATE before acting.>

## Trust

- <claim the successor will act on — evidence pointer — verified-at <sha> | UNVERIFIED>

## Dead ends

- <exclusion active for the NEXT phase only — evidence pointer — verified-at | source.
   Durable exclusions go to PLAN Decisions or your observations log, not here.>

## Working set

- <3–5 paths the successor reads first; everything else is archive>
