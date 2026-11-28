# Security review · FEAT-2622 · cycle 1

**FAIL — The plan-team carve-out can convert a reader FAIL to PASS without establishing that discounted findings were the only reason for the FAIL.** Reviewed `3e979ae3..d131c231`.

## SEC-01 · high · substance

`exposure: {trigger: plausible, vs_today: regression, control: adversary}`

`validate-digest.py:2265–2304` checks the on-disk rows and matching finding IDs, but does not check the current digest finding's exposure or the member's independent gates before `:2353–2358` ranks it as PASS. The product lead controls the fan-in and team digest. A current non-discounted finding can match an open discounted row by identity alone; `plan_merge/panel.py:519–536` also intentionally retains the prior row for an existing ID, so a stale discount can arise without anyone falsifying a rating. Separately, a scope reviewer with only discounted findings and an unrelated `must_fix` can legitimately FAIL (`validate-digest.py:1665–1674`); the team member contract does not carry that evidence (`schemas/digest/common.json:909–936`), so the carve-out can hide this FAIL too. The base required matching rows to be resolved and would not have relieved either case with a matching open row. D-06 preserves independently justified FAILs. The team verdict is what orchestration routes on.

**Must fix:** Require corroborated evidence that a member's FAIL rests solely on discounted findings before granting open-row relief. Deny relief on current rating conflicts or independent gating evidence; preserve the existing resolved-row path.

## Other boundaries

- **SC-06:** `panel_findings.py:97–116` owns the predicate and severity check; `validate-digest.py:1613–1615` and `plan_merge/panel.py:489–494` call it. Closed exposure shape, rating ceiling, sentinel limits, and legacy-row handling do not themselves grant malformed input relief. `gates_signature` keeps the base severity normalization.
- **SC-08:** `harness-code-review/SKILL.md:146–150` and `.omp/agents/harness-security-reviewer.md:322–330` explicitly protect adversary-controlled triggers at a gate meant to refuse, regardless of likelihood.
- **Tampering / repudiation:** DEC-260 accepts that truthfulness of the reader's rating is not mechanically verified; SEC-01 needs no false rating. SC-09's one-line reason is procedural: `.omp/agents/harness-product-lead.md:437–453` and `.omp/agents/harness-validator-lead.md:480–485` require it in the artifact, but roll-up does not check it. Absence can therefore be silent; SC-09 does not promise a machine check.
- No new credential handling, auth endpoint, network request, or export path. No evidence of a secret or cross-tenant data exposure from this diff.

**Evidence:** Pinned source and base-to-pin comparison; SEC-01 is static, not a live exploit or gate execution. Pinned code grade completed (`PASSING: 41`). Reported missing `node_modules/.bin/tsc` is an environment gap, not a feature defect. No product questions remain.