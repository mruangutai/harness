# Gate report — check-state.sh vs baseline (FEAT-05-build s7)

**Verdict: gate is green against baseline.** No defect found. Measurement only, nothing changed.

## Invocation (verbatim)

```
CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh; echo $?
```

## Result

- **Exit code:** `0`
- **Violation count:** `0` (`grep -c VIOLATION` on the output → 0)
- **Note count:** `40` (`grep -c "^  note"` → 40)

## Note-set diff against the recorded baseline (39, all INV-8 pruned-run-dir)

Baseline (`feature.yaml:28-31`, measured post-approval at `225cc98`): exit 0, 0 violations, 39
notes, all INV-8 pruned-run-dir.

This run: same 39 baseline notes present verbatim (FEAT-01, FEAT-02, FEAT-03-subissue-mirror,
FEAT-04-decisions-index pruned-run-dir notes — spot-checked, all still there), **plus exactly one
new note**:

```
note       FEAT-05-pyyaml-file-parsers: run dir 2026-08-03-04-eng exists on disk but feature.yaml
does not record it — orphaned work (interrupted flow?). A resume must reconcile it, not rediscover
it by luck.
```

This is the expected INV-8 orphaned-run-dir note naming this run's own directory
(`runs/2026-08-03-04-eng/`), consistent with the brief's prediction: recording the run in
`feature.yaml`'s `runs:` list is the orchestrator's write, not this agent's, so its absence at
measurement time is expected and correct — not a defect.

**Diff verdict:** membership matches expectation exactly (39 baseline + 1 new orphaned-run note =
40). No unexpected notes, no missing notes, no changed severities.

## Confirmation of the one delta

`check-state.sh` at this commit still uses the regex-based parser for this check (not converted in
this run), so the invalid `team-config.yaml:18` YAML does not affect it — confirmed: exit 0,
0 violations, as predicted.

## Unrelated context (not part of this gate, reported per task instructions)

`run-unit-tests.sh` overall suite is red: `test-harness-yaml.py` fails on
`test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` — parse error at
`.harness/team-config.yaml:18` ("while parsing a flow sequence... expected ',' or ']', but got
'<scalar>'"). This predates this task and is the known blocker named in the dispatch; not fixed
here, not in scope.
