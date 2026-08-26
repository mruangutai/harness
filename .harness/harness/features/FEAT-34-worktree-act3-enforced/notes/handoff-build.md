# Handoff — FEAT-34-worktree-act3-enforced, build → build (context) — at 4c7b650, seq-3

Supersedes seq-2. All re-verified by me at source; nothing inherited unchecked.

## Next

FULLY HELD ON THE OPERATOR — nothing is dispatchable, no squad can reach the remaining work.
Four operator acts, any order: (1) execute T-07/T-08/T-09, all `main-session-direct` + `pending`,
which ARE the qa gate's M1/M2/M3; (2) sign Amendment 3 / SC-16; (3) sign D-11; (4) approve the
one-clause D-01 `because` correction. THEN: re-run qa gate, SIMPLIFY (carrying Q7), operator
commits, pin `review_sha`, `gh-sync.py status <dir> Review`, panel, goal-check, close-out.

## Trust

- qa gate FAILed, matrix_ok false, and is CORRECT: the plan is incomplete, the squad work is not
  at fault — runs/2026-08-24-01-validator/digest.md — verified-at 4c7b650
- `INV-30` occurs 0 times in check-state.sh (`INV-29` 9x): REQ-12 is UNBUILT, not untested; SC-12
  has nothing to evidence — grep by me — verified-at 4c7b650
- `INV-29`/`INV-30` occur 0 times in test-check-state.py: SC-01..SC-05 have no gate-level
  evidence. Predicate tested, GATE not — grep by me — verified-at 4c7b650
- NO CYCLE spent on the qa FAIL, deliberately; cycles_used stays 6. DEC-157 = rework only, and
  T-07/T-08/T-09 were never executed — first-pass forward work — verified-at 4c7b650
- Suites measured by me: sweep 47, hooks-install 29, worktree-terminal 34, each exit 0;
  check-state.sh exit 0; run-unit-tests.sh exit 0, zero ^FAIL — verified-at 4c7b650
- REQ-07's repository scope was left OPEN BY THE BRIEF: BRIEF.md:237-239 — "REQ-07 through REQ-09
  are written to be satisfied by either." REQ-07 (:73-74) has no repo quantifier — verified-at 4c7b650
- `classify`->`classify_all` at post-merge-sweep.sh:234 is a NO-OP THAT LOOKS GREEN: no served
  checkout carries `.claude/skills/harness/hooks` (kaya-ai lacks it, smoke absent), and :163-167
  builds feat_dir under `main_checkout_root` so served records SKIP — measured — verified-at 4c7b650
- D-01's `because` (plan.yaml:88) is FALSE as written on the repository dimension. pm judges it a
  CORRECTION not a DEC-188 strike: the choice stands, the reason overreaches — verified-at 4c7b650
- SC-16's red proof is already DISCHARGED — test-post-merge-sweep.py:665-687 records "(RED: not
  found)" against today's code — verified-at 4c7b650

## Dead ends

- Do NOT route M4 to eng — the code change is a measured no-op; follow-up is TEST-ONLY and only if
  D-11 signs — verified-at 4c7b650
- Do NOT edit check-state.sh / test-check-state.py from a squad — DEC-174 am.4; the three tasks
  are main-session-direct by `execution_mode` — verified-at 4c7b650
- Do NOT pin `review_sha` before the operator commits — HEAD lacks the work, so a pin grades
  nothing (P-02/P-07); the trap was live all phase — verified-at 4c7b650
- Do NOT file Q3 — falsified; test-validate-digest.py is ALL PASSED exit 0. Q8 (concurrent runs)
  explains the phantom — verified-at 4c7b650
- Do NOT trust a count in any digest — THREE failed re-measurement (36/41, 27/29 twice). Measure
  without a pipe — verified-at 4c7b650
- Do NOT fold D-11 or the D-01 correction into Amendment 3 — three independent signatures, pm's
  explicit instruction — verified-at 4c7b650
- At distillation DROP backend-dev observations line 5 (D-10 falsified it) — UNVERIFIED

## Working set

- .harness/harness/features/FEAT-34-worktree-act3-enforced/STATE.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/runs/2026-08-24-01-validator/digest.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/research-req07-sweep-scope-2026-08-24.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/research-goal-scope-linked-worktree-2026-08-24.md
- .harness/harness/features/FEAT-34-worktree-act3-enforced/plan.yaml
