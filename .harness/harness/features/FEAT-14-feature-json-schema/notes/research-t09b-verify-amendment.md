# T-09 verify amendment — R-01 narrowing + R-02's two dead assertions repaired

**Done. The clause is RED, as it must be at this point** (exit 1, no traceback, three DEC entries
unwritten and no rename performed). Scope was T-09's `verify:` block only; `approval:`, `intent:`
and `decisions:` are untouched.

## What changed — three edits, nothing else

| Ruling | Was | Now |
|---|---|---|
| R-01 | `for f in (BUILD.md, org.html): if 'feature.yaml' in open(f).read()` | three exact anchor substrings asserted **present exactly once** in BUILD.md, stripped, then `'feature.yaml' not in` the remainder. `org.html` keeps the plain whole-file check |
| R-02 (a) | `_re.search(r'11\.3(...)', s, _re.S)` — matched the prose cross-reference at `SPEC.md:1604` (capture ran to :1631) | `_re.search(r'^###\s+11\.3(...)', s, _re.M \| _re.S)` — resolves to the real heading at `SPEC.md:1762` |
| R-02 (b) | `'Building' not in d` — already satisfied by unrelated prose at `DECISIONS.md:1159` | split on `^##\s+DEC-`, require **at least one entry containing all six** board values. Number-independent |

The three BUILD.md anchors, each carrying its own `feature.yaml`:

1. `feature.yaml matched disk in every flow (after the INV-12 block-form fix, acb8db4)` — :335, the
   bracketed marker only. Deliberately excludes the emoji and stops short of the two occurrences on
   that line that DO rename, so it still matches after the documentor's pass.
2. `recorded the contradiction in STATE and feature.yaml` — :353.
3. `` a second feature's `feature.yaml` `` — :357 (backticks are file content, not markdown).

## Disk facts, re-derived at this checkout

- BUILD.md: **11 occurrences over 8 lines** — 331×2, 335×3, 345, 352, 353, 357, 359, 969. 8 rename,
  3 stay → BUILD.md must land at exactly 3. Matches the dispatch.
- SPEC.md 14, org.html 2 (all present-tense, go to zero). DECISIONS.md is not swept.
- `Building` appears **once** in DECISIONS.md, at :1159, in unrelated prose. Confirmed dead.
- 0 DEC entries currently contain all six values; `max(DEC-NNN)` is **189**.

## Behaviour proven, not asserted (in-memory simulation, no repo file touched)

| Scenario | Result |
|---|---|
| after the documentor's rename, 3 exempt occurrences left | `OK` |
| rename + one new `feature.yaml` reference anywhere in BUILD.md | **fires** — "names feature.yaml outside the three exempt dated records" |
| rename + the :335 marker deleted | **fires** — anchor count 0 |
| rename + a marker duplicated | **fires** — anchor count 2 |

A bare `count == 3` passes all four. That is why it is forbidden and not used.

## Findings — report, do not fix

- **Citation drift stands as ruled.** `D-04` cites DEC-189 and `D-08` cites DEC-190 as reserved;
  DEC-189 is taken at `DECISIONS.md` (max entry = 189). Left alone per the operator's ruling — a
  goal-check finding, not a silent edit.
- DECISIONS.md holds **52** `feature.yaml` occurrences, not the dispatch's 50. Non-blocking: the
  clause does not sweep that file, consistent with T-08's `docs/harness/DECISIONS*` exemption.
- The old §11.3 capture ended at :1631, not the dispatch's ":1761". Does not change the repair.
- Residual on the six-values check: if some *other* DEC entry ever contains all six words, blanking
  the vocabulary entry would not fire. Zero such entries today; the number-independent shape is what
  R-02 prescribes, so no deviation was made.
- The dispatch declares a standing red elsewhere (`check-plan-routes.py` 35 violations across 16
  plans, `check-state.sh` exit 1); I did not observe those numbers and did not chase them. What I
  did observe: scoped to this plan the checker reports **0 violations**, T-09 `OK`.
