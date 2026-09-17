# FEAT-53 simplification receipt

**BLUF:** Three strictly behavior-preserving simplifications remain in the reviewed concrete code diff; no anchoring semantics or assertions are proposed for change.

- **Reviewed diff:** `a18d6a9f1f832084df84be22097a409d73bf4f61..7604b65e361f195e528ff7c5a48d42c97a91ec2b`
- **Base:** `a18d6a9f1f832084df84be22097a409d73bf4f61`
- **Head:** `7604b65e361f195e528ff7c5a48d42c97a91ec2b`

## Findings

1. **File:** `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`  
   **Line:** 10  
   **Summary:** `duration` interpolates a conditional expression whose two branches are both the empty string.  
   **Cost:** The dead conditional obscures that every non-null duration is rendered identically and adds an unnecessary evaluation at each displayed duration.  
   **Alternative:** Replace ```${value}s${value ? '' : ''}``` with ```${value}s``` while retaining the existing null branch.

2. **File:** `.claude/skills/harness/bin/dashboard/kpi.py`  
   **Lines:** 110-125  
   **Summary:** `_feature_trend` spells the same ten-field trend schema three times.  
   **Cost:** A future field addition or removal requires synchronized edits to three tuples; a missed edit silently makes the unavailable and record-present payload shapes diverge.  
   **Alternative:** Define one module-level immutable trend-field tuple and use it for both comprehensions, preserving every current field and unavailable reason.

3. **File:** `.claude/skills/harness/bin/dashboard/trend.py`  
   **Line:** 193  
   **Summary:** `_window` re-imports `kpi` even though the module already imports it at line 10.  
   **Cost:** The redundant statement adds needless import-cache work on every window resolution and falsely suggests a local import-order requirement.  
   **Alternative:** Remove the local `import kpi` and call the existing module-level binding.
