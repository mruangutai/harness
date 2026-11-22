# Receipt — altitude reader — r-20261121-2-simplify-eng-altitude

BLUF: 3 findings (1 med, 2 low). Read-only; nothing applied.

## A-1 (med, fold-in)
- file/line: plan.yaml T-01 intent, line 123 (narrow-gate matching paragraph)
- summary: Command applicability for the 3 narrow gates ends up stated twice: in each Python gate (gh-close-gate `denies`, plan-sign-gate matcher family, branch-create-gate `_branch_name`) and again in the extension so a spawn failure can still be classed applicable/unrelated. The plan hands the arrangement to a build-time "smallest matching arrangement" choice.
- cost: two matchers for one rule drift silently. A drift either blocks unrelated Bash (closed gate, can't be skipped) or lets a protected command through on spawn failure. This is the exact hole SC-02 exists to close, and nothing names a compensating control.
- alternative: keep the build choice open but require the plan to name the single authority for spellings: the existing per-gate regression spelling/exemption corpus, executed against BOTH the gate matcher and whatever extension-side classifier exists. The spawn-failure path must use the classifier proven equal on that corpus; otherwise state it is conservative-by-construction.
- recommendation: fold-in

## A-2 (low, briefing-row)
- file/line: BRIEF.md line 23 and line 40; plan.yaml T-03 SC-04 pointers
- summary: SC-04 cites "pinned OMP 19.1.0 shared spawn-path evidence" and "recorded published OMP 19.1.0 evidence" without a path. The only record is the grilling note (`.harness/notes/grilling-omp-native-enforcement-a-2026-11-21.md` lines 72-91, runner.ts / structured-subagent.ts citations), outside the feature directory.
- cost: the accepted residual (native assertDepthAndSpawnAllowed is sole spawns authority) rests on evidence a reviewer must hunt for; the note is a mutable control-plane file.
- alternative: add the note path and line range to the SC-04 reviewer-pointer text in T-03 so the receipt cites it at review_sha time.
- recommendation: briefing-row

## A-3 (low, leave)
- file/line: plan.yaml D-01 (82), T-01 (122), T-03 (168), BRIEF SC-01/SC-07
- summary: The D-01 wire contract (JSON fields, no dedup, deny precedence, exact phrase) is restated in T-01 and T-03 intents.
- cost: low drift risk; D-01 is signed and T-03 is the documenting task, so restating is tolerable. Mild.
- alternative: T-03 could say "record D-01 verbatim" instead of re-listing fields.
- recommendation: leave

## Checked, no finding
- Escalation guidance in the 3 lead files: right home (only leads dispatch); a rule-file copy would reach every harness-* member. Test pins each copy.
- Rule content groups in T-02 and SC-05: one grilling authority; asserted independently.
- Deleting dispatch-guard allowlist leaves one spawns authority (native); no parity check, consistent with settled scope.
