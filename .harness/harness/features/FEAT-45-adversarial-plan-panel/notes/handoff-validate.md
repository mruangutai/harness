# Handoff — FEAT-45-adversarial-plan-panel, validate → fix — written at 418d6f7, seq-5

The panel ran at the pinned `d0ebbe6` and returned FAIL, `severity_max: high`. Three findings must
be fixed and NONE of them can be dispatched to a lead.

## Next

MAIN-SESSION-DIRECT fix, then re-run the panel. All three `must_fix` land on
`.claude/skills/harness/bin/check-state.sh` and `.claude/skills/harness/bin/test-check-state.py` —
both ENUMERATED in DEC-174's enforcement layer, which bars executing such a change through a team
run. No lead may take this and a fix-cycle dispatch would be refused or futile.

Fix M1 and M3 in ONE edit (they are the same defect's two halves), then M2. Then re-pin
`review_sha` to the fix commit and re-dispatch the panel at cycle 1 — the notes render `c1`, so
they will not overwrite the `c0` set.

## Trust

- **M1 is real and I verified its premise at the pin, not from the digest.** `check-state.sh:212`
  reads `severity = str(item.get("severity", "")).strip().lower()` and gates on
  `severity in {"high","critical","unrated"}`. An absent key yields `""`, a YAML null yields
  `"none"`; neither gates, so a finding with a lost rating reaches signature un-vetted — read with
  `git show d0ebbe6:` — verified-at 418d6f7
- **The feature's own decision promises the opposite, verbatim.** DECISIONS.md at the pin:
  "**An omitted severity fails closed.** ... A reader that declines to rate, **or a normalization
  that loses a rating**, therefore withholds rather than passes." DEC-206 was written by THIS
  change — verified-at 418d6f7
- **M3 verified:** `test-check-state.py` contains ZERO occurrences of `unrated` at the pin, while
  `check-state.sh` contains exactly one — the gating set itself. The gating token has no test, and
  T-08's `verify:` never greps it, so the omission is invisible to the task's own gate — verified-at 418d6f7
- **M2's finding is real but its cited EVIDENCE is not.** `case_inv32` really is grade 1
  (cyclomatic 28, cognitive 14, ABC 95.1) against a bar of 3, and it is NEW in this feature
  (`def case_inv32` absent at `1d3e5db`). But `code-grade.py --base 1d3e5db --head d0ebbe6` exits 1
  from an unhandled `RuntimeError` — "path '...panel_findings.py' does not exist in '1d3e5db'" — and
  emits ZERO `RESULT: FAIL` lines. The exit code is a CRASH on a file new in the diff, not a grade
  verdict — I ran it myself; the lead holds no shell — verified-at 418d6f7
- **Context that should temper M2's priority, measured not assumed:** grading the file directly,
  19 of 96 functions sit below the bar and 10 are grade 1 — `case_n`, `case_q`, `case_o`, `case_u`,
  `case_v`, `case_x`, `case_inv29`, `main` among them, nearly all PRE-EXISTING. `case_inv32` is new
  code matching a file-wide convention, not an outlier — verified-at 418d6f7
- `code-grade.py` is ABSENT from the reviewed tree; it is a main-branch tool applied from outside,
  so the branch under review carries no such gate — verified-at 418d6f7
- QA re-ran the matrix at the pin: `matrix_ok true`, 29 unit + 27 integration = 56 discovered, both
  rc=0, and it independently confirmed all 9 previously author-reported mutants (16/16) — verified-at 418d6f7

## Dead ends

- Do NOT dispatch M1, M2 or M3 to `harness-eng-lead`. DEC-174 enumerates `check-state.sh`,
  `validate-digest.py` and **the test file of each**; planning such a change through the harness is
  fine, executing it is not — `DECISIONS.md:4303,4326` — verified-at 418d6f7
- Do NOT treat `code-grade.py`'s exit 1 as a grade verdict on this range. It crashes on any file new
  in the diff, so it will exit 1 again after a perfect fix — verified-at 418d6f7
- Do NOT fix M1 by adding `""` and `"none"` to the deny set. The reviewer's remedy is an ALLOW-list
  (`severity not in {"info","low","med"}` gates); `ui`'s independent census proved that vocabulary
  closed and byte-identical across all seven touched doctrine files — `notes/review-harness-ui-reviewer-c0.md`
- Do NOT reuse `notes/qa-*.md` for a panel qa note. That path is the qa SEGMENT's and already holds
  `qa-feat45-c0.md`; the panel step writes `review-harness-qa-c<cycle>.md`
- Do NOT re-litigate the wrapped reader's unvalidated return. It is DEC-206's signed, accepted trade

## Working set

- `.claude/skills/harness/bin/check-state.sh` — the M1 defect at `:212-214`
- `.claude/skills/harness/bin/test-check-state.py` — M3 (`unrated` fixtures), M2 (`case_inv32` at `:2982`)
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c0.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json` — re-pin `review_sha` after the fix
- `.harness/harness/docs/DECISIONS.md` — DEC-206, the promise M1 breaks
