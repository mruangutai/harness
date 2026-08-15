# Handoff — FEAT-07-verify-teeth-batch-probe, plan → build — written at 4091b36, seq-13

## Next

Nothing dispatches until the user signs BOTH artifacts. Nothing blocks the signature — D-07 was
redirected by the user, applied and re-verified; the three remaining items are preferences, signable
either way. On approval the build opens with `gh-sync.py open`, then T-01 — **main-session-direct**,
not a lead dispatch, per PLAN D-02 and the DEC-174 carve-out. Eight of ten tasks are
main-session-direct; only T-06 and T-09 (`docs/**`) go to product-lead → `harness-documentor`. Read
PLAN's `## Lanes` table and each task's `execution_mode:` before routing anything. T-01 is now
roughly DOUBLE its original diff — the conditional `task_verify` mechanism plus fixtures across all
nine — and it is the one task with no member review during the build.

## Trust

- BRIEF and PLAN are both `status: pending`, no `## Approval` body written — `grep -A2 '^## Approval'`
  on both — verified-at 4091b36
- The redirect is COMPLETE: ZERO `⚠️` redirect markers survive in BRIEF or PLAN — I grepped both at
  final state — verified-at 4091b36
- The 18 surviving `no-task` mentions are intentional: 9 are absence-GUARDS paired per DEC-169, the
  rest sit inside D-07's rejected-alternative record — `runs/redirect-product/digest.md` Q2 —
  verified-at 4091b36 (count), lead-judged (classification)
- T-09's precondition is KNOWN-CLEAN: `gen-decisions-index.py --stdout | diff -` against the index
  exits 0 and `git status` shows the file clean — I re-measured rather than trusting the relay —
  verified-at 4091b36
- `.claude/hooks/` DOES NOT EXIST in this repo, which is why D-06's old preload grep proved nothing
  — `ls -d .claude/hooks` fails — verified-at 4091b36
- `run-unit-tests.sh` exits 0 — I ran it, not cited — verified-at 4091b36
- Three fail-value rows are ACCEPTED today and are what T-01 closes: `dev suite:fail`,
  `qa suite:fail`, `qa matrix_ok:false`, each with `VERDICT: PASS` — verified-at 3bfedc9, code
  unchanged since
- pm's claim to have executed every task `verify:` rests on PLAN's receipts table; I re-ran the unit
  row and the index row myself, the remainder is UNVERIFIED at my tier

## Dead ends

- Do not re-open D-07. `no-task` is the REJECTED alternative and the user's reason is recorded —
  `notes/answers-amf-fix-product.md` — verified-at 4091b36
- Do not touch `docs/harness/DECISIONS-INDEX.md`. Committed alone at `4091b36` before any feature
  branch, with the measurement in the message — `git log --oneline -3` — verified-at 4091b36
- Do not fix or plan around pm's missing `receipt-*` grant — GitHub issue #46, out of scope by
  ruling — `notes/answers-amf-fix-product.md` Q4 — verified-at 4091b36
- Do not plan #20, #21 or perf-doc row 10 — `.harness/notes/grilling-perf-batch-1-2026-08-04.md`
  `## Out of scope` — verified-at 4091b36
- Do not re-open the architecture review's F1b/F1c/F2/F3/F4/F6 — resolved, and no further review is
  ordered — `runs/arch-review-eng/digest.md` — verified-at 4091b36

## Working set

- .harness/features/FEAT-07-verify-teeth-batch-probe/PLAN.md
- .harness/features/FEAT-07-verify-teeth-batch-probe/BRIEF.md
- .harness/features/FEAT-07-verify-teeth-batch-probe/feature.yaml
- .harness/features/FEAT-07-verify-teeth-batch-probe/notes/answers-amf-fix-product.md
- .claude/skills/harness/bin/validate-digest.py
