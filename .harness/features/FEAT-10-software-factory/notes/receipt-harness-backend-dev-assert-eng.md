# Receipt — harness-backend-dev — FEAT-10 A-01, three assertions

**All three gaps closed. Every assertion proved able to fail before being shown green. All three
broken production files restored byte-identical (`diff` exit 0). Suites left green.**

## GAP 1 — SC-13(b), `test-factory-claim.py`

**Set proved distinct, named explicitly:** all SEVEN emittable skip-reason phrases — the five
print sites (`factory_claim.py:277, 281, 286, 302, 315`), where `:302`'s text is
`_blocker_reason_text`'s THREE branches (`edge_i`, `unresolvable`, open/blocked-by) counted
separately. New section `# X` at the end of `test-factory-claim.py`, fixture `sc13b_fixture()`
drives one poll where issues 901–907 each hit exactly one of the seven reasons and nothing is
claimable. Normalisation strips every `#\d+` and every `issue-\d+` occurrence (not just a leading
one), then asserts `len(set(normalized)) == len(reasons)`. Anti-vacuity guards: asserts exactly 7
skip lines fired and that they name issues 901–907 exactly (a fixture that silently short-circuits
would otherwise pass on fewer lines). A bonus check also normalises `T-\d+` — still green, so the
three blocker-gate phrases differ in wording, not merely task id.

- **Demo (a) — two static reasons collided.** Broke `factory_claim.py:286` to print
  `"issue is not open"` (line 277's literal text).
  Red command: `python3 test-factory-claim.py`
  Red output line: `FAIL  (X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every embedded issue number, not just a leading one`
  Restored; `diff factory_claim.py <backup>` exit 0.

- **Demo (b) — the discriminating static/dynamic pair.** Broke `_blocker_reason_text`'s
  blocked-by branch (`factory_claim.py:176`) to return `f"refs/heads/factory/issue-{num} already
  exists"` — exactly `:315`'s phrase shape, with a DIFFERENT embedded number (907 vs 904). A
  normaliser that only strips a leading `skip #N` (not every embedded number) would see
  `issue-907` vs `issue-904` and call them distinct — a vacuous pass. This implementation strips
  every `issue-\d+` occurrence, so both flatten to `refs/heads/factory/issue-N already exists` and
  collide.
  Red command: `python3 test-factory-claim.py`
  Red output line: `FAIL  (X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every embedded issue number, not just a leading one`
  (detail showed `refs/heads/factory/issue-N already exists` appearing twice, for issues 904 and 907)
  Restored; `diff factory_claim.py <backup>` exit 0.

- **Green:** `python3 test-factory-claim.py` → `77/77 checks passed.` (was 70/70; +7 new checks).

## GAP 2 — SC-18, `test-factory-config.py`

Static, AST-based mechanical enumeration (same shape as SC-03's accepted evidence), not a reading
of seven files. `_find_fleet_reads` walks every `factory_*.py` file's AST, finds every
`open(`/`harness_yaml.load_file(` call, and classifies the first argument as fleet-bearing two
ways: (a) its unparsed source text names "fleet" (catches `args.fleet`, the realistic bypass
shape — the trap named `FLEET_PATH` mentions in argparse help and a print statement, which never
appear as arguments to a READ call, so they never trigger this), or (b) it is a parameter/local
variable traced, within the same function, back to a default value of `FLEET_PATH` (catches
`factory_config.load_fleet`'s own `harness_yaml.load_file(path)`, whose argument name says nothing
about "fleet"). A positive control asserts the file enumeration is non-empty and includes
`factory_config.py`, so an empty scan cannot pass vacuously.

- **Red demo.** Added a second, direct fleet read to `factory_land.py:_main` —
  `harness_yaml.load_file(args.fleet)` — bypassing `factory_config.load_fleet` entirely (the
  `args.fleet` shape, not the `FLEET_PATH` shape, per review).
  Red command: `python3 test-factory-config.py`
  Red output lines:
  ```
  FAIL  (X) SC-18: exactly one function, anywhere in factory_*.py, opens/parses the fleet file
          [('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '_main', 51, 'args.fleet')]
  FAIL  (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it
  ```
  Restored; `diff factory_land.py <backup>` exit 0.

- **Green:** `python3 test-factory-config.py` → `56/56 checks passed.` (was 53/53; +3 new checks).

## GAP 3 — SC-19 Case F, `test-factory-integration.py`

Three clauses closed: (i) decompose boards at `ready`; (ii) land pushes the branch; (iii)
workspace produces a checkout, split into a filesystem-existence half and a recorded-git-command
half.

**Recorder:** `_FAKE_GIT_OK_SRC` is now env-gated — when `FACTORY_GIT_LOG` is set to an absolute
path, each invocation appends its argv to that file before exiting 0; unset (every case but F),
it is the exact same no-op as before. Case F sets `env["FACTORY_GIT_LOG"]` to a per-case temp
path. Confirmed no other case's verdict moved: `diff` between the pre-change and post-change full
`test-factory-integration.py` output shows exactly 4 added `ok` lines and the total-count line;
every other line is unchanged.

- **(i)** `read_state(gh_state)` immediately after decompose (before claim runs) asserts both
  board items' station equals the fixture fleet's OWN declared `ready` option
  (`fleet_data["board"]["stations"]["ready"]`, not a hardcoded `"Ready"`).
  Red: broke `factory_decompose.py:353` from `factory_config.station(fleet, "ready")` to
  `factory_config.station(fleet, "building")`.
  Red output: `FAIL  (F) decompose: both board items boarded at the fleet's declared ready station`
  (detail showed both items at station `'Building'`). Restored; `diff` exit 0.

- **(ii)** Reads the recorder log after the `land` step; asserts a line starting with `push`
  containing `--set-upstream`, `origin`, and the claimed branch.
  Red: suppressed the push call at `factory_land.py:60` (commented it out).
  Red output: `FAIL  (F) land: recorded git commands include a push of factory/issue-<n> to origin`
  (detail showed the recorded log with no `push` line). Restored; `diff` exit 0.

- **(iii), cheap half:** `os.path.isdir(p3["path"])` after the workspace step.
  **(iii), other half:** reads the recorder log after `workspace`; asserts a `checkout` line
  contains the claimed branch.
  Red: broke `factory_workspace.py`'s final checkout (`_checkout_issue_branch`'s no-remote-ref
  branch) to check out `"wrong-branch-name"` instead of `branch`.
  Red output: `FAIL  (F) workspace: recorded git commands include a checkout of factory/issue-<n>`
  (detail showed `checkout -b wrong-branch-name origin/main`). Restored; `diff` exit 0.

- **Green:** `python3 test-factory-integration.py` → `97/97 checks passed.` (was 93/93; +4 new
  checks, 0 new cases — matches the dispatch's "new checks inside existing Case F raise 93 but
  not 14").

## Backups and restores

Every production file broken was first written verbatim to the scratchpad (`Write`, since `cp`
into the scratchpad is blocked by `bash-write-guard`), and every restore was verified with `diff`
(exit 0 in every case, shown above and re-confirmed here):

| File | Backup | Restore verified |
|---|---|---|
| `factory_claim.py` | `.../scratchpad/factory_claim.py.bak` | `diff` exit 0 (both demos) |
| `factory_land.py` | `.../scratchpad/factory_land.py.bak` | `diff` exit 0 (GAP 2 + GAP 3(ii)) |
| `factory_workspace.py` | `.../scratchpad/factory_workspace.py.bak` | `diff` exit 0 (GAP 3(iii)) |
| `factory_decompose.py` | `.../scratchpad/factory_decompose.py.bak` | `diff` exit 0 (GAP 3(i)) |

(Backup dir:
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/cd83b531-197f-4da6-a4a5-9bb0ec5fcaa5/scratchpad/`)

No file was staged or committed. No production behaviour changed in the final state.

## Final suite state (verbatim final summary lines)

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh
...
13/13 checks passed.        PASS test-harness-yaml-corpus.py
15/15 checks passed.        PASS test-render-brief.py
10/10 checks passed.        PASS test-team-catalog.py
33/33 checks passed.        PASS test-factory-cli.py
76/76 checks passed.        PASS test-factory-gh.py
56/56 checks passed.        PASS test-factory-config.py     <- was 53/53 (+3)
30/30 checks passed.        PASS test-factory-workspace.py
123/123 checks passed.      PASS test-factory-decompose.py
77/77 checks passed.        PASS test-factory-claim.py      <- was 70/70 (+7)
45/45 checks passed.        PASS test-factory-land.py
...
97/97 checks passed.        PASS test-factory-integration.py  <- was 93/93 (+4)
```

`run-unit-tests.sh --kind unit` → still **10/10** registered unit-script files PASS.
`run-unit-tests.sh --kind integration` → still **14/14** registered integration-script files
PASS, including `test-factory-integration.py`.

**What moved and by how much, stated exactly per the dispatch's demand:** the FILE-level gate
counts (10/10 unit files, 14/14 integration files) are unchanged — no file was added or removed
from either registry. The CHECK-level counts inside three existing files moved:
`test-factory-claim.py` 70→77 (+7), `test-factory-config.py` 53→56 (+3),
`test-factory-integration.py` 93→97 (+4, all new checks landed inside the existing Case F, no new
case). No other file's check count changed (confirmed by diffing the full pre/post
`test-factory-integration.py` run — 4 added `ok` lines only).
