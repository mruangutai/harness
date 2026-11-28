# BUG-2582, validate run 02 (ESCALATE): operator rulings, 2026-11-27

Source: `runs/2026-11-27-02-validate-validator/digest.md`.

- **MF-3 / OQ-1: ledgered amendment.** `tests/integration/canonical-reader-classification.json` is added to T-02's `files` with `plan-merge.py amend --reason …`. That writes an `amendment` judgement and does not reset approval. It appears in the ship briefing's amendment table, where the operator may overrule it.
- **MF-1: fix all three parts.** This is the operator's choice. The main session had recommended an advisory, on the grounds that lead-written member verdicts are uncorroborated at base. The three parts:
  - (a) exactly one member entry per reader slot;
  - (b) each slot's persona bound to the one `teams/plan.yaml` declares;
  - (c) relief refused when the live dispatch mission is not plan.
- **MF-2, MF-4, MF-5:** fixed inside T-02 and T-03, as the validator lead listed them.
- **OQ-2 (SC-06, never-in-play denials):** read SC-06 as covering carve-out candidates only. No change. The operator asked for an explanation; the main session decided, and the operator may override.
- **OQ-3:** MF-1(c)'s live-mission condition is accepted without rewording SC-05. Offline validation keeps `feature.json`'s mission as the only condition. The main session decided, as for OQ-2.
- **Advisories:**
  - SC-07's guard case is added: an eng-lead digest with plan reader steps is still refused.
  - The bare `approval:` null and the dropped indented comment are left as is. Both fail the practicality rule: each needs a hand-made file, with an outcome no worse than at base.
