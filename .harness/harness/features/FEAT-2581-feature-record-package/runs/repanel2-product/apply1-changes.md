# repanel2-product c3 — text pm changed in the first apply

This is pm's routing table from its apply return (harness-pm, first pass), transcribed by the lead and routed to the second read. Line numbers refer to the worktree plan.yaml and BRIEF.md after the edit.

pm's receipts:
- plan-merge apply printed `REPLACED T-03.verify`, `REPLACED T-03.intent` and `APPLIED`, exit 0, with no APPROVAL-RESET.
- check exited 0 with "3 task(s), 14 anchor(s) resolved, 0 failure(s)".
- Only T-03 and the BRIEF disclosure changed. SC-05, SC-06 and SC-08 are unchanged.

pm's apply log is in notes/research-feature-record-package.md §11.

| # | answers | where (worktree) | routed to |
|---|---|---|---|
| 1 | scope high: PF-14c27514 not closed (required stream keys) | T-03.verify :339 (the `RK=` / `bad=` statements before the D recompute); T-03.intent, Measurement files paragraph :360 (the required stream keys per kind, the recorder-failure rule, and the refusal list) | scope |
| 2 | scope med (audit count checked by regex only) and design high (disclosure not bound to measured bytes) | T-03.verify :346 (audit line: count pair derived from both committed audit stdouts); T-03.verify :341 (after `assert mv==D`: the build-divergences.md `divergence_entry` bodies must equal the recomputed pairs; source-only entries for d02#); T-03.intent, Audit paragraph :374; Compare paragraph :376 (entry format, payload = repr of the bytes after root replacement, source_only_entry) | scope, design |
| 3 | should-not-exist med: Q3(a) exceedance undisclosed | BRIEF.md Constraints, end of "Disclosure for signature", :104–110 (new sentence). Settled is untouched; whether to amend Q3(a) is an operator question | should-not-exist |
| 4 | should-not-exist low: two implementations | T-03.intent, appended at the end of the Compare paragraph :376 (normative for both cleanpin.py and the verify; a drift is a script bug fixed with `--reuse`, never a divergence and never a re-pin) | should-not-exist |

pm says it ran a synthetic probe: 11 mutants (streams {}, missing stderr, null stdout, empty exit, kind mismatch, cli without class, altered payload, missing entry, dropped source-only entry, audit 0 0, duplicated audit line) each failed at its intended assertion, and the good receipt passed. The probe was at /tmp/feat2581-c3-probe.py and was not committed. [pm's claim; the lead did not run it.]
