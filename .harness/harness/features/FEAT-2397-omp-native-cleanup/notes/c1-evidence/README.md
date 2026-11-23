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

## check-state at the c1 pin 9c38040397bb115583e71b13f1a7ca4bf2f10c2e

```
tracked feature.json: 34
exit=0
```

## SC-04: the exact executed check (appended after c1, closing the form finding)

`t02-transient-executed-check.sh` holds the exact bytes executed for both transient receipts. It
is 2208 bytes, sha256 `0b89614e55489428936ad5aaff1b46850fcde67ed9a1c57c422c36764e9783fd`. Those bytes are `plan.yaml` `tasks[1].verify` verbatim, plus one
trailing newline, extracted with
`python3 -c "import yaml;print(yaml.safe_load(open('<FD>/plan.yaml'))['tasks'][1]['verify'])" > /tmp/t02v.sh`.
No rerun was made for this append. The outputs, refs and exits above are the original
receipts.

The invocation for each ref, from the worktree:

```
D=$(mktemp -d); git archive <ref> | tar -x -C $D
(cd $D && unset HARNESS_AGENT_TYPE CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR && bash /tmp/t02v.sh) > t02-transient-<ref8>.txt 2>&1
echo "ref=<ref8> exit=$?" | tee -a t02-transient-<ref8>.txt
```

- `<ref>` = `522c94b2b79e5e2021cb670910772428c17914b0`: exit 1.
- `<ref>` = `f5c89121`: exit 0.

The script itself exports `HARNESS_PROJECT_DIR="$PWD"` (its line 2), so it reads the
archived tree it runs in.

## Correction (2026-11-23)

The original text above stands. Two claims in it are withdrawn under
`notes/answers-2026-11-23-fix-c2.md`.

- **test-omp-hooks.py "host-environmental": withdrawn.** The clone pair's own header shows that
  both runs exported `HARNESS_PROJECT_DIR=<clone>`. That export is what makes the FEAT-2225
  host-core block fail, and CI's Unit step exports it since T-02. This was a product defect. It is
  fixed test-only in `dfe27d14` and `c1eb9eaa`; see `notes/fix-c2.md`.
- **"the BUG-1290 lines": withdrawn.** They are the expected mutation-proof output of
  `test-factory-claim-mutation.py` ("MUTATION PROOF: 3/3 cases reddened", PASS, exit 0), not
  failures.

The only host-only reds are `test-factory-config.py` (21), from the `/var`→`/private/var`
realpath, and INV-29 on a host Kaya worktree. Both are the same at base:
`notes/fix-c2-evidence/checks-job-local.txt`.
