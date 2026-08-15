# Security review — FEAT-18-board-truth — `main...6d2d61b`

## Verdict: PASS, severity_max info

Scoped IN — the feature adds every new call site that shells out to `gh` for board writes
(`gh_board.py`, `gh-sync.py`'s `start-task`/`close-task`) plus a session-entry read
(`check-state.sh`'s INV-26 block), and widens `harness.json` with board config (`.harness/harness.json`
+24). Untrusted-ish input (`plan.yaml` task status) and a new command-construction surface are both
present, so this earns a full pass, not a scope-out.

## What I actually ran / checked

Reading:
- Read `gh_board.py`, `factory_gh.py` (pre-existing, unchanged by this diff — confirmed via
  `git log -1` on the file), the INV-26 block in `check-state.sh`, `gh-sync.py`'s diff, the
  `check-plan-routes.py` status-enum diff, `branch-create-gate.sh`'s diff (a deletion), and the
  `harness.json` `github.board` addition.
- Traced every call site that constructs a `station` value passed to `gh_board.set_station`:
  `gh-sync.py:574` (`"Building"`, literal) and `gh-sync.py:196` via `derive_station()`
  (`gh_board.py:90-118`, returns only the literals `"Building"`/`"Review"`/`None` — never a
  string read from `plan.yaml` or `feature.json`). No attacker-influenced string reaches a `gh`
  argv or GraphQL variable as a station value.
- Confirmed every `gh` invocation across `factory_gh.py`, `gh_board.py`, `gh-sync.py`'s new code,
  and INV-26's embedded Python uses **list-form argv to `subprocess.run`**, never `shell=True`
  and never string-built shell commands. GraphQL query text (`_FIELD_QUERY`, `_ISSUE_ITEM_QUERY`
  in `factory_gh.py`) is a fixed template; all values ride as bound `-f`/`-F` variables, not
  string-interpolated into the query — rules out GraphQL injection.
- Confirmed the INV-26 block is a single-quoted heredoc (`check-state.sh:24`,
  `python3 - "$root" <<'PY'`) — no shell variable expansion inside it, so nothing from the
  surrounding bash script is interpolated as shell syntax there either.
- Checked `check-plan-routes.py`'s new `status` enum gate (`+326-338`): rejects (appends a
  `VIOLATION`, `not isinstance(...) or status not in LEGAL_TASK_STATUSES`), does not coerce —
  correct fail-closed shape for the trust boundary this feature adds to `plan.yaml`.
- Grepped all new/changed files and fixtures for `token|password|secret|Authorization|ghp_|gho_`
  — zero hits. No credential is read, stored, or logged by any new code path; `gh` remains the
  sole auth holder, consistent with the module's own stated contract (`gh_board.py:1-17`).
- Read `branch-create-gate.sh`'s diff: it **deletes** a block that pinned `project_id`/
  `field_id`/`option_id` in `harness.json` and shelled a GraphQL call using them — net risk
  reduction, no new surface.
- **The fake-binary trap, verified, not assumed.** `gh_board.py:8-12` documents it: a test that
  sets only `GH_SYNC_GH` leaves every `gh_board`→`factory_gh` call going to the real `gh`. Grepped
  `test-gh-sync.py` for `FACTORY_GH`/`GH_SYNC_GH`: its `run()` helper (`:114-119`) sets
  `GH_SYNC_GH = tmp/gh` as a base default on every call, and every station-path test additionally
  passes `{"FACTORY_GH": os.path.join(tmp, "gh")}` — the identical path. Both variables point at
  the same fake in every station-write test; the trap does not fire.

Execution (probes actually run, not just read):
- `test-gh-sync.py` — **ALL PASSED** (100+ checks incl. exact item/option ids, call ordering —
  `--id ITEM_326`/`ITEM_40`, `OPT_BUILDING`/`OPT_REVIEW`, parent-write-before-close ordering, the
  loud-ERROR-line pair, the no-board-configured lifecycle-still-runs pair).
- `test-gh-board.py` — **all pass** (17 checks, incl. `set_station` raising `BoardError` naming
  issue+station on a failing fake `gh`).
- `test-check-plan-routes.py` — **ALL PASS** (incl. `case_25b`: `status: Building` — capital B,
  the board's own spelling — is a VIOLATION, confirming the enum gate is case-sensitive and
  rejects rather than silently passing a plausible-looking value).
- `test-check-state.py` — **EXIT:0**, INV-26's non-vacuity pair both pass: (v.1) mis-columned card
  is a VIOLATION naming feature/task/plan-status/column, (v.2) the corrected twin reports nothing;
  plus (v.4) empty issues map with in-flight tasks, (v.5) recorded-issue-absent-from-board is
  CANNOT VERIFY not a clean pass, (v.7) a nonexistent `gh` binary records no INV-26 finding
  (environmental silence, by design).
- `test-branch-create-gate.py` — **8/8 pass**, including an executed check that "the four config
  keys and the item-edit call are absent from the script" — confirms the deletion, not just the
  diff hunk.

## Findings

**None gating.** Three `info`-level notes, assessed and dismissed, recorded so a later reviewer
doesn't re-raise them cold (P-12):

1. **`info` — error messages surface the first line of `gh`'s own stdout/stderr to the operator.**
   `gh_board.py:33-40` (`BoardError`) wraps `factory_gh.GhError`, whose message includes
   `next_step = _first_line(r.stderr) or _first_line(r.stdout)` (`factory_gh.py:97`). This reaches
   stderr via `gh-sync.py`'s `print(f"gh-sync: ERROR - {e}", file=sys.stderr)` (`gh-sync.py:196,
   576`) and INV-26's `bad.append(...)` lines in `check-state.sh`. Not a new pattern — the same
   `GhError`-to-operator-stderr path already exists pre-diff in `factory_land.py`,
   `factory_claim.py`, `factory_decompose.py`. `gh` itself does not print bearer tokens in its
   error text by design (e.g. "HTTP 401: Bad credentials", not the credential), so this is
   provenance-closed on `gh`'s own error-message contract, not on anything this diff added.
   Reachable by: nobody new — any operator who can run harness tooling already has local `gh`
   auth. No fix proposed.

2. **`info` — INV-26's `gh` board read (`check-state.sh`, `board_stations` → `run_gh` →
   `subprocess.run`) carries no timeout**, unlike the adjacent `gh auth status` probe in the same
   block which does (`timeout=15`). This is pre-existing behavior in `factory_gh.run_gh`
   (unchanged file, not part of this diff), but this feature adds a new call site that now runs at
   **every session entry** rather than only inside an explicit tool invocation, raising how often a
   hung `gh` process (network stall, adversarial/MITM endpoint) could stall session start.
   Availability-only, no data exposure or write, and the mechanism is inherited, not introduced.
   `check-state.sh` is under the DEC-174 carve-out — if this were ever judged worth fixing, it is
   an **operator escalation**, never a team-run fix cycle, since it touches `check-state.sh`
   directly.

3. **`info` — INV-26's own read path fails silent, indistinguishable from "ran clean".**
   `gh auth status` failure, or any exception from `board_stations`, sets `_stations = None` and
   the entire per-feature loop is skipped — nothing is appended to `bad`. Confirmed live: (v.7)
   above shows a nonexistent `gh` binary records zero INV-26 findings, exit unaffected. An
   operator cannot tell "the board agrees with the plan" from "INV-26 never actually checked."
   This is signed design (D-02/DEC-138: "the network is not the tree" — an offline environment
   must never become a red gate), so it is `info`, assessed-and-dismissed rather than a gap — but
   worth naming because it is the G-04 shape (an unauditable silent skip) applied deliberately.

## STRIDE, boundary by boundary

| Boundary | STRIDE | Mitigated |
|---|---|---|
| `plan.yaml`/`feature.json` → `gh` argv/GraphQL vars | Tampering (injection) | yes — list argv, bound GraphQL vars, station values are code literals never plan-derived strings |
| `plan.yaml` task `status` → `check-plan-routes.py` gate | Tampering (bad enum silently accepted) | yes — rejects, does not coerce; case-sensitive, tested live |
| Failed station write → board state | Tampering (silent drift) | partial — loud on stderr per D-02 when a write is attempted and fails; but INV-26's own read can fail silently (finding 3), so a missed live write is only caught if the session-entry check itself succeeded |
| `gh` error text → operator stderr | Information disclosure | yes — provenance-closed on `gh`'s own error contract (not this diff's construction); see finding 1 |
| INV-26 board read at session entry | Denial of service | partial — see finding 2, info only, inherited mechanism |
| `gh` credentials | Spoofing / credential compromise | yes — no token read, stored, or logged anywhere in the diff; `gh` holds its own auth |

## Settled-premise note (required, per dispatch)

Every SC this diff's tests exercise automatically runs against a **fake `gh`** (`FACTORY_GH`/
`GH_SYNC_GH` pointed at a fixture script, verified above). This review's injection/tampering
analysis therefore rests on **code reading plus fake-`gh` test execution** — nothing automated in
this repository exercises the live GraphQL/`gh` API surface. A real-`gh`-only defect (e.g. a
`gh` CLI version whose flag parsing differs from what `factory_gh.py` assumes) would not be
caught by anything run here.

## Not reached / out of scope

`factory_gh.py` is read (consumer relationship) but **not part of this diff** — `git log -1` on
the file shows its last commit predates FEAT-18 (`8122948`, FEAT-13). Findings above about it are
dismissed-context, not gating findings against this diff.

## Carve-out note

`check-state.sh` was touched by this feature (INV-26 block). No finding here requires changing
it — all three `info` notes above are dismissed or, if ever acted on, explicitly flagged as an
**operator escalation**, never a fix cycle, per the DEC-174 carve-out.
