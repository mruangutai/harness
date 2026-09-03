# Ship review — FEAT-54 handoff `## Done when`

**Recommendation: ship, after you run one ~25-minute hand test.**

Every gate this feature can pass has passed. The adversarial panel returned PASS with nothing to
fix, and the product goal-check confirms 14 of 15 success criteria met. The fifteenth, SC-10, is
`verify: uat` — it is your judgment by design, and no agent may grade it. Its script is written and
waiting at `notes/uat-FEAT-54-SC-10.md`.

Two things deserve your attention before you decide, and neither blocks: the feature ships a gate
that cannot detect the exact defect the feature's own notes committed twice (B-1), and I measured a
second, separate way that gate can pass without looking at anything (B-2).

## How this briefing was assembled

**No report round was spawned.** I read the run records off disk rather than asking three leads to
re-narrate files I can open. The phases I did not run are reported from the handoff notes their own
orchestrators wrote while holding the context, plus the digests those notes cite:

- `notes/handoff-plan.md`, `notes/handoff-build.md`, `notes/handoff-validate.md`
- `runs/2026-09-03-review-c6-validator/digest.md`
- `runs/2026-09-03-goalcheck-validate-c6-product/digest.md`
- `runs/2026-09-03-review-c5-validator/digest.md`
- `runs/2026-09-02-02-eng/digest.md`
- `notes/research-FEAT-54-goalcheck-validate-c6.md`, `notes/qa-c6.md`,
  `notes/review-harness-code-reviewer-c6.md`, `notes/uat-FEAT-54-SC-10.md`

I did not read all 50 run directories. Where a claim below rests on a measurement, I say who took
it, and I re-took the two that mattered most myself.

## What each phase produced

**Plan** — the plan was amended under c4 and re-signed by you on 2026-09-02. Its adversarial panel
completed with both configured readers plus the product goal-check; four findings survived, all
advisory, maximum severity med, none high, critical or unrated. Recorded in `plan.yaml`'s `panel`
key. Source: `notes/handoff-plan.md`, citing `runs/2026-09-02-c4-validator/digest.md`.

**Build** — all twelve tasks T-01 through T-12 recorded `done`. The QA matrix passed at build exit;
SIMPLIFY ran all four angles and applied one cleanup, deliberately leaving two alternatives
unapplied as advisory. The deliverable is `handoff_done_when.py` (288 lines) plus its wiring into
`check-domain.sh` and `check-state.sh`, the `HANDOFF.md` template, and a manual comprehension probe
held out of the normal suites. Source: `notes/handoff-build.md`, `runs/2026-09-02-02-eng/digest.md`.

**Validate** — six panel cycles, c0 through c6. The last two are the ones that matter. c5 returned
FAIL on exactly two blockers; both are now closed:

- **F-11** — both real FEAT-54 handoff notes cited an approval that was *already satisfied* before
  the note's own next action began, so a successor could check the authority, see it green, and stop
  without doing the work. Repaired main-session-direct, and c6 confirmed the repair at a committed
  SHA by hand-applying the semantic test to all three notes, including `handoff-validate.md`, which
  c5 never scoped.
- **F-04 / SC-04** — the mandated repository-state command exited 1 on an unrelated standing
  worktree. That worktree is gone. **I re-ran the exact command myself** rather than accept the
  report: exit 0, 478 lines, zero refusal lines, zero lines naming `Done when`.

c6 also entered code review **Stage 2 for the first time in this feature** — every earlier cycle
stopped at a failing Stage 1, so until now no quality clearance existed at any commit. It cleared
90 of 90 on the Python risk grade.

## The goal-check

14 of 14 non-UAT criteria met at pinned `dd55b357`. Source:
`notes/research-FEAT-54-goalcheck-validate-c6.md`.

Worth knowing: pm did not simply ratify the panel. It found the panel's SC-04 evidence had been
measured in the main checkout, where this feature's own handoff notes **do not exist**, and
re-derived it in the worktree where they do — 812 lines over a 145-note corpus including all three
FEAT-54 notes, against a baseline of 141 with zero. That is a materially stronger measurement than
the one it replaced, and it is the kind of check that only happens when the goal-check is treated as
an independent read rather than a rubber stamp.

**SC-10 is `pending_uat`.** It asks for four separate judgments from you: that you can write a real
note in the new shape; that the refusal messages are actionable; that the section is worth its lines
against the 60-line budget; and that the template led you to write a `Scope:` naming the immediate
action — with a `Scope:` naming the phase or feature reading as *wrong*. The script elicits all four
separately and walks you into two real refusals so you judge actual message text.

## Open questions

- **Q1 (blocking the ship decision).** SC-10 is unrun. It is the last open criterion and only you can
  close it. `notes/uat-FEAT-54-SC-10.md`, about 25 minutes.
- **Q2 (not blocking).** Whether SC-04's clause naming `notes/review-<reviewer>-*.md` as the audit
  location is discharged by the run being recorded in `notes/qa-c6.md` and the goal-check note
  instead. The substance is recorded twice over; only the filename differs. My read: discharged —
  the clause names a deterministic location so the evidence can be found, and it can be. Yours to
  overrule.

## Escalations resolved without reaching you

- c5's Q1 — whether reviewers should use persona-qualified note names — I answered from the domain
  rules rather than passing it up, and c6 used the canonical names throughout.
- c6's VL-F-01 could have been routed as a fix cycle. It was not, correctly: the only remedy edits
  the gate tree that DEC-174 marks main-session-direct, so a fix cycle would have spent a cycle to
  prove the squad may not touch it. It appears below as B-1 instead.

## Budgets — the run count is over, and that is worth a sentence

**Cycles: 21 of 30.** The hard cap is unexhausted. Both runs in this session used zero send-backs.

**Runs: 48 against an informational budget of 20.** Over by more than double. My read: the runs
earned their place, but not uniformly. The c4/c5/c6 sequence closed two independent high-severity
defects, exposed an external repository-state blocker, and produced the only code-quality clearance
this feature has. The earlier cycles are a weaker story — the plan alone consumed roughly a dozen
runs across four panel rounds before signature. This is a feature about handoff discipline that
needed six validation panels to get its own two handoff notes right, which is either the strongest
possible argument for the feature or a sign the loop is too easy to re-enter. I would not treat the
count as a defect, but it is the honest number.

## Proposed backlog

Strike any row by ID and it dies. **Anything not listed here is lost silently**, so this is the
complete residual set.

| ID | Nature | What |
|---|---|---|
| B-1 | bug | **The shipped gate cannot detect the F-11 defect class.** The old, defective approval pointer resolved clean too — `problems: []` says nothing about whether an authority becomes satisfied only when the action finishes. The closure rests entirely on a hand-applied semantic test. Nothing mechanically stops the next author citing an already-satisfied approval and passing every gate green. Remedy edits the DEC-174 main-session-direct tree. Source: `runs/2026-09-03-review-c6-validator/digest.md` (VL-F-01) |
| B-2 | bug | **`check-domain.sh` fails open on a relative claimed path when cwd is outside the project.** I measured this myself, four arms: absolute path from `/tmp` → exit 2 (correct refusal); **relative path from `/tmp` → exit 0 on a note it never inspected**; relative path from the worktree root → exit 2. Setting `CLAUDE_PROJECT_DIR` does *not* fix it. Cause is `os.path.abspath(path)` resolving against cwd rather than the located root. Latent in production, where the hook's cwd is the project root — but it is a gate that returns green without looking |
| B-3 | bug | SEC-F-08 (med, advisory across c5 and c6): raw repository, model and provider terminal controls remain printable. Non-gating under `gates.review: advisory_unless_high`. Owner harness-dev-ops |
| B-4 | chore | `feature.json` is 336 lines against a 300-line shape budget — purely the 48-entry runs array. It will emit an INV-23 note after merge. The record is data worth keeping; the budget is what needs revisiting for long features |
| B-5 | enhancement | SC-04 is review-time by design: it asserts a repository-state fact at one pin and binds no later commit, and no standing gate replaces it. Consider a permanent detector, or accept as a known residual |
| B-6 | chore | Run ledger and disk disagree. Three run directories are unrecorded in `feature.json` (`2026-09-03-sec-f10-c5-correction-eng`, `2026-09-03-validation-c1-eng`, `2026-09-03-validation-c1-unreadable-eng`) and one ledger entry has no directory (`2026-09-02-goalcheck-c1-product`). Harmless here — the ledger is documented as a floor — but it means run counts are approximate |
| B-7 | chore | The comprehension benchmark's `eval` has `cmd: null`, so the BRIEF's comprehension claim is not mechanically gated. Correctly barred from carrying a criterion under DEC-163; noted so it is not mistaken for coverage |

## What I need from you

1. **Run the UAT** — `notes/uat-FEAT-54-SC-10.md`. It is the only thing standing between this feature
   and done.
2. **Strike any backlog rows** you do not want carried.
3. **Then: ship, fix, re-scope, or stop.**

Merge, PR and worktree removal are yours. I have moved no HEAD, rebased nothing, and opened no pull
request. The branch is 29 ahead of main and 60 behind; that gap is a merge decision, not a
validation one.
