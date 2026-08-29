# Receipt — harness-dev-ops — T-13 — 2026-08-29-07-eng

## Task
Sweep two stale DEC citations from `.github/workflows/tests.yml`: line 62's `DEC-171 am.1` and
line 124's `DEC-192`. Comments only, no job/step/condition/command changes.

## Re-derivation (grep, not trusted line numbers)

```
grep -nE 'am\.[0-9]|DEC-[0-9]+ amendment' .github/workflows/tests.yml
  62:      # PyYAML is REQUIRED, not optional (DEC-171 am.1). There is no line-scan fallback:

for n in 19 20 37 67 82 88 92 102 103 104 137 140 186 192 196; grep -nE "DEC-$n([^0-9]|$)"
  124:      # plan.yaml `status:` enum under DEC-192. It never opens this file. A reader following that
```

Both sites matched exactly the two the intent hypothesized; the full verify-list grep found no
additional stale citations. Lines 65 (`DEC-189`), 103/202 (`DEC-183`) are current and untouched.

## DEC-203 holding check

Read `.harness/harness/docs/DECISIONS.md` (read-only) at DEC-203 (line 7177+). Section 6:

> "**6. The status field, carried forward from DEC-192 unchanged in substance.** There is one
> lifecycle field, `status`. Its six values are the board's own column names: `Backlog`, `Plan`,
> `Ready`, `Building`, `Review`, `Done`."

DEC-203 explicitly carries forward DEC-192's status-enum content ("unchanged in substance") and its
opening line names DEC-192 as one of the three entries it replaces. **Branch taken: DEC-203 does
carry the status enum → cite DEC-203 plainly**, per the intent's positive branch. (The negative
branch — state the enum inline, cite nothing — was not needed.)

## Change made (comments only)

```diff
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -59,7 +59,7 @@ jobs:
       # is no longer pinned, so a runner-image bump changes the interpreter under the suite
       # without any diff here. Accepted as too little value for its weight.
       #
-      # PyYAML is REQUIRED, not optional (DEC-171 am.1). There is no line-scan fallback:
+      # PyYAML is REQUIRED, not optional (DEC-171). There is no line-scan fallback:
       # a missing parser is a loud failure by design, so install it rather than letting
       # the suite exercise a degraded path that does not exist. jsonschema is REQUIRED
       # too (DEC-189): FEAT-14's feature.json schema checker fails loudly, never silently,
@@ -121,7 +121,7 @@ jobs:
       # citation that used to sit here was the worse kind of wrong: it named
       # `test-check-plan-routes.py` case 25 as reading this file and asserting the step is present
       # and unneutered. Measured 2026-08-21 — case_25 exists at :1030 and PASSES, and it asserts a
-      # plan.yaml `status:` enum under DEC-192. It never opens this file. A reader following that
+      # plan.yaml `status:` enum under DEC-203. It never opens this file. A reader following that
       # citation found a green test and stopped looking, which is worse than finding nothing.
       # No test under bin/ asserts anything about this workflow's content.
       #
```

Only two comment lines changed. No job, step, condition, or command touched (`git -C <worktree>
diff -- .github/workflows/tests.yml` above is the full diff, verbatim).

## Verify — verbatim command and output

Confirmed the quoted verify string byte-matches `plan.yaml`'s T-13 `verify:` block before running
(lines ~1026-1032 of plan.yaml).

```
$ cd "$(git rev-parse --show-toplevel)"   # resolved to the worktree root
$ W=.github/workflows/tests.yml
$ grep -nE 'am\.[0-9]|DEC-[0-9]+ amendment' "$W" && exit 1
(no output — pattern absent)
$ for n in 19 20 37 67 82 88 92 102 103 104 137 140 186 192 196; do
    grep -nE "DEC-$n([^0-9]|$)" "$W" && { echo "cites DEC-$n"; exit 1; }
  done
(no output for any n)
$ python3 -c "import yaml,sys; yaml.safe_load(open('$W')); print('yaml ok')"
yaml ok
$ echo $?
0
```

Exit status: **0**. YAML parses cleanly.

## KNOWN ENVIRONMENT DEFECT encountered and worked around

The first `edit` call to `.github/workflows/tests.yml` reported success and rendered a plausible
diff, but landed in the MAIN checkout (`/Users/molchairuangutai/GitHub/harness/.github/workflows/tests.yml`)
instead of the worktree — confirmed by `git -C <worktree> status --porcelain` showing nothing and
`git -C <main> status --porcelain` showing the file modified. Recovery:

1. Restored main's file to HEAD content via `git -C <main> show HEAD:.github/workflows/tests.yml`
   piped to a temp file, then a plain `shutil.copyfile` (no git write command — `git show` is
   read-only) — confirmed `git -C <main> status --porcelain` clean of the file afterward.
2. Re-applied the two-line edit directly against the absolute worktree path via `python3` file
   read/write, then re-verified with `git -C <worktree> diff` (shown above) and `git -C <worktree>
   status --porcelain` (`M .github/workflows/tests.yml` only).

## Final state confirmation

- `git -C <worktree> status --porcelain -- .github/workflows/tests.yml` → `M .github/workflows/tests.yml`
- `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` → no entry for
  `.github/workflows/tests.yml` or any other file this task touched (untracked entries listed are
  pre-existing, unrelated to this dispatch).
- HEAD not moved in either checkout. No commit made.
