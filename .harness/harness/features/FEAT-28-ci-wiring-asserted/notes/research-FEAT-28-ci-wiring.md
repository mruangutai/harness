# Research — FEAT-28 CI wiring asserted

BLUF: the guard advertised in the workflow does not exist, in two places; the replacement design
was red-proven at plan time against temporary copies, so no build-phase manual proof is needed.

## Measured at this checkout

- `.github/workflows/tests.yml:112` cites "`test-check-plan-routes.py` case 25". `case_25`
  (`test-check-plan-routes.py:1030`) validates a task `status:` enum. `grep -n 'tests.yml\|workflows'`
  over that file returns nothing.
- `.github/workflows/tests.yml:44` cites `case_25b9`. `grep -rn 25b9 .claude/skills/harness/bin/`
  returns nothing. Second false citation, same file.
- No file under `.claude/skills/harness/bin/` reads the workflow as a subject. `test-check-domain.py`
  and `layout_migration.py` mention `tests.yml` only as a fixture path.
- `run-unit-tests.sh:40-54` is a drift detector: any `test-*.py` in the bin dir not listed in
  `UNIT_SCRIPTS` or `INTEGRATION_SCRIPTS` exits 2. Registration is mandatory, not optional.
- **THE ROAD NOT TAKEN — D-01 REJECTED THIS.** The next two bullets describe Route A, a NEW
  `bin/test-*.py` file. D-01 chose the other path: the predicate is hosted inside the existing
  `test-check-plan-routes.py`, which is already in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`).
  **No `UNIT_SCRIPTS` registration is part of this feature** — a downstream reading of these lines
  as the plan of record is where that false premise came from. Kept, marked, not deleted.
  - (rejected) `test_kinds.unit.detect` globs `.claude/skills/harness/bin/test-*.py`;
    `test_kinds.integration.detect` names files explicitly. The two lists OVERLAP on
    `test-check-plan-routes.py`, and which one wins is unverified here — so no test KIND is
    asserted from them, in this note or anywhere downstream.
  - (rejected) A new bin test file would have needed a `UNIT_SCRIPTS` line to satisfy the drift
    detector above. That line is not written, because the file is not created.

## Red proof, executed at plan time

Prototype at
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/070b3f94-b495-4deb-b352-6896cfb60ad3/scratchpad/proto-ci-wiring.py`
(scratchpad, discarded with the session). It takes the workflow path as argv.

- Real `.github/workflows/tests.yml`: 32 assertions, ALL PASS, exit 0. No tree mutation.
- Six mutations on `yaml.safe_dump`ed copies, each exit 1, each naming exactly the intended
  assertion: deleted `Plan-route gate` step; `run:` replaced with `echo skipped`;
  `continue-on-error: true` on `Unit suite`; `if: false` on `Layout gate`; `name: Tests` on the job;
  `container: python:3.12` on the job.

Conclusion for the plan: SC-02's proof is an in-suite test-file concern (T-02), not a deferred
build-phase manual step, and it never requires editing the real workflow.

## Open

- DEC-183 explicitly settles "nothing protects the gate — not pending, settled", and records that 39
  such assertions were deleted by owner decision. FEAT-28 reverses that clause; T-04 amends it. If
  the owner still wants the step unguarded, the whole feature is void — that is the one question
  approval should settle.

---

# Second measurement pass — pm, 2026-08-19 (the BRIEF and plan of record)

Written by the pm run that authored the sibling `BRIEF.md` and `plan.yaml`, after a concurrent
writer replaced this file. Nothing above is removed. The task ids above (T-02, T-04) belong to a
different draft and do NOT match `plan.yaml`, whose ids are T-01 assertion, T-02 citation repair,
T-03 DEC-183 amendment.

Measured at `git rev-parse HEAD` = de4b76a0b889827f1e6561cdfba9986f5abf893b, branch
`feat/FEAT-27-expertise-repository-tier`, with FEAT-27's uncommitted edits in the tree. Read-only.

## The four wiring defects

| Anchor | Claim in the file | Reality |
|---|---|---|
| `tests.yml:112` | case 25 "reads this file and asserts the step is here and unneutered" | `case_25a`-`case_25e` (`test-check-plan-routes.py:1030-1093`) assert `status:` values in `plan.yaml`. `grep -c case_25` = 7. DRIFTED — a real, green test guarding a different fact |
| `tests.yml:116` | "M IS ASSERTED, NOT JUST THE EXIT CODE" | False. `plans` is set at 154 and read only by the `echo` at 180; no conditional touches it. Lines 156-164 record the deliberate removal of the `plans == 0` check on 2026-08-13. STALE |
| `tests.yml:44` | "`case_25b9` keeps the key banned" | No such test anywhere under `bin/`. PHANTOM |
| `tests.yml:183-184` | "Nothing in the repository asserts this step is present or unneutered" | True and self-admitted, on the Layout gate |

## What "wired and unneutered" means for the Plan-route gate — 10 behaviours

Failure-forcing means: delete it and the step can go green while the gate examines nothing.

| # | Anchor | Behaviour | Failure-forcing |
|---|---|---|---|
| C-01 | 136 | invokes `check-plan-routes.py` and captures its exit via `\|\| rc=$?` | yes |
| C-02 | 137 | prints the checker's output | no |
| C-03 | 147 | extracts the summary line; `\|\| true` load-bearing under `bash -e` | no |
| C-04 | 149-152 | `exit 1` when no summary line | yes |
| C-05 | 154 | extracts the plan count `plans` | no — reported, never gated |
| C-06 | 165 | extracts `examined N feature dir(s)` | no |
| C-07 | 166-169 | `exit 1` when the `examined` line is absent | yes |
| C-08 | 170-173 | `exit 1` when `examined` is 0 | yes |
| C-09 | 180 | prints the diagnostic line | no |
| C-10 | 181 | `exit "$rc"` — propagates the verdict | yes |

Five are failure-forcing (C-01, C-04, C-07, C-08, C-10); the plan pins exactly those (D-05).
The issue's "eight" is not reproducible at HEAD: the title counts success criteria downstream of
the `Unit suite` step, not criteria this step enforces, and FEAT-14's BRIEF carries 18 unique
`SC-NN` ids (`grep -o "SC-[0-9]*" … | sort -u | wc -l` = 18). Neither number is 8.

## Route ground (D-01)

- The drift detector above means a new test file forces its registration line into the same PR —
  Route A's write into the file FEAT-27 is editing is forced, not deferrable.
- `test-check-plan-routes.py` is already in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`) and in
  `harness.json` `test_kinds.integration.detect`, so hosting the assertion there keeps
  `evidence: integration` honest with zero edits elsewhere. A new `bin/test-*.py` falls under
  `test_kinds.unit.detect`, so Route A would also change which kind grades these SCs.
- Domain: `tests.yml` -> `harness-dev-ops` only; `bin/test-*.py` -> `harness-backend-dev` and
  `harness-dev-ops`; `docs/DECISIONS*.md` -> `harness-documentor`. No DEC-174 carve-out.
- The cost on B's side, stated: the assertion lives in a file whose name does not name it, and
  discoverability rests on reciprocal comments — the mechanism that has already rotted three times
  in this very workflow.

## The irreducible hole

The assertion reaches CI only through the `Integration suite` step (`tests.yml:81`) and cannot
protect that step: `pull_request` runs the workflow from the PR's own ref, so deleting line 81
leaves a green `integration` with the guard never run. Recorded as D-03 and stated in the BRIEF;
closing it needs a second required context or a base-ref check, outside this feature.

## DEC-183

`DECISIONS.md:5317` records 39 such assertions plus a workflow-body-executing harness deleted by
owner decision, closing "nothing protects the gate — not pending, settled." This feature reverses
one clause. The ceiling is on KIND, not count: a pure predicate over the parsed
document - no workspace clone, no workflow-body execution - carried by eleven cases (case_26a
through case_26k). That is the amendment's point (D-04, T-03).

---

# Fix cycle — pm, 2026-08-19 (three corrections to BRIEF.md, nothing else edited)

BLUF: the signed number was wrong by 5x and the routing was unstated. Both corrected in the BRIEF;
the DEC-183 reversal question moved from this note into `## Approval`, unanswered.

1. **Count.** `## Constraints` said "on the order of six assertions". Measured: **32** (prototype
   over the real `.github/workflows/tests.yml` at `de4b76a`, all pass, exit 0, no tree mutation).
   BRIEF line ~141. The "deliberately far smaller" framing went with the six — 32 against the 39
   DEC-183 deleted is comparable in count. The surviving, honest ceiling is on **kind**: what was
   deleted executed workflow bodies against a cloned workspace; what is proposed is a pure predicate
   over `yaml.safe_load`.
2. **Routing, stated in the BRIEF** (line ~131). Anchors re-derived at `de4b76a`, all resolve:
   job id `integration` `tests.yml:32`; `test-check-plan-routes.py` in `INTEGRATION_SCRIPTS`
   `run-unit-tests.sh:18` and NOT in `UNIT_SCRIPTS` `:17`; `Integration suite` step `tests.yml:81`,
   its `run: … --kind integration` at `tests.yml:84`. **Test kind and CI context are both
   `integration` — there is no unit/integration mismatch.** A "kind is unit" claim would have been a
   new falsehood.
3. **DEC-183 question** now in `## Approval` (line ~166), `status: pending` byte-identical.
   check-state.sh:91-92 matches `status:\s*approved` inside that section; the added prose contains
   no such string, so the gate reading is unchanged.

## Open (for the plan owner, not for me — BRIEF-only scope)

- This note's earlier "nine cases" (D-04 paragraph above) is superseded: the BRIEF's SCs enumerate
  `case_26a`-`case_26k`, which is **eleven**. `grep -n nine plan.yaml` returns nothing, so the plan
  carries no stale count. Treat "nine" above as wrong.
- SC-08/SC-09 appeared in the BRIEF between my first read and my edit (a concurrent writer). The
  routing paragraph names all seven automated SCs, not five.

`python3 .claude/skills/harness/bin/check-plan-routes.py` -> `0 violation(s) across 3 plan(s)`.
