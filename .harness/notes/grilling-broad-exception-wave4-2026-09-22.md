# Grilling — broad-exception sweep, wave 4 (the other 28 bin/ scripts) — 2026-09-22

## Destination
Every `BROAD_CATCH_CEILINGS` entry is 0 except `harness_boundary.py`, which is the one home
of the two designed broad catches: `RepoModuleError` (FEAT-63) and a shared `hook_guard`
that spells the hooks' own-failure idiom once. Every other handler catches the type its
boundary raises; every silence keeps its written reason; no hook changes the verdict an
operator sees today. Two features, libs+tools first, then hooks.

## Mission
mission: plan
reason: the cause is known and the files are named, but the work adds a shared enforcement
helper every hook runs under (`hook_guard`), ratchets the census ceilings, and mints typed
errors in shared libraries that hooks then consume. Both features, main-session-direct
under DEC-174.
confirmed-by: operator

## Settled
- Destination → zero everywhere; the hook fail-open idiom lives once in `harness_boundary`
  (`hook_guard(main, name, fail=...)`), not once per hook and not as a ruled residual.
- Hooks' own-failure posture → **kept as measured today, per hook**; only the shape is
  consolidated. All eleven pass through (print `<hook>: … — passing through.`, exit 0) on
  their own failure, except `check-domain`, which BLOCKS (exit 2) when `harness_boundary`
  itself cannot load; `fail='closed'` is fixed at that call site with the reason beside it.
  Any change of posture is a separate later ruling. `SystemExit`/`KeyboardInterrupt` are
  never caught by the guard.
- Slicing → two features. **FEAT-64**: the 10 shared libs (24 sites) and 8 tools (19
  sites) — typed errors minted where the boundaries are; `hook_guard` added to
  `harness_boundary` but not yet wired. **FEAT-65**: the 11 hooks (77 sites) wired to
  `hook_guard` and narrowed, one task per hook; `check-domain` (24) and `validate-digest`
  (18) are each a FEAT-63-sized task.
- Silent handlers → keep their documented silence, narrowed to the boundary's real classes
  (`OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError` on parses, the loader's
  own error class); the reason stays as the comment on the narrowed handler. An offline
  machine must never red a gate (wave 3's rule stands).
- Loud handlers → narrowed to the callee's typed error, verified per site; the printed text
  is unchanged.
- Re-parses → deleted, not consolidated, where the same source is already parsed and
  reported once in that script (wave 3's rule; `_SHARED_SOURCE_LOADERS` already locks the
  three loaders repo-wide).
- Census → ceilings for every file a feature touches become 0 when it lands; unlisted
  files stay 0; `harness_boundary` is sized from HEAD (its own internal broad catches are
  narrowed too, so it ends at exactly the two designed ones).
- Receipts → byte-identity over the suites covering the touched scripts (FEAT-64: the
  `test-harness-boundary`, `test-harness-yaml`×2, `test-worktree-terminal`,
  `test-inflight-registry`, `test-post-merge-sweep`, `test-gh-sync`×6, `test-check-omp-port`,
  `test-run-unit-tests`×2, `test-check-plan-routes` suites and the singletons' suites;
  FEAT-65: `test-check-domain*`×8, `test-validate-digest`×2, one suite per gate/guard,
  `test-inject-expertise`, `test-feature-record`); divergences enumerated and ruled in
  `notes/build-divergences.md`, red-first, as FEAT-63 did.
- Comments → move byte-for-byte with their code; new facts as separate prose marked with
  the feature id (FEAT-63 c0's PM-63-01 lesson).
- Sequence → FEAT-64 → FEAT-65 → the grader/review-skill extension on the clean baseline.

## Not yet specified
- `hook_guard`'s exact message shape — whether it prints the hook's own first line verbatim
  (each hook's pass-through text differs slightly today) or one canonical line; the receipts
  decide per hook.
- Whether `inflight_registry`'s process-identity reads (`ps`/`/proc`) get their own typed
  error or stay `OSError`-narrowed silences.

## Out of scope
- Changing any hook's fail-open/closed verdict (ruled: keep today's posture; separate ruling).
- #1882 (identity-less claim binding) — investigated, not reproducible; not this wave.
- The grader/review-skill extension (the wave after).
- Turning any environment silence into a finding.

## Facts I verified (so pm does not re-derive them)
- 120 broad handlers by AST at a4a3d7f8 (tuple forms `except (X, Exception)` included; the
  census rule counts 118 — `except Exception` or bare `except:`). Per role: hooks 77
  (28 loud / 34 swallow / 15 assign-a-default), libs 24 (17 swallow, 3 rethrow), tools 19
  (11 loud, 7 swallow). Per file: check-domain 24, validate-digest 18, dispatch-guard 9,
  worktree_terminal 7, bash-write-guard 6, harness_boundary 6, merge-gate 5,
  post-merge-sweep 5, branch-create-gate 4, check-omp-port 4, gh-close-gate 3, gh-sync 3,
  harness_yaml 3, inflight_registry 3, then ≤2 each.
- Hook set = the scripts `harness-hooks.ts` invokes: inflight_registry, check-domain,
  validate-digest, feature-record, plan-sign-gate, merge-gate, inject-expertise,
  gh-close-gate, dispatch-guard, branch-create-gate, bash-write-guard.
- Every hook's outermost own-failure catch exits 0 with a "passing through" line; the one
  exit-2 own-failure path is check-domain's boundary-module load (`BLOCKED — the boundary
  module harness_boundary.py could not …`).
- The FEAT-63 patterns available for reuse: `Ctx.spawn`-style single process boundary,
  `RepoModuleError` / `load_repo_module` / `call_repo_module`, `BROAD_CATCH_CEILINGS` with
  `_broad_catch_count` in check-plan-routes.py (red-first mutants in
  `test-check-plan-routes.py`, unit lock in `tests/unit/test-broad-catch-census.py`).
- The consolidation audit reddens on a new broad catch today (measured during #1887: a
  19th in validate-digest was refused until narrowed).

## Addendum — 2026-09-25, grader/review-skill extension ruled out of scope
- Grilled after FEAT-65 shipped (#1920 → 0aa337f1). Settled: the rule would live in the fleet
  grader (`code-grade.py`) as a ratchet (new unmarked broad catch in a changed function → grade
  input, gated by the existing pre-image drop rule; a `# broad-catch: <reason>` marker as the
  boundary hatch). Then ruled **premature**: harness is already locked by the census (bin/ at
  zero, `harness_boundary.py` at its two designed boundaries); the only ungated surface is
  kaya-ai, which shows no measured regrowth. The two todos (`Extend code-grade/review rubric to
  grade new broad catches`, `Reduce BROAD_CATCH_CEILINGS to pure zero-list`) are DROPPED, not
  blocked. Revisit only on evidence: a rising kaya-ai count. This section is that feature's
  grilling if the evidence arrives.
- Monitor, not gate: kaya-ai baseline at `7d2f946` (master), main tree excluding
  `.claude/worktrees` — **35 broad catches in 7 of 127 .py files**: jobs_supabase.py 10,
  worker.py 7, extraction/citation.py 6, review/audit.py 5, api/review_supabase.py 4,
  cli/review.py 2, api/jwt_verify.py 1. Same AST rule as the census (bare, `Exception`, or a
  tuple naming `Exception`). Re-measure at the next kaya-ai review or sweep.
- The `BROAD_CATCH_CEILINGS` table stays as its two-entry self; replacing it with an in-source
  marker was judged a convention swap with no behaviour gain.
