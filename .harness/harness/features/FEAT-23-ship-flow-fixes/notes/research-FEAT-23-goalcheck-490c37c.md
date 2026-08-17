# Goal-check — FEAT-23-ship-flow-fixes — pin `490c37c`

## BLUF

**Twelve of thirteen criteria hold; SC-05 does not, and its gap is one small edit to a file the pin
can still absorb cheaply.** Ten are met on evidence re-taken at `490c37c` (not carried from qa's
`83e769b` gate), two are deferred by the BRIEF's own design, and **SC-05 is `not_met`**: the shipped
skill's ALTITUDE section carries no plan-surface / code-surface pair, while the other three angles
each carry one. **The emergent criterion from the simplify pass is genuinely NEW** — no REQ or SC
requires the skill to carry the apply bounds — so it does not gate this feature and reaches the
operator.

## SC verdicts — all thirteen, by each SC's own declared `verify:`

| SC | verify (BRIEF) | verdict | evidence |
|---|---|---|---|
| SC-01 | automated / integration | met | `run-unit-tests.sh --kind integration` rc=0 at `490c37c`; `ok    ship records feature.json status Done` |
| SC-02 | automated / integration | met | same run: `ok    abandon records feature.json status Abandoned`, plus the discriminating `ok    abandon with no milestone but WITH issues still records status Abandoned` (`test-gh-sync.py:729`) |
| SC-03 | automated / integration | met | same run: `ok` on `ship closes the milestone regardless of parent origin`, `ship leaves an adopted parent open`, `ship closes a created parent completed`, `ship --body-file posts once`, `ship without --body-file posts nothing`; `ALL PASSED`, 12/12 scripts |
| SC-04 | uat | **deferred** | `BRIEF.md:149-152` |
| SC-05 | inspection | **not_met** | `.claude/skills/harness-simplify/SKILL.md:79-91` |
| SC-06 | inspection | met | full read of `harness-simplify/SKILL.md`, `harness/SKILL.md:57-76`, `harness-plan.md:10-20` — every path named is in-tree; `code-simplifier` and `/simplify` absent (ci-grep, 0 hits in all three) |
| SC-07 | inspection | met | `harness/SKILL.md`: qa anchor :57 < `SIMPLIFY, the last build step` :59 < pin anchor :75; `harness-plan.md:20` orders `squad plans, … simplify … eng-lead reviews architecture` |
| SC-08 | inspection | met | zero `validator` occurrences in `harness-simplify/SKILL.md`; `grep -ni simplif harness/SKILL.md` returns only :59 and :67, both inside the step region, so no other build-playbook step mentions the pass at all; the region's two `validator` hits are the prohibition ("Never dispatched to the validator lead") and the unrelated INV-6 pin sentence; zero `validator` in `harness-plan.md` |
| SC-09 | inspection | met | `DECISIONS.md:5970` (DEC-195), `:6049` (DEC-196); `gen-decisions-index.py --stdout \| diff -q - DECISIONS-INDEX.md` clean; rows at `DECISIONS-INDEX.md:213-214` |
| SC-10 | automated / unit | met | `run-unit-tests.sh --kind unit` rc=0 at `490c37c`; all seven required labels `PASS` (`unit` log lines 836-843) incl. no-board, outside-root, sync-off, BoardError, non-BoardError, usage exit 2 |
| SC-11 | inspection | met | `harness-plan.md:10` kickoff marker precedes the sequence line :20; names `board-station.py` by path :11; `no ticket is named` :14; `git diff b7ae135 490c37c -- .claude/commands/harness-plan.md` shows the sequence line's only change is the SC-07 simplify insertion, both anchors byte-identical |
| SC-12 | inspection | met | `DECISIONS.md:6053-6060` (rule, cited by symbol), `:6072-6079` (no stations map, names closed issue 350 and that it has no implementing ticket) |
| SC-13 | uat | **deferred** | `BRIEF.md:149-152` |

**On the two deferrals, in the BRIEF's own words** (`BRIEF.md:149-152`): "SC-04 and SC-13 cannot be
met at ship time… Both stay `not_met` until then. That is deliberate, not an oversight." I record
them `deferred` to distinguish design from defect; the BRIEF's own token is `not_met`, and no fix
cycle is warranted for either.

## SC-05 — the one gap, and where it is owned

SC-05 requires the four angles "each present in the shipped skill, **in both their plan-surface and
code-surface forms**". REUSE (:41-44), SIMPLIFICATION (:53-60) and EFFICIENCY (:73-77) each carry an
explicit `On a **plan surface**:` / `On a **code surface**:` pair. **ALTITUDE (:79-91) carries
neither** — its text is surface-agnostic.

The distributive reading is not mine to choose: **T-02's own `intent:` instantiates it** —
"Under each angle, state what it looks for on a plan surface and what it looks for on a code
surface" (`plan.yaml`, T-02 intent). And the source note holds two distinct ALTITUDE prompts, one
per surface (`research-FEAT-23-simplify-angles-source.md:25`, `:53`), so both forms existed to port.

qa recorded SC-05 met; its method was file-global phrase greps for `plan surface` / `code surface`,
which three angles satisfy on their own. That method cannot detect a fourth angle missing both — it
is not corroboration of the verdict.

**Route:** task **T-02**, file `.claude/skills/harness-simplify/SKILL.md`, lane
**main-session-direct** (`plan.yaml` `lanes:` — `check-domain.sh --resolve` returns NOBODY). The
defect is in the skill, not the sentence: two labelled sentences under ALTITUDE make SC-05 true.

## The emergent criterion — **NEW**, not covered

**Measurement, re-derived whitespace-normalised (`re.sub(r'\s+',' ',text)`) over `git show 490c37c:`
for each file — the finding survives normalisation:**

| phrase | `harness-simplify/SKILL.md` | `harness/SKILL.md` | `DECISIONS.md` |
|---|---|---|---|
| `delete or weaken` | **0** | 1 | 1 (`:6002`, inside DEC-195's span 5970-6048) |
| `weaken an assertion` | **0** | 1 | 1 (`:6002`) |
| `backlog row` | **0** | 1 | 1 (`:6004`, inside DEC-195) |
| `ceiling of one` | **0** | 1 | **0** |
| `one fix` | **0** | 2 | **0** |

Case-insensitive counts are identical. `harness-simplify/SKILL.md`'s `## Applying what comes back`
(:93-114) states only that "the suites re-run after the apply". Both bounds live at
`harness/SKILL.md:68-73`. DEC-195 carries the assertion bound and **not** the one-fix ceiling —
confirmed by span, not by file-global count.

**Verdict: NEW.** Tested against the text, not adopted:

- **REQ-05** — "ships inside this repository and can be run without any file, command or plugin that
  lives outside it." Both files are in-tree. The requirement is about *external* dependency; it does
  not say the skill must be self-sufficient of its own playbook. Satisfied on its own words.
- **SC-05** — enumerates the four angles and the source-note citation. Says nothing about apply
  bounds. (Its separate failure above is unrelated to this finding.)
- **SC-06** — external names. Not engaged.
- **SC-08** — validator-lead assignment. Not engaged.
- **T-02's `intent:`** — its "THE DISCIPLINE the skill must state plainly" list covers dispatch
  shape, readers, finding shape, scope, the plan-surface and NOBODY flag-only branches, the
  never-validator rule and the no-external-dependency rule. **Neither apply bound appears.** They
  entered via **T-03's** intent (for `harness/SKILL.md`) and **T-04's** (the assertion bound only,
  for DEC-195).

So no approved REQ, SC or task intent requires it. It changes what "done" means, and therefore does
not gate this pin.

**§4.4 applied explicitly** — `.harness/harness/docs/SPEC.md:720`, "Autonomy is scoped by
reversibility". Its third row: a change that "changes scope, goal, or a `## Decisions` entry" is
**always ask**. Adopting an emergent criterion into an approved, signed BRIEF is exactly that row.
Non-gating, operator's call. (The cross-reference "§4.4's significance rubric" at
`harness/SKILL.md:98` has no target under that name; SPEC §4.4 is a reversibility rubric. Raised as
Q3.)

### Recommendation — fold it in, on SC-05's edit

SC-05 already forces an edit to `.claude/skills/harness-simplify/SKILL.md` and a pin move (unless
the operator rules SC-05's sentence wrong). **Adding both bounds to `## Applying what comes back`
rides that same edit and the same panel round — near-zero marginal cost.** Ship-as-is-plus-backlog
only makes sense if the operator overrules SC-05.

**The remedy spans two ownership regimes and both halves must be sequenced, or it half-lands:**
`.claude/skills/harness-simplify/SKILL.md` and `.claude/skills/harness/SKILL.md` both resolve to
**NOBODY** (main-session-direct); the DEC-195 half is `.harness/harness/docs/DECISIONS.md`, which is
**documentor-owned** (`plan.yaml` `lanes:`). Fixing only the skill leaves DEC-195 restating the
assertion bound free-standing — the exact drift the finding exists to end.

**Concrete cost if left:** an `eng-lead` that loads the skill at the point of use learns neither
bound. It reproduced on this feature's first execution of the step — the dispatch carried both by
hand (`runs/2026-08-17-10-simplify-eng/digest.md`, Q1).

## Provenance of evidence — why I did not carry qa's

qa's gate ran at `83e769b`. `git diff --stat 83e769b 490c37c` shows the simplify apply touched
`board-station.py` and `test-board-station.py` — the source SC-10 rests on. Both suites were
therefore re-run at `490c37c`: **unit rc=0 (16 scripts), integration rc=0 (12 scripts, 106/106
checks)**. qa's note is corroboration, not the pointer.

## Open questions

- **Q1 — SC-05 unmet.** Route T-02 / `harness-simplify/SKILL.md` (main-session-direct) to give
  ALTITUDE its plan-surface and code-surface forms. Blocking.
- **Q2 — D-05's `because:` says `gh-sync.py` takes the feature dir as `argv1`.** It is the second
  positional: `cmd, feat_dir = argv[0], argv[1]` over `sys.argv[1:]` (`gh-sync.py:777`), guarded by
  the usage `die()` at `:772`. **D-05's conclusion is unaffected**, and DEC-196 states the same fact
  by symbol without the ordinal (`DECISIONS.md:6081-6086`), so the record of authority is already
  correct. Only the signed plan prose is off. **Flagged, not edited** — a signed artifact is
  corrected by re-signature, not by me. Non-blocking.
- **Q3 — dangling cross-reference.** `harness/SKILL.md:98` cites "§4.4's significance rubric"; the
  string `significance` occurs nowhere else in `.claude/`, `docs/` or `.harness/harness/docs/`, and
  SPEC §4.4 is titled "Autonomy is scoped by reversibility". Harness-doc defect, not this feature's.
  Non-blocking.
