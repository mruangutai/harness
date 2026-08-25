# QA c1 close-out reassessment

## Conclusion

P-13, P-03, and G-06 remain **unapplied and not permitted** in this c1 run. No Expertise file was changed. The operator permits only operations expressible through the mandated `expertise-merge.py`; it offers lock-safe additive union, while these accepted curation actions require replacement/displacement. Direct or whole-file replacement is forbidden, so none was retried or applied.

## Individual dispositions

- **P-13 (Patterns):** unapplied; not permitted. The prior candidate would replace the existing cap-bound entry with aggregate-gate discovery/execution evidence.
- **P-03 (Patterns):** unapplied; not permitted. The prior candidate would replace the existing cap-bound entry with target-transition plus caller-preservation evidence.
- **G-06 (Gotchas):** unapplied; not permitted. The prior candidate would replace the existing entry with the equal-size Python-bytecode mutation-probe rule.

The immutable prior record documents the tool refusal as exit 8 (`CAP EXCEEDED section=Patterns cap=15 union_size=17`) before mutation. It records `Exact successfully applied Expertise ops: []` for QA and `Changed Expertise files: []`; this reassessment neither changes nor retries that result.

## Governing contract

`harness-distill/SKILL.md:26-28` requires a full section's new entry to displace a weaker entry and says to apply through the merge tool, never by writing the file. Lines 36-38 prohibit whole-file writes because they can lose concurrent entries. Lines 40-47 classify exit 8 as a section-cap refusal and require curation rather than append. The c1 operator rule narrows permitted outcomes further: only operations expressible through that mandated additive-union tool are permitted; direct/whole-file replacement is forbidden. Consequently, replacement/displacement cannot be performed in this run.

## Close-out status

The merge-tool replacement/displacement capability gap is a non-gating proposed follow-up, not a must-fix or blocking open question for c1. Stale code-reviewer P-06 is likewise outside this QA reassessment and non-gating. The two archive-recorded security/UI additive entries remain preserved; this QA reassessment made no change to them.

No formatter, linter, build, test, or project-wide validation was run, per scope.
