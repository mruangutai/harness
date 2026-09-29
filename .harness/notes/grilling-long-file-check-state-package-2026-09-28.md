# Grilling — long-file wave 1: check-state.py becomes the `check_state/` package — 2026-09-28

## Destination
`.claude/skills/harness/bin/check-state.py` (5,058 lines at e6f8493b) is a ~150-line entry over a
`bin/check_state/` package: `ctx.py`, `table.py`, `runner.py` and ten input-family modules holding the
39 invariants. Full-table output is byte-identical before and after; every function in the entry and
the package is at code-grade bar 4; the FEAT-62 structural lock walks the package with its transitive
reads rule intact and one new rule (a row's function lives in the module its reads name).

## Mission
mission: plan
reason: cause known and diff bounded, but a new importable surface (the package) and an enforcement change (the lock in check-plan-routes.py) — third test of the patch rule fails.
confirmed-by: operator

Every task is `execution_mode: main-session-direct` (DEC-174: check-state.py, check-plan-routes.py
and their suites are enforcement files; the main session writes the diff).

## Settled
- Which long file first → check-state.py, as a package split (option a); not the five-family
  extraction, not plan-merge first.
- Discretion → stays in the table. `check-state.py` never selects families; `table.py` holds
  `INVARIANTS` in today's exact order and imports every family; families export
  `inv_NN(ctx[, feat]) -> (bad, warn)` and know nothing of the runner. No per-family entry points.
- Families, by what the rows READ (not by subject):
  `plan.py` INV-35/3/4/5/34/32/44 · `feature_record.py` INV-1/2/6/7/8/12/18/22/23/33 + ledger
  INV-39/40/43/47 with `collate_feat59` · `run_state.py` INV-15/16/36/46 · `seams.py` INV-17 ·
  `brief.py` INV-38/41/49 (+ the INV-38..41 helpers now at 332-466) · `worktrees.py` INV-25/27/29/31 ·
  `board.py` INV-13/21/24/26/28/30/37 · `host.py` INV-19/42/45/48. Operator accepted the two
  judgement placements (INV-1/2 in feature_record; INV-27/31 in worktrees).
- Layout → `bin/check_state/` with `__init__.py`; the first subdirectory under bin. Entry keeps the
  hyphenated name and path every consumer forks; package name is importable (underscore). No flat
  `check_state_*.py` siblings.
- Code quality going in → SC-01 is FILE-WIDE and satisfiable: every function in `check-state.py`
  and `check_state/**` at grade ≥4 after the pin. The four below-bar functions are fixed in the
  module they land in, in scope: `_inv41_invocation` (2), `_unquoted_hash_digit` (2),
  `_quoted_scalar_closed` (3), `inv_49` (3). Moved code proves itself by grade identity against
  the pre-image; new functions (lock walker, table glue) are graded new at bar 4, no exemptions.
- Lock → option (a), package-aware: `feat62_findings` parses the entry plus every
  `check_state/*.py`, one combined function table, the same four rules (module body, no re-parse,
  transitive declared reads, authority) over all of it, plus the reads-family rule. Its cases in
  `test-check-plan-routes.py` mutate the package copy. Option (b) per-module rejected: the
  transitive walk is what catches an undeclared spawn two helpers deep; without it the reads rule
  passes vacuously and the gate degrades silently.
- Growth prevention → prose, not a cap. `harness-craft/references/delete-first.md` gained the
  placement bullet and trigger clause (#1970, a726bad8). The reads-family lock rule is the
  mechanical half for this file. No file-length ratchet; revisit only on evidence that the prose
  does not hold.
- Comments move byte-for-byte; the four load-bearing `# INV-32 … BEGIN/END` markers move with
  their code; no renames beyond what the package forces.

## Not yet specified
- The exact split of `ctx.py` if `Ctx` (412 lines) is judged too wide for one module — pm may keep
  it whole; nothing in the destination requires splitting it.
- Whether `host.py` is the right name for the repo-scope rows that shell out to sibling checkers
  (INV-19/42/45/48); the family is settled, the name is pm's.

## Out of scope
- plan-merge.py, validate-digest.py, check-domain.py, gh-sync.py, check-plan-routes.py as long
  files — later waves.
- The 19 remaining grade-1 functions (10 CLI dispatchers, 9 light) — the dispatcher wave.
- A file-length ratchet or cap (ruled: prose first).
- Changing any invariant's behaviour, message text, severity, or table order.
- The stringly-typed navigation family (918 `.get` sites).

## Facts I verified (so pm does not re-derive them)
All at e6f8493b unless noted; the structural map with line numbers is `agent://CheckStateMap/report`
(transcript history://CheckStateMap) — pm should copy what it needs into the plan, the agent id will
not outlive the session.
- check-state.py: 5,058 lines; bootstrap 1-118 (`root = sys.argv[1]` at :96 is the lock's
  bootstrap-end sentinel); `class Ctx` 467-878; invariant bodies 880-4563; `INVARIANTS` 4599-4750
  (26 groups, 39 rows); `RETIRED` 4754; runner 4759-5058. `code_grade.grade_source`: 287
  functions, 114@5 169@4 2@3 2@2.
- No invariant body lives outside the file. `board_lifecycle.py` is not imported by it.
- Structural lock: `check-plan-routes.py:1832-2330` (`CHECKER_REL` :1860, `_module_functions`
  :1969, `_reachable` :2124 resolves only same-tree names, `_inv_rows` :1992, `feat62_findings`
  :2299, `consolidation_findings` :2315). Lock cases: `test-check-plan-routes.py:2591-2923`,
  mutating a copy of bin/ at `_checker_path` :2547.
- Text scanners of `INV-\d+` in check-state.py: `check-plan-routes.py:886-890`
  (`_live_invariant_numbers`) and `check-skill-refs.py:32,104-105` (INV-48's engine). Both must
  read the package glob after the split.
- Nine suites fork the script via `tests/integration/check_state_support.py:24-26` (`SCRIPT`,
  `CHECK_STATE_BIN`); none imports it as a module. Four build scratch bins by copying the file:
  `test-check-state-worktrees.py:149-157,285-315`, `-records.py:192,555` (also mutates the INV-32
  markers at check-state.py:1380/1384/4605/4610), `-handoff.py:366,527,662` (cites :1366 for an
  emission shape), `-feat59.py:594-597` (patches at the `harness_yaml.require_or_die()` anchor).
  `test-check-state-entry.py:383-477` reads check-state.py and check-domain.py as text and asserts
  shared budget/CHECKPOINT/handoff literals. `test-check-state-table.py` asserts `--list` order:
  INV-35 first, INV-44 last, INV-46 right after INV-15, retired rows last.
- `tests/integration/fixtures/canonical-reader-classification.json:467-589` keys nine finding ids
  as `.claude/skills/harness/bin/check-state.py::<symbol>::<reader>#N` (incl. `station_of`,
  `_handoff_exempt`); a move re-keys them.
- CI forks the entry at `.github/workflows/tests.yml:276-311`; `.omp/commands/harness.md:11` at
  session entry; `.github/CODEOWNERS:39-43` names it DEC-174-guarded. `.agents/skills` is a
  symlink to `.claude/skills`, so the package appears under both paths.
- `bin/` has no subdirectory today (only `__pycache__`); the bootstrap puts bin on `sys.path`
  (:67), so `import check_state.table` needs no new machinery.
- No file-length gate exists anywhere in bin/ or tests/; the only per-file ceiling is FEAT-63's
  broad-catch census (check-state.py ceiling 0), which must apply to every package file.
- The four below-bar functions carry no written reason and no self-grading exemption in
  `tests/unit/test-code-grade.py`.
- Decisions governing the shape: DEC-174 (carve-out), DEC-205 (retired numbers never reused),
  DEC-188 (struck decisions leave every gate → authority rule), DEC-156/182/203/231 for the rows.
  No DEC names the FEAT-62 decomposition rules; they live only in code prose at
  check-plan-routes.py:1832-1858 — pm may want a DEC that records the package shape and the
  reads-family rule.
- Proof form (as FEAT-68, reuse `FEAT-68-…/notes/receipt-scripts/`): baseline in a clean detached
  checkout of the base, pin in a clean detached checkout, checkout-root normalisation only, every
  other byte difference ledgered with exact bytes, one execution per measurement, receipts
  committed after the pin naming the full SHA. Measurements: full-table stdout over every feature;
  `--list`; the nine suites' outputs; `feat62_findings`/`consolidation_findings` clean-tree runs;
  `code_grade` over entry+package.
- Cost record for the estimate: FEAT-66 evaluator split ~85 min plan→ship; FEAT-68 build 60 min,
  validate ~4 h (all receipt-form). This build is larger: lock rework + 4 suites + fixture re-key.
  Estimate build 5-6 h, validate 1-2 cycles.
