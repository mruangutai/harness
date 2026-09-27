# FEAT-68 — build divergence ledger

Base `e655f14a56a14bf1777cae55a19195c9af10505d` (= origin/main at the signed plan); implementation
pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`. Every
owning-suite comparison is exit status + stdout bytes + stderr bytes between a clean detached
checkout of the base and a clean detached checkout of the pin, after the ONE signed
normalisation — each checkout's own absolute root → `<checkout>` (BRIEF SC-02; FEAT-66 D-09;
three `ok` lines in `test-validate-digest.py` print the agent file's absolute path). Raw bytes
and sha1s are retained in `notes/clean-pin-byte-receipts.md`. Every other difference is a
divergence and is ledgered here: 53/57 suites identical, four not, five entries.

(The build's first receipt at this pin had also normalised mkdtemp paths and unittest timing;
validate c0 VF-01 ruled those substitutions outside the signed experiment, so they are gone and
the lines they masked are D-02..D-05 below. The earlier baseline capture in the feature worktree
was replaced by the detached one for the same finding.)

## Output divergences

- D-01 `tests/unit/test-suite-independence.py` (stdout, line 8)
  old: `discovered 112`
  new: `discovered 111`
  case: the suite's discovery count over `tests/**/test-*.py`.
  ruling: accepted — `tests/unit/test-render-brief.py` is deleted with its script (the
  operator's deviation, BRIEF SC-03/SC-05); one fewer suite is the deletion's consequence.
- D-02 `tests/integration/test-harness-yaml.py` (stderr, line 9)
  old: `PyYAML is not importable and the bootstrap marker at /var/folders/y3/…/T/tmpkbvkh756/.harness/.pyyaml-bootstrap could not be written …`
  new: `… at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpvmwjw2po/.harness/.pyyaml-bootstrap could not be written …`
  case: the bootstrap-marker warning names the `tempfile.mkdtemp()` directory the case created.
  ruling: accepted — run-to-run nondeterminism (a fresh directory name every run, at the base
  as at the pin); the code path and the message are the same. Operator ruling 2026-09-27
  (`notes/answers-validate-validator.md` A-1).
- D-03 `tests/unit/test-harness-boundary.py` (stderr, line 1)
  old: `harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/…/T/tmpc63ro8j0' — it does not carry .harness/team-config.yaml. Falling back …`
  new: `… HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpvaz3yhhy' …`
  case: the fallback warning names the case's `mkdtemp()` directory.
  ruling: accepted — same as D-02 (A-1).
- D-04 `tests/unit/test-suite-independence.py` (stderr, line 1)
  old: `ERROR could not resolve scan root above /var/folders/y3/…/T/tmp9sv7_pg1`
  new: `ERROR could not resolve scan root above /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmprm_hlbs4`
  case: the no-root error names the case's `mkdtemp()` directory.
  ruling: accepted — same as D-02 (A-1).
- D-05 `tests/unit/test-artifact-accessors.py` (stderr, line 3)
  old: `Ran 24 tests in 0.122s`
  new: `Ran 24 tests in 0.222s`
  case: unittest's footer wall-clock.
  ruling: accepted — timing, not output; 24 tests both sides, `OK` both sides (A-1).

## Structural decisions (not output divergences)

- D-06 `check-plan-routes.process_plan_yaml` — one rule per function returning its violation
  count; `_routing_rule` split further into `_literal_paths` / `_resolve_grants` /
  `_ungranted_findings` / `_granted_findings` (a first split left it at grade 3, which the bar
  rejects; the second reaches 5). `plan_anchors` is imported where it is used (simplify A1).
- D-07 `harness_boundary.classify` — ordered phases `_no_base_verdict` (three no-base outcomes,
  order preserved) → `_rel_candidates` → `_match_verdict` (`_reached` is the one match rule
  used for globs and shared) → `_deny_verdict` / `_harness_advertise`. `real(root)` now runs
  only on the deny path (it fed nothing else); no output effect.
- D-08 `board_lifecycle._audit_findings` — one function per finding class; the four network
  calls stay in the driver in their documented order and `issues`/`stations` are passed down.
  `_issue_label_names` replaces two identical set comprehensions.
- D-09 `layout_migration.scan` — `_scan_surface` → `_surface_report` → `_cannot_verify_reason`
  / `_is_mixed`; the reason order is stated in `_surface_report`'s docstring (altitude A2).
- D-10 `check-domain.domain_check` — `_refuse_out_of_place_root`, `_manifest_domains_or_exit`,
  then a `_VERDICT_HANDLERS` table keyed by `classify`'s outcome with `_deny_verdict` as the
  default, which is the inline chain's fall-through. Two source-anchor mutants repointed to the
  new shapes, same proof: `test-check-domain-artifact.py` (feature-checkout guards, now in
  `_allow_verdict`) and `test-check-domain-worktree.py` (bug895 block, now in
  `harness_boundary._no_base_verdict` at four-space indent).
- D-11 render-brief removal — beyond the grilling's list, `.omp/commands/harness.md` line 132
  told the main session to offer/regenerate the `.html`; that sentence is removed too
  (amendment to T-01's `files`, recorded at build close). `test-suite-independence` discovers
  111 suites (D-01).
- D-13 `tests/unit/test-code-grade.py` — the stale `("check-plan-routes.py", "process_plan_yaml"):
  1` self-grading exemption is removed (FEAT-66 MF-04 / FEAT-67 precedent: an allowlisted grade
  that no longer matches fails the unit kind; the first full unit run at `0c15bad6` caught it).
- D-12 Grade-2 helpers kept at 2 where the grader excepts them: none new this wave — every
  function the five decompositions introduced or retained grades 4 or better.

## Simplify pass (four read-only scouts, one per angle; applied before the pin)

Applied: S1 (five narrating comments → present facts, feature tag kept), S2 (load-bearing
parameters unprefixed: `legal`, `abs_root`, `verdict`), S3 (class markers on the driver's
calls, not split across callees), A1 (`plan_anchors` imported in `_literal_paths`), A2's
one-line docstring note.
Skipped: S4 (`_harness_advertise` single-use — it is what holds `_deny_verdict` at bar 4).
Efficiency and Reuse: empty returns.
