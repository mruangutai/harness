# SC-06 independent re-verification — BUG-1480

**Verdict: SC-06 SATISFIED.** Both (a) ancestry and (b) red-before-fix are independently confirmed
by direct measurement, not inherited from `notes/qa-BUG-1480-c0.md` (read only after this
measurement was complete). One coverage gap found on the REQ-02 direction; see Adequacy below.

## (a) Ordering and ancestry

```
$ git -C <worktree> merge-base --is-ancestor 6b5ae254 d8a99991 ; echo $?
0
```
Ancestry holds: `6b5ae254` is a real ancestor of `d8a99991`, not just chronologically earlier.

Commit subjects and dates:
- `6b5ae254617cdf4` 2026-09-07 20:10:49 -0700 — `BUG-1480 [harness:t-01] cover worktree handoff authority root`
  — `git show --stat`: `tests/integration/test-check-domain.py | 42 ++++...` (42 insertions, 1 file)
- `d8a9999172583eb` 2026-09-07 20:12:14 -0700 — `BUG-1480 [harness:t-02] resolve handoff authorities in owning checkout`
  — `git show --stat`: `.claude/skills/harness/bin/check-domain.sh | 16 +++...` (15 insertions, 1 deletion, 1 file)

Test commit touches only the test file; fix commit touches only the gate script. Test strictly
precedes and is ancestor of the fix. (a) is satisfied.

## (b) Red-before-fix measurement

Method used exactly as specified: never moved HEAD. Added a disposable detached worktree
`git worktree add --detach .claude/worktrees/harness/BUG-1480-qa-sc06-scratch 6b5ae254` (the
bash-write-guard denies ad-hoc `cp`/redirect scratch copies outside domain — confirmed live, matches
Expertise G-06 — so a worktree, not a bare directory copy, was used to get a whole sibling-module
tree at the test commit). Ran the suite from the real worktree with the override:

```
$ cd <worktree> && env -u HARNESS_AGENT_TYPE \
    CHECK_DOMAIN_BIN=<scratch-worktree>/.claude/skills/harness/bin/check-domain.sh \
    python3 tests/integration/test-check-domain.py
rc = 1
FAIL count (grep -c '^FAIL ') = 2
```

Verbatim rows (lines 382-387 of the run):
```
ok    handoff worktree-only main root has no feature dir 
FAIL  handoff worktree-only feature dir resolves exit 2: check-domain: BLOCKED — .claude/worktrees/harness/BUG-1480-wt/.harness/harness/features/BUG-1480-wt-fixture/notes/handoff-build.md: handoff shape (DEC-159).
  Authority pointer 'pl...
ok    handoff worktree-only unresolvable pointer refused 
FAIL  handoff worktree-only brief-sc pointer refused exit 2: check-domain: BLOCKED — .claude/worktrees/harness/BUG-1480-wt/.harness/harness/features/BUG-1480-wt-fixture/notes/handoff-build.md: handoff shape (DEC-159).
  Authority pointer 'br...
```

Re-run at HEAD (post-fix, same as review_sha for this file — no commits between `d8a99991` and
`4de92e75` touch `check-domain.sh`) for contrast:
```
$ cd <worktree> && env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py
rc = 0, FAIL count = 0
ok    handoff worktree-only main root has no feature dir 
ok    handoff worktree-only feature dir resolves 
ok    handoff worktree-only unresolvable pointer refused 
ok    handoff worktree-only brief-sc pointer refused 
```

(b) is satisfied: the case group is genuinely red at the test commit and genuinely green after the
fix, with the total suite `FAIL` count matching the two rows named below, no other row disturbed.

### Third-difference check

`diff` of the scratch (test-commit) `check-domain.sh` against `git show 4de92e75:...check-domain.sh`:
```
1150a1151,1163
> def _checkout_root(path):
>     """Which checkout does this path stand in? Absorb failures to keep shape non-gating."""
>     ... (13 lines: the whole helper)
1748c1761,1762
<             problems.extend(handoff_done_when.problems(rel, content, root, resolve=True))
---
>             problems.extend(handoff_done_when.problems(
>                 rel, content, _checkout_root(absolute_path), resolve=True))
```
Exactly two hunks: the added `_checkout_root` helper and the one call-site argument swap. **No
third difference** — the fix commit changes nothing else in this file.

## (c) Per-row classification (from my own run, cross-checked against `plan.yaml` T-01 intent, read after measuring)

| Row | Pre-fix | Post-fix | Class |
|---|---|---|---|
| `main root has no feature dir` | ok | ok | **fixture precondition** — asserts the test's own setup (`os.path.exists(main_feat)` is False), never invokes the hook. Can never be red from a `check-domain.sh` change. |
| `feature dir resolves` | **FAIL** (exit 2, "handoff shape (DEC-159)") | ok (exit 0) | **red-then-green** — the discriminating row. |
| `unresolvable pointer refused` | ok (exit 2, contains `T-99`) | ok (exit 2, contains `T-99`) | **vacuity control** — green both ways by design (plan.yaml T-01 intent calls this "the one vacuity control" explicitly). The needle `T-99` is the raw pointer token echoed back regardless of which checkout resolution failed against, so it does not discriminate the fix. |
| `brief-sc pointer refused` | **FAIL** (exit 2, but message is the generic "handoff shape" — needles `SC-99` + path absent) | ok (exit 2, containing both `SC-99` and the worktree-relative BRIEF.md path) | **red-then-green** — a second, independent discriminating row: pre-fix the refusal message names no BRIEF.md at all (main root's copy doesn't exist); post-fix it correctly names the worktree's BRIEF.md and both needles land. |

**Count of rows that can actually report red: 2 of 4** (`feature dir resolves`, `brief-sc pointer
refused`). This matches `plan.yaml`'s stated intent exactly ("This row is a SECOND red-then-green
row" for the brief-sc case, "the one vacuity control" for the T-99 case) — my measurement was taken
and classified before I read that file's intent block a second time, and it corroborates rather than
merely repeats the plan's claim. The group is not vacuous: 2 of its 4 rows demonstrably discriminate
the fix; the other 2 are correctly labelled by design (a static fixture-truth assertion and one
negative vacuity control against a token that isn't checkout-sensitive).

## Adequacy question — REQ-02 direction, worktree-present case

**Gap found.** REQ-02 requires validation of a main-checkout handoff note to be unchanged. The
fixture that exercises every *pre-existing* handoff row (`_handoff_grammar_cases` through
`_handoff_line_cap_cases`, called at `run_handoff_done_when` before `_handoff_worktree_cases`) never
has a linked worktree present at all — `make_linked_worktree` is called for the first and only time
inside `_handoff_worktree_cases`, which is the LAST call in the `with tempfile.TemporaryDirectory()`
block (test-check-domain.py: `_handoff_worktree_cases` defined at line 4401, called at line 4465,
after every other handoff group). By the time a worktree exists in that tempdir, all of the
main-checkout-note assertions have already run and their subprocess invocations have already
completed.

Inside `_handoff_worktree_cases` itself, every `_invoke_handoff` call targets a note **inside** the
worktree (`target = os.path.join(notes, "handoff-build.md")` where `notes` is under `wt_path`) —
none targets a note in the main checkout while a worktree co-exists in the tree.

**So: no executable row anywhere in the suite exercises "a linked worktree exists in the tree, AND
the note being validated stands in the MAIN checkout, AND it must still resolve against the main
root."** `_checkout_root`'s `_hb.real(_ck[0]) != _hb.real(root)` comparison and its `return root`
fallback are only ever exercised in the "no worktree exists anywhere" case (pre-existing rows) and
the "note IS in the worktree" case (T-01's new rows) — never in the "worktree exists elsewhere, note
is in main" case that is REQ-02's actual claim.

**Concrete failure scenario:** if `_checkout_root`'s comparison were regressed to always trust
`_ck[0]` (e.g. dropping the `!=` check, or a future `harness_boundary.checkout_relative` change that
returns a spurious non-root checkout for a main-checkout path whenever ANY worktree is registered
elsewhere in the tree), a main-checkout handoff note would silently start resolving its
`plan-task`/`brief-sc` authorities against the wrong root whenever any worktree happens to exist —
and every row in this suite would stay green, because none of them create that combination.

**Rating: med.** The comparison logic itself is a single, simple boolean and unlikely to break
spontaneously today, so this is not an active defect — but it is a real, plausible coverage hole on
exactly the requirement (REQ-02) this bug's fix was supposed to leave untouched, and the gap is
invisible to the standing gate.

## must_fix

- [ ] (med) Add one row to `_handoff_worktree_cases` (or a sibling group) that keeps
  `make_linked_worktree` present in the tempdir and then invokes `_invoke_handoff` against a note
  living in the MAIN checkout's own feature dir (not the worktree's), asserting it still resolves
  against `root` and not the worktree — currently unexercised. (Reported per DEC-174: this is a
  finding for the orchestrator to route, not a change I am making — no source or test file was
  edited by me.)

No other must_fix items. SC-06 itself is satisfied on both its named legs.
