# Security review — BUG-1309 c17 panel — merge-gate.py `git_merge` rewrite

**Verdict: PASS.** No must-fix. The rewrite closes the option-class as a class, not just the three
measured instances; no surviving silent-allow found by manual trace, a 27-case adversarial python
sweep of the pinned parser, or the pinned integration suite.

## Read and measured
Read both files in scope in full at `94b5e46` (merge-gate.py all 198 lines; test-merge-gate.py the
new blocks + `fixture()`/`gate()`/`check()` helpers). Measured, at the pin:
- `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gate.py` → all 34 cases print
  `ok`, `ALL PASSED`, exit 0 (individually confirmed the three SC-11 case lines, not a file grep —
  `T-05 merge --abort/--continue/--quit on an owing branch allows` each print `ok` on their own
  line).
- `code-grade.py .claude/skills/harness/bin/merge-gate.py --json` → `git_merge` cyclomatic 3 /
  cognitive 4 / abc 6.7 → **grade 4, PASS**; `main` grade 2 FAIL (excluded by name, matches packet).
- A 27-case pure-Python sweep of `merge_ref()` imported directly from the pinned file (no shell,
  no HEAD movement — this sandbox's `bash-write-guard` blocks every `git merge`/undetermined-git
  invocation outright, so verification is against the parser itself plus the fixture-driven suite,
  which already runs real `bash merge-gate.sh` subprocesses). Full input/output table below.

## Threat model — bypass of an enforcement gate, not a web-app surface
This script is a PreToolUse hook; the "input" is a shell command line an agent/human is about to
run, the "output" is a permission decision. The only interesting attack is ELEVATION: a command real
git executes as a merge that this parser fails to recognize or misresolves — a silent allow.

## The four scoped questions

**Q1 — parser option classes.** Traced `option_end`/`first_subcommand`/`merge_target`/`git_merge`
by hand against every value-taking option in real git's own documented sets (global: `-C -c
--work-tree --git-dir --namespace --config-env --super-prefix --attr-source`; merge: `-F --file
--cleanup --into-name -m --message -s --strategy -X --strategy-option`) — the code's two sets match
those lists exactly, and the two named exclusions (`--exec-path` value-taking only attached;
`-S`/`--gpg-sign`/`--log` optional-arg, never detached-consuming) are correctly absent from both
sets. The three previously-silent commands now resolve the real ref:
`merge_ref("git merge -F /tmp/message feature/test") == ('git','feature/test')`,
`merge_ref("git merge --cleanup strip feature/test") == ('git','feature/test')`,
`merge_ref("git --attr-source HEAD merge --no-ff feature/test") == ('git','feature/test')`
(measured directly, see sweep below) — matching the fixture-suite denies. Swept 27 additional forms
(attached/detached spellings of every value-taking option, `-C`/`-c` attached and detached,
combined `-s -X`, `-m`/`-F` with no trailing ref, `--exec-path` bare-before-`merge`, `-S`/
`--gpg-sign`/`--log` all three spellings, boolean flags after `merge`): every case that real git
would actually merge resolves `('git','feature/test')`; every case where the ref is genuinely
unrecoverable (`--file` with no ref, `-m feature/test` where `-m` eats the only token) resolves
`('git', None)` — clause-2 fail-closed, not a silent allow, and matches D-16. No unknown-option-
after-`merge` case swallows the ref (`--no-ff`, `--no-verify`, `--squash` all leave the ref intact).
**No surviving silent allow found in the class.**

**Q2 — duplicate records / attribution (SC-04).** `feature_for`/`head_branch` are unchanged by this
diff (confirmed: outside the diff hunks). The rewrite only makes the *input* to `feature_for`
(the resolved branch string) more accurate than before — it cannot widen or narrow the
duplicate-detection logic itself. Fixture suite confirms the four attribution cases still pass
individually: `duplicate valid records claiming the branch deny naming both`, `single owner plus
unrelated malformed record still allows`, `no-record branch ignores unrelated malformed record`,
`unrelated non-object feature record does not block healthy merge`. No regression.

**Q3 — fail-closed fallback (D-16).** Confirmed by trace and by the sweep: `git merge --file
/tmp/msg` (no ref) → `git_merge` returns `("git", None)`, `head_branch`'s
`if kind == "git" and value:` is false (value is `None`) → falls to `local_branch(cwd)`. Preserved
exactly as specified; the new `merge_target` never returns `(True, None)` in a way that skips this
path.

**Q4 — SC-11 recovery operations.** Verified individually (not file-global grep): `--abort`,
`--continue`, `--quit` each hit `merge_target`'s `token in {"--abort","--continue","--quit"}` check
*before* the option/value walk, at whatever position they appear (`-v --abort` also correctly
returns `None`, `--abort feature/test` also correctly returns `None` since `--abort` is inspected
first) → `git_merge` returns `None` → `main()`'s `if not merge_ref(command): return` exits before
any branch resolution — no permissionDecision object, confirmed live by `gate()`'s stdout-empty
check, not a synthesized assertion. All three integration cases print `ok` individually.

## Other checks (dispatch's "Change" section)
- **Tampering via malformed `feature.json`:** attribution code unchanged; already covered by Q2.
- **Fail-open on exception/`gh` outage:** `main()`'s try/except and the DEC-138 "GitHub is a mirror,
  never a gate" allow-on-outage path are both unchanged by this diff (outside the hunks). The new
  token functions (`option_end`, `first_subcommand`, `merge_target`) have no code path that can
  raise (every array-index access is behind its own `while index < len(tokens)` guard) — no new
  exception surface, so the existing fail-closed exception handler behavior in `main()` is
  unaffected by the parser change.
- **Information disclosure:** `deny()` and the reason-string templates are outside the diff; no new
  message construction was added. No new leakage.
- **Non-finding, noted for the record:** `git --exec-path merge feature/test` is treated by the
  parser as a merge (over-deny), even though real git's bare `--exec-path` prints the path and exits
  without running `merge`. This is the *conservative* direction (fail-closed, not fail-open) and is
  exactly the behavior the implementation packet's clause 1 mandates for this exact case ("consuming
  a following token for the bare form swallows `merge` and reintroduces a silent allow" — i.e. the
  alternative would be the vulnerability, not this). Not a finding.
- Considered whether abbreviated long options (`--abo` for `--abort`) could evade the exact-match
  `{"--abort","--continue","--quit"}` check. Could not empirically confirm git's abbreviation
  behavior here — this sandbox's `bash-write-guard` blocks every git invocation it cannot positively
  classify as not moving HEAD, including a bare `git --exec-path` probe in a disposable `/tmp` repo.
  Even if real, the failure mode is fail-closed (a legitimate `--abort` gets wrongly denied), not a
  bypass of the receipt gate — out of this dispatch's threat model (silent allow), not raised as a
  finding.

## Out of lens / already ruled
`gh_merge`, `nested_merge`'s depth cap, and shell-variable indirection are unchanged/ruled out of
scope (R-2) and not re-litigated. `words`/`is_bin`/`direct_merge` are unchanged by this diff (outside
the hunks); the dispatch's request to hunt the token-splitting layer was exercised via the 27-case
sweep (which runs through `merge_ref` → `words` → `direct_merge` end to end) and found no gap
attributable to this diff.
