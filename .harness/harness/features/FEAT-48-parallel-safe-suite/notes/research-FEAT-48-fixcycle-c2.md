# Fix cycle 2 — FEAT-48 plan.yaml, all four panel items closed

## BLUF

**All four items are dispositioned in one consolidated edit to `plan.yaml`; five hunks, nothing
else moved.** The gating item (`PF-scope-1`) is fixed by widening T-05's section regex, and the
widening is proved against the real 188 headings rather than argued. The plan is unsigned,
`check-plan-routes.py` exits 0 with 0 violations, and every cycle-1 repair is byte-identical.

## Dispositions

| id | sev | disposition | where |
|---|---|---|---|
| `PF-scope-1` / `Q1` | high | **FIXED — regex widened** | `plan.yaml:879` |
| `PF-scope-2` / `Q2` | med | **FIXED — skip list rewritten** | `plan.yaml:457-470` |
| `VL-03` | low | **FIXED — five → six** | `plan.yaml:104` |
| independent reader's third-blind-spot | low | **FIXED — named in both places** | `plan.yaml:160-166` (D-11), `:933-938` (T-05 intent) |

## PF-scope-1 — how the fix was verified, not reasoned about

`^## DEC-\d+ The suite runs in parallel` → `^## DEC-\d+\b[^\n]*?The suite runs in parallel`.

Verification, all against the live `.harness/harness/docs/DECISIONS.md`:

1. **Convention re-derived from the file, not from the reader.** Parsed all `^## DEC-` headings:
   **188 headings, 188 with the character after the number being a space, 188 with the next token
   being U+2014 (em-dash)**. Zero exceptions, first (`DEC-01`) and last (`DEC-205`) inspected.
2. **The regex was exercised as LOADED, not as typed** — extracted from
   `yaml.safe_load(plan)["tasks"]` T-05's `verify:` string and run, so the pattern proved is the
   one the doer receives.
3. **Satisfiability, against a synthetic appended entry on the real file:** em-dash `True`, plain
   space `True`, hyphen `True`, en-dash `True`, colon `True`. Old regex: em-dash `False`.
4. **Is there a tree in which it passes?** Yes, and the discriminating power survives: complete
   entry → exit 0 (339 words, 0 missing); short stub carrying all 15 phrases → exit 1 (39 words);
   entry missing 3 phrases → exit 1. The section lookahead still terminates at the next `## DEC-`
   heading (a following `DEC-207` body is excluded — asserted).
5. **No false match today** — the pattern finds nothing on the unmodified file, so the block is red
   before the work and green after.
6. **The assumption is baked nowhere else.** Greped the whole plan for DEC-heading patterns: line
   879 is the only regex over a heading, and `gen-decisions-index.py:28` (`^##\s+(DEC-(\d+))\b`) is
   already separator-agnostic, so the index/drift half never depended on the spelling.

T-05's intent additionally states the house-style em-dash **as a convenience explicitly labelled
"never a constraint the gate enforces"** — the fix does not depend on a future author reading it.

## PF-scope-2 — the skip list, measured both ways

Rewritten to prune **exactly four** directories (`.git`, `.claude/worktrees`, `node_modules`,
`.venv`) with **no general dot-directory rule**, and to say why `.claude` must be walked.

Measured on 2026-08-31 with a walk implementing each reading:

| reading | main checkout | FEAT-48 worktree |
|---|---|---|
| general dot-prune (the ambiguous one) | **0** | **0** |
| named prunes only (the intended one) | **58** | **56** |

All discovered files sit in `.claude/skills/harness/bin`. The verify's `disc[0] >= 50` floor is
therefore reachable with a 6-file margin in the worktree, and the intent now records both numbers
so a later reader can tell drift from falsification.

## VL-03 — the count

`D-09` said "All five tasks"; the plan carries six (`T-01, T-02, T-03, T-04, T-06, T-05`, confirmed
by loading the file). Now "All six tasks". The census contract clause FEAT-47 depends on was not
touched and still enumerates the two test files and two helpers — asserted at load time.

## Third uncovered class

`D-11` and `T-05`'s intent both now say it explicitly: T-03's taint model seeds only the literal
`__file__`, so a write to a path built from a **relative literal** or joined onto **`os.getcwd()`**
that lands **outside** the watched directory is seen by neither half — the runtime check because
the target is out of DIR, the static scan because no name is tainted. No task, `files:` or `verify:`
changed, per the reader. Neither addition introduces a new phrase into T-05's `need` list, so no
verify can redden on it.

## Cycle-1 repairs — how "undisturbed" was confirmed

A byte snapshot of `plan.yaml` was taken **before** the first edit and diffed after the last. The
diff is **five hunks and no others**: D-09 line 104, D-11's coverage paragraph, T-03's skip-list
sentence, T-05's regex line, T-05's intent (two hunks). No hunk falls in T-04's registration step,
T-06's `"${SCRIPTS[@]}"` substring or `tree condition:` regex, D-09's census contract, D-11's
residual-trade paragraph, or `BRIEF.md` (untouched entirely). Four of those were additionally
re-asserted by string check after loading the edited YAML, all `True`.

## Gate output — real

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py <FEAT-48 plan.yaml>
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 ... granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
DEVIATION T-02 ...   (same shape)
DEVIATION T-03 ...   (same shape)
DEVIATION T-04 ...   (same shape)
DEVIATION T-06 ...   (same shape)
DEVIATION T-05 .harness/harness/docs/DECISIONS.md, DECISIONS-INDEX.md granted to harness-documentor
0 violation(s) across 1 plan(s)          EXIT=0
```

Six `DEVIATION` lines, **zero** `VIOLATION` lines, exit 0 — the expected DEC-174 carve-out output;
only `VIOLATION` gates.

## State

`approval: {status: pending, approved_by: null, date: null}` — unsigned, untouched. No id
renumbered. YAML loads clean under `safe_load`.

## Open questions

None blocking. One note for whoever runs the next panel: every satisfiability verdict here, mine
included, is static analysis against today's tree — a heading-style change or a new `## DEC-` entry
between now and build cannot break the widened regex, but a rewrite of `gen-decisions-index.py`'s
row grammar would still move T-05's drift half.
