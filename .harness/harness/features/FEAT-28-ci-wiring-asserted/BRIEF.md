# BRIEF — FEAT-28 CI wiring asserted

## Problem

`.github/workflows/tests.yml` is the only mechanical runner for this repo's gates, and its comments
tell the next reader that guards exist where they do not.

Issue #279's literal wording — "no test asserts the step exists" and "**no such test exists**" — is
stale, and the reality is worse than an absent test. Measured at HEAD
(de4b76a0b889827f1e6561cdfba9986f5abf893b):

- **A real, green, passing test guards a different fact.** `tests.yml:112` cites
  `test-check-plan-routes.py` case 25 as what keeps the `Plan-route gate` step present and
  unneutered. Case 25 exists and passes — `test-check-plan-routes.py:1030-1093` asserts `status:`
  enum values inside `plan.yaml`. Nothing to do with CI. A reader who follows the citation finds a
  green test and stops looking. That manufactures false confidence, and it is defect #133's own
  shape — the shape the comment was written to prevent.
- **A second stale claim sits four lines below it.** `tests.yml:116` reads "M IS ASSERTED, NOT JUST
  THE EXIT CODE". False as written: `plans` is extracted at line 154 and read only by the `echo` at
  line 180. No conditional touches it. Lines 156-164 record why — the `plans == 0` check was
  deliberately removed on 2026-08-13 after FEAT-18 shipped and it failed a healthy tree.
- **A third citation names a test that does not exist.** `tests.yml:44` signs off the `container:`
  ban with "`case_25b9` keeps the key banned". There is no `case_25b9` under `bin/`. By the
  comment's own reasoning, a container job runs as root, root ignores file permissions, and the
  `chmod 000` assertions in `test-check-domain.py` and `test-gh-sync.py` would then pass for the
  wrong reason — `test-gh-sync.py` has a `skip … (running as root)` branch, so they go quiet rather
  than red.
- **A fourth hole is self-admitted in the file.** `tests.yml:183-184`: "Nothing in the repository
  asserts this step is present or unneutered" — the identical defect one step down, on the
  `Layout gate`.

`pull_request` runs the workflow from the PR's own ref, so a PR that deletes any of these steps
still emits a green `integration` context and satisfies branch protection. The gate can be removed
by the same PR it would have failed.

## Goal

Nothing in this repository currently reads `.github/workflows/tests.yml` and asserts anything about
it. After this feature, one parsed assertion, running inside the required `integration` context,
fails when a load-bearing CI gate step is deleted or hollowed out — and every citation in that
workflow points at a test that asserts what the citation claims.

## Requirements

- REQ-01: An automated assertion, reachable from the required `integration` CI context, fails when
  the `Plan-route gate` step is absent from the workflow.
- REQ-02: The same assertion fails when the step is present but any of its five failure-forcing
  behaviours is removed — the ones whose deletion lets the step pass while the gate examines
  nothing (enumerated in `notes/research-FEAT-28-ci-wiring.md`: capture the checker's exit; exit 1
  on a missing summary line; exit 1 on a missing `examined` line; exit 1 on `examined == 0`;
  propagate the checker's exit).
- REQ-03: The same assertion covers the `Layout gate` step and the `container:` ban on the
  `integration` job, which carry the identical defect.
- REQ-04: The assertion is proven able to fail, by a case that mutates a parsed copy of the real
  workflow — never the live file — and shows the predicate reports the mutation.
- REQ-05: Every case citation in `.github/workflows/tests.yml` names a test that asserts what the
  surrounding comment claims, and no comment states a behaviour the file does not have.
- REQ-06: The record states which clause of DEC-183 this feature reverses, and the ceiling on what
  is being reintroduced.
- REQ-07: The assertion fails if it is not itself wired into the required CI context — a guard
  nothing runs is the failure mode it would otherwise be blind to.
- REQ-08: The assertion also fails when a guarded step is switched OFF rather than deleted — a
  `continue-on-error` key or a step-level `if:` on any step the assertion depends on — and when the
  `Unit suite` step is absent, since that step is what carries the unit kind into the required
  context.

## Success Criteria

- SC-01: With the workflow unmodified, the predicate over the parsed real
  `.github/workflows/tests.yml` reports zero violations, and the case is graded by running code —
  `python3 .claude/skills/harness/bin/test-check-plan-routes.py` exits 0 and prints the new
  `case_26a` line as passing.
  verify: automated      evidence: integration
- SC-02: With the `Plan-route gate` step deleted from a deep copy of the parsed workflow, the
  predicate reports a violation naming that step (`case_26b`), and the suite leaves
  `.github/workflows/tests.yml` byte-identical -- `git status --porcelain
  .github/workflows/tests.yml` is empty after it runs.
  verify: automated      evidence: integration
- SC-03: Removing any ONE of the step's five failure-forcing behaviours, individually, is reported
  as its own violation naming what is gone: the checker's exit capture, the missing-summary exit 1,
  the missing-examined exit 1, the examined-zero exit 1, and the final `exit "$rc"`
  (`case_26c`, `case_26d`, `case_26j`, `case_26e`, `case_26f` — enumerated, never a range). Five
  behaviours, five cases -- a single combined case would pass on the four that survive.
  verify: automated      evidence: integration
- SC-04: Deleting the `Layout gate` step, and adding a `container:` key to the `integration` job,
  are each reported as a violation naming the thing (`case_26g`, `case_26h`).
  verify: automated      evidence: integration
- SC-10: For EACH of the four guarded steps individually — `Unit suite`, `Integration suite`,
  `Plan-route gate`, `Layout gate` — adding `continue-on-error: true` to a deep copy of the parsed
  workflow is reported, and so is adding a step-level `if:`; and deleting the `Unit suite` step is
  reported. Each violation names the step it was found on, so an implementation that inspects only
  one step fails this criterion. Measured baseline at `061acbb`: `grep -n "continue-on-error"` and
  `grep -nE "^[[:space:]]+if:"` over `tests.yml` both return zero hits, so the real workflow is
  clean today and `case_26a` stays green.
  verify: automated      evidence: integration
- SC-05: A case id cited in the workflow text is resolved as a **full identifier** — never
  truncated to its leading `case_NN` — against either a `def` name or a `check("` label under
  `.claude/skills/harness/bin/test-*.py`, and is reported as a phantom citation when neither
  exists. Both directions are asserted, because a check that only reports is not falsifiable:
  `case_25b9` (`tests.yml:44`) **is** reported, and `case_19a3b` (`tests.yml:177`) is **not** —
  it resolves through the `check("` label at `test-check-plan-routes.py:366`. The mutation proof
  is `case_26i` (an injected id whose base resolves, so it is red only under the full-identifier
  rule); the assertion against the real file is `case_26o`, added by T-02 because T-01 cannot
  make it true.
  verify: automated      evidence: integration
- SC-06: After the repair, each of the four sites -- `tests.yml:44`, `:112`, `:116` and `:183-184`
  -- cites a case that asserts the claim its surrounding comment makes, and no comment states a
  behaviour the file does not have. In particular `:116` no longer claims M is asserted. Every
  citation enumerates its cases individually and names each by its full `check()` label — never a
  range and never a bare `case_NN` — which is what makes this criterion checkable by eye: a range
  drops cases added later, and a bare number carries no claim to check the test against.
  verify: inspection
- SC-07: DEC-183 carries an amendment naming what is now asserted and the ceiling of it, with the
  original paragraph left standing, and `DECISIONS-INDEX.md` is regenerated by
  `gen-decisions-index.py` rather than hand-edited.
  verify: inspection
- SC-08: The guard asserts its own wiring into the required context: that its host file
  `test-check-plan-routes.py` is listed in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`, and that the
  `Integration suite` step in the workflow invokes `run-unit-tests.sh --kind integration`
  (`case_26k`). A guard nothing runs is this repository's most-repeated defect, and it is the one
  failure mode the guard would otherwise be blind to.
  verify: automated      evidence: integration
- SC-09: The full suite still passes end to end — `.claude/skills/harness/bin/run-unit-tests.sh`
  exits 0, including its drift detector.
  verify: automated      evidence: integration
- SC-10: A guarded step switched OFF without being deleted is reported too. With the `Unit suite`
  step removed from a deep copy of the parsed workflow, and with `continue-on-error: true` and a
  step-level `if:` each added to the `Plan-route gate` step in a deep copy, the predicate reports a
  violation naming the step and the key (`case_26l`, `case_26m`, `case_26n`). `continue-on-error`
  is the silent vector and the reason this criterion is separate from SC-02: the step runs, goes
  red, the failure is swallowed, and the required `integration` context still reports green — no
  step is missing, so every deletion case stays quiet.
  verify: automated      evidence: integration

Note on `verify: automated` in this brief: it means **graded by executing the named command and
reading its exit code and its per-case output**, not by the existence of a standing assertion.
FEAT-25 flagged that the token alone is ambiguous and that ambiguity is still open, so every
`automated` SC above is graded by running
`python3 .claude/skills/harness/bin/test-check-plan-routes.py` (SC-09 by
`.claude/skills/harness/bin/run-unit-tests.sh`) and reading the named `case_26…` line, not by
observing that a case exists. What `evidence: integration` names — the CI job id and required
context, not a test-kind classification — is spelled out under `## Constraints` below.

## Verification gaps

- `integration` has a runner (`run-unit-tests.sh --kind integration`, 12 scripts), so no SC here
  rests on a null kind.
- **The `Integration suite` step cannot protect itself, and no SC claims otherwise.** The assertion
  reaches CI only through `tests.yml:81`. Delete that step and the job still runs its remaining
  steps, still succeeds, still emits `integration`, and the guard never runs. Closing that needs
  something outside the PR's own ref — a second required context, or a check evaluated from the
  base ref. Out of scope here; recorded, not hidden.
- **Sub-case citations ARE covered; two narrower residues are not.** The earlier draft of this
  brief recorded truncation-to-`case_NN` as an open gap. It is closed: the check resolves the full
  identifier against a `def` name **or** a `check("` label, the label being a resolution source
  because sub-case ids exist only there (`case_19a3b` has no `def` and never will). The
  reconciliation with the citations already in the tree is a **measured, complete enumeration**,
  not a hazard: `.github/workflows/tests.yml` cites exactly two ids — `case_25b9` (line 44) and
  `case_19a3b` (line 177) — observed at `de4b76a` and re-derived at `061acbb`. Under the rule
  `case_25b9` is reported (T-02 removes it) and `case_19a3b` stays clean. What remains uncovered:
  (a) resolution is a **prefix** match, so a bare `case_25` citation still resolves and carries no
  claim — that is exactly what SC-06's full-label convention, graded by inspection, exists to
  carry; and (b) the scan reads `tests.yml` only, so case citations elsewhere in the tree are
  ungated.
- **Nothing verifies the assertion on a real CI run before merge.** Same limitation DEC-183
  recorded for itself. The local suite is the proof; the first PR run is the confirmation.

## Constraints

- The assertion must run inside the required `integration` context. Branch protection on `main`
  requires exactly one context, and it is the job id at `tests.yml:32` — the job carries no `name:`
  key, and adding one would rename the context and block every PR.
- **Where the guard actually runs — the path, end to end.** `evidence: integration` on every
  automated criterion here (SC-01, SC-02, SC-03, SC-04, SC-05, SC-08, SC-09, SC-10 —
  enumerated, never a range) names the CI **job id** and the required
  branch-protection context (`tests.yml:32`). It is not a claim about which test kind classifies
  the file: the two `detect` lists in `harness.json` both match `test-check-plan-routes.py`, so no
  kind is asserted anywhere in this brief. The assertion reaches the required context because
  `test-check-plan-routes.py` is listed in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`) and is
  executed by the `Integration suite` step (`tests.yml:81`) — the guard is hosted as new cases
  inside that existing file, so there is no separate `test-ci-wiring.py` to go looking for. Those
  three anchors re-derived at `de4b76a`; T-02 edits comments in the same workflow, so re-derive
  rather than trusting the line numbers after the build.
- **This partly reverses a settled owner decision.** DEC-183 records that 39 assertions defending
  this step, plus a harness that executed workflow bodies against a cloned workspace, were deleted
  by owner decision, and closes "nothing protects the gate — not pending, settled." What is
  proposed here is **different in KIND, and the ceiling is on kind, not on count**: what DEC-183
  removed executed workflow bodies against a cloned workspace; what is proposed is a pure predicate
  over `yaml.safe_load` of the workflow document, **no workspace clone and no workflow-body
  execution**. That ceiling is the reason it should not be deleted again, and it is what the user
  is signing. **No count of what will ship is claimed — nothing is built yet.** For scale only: the
  plan-time scratchpad prototype `proto-ci-wiring.py` measures 32 assertions over the real
  `.github/workflows/tests.yml` at `de4b76a`, all passing, exit 0, no tree mutation. That is a
  measurement of the prototype, not of what T-01 lands.
- Parsed assertions only. `test "$(git grep … | wc -l)" = 0` passes when the search errors (#248)
  and `git grep -E` does not honour `\b` (#249); both idioms are forbidden. Substring checks inside
  an already-parsed `run:` scalar are not grep-over-files and are fine.
- The live `.github/workflows/tests.yml` is never mutated to prove RED. Mutants are deep copies of
  the parsed document, in memory.
- No file outside this repo's `.github/`, `.claude/skills/harness/bin/`,
  `.harness/harness/docs/` and this feature's own folder is touched.
- `tests.yml` resolves to `harness-dev-ops` alone and is not a DEC-174 carve-out; the bin test files
  resolve to `harness-backend-dev` and `harness-dev-ops`.

## Approval

status: pending

**The one question this approval must settle.** DEC-183 settled that this step stays unguarded: it
deleted 39 assertions to make that true and closed the matter "not pending, settled." FEAT-28
reverses that clause and reintroduces a guard over the same step. If the owner still wants the step
unguarded, then the whole feature is void and must not be built. Left unanswered here by design —
only the owner can answer it.
