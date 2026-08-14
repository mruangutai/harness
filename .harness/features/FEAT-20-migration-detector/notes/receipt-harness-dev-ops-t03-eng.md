# Receipt — harness-dev-ops — T-03

**BLUF: T-03 done.** Added a step named exactly `Layout gate` to the `integration` job in
`.github/workflows/tests.yml`, immediately after `Plan-route gate`, same job (no `name:` key
added, DEC-183's required `integration` context is unchanged). Only file touched:
`.github/workflows/tests.yml`.

## What the step does
- Runs `python3 .claude/skills/harness/bin/layout_migration.py .`, captures stdout+stderr and
  `rc` without killing the step at the assignment, prints output unconditionally.
- Greps for `^layout: N surface(s) clean, ...$` with `|| true` (bash -e safety) — absent ⇒
  `::error::` "CHECKER COULD NOT RUN", exit 1.
- Greps for `^examined N feature dir(s), M doc root(s), R reader file(s)$` — absent ⇒ a second,
  differently-worded `::error::` "cannot tell broken discovery from a clean tree", exit 1.
- Parses all three counts (feature dirs / doc roots / reader files). If ANY is zero, a third
  `::error::` names WHICH one read zero ("Discovery did not run..."), exit 1. All three are
  hedged per plan.yaml's explicit correction (doc root gets equal defence to features, D-01).
- Otherwise echoes a one-line summary and `exit "$rc"` — the detector's own exit code, so both
  MIXED (1) and CANNOT_VERIFY (2) fail the step.
- Comment above the greps states the regex is coupled to `layout_migration.py`'s `render()`
  format strings (which carry a reciprocal comment) and that a reword must change both.
- Single comment about protection: "Nothing in the repository asserts this step is present or
  unneutered." No equivalent to the false claim above `Plan-route gate` (issue #279, left
  standing, unedited — confirmed lines 110-114 unchanged, see below).

## Verify — VERBATIM, run from repo root

Invocation form: bare `python3 -c "..."`, no redirect (single command, copy-pasted from
plan.yaml line 574, cross-checked character-for-character — identical).

```
$ python3 -c "import yaml; d=yaml.safe_load(open('.github/workflows/tests.yml')); J=[j for j in d['jobs'].values() if any(x.get('name')=='Plan-route gate' for x in j.get('steps',[]))]; assert len(J)==1, 'Plan-route gate job not found exactly once'; s=[x for x in J[0]['steps'] if x.get('name')=='Layout gate']; assert len(s)==1, 'Layout gate is not a step of the job holding Plan-route gate'; assert sum(1 for j in d['jobs'].values() for x in j.get('steps',[]) if x.get('name')=='Layout gate')==1, 'Layout gate appears in more than one job'; r=s[0]['run']; assert 'layout_migration' in r; assert 'examined' in r; assert '|| true' in r; assert r.count('::error::')>=3, 'fewer than three distinct error messages'; print('ok')"
ok
```

OBSERVED exit code: **0**.

## Additional checks the verify cannot see (done manually)
- Step order: `python3 -c "..."` listing job step names confirms `Layout gate` is immediately
  after `Plan-route gate` in `jobs.integration.steps` (index 6 of 7, previous is index 5).
- Ran the detector CLI directly against repo root:
  `python3 .claude/skills/harness/bin/layout_migration.py .` →
  `features: CLEAN`, `docs: CLEAN`, `examined 20 feature dir(s), 1 doc root(s), 7 reader
  file(s)`, `layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify`, exit 0.
- Extracted the step's `run:` block into a standalone script and ran it with `bash -e` against
  that live output — parsed all three counts correctly and exited 0 (detector's own code).
- `sed -n '110,114p' .github/workflows/tests.yml` — the pre-existing false comment about
  `test-check-plan-routes.py` case 25 protecting `Plan-route gate` is unedited (out of scope,
  GitHub issue #279).
- `CLAUDE_PROJECT_DIR: ${{ github.workspace }}` set identically to neighbouring steps.
- No new job, no `name:` key on the job, no branch-protection change.

## Scope / commit
`git status --porcelain` shows `M .github/workflows/tests.yml` as my only change. (Other
pre-existing dirty entries in the tree — `STATE.md`, `plan.yaml`, deleted member notes,
untracked logs — predate this dispatch and are not mine.) Working tree left dirty; no commit
made (DEC-153, commit pen is the orchestrator's).

## Open questions
None blocking. Note for the record: issue #279 (false CI-assertion comment) remains open and
untouched, as instructed.
