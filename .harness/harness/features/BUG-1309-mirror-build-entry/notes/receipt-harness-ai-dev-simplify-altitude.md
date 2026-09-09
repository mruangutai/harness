# ALTITUDE pass — BUG-1309-mirror-build-entry

BLUF: one real fold-in candidate — the terminal build-entry allow-set is a literal spelled
independently in two Python modules with no shared authority, even though a natural home
(`feature_schema.py`, which already hosts the sibling `BUILD_ENTRY_ERA_EXEMPT` constant) exists
and is already imported by both sites. Everything else checked (the station classifier's home,
`cmd_start_task`'s refusal placement, the fail-open posture, doctrine placement) sits at the
right depth or is a briefing-row, not an apply.

## Findings, ranked

### 1. [HIGHEST VALUE] Terminal build-entry set restated as two independent Python literals — `fold-in`

- **File/line:** `.claude/skills/harness/bin/merge-gate.py:135` and
  `.claude/skills/harness/bin/post-merge-sweep.sh:228` (the embedded Python).
- **Summary:** Both sites independently spell the literal
  `{"opened", "not-applicable", "recovered-terminal"}` — "what counts as a terminal, safe
  build-entry outcome" — as an inline frozenset, with no shared name between them.
- **Concrete cost:** a fifth (or sixth) recorded outcome added later — the schema enum already
  lists four (`feature-schema.json:98`) — must be reflected in both literals by hand; miss one and
  merge-gate and post-merge-sweep silently disagree about which features are safe to
  merge/retain, with no test that cross-checks the two spellings against each other (only against
  each module's own behaviour — `tests/integration/test-merge-gate.py:70`,
  `tests/integration/test-check-state.py` — so drift between the two files is invisible to CI).
- **Alternative:** add one module-level constant next to `BUILD_ENTRY_ERA_EXEMPT` in
  `feature_schema.py` (e.g. `BUILD_ENTRY_TERMINAL_STATES = frozenset({"opened",
  "not-applicable", "recovered-terminal"})`), and have `merge-gate.py:135` and
  `post-merge-sweep.sh:228` reference it instead of the inline set literal. Both files already
  `import feature_schema` for `BUILD_ENTRY_ERA_EXEMPT`/`recovery_command_for`, so this is a
  same-shape, mechanical, behavior-preserving change — no test asserts the raw string text, every
  existing case exercises the constant's *membership behaviour*, so nothing needs to move. Does
  not reopen T-11's case set, D-12's heredoc refusal, or the frozen era set.

### 2. gh-sync.py's own "all valid build_entry values" tuple is a third independent spelling — `briefing-row`

- **File/line:** `.claude/skills/harness/bin/gh-sync.py:625-626`.
- **Summary:** `gh-sync.py` separately spells the full four-value enum
  (`"opened", "recovery-required", "not-applicable", "recovered-terminal"`) as a tuple, matching
  `feature-schema.json:98`'s schema enum but stated nowhere as a named constant either.
- **Concrete cost:** the same "add a fifth value" scenario requires updating this tuple too, and
  it is semantically a different set (all valid values, not just terminal ones) from finding #1's
  set — folding it into the same constant would be wrong, and folding it into a new *second*
  constant in the same pass would exceed the one-fix ceiling this pass already documents.
- **Alternative:** a follow-up `BUILD_ENTRY_VALID_STATES` constant in `feature_schema.py`,
  applied separately from finding #1. Filed as a backlog row rather than bundled into #1's apply.

### 3. `feature_schema.py` hosting a station-classifier (`recovery_command_for`) alongside schema validation — `leave`

- **File/line:** `.claude/skills/harness/bin/feature_schema.py:324-338`.
- **Deletion test:** delete `recovery_command_for` and the branching logic (plan status, any-task-done)
  reappears at all three call sites that read it — `gh-sync.py:1362`, `merge-gate.py:143`,
  `check-state.sh:2011` — so it is earning its keep, not a pass-through.
  Two-or-more real adapters already exist (three call sites), so the seam is real, not
  hypothetical.
- **Judgment:** `feature_schema.py` already owns the sibling fact (`BUILD_ENTRY_ERA_EXEMPT`) and
  the directory-name parsing (`_feature_dir_name`) this classifier depends on, so co-locating the
  classifier keeps the whole "what does a recorded/absent build_entry mean" fact in one module
  rather than splitting it across two for no consuming benefit. The module is drifting from pure
  JSON-schema validation toward a broader "feature.json domain facts" module, which is worth
  naming for a future rename/split if it keeps growing, but moving it now is a rename with no
  behavioral or locality gain and no second module already exists to receive it — leaving it
  would not reopen a settled scope, and moving it would be pure churn.

### 4. `cmd_start_task`'s Build refusal — `leave`

- **File/line:** `.claude/skills/harness/bin/gh-sync.py:1357-1369` (`_build_entry_preflight`),
  called from `cmd_start_task:1452`.
- **Judgment:** D-06 (`plan.yaml:98-101`, DEC-174) specifically requires the refusal to live in
  `cmd_start_task`, "the one chokepoint every team and main-session task passes through at build
  time." The implementation matches exactly: one helper, called first thing inside that function,
  refusing at exit 2. This is the decision's home, not a special case bolted onto shared
  infrastructure — no finding.

### 5. Doctrine restated in `SKILL.md` and `github-mirror.md` — `leave`

- **File/line:** `.claude/skills/harness/SKILL.md:141-144` vs.
  `.claude/skills/harness/references/github-mirror.md:51-55`.
- **Judgment:** `SKILL.md` states only the *behavioral contract* (refuses at exit 2 when absent,
  `recovery-required` gates merge) with no enumerated literal values; `github-mirror.md` is the
  cited full reference and is the only place the four literal value names appear in prose. This
  matches the file's own stated convention (line 3-5: "this file is the whole contract... the
  orchestrator playbook carries only a pointer") applied consistently elsewhere in `SKILL.md` —
  not a new drift risk this diff introduces, so not flagged.

### 6. `merge-gate.py`'s fail-open path (D-07) — `leave`

- **File/line:** `.claude/skills/harness/bin/merge-gate.py:136-138`.
- **Judgment:** the "could not verify" branch is the honest posture D-07 argues for (GitHub is a
  mirror and never a gate, DEC-138) stated inline at the one site that reads the `gh` failure —
  not a symptom-patching workaround. The gate's standalone existence and this posture are both
  settled ground; no finding.

## Not re-flagged (settled ground checked and skipped)

T-11's 18 unit cases, D-12's heredoc-extraction refusal, the standalone merge-gate process,
`BUILD_ENTRY_ERA_EXEMPT`'s frozen membership and "era" wording — read, matched against the diff,
not re-proposed.
