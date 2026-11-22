# QA distill — FEAT-2257

**BLUF: no ops qualify; no `expertise_apply` call, no receipt.** Both candidates are covered by existing entries or fail the durable-rule test. No tests, review or builds were run.

## Candidates
1. **A-2 (coverage/suppression assertions never shown red): REJECTED, redundant.** Craft O-05 already says: report discrimination as unshown, never as "cannot discriminate", when no pre-change defect exists. O-03 already ranks and labels red-evidence tiers. The lead's "bounded assurance, no new mutation gate" is a feature judgment, not a QA rule.
2. **Run digests under gitignored `runs/**` absent from repo-state until force-tracked: REJECTED.** Independently evidenced here: only that run 45071452185 (SHA 4cc44d64) failed repo-state and was not used, and that exact-pin run 45071766676 is green. The force-tracking cause is Main's observation, unverified by this note. Craft G-15 already covers verifying pinned evidence artifacts are tracked at the exact SHA. A durable rule from this would encode a workaround for a possible harness defect (DEC-145), which belongs in `open_questions` to the harness owner, not Expertise. Raised in my digest as non-blocking open question.

## Own-note lessons
None independent. A-1 (change_type `config` understating logic; QA added unit) is covered by P-04 (floor resolution, add kinds the diff warrants) and the matrix's permitted additions. A-3/A-4 are single-feature provenance limits. Compiler-coverage-vs-discovery separation is specific to this feature's `typecheck` kind.

## Counts (unchanged)
|Tier|Patterns|Gotchas|Outcomes|Open|
|---|---|---|---|---|
|craft|15/15|15/15|10/10|1/5|
|repository (harness)|0/15|11/15|0/10|0/5|
