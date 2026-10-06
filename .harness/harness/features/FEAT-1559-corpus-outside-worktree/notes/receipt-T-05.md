# Receipt — FEAT-1559 T-05 (2026-10-05)

Executed directly in the main session under DEC-174.

T-05 has two halves. This file is the **build half**: the standing tests, the OMP adapter case,
the DEC-214 amendment and the guidance. The **receipt half** is done and recorded in
`notes/non-regression-receipt.md`. It ran at the code-final commit `69e3d819` (operator ruling,
2026-10-05) and covers:

- merge-base as `pre_change_sha` (`e8d868f7`);
- the whole-feature diff: no path under any other feature directory;
- the main-corpus manifest bytes: identical, 4635 entries;
- the full suites in a disposable full clone: unit 54/0, integration 86/0;
- the non-skipped real-owner run: 6 tests OK, probe pin removed.

## What changed

- **`tests/unit/omp-hooks.test.ts`**: an absolute main-corpus read (`/repo/.harness/kaya/features/…`
  with a `:1-20` selector, a quoted `:raw` form and a `;` list) reaches `read`, `grep` and `glob`
  byte for byte, with no `feature-root` lookup. A relative read of the run's own feature still
  roots in its worktree, after exactly one lookup. No TypeScript production change.
- **`tests/unit/test-corpus-regression.py`** locks ruling B's prohibitions by behaviour:
  - **no sibling provider:** neither `corpus_path` nor `population` answers from an in-progress
    sibling;
  - **no git-content read:** a worktree reads the owner's uncommitted working file;
  - **no symlink and no owner write:** repair leaves the owner's tree and index unchanged. The one
    config change is git's own `extensions.worktreeConfig = true`, measured below;
  - **landed means tracked:** an untracked owner directory is not landed.
- **`tests/integration/test-corpus-non-regression.py`**, the collected parts only (D-13):
  - fresh synthetic-clone retention, including a hooked `git pull`;
  - the planning-baseline finding set as a recorded literal, checked as a subset;
  - conversion-manifest consistency, plus a planted-inconsistency case;
  - `--conversion-manifest PATH` for T-06's live, read-only verify.
  - The manifest schema `feat-1559-conversion/1` is defined here, the consumer side.
- **`tests/integration/test-corpus-real-owner.py`** reads the real owner root, from the owner and
  from this worktree:
  - the landed names the audit requires equal `git ls-tree`'s tracked feature directories;
  - the count is above the floor of more than 70;
  - record-less directories are included;
  - check-state passes its corpus choke point.

  The same helper rejects a wrong-root clone and a staged missing directory built from the T-01
  fixture. One disposable pin at owner HEAD, made by `pinned-checkout.py` and removed at
  teardown, shows `dirty (8)` reported while the audit runs, then `materialisation (7)` refusing
  with "no invariant ran".
- **DEC-214 amended; `check-instruction-paths.py` follows it.** A concrete feature id names a landed
  record and is read at `<HARNESS_CONTROL_PLANE_ROOT>/`. A placeholder (`<feat>`, `FEAT-NN-slug`)
  is the active feature and stays at the feature tree. The `harness-simplify` FEAT-23 source
  citation moved to the control-plane anchor, and `DECISIONS-INDEX.md` was regenerated.
- **Guidance:**
  - `AGENTS.md`: a constraint bullet.
  - `.harness/README.md`: a full operator section covering the layout, the active-id rule, the
    exits table, A/B/C classification, hooks, `core.hooksPath` locality with INV-31, recovery,
    conversion and evidence.
  - `harness/SKILL.md` and `harness-verification-rules/SKILL.md`: the read and write split and
    the gate semantics.
- **`f58_sparse_fixture.install_hooks()`**: the T-04 integration test's hook install, moved into
  the shared fixture so `test-corpus-non-regression.py` reuses it.

## Deviations from the plan text, with reasons

All recorded through `plan-merge.py amend` on T-05 `files`.

- **The DEC-214 amendment and its classifier.** SC-14 requires instructions to distinguish
  active-feature writes from absolute landed-main-corpus reads, and ruling B places those reads at
  the owner root, which is the control-plane root. DEC-214's classifier refused every feature path
  at the control plane. That forced the one real landed-feature citation onto the feature-tree
  anchor, which names a missing file in a sparse worktree. The write half of DEC-214 is unchanged.
- **The owner config write.** The plan's text implies repair writes nothing at the owner.
  Measured: git's first per-worktree sparse checkout adds `extensions.worktreeConfig = true` to
  the shared config, and changes no tree or index byte. The live owner already carries it, from
  this worktree's conversion. The regression test pins exactly that one addition, and the README
  states it.

## Red-first evidence, and what is a positive control

- **`check-instruction-paths`**: pre-change, both new behaviours failed.
  - "a landed feature read at the control plane is clean" got `feature-directory path anchored to
    the control plane`.
  - "a landed feature read at the feature tree is refused" got 0 violations.
  - The three placeholder cases passed as controls. After the change: 18/18, and the live scan
    went to 1 violation (the citation), then 0 once it was re-anchored.
- **`test-corpus-regression.py`**: the four locks guard behaviour that already holds, so their
  red is shown by throwaway mutants rather than by stashing production code:

  | Mutant | Case | Result |
  |---|---|---|
  | `corpus_path` answers from any linked worktree that has the path | no sibling provider | FAIL |
  | `corpus_path` serves the owner's HEAD blob via `git show` | owner working file | FAIL |
  | `worktree-state.py` wrapped to symlink another feature in after repair | no symlink | FAIL |
  | `landed_dirs` returns every reached directory | untracked not landed | FAIL |

  Unmutated, all four pass. The mutant script was not kept.
- **Positive controls, not red-first claims:**
  - the OMP adapter case (BUG-1016 behaviour, no production change);
  - Retention and AuditFindings (non-regression by definition: they hold before and after);
  - the real-owner name-set and choke-point checks, whose discriminating power is shown in-test
    by the wrong-root and missing-directory mutants.

## Green

| Command | Exit | Cases |
|---|---|---|
| `python3 tests/unit/test-corpus-regression.py` | 0 | 4 (~1.6 s) |
| `python3 tests/integration/test-corpus-non-regression.py` | 0 | 6, 2 announced skips (no manifest yet; no `--conversion-manifest`) |
| `python3 tests/integration/test-corpus-real-owner.py` | 0 | 6 (~9 s; probe pin `BUG-1016-worktree-relative-paths--f1559-<pid>--probe` at owner HEAD `e8d868f7`, removed) |
| `python3 tests/unit/test-omp-hooks.py` (`bun test`) | 0 | 138 |
| `python3 tests/integration/test-check-instruction-paths.py` | 0 | 18 |
| `check-instruction-paths.py` / `check-skill-refs.py` on this sparse worktree | 0 / 0 | 68 / 73 files |
