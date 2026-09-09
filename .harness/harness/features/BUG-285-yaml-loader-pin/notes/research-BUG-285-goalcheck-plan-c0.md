# does this plan deliver the operator's stated intent?

**Almost — yes on all four of the operator's own "done" items, but ONE required edit before
signature:** T-01 never tells the builder to COMMIT the probe transcript note, and SC-03 grades that
note with `git show <review_sha>:<note path>`. A correctly-executed proof left untracked grades
`not_met`. Graded against `notes/intake-BUG-285.md` section 1 (the operator's words), not the BRIEF.

## must_fix (one, in plan.yaml, before the operator signs)

- **File** `.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml`, **field** `tasks[T-01].intent`,
  **step f** (`plan.yaml:116-118`). Replacement wording for its first sentence:
  *"Record both transcripts verbatim, plus the exact commands you ran, in your own notes file under
  this feature's notes/ directory, and COMMIT that note with the test change — SC-03 is graded with
  `git show <review_sha>:<that path>`, so an uncommitted note grades not_met however good the proof."*
  Nothing else in the plan needs to change. (The feature directory is not gitignored and is currently
  untracked in this worktree — `git check-ignore` exit 1, `git status --porcelain` shows `??` on the
  whole dir — so committing is possible and is the only thing standing between a real proof and a
  false `not_met`.)

## 1. Scope — still one fixture in one file. Nothing widens it.

One task (`plan.yaml` `tasks:` length 1, verified by `safe_load`), `files: [tests/integration/test-gh-sync.py]`
(`plan.yaml:42-43`), `intent` forbids editing `gh-sync.py` or any other file (`plan.yaml:49-51`).
BRIEF `## Constraints` (`BRIEF.md:38-48`) repeats the boundary. The one non-narrow sentence,
`BRIEF.md:43-45` ("nothing may later introduce YAML-only syntax … into `feature_json_write`'s
output"), is a standing rule with no REQ, SC or task behind it — inert, not scope.

## 2. Mutant-red/real-green is REQUIRED, not prose — with one honest limit.

`SC-03` (`BRIEF.md:65-70`) is a criterion with `verify: inspection` and a named grading procedure;
`T-01 intent` steps a–f (`plan.yaml:99-118`) mandate the probe and the transcript. The limit: T-01's
`verify:` runs only the suite (`plan.yaml:44-45`), so the probe is gated by SC-03's inspection of the
note — which is exactly the must_fix above. `REQ-02`/`SC-01`'s two-directional fixture checks
(`BRIEF.md:28-30`, `56-60`) are the re-runnable half and are in the suite.

## 3. T-01 is buildable with no further questions. Every anchor it cites is real.

Test file: `sys.path` insert :16, `json`/`os` :17-18, `harness_yaml` :25, `nested_feature_dir` :144,
`check()` :769, `_ghs` load :1406-1410, insertion point after the check ending :1442 and before the
`fix1 Part B` comment at :1444 (both literal strings present verbatim), neighbour idiom :1474-1480,
zero-byte fixture :1470-1473+. Reader: `load_recorded` `gh-sync.py:484`, `json.loads(text)` :523,
`does not parse` SystemExit :524-531 (message carries the full path), `isinstance` guard :535,
`import harness_yaml` :101, `harness_yaml.load_str(text, where)` `harness_yaml.py:207`. Nothing
drifted. Two feasibility points confirmed here, not assumed: `json.loads` on the block mapping raises
`JSONDecodeError` (a `ValueError`, so step 2's assertion type is right), and a `shutil.copy` of
`gh-sync.py` into a tempdir imports cleanly and exposes `load_recorded` — because `gh-sync.py:88-89`
inserts its own dir at `sys.path[0]` while the probe's real `BIN_DIR` stays at index 1, so the
siblings still resolve. Under the mutant the fixture reaches `:544-554` and yields `parent == 40`,
which is what step e asserts.

## 4. Nothing authorises an unasked production change.

`BRIEF.md:38-40` makes a red assertion a finding for the operator, not a licence to edit `gh-sync.py`;
`plan.yaml:49-51` forbids the edit; `D-04` (`plan.yaml:28-31`) and intent steps b–d confine the mutant
to a `shutil.copy` in a tempdir, naming the symlink-single-inode reason; step f requires the tempdir
and script deleted and nothing under `tests/` or `.claude/` left changed.

## Mechanical checks

`approval.status: pending` in both (`plan.yaml:3-4`, `BRIEF.md:91-95`); exactly one task; no `panel:`
key (`safe_load` top-level keys: approval, decisions, feature, lanes, schema, source_issues, status,
tasks); every decision scalar's tail survives `safe_load` (no truncating inline `#`);
`check-plan-routes.py <this plan>` → `OK T-01 granted to harness-backend-dev, harness-dev-ops,
harness-qa`, 0 violations, exit 0 — matching the recorded `team` lane.

## Advisory (do not gate)

- `SC-04` says "at least 318 `ok`" (`BRIEF.md:71-76`); T-01 says "more than 318" (`plan.yaml:122-123`).
  Both hold once the new checks land; no edit needed.
- No open question for the operator. No suite was run and nothing was edited by this goal-check.
