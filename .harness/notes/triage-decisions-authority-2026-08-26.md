# DECISIONS.md consolidation — impact report — 2026-08-26

Produced by harness-product-lead doing the analysis itself (no member dispatched — the
harness-pm single-flight defect killed three prior attempts). Written to disk by the main
session because a lead has no legal path for a note outside a feature run dir.

Every line number below was opened, not inferred. The main session independently re-verified
the five load-bearing claims marked VERIFIED.

## 0. Headline

**Deleting struck entries is safe for ONE of the eight today, four of eight after a repoint
sweep, and impossible for four.**

| Struck entry | Named successor | Source |
| --- | --- | --- |
| DEC-186 | DEC-203 | `DECISIONS.md:5673`; index `:204` |
| DEC-192 | DEC-203 | `DECISIONS.md:6099`; index `:210` |
| DEC-196 | DEC-203 | `DECISIONS.md:6505`; index `:214` |
| DEC-90 | SPEC 15.1 (not a decision) | `DECISIONS.md:1164` |
| DEC-103 | **none** | `:1591-1593` the mechanism was deleted |
| DEC-104 | **none** | `:1600-1606` "retired, not reused" |
| DEC-137 | none (glossary half to DEC-162) | `:3132`, `:3129` |
| DEC-140 | none, and none needed | zero external citations |

Four of the eight carry a sentence written specifically to make deletion wrong.

## 1. Contradiction ledger — SHOWN

**C-1. DEC-188's retention clause vs instruction 4.** VERIFIED at `DECISIONS.md:5942-5944`:
"**Struck decisions keep their heading and a strike record.** They are not deleted from the
file. A reader who finds `DEC-103` cited in a shipped digest must land somewhere that explains
what happened, and an absent entry reads as a broken reference rather than a decision."
Not reconcilable by interpretation. The honest mechanism is to strike that clause by the
procedure DEC-188 itself defines.

**C-2. DEC-188:5938-5940 routes partly-overtaken decisions to amendment**, which instruction 3
abolishes. Subsume-in-place erases the visible difference between "amended" and "always so".
That cost is recoverable only from git.

**C-3. DEC-159 contradicts itself on the handoff cap** (#678). `:4061` says ~60 raised from 40;
`:4079-4080` says denied above 40. Code settles it: `check-domain.sh:1258` caps at 60.
Eighteen lines apart, in one entry. `:4079-4080` is false.

**C-4. DEC-159 asserts a `phase:` field DEC-192/DEC-203 deleted.** NEW, unfiled. `:4052-4053`
vs `:6110` "The `phase` field is deleted", and `SKILL.md:243` says so live.

**C-5. DEC-159 spells it `feature.yaml`** (#687) — but the ticket's line numbers are stale
(DEC-159 now begins at `:4038`; both mentions are on `:4052`) and it understates scope:
`feature.yaml` appears **47 times** across the file. Which are live rules is the real question.

**C-6. DEC-181 states a budget and a code citation that are both false.** `:5409-5410` cites
`check-domain.sh:779-780`, which is an unrelated comment block. `:5416` says
"feature.yaml 200/20"; code says `feature.json` 300.

**C-7. The worktree layout falsifies DEC-193** (#626) — `:6151-6153` spells one segment; disk
has two (`worktrees/harness/<id>`). DEC-143's index row `:162` same defect. **DEC-95 is NOT
falsified** — the ticket over-claims. DEC-193 amendment 2 respelled the second location and
walked past the first.

**C-8. Two amendments are both "DEC-189 amendment 1"** — `:6015` and `:6394`, different dates,
and `:6394` sits physically inside DEC-194's span. The index declares one.

**C-9. Two index rows name a decision that does not exist.** VERIFIED — `DECISIONS-INDEX.md:123`
and `:206` both list `DEC-161` in refs. Zero `## DEC-161` headings exist. The generator scraped
the id out of sentences describing its deletion (`:1603`, `:5924`).

## 1b. SUSPECTED — not shown

- **S-1 (#748)** DEC-192 is already STRUCK; the ticket may be closed or moved to DEC-203.
  Unread: whether DEC-203 enumerates `Abandoned`.
- **S-2 (#473)** `dispatch` confirmed absent from DEC-195's tags; DEC-195's body unread.
- **S-3 (#803/#680)** DEC-199 ships a locked merge core. Whether DECISIONS.md is registered
  with it is unchecked. One grep settles both tickets.
- **S-4 (#438)** not opened.
- **S-5** the four excluded tickets were not opened. Silence is not agreement.

## 2. Consolidation map

| Cluster | Tickets | Survivor | Note |
| --- | --- | --- | --- |
| index generator | #439, #473 | **#439** | same surface, two prose-as-data heuristics |
| missing contract | #686 | **separate, BLOCKS #439** | cannot fix a generator against no contract |
| other script | #438 | **standalone** | different script, different defect class |
| DEC-159's body | #678, #687 | **#678** | broadened: three falsified statements, not one |
| struck-citation repoint | #844, #748 | **#844** | `DECISIONS.md:7276` already names #844 as the repoint |
| concurrent authorship | #803, #680 | **#680** | settle S-3 first |
| file structure | #615, #448 | see below | |

**#615 is NOT the parent, and #448 is its opposite.** #448 proposes a checker for amendment
spans — a construct #615 deletes. They are mutually exclusive on the same surface. Only one
ordering is cheap. Close #448 as superseded once #615 lands.

## 3. Amendment inventory — the premise was short by 13

**VERIFIED: 25 sub-section headings + 13 bold-inline = 38 amendments.** The bold-inline format
(`**Amendment N (date) — ...**`) is invisible to the sub-section grep.

The 25 sub-sections span 9 decisions. Hard cases: **DEC-138's eight** (split across ~1,300
lines and 29 intervening decisions; am.5 renumbered after a collision; am.7/am.8 partly struck)
and **DEC-196's four**.

The 13 bold-inline span 8 decisions: DEC-11 `:149`; DEC-145 `:3523,:3529,:3550`; DEC-149
`:3619`; DEC-152 `:3739`; DEC-157 `:3926`; DEC-158 `:3947`; DEC-183 `:5612`; DEC-196
`:6559,:6587,:6615,:6657`.

**Roughly 11 are mechanical, 27 need judgement.** Two are already dead and should be deleted
rather than folded: `DEC-145 am.3` (MOOTED at `:3545`) and `DEC-196 am.4` (struck at `:6514`).

Index `am-span` tokens declare 37. The excess of one is the duplicate at `:6394`. The index is
right by luck — it cannot see the bold-inline format at all.

## 4. Strike inventory

Eight fully struck: DEC-90, 103, 104, 137, 140, 186, 192, 196.

**A ninth exists, partial.** `DECISIONS.md:5409` — DEC-181 is "STRUCK IN PART". Instruction 4
has no defined behaviour for a half-struck entry. Rule on it or it stalls the sweep.

| Entry | Total | External | Live code/CI | Live docs |
| --- | --- | --- | --- | --- |
| DEC-90 | 22 | 18 | 0 | 0 |
| DEC-103 | 31 | 18 | 0 | 0 |
| DEC-104 | 33 | 27 | 1 | 1 |
| DEC-137 | 32 | 18 | 1 | 2 |
| **DEC-140** | **7** | **0** | **0** | **0** |
| DEC-186 | 185 | 161 | 7 | 0 |
| DEC-192 | 163 | 153 | 14 | 2 |
| DEC-196 | 185 | 167 | 0 | 0 |

## 5. Citation debt

VERIFIED: **DEC-140's 7 citations are 4 in DECISIONS.md and 3 in the generated index. Zero
external.** It is the only free deletion.

VERIFIED: **DEC-186 and DEC-192 are cited inside eight live files under `bin/` plus
`.github/workflows/tests.yml`** — while `DECISIONS.md:5915` says a struck decision is "removed
from every gate". They are struck and they are in the gates. Nobody has ruled on that.

`check-state.sh:918` carries a live invariant literally named `INV-24 (DEC-186)`.

`test-gen-decisions-index.py:133` uses **DEC-104's body as a test fixture**. Deleting the entry
may break the test, not merely orphan a citation.

**Reported separately, not counted as live:** roughly 481 historical feature-receipt citations
to DEC-186/192/196, concentrated in FEAT-10, 16, 18, 23, 24, 26, 33 and 40. These are signed,
shipped artifacts and cannot be rewritten. They are exactly the readership DEC-188's retention
clause was written for. Six worktrees each carry a full DECISIONS.md copy, roughly doubling
every count above; excluded throughout.

## 6. What cannot be done

1. **Deleting DEC-103, 104, 137 and 90 breaks 81 citations with no repoint target.** The
   mechanisms they created were removed, not superseded.
2. **The file already proves what that looks like.** DEC-161 was deleted outright. The index
   still lists it in two rows and the generator recreates them on every run, because it scrapes
   the id from the sentence describing the deletion. **The one prior outright deletion in this
   file's history produced a permanently self-regenerating broken reference.**
3. **Instruction 4 cannot execute while DEC-188:5942-5944 stands.** Any agent following the
   decision discipline will open DEC-188 and correctly refuse.
4. Whether DECISIONS.md carries a shape budget is UNVERIFIED — the full gate was not read.

**What CAN be done:** DEC-140 today at zero cost. DEC-186/192/196 after repointing 21 live
occurrences to DEC-203, plus a ruling on the dangling receipts. DEC-103/104/137/90 only by
accepting broken references or authoring a successor entry saying what was removed — which is
the struck entry under a new number, i.e. deletion in name only.

## 7. Recommended ordering

1. **Author the DECISIONS-INDEX generation contract as a decision (#686).** Until a signed
   contract says what happens to a row when its entry disappears, every deletion is undefined
   behaviour. DEC-161 is the proof.
2. **Rule on DEC-188's retention clause.** Recommended: strike `:5942-5944` and replace it with
   a narrower rule — *a struck decision is deleted only when a named successor exists to repoint
   its citations to*. That permits DEC-140/186/192/196, forbids DEC-90/103/104/137, and is
   derived from the measurement rather than asserted beside it.
3. **Delete DEC-140.** One entry, zero external citations — the cheapest possible test of steps
   1 and 2 together.
4. **Repoint DEC-186/192/196 to DEC-203 (21 live occurrences), then delete.** Fold #844 in as
   its first item. Settle #748 at the same time. `check-state.sh:918`'s `INV-24 (DEC-186)` needs
   a decision, not a find-and-replace.
5. **Execute #615: fold amendments in place. Budget for 38, not 25.** Mechanical ones first,
   DEC-138's eight and DEC-196's four last. Delete the two dead amendments. Fix the duplicate
   `DEC-189 am.1` and relocate `:6394` out of DEC-194's span.
6. **Fix DEC-159's three false statements, DEC-181's two, and DEC-193/143's worktree spelling**
   — in the same editing pass as step 5, never before it.
7. **Close #448 as superseded by #615.**

**Not in this ordering, deliberately:** #438 (independent, blocks nothing — run in parallel);
#680/#803 (settle S-3 first); #486 (re-file after step 5 or it targets text that no longer
exists).

## 8. Two things not asked about

**FEAT-38 IS #615 and FEAT-39 IS #439.** Both exist, both stalled, neither has a BRIEF or a
plan. FEAT-38 `STATE.md:10-12`: plan run 1 returned BLOCKED without spawning pm —
`dispatch-guard.sh` refused under single-flight on an orphaned `harness-pm` claim. FEAT-39
same cause, verdict ESCALATE. Neither has a feature dir in the main checkout.

**Four product-lead runs have now died the same death**, all on `harness-pm` single-flight
against a claim keyed by PERSONA, not instance. FEAT-38 and FEAT-39 raise it independently, in
the same words. It is why this report was produced by a lead doing member work, and it will
kill the next attempt too.

## 9. OPERATOR RULING, 2026-08-26 — successors checked, seven of eight are deletable

The main session re-checked section 0's "no successor exists" claim before the operator ruled.
**It was too strong.** It searched for a decision CARRYING THE RULE FORWARD. A citation does not
need that — DEC-188:5943 asks only that a reader "land somewhere that explains what happened."

| Struck | Successor | Evidence |
| --- | --- | --- |
| DEC-140 | none needed | zero external citations |
| DEC-186 | DEC-203 | `:5673` |
| DEC-192 | DEC-203 | `:6099` |
| DEC-196 | DEC-203 | `:6505` |
| **DEC-103** | **DEC-188** | DEC-188's own body, `:5918`: "DEC-103 and DEC-104 are struck" |
| **DEC-104** | **DEC-188** | same sentence, by number |
| **DEC-137** | **DEC-162** | `:3134` "DEC-162 and its INV-19 hold" (glossary half) |
| DEC-90 | SPEC 15.1 only | `SPEC.md:2208` exists, but a spec section is not a decision |

**RULING: delete the seven. DEC-90 stays in place with its strike record.**

DEC-90 is the one exception, and the reason is stated rather than assumed: its boundary lives in
a spec section, so a citation would degrade from a decision reference to a pointer of a different
kind, and its 18 historical citations cannot be edited. One exception, recorded, is cheaper than
a uniform rule that quietly breaks one case.

This makes section 6's "four cannot be done" obsolete. Only DEC-90 cannot, and it is not being
attempted. Sections 1-8 stand as written.
