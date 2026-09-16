# Validator fix c1 evidence — F-01 and F-04

Starting commit: `441309edf44ff3ff46713049fe630ff671cd8329`  
Strict-accounting commit: `0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800`

## F-01 — canonical-module accounting

Hypothesis: `_candidate_is_accounted` accepted every candidate whose file was
`artifact_accessors.py`, independently of the checked-in classification. A
self-test supplying an unclassified raw parse candidate at that path would
therefore fail before the shortcut was removed. This was falsifiable: the
unchanged audit would instead have reported the candidate with its exact
category-specific remedy and `PLAN AMENDMENT REQUIRED`.

The regression test was added first, while the production source remained at
starting commit `441309edf44ff3ff46713049fe630ff671cd8329`.

Command:

```text
python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test
```

Pre-fix result: exit `1`.

```text
FAIL canonical_reader_unclassified_accessor_module_call_is_rejected []
1 FAILURE(S): ['canonical_reader_unclassified_accessor_module_call_is_rejected']
```

After removing the file-wide shortcut, the audit initially named all seven
previously hidden canonical-module candidates. Four are accounted for by their
checked-in relocated implementation rows; the three native primitives now have
explicit checked-in exemptions with reasons. The same command then exited `0`:

```text
PASS canonical_reader_unclassified_accessor_module_call_is_rejected
ALL PASS
```

The production helper `_candidate_matches_relocated_row` grades `5` against a
bar of `4`; the new test grades `4` against a bar of `3`.

## F-04 — complete enforcement-output equivalence

The retired comparator and 29-case baseline were loaded unmodified from
historical commit `0259fce02d6196be92c94edb2cb4ec8c60cd0997`.
The target was exact strict-accounting commit
`0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800`. The historical module's `ROOT`
was rebound to the canonical worktree path captured by the baseline; its
comparison and normalization functions were not changed. Nothing was restored
to the shipping tree.

Proof-input SHA-256 values:

```text
e65599733cd2edbb91fdab37450ed627b0c7124953bb2fa2f3e2f43628fd33a5  historical test-check-plan-routes.py
6a480ca2498378ed020546df2334e410ee14cfef015e7e108ab33eaddce5ebce  historical baseline and copied /tmp baseline
```

Python evaluator body used for the successful comparison:

```python
import importlib.util
historical_test = "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-f04-evidence/tests/integration/test-check-plan-routes.py"
spec = importlib.util.spec_from_file_location("bug285_historical_comparator", historical_test)
historical_comparator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(historical_comparator)
historical_comparator.ROOT = "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader"
comparison_exit_committed = historical_comparator.verify_enforcement_bytes("/tmp/bug285-f04-baseline.json")
print(f"target=0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800 exit={comparison_exit_committed}")
```

Result:

```text
PASS 29 legacy enforcement baseline(s)
target=0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800 exit=0
```

To prove the assertion itself can fail, this exact command made one deliberate
expected-stdout divergence outside the repository:

```text
python3 -c 'import json, pathlib; source=pathlib.Path("tests/integration/canonical-reader-enforcement-baselines.json"); document=json.loads(source.read_text()); document["cases"][0]["stdout"] += "DELIBERATE-DIVERGENCE\n"; pathlib.Path("/tmp/bug285-f04-divergent-baseline.json").write_text(json.dumps(document, indent=2) + "\n")'
```

The divergent input SHA-256 was
`eb6837b741dc98343671974f36085c56c4f9112d968023f09735a6b0d4b312e9`.
Running the same historical comparator against that path produced:

```text
ENFORCEMENT BYTE MISMATCH test-check-omp-port: changed stdout
target=0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800 exit=1
```

The temporary baseline and `--verify-enforcement-bytes` mode remain absent from
the shipping tree.

## Green gates

The exact signed T-01 command exited `0`. The signed T-07 baseline-absence
predicate and retired-mode search both passed, followed by its complete ordered
Python command chain exiting `0`. Key terminal output:

```text
PASS canonical reader classification T-07
ALL PASS
0 unresolved reader site(s) across 69 Python file(s)
```

`git diff --check` was clean. The canonical state checker was run before the
strict-accounting commit; it reported only existing feature/fleet state debt:
two recorded FAIL cycles with `cycles_used=0`, the feature at Review without
`handoff-build.md`, and the standing terminal BUG-1563 worktree.
