# Observations - harness-backend-dev

- 2026-09-05: FEAT-55 T-01 — the write tool with a relative path ("tests/unit/...") resolved against the OMP session default cwd (main checkout), not the dispatched worktree, even though the dispatch named the worktree root explicitly and other tool calls (bash cd) targeted it correctly. Caught before verify via git status in both trees; fixed by using the full absolute worktree path in the write call. Confirms G-18 applies to the write tool itself, not just bash/edit.
- 2026-09-05: T-07 (FEAT-55) — a bash fake gh that logs "$*" via `tr "\n" "\001"` to keep one call per log line leaves one trailing "\x01" on EVERY line too (echo's own newline is also translated) — a regex token extraction like `--label (\S+)` on the raw line then sees the last label as "bug\x01" not "bug". Strip it (`l.rstrip("\x01")`) when reading the log back, or a control assertion checking today's real, unrelated-to-the-feature behaviour fails for a fixture-artifact reason instead of passing.
- 2026-09-05 (T-08): T-07's case A vs case H are only reconcilable if freshly-created issues
  are typed inline ONLY on the run that also creates the parent (`need_parent_create` true);
  otherwise typing of a fresh task defers entirely to the ordinary pre-create backfill on a
  LATER invocation. A naive literal reading of the intent's step-8 prose ("create, then
  apply_issue_type, then True" for both parent and task) types every fresh issue inline on
  every run, which passes A/B/C/D/F/G/I/J but fails E (parent's own inline apply aborts the
  whole run via propagated GhError before the task loop ever starts, so the fixture's later
  assumption that all four issues already exist is violated) and H (T-02/T-03 end up already
  True by the end of run1, so run2's backfill finds nothing left to do and the check that
  specifically inspects run2's log fails). Confirmed by instrumenting a throwaway copy of the
  test file with debug prints of `read_factory()`/`read_log()` right after run1 in case_h.
- 2026-09-05 (T-08): `.claude/skills/harness/bin/feature-schema.json`'s `factory` object
  (`additionalProperties: false`, properties repo/parent/issues/items/edges only, ~line 88-90)
  genuinely blocks writing a `factory["typed"]` key — confirmed live: `write_feature_json`
  raises `harness_merge.MergeRefusal(11)` with message `undeclared key 'typed' at /factory`.
  This is not just cosmetic to the NEW T-08 test: it also breaks `test-factory-decompose.py`
  wholesale (163/163 -> 8/163 checks reached, exits 1) since nearly every one of its fixtures
  creates/adopts a parent, which now writes `typed`. Verified the rest of T-08's logic is
  correct using a throwaway permissive schema copy dropped at
  `$TMPDIR/.claude/skills/harness/bin/feature-schema.json` — `feature_schema.schema_path_for`
  walks up from any `tempfile.TemporaryDirectory()`-rooted `feature.json` path and finds it
  before falling back to the real repo copy, so this needs zero edits to any test file and
  touches no repo path. With it in place: T-08's own 10-case RED test (62/62) and
  `test-factory-decompose.py` (163/163) both pass clean; `tests/unit/test-factory-gh.py`
  (244/244) is unaffected either way (never touches feature.json).
- 2026-09-05: T-06 cmd_backlog — the red test forces a two-phase create-all-then-apply-all split (mirroring cmd_open + _backfill_issue_types), NOT a single per-item create-then-apply loop: FAKE_TYPE_APPLY=fail makes gh() call skip()->sys.exit(0) on the first apply failure, and an interleaved loop would abort before creating items 2/3 — CASE E of test-gh-backlog-issue-types.py asserts all three still get receipt entries after one failed run.
- 2026-09-05: T-06 backlog-issues.json is a FLAT {"nature:title": {"number","typed"}} map at the JSON top level, not the intent prose's {"items": {...}} nesting — test-gh-backlog-issue-types.py's read_receipt/seed_receipt read/write keys at the top level, and matching the non-editable test took precedence over the paraphrased intent wording.
- 2026-09-05: to smoke-test cmd_open (test-gh-issue-types.py) past feature-schema.json's pending additionalProperties:false/github.typed defect without touching the repo schema: feature_schema.schema_path_for walks up from the checked file toward the filesystem root looking for .claude/skills/harness/bin/feature-schema.json, so pointing TMPDIR at a scratch dir that itself holds that relative path (with a typed property added) makes tempfile.TemporaryDirectory()'s nested feature.json resolve to the override — a genuine no-repo-file schema override for this specific gate.
