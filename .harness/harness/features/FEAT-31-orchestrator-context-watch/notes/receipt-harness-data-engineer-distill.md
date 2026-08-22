# Distillation receipt — harness-data-engineer — FEAT-31

**BLUF:** 2 entries accepted, both from the lead-relayed candidates (A and B) — my own receipt
supplied the material but produced no wording distinct enough to add beyond those two. No stale
entries found; no repository-tier changes.

## Material considered

- My own receipt: `notes/receipt-harness-data-engineer-simplify-efficiency.md` — the source
  measurement both relayed candidates describe.
- Candidate A (baseline-relative cost measurement) and Candidate B (file the cost even when the
  remedy is unwritable, naming what is not being re-opened) — both relayed in the dispatch.

## Accepted (2, both craft-tier)

- **P-10 (new)** — from Candidate A: `WHEN measuring a per-invocation cost DO baseline it
  against the empty operation and state the population that pays it — the same raw number reads
  as fixed overhead or a real regression depending on what it is measured against.` Passes the
  craft test: true and useful in any repository, no path/decision token.
- **P-11 (new)** — from Candidate B: `WHEN a finding's remedy touches a file outside your write
  scope DO still file the cost as a flag-only question, naming the prior signed decision you are
  explicitly not re-opening — that framing lets it route as a question, not a challenge.` Same
  test passed: generalizes past this repo's DEC-174 specifics (the entry itself names no
  decision id).

Neither displaced an existing entry — both sections were under cap (Patterns 9/15 before,
11/15 after; Gotchas untouched at 6/15).

**Correction on the merge tool's input format:** `expertise-merge.py apply --entries <file>`
parses the entries file with the same Expertise-markdown grammar as the target file (`##
Section` headers, `- P-NN: text` lines) — it does not accept the YAML `expertise_update:` ops
block from the digest schema as literal input. A first attempt using that YAML shape as the
`--entries` file was silently accepted (exit 0) but matched no `ENTRY_RE` pattern, so both
proposed entries were dropped and the tool reported only `PRESERVED` for the 15 existing ids —
no `ADDED` line, no error. Re-ran with the entries file in Expertise-markdown form (`##
Patterns (max 15)` header plus the two `- P-10:`/`- P-11:` lines); that run printed `ADDED P-10`,
`ADDED P-11` before the `PRESERVED` lines, confirming the write. The YAML block stays the
correct shape for the DIGEST's own `expertise_update:` field — it is a different artifact from
the file handed to `--entries`.

## Rejected

None. Both relayed candidates were accepted as-is; my own receipt's other observations (the
negligible-cost measurements in checks 1-2, the tail-read design note in check 3) restate
existing P-01/P-04 rather than adding new ground, so nothing further was drafted from it.

## Stale-entry check

Read the current craft file (`.harness/expertise/harness-data-engineer.md`, in context via the
spawn hook) against this feature's findings. No entry was falsified or made stale:
- P-01 (state cost in matching unit) — reinforced, not contradicted, by this feature's own
  measurements (checks 1-2 of my receipt did exactly this).
- G-01 through G-06 — none concern cost-measurement methodology or flag-only filing; no overlap
  to re-measure.
Also checked the repository-tier file (`.harness/harness/expertise/harness-data-engineer.md`,
1 gotcha about `inject-expertise.sh` sort ordering) — unrelated to this feature's surface
(`.claude/settings.json`, `context-watch-hook.py`), not touched.

## Worktree staleness guard

`diff` between this worktree's `.harness/expertise/harness-data-engineer.md` and the main
checkout's copy (`/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-data-engineer.md`)
before applying: **empty** — the two were identical, so applying carried no risk of reverting
another feature's entries.

## Section counts

`.harness/expertise/harness-data-engineer.md` (craft):
- Patterns: 9 before → 11 after
- Gotchas: 6 before → 6 after
- Outcomes: 0 before → 0 after
- Open: 0 before → 0 after

Repository-tier file: untouched, 0 changes.

## Accepted-entry counts by source

- From own receipt (net-new wording): 0
- From relayed Candidate A: 1 (P-10)
- From relayed Candidate B: 1 (P-11)

## check-expertise.sh result (verbatim, full directory)

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

`harness-data-engineer.md` reports clean (`OK`, no advisory). The advisories present are all in
other personas' files — not fixed here, reported only.
</content>
