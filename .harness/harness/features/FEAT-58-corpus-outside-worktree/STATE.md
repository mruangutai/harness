# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: RE-PLAN COMPLETE, mission `plan`, cycle 0, 2026-09-10. Plan drafted from the operator's new definition of done (`.harness/notes/dod-worktree-corpus-2026-09-10.md`) and its same-day shape correction. On disk: BRIEF.md at 10 REQ / SC-01..SC-13, plan.yaml at 9 tasks (N-01..N-09) and 12 decisions, `status: plan`, both approvals `pending`. Handoff: notes/handoff-plan.md
- squad: none — awaiting the operator's batched signature review
- status: awaiting_user
- gate: the adversarial panel returned FAIL, `severity_max: high`. Six high findings (F-01..F-06) are recorded in plan.yaml's `panel` key with disposition `open`. DEC-207 forbids a pre-signature fix dispatch and no agent in this chain may risk-accept a high, so they enter the operator's ONE batched review pass and are disposed of there — by an ordered fix, or by `sign-approval --overrule PF-ID:<reason>`.
- budget: cycles_used 3 of 10, after the operator's reset of the 8 spent against the superseded problem statement. runs 29 of a 20-run informational budget (19 inherited from the halted plan, 10 added this cycle) — INV-22 notes it and never stops a feature.

## Open Questions

- OPERATOR DECISIONS, all riding the signature: (1) F-01 — bring the four remaining cross-feature scan sites (`board_lifecycle.py:476`, `check-plan-routes.py:835`, `validate-feature-json.py:42`, `check-domain.sh:1916`) into this feature, or defer each by name with acceptance; deferred, they ship silently narrowed the day D-1 lands. (2) F-02 — does the DoD's "uniqueness index" mean a persisted tracked file, and if so which writer regenerates it on every `feature.json` creation? The plan names none. (3) D-06 — correct one of FEAT-02 / FEAT-03-subissue-mirror, or era-exempt the pair; picking Arm A also signs one named pathspec exclusion for `FEAT-03-subissue-mirror/feature.json`.
- F-03..F-06 are correctable spec defects rather than risk questions, but they are high and therefore the operator's to release: a verify that cannot pass under its own recommended arm, two tests specified to go red for every feature after this one, and a refusal contract `merge-gate.py` has never had (`deny()` prints JSON at `:144-145`; no `sys.exit` exists in the file).
- The goal-check graded the PRE-amendment plan; no goal-check has read the amended draft, which `check-state.sh:551-558` grades a WARN at signature. Not re-run deliberately: six open highs will change the draft, and re-grading an artifact about to move buys nothing. Order it with the batched fix.
- Harness defects observed this run, none folded into the feature: plan.yaml's top-level `lanes:` block is unwritable by any route (`lanes` in neither `UNION_KEYS` nor `AMENDABLE_KEYS`, plan-merge.py:121/:1249) so it still describes the halted plan while D-07 carries the live table — the remedy is a `set-lanes` verb mirroring `set-panel`; a subagent's `Write` to `/Users/molchairuangutai/GitHum/x`, an arbitrary absolute path outside every governed root, was permitted with no denial (file deleted); two lead returns exited 1 with "yield called with null data" while carrying a valid digest.
- Feature.json's cycles-vs-FAIL check reads `cycles_used=3` against 8 recorded FAIL runs, because the operator's budget reset kept the run record intact. The invariant has no concept of a reset; the record is honest and is not to be rewritten to satisfy it.
