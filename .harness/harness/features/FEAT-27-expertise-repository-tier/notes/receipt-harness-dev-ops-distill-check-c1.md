# Receipt — harness-dev-ops — distill-check-c1 (FEAT-27)

## Job 1 — format gate, verbatim output

### `.claude/skills/harness/bin/check-expertise.sh .harness/expertise/`

```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
ADVISORY .harness/expertise/harness-backend-dev.md:75: G-08 names 'team-config' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:20: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names '.claude/' — repository-layer candidate; rule on it (issue 340)
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names 'check-domain.sh' — repository-layer candidate; rule on it (issue 340)
FAIL .harness/expertise/harness-pm.md
  - line 33: P-10 is 57 words — cap is 50; a rule, not a story
ADVISORY .harness/expertise/harness-pm.md:4: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:63: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```
Captured exit code: **1**

Advisory line count observed: **6** (backend-dev G-08 x1, dev-ops G-03 x1, orchestrator G-11 x2, pm P-01 x1, security-reviewer G-01 x1) — matches the six expected, does not affect exit code.

A genuine `FAIL` is present: `harness-pm.md` line 33, P-10 is 57 words against a 50-word cap. This is a real violation, not advisory. It belongs to `harness-pm`, not `harness-dev-ops` — flagged here as the discrepancy this run was spawned to surface, no fix applied (out of scope, not mine to touch).

### `.claude/skills/harness/bin/check-expertise.sh .harness/harness/expertise/`

```
OK   .harness/harness/expertise/harness-ai-dev.md
OK   .harness/harness/expertise/harness-backend-dev.md
OK   .harness/harness/expertise/harness-data-engineer.md
OK   .harness/harness/expertise/harness-dev-ops.md
OK   .harness/harness/expertise/harness-documentor.md
OK   .harness/harness/expertise/harness-eng-lead.md
OK   .harness/harness/expertise/harness-orchestrator.md
OK   .harness/harness/expertise/harness-pm.md
OK   .harness/harness/expertise/harness-security-reviewer.md
```
Captured exit code: **0**

## Job 2 — id-set diff, HEAD vs working tree

For all five named craft-tier files, HEAD (`git show HEAD:<path>`) already reflects the state
**after** the migration commit `532806c5428733db836647f2e2d482466a67a933`
("[harness:t-04] Eleven repository-specific entries move into the harness repository tier",
Wed Aug 19 07:30:56 2026 -0700) — that commit is each file's most recent commit per `git log -1`.
**No id present at HEAD is absent in the working tree, for any of the five files.** The working
tree only adds ids relative to HEAD (this session's own distillation `add` ops). There is no
silent drop in this session's diff.

### harness-backend-dev.md
- Last commit: `532806c5428733db836647f2e2d482466a67a933` (see above)
- HEAD ids: G-01, G-02, G-04–G-15, P-01–P-15 (no G-03)
- Working ids: same + G-16, O-01
- Dropped between HEAD and working: **none**
- Note: G-03 is absent at HEAD itself (not dropped this session) — see migration check below

### harness-dev-ops.md
- Last commit: `532806c5428733db836647f2e2d482466a67a933`
- HEAD ids: G-02–G-04, G-06–G-12, P-02–P-10 (no G-01, no G-05)
- Working ids: same + G-13, P-11–P-14
- Dropped between HEAD and working: **none**
- Note: G-01 and G-05 are absent at HEAD itself (not dropped this session) — see migration check below

### harness-data-engineer.md
- Last commit: `1efc7d9b6a182f572f9a3f6fd7995bc1396636f7` ("The three leads drop to effort medium, and DEC-11's capability list is corrected (#544) (#545)", Tue Aug 18 23:16:40 2026 -0700)
- HEAD ids: G-01–G-03, P-01–P-05
- Working ids: same + G-04, G-05, P-06
- Dropped between HEAD and working: **none**

### harness-ai-dev.md
- Last commit: `ada8e9998694e8a72c3827f0103b369ab0bb66e9` ("FEAT-23: the ship path closes atomically, /simplify ships as a skill, and Plan gets its kickoff move (#491)", Tue Aug 18 05:54:53 2026 -0700)
- HEAD ids: G-01, P-01, P-02
- Working ids: same + G-02, G-03, P-03
- Dropped between HEAD and working: **none**

### harness-eng-lead.md
- Last commit: `532806c5428733db836647f2e2d482466a67a933`
- HEAD ids: G-02–G-15, P-01–P-15 (29 ids)
- Working ids: identical set — no diff at all
- Dropped between HEAD and working: **none**

## Job 2 continued — migration proof for the pre-HEAD "drops"

The digest's premise ("15/106 lines at close, 14 now, no G-03" for backend-dev; "12 at close, 11 now,
G-01/G-05 absent" for dev-ops) is about the state **before** commit `532806c`, whose parent is
`c4d5bc58bd612ff48931bc59993b927988e984ab` ("[harness:t-01] Every agent is granted its
repository-tier Expertise path", Wed Aug 19 07:30:54 2026 -0700). Checked each dropped id's text at
that parent commit and grepped for it now:

- **backend-dev G-03** (parent text: "WHEN writing fixtures against the fake-gh test harness DO
  read its logging and issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py`
  first — assumptions about counters, log format, or which calls get logged fail loudly but still
  cost a debug cycle.") — grep `"fake-gh test harness"` across both expertise dirs finds it at
  **`.harness/harness/expertise/harness-backend-dev.md:6` as G-01**, verbatim. **Migrated, not
  lost.**

- **dev-ops G-01** (parent text: "Nothing invokes check-state.sh automatically — it is manual-only,
  so a green session is not evidence it ran. (This gotcha used to also cover check-docs.sh's
  exec-bit fail-open; that script and INV-10 were struck under DEC-188.)") — grep
  `"Nothing invokes check-state.sh automatically"` finds it only in
  **`.harness/harness/expertise/harness-dev-ops.md`**, verbatim, as its repository-tier G-01.
  **Migrated, not lost.**

- **dev-ops G-05** (parent text: "`.claude/skills/harness/templates/harness.json` is merged
  additively into `.harness/harness.json` by `.claude/skills/harness/bin/upgrade-config.py`, and
  copied verbatim on init — editing one without the other creates silent drift on the next upgrade
  or init.") — grep `"merged additively into"` finds it only in
  **`.harness/harness/expertise/harness-dev-ops.md`**, verbatim, as its repository-tier G-02.
  **Migrated, not lost.**

All three dropped entries are accounted for as migrations to the repository tier, at commit
`532806c`, with content matching byte-for-byte.

## Job 2 — repository tier id-set comparison (HEAD vs working)

`git status --porcelain` over both expertise directories (unfiltered):

```
 M .harness/expertise/harness-ai-dev.md
 M .harness/expertise/harness-backend-dev.md
 M .harness/expertise/harness-data-engineer.md
 M .harness/expertise/harness-dev-ops.md
 M .harness/expertise/harness-documentor.md
 M .harness/expertise/harness-eng-lead.md
 M .harness/expertise/harness-pm.md
 M .harness/expertise/harness-qa.md
 M .harness/expertise/harness-validator-lead.md
 M .harness/harness/expertise/harness-dev-ops.md
 M .harness/harness/expertise/harness-documentor.md
 M .harness/harness/expertise/harness-eng-lead.md
?? .harness/harness/expertise/harness-ai-dev.md
?? .harness/harness/expertise/harness-data-engineer.md
?? .harness/harness/expertise/harness-pm.md
?? .harness/harness/expertise/harness-qa.md
?? .harness/harness/expertise/harness-validator-lead.md
```

Per-file id sets, repository tier (tracked ones only compared to HEAD; untracked noted as new):

- **harness-backend-dev.md**: tracked. Last commit `532806c…`. HEAD ids: {G-01}. Working ids:
  {G-01}. No diff.
- **harness-dev-ops.md**: tracked. Last commit `532806c…`. HEAD ids: {G-01, G-02}. Working ids:
  {G-01, G-02, G-03, G-04, P-01}. Additions only (G-03, G-04, P-01 — this session's own
  distillation), no drops.
- **harness-data-engineer.md**: **untracked, new in working tree** (`git ls-files` reports no
  match). No HEAD state to compare against. Working ids: {G-01}.
- **harness-ai-dev.md**: **untracked, new in working tree**. No HEAD state. Working ids: {G-01}.
- **harness-eng-lead.md**: tracked. Last commit `532806c…`. HEAD ids: {G-01}. Working ids:
  {G-01, G-02}. Addition only, no drop.

## Verdict rationale

Both checker invocations ran as specified. Craft tier exits 1 for a real `FAIL` (`harness-pm.md`
P-10, 57 words > 50-word cap) — this is a genuine violation, not an artifact of this check, and it
belongs to a different agent's file. Repository tier exits 0 clean. Every id absent now versus HEAD
was traced to a same-commit migration with byte-identical content; no genuine loss found in any of
the five files audited, nor in the two other repository-tier files inspected.

Per the dispatch's own rule ("Your VERDICT is PASS only if both checker invocations exit 0 and every
dropped id is accounted for as a migration"), the craft-tier checker did **not** exit 0 — it exited 1
on a real `FAIL`. That FAIL is unrelated to the wipe question (Job 2 is clean) but the stated PASS
condition is not met literally. Reporting `FAIL` on that basis; the evidence has no unresolved data
loss.
