# Handoff — FEAT-05 build → validate

## Next

- **RE-PIN `review_sha` before reviewing.** `feature.yaml:6` says `225cc98`; that was the
  baseline when the orchestrator stood down and **13 commits have landed since**. Diffing
  the recorded SHA reviews almost none of the work.
- The build ran **main-session, not a team** (DEC-174, taken mid-feature): the harness
  plans changes to its own enforcement layer but does not execute them through a run whose
  gates are the thing being changed. Expect no member digests for T-07..T-17.
- SC-09 stays `not_met` until the user runs `notes/uat-bootstrap-escape-expiry.md`. Ship
  gates on it (`harness.json:244`). Do not mark it passed.

## Trust

- **Trust the receipts over the plan's line numbers.** Every `:NN` in PLAN.md predates the
  conversions; the counts (census 10→7, 7→5) hold, the positions do not.
- **Trust the measurements over T-09's receipt.** It inferred that the main checkout's hook
  copy runs; two probes disproved it (11 and 21 fires, all from the worktree). It flagged
  that alternative itself — the caveat was right, the conclusion wrong.
- **Distrust any "verified" claim of mine that is not a receipt.** I asserted twice that
  DEC-173 was not in force here, on the strength of the two files *differing* rather than
  measuring which *runs*. Both retractions are in `PLAN.md` Amendment 2.
- Equivalence for T-13/T-15 is byte-level: 11/11 and 12/12 payload shapes identical in exit
  code **and stderr bytes** against pre-change copies, not just passing tests.

## Dead ends

- **Do not "resync" the two duplicate-key detectors.** `check-domain.sh` raises via the
  loader, `check-state.sh` scans — same vocabulary, deliberately different mechanism (D-02).
  The comment at the `ALLOWED` set says so; reverting it re-opens the fail-open.
- **Do not move `import harness_yaml` to the top of either hook.** It is lazy on purpose so
  a missing module still reaches the absent-manifest fail-open. T-13 shipped that bug; a
  test caught it.
- **Do not test the escape at module level only.** `test-harness-yaml.py` proves the state
  machine via `payload={"session_id":...}` — a **dead** identity entry in production. Two
  real defects hid behind it (see below).
- A single-key fixture cannot prove the typed-key coercion: `{True}` sorts fine. Mixed types
  are what raise.

## Working set

- **Hooks:** `check-domain.sh`, `bash-write-guard.sh` — both parse the manifest via
  `harness_yaml.manifest_domains()`; one shared walk, so they cannot diverge (D-03).
- **Module:** `harness_yaml.py` — the only `try: import yaml` in the tree (D-12).
- **Readers:** `check-state.sh` (closes issue #11), `gh-sync.py`, `upgrade-config.py`.
- **Gate:** `test-harness-yaml-corpus.py` — walks every `.harness/**/*.yaml`; its negative
  fixtures are load-bearing, an always-green validity gate is no gate.
- **Receipts:** `receipt-main-session-hook-resolution-probe.md` (Q3/Q6),
  `receipt-main-session-q4-session-identity.md` (Q4),
  `receipt-harness-backend-dev-typed-value-sweep.md` (SC-10, both halves).
- **Two defects worth re-reading in the diff** (commit `0775862`): both hooks discarded
  `require_or_bootstrap`'s return value, so the escape could open but never close; and the
  grant path then crashed into `yaml = None`, exiting 1 — which is non-blocking, so it
  looked like success while enforcement was off.
- **Backlog:** issue #16 (D-09, `review_sha: none` is truthy) filed and reproduced;
  issue #12 recommended for closure as not-a-defect (0 mismatches found).
