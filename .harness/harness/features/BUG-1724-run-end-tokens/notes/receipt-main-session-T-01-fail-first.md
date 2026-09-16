# Fail-first receipt — BUG-1724 T-01

The new tests from fix commit `e0ea15e0` run against its parent `1a1c1925` (origin/main), production code unchanged. Captured 2026-09-16T05:01Z by Main for validate c1 (qa V-01).

## tests/unit/test-feature-record.py StampTokensTest
```
FAIL: test_refuses_when_more_than_one_run_is_open_naming_each (__main__.StampTokensTest.test_refuses_when_more_than_one_run_is_open_naming_each)
FAIL: test_refuses_when_no_run_is_open (__main__.StampTokensTest.test_refuses_when_no_run_is_open)
FAIL: test_stamps_the_one_open_run_and_a_bare_run_end_preserves_it (__main__.StampTokensTest.test_stamps_the_one_open_run_and_a_bare_run_end_preserves_it)
Ran 5 tests in 0.356s
FAILED (failures=3)
```

## tests/unit/omp-hooks.test.ts "host-stamped tokens"
```
(fail) host-stamped tokens > sums every result's integer tokens and stamps the open run BEFORE spend is read [81.07ms]
 3 pass
 1 fail
```

Red for the right reason: `stamp-tokens` is not a verb at the parent (argparse exit 2) and the hook stamps nothing, so the positive SC-01/SC-04 cases fail; the SC-02 no-figure case and the SC-03 override pass at both ends by construction (they assert absence and an existing verb) and discriminate only through the positive cases beside them.
