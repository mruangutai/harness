# Review — harness-code-reviewer — BUG-1128 panel c3 (review_sha `20775866`)

**VERDICT: FAIL.** N1, N2, N3, N5 are genuinely closed, each confirmed by direct mutation or a
byte-level probe, not by re-reading the docstring. But the boundary hunt found TWO NEW exit-0
silent-corruption paths — the same class this whole feature exists to close — reachable through
the tool's own documented `--show` → `--value-file` workflow, neither previously reported. Real
motivating case (FEAT-46's actual `D-05.because`, `D-14.because`, `T-01.verify`) round-trips
perfectly; the corruption needs shapes FEAT-46's plan does not currently contain, but the tool is
used by more amend calls than FEAT-46's. `code_grade: fail`, and it is worse than disclosed: the
panel was told about 4 residue functions in `plan-merge.py`; a 5th and 6th exist, one of them a
NEW `test-plan-merge.py` regression this cycle's own additions caused. All experiments ran on
`/tmp/bug1128-c3/` copies against the real binary at `20775866`; the FEAT-46 plan was copied to
`/tmp` before any read.

## Stage 1 — spec compliance

Issue #1128 asked for: replace-by-field under the same lock/splice discipline, reach
`decisions:` as well as `tasks:`, refuse a nonexistent id, fail closed on ambiguity/unreadable
base. All four are met — `AMENDABLE_KEYS = ("tasks", "decisions")`, `_sole_item` refuses
duplicates and non-lists, V4's unparseable-base guard is inside the try. No scope creep: `_die`
and the `_verify_amend`/`_schema_error` extractions serve the stated fail-closed requirements,
nothing wider. No omission found against the issue text.

**Cycle-1 findings, closed-or-not, with mechanism (not claim):**

| id | status | mechanism, verified how |
|---|---|---|
| N1 | **CLOSED** | `_trim_tail` (plan-merge.py:1042) trims trailing blank/comment lines off the captured span before splicing. Verified live: a comment indented DEEPER than the field key, positioned after a plain field's body, survives a full replace with the sibling `approved: true` untouched (my probe 6). |
| N2 | **CLOSED, mutation-confirmed** | `case_amend_v3_identity_check_is_live` now calls `_verify_amend` DIRECTLY. Built a compile-checked mutant deleting the `if item.get(field) != want: raise` comparison (`/tmp/bug1128-c3/plan-merge-mutant-n2.py`) and ran the test's own assertion logic against it: `raised=None` — the mutant is NOT refused, so the current test would fail on it. The vacuous cycle-0 tautology is gone. |
| N3 | **CLOSED as named** | `_amend_show`/`_dedent_value` emit the bare VALUE, not the block. Confirmed on plain and block fields (my probes throughout). Two NEW gaps found in the value-derivation itself (below) are outside what N3's fix promised — N3 was about block-vs-value, not about null/CRLF fidelity. |
| N5 | **CLOSED, mutation-confirmed** | `_schema_valid_plan()` now genuinely satisfies `REQUIRED_TASK_FIELDS`. Built a compile-checked mutant removing the whole do-no-harm branch (`/tmp/bug1128-c3/plan-merge-mutant-n5.py`) and ran it against the schema-valid fixture: the mutant WRITES `title: ''` at exit 0 (schema-invalid, unrefused); the real code at `20775866` refuses the identical input at exit 8, plan byte-identical. |
| N1b (disclosed, not panel-found) | **CLOSED** | `_trim_tail(..., comments_are_document)` — False for block scalars, so a `#` line at the END of a `\|` body is kept as content. Verified: `--show` on a block whose last line is `# a shell comment` returns it as part of the value, matching `yaml.safe_load` exactly. |

## Stage 2 — the boundary hunt (all 8 assigned probes, real binary, real exit codes)

| # | probe | result | exit |
|---|---|---|---|
| 1 | `>` folded scalar | `--show` MISREPORTS the value (prints unfolded `"line one\nline two\n"`; real parsed value is `"line one line two\n"`). An identity replace using that misreported value REFUSES cleanly, file byte-identical. Any `>` replace refuses by construction (`_render_field` re-emits unfolded lines under a folding header, which reloads folded — can never equal `want`). **Fail-closed, not corrupting.** | show 0 / replace 5 |
| 2 | `\|2`, `\|-2`, `\|2-`, and `\|` with body indented 4 not 2 | `\|2` (indicator, no chomp): round-trips correctly, identity succeeds. `\|-2` (chomp-then-digit, STRIP): `--show` misreports (shows a trailing `\n` STRIP already removed); identity replace REFUSES, file unchanged. **`\|2-`** (digit-then-chomp, does NOT match `BLOCK_HEAD_RE`): **CORRUPTS.** See must_fix M1 below. Body indented 4: `--show` misreports (double-counts the hardcoded `indent+2` assumption, prints 2 stray leading spaces per line); an identity attempt using that misreported value REFUSES; a correctly-valued replace SUCCEEDS but silently RE-INDENTS the body from 8 spaces to 6 (`indent+2`), contradicting the "preserves the original field's form" docstring cosmetically — content unaffected. | show 0 / replace 5 or 0 (see M1 for `\|2-`) |
| 3 | body line at exactly the key's indent | Constructed the one YAML-legal instance (`verify: \|` immediately followed by a sibling key at the SAME indent as `verify:` — an empty block, per PyYAML). `_block_scalar_end`'s `<=` cutoff matches PyYAML exactly: `--show` correctly reports `''`, the sibling survives, and a replace with new content succeeds cleanly, sibling untouched. **Works, boundary is correct.** | show 0 / replace 0 |
| 4 | CRLF line endings | `--show` MISREPORTS a `\|` value on a CRLF file: prints `"line one\r\nline two\r\n"` while `yaml.safe_load` returns `"line one\nline two\n"` (YAML normalizes line breaks at parse time; the raw-line dedent does not). An "identity" replace using that misreported (but self-consistent) value SUCCEEDS at exit 0 — but the write emits the body with `_render_field`'s hardcoded `\n` — the replaced field's body silently converts from CRLF to LF while the rest of the document stays CRLF, producing a mixed-EOL file with no value-level change. **Should_fix, not corrupting content, but a silent unasked-for format change under a clean receipt.** | show 0 / replace 0 |
| 5 | last field of last item of last top-level key (`_item_range`'s `hi=len(lines)`, `_trim_tail`'s floor) | Plain and block variants both work correctly, with and without a final trailing newline in the source file; the tool even restores a missing trailing newline on write. **One real, distinct defect found here**, not about corruption of the plan: when the *dedented value itself* lacks a trailing newline (source file has none), `_amend_show` glues the `sha256:` line directly onto the end of the printed value with NO separator (`sys.stdout.write` then `print`, no newline in between). Demonstrated: `'...after thissha256: 706436f7...'` as ONE line. Any caller line-splitting `--show`'s stdout (exactly the pattern this review used throughout) gets a corrupted value or a broken hash extraction — a real interface defect, not disk corruption. **Should_fix.** | show 0 |
| 6 | comment indented DEEPER than the field key, after the field's body | Works correctly for plain scalars regardless of the comment's own indent — `_trim_tail`'s trim doesn't check indent, only blank/comment status. Verified live: an 8-space-indented comment after a 4-indent `verify:` survives a full replace, `approved: true` untouched. For BLOCK scalars a comment deeper than the key is correctly treated as CONTENT (it's genuinely inside the block per YAML), not a defect. | replace 0 |
| 7 | empty value: bare `field:` and `field: \|` with empty body | **`field: \|` empty body: works correctly** (`--show` and replace both correct; a cosmetic extra blank line appears on an identity round trip, harmless). **Bare `field:` (YAML `null`): genuine defect.** `--show` prints an empty value ('', not distinguishable from null) and a straight `--show` → `--value-file` round trip — the tool's own documented discipline — SILENTLY changes the reloaded type from `None` to `''` at exit 0, clean `AMENDED` receipt. `_verify_amend` cannot see it: both sides of its comparison are the empty string, self-consistently. See must_fix M2. | show 0 / replace 0 (silently wrong) |
| 8 | single-line field, `first+1==last` | Works correctly, mid-document and at EOF; `_trim_tail`'s loop correctly never runs (`last-1==first`), never risking the field's own line. | replace 0 |

**Real motivating case, run against a COPY of FEAT-46's actual plan.yaml** (never the live file):
identity replace of `D-05.because`, `D-14.because` (huge single-line plain scalars) and
`T-01.verify` (a real block-scalar shell/python script) — all three leave the file byte-identical
(`diff` empty, sha256 unchanged). **Scanned all 50 real `\|` fields in FEAT-46's plan: zero use a
non-bare header (`\|2`, `\|-`, `>`, etc.), zero CRLF, zero body-indent irregularities, zero
trailing-comment bodies.** So M1 and M2 below are not reachable through FEAT-46's specific eight
staged blocks as currently written — the panel's actual gating job (can this verb do FEAT-46's
job safely) is answered **yes** for the content that exists today. They ARE reachable by any
other author or any future amend call, which this tool exists to serve generally.

### must_fix (severity high)

**M1 — `BLOCK_HEAD_RE`'s incompleteness produces DIRECT-TARGET CORRUPTION, not merely a
fail-closed miss.** c2's S1 found that `\|2-` and a header-with-trailing-comment both miss
`BLOCK_HEAD_RE` and characterized the consequence as "fail-closed... but only incidentally"
because its repro used a DECOY (a separate real field elsewhere stays untouched, so the identity
check refuses). That characterization does not generalize: when the malformed-header field is
the field being amended DIRECTLY (no decoy), there is nothing else for the check to disagree
with. Reproduced live for BOTH shapes:
- `verify: \|2-` (2-line body) → `--show` returns the garbled plain-scalar text
  `'\|2- line one line two'`; feeding that back as `--value-file` succeeds at exit 0, and the
  file now reads `verify: '\|2- line one line two'` — the block structure, the two lines, and
  the header are all gone, permanently, under a clean `AMENDED tasks:T-01.verify` receipt.
- `verify: \|  # trailing comment on the header` (2-line body) → identical outcome:
  `verify: '\|  # trailing comment on the header line one line two'`.

Root cause: `_field_block` decides plain-vs-block via a single `BLOCK_HEAD_RE.match`; when it
misses, `_find_field_line`/`_plain_scalar_end` scan the header AND body as one multi-line PLAIN
scalar, `_dedent_value` folds them into one string, and `_render_field` writes that string back
as a quoted plain scalar — a complete, silent, one-way structural rewrite. Remedy is at
`BLOCK_HEAD_RE` itself (accept both indicator orders and an optional trailing comment) — the
same fix c2 recommended for S1, now justified by a HIGH rather than a should_fix consequence.

**M2 — a bare, null-valued field cannot survive the tool's own documented `--show` →
`--value-file` round trip; it becomes an empty string, silently, at exit 0.** `verify:` (nothing
after the colon) parses as YAML `null`. `--show` prints an empty line (indistinguishable from an
empty STRING). Doing exactly what `_amend_show`'s docstring recommends — pipe `--show`'s output
into `--value-file` — produces `verify: ''` after amend: reloaded type is now `str`, not
`NoneType`. `_verify_amend` passes because `want` (`""`, derived from the empty value-file) equals
`reloaded` (`""`, what got written) — the divergence from the TRUE prior value happened upstream
of the check, in `_dedent_value`, which has no representation for "no value at all" distinct from
"empty value." This is the exact discipline the feature exists to guarantee ("does this reload as
what was asked for") defeated by an ordinary, plausible input — any field that is present but not
yet filled in. Remedy: `--show` should mark a null distinctly (e.g. refuse `--value-file`
round-tripping for null fields, or print a sentinel), since raw-line dedenting genuinely cannot
recover the type without parsing.

### should_fix (severity med)

**S-CRLF — silent EOL conversion of the touched field on an otherwise-identity replace.** See
probe 4. Not corrupting content; produces a mixed-EOL file under a clean receipt. Remedy:
`_render_field` should reuse the document's detected line-break style rather than hardcode `\n`.

**S-glue — `_amend_show` can emit an unparseable two-in-one line.** See probe 5. When the
dedented value doesn't end in `\n` (file lacks a final trailing newline), the `sha256:` line has
no separator from the value. Remedy: always emit at least one `\n` before the `sha256:` line,
independent of the value's own content.

**S-reindent — a successful replace on a non-standard-indent block silently renormalizes to
`indent+2`, contradicting the "preserves original field's form" docstring.** Cosmetic; content is
unaffected; not corrupting, but the claim is now measurably imprecise for any block scalar not
already at the assumed indent.

**S1 (c2, carried) — status updated.** Both named shapes now measured as producing M1 rather than
"fail-closed incidentally." The nested-mapping-sibling-key sub-case c2 described is a THIRD
symptom of the same `BLOCK_HEAD_RE`/locate-loop gap; not independently re-tested this cycle since
the mechanism (and its fix) is identical to M1's.

## Stage 3 — N4 input: re-measured code grades

Ran `code-grade.py --base $(git merge-base origin/main 20775866) --head 20775866` myself (exit 1).
**6 blocking/reasoned records, not 4** — the dispatch's disclosure covered only the first four:

| function | file | cyclomatic | cognitive | ABC | grade | driver | result |
|---|---|---|---|---|---|---|---|
| `_item_range` | plan-merge.py:996 | 9 | 14 | 22.7 | 3 | cyclomatic+cognitive+abc | **FAIL, high** |
| `_find_field_line` | plan-merge.py:1095 | 7 | 11 | 15.7 | 3 | cognitive | **FAIL, high** |
| `cmd_amend` | plan-merge.py:1235 | 5 | 5 | 26.6 | 2 | abc | FAIL, med (reasoned) |
| `cmd_amend.transform` | plan-merge.py:1256 | 7 | 8 | 29.6 | 2 | abc | FAIL, med (reasoned) |
| `case_amend_n3_show_round_trips_into_value_file` | test-plan-merge.py:1515 | 8 | 2 | 26.2 | 2 | abc | FAIL, med (reasoned) |
| **`main`** | **test-plan-merge.py:1573** | 3 | 5 | **45.5** | **1** | abc | **FAIL, high** |

`_verify_amend` (plan-merge.py:344): grade 5, PASS. `_field_block` (plan-merge.py:1128): grade 4,
PASS. Both confirmed as the author claimed. `cmd_amend`'s improvement is real and reproduces
exactly: cyclomatic 11→5, ABC 42.9→26.6 (measured against the numbers cited to me). The author's
"below bar on cognitive" framing for `_item_range` is imprecise — its DRIVER is all three metrics,
not cognitive alone; `_find_field_line`'s driver genuinely is cognitive-only.

**The NEW item: `test-plan-merge.py:main`, grade 1 (worse than any plan-merge.py residue),
undisclosed to the panel.** Cyclomatic 3 / cognitive 5 — essentially no real branching — the
GRADE 1 is entirely ABC's call-count term, driven by the ~40 sequential
`case_whatever_it_is_called()` statements this file's `main()` has always used as its dispatcher,
now pushed over the edge by BUG-1128's own 19 new call lines (confirmed via diff: every one of the
`# BUG-1128` block's 19 lines is a `+` addition against `merge-base`). Reproduced with the exact
tool and range the digest-validator recomputes.

**Baseline, verified.** `apply_merge` (plan-merge.py:507, unchanged by this diff) is grade 1,
cyclomatic 53, cognitive 124, ABC 138.7 — confirmed exactly as the author cited. This is ~6x
`_item_range`'s cyclomatic and the file's pre-existing floor.

**Recommendation, not a ruling.** Two different things are on this list:

1. `_item_range` (unchanged three cycles running) and `_find_field_line` carry the ACTUAL
   locating logic this feature's safety depends on. I traced every branch of both while building
   the eight probes above, and every boundary I could construct for them (probes 3/5/6/8, plus
   the block-scalar-unawareness I checked by hand in `_item_range`'s raw `ITEM_ID_RE` scan)
   behaved correctly — the comprehension cost did NOT, in this review, hide a live defect in
   these two functions. The defects I found (M1, M2, S-CRLF, S-glue) live in the SIMPLER,
   already-passing `_render_field` (grade 4), `_dedent_value` (grade 4), and `BLOCK_HEAD_RE`'s
   own pattern completeness (not a graded function at all). Weighed against a file whose
   established floor is `apply_merge` at cyclomatic 53, I read this as a real but ORDINARY style
   deficit against an already-low bar, not a comprehension risk that is actively concealing a
   guarantee-bearing defect. `cmd_amend`/`cmd_amend.transform`'s grade-2 status is REASON-bearing,
   not blocking, and the reason (both duplicate the locate-then-verify sequence by design, same
   as cycle 0's F5) still holds.
2. `test-plan-merge.py:main`'s regression is a DIFFERENT kind of thing: it is new this cycle,
   entirely mechanical (zero real branching), and this exact shape has an EXISTING, ADOPTED fix
   in the same file family — `plan-merge.py`'s own `VERBS` table was built specifically to stop
   `main`/argument-registration from taking this same ABC hit (see its docstring:
   "EVERY VERB IS A ROW, NOT A PARAGRAPH"). Converting the flat call sequence into a
   `CASES = [...]` list plus one `for case in CASES: case()` loop is a same-cycle, near-zero-risk
   fix with a precedent already sitting in this repository. I recommend the lead require it this
   cycle rather than defer it — unlike `_item_range`, there is no safety-tradeoff argument for
   leaving it, only inertia.

## Verdict

`severity_max: high` (M1, M2) and `must_fix` non-empty → **FAIL**, independent of the N4
code-grade question. `code_grade: fail` (6 blocking/reasoned records; `_item_range` and
`_find_field_line` at high severity, unresolved for a 4th cycle running for `_item_range`).
