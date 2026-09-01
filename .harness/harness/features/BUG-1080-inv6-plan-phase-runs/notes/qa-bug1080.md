# QA — BUG-1080 INV-6 plan-phase runs — test-matrix gate + mutation re-derivation

Worktree confirmed: `.claude/worktrees/harness/BUG-1080-inv6-plan-phase-runs` (test-check-state.py
measured 3526 lines — matches the worktree spec, not the 3396-line stale main-checkout copy). All
commands below ran from that worktree root.

## 1–3. Suite + live run results (measured)

| command | result |
|---|---|
| `python3 .../test-check-state.py` | **161 ok / 0 FAIL**, exit **0** — matches author's claim exactly |
| `python3 .../test-validate-feature-json.py` | **61 PASS / 0 FAIL**, "ALL PASS", exit **0** |
| `bash .../check-state.sh` (live, worktree root) | exit **0**, **0 VIOLATION** lines (only `note`-level advisories, none referencing INV-6/BUG-1080) |

## 4. Mutation table — MY OWN mutants, run against a mirrored `/tmp` copy of the bin/ dir via
`CHECK_STATE_BIN` (the suite's own documented escape hatch). Six cases: `plan_run_is_exempt` (A),
`code_run_still_fires` (B), `unknown_grade_fails_closed` (C), `mixed_runs_still_fire` (D),
`exempt_survives_signature` (E), `pinned_plan_run_silent` (F).

| mutant | change | cases that FAIL (caught) |
|---|---|---|
| M1 | `code_grade` default `""` → `"n_a"` (fail-open) | **B, D — 2 cases, not 4** |
| M2 | drop `_squad == "validator"` conjunct | **none — 0 cases** |
| M3 | `!= "n_a"` → `not in ("n_a", "")` | B, D — 2 cases |
| M4 | exempt on key ABSENCE (`"code_grade" not in entry`) | A, B, E — 3 cases |
| M5 | revert exemption: `code_reviewing_runs` → `runs` | A, E — 2 cases |
| M6 | invert sha test: `_sha == ""` → `_sha != ""` | **F only — 1 case**, exactly as claimed |
| M7 (mine, targeting C) | exempt on ANY non-empty `code_grade` value (`== ""` instead of `!= "n_a"`) | **C only — 1 case** |

Raw tool output for each mutant, and the diff proving each mutant is a single clean hunk against
the real `check-state.sh`, is reproducible from `/tmp/run_inv6_cases.py` + `/tmp/mutbin_m{1..7}`
(ephemeral, built and run entirely outside the repo per the READ-ONLY constraint; worktree verified
`git status --porcelain` clean of any source change before and after).

**Finding 1 — the author's M1 count is wrong.** The dispatch says "author claims 4 cases catch
[the `""` → `n_a` fail-open mutant]." Measured: **2 cases** (`code_run_still_fires`,
`mixed_runs_still_fire`), not 4. Refuted, not confirmed.

**Finding 2 — M2 (dropping `_squad == "validator"`) is caught by ZERO of the six cases.** Not a
vacuous-assertion problem (see below) — it is a genuine untested axis. All six fixtures use
`squad: validator` for every run; none exercises a non-validator squad carrying (or missing)
`code_grade`. A rewrite that silently widened the exemption to every squad — e.g. an `eng` or
`product` run with no `code_grade` key becoming newly required-to-pin, or a `product` run bearing
`code_grade: n_a` becoming wrongly exempt — would ship undetected. Recorded as a `coverage_gap`.

**No case is vacuous.** Every one of the six is caught by at least one mutant: A/E by M4+M5, B/D by
M1+M3(+M4 for B), C by my own M7, F by M6. `unknown_grade_fails_closed` (C) looked suspicious
mid-probe (uncaught by M1–M6) but M7 — a mutant targeting its own specific axis (presence-of-any-value
treated as exemption) — reddens it and nothing else. Confirms P-09/O-05: absence of a hit from a
convenient mutant set is not evidence of vacuity; the assertion's own intended mutant must be tried.

## 5. Reachability of the six cases in the gate

`ok_i6_plan = all([case1(), ..., case6()])` (test-check-state.py:3500-3507) is a **list literal**,
so all six functions are called unconditionally before `all()` runs — no short-circuit skips a case.
`ok_i6_plan` sits in `main()`'s final `and`-chain (line 3519) gating `sys.exit(0)` vs `sys.exit(1)`.
**Confirmed: a single case silently failing flips the suite's exit code from 0 to 1.** No dead
weight in the six.

## 6. Schema/runtime agreement — feature-schema.json vs check-state.sh (DISAGREE, one direction)

`feature-schema.json:61` declares `"code_grade": {"enum": ["n_a"]}` — closed, **exact-string**
match (JSON Schema `enum` is not case- or whitespace-normalized). `check-state.sh:445` tests
`str(entry.get("code_grade","")).strip().lower() != "n_a"` — case- and whitespace-insensitive.

Measured directly: built a real JSON `feature.json` (not the test suite's YAML-in-`.json`
convenience fixture) with `code_grade: "N_A"` and ran both gates against it:
- `validate-feature-json.py <file>` → **rejects**: `/runs/0/code_grade: 'N_A' is not one of ['n_a']`
- `check-state.sh` over the same value (via `_inv6_feature`, which uses check-state.sh's own
  YAML-tolerant loader) → **exempts silently** (`_PIN_MSG` absent from output)

So a document can be **schema-INVALID and gate-EXEMPT** at once for any case/whitespace variant of
`n_a` (`"N_A"`, `" n_a "`, `"N_A "`, ...). The reverse direction does not occur: the only
schema-VALID value (`"n_a"` exactly) is always exempted by check-state.sh's test too, since exact
match implies the lenient match. **No test in the diff or in `test-validate-feature-json.py`
exercises this divergence** — that file has zero `code_grade` cases at all (`grep` empty). Recorded
as a `coverage_gap`.

## 7. Reachability of the exemption itself — is `code_grade` ever WRITTEN?

Searched the full worktree (`bin/`, `.claude/skills/harness/SKILL.md`, `DECISIONS.md`) for any
producer of `runs[].code_grade`:
- `feature-json-merge.py append-run` takes an arbitrary JSON object — schema-permitting, but **no
  caller anywhere in the repo passes `code_grade`** (grepped every `append-run` invocation; the only
  one outside the test file uses `squad: backend`, no `code_grade`).
- DEC-207 and the code-review skill's `code_grade` are a **different concept** — the reviewer
  DIGEST's own field (`pass`/`fail`/`grade_2`/`n_a`), validated by `validate-digest.py` against the
  DIGEST document, never transcribed anywhere into `feature.json`.
- The orchestrator playbook (`SKILL.md`) documents the plan-panel's record step (lines 108–112) as
  writing the validator lead's digest into **`plan.yaml`'s `panel` key** — not `feature.json`'s
  `runs[]`. The separate, generic "Adjust and record" step (lines 61–64) says to "update
  `feature.json`'s ... runs list" but **never mentions `code_grade` or instructs propagating it from
  the digest**.

**Finding 3 (severity: high) — the exemption is schema-legal and thoroughly unit-tested, but has
no documented or scripted producer.** Nothing in this diff, and nothing pre-existing, tells the
orchestrator (or any script) to write `code_grade: n_a` onto the run entry it records for a
plan-phase panel review. Absent that instruction, the next plan-panel run recorded following the
current `SKILL.md` text will most likely be a bare `{id, squad: validator, verdict}` entry — which
the fix's own fail-closed default (line 445) then treats as a **code-reviewing** run requiring a
pin, reproducing FEAT-46's exact failure. This is not hypothetical: it is the literal incident the
bug fix exists to resolve, and the diff fixes the *reader* half of the contract without touching the
*writer* half. I cannot rule out that a capable orchestrator LLM infers the field from DEC-207's
prose on its own — but nothing in the reviewed diff, the playbook, or the schema enforces or
prompts it, so the fix's real-world effect is unverified and plausibly inert.

## Test-first audit (re-derived against `git show 9f2a0702` copy in a mirrored tmp tree)

Ran the CURRENT six cases against the PRE-FIX `check-state.sh` (`any(sq == "validator" ...)`, no
`code_grade` concept at all):

```
FAIL - INV-6 exempts a plan-phase run (code_grade: n_a)
ok   - INV-6 still fires on a code run with no pin
ok   - INV-6 fails closed on an unknown code_grade
ok   - INV-6 fires when a code run sits beside an exempt plan run
FAIL - INV-6 exemption survives signature (not keyed on approval.status)
ok   - INV-6 silent on a pinned feature with both run kinds
```

**Exactly 2 FAIL** (`plan_run_is_exempt`, `exempt_survives_signature`) — matches the author's claim
precisely. The other four were green before AND after — but they are **not filler**: each is
independently caught by a mutant above (B/D by M1/M3, C by M7, F by M6), so each is a real
regression guard for the fix's fail-closed behavior, not a vacuous carry-over.

## Test-matrix gate

Change type: **bugfix** at minimum (BUG-1080, a defect fix to `check-state.sh`); the diff also
couples a shell predicate to a JSON Schema property (`feature-schema.json`) and its own test file,
which is exactly the shape `cross_module` names — floor is `unit` either way, `unit`+`integration`
under the broader reading. No `plan.yaml`/`BRIEF.md` exists for this feature (main-session-direct,
per DEC-174, confirmed by the dispatch's own constraints), so no `verify:` blocks or SC ids to cite.

| kind | required? | producer script | result |
|---|---|---|---|
| unit | yes (bugfix floor) | `test-validate-feature-json.py` (in `UNIT_SCRIPTS`) | **satisfied**, 61/61, but **does not exercise the diff's schema change** (zero `code_grade` cases) — coverage gap, not a missing kind |
| integration | yes (cross_module reading; `test-check-state.py` is in `INTEGRATION_SCRIPTS`, not `UNIT_SCRIPTS`, despite unit's broad `detect` glob also matching it) | `test-check-state.py` | **satisfied**, 161/161, the six `case_inv6_*` cases directly and non-vacuously exercise the fix |

`matrix_ok: true` — both required kinds are present, named to real scripts that actually run them
(verified against `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays, not just the
`detect` glob), and green.

## Verdict for this lens

The test-matrix/mutation task itself PASSES: the suite is green, the six new cases discriminate
(none vacuous), and the reachability/exit-code wiring is sound. Three findings need the lead's
attention and are not mine to close: (1) the author's stated M1 mutant-catch count is wrong (2, not
4); (2) the `_squad == "validator"` conjunct is entirely untested and the schema/runtime `n_a`
matching disagrees for case/whitespace variants; (3) — the one that matters most — nothing in this
diff or the existing playbook writes `code_grade: n_a` anywhere, so the fix may not change FEAT-46's
outcome in practice.
