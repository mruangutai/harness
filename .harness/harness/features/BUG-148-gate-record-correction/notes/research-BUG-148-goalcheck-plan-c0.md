# Plan goal-check — BUG-148 — does the plan deliver the operator's stated intent?

**Delivers with named gaps.** Graded against the grilling
(`.harness/harness/notes/grilling-gate-record-correction-2026-09-06.md`), not the BRIEF. Every
settled item is delivered by a task. Two gaps gate signature: SC-05 is unmeetable as written
(measured, below), and one settled item — "add a dated note" — is delivered as an in-place rewrite,
which is forced for DECISIONS.md and merely chosen for STATE.md. No re-plan is implied; both are
one-line fixes at signature.

## The settled list, item by item

| Settled (grilling:7-11,17) | Delivered? | Pointer |
|---|---|---|
| Three separate flows; #148 only | yes | `plan.yaml:6` `source_issues: [148]`; BRIEF:125-126 records #201/#206 out of scope; no task names them |
| Live records only; receipts/plans/research/reviews unchanged | yes | REQ-04 (BRIEF:49-50); T-01 intent `plan.yaml:133-134`, T-02 intent `:184-186`; SC-05 is the check (but see F-1) |
| The two live records are FEAT-05 `STATE.md` and DEC-174 | yes | `plan.yaml` `files:` :78-79 and :145; measured at `41c16c7`: `DECISIONS.md:4308` carries "Every gate was green", `FEAT-05.../STATE.md:14-15` carries "All four gates green" |
| Correction = a **dated** note that `--check` did not exist and its apparent success could not verify index drift | **partly — form diverges** | content delivered: REQ-02 (BRIEF:42-45) and both verifies grep `never a supported mode`, `could not prove index drift`. Form: D-01 (`plan.yaml:22-37`) rewrites in place, no note. Dating: T-02 greps `2026-09-06` (`:151`); T-01 does not (`:85-86`). See F-2/F-3 |
| Out of scope: historical feature artifacts; a new index-drift check | yes | no task adds a checker; T-01 only *names* the existing read-only form `--stdout \| diff` (`plan.yaml:116-117`) |

## The divergence — dated note vs in-place rewrite (D-01)

Read at source before judging:

- **DEC-205** (`DECISIONS.md:6320-6323`): "The amendment convention is ended… A correction rewrites
  the entry it corrects; it does not append a dated sub-section beside it." Its own heading scopes
  it — "**This file** states current truth". It governs `DECISIONS.md`, nothing else.
- **`test_no_amendment_construct_survives_in_the_authority`** (`tests/integration/test-gen-decisions-index.py:836-876`):
  opens exactly one file, `gdi.DECISIONS_PATH` (`:844`), which is
  `.harness/harness/docs/DECISIONS.md` (`gen-decisions-index.py:25`). It rejects three token shapes
  only: `^### DEC-N amendment` (`:849`), `^\*\*Amendment` (`:858`), `am\.\d` (`:866`). It says
  nothing about STATE.md, and nothing about a *date* in prose.

(a) **Does the in-place rewrite satisfy the intent?** Substantively yes, formally not exactly. The
operator settled on the *content* of a note ("`--check` did not exist; its apparent success could
not verify index drift") and both tasks carry that content verbatim as grep-enforced phrases. For
DECISIONS.md the appended form is foreclosed by DEC-205:6322-6323 — the plan is right to refuse it.
For STATE.md D-01's stated reason ("barred from a new section by its two-heading vocabulary",
`plan.yaml:34-36`) is true of a **new `## ` section** only: `check-domain.sh:1801-1805` bars
headings outside `## Current`/`## Open Questions`; nothing bars an inline dated sentence *inside*
`## Current`. That option was available, was not recorded as considered — and T-02 in fact lands
close to it: it writes the correction inline, dated 2026-09-06, in place of the false line
(`plan.yaml:166-172`). So the operator's "dated note" is honoured in STATE.md; what is lost there is
only the *appended* shape, and losing it is a choice, not a constraint.

(b) **Is "dated" still honoured?** Split. `2026-09-06` is asserted by T-02's verify (`plan.yaml:151`)
and by SC-02 (BRIEF:65-66). T-01's grep list (`plan.yaml:85-86`) is `never a supported mode`,
`could not prove index drift`, `ffbdbfa1`, `--stdout | diff …` — no `2026-09-06` and **no
`2026-08-03`**. The missing correction date in T-01 is justified: REQ-01 (BRIEF:39-41) scopes it to
the FEAT-05 record, and DEC-205:6325-6327 puts "dated reasoning about how a decision changed" in
`git log --follow`, deliberately, not in the entry. The missing **2026-08-03** is not justified —
REQ-01 requires each correction to name the run it corrects, and that date survives only as prose
instruction ("keep the bold lead-in naming the date", `plan.yaml:101-102`) with nothing asserting it.
That is F-3.

(c) **Does DEC-205 govern FEAT-05's STATE.md?** No — see the heading scope and the test's single
path above. What actually constrains STATE.md is `check-domain.sh:1796-1807` (heading vocabulary +
120-line budget; the file is 165 lines / 7 headings, measured), which forbids a new **section** and
nothing more. D-04 (`plan.yaml:58-66`) is correct about Edit-vs-Write; its heading claim does not
reach an inline note.

(d) **Settled by the signed decision, or needs the operator?** Half and half. The DECISIONS.md half
is settled by DEC-205 and needs no ruling. The STATE.md half is **not** — the operator settled a
form ("add a dated note") and the plan substitutes another for a reason that does not bind there.
Recommendation: **proceed, with one confirmation line at signature** — "STATE.md's correction is
written inline in `## Current`, dated 2026-09-06, replacing the false line rather than appended
beside it." No task change is needed if he agrees.

## Findings

- **F-1 (med) — SC-05 cannot pass as written.** It grades
  `git diff --name-only $(git merge-base origin/main <review_sha>)..<review_sha>` against a
  three-path allowlist (BRIEF:83-86). Measured now: `git merge-base origin/main HEAD` =
  `8bdc2477`, HEAD = `41c16c7`, and that range already lists three foreign paths —
  `BUG-440-…/plan.yaml`, `FEAT-55-…/feature.json`, `FEAT-55-…/plan.yaml` — from three pre-existing
  ship commits (`41c16c73`, `8b301daf`, `8510eac9`). The criterion fails for reasons no task can
  affect. Fix: pin the baseline to `41c16c7` (already the `lanes.resolved_at`, `plan.yaml:9`)
  instead of the merge-base. SC-03 uses the same merge-base but is path-scoped to `DECISIONS.md`,
  which none of those commits touch, so SC-03 stands — measured.
- **F-2 (med) — the D-01 divergence above.** Needs the operator's confirmation line, not a re-plan.
- **F-3 (low) — REQ-01's "names the 2026-08-03 run" is unasserted in T-01.** Add `2026-08-03` to
  T-01's grep list (`plan.yaml:85-86`), as T-02 already does for its own date.
- **F-4 (low) — SC-01/SC-02 measure what T-01/T-02's own verifies already grep.** Same method twice,
  so they add no independent measurement; the only independent grade of the prose is SC-06 (uat).
  Acceptable for prose, but the panel should not read four inspection criteria as four checks.
- **F-5 (info) — SC-04 is a regression guard, not evidence of the correction.** Ran, from the
  worktree at `41c16c7`, pre-correction: `bash .agents/skills/harness/bin/run-unit-tests.sh --kind
  integration` → `EXIT=0`; and directly, `python3 tests/integration/test-gen-decisions-index.py` →
  `ok - test_committed_index_matches_a_fresh_regeneration`,
  `ok - test_no_amendment_construct_survives_in_the_authority`, exit 0. Both already green, as
  BRIEF:78-81 states honestly. It discriminates only on the index-regeneration half (REQ-05).
- **F-6 (info) — two task assertions no REQ asked for.** T-02's `grep -c '^## ' = 7`
  (`plan.yaml:155`) and T-01's mandated exact contiguous phrases (`:104-109`). Both are defensible —
  the first guards REQ-04's unchanged-ness, the second is what makes the verify discriminate — but
  the phrase mandate constrains wording the operator grades at SC-06: a sentence can satisfy every
  grep and still read as an apology. No change recommended; the operator should know the prose is
  partly pinned.

**Nothing promised is unowned.** REQ-01..05 all appear in `traces:` (T-01 all five, `plan.yaml:71`;
T-02 REQ-01..04, `:138`). REQ-05 (index in sync) is owned by T-01, whose `files:` includes
`DECISIONS-INDEX.md` (`:79`) and whose intent mandates the regeneration (`:126-129`). SC-05 is owned
by no task — it is a whole-change constraint carried only by both intents' "edit no other file";
that is the correct shape, but see F-1 for why its command needs re-pinning.

**No file outside this note was created or modified.** `git status --porcelain` reports exactly two
untracked directories — `.harness/harness/features/BUG-148-gate-record-correction/` and
`.harness/harness/notes/` — the same two before and after this check. BRIEF.md
`e0db50b9…` and plan.yaml `e7144a8d…` (sha256) are unchanged.
