# FEAT-68 — build divergence ledger

Base `e655f14a56a14bf1777cae55a19195c9af10505d` (= origin/main at the signed plan). Every
owning-suite comparison is exit status + stdout bytes + stderr bytes after two normalisations
applied to both sides, with the raw bytes and hashes retained in the receipt:

- each checkout's own absolute root → `<checkout>` (the FEAT-66 D-09 ruling; three `ok` lines
  in `test-validate-digest.py` print the agent file's absolute path);
- a fresh `tempfile.mkdtemp()` directory → `<tmpdir>` (new this wave; operator ruling requested
  2026-09-27 and proceeded on the recommendation): one stderr line in each of
  `test-harness-yaml.py`, `test-harness-boundary.py` and `test-suite-independence.py` names a
  directory that differs on every run, at the base as much as at the pin. Run-to-run
  nondeterminism, not a code difference;
- unittest's footer wall-clock `Ran N tests in <t>s` → `Ran N tests in <t>s` (same class:
  `test-artifact-accessors.py` prints one; it differs on every run).

## Output divergences

- D-01 `tests/unit/test-suite-independence.py` stdout line 8 — old `discovered 112`, new
  `discovered 111`. Affected case: the suite's discovery count. Cause: `tests/unit/
  test-render-brief.py` is deleted with its script (the operator's deviation). Ruling: the
  expected consequence of the deletion; accepted. The only stdout divergence in 57 suites.

## Structural decisions (not output divergences)

- D-02 `check-plan-routes.process_plan_yaml` — one rule per function returning its violation
  count; `_routing_rule` split further into `_literal_paths` / `_resolve_grants` /
  `_ungranted_findings` / `_granted_findings` (a first split left it at grade 3, which the bar
  rejects; the second reaches 5). `plan_anchors` is imported where it is used (simplify A1).
- D-03 `harness_boundary.classify` — ordered phases `_no_base_verdict` (three no-base outcomes,
  order preserved) → `_rel_candidates` → `_match_verdict` (`_reached` is the one match rule
  used for globs and shared) → `_deny_verdict` / `_harness_advertise`. `real(root)` now runs
  only on the deny path (it fed nothing else); no output effect.
- D-04 `board_lifecycle._audit_findings` — one function per finding class; the four network
  calls stay in the driver in their documented order and `issues`/`stations` are passed down.
  `_issue_label_names` replaces two identical set comprehensions.
- D-05 `layout_migration.scan` — `_scan_surface` → `_surface_report` → `_cannot_verify_reason`
  / `_is_mixed`; the reason order is stated in `_surface_report`'s docstring (altitude A2).
- D-06 `check-domain.domain_check` — `_refuse_out_of_place_root`, `_manifest_domains_or_exit`,
  then a `_VERDICT_HANDLERS` table keyed by `classify`'s outcome with `_deny_verdict` as the
  default, which is the inline chain's fall-through. Two source-anchor mutants repointed to the
  new shapes, same proof: `test-check-domain-artifact.py` (feature-checkout guards, now in
  `_allow_verdict`) and `test-check-domain-worktree.py` (bug895 block, now in
  `harness_boundary._no_base_verdict` at four-space indent).
- D-07 render-brief removal — beyond the grilling's list, `.omp/commands/harness.md` line 132
  told the main session to offer/regenerate the `.html`; that sentence is removed too
  (amendment to T-01's `files`, recorded at build close). `test-suite-independence` discovers
  111 suites (D-01).
- D-09 `tests/unit/test-code-grade.py` — the stale `("check-plan-routes.py", "process_plan_yaml"):
  1` self-grading exemption is removed (FEAT-66 MF-04 / FEAT-67 precedent: an allowlisted grade
  that no longer matches fails the unit kind; the first full unit run at `0c15bad6` caught it).
- D-08 Grade-2 helpers kept at 2 where the grader excepts them: none new this wave — every
  function the five decompositions introduced or retained grades 4 or better.

## Simplify pass (four read-only scouts, one per angle; applied before the pin)

Applied: S1 (five narrating comments → present facts, feature tag kept), S2 (load-bearing
parameters unprefixed: `legal`, `abs_root`, `verdict`), S3 (class markers on the driver's
calls, not split across callees), A1 (`plan_anchors` imported in `_literal_paths`), A2's
one-line docstring note.
Skipped: S4 (`_harness_advertise` single-use — it is what holds `_deny_verdict` at bar 4).
Efficiency and Reuse: empty returns.
