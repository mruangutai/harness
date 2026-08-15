# Revision 2 — withdrawn ruling 1, and INV-17's execution-mode exemption

**BLUF.** Both changes landed inside the operator's signature. FEAT-15 now migrates to `Done`, the
rule behind T-04's table is override-guarded so a stale `phase` cannot outlive the corrected row, and
T-12 gains a plan-keyed INV-17 exemption alongside (never replacing) its literal FEAT-01/FEAT-02 set.
**The mechanical gate is green at the revised plan: `0 violation(s) across 12 plan(s)`.**

**The operator's stated justification for condition 2 is wrong, and the plan now carries the true
one.** Condition 2 excludes nobody in today's corpus. See below.

## The mechanical gate — actual output, run at the revised plan

```
DEVIATION T-04 .claude/skills/harness/bin/bash-write-guard.sh, .claude/skills/harness/bin/test-bash-write-guard.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
DEVIATION T-05 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/test-check-state.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
DEVIATION T-06 .harness/features/FEAT-17-guard-boundaries/notes/worktree-list-before.md, .harness/features/FEAT-17-guard-boundaries/notes/worktree-list-after.md granted to harness-orchestrator but declared main-session-direct
OK T-07 granted to harness-documentor
0 violation(s) across 12 plan(s)
```

(Those three `DEVIATION` lines are FEAT-17's, pre-existing and not violations.)

## Condition 2 — measured, not asserted

Predicate: exempt iff **(1)** a `plan.yaml` exists, **(2)** its `tasks:` list is non-empty, **(3)**
every task is `execution_mode: main-session-direct`.

| Feature | Plan artifact | `execution_mode` keys | Which condition excludes it |
|---|---|---|---|
| FEAT-01 | none | — | **1** (no plan file) |
| FEAT-02 | `PLAN.md` | 0 | **1** (not a `plan.yaml`) |
| FEAT-03 | `PLAN.md` | 0 | **1** |
| FEAT-04 | `PLAN.md` | 0 | **1** |
| FEAT-05 | `PLAN.md` | 0 | **1** |

**Condition 1 excludes all five. Condition 2 excludes none of them, and none of the rest of the
corpus either** — every `plan.yaml` on disk (FEAT-10 through FEAT-17) has a non-empty `tasks:` list.
Condition 2 is a **vacuity guard** and nothing more: `all(...)` over an empty list is `True`, so
without it a stub plan with `tasks: []` or a mistyped `tasks:` key would be silently exempted from a
seam invariant. That is an honest and sufficient reason to keep it, and it is now what the plan says.
The operator's grounding — that condition 2 stops FEAT-02/03/04/05 being exempted — is not what the
tree shows.

**A deliberate false negative, recorded:** FEAT-06 and FEAT-07 are all-`main-session-direct` but on
`PLAN.md`, so condition 1 keeps them non-exempt. Safe, and costless — FEAT-06 carries plan+build at
Review, FEAT-07 carries all three.

**The exempt set the checkers compute today** — run against the corpus with the exact expression now
in T-08's `verify:` — is `['FEAT-01', 'FEAT-02', 'FEAT-15-domain-product-base']`.

## What changed, by file

`plan.yaml` (approval block lines 4-7 byte-identical, untouched):
- **T-04** — table row → `FEAT-15 … -> Done`. The `awaiting_user`-splits-on-old-phase clause is
  **deleted** and replaced by an override that outranks every row: read the plan's `approval` block
  and merged state; `approval: approved` + merged PR ⇒ `Done` whatever the old `phase` said. The
  FEAT-15 note's false "carries approval pending" justification is rewritten around what is true at
  `a29ad06` (approved, PR #263 merged, #239 closed) and its zero notes are re-explained as correct.
- **T-11** item 5 — six Done / ELEVEN checked → **seven Done / TEN checked**. Not named in the
  dispatch; changed because it is SC-17's arithmetic restated inside the plan and would otherwise
  contradict it. T-11's `verify:` hardcodes no count (it asserts `>= 1`), so nothing mechanical moved.
- **T-12** — new §2b (the three-condition predicate, fail-closed citing SC-16, lazy evaluation via
  `harness_yaml.load_file`, the both-mechanisms-survive rationale, the measured condition-2
  justification above) and §2c (the report line: `warn.append`, must carry `exempt`, the feature name
  and `handoff`, and must **not** contain `VIOLATION`). §3's case list grows **four → seven** and now
  instructs extending `make_fixture` to write a `plan.yaml` first — without that the three new cases
  are unwritable. The dry-run paragraph is re-derived: zero violations **plus one exemption note for
  FEAT-15**; the "do not widen the exemption set to make it quiet" warning is verbatim. `files:` and
  `execution_mode: main-session-direct` unchanged.
- **T-08** — the hardcoded `FEAT-01/FEAT-02` clause is replaced by a **computed** exempt set, plus an
  assertion that an exemption note line exists at all (silence is not evidence of a granted
  exemption). `import glob, subprocess, sys` gained `yaml` rather than adding a line. Still a literal
  `|` block. **Budget: T-08 is 48 of the 50 machine-field lines DEC-182 allows per task** — 2 spare;
  the next editor of that clause must fold, not append.

`BRIEF.md`:
- **SC-17** — expected checked-plan count **11 → 10**; `Done` list gains FEAT-15.
- **SC-08** — adds the plan-keyed exemption on FEAT-15, the note-emission requirement, and that the
  exempt set is computed rather than a hardcoded roster.
- **SC-18** — three directions and seven cases, with the empty/absent-`tasks:` and no-`execution_mode`
  cases named explicitly, and "no assertion here is exit 0" strengthened from "two assertions".

## Ordering — checked, no `depends_on` changed

T-08's new note-line assertion and T-12's re-derived dry-run both require FEAT-15 to already be
`Done`, which only T-04 produces. Transitive closure over `depends_on`, computed from the revised
plan: **T-08 → {T-01, T-03, T-04, T-05, T-06, T-07, T-11, T-12}** and **T-12 → {T-01, T-04, T-06}**.
T-04 is reachable from both. No edge added, so T-08 stays at 48 budgeted lines.

## Not done, deliberately

- **No prose cited the withdrawn dry-run** ("0 INV-17 violations at `Plan`, 2 at `Review`") anywhere
  in `plan.yaml` or `BRIEF.md` — grepped; it lives only in `notes/answers-2026-08-11-revision.md`,
  where the CORRECTION section already withdraws it. Nothing to kill.
- **"FEAT-17 will be the second" appears nowhere in the plan or brief**, so nothing to strip. It is
  false: FEAT-17 T-07 is `execution_mode: team`, so FEAT-17 is not exempt and correctly still owes
  handoff notes. The predicate was not weakened to reach it.
- No lane changed; no task created; no `plan.yaml` path added to any `files:` block.
