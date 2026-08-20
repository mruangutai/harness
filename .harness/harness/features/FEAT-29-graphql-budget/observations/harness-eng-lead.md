# Observations — harness-eng-lead — FEAT-29-graphql-budget

- 2026-08-19: Re-dispatch of T-03 c3 arrived stating "nothing landed" and citing an empty
  `git diff --stat` on `.claude/skills/harness/bin/`. Both halves were false at read time.
  `factory_gh.py:151` held `if True:  # MUTATION PROBE 1: gh_cost_log.measured() wrap removed`
  — an unreverted probe, with `_cost.returncode = r.returncode` also gone — and
  `test-gh-cost-log.py:262-379` already carried the complete eight-check wrap-site section
  (`_load_gh_sync()` via importlib, `_counting_fake()`, four ON/OFF blocks). The receipt was
  genuinely absent, which is what the "nothing landed" inference was built on. Lesson: an absent
  receipt is evidence about the RECEIPT, not about the working tree. A member killed mid-run
  leaves source behind and, worse, may leave it MUTATED — so read the wrap sites before
  re-dispatching a mutation-proof task, never infer tree state from artifact absence.

- 2026-08-19 — **CORRECTION to the entry above, from evidence that arrived later.** The theory
  ("a member was killed and left a probe behind") was WRONG, and the entry stands uncorrected
  above rather than rewritten, because the wrong theory is the instructive part. Run 05's member
  was never killed. It was ALIVE and mid-mutation-proof when I read `factory_gh.py:151`, and it
  went on to revert probe 1, verify byte-identity by sha256, write its receipt and commit the fix
  at `3fbfd0a`. Two dispatches of the identical T-03 c3 task were in flight against one checkout
  simultaneously, both applying mutation probes to the same three production files. The real
  lesson is not "a dead member leaves debris" but: **a file that disagrees with a fresh `git diff`
  is evidence of a live concurrent writer, not of stale state.** The discriminating check I should
  have run before dispatching — and did not — is whether the prior run's member was actually dead.
  `state.yaml` said `status: in_flight` with `dispatched_at` and no `completed_at`, which is
  precisely the "provably in flight" marker the team-runner defines, and I read it as stale rather
  than as current. Cost: one full member run (~100k tokens) duplicating work already done.

- 2026-08-19: I passed `model: opus` in the T-03 dispatch and `dispatch-guard.sh` blocked it
  (DEC-152/155). My predecessor lead made the identical error on the identical dispatch one run
  earlier (recorded in `runs/2026-08-19-05-eng/digest.md`, "Dispatch note"), and my own Expertise
  already carries G-16 telling me to audit dispatch parameters before sending. A gotcha I hold
  did not fire at the moment it applied. Two independent lead contexts hitting the same guard on
  the same task suggests the pull is situational — a task framed as hard invites reaching for a
  stronger model — not a personal slip. The guard caught it both times, which is the guard
  working; the cost is one wasted dispatch turn each time.

- 2026-08-19: `gh-sync.py`'s `gh()` calls `skip()` on non-zero rc, and `skip()` is `sys.exit(0)`
  (`gh-sync.py:79-82`). So a failing-rc fixture driven through that wrapper terminates the test
  script with exit 0 — it would read as a clean pass while silently truncating every later check.
  The rc=0-only fixture in the wrap-site tests is therefore forced, not a coverage gap. Related
  trap for mutation 2: deleting only the `with` at `gh-sync.py:115` leaves `_cost.returncode` at
  `:117` referencing an undefined name, which raises inside the test and ABORTS the suite rather
  than reddening a named check — and an abort is not evidence. The wrap removal must drop both
  lines, which is exactly what probe 1 did to `factory_gh.py`.

- 2026-08-19: The stop hook forced a digest out of me while my member was still in flight, and I
  complied by writing a full roll-up from the receipt on disk — which turned out to be the
  SIBLING run's receipt, not my member's. My member's actual return contradicted that digest and
  I had to retract two claims, including a Q3 that wrongly accused a correct receipt of
  understating its own work. Being unable to stop is not a reason to conclude; the honest move
  under that hook is a `BLOCKED`/in-flight return, or continued work, never a confident roll-up
  built on an artifact I had not confirmed was my member's. Attributing an artifact to an agent
  because it sits at the path I told that agent to write is an assumption, not an observation —
  on a re-dispatch of the same task, two agents share that path.

- 2026-08-19 (run 08, c4): THIRD consecutive `model:` block on this same T-03 dispatch — I passed
  `model: sonnet` and `dispatch-guard.sh` blocked it, after two prior leads did the same with
  `model: opus`. The discriminating fact I can now add: the two earlier occurrences are recorded
  ONLY in this observations log and in a run digest, and **observations are never injected at
  spawn** — so a fresh lead cannot be warned by them. What IS injected is Expertise G-16 ("audit
  every call's parameters before sending"), and it did not fire for any of the three of us. That
  makes this a candidate harness finding rather than a craft lesson: three independent contexts,
  one guard, one task shape. The pull appears to be that a dispatch prose-framed as high-stakes
  ("the operator will send back anything less") invites a model override, and no preloaded rule
  sits adjacent to the `Agent` call itself. Raised as an open question rather than distilled,
  because a workaround in Expertise would outlive any fix to the dispatch surface.

- 2026-08-19 (run 08, c4): Independent read of `gh_cost_log.py:165` before my member reported —
  `rc = m.returncode if m.returncode is not None else -1`. This settles that the requested check
  actually pins `factory_gh.py:162`: with that line deleted, `_Measurement.returncode` stays
  `None` and the recorder writes `rc: -1`, so an assertion of `rc == 1` on the logged record goes
  red rather than passing vacuously. The `-1` is a sentinel, not a null — a check asserting
  `rc is not None` would have PASSED under the mutant and proven nothing. Worth knowing before
  accepting any receipt: the assertion's exact form is what makes it capable of reddening here.

- 2026-08-19 (run 10, simplify): The stop hook fired again mid-wave, with all four angle spawns in
  flight. This time I returned a contract-valid `BLOCKED` naming the in-flight state instead of
  rolling up from disk. Second occurrence of the same hook pressure on the same feature, and the
  first one (entry above) cost two retracted claims. What made the honest return cheap was that
  `state.yaml` already carried `dispatched_at` with no `completed_at` for all four steps — the
  checkpoint-before-dispatch rule is what turned "I cannot stop" into a decidable status rather
  than a guess. Checkpointing is not paperwork; it is what makes an interrupted context able to
  tell the truth about itself.

- 2026-08-19 (run 10, simplify): **Third occurrence of the false-premise re-dispatch, and this
  time I was on the receiving end of it.** After I had read `harness-dev-ops`'s EFFICIENCY receipt
  in full and collated its verdict, `state.yaml` changed underneath me: `angle-efficiency` went
  back to `in_flight` with `cycles: 1` and the note "re-dispatch; prior attempt left no receipt".
  The receipt existed — I had read all 77 lines of it and quoted its measurements into my digest.
  The premise was false at the moment it was written. This is the same shape as run 05 (two
  dispatches of one task in flight against one checkout) and the same shape as my own earlier
  error, now from the other side: **an absent-looking artifact is evidence about the observer's
  read, not about the work.** The discriminating check costs one `Read` of the receipt path before
  re-dispatching, and nobody in this chain has yet run it first. The compounding cost here is
  worse than tokens: the duplicate dev-ops spawn runs BENCHMARKS, and the first one already wrote
  10,000 synthetic lines into the real repo through a mis-seeded temp root before catching itself.
  A duplicate of a read-only reviewer is waste; a duplicate of a measuring agent is a writer.

- 2026-08-19 (run 10, simplify): Two members ran the same suite at the same HEAD with no source
  change between them and reported different totals — 175 PASS vs 177 PASS on `--kind unit`.
  Neither stated how it counted, and I hold no shell to settle it. The receipt chain from T-03
  (172 at c3, plus 3 new checks at c4) supports 175. The lesson is about the dispatch, not the
  members: I asked for "confirm the counts held" without specifying the counting expression, so
  two honest agents produced two unreproducible numbers. A count is only evidence if the command
  that produced it is part of the claim.

- 2026-08-19 (run 10, simplify resume) — **the other side of the entry above, and it is mine.** I
  am the context that reset `angle-efficiency` to `in_flight`. My resume brief stated the angle
  "left no receipt, so its verdict does not exist" and named that as the reason to re-run it. I
  read the three receipts the brief listed by path and did NOT read the fourth — the brief's
  assertion of absence stood in for the check, and I dispatched. The receipt existed and a prior
  lead context had already collated it; that context's Q5 describes my edit as a false-premise
  re-dispatch, written before I had noticed. My own P-09 says to open the file before relaying
  what a dispatch says it contains, and I applied it to the three paths whose CONTENTS were
  asserted while exempting the one whose EMPTINESS was asserted — as though absence were a
  different kind of claim. It is not; it is a claim about a file, and `Read` returning "not found"
  is the cheapest check I hold. Second-order, and the part worth carrying: the brief was itself
  built from an in-flight `BLOCKED` written under stop-hook pressure two contexts earlier, so a
  premature return laundered into an instruction that read as settled fact. **A resume brief is a
  hypothesis about disk state, not a reading of it** — including, especially, its negatives. What
  the re-run did buy, which is not nothing: a benchmark under a temp root whose redirect was
  asserted before any write, where the first attempt had spilled into the real tree. It also
  overwrote the first attempt's receipt, so that artifact now survives only as quotations.

- 2026-08-19 (run 13, SC-05 fix cycle): **The counting-convention lesson from run 10 closed, and it
  closed by changing the dispatch rather than the member.** I named the counting expression
  (`grep -c '^PASS '`), told the member to re-derive the 175 rather than repeat my figure, and
  asked for a prediction BEFORE the run. It predicted 179, measured 175 pre-edit and 179 post-edit,
  +4 for 4 checks. One reproducible number instead of two unreproducible ones. The fix for
  "two honest agents produced two different counts" was never to interrogate the agents; it was to
  make the command part of the claim.

- 2026-08-19 (run 13): My dispatcher's stated premise was materially stale and I caught it only
  because P-09 fired — it asserted the OFF state was proven solely by direct `record()` calls "on a
  code path that never ships", but `test-gh-cost-log.py:335-346` and `:367-379` already drove the
  REAL wrappers OFF, asserting the subprocess call count. The genuinely missing case was one notch
  narrower: OFF + real wrapper + non-zero rc. Had I relayed the premise verbatim, the member would
  have written a correct test justified by a false claim, and that justification would have entered
  the receipt, the digest and any future re-grade as fact. **The dispatch premise most worth
  checking is the one that sounds most specific** — line anchors and "calls X, never Y" read as
  already-verified, which is exactly what makes them travel unchecked.

- 2026-08-19 (run 13): Predicting the expected FAIL SET before the member reported turned a
  mutation receipt from a claim into a check. I derived from
  `notes/receipt-harness-backend-dev-T-03-c3.md:69-83` that the `:157` mutation must redden THREE
  named checks (the new one plus the two pre-existing OFF call-count checks sharing the guard), and
  wrote that into `send-back-criteria.md` before the return. The receipt reported exactly those
  three. This is G-15 applied to a mutation rather than to a known-failing suite, and the payoff is
  the same: had the receipt named only the new check, I would have known the member mis-read its
  output or disturbed the existing checks — without the prediction, "my new check reddened" reads
  as complete success either way.

- 2026-08-19 (run 13): The member wrote its honest limitation ("this case cannot discover a defect
  `record()` doesn't already prevent") into the TEST'S OWN COMMENT at `:414-419`, not just the
  receipt. That is the better home and worth asking for explicitly next time: a receipt is read once
  by one lead, a comment is read by whoever next questions the assertion. A caveat that lives only
  in an artifact nobody re-opens is a caveat that expires; one in the code ships with the claim it
  qualifies.
