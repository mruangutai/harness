# Code review — FEAT-22 docs layout migration — panel step `code`

**Verdict: PASS with notes. `must_fix: []`. severity_max: med (non-gating).**

Range measured, not quoted: `git rev-list --count 0f12f14..e26e628` = **5**,
`git diff --name-only 0f12f14..e26e628 | wc -l` = **32**. Matches the claim.

## Commits read (all 5; none `[harness:human]`)

- `e6e74c8` the atomic cluster (T-02–T-09, 29 files, verified via `git show --name-only` — 0 files
  under `docs/harness/`, 0 under the feature's own directory)
- `1246b06` logs only (2 files)
- `5faa832` T-10/T-11's boundary note (1 file)
- `0140dce` `[harness:simplify]` — post-signature hygiene pass under the operator-ruled #430
  process (`.harness/logs/2026-08-16.md:12-14`), not a plan task. Read in full; six files,
  comment/dedup only.
- `e26e628` the note's SHA line (1 file) — the pin

## What I executed, with counts

- **SC-06** (index byte-identical): ran `gen-decisions-index.py --stdout | diff -` against the
  committed file → **IDENTICAL**.
- **SC-07/SC-08** (both suites green): ran `run-unit-tests.sh --kind unit` and `--kind integration`
  directly, twice more via a background loop (4 total integration runs) → 0 `FAIL` lines every time
  but one (see the Info item below).
- **SC-09** (CI Layout gate's two real constraints): ran `layout_migration.py` myself → exit 0,
  `1 doc root(s)`, both surfaces `CLEAN — evidence migrated`.
- **SC-10** (survivor count/table): ran `git grep -lE 'docs/harness|"docs", ?"harness"' -- . ':!<FEAT-22 dir>' | wc -l` →
  **174**, matches the note. Ran the live-surface exact-count grep → `layout_fixtures.py:3,
  layout_migration.py:6, test-check-domain.py:1, test-check-state.py:1, test-layout-migration.py:1`
  — exact match to T-10's table.
- **T-03's own verify**, re-executed clause by clause against HEAD: 3 of 4 pass (migrated-form
  regexes, the withdrawn `holds no...entry anywhere` phrase, the three-climb symlink literal, the
  `guide.md` anchor+grantor awk); **1 fails** — see must-not-gate finding below.
- **Probe 1** (`templates/plan.yaml`): one-line literal substitution in a comment
  (`docs/harness/DECISIONS.md` → `.harness/harness/docs/DECISIONS.md`), nothing else touched. Does
  not propagate the argumentless `check-expertise.sh` pattern (that pattern lives in this feature's
  own `plan.yaml:927`, not the template, and is a separately-disclosed, already-ruled item — see
  "Already disclosed" below).
- **Probe 2** (fail-open/vacuous-green across the 17 `bin/` files whose walk/glob root moved):
  `test-no-distribution.py` case4's docs walk was widened to two roots and paired with a positive
  control, `case4_control_docs_walk_reached_decisions`, confirmed present and passing in the
  executed suite. `test-layout-migration.py` case 1 already required non-zero feature-dir/reader
  counts; case 21 (new) checks the `docs: CLEAN — evidence migrated` string but does **not**
  independently assert the doc-root count numerically — confirming qa's already-routed SC-09 label
  finding, not new. No other walk/glob root in the diff changed without a non-zero-count guard.
- **Probe 3** (em-dash literal, non-test consumers): grepped `.claude/skills/harness/bin/*.py`,
  `*.sh` excluding `test-*` for `CLEAN — evidence` and `evidence migrated|evidence legacy` →
  **zero non-test matches**. `check-state.sh`'s INV-27 block reads `layout_migration`'s structured
  `.verdict` attribute (`"MIXED"`/`"CANNOT_VERIFY"` strings compared via `==`, not the composed
  em-dash summary line) — verified at `check-state.sh:1282-1322`. No retyped-hyphen exposure in this
  diff.
- **Probe 4** (`test-check-domain.py:789`'s failure mode): the assertion is
  `"harness-documentor" in r_live.stdout.split()`. Traced `check-domain.sh --resolve`'s emission
  (`check-domain.sh:250-256`): a regression to under-granting prints the literal token `NOBODY` and
  the assertion **fails loudly**. A regression to *over*-granting (an extra agent matching alongside
  the correct one) would **not** be caught — membership, not equality — consistent with, and
  confirming, the already-accepted "missing direct assertion" residual. Not new.

## Findings

1. **[med, non-gating]** `.claude/skills/harness/bin/harness_boundary.py` — `0140dce`'s "comment
   truth" pass silently falsifies T-03's own signed verify clause. T-03's verify requires the word
   `redundant` (case-insensitive) within the 20 lines above `HARNESS_CONTROL_PLANE = [`
   (`plan.yaml` T-03 intent: *"USE THE WORD redundant... an addition is invisible to every check in
   this plan without it"*). `0140dce` rewrote that clause from "logically REDUNDANT" to "logically
   dead," dropping the word. I ran the exact grep from the signed verify against HEAD:
   `grep -B20 'HARNESS_CONTROL_PLANE = \[' harness_boundary.py | grep -qi 'redundant'` → **no match,
   T-03's verify would fail if re-run today.** The underlying decision (D-02 / DEC-189 amendment 1,
   which still says "redundant") is semantically intact — this is a word-level regression in a
   comment, zero behavior change, confirmed by re-running both suites green. It is a genuine,
   *unrecorded* deviation from signed plan text: STATE.md records three execution-time deviations
   explicitly (POST-MOVE HEAD, the SHA-line commit split, T-11's scope) but not this one. Failure
   scenario: a future contributor who diffs a task's `verify:` clause against HEAD to audit whether
   completed work still holds — the exact practice `harness-code-review`'s DEC-169 absence-assertion
   discipline and this feature's own T-10 depth-sweep methodology teach — hits a red that is
   cosmetic, not a regression, and has to spend time distinguishing the two with no record to point
   at. Routes to the operator, main-session-direct (`harness_boundary.py` is a carve-out by content
   under DEC-193, D-03): either restore the word or record the deviation the way the other three
   are recorded. Not a fix I am drafting.

2. **[low, non-gating]** `.claude/skills/harness/bin/test-check-domain.py:790-794` — the same
   `0140dce` pass left a garbled comment. Before: two sentences ("...CI requires on main. Under a
   glob-keyed rule this prints NOBODY, which is precisely the defect that would redden CI. Since
   FEAT-22's T-02..."). The diff deleted only the middle sentence's body, not the "Under a
   glob-keyed rule this" fragment that opens it, leaving: *"...CI requires on main. Under a
   glob-keyed rule this Since FEAT-22's T-02 the documentor holds..."* — a sentence that does not
   parse. Confirmed by direct read of the current file. No functional effect (comment only,
   assertion unchanged), but it sits in a commit whose own message certifies "comments told true."

3. **[info, non-blocking]** One integration-suite run (out of six executed across this review)
   showed `test-check-domain.py` not present in the `PASS` set via a `re.findall` scripted check;
   five other executions (direct run, `run-unit-tests.sh --kind integration` ×2 in-session, ×2 more
   via a background loop, plus one more direct `python3 test-check-domain.py`) were clean. Not
   reproduced; suspected mechanism is resource contention across back-to-back subprocess-heavy
   suite runs (several `hook()` calls carry `timeout=20`) rather than a real flake in the code under
   review — but recording the one anomalous observation rather than smoothing it away, per the
   don't-falsify-the-record rule. Does not affect the verdict.

## Already disclosed — confirmed, not re-raised as news

- `plan.yaml:927`'s argumentless `check-expertise.sh || exit 1` (T-07's verify): confirmed at
  source (`check-expertise.sh:18` exits 2 on empty argv) — this is `STATE.md`'s own Q1/Q2, already
  the operator's call, does not gate. I did not re-file it.
- `harness_boundary.py`'s "two of the four" clause (is_control_plane_target docstring, post-simplify
  still says "two" where DEC-189 amendment 1 says "one"): on the ACCEPTED RESIDUALS list, not
  re-litigated.
- `0140dce`'s weakening of `test-no-distribution.py` case4's control-check failure MESSAGE (from
  `f"walk visited {len(walked)} file(s), none of them DECISIONS.md"` to a plain string): the boolean
  predicate is unchanged (`saw_decisions` == the old `any(...)`), confirmed by reading both
  versions; already carried in `STATE.md`'s "Open findings."
- `audit-decisions.py`'s "E amendment sits outside its parent's section" for `DEC-189 amendment 1`
  (inside `DEC-194`'s section): reconstructed the audit at `0f12f14` in-memory — E-count was 4 then,
  is 5 now, so T-08 does add one instance of this class. But it is the SAME class the tool's own
  docstring names as a pre-existing, expected property of append-only amendment placement
  (precedent: "DEC-142 am.1 inside DEC-173"), and the total (10) matches `STATE.md`'s disclosed "10
  unowned inconsistencies." Not new, not re-raised.
- `test-layout-migration.py` case 21's entailed-not-asserted doc-root count: confirms qa's SC-09
  label finding (already routed to the goal-check), not independent news.

## Stage 1 — spec compliance

Every file in the 32-file union traces to a task (T-01–T-11) and a REQ/D. No scope creep found —
`0140dce`'s six files are outside the T-01–T-11 task list but are the operator-ruled #430 hygiene
process, not an unrequested change; its own STATE.md-recorded self-review ("harness_boundary.py's 20
changed lines are comment and docstring text, zero executable lines") is accurate but incomplete —
it missed finding 1 above, which is exactly why an independent pass still has value here. No
omissions found against REQ-01–REQ-07. Values match: SC-01 (5 docs, org.html included, 0 legacy
tracked — verified via `git ls-files`), SC-04 (29-file atomic commit, no `docs/harness/` in tree, no
feature-dir sweep — verified via `git show --name-only`), SC-05 (standing `--resolve` case present
and passing), SC-06 (byte-identical, confirmed), SC-12 (DEC-189 amendment 1 present, exact spans
confirmed by direct read, `git diff --find-renames` shows a clean 99%-similarity rename with a
pure append — no other DECISIONS.md content touched).

## Stage 2 — code quality

Findings 1–2 above are the only quality issues found, both low/med, both comment-only, both
introduced by the post-signature simplify pass rather than the plan tasks themselves. Everything
else read as consistent with existing codebase convention (structured-attribute checks over string
literals in `check-state.sh`, positive controls paired with widened absence sweeps, exact-count
survivor tables over exclusion lists).

## Probe hygiene

Read-only throughout. One blocked write attempt (a `bash-write-guard.sh` redirect denial) when I
tried to capture `gen-decisions-index.py --stdout` to a scratch file — corrected to pipe directly
into `diff` with no intermediate file. `git status --porcelain | grep -v '^??'` is empty at
finish — only pre-existing untracked feature-directory notes remain, none of them touched by me.
`git rev-parse HEAD` still `e26e628`.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both fresh findings from the post-signature simplify pass are comment-only with zero behavioral impact; every executable SC I could run is green; PASS with notes, nothing gates.
  severity_max: med
  findings: 3
  must_fix: []
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/harness_boundary.py, ref: D-02 }
  reviewed: "0f12f14..e26e628"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-22-docs-layout-migration/notes/review-harness-code-reviewer-2026-08-16-13-panel-validator.md
```
