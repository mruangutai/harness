# Handoff — validate phase — FEAT-10-software-factory

RECONSTRUCTED AT FEATURE CLOSE by the ship-phase orchestrator from the run digests. The validate
predecessor wrote none, so that working memory WAS lost and every successor ran the disk-only
path DEC-159 supports. This records the crossing; it is not contemporaneous.

## Next

VALIDATE DID NOT EXIT CLEAN, and that is the load-bearing fact. panel2 returned ESCALATE with one
`high` `must_fix` open — A1 — routing the feature BACK to build rather than forward. That
re-entry is closed (`runs/a1fix-eng`, PASS, committed b86565b) and the next action is the ship
decision.

## Trust

- The blocking test-matrix gate PASSES on `unit` and `integration` only, both exit 0; DEC-187
  removed `functional` by signed decision — `runs/qa2-validator/digest.md` — verified-at b86565b
- `gates.review` is `advisory_unless_high`, so with A1 closed nothing in the panel gates —
  `runs/panel2-validator/digest.md` — verified-at b86565b
- 20 criteria met / 0 partial / 0 not_met on the clause-level bar; the three re-graded ones were
  each proved by a MUTANT, not a reading — `runs/goalcheck2-product/digest.md` — verified-at b86565b
- All four INV-24 findings are CLOSED in the tree — C1 fail-open, C2 within-feature collision, C3
  four-of-eight binding, C4 missing remediation — re-read by me — verified-at b86565b
- Eleven panel2 advisory findings survive UNDISPATCHED, plus panel1's F3 and F7 —
  `runs/panel2-validator/digest.md` — verified-at b86565b
- panel2's `check-state.sh` line citations are anchored to a pin reachable only from
  `wip-omp-and-feat10-mixed` and will not match the file today —
  `runs/panel2-validator/digest.md` — UNVERIFIED
- The A1 fix is verified against the STUB ONLY; the operator's live typo journey, the one thing
  that ever reproduced it, has not been re-run — `notes/answers-a1fix-eng.md` Q5 — UNVERIFIED

## Dead ends

- Do not re-run the panel over the A1 fix — the operator ruled re-pin and re-run nothing —
  `notes/answers-a1fix-eng.md` Q4
- Do not amend `plan.yaml` for `_validate_stations` — the run digest stands as the record —
  `notes/answers-a1fix-eng.md` Q2
- Do not file anything on the disclosed worktree edit — accepted, nothing reached the tree —
  `notes/answers-a1fix-eng.md` Q3
- Do not re-derive the 19-versus-20 criterion bar — the operator settled it at clause level —
  `runs/goalcheck2-product/digest.md`
- Do not re-adjudicate `factory_land.py:77` upward — panel1 graded it `med` because merging is the
  operator's forced next action — `runs/panel-validator/digest.md`

## Working set

- `.harness/features/FEAT-10-software-factory/runs/panel2-validator/digest.md`
- `.harness/features/FEAT-10-software-factory/notes/answers-a1fix-eng.md`
- `.harness/features/FEAT-10-software-factory/feature.yaml`
- `.harness/features/FEAT-10-software-factory/notes/ship-review-ship-2026-08-09.md`
- `.harness/features/FEAT-10-software-factory/runs/goalcheck2-product/digest.md`
