# Panel transcription — FEAT-52-handoff-done-when, plan-panel c0

**BLUF: the c0 panel is recorded in plan.yaml's `panel:` key — `last_run: 2026-09-02-4-validator`,
`cycle: 0`, both readers `ran`, all five findings `open` at the readers' own severities. Nothing else
in the file moved: reverting the panel block byte-for-byte reproduces the pre-write file hash.
Transcription only — no finding answered, no task, decision, requirement or criterion touched,
`approval.status` still `pending`, top-level `status:` still `plan`.**

## The five findings, for the operator briefing

| rank | id | severity | reader | subject |
|---|---|---|---|---|
| 1 | `PF-4205e7e2f84e2eb24d421c924f4d7ac3` | med | should-not-exist | INV-17 re-resolves pointers in every post-contract note forever |
| 2 | `PF-570b9c87adac19d62513b5e90cce0f81` | low | should-not-exist | T-06(g) bakes the real-corpus scan + no-mutation audit into the permanent suite |
| 3 | `PF-918326616878584f5958be94fba0ede7` | low | scope | T-09's `test_kinds.handoff_comprehension` omits `exclude` |
| 4 | `PF-d0ea19ffc351a13d6b569f0169222109` | low | should-not-exist | SC-14 + T-03(h)/T-06(h) make an out-of-scope exclusion permanent machinery |
| 5 | `PF-1e45eb3a962725a1b45e3e0e90a271c6` | info | should-not-exist | striking D-04 costs four artifacts, not one task |

Severities are the readers' own, transcribed from `runs/2026-09-02-4-validator/digest.md:15-19`
unchanged; no `unrated` came back from either reader, and none was converted. All five are
`disposition: open` — no task addresses any of them and none may before signature (DEC-207, DEC-176:
findings enter the ONE batched review at the signature gate).

**Q1 (INV-17's permanent pointer re-resolution) and Q2 (the D-04 / T-09 / T-12 / SC-09 coupling if
D-04 is struck) are untouched.** They are the operator's calls at signature; neither is answered,
encoded as a decision, or given a task here.

## Finding identity — what was hashed and how

Ids are computed, never typed, via the single source of finding identity:

```
python3 .claude/skills/harness/bin/panel_findings.py id --reader <reader> --summary <summary>
```

which is `PF-` + the first 32 hex characters of `sha256(reader + "\n" + normalized_summary)`, where
normalization is lowercase + whitespace-run collapse + strip (`panel_findings.py:23-33`).
**The string hashed is the `summary:` value exactly as it now stands in plan.yaml** — verified by
re-deriving each id from the landed file after the write: all five reproduce (`canonical_reproduces=True`).

**Deviation from the dispatch, recorded rather than hidden.** The dispatch specified `PF-` + the
first **8** hex of `sha256(summary)` — the shape shown in `templates/plan.yaml:75` (`PF-0123abcd`) —
which is *not* what the harness's own tool computes: it is unscoped by reader, unnormalized, and
8 chars rather than 32. `harness-spec-driven` says "Compute every id with `panel_findings.py id`;
never type it", and `test-panel-findings.py:4` states panel_findings.py is *the ONE place* a panel
finding's identity is computed, asserting the 35-char form. Writing the ad-hoc form would produce
ids that no re-derivation through the canonical tool reproduces — the exact "reads as a stale
override" failure the id exists to prevent once the operator's `approval.rulings` cite them. So the
canonical ids are written. For completeness, the dispatch-formula values over the same strings are
`PF-473a8654` (rank 1), `PF-dd62d13e` (2), `PF-741311a5` (3), `PF-670df74d` (4), `PF-79781ad5` (5) —
either derivation names the same five findings.

## Summaries — what condensing did and did not do

Each summary is the digest's own wording, one line, with markdown stripped (backticks removed around
`exclude`, `omp_session_accessor`, `test_kinds`, `code_grade.py:468-471`) and two typographic
substitutions: rank 4's `T-03(h)/T-06(h)` written as "T-03(h) and T-06(h)", rank 5's em dashes as
hyphens. No mechanism and no consequence was dropped from any of the five; nothing was softened.
Rank 3's mechanism (the `code_grade.py:468-471` `kind.get("exclude", "")` default, and the
worktree-duplicated probe it misclassifies) is corroborated by the scope reader's note at
`notes/review-harness-code-reviewer-planpanel-c0.md:49-61`.

## How "every other key byte-unchanged" was verified

Two independent checks, both after the `set-panel` write:

1. **Per-key serialisation.** `sha256(yaml.safe_dump(value, sort_keys=True))` for every top-level key,
   captured before the write and recompared after: `approval decisions feature lanes schema
   source_issues status tasks` all `SAME`, `panel` the only `CHANGED`. Key set and key order
   identical (`schema,feature,approval,status,source_issues,panel,lanes,decisions,tasks`).
2. **Byte-level revert.** Pre-write file `sha256 =
   bf5810a65ab1d3fdaa5944dd2fa7c28c250d531d81eb65ff6085047f91db419e`. Replacing the post-write panel
   block (lines 10-58) with the original five lines plus the blank separator reproduces that hash
   exactly — so every byte outside the panel block is untouched.

Check 2 also surfaced the one incidental effect: **`set-panel` consumed the blank line that separated
`panel:` from `lanes:`** (`disposition: open` at :58 now abuts `lanes:` at :59). Cosmetic, inside no
key's value, and not repaired here — repairing it would need a non-verb write on plan.yaml.

Post-write assertions: `last_run='2026-09-02-4-validator'`, `cycle=0`, exactly two reader entries
both `status: ran` (`should-not-exist`, `scope`) with no `persona`/`reason` since neither is skipped,
exactly five findings, `disposition: open` on each, every summary single-line and markdown-free,
`approval.status='pending'`, `status='plan'`. The project-wide unit suite was not run.

## Open questions

- **Q1 (harness defect, non-blocking):** the panel finding id scheme has two live spellings —
  `templates/plan.yaml:75` shows an 8-hex `PF-0123abcd`, `panel_findings.py` produces 32 hex and its
  suite calls itself the only source. One of them should be amended so a dispatch cannot honestly
  specify the other. For the harness owner, not for this feature.
- **Q2 (harness nit, non-blocking):** `set-panel` deletes the blank line following the panel block.
