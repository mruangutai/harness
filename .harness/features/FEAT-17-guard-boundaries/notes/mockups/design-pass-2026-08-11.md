# Design pass — FEAT-17 guard boundaries — 2026-08-11

**Ruling: no prototype, no `DESIGN.md`. The stderr and `check-state.sh` verdict text is NOT a design
surface I own.** Three advisory notes on the refusal wording follow; none block.

## 1. The user-facing surface, precisely

I looked for a rendered surface and found none. Every task in `plan.yaml` writes to
`.claude/skills/harness/bin/*` or `docs/harness/*`: two `PreToolUse` hook scripts, one new importable
module, one state gate, their test files, and a decisions entry. Nothing renders. Nothing is
operated.

Three surfaces a human can read exist, and I ruled on each rather than on the feature's category:

| Surface | Where | Ruling |
|---|---|---|
| Write-route refusal stderr | T-02 verdict; `check-domain.sh` | not mine |
| Bash-route refusal stderr | T-03, T-04 verdicts; `bash-write-guard.sh` | not mine |
| `check-state.sh` INV-25 line at session entry | T-05 | not mine — and it is the most human-read of the three, which is why I name it: the dispatch did not |

## 2. Why that text is not my contract — stated so it can be argued with

The disagreement is available: refusal-message ergonomics *is* design work, and a bad refusal costs
an agent a whole loop. I am not denying that. I am denying that a `DESIGN.md` is the right home for
it, on two grounds.

- **My contract's vocabulary has no applicable values.** Palette, type scale, spacing, component
  direction, light/dark — every field resolves to nothing on a stderr line. A contract of mine here
  would contain only message-wording rules, which is not the artifact `ui-reviewer` mode A grades.
- **Those wording rules already exist, in the file, as executable convention.** The actionable
  rejection pattern is `check-domain.sh` at the `ACTIONABLE REJECTION (DEC-100b)` comment: name the
  refused path, then always print what the agent MAY write, then name the file that would grant it.
  `select_base`'s workspace refusal follows the same shape. Restating it in a `DESIGN.md` creates a
  **second authority for one rule** — which is precisely the defect class this feature exists to
  kill (REQ-05, one implementation behind both routes). I will not install the disease in the cure.

`DESIGN.md` is therefore `n/a` under DEC-173, not deferred. An empty or pro-forma one would be
graded as if it were meant, and it would be worse than its absence.

**Prototype: not required.** A prototype exists to let the user judge an experience before it is
built. There is no experience to operate here — no screen, no control, no flow. The equivalent
judgement is already made and already stronger: SC-01 asserts the literal string `.claude/worktrees`
in stderr, and SC-04/SC-08 assert exact exit codes with paired allows. Test assertions on verdict
text beat a mockup of it.

## 3. Advisory notes on the refusal wording (non-blocking)

**A-01 — the root-side verdict must not reuse the target-side wording, and must name the ROOT.**
T-03 says the root-side check denies "with the same verdict wording"; T-02 sets that wording to
`<path> is inside a git worktree…` plus "remove the tree with `git worktree remove` rather than
write into it". Two different situations with two different next actions. Target-side: you wrote
into a stray tree from a sound session — stop writing there. Root-side: your **whole session** is
misrooted, and *every* governed write will now be refused. Two costs, both real:

- If the message names the *target*, the agent reads the target as the fault and retries with a
  different path — refused again, indefinitely.
- "Remove it with `git worktree remove`" is followable from inside but is the wrong instruction
  mid-session. **Measured** just now (`git worktree remove .` from inside a linked worktree):
  exit `0`, the removal succeeds, and it deletes the directory the session is standing in.

Suggested root-side third line instead: start a session from `<owner_root>`, or from a checkout
under `<owner_root>/.claude/worktrees/`; remove this tree from there.

**A-02 — T-04's undeterminable-destination case should say what actually happened.** The plan
refuses an unparsed `git worktree add` "for the same reason" as a relative destination, i.e. with a
verdict saying an absolute path under `.claude/worktrees/` is required. An agent that already passed
an absolute path will re-issue the same command and be refused twice. That case should say the
destination could not be determined from the command, and name the parsed form that works.

**A-03 — cosmetic.** Every existing verdict prints `BLOCKED — ` with an em dash (U+2014);
`plan.yaml` spells the new ones with a hyphen. No test greps the dash. Worth one keystroke of care,
nothing more.

Hook naming is already handled — T-01 constraint 3 parameterises the label so a second caller cannot
print a verdict naming the wrong hook. No finding there.

## Open questions

- Q1 (non-blocking): none of the above blocks. If the user disagrees with the decline and wants a
  prototype of the refusal text, the cheap form is a fixture that prints the three new verdicts
  verbatim — not a `DESIGN.md`.
