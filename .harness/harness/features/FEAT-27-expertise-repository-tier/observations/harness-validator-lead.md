# Observations — harness-validator-lead — FEAT-27

- 2026-08-19: qa segment, T-02/T-03 matrix gate at 2117a46. I relayed a ruling to qa saying the
  stale `integration.detect` glob "never enters T-03's obligation". That overstates it —
  `harness-qa-gate/SKILL.md:57` explicitly directs the gate to use `detect` globs to confirm a
  covering test exists, so the stale glob DOES feed the step-4 presence check. The ruling still
  holds, but the correct footing is `:96` ("a runner that silently matched nothing has told you the
  glob is wrong") keyed on the RUNNER's discovery, plus `:73` defining `satisfied` as "at least one
  named test ran, none failed" — named tests, not globs. `run-unit-tests.sh --kind integration`
  discovers and runs `test-check-expertise.py`, so neither the FAIL at `:74` nor the BLOCKED at
  `:76`/`:96` fires. Lesson: when a dispatch hands me a ruling to relay, re-derive its mechanism
  before passing it down, because the member inherits my error and cannot see past it.

- 2026-08-19: I passed qa a leading hypothesis that `agent_type: "harness-*"` would, with the
  `^harness-[a-z0-9-]+$` regex removed, glob-match a real repository-tier file and therefore bind
  the validation against regression. It is FALSE and I measured it at source:
  `inject-expertise.sh:68` is `for f in "$root"/.harness/*/expertise/"$agent.md"`, where
  `"$agent.md"` is a QUOTED expansion — bash pathname expansion does not treat characters from a
  quoted portion as glob-active, so the value's `*` stays literal and looks for a file named
  `harness-*.md`. Case 12's temp root writes `harness-qa.md` (`test-inject-expertise.py:292`), not
  that. qa independently reached the same conclusion by mutation. Cost of the error: I handed a
  member a leading question on the one item I had asked it to assess independently, so its answer
  on that sub-item is worth less as evidence than it should be. Two derivations rescued it here;
  that was luck, not design.

- 2026-08-19: The eng squad's RED proofs (both dev-ops receipts) are against pre-change baseline
  `b4659cd`. That proves the new cases discriminate the feature's ARRIVAL. It does not prove they
  pin the behavior against REGRESSION, which needs mutation of the post-change script. These are
  different claims and only the second survives an edit. Worth carrying: a receipt that says
  "proven RED first" is answering the arrival question, and a lead reading it as regression
  assurance is reading in a guarantee that was never measured. On this feature both now exist —
  eng supplied arrival, qa supplied regression — and it took two squads to get there.

- 2026-08-19: Both of qa's coverage gaps have the same shape and it is worth naming as a class:
  the shipped code is CORRECT and nothing holds it there. The `[ -r ]` guard in
  `inject-expertise.sh`'s glob loop correctly skips an unreadable repository-tier file, but no
  fixture builds that file, so a mutant removing the guard survives 18/18. Intent 1c's
  `^harness-[a-z0-9-]+$` suffix rule correctly rejects hostile agent names, but every value case 12
  tries is vacuous, so a mutant removing the regex also survives. "Verified correct at source" and
  "pinned against regression" are two findings, and only the second survives a future edit.

- 2026-08-19: T-03's `verify:` asserts `^ADVISORY ` against the LIVE `.harness/expertise/` corpus
  rather than a fixture. It is green today only because the sixteen token-carrying entries are
  still in the craft tier, and it survives T-04 only because five of those sixteen were adjudicated
  to REMAIN craft (plan D-03). A verify clause whose truth depends on corpus state that no fixture
  pins is a latent flake, and the coupling is invisible from inside either task.

- 2026-08-19: Three different numbers describe the same live corpus and none is interchangeable:
  29 ADVISORY LINES (qa, from the checker's own output at 2117a46), 19 token LINE-OCCURRENCES
  across 7 files (eng lead's pre-dispatch grep), 16 flagged ENTRIES (BRIEF). Lines, line-occurrences
  and entries are three units. Carrying any one forward as "the count" would have been a false
  claim built from true measurements.

- 2026-08-19: Process defect on my side — I attempted to send a mid-run course correction to a
  running member and had no channel for it (leads hold Read/Glob/Grep/Agent/Write; no message tool).
  I burned a spawn on a placeholder discovering this. A correction that occurs to me after dispatch
  either waits for the return or costs a send-back; there is no cheap third option, so the dispatch
  prompt has to be right at write time.

- 2026-08-19: Polling the filesystem for a member's artifact is NOT a wait — tool calls return
  instantly and buy no wall-clock time, so ~50 polls advanced the run by nothing. The only real
  yield point is the end of a turn. Waiting on an in-flight member is not something a lead can do
  by looping.

- 2026-08-19 (qa-final): I repeated the no-channel mistake in a NEW form and it was expensive. I
  reached for `Agent` with `subagent_type: fork` as a placeholder to fill a wait, and a fork
  INHERITS THE PARENT'S FULL CONTEXT — the no-op returned the single word "noop" and still billed
  212k subagent tokens, roughly 2.5x the entire real send-back that followed (83k). A fork is never
  a cheap placeholder. And the send-back itself is a fresh `Agent` dispatch to the same persona with
  the prior artifact's PATH injected, not a message to the running agent; there is no SendMessage at
  the lead tier.

- 2026-08-19 (qa-final): The single highest-yield thing I did all segment was derive findings AT
  SOURCE during the in-flight wait, then route them back as a narrow send-back carrying ONE
  PREDICTION PER ITEM ("mutate `150`→other at `:100`, I predict 19/19"). Four claims I could not
  test (no Bash at the lead tier) became four measurements for one spawn, and every prediction
  held. The prediction format is what made it cheap: the member had only to run the mutant and
  report, not re-derive my reasoning. Generalise: when I lack a shell, a send-back with falsifiable
  per-item predictions is strictly better than either publishing an assumption or re-dispatching a
  vague "look again".

- 2026-08-19 (qa-final): "Green under an unrelated mutant" is NOT vacuity, and I nearly let a member
  and an eng lead entrench the opposite. case11's `"Traceback" not in stderr` was reported by two
  squads as a could-not-fail assertion because it stays green under T-07's guard-removal mutant.
  But case11's fixture contains no unreadable file at all — that mutant is INERT in its world. Run
  against the mutant case11 actually exists to catch (a YAML parse dependency added to the hook), it
  reddens. A vacuity claim is only meaningful against the assertion's OWN intended mutant; by the
  looser test most correct assertions in any suite are "vacuous". The narrower real weakness
  survived the correction: the `Traceback` substring misses SHELL-emitted noise, so `stderr == ""`
  is still the right remedy — for a different reason than the one given.

- 2026-08-19 (qa-final): A member's "swept thoroughly, no more found" is a claim to check, not a
  result to accept. qa declared `test-inject-expertise.py` (all 13 cases) thoroughly swept and
  returned "exactly four, no more"; I found two further items INSIDE that file by reading source
  during the wait, and an independent squad's simplify pass had found the same two without seeing my
  work. Two independent derivations of items a sweep declared absent means the sweep's METHOD missed
  a class, which is a different and more useful finding than the two items themselves. Final census:
  six, not four, with one of the handed-down four refuted outright.

- 2026-08-19 (qa-final): When one mutant flips TWO assertions, neither is individually
  load-bearing — and the overstatement is easy to miss because it sits beside the correct
  measurement. qa's own observations log recorded `checks=[True,True,True,False,False]` (indices 3
  AND 4 flip) in one bullet and, six lines later, that `stderr == ""` "is load-bearing" and a weaker
  form "would have stayed green under the exact mutant it exists to catch". The second is false:
  `"kaya" not in ctx` reddens case13 on its own. The same overstatement had already propagated into
  a research note and pm's log — three artifacts, all tracing to one un-split per-assertion record.
  Check a discriminator claim against the per-assertion flip record, which is usually right there.

- 2026-08-19 (qa-final): Eight prior runs on this feature all reported `cycles_used: 0` and
  `must_fix: []` — zero send-backs and zero blocking findings across the whole build, on a feature
  whose SUBJECT is test quality and which has now surfaced six assertions that cannot fail. Mine was
  the feature's first pushback. A review tier that never sends anything back is not evidence of
  flawless work; on this feature the census is direct evidence of the other reading.

- 2026-08-19 (panel): Dispatching the reviewer I fully expected to scope out was the highest-yield
  decision of the run, and I nearly skipped it. I told `ui-reviewer` there was no UI and no
  `DESIGN.md` — both true, and it confirmed them by census — but I also named an ADJACENT surface in
  its remit (the hook's emitted header text and the checker's advisory line). It came back with the
  panel's most interesting finding: the precedence line is emitted only when a repository block is
  present, so a global+project spawn now gets two un-arbitrated Expertise blocks where the pre-diff
  project header carried "authoritative on conflict" unconditionally. Generalise: a scoped-out
  reviewer is worth dispatching WITH a named adjacent surface, because the decline costs little and
  the adjacency is where its lens still reaches. Skipping it on my own prediction would have cost
  the finding outright.

- 2026-08-19 (panel): A finding gets stronger when I read it against a document the member did not
  have. `ui` rated the precedence gap `low` as a coverage gap. Reading it beside
  `arch-review.md:117-121` — "Emit one precedence line WITH THE BLOCKS", no condition, with the
  rationale at `:107-109` that an agent holding two blocks has only the headers to arbitrate with —
  turns it into a deviation from a REVIEWED RESOLUTION, which is a different and heavier finding.
  The member could not have done this: the arch review was not in the file set I gave it. Lesson:
  when a member reports a design-adjacent gap, check it against the review that settled the design,
  and consider whether my own file set omitted the document that would have re-rated it.

- 2026-08-19 (panel): I routed two measurements to a member that its own log said could not make
  them. C-2 and C-4 both needed FIXTURES, and `code-reviewer`'s c0 observations stated its Bash
  writes were blocked "even against the scratchpad". `qa` holds `Write` and `Bash` outright and was
  the correct owner. The measurements only landed because that blanket claim was itself wrong — the
  guard fires on shell REDIRECT syntax, not on an inline `python3 -c` write — and the member
  corrected its own log. I got four reproductions by luck. Before routing a measurement, check the
  member's CAPABILITY against the manifest rather than against its own prose summary of the
  capability, which is exactly the failure my G-12 already names in the opposite direction.

- 2026-08-19 (panel): The most valuable ranking move at this tier is re-ordering against WHAT
  HAPPENS NEXT, not against severity. This feature's next acts are goal-check, close-out and
  distillation — so a stale `STATE.md` and a wrong budget in the checklist a distiller is about to
  follow (`harness-curate/SKILL.md:34` says 150 where the repository tier is 40) both outrank three
  `med`s touching nothing imminent. No member can see the next step; every one of them ranks inside
  its own lens. Related and worth carrying: look for the SINGLE remedy that closes several findings
  — here one fixture writing `$HOME/.harness/expertise/<agent>.md` closes two handed-down census
  items and makes a third finding testable at all, and that leverage was invisible from every
  individual lens including, at first, my own.

- 2026-08-19 (panel): An interim prose reply at the lead tier is a TURN END, and the digest
  validator rejects it — I posted a "waiting on the panel" status and got a contract violation
  naming every missing DIGEST field. There is no way for a lead to yield mid-run: I must either
  return a complete digest or keep making tool calls. Combined with the earlier lesson that polling
  buys no wall-clock, the honest conclusion is that a lead waiting on members should spend the wait
  on independent source reading it can later use to ADJUDICATE, because that is the only activity
  that converts the unavoidable burn into value. Half this run's findings came out of that wait.
