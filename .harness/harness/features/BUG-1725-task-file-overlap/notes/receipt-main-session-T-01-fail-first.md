# Fail-first receipt — BUG-1725 T-01

The pinned test (from fix commit `14b731a9`) run against origin/main `1a1c1925`, checker unchanged. Captured 2026-09-16T05:16Z by Main for validate c2 (qa must_fix).

```
PASS  check: an otherwise valid plan with shared files still exits 0 (SC-02)
FAIL  check: exactly one OVERLAP line per shared path — two here, not one per anchor (SC-01)
PASS  check: a file one task names is never an overlap
PASS  check: repeated anchors confined to one task print no OVERLAP
PASS  check: an existing failure keeps its exit 1 when overlap is also present
FAIL  check: the overlap is still reported beside the failure
```

Red on the four assertions the fix introduces (one OVERLAP line per shared path; a.py named four ways is one line; new_module.py shared; overlap reported beside a failure). Green at the parent, by construction, on the two invariant-preservation assertions (exit 0 with shared files; exit 1 kept beside overlap): SC-02 as reworded attaches fail-first to the overlap-beside-failure assertion, which is in the red set.
