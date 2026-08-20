# Receipt — harness-data-engineer — FEAT-29-graphql-budget — distill-2026-08-20-14-eng

## Verdict: 4 accepted (all lead-relayed, reshaped), 1 rejected. No self-derived candidates beyond
what the relay already surfaced from my own receipt.

Source read in full: my own receipt (`receipt-harness-data-engineer-simplify-eng.md`) and the
lead's collation (`runs/2026-08-19-10-eng/digest.md`). No observations log exists for this feature
(none was written mid-run) — the dispatch's framing that I logged no observations is confirmed.

## Per relayed candidate

1. **P-04 enumeration ("checks performed" header)** — REJECTED. This is my receipt demonstrating
   existing craft entry P-04 correctly, not a new lesson. P-04 already says exactly this. Adding a
   second entry that restates it is the "distillation smell" `harness-distill` warns against
   (multiple incidents, same rule). No op applied.

2. **`import re as _re_station` reuse-of-precedent check** — ACCEPTED, reshaped to drop the
   file-specific example. Generalizes past this repo: before flagging a new import/name as
   complexity, check whether the file already uses the same convention. Added as **Patterns
   P-08** (craft). Self-derivable from my own receipt (`:45-48`) — this is material I would have
   found on my own, counted separately from the relay per the dispatch's instruction.

3. **`plan.yaml` T-03 staleness, deliberately not raised** — ACCEPTED, reshaped to the general
   rule underneath the two stated grounds (domain + existing backlog row), dropping the specific
   file and row id. Added as **Patterns P-09** (craft). Also self-derivable from my own receipt
   (`:60-63`).

4. **Falsified "full read" claim (`gh_cost_log.py` opt-in rationale spelled twice, missed by my
   check 2)** — ACCEPTED as-is; this is the highest-value entry of the four because it names a
   failure mode I could not see from my own receipt alone (the lead's probe, not mine). Added as
   **Gotchas G-06** (craft): a "full read" claim needs a targeted duplication probe, not just a
   linear pass, before it can back a zero finding.

## One additional self-derived entry, not in the relay

From my own receipt item 8 (log-integrity confirmation, `:49-50` and `:69-75`): I asserted
"no writes" for a read-only dispatch and backed it with a byte-count comparison before/after,
rather than resting on the assertion alone. Generalized and added as **Patterns P-07** (craft):
an unfalsifiable "no side effects" claim should carry a before/after hash or size comparison.

## Ops applied

```yaml
expertise_update:
  - op: add
    section: Patterns
    entry: "P-07: WHEN a dispatch requires zero side effects DO capture size/hash of any touched log or state file before and after and report both — an assertion of \"no writes\" is unfalsifiable without a before/after comparison."
    why: "self-derived from receipt item 8 (log byte-count check backing a read-only claim)"
  - op: add
    section: Patterns
    entry: "P-08: WHEN a diff adds an import or naming pattern that looks like new complexity DO grep the file for its own established precedent before flagging it — reuse of an existing in-file convention is not new complexity."
    why: "self-derived from receipt (_re_station reuse check), relayed candidate 2, reshaped to drop file-specific example"
  - op: add
    section: Patterns
    entry: "P-09: WHEN a candidate finding lives outside your domain and a backlog row already tracks it DO decline to re-raise it as new — verify the row still matches current state, but do not duplicate the record."
    why: "self-derived from receipt (plan.yaml/B-5 dedup), relayed candidate 3, reshaped to drop the file/row identifiers"
  - op: add
    section: Gotchas
    entry: "G-06: WHEN claiming a \"full read\" of a file as your check DO also run a targeted probe for the failure mode under review (e.g. grep a stated rationale across the file for duplication) — a linear read can miss content that repeats without registering as a repeat."
    why: "relayed candidate 4 (lead's withheld-duplication probe falsified my own full-read claim); not visible from my receipt alone"
```

Candidate 1 (enumerate-a-zero) received no op — rejected as a duplicate of existing P-04.

## Section counts — before / after

Craft (`.harness/expertise/harness-data-engineer.md`, cap 150 lines, 43 → 55 lines):
- Patterns: 6 → 9
- Gotchas: 5 → 6
- Outcomes: 0 → 0
- Open: 0 → 0

Repository (`.harness/harness/expertise/harness-data-engineer.md`, cap 40 lines, 13 → 13 lines):
- Patterns: 0 → 0
- Gotchas: 1 → 1
- Outcomes: 0 → 0
- Open: 0 → 0

No repository-tier op — all four relayed candidates and the one self-derived candidate are true of
review technique in general, not of this checkout specifically. `gh_cost_log.py` and `plan.yaml`
appear only as examples the reshaping deliberately stripped.

## Gate

`.claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-data-engineer.md` → `OK`
`.claude/skills/harness/bin/check-expertise.sh .harness/harness/expertise/harness-data-engineer.md` → `OK` (unchanged file, re-run for completeness)

## Open questions

None raised. No harness defect observed this pass.
