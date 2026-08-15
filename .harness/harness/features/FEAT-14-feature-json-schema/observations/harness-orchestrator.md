# Observations — harness-orchestrator — FEAT-14

- 2026-08-11: a task whose `verify` runs a REAL script over the LIVE corpus is order-coupled to
  every other task that changes what that script reads. T-11's verify demands 0 route violations;
  T-05 repoints the same script at a filename the corpus does not carry until T-08. `depends_on`
  recorded T-05 → T-11 and the two constraints cannot both hold. Three monkeypatched runs of the
  classifier settled it in one tool call — cheaper than one dispatch that would have returned FAIL.
- 2026-08-11: the cheap probe for "does order matter here" is to import the script with
  `importlib.util.spec_from_file_location`, replace the one function that reads disk, and run
  `main([])` under `redirect_stdout`. No file is written, so no guard fires and nothing needs
  restoring. Note `main()` took an `argv` positional — read the signature before assuming.
- 2026-08-11: `run-unit-tests.sh` splits into `UNIT_SCRIPTS` and `INTEGRATION_SCRIPTS` by fork
  behaviour, NOT by what the file is about. So a task whose verify says `--kind unit` can leave the
  very test file that task edits unexecuted. Grep the two arrays for the edited test file before
  trusting a `--kind`-scoped verify clause.
- 2026-08-11: a `python3 - <<'PY'` heredoc that rewrote a file was not intercepted by
  bash-write-guard, in the same session where `rm` against a scratchpad path WAS blocked. The write
  was in-domain so nothing was damaged, but the guard's own message ("file changes go through the
  Write tool") is not enforced on that route. Raised as an open question, not worked around.
- 2026-08-11: the DEC numbers a plan reserves go stale while the plan waits. DEC-189 was reserved
  for this feature's D-04 and was taken by another feature before T-09 ran. Check the highest
  entry at write time; report the stale citation upward rather than back-filling the plan.
- 2026-08-11: a docs task's `files:` list is not its rename list. DECISIONS.md was in T-09's
  `files:` with 50 historical `feature.yaml` citations that must all survive, while the intent's
  rename list named three other files. The dispatch has to state the LEAVE list explicitly, because
  "rename it everywhere" plus a `files:` array reads as authorization to sweep.
- 2026-08-12: **my LEAVE list was too broad and it cost a whole run.** I told the T-05 lead the
  status fixture loop was off-limits; the plan's own item 7 said only that changing what it
  COMPARES was off-limits, and changing the filename was the task's business. The eighth of nine
  files went undone and came back as an escalation. When a prohibition has a stated rationale,
  quote the rationale into the dispatch — the member can then see when it does not apply, which a
  bare "do not touch X" never permits.
- 2026-08-12: an escalation's ATTRIBUTION deserves the same check as its facts. The lead blamed the
  T-05/T-11 contradiction on my reorder. Running both loop versions against the repointed reader
  took one tool call and showed the old loop fails on TWO rows and the new on one — the defect was
  order-independent. Accepting the attribution would have meant reverting a correct reorder.
- 2026-08-12: a mutant/case pairing asserted from reading a comment can be wrong. I instructed
  "delete the isinstance guard, expect a_mapping_with_no_status to fail"; that fixture parses to a
  dict and survives correctly, because the comment was describing the `bool(token)` guard. Name the
  BEHAVIOUR the mutant should break and let the runner report which cases fall.
- 2026-08-12: "the count is unchanged" is not a gate. When exempting known occurrences from a
  string sweep, anchor each exemption on its distinctive text — a `count == N` check passes when
  someone deletes an exempt line and adds a fresh violation elsewhere.
- 2026-08-12: an inherited counter with no traceable basis is worth re-deriving from the run list.
  `cycles_used` read 5; the signature said 3 and the commit that raised it recorded no rework. One
  increment traced to a real send-back and one traced to nothing, so 4 is the defensible number and
  the arithmetic belongs in the commit rather than the result alone.
