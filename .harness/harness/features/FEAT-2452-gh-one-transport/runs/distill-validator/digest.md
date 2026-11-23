# Distill — FEAT-2452 — validator squad — distill-validator

**PASS.** The validator squad applied 8 Expertise ops across 3 batches. There was no suite run, no review and no git write.

## harness-qa (artifact `notes/qa-distill-validator.md`)
- **Craft** (`.harness/expertise/harness-qa.md`), batch `cadafcca…`. Counts: P 15→15, G 15→15, O 10→10, Open 1→1. The batch replaced P-05, P-07, P-12 and G-02.
- **Repository harness** (`.harness/harness/expertise/harness-qa.md`), batch `e5c6abca…`. Counts: P 0→0, G 11→13, O 0→0, Open 0→0. The batch replaced G-06 and added G-12 and G-13.
- Receipt: `notes/expertise-receipt-700924d9….json`. I read both resulting files, and every op is present as reported.

## Relayed candidates (3, all sourced)
- LC-1: CI's checks job runs a canonical-reader audit that the validate QA matrix omits. Sources: `notes/answers-2026-11-23-inventory.md`, `backlog-issues.json`, `observations/harness-orchestrator.md`. QA applied it as craft G-02.
- LC-2: the fix validated the container but not the decision field. Source: run 6 M1. QA merged it with LC-3 into craft P-05.
- LC-3: the identity of related records was discarded. Source: run 7 R1 and its coverage gap. QA merged it into craft P-05.

## Lead's own
- **Craft P-12 replaced** with batch `441b42e0…`. The new entry says that a must-fix against an input class names every axis the decision consumes. Evidence: across runs 5, 6 and 7, each round found the next axis of the same class (container, then field, then identity), and the last one arrived after the budget was spent. It displaced the old pin-range rule, because pinning belongs to the orchestrator. Counts: P 15→15, G 15→15, O 10→10, Open 0→0.
- The CI-parity lesson is already covered by my own G-03, so I added no lead op for it.

## Advisory
- QA's craft Q-01 is still open: the write-guard behaviour toward scratch writes is unclear. The new repository G-13 (variable-target redirects are blocked) probably isolates the cause, and QA's next curation could close Q-01.
- QA's craft Patterns list now ends with P-06, out of order. This is cosmetic.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/distill-validator/digest.md
DIGEST:
  headline: 'Validator distill PASS: 8 ops in 3 batches. All three relayed candidates
    landed in QA''s Expertise (LC-1 as craft G-02; LC-2 and LC-3 merged into craft
    P-05). The lead replaced its own craft P-12. Every section stayed at or under
    its cap.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/distill-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/qa-distill-validator.md
  expertise_update:
  - persona: harness-validator-lead
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN ruling a must-fix against a class of unusable input DO name every\
      \ axis the decision consumes \u2014 container shape, each read field's type\
      \ and domain, and related records' identity \u2014 a remedy scoped to the observed\
      \ instance leaves the adjacent axis for the next round, and rounds are budgeted."
    why: 'Three consecutive validate rounds each surfaced the next axis of one input
      class (container, then field, then identity) after remedies scoped to the instance
      seen; the last arrived with the rework budget spent and forced an escalation.
      Displaces P-12: pinning is the orchestrator''s act, not this seat''s.'
  - persona: harness-qa
    op: replace
    target: P-05
    section: Patterns
    entry: "WHEN a fix claims to reject malformed or foreign input DO probe each field\
      \ the downstream decision reads (missing, wrong type, out-of-domain) plus an\
      \ identity case (a related record from another scope) \u2014 container-shape\
      \ tests reach neither a bad field value nor a shape-valid record with the wrong\
      \ identity."
    why: 'LC-2+LC-3: two consecutive validate rounds missed field-level and identity
      classes after QA closed the container shape; displaces P-05, a dev design choice
      rather than a QA test action'
  - persona: harness-qa
    op: replace
    target: P-07
    section: Patterns
    entry: "WHEN fail-first needs a pre-fix red and source edits are refused DO load\
      \ the old blob (`git show <sha>:<path>`) into a fresh in-process module, or\
      \ check the new tests into a pin at the old SHA \u2014 either reproduces the\
      \ builder's reds without touching the reviewed tree."
    why: 'observed: both methods reproduced builder red counts exactly across two
      cycles; displaces P-07, a narrow lock-release fixture rule'
  - persona: harness-qa
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN a fake or recorder stands in for a call DO assert both the recorded\
      \ event and its selector arguments at each call site \u2014 an unasserted recorder\
      \ stays green when the call is dropped, and an argument-blind fake stays green\
      \ when a requested field is dropped."
    why: 'observed: a recorder lambda never asserted was blind to its call being dropped;
      same rule family as P-12, sharpened at equal length'
  - persona: harness-qa
    op: replace
    target: G-02
    section: Gotchas
    entry: "WHEN the repository's CI runs gates the QA matrix omits (audits, route\
      \ checks) DO enumerate CI's required steps and run or name each omitted one\
      \ at the reviewed tip \u2014 a green matrix is not CI-green, and drift only\
      \ those gates catch ships past repeated matrix_ok rounds."
    why: 'LC-1: a canonical-reader audit exited 2 at the reviewed tip after three
      matrix_ok rounds; displaces G-02, a ship-gate concern outside QA''s seat'
  - persona: harness-qa
    op: replace
    target: G-06
    section: Gotchas
    entry: "WHEN a perturbation proof must mutate code under .claude/skills/** DO\
      \ mutate in memory (monkeypatch the in-process module; route reached-markers\
      \ to sys.__stderr__, since redirect_stdout swallows print) \u2014 check-domain\
      \ refuses QA source edits even inside a managed pin, and bash-write-guard denies\
      \ ad hoc scratch copies."
    why: 'observed this run: check-domain refused source perturbation inside QA''s
      own managed pin, superseding G-06''s worktree-copy advice'
  - persona: harness-qa
    op: add
    target: G-12
    section: Gotchas
    entry: "WHEN running the integration kind in a fresh managed pin DO run `bun install\
      \ --frozen-lockfile` in the pin first \u2014 the pin has no node_modules, so\
      \ tests/integration/test-typescript-typecheck.py reds on missing tsc, a false\
      \ environment failure."
    why: 'observed: fresh pin reds integration until install; would otherwise be misgraded
      as a regression'
  - persona: harness-qa
    op: add
    target: G-13
    section: Gotchas
    entry: "WHEN redirecting output under bash-write-guard DO use a literal absolute\
      \ target path \u2014 a redirect whose target contains a shell variable (e.g.\
      \ `> mut-$m.txt`) is blocked even under /tmp; pipe to grep inside mutant loops\
      \ instead."
    why: 'observed: variable-target redirects blocked while literal /tmp paths pass;
      recurs in every mutant loop'
  team: distill
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: "QA applied 7 ops. Craft batch cadafcca: 4 replaces, with every section\
      \ count unchanged (P15 G15 O10 Open1). Repository harness batch e5c6abca: 1\
      \ replace and 2 adds, G 11\u219213. LC-1..LC-3 were all applied."
    files_touched:
    - .harness/expertise/harness-qa.md
    - .harness/harness/expertise/harness-qa.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "Counts before and after. QA craft: P 15\u219215, G 15\u219215, O 10\u219210,\
    \ Open 1\u21921. QA repository (harness): P 0\u21920, G 11\u219213, O 0\u2192\
    0, Open 0\u21920. Lead craft: P 15\u219215, G 15\u219215, O 10\u219210, Open 0\u2192\
    0 (batch 441b42e0). Lead repository: no ops, unchanged at P 2, G 4."
  - "The lead read QA's receipts (notes/qa-distill-validator.md and expertise-receipt-700924d9\u2026\
    .json) and both resulting QA files. Every reported op is present in the files."
  - I confirmed the LC-1 premise against notes/answers-2026-11-23-inventory.md (the
    audit exited 2 at the tip and 0 at base), backlog-issues.json, and the orchestrator
    observations. I added no lead op for it, because lead craft G-03 already covers
    CI-lock completeness.
  - Two advisory notes for QA's next curation. QA's craft Q-01, about unclear write-guard
    scratch behaviour, is probably isolated by the new repository G-13. QA's craft
    Patterns list now ends with P-06, out of order, which is cosmetic.
  - harness-pm (goalcheck) was not dispatched, because it already distilled under
    distill-product. No git writes were made.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers:
  - reader: distill-qa
    status: ran
    persona: harness-qa
    reason: none
```
