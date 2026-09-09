# Code review — T-05 merge-gate.py parser rewrite — c17

**Verdict: PASS.** I read exactly the two files in scope
(`.claude/skills/harness/bin/merge-gate.py`, `tests/integration/test-merge-gate.py`) at the diff
`e374c9a2..94b5e465` (+50/-26). No must-fix. One informational note (below) that falls outside my
two-file scope and is not gating.

## Stage 1 — spec compliance

Every changed line traces to D-16/D-17 and packet Edit A's four clauses. No scope creep, no
omission: `main()`, `feature_for()`, `head_branch()`, `deny()`, `repo_pinned()` and the
`gh_merge`/`nested_merge` route are byte-identical in the diff, matching "What must NOT change."

### Q1 — parser option classes (exhaustive)

Enumerated `merge_target`'s `values` (`merge-gate.py:61-62`) and `git_merge`'s
`globals_with_values` (`:76-77`) against `man git` and `man git-merge` (git 2.50.1, this machine),
then empirically confirmed detached-form behavior against real git in a scratch repo
(`/tmp/bug1309-probe`, outside the worktree, no HEAD ever moved in this checkout):

- `--namespace`, `--config-env`, `--attr-source`, `--git-dir`, `--work-tree` all confirmed to
  accept the space-separated (detached) form against real git (e.g. `git --attr-source HEAD
  status` succeeds) — all present in `globals_with_values`.
- `-C`/`-c` confirmed **detached-only**, no sticky/attached form (`git -Cstatus` and `git
  -cfoo.bar=baz` both error `unknown option`) — matches the exact-token-equality test in
  `option_end`.
- `--exec-path` confirmed **bare-and-exit**: `git --exec-path status` prints the path and never
  runs `status` — correctly excluded from the value set (consuming the next token would be wrong
  either way, since real git never reaches the subcommand when `--exec-path` is bare).
- `--list-cmds=<group>` confirmed **attached-only** (`git --list-cmds main status` →
  `unknown option: --list-cmds`, real git never merges on this input either) — correctly excluded,
  and harmless even though excluded since git itself refuses the detached form.
- `-S`/`--gpg-sign` and `--log` (post-`merge`, optional-argument, attached-only per `git-merge(1)`)
  are correctly excluded from `merge_target`'s value set — a bare `-S`/`--log` does not consume the
  ref token.
- Traced all three previously-silent escapes through the new code by hand and confirmed they now
  deny: `git merge -F <f> feature/test` → `-F` consumes `<f>` (`option_end`), target resolves to
  `feature/test`; `git merge --cleanup strip feature/test` → same; `git --attr-source HEAD merge
  --no-ff feature/test` → `--attr-source` consumes `HEAD` in the global walk, `merge` is correctly
  located at index 2. All three are also asserted directly by the new integration cases and pass
  (see Q4 command below).
- Tested one adversarial idea not in the packet — smuggling `--abort` past the control-op
  exemption via `git merge -- --abort` (git's `--` end-of-options idiom, which would make
  `--abort` a literal ref rather than the control op). **Verified not exploitable**: real git
  refuses to create a ref named `--abort` at all (`git branch -- --abort` →
  `fatal: '--abort' is not a valid branch name`), so no real ref can collide with the three
  control-op literals. No finding.

**Answer: no missing value-taking option found in either position or spelling.** The class is
complete against git's own documented and empirically-confirmed option lists.

### Q2 — duplicate records / attribution (SC-04)

Unaffected: `feature_for()` (attribution) and `main()`'s duplicate-owner branch are outside this
diff's touched lines (confirmed by the diff hunk, which only replaces `git_merge` and adds the four
helper functions). The two malformed-record fences and the duplicate-record case
(`tests/integration/test-merge-gate.py:128-172`, pre-existing, untouched) all still pass:
`T-05 duplicate valid records claiming the branch deny naming both`,
`T-05 single owner plus unrelated malformed record still allows`,
`T-05 unrelated non-object feature record does not block healthy merge`,
`T-05 no-record branch ignores unrelated malformed record` — all `ok` in my run (below). SC-04's
attribution rule is unwidened and unnarrowed by this delta.

### Q3 — fail-closed fallback (D-16)

Confirmed by hand-trace: `git merge --file <path>` (no ref) → `merge_target` consumes `<path>` via
`--file`'s entry in the value set, the loop exhausts with no further token, returns `(True, None)`
→ `git_merge` returns `("git", None)` → `head_branch` falls back to `local_branch(cwd)` → local
record decides. This is distinct from the `--abort`/`--continue`/`--quit` path, which returns
`(False, None)` → `git_merge` returns bare `None` (not `("git", None)`) → `main()`'s
`not merge_ref(command)` guard exits before any branch resolution. The two return shapes are
correctly kept separate — this is the ordering D-16 calls load-bearing.

### Q4 — SC-11 recovery operations, individually

```
$ git grep -n "T-05 merge --abort on an owing branch allows" -- tests/integration/test-merge-gate.py
192:    ("git merge --abort", "T-05 merge --abort on an owing branch allows"),
$ git grep -n "T-05 merge --continue on an owing branch allows" -- tests/integration/test-merge-gate.py
193:    ("git merge --continue", "T-05 merge --continue on an owing branch allows"),
$ git grep -n "T-05 merge --quit on an owing branch allows" -- tests/integration/test-merge-gate.py
194:    ("git merge --quit", "T-05 merge --quit on an owing branch allows"),
```
Each is its own tuple in the `for` loop at `:191-199`, each individually driven through `check()`
with `d is None` (no permissionDecision object). `fixture()` (`:23-40`) does
`git init -q -b feature/test` and the owning record's `branch` is `"feature/test"`, so
`local_branch(cwd)` resolves to the owing branch — the staging the packet flagged as
load-bearing is present.

## Stage 2 — code quality (fail-open hunt)

Ran the file directly (`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gate.py`):
all 34 cases `ok`, `ALL PASSED`, including all 26 T-05-gated names and the 8 pre-existing ones.

Traced every branch of the four new/changed functions (`option_end:46-47`,
`first_subcommand:50-58`, `merge_target:60-73`, `git_merge:75-83`) for the classes named in my
dispatch:

- **Off-by-one / run off the end**: `option_end` only *computes* `index+1`/`index+2`, it never
  dereferences `tokens[index+2]`; every caller re-checks `index < len(tokens)` before the next
  `tokens[index]` read. Traced `git merge -F` (value-taking option with no following token at all)
  — loop exits cleanly via the `while` guard, returns `(True, None)`, no `IndexError`.
- **Control-op check at the wrong position**: the `--abort`/`--continue`/`--quit` check runs once
  per *live* (non-consumed) token in the walk — a token already eaten as a preceding option's value
  (e.g. `git merge -m --abort feature/test`) is never re-examined, matching real git's own
  behavior (confirmed empirically: `git tag -m --something test-tag-1` set the tag message to the
  literal string `--something`, proving git's required-string options consume the very next token
  regardless of its spelling). No wrong-position reachability found.
- **Exception → silent exit 0**: none of the four new functions contains a `try`/`except`; nothing
  in them can raise given the bounds analysis above, so there is no new path into `main()`'s
  pre-existing (unchanged, out-of-scope) exception handling.

Grades (`code-grade.py --json` against the two-file diff's functions, bar 4):

| function | cyclomatic | cognitive | ABC | grade | bar | result |
|---|---|---|---|---|---|---|
| `option_end` | 1 | 1 | 2.0 | 5 | 4 | PASS |
| `first_subcommand` | 3 | 3 | 4.7 | 5 | 4 | PASS |
| `merge_target` | 4 | 5 | 7.1 | 4 | 4 | PASS |
| `git_merge` | 3 | 4 | 6.7 | 4 | 4 | PASS |

All four gated names pass at bar 4, per D-17.

## One informational note (not gating, not in my two-file scope)

`code-grade.py --base $(git merge-base origin/main 94b5e465) --head 94b5e465` (the canonical range
`validate-digest.py` recomputes, covering the whole feature not just T-05) shows T-05's own
`verify:` block in `plan.yaml:1063` only takes `min(grade)` over
`('git_merge','words','direct_merge','gh_merge')` — it does **not** name `option_end`,
`first_subcommand` or `merge_target`, the three helpers this very delta introduces, even though
D-17's `because:` and the packet's clause 4 both say "the bar binds `git_merge` **and the helpers
this change adds**." Substantively harmless today — all three measured at grade 4/5/5 above — but
the mechanical gate as currently worded would not have caught a future regression of those three
specific helpers below bar 4. `plan.yaml` is outside my file scope for this dispatch, so I record
this as an open question rather than a finding against the two files I reviewed.

## Overall code grade (canonical range, whole feature)

`code-grade.py --base 6ad7233f (merge-base origin/main 94b5e465) --head 94b5e465 --json`: 57
records, 4 `FAIL`, all grade 2 / severity `med` (never blocks the build): `main` in
`merge-gate.py` (pre-existing, `main:154`, already carries its own `GRADE-2 REASON` comment,
explicitly excluded from T-05's own grade gate by D-17 — pre-existing and unchanged, zero delta in
this diff), plus three grade-2 test functions in `tests/integration/test-check-state.py`,
`test-hooks-install.py` and `test-post-merge-sweep.py` — all outside my two-file scope, from
earlier tasks (T-06/T-07), unchanged by this delta. No grade-1 or below-bar-3 production record
anywhere in the range → `code_grade: grade_2`.

Reason for the one gated record in my scope (`main`, `merge-gate.py:154`): pre-existing GRADE-2
orchestration boundary, carries its own source comment, zero lines touched by this delta, D-17
names it excluded from T-05's grade assertion by design.
