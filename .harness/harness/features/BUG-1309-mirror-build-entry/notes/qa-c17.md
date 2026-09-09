# qa c17 — test-matrix gate, T-05 parser remediation, pinned at 94b5e465

**BLUF: PASS.** Both required matrix kinds are green, T-05's `verify:` printed `VERIFY-PASS`
(26/26 named cases), all four graded qualnames clear the bar-4 floor, and all three SC-11
recovery cases are independently confirmed discriminating (red at `e374c9a2`, green at the
pin) by my own re-run — not inherited from the packet's claim. The three previously-silent-allow
merge forms now deny, measured directly. One correction to the dispatch's own framing: T-05's
`change_type` in `plan.yaml` is `feature`, not `bugfix` — does not change the floor (`unit` +
`integration` are unconditionally required either way here), but the dispatch's premise was
wrong and is recorded per G-11.

## Matrix resolution (change_type = `feature`, not `bugfix` as dispatched — plan.yaml:1043 area)

`feature`: `always: [unit, integration]`. No `when` fires (`ui`/`has_interaction_flow`: n/a, no UI
surface touched). Floor = `{unit, integration}`, both required unconditionally.

| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0, 33 files, all PASS |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0, 50 files, all PASS (`test-merge-gate.py` independently confirmed via `run_pool.py -- tests/integration/test-merge-gate.py`: 25 `ok` lines + `ALL PASSED`) |

`matrix_ok: true`.

## T-05 `verify:` block, extracted programmatically from `plan.yaml` to `/tmp/t05_verify.sh`

Cross-check against the dispatch's quoted lines 1/2/4-11: byte-identical. The truncated `for n in`
line (26 quoted names) verified separately by regex extraction — **26/26 names present**, matching
the dispatch's cross-check list exactly (diffed name-by-name).

Ran `env -u HARNESS_AGENT_TYPE bash /tmp/t05_verify.sh` from the worktree root:
```
VERIFY-PASS
exit 0
```
All 26 gated `ok    <name>` lines matched (script would have `exit 1` on the first miss — it
didn't). `test-omp-hooks.py`, `merge-settings.py --check` ("all 9 prerequisites present (8 hooks")
and the grade assertion (`git_merge`≥4) all held inside the block.

## Code grades — four qualnames (`code-grade.py .../merge-gate.py --json`)

| qualname | grade | bar | result | cyclomatic | cognitive | abc |
|---|---|---|---|---|---|---|
| `git_merge` | 4 | 4 | PASS | 3 | 4 | 6.7 |
| `option_end` | 5 | 4 | PASS | 1 | 1 | 2.0 |
| `first_subcommand` | 5 | 4 | PASS | 3 | 3 | 4.7 |
| `merge_target` | 4 | 4 | PASS | 4 | 5 | 7.1 |

All four clear the bar-4 floor D-17/T-05 grade clause names.

## SC-11 recovery cases — individually discriminating (own re-run, not the packet's claim)

Built a scratch bin (`/tmp/oldbin`) = current `.claude/skills/harness/bin/` with `merge-gate.py`
overwritten by `git show e374c9a2:...merge-gate.py` (verified diff shows the swap landed only on
`git_merge` and its removed helpers). Harness at `/tmp/discriminate_sc11.py` reuses the pinned
test file's `fixture()`/`gate()` shape, pointed at each `merge-gate.sh` in turn:

| case | exists (test-merge-gate.py) | passes at pin | reddens at e374c9a2 |
|---|---|---|---|
| `T-05 merge --abort on an owing branch allows` | yes (line 192) | yes (rc=0, decision=None) | **yes** — old code denies (`deny`, reason names the fixture feature's `recovery-required`) |
| `T-05 merge --continue on an owing branch allows` | yes (line 193) | yes | **yes** — same |
| `T-05 merge --quit on an owing branch allows` | yes (line 194) | yes | **yes** — same |

All three DISCRIMINATING. None is reported non-discriminating.

## Premise check — the three measured silent-allow forms, at the pin

Fixture: `FEAT-9001-fixture-non-era`, `build_entry: recovery-required`, `github.sync: true`,
`github.repo: "acme/widgets"`. Drove `merge-gate.sh` (the pinned copy) directly, exact commands
and output:

- `git merge -F /tmp/msg.txt feature/test` → `decision=deny`, reason names the fixture feature and
  `recovery-required`.
- `git merge --cleanup strip feature/test` → `decision=deny`, same reason.
- `git --attr-source HEAD merge --no-ff feature/test` → `decision=deny`, same reason.

All three now DENY (were SILENT ALLOW at `e374c9a2` per the packet's measurement). Confirmed
directly, not inherited.

## Test-first audit — what the record shows and what it does not

The implementation and its seven new test cases landed in **one commit**
(`94b5e465`, `.claude/skills/harness/bin/merge-gate.py` + `tests/integration/test-merge-gate.py`
together, +50/-26). **Git history cannot show write-order within one commit** — this is stated
plainly, not inferred either way. The packet
(`notes/direct-packet-2026-09-08-c16-parser.md` §"Red before green") instructs adding the cases
first and running red before editing `merge-gate.py`, and claims all seven fail at `e374c9a2`.
The orchestrator's own c16 observation log (`observations/harness-orchestrator.md:47-50`) records
that a 10-line probe against `merge_ref` verified "every red-before-green claim in the packet" as
part of packet-writing, i.e. **before** dispatch — this corroborates the packet's redness claim
but is not itself evidence of the actual write-then-run-red step during implementation. No
preserved red-run output (stdout capture, note, or receipt) from the implementation step itself
was found under `notes/` or `observations/` for c16/c17. **I cannot verify the write-then-red
step occurred in that order; I can and did independently reproduce that the seven cases redden
against `e374c9a2` right now (three of the seven — the SC-11 cases — directly above; the other
four, all `deny` assertions, were not separately re-driven here as they are outside this
dispatch's SC-11 scope but their presence + pass-at-pin is confirmed via the 26/26 verify gate).**
This is a gap in the record, not a violation — reported per the rule that absence of evidence is
not itself a finding of non-compliance.

## Coverage gaps (Phase 1 vs Phase 2)

None identified beyond the above. Phase-1-derived expectations (BRIEF SC-04, SC-11; T-05 `verify:`
26 names; grade bar on `git_merge`/`option_end`/`first_subcommand`/`merge_target`) are all matched
by an actual test or gate in the diff.

## SC evidence

- SC-04 (deny on absent/`recovery-required` build_entry, incl. the flag-aware walk): T-05's 26-name
  `verify:` gate (`plan.yaml` T-05) + `tests/integration/test-merge-gate.py` full run — 50/50 files,
  25/25 cases in that file green.
- SC-11 (merge --abort/--continue/--quit allow on an owing branch, discriminating against
  `e374c9a2`): three cases above, individually confirmed discriminating by direct re-run.

## DIGEST is authoritative for routing; this note is the pointer trail.
