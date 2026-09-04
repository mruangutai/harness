# Handoff — <FEAT-NN>, <ending phase> → <next phase> — written at <sha>, seq-<N>

<!-- Working memory for your successor, NOT a summary — disk already has the history
     (DEC-159). Five sections, all required, ~60 lines total; check-domain denies the
     Write otherwise. Entry grammar for Trust and Dead ends:
       claim — evidence pointer — verified-at <sha> | UNVERIFIED
     No pointer, no entry. Superseded, never appended.

     Done when describes the ONE immediate action in Next, not the phase or feature.
     Its shape is exactly one Scope: line and one to four Authority: lines, with no
     other prose. Authorities combine as logical AND: every pointer must resolve when
     the note is written or edited. The only legal types are plan-task:T-NN.verify,
     brief-sc:SC-NN, finding:PATH#F-NN and approval:PATH#HEADING; a source-code
     location alone is not authority. RESOLVING IS NOT ENOUGH: an authority already
     satisfied when you write binds nothing, so a successor could check it, see it
     green, and skip the action entirely — at least one cited pointer must be one
     the action in Next actually discharges. A task at station done or abandoned,
     and an approval already reading approved, are satisfied; a criterion and a
     finding are judged, so neither counts either way. Both obligations are
     write-time only: the persisted-corpus state check validates shape and grammar
     but never reopens targets, so a note valid when written stays valid. -->

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


## Done when

Scope: <concise label for the ONE action in Next>
Authority: <plan-task:T-NN.verify | brief-sc:SC-NN | finding:PATH#F-NN | approval:PATH#HEADING>