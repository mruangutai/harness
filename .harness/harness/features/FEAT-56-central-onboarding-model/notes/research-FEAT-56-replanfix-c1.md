# Replan fix — FEAT-56 cycle 1 — the four goal-check findings are closed

**BLUF: all four are closed in `plan.yaml` (six `amend` writes) and `BRIEF.md` (one edit).** The hole
is closed by naming three EXPLICIT KEEPs in T-11 and giving each a positive grep that reddens on the
whole-range cut; T-10 no longer drags the control-plane instantiation sentence into the registration
skill; T-15's two halves now agree. Task count 17, `approval: pending`, T-01..T-08 still `done`,
`check-plan-routes.py` exit 0. `panel:` untouched, no production file touched, nothing committed.

## F1 + F2 — the hole (T-11 `intent` + `verify`)

Three KEEPs, each named as a KEEP inside the deleted `:239-418` range and folded into a stated SIX-step
sequence (1 prerequisites · **2 instantiate this checkout's config** · 3 interview · 4 detection ·
5 seed manifest · 6 verify), with the ordering reason written down (detection writes `test_kinds`
INTO `.harness/harness.json`; step 5 rewrites `team-config.yaml`'s `# SEED` globs — both need step 2
to have happened):

- **(a)** the control-plane instantiation sentence, the SECOND sentence of `:279-282` (it begins
  mid-line at `:280` — measured, and this matters to F3). Verified as the tree's only such
  instruction: `grep -n 'instantiate its own|from the templates|the only place'` returns `:281`,
  `:281-282`, `:282` and nothing else.
- **(b)** the technical interview `:284-291`, minus "decides whether step 7 runs at all" (D-09 removed
  that gate). The question SURVIVES with a new reason: dev-ops needs it to judge a null `ui` runner
  against a project with a real UI (`:307-312`).
- **(c)** dev-ops detection `:292-323`, restricted to this checkout — the fleet-member half
  (`:296-298`) is deleted as T-10's.

`intent` states why removal breaks the cut: surviving step 5 `:163-164` demands "the real path from
dev-ops's report", and surviving step 9 `:188-193` demands `check-state.sh` exit 0, unreachable on a
checkout with no instantiated `.harness/harness.json`.

**One existing assertion contradicted a KEEP and was narrowed:** `! grep -qE 'steps? [4-9]'` →
`[7-9]`. With six surviving steps, "step 4" and "step 5" are legitimate numbers, so the old ban made
the task unpassable; 7–9 exist under no numbering, and it is still RED today (`step 7` at `:251`,
`:290`, `:194`). Every other assertion is unchanged. **Hazard cleared:** `! grep -q
'factory/fleet.yaml'` still holds against the KEEPs — that string occurs only at `:10` and `:261`,
both of which leave. The detection prose says bare `fleet.yaml` at `:299` (dispatch guessed `:294`),
which the ban does not match.

### Evidence — the three POSITIVE greps, and their discrimination

Quoted from the amended block (each `&&`-chained, `$F` = `.claude/skills/harness-init/SKILL.md`):

```
grep -qF 'instantiate its own' "$F" &&                              # (a)
cat "$F" | tr '\n' ' ' | grep -qF 'from the templates' &&           # (a), flattened: the sentence wraps
grep -qF 'Interview' "$F" && grep -qF 'Project type' "$F" &&        # (b)
grep -qF 'harness-dev-ops' "$F" && grep -qF 'test_kinds' "$F" &&    # (c)
```
plus the negative guard on (c)'s restriction: `! grep -qF "fleet member's own" "$F" &&
! grep -qF 'lands the latter' "$F"`.

Per-conjunct probe (`/tmp/f56/probe-t11.sh`, one process per grep):

```
### against the REAL file (today)          ### against the mutant: :239-418 deleted whole
FAIL  ! fleet members own  (NEG-c)         PASS  ! fleet members own  (NEG-c)
FAIL  ! lands the latter   (NEG-c)         PASS  ! lands the latter   (NEG-c)
PASS  + instantiate its own   (POS-a)      FAIL  + instantiate its own   (POS-a)
PASS  + from the templates    (POS-a)      FAIL  + from the templates    (POS-a)
PASS  + Interview             (POS-b)      FAIL  + Interview             (POS-b)
PASS  + Project type          (POS-b)      FAIL  + Project type          (POS-b)
PASS  + harness-dev-ops       (POS-c)      FAIL  + harness-dev-ops       (POS-c)
PASS  + test_kinds            (POS-c)      PASS  + test_kinds            (POS-c)
```
The mutant is the cut T-11 originally specified. Five of six positives redden on it — the hole is
now visible to the verify. `test_kinds` alone does NOT discriminate (`:221` in `--upgrade` carries
it), which is why (c) is anchored on `harness-dev-ops` as well; noted rather than removed.

**T-11's amended block run VERBATIM against the current tree: `exit=1`** (first conjunct
`! grep -q 'Track A'`).

## F3 — the sentence moving the wrong way (T-10 `intent` + `verify`)

**Decision: the FIRST sentence MOVES IN, the second does not.** The prohibition ("No `team-config.yaml`
exists anywhere but the control plane; no `.harness/expertise/`, `.harness/products/`, `bin/`, hooks,
or settings are written in a product repository") is addressed to exactly the operator `harness-add-repo`
serves. The instantiation instruction is not. The split is mid-line at `:280`, and the intent says so.

Consequences recorded in the intent: the moved range is `:245-280` (through "...product repository."),
and the detection bullet moves in MINUS its control-plane half — the mirror of KEEP (c), added because
otherwise the two files would each instruct both writes.

**One Red-flags row was reassigned as a direct consequence:** "I'll copy the new team-config over
theirs" now stays with T-11. Its advice presumes a `team-config.yaml` in the repository being touched,
which the prohibition moving in at `:279` forbids — carrying it into `harness-add-repo` would
contradict that prohibition inside one file. It belongs to `--upgrade` (`:224`, reported never
rewritten). Both T-10's and T-11's intents were amended to agree.

The stale ban `! grep -qF 'templates/team-config.yaml'` is kept (it still catches the literal path
form) and widened by four conjuncts:

```
! grep -qF 'instantiate its own' "$F" &&
! cat "$F" | tr '\n' ' ' | grep -qF 'from the templates' &&
! cat "$F" | tr '\n' ' ' | grep -qF 'the only place a' &&
! grep -qF "into the control plane's" "$F" &&
grep -qF 'anywhere but the control plane' "$F" &&
```

**Evidence — T-10's amended block run verbatim, `F` repointed at scratch files in `/tmp/f56/`
(nothing in the tree touched); every other conjunct satisfied in all four, so the new ones are the
only variable:**

| scratch | content | exit |
|---|---|---|
| real tree | file absent | `1` (at `test -f`) |
| A | full paragraph, both sentences | `1` |
| B | A minus the instantiation sentence | `0` (`scanned 62 file(s), 0 violation(s)`) |
| C | B minus the prohibition sentence | `1` |
| D | B plus "into the control plane's `.harness/harness.json`, or" | `1` |

**T-17 needs no amendment:** its split test asserts only `The approval gate`, `then the BRIEF`,
`Design pass`, `harness-visual-designer` and the ordering markers — it never greps a team-config
string, so it was not looking at the wrong one. **SC-01 in BRIEF.md WAS**, and is fixed: "no
instruction to instantiate or to copy a `team-config.yaml` — not into a project and not for the
control plane, whose own instantiation instruction stays in `harness-init` (T-11)".

## F4 — T-15's contradiction

**Upheld the lead's reading:** the intent's "say both" is correct; the blanket ban was wrong. Primary
source: the operator's ruling isolates `harness-init` to fresh-checkout configuration, so detection
for THIS checkout is its by definition, and T-11 now keeps it there explicitly. The `verify` now bans
the STALE CLAIM — the backticked slash spelling `` `/harness-init` `` at `.omp/agents/harness-dev-ops.md:53`
— and REQUIRES the bare token, so the file must name both skills unslashed:

```
! grep -qF '`/harness-init`' .omp/agents/harness-dev-ops.md &&
grep -qF 'harness-init' .omp/agents/harness-dev-ops.md &&
grep -qF 'harness-add-repo' .omp/agents/harness-dev-ops.md &&
```
(and the same three for the `.claude/agents/` adapter). A bare `! grep -q '/harness-init'` was
rejected: it also matches the path `.claude/skills/harness-init/SKILL.md`.

```
### today, real .omp/agents/harness-dev-ops.md   ### scratch copy written as the intent asks
FAIL  ! `/harness-init`                          PASS  ! `/harness-init`
PASS  + harness-init                             PASS  + harness-init
FAIL  + harness-add-repo                         PASS  + harness-add-repo
```
Simultaneously satisfiable, and RED today. **Full amended block verbatim against the tree: `exit=1`.**

**The visual-designer half's blanket bans are kept, confirmed by reading the file, not assumed:**
`grep -n 'harness-init'` returns exactly one line in each of `.omp/agents/harness-visual-designer.md:42`
and its adapter `:41` — the design-pass claim D-09 deletes. That agent has no relationship to either
onboarding artifact, so banning the token outright is correct there.

## The five already-met SCs — all five UN-MARKED, none re-scoped

The operator ruled no prior grade is retained, and a stable subject cannot be manufactured for four of
the five (their subjects are files new tasks rewrite). Re-scoping the fifth would weaken a criterion to
protect a grade. So the marking is gone everywhere, and the preamble (`BRIEF.md:143-154`) now says
"No grade is carried forward, and every one of the five is re-taken at `<review_sha>`" and names which
task rewrites which subject. `grep -i 'already met|not re-prove|regression check'` over BRIEF.md now
returns nothing (exit 1), so preamble and paragraphs no longer contradict.

| SC | subject rewritten by | disposition |
|---|---|---|
| SC-02 | T-11 (blob, renumbering, three KEEPs inside it) | un-marked; "Graded ONLY at `<review_sha>`" |
| SC-05 | nobody | un-marked; re-taken because a grade at another pin is not evidence about this one; the 18/18 is kept as an expectation, not as the grade |
| SC-06 | T-17 (`tests/unit/test-no-distribution.py`) | un-marked; standing gate over this diff |
| SC-07 | T-14, T-17 (two new integration files) | un-marked; standing gate over this diff |
| SC-10 | T-12 (comment header) | un-marked; the #168 grade is about a different blob |

## Acceptance evidence

```
$ python3 -c "...len(d['tasks']),d['approval']"      -> 17 {'status': 'pending'}
$ T-01..T-08 statuses                                -> all 'done' (8/8)
$ scalar style of every amended field                -> '|' (literal) x6
$ bash <T-10 verify verbatim>  exit=1
$ bash <T-11 verify verbatim>  exit=1
$ bash <T-15 verify verbatim>  exit=1
$ check-plan-routes.py <plan>  -> "0 violation(s) across 1 plan(s)"  exit=0
```

## Open questions

- **Q1 (non-blocking, eng-lead):** goal-check finding 4's dependency advisory (re-point T-12/T-15/T-16
  at `depends_on: [T-10]`) is untouched, per this dispatch's non-goals. T-15's `depends_on: [T-11]`
  is now arguably real rather than habitual — T-11 is what decides that `harness-init` keeps detection,
  which is the claim T-15 writes into the agent file — so if the advisory is actioned, T-15 is the one
  edge worth keeping.
- **Q2 (non-blocking, operator):** the four step-2 phrase bans (`before step 2`, `skip to step 2`,
  `proceed to step 2`, `through step 2`) force the doer to REWORD those four sites rather than
  renumber them, since a legitimate step 2 now exists. The intent says so explicitly. If the operator
  prefers renumbering, those bans have to go and the seven-site list becomes unguarded.

## Send-back — the two `steps 4 and 8` sites

**Closed.** The `[7-9]` narrowing stays (steps 4 and 5 are legitimate under the six-step numbering);
one compound-reference conjunct was ADDED beside it, so all seven dangling sites T-11's intent
enumerates are guarded again. `intent` was amended in the one sentence that described the ban.
I picked a pattern that admits only valid pairs — the prescribed rewording "steps 4 and 5" is
UNCHANGED.

### 1. The new conjunct

```
! grep -qE 'steps? [1-9] and [7-9]' "$F" &&
```

Spliced immediately after `! grep -qE 'steps? [7-9]' "$F"` (`plan.yaml:1120`). Together the pair
catches `step 8`, `steps 8 and 4` (first conjunct) and `steps 4 and 8` (second), while `steps 4 and 5`
passes both.

### 2. Per-conjunct probe — fires on the real file, silent on the prescribed rewording

Real tree, read-only (`grep -nE 'steps? [1-9] and [7-9]' .claude/skills/harness-init/SKILL.md`):

```
159:... — steps 4 and 8 below run *with* enforcement
205:... which is why steps 4 and 8 work.
exit 0   → the `!` conjunct FAILS, as required
```

Scratch copy `/tmp/feat56-t11/scratch/SKILL.md`, generated by `/tmp/feat56-t11/build_scratch.py`
from the real file by performing T-11's prescribed cut and all seven rewordings (`:159` →
"steps 4 and 5", `:160` → "step 6", `:205` → "which is why step 4 works"): the same grep exits 1,
and so does the pre-existing `steps? [7-9]`. Both bans are silent on the corrected text.

### 3. The whole amended block, run VERBATIM against the tree

`python3 /tmp/feat56-t11/run_verify.py verbatim` loads `verify` out of `plan.yaml` and runs it under
`bash -c` with cwd = the worktree. **Exit 1** — RED, as it must be pre-build. It short-circuits at
the first conjunct (`Track A`, still at `SKILL.md:48`), which is why the new conjunct's own
discrimination is proven by the direct probe above rather than inferred from this exit code.

### 4. Satisfiability — the block and the intent do not contradict each other

`python3 /tmp/feat56-t11/run_verify.py scratch` runs the same block against the scratch file:
**exit 0**. Every step-number ban, every step-2 phrase ban, the two `tr`-flattened conjuncts and
every KEEP grep hold SIMULTANEOUSLY on a file written as the intent prescribes. **Excluded: the
final two conjuncts** `python3 tests/integration/test-hooks-install.py` and
`python3 .claude/skills/harness/bin/check-instruction-paths.py` — both read the real tree, not `$F`,
so they say nothing about the scratch file. Nothing else was excluded.

### 5–7. Plan invariants after the amend

- `len(tasks) == 17`, `approval == {'status': 'pending'}`, `panel` still present.
- `done`: T-01…T-08, unchanged. T-11 stays `ready`.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s) across 1 plan(s)`, **exit 0**.
- `plan.yaml:1109 verify: |` and `plan.yaml:1138 intent: |` — both still literal block scalars;
  both writes went through `plan-merge.py amend --expect-sha256 --value-file`.
