# Handoff — FEAT-38, build → validate — written at b460650, seq-1

Written LATE, at the end of validate rather than at the seam it names. That lapse is the DEC-159
one INV-26 caught, recorded rather than backdated: the seam was crossed at `dadbc41` with no note.

## Next

**Nothing is dispatchable. The next act is the operator's.** Present
`notes/ship-review-2026-08-30-ship.md` and have them run `notes/uat-FEAT-38.md` — SC-13, the only
`verify: uat` criterion, repointed at `635cd3ba` and operator-ready. `gates.uat` is
`blocking_when_uat_criteria_exist`, so no lead can close it and no agent may mark it met. On
`passed`, the remaining step is ship acceptance by the main session; on `failed`, the result names
the entry and claim, and that routes to `harness-product-lead` as a fix cycle.

## Trust

- All 28 tasks `done`, each task's own `verify:` exits 0 — run from the signed plan via
  `harness_yaml.load_plan`, never retyped — `plan.yaml` — verified-at `635cd3ba`
- Blocking qa gate PASSES, `matrix_ok: true`, `must_fix: []`; suite exit 0, zero `FAIL ` lines, and
  all 55 registered scripts ran, so the green is not a gate discovering nothing —
  `notes/qa-ship-gate.md` — verified-at `635cd3ba`
- Panel PASSES, `severity_max: low`, no `must_fix`; `gates.review` is `advisory_unless_high` —
  `runs/2026-08-29-18-panel-ship-validator/digest.md` — verified-at `635cd3ba`
- SC-11, SC-16, SC-17 met by reviewer inspection; SC-17 went to a code-reading persona, not the
  table's author — `notes/review-harness-qa-ship-panel.md` — verified-at `635cd3ba`
- 15 of 16 live criteria met — `notes/research-FEAT-38-goalcheck-635cd3b.md` — verified-at `635cd3ba`
- SC-13 is UNRUN, not failed: `status: ready`, all four `result:` blank — `notes/uat-FEAT-38.md` —
  verified-at `b460650`
- The SC-18 pair is byte-identical to `git show 99bb52c:` and named by both registration sides,
  asserted with `shasum` not inferred from the suite — verified-at `635cd3ba`
- The retained anchor checker still reports RED: 0 on a clean copy, 1 with a planted anchor, probed
  on a `/tmp` copy so the tree was never perturbed — verified-at `635cd3ba`
- T-27 touched no prose, so ruling 6's void condition did not fire: prose sequences identical either
  side, 5067 lines each — verified-at `0a94d91`
- DEC-138 and DEC-174 byte-identical across `48bbe7e..635cd3ba`; DEC-181 lost 3 markers and 2
  blanks, zero prose — verified-at `635cd3ba`
- Both approval fragments UNWRITTEN by this run: `BRIEF.md` byte-identical to `c9b85a4`,
  `plan.yaml`'s only diff is five `status:` lines — verified-at `b460650`

## Dead ends

- No successor to the deleted claims mechanism; a declarative replacement was specified in full and
  REJECTED — `notes/answers-2026-08-29-panel.md` — verified-at `b460650`
- Do not fix the stale docstring in `check-decision-anchors.py`; SC-18 pins it byte-identical to
  `99bb52c`, so the fix and the criterion are mutually exclusive — `BRIEF.md` SC-18 — B-27
- No positive guidance in DEC-205; the ruling is a deletion — `notes/answers-2026-08-29-24.md` — B-28
- Do not re-split T-24; the three-step order took the whole suite to exit 2 — `plan.yaml` — verified-at `635cd3ba`
- Do not count diff or suite lines with shell `grep`: `pi-uu-grep 0.2.0` matches a line-leading `+`
  against every line — four false readings this phase — B-26
- Do not pass a shell variable or post-`cd` relative path as a write target; `bash-write-guard.sh`
  resolves against the session root and denies — B-25
- Do not grade SC-09 or REQ-08; retired tombstones — `BRIEF.md` — verified-at `b460650`

## Working set

- `notes/ship-review-2026-08-30-ship.md`
- `notes/uat-FEAT-38.md`
- `STATE.md`
- `feature.json`
- `notes/research-FEAT-38-goalcheck-635cd3b.md`
