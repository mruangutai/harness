# QA gate - BUG-2169 - cycle 0 - pin 6c896d98

BLUF: **FAIL.** Signed T-01 verify is green at the pin and the pre-fix defect is genuinely red at
c4e8bbc8, but `tests/integration/test-check-domain-grant.py` (in T-01.files, outside the verify
line) goes **green -> red** in the image: `D-14a` still pins `"pip install"` while the fixed guard now
prints `sudo apt install python3-yaml`. Build evidence says that file's container failures are
"identical before and after"; measured here, the base passes it (exit 0) and the pin fails it (exit 1).
The Mac pass hides it. Kind: substance (stale test assertion contradicting the shipped advice), task T-01, unrated.

## Environment (identical both states)
`harness-2169-repro`, arm64 ubuntu:26.04; `/usr/bin/python3` 3.14.4; yaml
`/usr/lib/python3/dist-packages/yaml/__init__.py` 6.0.3, `__with_libyaml__` True, C module
`/usr/lib/python3/dist-packages/yaml/_yaml.cpython-314-aarch64-linux-gnu.so`; dpkg: python3-yaml
6.0.3-1build1, libyaml-0-2 0.2.5-2build3, python3-jsonschema 4.19.2; no yaml under any other
`*-packages` dir (single install). Trees: `git archive <sha>` -> ro mount -> `cp -a` -> `git init`
(a bind-mounted worktree `.git` file is dangling in the container, so my first attempt ran the
worktree HEAD for every label and is discarded). Raw logs (ephemeral): `/tmp/qa2169/{base,mix,pin}.log`,
`*.k.log`.

## Seam / scope
`git diff 1780b922 6c896d98 --stat` = `plan.yaml` 1 line only: dispatch claim confirmed (seam
code-identical to pin). base..pin non-`.harness` scope: 7 files, +246/-49: dispatch-guard.py,
harness_yaml.py, worktree_terminal.py (docstring only), checkout-prereqs.md, tests.yml,
test-check-domain-grant.py, test-lead-start-preflight.py. The two other suites were not edited.

## Phase 1 expectations (source-blind) vs found
SC-01 single system install (C loader) starts / distrusted-origin yaml purged; SC-02 3 advice branches +
warning, no `--user`; SC-04 existing guard + start-return pass, distrusted-origin regression.
Gaps: (a) distrusted-origin controls pass at base by construction - only the mutant discriminates them;
(b) SC-02 branch assertions have no pre-fix red (see below); (c) no non-C-loader case in the image
(builder notes this host cannot run it).

## Signed verify at pin (image), exit / time
- test-dispatch-guard.py exit 0, 135 of 135, 5 s
- test-lead-start-preflight.py exit 0, 62 of 62, 2 s
- test-lead-start-return.py exit 0, 57 of 57, 6 s (13 s together; under 60 s). FAIL lines: 0.

## Fail-first (c4e8bbc8 code, image)
Tier A natural red, old tests at base: dispatch-guard exit 1 (110/135, 25 FAIL lines); preflight exit 1
(30/50, 20); start-return exit 1 (13/36, 23). Stderr is the defect (`failed to parse YAML ...
could not determine a constructor for the tag N[one]`), not an invocation error; the only passes are
non-start refusals.
Tier A natural red, pin tests on base code ("mix"): preflight exit 1, 35/57,
`FAIL BUG-2169/single-install` and `FAIL BUG-2169/advice/function` (`harness_yaml has no install_command`).
|SC|test|red at base|green at pin|tier|
|---|---|---|---|---|
|SC-01|test-lead-start-preflight.py `BUG-2169/single-install`|yes|yes|natural, semantic (tag None)|
|SC-01|`BUG-2169/user-site-plant`, `pythonpath-plant`, `-symlink-plant`, `-dotdot-plant`|no (pass vacuously at base: base purges everything)|yes|mutant only: guard `_bootstrap_keep_yaml = True or all(...)` -> exactly these 4 red, 58/62; I ran it|
|SC-02|`BUG-2169/advice/function`|yes, signature-absent only (`hasattr`)|yes|natural but proves no behavior|
|SC-02|`advice/debian`, `homebrew`, `homebrew-warning`, `other`, `precedence`, `default`|never executed at base (function returns early)|yes|none: no semantic pre-fix red|
|SC-04|test-dispatch-guard.py (all start/claim cases), test-lead-start-return.py|yes (above)|yes|natural, semantic|
|SC-04|distrusted-origin regression (the four plant controls above, in the unit file)|no|yes|mutant only|

## Matrix (`.harness/harness.json`)
T-01 `bugfix`: `always: []`; `unit` when `touches_runtime_code` (true: bin/*.py) -> **required**;
`integration` when `fix_confined_to_tests_and_contract_docs` (false) -> not required; `__bug_class__`
unresolvable (G-08). Unit: `test-lead-start-preflight.py` is a file under tests/unit and is run by
`run-unit-tests.py --kind unit` (57 files; PASS at pin, FAIL at base); its 12 BUG-2169 cases ran green.
The kind-wide runner is **exit 1 at base and pin** from pre-existing image-only failure `test-omp-hooks.py`
(needs `bun`). `--kind integration`: exit 1 both; base fails post, plan-routes, dispatch-guard,
feature-worktree, harness-yaml, layout-migration, start-return; pin fails **grant (new)**, post,
plan-routes, feature-worktree, harness-yaml, layout-migration. The common failures are root/path/bun
image artifacts unrelated to this patch; none counted as fixed.
Kind discrimination: SC-01/02 are `unit` (file under tests/unit); SC-04's two suites are
`integration` by directory. `matrix_ok: true`.

## Finding F-1 (kind: substance, task T-01, unrated)
`tests/integration/test-check-domain-grant.py:359-362` D-14a asserts `"pip install" in r3.stderr`;
the fixed guard prints `PyYAML is not importable ... Install PyYAML to restore normal operation:
sudo apt install python3-yaml` on this Debian image. Base: grant exit 0, `ok D-14a`; pin exit 1,
`FAIL D-14a`, 26/27. The SC-08 lines (stderr/systemMessage) were migrated to `advice`; D-14a was not.
It is not in the signed verify line, but it is in T-01.files and the repo's standing `integration`
suite, and CI (ubuntu-26.04 image) will redden. Fix is a dev's (assert the per-platform advice, like
the SC-08 lines at 313-343). Contradicts build-evidence "identical before and after".

## Other observations (not gating)
- Build-evidence "21 tag None lines" vs my 25/23 FAIL lines counts differ only by counting method;
  same defect.
- Out of scope: `feature_schema.py` jsonschema `--user` advice (builder-noted; not measured).
- SC-03/SC-05 inspection: tests.yml diff shows a clean removal of `--ignore-installed` and the comment;
  worktree_terminal.py gains only a docstring, `_read_landed_plan_yaml` untouched. Reviewers own these.
- Only my own evidence has examined the mutant result (O-07).

## Principles applied
Delete First not applied. Build the Lever: one reusable container script per state (rebuilt each run).

## Corrections (re-prompt, existing evidence only)
- F-1 remediation is simply T-01 (assertion already in T-01.files); no operator or scope decision exists. Q-1 withdrawn; `open_questions: []`.
- `matrix_ok: true` means the changed-file coverage rule only: bugfix floor = `unit` when `touches_runtime_code`, and a named unit test for this change (`BUG-2169/*` in test-lead-start-preflight.py) ran green. It does NOT mean the `run-unit-tests.py --kind unit` runner passed: that exits 1 at base and pin from the image-only `test-omp-hooks.py` (`bun` absent), unchanged by the patch. Governing rule: harness-verification-rules "The matrix is a floor" / "satisfied = a named test ran, none failed" for this change. `suite: fail` stands because of F-1.
- Gap classification: SC-02 semantic-red gap = adequacy gap, not must-fix (fail-first for SC-02 is signature-absent only; the branch assertions run green at pin and never ran at base). Non-C-loader = adequacy gap, not must-fix (BRIEF accepts C-loader-or-not from the single-install image; not obtainable here). Plant controls mutant-only = adequacy note. Only F-1 is a finding.
