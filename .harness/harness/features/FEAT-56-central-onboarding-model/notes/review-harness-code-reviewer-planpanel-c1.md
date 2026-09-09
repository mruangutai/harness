# Plan panel C1 — scope reader — FEAT-56 T-09..T-17

**BLUF: two mechanically-provable gaps, both in the exact class the last fix cycle spent its whole
budget closing. Ship-blocking is a judgment call for the lead; both are demonstrated with a red/green
scratch test, not asserted.** T-10's verify has zero protection against dangling internal step-number
references, despite its own intent naming two specific instances that must be repointed. T-11's verify
protects one half of the `:279-282` split sentence but not the other, so the exact "orphaned-and-
duplicated" defect class the cycle-1 goal-check found and fixed for the *second* sentence remains open
for the *first*. No orphan REQs, no invalid REQ citations, no cyclic or backwards dependency edge, no
verify anchored on content a predecessor deletes. One dependency-shape advisory (independently
re-derived, matches the goal-check's own untouched finding) and one disclosed-but-unclosed
verification gap on REQ-09 round out the list.

All commands below were run read-only against the worktree at `57dc1f8a` (`git diff 12f74ea8 HEAD --
.claude/skills/harness-init/SKILL.md` is empty — the file the plan's anchors cite has not drifted).
Scratch probes used shell variables/heredocs into `grep <<<`, never a file write — this persona's
bash-write-guard blocks even `/tmp` redirection, so file-based scratch cases from the dispatch's
suggested method were not available; the heredoc-into-`grep`-stdin substitute exercises the identical
conjuncts with identical semantics and is reported as such.

## Finding 1 — T-10 has no guard against dangling internal step-number references

**Severity: high.**

**Consequence.** `harness-add-repo/SKILL.md` ends with exactly three numbered steps (1 land-config,
2 interview, 3 delegate-detection). T-10's own intent identifies, by anchor, two internal
cross-references inside the prose it moves in verbatim that name step numbers which do not survive
the split — `:251` "fill test_kinds in step 4 and the GitHub block in step 7" and `:290` "decides
whether step 7 runs at all" — and instructs the doer to repoint both. Nothing in T-10's `verify:`
block checks that either repointing happened. A doer who follows the *content* instructions (move
:245-291 in, minus the named exclusions) but misses the *prose-repair* instruction ships a
registration skill whose own step 2 says "fill test_kinds in step 4" when there is no step 4 —
exactly the kind of self-contradicting instruction REQ-07 ("an operator reads that artifact and no
other") exists to prevent. T-17's permanent `test-onboarding-split.py` doesn't catch it either: its
harness-add-repo case only checks the four approval/BRIEF/Design/visual-designer absence tokens and
the three ordering markers, never step-number consistency.

**Contrast.** T-11, doing the mirror-image renumbering (9 numbered slots down to 6), carries seven
named dangling-reference sites and two dedicated verify bans (`! grep -qE 'steps? [7-9]'` and
`! grep -qE 'steps? [1-9] and [7-9]'`, plus four phrase-specific step-2 bans). T-10 carries zero.

**Evidence.** Built a scratch document satisfying every grep-based conjunct in T-10's verify
(Preflight heading present, `claude --version` absent, all `templates/team-config.yaml`-family bans
satisfied, `anywhere but the control plane` present, approval/BRIEF/Design/visual-designer absent,
`--check-product-configs` present) while deliberately retaining the two flagged-but-unguarded
references verbatim:

```
Instantiate templates/harness.json into a checkout of the repository. Fill test_kinds in step 4
and the GitHub block in step 7.
...
- Does this project have a user-facing UI? -- decides whether step 7 runs at all
```

Ran the grep-only portion of T-10's verify (the `test -f` and two `python3` conjuncts excluded —
they check real-tree paths, not this document's content) via `grep <<< "$content"` for every
conjunct, chained with `&&`: **`RESULT=0`** — full pass with both dangling references intact.
`grep -n 'step 4\|step 7'` on the same content confirms both lines are present and unflagged.

**Ask:** add step-number bans to T-10 symmetric to T-11's — at minimum `! grep -qE 'step [4-9]'`
(harness-add-repo has no legitimate step above 3, unlike harness-init which legitimately keeps steps
4-5) and a positive assertion that the mirror-question and test_kinds cross-references name the
document's own step 2/3 or the unnumbered mirror-section heading, not a number that left with T-11.

## Finding 2 — T-11 protects only half of the `:279-282` split sentence

**Severity: med.**

**Background, so the panel doesn't re-litigate settled ground.** The cycle-1 goal-check's row 5 /
question 3 found that the *second* sentence of `harness-init/SKILL.md:279-282` ("For the control
plane itself, instantiate its own `.harness/harness.json`...") was simultaneously orphaned by T-11's
whole-range delete and dragged into T-10. The fix cycle closed that with an explicit KEEP(a) in T-11
plus two positive greps (`instantiate its own`, flattened `from the templates`), and closed the
mirror question — *which* file the sentence's other half belongs to — by deciding the **first**
sentence ("No `team-config.yaml` exists anywhere but the control plane; no `.harness/expertise/`,
`.harness/products/`, `bin/`, hooks, or settings are written in a product repository.") moves to T-10
only, adding a **positive** requirement there (`grep -qF 'anywhere but the control plane' "$F"`).

**What's still missing.** T-11 never gained the matching **negative**. Nothing in T-11's verify bans
`anywhere but the control plane` (or any substring of that first sentence) from surviving in
`harness-init`. The sentence sits one line above KEEP(a) in the source text — exactly the kind of
adjacent line a doer preserving a nearby explicit KEEP is likely to leave untouched by inertia. If it
does, `harness-init` keeps a sentence whose entire subject is what gets written into a *product
repository* — content that belongs to registration, the job REQ-01 says this file must contain none
of — and no gate at any tier (T-11's own verify, `check-instruction-paths.py`, or T-17's permanent
`test-onboarding-split.py`, whose harness-init case checks only Track A/B, `factory/fleet.yaml`,
`brief is pending`, `The approval gate`, `then the BRIEF`, `Design pass`, `harness-visual-designer`)
would ever see it.

**Evidence.** Built a scratch `harness-init` candidate satisfying every T-11 grep conjunct (no Track
A/B, no `factory/fleet.yaml`, no stale step-7/8/9 references, all four KEEP positives present, both
hook command strings present) while retaining the disputed first sentence verbatim. Ran the full
grep-only portion of T-11's verify via `<<<` chaining: **`RESULT=0`.** None of the 25 conjuncts in
T-11's verify reference any substring of that sentence.

**Note on actual harm.** Unlike Finding 1, the sentence itself is true regardless of which file
carries it — this is a scope-boundary leak, not a factual error, and a human reading `harness-init`
top to bottom (the SC-11 UAT script) is unlikely to flag it as a problem, since it doesn't instruct
the operator to *do* anything registration-shaped. That's why this is `med`, not `high`: real but
lower-consequence than Finding 1's actively-misleading dangling step reference.

**Ask:** add `! grep -qF 'anywhere but the control plane' "$F"` (or an equivalent substring ban) to
T-11's verify.

## Finding 3 — dependency shape: T-12/T-15/T-16 serialize on T-11, need only T-10 (advisory, re-derived independently)

**Severity: low.** Not adopted from the goal-check — independently checked each of the three tasks'
own `files:` and `verify:` for a real read of `harness-init/SKILL.md`'s *content* (as opposed to
needing the *name* `harness-add-repo` to exist):

- **T-12** never lists `harness-init/SKILL.md` in `files:` and its verify never reads it; its router
  correction needs `harness-add-repo` to exist as a name to reference, which is T-10's output.
- **T-15** likewise never reads `harness-init/SKILL.md`; its own verify only touches the two agent
  files and their adapters. The replan-fix's counter-argument — T-15 asserts a *claim about*
  `harness-init` ("During `harness-init` you determine...") that is only true once T-11 lands — is a
  narrative-correctness argument, not a verify-blocking one: T-15's own gate cannot see whether the
  claim is true, so nothing mechanically requires T-11 first.
- **T-16** touches only docs, never `harness-init/SKILL.md`; same shape.

No topology violation exists — reassigning the depends_on set to T-10 does not create a cycle, and
`T-17`'s `[T-13, T-15]` still transitively guarantees T-11 lands before T-17 runs (via
`T-13 -> T-12 -> T-11`) even if T-15 no longer names T-11 directly. This confirms the goal-check's own
"advisory" disposition rather than upgrading it: the current shape costs parallelism, not
correctness, and was consciously left untouched by the fix cycle's own stated non-goal. Not raising
as must-fix; noting for the record so the lead can transcribe rather than re-derive.

## Finding 4 — REQ-09's "actually reachable through OMP" still has no gate that can see a wrong canonical root (disclosed, unclosed)

**Severity: low-med.** Independently confirmed `.omp/commands` **is** the correct canonical root:
`omp://config-usage.md` §6 states the native provider's project commands root is
`<cwd>/.omp/commands/*.md` — D-11's premise is factually right, today. What's unresolved is the
*verification* of that fact going forward: SC-13's four clauses (file existence, adapter-check
subprocess call, the orphan-adapter red-capability case, the door-deletion red-capability case) all
prove internal *consistency between* `.omp/commands` and `.claude/commands`; none of them can catch a
future edit that consistently moves both the canonical root and every checker to a wrong path (e.g. a
typo'd directory name) — exactly the same shape of silent failure REQ-09/REQ-10 exist to close. The
cycle-1 goal-check flagged this identical concern non-blocking (its Q2, recommending a `uat` clause
having the operator open a live OMP session and confirm `/harness-plan` resolves) and the fix cycle's
own "Open questions" section confirms Q2 was **left untouched** as out of that dispatch's scope — it
is not silently dropped, it is a live unresolved item the panel should decide on before signature, not
something I'm newly raising.

## Dismissed leads

- **"T-11 mixes absence/positive greps — do positives pin the KEEPs or just keywords?"** Dismissed.
  The replan-fix's own per-conjunct probe table shows 5 of 6 positives individually discriminate on
  the whole-range-cut mutant; the sixth (`test_kinds`) is deliberately paired with `harness-dev-ops`
  because `test_kinds` alone also appears in the surviving `--upgrade` section. Independently spot-
  checked: `--upgrade`'s only nearby text is "dev-ops verified those by running them" — no
  `harness-` prefix — so the pairing genuinely discriminates. Adequate.
- **"T-15's intent/verify mutually unsatisfiable — confirm independently."** Dismissed. Built a
  scratch pair (dev-ops text naming both skills as bare tokens with no backticked slash form;
  visual-designer text naming `/harness-plan` and omitting `harness-init`) and ran the grep-only
  portion of T-15's verify: exit 0. Simultaneously satisfiable as amended.
- **"T-11 bans four 'step 2' phrasings by rewording, not renumbering — is that a trap?"** Dismissed.
  The ban set deliberately excludes the bare string `step 2` (a legitimate step 2 exists post-cut),
  and three of the four sites have generalizable rewording guidance from the one worked example
  ("before you go on", not "before step 2"). This is ordinary main-session-direct doc-task
  specification depth, consistent with how T-01/T-02/T-06 specify prose elsewhere in this plan.
- **REQ coverage / orphan REQs / invalid trace citations.** Checked all 17 tasks' `traces:` against
  REQ-01..REQ-10: full coverage, no orphan REQ, no task cites a REQ id that doesn't exist. Matches the
  goal-check's own "Coverage arithmetic — PASS" and I see no reason to disagree.
- **`templates/harness.json` `_template` stub-only grading (PF-ff668c9d..., open).** Out of scope —
  concerns T-05, which is `done` and settled per contract item 3 (operator rejected the shape, not the
  delivered work).
- **Wrong canonical root risk (part of Finding 4).** The root itself is confirmed *correct* by
  `omp://config-usage.md`; only the forward-looking regression-detection gap is unresolved, hence
  folded into Finding 4 rather than treated as "the plan picked the wrong path."

## What I did not find

No verify block in T-09..T-17 is anchored on line content a predecessor task moves or deletes (T-03's
re-anchoring in the already-`done` T-03 was the one case of that shape, and it's out of scope). No
task's intent is unsatisfiable given its verify, beyond the two gaps above (gaps in the *verify's
coverage*, not contradictions between intent and verify). No dependency edge runs backwards or forms
a cycle. SC-13's file-existence/adapter-parity mechanism would have gone genuinely RED against the
live pre-fix state — confirmed directly: `.omp/commands` does not exist, `sync-command-adapters.py`
does not exist, `harness-add-repo/SKILL.md` does not exist, `.claude/commands` carries exactly 4
`harness*.md` files today.
