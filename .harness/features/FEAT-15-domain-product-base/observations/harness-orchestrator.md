# Observations — harness-orchestrator — FEAT-15-domain-product-base

- 2026-08-10: I wrote a marker grammar into the dispatch prompt
  (`execution_mode: <mode> — reason: <text>`) copied from FEAT-07's `PLAN.md`. That shape is
  UNLOADABLE in a `plan.yaml` — `templates/plan.yaml:7-8` documents it as breaking `safe_load`
  because a second `": "` lands inside a plain scalar. pm rendered sibling keys
  (`execution_mode` + `execution_reason`) instead and was right. Carrying a pre-DEC-182 `PLAN.md`
  precedent into a `plan.yaml` dispatch is a format transposition error, not a citation.

- 2026-08-10: My dispatch asserted the concurrent flows were disjoint on the basis that they touch
  different FILES. That test is wrong when the feature changes a RESOLVER other plans are checked
  against. `check-plan-routes.py` is run tree-wide by `tests.yml:109` as a required check, so
  FEAT-15's change to `check-domain.sh --resolve` would have turned two other approved plans
  (FEAT-12, FEAT-14) red without sharing a single file with them. The lead caught FEAT-12; I found
  FEAT-14 only by running the checker myself. Measured: `0 violation(s) across 10 plan(s)` today.

- 2026-08-10: The grilling artifact stated ruling 1's cost as an accepted FUTURE risk ("a future
  control-plane path not starting with those prefixes"). It was already live: `docs/**`,
  `README.md` and `.github/**` are present control-plane paths in this self-hosted repo, granted to
  documentor and dev-ops. I found this with one grep before dispatching, and it became the
  feature's blocking question. A grilling's "accepted risk" phrased in the future tense is worth one
  grep against the present tree before it is carried forward as hypothetical.

- 2026-08-10: The advisor's suggestion that the plan might falsify its own route check (FEAT-15 T-05
  on `docs/harness/DECISIONS.md`) was checkable in one read of `check-plan-routes.py:188-210`:
  `main-session-direct` + ungranted is the `OK` branch, so T-05 goes DEVIATION → OK. Reading the
  verdict logic beat reasoning about it, and it kept a send-back from being issued for nothing.

- 2026-08-10 (revision cycle): The operator asked me to MEASURE whether Q2 dissolved rather than
  assert it. The cheap faithful way was to import `check-plan-routes.py` as a module and monkeypatch
  only `resolve_agents`, keeping its real parser and plan discovery. That took one script and
  returned a decisive answer (0 violations, ZERO paths flipped) where reasoning would have produced
  a confident guess. Swapping ONE function out of a real gate is a better simulation than
  re-implementing its logic — the parser is the part that is hard to get right, and it is exactly
  the part worth not re-writing.

- 2026-08-10: My own simulation was structurally blind in a direction I did not notice until it was
  pointed out: it modelled only IN-HARNESS resolution, so it could not see a dual-base error that
  would land entirely on the product side. A clean measurement invites over-trust. WHEN a
  simulation returns a clean number DO state what it is silent about in the same breath, or the
  number will be read as covering more than it does.

- 2026-08-10: `check-state.sh` flagged four violations in MY OWN `STATE.md` — it parses bare `T-NN`
  tokens and cross-checks them against THIS feature's plan, so naming another feature's task ids in
  prose (FEAT-12's T-12/T-14, FEAT-14's T-09/T-10) reads as dangling references. Write foreign task
  ids in words, never in the `T-NN` form. product-lead caught this before I did; running
  `check-state.sh` on my own artifacts should be part of recording, not something a lead reports.

- 2026-08-10: I nearly wrote `cycles_used: 0` on the revision because the revision run itself had
  zero send-backs. The first run had one, and the counter is cumulative for the feature. A phase
  boundary is exactly where a cumulative counter gets silently reset to the current run's value.

- 2026-08-10: A count in an artifact produced three different answers from three readers (BRIEF said
  five in-root allow assertions, product-lead counted six, I counted four) because the phrase never
  pinned its counting rule. The right output was not a fourth number but the recommendation to
  strike the count — the dispositions it decorated were independently verified and correct. WHEN
  two readers disagree on a tally DO check whether the counting rule is even specified before
  spending a cycle adjudicating the number.
