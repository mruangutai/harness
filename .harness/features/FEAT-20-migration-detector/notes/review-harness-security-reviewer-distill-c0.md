# Expertise distillation — harness-security-reviewer — FEAT-20-migration-detector (cold pass)

Sources: my panel note `notes/review-harness-security-reviewer-c0.md` (only self-source — no
observations log this feature) and three lead-relayed candidates plus one lead-flagged clerical
item, per the dispatch.

**Send-back correction (this revision):** G-08 measured 51 words against the 50-word cap
(`check-expertise.sh:112-114`, `WORD_CAP = 50` at line 37) — `text.split()` on the entry text after
the `- XX-NN: ` prefix, continuation lines joined with a single space. Condensed to exactly 50 words
by removing one word ("even") from the clause "this review's finding, even at info severity" → "this
review's finding, at info severity" — the rule is unchanged: a diff-introduced false safety claim is
this review's finding now, regardless of severity, not deferrable maintenance debt. The other three
ops (O-02, P-13, P-14) are untouched from the prior cycle and were already clear of the cap (43, 45,
37 words respectively).

## Section fill — before → after

| Section | Before | After | Cap |
|---|---|---|---|
| Patterns | 12 | 14 | 15 |
| Gotchas | 7 | 8 | 15 |
| Outcomes | 1 | 2 | 10 |
| Open | 0 | 0 | 5 |

## Accepted ops

**G-08 — relay (candidate 1, remedy-timing re-rating).** The lead's re-rating was scoping-correct
and I'm not re-litigating severity — only remedy timing. My artifact deferred correcting a false
safety claim ("cannot outrank the real module") to "whenever this area is next touched." The lead's
distinction holds: that phrasing is right for a *pre-existing* false claim, wrong for one the *diff
under review introduces* — the latter is this review's finding now, at whatever severity, because a
later reviewer can cite it to close my own Q1 unfixed. New entry, not a replacement — no existing
entry states this timing rule; G-04/G-07 are adjacent (severity grading) but neither covers when a
correction is due. Wording condensed to 50 words in this revision; rule content unchanged.

**O-02 — relay (candidate 2, measurement over reasoning).** Judged distinct from O-01, not a
duplicate. O-01 is about identity-level evidence for "this surface looks clean" (assertions proving
equality, consumers traced to their write). The new lesson is narrower and different in kind: for a
*theoretical vulnerability class* (ReDoS backtracking, path-precedence, race ordering), produce a
runnable measurement rather than a structural argument, because complexity-class and
language-semantics arguments are cheap to get wrong. Kept as a second Outcome rather than merged
into O-01 — merging would blur "prove identity" with "prove behavior empirically," two different
techniques worth naming separately, and Outcomes has room (1/10).

**P-13 — relay (candidate 3, widen-vs-create discipline).** Sharpens the existing P-12
(pre-existing items get recorded as assessed-and-dismissed, not omitted) with the harder judgment
call: when a diff adds one instance to an already-open exposure, "pre-existing" is not earned by
assertion — it has to be earned by diffing the surrounding mechanism against the pre-change commit.
Added as a new pattern rather than replacing P-12, since P-12 is about *recording* the dismissal and
P-13 is about *earning* it before recording — different steps in the same review, both worth
keeping at full length.

**P-14 — own-artifact (secrets-sweep scope).** Derived from re-reading my own note: the dispatch
named ~8 source files, but the exploitable finding-shaped step I actually took was grepping
credential patterns across the full 2696-line, 22-file diff, which caught nothing but would have
caught something in `DECISIONS.md` prose had it existed there. No existing entry tells a future
spawn to widen the secrets sweep past a dispatch's named files, and dispatches narrowing to "review
these N files" is a repeatable shape. Passes the six-spawns test: the next dispatch that names files
will again tempt a narrowed sweep.

## Rejected

**Clerical item (`files_touched: []` alongside a written artifact).** Lead pre-judged this as not
worth an entry and I agree, so no op. Reason: the field means source files edited, not artifact
notes written — the handoff contract (`harness-handoff` SKILL.md) already separates `artifact:`
(the note path) from `files_touched:` (source edits), so `[]` alongside a filled `artifact:` field is
correct behavior under the existing contract, not a gap this role's Expertise needs to close.

## Stale-entry check

Re-read all 12 Patterns, 7 Gotchas, 1 Outcome against this feature's record. None contradicted —
P-08 and P-12 were both applied correctly here (pre/post-change comparison for data exposure;
recording the cwd-shadow issue as assessed-and-dismissed pre-existing). G-07 fired correctly
(`severity_max: info`, not `n/a`, on a scoped-in zero-must-fix review). No drops.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Distilled FEAT-20 panel note into 4 new entries (G-08, O-02, P-13, P-14); Patterns 12→14, Gotchas 7→8, Outcomes 1→2, Open unchanged at 0; one clerical relay rejected as already covered by the handoff contract. G-08 re-worded to 50 words (was 51) after send-back."
  in_scope: true
  scope_reason: "Distillation dispatch — writing Expertise ops is this role's job on this dispatch."
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  open_questions: []
  files_touched: []
  expertise_update:
    - op: add
      section: Gotchas
      target: G-08
      entry: "WHEN a diff introduces a comment asserting a safety property DO verify it now, not defer to 'next touch' — a pre-existing false claim can wait; one the diff itself introduces is this review's finding, at info severity, since a later reviewer may cite it to close a question unfixed."
      why: "relay: lead re-rated remedy timing (not severity) on the x.5 test-comment finding — a diff-introduced false claim is not deferrable maintenance debt. Re-worded from 51 to 50 words on send-back (removed 'even'); rule unchanged."
    - op: add
      section: Outcomes
      target: O-02
      entry: "WHEN closing a theoretical vulnerability class (ReDoS backtracking, path-precedence, race ordering) DO produce a runnable measurement — timed adversarial input, printed resolved value — rather than a structural argument alone; complexity-class and language-semantics arguments are cheap to get wrong and expensive to trust."
      why: "relay: this feature closed both a ReDoS question and a CPython path-precedence question by timing/printing rather than arguing; distinct technique from O-01's identity-evidence rule, kept separate rather than merged."
    - op: add
      section: Patterns
      target: P-13
      entry: "WHEN a diff adds one instance to a pre-existing exposure (e.g. one more shadowable name) without an obvious mechanism change DO diff the surrounding code against the pre-diff commit before dismissing as pre-existing — only a proven-unchanged mechanism, reachability, and affected-party set earns the dismissal."
      why: "relay: this feature earned its 'pre-existing, not a regression' claim on check-state.sh's cwd-shadow issue by byte-diffing against 88b1182, not by inspection alone; sharpens P-12's recording rule with the earning step."
    - op: add
      section: Patterns
      target: P-14
      entry: "WHEN a dispatch names specific files to check DO also grep the full diff for secrets/credentials, not only the named files — docs, config, and workflow changes carry credential-shaped strings too, and a narrowed sweep misses them."
      why: "own-artifact: this feature's secrets sweep covered all 22 files/2696 lines despite ~8 named source files; no existing entry tells a future spawn to widen past a dispatch's named scope."
  expertise_full: false
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-distill-c0.md
```
