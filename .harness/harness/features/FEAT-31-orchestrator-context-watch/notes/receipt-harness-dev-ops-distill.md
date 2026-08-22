# Receipt — harness-dev-ops — FEAT-31 distillation

## BLUF

Craft file (`.harness/expertise/harness-dev-ops.md`): Patterns 15→15 (net: -1 merge, +1 add),
Gotchas 14→14 (unchanged). Repository file (`.harness/harness/expertise/harness-dev-ops.md`):
Patterns 1→1 (unchanged), Gotchas 5→5 (net: -1 drop stale, +1 add). `check-expertise.sh` on both
targets: **exit 0**, one pre-existing advisory not introduced by this run.

## Staleness guard

Worktree vs main checkout: both `.harness/expertise/harness-dev-ops.md` and
`.harness/harness/expertise/harness-dev-ops.md` were byte-identical to main before I touched them
(`diff` exit 0 both times) — no stale-base risk.

## Stale-entry check (found one, acted on it)

**Repository G-03 was falsified — measured, not assumed.** It claimed an unregistered
`test-*.py` script is "invisible to [the drift detector], not caught by it." I created a scratch
`test-zzz-scratch-probe.py` in `.claude/skills/harness/bin/` and ran
`run-unit-tests.sh --check-kinds`: it printed `MISCONFIGURED: ... is not in run-unit-tests.sh's
explicit script list` and exited 2 — the opposite of the claim. Additionally, reading the current
`run-unit-tests.sh`, the T-12 KIND-DRIFT cross-check (arrays vs `harness.json`'s
`test_kinds.integration.detect`) now runs on every invocation, closing the other half of the class
G-03 warned about. **Dropped G-03** — deleted (no drop op in the tool; done via direct Edit, see
below). Scratch probe file was removed immediately after the measurement; confirmed via
`git status --porcelain` showing no new untracked file afterward.

## Tooling gap found: expertise-merge.py has no replace/drop/merge op

`harness-distill/SKILL.md` documents `add | replace | merge | drop`, but reading
`expertise-merge.py` end to end: `compute_union` only adds a proposed id if absent, and errors
(exit 7) if the same id already carries different text — there is no code path that removes an
entry or accepts a same-id text change. **Replace, merge, and drop are not executable through the
CLI as documented.** I resolved this locally by using the tool only for genuine adds (P-17,
G-06 — both show `ADDED` with every other id `PRESERVED` in the tool's own output, i.e. no data
lost), and doing the replace/merge/drop text changes as targeted `Edit` calls scoped to the exact
line(s), re-reading the file immediately beforehand each time. This is not raised as a decision
I made unilaterally to route around a rule — it's the only way to execute what the SKILL asked for
given what the tool can do, and I'm flagging it as an `open_question` for the harness owner rather
than quietly treating a workaround as durable.

## Candidates — my judgment, with reasons

- **A (mutation methodology: diff-confirm applied, confirm restore, require isolation) — ACCEPTED.**
  Added as craft Pattern P-17. Strong, repo-agnostic, has a receipt-backed example (`fix1-s2`, four
  independently rebuilt mutants + a fifth isolated one). No existing entry covers this; entered via
  a genuine `add` (Patterns was already at cap 15, so I first freed a slot — see below).

- **B (reconcile two counts by set difference, both directions) — ACCEPTED, merged, not appended.**
  P-09 already stated "prove no case is lost via the ordered SET of ok-line texts" for the
  dead-code-deletion case; B is the same mechanism (identity/set comparison over raw counts) applied
  to a different situation (reconciling two totals). Per distillation guidance an entry citing more
  than one incident is a smell — I generalized P-09's rule to cover both situations rather than add
  a second, narrower entry making the same point twice.

- **C (measure a framing, including your lead's) — ACCEPTED, replaced P-07, not appended.**
  P-07 said: run a gate standalone when a dispatch calls it "risky" without saying whether it
  currently passes. C is the general form of the same instinct — any framing a measurement can
  settle, not only "gate as risk," and explicitly includes the lead's own framing (the `fix1-s2`
  footer-timing receipt is the concrete case: I measured the double-read at ~49% of wall clock
  against the lead's "irrelevant" framing). Replaced P-07's text with C's, same id, since keeping
  both would restate the same lesson at two different generalities.

To make room for A without displacing a fourth entry outright, I merged the two closely related
git-status-evidence patterns P-05 ("record it unfiltered") and P-06 ("re-check it at both ends of
the window in a shared tree") into one entry at P-05 — both describe the same underlying practice
(a git-status capture used as verification evidence should be complete and taken at more than one
point), and merging them freed exactly the slot A needed. This was my own call, not one of the
three relayed candidates, made because Patterns was at its 15-entry cap.

## My own material — the em-dash observation

**Judged repository-tier, not craft.** The test is "true and useful in a repo I've never seen?" —
no: it turns on this repo's specific convention that `budgets` rationale strings in
`.harness/harness.json` use the `—` JSON escape rather than a raw UTF-8 em-dash character, a
fact about one file in one repository. Added as repository Gotcha G-06.

## Accepted-entry counts by source

- Own observations log: 1 accepted (em-dash → repo G-06).
- Own receipts (not relayed by anyone): 1 accepted (T-11's "basename-only comparison hole" was
  read but NOT distilled separately — it's a specific instance of P-14's "resolve to absolute path
  first" family and P-09's identity-comparison family; no new entry needed, already covered in
  spirit by existing rules once P-09 was generalized). The stale-G-03 drop also came from my own
  receipts/observations (T-11's open question about T-12 not having landed yet, re-verified now).
- Lead-relayed candidates: 3 offered (A, B, C), 3 accepted — 1 as a straight `add` (A), 2 as
  `merge`/`replace` onto existing entries (B into P-09, C replacing P-07).
- Rejections: none of A/B/C rejected outright; all three passed the six-spawns test on inspection
  of my own receipts backing them.

## Entry counts before/after

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15 | 15 |
| craft | Gotchas | 14 | 14 |
| repo | Patterns | 1 | 1 |
| repo | Gotchas | 5 | 5 |

## check-expertise.sh — verbatim

```
$ bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:20: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
[... other agents' files, unrelated, not mine to fix ...]
EXIT=0

$ bash .claude/skills/harness/bin/check-expertise.sh .harness/harness/expertise/harness-dev-ops.md
OK   .harness/harness/expertise/harness-dev-ops.md
EXIT=0
```
The `G-03` advisory above is the craft file's pre-existing `declare -A` gotcha (unrelated to the
repository-tier `G-03` I dropped, which lived in a different file and had a different id-collision
by coincidence only) — pre-existing before this run, not introduced by it, advisory not a
violation, not mine to act on unilaterally.

## Open questions

- Q1: `expertise-merge.py apply` does not implement `replace`/`merge`/`drop` — only pure
  same-id-absent adds succeed; a same-id text change always hits the exit-7 conflict path with no
  resolution mechanism, and there is no removal path at all. Every distillation that needs to
  condense at a section cap (explicitly required by `harness-distill/SKILL.md`: "condense until you
  are under it") currently has no CLI-only way to do so. Not blocking (I resolved it via scoped
  `Edit` calls, minimizing the DEC-125 race by re-reading immediately before each edit), but the
  gap should close before another close-out hits a full section and does something less careful.
  `blocking: false`.
