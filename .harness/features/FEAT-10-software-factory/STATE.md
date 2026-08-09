# STATE

## Current

- feature: FEAT-10-software-factory
- run: .harness/features/FEAT-10-software-factory/runs/prose-delta-validator/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- SIGNATURE READY. All five operator rulings have landed and been reviewed; the final contract review returned PASS with must_fix empty. One signature covers BRIEF.md and plan.yaml. No prototype, and no UAT script — SC-07's deletion left zero uat criteria, recorded in feature.yaml gate_status.uat so the ship gate cannot skip it silently.
- FOR THE SIGNER: the delta contains ONE changed assertion, not zero. SC-01 gained the precondition "Given a feature.yaml ledger that accurately records the first run". It narrows the criterion and makes it match its only fixture; D-14 already recorded the unconditional reading as false.
- ADVISORY, not gating: the "edge (i)" label is bound to two different scenarios (plan.yaml:1069-1072 versus D-01 and DESIGN.md:121-124), whose repairs differ. Smallest fix is renaming one to edge (iv).
- ADVISORY, pre-existing not drift: SC-10 declares evidence: unit while plan.yaml's own T-12 reasoning argues the case is integration.
- ADVISORY: the Q12 refusal is instructed but no criterion asserts it — SC-13(a) binds exactly five unclaimable reasons and this is not among them.
- PROCESS: the feature dir is untracked, which is why 13 of 20 criteria could not be semantically diffed. .gitignore ignores only runs/**, so these files are meant to be tracked. Committing before any future rewrite turns a judgement call into a diff. Not committed by me — we are on main and no commit was requested.
- PRE-CONDITION still not true: board 3's Status has no Building or Review option. The operator's, before T-01 runs.
- Budget: 8 of 10 cycles, 16 of 20 runs.
