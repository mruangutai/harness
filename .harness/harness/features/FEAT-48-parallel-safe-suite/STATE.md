# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: none this round — I re-validated at my own tier; no squad was dispatched
- squad: none
- status: awaiting_user — **not shippable**, one operator ruling blocks the last criterion

Station `review`. `review_sha: e64e863e` (repinned by the main session at `8861850d`). The
main-session-direct fix landed at `e64e863e`: T-03's in-file red proof and the symlink hardening.

**The headline: the fix worked, and one criterion turns out to have a wrong premise.**

**What the fix closed, verified by my own runs and probes rather than accepted on report:**
- **M1 is FIXED.** A dangling symlink and a symlinked subdirectory now each give exit 1 with a
  `MUTATED` line naming the path relative to DIR; the clean control still exits 0, so no false
  positive was traded for the fix. `snapshot()` now uses `os.lstat`, records symlinked directories
  as entries instead of descending, and carries `st_mode`. `test-run-pool.py:92-105` pins both legs.
- **SC-03's first half is now genuinely met.** The live-tree case asserts the resolved root against
  an **inline recomputation** — a real second computation, not a call back into `harness_boundary` —
  plus `discovered 63 >= 50` and zero findings. That was the exact defect pm named last round.
- **SC-01, SC-04, SC-05, SC-06, SC-07, SC-09, SC-10 re-verified at the new pin**, not inherited.
  SC-05 needed re-taking on the merits: the note's original ten runs were measured at `b86ce66a`,
  **before `snapshot()` was rewritten**, so they no longer covered the shipped pool. My own ten
  consecutive `--kind all` runs at `e64e863e`: all exit 0, zero `MUTATED`, zero `FAIL`,
  42.61–48.71s wall at 8 workers over 63 files, on a tree with 0 modified paths at start and end.
  Eleven green full runs in total this round.

**What blocks the ship — SC-03's second half, and it is not a coding oversight.**
SC-03 requires the invariant to flag, *in the same run*, the ten historical sites at `ea6f51f`,
each asserted individually. No file under `bin/` mentions `ea6f51f`. But the remedy is not simply
"write the assertion": **CI checks out with `actions/checkout@v4` and no `fetch-depth`
(`.github/workflows/tests.yml:50`), so the default shallow clone puts `ea6f51f` out of reach**,
while SC-04 requires that same file to pass in CI. Written literally, SC-03 and SC-04 cannot both
hold on today's workflow. That makes SC-03 **unmet and unmeetable as written** — pm's to re-plan
under the operator's approval, never mine to mark met, waived or edited.

**The scanner itself is not in doubt.** I ran it over `git show ea6f51f:` for all three files and
asserted each of the ten sites separately: **found 10, missing 0, extra 0**. The capability SC-03
describes is present and proven at the new pin; what is missing is its enshrinement in a gate CI
runs. That distinction is the whole of the remaining decision.

**Still outstanding, all main-session-direct:**
- **`code_grade` is still `fail`, and it moved the wrong way**: 7 FAIL records → **9** (19 passing).
  The fix added grade-1 `test-suite-independence.py:170 run_self_tests` and grade-2
  `run_pool.py:29 snapshot`. The panel had predicted the decomposition would clear three of five;
  it added two instead. Worth naming plainly rather than filing as noise.
- **M4 still open**: zero `pycache` mentions in `test-run-pool.py`, so T-04 intent item (g) is
  unpinned. `run_pool.py` excludes `__pycache__` correctly, so this is unpinned behaviour, not a
  live defect.
- **M5 still open**: a same-size overwrite with an exact `os.utime` restore remains invisible —
  I reproduced it, content demonstrably changed A→B with exit 0 and no `MUTATED`. Adding `st_mode`
  narrowed the tuple's blind spot but did not close this one. Disclosure-level.
- **Minor, new**: the clean control omits the `src.replace(...)` leg T-03 enumerates — the shape
  that historically produced 4 of 47 false positives — so a regression that starts flagging
  `str.replace` on `__file__`-derived text would not be caught.
- **Residual risk, stated because nobody else will**: the code added by `e64e863e` has been through
  **no reviewer panel**. Only my mechanical verification covers `run_self_tests` and the rewritten
  `snapshot`. The scoped re-validation I was asked for does not substitute for a review of new code.

Budgets: `cycles_used` stays **8 of 10** and `runs` stays 17. No squad ran this round, so no run is
recorded, and the rework loop this fix belongs to was already counted when the two FAIL runs landed
— counting the fix again would count one loop twice. `check-state.sh` agrees (8 >= 7 FAIL runs) and
FEAT-48 carries zero findings. **The next rework loop does count, and it is the last one before
`max_total_cycles` binds.**

## Open Questions

- **BLOCKING — operator ruling.** SC-03's ten-site clause cannot be met as written. **(A)** Add
  `fetch-depth: 0` to `.github/workflows/tests.yml` and assert the ten sites inside
  `test-suite-independence.py`: meets SC-03 literally, at the cost of a file outside the signed
  plan's set and a full-history fetch on every CI run. **(B)** Amend SC-03 so the ten-site assertion
  is a review-time automated check — which is what T-03's `verify:` block already is, and what I
  re-executed cleanly this round. My recommendation is **(B)**, because the assertion's value is
  proving the scanner detects the historical shapes, and that is fully obtained at review time,
  whereas (A) charges every future CI run for a fixed historical fact. Either way it is a BRIEF
  amendment and needs the signature.
- **Needs a call.** Whether `code_grade: fail` (now 9 records) is remediated inside FEAT-48 or split
  out. It moved the wrong way, so "it will clear itself with the next fix" is no longer a safe bet.
- **Needs a call.** Whether M4, M5 and the missing `src.replace` control leg are fixed now or become
  backlog rows.
- **Backlog, not a gate.** The suite is not independent of the ambient environment: with
  `HARNESS_AGENT_TYPE` set, `test-plan-merge.py` fails 11 `sign-approval` checks and the whole suite
  exits 1. Pre-existing; the file is untouched by the diff.
- **Backlog, not a gate.** `PASS <file>.py` is not a runner-reserved line shape — 63 files yield 69
  file-level lines. Pre-existing, identical on `main`.
- **Advisory.** SC-07's failing-file clause is established by composition, not by a gate.
- Whether issue #1053 CLOSES on ship remains the operator's call; #1053's `## Scope` still reads
  "Folded into FEAT-47" and only the operator's hand fixes an issue body.
