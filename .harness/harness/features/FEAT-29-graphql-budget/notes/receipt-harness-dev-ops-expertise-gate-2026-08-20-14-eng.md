# Receipt — harness-dev-ops — expertise gate + silent-drop audit — 2026-08-20-14-eng

## Part 1 — gate

Command run verbatim:
```
.claude/skills/harness/bin/check-expertise.sh .harness/expertise/
```

Exact output:
```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
ADVISORY .harness/expertise/harness-backend-dev.md:78: G-08 names 'team-config' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:22: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names '.claude/' — repository-layer candidate; rule on it (issue 340)
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names 'check-domain.sh' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-pm.md
ADVISORY .harness/expertise/harness-pm.md:4: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:66: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```
Exit code: `0`

Every file reports `OK`. No file reports FAIL. Advisories only (repository-layer-candidate hints,
not failures). Since there is no failure at all, the DEC-race re-run rule (re-run once on a
non-{backend-dev, data-engineer, dev-ops} failure) does not apply — nothing to re-run.

Per-file: all 16 files `OK`, zero `FAIL` lines, zero errors.

## Part 2 — silent-drop audit

Method: for each of the 6 paths, `git show HEAD:<path>` vs current working-tree content, extracted
the `^- (P|G|O)-NN:` ID set for each section, diffed the sets, then inspected `git diff -- <path>`
for any removed line whose text is not recognisably preserved under the same or a related ID.

All 6 paths are **tracked at HEAD** (none untracked/new).

### `.harness/expertise/harness-backend-dev.md` (craft)
- HEAD IDs: G-{01,02,04-16} (no G-03), O-01, P-{01-15} — 30 entries
- Worktree IDs: same set **plus** O-02, O-03 — 32 entries
- Dropped: **none**. Added: O-02, O-03.
- `git diff` shows 8 same-ID rewrites at capped Patterns/Gotchas sections (P-01, P-10, P-11, G-01,
  G-07, G-12, G-15, G-16): text replaced but ID preserved. G-01, G-07, G-12, G-15, G-16 are
  on-topic generalizations of the prior entry (broadened trigger, same underlying lesson,
  recognizable continuity). P-10 and P-11 are genuinely new/unrelated topics (mutation-scoping,
  coverage-hole-by-mutation) under a reused ID slot — consistent with backend-dev's disclosed
  "replaced entries at capped sections with unrelated new rules." **This is disclosed
  displacement, not a silent drop**: the ID survives, nothing vanished without an op naming it.

### `.harness/harness/expertise/harness-backend-dev.md` (repository tier)
- HEAD IDs: G-01 — 1 entry. Worktree IDs: G-01, G-02 — 2 entries.
- Dropped: **none**. Added: G-02. Pure append.

### `.harness/expertise/harness-data-engineer.md` (craft)
- HEAD IDs: G-{01-05}, P-{01-06} — 11 entries.
- Worktree IDs: HEAD set **plus** G-06, P-{07,08,09} — 15 entries.
- Dropped: **none**. `git diff` for this file showed zero removed content lines. Pure append.

### `.harness/harness/expertise/harness-data-engineer.md` (repository tier)
- HEAD IDs: G-01. Worktree IDs: G-01. Identical — no change this run.

### `.harness/expertise/harness-dev-ops.md` (craft — my own file)
- HEAD IDs: G-{02,03,04,06-13}, P-{02-14} — 24 entries.
- Worktree IDs: HEAD set **plus** G-14, G-15, P-15, P-16 — 28 entries.
- Dropped: **none**. Zero removed content lines in `git diff`. Pure append (my earlier
  distillation this run).

### `.harness/harness/expertise/harness-dev-ops.md` (repository tier — my own file)
- HEAD IDs: G-{01-04}, P-01 — 5 entries.
- Worktree IDs: HEAD set **plus** G-05 — 6 entries.
- Dropped: **none**. Pure append.

### The G-03 question — direct answer

**No, G-03 was not dropped during this run.** `.harness/expertise/harness-backend-dev.md` (craft
tier) has **no G-03 at HEAD either** — the committed prior version already runs
G-01, G-02, G-04 … G-16. This is a **pre-existing ID gap**, unrelated to this run's writes. Nothing
in this run's diff touches a G-03 line for that file (confirmed: the diff's removed-Gotchas lines
are G-01, G-07, G-12, G-15, G-16 only — never G-03).

## Summary

No silent drops found in any of the 6 files. All ID-set deltas are HEAD-subset-of-worktree
(append-only or same-ID-rewrite). The 8 same-ID rewrites in the craft backend-dev file match the
disclosed capped-section displacement; 5 of those 8 are recognizable generalizations of the prior
text, 2 (P-10, P-11) are disclosed unrelated replacements, not a silent loss.

## Part 3 — follow-up: the P-07 discrepancy

Command run: `git show HEAD:.harness/expertise/harness-backend-dev.md` (craft tier), P-07 entry
extracted.

**Verbatim P-07 text at HEAD:**
```
- P-07: WHEN adding or fixing an assertion to close a vacuous-pass gap DO prove it with a mutant,
  predicting by name which checks redden before the run — and treat "a different check reddened
  instead" as a FAIL of the fix, not a pass.
```

**Verbatim P-07 text in the current working tree:**
```
- P-07: WHEN adding or fixing an assertion to close a vacuous-pass gap DO prove it with a mutant,
  predicting by name which checks redden before the run — an unpredicted redness is a FAIL unless
  it is a pre-existing check already coupled to the same path, which you verify, never assume.
```

**Did P-07's text change between HEAD and the working tree? YES.** The clause after the em-dash was
rewritten: HEAD's "and treat 'a different check reddened instead' as a FAIL of the fix, not a pass"
became worktree's "an unpredicted redness is a FAIL unless it is a pre-existing check already
coupled to the same path, which you verify, never assume." The ID (P-07) is preserved but the body
is a genuine same-ID rewrite, not a copy.

**Conclusion: my Part 2 audit's 8-item same-ID-rewrite list was incomplete — it omitted P-07.**
backend-dev's reported nine ops (the 8 I found plus `op: replace, target: P-07`) was accurate; the
count is settled at **9 same-ID rewrites**, not 8. This is a record-accuracy correction to my own
Part 2 audit, not a finding against backend-dev — backend-dev's `expertise_update` did not overstate
what it applied; my prior count understated what happened.
