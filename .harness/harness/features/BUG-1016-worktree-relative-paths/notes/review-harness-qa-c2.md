# QA gate c2 — BUG-1016, pin 55c99a85 (validate c2)

**BLUF: PASS.** Matrix floor met (`unit` satisfied), both task verifies and the standing unit runner exit 0 on my single run, the amended BRIEF predicate matches the unchanged code, every automated SC-01..06 maps to a named red-first case in the retained main-session receipt. One low advisory coverage gap (quote leg of the amended predicate). Settled c1 F1 (SC-06 red-first) and F2 (receipt shape) are not re-raised.

## Measured identity facts
- `feature.json` review_sha = `55c99a856321ef9d059b144b6ee2ac2bf1f75096`. Worktree HEAD = `3cc20f05` (re-pin commit; 55c99a85 is an ancestor, `merge-base --is-ancestor` exit 0). HEAD never moved by me.
- Canonical range: `git merge-base main 55c99a85` = `af2a958ab06c0d6fc026b363b59fc3147e3982f1` → `af2a958a..55c99a85`. Its non-feature-record changes: `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`, `DECISIONS.md`, `DECISIONS-INDEX.md` (plus feature-dir notes/state and `.harness/notes/grilling-…`).
- Lead's exact command `git diff --stat 8211687f 55c99a85 -- .omp tests .harness/harness/docs`: **empty output, exit 0**. So c1's pin and c2's pin are byte-identical on source/tests/docs; the only c1→c2 delta is the BRIEF amendment (b011c90f) and feature record.
- `git diff --stat 55c99a85 -- .omp tests .harness/harness/docs` (worktree vs pin): **empty, exit 0** → files I ran are byte-equal to the pin. `git status --porcelain` empty.
- Amended BRIEF at pin (`git show 55c99a85:<FD>/BRIEF.md`, Constraints): "classify each path-list entry independently, judging the entry after trimming surrounding whitespace and removing one surrounding pair of double quotes … relative when nonblank, node:path.isAbsolute false, first character not `~`, no leading `[A-Za-z][A-Za-z0-9+.-]*://` scheme. A rooted entry keeps its surrounding whitespace and quotes. Preserve explicit excluded entries verbatim… Only omitted/undefined/null paths default, only for grep, glob and ast_grep." plan.yaml approval: approved (molchairuangutai, 2026-10-04); amendment note present.
- **Code vs amended predicate (verified, not assumed)** `.omp/extensions/harness-hooks.ts:354-361` `rootTarget`: `target = raw.trim().replace(/^"(.*)"$/, "$1")`; returns `raw` when `!target.trim() || isAbsolute(target) || target.startsWith("~") || URI_SCHEME.test(target)` (URI_SCHEME `:269` = the BRIEF regex); else inserts `root/` at `raw.indexOf(target)`, so surrounding whitespace and quotes survive. Default-path set `ROOT_DEFAULT_TOOLS = grep, glob, ast_grep` (`:369`), applied only for undefined/null (`:387-388`). Predicate and code agree; R1 is closed by the amendment, no code change.

## Phase 1 (BRIEF/plan only)
Expected tests: per-tool rooting ×6; list entries; edit section/MV incl. multi-section and quoted-with-space; omitted/null defaults + blank passthrough; resolver authority (unique, no-match, ambiguous, error/unusable, prose spoof, siblings, cache); absolute/~/URI untouched + BUG-2003 pre/post incl. mixed edit; silent success, main/Bash untouched; amended predicate legs (trim, quote strip, ~/scheme/absolute classification after strip). All present except the amended predicate's quote leg, which is only partly pinned (G1).

## Matrix (`.harness/harness.json`, control plane)
- T-01 `change_type: bugfix`: `always: []`; `unit` when `touches_runtime_code` → true (`harness-hooks.ts` is runtime adapter in the range); `integration` when `fix_confined_to_tests_and_contract_docs` → false; `__bug_class__`/`match_bug_class` unresolved placeholder (repo G-08), fires nothing.
- T-02 `change_type: docs`: `always: []`; no kind.
- Required kinds: `unit` only. Other kinds: functional/eval excluded (DEC-187), integration not triggered, component/ui/typecheck unresolved and not in matrix, four `locally_run` probes' `detect` surface (`tests/manual/**`) untouched by the range → no recorded run needed.
- Standing honest gap: no TypeScript typecheck runner (BRIEF Verification gaps sanctions it); SC-07's TS side is inspection.
- `matrix_ok: true`.

## Gate execution (mine, once, `env -u HARNESS_AGENT_TYPE`, worktree)
| Check | Result |
|---|---|
| T-01 `python3 tests/unit/test-omp-hooks.py` | exit 0; bun: **123 pass / 0 fail**, 545 expect(), 1 file, 4.99s |
| T-02 `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout \| diff - .harness/harness/docs/DECISIONS-INDEX.md` | diff exit 0, no output |
| Standing unit kind `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; 44 files, 8 workers, 11.48s; `PASS test-omp-hooks.py` present (line 1893 of captured output) — P-14 list membership confirmed; 760 `^PASS` lines (≠ case count, repo G-04). Known deliberate `FAIL BUG-1290` mutation prints (repo G-09) graded on exit code. |
Counts match c1 (123/0), consistent with code and tests unchanged between pins.

## Fail-first (receipt `notes/t01-receipts-main-session.md:8-24`: 109 pass / 14 fail vs unmodified adapter; assurance tier = retained receipt, not reproduced by me)
Test titles in the receipt matched to titles/lines at the pin:
| SC | named test (tests/unit/omp-hooks.test.ts) | pre-fix failure receipt |
|---|---|---|
| SC-01 | :1320, :1338, :1347 | receipt :8, :9, :10 `(fail)` |
| SC-02 | :1400, :1505 | :13, :20 |
| SC-03 | :1357 (red), :1369 (red; blank-passthrough control inside a new case) | :11, :12 |
| SC-04 | :1432, :1448, :1455, :1477, :1488, :1495 | :14-:19 |
| SC-05 | :1529 (mixed rooted+URI, red), :1505 | :21, :20; URI controls pass pre-change (receipt :26) |
| SC-06 | :1382, :1545 controls (passed pre-change, correctly labelled); governed rewrite path red via the shared cases above | controls :26; rewrite red :8-:21 — settled, not re-raised |
Mutation proofs (receipt :30: 7 mutants each reddening ≥1 case) are present-state, lower tier than natural RED (O-03).

## Own perturbation (pinned checkout, restored; pins removed)
Two mutants of `rootTarget` classification at 55c99a85, each run against `omp-hooks.test.ts` in a disposable pin checkout:
1. drop the quote-strip (`raw.trim()` only): **1 fail** (the quoted-MV case :1400).
2. classify absolute/~/scheme on `raw.trim()` instead of the unquoted target: **1 fail**, at :1429 (idempotence re-run of an already-rooted quoted MV `"/wt/…/with space/c d.md"` gets rooted twice).
So the quote leg for **relative** (quoted MV) and for **absolute** (incidentally, via the idempotence assertion) is pinned. Both mutants are caught by the same single test.

## Findings
- **G1 · severity low · kind substance (advisory, not must_fix) · T-01 · amended-predicate quote leg thinly pinned.** No test feeds a quoted `~`, quoted `scheme://`, or any quoted/whitespace-padded-quote entry to a *path-field* tool (read/grep/glob/write/ast_grep/ast_edit); quoting is exercised only by one quoted MV destination in the edit case (:1405) and, incidentally, its idempotence re-run (:1429). Concrete failure: a regression that classifies the quoted `"~/x"` or `"agent://x"` entry after only trimming (so it is rooted into `root/"~/x"`) would pass the whole suite; the tilde/scheme legs of the amended predicate rely on the unquoted-entry cases (:1338-:1345, `"; ~/h"`) alone (P-06). Current code behaves per the amended BRIEF (verified by reading `:354-361`); this is residual risk, not a defect. Recommendation: main session (DEC-174 lane, T-01) may add a quoted-entry row to :1338 at its discretion; no fix hosted here and I do not block on it.
- No new must_fix. c1 F1/F2 stay dismissed. Simplify F1 (rootedHooks vs governedUriHooks duplicate) and `ast_edit` mutation-set omission (receipt :39) are operator-backlog / pre-existing, not re-raised.

## SC trace
| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated/unit | :1320,:1338,:1347; red-first receipt :8-10; 123/0 |
| SC-02 | met | automated/unit | :1400,:1505; receipt :13,:20 |
| SC-03 | met | automated/unit | :1357,:1369; receipt :11-12; explicit-blank preserved by amended predicate |
| SC-04 | met | automated/unit | :1432-:1495 six cases; receipt :14-19 |
| SC-05 | met | automated/unit | :1529,:1505,:1382 controls; receipt :20-21 |
| SC-06 | met (settled F1) | automated/unit | :1382,:1545 + shared red-first cases |
| SC-07 | out of my method (inspection) | inspection | I confirmed only that DECISIONS-INDEX is generator-consistent (T-02 diff exit 0) and the adapter/predicate agree with the amended BRIEF text; DEC-251 prose judgement belongs to the inspection readers |

## Coverage gaps
G1 only (quote leg for ~/scheme on path-field tools).

## Principles applied
None cited from leaves (none read this run).

## Residual
Red-first evidence is the main-session receipt (retained excerpt); I did not rerun the unmodified adapter. Typecheck for TS is not available.
