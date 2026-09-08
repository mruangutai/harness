# BUG-1290 · plan fix cycle 3 — panel findings closed, panel recorded

**Both gating findings are closed as plan edits, and the panel is transcribed.** PANEL-01 was routed
by widening `T-02` rather than adding a task; A-01 was reconciled in `T-03` (paren-free local) rather
than by widening the detector in `T-04`. `approval.status` is still `pending`; no criterion was
weakened — `BRIEF.md` is untouched.

## PANEL-01 — widen T-02, not a new task

**Routing:** case (H)'s fixture move joins `T-02`. Same file, same mechanical edit, same
`change_type`, same agent, and `T-03` already `depends_on: [T-01, T-02]`, so no new DAG edge and no
`depends_on` rewrite. A separate task would have bought a second id and an extra edge for one line.
`T-02` step 4 now forbids only *adding* a case; its title is now "Move both integration claim
fixtures onto the repository's own segment".

**Scope set by a whole-file grep, not by the two known line numbers** (the panel's own lesson).
`grep -n '\.harness' tests/integration/test-factory-integration.py` at `eb9d044e`, every hit:

| lines | what | disposition |
|---|---|---|
| `:882` (case F), `:1246` (case H) | the only two hardcoded `.harness/harness/features` fixture joins | **in `T-02`'s `files:`, both instructed** |
| `:538-542` | `HARNESS_PROJECT_DIR` marker probe (`docs/SPEC.md` + `team-config.yaml`) | out of scope — not a features root |
| `:1404, :1452, :1495, :1558, :1608` | per-case `.harness/harness.json` writes | out of scope — a file, not a features root |
| `:1506` | `.harness/widget/features/FEAT-STATUS` | out of scope — already on the segment, drives `board_lifecycle.py audit`, not claim |
| `:27, :30-31, :429`, `:879-880` | prose | `:30` in `T-02` step 3, `:879-880` in step 1 (both become false); rest out of scope |

**Measured.** `python3 tests/integration/test-factory-integration.py` at `eb9d044e`: exit 0, 9.3s,
131 `ok`, zero `FAIL`; `ok    (F) claim exits 0` and `ok    (H) claim against the two-board fleet
exits 0` both present. `T-02`'s amended verify (both `FAIL` markers) run against that captured
output **exits 1** — it can only go green once *both* fixtures sit on `widget` while claim still
hardcodes `harness`. `T-03`'s verify then goes red only if per-repository resolution is wrong,
because the case that used to redden it on a correct build is now migrated by its predecessor.

## A-01 — reconcile in T-03, not T-04

`T-03` step 1 now mandates `seg = segment_of(repo_name)` before the join. Measured against the real
row patterns (`layout_migration.py:91,94`): the inline `segment_of(repo_name)` spelling matches
**neither** `r'"\.harness", [^,)]+, "features"'` nor the legacy pattern → `neither` →
`CANNOT_VERIFY`; the paren-free `".harness", seg, "features"` matches migrated and not legacy → the
moved row classifies `factory_config.py` as `migrated`, both conjuncts of `T-04`'s verify pass on a
correct build. Widening the row to `[^,]+` is refused in `T-04` step 1 with its reason: loosening a
drift detector to fit the code it watches. **The probe's ladder needs no edit** — its migrated
control string `os.path.join(H, ".harness", seg, "features")` is *already* the paren-free form:
legacy matches L, legacy misses M, migrated matches M, all three still hold.

## Panel

`plan.yaml` top-level `panel`: `last_run: 2026-09-05-06-validator`, `cycle: 1`, 2 readers both
`ran` (`harness-code-reviewer`/`scope`, `fable-advisor`/`should-not-exist`), 9 findings. Ids computed
with `panel_findings.py`, never typed; each verified to re-derive from its recorded summary.
PANEL-01 → `resolved_by: T-02`, A-01 → `resolved_by: T-03`; the other seven `dismissed` with their
reader's reasoning. `record_notes` preserve the lead's `none`→`info` normalisation on the T-05
mechanism entry, the reviewer's "PANEL-03 (P2)" mislabel, and that P2 rests on `should-not-exist`
alone. Severity was never edited; the five entries whose reader stated none are recorded at `info`
and say so.

## Verified

`safe_load` parses; `approval: {status: pending}`; all five tasks keep `files`/`intent`/`verify`/
`traces`/`change_type`; no `verify: >` or `intent: >` anywhere;
`check-plan-routes.py <plan>` → `0 violation(s)`, exit 0.

## Open

- None blocking. Advisory carried forward from the panel, unchanged: 5d is the suite's weakest link
  (nothing binds its discrimination) — the build's reviewer's item, not a plan edit.
