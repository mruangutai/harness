# Receipt — harness-backend-dev — ALTITUDE angle — BUG-1290 B-16

**BLUF: empty pass.** Nothing in the diff (`tests/unit/test-factory-claim.py` 5b/5g rework,
:1178-1330) sits at the wrong depth. `leave` on every question the dispatch raised.

## What I checked

1. **Seam choice for 5g's mutation** (`claim._BlockerCache = _FeatureOnlyIssueMapCache`,
   :1315-1320). Compared against the two named precedents:
   - `run_main`'s `features_root_fn` argument (:403,:412,:884-887) — a real injected seam,
     but it exists for `factory_config.features_root`, a function with no analog need here;
     `main()` has no `cache_cls`-shaped parameter, and none is warranted for one mutation test.
   - B6's `harness_yaml.load_plan = recording_load_plan` swap (:912-927) — a direct
     module-attribute rebind with save/finally-restore, the *exact* idiom 5g uses. B6 already
     normalizes this technique in this file; 5g does not introduce a new pattern, it reuses
     the established one. `product_config` (:419) is the third instance of the same idiom.
   Verdict: **leave**. The rebind is coupled to the concrete name `claim._BlockerCache`, so it
   fails loudly (caught exception → `check(name_5g, False, ...)`) rather than passing vacuously
   if the class were renamed or inlined — the failure mode the dispatch asked me to name doesn't
   materialize. Production is frozen at review_sha regardless, so a new injection seam is a
   briefing-row at best; I judge it not worth one given B6's precedent already covers this shape.

2. **Single authoritative statement of 5b's property.** `_5b_property_holds` (:1208-1223) is
   called by both 5b (:1229, direct) and 5g (:1321, negated) — one predicate, zero restatement.
   No drift risk. **leave.**

3. **Placement/scope proportionality.** `_run_5b_scenario`/`_5b_property_holds` are module-level
   because two cases share them; the mutant class `_FeatureOnlyIssueMapCache` is scoped inside
   5g's own `try` block because only 5g uses it, matching the file's existing convention (e.g.
   `fake_product_config` at :421 is similarly local to its one call site). **leave.**

4. **Accepted residuals.** The save/restore of `claim._BlockerCache` is wrapped in `try/finally`
   (:1317-1320), matching B6's and the product_config pattern's compensating control. No
   residual left uncontrolled. **leave.**

## Findings

`[]` — none met the bar for a five-part finding with a concrete cost.

```yaml
angle: ALTITUDE
findings: []
```
