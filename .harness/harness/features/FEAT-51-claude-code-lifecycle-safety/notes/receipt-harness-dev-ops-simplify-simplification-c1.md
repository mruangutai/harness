# SIMPLIFY — SIMPLIFICATION angle — FEAT-51 — c1

**BLUF:** One real finding, the one already pre-located: `COLLECT_FIXTURE` in
`test-harness-yaml.py` restates a 9-element `shared` list verbatim six times. Fix: hoist to one
module-level constant, reference it six times, keep six independent comparisons. `applicable:
writable`. No other simplification finding survived a read of the rest of the writable diff
(`quarantine.py`, `test-quarantine.py`, `test-gen-decisions-index.py`, `run-unit-tests.sh`,
`harness.json`) — comments there state present facts or justify anchoring, not narrate change,
and no redundant conjuncts or unnecessary pipelines were found. `findings_count: 1`.

## Finding 1 — `COLLECT_FIXTURE`'s `shared` tuple repeated 6× verbatim

- **File:** `.claude/skills/harness/bin/test-harness-yaml.py`
- **Line anchor:** `COLLECT_FIXTURE = {` at line 31; the repeated `shared` list appears at
  lines 41-45 (`harness-backend-dev`), 58-62 (`harness-dev-ops`), 77-81 (`harness-pm`), 94-98
  (`harness-documentor`), 117-121 (`harness-eng-lead`), 132-136 (`harness-orchestrator`).
- **Verified identical:** all six copies are byte-identical:
  ```
  [
      ".harness/*/features/*/quarantine/**",
      "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
      "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
  ]
  ```
- **Concrete cost:** a seventh agent, or a change to any one of the nine shared-manifest
  paths, requires editing six sites by hand — this fix cycle already had to do exactly that.
  Worse, `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` (line ~194)
  iterates `COLLECT_FIXTURE.items()` in a plain `for` loop with a bare `assert`: the FIRST
  agent whose `shared` mismatches raises and aborts the loop, so the other five copies are
  never compared in that run. A hand-edit that updates five of six sites correctly and slips
  on the sixth is invisible unless that sixth agent happens to sort first.
- **Alternative (exact edit):**
  1. Add a module-level constant directly above `COLLECT_FIXTURE` (after the D-03 fixture
     comment block, i.e. immediately before line 31):
     ```python
     # The nine `shared` manifest paths every agent's row repeats verbatim below. One
     # literal list, not derived from harness_yaml — same reason the fixture as a whole is
     # inlined (see the comment above): this must catch harness_yaml disagreeing with the
     # manifest, not agree with it by construction.
     SHARED_MANIFEST_PATHS = [
         ".harness/*/features/*/quarantine/**",
         "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
         "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
     ]
     ```
  2. Replace each of the six inline 5-line `shared` lists with `SHARED_MANIFEST_PATHS`, e.g.
     line pair for `harness-backend-dev` (currently lines 41-45) becomes:
     ```python
         SHARED_MANIFEST_PATHS,
     ```
     — same for the other five agents, each site becoming a single reference line instead of
     five literal lines.
  3. No change to `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`: it
     still calls `hy.manifest_domains(MANIFEST_PATH, agent)` and compares against
     `expected_shared` per agent inside the same `for agent, (expected_mine, expected_shared)
     in COLLECT_FIXTURE.items():` loop — **six iterations, six independent `assert list(shared)
     == expected_shared` comparisons**, unchanged in count or order. Each iteration still reads
     its own tuple element from `COLLECT_FIXTURE[agent]`; only the *literal that populates* that
     element moves out of six textual copies into one, so the comparison the loop performs
     against the module under test is untouched.
- **Property preserved:** the fixture's own comment (lines 27-30) says the values are inlined
  deliberately, independent of `harness_yaml`, "not derived from `harness_yaml` — that would
  prove nothing." `SHARED_MANIFEST_PATHS` is still a plain Python literal defined in the test
  file itself, never computed from `harness_yaml.manifest_domains` or from
  `.harness/team-config.yaml` — it is the exact same nine strings, just written once instead
  of six times. The independence the fixture fought for is unchanged; only the six-fold
  textual restatement is removed.
- **applicable: writable** — `test-harness-yaml.py` is squad-writable per the manifest (not in
  the DEC-174 no-edit set), so this can be applied directly.

## Other candidates considered, not flagged

- `quarantine.py`'s three `cmd_*` handlers (`cmd_list`, `cmd_adopt`, `cmd_discard`) each open
  with an identical 3-line "no checkout root" guard (lines 82-84, 102-104, 152-154). This is
  restated code, not restated *fact-through-different-spellings* — it is REUSE-angle territory
  (a helper restated where one could be extracted), not SIMPLIFICATION's target. Left for the
  Reuse reader; not claimed here to avoid double-counting across the two independent passes.
- `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` comment block (lines 19-29) and
  `--check-kinds` comment (lines 40-42) both state present facts and measured numbers, not
  change narration ("now we also…", "previously…") — no finding.
- `test-gen-decisions-index.py`'s new `QUARANTINE_DEC`/`_dec_region`/three `test_dec_210_*`
  functions: docstrings state present invariants and reasons for the check's shape (e.g. "so
  the clauses that hold never blind the check to the one that does not"), not a narration of
  what changed. No redundant conjuncts found in the three new test bodies — each `if` guards a
  genuinely distinct failure mode (missing heading, missing tool name, missing sentence
  co-occurrence, missing index-row ruling text).
- `.harness/harness.json`'s `integration.detect` diff is a single mechanical append of
  `test-quarantine.py` to the existing pipe-delimited list, mirroring every other test file's
  entry — no restatement or drift risk introduced.
- `test-quarantine.py`: eight case functions, each with its own `fixture_root()` +
  `quarantine_dir()` setup calls (already factored as helpers) and one dedicated assertion
  block. No duplicate fact-restatement across cases — each case's `check()` calls test a
  distinct outcome (union+approval-carry-forward, BRIEF replace, illegal-basename refusal,
  directory-scoped discard, path-outside-quarantine refusal, list-is-read-only, empty-list
  silence).
