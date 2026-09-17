# REUSE simplify receipt — FEAT-53

## BLUF

One reuse finding: the KPI collector reimplements the repository's canonical `feature.json` reader. No other changed code reimplements an importable existing tree mechanism.

## Reviewed scope

- Base: `a18d6a9f1f832084df84be22097a409d73bf4f61`
- Head: `7604b65e361f195e528ff7c5a48d42c97a91ec2b`
- Scope: concrete code diff only; excluded feature ledger, runs, receipts, and observations.

## Findings

### R-01 — use the canonical feature record reader

1. **Changed file and line:** `.claude/skills/harness/bin/dashboard/kpi.py:60`
2. **Summary:** `_feature` directly parses `feature.json` with `json.loads`, reimplementing the canonical feature-record load path.
3. **Concrete cost:** This reader bypasses duplicate-key rejection, non-finite-value rejection, mapping validation, recorded-block validation, and normalized `FeatureJsonError` diagnostics; future feature-record reader changes must be made in two places and the dashboard copy can silently drift.
4. **Concrete alternative:** Replace the direct `json.loads((feature_dir / "feature.json").read_text(...))` expression with `artifact_accessors.load_feature_json(feature_dir / "feature.json")`, retaining the existing imported module and handling `None` only if the KPI contract requires an absent record path.
5. **Existing reusable mechanism:** `.claude/skills/harness/bin/artifact_accessors.py:81-88` (`load_feature_json`); the same new dashboard surface already uses it at `.claude/skills/harness/bin/dashboard/work.py:188`.
