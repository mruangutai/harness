# Distillation pass — harness-pm — FEAT-25

**Two candidates accepted by displacement, one rejected. Counts unchanged: 15/15/6/0 before and
after; `check-expertise.sh` exits 0.** No repository-tier file created — neither entry turns on a
fact true of this repository alone.

## Ops applied to `.harness/expertise/harness-pm.md`

| op | target | section | source |
|---|---|---|---|
| replace | G-08 | Gotchas | C1 — a runner's exit code and ok-count cannot carry a "passes" claim |
| replace | P-03 | Patterns | C2 — a criterion whose grading set is derived from the artifact under grading |

Read-modify-write over the on-disk file; every other entry preserved verbatim (123 lines, under the
150-line craft budget).

### Why G-08 was the weaker Gotcha
Its failure mode is **loud** — an unregistered file reds the whole run and announces itself within
one cycle. C1's failure is silent: a suite prints `FAIL - <name>`, exits 0, and the criterion grades
met forever. Between two entries competing for one slot, the silent failure earns it.

I considered G-03 (capture by command substitution, never pipe to `tail`) as the displacement target
since it is the same family, and rejected that: G-03's remedy *supplies* what C1's remedy consumes —
whole captured output to grep the failure prefix against. They compose rather than conflict.

Verified at source before accepting: `.claude/skills/harness/bin/test-layout-migration.py` — `fails
+= 1` sits inside `if not ok and detail:`, and the runner exits `1 if fails else 0`. Failed cases
print a `FAIL - ` prefix that no `ok   - ` count sees.

### Why P-03 was the weaker Pattern
P-03 restated a rule that reaches every spawn already — `harness-brief`'s verify-method table and the
pm role prompt's "for `verify: automated`, read qa's DIGEST and cite the specific test". An Expertise
slot spent on a preloaded rule earns nothing. The alternative candidate for displacement, P-02
(a test kind's detect globs matching zero files on the changed surface), is stated nowhere preloaded
and therefore lives in Expertise or nowhere. P-02 kept.

C2 is distinct from P-01: P-01 covers a check that *would already have passed before the change*;
the new P-03 covers a check whose **input set is defined by the artifact it grades**, which is true
by construction and cannot fail at any commit. Both halves of the rule are in the entry — re-base on
an independent source, and prove de-vacuification by naming the case that now fails.

Verified at source: `runs/2026-08-18-3-product/digest.md:42-50`.

## Rejected

- **C3 — declining a dispatch order to record a true sentence as false.** Verified at source
  (`runs/2026-08-18-2-product/digest.md:36-67`; the fleet-filtering and fleet-absence evidence is as
  recorded) and rejected anyway. The duty it teaches is already carried twice: P-08 mandates
  verifying at source any factual claim my own intent prose directs, and P-06 forbids adopting a
  handed-down framing the evidence defeats, even one a downstream gate upheld. PRINCIPLES rule 15 is
  preloaded on top. The residue — that the pressure arrived via the dispatch rather than via a gate —
  is a **circumstance, not a rule**. I explicitly declined to sharpen P-08 to absorb it: bolting the
  new trigger onto a surviving entry is adding an instance to a rule, which is the story-not-rule
  failure the distill skill names first.

Not re-litigated: the four candidates the relay filtered out (baseline re-derivation, the
`verify: automated` open question, AST baseline non-emptiness, the zero-send-back `intent:` result).
I concur with each filtering reason and resurrect none.

## Section counts

| Section | Cap | Before | After |
|---|---|---|---|
| Patterns | 15 | 15 | 15 |
| Gotchas | 15 | 15 | 15 |
| Outcomes | 10 | 6 | 6 |
| Open | 5 | 0 | 0 |

`.claude/skills/harness/bin/check-expertise.sh .harness/expertise/` → exit 0, all 15 files OK, no
advisory flag on `harness-pm.md`. Nothing committed or staged.
