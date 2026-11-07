# T-01 build evidence - BUG-2169 - 2026-11-07

Main-session-direct under DEC-174. Commit `fe54232a`, base `c4e8bbc8` (origin/main).
Regression source: `harness-2169-repro` (ubuntu:26.04, `/usr/bin/python3` 3.14.4, Debian
PyYAML 6.0.3 at `/usr/lib/python3/dist-packages/yaml/__init__.py`, libyaml True, single
system-wide install). The Mac is a secondary check only.

## Fail-first (pre-fix, container)

- `test-dispatch-guard.py` exit 1, 21 "tag None" lines; `test-lead-start-return.py` exit 1,
  21 "tag None" lines; `test-lead-start-preflight.py` exit 1 at `BUG-2169/single-install`
  (33 of 54 passed). The failure is the bootstrap re-import, not an invocation error.
- Advice: `BUG-2169/advice/function` failed (no `install_command`), 54 of 55 passed.
- `test-check-domain-grant.py` SC-08 install-command assertions (stderr, systemMessage)
  failed on the image's PyYAML because they pinned `pip install` wording.

## Fixed (container and Mac)

- T-01 verify: dispatch-guard 135/135, preflight 62/62, start-return 57/57, all exit 0;
  container 13 s, Mac 16 s (under 60 s).
- Mutant "keep every PyYAML": the four plant controls (user site, PYTHONPATH, symlinked
  and `..`-spelled PYTHONPATH) go red, 58 of 62, proving they discriminate.
- Debian smoke: PyYAML removed -> guard prints `sudo apt install python3-yaml`; following
  it -> 60 of 60 at that point (before alias cases were added).
- Also green on Mac: test-post-merge-sweep, test-harness-yaml-corpus, test-team-catalog,
  test-check-domain-grant. In the container test-check-domain-grant has unrelated
  root/macOS-path failures, identical before and after; its SC-08 lines go red -> green.
- SC-03: `tests.yml` is a clean revert of #2168 (`ee29e049`); both jobs run
  `python3 -m pip install --upgrade pyyaml jsonschema`, no `--ignore-installed`.

## Scope amendment

`tests/integration/test-check-domain-grant.py` added to T-01.files through
`plan-merge.py amend` (ledgered amendment; approval and signed hashes unchanged).

## Risk grading (`code-grade.py --base c4e8bbc8 --head fe54232a`)

8 passing, none ungraded, no high. Two grade-2 reasons:

1. `tests/unit/test-lead-start-preflight.py::bug2169_cases` - one scenario's fixture setup
   and a flat loop of named `check` calls over plant spellings; splitting would scatter the
   shared temp-dir lifecycle across helpers.
2. `tests/unit/test-lead-start-preflight.py::bug2169_advice` - a straight sequence of named
   `check` calls, one per advice branch; no branching logic to extract.

## Simplify pass (four read-only angles over c4e8bbc8..b9bd9558)

- Efficiency: no findings.
- Applied (`af7cc5d1`): `checkout-prereqs.md` retyped the retired `--user` PyYAML advice
  (reuse + altitude, fold-in); it now prints `harness_yaml.INSTALL_COMMAND`, jsonschema's own
  line unchanged. Ledgered as a second files-only amendment. Guard bootstrap: one
  `_bootstrap_within` (resolves once) and one `_bootstrap_is_yaml` replace the duplicated
  inline checks (reuse + simplification). Two change-narrating comments reworded.
- Not applied: plan.yaml line-1 BLUF wording - signed plan text, not editable outside the
  verbs; cosmetic.
- Briefing row (out of scope, predates the patch): `feature_schema.py:59-60` jsonschema advice
  and the bail-out messages in `test-plan-team.py:39`, `test-harness-yaml-corpus.py:59`,
  `test-team-catalog.py:44` still say `--user`; isolated hooks importing `feature_schema`
  likely cannot see a per-user jsonschema [INFERENCE, not measured].
- After apply: T-01 verify green in container and on Mac (135/62/57), plant mutant red on
  all four controls (58/62), grant, post-merge-sweep, hooks-install, instruction-paths and
  skill-refs green. Grader at `af7cc5d1`: 8 passing, the same two grade-2 reasons above.
