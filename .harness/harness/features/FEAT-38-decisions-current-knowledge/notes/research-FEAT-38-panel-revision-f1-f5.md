# Panel revision F1-F5 applied — FEAT-38 — 2026-08-29

**All five operator rulings from `notes/answers-2026-08-29-panel.md` are applied, as nine surgical
edits across two files. Nothing else changed.** Plan still holds 28 tasks (23 done / 5 pending), no id
renumbered, reused or added, no `status:`, `depends_on:`, `files:`, `execution_*` or `id:` touched.
Neither approval fragment was written — `plan.yaml`'s `approval:` block and `BRIEF.md`'s `## Approval`
are byte-identical to what I found (measured: `git diff -U0` reports hunks only at plan.yaml
1828/1883/1886/1906/1911 and BRIEF.md 192/282/319/332, all far from both fragments).

## F1 — `plan.yaml` T-24 (high)

**F1a, the verify.** The blast-radius sweep now reads, verbatim as landed:

```
      git grep -l check-decision-claims -- . ':!.harness/harness/features' ':!.harness/notes' \
        ':!.harness/logs' ':!.harness/harness.json' && { echo 'references survive'; exit 1; }
```

Nothing else in the verify moved: the three prior exclusions, the `--check-kinds` clause and the
anchor-checker clause are unchanged, and `verify:` is still a literal `|` block (re-loaded with
`yaml.safe_load`; the two lines above are the loaded value).

**F1b, the intent.** The paragraph that opened
`THE BLAST-RADIUS SWEEP STAYS UNSCOPED, WHICH IS WHY THIS TASK DEPENDS ON T-27.` is replaced by three
paragraphs at plan.yaml:1883-1908:

1. `THE BLAST-RADIUS SWEEP EXCLUDES .harness/harness.json, AND THAT EXCLUSION IS STRUCTURAL RATHER
   THAN CONVENIENT.` — T-25 cleans that file and `T-25 depends_on: T-24`, so at T-24's own completion
   the reference is necessarily live; without the exclusion the clause is unsatisfiable at the only
   moment it is evaluated, a cycle under the completion-time model. Carries the measured mid-state
   (unexcluded exits 1, excluded exits 0) and states that the other three exclusions are dated records
   never rewritten (D-05) while this fourth is a dependency-order artifact, narrower in kind and
   discharged elsewhere.
2. `THIS TASK DEPENDS ON T-27 FOR A DIFFERENT REASON, AND THAT REASON STILL STANDS.` — the five-site
   enumeration is kept intact (now reading `.harness/harness.json (T-25, excluded above)`), as is the
   T-28-is-not-in-the-path rationale.
3. `THE PROOF THAT NO SIXTH REFERENCE SITE EXISTS IS SC-14's THIRD ASSERTION, NOT THIS CLAUSE.` — the
   false "only thing in the plan that proves" sentence is gone; the proof MOVES to SC-14, graded at
   `review_sha` where the file is clean. The report-upward closing instruction is kept.

**Third occurrence fixed in the same edit:** T-24's closing traces sentence said "its unscoped sweep
ARE that criterion's evidence"; it now reads `its blast-radius sweep`. That word was false in two
places, not one.

## F2 — `BRIEF.md` (blocking)

**F2a, SC-11** (now :289-293): states the re-grade reaches FIVE entries — DEC-145, DEC-157, DEC-181,
DEC-183, DEC-193 — being T-27's six marker-carrying entries minus DEC-205, and that
`DEC-205 is excluded from this criterion because it has no pre-fold form`, its coverage being SC-16's.
The 15-entry set, the per-entry read-back and `verify: inspection` are unchanged.

**F2b, SC-16** (now :331-341): extends the criterion to DEC-205's considered-and-refused paragraph,
**anchored on the content string `What was considered and refused`**, with `DECISIONS.md:6293-6299`
carried only as an as-measured-at-`99bb52c` aside — explicitly because T-27 and T-28 both shorten
`DECISIONS.md` before `review_sha` is pinned. Requires both refusals (M3 referenced-file-watch, M4
LLM-audit) and their stated reasons to survive, nothing in it still asserting the deleted marker
mechanism, cited at `review_sha` beside `git show 99bb52c:`. No SC-19 was created.

## F3 — `BRIEF.md` REQ-10 (med), one sentence at :193-198

`**Reconciled with the recorded Destination** in .harness/notes/grilling-remove-executable-claims-2026-08-29.md`
— that Destination is the END STATE, REQ-10 is the step this feature takes toward it; the feature
closes the one known instance and NAMES the rest, and any further site the audit finds is carried to
the backlog rather than silently accepted as the destination reached. **Scope unwidened:** the
CONDITIONED DELIBERATELY sentences, the `test_kinds.<kind>.cmd` candidate and the out-of-scope
remediation clause are all untouched.

## F4 — `BRIEF.md` SC-17 (med), added at :355-362

Names the inspector: `harness-code-reviewer` or `harness-backend-dev`, **not** the author of the table
(T-29's `execution_agent` is `harness-pm`), with the duty spelled out — re-read the call sites behind a
sample of the verdicts, and re-derive the verdict for any file whose rationale cites a `test_kinds` cmd
reader. No plan-structure change: T-29's `execution_agent`, `files:`, `verify:` and `traces:` untouched.

## F5 — `plan.yaml` T-25 trace (low)

`T-25 traces: [REQ-10, SC-15]`, placed as dispatched — T-25 lands second and its verify runs
`--check-kinds` against both registration lists and the tree, which is SC-15's own both-halves claim.
**Named hazard checked:** T-27's `traces:` still reads exactly `traces: [REQ-10]` (plan.yaml:1977,
confirmed by loaded value, not by a text search). No `replace_all` was used anywhere. SC-18 left
untraced, deliberately.

## For the next reader

- The orchestrator's gates are unrun by me by instruction. It re-runs `harness_yaml.load_plan`,
  `check-plan-routes.py` and the mid-state verify. I did run one scoped `yaml.safe_load` of this plan:
  28 tasks, T-24's verify loads with the amended pathspec, `approval:` keys intact.
- The two pre-existing informational DEVIATION lines on T-22/T-23 are untouched and expected.
- The signature must be re-taken by the main session; both artifacts changed after `73898a3`.
