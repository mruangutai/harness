# Receipt — harness-backend-dev — T-04 — c1

**Verdict: PASS.** `test-post-merge-sweep.py` now covers (a)-(g) — every case T-04 lists plus the
brief-added SKIP-is-not-success case (g), all against REAL `git` fixtures (real `git merge`,
`git merge --squash`, `git worktree add`), a stubbed `gh` on `PATH` (logs every call, no network),
and two red-proof source mutations of `post-merge-sweep.sh` by name (never touched in place —
T-03's delivered file is unmodified). Nobody removed a real worktree; every mutation happened in a
`tempfile.TemporaryDirectory()`.

## Verify — verbatim command and ACTUAL output

```
$ python3 .claude/skills/harness/bin/test-post-merge-sweep.py
PASS: --dry-run exits 0
PASS: --dry-run leaves the terminal worktree standing
PASS: --dry-run mentions the feature id in its output
PASS: --dry-run makes no `gh` invocation
PASS: (a) fast-forward merge succeeds
PASS: (a) MEASURED: fast-forward fires post-merge with hook arg 0
PASS: (a) the Done feature's worktree is gone after the merge
PASS: (b) squash merge succeeds
PASS: (b) MEASURED: squash fires post-merge with hook arg 1
PASS: (b) the Done feature's worktree is gone after the merge
PASS: (c) sweep run from inside its own eligible worktree exits 0
PASS: (c) SELF-EXCLUSION: that worktree is still standing afterwards
PASS: (c) SELF-EXCLUSION: stdout states the sweep declined because it is running inside the worktree
PASS: (c) RED PROOF: with the self-exclusion guard removed, an unguarded sweep DELETES the worktree it is running inside — demonstrating the guard was load-bearing
PASS: (d) sweep over two terminal features exits 0
PASS: (d) SC-11: milestone close call logged for FEAT-30-two-a's OWN milestone (801), checked on its own
PASS: (d) SC-11: milestone close call logged for FEAT-31-two-b's OWN milestone (802), checked separately from FEAT-30's
PASS: (d) both worktrees removed after their own record succeeded
PASS: (e) sweep exits 0 even though the `gh` write for one feature failed
PASS: (e) D-04 ORDER: the feature whose write failed keeps its worktree standing — removal never runs ahead of a confirmed record
PASS: (e) D-04 ORDER: the OTHER feature, whose write succeeded, has its worktree removed
PASS: (f) sweep exits 0 on an unresolved record
PASS: (f) the unresolved record is printed
PASS: (f) the unresolved record's worktree is left standing
PASS: (g) sweep exits 0 even though ship SKIPped
PASS: (g) SKIP IS NOT SUCCESS: a feature whose ship exited 0 but printed `gh-sync: SKIP` keeps its worktree standing
PASS: (g) no milestone-close call was ever made for this feature (ship SKIPped before reaching gh() for the write)
PASS: (g) RED PROOF: gated on exit code alone, the sweep DELETES a worktree whose ship only SKIPped — the destructive fail-open D-04's comment warns about
EXIT=0
```
Exit code: `0`. 27/27 assertions PASS.

## Per-case results
- **(a) fast-forward, arg 0** — worktree added from a topic branch's tip (so its tracked
  `feature.json` already matches the landed blob once `main` fast-forwards); `git merge topic-ff`
  fires the installed hook with `$1=0`; worktree gone after.
- **(b) squash, arg 1** — MEASURED empirically first (throwaway probe script, not committed):
  `git merge --squash` fires post-merge with `$1=1` **before** `main`'s ref advances (squash never
  auto-commits), so the terminal feature under test is landed on `main` in an earlier commit, and
  the squash itself carries only an unrelated file — decouples the squash *shape* (what this case
  tests) from the landing-timing gap. Worktree gone after both `merge --squash` + `commit`.
- **(c) self-exclusion** — sweep invoked directly with `cwd` inside its own eligible worktree;
  worktree survives, stdout carries the decline line. **Red proof**: `_mutated_copy()` flips the
  guard's condition line (`if cwd_real == path_real or …:`) to `if False:` in a source copy (never
  touches T-03's file) — that variant deletes the worktree it's running inside, proving the guard
  was load-bearing.
- **(d) SC-11 per-feature record** — two terminal features, distinct milestones (801, 802); stub
  log checked for a `milestones/801 … state=closed` line and a `milestones/802 … state=closed`
  line, **as two separate assertions** (never a total call count, which a
  ship-the-triggering-feature-twice bug could satisfy).
- **(e) D-04 order** — stub forced to fail exactly the `milestones/901` call (`FEAT-32-order-fails`);
  that feature's worktree stands, `FEAT-33-order-ok` (milestone 902, untouched by the stub) is
  removed. Mechanically this exercises `gh()`'s own `skip()` conversion (a failed `gh` call never
  makes `gh-sync.py` itself exit non-zero — it prints `gh-sync: SKIP` and exits 0, `gh()`'s own
  documented contract) rather than the `ship.returncode != 0` branch; both are the SAME
  "positive-signal gate" in `post-merge-sweep.sh`, and this case demonstrates the write-failure
  side of it distinct from (g)'s never-attempted-write side.
- **(f) unresolved** — an AMBIGUOUS-PREFIX fixture (`FEAT-40` prefixing two landed dirs
  `FEAT-40-amb-one`/`-two`), which is `worktree_terminal.classify()`'s actual `"unresolved"`
  trigger for a short name (confirmed by re-reading the delivered `classify()` and its own
  `test-worktree-terminal.py` cases). **Note on wording**: T-04's case (f) text says "a short-named
  worktree matching no landed directory" — the delivered `classify()` treats a prefix matching
  **zero** landed directories as `exempt_absent` (the class the sweep silently skips), not
  `unresolved`; only a prefix matching **more than one** (or an unparseable/unreadable landed
  `feature.json`, or a `default_branch`/`git ls-tree` resolution failure) is `unresolved`. I built
  the fixture against the real predicate rather than the literal phrase, since `worktree_terminal.py`
  is delivered work I don't touch and its own test suite already fixes what "unresolved" means.
  Flagging this as an `open_question` rather than silently reinterpreting.
- **(g) SKIP is not success** — a Done feature with **no** recorded `github.milestone`; `cmd_ship`
  hits its own `skip("no recorded milestone — nothing to close")` before any `gh` call for the
  write; worktree stands; stub log confirms zero `milestones/…` calls (though `load_config`'s own
  `gh auth status` call does land in the log — the first version of this assertion wrongly expected
  an empty log and failed; fixed to check for the absence of a milestone-close line specifically).
  **Red proof**: `_mutated_copy()` deletes the `"gh-sync: SKIP" in combined` gate (source copy,
  `if False:`) — that variant deletes the worktree on exit-code-0 alone, the exact destructive
  fail-open D-04's comment names.

## Open question
- **Q1**: T-04's case (f) prose ("a short-named worktree matching no landed directory") does not
  match the delivered `worktree_terminal.classify()`'s actual `unresolved` trigger (that shape is
  `exempt_absent`, silently skipped). I built the fixture against the real predicate (ambiguous
  prefix) rather than BLOCKING, since the assertion's *intent* — an unresolved record is printed
  and left standing — is fully satisfiable and tested. Worth reconciling the plan's T-01 intent
  text against T-01's delivered code at some point; not blocking for this task. `blocking: false`.

## Files touched
- `.claude/skills/harness/bin/test-post-merge-sweep.py` (extended, T-03's baseline case
  untouched)

No other file was modified. `post-merge-sweep.sh`, `worktree_terminal.py`,
`feature-worktree.py`, `gh-sync.py` were read only; every mutation used for a red proof lives in
a `tempfile.TemporaryDirectory()` and is discarded when the case's `with` block exits.
