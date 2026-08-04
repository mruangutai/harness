# Audit — DECISIONS.md conflicts and fragmentation — 2026-08-03

Main session, at `225cc98` + working tree. Reproducer: `.harness/notes/audit-decisions.py`.
Method: mechanical checks over the body and index, then read every flagged entry before calling it
a defect. Two of the five signal classes turned out to be my own false positives and are recorded as
such rather than deleted.

## Inventory

**173 top-level decisions** (fence-guarded), **11 amendment headings**, **173 index rows.**
No duplicate decision numbers. Every `DEC-NNN` reference in the body resolves to a real decision.
Index membership is complete in both directions — no row without a body, no body without a row.

`check-docs.sh`, `gen-decisions-index.py --check`, `check-state.sh` and `run-unit-tests.sh` all
exit 0. **Everything below is invisible to all four**, which is the point of auditing by hand.

## CONFIRMED — five index rows describe superseded rules as live

DEC-145 states: *"Supersedes the mid-run write discipline of DEC-24/66/67 (the op format, IDs, and
who-holds-the-pen all survive; only the **when** moved) and DEC-25/68's overflow flow becomes the
escalation path."*

So five decisions are **partially** superseded — their timing is dead, their substance lives. None of
the five index rows carries any marker:

| row | still says | actually |
|---|---|---|
| DEC-24 | Expertise write quality advisory in three layers | the mid-run *when* is dead (DEC-145) |
| DEC-25 | on overflow the member flags `expertise_full`... | now the escalation path only |
| DEC-66 | entries carry stable IDs, updates are ops | ops survive; mid-run timing dead |
| DEC-67 | doers reconcile and apply their own file in place | survives, but only under distillation |
| DEC-68 | a curation note is applied immediately | "immediately" is the superseded part |

**Why it matters.** The index is the sanctioned entry point and DECISIONS.md is explicitly never read
whole (DEC-150). A row is an open-or-skip filter — so an agent grepping `expertise` sees five live-
looking rows describing mid-run Expertise writing, which DEC-145 moved to distillation-only. The
harness's own `harness-expertise` skill is the thing that would be got wrong.

**This is an authoring gap, not a tooling one.** Ruling text after ` :: ` is hand-written (the index
header says so), and `check-docs.sh` only chases superseded *statements in other files*, not stale
rulings inside the index. DEC-19's row does carry `— SUPERSEDED BY DEC-84 — SUPERSEDED BY DEC-85`,
so the convention exists; these five simply never got it.

**Fix:** append a partial-supersession clause to each of the five rulings. Cheap, and it is the one
finding here with a live cost.

## CONFIRMED — four amendments sit outside their parent's section

| amendment | physically inside |
|---|---|
| DEC-137 amendment @3327 | DEC-138's section |
| DEC-138 amendment @4276 | DEC-168's section |
| DEC-138 amendment @4303 | DEC-168's section |
| DEC-138 amendment @4331 | DEC-168's section |

The generator matches amendments by heading name, so the `am.N` counts are right (DEC-137 shows
`am.1-am.2`, DEC-138 `am.1-am.7`). What misattributes is **refs and the `@line` anchor**, because
those are harvested positionally.

**The mechanism is proven, not theorised** — I reproduced it accidentally today. Appending a
`### DEC-142 amendment` at the end of the file put it inside DEC-173's section, and DEC-173's refs
silently gained `DEC-133 DEC-142`. Relocating the amendment next to DEC-142 reverted them and gave
DEC-142 the correct `refs: DEC-133`. So each of the four above is very likely donating refs to a
decision it has nothing to do with, and DEC-138's three donate to DEC-168.

**Fix:** relocate each amendment into its parent's section and regenerate. Mechanical, low risk.
**Better fix:** teach `gen-decisions-index.py` to attribute an amendment's refs to its named parent
rather than its position — otherwise this recurs every time someone appends.

## FRAGMENTATION — the DIGEST contract is the one real consolidation candidate

Surfaces named by 3+ index rulings:

| surface | decisions | internal cross-refs |
|---|---|---|
| `validate-digest.py` | DEC-122, 123, 127 | **3** — tight |
| `check-domain.sh` | DEC-19, 84, 143, 150, 160 | 1 |
| `feature.yaml` | DEC-47, 49, 129, 131, 150 | 1 |
| `harness.json` | DEC-03, 33, 35, 160 | 0 |
| `state.yaml` | DEC-46, 51, 154, 160 | 1 |
| `settings.json` | DEC-110, 111, 115 | 1 |

Two different shapes hide in that table, and only one is a problem:

- **Supersession chains are history, not fragmentation.** `check-domain.sh`'s five is really
  DEC-19 → 84 → 85 plus three live entries. The index marks the dead ones. Leave them.
- **Parallel LIVE rules on one contract is real fragmentation.** The DIGEST contract is governed
  simultaneously by **DEC-29** (three-part return), **121** (every field required), **122**
  (`SubagentStop` enforcement, exit 2), **123** (verdict roll-up), **126** (shared schema in one
  canonical template), **127** (read by key, fail open on own bugs — the hub, 6 refs into the
  cluster), **156** (a lead's written `digest.md` carries the block), **172** (the `yaml` fence) and
  **173** (`n/a`). **Nine live decisions, no single entry that states the contract.**

To know what a valid DIGEST is, an agent must open five or more entries and compose them. That is
exactly the cost DEC-150's index was created to avoid, and it is the strongest argument in this audit
for a consolidating entry — one "the DIGEST contract" decision that states the whole rule and cites
the nine as its lineage. **Recommended, not done:** it is a real decision about the authority's
shape, so it is the user's call, not a cleanup.

## Two signals I tested and REJECTED — recorded so nobody re-derives them

- **"Claimed reversal, no marker on the target" flagged DEC-62 → DEC-35.** False positive. DEC-62
  says GSD's *"(v1) no browser automation" limitation* is superseded and cites DEC-35 as the
  authority doing the superseding. My regex attached the verb to the wrong noun. DEC-35 is fine.
  Note the same regex **undercounted** the real finding: `DEC-24/66/67` slash-form meant only DEC-24
  was checked, and four more were missed until read by hand.
- **"Many decisions on one tag + zero cross-refs = authors unaware of siblings."** `approval` scored
  worst (19 live, 0 cross-refs), so I read all 19. They are decisions that *touch* approval
  incidentally — init interviews, merge gating, prototype sign-off — not competing rules about it.
  The zero is explained by a broad tag, not by drift. **Tag cohesion is a weak signal; file-surface
  clustering is the one that found something.**

## What was NOT audited

Semantic conflict between decisions that name no shared artifact and share no tag. Detecting that
needs reading 4,600 lines against itself, which DEC-150 forbids as routine practice and which this
audit deliberately did not attempt. The mechanical layer above is a floor, not a proof of consistency.
