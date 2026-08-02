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
