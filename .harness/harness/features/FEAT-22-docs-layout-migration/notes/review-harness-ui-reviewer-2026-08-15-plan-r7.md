# Review — harness-ui-reviewer — FEAT-22-docs-layout-migration (Mode A, whole-plan, r7 re-fire)

BLUF: **PASS.** `must_fix: []`. The three r6→r7 insertions are exactly what the dispatch table
described, land at exactly the predicted offsets, and the two new operator-visible strings (the
`:605-606` error message, the `:688-705` instruction prose) are checkable and adequate. My own S-04c
Q1 is disposed: **premise unchanged, not narrowed, not resolved** — see below. No fourth,
unannounced edit found. Verdict binds plan TEXT; all 11 tasks remain `status: pending` — nothing has
executed.

Pin confirmed: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`, matching every
prior cycle and the feature.json `review_sha`.

## The three hunks — confirmed verbatim against the dispatch table

Read directly at their stated line numbers, not relayed:

- **`:604-606`**: `if grep -qE 'entry exists anywhere|nothing to match' ...; fi` followed by
  `grep -qF 'hook(".harness/harness/docs/SPEC.md", "harness-documentor")' $B/test-check-domain.py
  || { echo "case (h) at :924: the hook subject is not pinned to the migrated docs path"; exit 1; }`.
  Matches the dispatch description exactly.
- **`:688-705`**: the `test-check-domain.py:924` enumeration entry, closing with `KEEP THE PAIR
  DISTINGUISHABLE: :924 is the hook half, :789 is the --resolve half...` at `:700-705`. Matches.
- **`:990`**: `docs/harness/*) ;;` added to the T-09 allow-list `case`; `:994`'s
  `grep -v '^docs/harness/'` left untouched, confirmed by direct read. Matches.

**Non-vacuity of the new `-qF` clause, checked myself rather than accepted from eng-lead's digest**
(their MF-4 closure said the same, but I ran it independently rather than relaying it):
`git show 0f12f14:.claude/skills/harness/bin/test-check-domain.py | grep -cF
'hook(".harness/harness/docs/SPEC.md"'` → **0** at the pin. The migrated literal does not already
exist, so the clause is not a vacuous-green rubber stamp — it genuinely reds until T-05 lands the
repoint. The legacy call sits exactly where cited: `grep -n 'hook("docs/harness/SPEC.md"'` → line
**924**.

## Q1 disposition — the item this cycle asked me to rule on

r6 Q1 (from `t05-remedy-recheck.md`): T-05's intent mandates a subject-path change at
`test-check-domain.py:789` (the `--resolve` half) with no verify assertion naming it directly; the
only backstop is the pre-existing `PASS test-check-domain.py` gate plus T-05's D-03
human-read-diff carve-out.

**Ruling: UNCHANGED, not narrowed, not resolved.** The r7 insertion pins `:924` — the **HOOK**
half of the pair — with a new `grep -qF` assertion. No new assertion in T-05's verify (`:581-610`,
re-read in full this cycle) touches `:789` or the `--resolve` call form. The `KEEP THE PAIR
DISTINGUISHABLE` clause at `:700-705` is intent prose aimed at a human implementer (D-03 class),
not a mechanical check — it does not cross-check `:789` against `:924`, and could not: they are
independent lines in independent test functions. So Q1's literal premise — "no assertion names the
`:789` subject-path change directly" — still holds true, verbatim, at r7.

What r7 *does* do: close the **analogous** gap at the paired case, `:924`, which Q1 never covered
(Q1 was scoped to `:789` only), and add explicit prose naming the exact failure mode Q1's residual
worried about (subject changed at one half, expectation mismatched, or the pair collapsed to prove
only one direction). That reduces the *chance* a human misses the coupling, but it is guidance, not
gate — it leaves the residual in the same class already accepted at `harness_boundary.py:221`
(declared ceiling, named human receiver, no positive machine check). Carrying this forward as `Q1`,
`blocking: false`, disposition stated: same non-blocking residual, not worth a cycle on its own.

## The two new operator-visible strings — this cycle's specific remit

**`:606` error message** (`"case (h) at :924: the hook subject is not pinned to the migrated docs
path"`) — engaging eng-lead's A5/A6 rather than re-deriving:

- **P-09 check (message diagnosing a state the feature makes normal): clear.** This is a
  positive-presence check — it only fires when the migrated literal is *absent*. It cannot fire on
  the post-migration normal state; confirmed above (count = 0 at pin, so pre-migration state reds
  it, which is correct).
- **A6 (line will drift as T-05's earlier insertions shift `:924`): I agree it's advisory, and I'd
  go further — it's less of a problem than it looks.** The message embeds `"case (h)"` as a
  semantic locator *alongside* the line number. That's a house-convention departure worth naming:
  every other pin-referencing error message in this file uses a bare `"site NNN[-NNN]:"` prefix
  (`:370` "site 221: ..."; `:602` "site 785-788: ..."). This is the only one that also names a
  case label. That's not a defect — it makes this message *more* drift-resistant than its own
  siblings, since "case (h)" is greppable in the test file regardless of where insertions move the
  line. Net: A6's concern is real in the narrow sense (the number can go stale) but the message
  carries a second, non-drifting handle the sibling idiom doesn't. Not worth reopening signed text
  to reword — cost to fix is one echo edit, cost to leave is bounded one-hop confusion, same
  calculus eng-lead already ran. **Concur: advisory, not blocking.**
- **A5 (exact-text brittleness on a line-wrapped/re-quoted correct execution): concur, advisory.**
  The intent's own `:688-705` insertion states "The verify greps for the migrated call text," which
  pre-warns the implementer of the exact-match requirement before they touch the file — that's a
  mitigation r7 itself adds, not just inherited precedent.

**`:688-705` instruction prose** — concrete and checkable, in Mode A terms: it pins the exact
subject string (`.harness/harness/docs/SPEC.md`), states what must NOT change (the exit-0
expectation, the case not becoming a refused-direction case), and names the collision risk
explicitly (`:924` vs `:789` both ending on the identical path string post-move). This is the kind
of concrete, checkable instruction Mode A asks for — not an adjective needing a scale.

## Anchor audit — no fourth, unannounced edit found

Re-resolved every r6-native anchor available from my own priors (only `t05-remedy-recheck.md`
carries genuine r6 coordinates — `plan-recheck.md` predates it and cites an earlier revision;
excluded from this audit for that reason, not reused):

| r6 anchor (my prior note) | Zone | Predicted r7 | Actual r7 | Match |
|---|---|---|---|---|
| `:601-604` ("Check 1" heading text) | before `:605`, +0 | `:601-604` | `:601-604` (confirmed by direct read of the same clause text) | yes |
| `:621` ("After T-03, docs/harness/x is no longer...") | `:605`–`:688`, +2 | `:623` | `:623` | yes |
| `:661` ("REWRITTEN MEANS REWRITTEN, NOT RESPELLED") | `:605`–`:688`, +2 | `:663` | `:663` | yes |
| `:671` ("...is yours to get right, and a reviewer reads it.") | `:605`–`:688`, +2 | `:673` | `:672` | off by 1 |

The last row's off-by-one investigated, not waved past: the opening anchor of the same paragraph
(`:661`→`:663`) matched exactly, and the closing phrase's wording matches my prior note's quote
word-for-word at `:672`. A YAML block-scalar's manual line-wrap does not spontaneously reflow
without a hand edit, and the dispatch's own three-hunk table accounts for every change in the file
— this paragraph is outside all three hunks. Most likely explanation: my own S-04c note's closing
line was off by one when it summarized a multi-line paragraph (a citation slip, not a re-verified
grep at the time). Treated as resolved, not a finding — flagged here per instruction to report
off-model anchors rather than silently reconcile them.

No r6-native prior anchor exists past `:705` to test the `+20`/`+21` zones (my own notes never cite
that far into the file). Compensating evidence, same standard eng-lead used for byte-identity
outside the hunks: the `:990` hunk and the untouched `:994` line were read directly this cycle and
match the dispatch's description exactly; eng-lead's own `plan\.yaml:[0-9]` self-reference sweep
found nothing needing re-pinning. Attested, not independently re-derived past `:705`.

**Line-count aside, not a finding:** the dispatch states "1218 lines"; `wc -l` reads **1217**. File
ends with a trailing newline (confirmed via `tail -c1 | xxd` → `0a`), so 1217 is the correct count
of the file as written. This is a one-line discrepancy in the dispatch's own framing text, not in
the plan; noted for completeness, not raised as a plan defect.

## Not reopened

Per LEAVE DISCIPLINE and the dispatch's own closure list: the withdrawn S-02b MF-1 remedy, the Q1
suite measurement (0/0, both green at the pin), Q4's accepted residual at
`test-check-domain.py:789`, and everything outside the three hunks that carried its own r6 PASS from
me. eng-lead's `:990` architecture ruling (self-consistent exclusion of rename sources from the
28-file floor) is not re-derived here — outside my lens, already closed at the tier that owns it.

## Accessibility and theme parity

Not applicable, stated explicitly rather than omitted: every surface in scope this cycle is a
`plan.yaml` verify script, YAML instruction prose, and Python test-file comments/call literals — no
rendered output, no colour, no interactive state, nothing colour-only conveys state. Batch/CLI
error-message text is the operator-visible surface in scope, audited above.

## What this verdict does and does not bind

All 11 tasks are `status: pending`; nothing has executed. This verdict is on plan **text** — the
contract as written — not on any landed shape. A future post-build (Mode B) review is a separate,
later act and is not proposed or implied here.

```yaml
VERDICT: PASS
DIGEST:
  headline: The three r6->r7 insertions land exactly where dispatched and are non-vacuous (checked at the pin, not relayed); S-04c's Q1 is disposed UNCHANGED at :789, with the analogous :924 gap closed instead; no fourth unannounced edit found. must_fix:[].
  mode: A
  in_scope: true
  severity_max: info
  findings: 2
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q1, question: "r6 Q1 carried forward, disposition ruled this cycle: T-05's intent mandates a subject-path change at test-check-domain.py:789 (the --resolve half); no verify assertion names it directly, at r6 or r7. r7 closed the analogous gap at the paired case :924 (hook half) with a new grep -qF assertion and added KEEP THE PAIR DISTINGUISHABLE prose (:700-705), but that prose is D-03-class human guidance, not a mechanical cross-check between :789 and :924 -- it cannot be, they are independent lines in independent test functions. Q1's premise for :789 specifically is therefore UNCHANGED, not narrowed. Residual: subject-changed-but-expectation-mismatched at :789, guarded only by the PASS test-check-domain.py gate (which catches a fully-unrepointed :789) plus T-05's D-03 human-read-diff carve-out -- same residual class already accepted at harness_boundary.py:221. Non-blocking; would not spend a cycle on this alone.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-ui-reviewer-2026-08-15-plan-r7.md
```
