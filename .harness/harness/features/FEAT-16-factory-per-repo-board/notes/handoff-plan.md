# Handoff — plan — FEAT-16

Written after the fact by the main session, from the two plan runs' digests on disk
(`runs/2026-08-11-01-plan-product`, `runs/2026-08-11-02-plan-product`). Recorded that way rather
than implied to have been written at the seam. INV-17 raised its absence on 2026-08-12; the note
was owed and was not fabricated to silence the check.

## Next

- **Build. The precondition has cleared** — FEAT-14's migration is merged, so the settled
  `feature.json` format is in place and this plan builds once on it rather than being rewritten
  mid-flight.
- **SC-06 is operator-only and stays `not_met` until they run it.** A live factory claim creates a
  throwaway issue and a `factory/issue-N` branch in `mruangutai/kaya-ai`, a real product
  repository, and moves a station on live board 2. **The issue used must not be one of the 118 in
  `Done`** — the run moves a station, and moving a finished issue breaks the 118-in-Done criterion.
- Eleven tasks in three phases. The phasing is itself the finding: a single-shot schema change
  would have bricked every governed write in the repo, including the write that undoes it.
- `#278` is the deliberately excluded neighbour — product-board station drift, unmeasured, waiting
  on this feature landing.

## Trust

- Both gates exit 0 on this plan, and `check-plan-routes.py` reports **0 violations** for it.
- Architecture review PASS. Six defects were found across three passes, every one of them in a
  fix rather than in the original design.
- No prototype gate fires: a fleet-schema plus Python-config change with a board mutation has no
  end-user interactive surface. Decided by the product lead rather than by `visual-designer`,
  which was never spawned. Overridable in either direction.
- Both boards already carry the six-value vocabulary, verified by counting items before and after
  rather than by trusting the mutation. T-07's board edit was converted to a **precondition read**
  for that reason — it must not re-do work already done, nor fight the live state.

## Dead ends

- **The research note carried a false claim and it was corrected at source, not quietly edited.**
  It said `check-plan-routes.py` "contains no budget logic at all". That is FALSE:
  `MACHINE_LINES_PER_TASK = 50` at `:280`, emitted as a violation at `:322-327`. The real reason
  its FEAT-14 figure was void is narrower and stronger — `BUDGETED_FIELDS` excludes `intent:`, so
  intent length can never produce a budget violation. pm overturned the dispatch's own ground
  truth here, and was upheld on re-measurement.
- **`traces:` deviation, recorded rather than hidden.** SC ids were directed into `traces:`; pm
  declined, because zero SC ids appear in `traces:` anywhere in the tree — that is a convention of
  the pre-DEC-182 `PLAN.md` format only. Accepted as format-correct. Two-token edit if wanted.
- **A question-id collision survives in `STATE.md`**, which pm could not fix because that file
  belongs to the orchestrator: `STATE.md:36-40` numbers three questions Q3/Q4/Q5 that
  `notes/answers-2026-08-11-01.md` calls Q4/Q5/Q6. A reader following STATE.md lands on the wrong
  answer.
- Promotion from `Backlog` to `Ready` has **no recorded step anywhere in the harness**. Out of
  scope by ruling, recorded so it is not silently absorbed.

## Working set

- `BRIEF.md`, `plan.yaml` — eleven tasks, six REQs, thirteen SCs, eleven decisions.
- `notes/answers-2026-08-11-01.md` — the operator's rulings and the signature.
- `notes/research-feat16-plan-2026-08-11.md` — corrected, with every figure carrying how it was
  measured.
- Board 3 `PVT_kwHOAAases4BfZ9Z` and board 2 `PVT_kwHOAAases4Bc7h3`, both on the six stations.
