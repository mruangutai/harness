# FEAT-21 — consolidated revision pass (Q3 checks, lane credit, sha anchors)

BLUF: all three edits landed in `plan.yaml` and nothing else changed. Both new verify clauses are
region-anchored and were proven RED against today's tree AND against the named evasion tree, GREEN
only once the work is done. `check-plan-routes.py` is back to **0 violations**, the plan re-parses
under `yaml.safe_load` and `harness_yaml.load_plan`, and `approval.status` is still `pending`.

One premise correction and one budget collision surfaced; both are recorded below and neither
changed the plan's shape.

## Edit 1 — Q3, the two region-anchored clauses

**T-06 verify** (enforces the case_22a conjunct SC-14 claims):

```
i = cpr.find('case_22a_unreadable_feature_dir_exits_2')
e = [p for p in (cpr.find('check(', i), cpr.find('finally:', i)) if p != -1] if i >= 0 else []
if not e or cpr[i:min(e)].count('.harness/*/features/') != 1:
```

Region rule **tightened** from the dispatch's recipe: label → the earliest of the next `check(` **or**
the next `finally:`. In the real file `finally:` closes case_22a's `try` two lines after the check
call (`test-check-plan-routes.py:552`), so the slice is exactly case_22a's assertion expression —
whereas label → next `check(` would have swept case_22b's whole fixture setup in as well. Falls back
to the `check(` bound if the `finally:` is ever removed.

**T-10 verify** (enforces the migrated_depth stderr conjunct, target is
`test-validate-feature-json.py` via `tv`, not `test-gh-sync.py`):

```
k = tv.find('migrated_depth')
m = re.search(r'^def ', tv[k:], re.M) if k >= 0 else None
if k < 0 or tv[k:(k + m.start()) if m else len(tv)].count('.harness/*/features/') != 1:
```

The pre-existing `assert 'migrated_depth' in tv` was **replaced**, not supplemented: it sat above the
new clause and would have died with an `AssertionError` traceback on a missing label, which is the
unclean red the dispatch forbids. `import sys` became `import re, sys`.

**Exact count of 1** inside each slice, chosen because both intents specify "one conjunct" / "ONE MORE
CONJUNCT" — so it reds on absence and on deletion alike, mirroring T-04's exactly-2 property inside
the region. Rationale for both anchors moved into `intent:` (unbudgeted, and DEC-182's rule for
justification).

### Reachability evidence — shipped clause text, extracted from `plan.yaml` and run standalone

```
== T-06 vs TODAY ==
case_22a: label missing, or its assertion expression does not name .harness/*/features/ exactly once
EXIT=1
== T-06 vs EVASION (case_19a5's expected string rewritten, case_22a untouched) ==
case_22a: label missing, or its assertion expression does not name .harness/*/features/ exactly once
EXIT=1
== T-06 vs WORK DONE (conjunct added to case_22a) ==
CLAUSE OK
EXIT=0
== T-10 vs TODAY (no such case) ==
test-validate-feature-json.py: no migrated_depth case, or its body does not name .harness/*/features/ exactly once
EXIT=1
== T-10 vs EVASION (docstring re-anchored + bare migrated_depth label) ==
test-validate-feature-json.py: no migrated_depth case, or its body does not name .harness/*/features/ exactly once
EXIT=1
== T-10 vs WORK DONE (conjunct added) ==
CLAUSE OK
EXIT=0
```

**Why the named evasions fail — measured, not argued.** On the T-06 evasion tree a whole-file
`grep -c '\.harness/\*/features/'` over `test-check-plan-routes.py` returns **1** (false green); the
region clause returns 0 inside case_22a and reds. On the T-10 evasion tree the whole-file grep
returns **1** from the GROUP 3 docstring alone and `'migrated_depth' in tv` is true — both false
greens; starting the region at the first `migrated_depth` occurrence excludes the docstring, which
sits above every `def`, so the clause still reds.

## Edit 2 — lane credit

`lanes.measurement` now ends "…per DEC-116); pm took them here." The DEC-116 clause is unchanged.

## Edit 3 — sha anchors in `tests.yml`, folded into T-10's intent

The KNOWING SURVIVORS paragraph was **rewritten**, not appended to: the three legacy path literals
stay (true as taken), the block gains the anchor, and the "change nothing else in this file" sentence
now admits exactly this one further edit. Three verbatim, content-anchored substitutions are spelled
out for the builder.

**I chose a pinned literal sha (`62fef85`) over "re-measure the pre-move HEAD"**, for two reasons:
T-10 depends only on T-01 and may run *after* T-08 has moved the tree, in which case a re-measure
returns a post-move figure under a pre-move label; and FEAT-21's own `plan.yaml` becomes tracked at
signature, which would move the count again. A pinned figure makes it a pure text substitution.

**Premise correction (non-blocking, but it changes the edit).** The block's claim
`` `git ls-files '.harness/features/*/PLAN.md' '.harness/features/*/plan.yaml'` returns 8 `` is
**already false at HEAD 62fef85 — it returns 19.** It returned 8 at `eafc8ad`, the commit that wrote
the comment (`git ls-tree -r --name-only eafc8ad | grep -E '^\.harness/features/[^/]+/(PLAN\.md|plan\.yaml)$' | wc -l` → 8;
same at HEAD → 19). Anchoring a known-false number with a sha would falsify the record, so the
intent corrects it to 19 *and* dates it. The count appears **twice** in the block ("all 8 plan files
are git-tracked" as well), and both move together or the block contradicts itself two sentences
apart. `git check-ignore -v .harness/features` exits 1, confirmed at 62fef85.

## Collision I caused and fixed

My first draft of the clauses blew DEC-182's 50-machine-field-line budget (T-06 61, T-10 60) —
`check-plan-routes.py` went from 0 to 2 violations. `verify:` counts, `intent:` does not. Both
clauses were compressed to 6 and 4 lines and the rationale moved to `intent:`. Now **0 violations,
exit 0** — but with **zero headroom**: T-10's machine fields sit at exactly 50/50 and T-06 at 49/50,
so the next line added to either `verify:` trips DEC-182 on contact.

## What the clauses do not prove

They prove the conjunct's text is present in the case body, not that the case runs — registration in
`main()` is the builder's. T-10's verify executes both suites, which covers the other half; T-06's
suite runs at T-09.

## Verification run at the end

- `yaml.safe_load` and `harness_yaml.load_plan`: both OK, 10 tasks, 8 decisions.
- Both `verify:` values load as multi-line strings (literal `|` preserved); both heredoc bodies
  `py_compile` clean and both full verify strings pass `bash -n`.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0.
- `approval:` read back at `plan.yaml:4-7` → `status: pending`, `approved_by: none`, `date: none`.
- No task or SC added, removed or renumbered; LEAVE list untouched; `BRIEF.md` untouched.

## Open

- Nothing blocking. The 8→19 drift is a fact about `tests.yml`'s comment, now handled inside T-10;
  no other artifact repeats that number.
