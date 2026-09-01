# Handoff — validate phase — FEAT-41-one-station-vocabulary

## Next

Nothing. Shipped: PR #1108 merged as `ad93d43e`, close records in #1110 (`e7ef01bc`), station `done`
at `b3e943ca`, all 16 cards at done, #845/#867/#1036 closed.

WRITTEN BY THE MAIN SESSION, NOT BY A VALIDATOR LEAD, and that is the honest provenance. Five panel
cycles ran and each returned a verdict to the main session, which acted on every finding; no lead
wrote this note at the time, and the per-cycle digests went to `runs/**`, which is gitignored here.
So it is assembled from the tracked member artifacts in `notes/` plus the fix commits — every claim
below is checkable against those, and nothing is reconstructed from memory.

## Trust

- Five cycles, **eleven `high` findings**, all closed with a commit each — `787c7fa..b3e943ca`
- Cycle 0 (5 high): F-01 a station written nowhere read as a clean ship; F-02 a signer name with a colon corrupted a signed plan; F-03/F-04 spelling and separator evasions; F-05 five gated grade-1 records
- Cycle 1 (2 high): a symlink bypassed the plan write-denial — **Write follows symlinks, measured**; backslash-newline forged a signature
- Cycle 2 (3 high): hardlink, linked parent directory and an over-cap chain all reached `plan.yaml`, the chain **failing open**; `${IFS}` forged a signature
- Cycle 3 (3 high): T-07 destroyed BUG-1030's only non-terminal record; `$(printf ' ')`; a NUL byte disabled the whole hook fail-open
- Cycle 4 (3 high): the `station_only` credential was **mintable**; `xargs` forged a signature; `real()`'s fallback misclassified silently
- Final suites: unit exit 0 **517 PASS**, integration exit 0 **822 PASS**, run serially; gated HIGH code-grade records **0**
- SC-08 measured verbatim at ship: **0** `feature.json` carry a `status` key; INV-34: **0** features without a `plan.yaml`
- Nine sign-gate evasion forms denied END TO END through the real gate, five controls still allowed — verified-at `ba4ba22`
- Two guards the panel proved were DELETABLE without failing anything are now pinned by tests — `_I` case-folding and `_verify_signature`

## Dead ends

- Do NOT re-litigate the nine inverted approval-guard cases; the ALLOW direction they assert is unreachable by design (T-09)
- Do NOT resolve paths on ONE side only in check-domain.sh — shape-matching stays, and resolution must realpath the path AND the root or it lands in a different namespace and matches nothing
- Do NOT treat `--kind unit` as the suite: it covers 29 of 56 scripts, and that gap hid T-01's breakage for four tasks
- Do NOT run the suite from a `/tmp` checkout: cases asserting behaviour for paths outside the repo invert, and 47 of them fail for that reason alone
- Do NOT close SC-01 by scrubbing prose; the operator accepted the narrowed reading in D-18 — 45 `.md` + 10 prose-value hits, **zero** declarations

## Open, deliberately not fixed here

- **#1103** — `plan-sign-gate.py` is a DENYLIST that leaked five times in one class. The structural
  fix is an identity check inside `cmd_sign_approval`; no runtime identity signal reaches a
  subprocess today, verified rather than assumed. It is not a security boundary and does not claim to be.
- **#1104** — a `BRIEF.md`-less directory is never approval-checked. Predates this branch.
- **NEW, found while shipping this feature**: `gh-sync.py` `_commit_terminal_station` runs
  `git -C <feature dir>` while passing the pathspec **as given**, so a RELATIVE feature dir
  resolves the pathspec against that directory, produces a doubled path, reads empty, and reports
  "station already committed — clean against HEAD" without committing. Measured both ways: relative
  → no commit at exit 0; absolute → `station done committed as b3e943ca`. A silent no-op in the
  safe-looking direction, in this feature's own T-06/T-10 surface. Filed separately.

## Working set

- `.harness/harness/features/FEAT-41-one-station-vocabulary/notes/` — 4 cycle-3 member artifacts, two of them recovered from the main checkout where they had been misfiled (FEAT-50 #1057, instances seven and eight)
- `.claude/skills/harness/bin/` — `factory_config.py`, `gh_board.py`, `plan-merge.py`, `check-domain.sh`, `check-state.sh`, `harness_yaml.py`, `plan-sign-gate.py`
- `.harness/harness/docs/DECISIONS.md` — three clauses amended by T-15; D-01..D-18 in `plan.yaml`
