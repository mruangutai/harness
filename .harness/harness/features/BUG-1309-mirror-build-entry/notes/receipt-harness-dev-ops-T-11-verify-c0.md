# Receipt — harness-dev-ops — T-11 independent verify witness — BUG-1309-mirror-build-entry

## 1. verify: block byte-diff

Extracted verbatim from `.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml` (T-11, lines
1681-1687), the `verify: |` literal scalar body is:

```
out=$(python3 tests/unit/test-feature-schema-build-entry.py && python3 tests/unit/test-gh-sync-build-entry.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL '; then exit 1; fi
for n in 02 03 04 06 08 09 10 11 12 14 19 23 24 25 27 28 29 30; do
  printf '%s\n' "$out" | grep -qF "PASS BE-$n " || exit 1
done
echo VERIFY-PASS
```

Compared byte-for-byte against the string quoted in the dispatch: **IDENTICAL**. No diff.

## 2. Verify block run verbatim (cwd = worktree root)

Command run exactly as extracted, via `bash -c '...'` (this session's default shell is zsh; the
extracted body has no PIPESTATUS dependency but was still run under bash to match the plan's shell
assumptions):

Full stdout+stderr:
```
VERIFY-PASS
```

Exit status: `0`

## 3. Individual file runs

### `python3 tests/unit/test-feature-schema-build-entry.py`
- Exit status: `0`
- `PASS ` line count: `7`
- `FAIL ` line count: `0`
- BE ids in `PASS BE-NN ` lines, in order: `02, 03, 04, 06, 08, 09, 10`

Full output:
```
PASS BE-02 an era-set member with a trailing slash still returns recover-terminal
PASS BE-03 a non-era feature with no plan.yaml returns recover-terminal
PASS BE-04 a non-era feature whose plan.yaml does not parse returns recover-terminal
PASS BE-06 plan status done returns recover-terminal
PASS BE-08 building with three tasks none done is open, and only-last-done is recover-terminal
PASS BE-09 plan status building with an empty tasks list returns open
PASS BE-10 membership is exact, never a prefix and never case-insensitive
```

### `python3 tests/unit/test-gh-sync-build-entry.py`
- Exit status: `0`
- `PASS ` line count: `11`
- `FAIL ` line count: `0`
- BE ids in `PASS BE-NN ` lines, in order: `11, 12, 14, 19, 23, 24, 25, 27, 28, 29, 30`

Full output:
```
PASS BE-11 load_recorded normalizes an out-of-enum build_entry to None
PASS BE-12 save_recorded of a normalized record drops the build_entry key
PASS BE-14 record_build_entry upgrades a recorded recovery-required to opened
PASS BE-19 skip armed with feature.json absent records nothing and creates no file
PASS BE-23 an era-exempt feature with a trailing slash and recovery-required is not refused
PASS BE-24 a recorded opened continues with no SystemExit and nothing printed
PASS BE-25 a matching string --parent against the recorded parent is no conflict
PASS BE-27 conflict is None with no --parent given, and None with no parent recorded
PASS BE-28 milestone and parent recorded yields no creates and both adoption lines
PASS BE-29 neither milestone nor parent recorded yields the exact two-line creates list
PASS BE-30 milestone recorded plus --parent 9 given adopts by number, and no adoption state ever mentions a task or a sub-issue
```

### Union check

Union across both files, sorted: `02, 03, 04, 06, 08, 09, 10, 11, 12, 14, 19, 23, 24, 25, 27, 28, 29,
30` — 18 ids.

Expected set (from the verify's `for n in ...` loop): `02 03 04 06 08 09 10 11 12 14 19 23 24 25 27
28 29 30` — 18 ids.

**Result: EXACT MATCH.** No missing id. No extra `BE-NN` id printed outside the expected set (i.e. no
unplanned id would silently pass the gate).

## 4. `git status --porcelain` and `git diff --stat HEAD`

`git status --porcelain` (verbatim, unfiltered):
```
?? .harness/harness/features/BUG-1309-mirror-build-entry/notes/receipt-harness-backend-dev-T-11-c0.md
?? tests/unit/test-feature-schema-build-entry.py
?? tests/unit/test-gh-sync-build-entry.py
```

`git diff --stat HEAD` (verbatim):
```
(empty — no output)
```

All three untracked paths are exactly the T-11-owned deliverables named in the acceptance list (the
two new test files plus harness-backend-dev's own T-11 receipt). The
`runs/2026-09-07-01-eng/state.yaml` path named as allowed in the dispatch does not appear in
`git status --porcelain` output at all — either untouched, not yet created, or already tracked with no
diff; either way it contributes no unaccounted path.

**No path outside the allowed set appears.** In particular neither of the two known concurrent-work
paths (`tests/integration/test-hooks-install.py`, `tests/integration/test-post-merge-sweep.py`, owned
by the main session for T-10/T-13) appears in status or diff — no collision observed.

Confirmed via `git status --porcelain` alone (grep for the two production paths): **neither
`.claude/skills/harness/bin/gh-sync.py` nor `.claude/skills/harness/bin/feature_schema.py` appears** —
both are unmodified.

## Conclusion

- verify: block text matches dispatch exactly (byte-identical).
- Verbatim verify run: exit `0`, stdout `VERIFY-PASS`.
- Both test files individually: exit `0`, 0 FAIL lines each, PASS id union exactly the 18 planned BE
  ids, no extras.
- No production file modified; no scope violation; no path outside the allowed set.

Independent re-run **corroborates** harness-backend-dev's VERIFY-PASS claim in full.
