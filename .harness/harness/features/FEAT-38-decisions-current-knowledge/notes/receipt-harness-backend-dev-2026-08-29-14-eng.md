# Receipt — harness-backend-dev — fix-claims-checker (F-1/F-3/F-4, F-5 skipped) + SEND-BACK c1 (Item A/B/C)

BLUF: send-back closed. Item A reverted the gratuitous `frozenset` reformat —
`ALLOWED_FIRST_TOKENS` is byte-identical to pre-hardening, the three other
ADDED constants are now plain set literals too (no mixed style). Item B adds
an end-to-end regression test pinning rule 5 (neutralized
`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM`/`GIT_CONFIG_NOSYSTEM`) — the only rule
of the six with no prior test. Item C: this digest is non-empty, fenced, all
keys present. All 10 F-3 vectors still refused, all six payloads still
absent. Suite is now FULLY GREEN (0 FAIL, exit 0) — the marker mismatch that
manufactured the one prior FAIL is gone with the revert.

## Item A — constant reformat reverted

```
ALLOWED_FIRST_TOKENS = {"git", "grep"}
```
Byte-identical to pre-change (confirmed via direct `sed` extraction, no
frozenset anywhere in the file — `grep -n frozenset` empty). This matches
`DECISIONS.md:6290`'s live marker verbatim:
`<!-- claim: grep -F "ALLOWED_FIRST_TOKENS = " .claude/skills/harness/bin/check-decision-claims.py :: ALLOWED_FIRST_TOKENS = {"git", "grep"} -->`.
The three ADDED constants are now plain set literals, no mixed style:
```
ALLOWED_GIT_SUBCOMMANDS = {
    "grep", "log", "show", "ls-files", "rev-parse", "cat-file", "diff",
}
_GIT_OPEN_PAGER_LONG = {"--open-files-in-pager"}
_GREP_FILE_OR_DEVICE_LONG = {"--file", "--devices"}
_GREP_FILE_OR_DEVICE_LETTERS = {"f", "d"}
```
Behaviour unchanged: same refusal messages verbatim (module-level constants,
never mutated at runtime).

## Item B — rule 5 regression test added

`test_ambient_git_config_env_is_neutralized_and_payload_does_not_run` in
`test-check-decision-claims.py` (registered in `TESTS`). Config key used:
**`diff.external`** (same key as the existing F-3 `-c diff.external=` vectors,
reached ambiently this time, not via `-c`) — chosen because `git diff
--ext-diff` is a *bare* allowlisted subcommand with no options at all, so the
test exercises rule 5 in isolation from rules 1/2/3/4/6.

Mechanics: builds a scratch git repo (`git init` + one commit + an
uncommitted edit to a tracked file, so `git diff` has real content to
diff), writes a hostile `~/.gitconfig`-equivalent file containing
`[diff]\n\texternal = touch <unique tmp path>`, then spawns the checker
itself (not `run_checker` — needs a custom `cwd=<scratch repo>` and a custom
env) with `GIT_CONFIG_GLOBAL=<hostile file>` and `HOME=<tmp>` in the
**checker's own process environment** (simulating what a CI runner/dev shell
ambiently sets, never named in the marker or argv). Assertions: (1) not
`REFUSED` — proves rule 1-4/6 didn't block it, so rule 5 is what's actually
under test; (2) the unique payload path does **not exist** afterward — the
behavioural pin, not exit-code-only; (3) exit 0, because once neutralized the
real internal diff runs and its output (`diff --git`) matches the claim's
expected substring — a green run is itself evidence the ambient config was
never consulted.

**Mutation-proof (in-place, hash-verified restore, no `git checkout --`):**
hashed `check-decision-claims.py` (`c74b8efe...`), deleted the
`env=_subprocess_env(),` line at the one `subprocess.run` call site, reran
the full 21-test suite:
```
FAIL - test_ambient_git_config_env_is_neutralized_and_payload_does_not_run: the ambient
  diff.external payload RAN — .../touched was created; rule 5's env override did not
  reach the subprocess.run call: ...
```
**Exactly one test reddened — the new one, as predicted.** All other 20
stayed `ok -` (they don't reach `subprocess.run` with a hostile ambient
config since they're refused earlier or don't touch git config). Restored
the file byte-for-byte from a pre-mutation copy; hash re-verified identical
(`c74b8efe...` both sides); `git status --porcelain` on the file shows only
the legitimate (Item A + Item B) diff, nothing else.

## 1. All ten F-3 vectors, re-run, refused, payload absent (real end-to-end run)

Fixture `/tmp/e2e/decisions.md`, 10 markers, run via
`python3 .claude/skills/harness/bin/check-decision-claims.py --file /tmp/e2e/decisions.md`:

```
(no preceding DEC heading): `git -c core.fsmonitor="touch /tmp/p_f1" status` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed — only a bare subcommand may follow `git`
(no preceding DEC heading): `git -c 'core.fsmonitor=touch /tmp/p_f1b' status` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed...
(no preceding DEC heading): `git -c diff.external=touch --ext-diff` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed...
(no preceding DEC heading): `git -c "diff.external=touch /tmp/p_f2" diff --ext-diff` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed...
(no preceding DEC heading): `git -c alias.zz='!touch /tmp/p_f3' zz` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed...
(no preceding DEC heading): `git -c "alias.zz=!touch /tmp/p_f3b" zz` :: 'nothing': REFUSED: git option '-c' before the subcommand is not allowed...
(no preceding DEC heading): `git status` :: 'nothing': REFUSED: git subcommand 'status' is not in the read-only allowlist (cat-file, diff, grep, log, ls-files, rev-parse, show)
(no preceding DEC heading): `git -C /tmp grep foo` :: 'nothing': REFUSED: git option '-C' before the subcommand is not allowed...
(no preceding DEC heading): `grep -f /tmp/nonexistent` :: 'nothing': REFUSED: grep option '-f' reads from an argument file or a device instead of argv/stdin and is never allowed
(no preceding DEC heading): `git grep -Otouch\ /tmp/p_f4 -e budget .claude/skills/harness/bin/check-domain.sh` :: 'nothing': REFUSED: git option '-Otouch /tmp/p_f4' opens a pager/program directly (-O/--open-files-in-pager) and is never allowed
examined 10 claim(s), 10 failed
EXIT=1
```
Payload check (all 6 paths a naive RCE would produce):
```
safe (absent): /tmp/p_f1
safe (absent): /tmp/p_f1b
safe (absent): /tmp/p_f2
safe (absent): /tmp/p_f3
safe (absent): /tmp/p_f3b
safe (absent): /tmp/p_f4
```
All ten payloads unexecuted, re-measured this cycle (fixture rebuilt fresh,
payload paths cleared before the run).

## 2. T-20 verify (verbatim, cross-checked against `plan.yaml:1375-1381` — identical)

```
$ cd "$(git rev-parse --show-toplevel)"   # = worktree root, confirmed via git rev-parse
$ python3 .claude/skills/harness/bin/test-check-decision-claims.py > /tmp/t20.out 2>&1
$ rc=$?
$ grep '^FAIL' /tmp/t20.out && exit 1      # no output — no FAIL lines
$ test "$(grep -c '^ok - ' /tmp/t20.out)" -ge 5 || exit 1   # ok-count=21, passes
$ exit $rc
T-20 VERIFY RC=0
```
**21/21 `ok -`, zero `FAIL`, exit 0** — the prior single `FAIL`
(`test_live_authority_claims_all_hold`) is gone now that the
`ALLOWED_FIRST_TOKENS` marker matches again (Item A). Separately,
`test-check-decision-anchors.py`: **8/8 `ok -`, exit 0.**

## 3. `run-unit-tests.sh` (from worktree, captured to a variable, `grep`'d — never piped to head/tail)

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh > /tmp/run-unit-tests.out 2>&1
RC=0
$ grep -c '^FAIL' /tmp/run-unit-tests.out
0
```
**Fully green, as predicted: zero `FAIL` lines anywhere in the 3405-line
output, exit 0.** No pre-existing or newly-introduced failures observed.
`test_live_authority_claims_all_hold` now passes (confirmed individually in
§2 and inside this full run — no `FAIL` line names it).

## 4. Final `ALLOWED_*` lines (verbatim, byte-for-byte, post-revert)

```python
ALLOWED_FIRST_TOKENS = {"git", "grep"}
```
```python
ALLOWED_GIT_SUBCOMMANDS = {
    "grep", "log", "show", "ls-files", "rev-parse", "cat-file", "diff",
}
```
`ALLOWED_FIRST_TOKENS` is now byte-identical to the pre-hardening literal and
to `DECISIONS.md:6290`'s marker; no documentor action needed for this
marker. `ALLOWED_GIT_SUBCOMMANDS` remains unmarked (product squad's/
documentor's call, unchanged from prior cycle).

## 5. DECISIONS.md / DECISIONS-INDEX.md — untouched

```
$ git diff --stat -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
(empty)
```
Confirmed empty. Neither file was opened for writing this cycle either.

## 6. Nothing committed; main checkout carries none of this work

```
$ git status --porcelain   # worktree
 M .claude/skills/harness/bin/check-decision-anchors.py
 M .claude/skills/harness/bin/check-decision-claims.py
 M .claude/skills/harness/bin/test-check-decision-anchors.py
 M .claude/skills/harness/bin/test-check-decision-claims.py
(+ pre-existing untracked review/grilling notes and stray root files, not mine)

$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain -- \
    .claude/skills/harness/bin/check-decision-claims.py \
    .claude/skills/harness/bin/test-check-decision-claims.py \
    .claude/skills/harness/bin/check-decision-anchors.py \
    .claude/skills/harness/bin/test-check-decision-anchors.py
(empty — main checkout carries none of this work)
```

## F-4 detail (both checkers) — unchanged from cycle 0, re-verified clean

`extract_claims`/`extract_anchors` still raise `MalformedClaim`/
`MalformedAnchor` on lookalike-but-unparsed marker lines; both malformed-line
tests (`single_colon`, `trailing_text`) pass in §2's 21-test run. No live
false positive (anchor checker: `examined 20 anchor(s), 0 failed` against the
real document, run implicitly inside `test_live_authority_anchors_all_resolve`
in §2).

## F-5 — skipped (unchanged)

The anchor checker's "line past end of file" message still doesn't state the
file's total line count; no existing assertion pins that omission. Left as
advisory per the original dispatch's "skip if not covered" instruction.

## Files touched
- `.claude/skills/harness/bin/check-decision-claims.py` (Item A revert)
- `.claude/skills/harness/bin/test-check-decision-claims.py` (Item B new test)
- `.claude/skills/harness/bin/check-decision-anchors.py` (unchanged from cycle 0, carried in this receipt's file list since it's part of the same working diff)
- `.claude/skills/harness/bin/test-check-decision-anchors.py` (unchanged from cycle 0, same note)
