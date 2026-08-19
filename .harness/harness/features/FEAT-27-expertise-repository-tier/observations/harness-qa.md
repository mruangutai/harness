# Observations — harness-qa — FEAT-27

- 2026-08-19: `bash-write-guard.sh` denies `cp`/`sed -i` on ANY path under the scratchpad
  (`check-domain.sh --resolve` answers `NOBODY` there) — not just repo paths. Mutation-probe
  copies must go through the `Write` tool, never `Bash cp`, even in scratchpad. Cost me one
  self-inflicted bug: I wrote a mutated `check-expertise.sh` copy under the baseline's filename
  by re-using a mutation draft as the "baseline" — caught only because the T-03 abspath probe
  (case6) failed against what I *thought* was the unmutated baseline. Lesson: run the baseline
  probe FIRST, unconditionally, before touching any mutant file, and diff the baseline copy
  against the real file's content (not just its md5/existence) before trusting it as control.
- 2026-08-19: `run_cmd([CHECK, ...], cwd=some_tempdir)` in a probe harness needs `CHECK` to be an
  **absolute** path — `./check-expertise.sh` resolves against the harness's own cwd at spawn
  time, not the subprocess's `cwd=` override, so a relative `CHECK_EXPERTISE_BIN` silently
  breaks exactly the bare-path-invocation case (case6) it's supposed to prove.
- 2026-08-19: FEAT-27 T-02's case12 (hostile `agent_type` values against the
  `^harness-[a-z0-9-]+$` regex) is fully vacuous under mutation — removing the regex entirely
  produces empty stdout for all four hostile values (`harness-`, `harness-qa/../../etc`,
  `harness-*`, `harness-qa;id`) because none of their interpolated paths match a real file on
  disk in the case's own fixture (which only writes `harness-qa.md`). The `harness-*` value in
  particular does NOT glob-match a real `harness-qa.md` file, because it sits inside double
  quotes in the script (`"$agent.md"`), so the shell treats its `*` as a literal character, not
  a wildcard, when the surrounding word undergoes pathname expansion. The regex's actual "only
  harness-agents" filtering IS bound — but by case6 (`some-other-agent`), a value that predates
  T-02's suffix-hygiene addition and would have been rejected by the pre-change script's plain
  `case` pattern too. So 1c's specific contribution (rejecting a bad *suffix* after a valid
  `harness-` prefix) has zero test coverage in the current suite.
