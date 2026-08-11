# Operator answer — FEAT-12 — the kaya STOP condition — 2026-08-10

## The ruling

**Reading B. The STOP condition means entries under `.claude/skills/harness*` or
`.claude/commands/harness*` that are NOT already accounted for.** The 34 signed modifications do not
trip it. Segment A proceeds.

The tripwire existed to catch harness files in kaya that nobody knew about. There are none.

## Why the operator could rule it — every entry was identified first

Measured in `/Users/molchairuangutai/GitHub/kaya-ai` on 2026-08-10, before the ruling:

| | Count |
|---|---|
| Tracked, modified (`M`) | **34** |
| Tracked, deleted (`D`) | 2 — `bin/cost-report.py`, `teams/gate-probe.yaml` |
| Untracked (`??`) | 21 |
| **Total under those paths** | **57** |

That resolves the arithmetic the work order flagged: `BRIEF.md`'s "34" counts modifications only;
adding the two deletions gives the 36 tracked entries `git status` reports.

**All 57 are `deploy.sh` artifacts. None was authored in kaya.** Contents: `harness.md`, thirteen
`harness-*/SKILL.md` files, fourteen `bin/` scripts (including `check-domain.sh`, `check-state.sh`,
`bash-write-guard.sh`, `validate-digest.py`), templates and team files. Kaya's own product code is
not involved.

**Why the working tree shows them modified:** kaya last COMMITTED under those paths on **2026-08-02**
(`1ad0f1d`). The uncommitted changes are a LATER `deploy.sh` run that copied this repo's newer files
over kaya's older tracked copies and was never committed. Spot-checked
`harness-handoff/SKILL.md`: kaya's working-tree version carries the DEC-172 fenced-yaml shape, which
is this repo's current text.

So the discard is safe for a stronger reason than "reproducible from harness": **the working-tree
diff IS a half-applied harness deploy.** Committing the deletion removes a stale copy of this
repository from a product repository, which is what FEAT-12 exists to do.

## What still binds, unchanged

- Staging is by **explicit pathspec**. Never `git commit -a`, never `git add .`, never `git add -A`.
- `git rm -f` is authorized for the tracked modified files, and only because every one is
  reproducible here.
- Keep kaya's `.harness/expertise/`, `codebase/`, `features/`, `artifacts/`, `notes/`,
  `harness.json`, `team-config.yaml`, `.claude/agents/` (the directory), and
  `.claude/commands/review-team.md`.
- The push covers `mruangutai/kaya-ai` `master`, the deletion commit ONLY. **Nothing in this
  repository may be pushed on that authorization.**
- D-06 is REVERSED: remove `.claude/settings.json.harness-bak`. One path on T-03, one entry on
  T-05's pathspec. Not a new task.
