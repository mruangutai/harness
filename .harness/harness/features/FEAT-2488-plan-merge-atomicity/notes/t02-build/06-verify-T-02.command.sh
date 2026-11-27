python3 .claude/skills/harness/bin/run_pool.py --workers 4 tests/integration/test-plan-merge.py tests/integration/test-check-state-feat59.py tests/integration/test-feature-json-merge.py tests/integration/test-plan-decision-dispositions.py tests/unit/test-plan-merge-first-station.py tests/unit/test-plan-merge-union-head.py tests/unit/test-harness-merge-journal.py tests/integration/test-harness-merge.py tests/integration/test-observations-merge.py tests/integration/test-expertise-merge.py tests/integration/test-inflight-registry.py && python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit && python3 - <<'PY'
import pathlib
b = pathlib.Path('.claude/skills/harness/bin')
mods = sorted((b / 'plan_merge').glob('*.py'))
assert 10 <= len(mods), mods
for m in mods:
    t = m.read_text()
    assert 'mkstemp' not in t and 'os.replace' not in t, m
    assert 'harness-merge.journal' not in t and 'JOURNAL_SUFFIX' not in t, m
g = (b / 'plan_merge' / 'guards.py').read_text()
assert 'def _replace_bytes' not in g and 'def _restore_plan' not in g and 'recover_journals(' in g
a = (b / 'plan_merge' / 'amend.py').read_text()
assert 'APPROVAL_RESET_LINE' not in a and 'result["reset"]' not in a and 'result.get("reset")' not in a
am = (b / 'plan_merge' / 'amendments.py').read_text()
assert 'harness_merge.locked_pair_update(' in am and 'JournalPending' in am and '_restore_plan' not in am
doc = (b / 'feature_json_write.py').read_text().split('"""')[1]
assert 'the fsync' not in doc and 'fsync' in doc
assert 'intent journal' in (b / 'plan-merge.py').read_text()
print('PASS no rename primitive or journal handling in plan_merge; reset bookkeeping and false fsync claim gone')
PY
