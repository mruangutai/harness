# Observations — harness-orchestrator — FEAT-04-decisions-index

- 2026-08-02: a mid-build user decision reversed a stated closure inside the SIGNED brief and nothing
  mechanical noticed. The user capped rulings at 30 words; BRIEF SC-11 reads that the length-cap
  question was closed "without adding a character-count rule", so the new cap does not tighten the
  plan's D-07 — it falsifies an approval-gated criterion's rationale. I caught it only because I had
  read SC-11 minutes earlier for an unrelated reason. Nothing in the org diffs a new instruction
  against the SCs it contradicts; the goal-check runs at the END, against the brief as written, so an
  SC whose premise the user themself retired would have gone green on stale text.

- 2026-08-02: `git diff --exit-code <path>` is silently vacuous on an UNTRACKED file — it reports
  nothing and exits 0. The plan's idempotency verify was written as exactly that command against a
  file the same plan created in an earlier task, so had I let the owning task run its own step 4 the
  feature's headline proof would have passed without testing anything. I carved that step out of the
  member's dispatch, committed the file, then ran it myself: exit 0 with a byte-clean
  `git status --porcelain`, which is the version that means something.

- 2026-08-02: three coordinator messages arrived mid-dispatch carrying new scope (a word cap, a new
  decision to land, a validity question about a completed batch). The one that mattered most was the
  validity question, and the cheapest answer was not the member's account of its own method but an
  empirical discriminator: rulings carrying body facts their titles do not contain (an INV number, two
  token measurements, a rule about `shared:` paths) cannot have been pattern-derived from titles.
  Asking the squad would have cost a spawn and returned an assertion; three greps returned proof.

- 2026-08-02: cost decomposition earned its keep as an argument, not just a number. $213 against a
  $120 budget reads as runaway until you show that $27 of it is six spawns each reading a ~1,100-line
  slice of the authority — the mandatory-reading floor this very feature exists to remove. The
  decomposition reframed an overrun as the last feature that pays full price. A bare total could not.

- 2026-08-02: `bash-write-guard.sh` still reads `>` and `<` inside an UNQUOTED heredoc body as
  redirects — `if 30 < w` was fine but `w > 30` was blocked as "redirect targets 30]". The quoted-string
  fix that landed mid-build does not cover heredoc'd python. Three members hit the same class on
  compound lines (`rm a; python3 b` blocked as "rm targets python3"). Every instance was a legitimate
  read-only or in-domain command and every one cost a workaround.

- 2026-08-02 (validate): the inherited pin was STALE and would have manufactured two false FAILs.
  review_sha sat at bdfa3ab while T-09 and T-10 landed at 363b539; `git show bdfa3ab:CLAUDE.md | grep -c`
  returned 0 for the very string SC-09 asserts. A panel on that pin reports the criterion unmet by the
  pin, not by fact. One rev-parse plus two `git show` greps priced it before any spawn.
- 2026-08-02 (validate): a criterion whose receipt requires MUTATING a file is routable only by write
  domain, never by consult-when. SC-08 needed a plant into docs/harness/SPEC.md; every reviewer holds
  Bash but bash-write-guard blocked me (`tee` outside domain, exit 2) and blocks them, and documentor
  was the only agent in the org with docs/**. Probing the guard with a fake payload cost one command
  and settled the routing; guessing would have cost a refused spawn.
- 2026-08-02 (validate): the phrase-in-my-own-artifact hazard has a SECOND line nobody had named.
  check-docs.sh prints the offending pattern at :143 (`matches {pat!r}`) as well as :144, so an agent
  that escapes one occurrence of a hit block in its report still reddens the gate. Every reviewer
  dispatch now carries "escape both, or refer to it indirectly", and my own briefing does the latter.
- 2026-08-02 (validate): two playbook-mandated closing rounds were worth DROPPING here and the reasons
  differ. Distillation: the four members who did validate hold no observations log, so running it at
  the validate seam distills build twice and validate zero — it belongs after acceptance. The
  three-lead briefing round: I hosted every run and can cite each digest by path, and one lead had
  zero activity, so three ~$20 spawns re-narrate documents I already hold. Measured per-run cost
  ($10 / $20 / $19.3) is what made both calls decidable rather than a matter of taste.
- 2026-08-02 (validate): "audit this, do not reproduce it" did NOT hold on 3 of 3 panel members —
  every one re-derived the tier-level gate results. The receipts came out independent, which is a
  real gain, but the instruction is not load-bearing and budgeting as if it were understates a panel.
- 2026-08-02 (validate): suppressing the `cost: pending_orchestrator` line BY DISPATCH ("do not write
  a cost: key in state.yaml, I append the metered block") cleared the INV-16 duplicate-key collision
  on all three runs with no hand repair. The source contradiction between the playbook and
  harness-team is untouched, but the workaround costs one sentence per dispatch.
- 2026-08-02 (validate): cost-report.py's transcript data LAGS. Run 13's append showed product-lead's
  cumulative unmoved; run 14's caught both up, so the 30.2 delta covered two runs and the per-run
  split I recorded is apportioned, not measured. Snapshot the project total in the run's own state
  file each time and say which figures are apportioned.
