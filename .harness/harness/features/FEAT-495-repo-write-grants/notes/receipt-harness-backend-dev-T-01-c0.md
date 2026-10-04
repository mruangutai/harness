# T-01 receipt — harness-backend-dev — c0

Implemented optional factory-claim repository identity and dispatch correlation, deterministic same-repository child attachment, explicit active/missing/unreadable/stale/released/mismatched binding states, and target repository metadata from the existing two-base classifier.

## RED evidence

Before production edits:

```text
$ python3 tests/unit/test-harness-boundary.py && python3 tests/integration/test-inflight-registry.py
FAIL case_target_repository_metadata_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'RepositoryBases'")
1 FAILURE(S): ['case_target_repository_metadata_did_not_crash']
```

```text
$ python3 tests/integration/test-inflight-registry.py
TypeError: claim_with_receipt() got an unexpected keyword argument 'repository'
```

## Targeted verification

```text
$ python3 tests/unit/test-harness-boundary.py && python3 tests/integration/test-inflight-registry.py
... ALL PASS
... PASS - 153/153 checks passed
```

The boundary script executes its registered cases and reports `ALL PASS`; the registry script reports 153 discovered assertions/checks passed.
