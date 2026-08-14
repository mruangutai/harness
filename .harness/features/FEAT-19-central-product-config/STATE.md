# STATE

## Current

- feature: FEAT-19-central-product-config
- run: .harness/features/FEAT-19-central-product-config/runs/plan-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase complete. BRIEF.md, plan.yaml and DESIGN.md are written and `pending`; the operator's
signature is the phase exit. Nothing is committed and no branch exists — `feat/FEAT-19-central-product-config`
is created only after approval. Seven tasks, three of them `main-session-direct` by DEC-179 route
resolution; no task touches any of DEC-174's four gate scripts.

## Open Questions

- Q2: two of T-01's operator-facing message strings (DESIGN.md rows 6 and 7) live only in
  DESIGN.md, which is not in the signature. Cover DESIGN.md in the signature, or lift the strings
  into T-01's intent? — blocks nothing; blocks T-01's message contract being fully signed.
- Q3: if the operator takes D-02 option B at signature, the DEC-174-in-substance question about
  sharing `harness_boundary.select_base` re-fires and needs a ruling before T-01 is dispatched.
  Under the recorded D-08 choice it does not fire. — blocked party: whoever dispatches T-01.
- Q4: D-06 rewires the qa gate only; `gh-sync.py` keeps hand-joining `.harness/harness.json`.
  Option B (rewire both) is priced in the BRIEF. — the operator's call at signature.
- Q5: two eng-lead advisories deliberately not spent a fourth pm cycle on — T-01's relative-path
  `main()` names no cwd save/restore, and nothing asserts `config_path` is absolute. Fold at
  signature or let the build pick them up. — blocked party: nobody.
