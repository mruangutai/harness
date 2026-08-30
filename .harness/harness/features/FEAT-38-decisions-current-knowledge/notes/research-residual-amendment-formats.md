# COVERED

All eight residual sites fall inside the approved REQ-01/REQ-02. Folding them is a fix cycle in this
segment, needs no re-signature, and carries one **required companion edit** at `DECISIONS.md`
`- **Zero dependencies.**` (DEC-101 body) without which site 5 cannot be folded honestly.

Line numbers below re-derived by content in the worktree at `0a120c657cb7` (dispatch's 09e3d7b numbers
had not shifted for these eight, but `DECISIONS.md` is under concurrent edit — re-derive again).

## Why COVERED, on four grounds, none of them SC-01's grep coverage

1. **REQ-01's leading clause binds; its em-dash list illustrates.** The requirement is "a reader sees
   only live decisions, **each stating current truth directly**" — then four named instances. A
   paragraph opening `**Amended same day, per the user:**` or `**Correction to this entry as first
   written.**` states how the entry *changed*, with attribution, which is the negation of the leading
   clause whatever the markup. A ruling that reads the four instances as exhaustive is reading the
   illustration as the requirement.
2. **DEC-205 — landed by this feature — already forbids them by substance.** "An entry states current
   truth directly. A correction rewrites the entry it corrects" and "Supersession is deletion. There is
   no `SUPERSEDED BY` marker" (DEC-205, first two clauses). Ship the eight unfolded and the file
   violates its own new convention in eight places on day one, two of them (`**Supersedes the …**`,
   `**Superseded:**`) against the supersession clause specifically. That is a self-contradiction inside
   the approved deliverable, not an extension of it.
3. **REQ-02 is actively violated today, not merely under-covered.** DEC-171 quotes the reversed "Zero
   dependencies" bullet inside a supersession marker while that bullet is **still live in DEC-101's
   body** stating the opposite. A reader of DEC-101 sees a rule the tree measured false, presented as
   current. REQ-02 exists to prevent exactly the re-proposal that bullet invites.
4. **Nothing about scope, goal or an approved decision changes.** No new REQ, no new SC, no new file —
   every site plus the companion edit is inside `.harness/harness/docs/DECISIONS.md`, already T-08's
   sole `files:` entry, and the work traces REQ-01/REQ-02 unchanged. The "38 amendments = 25 + 13"
   figure lives in T-08's `intent:`, a dispatch instruction, not in any signed requirement; T-08's own
   intent opens by overriding "every intake figure for this", which is the precedent for correcting a
   count without re-signature.

**The case for NEW, and why it loses.** The operator read an enumeration of four shapes and may have
priced the work by it. But a signature attaches to the outcome sentence, and every additional fold
delivers *more* of that outcome rather than something else; the operator's prune-at-signature lever
(DEC-132) does not apply to work that narrows nothing. Cost is one file, eight paragraphs, one bullet.

**Inspected and deliberately EXCLUDED** — do not refold these; their lead-ins state a relation between
decisions as current truth, not the paragraph's own provenance: DEC-99 "What the pilot work bought
before being superseded" (the *pilot gate* was superseded, not the entry), DEC-178 "DEC-148 is only
PARTIALLY superseded here", DEC-187 "This clarifies DEC-35's scope rather than amending it", DEC-203
"the superseded bound". A sweep of every bold lead-in carrying an amend/correct/supersede/revise verb
returns 24 lines; eight are provenance-announcing, these four are the near misses.

## The eight sites

| DEC | line | lead-in | does | recommended current-truth clause |
|---|---|---|---|---|
| 38 | 414 | `Correction to an earlier design.` | falsifies a pre-decision design (never a recorded DEC) | Delete the lead-in only; open at "The orchestrator is the main session running the `/harness` playbook". The `**Because:**` line already carries the falsification ("two names for one actor produced contradictory statements") — keep it. |
| 41 | 453 | `Correction to an earlier design.` | falsifies the belief that panels need a synthesizer | "**Chose:** no `harness-synthesizer` and no generic consolidation step exists — running the panel and assessing its feedback is the validator lead's defining job." The negation carries REQ-02. |
| 76 | 880 | `Correction to a stated assumption:` | falsifies the assumption Astryx is globally available | Drop the wrapper; the sentence already begins with the negation — "**Astryx is not globally available as a Claude Code capability.**" Keep it in body position, before `**Tradeoff accepted:**`. |
| 132 | 2854 | `Amended same day, per the user:` | falsifies the weaker "merely permitted" reading | Merge into the second body paragraph: "Adding criteria beyond the user's is **expected**, not merely permitted; SCs that merely restate the user's list are under-delivery, and the signature is where the user prunes over-reach." |
| 171 | 4105 | `Supersedes the "Zero dependencies" bullet of DEC-101.` | falsifies DEC-101's bullet — **which is still live** | "PyYAML is permitted. The earlier zero-dependency ruling — no YAML library, the manifest reader a narrow line scanner — was measured false: the scanner dropped an entire run from `runs` on a legal trailing `# comment`. Everything else in DEC-101 stands, as does CLAUDE.md's files-only constraint." **Companion edit, same commit:** delete DEC-101's `- **Zero dependencies.**` bullet (its body, two lines) — per DEC-205 supersession is deletion, and per REQ-02 the falsified claim now survives here, once. |
| 172 | 4195 | `Correction to this entry as first written.` | falsifies two of this entry's own claims | State both as current truth, keeping one falsification clause so neither is re-proposed: "**13 files** carry a return template — nine `.claude/agents/harness-*.md` plus four skills; seven agents inherit `harness-handoff`'s, which is why the count is not 16. **The ordering constraint binds in one direction only:** the parser already accepts a fenced return, so templates may ship first; what must not ship first is the parser's rejection of unfenced returns." Drop "Both halves were wrong" and "as first written". |
| 180 | 4727 | `Superseded:` | *is* the falsified prior behaviour, mislabelled | Reattach as the closing clause of the preceding `_norm`/`_show` paragraph: "Before this change the sweep walked up to 234 candidates across the main checkout and every worktree and named none of them — one logical file in five checkouts produced five byte-identical findings, and a reviewer received another agent's transient fixture, unattributable, in their own session." |
| 202 | 5977 | `Amended by #836 after local compatibility testing.` | falsifies the first cut's link direction | One clause onto the existing "Claude Code stays usable" paragraph (which already states the correct direction): "The reverse — authored tree at `.agents/skills`, `.claude/skills` a symlink — was tried and measured to fail: Claude Code's discovery contract requires the real directory at its native path, and local filesystem reads succeeding is not that contract." Drop the lead-in and its issue attribution. |

## For whoever folds these

- Sites 38 and 41 are lead-in deletions, not rewrites: the falsification already survives in the
  `**Because:**` line. Do not "restate" it twice.
- Site 171 is the only one that touches a second entry. Fold it and DEC-101's bullet in one edit; a
  fold that leaves the bullet live makes the file assert both halves and is worse than not folding.
- DEC-205's own clauses are the acceptance standard here. Read them before writing, not after.
- Every task editing this file also lists `DECISIONS-INDEX.md` and re-runs `gen-decisions-index.py`:
  the index stores a per-row source line, so lengthening any entry shifts later anchors.

## Open questions

- Q1 (non-blocking): site 172's correction is a two-bullet list. Collapsing it to prose versus keeping
  two bullets is the documentor's call; both satisfy REQ-01.
