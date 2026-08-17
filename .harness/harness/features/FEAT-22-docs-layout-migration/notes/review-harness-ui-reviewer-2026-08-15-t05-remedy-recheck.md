# Review — harness-ui-reviewer — FEAT-22-docs-layout-migration (Mode A, unit 4, cycle 3, narrow)

BLUF: **PASS.** The remedy I named in cycle 2 for `test-check-domain.py:785–788` landed and
discriminates. All four checks in scope confirmed by independent reproduction, not by trusting
pm's table or its research artifact (whose digest never returned). `must_fix: []`.

Base re-confirmed: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`, matching the
dispatch's pin, before any measurement.

## Scope note

T-05's `status:` is still `pending` — no production edit to `test-check-domain.py` has happened
yet (every task in the plan is `status: pending`; nothing has executed). That is expected and
correct for this review: what changed is `plan.yaml` itself (T-05's `verify:` and `intent:`), which
is the artifact this cycle audits. The comment at `test-check-domain.py:785–788` remains in its
original, unfixed state at the pin — I checked this directly and use it as the "build 1" case
below.

## Check 1 — does `plan.yaml:601–604` red a token-swap-only build?

Reproduced independently, not from pm's table. Took the verbatim comment block at the pin
(`test-check-domain.py:784–788`) and built two variants in `/tmp`:

- **Build 2, token-swap-only**: respelled only the glob token (`` `docs/harness/**` `` →
  `` `.harness/*/docs/**` ``), left `entry exists anywhere` / `nothing to match` standing verbatim.
  `grep -nE 'entry exists anywhere|nothing to match'` **still matches** (both fragments present,
  unmodified) — the `if` in the verify fires, `exit 1`. **Reds**, as required.
- **Build 3, correct rewrite**: dropped the claim entirely, replaced with "The live tree resolves
  the migrated docs path to harness-documentor." `grep -qE` **no match** — clean. **Greens**, as
  required.

This matches pm's reported table (build 2 REDS, build 3 GREEN) and I built and ran both variants
myself rather than accepting the table.

## Check 2 — non-vacuous at the pin?

Confirmed directly: `grep -qE 'entry exists anywhere|nothing to match' test-check-domain.py` on the
unmodified pinned file matches lines 787–788 (the original, still-unfixed comment). The assertion
reds the current tree — it forces a change rather than passing over it vacuously.

## Check 3 — collision with either existing pin?

Measured at the pin, not inherited:

- **`:596–598`, exact-count-1** (`n=$(grep -cE "$P" test-check-domain.py); test "$n" = 1`, where
  `P = 'docs/harness|"docs", ?"harness"'`): current `n = 19`. Neither `entry exists anywhere` nor
  `nothing to match` contains `docs/harness` or the quoted variant — no shared token, so the new
  check cannot move `n`. No collision.
- **`:599–600`, positive pin** (`grep -q 'docs/harness/guide\.md'`): current occurrence count = 4,
  unrelated string. No collision.
- **Load-bearing premise of pm's whole-file-not-window choice** — verified myself, not inherited:
  both fragments occur **exactly once each** in the file (`grep -c` = 1 for each), and both
  occurrences are at lines 787–788, inside the target comment, nowhere else. The premise holds.
- **Vacuous-green on path rot, checked**: `grep -qE` against a missing path would exit 2, making the
  `if` false and the negative check green silently. Not a live gap — `:599–600`'s positive grep uses
  the identical `$B/test-check-domain.py` literal one line above and fails the verify first if that
  path rotted.

## Check 4 — is the intent tightening at `:661–671` adequate against the `:221` standard?

Confirmed line range: `:661` opens "REWRITTEN MEANS REWRITTEN, NOT RESPELLED"; `:671` closes "...is
yours to get right, and a reviewer reads it." Matches the dispatch's citation exactly.

Compared directly against what I accepted at `:221` in cycle 2 (`plan.yaml:426–431`):

- Same delegation register: `:221`'s accepted ceiling said "the verify can force the false claim
  out but cannot prove the replacement is right; the replacement sentence is yours to get right, and
  a reviewer reads it" (`:430–431`). This site's intent closes on the identical clause, word for
  word (`:670`: "is yours to get right, and a reviewer reads it."). Same named receiver, same scope
  of what the grep is and is not claimed to prove.
- Same "any spelling" framing: `:221`'s verify was accepted as a negative-only ceiling because it
  enforced exactly what the intent mandated ("MUST NOT SURVIVE IN ANY SPELLING"). This site's intent
  states the equivalent explicitly: the fragments must not survive "ANYWHERE in this file, in any
  spelling of the glob, and any retelling of the claim — past tense, negated, hedged — reds it too."
  That "any retelling" line is itself an overclaim of what a literal-fragment grep can do — a
  case-changed or fully reworded retelling would evade it — but that is the same declared residual
  already accepted at `:221` (ceiling plus named reviewer), not a new gap.
- Vacuity of a positive pin: at `:221` I accepted skipping a positive check because the only
  candidate positive handle was unchanged pre- and post-fix (vacuous). pm's research artifact does
  not restate this argument for this site, but I checked it independently: the phrase most likely to
  serve as a positive handle ("names harness-documentor") already exists, unchanged, in the
  `fleet_case` assertion message at line 793 pre- and post-fix — pinning it would be equally vacuous
  here. The omission is consistent with the accepted standard, not a gap.

**Ruling: adequate, and consistent with what I accepted at `:221`.** Same declared ceiling, same
named receiver, same residual (a determined edit could delete the forbidden phrase and leave a
differently-false sentence — inherent to grepping freeform prose, already ruled acceptable and not
reopened here).

## Not reopened, per LEAVE DISCIPLINE

Cycle 1's clean list and cycle 2's Finding-1 closure (the five T-03 assertions) stand, untouched.

## Encountered in passing, not scoped in — reporting per dispatch instruction, checked, not fully investigated

T-05's intent (the same paragraph block, just above `:661`) separately mandates a **subject-path**
change at line 789 — "Change the subject to `.harness/harness/docs/SPEC.md` and keep the
expectation" — distinct from the comment-rewrite mandate my cycle-2 must_fix targeted. I did not
find any assertion in T-05's verify (`:581–610`) that names this subject-path change directly.

I traced one level further before flagging: T-05's own rationale, two lines above this passage
(`:621`, "After T-03, docs/harness/x is no longer a control-plane target, so ... the documentor's
`docs/**` grant match is discarded by the target-side filter"), implies that leaving the subject
at the old `docs/harness/SPEC.md` while keeping the `harness-documentor` expectation would make the
live `--resolve` call return something other than `harness-documentor` once T-01–T-04 land — which
the pre-existing `grep -q '^PASS test-check-domain\.py$'` gate at `:588–590` already reds. So the
"subject silently left unchanged" build looks like it is already caught, not a hole. What is *not*
caught by any assertion is the narrower case — subject changed correctly but the paired expectation
is also (wrongly) flipped to something that happens to still resolve, or the reverse — which would
need a behavioral resolve, not a string grep, to build a counter-case for. I have not built that
counter-case; it is guarded today only by T-05's D-03 human-read-diff carve-out, same as `:221`'s
declared residual. Flagging as non-blocking: narrower than my first framing, and I would not
dispatch a cycle 4 on this alone.

## Accessibility and theme parity

Not applicable, unchanged from cycles 1–2: this recheck's scope is a `plan.yaml` verify script and
Python test-file comments — no rendered output, no colour, no interactive state.

```yaml
VERDICT: PASS
DIGEST:
  headline: The remedy for test-check-domain.py:785-788 landed in plan.yaml and discriminates the exact token-swap-only build it was named to catch; reproduced independently in three variants.
  mode: A
  in_scope: true
  severity_max: info
  findings: 1
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q1, question: "T-05's intent also mandates changing the --resolve subject at test-check-domain.py:789 from docs/harness/SPEC.md to .harness/harness/docs/SPEC.md. No assertion in T-05's verify names this directly, but the pre-existing PASS/FAIL gate at plan.yaml:588-590 likely already reds a build that silently leaves the subject unchanged (per T-05's own :621 rationale). The narrower uncovered case is subject-changed-but-expectation-mismatched, guarded today only by T-05's D-03 human-read-diff carve-out, same residual class as :221. Not something I would spend a cycle 4 on alone.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-ui-reviewer-2026-08-15-t05-remedy-recheck.md
```
