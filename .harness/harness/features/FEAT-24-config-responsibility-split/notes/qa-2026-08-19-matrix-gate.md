# QA — test_matrix gate — FEAT-24 — pinned at `b0604c3`

## VERDICT: FAIL

`T-05` (a DEC-174 carve-out, `status: done` in `plan.yaml`) never got its own required test cases
written. Its own `verify:` block fails at the first assertion. `SC-03` (check-state.sh half) and
`SC-12` have **zero automated evidence** in the tree, despite both being `verify: automated`.
The full suite is green only because nothing exercises the missing behavior — this is exactly the
fail-open-nothing-can-see defect class this feature exists to remove.

Separately: **the dispatch's "Gap 2" is stale — both halves (base64 line-wrapping, and the
`-f`/POST argv shape) are already closed inside the pinned diff**, at commit `574f73c` and the
`"-f" not in argv` assertion added alongside it. I mutation-proved the `-f` assertion reddens
against the real historical defect shape (`-f ref=<branch>`, which forces `gh` to POST). No live
smoke is warranted for Gap 2. Gap 1 (the `validate=True`/`validate=False` base64 fail-open) is
real and remains open — I could not close it myself; `check-domain.sh` denies `harness-qa` write
access to `test-factory-gh.py`.

## Branch tip vs pin

`b0604c3..HEAD` touches only `feature.json`, `notes/handoff-build.md`, `plan.yaml` (2-line status
edit) — no code. Confirmed via `git diff --stat b0604c3..HEAD`. Measured against the pin throughout.

## T-05 is broken — the load-bearing finding

Ran T-05's own `verify:` block from `plan.yaml` verbatim against `test-check-state.py` at the pin:
it fails immediately — `"INV-26 reports a violation when the board declaration is unusable"` is not
a case in the file. Checked all five required ok-lines directly against `test-check-state.py`; **none
exist**:
- `INV-26 reports a violation when the board declaration is unusable` — absent
- `INV-26 completes the gate rather than aborting on an unusable board` — absent
- `INV-26 expects the declared station for status: backlog/building/done` — absent, all three

Also absent: the `INV-26 BEGINS` / `INV-26 ENDS` marker comments T-05 item 7 requires
(`.claude/skills/harness/bin/check-state.sh` — `grep -c "BEGINS\|ENDS"` = 0), so even the verify's own
positive-control slice can't run.

`check-state.sh`'s **production code** looks correct on inspection (`:1123-1146`): `load_board` is
wrapped in `try/except FleetError`, appends one `bad` entry naming the invariant, and the block
continues rather than aborting; `_EXPECT` (`:1180`) is built from the loaded board's `stations`, not
literals. I did not find a way to prove this behaviour live without perturbing a tracked config file
in the main checkout (forbidden), so this is a **reasoned**, not measured, assessment of the source
(O-03) — the point stands regardless: there is no automated evidence for it in the tree.

This resolves as **missing → FAIL**, not misconfigured (no import/collection error — the assertions
were simply never written) and not a "kind" shortfall (`test-check-state.py` runs fine under
`--kind integration`; the specific cases required by `SC-03`/`SC-12` just don't exist inside it).

**`must_fix`**: add the five T-05 cases and the two marker comments to `test-check-state.py` /
`check-state.sh`. Route to `harness-backend-dev`/main-session-direct per the DEC-174 carve-out that
already governs this file. `SC-03` and `SC-12` cannot be marked met until this lands.

Everything else pre-ruled GREEN was re-confirmed live and holds: T-01, T-02, T-04 (I additionally
ran T-04's verify myself — it passes in full, including the four non-reader positive controls and
the gh-sync/board-station loud-exit cases), T-08, T-09, T-10, `gen-decisions-index.py --stdout`
byte-identity, and the full suite (`run-unit-tests.sh --kind all` → `rc=0`, zero `FAIL` lines,
1365 `ok` lines).

## Task 1 — detect table

`test_kinds.integration.detect` in `.harness/harness.json` is a 4-item explicit enumeration:
`test-check-state.py`, `test-factory-integration.py`, `test-gh-sync.py`,
`test-check-plan-routes.py`. Confirmed at source. `test-factory-gh.py` and `test-factory-config.py`
match only `unit`'s glob (`.claude/skills/harness/bin/test-*.py`) and appear in **no** integration
entry — confirmed.

A second, systemic fact this exposed: `run-unit-tests.sh`'s real `INTEGRATION_SCRIPTS` array has
**12** scripts, not 4 — it also runs `test-check-domain.py`, `test-bash-write-guard.py`,
`test-check-expertise.py`, `test-gen-decisions-index.py`, `test-harness-yaml.py`,
`test-upgrade-config.py`, `test-merge-settings.py`, `test-validate-digest.py` under `--kind
integration`, none of which the `harness.json` detect glob names. This predates FEAT-24 (not
introduced by this diff) and is a config-accuracy gap in `test_kinds.integration.detect`, not this
feature's defect — noted, not blocking.

| change_type | task | detect (a): does integration's glob name a changed file? | exercise (b): does an integration-kind test actually run the changed code? |
|---|---|---|---|
| api | T-01 (`factory_gh.py`) | **No** — `test-factory-gh.py` matches only `unit` | **Yes** — `test-factory-integration.py` (integration-registered, and its `contents/` endpoint fake was *added in this diff*, part of T-03) drives `product_config`→`file_at_ref` end-to-end |
| cross_module | T-02 (`factory_config.py`) | **No** — `test-factory-config.py` matches only `unit` | **Yes** — same `test-factory-integration.py` path exercises `product_config`/`board_for`/`validate_board` |
| cross_module | T-03 (5 test files) | Mixed — `test-factory-integration.py` and `test-check-domain.py` both run under integration (registration, not detect-glob) | **Yes** — T-03's own verify (pre-ruled GREEN) runs all five suites live |
| cross_module | T-04 (`gh_board.py`, `gh-sync.py`, `board-station.py`) | `test-gh-sync.py` is named in detect **and** registered | **Yes** — confirmed live, full T-04 verify green |
| cross_module | T-05 (`check-state.sh`) | `test-check-state.py` is named in detect **and** registered, kind executes it | **No** for the specific new behaviour — see finding above. The kind runs the file; the file lacks the assertions |

So: for T-01 and T-02, (a) is false but (b) is true — real coverage exists, the detect list is just
stale/incomplete for those two files. That is a config finding, not a kind shortfall — I am not
marking `matrix_ok: false` for it (rule: kind shortfall vs adequacy finding are different keys). For
T-05, neither (a) nor (b) holds for the specific behaviour under test — that is a genuine adequacy
gap, reported above.

## Task 2 — `touches_db_or_external` for `api` (T-01)

**Ruling: true.** `factory_gh.file_at_ref` (T-01) issues a live `gh api repos/.../contents/...`
call to the GitHub REST API — that is external by any reading of the predicate; the object under
test is the diff, not its test harness (the counter-reading conflates the two). `T-02`'s
`product_config` reads a fleet member's `harness.json` from the remote at `default_branch` with **no
checkout**, by design (D-03) — same call.

Given `true`, T-01 requires `integration` per the floor. Per the detect table above, mechanical
detect (a) fails but substantive exercise (b) is satisfied via `test-factory-integration.py`. I rule
this **satisfied**, not missing, with the detect-list staleness flagged as a separate, non-blocking
config finding.

## Task 3 — the two coverage gaps

### Gap 1 — `validate=True`/`validate=False` fail-open in `factory_gh.py:453`

**Confirmed live, not closed, and I could not close it myself.**

Measured (standalone script, no tracked file touched):
```
"not-valid-base64!!!" -> validate=True raises Error("Only base64 data is allowed")
                       -> validate=False ALSO raises Error("Incorrect padding")
"aGV!sbG8="            -> validate=True raises Error("Only base64 data is allowed")
                       -> validate=False decodes SILENTLY to b"hello"
```
This confirms the dispatch's premise exactly: the existing case cannot discriminate; `aGV!sbG8=` can.

**I attempted to add the discriminating case to `test-factory-gh.py`** (after `file_at_ref:
undecodable content raises rather than returning empty`, ok-line: `file_at_ref: non-alphabet
base64 raises rather than silently decoding under lax mode`) and **the write was denied by
`check-domain.sh`**: `harness-qa` is not a granted writer for
`.claude/skills/harness/bin/test-factory-gh.py` in this repository's own manifest — only
`.harness/*/features/*/notes/qa-*.md` and Expertise/observations paths are mine. This is the
project's own DEC-189-style domain guard working as designed; per QA rules I do not work around it.

**Ruling: the matrix demands it (T-01 is `api`, `unit` is the floor, and this is the exact
silent-vs-loud distinction `REQ-04`/T-01 item 3 pins), and it is unclosed.** `must_fix`, routed to
`harness-backend-dev`: add the case above (exact text and driver given).

**What I actually measured, precisely stated** (no overclaim): a bare `base64.b64decode` probe on
the two candidate strings, in a throwaway interpreter, touching no tracked file:
`aGV!sbG8=` raises `Error("Only base64 data is allowed")` under `validate=True` and decodes
silently to `b"hello"` under `validate=False`; `"not-valid-base64!!!"` raises under **both** modes.
This establishes the discriminating driver exists. **I did not run this against the real
`file_at_ref` function** — I have no write access to add the case or to run a perturbation proof
against the real file, so I cannot claim a mutation proof for Gap 1 (unlike Gap 2 below, where I
did run the real assertion against a reproduction of the real defect shape). A dev with write
access should apply the mutation (flip `validate=True` → `validate=False` in a worktree, per
DEC-153), confirm the new case reddens and `"not-valid-base64!!!"` stays green, then revert and
show `git status --porcelain` clean.

### Gap 2 — the fake-recorder systemic gap (POST-vs-GET, base64 wrapping)

**Both halves are already closed, inside the pinned diff — the dispatch's description is stale.**

- **Wrapping**: `test-factory-gh.py` already has a case (`file_at_ref: decodes GitHub's
  line-wrapped base64 content`, added at commit `574f73c`, inside `ada8e99..b0604c3`) that wraps a
  synthetic payload at 60 chars and asserts the decoded body round-trips. `"".join(raw.split())`
  handles it, so this is correctly a **regression pin**, not a discovery — consistent with what the
  dispatch predicted this half would look like once done.
- **Method/POST**: the `file_at_ref: hits the contents path with the ref` case already asserts
  `"-f" not in calls[0]["argv"]` (added in the same commit range) — the cheaper, no-network remedy
  the dispatch asked me to evaluate. **Mutation-proved live**: I wrote a standalone `bad_file_at_ref`
  reproducing the historical defect shape (`-f ref=<branch>`, which is what forces `gh` to POST) and
  ran the real assertion against its recorded argv — it correctly evaluates to `False` (would redden
  the real case). No source file was touched to run this proof.

**Ruling on the live-smoke question** (per the dispatch's own distinction): T-07 and T-09's
`verify:` blocks already run live `gh api` against kaya at `master`, and
`test-factory-workspace.py` already smokes a real `git` binary — so *"a live check is
unprecedented here"* is false; only *"no live network inside the unit suite"* (the BRIEF's actual
objection) is supported. Given both halves of Gap 2 are now closed by fast, deterministic,
no-network cases that are proven to discriminate, **no live smoke is warranted for this gap** — the
cheaper remedy the dispatch asked me to check for was already available and used.

## File set — lanes vs diff

One discrepancy: **`.claude/skills/harness/bin/test-factory-workspace.py` is in the diff
(`ada8e99..b0604c3`) but is not listed in `plan.yaml`'s `lanes:` rows, and appears in no task's
`files:` list.** The change itself is small and correct in isolation — `good_fleet_dict()` drops the
`board` key from the fleet entry (T-02/T-03's own cutover would otherwise redden this fixture) — but
it was made outside any declared task surface or lane grant. Flagging per the dispatch's explicit
instruction to report any diff file `lanes:` doesn't list. Not a blocking finding on its own (the
edit is correct and necessary), but the lane bookkeeping is incomplete.

All other `lanes:` rows are touched in the diff. The one lane row not expected to appear in this
repo's diff — kaya-ai's own `harness.json` — is external by design (D-04) and is verified separately
by T-07/T-09's live `gh api` checks, both pre-ruled GREEN.

## SC evidence map

| SC | test | status |
|---|---|---|
| SC-01 | `test-factory-config.py:316` `load_fleet rejects a repos entry carrying a board key` | met (T-02 green) |
| SC-02 | per-key tally, 2/5 satisfy SC-02's own "fails if reverted to literal" bar: **building** — `test-gh-board.py:` `derive_station returns the declared building station` (board deliberately uses `Col-B`, so a reverted literal reddens it) ✓. **review** — same file, `Col-R` ✓. **ready** — `test-factory-decompose.py:412` `(2) both stations set to the fleet's ready option` asserts `== "Ready"`, but the fixture's own `ready` value is also literally `"Ready"` (`:196,224`), so a hardcoded `"Ready"` fallback would pass this case too — present but non-discriminating ✗ (does not meet SC-02's "fails if reverted" bar; same for `test-factory-land.py`'s review-station case, which uses `"Review"` against a fixture value of `"Review"`). **backlog** and **done** — resolved only inside T-05's missing INV-26 cases; no test exists ✗. **SC-02: 2/5 satisfied, 3/5 not** (`ready` non-discriminating, `backlog`/`done` absent) |
| SC-03 | `test-gh-board.py` literal-grep (met, T-04 green) + T-05's marker-sliced grep on `check-state.sh` | **unmet for the check-state.sh half** — no positive-control slice exists (markers absent) |
| SC-04 | `test-gh-board.py` (8 `load_board` raise cases) + `test-factory-config.py` (8 `board_for` raise cases) | met (both T-02 and T-04 green, 16 cases confirmed) |
| SC-05 | `test-factory-config.py`/`test-gh-board.py:90` null-board and absent-board cases | met |
| SC-06 | `test-factory-config.py:526,560` no-checkout + no-fallback cases | met |
| SC-07 | `test-factory-land.py:288` `(M1) pr create base is the fleet's default_branch`, `test-factory-claim.py:709` default_branch case, `test-factory-integration.py:618` `(D-workspace) success: exits 0`, `test-no-distribution.py:166` `case3_presence_kaya_default_branch_is_master` | met (T-03/T-07 green) |
| SC-08 | `test-no-distribution.py:160` `case3_absence_harness_is_not_a_fleet_member` | met |
| SC-09 | inspection — not mine to verify further | n/a (inspection) |
| SC-10 | T-04's non-reader grep (4 files, positive-controlled) + `test-factory-config.py`/`test-gh-board.py`/`test-gh-sync.py` behavioural cases | met |
| SC-11 | `gen-decisions-index.py --stdout` byte-identity (pre-ruled), T-10 verify (pre-ruled) | met |
| SC-12 | T-05's `INV-26 reports a violation...` / `INV-26 completes the gate...` cases | **unmet — no test exists** |
| SC-13 | `run-unit-tests.sh --kind all` (confirmed rc=0, 1365 ok, zero FAIL) + `git diff --diff-filter=D --name-only ada8e99..b0604c3` (empty — no file deleted) + `run-unit-tests.sh` itself absent from the diff (registration arrays unchanged) | met, both halves |

## One more matrix note — T-05's unit kind is detected but never executed

`test-check-state.py` matches `unit`'s detect glob (`.claude/skills/harness/bin/test-*.py`), so
`matrix_ok` stays `true` on the "nothing detecting" trigger the dispatch defines. But
`run-unit-tests.sh`'s `UNIT_SCRIPTS` array never lists it — it is registered only in
`INTEGRATION_SCRIPTS` — so `--kind unit` executes nothing over `check-state.sh`. Detected, not
executed (P-14). Not a `matrix_ok` violation under the dispatch's own definition, but worth saying
out loud rather than leaving silent.

## Coverage gaps vs Phase 1

I read `BRIEF.md` before `plan.yaml`, but `plan.yaml` itself pins every required test's exact
ok-line text verbatim (T-01 through T-10 all list literal strings), which structurally collapses
most of the Phase-1-vs-Phase-2 gap for this feature — a prescriptive plan, not independent
derivation on my part (O-05). From the BRIEF alone, the tests I'd have expected are exactly what
the plan pins: one loud raise per malformed board shape at both entry points, one per-station-key
proof that fails on a reverted literal, and a check-state.sh behavioural test proving INV-26
reports rather than aborts. **The last of those three is exactly what's missing** — `SC-03`'s
check-state.sh half and `SC-12` have zero automated evidence, which is the one place Phase 1's
un-primed expectation and the actual tree diverge.

## Open questions

- `{ id: Q1, question: "The dispatch instructed me to close Gap 1 myself ('these are yours to close or to rule out'), but check-domain.sh denies harness-qa write access to .claude/skills/harness/bin/test-factory-gh.py — only notes/observations/expertise paths are granted. The guard is correct per this repo's manifest; the dispatch's premise that I could write test files here was false. Should qa dispatches for this repo stop assuming test-file write access, or should the manifest grant qa a scoped test-file path?", blocking: false }`
