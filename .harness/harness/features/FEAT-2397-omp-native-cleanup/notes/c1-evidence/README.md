# c1 evidence index — FEAT-2397 rework round 1

Per ruling `notes/answers-2026-11-22-c0-escalations.md`, item 4: each receipt records the ref it
actually ran at. The c1 fixes are committed at `b9a8c3adb8c387d24d149e7054ade3fc4654f2b5`. A pin
cannot contain a receipt of its own validation, so these receipts bind forward to the c1 review pin
through the blob identity of the files they cover. The review base is
`522c94b2b79e5e2021cb670910772428c17914b0` (origin/main as merged at `3912d98a`).

| Receipt | Ref | Result |
|---|---|---|
| `t02-transient-522c94b2.txt` | review base | T-02 verify: exit 1, 16 FAIL rows (the red half) |
| `t02-transient-f5c89121.txt` | `f5c89121` (T-02 files byte-identical at b9a8c3ad) | exit 0, 17 OK rows (the green half) |
| `grade-522c94b2-to-b9a8c3ad.json` | base → `b9a8c3ad` | `code-grade.py --base --head --json`: 93 changed functions, 93 passing at their own bar, 0 ungraded |
| `unit-b9a8c3ad-clone-cleanenv.txt` | `b9a8c3ad` | standalone clone, `env -i`, CI command `run-unit-tests.py --kind unit`: every file passes except `test-omp-hooks.py` and `test-factory-config.py` |
| `unit-522c94b2-clone-cleanenv.txt` | review base | same command and environment: the **identical** FAIL set |
| `unit-b9a8c3ad.txt` | `b9a8c3ad` | run in the linked worktree: also red on `test-omp-hooks.py`. Superseded by the clone pair above |
| `check-state-b9a8c3ad.txt` | `b9a8c3ad` | positive discovery: 34 tracked feature.json, then `check-state.py` exit 0 |

## Reading the unit pair

- The two c0 regressions now pass: `test-lead-stop-and-wake.py` and `test-no-distribution.py`.
- The remaining reds are host-environmental. The review base fails the same way on this host:
  - `test-omp-hooks.py`: the five FEAT-2225 `expertise_apply … real core` cases;
  - `test-factory-config.py` (21): FLEET_PATH root identity under the `/var` → `/private/var` temp
    realpath;
  - the BUG-1290 5a/5b/5c lines.
- [INFERENCE] PR CI on a clean runner is the 67/67 receipt for these.

The full check-state run is repeated at the c1 review pin, after the seam commits, and appended
below.
