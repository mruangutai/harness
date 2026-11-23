# Receipt — simplify · altitude — FEAT-2397 (plan surface, flag-only)

BLUF: 4 findings (1 med-low, 2 low, 1 info), no blockers. Each ends fold-in, briefing-row or leave. Doctrine authority is sound: D-01..D-04 carry the contracts, T-05 owns all DEC/SPEC rewrites, the escalation route lives once in `.omp/rules/harness-constraints.md` (T-05 intent), residuals name compensating controls (perCallModel -> SC-06 pin + rules text; estimate-vs-anchor -> advisory-only, T-06 real observation).

## Findings

1. T-05 · plan.yaml:510-515,542 (bin comment edits under `change_type: docs`) — severity low
   - Summary: six production bin modules (check-domain, check-plan-routes, check_state/ctx, run_state, worktrees, feature_schema) are edited inside a docs task, so the test_matrix exemption applies; "without changing resolver/gate logic" has no check.
   - Cost: a stray logic edit in a gate module passes T-05 verify (gates exercise routes/layout, not each file's logic) and SC-09 inspection is the only net.
   - Alternative: briefing-row — add to T-05/SC-09 the receipt a comment-only proof (AST-with-comments-stripped equality of those six files, baseline 9eb07b4 vs review pin). One transient command, same style as T-02's inline check.

2. T-03 · plan.yaml:431 (title) vs 465 — severity low
   - Summary: title says "and stale bin comments" but T-03's files are tests only and its intent says T-05 owns bin comments; same capability named in two homes.
   - Cost: reader/Main may edit bin files in T-03 and collide with T-05's ownership (T-05 depends on T-03).
   - Alternative: fold-in — retitle T-03 "Remove redundant legacy environment setup in standing tests".

3. D-01..D-04 successors · plan.yaml:121-327 vs T-05 intent line 538 — severity low (open question)
   - Summary: 14 rows cite successor `D-04`, others D-01/02/03, yet T-05 says "do not assume a new DEC number". Plan-local D-NN ids do not exist in DECISIONS.md.
   - Cost: amended DEC tails/clauses need either a citable successor or none; unspecified, Main may write "D-04" into the corpus (dangling) or invent a DEC number.
   - Alternative: briefing-row — state in T-05 that amended entries cite DEC-233/DEC-188 (existing) or none, never D-NN, until plan-merge/ship assigns numbers.

4. T-06 · plan.yaml:553-555 (depends_on T-05) — severity info
   - Summary: T-06's verify/intent read the repaired probe (T-04) and the review pin, not any T-05 output; no shared file written (receipt only). The edge serializes the credentialled manual observation behind the largest doc task.
   - Cost: latency on the user-gated acceptance only; no correctness risk (review pin follows all tasks regardless).
   - Alternative: leave if ordering is intended for a single review pin; else fold-in drop T-05 edge.

## Considered, not flagged
- Settled/panel items: T-05 Repository-state gate, transient SC-04 proof, T-06 trimmed receipt, eight extra DEC dispositions (not re-flagged), mandatory completeness lists/grades/index tails/force-add runs/**.
- Per-intent boilerplate (checkout path, SPEC consult, DEC-174) repeats across six intents but all are main-session-direct and intents are read standalone: leave.
- T-01 breadth settled (#10/#11 atomic).
- DEC-155/156 escalation text single-homed in rules file; SPEC/DEC cite it — right altitude.

## Open questions
- Finding 3 (successor citation form for amended DEC text). Non-blocking.

## Verification
Read-only; no build/test/lint run.
