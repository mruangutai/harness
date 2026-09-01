# Security Review — BUG-1055-code-grade-absent-path — c0

## Scope
In scope: argv/subprocess surface of the new `_tree_has_path` helper and the changed
`_git_show` fallback in `.claude/skills/harness/bin/code_grade.py` (diff `9f2a070..e353c7e`).
Diff also touches only test files and feature bookkeeping (`git diff --stat` confirms the file
set matches the dispatch exactly — no extra files). No shell, no new dependency, no logging
sink, no new network/auth surface.

## Verdict: PASS — no must_fix, no exploitable finding

## Findings (all info-level, none blocking)

**F1 — `ref` has no internal validation in `_tree_has_path`/`_git_show`; safety is entirely a
call-site invariant (info, verified by reading + execution).**
`_tree_has_path`'s argv is `["git", "-C", root, "--literal-pathspecs", "ls-tree",
"--name-only", "-z", ref, "--", path]` (`code_grade.py:316-321`) — `ref` sits *before* `--`,
so an option-like ref string (e.g. `--abbrev=1`) would be consumed as a flag, not a revision.
Verified live: calling `_tree_has_path(root, "--abbrev=1", "old.py")` directly causes git to
mis-consume the flag and then fail with `fatal: Not a valid object name old.py` — the function
**raises `RuntimeError`, it does not misbehave silently.** This is unreachable today: the only
two production call sites (`_resolve_base_source` → `base_oid`, `_gate_file_records` →
`head_oid`) pass values exclusively from `commit_oid()`, which already rejects any revision
`str`-checked and `startswith("-")` before resolving it through `git rev-parse --verify
--end-of-options <rev>^{commit}` — so `ref` is always a git-verified hex OID by the time it
reaches `_tree_has_path`, never raw caller text. Recorded as a defense-in-depth gap for future
callers, not a live gap in this diff.

**F2 — `path` is correctly guarded by `--`; verified with an adversarial option-like filename
(info, verified by execution).**
Ran `_git_show(base_oid, "--upload-pack=/bin/sh")` against a repo where that path is absent —
returned `None` cleanly, no command execution, no misparse. Ran it again where a real file
named `-weird.py` (leading dash) exists at `head` and is absent at `base` — `_git_show`
correctly read the file's content at `head` and correctly returned `None` at `base`. The `--`
boundary does its job in both directions (rejecting the dangerous case, accepting the
legitimate dash-prefixed case).

**F3 — `--literal-pathspecs` is scoped correctly (info, verified by reading).**
It is passed only on the new `ls-tree` probe's own `subprocess.run` argv — each call builds an
independent argv, so it has no effect on the untouched `git show f"{ref}:{path}"` call in
`_git_show` (`code_grade.py:328`), which never was a pathspec consumer anyway (it addresses a
blob by `ref:path` syntax, not a pathspec argument) — nor on `_git_output`'s `git diff`
invocation, which takes no path arguments. The probe is the only call that accepts an arbitrary
tracked path as a bare pathspec after `--`, and it is the only one hardened. No under-scoped or
over-scoped application.

**F4 — no leakage of git stderr, ref, path, or file content into the gate's output (info,
verified by execution).**
Forced a genuine `RuntimeError` (bogus ref against a repo containing a fake secret in
`secret.py`) and inspected the exception message: `'fatal: not a tree object'` — generic git
diagnostic text only, never file content, never the graded repository's contents. Neither
`_tree_has_path` nor `_git_show` contains a `print`/log call (grepped the whole file); the
`RuntimeError` propagates as an exception, not a formatted report line.

## STRIDE — fail-open assessment of the trust boundary (DEC-174: this feeds the review gate)

Traced whether a crafted branch/path could make `code_grade.py` (or the CLI wrapping it,
`code-grade.py`) **silently pass** (report zero findings) instead of failing. Two directions
matter, both verified:

- If `_tree_has_path` ever wrongly reports "absent" for a path that truly has base content,
  `_resolve_base_source` returns `None`, and `_gate_file_records` treats every function in the
  new file as having **no prior grade** (`before is None → gated.append(record)`). That is the
  *strict* direction — everything becomes gated, nothing is silently excused.
- If it ever wrongly reports "present" when git genuinely can't answer, `_git_show` re-raises
  `RuntimeError`, crashing the run rather than emitting a clean report. Not silent-pass; it is
  fail-closed (loud, not quiet).

Independently confirmed by executing the new integration test
`test_absent_new_path_grades_the_range` (`test-code-grade-cli.py:290`): a range whose new,
already-below-bar function (`added_risky`, deliberately over the cyclomatic bar) is later
removed from the worktree still reports `QUALNAME: added_risky`, `RESULT: FAIL`, and exit code
1 — the exact case the pre-fix code silently dropped by crashing mid-loop. Ran both
`test-code-grade-cli.py` and `test-code-grade.py` directly; both `PASS`.

Note: `validate-digest.py`'s SEC-01 range-binding (merge-base-derived `reviewed:` range) does
not itself re-execute `gated_set()` — it trusts the reviewer's self-reported `code_grade` enum,
bound only to a verified range. This diff does not touch that trust boundary and does not
change its posture; noted as pre-existing and out of scope for this fix (assessed and
dismissed, not a finding here).

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| `path`/`old_path` from a reviewed diff's own filenames → `git ls-tree`/`git show` argv | Tampering (argument injection via crafted filename) | true — `--` boundary verified live against an option-like filename |
| `ref` argv position (before `--`) → `git ls-tree` | Tampering (option injection via ref) | true — only ever fed a `commit_oid()`-verified OID; direct bypass verified to fail closed, not silently |
| gate silently passing on absent/removed path | Tampering / Repudiation (fail-open grading) | true — verified the range-strict direction and the crash-if-genuinely-unknown direction; neither yields a silent clean report |
| git stderr / exception text reaching the gate's output | Information disclosure | true — verified generic-only diagnostic text, no file content |

## Open questions
None blocking.

## files_touched
None (advisory only).
