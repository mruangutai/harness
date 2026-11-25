# Fix round c1 receipt — case 18 byte-exact, full returns, two new inputs (AdvisorF5Validate scope)

Diff vs pin 8ae96bea: `tests/integration/test-inflight-registry.py` (case 18 and its helpers, table-driven) and the `inflight_registry.py` module docstring only (zero executable lines).

- GREEN at the fix tree: `python3 tests/integration/test-inflight-registry.py` → `PASS - 200/200 checks passed`
- BASE swap (`INFLIGHT_REGISTRY_DIR` = a24eacee module): exit 1. The case-18 failures are exactly the ruled direction; every writer-producible control stays green:
```
FAIL - case18: v1 persona map: the strict read returns exactly its expected answer
FAIL - case18: v1 persona map: the locked writer returns exactly its expected answer ((None, 1))
FAIL - case18: v1 persona map: the writer warns only when it discards a non-empty file
FAIL - case18: v1 empty map: the strict read returns exactly its expected answer
FAIL - case18: v1 empty map: the writer warns only when it discards a non-empty file
FAIL - case18: version-less claims envelope: the strict read returns exactly its expected answer ([{'claim_id': 'c1', 'a
FAIL - case18: version-less claims envelope: the locked writer returns exactly its expected answer (({'claim_id': 'c1', 
FAIL - case18: version-less claims envelope: the locked writer leaves exactly the expected bytes ({
FAIL - case18: version-less claims envelope: the writer warns only when it discards a non-empty file
FAIL - case18: schema-1 claims envelope: the locked writer returns exactly its expected answer (({'claim_id': 'c1', 'age
FAIL - case18: schema-1 claims envelope: the locked writer leaves exactly the expected bytes ({
FAIL - case18: schema-1 claims envelope: the writer warns only when it discards a non-empty file
```
- Default-to-v2 MUTANT (`schema_version` defaulting to 2 in `_known_shape` and `_parse`): exit 1. The case-18 failures:
```
FAIL - case18: version-less claims envelope: the strict read returns exactly its expected answer ([{'claim_id': 'c1', 'a
FAIL - case18: version-less claims envelope: the locked writer returns exactly its expected answer (({'claim_id': 'c1', 
FAIL - case18: version-less claims envelope: the locked writer leaves exactly the expected bytes ({
FAIL - case18: version-less claims envelope: the writer warns only when it discards a non-empty file
```
- Swap-harness artifact: both swap runs also fail the same CLI-subprocess cases (7, 9, 35, 40, 41, feat65), because the copied module dir lacks its sibling imports. These are identical across the base and mutant swaps and unrelated to case 18 (qa's bin/-copy caveat).
