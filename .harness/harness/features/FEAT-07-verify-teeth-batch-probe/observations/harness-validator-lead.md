# Observations — harness-validator-lead — FEAT-07-verify-teeth-batch-probe

- 2026-08-04: Two-step review panel (`code`, `qa`) at 29b612e; `security`/`ui` pre-skipped by the
  caller. Verdict FAIL on one med `must_fix`. Blocking gate (`qa`) PASSED and the ADVISORY gate
  (`code`) carried the only defect — the inverse of what the dispatch framing led me to expect.
  Worth remembering as a shape: which gate is blocking says nothing about which gate finds things.

- 2026-08-04: CALIBRATION, against OQ-01. I handed both members three facts as explicit "context,
  not instruction" and asked them to audit rather than agree. Both returned ADDITIVE findings:
  `qa` stated it re-derived the SHA, diff stat, change_type split, matrix contents and case count
  from source rather than my framing, and produced an SC-06 coverage gap I had not mentioned;
  `code` returned FAIL on `harness-digest-dev/SKILL.md`, a file my prompt barely pointed at, while
  my prompt steered hard toward `validate-digest.py`. So the "member treats lead recall as
  instruction" risk did not materialise here. One run, one data point — but the discriminating
  detail is that both findings were things I had NOT said, which is the signal OQ-01 asks for and
  which a pure acceptance rate cannot show.

- 2026-08-04: My own `state.yaml` was BLOCKED by `check-domain.sh` on the first write — I had added
  a top-level `pre_dispatch:` key holding my verified pre-dispatch facts. DEC-154: state.yaml is a
  checkpoint, not a notebook. The hook was right and it caught a lead doing exactly what the rule
  names. Verified facts belong in `digest.md`; the step `note:` is the prose ceiling.

- 2026-08-04: Verifying member citations at my own tier paid three times and cost ~4 tool calls.
  `code` cited `harness-digest-dev/SKILL.md:50-54` (actual span :50-55) and `qa` cited
  `test-validate-digest.py:1132` (actual `case()` head :1133). Both findings were REAL and my
  independent greps confirmed the substance while correcting the anchors — which is what I then
  put in the digest. Cheap insurance: anchors drift by a line or two even in honest reports, and
  the digest is what travels two tiers as a measurement.

- 2026-08-04: A generalisable check that turned a nit into a bounded item — `code` reported a stale
  self-referential line anchor in `validate-digest.py:572` (cites `:691-692`; the real
  `stop_hook_active` check is `:838`, the same commit having shifted ~150 lines). One grep for
  other three-digit self-anchors in the file showed line 572 is the ONLY one. That converted
  "there may be stale anchors" into "there is exactly one, and the fix is an in-place same-length
  substitution that shifts no DEC-175 committed anchor". The generalising grep is what made the
  finding actionable rather than worrying.

- 2026-08-04: ADEQUACY, the finding neither member could make. `matrix_ok: true` was correct AND
  thin: 9 of 10 tasks were `change_type: docs` -> `{"always": []}`, so the project's only blocking
  gate mechanically covered ONE task (T-01) and asserted nothing about the other nine files. And
  the single defect the panel found landed on SC-16 — one of the seven `verify: inspection`
  criteria that BRIEF itself says nothing mechanical discriminates. Residual risk sat in the
  unmechanized half, and only a reviewer READING found it. `qa` could not see `code`'s finding and
  `code` could not see the matrix shape; the observation exists only at the fan-in.
