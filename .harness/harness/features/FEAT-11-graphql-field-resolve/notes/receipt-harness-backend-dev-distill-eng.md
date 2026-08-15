# Receipt — harness-backend-dev — FEAT-11 distill-eng

## BLUF

`.harness/expertise/harness-backend-dev.md` distilled: 4 ops (3 add, 1 replace), none
displacing (no section at cap). `check-expertise.sh` reports `OK` for this file specifically;
the directory-wide invocation exits 1 for reasons entirely outside this domain (see Gate below).

## Sources read

- `notes/receipt-harness-backend-dev-T-01-c0.md`
- `notes/receipt-harness-backend-dev-MF-1-c1.md`
- `notes/receipt-harness-backend-dev-MF-2-c2.md`
- `runs/mf1-eng/digest.md` (full file, not just cited lines)
- `runs/mf2-eng/digest.md` (full file, not just cited lines)
- No `observations/harness-backend-dev.md` exists for this feature — confirmed absent, matches
  the dispatch's claim.

## The three relayed candidates

**(a) ACCEPTED as `P-09` (add).** `runs/mf1-eng/digest.md:77-83` states two clauses: (1) a
value-slot assertion must use a value absent from the message's fixed prose, (2) messages
cross-compared for inequality must share the same value. They constrain each other — clause 2
only matters because clause 1's fix has to be applied consistently across every case in a
cross-comparison, or the inequality passes on the value rather than the wording. Distilled to
one rule, not two. **Not merged with `P-03`** (log-grep payload-vs-path scoping) despite the
orchestrator's flagged adjacency — same defect family (an assertion that would pass on
incidental text) but a different mechanism: P-03 is about scoping a *grep over structured log
calls*, P-09 is about *value selection inside a formatted exception message and matching it
across cross-compared cases*. Neither is an instance of the other; both stay as distinct,
actionable rules.

**(b) ACCEPTED as `P-10` (add).** `runs/mf2-eng/digest.md:60-66` (the premise check) plus
`:46-52` (the prediction table): SC-11 required three messages be pairwise distinct but only 2
of the 3 pairs (C(3,2)=3) had an assertion — the missing pair was found by counting comparisons
against required distinctions, not by re-reading the messages. The general shape (N enumerated
distinctions need C(N,2) pairwise comparisons, not N-1 chained ones, because inequality is not
transitive) is durable and applies beyond this feature's three-message case.

**(c) ACCEPTED as a `replace` of `P-08`, not an add alongside it.** Both `runs/mf1-eng/digest.md`
and `runs/mf2-eng/digest.md` closed on predicting which checks redden BY NAME before running the
mutant, and treating "only the other check reddened" as a FAIL of the fix. Old `P-08` already
covered the underlying principle (an assertion must be shown to distinguish broken from
correct) but not this operational sharpening. First draft of the replacement dropped `P-08`'s
trigger ("when adding an assertion to close a gap") in favor of "when a mutant proves...", which
presupposes the mutant is already running — caught in advisor review and fixed: the merged
wording keeps both the original trigger and the by-name-prediction discipline, so the entry
still fires at the point someone is *deciding* whether to add a mutant-proof, not only once one
is underway.

## Staleness — P-04

**Not stale, but the two fix cycles exposed a gap next to it, closed by a new entry rather than
a rewrite of P-04 itself.** P-04 governs one specific claim type: "this file is byte-identical to
what's deployed" — the deployed copy under `~/.claude/skills/harness/bin/` is the right reference
for that question and nothing in this feature falsifies it. MF-1/MF-2 answered a *different*
question — "did this cycle's mutate-and-restore leave a net change" — for which `git show HEAD:`
is the right baseline, since the deployed copy has no bearing on same-cycle drift. First draft of
`P-11` restated P-04's clause verbatim before adding the new one; advisor caught the duplication.
Final `P-11` states only the non-overlapping half: the mutate-and-restore protocol itself
(sha256 before, restore, re-verify hash, confirm absence from `git status --porcelain`) — the
practice both MF-1 and MF-2 actually used, twice, to make a "no net change" claim checkable
rather than merely asserted.

## Counts — before / after

| Section | Before | After |
|---|---|---|
| Patterns | 8 | 11 |
| Gotchas | 8 | 8 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

`wc -l .harness/expertise/harness-backend-dev.md`: 54 → 64, well under the 150-line budget.

## `check-expertise.sh` — verbatim invocation and output

```
$ .claude/skills/harness/bin/check-expertise.sh .harness/expertise/
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
FAIL .harness/expertise/harness-documentor.md
  - line 43: G-04 is 53 words — cap is 50; a rule, not a story
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
Exit code: 1
```

The script accepted the directory argument (no substitution needed, contrary to the dispatch's
contingency). `harness-backend-dev.md` reports `OK`. The nonzero exit is `harness-documentor.md`
alone — a pre-existing violation, not introduced or touched by this run. I did not re-run with
just my own file path to force a clean exit; that would have been the argument-narrowing the
dispatch explicitly warned against.

`git status --porcelain .harness/expertise/` before writing my file showed
`harness-code-reviewer.md`, `harness-qa.md`, `harness-security-reviewer.md`,
`harness-ui-reviewer.md` already modified — none touched by this run (I made exactly one `Write`
and one `Edit`, both against `harness-backend-dev.md`).

## `expertise_update` (the DIGEST's op receipt, same list, restated here)

```yaml
expertise_update:
  - op: add
    target: none
    section: Patterns
    entry: "P-09"
    why: "candidate (a): value-slot text must be absent from a message's fixed prose, and cases cross-compared for inequality must share the same value — two clauses that only work together, distilled to one entry"
  - op: add
    target: none
    section: Patterns
    entry: "P-10"
    why: "candidate (b): N pairwise-distinct things need C(N,2) comparisons, not N-1 chained ones — the missing SC-11 pair was found by counting comparisons, not by re-reading text"
  - op: replace
    target: P-08
    section: Patterns
    entry: "P-08 (sharpened)"
    why: "candidate (c): both fix cycles closed on predicting by-name which checks redden before running the mutant, and treating a wrong-check redden as a FAIL — old P-08 stated the principle without the operational discipline; kept the original trigger after advisor caught a first draft that dropped it"
  - op: add
    target: none
    section: Patterns
    entry: "P-11"
    why: "the mutate-and-restore protocol (sha256 before, restore, re-verify, confirm absent from git status --porcelain) both fix cycles used twice to make a 'no net change this cycle' claim checkable; deliberately does not restate P-04, which governs a different claim (byte-identical to deployed)"
```

## Open questions

- **Q1 (non-blocking):** `check-expertise.sh .harness/expertise/` cannot exit clean from inside
  this domain alone — `harness-documentor.md` and `harness-ui-reviewer.md` (at the time this run
  started) carry unrelated word-cap violations. Not fixed here; not my domain.
- **Q2 (non-blocking):** `harness-digest-dev`'s schema documents `suite: n/a` as legal when no
  tests ran, but `validate-digest.py` rejects `suite: n/a` + `VERDICT: PASS` unconditionally for
  the `dev` persona (which `harness-backend-dev` normalizes to), with no exemption for
  `task: none` (a distillation dispatch touching no production code). I reported `suite: pass`
  meaning the applicable gate for this task type — `check-expertise.sh` — passed for my file, not
  that a code test suite ran. Confirmed by running the validator against both spellings: `n/a` +
  `PASS` is rejected, `pass` + `PASS` is accepted. Flagging as a harness schema gap, not deciding
  it myself.

## Constraints honoured

No DEC-174 carve-out file touched. No commit, no push, no live `gh` call.
