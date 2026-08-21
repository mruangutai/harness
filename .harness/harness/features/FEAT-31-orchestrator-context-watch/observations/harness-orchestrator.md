# Observations — harness-orchestrator — FEAT-31-orchestrator-context-watch

- 2026-08-21: verifying a "3 files are non-conforming" claim, I invented the conforming set from
  the name instead of reading it. I assumed `SEAM_NOTES` contained `ship` and measured 1 non-seam
  handoff stem where the operator's answers file said 3. Reading `check-state.sh:495-508` showed the
  values are exactly `["plan","build","validate"]` — `ship` is NOT a seam stem, so `handoff-ship.md`
  IS non-seam and the answers file was right. The failure mode: a plausible enum guessed from a
  domain word, producing a confident number that contradicted the operator. Read the literal.

- 2026-08-21: a corpus count taken by glob is CHECKOUT-DEPENDENT and two honest measurements can
  disagree without either being wrong. `.harness/*/features/*/notes/handoff-*.md` gives 69 in the
  FEAT-31 worktree and 71 in the main checkout; the set difference is exactly FEAT-30's three notes
  (present in main, on an unmerged branch) minus FEAT-31's own one. Reconciled by set difference,
  not by inference. Any receipt asserting a corpus size must name the checkout AND the sha, or a
  re-run looks like a failed receipt.

- 2026-08-21: `bash-write-guard.sh` parses the UNEXPANDED text of a Bash command, so a `>` anywhere
  in a python3 heredoc is read as a shell redirect. `if len(hl) > 60:` was refused with
  "`redirect` targets 60:, outside your domain". Rewriting as `if len(hl) not in range(61)` ran
  fine. The guard is not wrong to be conservative, but it means analysis scripts passed through
  Bash must avoid `<` and `>` entirely — use `range`, `max`, `min`, or the Write tool plus a
  separate run.

- 2026-08-21: the same guard blocked an APPEND to a file I own — `cat >> "$F/observations/..."` was
  refused as "`redirect` targets xxxxxxx, outside your domain", because it reads unexpanded text and
  cannot resolve `$F`. The path IS mine; the shell variable is what defeated the check. Generalises
  the note above: never route a domain-owned write through a shell variable. Use the Write tool
  (read-modify-write), or a fully literal absolute path.

- 2026-08-21: I have no `SendMessage` tool, so a mid-flight fact cannot reach an already-running
  lead. I tried and mis-issued it as an `Agent` call with a placeholder prompt, which launched a
  junk fork. Consequence worth keeping: everything a lead needs must be in the DISPATCH, because
  there is no second channel. When a measurement lands after dispatch, its value is as INDEPENDENT
  verification of the lead's returned receipt — which is the stronger position anyway, since feeding
  my own numbers in would have made its receipt a restatement of mine rather than a check on it.

- 2026-08-21: under a no-merge-path whole-file artifact (plan.yaml, issue #628), the only guard
  available to me is dispatch discipline, and it has to be stated as a mechanism with its incident
  attached, not as a caution. I gave the lead the 1002-lines-to-191-in-63-seconds figure, the reason
  no gate catches it (the smaller file PARSES), and an explicit instruction that an incomplete pm
  return comes back to me as a finding rather than triggering a second spawn. Naming the escape
  hatch is what stops the lead inventing one.

- 2026-08-21: **and it was not enough.** The lead spawned a second `harness-pm` anyway and logged it
  itself as "LEAD ERROR"; the run survived only because that spawn returned BLOCKED with 0 tool uses
  and wrote nothing (verified independently: plan.yaml still 41503 bytes, mtime 06:16,
  clean-tracked). So the strongest prose I can write into a dispatch does NOT prevent a second
  writer — it only makes the breach legible afterwards. For a whole-file artifact with no merge
  path, the constraint needs a mechanical interlock, and an orchestrator should report the spawn
  count as a measured fact rather than trusting the instruction it issued.

- 2026-08-21: took D-4's count INDEPENDENTLY while the lead ran, so its receipt would be a check on
  mine rather than a restatement. At 7299669 in the FEAT-31 worktree: 30 `test-*.py` files in `bin/`,
  `UNIT_SCRIPTS` 18 + `INTEGRATION_SCRIPTS` 12 = 30, so the drift detector is fully satisfied — while
  `test_kinds.integration.detect` names only 4 of the 12, leaving EIGHT that the qa matrix reads as
  unit. The detector builds `ALL_SCRIPTS` from its own two bash arrays and never opens harness.json,
  so a gate is green on both halves of a contradiction. Cost: two bash calls, during time an
  orchestrator otherwise spends idle.

- 2026-08-21: **the operator's own receipt was incomplete and measuring it wider paid.** A-2 named
  FEAT-24's handoff note as the one sitting exactly on the 60-line cap; applying the predicate to
  the whole corpus found TEN at exactly 60. Separately, A-2 measured the empty-body rule against 3
  non-seam notes, but the approved glob widens INV-17 to all 69 — so all 69 are what must pass, and
  they do (0 heading failures, 0 cap failures, 0 empty `## Next`). Lesson: when a ruling widens a
  gate's REACH, re-measure over the new reach, not over the sample the ruling happened to cite.
  Confirming a cited number is weaker than measuring the set the change actually touches.

- 2026-08-21: two consecutive rounds lost their work to a turn ending while the lead still ran. The
  fix is ORDERING, not tooling: read, then dispatch, then keep turn in reserve to collect. I
  dispatched at my third tool call this round instead of my fifteenth, and spent the wait on
  read-only verification that made the eventual assessment cheap. My tool set is
  Read/Glob/Grep/Agent/Write/Bash — the `Agent` tool's own contract text mentions a `SendMessage`,
  but I do not hold it, so "no channel to a running lead" is measured for this persona, not assumed.

- 2026-08-21: a stale measurement inside enforcement-layer code survives indefinitely because
  nothing checks prose. `check-plan-routes.py:265` still reads "THE HONEST CAVEAT: `find .harness
  -name plan.yaml` returns ZERO … this budget has never been applied to a real file of the format it
  governs" — there are 21 `plan.yaml` files on disk in this worktree. I formed and then DISPROVED my
  own hypothesis that FEAT-31 would be the first such file, by running the find instead of reasoning
  from the comment. The comment is what would have misled a reader; the command settled it in one call.

- 2026-08-21: the ordering discipline held for a THIRD round and is now the settled way I run a build
  turn: verify the premise, dispatch, then spend the wait on bookkeeping that the dispatch does not
  depend on. This round the wait paid for the whole GitHub mirror (`open` + eight `start-task` calls),
  the feature.json status write, the STATE.md rewrite and the state gate — none of which the lead's
  result feeds into. The generalisable rule: sort the turn's work by whether it CONSUMES the lead's
  output, do everything that does not first, and never let a dispatch be the last call of a turn.

- 2026-08-21: I marked eight plan.yaml task statuses without ever rewriting the file, which is the
  technique that makes the issue-#628 hazard avoidable rather than merely warned about. A
  `harness_yaml` round-trip would have reserialised all 1026 lines and could silently reformat the
  signed `approval:` block; instead I asserted each target line equalled the exact literal
  `    status: pending` before touching it, edited by line NUMBER, and proved the blast radius after
  the fact with `git diff --numstat` (8 insertions / 8 deletions) plus a sha256 of the extracted
  `approval:` block matching `git show e5f88c4:` byte for byte. Assert-then-edit-by-line, then prove
  the diff is the shape you intended — a whole-file writer cannot make that proof.

- 2026-08-21: the `phase` contradiction is now settled at the SCHEMA, which is a stronger reading
  than the earlier guard observation. `bin/feature-schema.json` is `additionalProperties: false`
  with eleven declared properties and NO `phase` among them, so `check-domain.sh` rejecting the key
  is the schema working exactly as designed — the orchestrator playbook's "record your phase in
  feature.json `phase:`" is the side that is wrong, and no amount of retrying will land it. When a
  rule and a gate disagree, read the gate's DATA (the schema) rather than the gate's error text: the
  error says a write was refused, the schema says whether it could ever have succeeded.

- 2026-08-21: the STATE.md shape gate refused my rewrite at 127 lines against a 120 budget, and it
  was right to. The lesson is not "trim afterwards" but that a state file inherits the previous
  round's structure by default, and each round's genuinely-new material arrives on top of narrative
  the round before thought essential. Budget the file at write time by asking which sections the NEXT
  cycle must act on; the rest belongs in the run digest, which has no cap. A refused write cost one
  tool call here, but the same drift is why FEAT-05's STATE.md sits at 165 lines and is still flagged.
