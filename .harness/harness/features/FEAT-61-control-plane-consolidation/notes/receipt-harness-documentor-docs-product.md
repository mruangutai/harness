# FEAT-61 shipped-documentation audit receipt

- Reference task: `T-05`
- Immutable shipped range audited: `066638e8acf68b47e74637006a01c8823cff939c..f798e2e600ed08aeb49d61a3a229a626750a9ccb`
- Verdict: **PASS**

## Result

```yaml
docs_updated:
  - .harness/harness/docs/SPEC.md
gaps: []
```

One existing present-tense user reference was genuinely stale. `.harness/harness/docs/SPEC.md` still described six capitalised lifecycle values, omitted `rejected`, treated `abandoned` as folded into `Done`, and called terminal outcomes board columns. The minimum correction now:

- names all eight lowercase on-disk stations and distinguishes the first six board-backed stations from `abandoned` and `rejected` (`.harness/harness/docs/SPEC.md:1850-1855`);
- records the eight-value meanings, case boundary, and no-column terminal behavior (`.harness/harness/docs/SPEC.md:2011-2036`); and
- states that cycle exhaustion does not itself choose `done` or `abandoned` (`.harness/harness/docs/SPEC.md:1776-1779`).

No other existing guide or README contained a FEAT-61-stale user-facing claim. No gap remains.

## Audit coverage and evidence

### Authoritative inputs

- Read the reader perspective and SC-08 in `.harness/harness/features/FEAT-61-control-plane-consolidation/BRIEF.md`.
- Read T-05 in `.harness/harness/features/FEAT-61-control-plane-consolidation/plan.yaml` and preserved its approved decisions.
- Inspected the full immutable diff, all 4,401 displayed lines, across the exact shipped range above.

### Accepted bootstrap duplication

`DEC-234` names the five scripts, explains why the trusted import seam cannot be shared, and requires reciprocal comments without enforcing their wording (`.harness/harness/docs/DECISIONS.md:7647-7672`). The generated index agrees (`.harness/harness/docs/DECISIONS-INDEX.md:233`).

Each shipped comment names the other four scripts, cites FEAT-61 D-09 and DEC-234, explains that the prologue creates the import seam, and says to change all five together:

- `.claude/skills/harness/bin/branch-create-gate.py:46-49`
- `.claude/skills/harness/bin/gh-close-gate.py:39-42`
- `.claude/skills/harness/bin/merge-gate.py:39-42`
- `.claude/skills/harness/bin/plan-sign-gate.py:65-68`
- `.claude/skills/harness/bin/run-unit-tests.py:41-44`

DEC-234 and its indexed summary are coherent with those five comments and were not revised.

### Lifecycle vocabulary

`.harness/glossary.md:27-45` coherently defines:

- the eight stations and the six-board-column/two-terminal split;
- the `not_started`, `active`, and `finished` partition;
- `active` as `plan`, `ready`, `building`, and `review`;
- `finished` as `done`, `abandoned`, and `rejected`; and
- historical `_work_started` as `building`, `review`, and `done`, explicitly distinct from `active` and not derived from `finished`.

The corrected present-tense SPEC now agrees with that vocabulary. The glossary was audited only and was not edited.

### Existing guides and READMEs

Audited the existing user-facing inventory for FEAT-61 lifecycle, gate-policy, bootstrap, and consolidation claims:

- `README.md`
- `.harness/README.md`
- `.harness/harness/docs/SPEC.md`
- `.harness/harness/docs/BUILD.md`
- `.harness/harness/docs/org.html`
- `.harness/harness/docs/DECISIONS.md`
- `.harness/harness/docs/DECISIONS-INDEX.md`
- `docs/PRINCIPLES.md`
- `docs/invalid-states-audit.html`

The removed gate-policy names and helpers (`qa_gate`, `gates.uat`, `gates.merge`, `blocking_when_uat_criteria_exist`, `user_gated`, `evaluate_qa`, `QaResult`, and `SUITE_OUTCOMES`) do not appear in those current user-facing surfaces. Historical decision/build records were read in context rather than rewritten as present-tense guidance.

## Verification boundary

Per the post-validation audit contract, no formatter, linter, build, test suite, or T-05 verify command was run. Verification was document inspection against the immutable diff and the cited shipped/current source lines. The exact carried T-05 command was cross-checked but not executed.
