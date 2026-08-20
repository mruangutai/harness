# ALTITUDE receipt — FEAT-26 plan draft (base ada8e99)

## Read

- `plan.yaml` (686 lines, full) — all eight D-entries, all eight tasks' intents and verifies.
- `BRIEF.md` (127 lines, full).
- `.claude/skills/harness-simplify/SKILL.md` `## ALTITUDE` section, as charter.
- Confirmed by grep that `.claude/skills/harness/SKILL.md` carries none of `record-pr`,
  `gh-sync.py closes`, `source_issues` yet — the plan surface is pre-execution, as expected.

## Checked for

1. T-03's dual wiring of `_record_pr` (into `cmd_ship` and into a new `record-pr` subcommand) —
   is the capability at the right home, or bolted onto a caller?
2. T-02 threading `source_issues` through `load_recorded`/`save_recorded`/`cmd_open` — right home?
3. Where the `source_issues` rule lives authoritatively: schema description (T-01), mirror
   behaviour (T-02 intent), renderer (T-04 intent), template comment + SKILL.md row (T-07),
   DEC-197 (T-08).
4. T-02 item 3's orphaned-milestone residual and T-06's four operator-confirmed-number residual —
   accepted with a named compensating control, or accepted bare.
5. D-01..D-08 for restatement or a choice nothing in the plan depends on.

## Finding 1 — T-06's four operator-confirmed numbers, no compensating control named

`plan.yaml:542-558` (T-06 intent). Compare `plan.yaml:216-224` (T-02 item 3), which explicitly
names its compensating control for the accepted residual: "the existing 422 title-lookup recovery
in cmd_open resolves it on the next run once the file exists." T-06's residual — four PR numbers
that derivation cannot produce, confirmed instead by the operator reading merged-PR titles by
hand — names no equivalent control. The only downstream check is the task's own `verify` block
(`plan.yaml:496-524`), which asserts `feature.json`'s `pr` equals the same hardcoded table the
intent itself supplies — a check against itself, not against an independent source.

**Cost:** if one of the four confirmed numbers is wrong (transposed digit, wrong title match on a
branch that in fact carries other PRs too), the write still succeeds, `verify` still passes
(it's checking against the same wrong number), and INV-28 (T-05) goes permanently silent for that
feature because `pr` is now a real int. Nothing in the plan re-derives or spot-checks these four
against GitHub itself. The seven derived numbers get that protection for free (`gh pr list ...
--state merged` is the source of truth they're written from); the four hand-attributed ones don't.

**Alternative:** T-06's intent adds one independent check before each of the four `--pr` runs:
`gh pr view <n> --repo <repo> --json headRefName,title` and confirm the returned `headRefName`
matches the feature's recorded branch and the title matches the string the intent already names
(e.g. PR 4 is "Replace GSD with the harness (foundation)"). Paste that output into the T-06
receipt. This is the same shape of control T-02 already accepted for its own residual — cheap,
and it turns "operator remembers correctly" into "operator's memory is checked against GitHub
before the write."

**fold-in**

## Judgment — where the source_issues rule lives (no finding, answering the posed question)

The schema description (T-01, `plan.yaml:129-136`) is the authoritative *technical* statement —
machine-validated, always present at runtime, and it names both writer (`gh-sync.py open`) and
reader (`gh-sync.py`'s `closes`). DEC-197 (T-08) is explicitly scoped by its own intent
(`plan.yaml:685`, "Do not restate the implementation. Carry the rule and one clause of why, as
DEC-158 requires.") to carry *why*, not mechanism — so it cannot drift against the schema
description because it isn't trying to restate it. The template comment and SKILL.md row (T-07)
are human-facing pointers for the two authors (pm at plan time, operator at ship time) who will
never open `feature-schema.json`. This is layering by audience, not four competing authorities —
the plan's own DEC-158 citation is what keeps DEC-197 from becoming a fifth restatement.
**leave.**

## Judgment — T-03 dual wiring, T-02 threading (no finding)

`_record_pr` lives once, in `gh-sync.py`, called from two sites (`cmd_ship`, `record-pr`
subcommand) — this is one implementation with two entry points, not a capability bolted onto a
caller; T-07's SKILL.md row (`plan.yaml:598-601`) even says explicitly that `ship` runs it too "so
the ordinary flow needs no separate call," which forecloses the redundant-restatement risk. T-02's
threading through `load_recorded`/`save_recorded`/`cmd_open` extends the same mapping-rebuild
pattern those functions already use for `milestone`/`parent`/`attached`/`issues` — right home,
consistent with the existing module contract. **leave** on both.

## D-01..D-08

No entry restates another; each is cited by at least one task (`T-02`↔D-03/D-08, `T-03`↔D-01/D-02,
`T-05`↔D-06, `T-06`↔D-05, `T-02` item 3↔D-07, `T-04`↔D-04). No residual finding here.

## OUT-OF-CHARTER (not an altitude finding — flagging per charter instruction only)

D-06 (`plan.yaml:81-85`) cites `dec: DEC-138` for "the new invariant is warn level," but the
`because` clause attributes the precedent to INV-21's own recorded reason, not to DEC-138's
content. Whether DEC-138 is the correct citation for this specific choice is a factual question
for the review panel, not an altitude question.

```yaml
VERDICT: PASS
DIGEST:
  headline: "one altitude finding — T-06's four hand-confirmed PR numbers accept a residual without T-02's residual's compensating-control discipline; everything else checked (T-03 dual wiring, T-02 threading, source_issues authority layering, D-01..D-08) is at the right depth"
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-ai-dev-2026-08-18-2-altitude.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-26-pr-linkage-recorded/notes/receipt-harness-ai-dev-2026-08-18-2-altitude.md
```
