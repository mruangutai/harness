# Grilling — orchestrator close-out is one verb, and a phase seam ends the context (#1723) — 2026-09-15

## Destination
Closing a dispatched run costs the orchestrator one command instead of ~11, and an orchestrator
context never records runs in two phases: the seam DEC-159 names is enforced by an invariant, not
advised. Measured on the next `plan` mission the same way #1713 measured BUG-285-canonical-reader:
≤ 8 orchestrator model calls per dispatch, median context per call under 100k, no retrospective
`succession` judgement.

## Mission
mission: plan
reason: new verb composing four existing writers (feature-record.py, plan-merge.py, validate-digest.py) plus a new check-state.py invariant — a new enforcement surface; cause and files are known.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do all of them from plan (or patch) to ship")

## Settled
- Lever 1, one close-out verb → `feature-record.py close-run --file <feature.json> --id <run-id>
  --digest <digest.md> --verdict V [--task T-NN --station S] [--judgement kind=…,decision=…,reason=…]
  [--code-grade n_a]`: validates the digest (`validate-digest.py <persona> <path>`), stamps
  `run-end` (tokens already stamped by #1724's hook), sets the task station through
  `plan-merge.py set-task-station`, appends the judgement, prints the `spend` line. One process,
  one transcript line. Each composed writer keeps its own refusals; `close-run` stops at the first
  and names it.
- What stays separate → `STATE.md` (the orchestrator's prose, DEC-150), the handoff note, and the
  git commit. Those are the orchestrator's own writes and are not bookkeeping the verb can do for
  it. `quarantine.py list` stays a wake-time act (DEC-204), not a close-time one.
- Lever 2, seam enforced → `feature.json` runs gain nothing new; the phase of a run is derived as
  today (`feature-record.py spend` derives `plan`/`build` from `github.build_entry`). New INV: two
  runs in different phases recorded by the same orchestrator context with no handoff note whose
  `seq-N` falls between them is a violation. The orchestrator context is identified by the
  `run_uid`/`.run-identity.json` mechanism already minted per run (B-4 of BUG-285 ship review
  notes it is unreliable for product runs — pm must check #1708 before relying on it, and if it
  is not usable, the trigger is a `succession` judgement whose `at` postdates a run in the later
  phase, i.e. the retrospective shape #1713 measured).
- Advisory stays → the context advisory (DEC-198) is unchanged; this adds the invariant that
  catches the seam being crossed, after the fact, so the ledger records it as a violation rather
  than a footnote.
- Measurement is the acceptance → the DoD is measured on the next `plan` mission with the same
  method as #1713 (OMP session JSONL, `.message.usage`, tool-call census). pm writes the SC so a
  reader can re-run the census.
- Build execution → `feature-record.py`, `check-state.py`, `validate-digest.py` and tests are
  DEC-174 carve-out → `main-session-direct`. Playbook prose (`harness/SKILL.md` step 6,
  `references/build-phase.md`, `ledger.md`) is dispatchable.

## Not yet specified
- Whether `close-run` should also write the STATE.md `## Current` block from digest fields. Left
  to pm: DEC-150 makes STATE.md values-not-narrative, so a templated write may be legitimate, but
  it changes who authors STATE.md.

## Out of scope
- Shrinking what the orchestrator reads per wake (DEC-204 requires re-reading state from disk).
- Changing what the orchestrator decides.
- Reducing dispatch count (that is #1725's slicing and #1716's amendments).

## Facts I verified (so pm does not re-derive them)
- `ResumeCanonicalReaders`: 448 calls, $32.50, 55.5M cache-read tokens, median context 125k, p95
  219k, 2 compactions; 214/235 bash calls bookkeeping (git 80, quarantine list 26, run-end 26,
  validate-digest 27, run-start 14, set-task-station 13, judgement 11, spend 6); 19 dispatches →
  ~24 calls each. Two `succession` judgements are marked "Retrospective … seam correction"
  (#1713 Finding 1, #1723).
- Playbook close sequence: `harness/SKILL.md:79-85` (step 6) and `:100-108`.
- `feature-record.py` verbs: run-start, run-end, judgement, set-rework, propose-rework,
  raise-cycles, spend (`feature-record.py:1-40` docstring).
- DEC-159: one phase per orchestrator, seam handoff is normal termination. DEC-198/201: advisory
  never refuses.
- Base: `origin/main` at 82c9d074.
