# Red-first receipt — T-01 (FEAT-2229, SC-01..SC-03)

Main-session-direct (DEC-174). Tests written before any source change; run against the
unmodified tree (HEAD d22d1860), then against the implementation.

## Red (source unchanged)

`python3 tests/unit/test-decision-disposition-schema.py` → exit 1, **13/40 passed** (27 failed):

- FAIL a mapping block is refused
- FAIL a null block is refused
- FAIL a string row is refused
- FAIL a list row is refused
- FAIL a row missing dec is refused
- FAIL a row missing disposition is refused
- FAIL a row missing clause is refused
- FAIL a row missing successor is refused
- FAIL a row missing reason is refused
- FAIL a sixth key is refused
- FAIL amend with successor none is refused
- FAIL amend with a free-text successor is refused
- FAIL strike with successor none is refused
- FAIL strike with a free-text successor is refused
- FAIL keep naming a successor is refused
- FAIL an unknown disposition is refused
- FAIL a title-case disposition is refused
- FAIL a non-DEC dec is refused
- FAIL a lowercase dec is refused
- FAIL an empty clause is refused
- FAIL a whitespace clause is refused
- FAIL a non-string clause is refused
- FAIL an empty reason is refused
- FAIL a two-line reason is refused
- FAIL a non-string successor is refused
- FAIL set-key refuses a malformed row
- FAIL a refused row leaves the plan byte-identical

`python3 tests/integration/test-plan-decision-dispositions.py` → exit 1, **42/90 passed** (48 failed):

- FAIL an eligible draft without decisions_affected fails
- FAIL an unindexed dec fails with row index and dec
- FAIL keep on STRUCK fails
- FAIL amend on title-case Struck fails
- FAIL a clause from a neighbouring section fails
- FAIL a partial clause match fails
- FAIL markdown is not normalised away
- FAIL whitespace is not normalised away
- FAIL an amend to a D id this plan lacks fails
- FAIL a strike to an unindexed DEC fails
- FAIL an amend with no task owning DECISIONS.md fails
- FAIL disposition failures sit beside unrelated anchor failures
- FAIL a served plan never borrows the harness decision corpus
- FAIL a draft stamped exactly at activation is eligible
- FAIL a draft stamped after activation is eligible
- FAIL an offset instant compares as an instant
- FAIL a null era requires the block on every stamped draft
- FAIL a malformed era is a diagnostic, never an exemption
- FAIL a date-only era is not an instant
- FAIL a malformed drafted_at is a diagnostic
- FAIL a naive drafted_at is a diagnostic
- FAIL creation stamps a timezone-qualified UTC drafted_at
- FAIL creation refuses a caller-supplied drafted_at
- FAIL the refused creation writes no file
- FAIL set-key backdate on stamped plan: refused nonzero
- FAIL set-key backdate on stamped plan: plan bytes identical
- FAIL set-key forward-date on stamped plan: refused nonzero
- FAIL set-key forward-date on stamped plan: plan bytes identical
- FAIL set-key null on stamped plan: refused nonzero
- FAIL set-key null on stamped plan: plan bytes identical
- FAIL set-key backdate on undated plan: refused nonzero
- FAIL set-key backdate on undated plan: plan bytes identical
- FAIL set-key forward-date on undated plan: refused nonzero
- FAIL set-key forward-date on undated plan: plan bytes identical
- FAIL set-key null on undated plan: refused nonzero
- FAIL set-key null on undated plan: plan bytes identical
- FAIL apply backdate on undated plan (byte-preserving): refused nonzero
- FAIL apply backdate on undated plan (byte-preserving): plan bytes identical
- FAIL apply forward-date on undated plan (byte-preserving): refused nonzero
- FAIL apply forward-date on undated plan (byte-preserving): plan bytes identical
- FAIL apply null on undated plan (byte-preserving): refused nonzero
- FAIL apply null on undated plan (byte-preserving): plan bytes identical
- FAIL apply backdate on undated plan (safe_dump rendering): refused nonzero
- FAIL apply backdate on undated plan (safe_dump rendering): plan bytes identical
- FAIL apply forward-date on undated plan (safe_dump rendering): refused nonzero
- FAIL apply forward-date on undated plan (safe_dump rendering): plan bytes identical
- FAIL apply null on undated plan (safe_dump rendering): refused nonzero
- FAIL apply null on undated plan (safe_dump rendering): plan bytes identical

(The integration suite's fixture defects found on that first run — the served-segment fleet
fixture, a non-vocabulary `landed` station, and the PRESERVE_BASE_BYTES-off copy needing its own
manifest root — were fixed in the tests before any source edit; the 48 above are the re-run.)

## Green (after implementation)

T-01 verify, verbatim:

```
set -eu
python3 tests/unit/test-decision-disposition-schema.py      # 40/40 passed
python3 tests/integration/test-plan-decision-dispositions.py # 91/91 passed
```

exit 0, ~0.4 s and ~12 s. Regression: `python3 tests/integration/test-plan-merge.py` exit 0 with
`case_create_path_approval` unchanged (it asserts approval/content, not exact bytes, so the
new stamp needed no expectation change); `tests/unit/test-harness-yaml-corpus.py` 16/16.

## Validate c1 fix (F1 high, F2 med) — red → green

Regressions added first to `tests/integration/test-plan-decision-dispositions.py`
(`case_fenced_heading_is_not_a_section`, `case_creation_validates_dispositions`), run against
the c1 source (worktree HEAD 98305097) → exit 1, **92/98 passed**:

- FAIL a clause only in a fenced DEC-10 example fails the DEC-10 row (F2)
- FAIL a nested-fence DEC-10 example is still fenced (F2, ```` fence holding ``` lines)
- FAIL DEC-11's section runs past its fenced examples (F2 end-scan)
- FAIL creation refuses a malformed decisions_affected row (F1: `[{dec: DEC-10}]` was APPLIED)
- FAIL the refused malformed creation writes no file (F1)
- FAIL creation with a valid row still creates (F1 control; failed only because the malformed
  plan had been written, so the second apply hit CONFLICT)

Fix: `plan_merge/union.py` `_refuse_illegal_dispositions` runs
`harness_yaml.validate_decisions_affected` (the reader's own rule, made public) on the creation
proposal before the write — exit 5, no file. `plan_merge/check.py` locates headings only outside
fences tracked from the top of the file (`_real_headings`, `_fence_after`: a fence closes only on
a same-character run at least as long), and bounds a section at the next real heading.

Green: T-01 verify exit 0 — unit 40/40, integration 98/98; `test-plan-merge.py` exit 0;
`test-checker-structure-locks.py` ALL PASS.

## Validate c2 fix (F3 med, SC-02) — red → green

Regression added first: `case_info_string_run_does_not_close_a_fence` — inside DEC-11, an outer
```` ```text ```` fence holding a ```` ```python ```` line, a `## DEC-10` spoof heading and a spoof
clause, then the outer closer, then the real DEC-10. Against the c2 source (HEAD 48cc5b6a) →
exit 1, **99/100 passed**:

- FAIL a clause after a ```python run inside an open fence fails the DEC-10 row

Fix: `plan_merge/check.py` `_fence_after` closes an open fence only on a run of the opener's
character at least as long followed by nothing but whitespace (CommonMark 4.5); a run carrying an
info string is content. Openers may still carry info strings.

Green: unit 40/40, integration 100/100, `test-plan-team.py` 184/184 (the acceptance chain exits
0); `test-plan-merge.py` exit 0; `_fence_after` grade 4.

## Validate c3 fix (F3-I med, SC-02; operator ruling: close the class) — red → green

One actual-CLI spoof case per CommonMark rule, added to
`tests/integration/test-plan-decision-dispositions.py` first and run against the c3 source
(HEAD d1fd4aa1) → exit 1, **108/113 passed**:

| Rule | Case | Red (c3 source) | Green |
|---|---|---|---|
| 1 fence lines 0–3 spaces | `case_overindented_fence_lines_are_content` (4-space closer — the reviewer's input — and 4-space opener) | FAIL ×2: the spoof clause passed the DEC-10 row (controls passed) | PASS 4/4 |
| 2 ATX heading 0–3 spaces, at lookup and section end | `case_heading_indentation_limits` | FAIL ×2: a 3-space `## DEC-11` did not end DEC-10's section (neighbour clause accepted) and was not found as DEC-11's heading; the 4-space spoof assertions passed | PASS 5/5 |
| 3 backtick info string may not hold a backtick | `case_backtick_info_string_cannot_open` | FAIL: the spoof clause passed the DEC-10 row | PASS 2/2 |
| 4 closer bare + fenced `## DEC-` never a heading (landed F3/F2) | `case_info_string_run_does_not_close_a_fence`, `case_fenced_heading_is_not_a_section` | already green (landed) | PASS 6/6 |
| 5 unclosed fence runs to EOF | `case_unclosed_fence_runs_to_end` | already green: the scanner already agreed, so no red was possible | PASS 2/2 |

Fix: `plan_merge/check.py` keeps a single scanner. `FENCE_RE` is `^ {0,3}` plus the run and
its info string; `HEADING_RE` is `^ {0,3}#{1,6}` followed by a space, tab or line end, and is used for both
heading lookup and section end. `_opener` refuses a backtick opener whose info string holds a backtick.
`_fence_after` keeps the bare-closer rule, and an unclosed fence stays open to EOF.

Green: unit 40/40, integration 113/113, `test-plan-team.py` 184/184 (acceptance chain exit 0);
`test-plan-merge.py` exit 0. Touched functions grade 4–5.

## Validate c4 round (operator ruling 2026-11-22) — red → green

### Item 1: tilde coverage, test-only (red by mutation, production unchanged)

New actual-CLI spoof cases with real-clause controls: `case_closer_must_match_opener_character`
(a `~~~` run inside a ```` ```text ```` fence, and a ```` ``` ```` run inside a `~~~text` fence) and
`case_tilde_info_string_may_hold_backticks` (`~~~ a`b` opener holding a spoof `## DEC-10`).

| Run of `test-plan-decision-dispositions.py` | Result for the new tilde assertions |
|---|---|
| unmutated source | all 6 PASS |
| M6 applied (`closes = len(run) >= len(fence) and not info.strip()` — closer character ignored) | FAIL `rule 4 ~~~ in ```` and FAIL `rule 4 ``` in ~~~` (spoof accepted); 120/130 |
| M8 applied (`_opener`: `None if "`" in info` — rule applied to tildes too) | FAIL `rule 3 tilde` (spoof accepted); 121/130 |
| mutation reverted | all 6 PASS |

(The mutant counts include the 8 SEC-C4-01 failures below, which were still red at that point.)

### Item 2: SEC-C4-01, `## DEC-10x` impersonating DEC-10

`case_heading_names_the_full_identifier`: spoof headings `DEC-10x — not DEC-10`, `DEC-10_a`,
`DEC-10-1 — another id`, `DEC-10.5` each placed before the real `## DEC-10 — Ten`; plus positive
shapes `## DEC-10: Ten`, `## DEC-10 (Ten)`, `## DEC-10`. Red against the source as received
(122/130): all 8 spoof/control assertions FAIL (the spoof section was selected); the 3 positive
shapes PASS.

Fix: `plan_merge/check.py` `_heading_level` matches `dec` followed by `DEC_ID_END` —
line end, whitespace, `:`, `(`, an em/en dash, or `-` plus whitespace — replacing `(?!\d)`.

Full-corpus proof: the real DECISIONS.md has 223 `DEC-` headings, and each matches its own id.
All 220 indexed DECs resolve to a section. The real `plan-merge.py check` was run against
`--root` = this worktree on a temporary copy of this feature's plan (pending, `drafted_at` after
the era, one row per indexed DEC — 217 keep and 3 struck→strike — quoting each real heading line). It
reported **0 `decisions_affected` failures**. The copy was deleted. The only FAILs are the two
known `create: true` "already exists" lines, which are on the backlog.

Green: unit 40/40, integration 130/130, `test-plan-team.py` 184/184 (acceptance chain exit 0);
`test-plan-merge.py` exit 0.
