# UI review — BUG-1290 B-3 fix cycle — pin 7104aa43

**Verdict: PASS.** No production surface changed; the only operator-facing behaviour in
scope — `factory_claim.py`'s `no_plan` refusal text and `_blocker_reason_text` grammar — is
byte-unchanged, and the touched fixture strengthens what case 5b proves without weakening any
pinned string. Feature-directory bookkeeping in this commit (`STATE.md`, `feature.json`) reads
accurately for a resuming human.

## 1. Operator-facing CLI output byte-unchanged?

`git diff --stat 76e26386 7104aa43 -- .agents/ .claude/skills/` — empty (re-measured, matches
orchestrator's figure). Widened the check myself: `git diff --stat 76e26386 7104aa43 -- .
':!.harness'` returns only `tests/unit/test-factory-claim.py | 23 +++++++++++--------` — no path
outside `tests/` and `.harness/<feature>/` changed. `factory_claim.py:161-213`
(`_blocker_gate`/`_blocker_reason_text`, the code that produces the `no_plan` / `unresolvable` /
`open` reason strings `factory_cli.refuse` prints) is untouched since `76e26386`.

Case 5b's fixture changed (`tests/unit/test-factory-claim.py:373-386`): kaya-ai's issue map went
from `{}` to `{"T-77": 850}` (T-88 still absent → still `unresolvable`); harness's `T-77` gained
`depends_on: ["T-99"]` (was clear with zero deps) and harness's own map now resolves `T-99 → 954`,
issue 954 seeded `CLOSED`. This does **not** change which reason-kind either segment hits: kaya
still lands `"unresolvable"` (T-88 has no entry in kaya's own map, same as before), harness still
lands clear (`None`) — but now via a real dependency lookup instead of trivially (no deps at all).
That is exactly the strengthening the commit message claims, and it is why the issue-map-keyed
mutant now reddens 5b (harness's own map must supply `T-99`; a feature-only key would instead find
kaya's map, which lacks `T-99`, and misroute the verdict) where before it had nothing to trip over.

## 2. Do the touched cases still pin meaningful operator-visible text?

`check(name_5b, ...)` itself has zero `+`/`-` lines in the diff — same four conjuncts as before:
`code == 0`, `issue == 952`, `"951" in err`, `"unresolvable blocker" in err`,
`"no plan could be read" not in err`. `"unresolvable blocker"` is the literal substring
`_blocker_reason_text` emits for the `"unresolvable"` kind (`factory_claim.py:~199`) — confirmed
the fixture change doesn't cause that reason-kind to flip to `"open"` or `"no_plan"` for kaya, which
would have silently satisfied the same substring check for the wrong reason (it doesn't: `"open"`'s
text has no `"unresolvable"` substring, `"no_plan"`'s is explicitly excluded). No pinned string
weakened. 5a/5c (the other `no_plan`/`unresolvable` cases) are byte-unchanged in this diff.

Ran the suite live (`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py`):
`124/124 checks passed`, 5a/5b/5c/5d/5e/5f all `ok`.

## 3. Feature-directory bookkeeping — `STATE.md` accurate for a resuming human?

`STATE.md` diff (43+/12-, `76e26386`→`7104aa43`): claims "+14/-9 in one file" — matches
`git diff --stat` exactly (14 insertions, 9 deletions, one file). Claims "no production file
changed" — confirmed by the widened diff in §1. Claims "Plan station back at `review`, T-01 back
at `done`" — `plan.yaml` itself has zero diff in this commit, but its current committed content
(`status: review` at top, `T-01 status: done`) matches the claim; it was set in an earlier cycle,
STATE.md doesn't claim this commit moved it. `cycles_used: 8` in `feature.json` matches STATE.md's
"Cycles 8 of a hard 10" and the dispatch's own figure. `feature.json`'s `review_sha` still reads
the prior pin `76e26386` (not `7104aa43`) — correct: it records the last *reviewed* pin, and this
fix landed after that review, before this panel's verdict updates it forward. Not a defect.

No `DESIGN.md`, no rendered surface, no colour/contrast/theme dimension applies to this
CLI-batch/bookkeeping surface — not omitted, genuinely not applicable.

## Findings

None gating. One non-gating note:

- N-01 (severity: low) — `STATE.md`'s Q1 entry states the ship handoff's Trust line ("All five
  task `verify:` commands pass on the committed tree") is "FALSE for T-01 and always was." This is
  a correction to a *prior* cycle's record, not something this commit's diff introduces or could
  fix; it's accurately self-reported here, which is the right place for it, but it's carried
  forward unresolved (T-01's `verify:` still exits 1 on this tree per STATE.md's own account). Not
  this role's fix to make — noting for traceability only.

## Scope note

Named file set per dispatch: `tests/unit/test-factory-claim.py` (delta reviewed above),
`factory_claim.py` (unchanged since prior PASS, audited as the code the fixture binds — §1),
`STATE.md`/`feature.json`/`plan.yaml` (bookkeeping — §3, `plan.yaml` has zero diff, confirmed by
direct `git diff`, not assumed).
