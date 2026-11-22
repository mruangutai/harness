# Handoff — FEAT-2225-member-expertise-writes, validate c3 → operator decision — written after r-20261121-8 closed, seq-8

## Next

Validate c3 over review_sha 6d9e6053a6367c78f1e5848a6801e7ca09d82dd1 (code tree ≡ 219690d0) returned FAIL: F1 and F3 CLOSED by every reader; **F2 STILL OPEN, high substance, T-01 + T-04** (runs/r-20261121-8-validate-c3-validator/digest.md). The rework ruling (notes/answers-2026-11-21-signoff.md, 2 rounds / 90 min) is exhausted on rounds: c2 was round 1, c3 round 2. No further fix round is dispatched; the `continue` judgement on r-8 records `decision=stop`. The feature waits on the operator.

F2 at c3, verified against the readers' own notes (not the receipt):

- The c2 fix (219690d0) closed the c2 counterexample: `expertise-merge.py` `authorized_base` anchors on merge-base(HEAD, default branch) or merge-base(--base, HEAD); `validate-digest.py` supplies no digest-controlled base. QA: matrix green (unit 61 files/1136, integration 88 files/2922 under `env -u HARNESS_AGENT_TYPE`), committed-tamper regressions red-first, N2 mutant caught by one discriminating check.
- The remaining counterexample is EXECUTED by security (notes/review-harness-security-reviewer-c3.md §F2): on `feat/probe`, commit an unreceipted G-01 deletion, legitimately apply P-01, then `git update-ref refs/remotes/origin/main <deletion commit>` (or, with no origin refs, `git branch -f main <it>`); `verify_receipt` flips from refusal 15 to `verified: true` while the branch stays `feat/probe`. The receipt's "only the main checkout anchors on itself" premise is false: the anchor is a mutable feature-local ref. `bash-write-guard.py` does not classify `update-ref` or `branch -f` as a forbidden HEAD mover (security, :181-235,245-267). Code reviewer derived the same from pinned source.
- SC-03 / SPEC §5.3 / DEC-253 promise close-time refusal; replay/merge containment is not close compliance (lead, code, security, pm concur). QA's N3 (explicit `--base` = feature HEAD self-anchors; no caller does this today) and N4 (default-branch self-anchor) are low advisory, deduplicated into F2.

Operator options, with the orchestrator's recommendation first:

1. **Extend the ruling by one round** (`feature-record.py set-rework`, and `raise-cycles` only if needed — cycles_used is 1/10) for ONE more main-direct fix segment (T-04 is DEC-174 main-direct; F2 spans T-01 and T-04 as before). Remedy direction, for pm/the main session to judge, not a decision taken here: anchor the chain on an authority a feature-local shell cannot move — e.g. the base sha the main session recorded at signature (`feature.json` `github.build_entry` / `signed_task_hashes` era) or the fetched remote tip verified against the registry — and have `bash-write-guard.py` refuse `update-ref`/`branch -f`/`symbolic-ref` on default-branch refs for governed agents. Add regressions: moved `origin/main`, moved local `main`, nonancestor `--base`.
2. **Accept F2 as a documented boundary** — requires amending BRIEF SC-03 and T-04's intent under approval (pm, re-signature); the panel will not pass it as written.
3. **Abandon** (`set-feature-station abandoned`).

Branch tip to push (nothing pushed by the orchestrator): see `## Working set`.

## Trust

- Validate c3 r-20261121-8: five readers ran, every return structured and accepted; run state.yaml shows all five steps complete — runs/r-20261121-8-validate-c3-validator/digest.md — source
- Security's executed probe used `git show <pin>:…/expertise-merge.py` in temporary repositories; live/durable propagation source-derived — notes/review-harness-security-reviewer-c3.md — source
- Goalcheck c3: SC-01/04/05/06 met, SC-02 partial, SC-03 not_met; pm records the c3 re-grade of SC-02/03 as a deviation from SC-09's once-per-phase cadence, requested by the dispatch — notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c3.md — source
- Cycle attribution: r-8 closed with the digest's count 0; `run-end r-7 --cycles-used 1` was REFUSED ("disagrees with authentic digest evidence", r-7 digest count 0). cycles_used stays 1/10; the c2→c3 send-back is unattributed in cycles and recorded through the r-8 `regate` judgement — source
- Spend at close: runs 8, wall_clock 158 min, tokens 497000, rework_minutes 36, rework_rounds 0 (ledger counts only regate-opened fix runs; operator framing counts c2+c3 as 2 of 2) — source

## Dead ends

- Re-closing a FAIL run to attribute a main-direct fix's cycle (repo Expertise P-11) is refused when that run's digest carries an explicit `cycles_used: 0` — the authentic digest count wins — source
- `rm` of an orchestrator-written helper under notes/ is refused by bash-write-guard when the path is spelled through `$VAR`; absolute spelling passes — source

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json (review_sha 6d9e6053; r-8 closed FAIL; judgements regate, succession, continue:stop)
- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml (status review)
- runs/r-20261121-8-validate-c3-validator/digest.md
- notes/review-harness-{code-reviewer,security-reviewer,qa,ui-reviewer}-c3.md, notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c3.md
- notes/receipt-main-session-fix-c2.md (its `## Remaining boundary` is the F2 premise c3 falsified)

## Done when

Scope: operator ruling on F2 (extend / amend SC-03 / abandon); if extended, one main-direct fix segment then validate c4 PASS over a fresh pin
Authority: plan-task:T-01.verify
Authority: plan-task:T-04.verify
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
