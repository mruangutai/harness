# Receipt — harness-backend-dev — FEAT-31 distillation

## BLUF

Applied 2 merges + 2 replacements + 2 drops + 2 adds to the craft file
(`.harness/expertise/harness-backend-dev.md`), and 1 add to the repository-tier file
(`.harness/harness/expertise/harness-backend-dev.md`). Both sections that were at cap (Patterns,
Gotchas — 15/15 each) stayed at cap: each new entry displaced room freed by merging two existing
entries that shared a root cause, never a bare append over cap. `check-expertise.sh` is clean on
both my files (one pre-existing, unrelated ADVISORY on G-08, not introduced this run).

## Tool-shape correction, recorded because it cost real work

`expertise-merge.py apply` is **pure union-add with conflict detection** — it has no `replace` or
`drop` verb at the tool level; the ops schema in `harness-distill/SKILL.md` (`add|replace|merge|drop`)
describes what to *report*, not a tool argument. My first attempt (a YAML file of ops) applied
nothing silently (0 adds, all PRESERVED) because the parser only understands Expertise markdown
(`## Section` + `- ID: text`), not YAML. Per the skill's own exit-7 semantics ("the same entry id
carries different text — a real conflict — resolve it yourself"), replace/drop is done by hand-editing
the specific line via `Edit` (never a whole-file `Write`), then the tool is used only for pure `add`s
under the now-freed cap headroom. Confirmed no drift against main's copy of both files before touching
either (`diff` exit 0, both files).

## Section counts, before → after

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 |
| craft | Gotchas | 15/15 | 15/15 |
| craft | Outcomes | 3/10 | 3/10 |
| craft | Open | 0/5 | 0/5 |
| repository | Patterns | 0/15 | 0/15 |
| repository | Gotchas | 2/15 | 3/15 |
| repository | Outcomes | 0/10 | 0/10 |
| repository | Open | 0/5 | 0/5 |

## Ops applied

1. **replace P-05** (craft, Patterns) — broadened "never assert `fixture == result`" to cover any
   self-referential oracle, including an independent verifier importing the tool's own helper.
   Source: my own T-13 observation (SC-01 second-opinion script must not import `context-watch.py`'s
   own `entry_context_size`/`_three_field_sum`) folded into the existing P-05 principle.
2. **replace P-09 / drop P-13** (craft, Patterns) — merged two hash-restore-reverify entries (mutation
   loop and RED-reconstruction) into one, since both used the identical restore-and-reverify
   mechanism for two different triggers. Frees one Patterns slot.
3. **add P-16** (craft, Patterns) — Candidate B: "reuse the correct site rather than patching the
   reimplementation." Uses the slot freed by (2).
4. **replace G-10 / drop G-15** (craft, Gotchas) — merged two under-modeled-test-double entries
   (argv-text-only, payload-shape-only) into one covering both dimensions. Frees one Gotchas slot.
5. **add G-17** (craft, Gotchas) — Candidate A: fixtures sharing the code's own wrong mental model
   need a paired wrong-shaped-fixture-must-yield-zero assertion, not just a correct-shaped one.
   Uses the slot freed by (4).
6. **add G-03** (repository, Gotchas) — my own T-01 observation: the bash-write-guard blocks `>`
   redirection even to the session scratchpad, not just repo paths; use a `python3 -` heredoc
   instead. This is specific to this repo's guard, hence repository tier.

## Accepted-entry counts by source

- From my own observations log / own receipts: **2** (P-05's broadening via the T-13 independent-
  oracle observation; G-03, the bash-write-guard workaround).
- From the 3 relayed candidates: **2** (Candidate A → G-17; Candidate B → P-16).
- Rejected relayed candidates: **1** (Candidate C).

## Rejections

- **Candidate C (order-property needs order-assertion)** — REJECTED. Its core claim ("assert the
  exact property under test, not a weaker co-occurrence/substring proxy") is already covered by the
  combination of existing P-01 (exact-value assertion over weak existence/type checks) and G-11
  (confirm which channel/stream a message actually reaches before asserting against it). P-01 is
  already at the 50-word entry cap, so folding order/precedence language in would either blow the
  cap or dilute its sharper, already-tight existing wording. With both Patterns and Gotchas at their
  15-entry section cap and no further mergeable pair identified without losing distinct content, I
  judged Candidate C weaker than the two accepted candidates and let it die per the skill's own rule
  ("nothing weaker, it dies").
- Also considered and left out (own log, not strong enough to clear the six-spawns-from-now bar
  given no free slot): T-01's `run-unit-tests.sh --kind unit` exit-1-from-an-unrelated-fixture
  observation (adjacent to existing G-04, not sufficiently distinct); T-08's grep-prefix-collision
  observation (too narrow/single-incident to generalize past what P-08/P-12 already cover).

## Stale-entry check

Read the full injected Expertise (craft + repository tier) at spawn. No existing entry was falsified
by this feature. Two entries were re-measured and reinforced rather than contradicted: G-09
(worktree vs stale main-checkout `__file__`) — fix3-eng's Q3 (a stray `state.yaml` written into the
main checkout by mistake) is a live instance of exactly the risk G-09 already names, not a
counter-example. P-06 (stop on a green pre-edit RED) — fix1-eng's Q-IRONLAW is a *different* failure
mode (code fixed before tests were written at all, not a RED run that came back green on an untouched
tree), so it does not contradict P-06; it is the trigger P-13 used to cover, now folded into P-09.
No `drop`/`replace` was needed on stale-entry grounds alone.

## check-expertise.sh result (verbatim, whole directory)

```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
ADVISORY .harness/expertise/harness-backend-dev.md:25: G-08 names 'team-config' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:20: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
ADVISORY .harness/expertise/harness-orchestrator.md:29: G-11 names '.claude/' — repository-layer candidate; rule on it (issue 340)
ADVISORY .harness/expertise/harness-orchestrator.md:29: G-11 names 'check-domain.sh' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-pm.md
ADVISORY .harness/expertise/harness-pm.md:4: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:66: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
EXIT=0
```

My file (`harness-backend-dev.md`) is `OK` (exit 0); the one ADVISORY it carries (G-08, `team-config`)
is a pre-existing entry from before this distillation, not introduced by any op above — advisory, not
a violation, left for a human to rule on per the skill's own text. All other ADVISORY lines are in
files outside my domain (`harness-dev-ops.md`, `harness-orchestrator.md`, `harness-pm.md`,
`harness-security-reviewer.md`) — reported here, not fixed, since I do not own those files.
