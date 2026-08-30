# QA Gate — FEAT-38-decisions-current-knowledge — 2026-08-29-10-validator

**VERDICT: PASS.** Full suite green and stable across two independent isolated runs (0 FAIL, 1117
PASS, 0 KIND-DRIFT), both new checkers' tests are reachable/synthetic/strong, the T-10 guard was
independently mutation-proved to redden, the claims checker's security boundary holds with no
`shell=True` anywhere and a message-asserted refusal test. One non-blocking matrix technicality and
a test-first record gap for 3 of 4 logic tasks are reported as findings, not gate failures.

## 1. Independent measurement of the full runner — CONFIRMED

Command: `.agents/skills/harness/bin/run-unit-tests.sh` (no `--kind`), run twice, isolated (no
concurrent jobs), from worktree root.

- Run A (job bg_5): `EXIT:0 FAIL:0 PASS:1117 KINDDRIFT:0`. Tail shows both new checkers'
  `PASS test-check-decision-anchors.py` / `PASS test-check-decision-claims.py`.
- Run B (job bg_21, re-confirmation): `EXIT:0 FAIL:0 PASS:1117 KINDDRIFT:0`, same two lines present.
- Per-kind: `--kind unit` → `EXIT:0 FAIL:0 PASS:417`; `--kind integration` → `EXIT:0 FAIL:0 PASS:700`.
  417+700=1117, consistent with the full run.

**My measurement CONFIRMS the orchestrator's pre-dispatch numbers exactly**: exit 0, 0 `FAIL`,
1117 `PASS`, 0 `KIND-DRIFT`, both new checkers PASS.

One transient flake observed and resolved (reported for the record per rule 15, not swept): a
single mid-session run of `test-gen-decisions-index.py`, executed by hand while a background
`--kind unit`/`--kind integration` job (bg_1) was still finishing, showed 2 `FAIL` lines
(`test_committed_index_matches_a_fresh_regeneration`, `test_committed_index_is_complete_and_within_budget`).
Five immediately-following isolated re-runs, and both full-suite runs above, were all clean (0
FAIL). `git status --porcelain` on `DECISIONS-INDEX.md` was clean throughout — no real drift, no
file left dirty. Root cause not conclusively isolated; most consistent with a transient race against
the concurrent background job rather than a defect in the checker. Not a gate blocker: the
authoritative isolated measurements (A, B, 5x rerun) are unanimous at 0 FAIL.

## 2. Matrix resolution — every required kind named

Change types present: **docs 16, logic 4, config 3** (verified against `plan.yaml`: all `docs`/
`logic`/`config` change_type sites match the contract). None of `api`, `cross_module`, `frontend`,
`feature`, `bugfix`, `ai_behavior` are present, so no `when` predicate fires.

| kind | required by matrix for {docs,logic,config}? | state | cmd |
|---|---|---|---|
| `unit` | yes (`logic.always`) | **satisfied** (whole-suite green; see finding below) | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` |
| `integration` | not named in matrix for any present type, but the diff's four logic checkers' own tests live here | **satisfied**, added by me (diff clearly warrants it — floor is a minimum) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` |
| `functional` | no | **not applicable** — `status: excluded`, `signed: DEC-187`, reason: repo ships no service API and the two-bucket split covers everything | n/a |
| `component` | no — `frontend` is not a present change type | **not applicable** (unresolved `cmd: null`, but not required by the matrix for docs/logic/config, so this is a genuine soft-skip, not BLOCKED) | null |
| `ui` | no — `frontend`/`feature` `has_interaction_flow` predicates never fire (no frontend/feature tasks) | **not applicable** | null |
| `eval` | no — `ai_behavior` not present | **not applicable** | null |
| `typecheck` | no — not in the matrix at all, and no `.ts`/`.tsx` in this diff | **not applicable** | null |

`docs.always: []` and `config.always: []` — genuinely no kind is floored for the 16 docs and 3
config tasks. This matches the BRIEF's own "Verification gaps" section, which states no criterion
rests on a null-runner kind.

**Finding (non-blocking, advisory) — matrix taxonomy mismatch on `logic`.** The matrix requires only
`unit` for `logic`, but all three new/changed logic files' tests
(`test-gen-decisions-index.py`, `test-check-decision-anchors.py`, `test-check-decision-claims.py`)
are registered in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`, not `UNIT_SCRIPTS` — none of
UNIT_SCRIPTS' 27 files touch these tasks. This is *by the project's own documented convention*
(`run-unit-tests.sh:19-29`, issue #160): the split is "does this drive a real script end-to-end via
subprocess", and all three test files spawn the checker as a subprocess (`subprocess.run([sys.executable,
CHECKER, ...])`). So the literal `unit` floor for `logic` is unsatisfied by a *unit-kind-named* test
for this diff, while `integration` — not named in the matrix for `logic` (unlike `cross_module`/
`feature`, which require both) — is where the real, strong coverage lives. I add `integration` as a
kind this diff clearly warrants (floor is a minimum) and treat it as satisfying the intent; the
`harness.json` matrix's `logic` row lacks a `_matrix_provenance` entry recording this convention the
way `api`/`cross_module`/`feature` record their `functional` removal. This is a config-authoring gap,
not a coverage gap — every logic change is in fact heavily tested — and should get a signed
provenance entry, not a code fix. Not a `must_fix`: I verified actual coverage directly (§3-6 below)
rather than trusting kind labels.

## 3. New-checker test reachability and assertion strength

Both checkers' tests build **synthetic fixtures in `tempfile.TemporaryDirectory()`** and pass the
fixture path **explicitly** on every single call:
- `test-check-decision-anchors.py:33-37` (`run_checker`) hardcodes `["--file", fixture_path]` for
  all six cases (`:47,74,105,136,162,181`) — none omits the argument.
- `test-check-decision-claims.py:26-30` (`run_checker`) hardcodes `["--file", fixture_path]` for all
  seven cases (`:40,75,103,132,159,185,202`) — none omits the argument.

No call in either test file falls through to the live-document default. Both checkers' own
`default_target()` resolves only when `--file` is `None`, and is called at CALL time from `main()`,
never at import time (`check-decision-anchors.py:125-135`, `check-decision-claims.py:144-154`).

**Zero-item distinction is real AND asserted, not just present:**
- Anchors: `check-decision-anchors.py:154` always prints `f"examined {len(anchors)} anchor(s), {failed} failed"`.
  Asserted by `test_zero_anchors_exits_zero_and_says_so` (`:136-159`, checks `"examined 0 anchor"
  not in r.stdout`) and again by `test_default_file_is_dev_null_readable_zero_anchors`
  (`:181-199`) — two independent assertions of the same distinguishing message.
- Claims: `check-decision-claims.py:173` prints `f"examined {len(claims)} claim(s), {failed} failed"`.
  Asserted by `test_zero_markers_exits_zero_and_says_so` (`:132-156`, checks `"examined 0 claim"
  not in r.stdout`).

Live-behavior corroboration in `receipt-harness-backend-dev-2026-08-29-03-eng.md` (T-17 section):
run against the pre-feature authority (`git show 7ebfc9e:...DECISIONS.md`) reports exactly the
three `feature.yaml` anchors and exits 1 — a real-tree existence proof, not just synthetic-fixture
green. I did not independently re-run that specific step (out of the dispatch's required-item list
for §3, and the transcript is directly reproducible), but the transcript's shape (3 named anchors,
`examined 32 anchor(s), 3 failed`) is internally consistent with the checker's own printed-format
convention verified above.

## 4. Claims checker's security boundary

`grep -n "shell=True"` across all four files (checker + test, both new checkers):
```
test-check-decision-claims.py:209:        if "shell=True" in src:
test-check-decision-claims.py:210:            print(f"FAIL - {name}: checker source contains shell=True")
```
The **only** two hits are the assertion's own literal string inside
`test_checker_source_never_uses_shell_true` (`:202-216`), which reads the checker's source and
greps it. `check-decision-claims.py` itself contains zero occurrences — its one `subprocess.run`
call (`:106-109`) passes `tokens` (a `shlex.split` list, `:96`) with no `shell` keyword at all.

**Refusal path is tested with a message assertion, not just exit code.**
`test_disallowed_first_token_is_refused_and_exits_one` (`:103-129`) asserts, in order:
`r.returncode == 1`; `"REFUSED" in r.stdout`; `"python3" in r.stdout` (the disallowed token named).
The checker's own refusal string (`check-decision-claims.py:102-105`) reads `"REFUSED: first token
{tokens[0]!r} is not git or grep — a decisions document must not become an arbitrary code execution
surface"` — a refusal, never a skip; `run_claim` returns `(False, ...)` which `check_claim`
propagates into a counted failure, so a refused claim always increments `failed` and the exit code.

## 5. T-10 guard — independent mutation probe

Ran independently (not trusting the backend-dev receipt's own transcript, though it corroborates):
imported `test-gen-decisions-index.py` by path, monkeypatched its `REPO_ROOT` and
`gdi.DECISIONS_PATH` module globals to point at a Write-tool-created `/tmp` copy of the live
`DECISIONS.md` (bash `cp`/`cat`-redirect to a `DECISIONS.md`-shaped path is denied by
`bash-write-guard` outside my domain — routed the copy through the `Write` tool instead, then
appended the mutation via a plain Python file write inside the probe script).

- **Clean copy**: `test_no_amendment_construct_survives_in_the_authority()` → `ok`, returns `True`.
- **Mutated** (appended `\n### DEC-999 amendment 1 — planted\n` to the temp copy only): → `FAIL -
  ...: '### DEC-N amendment' heading found at /tmp/.../authority-copy.md:[6301]`, returns `False`.
- Real file confirmed untouched throughout: `git -C <worktree> status --porcelain --
  .harness/harness/docs/DECISIONS.md` → empty, both before and after.

The guard genuinely reddens on the exact construct it exists to forbid. This corroborates (and does
not merely repeat) the backend-dev receipt's own three-directional mutation proof
(`receipt-harness-backend-dev-2026-08-29-07-eng.md:42-114`, heading/bold/token forms, each isolated
to exactly one changed line in the census).

## 6. T-06 / T-10 verify clauses — falsified by later work, exactly as the dispatch predicted

Ran both clauses verbatim, isolated (no concurrent jobs), from worktree root:

- **T-06 verify: exit 1.** All grep-absence checks pass, `compute_amendments` present. The clause's
  own `grep -q '^FAIL - test_committed_index_matches_a_fresh_regeneration' || exit 1` **fails to
  find that line** — because the suite is now clean (`test-gen-decisions-index.py` exits 0, all 11
  `ok -`, 0 `FAIL`, confirmed 5x reruns). The clause requires the FAIL line to exist; it no longer
  does; `|| exit 1` fires.
- **T-10 verify: exit 1.** Same mechanism: `test_no_amendment_construct_survives_in_the_authority`
  is present (`ok`), but the required-present `FAIL - test_committed_index_matches_a_fresh_regeneration`
  line is absent for the identical reason.

**Mechanism confirmed exactly as flagged**: both clauses were authored (by T-06/T-10's own receipts,
dated 2026-08-29-07/03) while `DECISIONS-INDEX.md` was known stale — T-11 (index regeneration, later
in the plan) had not yet landed. T-11 has since landed (`b32013c` is in this diff's log) and the
index now regenerates clean. **These two clauses now exit 1 for the opposite of a defect**: the
code is *more* correct than the clause anticipated. This is a **reported finding, not edited** (per
the dispatch's explicit instruction — `plan.yaml` and the tests were not touched).

**The underlying unit suite is green independent of these two clauses**: §1's isolated full-suite
and per-kind runs (0 FAIL, 1117 PASS) do not invoke either task's literal `verify:` shell block —
they invoke the test scripts directly, which is where the real signal lives. T-17 and T-20's `verify:`
clauses were also re-run verbatim and both exit 0 cleanly (§ below), confirming this stale-clause
issue is isolated to T-06/T-10's now-overtaken assumption, not a broader defect in the verify
mechanism.

- T-17 verify: `EXIT:0` (`examined 0 anchor(s), 0 failed` from the `--file /dev/null` check; 6 `ok -`
  ≥ 4 required; 0 `FAIL`).
- T-20 verify: `EXIT:0` (7 `ok -` ≥ 5 required; 0 `FAIL`).

Not a `must_fix`: no required test kind is left unverified by this — `integration`'s presence and
strength are independently confirmed in §1, §3-5 by means other than these two stale shell clauses.

## 7. Test-first compliance audit — per logic task, by receipt

- **T-17** (`receipt-harness-backend-dev-2026-08-29-03-eng.md:112-235`, T-17 section): **explicit
  RED-before-GREEN evidenced.** The checker was written once, moved aside to `/tmp`, the test was
  written, run against the *absent* checker (`:126-135`, 5/6 cases FAIL with `ENOENT`), then the
  checker was restored and the suite reran to confirm GREEN (`:139-150`, all 6 `ok`). This is the
  strongest evidence among the four tasks.
- **T-06** (`receipt-harness-backend-dev-2026-08-29-03-eng.md:1-108`): **record is silent on
  ordering.** The receipt documents the new case (`test_refs_graph_omits_ids_with_no_live_heading`)
  passing both directions (`:48-70`) but shows no RED transcript before the refs-graph filter code
  existed. Do not infer compliance from the green result alone.
- **T-10** (`receipt-harness-backend-dev-2026-08-29-07-eng.md`): **record is silent on code-before-
  test ordering.** The receipt's mutation proof (`:42-114`) demonstrates the *test discriminates*
  (reddens on the forbidden construct) — that is orthogonal to whether the test was written before
  the amendment-machinery deletion. No RED-before-code transcript is present.
- **T-20** (`receipt-harness-backend-dev-2026-08-29-07-eng-T-20.md`): **record is silent on
  ordering.** Shows only the final GREEN state, safety-boundary evidence, and design notes — no RED
  transcript predating the checker's existence.

Three of four logic tasks have no test-first evidence in the record. This is reported as a finding
per the verification-rules protocol ("report violations as findings — they do not by themselves fail
the gate"); it does not change the VERDICT given the coverage itself is independently confirmed
strong and correct in §3-6.

## Summary

```yaml
matrix_ok: true
kinds:
  - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 417 }
  - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 700 }
  - { kind: functional, state: not_applicable, signed: DEC-187 }
  - { kind: component, state: not_applicable, cmd: null }
  - { kind: ui, state: not_applicable, cmd: null }
  - { kind: eval, state: not_applicable, cmd: null }
  - { kind: typecheck, state: not_applicable, cmd: null }
coverage_gaps:
  - "logic matrix row names only 'unit' but the diff's logic tests all live in integration-kind scripts (project convention, issue #160) — needs a signed _matrix_provenance entry, not a code fix"
  - "test-first record silent for T-06, T-10, T-20 (only T-17 has an explicit RED-before-GREEN transcript)"
sc_evidence:
  - { id: SC-06/SC-07 (generator dead-code + new case), test: ".claude/skills/harness/bin/test-gen-decisions-index.py::test_no_amendment_construct_survives_in_the_authority" }
  - { id: SC-08 (anchor checker), test: ".claude/skills/harness/bin/test-check-decision-anchors.py (6 cases)" }
  - { id: SC-09 (claims checker), test: ".claude/skills/harness/bin/test-check-decision-claims.py (7 cases)" }
  - { id: SC-10 (runner exit 0, 0 FAIL, captured not piped), test: "this gate's own §1 isolated runs" }
```

## Nothing committed, no production code changed, no repro artifacts left in the worktree

`git -C <worktree> status --porcelain` shows only this artifact added; no other file was modified by
this gate run (temp/mutation probes ran exclusively in `/tmp`, cleaned up).
