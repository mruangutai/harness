# T-01.intent — stale T-02 clause amended (FEAT-104)

**Done.** `T-01.intent` no longer says the former T-02 was "abandoned"; it now records that the
operator struck it under ruling OD-5 on 2026-09-09 and removed it from this plan. Every claim about
the WORK survives verbatim. Nothing else in `plan.yaml` moved; `approval:` is still `{status: pending}`.

## The one change

- Old clause: `which is abandoned:`
- New clause: `which the operator struck under ruling OD-5 on 2026-09-09 and removed from this plan:`
- Field length: `10432` -> `10498` (delta `+66` == `len(new) - len(old)`).
- Pre-write sha256 of the field block (from `plan-merge.py amend --show`, used as `--expect-sha256`):
  `5408f79214c49f607f1f6f72061da9a36bfda5ee6a8c3ba8a4ed4d695ad9fbd8`.
  Pre-write sha256 prefix of the value itself: `ebbe9d700ae0bad9` — matches the contract measured by
  the tier above, so the field had not drifted before the write.

## How it was built (never retyped)

`yaml.safe_load` -> `T-01.intent` -> one `str.replace(old, new, 1)`. Both assertions ran and passed
BEFORE the write, on the pure-replacement string:
(a) `old_value.count(old) == 1` and the result differs; (b) `len(new_value) - 10432 == len(new) - len(old)` = 66.

**Rewrap, disclosed.** The replacement lengthens line 1, so the sentence's own three physical lines
were re-wrapped to four at width 95 (line lengths 93/95/95/32 — inside the block's existing 92–97
range). No later paragraph was touched or re-indented. Whitespace-normalised equality of the pure
string and the rewrapped string was asserted, so the rewrap moved newlines only. Lengths: pure
replacement `10498`, after rewrap `10498` (newline count inside the sentence went 3 lines -> 4, i.e.
one newline added, one inter-word space removed — net zero).

## Write route

`plan-merge.py amend` at the control-plane absolute path
(`/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py`), value passed as a
file written by the same Python process — never an editor, never a redirect, never retyped.
Note for the tier above: the control-plane `amend` interface is
`--key tasks --id T-01 --field intent --expect-sha256 <sha> --value-file <path>`; the dispatch's
`--task/--value` spelling does not exist on this script. Same verb, same single field.

## Verification (by reading the file back)

1. Reloaded plan: `T-01.intent` contains no `abandon` substring; the opening sentence reads as one
   grammatical sentence across its four wrapped lines ("This task subsumes the former T-02, which the
   operator struck under ruling OD-5 on 2026-09-09 and removed from this plan: the declaration and its
   documentation land as ONE commit, because a lead return omitting adequacy_notes exits 2 from the
   first of the two onward and this feature's own build runs are lead returns.") — no splice.
2. `difflib.unified_diff(old_intent, new_intent)` is exactly one hunk at lines 1–3 -> 1–4: the clause
   substitution plus newline moves inside that sentence. `git diff -U1` on the file shows the same
   3 deletions / 4 insertions and nothing else.
3. Every other `T-01` field compared against `git show HEAD:` — `[]` changed; key order identical.
4. Nine tasks (T-01, T-03..T-10), twelve decisions, `panel:` with 3 readers, 4 findings, 2 dismissals;
   all non-`tasks` top-level keys byte-equal to HEAD.
5. `approval: {status: pending}` in plan.yaml; `status: pending` in BRIEF.md.

## Open questions

None. Nothing implemented; the plan remains unsigned.
