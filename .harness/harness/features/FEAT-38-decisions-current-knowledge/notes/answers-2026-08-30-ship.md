# Operator answers — FEAT-38 ship decision — 2026-08-30

Written by the main session at branch tip `2f991ba`, `review_sha` `635cd3ba`.

## Q1 — SC-13: THE OPERATOR IS RUNNING THE UAT

Not waived, not recorded retroactively. `notes/uat-FEAT-38.md` is repointed at `635cd3ba` and the
operator is running it now. The ship decision waits on their `result:` text and `status:`.

**A main-session error is the reason this was ever in doubt, and it is recorded here rather than
quietly fixed.** The operator answered "Not run yet" when asked about the UAT during the plan phase.
The main session then wrote *"SC-13's UAT judgement STANDS and is not re-run"* into
`notes/answers-2026-08-29-24.md`, and that claim propagated into TWO signature blocks in `plan.yaml`
and `BRIEF.md`. It asserted a judgement that had never been made, immediately after being told it
had not been made. No automated gate could have caught it: the claim lived in operator-authored
prose, which nothing grades.

The ship orchestrator caught it by reading the UAT file rather than trusting the premise in its own
dispatch, refused to backdate the judgement, and corrected `STATE.md` instead of repeating the claim.
That is the correct behaviour and it is worth keeping.

**Ruling 6's stated void condition did NOT fire**, verified: T-27 touched no prose. Prose sequences
are identical at 5067 lines each side; 20 lines removed = 11 markers + 9 blank lines; zero
insertions. Across the pin gap DEC-138 and DEC-174 are byte-identical and DEC-181 lost only 3 markers
and 2 blanks. So the folded text the operator judges now is the text the criterion is about.

## Q2 — backlog: KEEP EXACTLY THREE, THE PLATFORM DEFECTS

Of B-1..B-39, only these three become issues on ship acceptance. **Every other live row is struck and
dies with the feature**, including rows carried since the first briefing.

- **B-25 — `bash-write-guard.sh` diverges from `check-domain.sh`.** The write guard cannot expand
  shell variables and does not track `cd`; `check-domain.sh --resolve` grants `plan.yaml` to
  `harness-orchestrator` while the write guard denies it. The guard's own comments call such
  divergence a bypass by construction.
- **B-26 — `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`**, in which a line-leading `+`
  pattern matches EVERY line. Four false readings this phase, including 83 apparent insertions
  against a true numstat of 0. Any gate counting diff or suite lines with shell grep on this machine
  is unreliable. This is the widest-reaching of the three: it is not specific to FEAT-38 and it
  silently corrupts measurement rather than failing.
- **B-39 — eight run `digest.md` files fail the DEC-156 lead digest contract**, three from this
  phase. Each lead returned a valid structured result and then wrote a non-conforming file, so
  `SubagentStop` passed the RETURN while the successor-facing ARTIFACT is unusable. The hook
  validates the return, not the file. Not rewritten — inventing another agent's verdict is worse than
  an honest gap.

Struck by this ruling, non-exhaustively: the renderer defects, the WCAG contrast row, the citation
tidy-ups, the verify-block amendments already applied, the run-slug collision (B-24), the stray
main-checkout artifacts (B-35), and the DEC-205 positive-content row (B-28), which the operator's
earlier weakest-sufficient-specification ruling forbids anyway.

Previously struck by the operator and unchanged: B-8, B-9, B-10, B-11.

## Not decided here

- PR and merge. Neither is automatic and neither has been requested.
- Plan-phase Q6..Q10 remain open and gate nothing.
- SC-04's pinned baseline `37` does not reproduce (34/31 observed) while `30` and `24` do. Every
  pattern is 0 at the pin so the criterion's intent is met; it was reported rather than passed
  silently (B-33) and is struck as a backlog row by the ruling above.
