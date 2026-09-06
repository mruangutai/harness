# Goal-check c4 — SC-07 re-grade @ `review_sha 154ff2a0` (code-identical to `1155f188`)

**SC-07 is still `not_met` — but for a different reason than at c3, and the new reason cannot be
fixed by any builder.** The c3 remedy landed and is correct on the merits: both directions of the
criterion are now satisfied in substance, every citation is corrected and correct, and the section
BLUF that was false at `5ed929bd` is true at the pin. What fails is SC-07's **final `FAILS if` leg**
(`BRIEF.md:389-390`), which fires on a note BLUF that discloses a previously-permitted write now
refused "other than the disclosed dropped-`run_uid` one". The reconstruction-`None` refusal **is**
such a class, it was **ordered by the Advisor** at cycle 13 (`STATE.md:15`) and is **required by
SC-01(a)** — and SC-07's carve-out, written before that ruling, was never widened. The only way to
green the leg is to demote a true, material disclosure out of the BLUF. **Advisor lane, not a work
item.** Mode A and Mode B are each independently declarable delivered.

## Direction one — nothing removed: **satisfied**

- Both BUG-1106 flips are enumerated at `notes/regression-delta-BUG-1305.md:12` — "an unmatched
  `old_string` and a non-unique `old_string` on governed artifacts now fail closed instead of
  delegating refusal to the editor".
- **The justification is TRUE at the pin, not merely present.** Both flipped cases
  (`test-check-domain.py:3839`, `:3848`) use `_bug1124_state_fixture` — a governed `state.yaml` — and
  both now assert exit 2 plus `Write the complete file instead`. The branch they exercise is
  `check-domain.sh:2057-2072` (`_content is None` → exit 2). `_edit_reconstructed_content`
  (`:2005-2035`) returns `None` on `count == 0` and on `count > 1 and not replace_all`, i.e. exactly
  the two payload shapes the Edit tool itself refuses. Strictly more refusing, nothing permitted
  lost: **fail-closed strengthening, confirmed.**
- `314e0227` is pure addition (+36, no `-` lines), so the delta introduced no further removal or
  weakening for direction one to enumerate.

## Direction two — nothing newly refused beyond disclosure: **paired, and true**

- The new branch is paired at `:33` with `uniquely reconstructable state Edit remains allowed` plus
  the digest-append and handoff Edit controls. **All verified green by me at the pin** (probe over
  the pinned test module, in-place tree byte-identical to `154ff2a0` for `tests/` and `.claude/`):
  `uniquely reconstructable state Edit remains allowed` ok; `digest Edit append repair remains
  allowed` ok (5/5 in `run_bug1305_digest_repair_cases`); the six new cases ok
  (`digest|handoff × absent-prior|unmatched|omp file-path-only`). 21 + 6 = the 27/27 marker count
  main measured at the seam.
- **Re-verified, not carried forward:** pair 3 `digest Edit append repair remains allowed` is the
  **Edit** route and exits 0 at `154ff2a0`. The signed permit set is intact.
- **Handoff arm measured directly** (no in-suite PRE permit control exists): a unique, reconstructable
  handoff PRE-Edit that keeps the note valid **exits 0**; the same target with an omp path-only
  payload exits 2. So the rule is genuinely candidate-bytes-based, not a path ban — the note's
  characterisation at `:33` is true.
- **The omp consequence is named, but not sized.** `:33` names "OMP's path-only Edit payload" and the
  Write route. It does not say that on this host *every* Edit payload is path-only, so *every*
  governed Edit refuses here; the closing "rather than a blanket path denial" reads narrower than the
  host reality. SC-07 never requires that quantification → advisory (F-02), not gating.
- **Citation rot corrected and correct.** All three cited names resolve at the pin: `run_uid is a
  legal checkpoint key beside identity witness` (1), `digest Write append remains allowed` (2) and
  `... beside identity witness` (1) in `test-check-domain.py`; `located compliant digest passes` and
  `unresolvable artifact lookup still fails open` in `test-validate-digest.py` (`:22`, correct file).
- Section BLUF `:27` — "foreign writers still cannot mutate an already minted run without its durable
  identity. In addition, an Edit … that cannot be reconstructed now fails closed" — **is true at the
  pin.** The false `:27` c3 found is gone.

## Does the feature break a live path? **No — bounded search, named**

Nothing in the harness reaches for Edit on a run digest or handoff note. `harness-eng-lead.md`,
`harness-product-lead.md`, `harness-validator-lead.md` and `harness-orchestrator.md` frontmatter grant
`Read Glob Grep Agent Write` (+`Bash` for the orchestrator) — **no `Edit` tool at all**, and those are
the only authors: digest per `harness-team/SKILL.md:214-215` ("write your team digest to
`<run_dir>/digest.md`"), handoff per `harness/SKILL.md:311` ("write the handoff"). A regex for
`Edit` within 120 chars of `digest.md|handoff-*.md|state.yaml` across `.claude/skills` and
`.claude/agents` returned **no matches**. Only the main session holds Edit; on omp its Edit of these
three classes now refuses with a routing message.

## Do the two legs compose or contradict?

They **compose** for a feature that adds no second class of newly-refused-but-previously-permitted
writes — and this feature necessarily adds one, because SC-01(a) demands it and the Advisor ordered
it. A BLUF that merely omitted the fact (keeping bullet `:33`) would satisfy direction two's pairing
and not fire the leg. So the criterion is meetable **only by under-reporting**. Graded as
**criterion unmeetable as written without falsifying the record** (rule 15). Resolution is the
operator's: widen SC-07's carve-out to include the reconstruction-`None` class, or accept `not_met`
on the record. Both are outside DEC-174's no-edit cycle and outside any cycle that exists.

## Criteria not re-checked, one line each

The delta touches exactly two files: `tests/integration/test-check-domain.py` (`314e0227`) and this
note (`1155f188`). `check-domain.sh`, `bash-write-guard.sh`, `check-state.sh`, `validate-digest.py`
and every other test file are byte-unchanged across `5ed929bd..154ff2a0`.

- SC-02, SC-03, SC-09 — rest on `check-state.sh` + `test-check-state.py`, both untouched by the delta.
- SC-04 — rests on `validate-digest.py` + its test file, both untouched.
- SC-10 — POST minting path and `run_identity.py` untouched.
- SC-11 — grades `probe-notebookedit-BUG-1305.md`, untouched.
- SC-08, SC-12 — retired at signature, not graded.

## Findings, classified

- **F-01 — gating, SC-07. ADVISOR-bound, not delta-scoped.** SC-07's final leg vs SC-01(a) + the
  cycle-13 ruling. No builder remedy exists; needs an operator amendment or an accepted `not_met`.
- **F-02 — advisory, delta-scoped.** `:33` names the omp payload but not its blast radius on this
  host (all governed Edits). One clause would fix it; no cycle to spend.
- **F-03 — advisory.** The handoff arm has **no in-suite PRE permit control**; the note's
  "valid-handoff Edit control" resolves to `handoff edit with Done when`, a **PostToolUse** case that
  never reaches the PRE branch. I measured the permit myself; the suite cannot.
- **F-04 — advisory, provenance.** `## Suite results` (`:37-40`) predates the six new cases (46 files,
  cycle-10/12 timings). Records exit 0 / 0 FAIL, so no leg fires, but it is not a pin measurement.
- **F-05 — advisory, carried unchanged.** `check-domain.sh:1240` — outside the delta (my c3 F-03).

## Tree state

`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber status --porcelain`, verbatim:

Before I wrote anything, and throughout every grading read, it produced **no output at all** (empty).
After writing this note, verbatim:

```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c4.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c4.md
?? .harness/harness/features/BUG-1305-run-state-clobber/observations/harness-qa.md
```

The first entry is this note. The other two belong to the concurrent validator squad verifying the
panel's F-1 — I neither read nor touched them. No tracked file is modified. HEAD is `7ad4f42b`, past
the pin; `git diff 154ff2a0 -- tests/ .claude/` is empty, so every script and test I executed is
byte-identical to the pin. Both probe drivers live under `/tmp`. I wrote only this note and my
observations log; no code, test, `plan.yaml`, `BRIEF.md` or run directory was touched, and no ref
moved.

## Open questions

- **Q1 (blocking SC-07, operator-only):** widen SC-07's disclosure carve-out to cover the
  Advisor-ordered reconstruction-`None` refusal, or ship with SC-07 `not_met` and the record intact?
  No cycle can decide this and no note edit can green it.
