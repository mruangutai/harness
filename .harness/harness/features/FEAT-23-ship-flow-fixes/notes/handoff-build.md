# Handoff — FEAT-23, build → ship acceptance — written at 9885670, refreshed at 1d49644

## Next

**Nothing is dispatchable. The feature is complete and waiting on the operator's ship acceptance.**
The briefing is written and rendered: `notes/ship-review-2026-08-17-13.md` (+ `.html`). On acceptance
the MAIN SESSION runs `gh-sync.py ship .harness/harness/features/FEAT-23-ship-flow-fixes` — closing
milestone 14 and parent #454 (`parent_origin: created`) — then `gh-sync.py backlog` for the unstruck
B-rows. Merge is user-gated and nothing has merged. If the operator rejects or re-scopes, that is a
pm re-plan under a fresh signature, not a fix cycle.

## Trust

- All 13 SCs met or deferred: 11 met, SC-04 and SC-13 **deferred by `BRIEF.md:149-152`**, provable
  only on the next feature shipped / planned from a named ticket — pm's `sc_status` table plus my own
  re-measure — verified-at 9885670
- SC-05's fix holds per-section, which is the ONLY method that can see it: all four angles read
  `plan surface` 1 / `code surface` 1 — my own script, not T-02's file-global verify — verified-at 9885670
- Suites green: `--kind unit` 16/16 exit 0, `--kind integration` 12/12 exit 0 — re-run by me at the
  final tip, not carried from qa's pin — verified-at 9885670
- **The operator's final validator pass re-took the panel-transfer measurement independently and
  upheld it** — executables in `git diff --name-only 490c37c afc8cfd` is EMPTY — and then found the
  one must_fix the earlier panel and qa both missed — `runs/2026-08-17-14-finalpass-validator/` —
  verified-at 1d49644
- **`board-station.py`'s Unicode-digit gate is fixed and red-first proved AFTER the fact by me**:
  reverting the one line reddens the new case with `rc4=1 (1 means int() raised)`, restoring greens
  it, file byte-identical by SHA — my own probe — verified-at 1d49644
- `check-expertise.sh` exits 0 over all 15 files after 30 distilled entries — verified-at 9885670
- Parent #454 is at `Review`; `check-state.sh` exits 0 — verified-at 9885670
- `cycles_used` 5 of 10, `len(runs)` 20 of 20 (AT the bound) — the run budget is INFORMATIONAL and must not stop
  anything (INV-22) — `feature.json` — verified-at 9885670

## Dead ends

- Do NOT re-open arch finding G — deliberately unapplied by the operator's signature — source: operator
- Do NOT treat SC-04 / SC-13 as unmet work — `BRIEF.md:149-152` defers them by design — verified-at 9885670
- Do NOT trust a lead's returned verdict over disk on this feature — `validate-digest.py --hook` fired
  eight times mid-flight; **read the run's own `state.yaml` `completed_at` per step before concluding a
  run is over** — that omission cost one duplicate T-05 dispatch — verified-at 9885670
- Do NOT hand-edit `DECISIONS-INDEX.md` — T-04's verify diffs it against a fresh
  `gen-decisions-index.py --stdout`, so any hand-edit reddens — verified-at 9885670
- Do NOT apply a reviewer's Expertise ops on its behalf — `check-domain.sh --resolve` grants each
  reviewer its OWN file; the playbook's "write-less reviewers" phrasing is false and is row B-16 —
  verified-at 9885670
- Do NOT verify prose with a flat `grep -F` — false zero on a wrapped phrase, and case-sensitive;
  normalise whitespace first — verified-at 9885670

## Working set

- `.harness/harness/features/FEAT-23-ship-flow-fixes/notes/ship-review-2026-08-17-13.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/feature.json`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/STATE.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/runs/2026-08-17-11-goalcheck-product/digest.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/runs/2026-08-17-10-simplify-eng/digest.md`
