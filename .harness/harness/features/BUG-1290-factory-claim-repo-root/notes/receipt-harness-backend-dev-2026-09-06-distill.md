# Receipt — harness-backend-dev — distillation — BUG-1290-factory-claim-repo-root

**BLUF:** Applied 2 replaces to the craft file (net zero growth, both via the merge tool) and 2
adds to the repository file (+2 lines, well under budget). All three lead-relayed candidates were
judged and rejected or absorbed as noted below; the two accepted entries are both my own
artifacts. Both `expertise-merge.py ops` and `check-expertise.sh` ran successfully by me directly
— nothing here is unapplied.

## Counts (read from disk, before → after)

| File | Section | Before | After |
|---|---|---|---|
| craft (`.harness/expertise/harness-backend-dev.md`) | Patterns | 15/15 | 15/15 (untouched) |
| craft | Gotchas | 15/15 | 15/15 (G-06, G-18 replaced in place) |
| craft | Outcomes | 10/10 | 10/10 (untouched) |
| craft | Open | 0/5 | 0/5 |
| craft | **file lines** | 45 | 45 |
| repository (`.harness/harness/expertise/harness-backend-dev.md`) | Patterns | 1 | 1 (untouched) |
| repository | Gotchas | 9 | 11 (G-10, G-11 added) |
| repository | Outcomes | 1 | 1 (untouched) |
| repository | Open | 0 | 0 |
| repository | **file lines** | 16 | 18 (budget 40) |

## Applied ops (`expertise_update`)

1. `replace G-06` (craft, Gotchas) — own artifact. Receipt
   `notes/receipt-harness-backend-dev-2026-09-06-13-eng.md` shows case 5g's assertion was
   `not _5b_property_holds(...)`, a bare negation satisfied by anything falsy — the B-27 raising
   mutant stayed green at 125/125 until replaced by the specific six-clause observable (exit
   code, empty stdout, required/forbidden stderr substrings). New text: "WHEN a mutation check
   asserts a bare negation of a compound boolean predicate DO replace it with the specific
   expected observable... — bare negation is satisfied by anything falsy, including a mutant that
   merely raises." **Displaced** G-06 (AST-vs-shared-helper guard technique), judged narrower and
   rarer than a trap recurring in any mutation/property-based suite.
2. `replace G-18` (craft, Gotchas) — own material, sharpened per the lead's un-relayed but
   invited correction. Old text said "confirm... after the first write"; new text says "after
   each write" and states plainly that a clean check for one write is not evidence later writes
   stayed in the worktree too. Same id, same subject, tightened scope claim.
3. `add G-10` (repository, Gotchas) — own artifact, T-04 receipt: `layout_migration.py`'s
   `READER_TABLE` row and `layout_fixtures.py`'s STUB key both had to be retargeted from
   `factory_claim.py` to `factory_config.py` in the same change, or the drift-guard would
   misclassify the old (now-dead) path as still the reader. Repo-specific: this mechanism exists
   only here.
4. `add G-11` (repository, Gotchas) — own material across T-01/T-03/T-04/T-05 receipts: every bin
   edit under `.agents/skills/harness/bin` needed an inode check (`stat -f %i`) against its
   `.claude/skills/harness/bin` twin to confirm the hardlink held. Repo-specific convention (this
   repo mirrors bin scripts as hardlinks); the entry states the convention and check, not the
   T-04 tool anomaly itself (see rejection below).

## Lead-relayed candidates — my judgment

1. **Bare-negation fail-open (ship-review case 5g).** **Accepted**, folded into G-06 above — this
   is my own artifact (receipt `-13-eng.md`), not merely the lead's relay; counted as
   own-artifact, not lead-relayed, since I built and verified the fix myself before the ship
   review cited it.
2. **F-02 measurement: missing file gives exit 2, mimics discrimination.** **Rejected.** Already
   covered in spirit by existing craft P-02 (smoke the real call path — a can't-open-file failure
   is exactly what a real-call-path smoke test surfaces) and G-01 (treat an ambiguous
   zero/nonzero result as inconclusive, not proof). Distinct framing, not a distinct rule; does
   not clear the bar to displace a full Gotchas section.
3. **B-32: diagnostic FAIL lines byte-identical to genuine ones.** **Rejected**, though I have my
   own instance of exactly this (receipt `-14-eng.md`'s `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b
   printed` line, an intentional diagnostic in the same format as a real suite FAIL). Already
   captured in spirit by existing craft G-16 (re-run the count and check it against the expected
   delta) — the discipline that catches a false negative from a silent zero-FAIL also catches a
   false positive from format-collision noise: check the count against what's expected, don't
   trust the raw grep. Not distinct enough on its own to displace a full section.

## Un-relayed correction (G-18) — used, not rejected

The orchestrator's framing note (a leak-report scoped to one task is not evidence the other tasks
are clean) sharpened G-18 as described above (op 2).

## Harness defects — NOT entered as Expertise, raised as open_questions instead

- The T-04 edit-tool anomaly on hardlinked `layout_migration.py` (edit reported success, read-back
  showed new content, but independent `stat`/`md5sum` showed stale bytes, and a retry was
  rejected as stale against an unpersisted internal snapshot) is a tool/harness defect, not a repo
  fact. It is NOT in Expertise. It was already flagged in the T-04 receipt as unfilable via
  `xd://report_issue` (check-domain blocked the path from this worktree); I am re-raising it as an
  open_question below since the underlying tool behavior was never filed anywhere durable.

## Source counts

- Own-observations (from my observations log): 1 substantive candidate used (bare-negation basis
  already folded via own-artifact receipt; the observations log's B-3 cache-coverage entry and the
  worktree-relative-path entry were already captured as G-18/existing craft, no new op needed).
- Own-artifacts (receipts): 3 used (G-06 replace, G-10 add, G-11 add) — the primary source this
  cycle.
- Lead-relayed: 0 accepted as relayed (candidate 1 recounted as own-artifact since I hold the
  primary receipt; candidates 2 and 3 rejected).

```yaml
VERDICT: PASS
DIGEST:
  headline: distilled BUG-1290 into 2 craft replaces (net-neutral, still 45/45/150 lines) and 2 repository adds (16->18/40 lines); rejected 2 of 3 lead-relayed candidates as already covered, one harness-tool defect re-raised as an open question
  tests_added: 0
  suite: n/a
  task: none
  files_touched:
    - .harness/expertise/harness-backend-dev.md
    - .harness/harness/expertise/harness-backend-dev.md
  expertise_update:
    - { op: replace, target: G-06, section: Gotchas, entry: "WHEN a mutation check asserts a bare negation of a compound boolean predicate DO replace it with the specific expected observable (exit code, output, required/forbidden substrings) — bare negation is satisfied by anything falsy, including a mutant that merely raises, staying green under exactly the mutant it exists to catch.", why: "own artifact, T-01-followup receipt: case 5g stayed green at 125/125 under a raising mutant until the bare negation was replaced" }
    - { op: replace, target: G-18, section: Gotchas, entry: "WHEN operating inside a worktree-based session DO pass every edit/write/bash path (and any loaded module's root) as the absolute worktree path, and confirm with `git status --porcelain` in that worktree after each write — a clean check after one write is not evidence later writes stayed in the worktree too.", why: "sharpened per orchestrator's framing note: a scoped leak-check is not blanket evidence" }
    - { op: add, target: G-10, section: Gotchas, entry: "WHEN a module reading a tracked surface (e.g. the features root) moves to a new file DO retarget its row in layout_migration.py's READER_TABLE and its layout_fixtures.py STUB key together — the drift-guard tracks specific module paths and misclassifies silently if the row still names the old file.", why: "own artifact, T-04 receipt: FEATURES_ROOT->factory_config move required retargeting both the reader row and the STUB key" }
    - { op: add, target: G-11, section: Gotchas, entry: "WHEN editing a file under .agents/skills/harness/bin DO check whether .claude/skills/harness/bin holds a hardlinked twin (same inode) and confirm via stat -f %i after the edit — several bin scripts are mirrored as hardlinks, and checking only one path can miss the pair going out of sync.", why: "own material across T-01/T-03/T-04/T-05 receipts: every bin edit required an inode check" }
  open_questions:
    - { id: Q1, question: "The T-04 edit-tool anomaly (edit reported success on a hardlinked file, read-back showed new content, but independent stat/md5sum showed stale on-disk bytes, and a retry was rejected as stale against an unpersisted internal tag) was never filed — check-domain blocked xd://report_issue from this worktree. Is there a durable channel for a build-time-only agent to file a tool defect it cannot reach via xd://report_issue?", blocking: false }
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-distill.md
```
