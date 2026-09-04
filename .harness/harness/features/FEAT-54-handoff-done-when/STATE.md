# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: main-session-direct backlog pass over B-1..B-7 (no run dir; no squad ran)
- squad: none — main session, DEC-174 carve-out
- status: review (plan.yaml `status: review`), awaiting the operator's ship decision

Validate completed at c6: panel PASS with `must_fix` empty at pinned `dd55b357`, and the product
goal-check met 14 of 14 non-UAT criteria. SC-10's operator UAT was executed; every mechanical step
behaved as scripted and the operator confirmed the agent-successor grounds, so the criterion is met.
The three refusal messages measured actionable, the section costs 5 lines of a 60-line budget, and
the template steered an action-shaped `Scope:` unprompted.

The operator then directed that the whole proposed backlog be fixed rather than filed. All seven
landed main-session-direct, because every remedy touches the enforcement tree DEC-174 reserves:

- B-1 — `handoff_done_when.py` now refuses a `## Done when` whose EVERY authority is already
  satisfied. A `plan-task:` at `done`/`abandoned` and an `approval:` reading `approved` are
  satisfied; `brief-sc:` and `finding:` are judged, so they stay indeterminate and never refuse.
  The F-11 defect class is mechanical for the first time; 12 unit cases, write-time only.
- B-2 — `check-domain.sh` had TWO cwd fail-opens, not one. The shape phase resolved a claimed path
  with `os.path.abspath`, and the domain phase handed the raw claimed path to
  `harness_boundary.classify`, whose parameter is `abs_target`. Both now go through `_claimed_abs`.
  12 integration cases fire every payload from two working directories; 3 fail without the fix.
- B-3 — the comprehension probe escapes C0/C1 and DEL at every print sink; newline and tab survive.
- B-4 — the 300-line `feature.json` budget now counts the JOURNAL, not the `runs` ledger, through
  one shared `feature_schema.journal_lines`. FEAT-54's own record: 336 lines, 43 of them journal.
- B-5 — CI gained a Repository-state gate step running `check-state.sh` per commit, with a
  git-derived corpus count as its positive control. SC-04 is no longer pin-only.
- B-6 — the three unrecorded run dirs are in the ledger and `cycles_used` corrected 21 -> 22 from
  the sec-f10 run's own reported send-back.
- B-7 — `eval` moved from `unresolved`/"detection has not run" to `excluded` with a reason naming
  the two `locally_run` probe kinds that are this repository's ai_behavior surface.

Unit and integration suites pass (exit 0 each); the repository-root state gate exits 0 over 805
rows, all NOTE. Three suite fixtures were corrected, not relaxed: the 301-line boundary case now
counts real journal lines, `_PLAN_LEGAL` gained a non-terminal T-02 so a legal fixture handoff does
not cite a satisfied authority, and the cross-file drift detector asserts the single-sourced budget
plus the shared counting rule.

Cycles used: 22 of 30. Runs stand at 51 against the informational budget of 20 — over by more than
double, disclosed rather than excused. Merge, PR and worktree removal remain the operator's acts;
nothing was rebased and no pull request was opened.

## Open Questions

- One residual cannot be closed without fabricating an artifact: ledger entry
  `2026-09-02-goalcheck-c1-product` has no run directory. The run is real — its evidence survives
  as `notes/research-FEAT-54-goalcheck-plan-c1.md` — so the entry is truthful and was kept.
  Deleting it would erase a recorded FAIL; writing a digest for a run whose digest was never
  created would invent one. Left as a known ledger-floor gap.
- The B-7 exclusion cites `signed: DEC-187`, the decision that established the rule and signed
  `functional`'s exclusion on the same double-count rationale. If the operator wants a DEC of its
  own for `eval`, that is a documentor dispatch.
