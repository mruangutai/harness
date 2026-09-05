# Advisor answers — BUG-1308 plan panel, cycle 1

Attribution: the operator-delegated **Advisor**, persona `fable-advisor`, running as the panel's
`should-not-exist` reader in `runs/2026-09-05-plan-panel-c1-validator`. All three answers are
recommendations to the operator, not panel findings; none is counted in `severity_max`. They are
copied verbatim below from the validator lead's digest `advisor_answers:` block. Recorded as `D-14`.

## What each answer settles for this plan

**A1 — D-12 stands as written.** Enforce the id-reuse ban only in-proposal (a drop plus an add of the
same section and id in one proposal exits 11); build **no tombstone** — neither an in-file ledger nor
a side store. One honest caveat the Advisor records: after a *tail* drop the numbering shows no gap,
so accidental reuse over time is likely. If the operator ever wants across-time protection, the
mitigation is **one contract sentence** ("continue from the highest id ever used"), not a mechanism.
No task changes from this.

**A2 — T-02 keeps `change_type: scaffolding`.** Settled on the qa gate's own terms, not by
convention: the gate classifies from the **diff**, and this feature's diff contains
`expertise-merge.py`, so the gate binds the bugfix matrix row through T-01's surface regardless of
T-02's label. Typing T-02 `bugfix` would be false on the gate's own terms — its diff is test files
only, and the bugfix row would then demand a regression test *of* the regression test.

**A3 — the contract/tool split in D-10 stands.** The tool takes `add`/`replace`/`drop`; the contract
keeps `merge` as an **authoring** concept it rewrites in its own text; the tool refuses `op: merge`
at exit 12 with a message naming the rewrite. Neither vocabulary wins outright. The priced cost of
the split is the drift-detector's REWRITTEN special case and its verbatim-sentence pin — which is the
Advisor's own low finding (`PF-5674cd36…`), proposing to soften the pin, not the split.

## Unsettled — an operator call at signature

The validator lead flagged a tension in `adequacy_notes` that the panel **could not settle**: A3 keeps
a verb the tool *refuses* (`merge`), while the same reader's med finding `PF-3f8a1114…` proposes
deleting an affordance the tool *accepts* (D-02's optional `section` on replace/drop). Both pull the
verb/argument vocabulary in opposite directions in the same breath, and both are **contract-shape
calls for the operator at signature**, not for a dev at build time. Digest open question Q3 carries
the second half of it. Nothing in this note resolves either; no finding was repaired in this segment
and all seven remain `disposition: open`.

## Verbatim — as returned by `fable-advisor`

### A1

> **answer:** D-12's boundary is right: enforce the id-reuse ban only where the tool can see it
> (in-proposal), and build no tombstone.
>
> **reasoning:** Three grounds. (1) Consequence of violation is low: the Expertise file is the sole
> runtime source - it is injected as-is at spawn - so a resurrected id misleads no consumer; the
> across-time ban protects only diff archaeology. (2) Every tombstone design costs more than that. An
> in-file ledger spends the spawn-injection budget the SKILL.md itself calls physics - the hook hard-
> truncates at 150/40 lines, so tombstones would displace live rules, an actively harmful trade. A
> side file is a second persistent store beside DEC-199's one merging core, needing its own lock,
> format, checker and unbounded growth policy, to enforce an authoring-hygiene rule DEC-66 already
> records as an accepted tradeoff. (3) The record already exists for free: the Expertise files are
> git-tracked, so any future audit of "was this id ever used" reads history rather than a new
> mechanism. One honest caveat for the record: after a tail drop (e.g. P-15), numbering shows no gap,
> so accidental reuse over time is likely - if the operator ever cares, the mitigation is one contract
> sentence about continuing from the highest id ever used, not a mechanism.

### A2

> **answer:** Keep change_type: scaffolding on T-02. Do not retype it bugfix.
>
> **reasoning:** Verified in the qa machinery, not from convention alone. (1) The gate classifies from
> the DIFF, not the task label - harness-qa-gate SKILL.md: "Judge from the diff, not from a task
> description" - and the feature's pinned diff contains expertise-merge.py, which the gate will
> classify bugfix on its own, binding the matrix's bugfix row (unit always, plus match_bug_class;
> harness.json:203-213) against exactly the files T-01 and T-02 deliver. The matrix therefore already
> binds this feature's coverage through T-01's surface; T-02's label adds or removes nothing at gate
> time. (2) Typing T-02 bugfix would be false on the gate's own terms: T-02's diff is test files only;
> the bugfix row demands "a regression test that reproduces the bug" of a diff that IS that regression
> test - circular, and a misclassification a reviewer must then explain away. (3) Precedent:
> BUG-1286's plan typed its test-only tasks scaffolding (plan.yaml:858,896); a second convention
> beside an existing one is a cost by itself. (4) The residual risk - scaffolding's empty matrix row
> means nothing forces T-02's cases to be adequate - is closed by a stronger binding than the matrix:
> SC-01..SC-11 name exact commands, exit codes, tokens and sha256 observables, graded at goal-check.

### A3

> **answer:** The split is sound: build the ops mechanism with add/replace/drop, keep merge an
> authoring concept the contract rewrites, and let the tool refuse op=merge naming the rewrite.
> Neither vocabulary should win outright.
>
> **reasoning:** A tool-side merge verb is unimplementable as anything but sugar: synthesizing the
> survivor's text is authoring judgment, so a mechanism merge collapses to replace-with-supplied-text
> plus drop - the rewrite - while adding a genuine ambiguity (which id survives) the enumerated
> refusal set would then have to grow for. Dropping merge from the contract outright would simplify
> case17 but deletes real contract content: the length rule ("a merge result is no longer than the
> longer input") and the instance-list ban attach to merge, and a DIGEST receipt reading op: merge
> preserves the provenance of a synthesis that a bare replace+drop pair erases for curation and audit;
> DEC-66 blesses the four-verb schema, so removing a verb churns a signed contract to close no defect.
> D-10's refusal message makes the asymmetry self-teaching at the point of use: the one agent who ever
> emits op=merge to the tool is told the rewrite in the refusal itself. The honest cost of the split
> is the drift-detector's REWRITTEN special case and its verbatim-sentence pin - priced in my third
> finding, which proposes softening the pin, not the split.

Source of record: `runs/2026-09-05-plan-panel-c1-validator/digest.md` (`advisor_answers:`).
