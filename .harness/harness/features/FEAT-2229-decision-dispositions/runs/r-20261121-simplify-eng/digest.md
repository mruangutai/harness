# FEAT-2229 — four-angle plan simplify

**PASS: no blocking quality findings.** One optional wording fold-in to pm; one implementation briefing row; three leave decisions. Efficiency is explicitly empty. Four separate read-only readers completed; zero send-backs, no checks run, no draft/BRIEF/source edits.

Paths: `P` = `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml`; `W` = that assigned product worktree; receipts are beside `P` in `notes/`.

## Findings and lead routing

| ID / angle | File, line | Summary | Concrete cost | Alternative | Lead route |
|---|---|---|---|---|---|
| R-1 / reuse | P:184–200 | Reader proposes existing index reader and DEC-section slicer instead of potential duplicates. | Separate parsers could drift on STRUCK case or section content. | Reuse `check-plan-routes._decisions_index` and `gen-decisions-index.parse_decisions`, adapting them. | **Leave: proposed reuse is not interface-compatible.** Existing reader is fixed-root/case-sensitive; slicer strips fenced bytes and ends at next DEC heading, not every same-level heading. T-01 requires exact raw substring and segment authority. Plan does not mandate duplicate parsers; broadening another gate is unjustified. No change to settled exact-clause behavior. |
| S-1 / simplification | P:168–172,216–217,226–236 | Creation and mutation paragraphs repeat provenance invariants. | Reader must distinguish two related preservation statements. | Merge reservation prose/test lists without removing cases. | **Leave: settled panel fix remains intact.** Creation/ordinary-edit preservation and explicit caller-mutation refusal cover different failure modes; wording alone does not justify disturbing that distinction. |
| S-2 / simplification | P:347–348 | T-03 repeats reciprocal-link exclusion in adjacent sentences. | Two copies in one intent can drift; no runtime cost. | Merge the two exclusion sentences, retaining every unique exclusion and BRIEF's scope. | **Optional fold-in to pm**, no assertion or SC change. |
| A-1 / altitude | P:173–183 | Era resolver implementation home is unspecified. | A bespoke root walk could duplicate an existing manifest-probe invariant. | Use supplied product `--root` (preferred), or existing `plan_merge.guards._harness_root` if discovery is necessary; keep instant parsing local and cohesive. | **Briefing-row for T-01**, not a plan restriction or a new module requirement. |
| A-2 / altitude | P:277–286 | Author-facing prompt repeats mechanical authoring requirements. | Several prose owners must track future rule changes. | Pointer-only draft instruction to the checker. | **Leave:** alternative weakens SC-04/SC-07's point-of-use obligations and reopens already-settled prompt trims. |

Lead resolves reuse reader's nonblocking question: do not mandate the two incompatible helpers or change fenced-text semantics. No user question remains. Findings are distinct mechanisms; none needs deduplication. S-1/A-2 are recorded only to explain rejection, not re-raised to pm.

## Per-member receipts

- **reuse / harness-backend-dev / PASS:** one proposed reuse finding, lead leaves it; `notes/receipt-harness-backend-dev-r-20261121-simplify-eng.md`.
- **simplification / harness-data-engineer / PASS:** two wording findings; one optional fold-in, one leave; `notes/receipt-harness-data-engineer-r-20261121-simplify-eng.md`.
- **efficiency / harness-dev-ops / PASS:** zero findings; `notes/receipt-harness-dev-ops-r-20261121-simplify-eng.md`. Runtime estimates are inference, not measured results.
- **altitude / harness-ai-dev / PASS:** one briefing-row and one leave; `notes/receipt-harness-ai-dev-r-20261121-simplify-eng.md` (its F-1/F-2 correspond to A-1/A-2 above).

Adjudication evidence: `W/.claude/skills/harness/bin/check-plan-routes.py:2394–2407`, `gen-decisions-index.py:89–130`, and `plan_merge/guards.py:50–68`. These reads resolve helper compatibility and the briefing decision, not correctness certification. No test/matrix/UAT or ship-readiness claim. Open questions: none. Bookkeeping is `state.yaml`; reported work paths are only the four receipts and this digest. All plan changes, if any, remain pm-owned.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Four-angle flag-only pass complete: one optional pm wording fold-in,
    one implementation briefing row, no blocking findings; efficiency clean.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/notes/receipt-harness-backend-dev-r-20261121-simplify-eng.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/notes/receipt-harness-data-engineer-r-20261121-simplify-eng.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/notes/receipt-harness-dev-ops-r-20261121-simplify-eng.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/notes/receipt-harness-ai-dev-r-20261121-simplify-eng.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-simplify-eng/digest.md
  expertise_update: []
  team: simplify-eng
  steps_run: 4
  cycles_used: 0
  members:
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: One reuse proposal; lead leaves it because existing parser interfaces
      differ from required behavior.
    files_touched: []
  - step: simplification
    persona: harness-data-engineer
    verdict: PASS
    headline: Two low wording findings; one optional pm fold-in, one leave.
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: PASS
    headline: 'Efficiency angle clean: zero findings.'
    files_touched: []
  - step: altitude
    persona: harness-ai-dev
    verdict: PASS
    headline: 'Two low findings: one briefing row, one leave.'
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'FLAG-ONLY: no plan.yaml, BRIEF.md or code edits; no builds, tests, linters, formatters
    or smoke runs.'
  - Every reader finding retains angle, five-part shape and lead route in the artifact;
    no duplicate mechanisms required merging.
  - 'Reuse reader''s nonblocking question resolved: do not mandate incompatible helpers
    or alter settled raw-clause semantics.'
  - S-1 and A-2 are rejected/leave entries, not reopened settled panel findings. S-2
    is optional wording consolidation only.
  - 'Reader adjacency: backend command/writer reuse; data schema/serialization simplification;
    dev-ops gate/configuration efficiency; AI canonical-prompt altitude.'
  - Member files_touched remain as returned; lead work paths include receipts and
    digest per assignment, excluding state bookkeeping.
  - Efficiency runtime estimates are unmeasured inference. No correctness, test-matrix
    or ship-readiness claim.
  - Validator required scope and ran-reader reason sentinels despite broader injected
    tool schema; finding task identities remain in summaries and evidence.
  sc_status: []
  needs_approval: none
  severity_max: low
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'R-1 / reuse / T-01: existing index and DEC-section parser reuse proposal;
      leave.'
    why: "File plan.yaml:184\u2013200. Cost: potential parser drift on STRUCK case\
      \ and section content. Alternative: adapt check-plan-routes._decisions_index\
      \ and gen-decisions-index.parse_decisions. Leave: fixed-root/case-sensitive\
      \ index semantics and defenced DEC-only section slicing conflict with required\
      \ segment authority/raw substring behavior; plan does not mandate duplicate\
      \ parsing."
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'S-1 / simplification / T-01: repeated provenance wording; leave.'
    why: "File plan.yaml:168\u2013172,216\u2013217,226\u2013236. Cost: related statements\
      \ require reconciliation. Alternative: merge creation/mutation prose and test\
      \ lists. Leave: ordinary-edit preservation differs from explicit caller-mutation\
      \ refusal; retain already-applied panel fix and distinct cases."
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'S-2 / simplification / T-03: adjacent exclusion repetition; optional
      fold-in to pm.'
    why: "File plan.yaml:347\u2013348. Cost: reciprocal-link exclusion repeated within\
      \ one intent can drift. Alternative: merge exclusion sentences while preserving\
      \ every unique exclusion and BRIEF scope. Route: optional fold-in to pm; no\
      \ assertion weakening."
  - kind: form
    scope: none
    severity: low
    reader: altitude
    summary: 'A-1 / altitude / T-01: era resolver placement unspecified; briefing-row.'
    why: "File plan.yaml:173\u2013183. Cost: ad-hoc root discovery could duplicate\
      \ manifest-probe invariant. Alternative: prefer supplied product --root; reuse\
      \ plan_merge.guards._harness_root only if discovery needed, keeping instant\
      \ parsing cohesive. Route: implementation briefing row, not new module or plan\
      \ constraint."
  - kind: form
    scope: none
    severity: low
    reader: altitude
    summary: 'A-2 / altitude / T-02: repeated author-facing mechanical obligations;
      leave.'
    why: "File plan.yaml:277\u2013286. Cost: future changes touch multiple prose owners.\
      \ Alternative: pointer-only draft prompt to checker. Leave: weakens SC-04/SC-07\
      \ point-of-use obligations and reopens settled prompt trims."
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-data-engineer
    reason: none
  - reader: efficiency
    status: ran
    persona: harness-dev-ops
    reason: none
  - reader: altitude
    status: ran
    persona: harness-ai-dev
    reason: none
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2229-decision-dispositions/.harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-simplify-eng/digest.md
```
