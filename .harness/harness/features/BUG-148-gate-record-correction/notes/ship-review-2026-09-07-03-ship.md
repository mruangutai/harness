# Ship review — BUG-148-gate-record-correction

**Recommendation: ship.** All six success criteria are met. The feature removes a false claim from
two live records: DEC-174 and FEAT-05's `STATE.md` both asserted that
`gen-decisions-index.py --check` was a green gate. It never was — `--check` was not a supported
mode, and before `ffbdbfa1` an unrecognised argument fell through to the *write* path, so the exit 0
that was cited as proof was a regeneration that overwrote exactly the drift a check would have
reported. Both records now state that, in place, dated 2026-09-06. No ruling was rewritten and no
historical artifact was touched.

**Two things you should know before you accept this, both stated rather than smoothed:**

1. **You have not read the text that is now in the authority.** You read FEAT-05's passage and the
   *longer* DEC-174 paragraph at cycle 4, accepted the facts, and sent it back on length alone. The
   shortened paragraph (115 words/10 lines → 88/8) was cleared by `fable-advisor` under your
   standing authorisation, not by you. `notes/uat-BUG-148-sc06-c5.md` records exactly that.
2. **The reviewer panel graded the previous wording.** Its PASS is pinned at `87e6033`; the wording
   fix moved the product diff to `651e60e2`, so no panel run has read the shortened prose. I
   referred this and the advisor ruled **ship without a panel re-run**: the only evidence gap at the
   current pin is *prose truth*, which the panel's own adequacy note says it cannot grade and which
   SC-06 owns. Everything mechanical was re-measured at the new pin. If you want panel eyes on the
   new paragraph anyway, that is one validator dispatch and this briefing is where to say so.

**No report round was spawned.** This briefing was assembled by reading the eleven run digests under
`.harness/harness/features/BUG-148-gate-record-correction/runs/*/digest.md` directly — that is
`2026-09-06-01-product`, `-01-validator`, `-02-product`, `-03-product`, `-04-product`,
`-05-product`, `-06-validator`, `-07-eng`, `-08-validator`, `2026-09-07-01-product` and
`2026-09-07-02-product` — plus `notes/uat-BUG-148-sc06-c5.md`,
`notes/research-BUG-148-goalcheck-delivery-c5.md` and
`notes/qa-digest-repair-verification-2026-09-07.md`.

## Success criteria — all six met

Graded by pm at `review_sha` `651e60e2`, each by its own declared method
(`notes/research-BUG-148-goalcheck-delivery-c5.md`). The pin has since moved to `ead8eb21` to carry
that evidence; the diff between the two over the three product paths is empty.

| SC | Method | Verdict | Evidence |
|---|---|---|---|
| SC-01 | inspection | **met** | `"Every gate was green"` absent from the `## DEC-174`..`## DEC-175` region; the four required facts each grepped separately, each present |
| SC-02 | inspection | **met** | FEAT-05 `STATE.md` reads `Three gates green:`; all five required facts present separately, including the 2026-09-06 correction date |
| SC-03 | inspection | **met** | one hunk, wholly inside DEC-174's evidence paragraph; heading, defect bullets and carve-out table appear only as context |
| SC-04 | automated | **met** | `run-unit-tests.sh --kind integration` exit **0**, **0** `FAIL` lines, both named index tests `ok` |
| SC-05 | inspection | **met** | outside this feature's own directory, exactly the three allowed paths changed |
| SC-06 | uat | **met** | split attribution — see point 1 above |

## What each squad did

- **Product** (7 runs, digests as listed). Wrote and twice repaired the plan
  (`2026-09-06-01`, `-02-product`), transcribed the plan panel's five findings into `plan.yaml`
  (`-03-product`), applied your four signature rulings (`-04-product`), landed the DEC-174
  correction (`-05-product`), shortened it on your send-back (`2026-09-07-01-product`), and ran the
  delivery goal-check (`2026-09-07-02-product`). All PASS.
- **Validation** (3 runs). Plan panel confirmed the correction's load-bearing 2026-08-03 write-path
  claim *at source*, independently, by both readers — the correction writes truth, not a different
  guess (`2026-09-06-01-validator`). The QA gate passed on the docs-only change and, importantly,
  proved SC-04's index test actually discriminates rather than merely reporting green
  (`-06-validator`). The reviewer panel ran four reviewers, skipped none, and returned zero blocking
  findings (`-08-validator`).
- **Engineering** (1 run). The simplify pass was an **empty pass** — three angles looked and
  declined; altitude's single finding would have reversed a plan instruction you approved, so it
  became a briefing row instead of an edit (`2026-09-06-07-eng`). Nothing was invented to justify
  the step.

## Budget

`cycles_used` **5** of 10 · `len(runs)` **11** of 20. Both under budget; nothing to flag. The five
cycles are all yours or the panel's: two plan repairs, the panel record, your four rulings, and your
length send-back. No fix loop ran twice on the same fault.

## Resolved escalations

- **SIMPLIFY altitude, on FEAT-05's bold `Corrected 2026-09-06 under BUG-148:` lead-in** — resolved
  at rung 1 against BRIEF REQ-01, which positively requires the date, and carried into SC-06's read
  rather than pre-decided. Cleared there.
- **Panel PASS pinned at superseded prose** — referred to `fable-advisor`, ruled ship. See point 2.
- **The untracked QA verification note** — referred; ruled commit-under-a-corrected-name. It is now
  `notes/qa-digest-repair-verification-2026-09-07.md`; the `c1` suffix went because no cycle 1 ran.
- **Whether to file the backlog rows below at merge** — referred; ruled **file none**. Your row-level
  veto is not consumed by your advance authorisation of the ship phase.

## Proposed backlog

**No issue has been filed for any of these.** Filing happens mechanically at your acceptance, so
strike any row by ID and the rest are created for you. **Unstruck rows become backlog issues;
anything not listed here dies silently.**

| ID | Nature | Row |
|---|---|---|
| B-1 | chore | REQ-04's *"no historical artifact is modified"* had no criterion grading it. It holds on measurement, but a BRIEF of this shape should state it as its own SC or carve the feature's own directory out of the allowlist |
| B-2 | chore | Of SC-04's two named tests only `test_committed_index_matches_a_fresh_regeneration` was ever proven red-capable; `test_no_amendment_construct_survives_in_the_authority` has only ever been observed green. Perturb it once and record the result |
| B-3 | bug | DEC-153's disposable-worktree perturbation carve-out is unreachable for `harness-qa` on any non-`tests/**` path — both guards deny, and a self-created sibling worktree is refused under DEC-218 claim binding. QA cannot prove red-capability where it matters most |
| B-4 | bug | `harness-digest-dev` forbids `suite: n/a` with `VERDICT: PASS` (DEC-173), but a read-only reviewer dispatch runs no suite. An honest reader has no legal value for the field |
| B-5 | bug | `handoff_done_when.py::_feature_dir` cannot resolve `brief-sc:` or `plan-task:` pointers for a feature whose directory lives only in a worktree — it strips the `.claude/worktrees/<name>/` prefix and rejoins to the main checkout root |
| B-6 | bug | QA subagent wrapper return path: `yield` with null data exits 1 and re-emits. Orthogonal to this feature; worst unfixed consequence is a spurious re-dispatch, not record corruption. **The advisor recommends keeping this row** — but it is a row like any other and your strike outranks that |
| B-7 | chore | Three INV-29 stale worktrees stand for features that already reached a terminal state — `BUG-440-digest-verdict-reconciliation`, `FEAT-55-issue-types-created-work`, `qa-bug440-c3-probe`. They are the only reason `check-state.sh` exits non-zero, and none concerns BUG-148 |

Two plan-panel findings stay open **by design** and are not backlog rows:
`PF-a2df57f48de3e81d49745cfd1adaa20b` (med, accepted-by-design, disclosed in the BRIEF's
*Verification gaps*) and `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` (low, informational). Neither was
ruled on and neither gates.
