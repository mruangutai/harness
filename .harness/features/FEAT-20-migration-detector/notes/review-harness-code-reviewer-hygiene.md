# Review — PR #385 (chore/382-detector-hygiene), pinned a714bd0, base 3c75aa6

**BLUF: FAIL.** Two must-fix findings, both evidenced against the pinned bytes: (1) the DEC-194
narrowing rewrites the ORIGINAL decision entry in place, violating this same file's own header rule
("APPEND-ONLY. Never rewrite... an existing entry"), the same day amendment 1 followed that rule
correctly. (2) `render()` and check-state.sh's INV-27 — the two call sites #379 claims can "never
name different readers for the same tree" — actually diverge on the `undeclared-segment` cause when a
coupled reader also disagrees: `render()` calls `blame()` unconditionally for every CANNOT_VERIFY
cause; check-state.sh's `_cv_wording` table only calls `blame()` for `unreadable`/`neither`. Probe
below reproduces it. Everything else checked out clean; several candidates considered and rejected
(list at bottom).

No `[harness:human]` commits in `3c75aa6..a714bd0` (single commit, author Mike Ruangutai). Working
tree matches the pinned SHA for every reviewed path (git-show equality spot-checked for
layout_migration.py, check-state.sh diffs); no dirty-tree reads needed.

## A. #379 one blame policy — mostly clean, one real gap

- Repo-wide sweep of `check-state.sh` for residual per-form filtering (`readers`, `_tagged`, `f ==`,
  `blame`) found exactly the two composed call sites at `check-state.sh:1301,1304,1325`, both routed
  through `_lmod.blame(_srep)`. No leftover local filter anywhere else in the file.
- Same sweep of `layout_migration.py`: `render()` (`:319`) is the only other consumer; `scan()`'s own
  `f == "unreadable"/"neither"/"both"` comparisons (`:239,242,248-249`) are verdict classification,
  a different concern from blame-naming, not a residual.
- Alias→copy change (`blame = rep.readers` → `named = list(rep.readers)`): no caller mutates
  `rep.readers` after `scan()` builds it (tuples of immutable strings); functionally equivalent,
  `blame()` itself is side-effect free. Not a finding.
- **Real gap — call-site divergence on `undeclared-segment`.** `layout_migration.py:318-320`:
  `if rep.verdict in (MIXED, CANNOT_VERIFY): for p, f in blame(rep): ...` — this fires for **every**
  CANNOT_VERIFY cause. `check-state.sh:1295-1312`'s `_cv_wording` table calls `blame()` only inside
  the `"unreadable"` and `"neither"` lambdas; `"undeclared-segment"` (`:1307-1311`) prints only
  `_srep.detail` (the evidence paths), never a reader. Since `undeclared-segment` is decided in
  `scan()` (`layout_migration.py:235`) *before* the unreadable/neither/no-evidence checks, a tree can
  have BOTH an undeclared-segment cause AND a reader that disagrees with the (single) evidence shape,
  making `blame()` non-empty. Reproduced directly:
  ```
  rep = SurfaceReport("features", CANNOT_VERIFY, {"legacy"}, [("r1","migrated")],
                       "undeclared-segment", ("evidence/path",))
  blame(rep) -> [('r1', 'migrated')]
  ```
  On such a tree, CI's Layout gate (`.github/workflows/tests.yml:190` runs `layout_migration.py`
  directly → `main()` → `render()`) prints the reader `r1 [migrated]` on the finding line;
  check-state.sh's INV-27 (session entry) does not. That is exactly the residual #379 says is closed
  — it isn't, for this one cause. Severity high: falsifies the ticket's own claim with a realistic,
  reproducible combination (legacy evidence + one premature reader + one undeclared-segment file).

## B. #382 one fixture copy

- Structural check of `test-layout-migration.py`'s refactor: the deleted inline block
  (`git diff` at `test-layout-migration.py:54-105` in the base) is line-for-line identical to
  `layout_fixtures.py:20-67`; `MARKER_REL = lm.MARKER` resolves to the same
  `os.path.join(".harness","factory","fleet.yaml")` the old literal used
  (`layout_migration.py:115`). For **this file**, the marker path is genuinely never restated
  elsewhere (`grep` confirms one occurrence, at `test-layout-migration.py:56`).
- `check-plan-routes.py` case_20 reachability (`test-check-plan-routes.py:1167-1170`): it scans every
  non-`test-*` `.py`/`.sh` file under `bin/`, so `layout_fixtures.py` **is in scope** — the "does it
  not trip case_20" protection is NOT vacuous by out-of-scan exclusion. It is operative for a
  different reason: case_20 only flags a "root probe" line containing both `.harness` and one of six
  predicate substrings (`os.path.isdir(`, `os.access(`, etc. — `test-check-plan-routes.py:1120`), and
  `layout_fixtures.py` contains none of those substrings anywhere, so paren-joining can't manufacture
  a false match regardless of balance. Independently verified the balance claim anyway (AST-parsed
  every string constant in `layout_fixtures.py`; every one has equal `(`/`)` counts) — the docstring's
  claim is true, and currently non-load-bearing for case_20 specifically (would matter only if
  PREDICATES-shaped text were later added to the module).
- `run-unit-tests.sh` drift detector (`:42`, `for f in "$BIN_DIR"/test-*.py`) globs only `test-*.py`,
  correctly excluding `layout_fixtures.py`. Not a gap: both importers of the module
  (`test-layout-migration.py`, `test-check-state.py`) are registered scripts, so a broken
  `layout_fixtures.py` surfaces as an import failure in either, not silently.
- **Real gap, tied to the already-known duplication (see interaction note below).** The *executing*
  `case_x` in `test-check-state.py` is the one at `:2718` (Python keeps the later of two same-named
  top-level defs), and it does **not** use `layout_fixtures` — it restates `MARKER_REL =
  os.path.join(".harness", "factory", "fleet.yaml")` at `:2729` and the full inline `STUBS` dict
  inline, verbatim. So for this file, in the code that actually runs, "one fixture copy" and "the
  marker path is never restated" are both **false**. The `layout_fixtures`-based `case_x` at `:1585`
  (which does satisfy #382) is dead code, shadowed by the duplicate. This is a `mismatch` against
  #382's own claim, and it is a direct consequence of the duplication issue already found and handed
  to qa to measure — flagging the causal link here rather than re-filing the duplication itself.

## C. #383 run_cs → module-level run()

Confirmed identical: base `run()` (`test-check-state.py:50-54` at 3c75aa6) and the deleted local
`run_cs` (removed at the same file, formerly inside the old budget-check case) have byte-identical
bodies — same `env["CLAUDE_PROJECT_DIR"] = tmp`, same `cwd=tmp`, same
`subprocess.run([SCRIPT], capture_output=True, text=True, env=env)`, same `(returncode, stdout)`
return shape. No behavioral difference.

## D. #366 DEC-194 narrowing

- Enumerated every CANNOT_VERIFY cause in `scan()` (`layout_migration.py:233-247`): `no-rows`,
  `undeclared-segment`, `unreadable`, `neither`, `no-evidence`, plus the `MIXED` verdict (not a
  "cause" but also reader-bearing via `blame()`). Classification against the amended sentence:
  `{no-evidence, no-rows, undeclared-segment}` = reader-less as claimed; `{unreadable, neither}` +
  `MIXED` = reader-bearing, and each still emits path+`[form]` in `check-state.sh` — **when `render()`
  is not the call site in play**. Per finding A above, `render()` breaks this classification for
  `undeclared-segment`, so the amended sentence is correct for check-state.sh's wording but **false**
  for `render()`'s. The narrowing itself (which causes are reader-less in principle) is the right
  set; the code doesn't uniformly implement it.
- `docs/harness/DECISIONS-INDEX.md:212`'s DEC-194 row (`am.1`, ruling text about the neither-form
  rule) does not restate the "every finding names..." sentence at all, so it is not literally stale
  relative to the wording change — but it IS stale relative to the intended remedy below (see must-fix
  2): once the narrowing is moved into `### DEC-194 amendment 2`, the row's `am-span` must become
  `am.1-am.2` or a future reader will miss the entry entirely (the index is generated except the
  `::` ruling text — regenerate after the doc restructure, per `DECISIONS-INDEX.md:2-3`).
- **Must-fix 1 — append-only violation.** `docs/harness/DECISIONS.md`'s own header (line 3-6):
  *"APPEND-ONLY. Never rewrite or renumber an existing entry. If a decision changes, add a new entry
  that references and supersedes the old one."* This PR's hunk (`DECISIONS.md:5853-5857`) edits the
  sentence **inside the original DEC-194 body** (lines 5834-5899, before `### DEC-194 amendment 1` at
  5901) rather than appending `### DEC-194 amendment 2`. Confirmed by line position: the changed text
  sits above the existing amendment-1 heading, i.e. inside the base entry, not in a new section.
  DEC-194 amendment 1 was added correctly as its own heading the same day this narrowing landed —
  making the inconsistency self-evident within one PR's blast radius. The original overclaiming
  sentence is now unrecoverable from the authority itself; a reader diffing the entry sees no
  reversal, only a rewritten fact, which is exactly what the append-only rule exists to prevent.
  Remedy: restore the original sentence in the base entry, record the narrowing as `### DEC-194
  amendment 2 (2026-08-14)`, and update the index row to `am.1-am.2`.
- Hunk locality: confirmed via `git diff` — the `DECISIONS.md` diff is a single hunk inside DEC-194's
  base body; no neighbouring entries touched.
- `plan.yaml` (`:660-670`) mirrors the same (currently misplaced) wording and does not contradict the
  authority text as written; it will need the same restructure note if/when DECISIONS.md is fixed, but
  is not itself a second violation (plan.yaml carries no append-only rule).

## Interaction note — duplication scope is larger than "two `def case_x`"

Already flagged to me as found and being measured by qa: two top-level `case_x` defs in
`test-check-state.py`, later wins, doesn't use `layout_fixtures`. Verified against the pinned blob
that the actual scope is much bigger: **13 other functions** (`case_m`, `case_m2`, `case_m3`,
`case_n`, `case_p`, `case_q`, `case_t`, `case_r`, `case_s`, `case_o`, `case_u`, `case_v`, `case_w`)
are each defined **twice**, byte-identical both times (diffed programmatically against
`a714bd0:test-check-state.py`, all 13 pairs match exactly). The whole block
`case_x`(new, uses `layout_fixtures`) → `case_m`...`case_w`(exact re-paste) → `case_x`(old, inline
STUBS) → `main()` was inserted as one unit before the pre-existing tail of the file, which was never
removed. Net effect: ~1080 lines of this file are dead, exact-duplicate test bodies (functionally
inert — since the pairs are byte-identical, no behavior changes for those 13), and the one place the
duplication is NOT inert is `case_x`, where the dead copy is the intended #382 fix and the live copy
is the pre-refactor original. Passing this scope correction to qa's remediation rather than re-filing
it: the fix isn't "delete one dead function," it's "delete the entire re-pasted block."

## Stage 2 — code quality on changed lines

- `import layout_fixtures as lf` (`test-layout-migration.py:54`, `test-check-state.py:1595`) is bare,
  no try/except — a missing module raises `ImportError` uncaught, halting the suite loudly. Matches
  repo convention (no quiet-skip fallback). Note: in `test-check-state.py` this import only executes
  inside the shadowed (dead) `case_x`, so the loud-failure property is currently unexercised by the
  live suite — a consequence of the duplication above, not a new defect.
- `blame()`'s docstring (`layout_migration.py:262-268`) accurately describes its behavior for the two
  callers it names (`render()`, check-state's INV-27) but the docstring's own claim — "so CI and
  session entry can never name different readers for the same tree" — is the exact claim finding A
  falsifies for one cause. The docstring is accurate about what `blame()` does; it is not accurate
  about what calling it inconsistently guarantees.
- No other source regression found outside #379/#382/#383/#366 or log/plan bookkeeping — every hunk
  in `git diff 3c75aa6..a714bd0 --stat` maps to one of the four tickets or `.harness/logs/2026-08-14.md`.

## Rejected candidates (with reason)

1. Alias-to-copy change (`rep.readers` → `list(rep.readers)`) as a behavior risk — rejected, no
   caller mutates the list, `blame()` doesn't mutate `rep`.
2. `blame()` including `"neither"`/`"unreadable"` tags for the MIXED branch as over-broad — rejected,
   those form-sets are unreachable on a MIXED verdict (scan() routes them to CANNOT_VERIFY first), so
   it's dead-but-harmless generality, not a behavior change from the old inline MIXED filter.
3. Drift detector excluding `layout_fixtures.py` as an unenforced fixture module — rejected, both
   importers are registered test scripts; breakage surfaces via their own import failure.
4. Pre-existing `fleet.yaml` writes in `test-check-state.py` (`:947,:1353,:2081,:2487`, the INV-24
   factory tests) as unswept fixture duplication under #382 — rejected, different invariant (factory
   claim resolution, not the layout detector's reader table), out of #382's stated scope.
5. `layout_fixtures.py`'s paren-balance docstring claim as an unenforced assertion — rejected as
   stated (it's independently true by AST check) but noted as currently non-load-bearing for case_20
   specifically, since no PREDICATES substring exists in the file yet.
6. The broadened `unreadable`/`neither` wording in check-state.sh's `_cv_wording` (now calling
   `blame()` instead of the narrower old `_tagged()`) as a scope-creep widening — rejected, this is
   the intended unification per #379, and for these two causes `blame()`'s output is a strict superset
   match to the old `_tagged(_form)` single-form output only when exactly one reader carries that
   form; for MIXED-cause reader sets where multiple readers are unreadable/neither, `blame()` now
   correctly names all of them where `_tagged` already did (same list comprehension shape) — no
   observed divergence, so this is an accepted improvement, not creep.

## What I did not re-file

Per dispatch: #365, #367, #368-#375, #377, #378, #380, #381, #384, #279 — not re-derived. #380 (case_20
parens-in-strings) — accepted, owned elsewhere; I used its existing mechanism to verify B rather than
relitigating it. The two `case_x` defs — not re-filed as a new finding; scope-corrected as an
interaction note above, per instruction not to re-derive it as new.
