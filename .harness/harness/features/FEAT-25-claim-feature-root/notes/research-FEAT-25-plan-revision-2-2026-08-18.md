# FEAT-25 · plan revision 2 — baselines re-pinned at d1ffd7f, SC-08 de-vacuified

**Both findings landed.** Gate passed: `git rev-parse --short HEAD` = **d1ffd7f** (FEAT-24 merged,
`#538`); counts re-derived at HEAD are **114 / 106 / 40**, matching the dispatch exactly. Tasks 3,
decisions 4, `status: pending` untouched in both artifacts, SC set still SC-01…SC-08.

## F-A — the four count clauses, re-pinned and re-tested

| Clause | Baseline @d1ffd7f | Planned additions | Threshold | baseline−1 fails? |
|---|---|---|---|---|
| T-01 `test-factory-claim.py` | 114 | 2 (pinning equality + existence) | `-ge 116` | yes: 113 < 116 |
| T-01 `test-factory-integration.py` | 106 | 0 (fixture paths move, nothing added) | `-ge 106` | yes: 105 < 106 |
| T-02 `test-factory-claim.py` | 116 (post-T-01) | 4 B5-ter (sc13b is a rename, adds 0) | `-ge 120` | yes: 115 < 120 |
| T-03 `test-layout-migration.py` | 40 | 1 (case 22) | `-ge 41` | yes: 39 < 41 |

threshold == baseline + planned additions holds for all four. No clause derives its baseline at
runtime; every one is a literal against a named sha. No assertion dropped, merged or weakened.

**T-01's integration clause is deliberately non-firing at HEAD and that is correct.** It is a pure
deletion guard with zero planned additions: 106 ≥ 106 passes today, 105 fires. Its digit was not
touched; only `ada8e99` → `d1ffd7f` in its message. T-01 as a whole still exits 1.

Also changed: `lanes.resolved_at` `ada8e99` → `d1ffd7f`. Re-confirmed at d1ffd7f — `team-config.yaml`
is not in `git diff --name-only ada8e99 d1ffd7f`, and `harness-backend-dev` holds
`.claude/skills/harness/bin/** upsert` (`team-config.yaml:161`), so all six lane rows still resolve
to `harness-backend-dev`. `check-plan-routes.py` agrees: three OK lines, no deviation.

BRIEF SC-07 now carries the three **baselines** 114 / 106 / 40 at `d1ffd7f`, explicitly not the
thresholds — SC-07 grades "no case was deleted"; that the new cases exist is SC-01…SC-06's job and
the `need`/`hasok` clauses'.

T-01 gained one intent paragraph (not a verify line) pinning all three counts at d1ffd7f and telling
a doer who finds `main` has moved to re-derive and report rather than widen. `intent:` is excluded
from `BUDGETED_FIELDS` (`check-plan-routes.py:286-288`), so it cost zero machine lines.

**`ada8e99` deliberately left standing in three places**: D-01:41 and D-02:68 (decisions not
reopened, byte-identical) and T-03's pattern audit at :442. `factory_claim.py` is not in the
ada8e99→d1ffd7f diff, so that audit's anchor is still a true observation.

## F-B — SC-08 now grades what changed, not what was declared

Old first clause was true by construction: all eight declared paths already sit under
`.claude/skills/harness/bin/`. New basis: `git diff --name-only d1ffd7f...<branch head>` — three-dot,
tracked files only, so untracked `FEAT-26-*/` and `FEAT-27-*/` are outside the comparison and cannot
fail it — **minus** paths under `.harness/harness/features/FEAT-25-claim-feature-root/`, which is
R-6's one warranted exclusion.

Clause (a) is **wider than the dispatch asked**, and deliberately: every remaining path must be one
of the **eight declared** `files:` entries. Clause (b) enumerates the six forbidden members one at a
time with six separate verdicts (P-04), citing the single `## Constraints` enumeration; no second
spelling created. `verify: inspection` unchanged.

**Concrete falsifying changes** — either makes SC-08 FAIL:

1. `.claude/skills/harness/bin/factory_land.py` — inside `bin/`, not forbidden, never declared. This
   is the one the old wording and the dispatch's narrower scope both miss, and it is the literal
   shape of "a doer modified a file the plan never declared".
2. `.claude/skills/harness-spec-driven/SKILL.md` — outside `.claude/skills/harness/`, satisfying the
   dispatch's discriminating check (b).

## Observed, not asserted

- `python3 .claude/skills/harness/bin/check-plan-routes.py` → **EXIT=0** (repo-wide and on this plan
  alone); T-02 still within the 50-line cap. Its count clause stayed one physical line — no
  `d1ffd7f` string added to T-02's message, digits only.
- All three `verify:` blocks extracted with `yaml.safe_load` from the edited plan and run at
  d1ffd7f with `CLAUDE_PROJECT_DIR` set: **all EXIT=1**.
  - T-01: `FEATURES_ROOT` equality assert (`.harness/features` vs `.harness/harness/features`),
    migrated-join grep, legacy-join grep, both pinning-case `hasok`s, claim count 114 < 116, legacy
    path in `test-factory-integration.py`. Integration count 106 did **not** fire — correct.
  - T-02: all five `need` names absent, count 114 < 120, python heredoc
    `AssertionError: ('edge_i', 'T-01')`.
  - T-03: `READER_TABLE` row list empty (`AssertionError: []`), case-22 `hasok`, layout count 40 < 41.
- `decisions:` block byte-identical: `sed -n '/^decisions:/,/^tasks:/p'` piped to `shasum -a 256`
  before and after the edits — both `f86ce7a3b035f4c8a0ce06f618c283b2a21dc7e2ed1c9a4af12adb3961d9d43f`,
  72 lines / 4993 bytes. (Backing up a copy to scratchpad was blocked by `bash-write-guard`, so the
  hash was taken in place first.)
- Tasks 3, decisions 4, `approval: status: pending` in both artifacts, SC-01…SC-08 exactly, no SC
  weakened, no count clause added for `test-check-state.py` (T-03 still runs it pass/fail only).
- BRIEF's `## Verification gaps` re-checked at HEAD, still true: `unit` and `integration` both
  `status: active` with non-null `cmd` in `.harness/harness.json`, both `detect` globs matching
  `.claude/skills/harness/bin/test-*.py`.

## Open

- **Fixed, not left open:** BRIEF `## Constraints` last bullet said FEAT-24's plan and this one are
  "both pending; the merges need sequencing". False at d1ffd7f — FEAT-24 is merged, and that merge is
  exactly why the claim baseline moved 113 → 114. Rewritten to record the merge, the sha, and the
  re-derive instruction if `main` moves again. This finishes F-A rather than expanding it: the
  falsified sentence is the cause of the stale baseline.
- **SC-08 exposure — this needs the user before signature, not the grader afterwards.** FEAT-24's
  branch also modified
  `.harness/expertise/harness-*.md` and `.harness/harness/docs/DECISIONS*.md` — outside the feature
  dir and outside the eight declared paths. If FEAT-25's branch carries the same distillation and
  ship-doc passes, a literal grading of clause (a) reads not_met. I did **not** add exclusions for
  them: that is the narrowing F-B exists to prevent, and I cannot yet know whether this feature's run
  shape includes those passes. Raised as a BLOCKING open question — an unsatisfiable criterion is
  F-A's mirror image, and P-06 forbids the grader adopting a narrower reading later.

Clause (b) is bound to clause (a)'s set — the same post-exclusion remainder — so this feature's own
notes naming `load_board` or a forbidden file in prose cannot fail it. All five forbidden files live
outside the feature directory, so nothing detectable is lost.
- Carried forward, still true: two feature directories share the id `FEAT-25`.

---

## Cycle 3 — two prose send-backs; one was already closed

**S2 (fixed).** SC-08 clause (a) said "one of the eight paths declared in the `files:` lists of T-01,
T-02 and T-03". There are 8 `files:` **entries** but only **6 distinct paths** — T-02's two entries
(`factory_claim.py`, `test-factory-claim.py`) both duplicate T-01's (`plan.yaml:111-114`, `229-231`,
`383-386`). Clause (a) now reads "every remaining path appears in the **union** of the `files:` lists
of T-01, T-02 and T-03". The set is named rather than counted, so no second number sits beside clause
(b)'s "six", which counts a different set (five files plus `load_board`). Nothing else in SC-08
moved: three-dot basis, R-6 exclusion, clause structure, `verify: inspection` and clause (b) are
byte-identical to cycle 2.

**This correction supersedes two lines of this note.** Line 48-49 above ("every remaining path must be
one of the **eight declared** `files:` entries") and line 94 ("outside the eight declared paths") are
both wrong in the same way. Read both as **the union of the three `files:` lists — six distinct
members**. The grader reads clause (a) in BRIEF, not those lines.

**S1 (no change needed — it landed in cycle 2).** The dispatch quoted `BRIEF.md:114-116` as ending
"Both plans are pending; the merges need sequencing." That sentence is not in the file. The last
`## Constraints` bullet, now `BRIEF.md:117-122`, already reads "Merge collision, now resolved: …
FEAT-24 **merged at `d1ffd7f`**, so no sequencing is left to do — and its added case is why the
claim-suite baseline is 114 rather than the 113 counted at `ada8e99`", and it keeps the history
rather than deleting it (PRINCIPLES rule 15). It was rewritten in cycle 2 and recorded above under
"Fixed, not left open"; the dispatch read that entry as an unexercised Open. Re-editing correct prose
to satisfy a stale quotation would be churn, so the bullet was left byte-identical.

**Still open, still unfixed, still BLOCKING — deliberately.** FEAT-24's branch also modified
`.harness/expertise/harness-*.md` and `.harness/harness/docs/DECISIONS*.md`. If FEAT-25's branch
carries a distillation or ship-doc pass, those paths fall outside clause (a)'s union and it reads
`not_met`. **No exclusion was added** — inventing one is the narrowing F-B exists to prevent. The
dispatcher is carrying it to the operator at approval, unchanged.

**Observed this cycle, not asserted.**
- `plan.yaml` untouched: `shasum -a 256` = `51aafa50d3bacc2ebe25f347fd0854dcca7f71c58adbd75fc9f193c6433d979c`
  taken before the BRIEF edit and again after — identical.
- `python3 .claude/skills/harness/bin/check-plan-routes.py` → EXIT 0.
- `grep -n eight plan.yaml` → five hits, all the skip-reason count (seven → eight). None concerns
  paths, so the two artifacts do not contradict each other and nothing was raised on it.
- SC-07's authorised "seven reasons to eight" rename count untouched; SC set exactly SC-01…SC-08;
  tasks 3, decisions 4; `approval: status: pending` in both artifacts.
