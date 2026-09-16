# F-02/F-03 fix c1 evidence

**Result:** F-02 and F-03 are resolved at implementation commit
`26b1ad93e678de31a508b10069ecc8f8e874c540`.

**Committed implementation path:**
`tests/unit/test-feature-json-reader.py`

## F-02 — issue-285 comment-bearing inverse

**Hypothesis:** the former `factory_decompose` YAML route accepts issue #285's
comment-bearing feature document, while the public strict feature-JSON reader
must refuse the same bytes. Falsifier: historical YAML parsing would not return
the complete mapping.

**Historical isolated input:** worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-f02-evidence`
at `97b39c504151f3c7c011d9d479b8d8a53abc6bf0`
(`a43592cce53f7b0db8e1b386d446e9bd2b7721ce^`). Its
`factory_decompose.harness_yaml.load_file` received the exact bytes now in
`LoadFeatureJsonTest.test_issue_285_comment_bearing_yaml_document_is_rejected`:
`feature_id: F1`, a `github` mapping, and the three trailing comments on
`parent`, `milestone`, and `T-01`.

**Fail-first command (exit 1):**
```text
python3 -c 'import os,tempfile,sys; sys.path.insert(0,".claude/skills/harness/bin"); import factory_decompose; text=b"feature_id: F1\ngithub:\n  parent: 40        # the container issue, adopted\n  milestone: \"7\"    # quoted on purpose\n  parent_origin: adopted\n  attached: [T-01]\n  issues:\n    T-01: 41   # trailing comment here too\n"; expected={"feature_id":"F1","github":{"parent":40,"milestone":"7","parent_origin":"adopted","attached":["T-01"],"issues":{"T-01":41}}}; d=tempfile.mkdtemp(); p=os.path.join(d,"feature.json"); open(p,"wb").write(text); actual=factory_decompose.harness_yaml.load_file(p); print("FAIL issue_285_comment_bearing_yaml_document_is_rejected", repr(actual)); raise SystemExit(1 if actual == expected else 2)'
```
```text
FAIL issue_285_comment_bearing_yaml_document_is_rejected {'feature_id': 'F1', 'github': {'parent': 40, 'milestone': '7', 'parent_origin': 'adopted', 'attached': ['T-01'], 'issues': {'T-01': 41}}}
```

**Current green command (exit 0):**
```text
python3 tests/unit/test-feature-json-reader.py
```
```text
Ran 22 tests in 0.008s
OK
```
The test asserts the complete public `harness_yaml.load_file` result, then
asserts public `artifact_accessors.load_feature_json` raises
`FeatureJsonError`; it inspects no implementation text.

## F-03 — canonical cutover assertion

**Hypothesis:** the existing `case_canonical_reader_live_baseline` assertion
rejects a compatible pre-cutover tree with dispatchable readers. Falsifier: it
would report no failure for that tree.

**Historical isolated input:** worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-f03-compatible-evidence`
at `5369a9ba8326fb95a74ee32b3468cb1268b960f4` (`fix: route enforcement
readers through canonical accessors`). This SHA supplies the then-live
classification and compatible checker API; the evaluator loads the current
assertion source from this feature worktree without modifying either tree.

**Fail-first command (exit 1):**
```text
python3 -c 'import importlib.util; current="/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/tests/integration/test-check-plan-routes.py"; historical="/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-f03-compatible-evidence"; spec=importlib.util.spec_from_file_location("bug285_current_cutover_assertion", current); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); mod.ROOT=historical; mod.TESTS_DIR=historical+"/tests/integration"; mod.SCRIPT=historical+"/.claude/skills/harness/bin/check-plan-routes.py"; mod.failures=[]; mod.case_canonical_reader_live_baseline(); print("failures=", mod.failures); raise SystemExit(1 if mod.failures else 0)'
```
```text
PASS canonical_reader_live_classification_consistent
FAIL canonical_reader_live_audit_is_zero {'exit_code': 2, 'unresolved': 116, ...}
PASS canonical_reader_scans_converted_python_entrypoints
failures= ['canonical_reader_live_audit_is_zero']
```

**Current green command (exit 0):**
```text
python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test
```
```text
PASS canonical_reader_live_audit_is_zero
PASS canonical_reader_T-03_postcondition
PASS canonical_reader_T-04_postcondition
ALL PASS
```

## Signed task verification

All commands ran from the feature worktree and exited `0`:

```text
python3 tests/unit/test-artifact-accessors.py && python3 tests/unit/test-feature-json-reader.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/unit/test-factory-config.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-upgrade-config.py
python3 tests/unit/test-factory-gh.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/integration/test-merge-settings.py && python3 tests/integration/test-sync-agent-adapters.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-board-lifecycle.py
python3 tests/unit/test-factory-config.py && python3 tests/unit/test-factory-claim.py && python3 tests/unit/test-plan-depends-on.py && python3 tests/integration/test-board-lifecycle.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-worktree-terminal.py && python3 tests/integration/test-feature-worktree.py
```

Representative terminal results were `OK` for both unit suites,
`ALL PASSED`/`all checks passed` for integration scripts, and
`PASS test-feature-worktree.py` for the final T-04 script.

## Finding dispositions

- **F-02:** fixed — central consumer-observable coverage now uses the original
  comment-bearing YAML document and preserves its historical red/current green
  proof.
- **F-03:** fixed — an isolated compatible pre-cutover SHA makes the exact live
  cutover assertion fail; the current self-test passes.
- **F-01/F-04:** not touched; their direct-fix evidence is
  `notes/receipt-main-session-fix-c1.md`.
