# D-16 is reachable — D-17 + T-09 added, SC-12 grades it (fix cycle 3)

**BLUF.** The one defect is closed by addition, not edit. `D-17` supersedes, by name and by verbatim
quotation, the two clauses that contradicted each other, and `T-09` carries the `--dir` branch.
`plan-merge.py apply` printed `ADDED D-17`, `ADDED T-09`, `APPLIED`, exit 0. `check-plan-routes.py`
reports **0 violations**, exit 0. `T-09`'s `verify:` run verbatim from the main checkout **exits 1**
today — the three greps are the whole discriminator, proven separately.

## The chain a reader now follows, by id

`D-16` (`plan.yaml:143`) → `D-17` (`plan.yaml:148`) → `T-09` (`plan.yaml:851`) → `BRIEF.md` `SC-12`
(`BRIEF.md:178`).

`D-17` quotes both superseded clauses verbatim, so a reader arriving at either finds it from the
`decisions:` block alone:

- `D-16`'s `and T-07 is the task that implements it` — no longer governs; **T-09 owns the `--dir`
  branch**.
- `T-07`'s `intent:` sentence `discard is deliberately NOT covered - it removes a quarantine
  directory and can make nothing canonical - and list is read-only. Say so in a comment, because the
  omission must read as a choice.` — no longer governs. `T-09` step zero **corrects that comment** if
  `T-07` wrote it, because a shipped comment asserting a non-omission is the same defect one layer
  down.

Pattern followed: `D-15`, which already supersedes two bullets of `T-06`'s immutable `intent:` by
name. No second mechanism invented. Addition was the only route: `apply` is add-only and exits 7 on
any change to `D-16`'s or `T-07`'s existing text.

## The tension D-16 left open, resolved explicitly

`D-16`'s immutable `because` says "REQ-05 is untouched since discard makes nothing canonical". That
is true of **REQ-05's first sentence only**. `D-17` states the footing plainly: the `--dir` branch
stands on **REQ-05's second sentence** — adoption *and discard* are both explicit acts of a resumed
parent, neither a default nor a timeout — read together with **REQ-04**, whose remedy is that an
orphan's canonical write is quarantined rather than lost, and with **issue #280**'s boundary that a
completed child's analysis stays *recoverable*. An orphan running `discard` destroys exactly that.
`T-09` therefore `traces: [REQ-04, REQ-05]`. No requirement was added or reworded.

## T-09, in one paragraph

Extends `quarantines()` — the function `T-07` creates — with a `discard` verb beside `ADOPT_TOOL`:
match on the value of **`--dir`** (not `--file`; `discard` takes `--dir`), normalise from the **last**
`.harness/` segment, match `^\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/?$` (D-16's own regex,
a *directory* pattern, optional trailing slash), feature from group 1, refuse only when
**T-02's `orphan_write`** is True — one predicate, not a second — and fail **open** on an absent or
unresolvable value, D-13's posture restated. D-04's OMP carve-out holds with **no extra code**:
`orphan_write` itself returns False when the feature's only live claims carry `runtime: omp`, and the
intent forbids a second runtime test. Return shape stays `T-07`'s `(rel, feature, quarantine_rel)`
with a `None` third element meaning *no path to advise*; the refusal says discarding is the resumed
parent's act and this caller is not it, and never names a quarantine path. `depends_on: [T-07]`,
`main-session-direct` with `T-07`'s DEC-174 enforcement-layer reason, `change_type: cross_module`,
`status: ready`, same three files as `T-07`.

## Discrimination, measured — not assumed

`T-09`'s `verify:` (a literal `|` block; 0 folded `>` blocks anywhere in the plan) run **verbatim from
the main checkout before the task was written**:

| measurement | result |
|---|---|
| whole block, verbatim | **exit 1**, no output (first grep fails) |
| each of the three greps, individually | **exit 1** each |
| tail conjunct alone, `python3 .agents/skills/harness/bin/test-plan-sign-gate.py` | **exit 0**, 45 `ok`, 0 `FAIL` |
| literal `discard` in `test-plan-sign-gate.py` / `plan-sign-gate.py` | **0 / 0** occurrences |

So the greps are the whole discriminator and no earlier conjunct masks them. The first grep string is
the one `D-16` pins verbatim: `an orphan quarantine.py discard of a quarantine directory is refused`.
Two of the three greps are **negative controls** (own-claim allow; a `--dir` outside a quarantine
segment allowed). Seven labels total, including the omp case, the no-live-claim case, a shell-variable
`--dir`, and `quarantine.py list` never denied.

## BRIEF.md — SC-12 added (nothing else touched)

I read the whole `## Success Criteria` section. **`discard` was graded nowhere.** `SC-11` grades
`apply`, `set-task-station` and `adopt`; `SC-06` grades `quarantine.py discard` as a CLI behaviour, not
the gate refusing an orphan's discard. Left ungraded, the same failure repeats one level up. `SC-12`
(`verify: automated`, `evidence: integration`) grades the branch and names its red-making mutation the
way `SC-11` does: delete the `--dir` branch from `quarantines()`, or point the suite by
`PLAN_SIGN_GATE_BIN` at a copy of the gate **as `T-07` left it** — the pre-`T-07` copy would redden
`T-07`'s own cases and prove nothing about this branch. `SC-09` deliberately untouched: `D-15` already
directs the DEC-209 entry to name adopt *and* discard, and widening `SC-09` would reopen `T-08`.

## Anchor note — the dispatch's sha is stale by one merge, harmlessly

The dispatch says the main checkout is at `ad93d43e`. It is at **`a7569463`** (the FEAT-41 ship merge);
`ad93d43e` is an ancestor. `git diff --stat ad93d43e a7569463` over `plan-sign-gate.py`,
`plan-sign-gate.sh`, `test-plan-sign-gate.py` and `inflight_registry.py` is **empty**, so every anchor
`T-09` cites holds at both shas. `T-09`'s `intent:` records this rather than asserting a sha it was
not measured at. Anchors re-measured at source: `_basename` `:224`, `denies` `:256`, the `SEP` skip
`:291`, the recursion `:299`, the decision foot `:304`, `ROOT` `:35`, `agent_type` read `:73`
(`plan-sign-gate.py`); `GATE`/`PLAN_SIGN_GATE_BIN` `:22`, `_root()` `:36`, `ROOT` `:54`, `gate()`
`:57`, HIGH-2 group ends `:443`, summary print `:446`, `SystemExit` `:447`
(`test-plan-sign-gate.py`). `orphan_write` / `quarantine_rel` / `canonical_artifact`: **0** occurrences
in `inflight_registry.py`; `quarantine.py`: **absent** — both as the plan expects (T-02, T-04 unbuilt).

## Untouched, as instructed

`T-08`, `T-05`'s wake clause, the requirement set, `lanes:`, `panel:`, top-level `status: plan`, the
absent `approval:` mapping (still absent — correct, and `sign-approval` was not run), `feature.json`,
`STATE.md`, and the seven other tasks. Every task `status: ready`. **0** occurrences of `DEC-208`.

## Open questions

- **Q1 (non-blocking, pre-existing):** the plan carries no `approval:` mapping and `sign-approval`
  refuses such a plan (`plan-merge.py:879`). A FEAT-41 harness defect, already carried to the
  operator; out of scope here.
- **Q2 (non-blocking):** `lanes.rows` names no row for `plan-sign-gate.py`, `plan-sign-gate.sh`,
  `test-plan-sign-gate.py` or `test-gen-decisions-index.py`, so `T-07`, `T-08` and `T-09` run against
  surfaces the block does not list. `check-plan-routes.py` still exits 0 (it resolves against the live
  manifest, not the block), so nothing gates on it. `lanes:` was a declared non-goal; flagging, not
  fixing.
