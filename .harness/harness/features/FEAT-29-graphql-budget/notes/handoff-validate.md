# handoff — validate → ship — FEAT-29-graphql-budget

RECONSTRUCTED 2026-08-21 by the main session, not written at the seam. The validate crossing
happened across runs 2026-08-19-04, -07, -09 and 2026-08-20-14 and no handoff was written; the
feature shipped in PR #601 (merged `5d9b428`) and INV-17 only surfaced the gap when status moved to
Done. Every claim below is quoted from those run digests, which survive on disk. Nothing here is a
recalled intention — where the record is silent, this note is silent.

## Next

Four questions from run -09 were left open at ship and none was answered. Q1 and Q4 share one
remedy: `.harness/logs/gh-cost-*.jsonl` needs a gitignore rule and the log is created `0644`. Use
that exact glob, **not** all of `.harness/logs/` — the sibling session logs there are tracked, so a
blanket rule would be wrong. Q1 also asks whether backlog item B-8 should be un-struck in the
narrow form: it was struck as moot because the opt-in default made it so, and that conflates two
controls — the default shrinks the window in which recording happens, while an ignore rule and a
file mode shrink what a recorded secret can reach.

## Trust

Trust the panel verdict: run -09 returned PASS, `must_fix: []`, `severity_max: low`, `matrix_ok:
true` at `c472a02`, with qa, code review and security all PASS.

Trust **script counts only**. Every suite figure in that run is script-level — 18 unit, 12
integration — never the per-check PASS-line convention that produced an earlier 164/172/806
confusion in this feature. Only script counts and the file-native 35/35 are load-bearing.

Do not trust SC-01, SC-03 or SC-04 as graded. The panel could not grade them: they rest on T-07 and
T-09, which are main-session-direct. Pending evidence, never failures. SC-08 and SC-09 sit on NOBODY
paths for that squad, so not-assessed is correct.

## Dead ends

**A mutation that discriminates nothing.** Making `measured()` record when `rc != 0` looks like it
would turn SC-05's OFF clause into an assertable one. It does not — `record()` re-checks
`_enabled()` at `gh_cost_log.py:112`, so the added call is a no-op and the mutant is equivalent. The
sharper form is that `measured()`'s OFF branch is `yield m; return` with no `try/finally` at
`:157-159`, so `record()` is never reached on that path at all.

**An escalation premise that did not survive one grep.** The claim that SC-05's OFF-side failing
clause is asserted nowhere is false: it is at `test-gh-cost-log.py:251-259`. Two tiers reasoned in
the same wrong direction from control flow without checking the assertion set, because an escalation
arriving with a defect already named makes the named defect feel like the question.

**A red gate reading that was not a defect.** `check-expertise.sh` exited 1 on
`harness-backend-dev.md` — a peer squad's file that was mid-write. Re-measured after all writers
closed: both tiers exit 0, every file OK.

## Working set

`.claude/skills/harness/bin/gh_cost_log.py` and `factory_gh.py` are the change surface;
`test-gh-cost-log.py` holds the assertions, including the OFF case above. The panel's own reports
are under `notes/` as `qa-matrix-gate-final-c472a02.md`,
`review-harness-code-reviewer-sc05-c472a02.md` (plus its `-c2` re-grade) and
`review-harness-security-reviewer-costlog-c472a02.md`. The untracked, un-ignored
`.harness/logs/gh-cost-2026-08-19.jsonl` is the artifact Q4 names.
