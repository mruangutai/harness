# Observations — harness-backend-dev — FEAT-05-pyyaml-file-parsers

- 2026-08-03: computed the D-03 `collect()` fixture by extracting check-domain.sh's exact regex
  walk into a standalone script and running it against the real `.harness/team-config.yaml`, rather
  than hand-tracing the regex — a hand trace matched on this pass but is the wrong default; the
  extracted-and-run approach is worth reusing for any future "prove old and new logic agree" test.
- 2026-08-03: `require_or_bootstrap`'s signature isn't pinned in PLAN.md beyond `(root)` — a hook
  needs stdin JSON for session identity, but tests need deterministic control. Settled on
  `(root, payload=None)` where `None` means "read stdin" and tests pass an explicit dict. T-03 should
  follow this or raise a plan revision, not silently diverge.
- 2026-08-03: the D-03 fixture's first draft only covered `teams[].members[]` agents (backend-dev,
  dev-ops, pm, documentor) and would have let a `manifest_domains` that walks only that path pass
  while silently returning empty `mine` for `leads:` entries and the bare top-level `orchestrator:`
  block — both nest differently and both are real callers via `check-domain.sh`/`bash-write-guard.sh`.
  Added `harness-eng-lead` and `harness-orchestrator` rows. When proving old/new logic equivalent,
  the fixture set must span every distinct nesting shape the walked structure contains, not just the
  shapes the brief happened to name.
- 2026-08-03: T-03 corrected T-02's receipt on `require_or_bootstrap`'s stdin plan (dispatch verified
  at `check-domain.sh:232-234` — a payload piped alongside `python3 - <<'PY'` is lost because `python3
  -` takes its *program* from stdin). Built `payload=None` to mean "parse `HOOK_PAYLOAD` env var",
  never stdin. `check-domain.sh:97`'s call site (T-12 converts) passes no `HOOK_PAYLOAD` at all, so
  identity there resolves only through the env-var chain tail — worth re-checking at T-12 time.
- 2026-08-03: `.harness/team-config.yaml:18`'s `main_session.writes` flow sequence contains
  ` ## Approval` twice — stock PyYAML treats a whitespace-preceded `#` as a comment start even inside
  `[...]`, so the bracket never closes and the WHOLE document fails to parse (verified with a bare
  `yaml.safe_load`, independent of this module's stricter loader). `main_session` has no `name:`/
  `domain:` keys so `manifest_domains` never reads that subtree, but `load_file` parses the whole
  document up front, so this one line currently blocks the real-manifest equivalence test entirely.
  Not fixed here — `team-config.yaml` is outside every dev's domain; raised as `open_questions`
  instead. Surveyed the same hazard elsewhere (read-only): `.harness/features/FEAT-03-subissue-mirror/
  feature.yaml`, `FEAT-04-decisions-index/feature.yaml`, and this feature's own `feature.yaml` also
  fail a bare `yaml.safe_load` (different causes — stray backtick, bad simple key, `mapping values
  not allowed here`). None of the four committed `state.yaml` files under this feature carry a
  duplicate `cost:` key (the "2 cost: keys" message in the cost-report suite output is from that
  test's own synthetic tmp fixtures, not real repo data).
- 2026-08-03: T-09 pitfall, caught by an advisor review, not by my own first pass: running a hook
  script's own test harness with `CLAUDE_PROJECT_DIR=$(pwd)` forced manually is a SYNTHETIC
  subprocess invocation, not evidence about what Claude Code's real `PreToolUse` dispatch does.
  I initially read 6 probe appends from that forced run as proof the worktree's `check-domain.sh`
  executes for real Writes — wrong. Two subsequent genuine `Write`/`Edit` tool calls (no env
  override) produced zero appends anywhere. Net finding: the real hook likely resolves to the
  MAIN CHECKOUT's copy here too (consistent with PLAN Q6's digest-validator finding), reversing
  my first-pass conclusion. Rule: to test what a `${CLAUDE_PROJECT_DIR}`-templated hook actually
  does, trigger it via the real tool call the hook is registered for — never via a test script
  that sets the env var itself.
