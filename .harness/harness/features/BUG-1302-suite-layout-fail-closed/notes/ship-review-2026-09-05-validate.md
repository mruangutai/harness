# Ship review — BUG-1302-suite-layout-fail-closed — validation complete

**Recommendation: SHIP.** Validation passes at the pinned `review_sha` (now
`d5dbb9dab31853eaa65823aaec752724ce98bc91`; the code under review is byte-identical to the original
pin `ac8dd671`) with zero gating findings. All ten success criteria are met, the qa test-matrix hard
gate passes, the four-seat review panel returned PASS with `must_fix: []` and `severity_max: low`,
and `check-state.sh` now exits 0 with **zero violations tree-wide**. Nothing is merged, PR'd or
shipped; that decision is yours.

**The thing that makes this verdict worth trusting** is not that the suites are green — they were
green before the feature too. It is that every one of the five fixes was **mutation-proven to
discriminate the defect it names**. qa reintroduced each original defect in a disposable probe
worktree at the pin and watched the specific new check go red, then reverted. The two DEC-174 files
were byte-identical to the pin before validation and byte-identical after it (`git diff ac8dd671 --
tests/` is empty), so nothing in the reviewed tree was disturbed to obtain that evidence.

## What was fixed, and what proves it

| Row | Fix | Does the evidence discriminate? |
|---|---|---|
| B-4 | tautological conjunct removed from `_literal_key_present` | **Yes** — but only the structural AST pin fires. The behavioural corpus stays PASS with the dead code restored, because dead code is invisible to every input. That is expected, not a gap |
| B-5 | unreachable `".."` comparison removed from `_is_inside_tests` | **Yes**, same shape — structural pin fires, corpus cannot |
| B-6 | case 11's fail-open `INAPPLICABLE` print became a hard failure naming both remedies | **Yes**, three independent mutants all reddened, including the two the criterion names |
| B-14 | `_violations_callers` reports unreadable tracked sources instead of raising | **Yes** — the unguarded form reddens with the literal `UnicodeDecodeError` text |
| B-8 | integration case 2 widened to reject either sentinel | **Yes**, and this is the strong one: against an identical mutated runner the widened clause reddens and the old narrow clause falsely passes |

Independent of the panel, the orchestrator confirmed the suite now **discovers more, not less**:
`check(` call sites in the unit file went 39 → 48, and no pre-existing named check disappeared.

## Where the verdict came from

**No report round was spawned.** This briefing was assembled by reading the run digests already on
disk (DEC-69). The files read, all under
`.harness/harness/features/BUG-1302-suite-layout-fail-closed/`:

- `runs/2026-09-05-1-validator/digest.md` — Advisor: DEC-174 binds both test files (RULING); B-6 remedy (a) (recommendation)
- `runs/2026-09-05-2-validator/digest.md` — same ruling, recorded with its evidence paragraph
- `runs/2026-09-05-2-product/digest.md` — plan goal-check FAIL: three BRIEF defects before signature
- `runs/2026-09-05-3-product/digest.md`, `runs/2026-09-05-4-product/digest.md` — BRIEF and plan drafted, then all 12 findings applied
- `runs/2026-09-05-3-validator/digest.md`, `runs/2026-09-05-4-validator/digest.md` — plan panel, cycle 1, `severity_max: med`, `must_fix` empty
- `runs/2026-09-05-1-eng/digest.md`, `runs/2026-09-05-2-eng/digest.md` — four-angle pass and architecture review of the plan draft
- `runs/2026-09-05-5-product/digest.md` — all four panel findings resolved and transcribed
- `runs/2026-09-05-6-validator/digest.md` — **the review panel at the pin: PASS, must_fix empty**
- `runs/2026-09-05-6-product/digest.md`, `runs/2026-09-05-7-product/digest.md` — goal-check, then SC-06 re-graded to met
- `notes/qa-2026-09-05-6.md` — the mutation evidence the whole verdict rests on

The build phase left no run digest: it was main-session-direct under DEC-174, so `runs:` records no
eng run for T-01..T-05. Its evidence is `notes/handoff-build.md` and
`notes/red-demonstrations-2026-09-05.md`.

## Budget

Cycles 4 of 8 — three from the plan phase, one from this phase (SC-06 was returned to pm for
re-grading once the qa evidence surfaced). Runs 13 of 20. Neither budget is near its bound and no
crossing needs surfacing.

## Two things you should know before you sign

1. **B-6's residual blind spot is real and is the price of the chosen remedy.** A well-formed
   `test_kinds` change that blinds the gate to a genuine offending path is caught by neither the
   positive control nor the hygiene certification. BRIEF.md records this; the panel found nothing
   that narrows it. The compensating control certifies detect-pattern *shape*, never a live path
   through `offenders()`.
2. **Two of the four panel seats reached PASS by reading, not by falsification.** Security and UI
   both declined-after-looking rather than being skipped, which is the correct outcome for this
   surface, but it means the panel's discriminating power came almost entirely from qa's mutants and
   the code reviewer's base-vs-pin re-derivation. A clean panel is not by itself proof of a clean
   diff.

## What this run repaired along the way

Four state defects against this feature were open when validation began and all four are now closed:
the INV-32 `goalcheck` reader was never transcribed into `plan.yaml`'s panel record; `handoff-build.md`
did not satisfy the DEC-159 shape gate; run `2026-09-05-5-product` was orphaned on disk and unrecorded
in `feature.json`; and `runs/2026-09-05-1-eng/digest.md` carried no contract block. Re-pinning
`review_sha` past the plan.yaml write closed the INV-33 staleness that repairing the first one caused.

## Proposed backlog

Unstruck rows become issues on ship acceptance. **Anything not listed here dies silently.**

| ID | Nature | Row |
|---|---|---|
| B-1 | bug | `sole_implementations()` handles the same two hazards T-04 just fixed by **silently skipping** them — a tracked-then-deleted `.py` drops out of the sole-implementation sweep with no signal. After this feature the one file holds two opposite policies for one hazard class. Ruled out of scope here; it is a genuine fail-open of B-6's own class |
| B-2 | chore | A lead can write a digest with no contract block and never learn: the eng lead stated in `runs/2026-09-05-1-eng/digest.md` that the structured DIGEST "is in the DIGEST returned to the orchestrator", so it deliberately omitted it from the file. Nothing at write time contradicted that, and only `check-state.sh` caught it later. Repaired here by appending (a Write that REPLACES a recorded digest is refused; one that EXTENDS it is allowed), but the doctrine gap that produced it is untouched |
| B-3 | bug | `plan-merge.py apply` cannot write `panel.readers` — `UNION_KEYS` is `(tasks, decisions)` only, so `panel` falls to whole-value equality and exits 7 CONFLICT. The working verb is `set-panel`. Any instruction that mandates `apply` for a panel edit is unsatisfiable |
| B-4 | bug | Handoff authority pointers `brief-sc:` and `plan-task:` cannot resolve for a feature living in a worktree: `handoff_done_when.py` derives the feature dir and reads it against the **main checkout** root, where the feature directory does not exist. Only `approval:` and `finding:`, which carry an explicit path, work from a worktree |
| B-5 | bug | A subagent job exits 1 with `Subagent called yield with null data` while emitting a complete, conformant fenced return whose artifact is present and correct on disk. Observed twice in this feature (pm in `5-product`, code-reviewer in `6-validator`). Routing on job status alone would discard valid PASSes |
| B-6 | chore | `notes/red-demonstrations-2026-09-05.md` carries no cross-reference to the two SC-06 mutation transcripts, which live in `notes/qa-2026-09-05-6.md`. A reader following SC-06's literal wording finds only the one fail-open FAIL line. One line fixes it |
| B-7 | chore | BRIEF SC-08's prose calls the two surviving `"PASS test-" not in p.stdout` occurrences "cases 2 and 4". Measured, they are at `:93` and `:121`, and `:121` is the *git enumeration failure* case. SC-08's actual pin — narrow clause absent, generic count exactly 2 — holds; only the prose anchor is wrong |
| B-8 | enhancement | DEC-174's enumeration still does not name `run-unit-tests.sh`, so its carve-out over both gate test files rests on an Advisor ruling by category rather than on the text. An explicit non-goal of this feature; amending it is your call |

## Next steps, and who owns them

Everything below is **yours or the main session's** — no squad can perform any of it.

1. **Merge the branch.** `feat/BUG-1302-suite-layout-fail-closed`. GitHub milestone 46, parent issue
   **#1311**, sub-issues **#1312–#1316** (T-01..T-05), source issue **#1302**. All six cards are at
   the `review` station.
2. **`gh-sync.py ship`** from the **main checkout**, not this worktree — it refuses at exit 1 when
   the feature directory resolves inside `.claude/worktrees/`. Pass `--body-file` pointing at this
   note so the briefing posts on #1311.
3. **File the unstruck backlog rows** above as issues, mapping each `nature` onto `bug`, `chore` or
   `enhancement` and prefixing every title with its row id.
4. **Let the `post-merge` hook remove this worktree.** Do not remove it from inside; `check-state.sh`
   INV-29 refuses while a worktree stands for a feature that reached a terminal state.
