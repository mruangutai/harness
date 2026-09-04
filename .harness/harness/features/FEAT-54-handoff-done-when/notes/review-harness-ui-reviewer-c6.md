# UI/user-surface review c6 — FEAT-54 handoff Done when

## BLUF

**PASS.** At pinned `review_sha = dd55b3570c6a20f5ca1da016d6959752bd0ffc74`, the four text surfaces
in this role's remit — `handoff_done_when.py`'s refusal messages, `check-domain.sh`'s write-gate
wrapper text, `check-state.sh`'s persisted-report text, and `templates/HANDOFF.md` — are **byte-identical**
to the bytes c5's ui-reviewer already audited and passed clean (`git diff 4690f724..dd55b357` over
those four paths returns 0 lines). No new gating UI/message defect exists at this pin. F-04 (literal
SC-04 exit code) is out of this lens per this dispatch's explicit instruction — QA's lane, not
re-imported here. F-11 (already-satisfied authority) is a content-authoring correctness question
that belongs to code-review's Stage 1 lane, not a message-actionability defect; from my lens I traced
the repaired pointers through the unchanged resolver and confirm they are well-formed and produce no
new refusal, so the fix introduces no message-actionability regression. SEC-F-08 (med, raw terminal
controls) is carried forward unchanged and remains security's advisory, non-gating in this run.

## Method — what I actually checked at this pin, not what I assumed

1. **Byte-identity census (measured, not predicted).** `git diff 4690f724 dd55b357 -- \
   .claude/skills/harness/templates/HANDOFF.md .claude/skills/harness/bin/check-domain.sh \
   .claude/skills/harness/bin/check-state.sh .claude/skills/harness/bin/handoff_done_when.py`
   returns **0 lines**. c5's pin (`4690f724`) is the SHA c5's ui-reviewer audited exhaustively and
   passed with no gating UI defect (`notes/review-harness-ui-reviewer-c5.md`). Since none of the
   four message-emitting/template files changed between c5's pin and this one, that clean result
   carries forward rather than needing re-derivation from scratch (O-07).
2. **Direct read of `handoff_done_when.py` at `dd55b357`** (full file, `git show dd55b357:<path>`):
   confirmed unchanged — `LEGAL_PREFIXES = ("plan-task:", "brief-sc:", "finding:", "approval:")`
   (4 types, satisfying SC-13's "four legal prefixes" requirement); `_unknown()` names the pointer
   value and lists all four legal prefixes; `_unresolved()` names the pointer, the target file, and
   the specific detail (missing task id / SC id / finding token / heading); `_scope_problems` and
   `_authority_count_problems` name the actual count that broke the rule (SC-02); `_message()`
   appends "follow templates/HANDOFF.md" to every message (SC-01's "names ... the template").
3. **Direct read of `check-domain.sh:1546-1569`** at the pin: identical to the lines c5 cited
   (`1547-1569`) — cap message names the actual line count and the 60 cap; missing-section message
   names the missing headings and points to `templates/HANDOFF.md`; both wrap
   `handoff_done_when.problems(..., resolve=True)` and fail closed on import/exec failure with an
   explicit "REFUSING the write" message.
4. **Direct read of `check-state.sh:1195-1264`** at the pin: identical to what c5 cited
   (`1211-1264`) — the persisted report calls `handoff_done_when.problems(..., resolve=False)` (a
   grammar check only, per SC-15's contract that the corpus scan never re-resolves targets), and
   composes a single `bad.append(...)` line per note naming the feature, the note filename, and every
   concrete reason (missing sections / cap / empty sections / grammar problems).
5. **F-11 repair traced against the unchanged resolver, by hand (write access to run the parser
   directly is denied to this read-only role, so this is static trace, not execution):**
   - `notes/handoff-plan.md` Authority is now `plan-task:T-01.verify` (previously an approval
     pointer). `plan.yaml:143-154` at the pin has `id: T-01` with a non-empty `verify:` block, so
     `_resolve_plan` finds a match — the pointer is well-formed and resolves.
   - `notes/handoff-build.md` Authority is now `brief-sc:SC-04`. `BRIEF.md` at the pin has a line
     `- SC-04: The state check run ...`, so `_resolve_brief` finds the criterion — well-formed and
     resolves.
   - `notes/handoff-validate.md` carries `brief-sc:SC-04` (same) plus
     `finding:.../review-harness-code-reviewer-c5.md#F-04`; that note contains the literal token
     `F-04` (heading `### F-04 — high, must-fix — literal SC-04 exits 1`), so `_resolve_finding`
     finds it — well-formed and resolves.
   - All three notes are within the 60-line cap at this pin (54, 38, 46 lines respectively,
     `git show dd55b357:<path> | wc -l`).
   None of these three pointers is the old "already-satisfied approval heading" shape flagged by
   F-11 at c5; each now names a criterion, task, or finding a successor can independently check
   against live state rather than a heading that was true from the moment `BRIEF.md` was signed.
   Whether citing *these particular* pointers is the semantically correct authority for each note's
   stated `## Next` action is a content-correctness judgment for code-review Stage 1, not a
   message-actionability question — I note it only to confirm the repair does not regress this
   lens: no new refusal shape, no new message wording, nothing an author would find newly
   inscrutable.

## Accessibility / theme parity

Not applicable, as at c5: every reviewed surface is plain, non-interactive stdout/stderr/markdown
text. No colour-only state encoding, no ANSI styling introduced, no keyboard/focus/hit-target
surface exists to audit. SEC-F-08 (med, carried forward, unchanged bytes at this pin) is the raw
terminal-control-printability advisory already owned by harness-dev-ops/security under
`advisory_unless_high`; it is not this role's finding to re-file and does not gate this verdict.

## What is explicitly out of this lens

- **F-04** (literal SC-04 command exit code): per this dispatch, QA's lane. Not graded or
  re-imported here.
- **SC-10** (operator UAT judgment of message actionability): `not_run` this cycle, out of scope per
  constraints. My read above (messages name the missing section/count/prefixes/template) is offered
  as input to that later UAT, not a substitute for it.
- **F-11's semantic correctness** (is `plan-task:T-01.verify` / `brief-sc:SC-04` the *right* authority
  for each note's specific next action, beyond "well-formed and resolves"): code-review Stage 1's
  lane. I traced the mechanics only to confirm no new message-actionability regression.

## Verification and limits

Read-only source-and-terminal audit; no write access exercised (role is READ-ONLY by domain grant).
Verified via direct `git show`/`git diff` reads at the pin, not rendered output — appropriate here
since every surface is unstyled batch text with no rendered-pixel dimension to miss.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The four message/template surfaces in this lens are byte-identical to the c5-audited bytes; F-11's repaired authority pointers are well-formed and introduce no new refusal shape; F-04 is QA's lane and not re-graded here."
  mode: B
  in_scope: true
  severity_max: none
  findings: 0
  must_fix: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c6.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c6.md
```
