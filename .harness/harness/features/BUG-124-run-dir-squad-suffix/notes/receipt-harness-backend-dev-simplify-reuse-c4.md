# SIMPLIFY · REUSE angle — BUG-124 run-dir squad suffix

Read-only pass over the exact 4-file scope (`dispatch-guard.sh`,
`harness_boundary.py`, `tests/integration/test-dispatch-guard.py`,
`tests/unit/test-harness-boundary.py`) at `80ce35d1..dac8f099`. Three findings.

## F-1: `run_dir_grant_globs`'s tree-walk duplicates `manifest_domains`'s tree-walk

- **file:line**: `.claude/skills/harness/bin/harness_boundary.py:833-844` (the
  `walk()` closure inside `run_dir_grant_globs`)
- **existing thing**: `.claude/skills/harness/bin/harness_yaml.py:403-414`, the
  `walk()` closure inside `manifest_domains()` — same document (parsed
  `team-config.yaml`), same generic dict-then-list recursive traversal
  (`isinstance(node, dict)` → walk each value; `isinstance(node, list)` → walk
  each item), differing only in the per-node leaf test.
- **cost**: the recursion shape is now written twice against the same parsed
  manifest tree. A future fix to the traversal itself (e.g. a guard against a
  YAML anchor cycle, or a `None`/scalar-node edge case) applied to one copy
  has no reason to reach the other — `manifest_domains` lives in
  `harness_yaml.py`, `run_dir_grant_globs`'s copy lives in
  `harness_boundary.py`, so an editor fixing one file isn't looking at the
  other. A third grant-collector (there is real appetite for one — this file
  already has `RE_RUN_DIGEST`/`RE_STATE_YAML`/`RE_RUN_IDENTITY` as separate
  manifest-adjacent concerns) reinvents the same six lines a third time.
- **alternative**: factor the recursive traversal into one generic walker in
  `harness_yaml.py` (e.g. a `walk_nodes(parsed)` generator yielding every
  dict/list node), and have both `manifest_domains` and `run_dir_grant_globs`
  drive it with their own leaf predicate instead of restating the recursion.

## F-2: `_RUN_DIR_REF_RE` restates a path shape already spelled three times

- **file:line**: `.claude/skills/harness/bin/harness_boundary.py:860-861`
- **existing thing**: `.claude/skills/harness/bin/harness_boundary.py:39-46` —
  `RE_RUN_DIGEST`, `RE_STATE_YAML`, `RE_RUN_IDENTITY`, each already spelling
  the literal `\.harness/[^/]+/features/[^/]+/runs/[^/]+/` path shape.
  `_RUN_DIR_REF_RE` spells the same shape a fourth time (unanchored, with
  capture groups, for `finditer` over free text rather than `fullmatch` over a
  bare path — a real usage difference, not a straight swap).
- **cost**: the run-dir path shape now has four independent regex spellings
  in one file. If the shape ever changes (an extra path segment, a different
  separator), a dev fixing the three anchored ones has no structural signal
  that a fourth, differently-shaped regex 800 lines away also encodes the
  same assumption — it can silently stop matching current dispatch prompts
  while the three file-path regexes keep working.
- **alternative**: pull the shared fragment `r"\.harness/([^/\s]+)/features/([^/\s]+)/runs/([^/\s]+)"`
  into one named constant (e.g. `_RUN_DIR_PATH_FRAGMENT`) near line 39 and
  build all four regexes — the three `^...$`-anchored ones and
  `_RUN_DIR_REF_RE` — from it, so the path shape has exactly one spelling.

## F-3: `_checkout_with_run_dir_grants` duplicates `_checkout`'s persona-copy block

- **file:line**: `tests/integration/test-dispatch-guard.py:182-187`
- **existing thing**: `tests/integration/test-dispatch-guard.py:155-160`, the
  identical `os.makedirs(.../".omp", "agents")` + `for persona in
  ("harness-backend-dev", "harness-product-lead"): shutil.copyfile(...)`
  block inside `_checkout()`. The new function's own docstring
  acknowledges copying "the same personas `_checkout` copies."
- **cost**: the persona tuple and copy loop are now typed twice. Whoever
  next needs a third persona in these fixtures (a new case exercising a
  different agent type) has to remember to edit both functions — miss the
  second and a case built on `_checkout_with_run_dir_grants` silently keeps
  running against a stale, narrower persona set than the one `_checkout`
  cases get, with nothing failing to point at the gap.
- **alternative**: extract the shared "make tmp dir, mkdir `.omp/agents`, copy
  the fixed persona list" step into one helper (e.g.
  `_seed_personas(tmp)`), call it from both `_checkout()` and
  `_checkout_with_run_dir_grants()`, and let each keep writing its own
  `team-config.yaml` content afterward — no behavioural change, no widened
  scope.

## Rejected (not filed)

- The second `team-config.yaml` parse inside T-02's derivation subprocess
  (`dispatch-guard.sh`'s heredoc, ~line 47-50) versus `run_dir_grant_globs`'s
  own `harness_yaml.load_file` call: settled per the shared context (Q4,
  needed to distinguish "no grants" from "broken derivation" — F-4/D-04). Not
  refiled.
- `run_dir_slug_ok`'s synthesized `.../runs/<slug>/x` leaf versus reusing
  `matches()` directly on a bare directory glob: not substitutable — `matches`
  needs a concrete leaf to test a `/**` grant against, and the existing
  worktree/domain call sites all pass real file paths, never a bare directory.
  Fought-for anchor per the shared settled list; not refiled.
