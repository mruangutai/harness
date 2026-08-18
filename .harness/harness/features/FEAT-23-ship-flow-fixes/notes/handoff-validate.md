# Handoff — FEAT-23, validate → shipped — written at 7596cd0

## Next

**Nothing. The feature is shipped.** The operator accepted at `7596cd0`; `gh-sync.py ship`
closed milestone 14 and parent `#454`, and flipped `feature.json` to `Done` — the first ship to
do that automatically, which is this feature's own `#417` fix working on its own close.

Remaining, and it is the main session's: file the unstruck backlog rows, push the branch, open
the PR. `#417`, `#430` and `#453` close on merge, not before.

## Trust

- **Four validator rounds ran on one contract, and only the fourth passed clean.** Round 1
  (`afc8cfd`) found the argument gate crashed on a Unicode digit. Round 2 found the fix pinned
  one of two classes — the untested half moved the WRONG CARD silently. Round 3 found a third
  class no predicate had reached, and recommended closing by construction rather than
  enumerating. Round 4 confirmed the family closed: `must_fix: []`, `severity_max: low`.
- **The guard's two conjuncts read different variables and that is load-bearing.** `isascii()`
  and `isdigit()` read the original string; only positivity reads the parsed number. The
  reviewer built the merged form a tidier reader would write and measured it passing `٢` at
  exit 0. The comment at `board-station.py` says so; the Arabic-Indic case pins it.
- **The EXIT CONTRACT is now scoped to command-line arguments.** It previously claimed 2 was the
  only non-zero exit unconditionally, which no guard in the file can hold — a closed stdout ends
  in 120 at shutdown flush.
- Gates at this tip: unit 0, integration 0, T-02/T-03/T-05 GREEN, `check-state.sh` 0.

## Dead ends

- **Do not merge the guard's two conjuncts onto the parsed value.** Measured: it reopens the
  silent-wrong-card class.
- **Do not add a fourth predicate for a newly-found bad input.** Two rounds did that and each
  shipped with one class open. The parse is wrapped; new refusals are caught already.
- **Do not shrink the playbook's copy of the apply bounds.** T-03's signed intent requires them
  there; the drift rule decides which statement wins, it does not licence deleting one.

## Working set

- `.claude/skills/harness/bin/board-station.py` and its suite
- `.claude/skills/harness-simplify/SKILL.md`
- `notes/ship-review-2026-08-17-13.md` — 30 backlog rows
- `runs/2026-08-18-16-construct-validator/digest.md` — the passing round
