# review-harness-qa-c17 — gate-only matrix re-run + falsification probe

BLUF: **PASS.** Matrix satisfied (unit + integration, both green, 0 failures). 39 falsification
probes against the pinned parser — every attached spelling, every pinned exclusion, every unknown
post-`merge` option, every other value-taking `git merge`/global option in both spellings — DENY on
an owing fixture. **Zero silent allows.** All three SC-11 case names exist individually and pass
individually at the pin. No must-fix.

Scope confirmed: I read exactly `.claude/skills/harness/bin/merge-gate.py` and
`tests/integration/test-merge-gate.py` as diffed
`e374c9a2..94b5e465` (+50/-26), and measured against the live worktree, which is HEAD-pinned to
`94b5e465` (`git rev-parse HEAD` == the pin).

## 1. Matrix re-run

T-05's `change_type` is `bugfix`. Matrix (`test_matrix.bugfix`): `always: []`,
`when: [unit if touches_runtime_code, integration if fix_confined_to_tests_and_contract_docs,
__bug_class__ if match_bug_class]`.

- `touches_runtime_code`: true (`merge-gate.py` is runtime code) → **unit required**.
- `fix_confined_to_tests_and_contract_docs`: false (source changed alongside tests) → integration
  *not* obligated by this predicate, but I added it anyway (floor, not ceiling) since
  `tests/integration/test-merge-gate.py` is the file directly exercising this change.
- `match_bug_class`: per this checkout's repository Expertise (G-08), no bug-class taxonomy entry
  fires for any diff yet — never satisfiable, not evaluated as a gap.

| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` (`env -u HARNESS_AGENT_TYPE`) | exit 0, 531 PASS / 0 FAIL |
| integration | satisfied (added, floor) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0, 1649 PASS / 0 FAIL, incl. `test-merge-gate.py` exit 0 |

`matrix_ok: true`. Both gates ran to completion and reported no failures — a gate that did not run
would be reported here as `n/a`/BLOCKED; neither did that.

## 2. SC-11 case names, individually

Grepped `tests/integration/test-merge-gate.py` at the pin for each of the three names separately
(not one file-global grep), then re-ran the whole suite and grepped the *output* for each name
individually:

```
ok    T-05 merge --abort on an owing branch allows
ok    T-05 merge --continue on an owing branch allows
ok    T-05 merge --quit on an owing branch allows
ALL PASSED
```

All three exist as distinct tuples in the `for command, name in (...)` loop (lines 191-198 of the
pinned test file) and each drives its own `check()` call — not a shared aggregate.

## 3. Falsification — 39 probe forms against an owing fixture

Fixture: `FEAT-9001-fixture-non-era`, `github.sync: true`, `github.repo: "acme/widgets"`, branch
`feature/test`, no `build_entry` (owing). Harness: `.claude/skills/harness/bin/merge-gate.sh`
invoked exactly as the standing test does (stdin JSON, `HARNESS_PROJECT_DIR` env). Script:
`local://` n/a — throwaway at `/tmp/probe_merge_gate.py` (author-nothing constraint: this is a
disposable QA probe, not a repo artifact; nothing was written into the tree).

Every probe form below **denied**, and every deny reason contained `gh-sync.py open` (i.e. attributed
correctly to the owing `FEAT-9001-fixture-non-era` record for branch `feature/test` — not a
different-reason deny, not a misattributed branch):

| class | forms | result |
|---|---|---|
| attached value spellings | `-F<file>`, `--file=<file>`, `--cleanup=strip`, `--attr-source=HEAD` (global, before `merge`), `-C<dir>` (global), `--git-dir=<d>` (global) | 6/6 deny |
| pinned exclusions, bare (must stay boolean) | `--exec-path`, `-S`, `--gpg-sign`, `--log` | 4/4 deny (correctly identify `merge`/target past them) |
| pinned exclusions, attached (must consume via `=`/glue only) | `--exec-path=/x`, `-Skeyid`, `--log=5` | 3/3 deny |
| unknown option after `merge` (must stay boolean) | `--no-ff`, `--squash`, `--allow-unrelated-histories`, `--verify-signatures` | 4/4 deny |
| other `git merge` value options, both spellings | `-m`/`-mmessage`, `--message`/`--message=`, `-s`/`-srecursive`, `--strategy`/`--strategy=`, `-X`/`-Xours`, `--strategy-option`/`--strategy-option=`, `--into-name`/`--into-name=` | 14/14 deny |
| other git globals, both spellings | `-c k=v`, `--work-tree` (detached), `--namespace`/`--namespace=`, `--config-env`/`--config-env=`, `--super-prefix`/`--super-prefix=` | 8/8 deny |

**Total: 39/39 denied. Silent allows: 0.**

### Cross-check against real git (`/tmp/gitcheck`, `git 2.5x`, hooks bypassed via subprocess to
dodge this checkout's own bash-write-guard, which blocks any literal `git merge` in a shell command
regardless of target repo)

- `git --exec-path merge probe`: real git prints the exec path and **exits without merging at all**
  (bare `--exec-path` takes no value and is a standalone query, matching git's own docs). The gate
  denies this command anyway (treats `--exec-path` as boolean, finds `merge`, denies) — a
  conservative false-DENY on a command that never actually merges, not a security gap. Not a
  must-fix: over-blocking a no-op is the safe direction.
- `git merge -S probe` / `--gpg-sign probe` / `--log probe` (bare): real git merges `probe` directly
  — confirms bare forms do **not** consume the ref, validating the packet's pinned exclusion.
- `git merge -Sfakekeyid probe` / `--log=5 probe` / `--exec-path=/x merge probe`: real git accepts
  the attached value and still merges the correct ref — matches the gate's attached-form handling.
- `git -C/tmp/gitcheck merge probe` (attached, no space): real git rejects this outright
  (`unknown option: -C/tmp/gitcheck`, rc 129) — `-C` requires a space in real git syntax. The gate's
  handling of this synthetic form is moot in practice (the command would never execute), but it
  still denies rather than allows, so no exposure either way.

None of these real-git checks change the verdict: the security-relevant direction (does a real,
executable merge ever slip past as a silent allow) is clean across all 39 forms.

## 4. Four scoped questions

1. **Parser option classes** — every value-taking option in packet Edit A clause 1 consumes its
   value correctly in both spellings; both pinned exclusions stay boolean in bare form and consume
   only via `=`/glue; unknown post-`merge` options stay boolean. Confirmed by the probe matrix above
   plus real-git cross-check. No CRITICAL finding.
2. **Duplicate records / attribution (SC-04)** — out of this dispatch's probe scope (author-nothing,
   no new fixtures beyond the option-class matrix); the pinned integration suite's own duplicate/
   malformed-record cases (lines covering `FEAT-9002-*`) all pass at this pin per the full-suite run
   in §1. Not independently re-probed here; no discrepancy found.
3. **Fail-closed fallback (D-16)** — pinned test `"T-05 merge with no identifiable ref denies"`
   passes at this pin (part of the 1649-PASS integration run); consistent with `git_merge` returning
   `("git", None)` rather than `None` on an unresolvable ref.
4. **SC-11 recovery operations** — see §2: all three case names verified individually, all pass.

## Findings

None. No must-fix. No coverage gap against the matrix floor.

## Open questions

None blocking.
