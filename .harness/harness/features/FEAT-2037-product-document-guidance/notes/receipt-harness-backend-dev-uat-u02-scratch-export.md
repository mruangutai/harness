# Receipt: harness-backend-dev, uat-u02-eng, scratch T-01 (read-only handoff)

BLUF: Replace the body of `export(records)` in `/tmp/harness-2037-product-c0/export.py` with the one-line body below. I did not write the fixture, run anything, or grade any assertion. Main applies it.

## Exact replacement (signature and empty predicate `not records` preserved)

```python
def export(records):
    return "EMPTY-PRODUCT-2037" if not records else "\n".join(records)
```

Only two literals change from the current source (`export.py:1-2`): `"EMPTY-WRONG-2037"` becomes `"EMPTY-PRODUCT-2037"`, and the `"|"` join becomes `"\n"`. `"\n".join` puts exactly one newline between records, keeps input order, and adds no leading or trailing separator. A single record comes back unchanged.

## Answer (verbatim for relay)

**Why is Queue absent, and what should empty export return?**

- Queue is absent because the PRODUCT architecture says so. `/tmp/harness-2037-product-c0/docs/architecture.md`, "Export components": "Exporter reads Store directly; marker ARCH-PRODUCT-2037. No Queue participates." The replacement therefore only formats the `records` it is given. It adds no Queue, no new Store API, no storage plumbing and no dependency, and the existing `export(records)` seam is unchanged.
- An empty export returns the string `EMPTY-PRODUCT-2037`. `/tmp/harness-2037-product-c0/docs/spec.md`, "Export behavior": "An empty export returns EMPTY-PRODUCT-2037."
- Newline decision: `/tmp/harness-2037-product-c0/docs/decisions.md`, "Export decision": "Adopt newline-separated records, marker DECISION-PRODUCT-2037." Records are therefore joined with `\n`, which replaces the current pipe. The decision says "separated", so the separator goes between records only (no leading or trailing newline).

## Principles applied

- Foundational Thinking (read this run): the data shape is already a list of strings with one existing seam. I reused it and added no new type, layer or seam.
- Fail-open check: the empty case is decided by the existing `not records` predicate. It returns the explicit marker and does not fall through to a blank string.

## Not done

- Verify command not run (Main only):
  `python3 -c 'import runpy; e = runpy.run_path("/tmp/harness-2037-product-c0/export.py")["export"]; assert e([]) == "EMPTY-PRODUCT-2037"; assert e(["alpha"]) == "alpha"; assert e(["alpha", "beta"]) == "alpha\nbeta"; print("scratch export assertions satisfied")'`
- No assertion graded. PASS means only that the read-only handoff is complete.
- Retry and timeout guidance (retry count unresolved in spec.md; timeout 5 s in spec.md vs 9 s in decisions.md) is outside this task. I made no choice on it.
