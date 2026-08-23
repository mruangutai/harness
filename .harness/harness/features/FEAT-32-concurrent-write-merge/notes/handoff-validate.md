# FEAT-32 validate seam — the panel's five must-fixes, closed by the main session

## Next
Nothing on this feature. It is merged as `9ad8f35` (PR #721) and its status is Done.
Two things it leaves open, both filed rather than carried:
- **#720** — plan-merge.py's strict reader, both halves.
- **Q6 and Q7** from the panel, non-blocking. Q6: should a verify that names required cases
  also assert those cases exist. Q7: B-2 contradicts D-09's orphan-residual rule.

## Trust
- The full suite at merge: **45 PASS / 0 FAIL**. `check-plan-routes.py` 0 violations.
- `test-check-domain.py` 201 ok, 28 of 28 T-14 cases; `test-dispatch-guard.py` 28 of 28;
  `test-validate-digest.py` 20 of 20, red-proved with a `live_children` mutant at 17/20.
- The approval guard fix is written against the **reviewer's exact payloads**, not mine.
  Two of the three payloads I guessed at did not reproduce; all of the reviewer's did.

## Dead ends
- **Containment was the wrong test for the approval guard.** The panel defeated it three
  ways and every one crossed a boundary of the range rather than sitting inside it. It is
  overlap now.
- **"Child key at the on-disk indent OR DEEPER" was too broad.** Approval children sit at
  indent 2 and task keys at 4, so it denied every legitimate task edit. The allow case
  caught it; reasoning did not. Exact indent only.
- **A mutant copied into a tmpdir is not a proof.** It dies on a path derived from its own
  location and returns a code indistinguishable from the finding. Place it beside the
  original.
- **`FIXTURE_MANIFEST` granted only `harness-documentor`.** Twenty-two cases firing as
  `harness-pm` took an ordinary DOMAIN denial and never reached the check under test —
  green and incapable of going red. Same trap as FEAT-31 T-15, hit again in the same file.

## Working set
- `.claude/skills/harness/bin/check-domain.sh` — the approval guard, on the ALLOW path.
- `.claude/skills/harness/bin/dispatch-guard.sh` — claim after the model refusal; root from
  the manifest FILE, never the `.harness` directory, which resolves `$HOME` when installed
  globally.
- `.claude/skills/harness/bin/inflight_registry.py`, `harness_merge.py`.
- `.claude/skills/harness/bin/validate-digest.py` — the D-09 children refusal.
- `.harness/harness/docs/DECISIONS.md` — DEC-199, and DEC-174 amendment 4's enumeration.

## Log
- The feature reached the review panel with **T-13 and T-17 still `pending`** and nothing
  reported it. The panel does not read task status and neither does this seam. The operator
  accepted the main-session repair rather than re-running the documentor.
