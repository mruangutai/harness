# Research — FEAT-22 — T-05 must_fix close: the LIVE-resolve comment at test-check-domain.py:785-788

BLUF: **CLOSED.** T-05's `verify:` now carries a negative grep (`plan.yaml:601-604`) that reds the
token-swap-only build the reviewer named, and T-05's intent (`plan.yaml:661-671`) now tells the
builder the claim must be rewritten, not respelled, and names who owns the residual. Base
re-confirmed at `0f12f14c166d231ddf648cc00ff4d12029ce0122` before any measurement. Nothing else in
the plan was reopened; both artifacts stay `approval: pending`.

## The assertion, verbatim (`plan.yaml:601-604`)

    if grep -qE 'entry exists anywhere|nothing to match' $B/test-check-domain.py; then
      echo "site 785-788: the no-such-entry glob-keyed claim survives, and T-02 makes it false"
      grep -nE 'entry exists anywhere|nothing to match' $B/test-check-domain.py; exit 1
    fi

Placed immediately after the `:599-600` guide.md positive pin, deliberately: the two positive greps
on the same file directly above act as its positive control (G-14). A wrong path makes `grep` exit 2,
the `if` false, and a negative check standing alone would green vacuously.

## Measured, at the pin

Source: `git show 0f12f14:.claude/skills/harness/bin/test-check-domain.py`. Three builds, the
variants generated in memory and piped to the exact shipped pattern — no re-cased, re-flagged trial.

| Build | Result | countP | `docs/harness/guide.md` |
|---|---|---|---|
| 1. pin, unfixed | **REDS** — hits 787 and 788 | 19 | 4 |
| 2. token-swap-only (respell the glob inside :787, sentence otherwise intact) | **REDS** — hits 787 and 788 | 18 | 4 |
| 3. correct rewrite (claim dropped, "the live tree resolves the migrated docs path to harness-documentor") | **GREEN** | 18 | 4 |

Build 2 is the build this assertion exists to catch, and it fails it. Build 1 reds, so the assertion
is non-vacuous — it forces a change rather than passing over the current tree.

## Why whole-file, not a window

Both fragments occur **exactly once each** at the pin, and only inside the target comment
(`787`, `788`). Neither appears on the mandated survivor line (the refused-direction case's path
argument), nor anywhere else. A window anchored on a nearby literal would add G-04 anchor rot for
zero discrimination gain. This matches the exemplar the reviewer cited (`plan.yaml:369-372`), which
is also whole-file.

## Collision check — both existing pins unaffected

- **`:596-598`, exact count 1.** The new patterns share no token with `P =
  'docs/harness|"docs", ?"harness"'`, so the assertion cannot move `n`. Independently: the mandated
  rewrite takes countP from 19 to 18 (en route to the required 1 once every other T-05 site is
  repointed) — driven by the rewrite, not by this check, and in the direction the count pin demands.
  Confirmed at `plan.yaml:597`, unshifted by the edit.
- **`:599-600`, positive pin on `docs/harness/guide.md`.** Presence-only `grep -q`; occurrence count
  is 4 in all three builds, unchanged. Confirmed at `plan.yaml:600`, unshifted by the edit.

The insertion sits below both, so neither line number moved.

## Intent tightening (`plan.yaml:661-671`)

Two halves, per the `:221` contract the reviewer used as its standard:

1. Respelling the glob inside the sentence is named as the exact failure the grep catches; the two
   forbidden fragments are quoted so the builder knows the shape, and any retelling — past tense,
   negated, hedged — is called out as also red. The claim shape goes, not just its token.
2. The declared ceiling with a named receiver, mirroring `plan.yaml:430-431`: the grep forces the
   false claim out but cannot prove the replacement right; the replacement sentence is the builder's
   and a reviewer reads it. This is what put `:221` under the reviewer's acceptable-ceiling ruling,
   and it now covers this site too.

Safe to quote the fragments here and in the intent: nothing greps this `plan.yaml` for them (the
only plan-file greps in the plan target `.claude/skills/harness/templates/plan.yaml`, a different
file).

## Post-edit checks

- `yaml.safe_load` over `plan.yaml`: parses; T-05's `verify:` literal block round-trips with the new
  four lines and no folding.
- `check-plan-routes.py plan.yaml`: exit 0, `0 violation(s)`. The eleven `DEVIATION` lines are the
  pre-existing D-03 main-session-direct carve-out declarations, unchanged by this edit.

## Residual, declared

An adversarial rewrite could delete the forbidden phrase and leave a grammatically incomplete or
differently-false sentence. That is inherent to grepping freeform prose, is the same residual the
reviewer ruled acceptable at `:221`, and is assigned to the reviewer by the intent's second half.
