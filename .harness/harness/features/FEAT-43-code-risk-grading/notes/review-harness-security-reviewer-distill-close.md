# Distill close — harness-security-reviewer — FEAT-43-code-risk-grading

Final state: 3 candidates landed (O-09, O-10 as pure adds; C3 as a genuine displacement of G-09),
0 rejected. Both the durable main checkout and the (now-disposable) worktree copy of
`harness-security-reviewer.md` are verified byte-identical (md5 `09ffe777a295de5ea849483ca6ef56a2`)
and `check-expertise.sh` OK (exit 0) on both.

## Sources
Own notes: only one of the four named paths actually exists on disk this feature —
`notes/review-harness-security-reviewer-validate-final-panel.md` (the other three filenames in
the dispatch are not present in this worktree; not hunted further, per instruction). Relay
candidates C1, C2, C3 as given in the dispatch (not independently re-read; trusted on the text
as relayed, per the six-spawns test).

## Root cause of the durable-checkout miss — my error, not a tool artifact
My first `apply` ran `cd <worktree root> && expertise-merge.py apply --file
.harness/expertise/harness-security-reviewer.md ...` — a relative `--file` resolved against the
worktree cwd, so it wrote only the worktree copy and never touched the main checkout at all.
`Feat43ValidationDistill` caught this by grepping both absolute paths seconds apart and found a
real split (O-09/O-10 present in one, absent in the other, neighboring ids matching fine in
both) — this was a correct, checkable diagnosis, not a stale read. **I initially told the lead
their read was "likely stale"; that was wrong, and I retracted it once I checked my own command
history and found the cwd-relative-path bug directly.** Re-ran with `cd
/Users/molchairuangutai/GitHub/harness && expertise-merge.py apply --file
.harness/expertise/harness-security-reviewer.md ...` (relative path now resolving under the main
checkout root), which landed correctly. Lesson: a relative `--file` under this tool is only as
safe as the caller's cwd discipline when two live copies of the same repo-relative path exist —
name the durable checkout by absolute path in future distillation dispatches.

## Correction: displacement at a cap IS achievable — my earlier conclusion was wrong
I initially reported that `expertise-merge.py apply`'s pure-add union semantics made "replace"
mechanically impossible at a full section, and rejected C3 on that basis. `Feat43ValidationDistill`
corrected this, citing dev-ops precedent: the two-step procedure is (1) `apply` with the
replacement text under the SAME id — this exits 7 and applies nothing, but the CONFLICT output
confirms the existing text really is what you think it is; (2) a targeted single-line replacement
of exactly that line (verified before/after: only that one line changed, both copies stay
byte-identical, `check-expertise.sh` still OK). This is the "7 = real conflict — resolve it
yourself" branch of the retry table, not a workaround of it. What remains true and still holds:
exit 8 (cap exceeded) fires only for a genuinely NEW id past cap, and there is still no
CLI-only path that both adds a new id and removes an old one in one `apply` call — the removal
step is necessarily a direct, minimal, verified edit, never a blind whole-file overwrite.

## Candidates — final dispositions
- **O-09 (own, accepted):** self-report vs. ground-truth binding, from my own `validate-final-panel`
  Finding 1 (`code_grade: n_a` self-certification bypass) — added, room was available (8/10 → 9/10).
- **O-10 (relay C1+C2 merged, accepted):** enumerate every ref state including the ordinary/mundane
  one, and read fail-open/fail-closed off whether the delta widens or narrows the accepted set —
  added (9/10 → 10/10). Natural home was Patterns, but this file's own O-01..O-08 are already
  audit-heuristic in shape, so Outcomes was not a stretch.
- **C3 (relay, accepted → displaces G-09):** "trace an observed symptom to its actual producing
  mechanism before charging the artifact under review" — displaced **G-09** ("migration adopts a
  wildcard pattern but one site keeps a hardcoded literal"), which I judged the narrowest/most
  situational of the 15 Gotchas (a single specific migration shape vs. C3's general
  misattribution discipline).

No candidates remain rejected without disposition.

```yaml
VERDICT: PASS
DIGEST:
  headline: three candidates landed on the DURABLE main checkout (O-09, O-10 added; C3 displaces G-09), verified byte-identical against the worktree copy and check-expertise.sh clean on both; both of my first-round conclusions (durable-copy miss, and "no replace at cap") were mistakes on my part, corrected this round
  expertise_update:
    - { op: add, target: none, section: Outcomes, entry: "O-09: WHEN a check accepts a self-reported field as proof of a security claim (e.g. a digest's own reviewed: range) DO verify it is bound to an external ground truth (e.g. the feature's actual pinned commit) — unbound self-consistency lets a same-commit no-op range satisfy the check as if nothing changed.", why: "own note, validate-final-panel Finding 1 — self-certification without external binding is a distinct vulnerability shape" }
    - { op: add, target: none, section: Outcomes, entry: "O-10: WHEN judging fail-open/fail-closed of a range- or ref-based check DO enumerate every ref state (fresh, stale ancestor, missing, descendant, diverged) in a table, including the ordinary post-merge case most often skipped — and rate each by whether the delta widens (fail-closed) or narrows (fail-open).", why: "relay C1+C2 merged — the send-back that changed a PASS to FAIL turned on enumerating the mundane state and reading widen/narrow off the ref-state table" }
    - { op: replace, target: G-09, section: Gotchas, entry: "G-09: WHEN an observed symptom (e.g. a widening effect) could come from either the reviewed artifact or a nearby script DO trace it to the exact producing mechanism before charging the artifact — a symptom from a different script's own merge-base call is not evidence against the code under review.", why: "relay C3 — attribution discipline is more broadly useful than the wildcard-vs-hardcoded-literal migration case G-09 named; confirmed real conflict via apply exit 7, then a verified single-line replacement" }
  candidates_accepted: { relay: 3, own: 1 }
  candidates_rejected: { relay: 0, own: 0, reasons: [] }
  section_counts_before:
    harness-security-reviewer.md: { Patterns: 15, Gotchas: 15, Outcomes: 8, Open: 0 }
  section_counts_after:
    harness-security-reviewer.md: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 0 }
  check_expertise:
    harness-security-reviewer.md (main checkout): 0
    harness-security-reviewer.md (worktree): 0
  open_questions:
    - { id: Q1, question: "expertise-merge.py apply's exit-7 conflict is the intended signal for a genuine displacement at a cap, resolved by a verified single-line edit rather than a whole-file write — worth stating explicitly in harness-distill/SKILL.md, since my first pass read the retry table as forbidding this and wrongly concluded displacement was impossible.", blocking: false }
    - { id: Q2, question: "A relative --file to expertise-merge.py is only as safe as caller cwd discipline when two live copies of the same repo-relative path exist (a merged worktree plus the main checkout). My first apply's cwd was the worktree, so it silently wrote the disposable copy. Dispatches spanning a soon-to-be-removed worktree should name the durable Expertise checkout by absolute path.", blocking: false }
  files_touched:
    - ".harness/expertise/harness-security-reviewer.md (worktree)"
    - "/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md (main checkout, durable)"
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-security-reviewer-distill-close.md
```
