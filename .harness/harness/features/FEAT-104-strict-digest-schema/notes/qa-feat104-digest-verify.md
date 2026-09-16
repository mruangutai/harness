# QA · FEAT-104 digest-repair verify

**Conclusion: PASS.** The repaired digest at `runs/2026-09-09-02-qa-gate-validator/digest.md` is
schema-valid, its operative (last) anchor is `PASS`, the cycle-1 `FAIL` record survives intact
beneath it, and nothing outside the record file was touched.

## 1. Validator (persona `lead`, path second)
```
$ python3 .claude/skills/harness/bin/validate-digest.py lead .harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-02-qa-gate-validator/digest.md
digest ok
VALIDATE_EXIT=0
```
stdout is exactly `digest ok`; stderr empty. Exit 0. Per the assignment this is a shape check only
— it would pass whichever verdict block were last — so it does not by itself say which verdict is
operative. See §2 for that.

## 2. Verdict anchors (`grep -nE '^[[:space:]]*VERDICT:'`)
```
4:VERDICT: PASS
150:VERDICT: FAIL
216:VERDICT: PASS
```
Three anchors found, confirming the lead's reported set exactly: line 4 `PASS`, line 150 `FAIL`,
line 216 `PASS`. **The LAST anchor is line 216, token `PASS`** — this is the block
`validate-digest.py` actually sliced and validated in §1, since it anchors from the last match.

## 3. Cycle-1 FAIL block survival
`sed -n '149,153p'` shows the FAIL block's head intact, unaltered:
```
```yaml
VERDICT: FAIL
DIGEST:
  headline: "QA gate FAILS: the suite is red at committed tip 50c4bce9 (exit=1), and the only green reading came from team-authored edits to two of the gates' own test files, which DEC-174 forbids — five exact reapply sites handed to Main."
  team: qa-gate
```
The four distinctive cycle-1 strings (`AMENDED RETURN — DEC-174 ruling`, `Exact reapply set for
Main`, `_bug1305_marker_recovery_cases`, `severity_max: high`) each match exactly once —
`grep -c` returns **4**. File is 261 lines total. **The cycle-1 FAIL block and its reapply-set
table are intact**, not erased by the append.

## 4. Blast-radius check outside the record file
```
$ git -C .../FEAT-104-strict-digest-schema status --porcelain -- tests/ .claude/skills/harness/bin/ .agents/skills/harness/bin/ .omp/agents/
(empty)
```
Empty output. **No file under `tests/`, either `bin/` tree, or `.omp/agents/` was modified.**
(`runs/**` is gitignored, so the digest itself never shows here — expected, not evidence of no
change; the direct reads in §2/§3 are the actual proof for that file.)

## Verdict basis
All four PASS conditions hold: validator clean · last anchor (216) is `PASS` · cycle-1 FAIL block
survives (grep count 4, sed confirms header) · git status outside the record file is empty.
