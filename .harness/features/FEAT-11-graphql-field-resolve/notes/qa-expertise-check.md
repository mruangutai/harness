# QA relay — Expertise format gate (FEAT-11, distill-validator)

Verification-only. No files under `.harness/expertise/` were edited. No commits made.

## Verbatim gate output

Command: `.claude/skills/harness/bin/check-expertise.sh .harness/expertise/`

```
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
FAIL .harness/expertise/harness-documentor.md
  - line 43: G-04 is 53 words — cap is 50; a rule, not a story
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

Exit code: `1`

## Per-file counted entries (Patterns / Gotchas / Outcomes / Open) and line count

Counted with `awk` isolating each `## <Section>` block and `grep -c '^- '` for entry bullets.
`wc -l` for line count.

| File | Lines | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|---|
| harness-backend-dev.md | 64 | 11 | 8 | 0 | 0 |
| harness-code-reviewer.md | 24 | 13 | 2 | 0 | 0 |
| harness-dev-ops.md | 17 | 3 | 5 | 0 | 0 |
| harness-documentor.md | 79 | 10 | 14 | 0 | 0 |
| harness-eng-lead.md | 49 | 10 | 3 | 0 | 0 |
| harness-orchestrator.md | 127 | 15 | 15 | 7 | 1 |
| harness-pm.md | 78 | 14 | 8 | 0 | 0 |
| harness-product-lead.md | 51 | 9 | 3 | 2 | 0 |
| harness-qa.md | 55 | 9 | 4 | 2 | 0 |
| harness-security-reviewer.md | 63 | 8 | 5 | 0 | 0 |
| harness-ui-reviewer.md | 16 | 6 | 0 | 1 | 0 |
| harness-validator-lead.md | 43 | 7 | 3 | 0 | 1 |
| harness-visual-designer.md | 21 | 4 | 0 | 0 | 0 |

No file is close to the 150-line spawn-hook truncation budget; `harness-orchestrator.md` at 127
lines is the nearest.

## Comparison against validator-lead's stated BEFORE counts

BEFORE counts given in the dispatch (Patterns/Gotchas/Outcomes/Open):
`harness-qa` 7/3/2/0, `harness-code-reviewer` 10/2/0/0, `harness-security-reviewer` 6/5/0/0,
`harness-ui-reviewer` 6/0/1/0, `harness-validator-lead` 7/3/0/1.

Counted AFTER (this run), same order:

| File | BEFORE (validator-lead) | AFTER (counted here) | Changed? |
|---|---|---|---|
| harness-qa | 7/3/2/0 | 9/4/2/0 | yes — Patterns +2, Gotchas +1 |
| harness-code-reviewer | 10/2/0/0 | 13/2/0/0 | yes — Patterns +3 |
| harness-security-reviewer | 6/5/0/0 | 8/5/0/0 | yes — Patterns +2 |
| harness-ui-reviewer | 6/0/1/0 | 6/0/1/0 | no change |
| harness-validator-lead | 7/3/0/1 | 7/3/0/1 | no change |

`harness-ui-reviewer` and `harness-validator-lead` show **no delta** from the stated BEFORE —
if either member reported a distillation landing that changed their own counts, that self-report
disagrees with what is counted in the tree right now. `harness-qa`, `harness-code-reviewer`, and
`harness-security-reviewer` all counted higher than BEFORE, consistent with a landed distillation.
I hold no record of the four members' own claimed AFTER numbers, only validator-lead's BEFORE
figures, so I cannot confirm or refute the self-reports directly — only report what the files
contain right now.

## Gate result

`check-expertise.sh` exits 1 (FAIL) because `harness-documentor.md` line 43 (Gotcha G-04) is 53
words against a 50-word cap. This is not an author I hold write access to — no `harness-qa`
Expertise action is implied, but the overall gate did not pass clean.

---

## FINAL run — after the second distillation round (validator-lead dispatch)

Verification-only, as before. No files under `.harness/expertise/` edited. No commits made.

### 1. Verbatim gate output

Command: `.claude/skills/harness/bin/check-expertise.sh .harness/expertise/`

```
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
FAIL .harness/expertise/harness-documentor.md
  - line 43: G-04 is 53 words — cap is 50; a rule, not a story
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

Exit code: `1`. Unchanged from the earlier check — `harness-documentor.md` is still the sole
failure, same line, same violation. I did not edit it (product squad's file, not mine).

### 2. Counted per-section entries + line count, the five named files

Counted by reading each file directly and counting `- P-`/`- G-`/`- O-`/`- OQ-` bullets under each
`## <Section>` heading. `wc -l` for line count.

| File | Lines (`wc -l`) | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|---|
| `harness-qa.md` | 59 | 10 (P-01..P-10) | 4 (G-01..G-04) | 2 (O-01,O-02) | 0 |
| `harness-code-reviewer.md` | 25 | 14 (P-01..P-14) | 2 (G-01,G-02) | 0 | 0 |
| `harness-security-reviewer.md` | 67 | 9 (P-01..P-09) | 5 (G-01..G-05) | 0 | 0 |
| `harness-ui-reviewer.md` | 19 | 8 (P-01..P-08) | 1 (G-01) | 1 (O-01) | 0 |
| `harness-validator-lead.md` | 43 | 7 (P-01..P-07) | 3 (G-01..G-03) | 0 | 1 (OQ-01) |

### 3. `harness-documentor.md`

`wc -l` = **79 lines**. Still **fails** the gate: line 43, Gotcha G-04, 53 words against the
50-word cap (verbatim from the check-expertise.sh output above). Unedited — not my file to fix.

### 4. Comparison against the five self-reported AFTER counts in this dispatch

| File | Self-reported AFTER | Counted (this run) | Agreement |
|---|---|---|---|
| `harness-qa.md` | 10/4/2/0 | 10/4/2/0 | **match** |
| `harness-code-reviewer.md` | 14/2/0/0 | 14/2/0/0 | **match** |
| `harness-security-reviewer.md` | 9/5/0/0 | 9/5/0/0 | **match** |
| `harness-ui-reviewer.md` | 8/1/1/0 | 8/1/1/0 | **match** |
| `harness-validator-lead.md` | 7/3/0/1 (expected unchanged) | 7/3/0/1 | **match, and unchanged as expected** |

No disagreements this round. (Contrast with my earlier, pre-second-round check, which measured
`harness-qa.md` at 9/4/2/0 with 55 lines — that reflects the state before the second distillation
landed; the current 10/4/2/0 at 59 lines is consistent with one more Pattern having landed since.)

### 5. Integrity check requested: `harness-code-reviewer.md` at "14 of 15"

Confirmed: **14 Patterns**, cap is 15 (`## Patterns (max 15)` heading) — one slot of headroom
remains, not over cap. Line count **25** — the shortest of the five files by a wide margin, and
nowhere near the 150-line spawn-hook truncation budget (125 lines of headroom).

### 6. Proximity to the 150-line spawn-hook truncation budget

None of the five named files is within 20 lines of 150:

| File | Lines | Headroom to 150 |
|---|---|---|
| `harness-qa.md` | 59 | 91 |
| `harness-code-reviewer.md` | 25 | 125 |
| `harness-security-reviewer.md` | 67 | 83 |
| `harness-ui-reviewer.md` | 19 | 131 |
| `harness-validator-lead.md` | 43 | 107 |

No flag needed on any of the five. (For context only, outside the requested set:
`harness-orchestrator.md` was 127 lines on the earlier full-directory scan — 23 lines of headroom,
not within-20 either, but the closest file in the whole directory to the cap. Not one of the five
gated here, noted for awareness only.)

### Final gate result

`check-expertise.sh` still exits **1 (FAIL)** — sole cause is `harness-documentor.md`'s G-04
word-cap violation (line 43, unchanged, not mine to fix — DEC-174/product-squad-owned file). All
five files this dispatch asked about are format-clean (`OK` in the gate output) and their counted
entry tallies **match every self-reported AFTER figure exactly**, with `harness-validator-lead.md`
correctly unchanged as expected. No count disagreement to report for the five in scope.
