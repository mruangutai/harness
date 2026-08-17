# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: none in flight — awaiting the operator on one question, with one fix card out
- squad: none
- status: awaiting-user

Mission `build`, at the goal-check seam. Branch `feat/FEAT-23-ship-flow-fixes`, tip **`490c37c`**,
`review_sha` pinned there. **All six tasks are landed, committed and green; the qa gate PASSED; the
review panel PASSED advisory; and the feature still does NOT meet its goal — SC-05 is unmet.** That
divergence is the whole reason a goal-check exists.

Seven commits: T-02 `9016628`, T-01 `d96ab5e`, T-05 `e50b8b4`, T-03 `17b7a9d`, T-06 `ceee94a`,
T-04 `83e769b`, simplify apply `490c37c`.

**SC-05 is NOT MET, verified at source by me and independently by pm and the product lead.** The
skill gives REUSE (`:41`,`:44`), SIMPLIFICATION (`:53`,`:57`) and EFFICIENCY (`:73`,`:76`) an
explicit plan-surface/code-surface pair. **ALTITUDE (`:79-92`) carries neither** — my own
per-section whitespace-normalised count is `plan surface` 0, `code surface` 0 against 1/1 for each
of the other three. **T-02's `verify:` structurally cannot see this**: it greps the two literals
**file-globally**, so three conforming angles satisfy the clause and a fourth missing both is
invisible. Six green tasks, one false criterion, and qa graded it `met` by the same file-global
method. A method failure against a distributive clause, not a diligence failure.

Gate results at this pin, each verified by me on disk:
- **qa gate PASS**, `matrix_ok: true`, `severity_max: low`, one applied-and-killed mutant. Binds
  only 2 of 6 tasks — `docs.always` is `[]` and four tasks are docs.
- **Panel PASS**, advisory (`gates.review: advisory_unless_high`), `severity_max: low`, zero
  `must_fix`. It measured the `83e769b..490c37c` delta as **zero executable lines** and so carried
  qa's green forward rather than assuming it.
- **Goal-check FAIL** — 10 met, 2 deferred by BRIEF design (SC-04, SC-13 at `BRIEF.md:149-152`,
  provable only on the next feature shipped and the next planned from a named ticket), 1 unmet.

Budget: `cycles_used` **4 of 10** — incremented for the unmet-SC re-dispatch (DEC-157 counts that as
rework). It sat at 3 for the entire build: no task was ever routed back and every lead reported zero
send-backs. 15 runs of 20.

## Open Questions

- **AWAITING THE OPERATOR — the emergent criterion.** `.claude/skills/harness-simplify/SKILL.md`
  carries **neither** bound on the apply: whitespace-normalised, `delete or weaken` 0,
  `ceiling of one` 0, `one fix` 0, against 1/1/2 in `.claude/skills/harness/SKILL.md`. DEC-195
  carries the assertion bound at `:6002` and no ceiling clause. So an eng-lead running the step from
  the skill alone learns neither rule — on this feature's own first execution, my dispatch had to
  carry both by hand. **pm judged it genuinely NEW, not covered**: REQ-05 only requires no file
  *outside this repository*, and no SC or task intent requires the bounds. It therefore does **not**
  gate. Adopting it amends an approved BRIEF, so it is the operator's signature. pm recommends
  folding it into SC-05's edit at near-zero marginal cost. **The remedy spans two ownership
  regimes** — the two `.claude/` files are NOBODY/main-session-direct, the DEC-195 half is
  documentor-owned — and half-landing it leaves the drift it exists to end.
- **THE PANEL'S PASS IS PINNED AT `490c37c` AND THE SC-05 FIX WILL MOVE THE TIP.** Raised by the
  product lead; neither pm nor the panel could see it. This is the FEAT-20 failure DEC-195 exists to
  prevent, arriving from the goal-check side. After the fix I re-pin and **measure the delta** the
  way the panel itself did — it validated exactly this reasoning for `83e769b..490c37c` by showing
  zero executable-line change. I will not assert the transfer without measuring it.
- **THIS ORCHESTRATOR'S OWN ERROR.** I dispatched T-05 **twice**. Run `-6-t01t05-eng` returned a
  PROVISIONAL digest while its member was in flight; I waited out T-01 correctly, then wrongly read
  the run as finished and spawned `-7-t05-eng` for a task run 6 went on to dispatch itself. **Run 6's
  own `state.yaml`** would have stopped me and I never opened it. Cost: one lead run, two member
  spawns, ~146k tokens, zero code. Not a cycle under DEC-157, so the budget is blind to it.
- **Harness defect, EIGHT recurrences, the single largest cost driver.** `validate-digest.py --hook`
  fires on a lead's turn-end while its member is still in flight; a lead has no await primitive and
  no sleep, so its only exits are a premature verdict or a fabrication. It manufactures the disk
  state that caused my duplicate dispatch. **A mitigation now works reliably** — hold the turn open
  with read-only calls until members return — and it held for the qa, simplify, panel and goal-check
  leads, four in a row, at zero cost. DEC-174 surface: operator-only.
- Advisory, panel, low: `gh-sync.py:445-466` — `_record_status`'s **write**-failure path re-raises;
  intent item 6 made only the *read* path non-raising. A disk error after GitHub's close succeeds
  leaves `feature.json` non-terminal against a terminal board — this feature's own defect class. Not
  a regression; `save_recorded`'s six call sites share the shape.
- Record fidelity, panel: the security reviewer's digest YAML says `mitigated: true` where its own
  prose says "Unmitigated in code … out of scope". Both agree it does not gate; they disagree in the
  machine-readable field.
- **`grep -F` on prose is a false-negative machine** — zero on a phrase spanning a wrapped line, and
  case-sensitive. It nearly made me report three correct points as missing today.
- `plan.yaml` D-05's `because:` says `gh-sync.py` takes the feature dir as `argv1`; it is the SECOND
  positional (`:752`, `:777`). D-05's conclusion is unaffected and DEC-196 records the true shape.
  Correcting signed prose needs re-signature — flagged, not edited.
- `harness/SKILL.md:98` cites "§4.4's significance rubric"; `SPEC.md:720` §4.4 is titled "Autonomy is
  scoped by reversibility" and "significance" appears nowhere. Naming defect, still resolves.
- Backlog from qa and simplify: `board-station.py:100-102` and `:106-109` untested;
  `_record_status`'s absent-file branch untested; `_atomic_write`'s third copy at
  `factory_decompose.py:173-186` falsifies its own docstring; `board-station.py`'s double
  `harness.json` read; `board-station.py` missing from the call-site inventory at
  `harness/SKILL.md:188-195`.
- A simplify-angle member reached the **real** `gh` with one read-only GraphQL lookup against my
  no-gh bound, self-disclosed. Blast radius verified at source: `set_station` raises before
  `project_field_set`, so nothing was written to board 3.
- **RESOLVED this phase:** parent `#454` is now at `Review` after seven failed station writes;
  GitHub's GraphQL 503s cleared and `check-state.sh` exits 0.
- Arch finding G remains deliberately unapplied by the operator's signature.
