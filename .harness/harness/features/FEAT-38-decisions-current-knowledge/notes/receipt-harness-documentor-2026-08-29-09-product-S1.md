# Receipt — harness-documentor — FEAT-38 · S1 · drop BUILD.md's am.2 citation

**PASS.** `BUILD.md`'s sole `am.N` citation is gone; the row now cites `DEC-145` plainly, and its
assertion is still true of DEC-145's post-fold body. One row changed, one hunk, `1 insertion(+),
1 deletion(-)`. `DECISIONS.md` and `DECISIONS-INDEX.md` untouched. SC-04's last squad-writable site
is closed.

## The truth-check (the acceptance sentence)

**The row's claim survives the fold:** DEC-145's current body states at `DECISIONS.md:3239-3240`
*"the distillation digest carries per-source accept counts so a skim that stops yielding can be
cut"*, which is exactly the row's ruling *"non-zero accepted count per feature, else sunset it"*.

The row's two supporting halves are also live in the same paragraph, so no part of the row is
orphaned by dropping the suffix:

- *"1 reasoned rejection"* → `DECISIONS.md:3237-3238`: *"the member accepts or REJECTS each with a
  reason, and a rejection is a first-class recorded outcome"*.
- *"2 stale-entry catches"* → `DECISIONS.md:3240-3241`: *"The skim doubles as a staleness audit — it
  surfaces entries that code shipped later in the same feature has contradicted"*.

## The trap, checked independently — am.2 was FOLDED, am.3 was DELETED

I did not take this on trust from the T-08 receipt; I read `base_sha` directly.
`git show 7ebfc9e:.harness/harness/docs/DECISIONS.md` shows DEC-145 (heading @3494) carrying **two**
amendment blocks before DEC-146 (@3573):

| Block | At `7ebfc9e` | Fate |
|---|---|---|
| `**Amendment 2 (2026-07-29) — the digest-skim, dry-run-proven before wiring.**` | @3536 | **folded** into the body |
| `**Note (2026-08-24): am.3 below is MOOTED.**` + `**Amendment am.3 (issue #80)`  | @3552, @3557 | **deleted** by T-08 |

So the missing `am.2` is explained by the fold, **not** by T-08's deletion. The deleted block was
am.3, corroborated by T-08's own receipt (`receipt-harness-documentor-2026-08-29-06-product-T-08.md:55`:
*"The MOOTED DEC-145 block (`Note (2026-08-24): am.3 below is MOOTED` plus the ship-refresh…"*).

The fold is content-verifiable, not just positional: old am.2's clauses map one-to-one onto current
body lines 3236-3246 — three-party pipeline with ≤3 candidates, rejection as first-class outcome,
displacement-never-merge, per-source accept counts, the run-dir slug grammar, and the 9-of-15
re-bloat finding.

**One narrowing worth recording (P-12).** The body kept the *ruling* but dropped am.2's numeric
dry-run evidence (11 digests / 2 accepted / 1 rejection / 2 catches). Those figures now survive only
in this BUILD.md row itself and in history at
`git show 7ebfc9e:.harness/harness/docs/DECISIONS.md` (lines 3536-3551). Nothing is lost, but
BUILD.md is now the only live in-tree site for them — which is fine, since the row's own middle
column is where that evidence belongs.

## Verify — run from the worktree, literal output

| Check | Result |
|---|---|
| `grep -nE 'am\.[0-9]' .harness/harness/docs/BUILD.md` | no output (exit 1) — **PASS** |
| `grep -cE 'am\.[0-9]' .harness/harness/docs/SPEC.md` | `0` |
| `grep -cE 'am\.[0-9]' .harness/harness/docs/DECISIONS.md` | `0` |
| `git diff --stat -- …/DECISIONS.md …/DECISIONS-INDEX.md` | **empty output** (quoted literally below) |
| `git diff --stat -- …/BUILD.md` | `1 file changed, 1 insertion(+), 1 deletion(-)` |
| `git -C <main checkout> status --porcelain` | BUILD.md **absent** (only pre-existing untracked `??` noise) |
| worktree `status --porcelain` | ` M .harness/harness/docs/BUILD.md` |
| `rev-parse HEAD` | `b32013c7213c045aeb90da4a6d1ffc10c7d7d7e5` — unmoved |

The frozen-pair diffstat, literally — the command produced **zero bytes of output**, naming neither
path because neither differs:

```
$ git -C <worktree> diff --stat -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md
$
```

DECISIONS.md remains 6299 lines. Nothing staged, nothing committed.

**Baseline first (G-03).** I ran the verify block *before* editing: BUILD.md then matched at line 226,
so the work had not already landed and I did not double-write it.

**Hunk bound (P-03/P-08).** The tree was dirty at spawn, so `--stat` alone is not proof of authorship.
`git diff -U1` shows exactly one hunk, `@@ -225,3 +225,3 @@`, one line replaced, tail shortened by
5 characters — precisely `" am.2"`. No whitespace, alignment, or neighbouring-row change.

## Scope held

Swept BUILD.md for the concept, not just the token (P-16): `grep -niE 'amendment|supersed|amend'`
returns three hits (lines 211, 547, 605), all describing **BUILD.md's own** record history — a
superseded ledger row and a superseded pilot-gate section. None is DECISIONS.md amendment machinery
and none is falsified by this feature, so all three stand untouched.

Did not touch T-14's remaining `am.N` sites (`.claude/skills/**`, `.claude/commands/harness.md`,
`.gitignore`, `.harness/factory/fleet.yaml`, `templates/gitignore.snippet`) — those are
main-session-direct.

## Open questions

None blocking. One advisory, for the orchestrator's SC-04 evidence: this row was asserted by SC-04
and owned by no task's `verify:`, so after this fix SC-04 still has **no automated clause** covering
`.harness/harness/docs/`. The gate that proves it is a manual sweep — mine. If SC-04 is meant to
stay true past `review_sha`, the sweep root belongs in a checker rather than in a receipt.
