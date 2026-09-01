# QA — BUG-1071 era guard, mutation verification

**Verdict input: PASS with two findings for the panel (Q1 medium, Q2 high-severity-but-defensible-given-scope).**
All four new assertions are measured, not read, to discriminate. No coverage hole found across 7 mutants.

## 1. Baseline — measured, matches author's claim exactly

| Command | Claimed | Measured |
|---|---|---|
| `test-check-state.py` | 151 ok / 0 FAIL / exit 0 | **151 ok / 0 FAIL / exit 0** |
| `check-state.sh` (real tree) | exit 0 / 0 violations / 32 INV-32 notes (31 pre-era + 1 undated) | **exit 0 / 0 violations / 32 notes (31 pre-era + 1 undated, FEAT-40-harness-writes-done)** |

No discrepancy. The 32-note discovery is non-vacuous: real plan data drove every note.

## 2. Mutation table (measured via `_inv32_run` against hand-built mutant scripts, never read-only)

| Mutant | pre_era_is_exempt | era_boundary_is_exact | undated_approval_warns | load_bearing |
|---|---|---|---|---|
| M1 pre-panel branch made unconditional (exempts everything) | green | **RED** | green | n/a |
| M2 `INV32_ERA_START="2026-08-30"` | **RED** | **RED** | green | n/a |
| M3 `INV32_ERA_START="2026-09-01"` | green | **RED** | green | n/a |
| M4 undated/malformed branch deleted | green | green | **RED** | n/a |
| M5 warn text no longer says `approval.date` | green | green | **RED** | n/a |
| M6 era logic moved live above `ERA BEGIN`, marked span reduced to a comment | — | — | — | **RED** (real=0, mutant=0 — the excision removes nothing, so the case correctly refuses to call itself load-bearing) |
| M7 `# INV-32 ERA BEGIN (BUG-1071)` renamed | — | — | — | **RED**, via the explicit `"FAIL - INV-32 era guard markers absent; cannot mutate"` branch (confirmed firing, not erroring) |

Every mutant reddens at least one of the four assertions. **No coverage hole.** M1 specifically confirms the
author's own claim: `case_inv32_era_boundary_is_exact`'s `ok = not violations(before) and bool(violations(after))`
does go RED when the whole guard is made an unconditional exemption, exactly as the lead's reading predicted.

M6 is the marker-drift probe the dispatch asked for: moving the functioning era logic to live *above*
`ERA BEGIN` (leaving only an inert comment inside the delimited span) does **not** let the load-bearing case
silently pass — it goes red, because excising the (now-empty) marked span changes nothing, so
`real==mutant==0 violations` fails the case's own `bool(violations(mutant))` assertion. **The markers cannot
drift without the suite noticing** — this is a positive property, not a hole, and the earlier framing ("can
markers drift from the code they claim to delimit") is answered NO for this repository's current suite.

The load-bearing case's own baseline (real markers, unmutated) was independently confirmed from the initial
151-ok run: `real=0 mutant=1 violations`, no Traceback — it measures the guard, not a crash.

## 3. Exit-code assertion — CONFIRMED, not refuted

Added a temporary exit-code check to the bare pre-era fixture (`panel_marker=False, date="2026-08-30"`,
nothing else) and ran it standalone:

```
exit code: 1
VIOLATION  .harness/harness.json missing — not onboarded (or half-onboarded). Run /harness-init.
VIOLATION  No .claude/settings.json — the spawn-depth and Expertise-injection prerequisites are unset...
VIOLATION  INV-29: cross-repository enumeration failed ... fleet.yaml ... No such file or directory
VIOLATION  INV-31: core.hooksPath is unset, not .claude/skills/harness/hooks ...
note       INV-32: FEAT-INV32 was signed 2026-08-30, before the adversarial panel shipped ...
```

**CONFIRM.** An exit-code assertion on this fixture binds four unrelated invariants (harness.json presence,
settings.json presence, INV-29 fleet enumeration, INV-31 hooks config) and none of them are the era guard.
The author's design choice to assert on the VIOLATION line rather than the exit code is correct and load-bearing.

## 4. Question 5 — post-era + panel, and malformed-non-empty date

- **Post-era + full valid `panel:` block**: `_inv32_plan()`'s own default (`date="2026-08-31"`) is what every
  pre-existing `case_inv32()` sub-check (open finding, resolved, rulings, readers, mutation) already runs
  against. **This is already bound** — not a coverage gap. Ran it standalone too: 0 violations, 0 notes,
  clean fall-through to panel grading, as expected.
- **Malformed but non-empty date `"2026-8-31"`** (fails `\d{4}-\d{2}-\d{2}` fullmatch): observed behaviour —
  same "missing or malformed" warn branch as `date=None`, same message shape, 0 violations. This is the SAME
  code branch as the undated case (one `if not re.fullmatch(...)` guards both empty and malformed strings),
  so it is not a functionally distinct path — but no existing case exercises a non-empty malformed value
  independently of the `date=None` case. **Minor coverage gap** (info severity): the regex's malformed-but-
  present branch is exercised only by inference from the empty-string case, not directly. Not added
  permanently — it does not close a real hole since the branch condition is provably the same one line for
  both inputs (confirmed by reading `check-state.sh:201`, not merely asserted).

## 5. The five questions

**Q1 (hardcoded date) — MEDIUM, concrete scenario.** `INV32_ERA_START = "2026-08-31"` is this repository's
own bootstrap date, hardcoded into code the dispatch says ships to arbitrary onboarded repositories. Concrete
failure: a *different* repository that installs this harness version and onboards later, but is itself a
long-lived fork carrying plans signed before **its own** INV-32 arrived (which could be any date, since that
depends on when this file reaches that repo, not on 2026-08-31), gets graded against a boundary that has zero
relationship to its own panel-availability history. A plan in that repo signed 2026-11-01 — genuinely before
its panel shipped there — would be WRONGLY graded (false VIOLATION) because 2026-11-01 > 2026-08-31. The
right key is something the repository can verify locally: the commit that introduced INV-32 in *that* repo's
own history, or a value written to `.harness/harness.json` at onboarding/upgrade time. This is a real, if
narrow, portability defect — it does not affect this repository's own remaining plans (all future signings
here postdate 2026-08-31 and are correctly graded), but it will misfire the day this script is vendored
into a second repository with its own timeline.

**Q2 (undated fail-open) — the highest-severity finding, and it is LIVE.** Grepped the full script and
`harness_yaml.py`'s schema (`REQUIRED_TASK_FIELDS`, no `approval` field validation at all) for any other
place `approval.date` is required on an approved plan: **none exists.** No second guard forces the field.
An author who omits `approval.date` from an approved plan's `approval:` block is **never graded by the
panel, permanently, silently** (a `note`, never a `VIOLATION`) — that is a full, trivial, standing bypass of
INV-32 with no upstream cost: nothing else in `load_plan` or `check-state.sh` requires the date to exist
before a plan can be marked `approved`. FEAT-40-harness-writes-done is cited by the fix's own comment as a
live instance of exactly this gap. **This should be escalated**: the warn-and-skip design correctly avoids
blaming the panel for an unrelated defect, but the absence of *any* companion check that an approved plan's
`approval.date` field exists at all (as a VIOLATION, separate from the era question) leaves the door open
indefinitely.

**Q3 — the four assertions bind what they name.** Confirmed by mutation, table above. Every named behaviour
(exempt-when-pre-era, exempt-in-both-directions-at-the-boundary, undated-warns-naming-the-field,
guard-is-load-bearing-including-a-markers-absent branch) reddens under its corresponding defect and no other
assertion silently compensates.

**Q4 (`INV32_ERA_START` inside the loop) — INFO, not a defect.** It is a literal string reassigned
identically on every iteration of `for feat, doc in plan_docs.items()`; it never varies with `feat`/`doc`, so
there is no correctness impact — only a style nit (module-level constant would read cleaner and avoid the
redundant reassignment). No concrete failure scenario exists for it.

**Q5 (coverage gap: post-era + panel block, behaviour change untested?) — none found.** See §4: this
combination is exactly the pre-existing `case_inv32()` fixture default and is already exercised by every one
of its sub-checks.

## Test-matrix gate

Change is `logic`/gate-script + its own test file — the diff's own two files ARE the unit-test surface (the
matrix's `unit` kind is satisfied by `test-check-state.py`, which is part of the diff, run above with 151/151
green). No `ai_behavior`, `ui`, `integration`-with-external-service, or `e2e` surface is touched. `matrix_ok:
true`.

## Tree state

Left byte-identical to `bf12a96b` — `git diff bf12a96b -- check-state.sh test-check-state.py` is empty,
`md5sum check-state.sh` unchanged across the session. All mutants were written to and deleted from
`.claude/skills/harness/bin/.mutant-*.sh` (untracked, git-ignored scratch names), never edited in place. No
new test cases were added permanently (§4's gap was judged not worth a fifth case, since the branch it would
cover is provably the same source line as an already-tested one).
