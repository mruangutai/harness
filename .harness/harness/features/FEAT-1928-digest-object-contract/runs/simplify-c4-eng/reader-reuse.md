# Recovered original reuse assessment — transport failed

Main recovered this exact attempted payload from the reader's session JSONL (first of six yield attempts). Its declared PASS was NOT an accepted terminal handoff. The disclosed partial coverage still needs the same reader's continuation; this file is not a clean full-scope quality verdict. No runtime claim was forged or restored manually.

# FEAT-1928 reuse reader (simplify-c4-eng)

**Verdict: PASS (2 low advisories).** Angle: reuse only. Settled decisions were not reopened.

## Findings
1. `digest_destination.py:24-25` — the feature-id regex is a third Python copy; the copies are dispatch-guard.py:212, check-domain.py:975 and harness-hooks.ts:8. The existing parity test (test-check-domain-grant.py:1180-1202) covers only check-domain vs dispatch-guard.
   - Cost: grammar drift between the append-authorization gate and dispatch-guard goes untested.
   - Alternative: import or export one pattern via `harness_boundary` (already imported here), or extend the parity test.
2. `digest_destination.py:15-16` — `LEAD_SQUADS` restates the lead roster held in `check_state/run_state.py:6` (`LEADS`); lead membership is also encoded at validate-digest.py:209-210 and in `digest_schema.ALIASES`.
   - Cost: adding or renaming a lead needs edits in several tables, and a miss refuses append authority only at run close.
   - Alternative: derive membership from one lead set, or add an equality assertion in an existing test.

## Reuse confirmed good
- Durable consumers (check_state ctx/run_state/feature_record, plan_merge/panel, the validator's append comparison) all use `digest_record.last_fenced_mapping`.
- Strict JSON loading goes through `artifact_accessors.load_harness_json` and `read_hook_payload`.
- YAML parsing uses `harness_yaml.load_str`; placeholders use `harness_yaml.PLACEHOLDER_UNSET`.
- Grant matching uses `harness_boundary.matches` and `artifact_accessors.manifest_domains`.
- Claim and feature-root lookup use `inflight_registry`.
- The TS persona table is drift-tested against Python `PERSONAS` and `ALIASES` (omp-hooks.test.ts:1444-1448).

## Coverage and limits
Read the three new digest modules in full, targeted regions of validate-digest.py, and greps across bin/, .omp/extensions and tests. Persona and skill markdown, docs, the full validate-digest.py body, the TS bodies, the schema JSONs and the test bodies were not read line-by-line. No checks were run.

## Complete five-part findings and disclosed limits

```json
{
  "findings": [
    {
      "file": ".claude/skills/harness/bin/digest_destination.py",
      "line": "24-25",
      "summary": "The feature-id pattern `(?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+` is restated inline a third time in Python; copies already exist at dispatch-guard.py:212 and check-domain.py:975, plus .omp/extensions/harness-hooks.ts:8. The new copy is not covered by the existing parity test.",
      "concrete_cost": "The repo guards only check-domain vs dispatch-guard (tests/integration/test-check-domain-grant.py:1180-1202). If the id grammar changes, the digest-append authorization gate can accept or refuse different feature ids than dispatch-guard without any test failing. That gate is a security binding.",
      "alternative": "digest_destination.py already imports harness_boundary and has no bootstrap constraint, so import or export one shared pattern from it. Otherwise extend run_feature_id_regex_parity to compare digest_destination's literal as well."
    },
    {
      "file": ".claude/skills/harness/bin/digest_destination.py",
      "line": "15-16",
      "summary": "LEAD_SQUADS restates the three lead personas, which check_state/run_state.py:6 already holds as `LEADS`. validate-digest.py:209-210 and digest_schema.ALIASES also encode lead membership.",
      "concrete_cost": "Adding or renaming a lead requires editing the lead roster in at least three Python tables. A lead missing from LEAD_SQUADS is refused append authority, which surfaces only when that lead's run closes.",
      "alternative": "Derive membership from one shared lead set, such as `run_state.LEADS`, and keep only the squad-name values local. Alternatively add a one-line test asserting `set(LEAD_SQUADS) == run_state.LEADS`."
    }
  ],
  "recommendations": [
    "Optional advisory: pin digest_destination's feature-id literal to the existing parity test, or import it, before the next id-grammar change.",
    "Optional advisory: assert LEAD_SQUADS keys equal run_state.LEADS in an existing unit test.",
    "No action needed on digest_record, digest_schema or validate-digest. They reuse artifact_accessors.read_hook_payload/load_harness_json, harness_yaml.load_str/PLACEHOLDER_UNSET, harness_boundary.matches, inflight_registry.feature_root/find_run_claim and digest_record.last_fenced_mapping. The only restated table is the TS persona roster, which is drift-tested against Python at omp-hooks.test.ts:1444-1448."
  ],
  "coverage": [
    "Read digest_destination.py, digest_record.py and digest_schema.py in full.",
    "Read validate-digest.py header, the ALIAS/norm region, the persona-resolution call sites and the append/last-record region.",
    "Grepped bin/, .omp/extensions and tests for restated feature-id regexes, persona and lead rosters, fence and YAML parsers, strict-JSON decoders and safe_dump use.",
    "Confirmed check_state consumers (ctx.py, run_state.py, feature_record.py, table.py) and plan_merge/panel.py all route through digest_record.",
    "Confirmed the TS persona table is drift-checked against Python PERSONAS/ALIASES.",
    "Confirmed digest_schema reuses the strict JSON loader."
  ],
  "limitations": [
    "Did not read persona and skill markdown (.omp/agents, harness-digest-dev, handoff and team skills) or doctrine/UI docs line-by-line for restated instruction text.",
    "Did not read the full validate-digest.py body (about 2290 lines), digest-schema.ts and harness-hooks.ts bodies, the 16 schema JSONs or the changed test bodies.",
    "Did not read the pending integration working-tree contents beyond the files above.",
    "Read-only; no checks or tests were run."
  ]
}
```
