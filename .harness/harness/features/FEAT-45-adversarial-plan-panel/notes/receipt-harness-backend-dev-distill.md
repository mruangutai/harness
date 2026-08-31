# Receipt — harness-backend-dev — distill — FEAT-45-adversarial-plan-panel

BLUF: applied 3 ops (2 craft, 1 repository), all self-derived from my own two SIMPLIFY-cycle
receipts (REUSE, SIMPLIFICATION angles). No observation log existed for this agent this feature
(confirmed absent). Accepted all 3 lead-relayed candidates (C1/C2/C3) — they are exactly the
findings already in my own receipts, correctly relayed. No displacement needed; both tiers had
room in every section touched.

## Material read

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/receipt-harness-backend-dev-simplify-reuse.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/receipt-harness-backend-dev-simplify-simplification.md`
- `notes/handoff-build.md`, `notes/ship-review-2026-08-31.md` (cross-cutting skim)
- `notes/review-harness-code-reviewer-c0..c4.md`, `notes/review-harness-qa-c0..c4.md` — checked
  whether any reviewer/QA finding landed on backend-dev's own build-phase work. Confirmed from
  `plan.yaml` that `panel_findings.py`/`check-state.sh`/`test-panel-findings.py` (T-09) were all
  `execution_agent: harness-dev-ops`, not backend-dev — the M1 fail-open severity finding and B-1
  width finding are dev-ops's code, not mine. No reviewer/QA finding attaches to backend-dev's
  build work this feature. Nothing additional to distill from those files.

## Candidate adjudication

**C1 (decisions-list measurement misclassified as a decision)** — ACCEPT, but re-tiered to
**repository**, not craft. The finding turns on this repo's `plan.yaml` `decisions:` schema
(`dec: none` field, adjacent `lanes:` methodology block) — not a rule true of an unseen repo.
Applied to the repository file as O-01.

**C2 (repetition across independent consumer types is load-bearing, not drift)** — ACCEPT as
craft. The judgment principle (check whether one mechanism could span all consumer types before
calling repetition drift) generalizes to any codebase mixing LLM prompts, agent config, and
enforcement code — true in a repo I've never seen. Applied as O-08.

**C3 (duplicated test scaffolding from "match this file's shape exactly")** — ACCEPT as craft.
General reuse-audit technique, not repo-specific. Applied as O-07.

No additional self-derived candidates beyond C1–C3: my two receipts' findings are exhaustively
C1–C3 (reuse Finding 1 = C3; simplification Finding 1 = C1; simplification's "defended
non-findings" section = C2). Every other item in both receipts was an explicit non-finding
(T-07/T-08 split correct, T-09/T-10 shared-file correct, T-03/T-04 split correct, D-12 keep,
SC-04/SC-07 and SC-02/SC-14 distinct, no dead references) — none of those pass the "would this
change what I do six spawns from now" test as a standalone rule; they are case-specific
adjudications, not durable techniques.

None judged stale at HEAD d7f31bb — all three describe durable audit techniques/repo facts, not
feature-specific state.

## Ops applied (verbatim)

Craft (`.harness/expertise/harness-backend-dev.md`):
```
op: add, section: Outcomes, id: O-07
entry: "WHEN a new file is instructed to match an existing file's shape exactly DO import shared
scaffolding (path/env resolution, counters) rather than reproduce it line-for-line — two
duplicated copies need lockstep edits, and the newer, less-visited file is the one an editor
forgets to update."

op: add, section: Outcomes, id: O-08
entry: "WHEN the same rule is restated across genuinely independent consumer types (an LLM
prompt, an agent definition, an enforcement script, a decision log) DO check whether any single
mechanism could span all of them before calling it drift — no shared-constant span means the
repetition is load-bearing, not duplication."
```

Repository (`.harness/harness/expertise/harness-backend-dev.md`):
```
op: add, section: Outcomes, id: O-01
entry: "WHEN reviewing this repo's plan decisions list for simplification DO flag an entry
marked dec: none whose body only restates an adjacent block's already-stated methodology — it
inflates the decision count with an audit record nobody chose, not a real decision."
```

Applied via `expertise-merge.py apply` (markdown-shaped `--entries` file — the DIGEST op schema
in `harness-distill` describes the report format, not the tool's input format, which is
Expertise-markdown for a union merge). Both runs exit 0, no conflicts, no cap breaches.

## Per-section counts

Craft (`.harness/expertise/harness-backend-dev.md`, 150-line budget, 43 lines after):
| Section | Before | After |
|---|---|---|
| Patterns | 15 | 15 |
| Gotchas | 15 | 15 |
| Outcomes | 6 | 8 |
| Open | 0 | 0 |

Repository (`.harness/harness/expertise/harness-backend-dev.md`, 40-line budget, 12 lines after):
| Section | Before | After |
|---|---|---|
| Patterns | 1 | 1 |
| Gotchas | 5 | 5 |
| Outcomes | 0 | 1 |
| Open | 0 | 0 |

No displacement occurred; no section was at cap when I wrote.

## Verification

Neither `check-expertise.sh` nor any formatter/linter/test suite run, per dispatch constraints.
`git status --porcelain` shows only the two Expertise files and this receipt changed (checked
via the merge tool's own PRESERVED/ADDED output, not a whole-file diff).
