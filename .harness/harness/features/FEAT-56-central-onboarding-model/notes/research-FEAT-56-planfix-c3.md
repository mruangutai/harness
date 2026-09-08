# plan-fix3 — the panel record is now complete and self-consistent

**BLUF.** All three record defects are closed in `plan.yaml` through `plan-merge.py` only. The panel
now records **three readers, all `ran`** (`should-not-exist`, `scope`, `goalcheck`) and **13 findings**,
every one of whose `id` hashes its own recorded `reader` + `summary`. T-02 lists **six** files.
`approval:` is untouched at `{status: pending}`. `check-plan-routes.py` exits 0 (0 violations, 1 plan,
and 0 across all 4 live plans). No substance changed: no task intent, no new task, no decision, no SC.

## 1. `goalcheck` recorded as the reader it was

The plan phase's first segment ran and produced `notes/research-FEAT-56-goalcheck-plan-c0.md` and
`runs/2026-09-08-02-plan-goalcheck-product/digest.md` (verdict FAIL, `must_fix` lines `:61-62`).
Omitting it asserted that a reader which ran was never recorded, so the reader entry plus one finding
per MISSING row is the honest record. `check-state.sh:534`'s `expected_readers` set needed no change.

| id | row | severity | disposition | resolved_by |
|---|---|---|---|---|
| `PF-ac9a3edd4eea3eeb49908cf69b474f1e` | goal-check D2 — issue 206 ordered issue 203 reconciled before either is picked up; the drafted plan discharged it with nothing (zero matches for `203`, reconciliation only in an ungated run digest) | `unrated` | resolved | T-07 |
| `PF-d94deb76b4cd660a77ea3975421a6067` | goal-check D3 — issue 168's shipped-template parse error is live at `4b5dbb23`, not hypothetical; no drafted task repaired it and T-05 item 3 asserted the false premise that the file loads | `unrated` | resolved | T-05 |

`unrated` is recorded because the goal-check stated no severity for either row; inventing one would
falsify it. Both are `resolved`, so INV-32 (`check-state.sh:521-533`) only warns and nothing gates.

**Closure verified at source before recording, not assumed.** #203: `decisions[D-06]` ("reconciled IN
FAVOUR OF REWRITE") plus T-07 item 1's `Over` clause, which puts the reconciliation into the signed
DECISIONS.md entry. #168: T-05 item 3b's repair instruction (quote all three `main_session.writes`
entries), `yaml.safe_load` as T-05's first `verify:` conjunct, and `BRIEF.md:147-150` SC-10, which is
red today and graded at `review_sha`.

## 2. Finding 7 — the panel reader's ORIGINAL summary is canonical

Kept the summary exactly as `runs/2026-09-08-02-plan-panel-validator/digest.md:137` records it, so the
id is `PF-7d76024145e414eeaf8eee356820f780`, replacing `PF-38d92d6f318e9295e88ac433fcfe9935`, which
hashed a summary nobody held. **Why the original and not the amended one:** a `panel.findings` entry
records what a reader reported, and the panel run digest is the immutable source it is transcribed
from — an id computed over an altered summary makes the panel unreconcilable against its own run and,
per this persona's transcription rule, reads later as a stale override. Closure information has its own
fields (`disposition: resolved`, `resolved_by: T-01`); the two-halves closure narrative survives in the
fix-cycle notes, so nothing was lost by dropping it out of the summary. No `approval.rulings` exist
(`check-state.sh:514-517`), so the id change invalidates no risk acceptance.

## 3. T-02 no longer names a file its own intent forbids

`tasks[T-02].files` entry 7 was `tests/unit/test-onboarding-model-strings.py`, while T-02's `intent:`
says "Do NOT create tests/unit/test-onboarding-model-strings.py". Dropped via
`amend --field files --yaml-value --expect-sha256 8bc2c2c4…`; the six `.claude/skills/harness/bin/`
paths stay in their original order. T-02's `verify:` never referenced the file, so nothing else moved.

## Open questions

None. `panel.cycle` stays `0` and `last_run` stays `2026-09-08-02-plan-panel-validator`: this was a
transcription repair, not a new panel run.
