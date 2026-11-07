# Receipt — harness-dev-ops — BUG-2161 distill (runid 2026-11-06-11-distill-eng)

BLUF: no Expertise writes. Zero accepted, three rejected. No diff reviewed, no suite run.

Counts (before = after): craft P 15/15, G 15/15, O 8/10, Open 0; repo P 2, G 14, O 0, Open 0. Accepted: self-derived 0, lead-relayed 0.

Rejections:
- Self: "a signed verify chain at a boundary step is evidence, not waste" — already covered by craft P-16 and the efficiency angle rule; craft P and G are full and nothing weaker to displace.
- Self: "one-shot CLI parse cost is negligible" — a verdict on one diff, not a reusable rule.
- Relayed: runner-image drift versus feature defect. The orchestrator observations (observations/harness-orchestrator.md, 10 lines, last dated 2026-11-03) and a grep of the feature tree's .harness for `ubuntu-26`/`2169` hold no ship-phase record, so the claim is unsupported by anything I can read. Rejected as unsupported; if the record lands, the premise should be re-measured first. Both craft sections are full besides.

Applied ops: none. check-expertise.py run on both own files; output in the final message.

## Lead read-only assist (harness-eng-lead; nothing written)
Lead craft is full on P (15/15) and G (15/16 ids, 15 entries); repo tier has G-01, G-02, G-10, G-03 only. Candidates from handoff-build, research-simplify-apply and orchestrator observations:
- Restated ordering in a validate dispatch becomes a must-fix the signed criterion never required: overlaps P-02/P-05 (dispatch restatement drift); does not beat either.
- Pin / station / re-pin commit sequence for review_sha: a procedure, not craft; repo-specific and rots.
- Leads return by final message, so digests must be validated and appended by hand: a runtime harness defect, goes to open_questions, never Expertise.
- Run-id suffix -eng|-product|-validator refusal: harness defect or repo fact; at most a repo G, weaker than the existing four.
- PyYAML user-site stripped by the guard: environment, rots.
- Plan-surface four-angle pass is not in the team file: repo fact, not stronger than the existing G entries.
Verdict: none beats a full-section entry.

files_touched: []
