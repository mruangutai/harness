# QA Gate — BUG-124-run-dir-squad-suffix — cycle 2 (confirmation)

## VERDICT: PASS — `matrix_ok: true`

The single cycle-1 `must_fix` (naked `python3 -c` launch at `dispatch-guard.sh:34`, breaking
`test-no-distribution.py` case7) is cleared at `c06c483c`. All other cycle-1 rulings (matrix
resolution → `{unit, integration}`, the three `bugfix` predicate evaluations, the assertion-strength
review, the Q1 test-first ruling) stand unchanged and were not re-litigated, per dispatch.

Working tree confirmed clean myself: `git -C <worktree> status --porcelain` → empty. HEAD =
`c06c483c` on `feat/BUG-124-run-dir-squad-suffix`.

## 1. Re-resolved `unit` kind — now **satisfied**

- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-no-distribution.py` → **34 of 34 checks PASS**,
  `ALL PASS`, exit 0. Both case7 halves green: `case7_every_python_launch_isolates_the_cwd` (no naked
  launches) and `case7_the_scan_can_see_the_invocations`. I independently recomputed the counts the
  paired check gates on (`.claude/skills/harness/bin/*.sh`, 13 scripts): `hits=18` (`python3 -I`,
  needs `>=16`) and **`safe_hits=4`** (`python3 -c` + same-line `sys.path.pop(0)`, needs `>=3`) — the
  fix's new same-line bootstrap at `dispatch-guard.sh:37` is exactly the fourth site the assertion now
  counts.
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-harness-boundary.py` → **60 of 60 checks PASS**,
  `ALL PASS`, exit 0 (unaffected by T-02; unchanged from cycle 1).

**`unit`: satisfied.**

## 2. `integration` kind re-run at new commit — still **satisfied**

`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-dispatch-guard.py` → **69 of 69 cases
passed**, exit 0.

## 3. Red-capability confirmed at the new commit

`DISPATCH_GUARD_BIN=<main-checkout guard>` (md5 `ca904b2906ad8d44662db428cb2dbc89`, verified myself
against `.claude/skills/harness/bin/dispatch-guard.sh` in the main checkout before use) against the
worktree's test file at `c06c483c` → **61 of 69 cases passed**, with exactly the same 8 red lines as
cycle 1: `case 18a` (bare + `18a/b` combined-message), `case 18b`, `case 18g`, `case 21`-message,
`case 22` (×2), `case 23`-message. The gate still reports red against the old guard binary; a fully
green result here would itself have been a FAIL. It was not.

## 4. Behavioural-equivalence ruling on the launch change (new for this cycle)

Read directly from `dispatch-guard.sh:27-59` at `c06c483c`:

- **(a) non-isolated interpreter — HOLDS.** Line 37: `python3 -c '...' "$GUARD_BIN_DIR" 2>/dev/null
  <<'PY'` — no `-I` flag anywhere in the launch. PyYAML (user site-packages, D-03) remains reachable.
- **(b) `sys.argv[1]` still resolves to `$GUARD_BIN_DIR` — HOLDS.** `python3 -c '<code>' arg1` sets
  `sys.argv[0]='-c'`, `sys.argv[1]=arg1`; `$GUARD_BIN_DIR` is the sole trailing argument on line 37.
  The heredoc body (`sys.path.insert(0, sys.argv[1])` line 41, `hb.resolve_root(sys.argv[1], ...)`
  line 46) consumes it unchanged from the pre-fix version — only the launch syntax moved, not the
  argument wiring. Confirmed by running: case 16 ("macOS system Python can run the dispatch guard")
  and case 12 ("the claim lands in the DECLARED worktree") both pass at 69/69, and both require
  `GUARD_BIN_DIR`-relative module resolution to succeed.
- **(c) `2>/dev/null` redirect survives — HOLDS.** Same line 37, immediately after the closing quote
  of the `-c` program, unchanged position relative to the command.
- **(d) `if _globs=$(...)` still captures the python exit status — HOLDS, confirmed by running.**
  Lines 37–55: the entire `python3 -c ... <<'PY' ... PY` heredoc sits inside one `$(...)` command
  substitution, and `if _globs=$(...); then` (closing at line 55) is untouched by the diff — only the
  substitution's *interior* changed shape (multi-line body → heredoc). Case 21 ("grant-less manifest
  is not refused" / "declares no run-dir write grant") and case 23 ("unparseable manifest is not
  refused" / "vocabulary derivation failed") are the pair the plan cites (F-4) as depending on this
  distinction, and both pass their full 3-check sets at 69/69 — the benign-empty-glob-list case and
  the broken-parse case are still told apart by exit status, not conflated.

All four properties hold, three confirmed by direct reading, one ((b)/(d)) additionally confirmed by
the passing integration cases that depend on it — preferring the run where a property was checkable
by running, per instruction.

## 5. T-02 `verify:` clause — cross-checked verbatim, then re-run

Read `plan.yaml:325` directly: the string matches the dispatch's copy character-for-character
(confirmed by direct comparison, not just presence). Re-ran verbatim at `c06c483c`:

```
python3 tests/integration/test-dispatch-guard.py && python3 -c '...' | .claude/skills/harness/bin/dispatch-guard.sh 2>&1 | grep -q "eng-t01"
```

→ integration suite prints `69 of 69 cases passed`; piped guard invocation matched by
`grep -q "eng-t01"`. **Combined exit: 0.** This is the strongest available behavioural-equivalence
probe (it exercises the guard end-to-end through the exact launch block that changed) and it passes.

## Full-project sweep re-investigated (automated post-hoc check fired again)

The delivery harness's own post-hoc check flagged `suite: pass` against an independent
`run-unit-tests.sh` sweep exiting 1 — the identical class of complaint cycle 1 investigated and
recorded in its Addendum. I re-ran the full sweep MYSELF, twice, from this worktree at `c06c483c`
(`env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh`), rather than accepting
either the automated flag or the cycle-1 finding on faith:

- **Both runs: exit 1, identical failing file set, deterministic this time** (unlike cycle 1's own
  non-deterministic pair): `test-run-unit-tests-kinds.py`, `test-run-unit-tests-layout.py`,
  `test-check-plan-routes.py`, `test-check-domain.py`. Same four files cycle 1 named.
- **Failure signatures match cycle 1 exactly:** `no harness root could be resolved from <tmpdir>/
  .claude/skills/harness/bin — refusing to run` (root-resolution race under concurrent load — four
  sibling BUG worktrees are still live per this dispatch's own constraint), plus
  `case_19b_unresolvable_root_exits_2_not_0` importing `harness_boundary` inside a synthetic broken
  tree, plus `test-check-domain.py`'s `sweep/clean-tracked RED` non-discriminating mutation
  self-test.
- **None of the four failing files are in this diff.** `git show c06c483c --stat` names only
  `.claude/skills/harness/bin/dispatch-guard.sh` (this cycle's sole change). The full BUG-124 diff
  (both cycles) touches `harness_boundary.py`, `tests/unit/test-harness-boundary.py`,
  `dispatch-guard.sh`, `tests/integration/test-dispatch-guard.py` only — confirmed again by
  `git diff -U0 80ce35d1..e7994376 -- harness_boundary.py`, hunks only at `@@ -21,0 +22 @@` and
  `@@ -806,0 +808,98 @@`; `resolve_root` (the function whose behavior the root-resolution race
  depends on) is untouched by either cycle.
- **The two files this gate is actually scoped to remain deterministic across both sweep runs:**
  `test-harness-boundary.py` and `test-dispatch-guard.py` show zero failures inside both full-sweep
  logs (grepped for their own script markers), consistent with the isolated 60/60 and 69/69 runs in
  §1–2.

**Conclusion, now measured twice independently rather than inferred once: the full-sweep exit 1 is
real, reproducible on THIS diff's commit, but its failing surface is entirely pre-existing,
unrelated code untouched by BUG-124.** `matrix_ok: true` and `suite: pass` stand, scoped to the
`unit`/`integration` kinds resolved against the files this diff actually changed, per the dispatch's
explicit bounded-evidence instruction (four live sibling BUG worktrees, do not walk the whole tree
as this gate's own evidence). This is a standing harness-maintenance defect (root-resolution race +
non-discriminating mutation self-test in `test-check-domain.py`), independent of BUG-124 — flagged
in `open_questions`, not treated as a `must_fix` here.

## Not re-opened (per dispatch, non-goal)

The above full-sweep investigation supersedes cycle 1's own addendum with a second, deterministic
confirmation. This is the worktree-hosted-grading defect already recorded as Q2 in STATE.md.

## SC evidence map

Unchanged from cycle 1 (`notes/qa-c1.md` §"SC evidence map") — no SC's evidence source changed by
this fix cycle.

## Open items

None new. Cycle-1's two non-blocking receipt-hygiene notes (check-count mismatch, diff-stat
attribution reversal) still apply and are unaffected by this cycle.
