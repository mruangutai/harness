# Goal-check c3 — does this plan deliver the operator's stated intent? YES — PASS, with three advisories.

Grade of `plan.yaml` at working state (post-`66be772b`) against the operator's 2026-09-11 amendment
and `notes/intake-BUG-285.md`. Every claim below was re-measured in this worktree today. The
signature question (`approval.status: approved` dated 2026-09-09 over a task set amended since) is
an open operator escalation and is deliberately NOT graded here.

## The seven checks

1. **T-01 survives unchanged — VERIFIED AT SOURCE.** `yaml.safe_load` of T-01 at `bb488145` (the
   signature commit) vs the current file: every key identical, whole-task equality `True`
   (`id, title, traces, change_type, execution_mode, execution_agent, depends_on, status, files,
   verify, intent`). Old plan carried one task; new carries three.
2. **T-02 fixes the real defect and preserves #208 — VERIFIED AT SOURCE.** `factory_decompose.py`
   measured: `try` `:120`, `doc = harness_yaml.load_file(path)` `:121`, `except
   harness_yaml.YamlParseError` `:122`, `refuse(...)` `:123`, isinstance guard `:124`, history
   comment `:116-119`, `import json` `:35`, `harness_yaml` still needed at `:480` (`load_plan`) —
   every line anchor in T-02's intent matches, no off-by-one. Intent item 3 keeps
   `factory_cli.refuse(TOOL, "feature.json invalid", path, f"does not load: {e}")` byte for byte;
   item 4 says the comment is UPDATED, never deleted, and must record the new arms; item 5 keeps the
   type guard. Propagation claim confirmed at `factory_cli.py:83-84` (`except SystemExit: raise`)
   with the generic leak at `:88-96`. `str()` of both `JSONDecodeError` and `UnicodeDecodeError`
   carries no class name (measured), so the preserved message cannot leak one.
3. **T-03 matches T-01's able-to-fail discipline — VERIFIED AT SOURCE.** Steps a–f: probe script and
   `shutil.copy` in a tempdir, reversion to `harness_yaml.load_file` as the whole mutant, real
   `BIN_DIR` at `sys.path[0]`, mutant-accepts/real-refuses assertions, transcripts left in
   `notes/qa-<runid>.md` for grading at the pinned sha. Fixture `"factory:\n  repo: owner/name\n"`
   is YAML-mapping / `json.loads` → `JSONDecodeError` (measured), and returns a well-formed factory
   block under the mutant, so an accepting probe proves it reached the parse branch (my O-06).
4. **Consequence (a) — D-03 RE-DERIVED, not carried forward — VERIFIED AT SOURCE.** Old D-03:
   "the only required kind is integration … touches_runtime_code is false here". New D-03 derives
   `touches_runtime_code = TRUE` from DEC-217 (`DECISIONS.md:6875-6880`: not under `tests/**`, not
   `*.md`, not under `.harness/`) — `.claude/skills/harness/bin/factory_decompose.py` satisfies all
   three, so the `unit` leg of `harness.json test_matrix.bugfix` fires and
   `fix_confined_to_tests_and_contract_docs` is now FALSE. All three tasks carry
   `change_type: bugfix`; the `unit` demand is discharged by T-03's `tests/unit/` file (DEC-213,
   directory selects kind, name free of the `tests/integration/` collision); `integration` is
   retained per DEC-35. `verify:` is a literal `|` block on all three.
   `check-plan-routes.py <plan>` → **exit 0, 0 violation(s)**. All 8 REQs traced (T-01 01–04,
   T-02 05–06, T-03 07–08).
5. **Consequence (b) — execution_agent correct per surface — VERIFIED AT SOURCE.** Checker output:
   `T-01 granted to backend-dev, dev-ops, qa` / `T-02 granted to backend-dev, dev-ops` (qa NOT
   granted) / `T-03 granted to backend-dev, dev-ops, qa`. Plan routes T-02 → `harness-backend-dev`,
   T-01/T-03 → `harness-qa`. Exactly the operator's (b). D-05 correctly records that no verb writes
   `lanes:` and that `execution_agent` + `check-domain.py` is what binds.
6. **Consequence (c) — BRIEF states the measured truth — VERIFIED AT SOURCE.** `BRIEF.md:3-36` names
   both readers separately: gh-sync "correct, unpinned" (`:8-16`, work is "a regression pin over
   already-correct code — worth having, but it fixes nothing") and factory_decompose "still
   defective" (`:18-27`), with the both-directions disagreement at `:29-36`. No false-premise
   sentence survives. The 79-file latent-divergence risk reaches a BRIEF-only reader under its own
   `## Risk` heading (`:89-103`), including that a corpus scan cannot serve as the able-to-fail
   proof. `SC-08`'s anchor re-measured: case `(1c)` is at `test-factory-decompose.py:426-437`.
7. **Nothing authorises unrequested work — VERIFIED AT SOURCE.** `files:` across the plan is exactly
   three paths: the gh-sync integration suite, `factory_decompose.py`, the new unit file. gh-sync.py
   is explicitly forbidden (T-01 intent, BRIEF Constraints); no corpus sweep, no `harness.json`
   edit, no fourth task. **Cycle cost recorded** — `feature.json cycles_used` 2 at `bb488145` → 5
   now, runs list carries the `amend` and `panelfix` ESCALATEs and the cycle-1 FAIL (DEC-157,
   honest record).

## Advisories — for the lead to route, NOT written into plan.yaml

- **PF-142f3a (low, open) does not reproduce at current state.** It claims the panelfix note's
  "check-plan-routes.py → exit 0, 0 violation(s)" fails to reproduce in this worktree; I measured
  exit 0 / 0 violations against the owner manifest today. The finding is stale or manifest-state
  dependent — the disposition needs a re-measure, not a fix.
- **PF-a5b9a3 (low, open) is a real letter-conflict and T-03's letter should win.** BRIEF SC-11 says
  "in one check"; T-03 check 4 mandates two named checks. T-03 is the dispatch the builder receives.
- **`code == EXIT_REFUSED` is non-discriminating alone** (`factory_cli.py:96` also exits
  `EXIT_REFUSED` from the generic handler). The stderr clauses in SC-11 / T-03 check 4 are what
  carry it — both are required, so this is a note, not a gap.
- **No task's `verify:` invokes `run-unit-tests.sh --kind integration`**; both integration suites are
  run by direct `python3` with a FAIL-line count asserted (stronger, per G-08). The declared kind
  runner is exercised by the qa gate, not by a task.

## Open questions

- None blocking. The `approval.status: approved` / amended-task-set mismatch is the operator's, and
  is out of this grade by dispatch.
