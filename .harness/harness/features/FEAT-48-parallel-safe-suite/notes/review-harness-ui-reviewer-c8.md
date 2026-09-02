# UI Review — FEAT-48-parallel-safe-suite — cycle 8 (Mode B, `e64e863e`)

**BLUF:** No rendered UI surface (measured, not assumed). The two operator-facing terminal
surfaces named in dispatch are both low-severity but real: `MUTATED <name>` names the file but
never says what changed about it, and a self-test's own `ERROR` trigger line prints unlabeled
into an otherwise-passing run. Neither gates. None of the five c7 findings sit in this lens.

## 1. Census (measured)

- `git diff --stat e64e863e~1..e64e863e`: 3 files, all `.py`, all under `.claude/skills/harness/bin/`.
  Extension census on that diff (`grep -Ei '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'`): **0
  matches** — confirmed, not assumed.
- `DESIGN.md` anywhere under `.harness/harness/features/FEAT-48-parallel-safe-suite/`: **0 files**
  (`find … -iname 'DESIGN.md'` empty).
- Colour/contrast/markup surfaces: **0** — the diff is pure Python; no template, stylesheet, or
  markup touched.
- Conclusion: Mode A/B visual-fidelity, theme-parity, and WCAG-contrast dimensions have no object
  in this diff. Not applicable, not skipped.

## 2. The operator-output surfaces (in-lens per dispatch)

**`run_pool.py:113-115` — `MUTATED <name>`.** `snapshot()` (`:29-52`) records a 3-tuple
(`st_mode, st_size, st_mtime_ns`) per path, including symlinked dirs and dangling symlinks via
`lstat`. `main()` (`:109-115`) diffs `before.keys() | after.keys()` and prints only
`MUTATED {name}` — never which field of the tuple diverged, and never "appeared"/"disappeared"
vs. "changed". Confirmed by reading `test-run-pool.py:92-105`: the test itself only asserts the
substring `"MUTATED dangling"` / `"MUTATED linked-dir"` — no test anywhere asserts a
diagnostic beyond the name. **Verdict: actionable but not diagnostic.** An operator gets a
filename and the generic explanation string (`:115`, "A file … changed while the suite ran; this
violates REQ-01 …") — enough to `git status`/`git diff` that one name, not enough to tell
mode-change from append-in-place from delete-and-recreate at a glance. LOW: real gap, not
gating, does not block ship.

**`test-suite-independence.py:249-265` — failure output.** Ran directly
(`env -u HARNESS_AGENT_TYPE python3 test-suite-independence.py`): passing run emits six
`ok self-test <name>` lines, `root <path>`, `discovered 63`, `ok no test mutates …`. One of the
six self-tests (`unresolved root refuses`, `:225-236`) deliberately triggers
`_resolved_root_or_exit`'s refusal path, which prints `ERROR could not resolve scan root above
<tmpdir>` to stderr (`:165`) with **no `self-test:` framing and no tool-name prefix** (unlike
run_pool's own `run_pool.py: ERROR: …` convention at `:96`). Reproduced live: this `ERROR` line
appears interleaved between two `ok` lines on a clean, fully-passing run — momentarily reads as a
real failure to an operator scanning for the word ERROR, resolved one line later by
`ok self-test unresolved root refuses` but not self-evidently at the point it appears. LOW,
non-gating: the trailing `ok no test mutates …` / exit code still correctly signals overall pass.
Separately reproduced a real fault: monkeypatching `scan_file → []` reddens
`FAIL self-test injection idiom` / `mutant beside original` / `pid named mutant`, each followed
by `FAIL self-test detail: <case>: expected […] got […]`, then the summary
`FAIL 0 live-tree mutation site(s), 3 self-test failure(s)`. Monkeypatching `scan_directory` to
return a fake finding produces `VIOLATION bin/some_test.py:42 open mutates a path derived from
the live checkout` printed *before* any `FAIL self-test detail` lines, then the same summary
line. **Verdict: yes, an operator can tell them apart** — `VIOLATION <path>:<line> <sink>` is the
live-tree-defect vocabulary; `FAIL self-test detail: <case>: expected … got …` is the
self-test-regression vocabulary; they never share a line shape. The six `ok self-test` lines on a
passing run are compact (9 lines total including `root`/`discovered`) — not noise burying signal.

**Vocabulary consistency.** `VIOLATION` and `MUTATED` are each used by exactly one file in
`bin/` (`grep -l` across all 63 files) — no collision with another tool's meaning for the same
word. `ERROR` prefix style varies repo-wide already (`run_pool.py: ERROR: …` vs.
`check-plan-routes.py`'s bare `ERROR: …` vs. `board-station.py`'s `ERROR - #N -> …`) — the new
line's lack of a tool-name prefix is not a new inconsistency, it matches existing precedent
elsewhere in `bin/`. Not filing as a finding.

## 3. c7 reconciliation

None of the five c7 panel findings (M1 symlink blindness, self-test durability, `code_grade`
fail, M5 content-swap, M4 missing `__pycache__` leg) sit in the UI-reviewer lens — all five are
code-review/qa/security findings about detection correctness and code-quality grading, not about
a rendered or operator-facing surface this role judges. My own c7 report
(`notes/review-harness-ui-reviewer-c7.md`) found nothing in scope at the prior pin either, for
the same reason. Explicitly: **none apply to this lens; none carried forward.**

```yaml
VERDICT: PASS
DIGEST:
  headline: No rendered UI surface (measured); two operator-output gaps found, both low, neither gates.
  mode: B
  in_scope: true
  severity_max: low
  findings: 2
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-ui-reviewer-c8.md
```
