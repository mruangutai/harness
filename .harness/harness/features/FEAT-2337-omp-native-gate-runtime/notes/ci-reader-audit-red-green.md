# CI canonical-reader audit fix — RED/GREEN

PR #2391 CI 'checks' failed: canonical-reader audit flagged validate-digest.py::_read_receipt (raw json.loads, json_string, absent from migration inventory). Fix: decode through artifact_accessors.strict_json_loads (THE ONE strict decode), not an inventory exemption. Behaviour change: a receipt with a repeated key is Malformed (a lenient decode would keep the last value).

## RED (row added, production unchanged)
```
FAIL  [feat2337] a duplicated key refuses the PASS
1 FAILING.
```

## GREEN
```
run_feat2337_qa_receipt_cases: ALL PASSED; full test-validate-digest: ALL PASSED; --canonical-reader-audit exit 0
```
