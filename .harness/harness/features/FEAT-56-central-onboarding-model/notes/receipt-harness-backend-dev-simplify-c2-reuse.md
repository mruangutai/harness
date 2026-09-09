# SIMPLIFY-C2 · REUSE angle · FEAT-56

Scope: `git diff 4b5dbb23..HEAD`, read-only. No repo file touched other than this receipt.

## Item 2 — root resolver (explicit verdict)

**Held for every touched script except one.** `factory_config.py` (35, 58, 437) and
`check-instruction-paths.py` (10, 143) both resolve root via the canonical
`harness_boundary.resolve_root(_BIN_DIR)` (`harness_boundary.py`). All other message-only
diffs (`check-domain.sh`, `check-state.sh`, `gh-sync.py`, `layout_migration.py`,
`post-merge-sweep.sh`, `upgrade-config.py`) touch prose only and leave their existing
`harness_boundary` calls untouched.

**`sync-command-adapters.py` does not call `harness_boundary.resolve_root`.** Its `--root`
default at line 61 (`Path(__file__).resolve().parents[4]`) hand-rolls the walk. But this is
not a *new* scheme: it is byte-identical to the sibling's own pre-existing, unmodified default
at `sync-agent-adapters.py:286` — that file predates FEAT-42's shared-resolver convention and
was not touched by this diff. So the dispatch's forbiddance against inventing a *second,
divergent* resolver held; what it did not do was migrate this adapter-sync pair onto the
canonical one. See REUSE-2 below.

## Item 1 — sync-command-adapters.py vs sync-agent-adapters.py (decided: faithful sibling)

Function by function:
- `canonical_paths`/`expected_adapters`/`bootstrap*`/`claude_adapter`/`parse_*`/`render` in
  the agent file: **no analog** in the command file — commands carry no frontmatter, so there
  is nothing to parse/transform/validate/bootstrap. This is the bulk of the agent file (~190
  of its ~230 meaningful lines) and genuinely does not apply to commands.
- `sync()`: materially the same control flow — resolve two dirs, diff expected vs actual by
  name, write/delete on `--apply`, collect `drift`. ~15 of 17 lines are the same shape modulo
  dir names/glob pattern; the only behavioral difference is the command version prints an
  "Updated …" line on apply and the agent version returns silently.
- `main()`: same shape — argparse, mutually-exclusive `--apply`/`--check` (agent adds a third
  `--bootstrap-from-claude`), `--root` default, try/except printing a prefixed error and
  returning 2. ~9 of 13 lines identical modulo the extra bootstrap branch and a wider except
  tuple in the agent version (it also catches `ValueError`/`yaml.YAMLError`, which command
  doesn't need since it never parses YAML).

**Verdict: faithful sibling.** ~24–25 lines of `sync()`+`main()` are substantively shared
control flow; the rest (frontmatter parsing, transformation, bootstrap, validation) is
genuinely different and dominates the agent file. Per the skill's own framing this is the
cheap, honest cost of two independent surfaces — not a near-duplicate. See REUSE-1 for the
optional (non-blocking) extraction this makes possible.

## Item 3 — check-omp-port.py's two door blocks (decided: one shape)

Both blocks (156–166 agent, 172–182 command) do exactly the same thing: resolve a fixed
script path under `.agents/skills/harness/bin/`, run it `--root <root> --check`, and on
non-zero append `stderr.strip() or "<label> adapters are stale"`; else append
`"<script> is missing"`. The preceding door-presence loop (168–171) has no analog in the
agent block and is genuinely new — that part is not duplicated. See REUSE-3 for the exact
refactor.

## Item 4 — new/extended test suites

`test-sync-command-adapters.py`, `test-onboarding-split.py`, `test-fleet-product-config.py`,
and the `test-check-omp-port.py` extension all use the tree-wide 5-line `_anchor_os/_anchor_sys`
sys.path boilerplate and per-file `run()`/`check()` helpers — same pattern as ~69 existing
test files (confirmed via grep across `tests/`, e.g. `test-sync-agent-adapters.py:5-9,38-44`,
`test-check-domain.py:15-19`). This is the pre-existing, tree-wide convention this pass's
own dispatch already backlogs as REUSE-3 ("a shared test-fixtures module"). Nothing in this
diff makes it materially worse — the new files match the existing convention exactly, they
don't add a second, different flavor of it. **No update to REUSE-3.**

The `test-check-omp-port.py` extension re-lists the four door names as a tuple literal
(line 159) that also appears in `check-omp-port.py:169`. This is a test asserting against a
fixed production list, the same pattern every other case in that file already uses for other
fixed lists — not a new class of duplication. **No finding.**

## Item 5 — factory_config.py's product_config_report / --check-product-configs

`product_config_report` calls the existing `product_config()` and only catches `FleetError`;
`_check_product_configs` reuses `repo_entry` (existing, for `--repo` narrowing),
`factory_cli.payload`, `factory_cli.EXIT_REFUSED`, and `_PRODUCT_CONFIG_PATH`. Its own inline
comment (factory_config.py ~465–470) explicitly documents choosing to print `m["detail"]`
verbatim rather than re-deriving the `repo@ref:path` token a second time — i.e. it was
written *against* REUSE-1 rather than deepening it. **No finding; REUSE-1 not worsened.**

## Findings

### REUSE-1 (low, advisory) — sync-command-adapters.py/sync-agent-adapters.py `sync()`+`main()`
- file: `.claude/skills/harness/bin/sync-command-adapters.py:31-56,59-72`; sibling
  `.claude/skills/harness/bin/sync-agent-adapters.py:258-282,284-301`
- summary: ~24 lines of control flow (diff-by-name, write/delete on apply, argparse/try-except
  shell) are the same shape in both files.
- cost: a change to the diff/apply algorithm (e.g. adding a `--dry-run` count, changing the
  drift message format) must be made in both files by hand; the file touched less often
  (`sync-command-adapters.py`, new and smaller) is the one an editor forgets.
- alternative: extract a shared `_sync_dir(canonical_dir, adapter_dir, glob_pattern, expected, check, label) -> int` helper (or a small `AdapterSync` module) both scripts call, parameterizing only the glob pattern and stale/updated message wording.
- lane: applicable (both files under `.claude/skills/harness/bin/`)
- severity: low (design-accepted duplication per the skill's own "cheap and honest cost" framing; flagged only because the extraction is unusually clean, not because the current state is wrong)

### REUSE-2 (low, advisory) — hand-rolled root default instead of harness_boundary.resolve_root
- file: `.claude/skills/harness/bin/sync-command-adapters.py:61`; canonical resolver:
  `.claude/skills/harness/bin/harness_boundary.py` (`resolve_root`), already used by
  `.claude/skills/harness/bin/factory_config.py:35` and
  `.claude/skills/harness/bin/check-instruction-paths.py:143`
- summary: `--root` defaults to `Path(__file__).resolve().parents[4])`, not
  `harness_boundary.resolve_root(...)` — this diff had the chance to migrate the
  adapter-sync pair onto the canonical resolver and instead copied the sibling's
  pre-FEAT-42 pattern into a second file.
- cost: `harness_boundary.resolve_root`'s override-var handling and stderr announcement on a
  discarded override is silently absent from both adapter-sync scripts; a future fix to that
  behavior (e.g. tightening the override contract) must now remember two non-canonical
  spellings instead of one, and the newer, smaller file is the one likely forgotten.
- alternative: `parser.add_argument("--root", type=Path, default=None)`, then
  `root = args.root.resolve() if args.root else Path(harness_boundary.resolve_root(Path(__file__).resolve().parent))`.
  Out of scope to also fix `sync-agent-adapters.py` here (untouched by this diff); note it as
  a follow-up if the pair is revisited.
- lane: applicable (`.claude/skills/harness/bin/sync-command-adapters.py`)
- severity: low (mirrors, does not introduce, an existing sibling gap; the forbidden "new
  second resolver" did not happen)

### REUSE-3 (medium) — check-omp-port.py duplicated subprocess-check block
- file: `.claude/skills/harness/bin/check-omp-port.py:156-166` (agent block) and
  `:172-182` (command block)
- summary: both blocks are the identical "resolve script path under
  `.agents/skills/harness/bin/`, run `--check`, append stderr-or-default on non-zero, append
  '<script> is missing' if absent" shape — 10 of ~11 lines match line-for-line modulo the
  script filename and the label text ("agent"/"command").
- cost: a change to how these checks are invoked (e.g. passing `--root` differently, changing
  the missing-script message format) must be applied to both blocks by hand; the block a
  reviewer scans second is the one likely to drift.
- alternative: extract
  `def _check_adapter_sync(root: Path, script_name: str, label: str) -> list[str]:` that
  resolves `root / ".agents" / "skills" / "harness" / "bin" / script_name`, runs it
  `--root <root> --check`, and returns `[]`/`[stderr-or-default]`/`["<script_name> is missing"]`.
  Call sites: `errors.extend(_check_adapter_sync(root, "sync-agent-adapters.py", "agent"))`
  and `errors.extend(_check_adapter_sync(root, "sync-command-adapters.py", "command"))`,
  replacing lines 156-166 and 172-182 respectively. The door-presence loop (168-171) stays
  inline — it has no counterpart to share with.
- lane: applicable (`.claude/skills/harness/bin/check-omp-port.py`)
- severity: medium (real, mechanical duplication with a clean, low-risk extraction; not
  design-accepted the way REUSE-1 is)

## What else was checked, no finding
- `factory_config.py`'s new `product_config_report`/`_check_product_configs`: reuse existing
  `product_config`, `repo_entry`, `factory_cli.payload`/`EXIT_REFUSED`; deliberately avoid
  re-deriving the `repo@ref:path` token (REUSE-1-from-prior-round not worsened).
- Test suites' anchor/run/check boilerplate: matches tree-wide convention exactly
  (REUSE-3-from-prior-round not worsened).
- `test-check-omp-port.py`'s door-name literal: mirrors an existing per-file pattern of
  asserting against fixed production lists, not a new duplication class.
