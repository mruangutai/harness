# QA gate — FEAT-2229 c4 (pin 46d0c4bce7cec18e0aabec56a490981496970cc0)

**BLUF (amended, contract reconciliation): ESCALATE, not PASS. Two MANDATORY must_fix test gaps (T-01 / SC-02), not advisory; plus two NEW CLASS advisories.** Measured facts are unchanged: matrix_ok true; unit and integration `satisfied`; T-01 verify, full unit and integration runners exit 0; code-grade `--base dfa52536 --head 46d0c4bc` PASSING 97, no failing function. F3-I's three cases are RED 108/113 at d1fd4aa1 and GREEN 113/113 at the pin (own reproduction). Every CommonMark boundary the ruling names behaves correctly through the real CLI (40-case probe). Why the gate does not clear: the operator ruling (notes/answers-2026-11-21-f3i-ruling.md) requires each of its rules "written test-first with its own actual-CLI case". Findings 1 and 2 are the ruling's own rules 4 (closer same-character) and 3 (backtick-info limited to backtick openers) with no case of their own: mutants M6 and M8 survive 113/113. That is unmet within-ruling acceptance, so it is must_fix; findings 3 and 4 are outside the four ruled rules and stay advisory. Why ESCALATE rather than FAIL: the digest validator refuses FAIL when suite, matrix and failure count are all green, and refuses a PASS that hides mandatory gaps; the routing decision (dev test-only fix vs. operator waiver of the two legs) belongs to the tier above. The original PASS label contradicted the report's own must_fix classification. Only my own evidence has examined this fix beyond the dev receipt; no second-reviewer independence applied by me.

## Pin, equivalence, environment
- Pinned via pinned-checkout.py (persona harness-qa, run r-20261121-validate-c4-qa): HEAD 46d0c4bc, clean. Removed on return. Review range dfa52536..46d0c4bc.
- Equivalence MEASURED: `git diff --quiet ef269da2 46d0c4bc -- . ':!.harness'` -> identical; `git diff --name-only ef269da2 46d0c4bc` = feature.json, plan.yaml only. Gates still run at the actual pin.
- Every command `env -u HARNESS_AGENT_TYPE` (also -u HARNESS_CONTROL_PLANE_ROOT/-u HARNESS_FEATURE_TREE_ROOT, G-07/G-11). Phase 1 (BRIEF + plan + ruling, before source), expected: SC-01 unit shape; SC-02 CLI each failure + controls; SC-03 era both sides; SC-07 per-owner; plus ruling: one actual-CLI case per rule (indent 0-3 for fence open/close/heading; backtick-info; closer char/length/whitespace-only suffix; fenced heading never heading). Phase-1 gap: rule 4's closer-character leg and the tilde-info-backtick boundary have no case (below).

## Matrix
T-01 cross_module -> always unit + integration (active both); T-02/T-03 docs -> []. functional/eval excluded (DEC-187); locally_run/component/ui/typecheck untouched. Each required kind exercises T-01 directly (P-04): unit = schema contract; integration = real plan-merge CLI.

## Commands (at pin)
| Command | Exit | Result |
|---|---|---|
| T-01 verify (`set -eu`; unit schema; integration dispositions) | 0 | 40/40 ; 113/113 |
| `run-unit-tests.py --kind unit` | 0 | OK; 62 files; 24.1s |
| `run-unit-tests.py --kind integration` | 0 | OK; 89 files; 119.8s; test-plan-decision-dispositions 43.0s under load (advisory, ruled earlier; ~12-20s alone) |
| `code-grade.py --base dfa52536 --head 46d0c4bc` | 0 | PASSING 97, no FAIL; `_opener` cyc 2/cog 2/ABC 4.0 grade 5 vs bar 4; `_fence_after` cyc 5/cog 4/ABC 12.8 grade 4; `_real_headings` cyc 4/cog 6/ABC 8.1 grade 4 |
(T-02/T-03 verifies were not re-run: c3 ran them at ab1e4246 and the pin differs from it only in check.py, its test and docs/receipts; test-plan-team 184/184 is inside the integration runner exit 0.)

## Fail-first (natural RED, semantic, signature-bearing)
- **F3-I** (red-first-T-01.md c3 table inspected: claims 108/113, three named cases). Reproduced: `git archive d1fd4aa1` into a mktemp dir (check.py byte-equal to d1fd4aa1's) overlaid with the pin's integration test; no mutation, current HEAD never moved. Exit 1, **108/113**; FAIL lines: `rule 1 closer`, `rule 1 opener` (case_overindented_fence_lines_are_content), `rule 2: a 3-space DEC-11 heading ends DEC-10's section`, `rule 2: a 3-space heading is DEC-11's own heading` (case_heading_indentation_limits, +1 detail line), `rule 3: the spoof clause fails the DEC-10 row` (case_backtick_info_string_cannot_open). Pin: 113/113. Numbers match the receipt.
- Controls in each case pass on both trees (genuine DEC-10 clause), so the reds are spoof-acceptance, not fixture breakage.
- **SC-01 / SC-02 / SC-03 / SC-07** re-measured at base dfa52536 with the pin's tests overlaid: unit 13/40 exit 1; integration dispositions 52/112 exit 1; test-plan-team 31 of 154 FAILING exit 1 (matches c2 note 13/40 and 31 of 154; the dispositions file has since grown, hence 52/112 not 44/97). All green at the pin.
- Prior F1/F2/F3 and F-01 reds stand from c2/c3 (source equivalence); not re-run.

## CLI boundary probe (real `plan-merge.py check`, temp fixtures, no product writes)
Imported the pin's test fixtures; 40 probes; spoof clause under a fake `## DEC-10` placed after the line under test, genuine DEC-10 later; expected outcome per CommonMark.
- Correct (all): closer 0/3-space closes, 4-space, tab, 2-space+tab do not; trailing space/tab/CR closes; too-short closer (```` opener, ``` closer; ~~~~ vs ~~~) does not; longer closer closes; closer with info (`` ``` x``) does not; ~~~ vs ``` mismatch does not (both ways); opener 0/3-space opens, 4-space and tab do not; backtick opener with backtick in info (also after a space) and a 2-tick run do not open; **tilde opener with a backtick in info does open**; heading 0/3-space and `#<TAB>` real, 4-space, tab-indented, `##DEC-10` (no space), 7 hashes not; unclosed fence runs to EOF; genuine heading after a fenced spoof is found; blockquote-fenced spoof stays non-heading. (My "EOF unclosed" probe flagged DIVERGE only because DEC-10's own section legitimately spans to EOF; probe expectation error, not a defect; the suite's rule 5 case uses the correct DEC-11 shape.)
- Live corpus: pinned DECISIONS.md 8326 lines, 220/220 `## DEC-` headings real, 0 indented fence lines, 0 list/quote fences, none of \v \f \x1c-\x1e \x85 \u2028 \u2029 \u00a0 \u3000 \r \t.

## Mutation proof at the pin (temp copies of `git archive 46d0c4bc`; each runs the integration file)
| Mutant | Result |
|---|---|
| M1 fence indent 0-3 -> 0-4 | RED 111/113 (rule 1 closer, rule 1 opener) |
| M2 heading indent 0-3 -> 0-4 | RED 112/113 (rule 2 4-space case) |
| M3 backtick-info rule removed | RED 112/113 (rule 3) |
| M4 closer may carry info | RED 112/113 (info-string run case) |
| M5 closer length ignored | RED 110/113 (nested-fence, DEC-11 runs past examples) |
| M7 fences never open | RED 102/113 |
| **M6 closer character ignored** (``` closes ~~~ and vice versa) | **GREEN 113/113 - survives** |
| **M8 tilde info wrongly refused (rule applied to ~ as well)** | **GREEN 113/113 - survives** |

## Findings
1. **test-gap, medium, T-01, SC-02, WITHIN RULING -> must_fix.** Rule 4 requires the closer to be the opener's character. The pin's behavior is correct (probe above) but no case pins it: mutant M6 passes 113/113. Ruling: "each rule written test-first with its own actual-CLI case"; this leg has none (red-first table calls rule 4 "already green (landed)" and cites only the info-suffix and fenced-heading cases). Recommendation: one CLI case, ```` ```text ```` fence holding `~~~` then a spoof `## DEC-10`, plus tilde fence holding ```` ``` ````, spoof must fail.
2. **test-gap, low, T-01, SC-02, WITHIN RULING -> must_fix (same edit).** Rule 3 limits the no-backtick-in-info rule to backtick openers; M8 (apply it to tildes too) survives. A tilde fence with backticks in its info is legal and would be dropped, exposing its fenced headings. Recommendation: one CLI case with `~~~ a`b` fence holding a spoof DEC-10 heading.
3. **NEW CLASS - CommonMark line-terminator / whitespace set, low advisory, T-01, SC-02; outside the four ruled rules; not folded into F3-I.** `check.py` splits with `str.splitlines()` and closes on `not info.strip()`. Python splits on \v \f \x1c-\x1e \x85 \u2028 \u2029 and strips NBSP/U+3000/FF, none of which CommonMark treats as line break or spaces/tabs. Reproduced via the CLI: a content line `x<U+2028>```` inside an open fence, or a closer followed by U+00A0/U+3000/FF, closes the fence here, so a following spoof `## DEC-10` heading is accepted (and the genuine one then also resolves, so the spoof gate fails open). Pre-existing since c1; live DECISIONS.md contains none of these characters, and exploitation needs write access to DECISIONS.md. Recommendation: backlog, or scanner-only fix splitting on \n/\r\n/\r and stripping only space/tab; decide at lead/operator tier.
4. **NEW CLASS - container-block fences, low advisory, same task/SC; outside the ruled rules.** A fence inside a list item (`- ```text` / indented continuation) is not recognized as an opener while its 2-space `  ```` line is, so an unclosed phantom fence can swallow the real DEC-10 heading and the list-fenced spoof heading resolves (probe: spoofPass and realPass both True). Blockquote-fenced input happens to be handled. Corpus has no list/quote fences. Recommendation: backlog; the single-scanner design cannot track containers without becoming a Markdown parser.

## SC -> covering test -> evidence
- SC-01 tests/unit/test-decision-disposition-schema.py (red 13/40 at dfa52536).
- SC-02 tests/integration/test-plan-decision-dispositions.py: case_overindented_fence_lines_are_content:346, case_heading_indentation_limits:356, case_backtick_info_string_cannot_open:373, case_unclosed_fence_runs_to_end:380, case_info_string_run_does_not_close_a_fence:317, case_fenced_heading_is_not_a_section:281 (F3-I red 108/113 at d1fd4aa1; 52/112 at base).
- SC-03 same file era/creation/reservation cases (red at base).
- SC-07 tests/integration/test-plan-team.py (red 31 of 154 at base).
- SC-04/05/06 `verify: inspection`, not graded by QA.

## Assurance limits
- Probe is the pin's scanner via the CLI versus my reading of CommonMark 0.30 indentation/closer rules, not a reference parser run.
- Static prompt tests prove presence at owner, not agent obedience.
- bash-write-guard denied redirects into feature/tmp paths (Q-01 reproduces); evidence was kept on stdout and in this note, mutation copies built with git archive/tar and python in mktemp dirs, then removed.
