# REUSE angle — FEAT-45-adversarial-plan-panel

Scope: `git -C .claude/worktrees/harness/FEAT-45-adversarial-plan-panel diff 1d3e5db..HEAD`.

## Examined

- `panel_findings.py` (identity: `normalize_summary`, `finding_id`, CLI `id` subcommand)
- `check-state.sh`'s INV-32 branch (lines ~174-238)
- `test-panel-findings.py` (all 6 cases + CLI harness)
- `test-plan-panel.py` (all 8 numbered assertion groups)
- `test-check-state.py`'s INV-32 addition (`_inv32_plan`, `_inv32_run`, `case_inv32`, incl. the
  inv32-red mutation)
- `test-team-catalog.py` (pre-existing, unchanged by this diff — read as the reuse baseline)
- `test-harness-yaml-corpus.py`'s diff (`TEAMS_EXPECTED` 2→3, comment rewrite)
- `sync-agent-adapters.py`'s `SPAWNS` addition and `run-unit-tests.sh`'s `UNIT_SCRIPTS` append
- `plan-panel.yaml`, `.omp/agents/harness-validator-lead.md`, `.claude/agents/harness-validator-lead.md`
- `harness-spec-driven/SKILL.md`'s panel-transcription passage
- grepped the whole worktree for `hashlib|sha256\(` and for a second `\s+`/`.lower()`/`.strip()`
  normalization pattern

## Findings

### Finding 1

- **file**: `.claude/skills/harness/bin/test-plan-panel.py`
- **line**: 38-72 (`REPO`, `TEAMS`, `BIN`, `SKILL_MD`, `check()`, `read()`)
- **summary**: New file restates the repo-root resolution, path constants, and check-counting
  scaffolding that `test-team-catalog.py:41-66` (pre-existing, untouched by this diff) already
  defines line-for-line: same `REPO = (os.environ.get("HARNESS_PROJECT_DIR") or
  os.environ.get("CLAUDE_PROJECT_DIR")) or os.getcwd()` fallback, same `TEAMS`/`BIN`/`SKILL_MD`
  joins, same `check(name, ok, detail)` counted-not-literal-total pattern (identical comment:
  "Counted, never a literal total: a frozen count reddens the moment a case is added."), same
  `read(path)` one-liner.
- **cost**: Two independent copies of the repo-root/env-var fallback and the pass/fail-counting
  harness now have to be edited in lockstep. If `HARNESS_PROJECT_DIR`/`CLAUDE_PROJECT_DIR`
  resolution ever needs a third fallback (e.g. a worktree-relative default), or if the `check()`
  counter format changes (its output line is itself grepped by CI log tooling), one of the two
  files is the one an editor forgets — most plausibly `test-plan-panel.py`, since it is the newer
  and less-visited of the pair, and its copy would then silently keep counting/resolving the old
  way while `test-team-catalog.py` moved on.
- **alternative**: Factor `REPO`/`TEAMS`/`BIN`/`SKILL_MD` resolution and the `check()`/`read()`
  pair into a small shared test-helper module (e.g. `bin/harness_test_support.py`) that both
  `test-team-catalog.py` and `test-plan-panel.py` import, the same way both already import
  `harness_yaml` for parsing. Given D-05/INV-32 are pinned scope, this touches only the two test
  files' own scaffolding, not any assertion content.
- **appliable**: true (`test-plan-panel.py` is in-grant; `test-team-catalog.py` is not touched by
  this diff and is also in-grant by the same `bin/` resolution — but note SIMPLIFICATION/ALTITUDE
  readers may already be weighing whether this fold-in is worth the apply-cycle ceiling; if so,
  defer to whichever angle's finding this dedupes against and treat this as the reuse half of
  that pair).

## What was NOT found (the panel_findings.py identity check, run to completion)

`panel_findings.py`'s module docstring names itself "the ONE place a finding's identity is
computed." Grepped the whole worktree for a second sha256/hashing of a finding summary and for a
second `\s+`-collapse/`.lower()`/`.strip()` normalization:

- `check-state.sh`'s INV-32 branch never recomputes an id — it only reads `item.get("id")` and
  `ruling.get("finding")` as opaque strings and compares them against the recorded finding-id set.
  No re-implementation.
- `test-check-state.py`'s `_inv32_plan`/`case_inv32` fixtures use a literal `fid = "PF-deadbeef"`
  string, never re-derived from `finding_id()` — but since `check-state.sh` treats ids as opaque,
  this is a fixture value, not a second identity rule, and does not qualify as reuse drift.
- `harness-spec-driven/SKILL.md` and both `harness-validator-lead.md` copies explicitly delegate
  id computation to the CLI ("Compute every id with `python3 …/panel_findings.py id --reader <r>
  --summary <s>`; never type it" / "pm computes it once with `panel_findings.py`") and describe
  the lead's own "de-duplicate on normalized summary plus reader id" step as an LLM judgment call
  over candidate findings, not a second coded hash — no second spelling of D-05's rule.
- The only other `hashlib`/`sha256` hit in the whole worktree is `test-factory-decompose.py`,
  a directory-tree file-hasher for an unrelated purpose (detecting incidental file drift during a
  decompose run), pre-dating this feature and untouched by it.

`sync-agent-adapters.py`'s `SPAWNS["harness-validator-lead"]` addition and `run-unit-tests.sh`'s
`UNIT_SCRIPTS` append both extend pre-existing lists in place, using the pre-existing convention
(no new enumeration mechanism introduced). `test-harness-yaml-corpus.py`'s `TEAMS_EXPECTED`
2→3 change is a constant bump with rationale, not a new fixture. None of these are findings.

## Conclusion

One reuse finding: `test-plan-panel.py` re-implements `test-team-catalog.py`'s scaffolding
(repo-root resolution, path constants, check-counter) instead of sharing it. The identity module
this feature exists to centralize (`panel_findings.py`) is, in fact, the single source — every
consumer checked (gate, doctrine, tests) delegates to it or treats its output as opaque.
