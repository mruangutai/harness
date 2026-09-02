# Scope review — FEAT-53 plan-panel, cycle 2

BLUF: the three cycle-2 amendments (D-03/Flask, D-21, T-21/T-22) are internally consistent with
each other and with D-16/D-18/D-19/T-06/T-10 — no orphan REQ, no dangling `traces:`, no cycle in
the 22-task `depends_on` graph. But the artifact T-21/T-22 gate on (the wired render) is never
required to precede the ONE task that builds and commits the shipped bundle, so the fix this cycle
exists to deliver can ship un-mounted in production while every declared verify stays green. Two
smaller, previously-unraised defects follow the same "declared protection ≠ actual protection"
shape. This is a genuine finding, not padding — I looked hard at the three flagged areas and they
hold up; what I found is adjacent to them.

## Findings

1. **[high]** `T-16` (commits the production `dist/` bundle, `plan.yaml:909-915`) depends only on
   `[T-12, T-15]` — never on `T-21`, which is the task that imports `charts.tsx` into `panels.tsx`
   (`plan.yaml:1066-1072`). Both `T-16` (dev-ops lane) and `T-21` (frontend-dev lane) become
   ready at the same point in the graph (once `T-15` lands) and run on different agents, so
   nothing stops — and the natural concurrent-lane scheduling actively invites — `T-16` building
   and committing `dist/` from the pre-`T-21` `panels.tsx`, i.e. panels with no chart imported.
   No task after `T-21`/`T-22` ever reruns `npm run build` and recommits `dist/`; `T-17`
   (docs, depends on `T-16` only) and `T-22`'s own script only run tests. Consequence: `T-21`'s
   and `T-22`'s render assertions can be green (they test source through `@testing-library/react`,
   never the built artifact) while the actual bytes a user gets from `python3 serve.py` — the one
   thing D-04 says ships with no build step — still render with no chart, reproducing
   PF-7408d83a's exact user-visible failure in the shipped product even though every declared gate
   passed. Fix shape: add `T-21` (or `T-22`) to `T-16`'s `depends_on`.

2. **[med]** The ~205-line stale trailing comment block (`plan.yaml:1204` onward, the already-
   raised `plan-merge.py apply` splice defect) contains a factual contradiction with the live YAML
   above it, which the assignment says is in scope even though the splice itself is not. At
   `plan.yaml:1338-1341` the comment states "T-21's verify, verbatim" as a `--reporter=verbose` +
   `grep -q 'label text'` form — exactly the weak "label present" pattern T-21's own live intent
   calls out and rejects two paragraphs earlier in the same file (`plan.yaml:1143-1147`: "a
   skipped case must not pass this gate… therefore drives `--reporter=json` and requires each
   label to be carried by an assertionResults entry whose status is exactly 'passed'… choosing a
   weaker gate is not yours"). The actual live `T-21.verify` (`plan.yaml:1078-1080`) is the
   `--reporter=json` + status-check form, not the grep form the comment claims is verbatim.
   Consequence: a future reader (distiller, auditor, or an implementer skimming the record instead
   of the task) who trusts the comment's "verbatim" claim believes the render gate accepts a
   skipped test — the precise defect class T-21 exists to close — and could "fix" the real verify
   to match the stale, weaker one they read in the record.

3. **[med]** `SC-17` declares `verify: automated  evidence: integration` as one block
   (`BRIEF.md:216-224`), but its own "the aggregate reports the not-tracked count by name" clause
   is asserted only in `test-metrics-kpi.py`, which `T-06` registers in `UNIT_SCRIPTS`
   (`plan.yaml:405`), and `T-11`'s own intent says so directly: "the aggregate mean, the count at
   zero and the count not tracked in `kpi.compute()`'s payload match the hand-labelled numbers…
   The wiring into kpi.py is a unit-level fact and belongs in the unit script"
   (`plan.yaml:695-699`). This is the same shape as the already-backlogged `PF-d2fc9563` (SC
   declares one evidence kind, its assertion lives under the other), just the opposite direction
   and on the newly added SC-17 rather than SC-07 — and unlike SC-07 it was never raised or
   dispositioned this cycle. Consequence: a coverage matrix that checks "is SC-17 satisfied by an
   `integration`-kind test" sees `test-metrics-trend.py` (integration) cover the two branch cases
   and reads SC-17 as fully covered, while the aggregate clause specifically has no
   integration-kind assertion at all — it could regress silently under any change that runs only
   the `integration` kind (e.g. CI's own two-step split in `.github/workflows/tests.yml:83-92`).

## Dismissed candidates (recorded, not re-raised)

- `T-20`'s `main-session-direct` claim over `.claude/commands/harness-plan.md`,
  `.claude/commands/harness.md` and `.claude/skills/harness-uat/SKILL.md` has no matching row in
  the feature's `lanes:` table, unlike `T-01`/`T-02`'s main-session-direct claims. Verified live
  with `check-domain.sh --resolve` against all three paths — each genuinely resolves to `NOBODY`,
  so the claim is factually correct today. The `lanes:` rows all cover *deliberately* ungranted,
  security-relevant surfaces (the routing file itself, the ignore files, the write-once ship
  path); T-20's paths are incidentally uncovered by `team-config.yaml`'s globs, a different
  category the table doesn't appear to promise exhaustive coverage of. Not reporting as a finding.
- The three flagged probe areas (D-03/Flask+T-12+CI, D-21 vs D-16/D-18/D-19/T-06/T-10/T-11,
  T-21/T-22's RED-ability and planned prerequisites in T-04/T-03/run-unit-tests.sh) were checked
  in force and hold up — confirmed independently against `run-unit-tests.sh:1-93` and
  `.github/workflows/tests.yml:54-92` (both cited facts in the plan's own record, e.g. "PyYAML and
  jsonschema" at :67-68, matched byte-for-byte). No new defect found in these three areas beyond
  finding 1 above, which sits one step downstream of them (the wiring gate itself is sound; what's
  missing is what depends on its output).

## REQ/SC coverage — both directions

All REQ-01..REQ-14 are traced by at least one task; all task `traces:` reference REQ ids that
exist (no orphans, no dangling references). All SC-01..SC-18 appear in the coverage table's SC→REQ
direction and all REQ-01..REQ-14 appear in the REQ→SC direction (`BRIEF.md:239-254`). The 22-node
`depends_on` graph (`T-01`..`T-22`, no gaps in numbering) is acyclic and every dependency id
resolves to a task that exists — independently re-derived, matching the goalcheck's own claim.

## Not re-raised (already ruled this cycle, per dispatch)

D-20 (client build stays), D-08 (alpha accepted, no second library), Shape B build-now
(overrules PF-6aa9faae), and the five backlogged med findings (PF-04c95fd6, PF-3713534d,
PF-55e28a6e, PF-d2fc9563, PF-ce8b018f as B-1..B-5).
