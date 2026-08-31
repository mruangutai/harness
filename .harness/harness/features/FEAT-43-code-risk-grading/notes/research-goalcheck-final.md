# FEAT-43 final goal-check — SC-11 recorded `met`, 20 of 20

**BLUF: 20 met, 0 not_met, 0 open.** SC-11 — the feature's central claim, that the shipped guidance
changes what an engineer writes — is **met**. Evidence: `notes/uat-sc11-c21.md` (`status: passed`,
operator-issued 2026-08-29 at pin `cd8dae47`). I did not adopt the arithmetic: I re-derived it from
the raw numbers, and I re-ran the grader over the four surviving arm outputs and reproduced all four
values exactly. The other nineteen are **carried forward by reference** from
`notes/research-goalcheck-c26.md`, not re-derived here.

## 1. SC-11 against its own frozen rule — derived, then corroborated

The rule was ruled by the operator on arm **MAXIMA** and stamped SETTLED **before any number was
drawn** (`answers/Q9-sc11-maxima-and-t01-no-exemption.md:7-22`). SC-11's own text
(`BRIEF.md:154-171`) says "the worst cognitive complexity in the skill-loading arm", and Q9 fixes
"worst" as the maximum.

Raw numbers read by me out of `notes/uat-sc11-c21.md:146`: `a1 = 6`, `a2 = 5`, `b1 = 16`, `b2 = 14`.

```
worst_A  = max(6, 5)  = 6          spread_A = |6 - 5|  = 1
worst_B  = max(16, 14) = 16        spread_B = |16 - 14| = 2
gap      = 16 - 6 = 10             max(spread_A, spread_B) = 2
```

- Condition 1 — `worst_A < worst_B`: **6 < 16 → holds.**
- Condition 2 — `gap > max(spread_A, spread_B)`: **10 > 2 → holds.**
- **Both hold → `met`.** Neither is marginal; the gap is 5× the larger within-arm spread.

**Ungraded counts, independently established rather than taken on the record's word.** The four
variant outputs survive at `/tmp/sc11-uat/arm_{a1,a2,b1,b2}.py`. I re-ran the exact grading command
from the script (`.agents/skills/harness/bin/code-grade.py --json <f>`, worst = `max` over
`.records[].cognitive`) against all four, read-only:

| variant | worst cognitive | `ungraded` len | functions |
|---|---|---|---|
| arm_a1 | **6** | 0 | 21 |
| arm_a2 | **5** | 0 | 25 |
| arm_b1 | **16** | 0 | 15 |
| arm_b2 | **14** | 0 | 11 |

**All four numbers reproduce the transcribed values exactly, and every `ungraded` list is empty** —
so no variant is inconclusive under the script's own clause (`notes/uat-sc11-c21.md:113-114`). This
is a stronger basis than transcription: the arithmetic and its inputs are both re-derived.

## 2. The integrity note, carried forward — and my assessment

`notes/uat-sc11-c21.md:154-159` discloses that **an initial dispatch was discarded before any number
was recorded.** Shared context had revealed the experimental arms to the control agents — exactly the
contamination the script's control-arm rules exist to prevent (`:96-98`). Its scratch outputs were
deleted, and every reported value comes only from the subsequent neutral-context run.

**My assessment: it does not change the verdict, and the lead's read holds.** A discard is a
selection between draws only if the discarded draw's *numbers* influenced the choice to discard it.
Here the void was declared on a **procedural** defect that is identifiable without looking at any
number, and the record states no number existed when it was declared. So this is a disclosed
protocol violation and re-run, not a best-of-two.

One corroboration I ran rather than argued: none of the four surviving outputs contains any of
`cognitive`, `cyclomatic`, `complexit*`, `grade <n>` or `ABC magnitude` (case-insensitive) — the
controls carry no trace of the metric vocabulary a contaminated dispatch would have leaked. That is
consistent with a clean run, not proof of one.

**The residual limitation, stated plainly:** I can verify the numbers the surviving files produce; I
cannot verify by inspection that these files are the neutral run's rather than the discarded run's.
That rests on the operator's disclosure. The mtimes (21:54, after the 21:47 scratch-repo init) and
the vocabulary check are consistent with it; neither settles it. This is the one link in the SC-11
chain that is testimonial rather than measured, and a reader of the ship briefing should know that.

## 3. What the pass licenses, and what it does not

SC-11 passing means the feature's central claim is now supported by a **measurement rather than an
argument**: agents that loaded the shipped skill wrote code whose worst cognitive complexity was
lower than the control's, by a margin well outside the within-arm noise, on an identical task with
the control provably ignorant of the metric. That licenses the claim *the guidance demonstrably
changed what was written on this task*. It does **not** license a general effect size, a claim about
other task shapes or languages, or a claim about durability over time: this is a **single A/B on one
task with two variants per arm**, n=2 per arm, one metric, one model, one sitting. The pass clears
SC-11 as written — it does not convert the skill's benefit into a measured constant, and a later
regression on a different task would not contradict this result.

## 4. The nineteen — carry-forward by reference, not re-derived

**Explicitly a carry-forward.** SC-01 through SC-10 and SC-12 through SC-20 were re-derived at the
pin `cd8dae47` in `notes/research-goalcheck-c26.md` (delta bound at `:9-20`, re-run evidence
`:22-45`, SC-15 basis `:65-83`, inherited set `:89-99`, overall `:103`). I re-ran nothing here and
changed no verdict. Every source and test file is byte-identical to `cd8dae47` (§6), so that
derivation still describes the tree it was made against.

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated (unit) | `check_fixtures` — c26 §1 |
| SC-02 | met | inspection | fixture-table md5 `df9f4fd0…` identical at 3 pins — c26 §1 |
| SC-03 | met | automated (unit) | `check_direction_pairs` — c26 §1 |
| SC-04 | met | automated (integration) | `test-code-grade-cli.py` — c26 §4 |
| SC-05 | met | automated (integration) | `test-code-grade-cli.py` — c26 §4 |
| SC-06 | met | automated (integration) | `test-code-grade-cli.py` — c26 §4 |
| SC-07 | met | automated (integration) | `check_changed_function_resolution` — c26 §1 |
| SC-08 | met | automated (integration) | same case, absence assertions — c26 §1 |
| SC-09 | met | automated (unit) | `check_worked_examples` — c26 §1 |
| SC-10 | met | automated (unit) | `check_delivery` — c26 §1 |
| **SC-11** | **met** | **uat** | **`notes/uat-sc11-c21.md` — `status: passed`; re-derived §1** |
| SC-12 | met | automated (unit) | `test-gate-policy.py` — c26 §4 |
| SC-13 | met | automated (unit) | `test-gate-policy.py` — c26 §4 |
| SC-14 | met | automated (integration) | 12 live demands, `--base 7ccfae8d --head cd8dae47` — c26 §3 |
| SC-15 | met | inspection | set equality 12/12 vs `review-…-c25.md:148-188` — c26 §3 |
| SC-16 | met | automated (integration) | `test-check-plan-routes.py` — c26 §4 |
| SC-17 | met | automated (unit) | `test-code-grade.py` — c26 §1/§4 |
| SC-18 | met | inspection | `harness-code-risk-grading/SKILL.md` — c26 §4 |
| SC-19 | met | automated (integration) | `test-validate-digest.py` — c26 §4 |
| SC-20 | met | automated (integration) | `test-validate-digest.py` — c26 §4 |

**20 met · 0 not_met · 0 partial · 0 open.** REQ coverage is unchanged from c26; no requirement lost
its trace and none was added.

## 5. Two precisions a ship briefing must not trip over

- **The operator's `passed` transcription is working-tree only.** The copy committed at HEAD still
  reads `status: ready` (`git show HEAD:…/uat-sc11-c21.md` line 2). The evidence pointer is the
  **working-tree** file, as in the c26 precision about the pin line (`c26 §6`). Expected, not a
  defect — but a reader of the committed tree would see `ready` and conclude SC-11 is open.
- **HEAD is not `cd8dae47`.** It is `0989f286`, two commits ahead (`7dc6c67`, `0989f28`). **I did not
  move it.** `git diff --name-only cd8dae47..HEAD -- ':!.harness'` is **empty** and
  `git diff --numstat cd8dae47..HEAD -- .claude .agents .omp code_grade.py` is **empty** — both
  commits are `.harness/` bookkeeping only. The review basis is therefore intact and every
  carried-forward verdict still describes the shipped bytes.

## 6. Working tree

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
```

That entry is the operator's transcription and predates me — I did not touch that file. My own
artifact (this file) appears after this snapshot was taken; nothing else is mine. No source, test,
`BRIEF.md` or commit was touched, and I ran no formatter, linter or project suite. The four regrades
were read-only over `/tmp`.

## Open questions

- **Q1 (non-blocking):** commit the operator's `passed` transcription before or with the ship
  decision, so the record on disk matches the record in the working tree. Not mine to commit.
- **Q2 (non-blocking, carried from c26):** the stray untracked `FEAT-43-code-risk-grading/` directory
  in the MAIN checkout persists. Still worth cleaning before the next feature.
