# Goal-check — FEAT-10, 20 success criteria, working tree (nothing committed)

## BLUF

**16 of 20 met, 4 unmet: SC-06, SC-13, SC-18, SC-19.** Verdict ESCALATE, not FAIL: SC-06's only
remedy is T-08, which no squad may execute under the DEC-174 carve-out, so looping back to the build
tier is futile. SC-13/SC-18/SC-19 are ordinary build gaps and could go back to qa.

**The bar applied, stated once.** A criterion is met when every clause of its BRIEF text is
demonstrated **by evidence of that criterion's own declared method**. A clause with **zero**
assertion of its declared method makes the criterion unmet. A clause asserted but not exhaustively
stays met with the narrowness named. The three non-SC-06 unmets are all the first case.

**Suites re-run by me, unpiped.** `run-unit-tests.sh --kind unit` exit 0, `--kind integration` exit
0. All seven `test-factory-*.py` files report `PASS`, `test-factory-integration.py` reports `PASS`,
zero `FAIL` lines in either log. `check-docs.sh` exit 0, unpiped, `no stale statements found`.
BRIEF counts re-derived here, not inherited: 20 SC ids, 15 `evidence: unit`, 3 `evidence:
integration`, 2 `verify: inspection` (lines 213 and 231; a third grep hit at line 290 is prose),
0 `verify: uat`.

## The four unmet

- **SC-06 — unmet, and not finessable.** Its evidence is `check-state.sh` INV-24. `grep -rn INV-24
  .claude/skills/harness/bin/` returns nothing (exit 1). T-08 is withheld from every squad; only the
  main session can land it. Not waived, not substituted.
- **SC-19 — three clauses unbound in the forked journey (Case F,
  `test-factory-integration.py:574+`).** "boards them at `ready`" has no assertion after decompose —
  the station is only ever read as `Building` and `Review`, later. "land pushes that branch" has no
  assertion; only exit 0 and a payload URL. "workspace produces a checkout" is bound as a payload
  string, not a filesystem or HEAD state — the fixture pre-creates `.git` and stub git does nothing.
  Case G's real-`git` HEAD check is a separate fixture, not the journey. The unit suites bind all
  three (decompose case (2) station-is-ready, land M1 push), but SC-19's declared method is
  `integration` and its text names the forked run.
- **SC-13 — the resting condition is unbound.** Clause (a)'s five unclaimable conditions are covered
  (R3's four plus B1's blocked case), and clause (b) is covered by R2 route1/route2 and B2. But "no
  two of those reasons read alike" is demonstrated only by reading the five stderr strings in
  `factory_claim.py` (:277, :281, :286, :302 via `_blocker_reason_text`, :315). R3's four cases
  assert exit 0 and `#92` and never touch stderr; R2's `err1 != err2` is route-level, not
  reason-level. A source read is not `unit` evidence.
- **SC-18 — "one fleet loader is the only reader of the fleet file" is unbound.** Round-trip (case
  1), `--show` JSON (23), `workspace_path` sharing (22) are all unit-bound. Exclusivity is bound only
  by my grep: `factory_config.py` is the sole module naming `fleet.yaml`/`FLEET_PATH`, and
  `factory_land.py:59` and `factory_workspace.py:117` both call `factory_config.workspace_path`. No
  unit case asserts it.

## Clause counts on the four the dispatch named

- **SC-22 — 9 clauses, 9 covered, one narrowly.** claim-the-clear-candidate (B1), asserted as the
  exact `create_ref` issue number exactly once (B1), all-blocked → exit 1 + zero mutating calls +
  `no claimable work` (B2, all three), blockers-closed → formerly blocked IS claimed (B3),
  multi-blocker skipped until the last closes (B4, both halves), unresolvable `depends_on` blocked
  (B5), no `feature:` label not gated (B6, plus no plan file consulted), fresh `--issue` on blocked →
  exit 2 (B7) distinguishable from exit 3 (R4). **Narrow:** "a reason distinct from every other skip
  reason" is asserted pairwise against two named reasons in B1 and three in B5-bis, never as a
  pairwise set over all five. Met.
- **SC-13** — see above. Unmet.
- **SC-16 — 7 clauses, 7 covered, one narrowly.** N issues (case 2, at N=2), at most one parent only
  when none recorded (12 created / 13 adopted, no create), parent counted separately (12/13
  `parent_origin`), board add (2), station = fleet `ready` (2), labels (8), body shape (11).
  **Narrow:** "and nothing else" is bound as `len(parts) == 2` and by pinning `meta_lines[0]` and
  `[1]`; `len(meta_lines) == 2` is not asserted, so a third trailing meta line would pass. Met.
- **SC-17 — 4 clauses, 4 covered.** Every task a sub-issue of the one parent (15, exactly two attach
  calls carrying the internal id), exactly one `blocked_by` per `depends_on` asserted for the
  six-blocker task (16, six calls, six distinct resolved ids), parent never boarded (14), second
  publish draws zero duplicate edges (19 run 3, `mutating_calls() == []`). Met.

## The `factory_land.py:77` dependency

| SC | As it stands | If :77 is a defect | Why |
|---|---|---|---|
| SC-05 | met | **unmet** | The positive clause "opens a pull request" is not guaranteed: the branch can exit 0, advance the station and return a URL for a PR that was never opened. |
| SC-14 | met | **unchanged** | :77 is after the declared point of no return — the comment at :58 and the push at :60. SC-14 binds pre-PNR refusal paths only (land M3/M4). |
| SC-11 | met | **unchanged** | The adoption diagnostic at :81-84 carries `file=sys.stderr`, so stdout stays one JSON document. |
| SC-10 | met | **unchanged in letter** | A deliberately caught `GhError` is not an unexpected exception, so "exit 2 never 1" holds. REQ-08's "a failure is never mistakable for nothing to do" fails worse than stated here: the failure is mistakable for **success**. |
| SC-19 | already unmet | unchanged | The stub `gh` never raises, so the branch is unexercised. That bounds what SC-19 proves; it is not a verdict driver. |

**A test that passes without binding the behaviour.** `test-factory-land.py` M2b is the guard against
this defect, and its fixture omits **both** discriminators at once — no "already exists" text and no
URL. No case supplies "already exists" for an unrelated reason together with an unrelated URL, which
is exactly the input :77 mishandles. M2b passing is not evidence the narrowing is correct.

## Where I disagree with qa's SC map

- **SC-21** → `test-factory-claim.py` M5 (:336-346), not `test-factory-config.py`. M5 binds all four
  clauses: exit 2, no board read (`project_items` absent), stderr names the option, the station field
  and the fleet file. Met.
- **SC-11** → qa cited integration Case D, but the declared method is `unit`. Unit evidence exists
  and is what I cite: config (23)/(24), claim C1-C3, land C1-C3, workspace I/J, decompose C-3a/b.
- **SC-10** → same shape. Declared `unit`; qa cited integration Cases A/B/C. Unit evidence: claim
  C1-C3, land C1-C3, workspace I/K, decompose C-3c.
- **SC-08** → not one file. Per-tool refusal lives in decompose (4), workspace (G), land (M4), claim
  (M2), with config (17) for the loader.

## Accepted residuals — signed, not re-argued

These bound what a full-green goal-check would **mean**; none is counted unmet.

- No criterion exercises the live GitHub API before ship. The one `verify: uat` criterion was deleted
  on the operator's 2026-08-08 ruling; the first real dispatch is the live verification.
- The `create_ref` concurrency serialisation is inferred from the endpoint being create-only, not
  measured. Nothing in this checkout can race two real agents.
- The whole automated set can be green against stub `gh` and `git`. REQ-04 and REQ-05 are proven
  against test doubles only.
- No mutation run at this gate, so every "met" above is a statement about assertions present, not
  about how much of the changed behaviour the suite would hold under perturbation.

## Open questions

- **Q1 (blocking, routing only):** SC-06 needs T-08, executable by the main session alone. Route it
  there, not to qa.
- **Q2 (non-blocking):** qa's gate returned BLOCKED on `test_kinds.functional.cmd: null` with
  `tests/functional/**` matching zero files. Asserted, not inherited: no SC declares `functional` as
  its evidence — the 20 split 15 unit / 3 integration / 2 inspection, re-counted from BRIEF.md here.
  No individual SC verdict moves. It is a gate-configuration finding, not an SC verdict.
- **Q3 (non-blocking):** SC-13, SC-18 and SC-19's unbound clauses are each one added assertion.
  Recommend routing to qa rather than amending the criteria.
- **Q4 (non-blocking, emergent — not adopted here):** no criterion states that the "already open PR"
  adoption at `factory_land.py:77` must be co-conditioned on a 422 and a PR-URL shape. BRIEF never
  wrote it, so it is not part of this pass/fail. Recommend it be raised as a defect against the
  review panel's finding, not retrofitted as an SC.
