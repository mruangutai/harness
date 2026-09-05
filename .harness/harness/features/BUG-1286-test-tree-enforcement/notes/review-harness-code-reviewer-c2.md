# Code Review — BUG-1286 — cycle 2 (re-pinned at bb3a31ed)

**BLUF: PASS.** The single gating finding from c1 (`violations` grade 1 / `_registry_findings`
grade 3, both below the production bar of 4) is closed. B-1's decomposition is behaviour-preserving
(string- and order-identical, mechanically verified). D-03's ordering is structurally enforced and
empirically fails closed against a constructed nested-checkout/mismatched-toplevel fixture. B-3's new
assertion kills a real second-caller mutant. No must_fix. Two informational notes, neither gating.

## What I examined
`suite_layout.py` (full, both at `bb3a31ed` and its parent, diffed line-by-line),
`tests/unit/test-suite-layout.py` (B-3's new lines 145-176, plus the case-numbered fixtures cases
1-11 for registry/D-01/D-04/self-ownership coverage), `tests/integration/test-run-unit-tests-layout.py`,
`tests/manual/suite-census.py`, `run-unit-tests.sh`, `plan.yaml` D-01–D-04, `BRIEF.md` REQ/SC list,
`qa-tree-audit.md`, `qa-audit-sha-correction.md`, `feature.json`, and every c1-cycle receipt/review
note under `notes/` that discusses D-03, the registry-scoping backlog item, and QA-1
(toplevel-mismatch coverage gap) so I would not re-litigate already-dispositioned items.

## Grader — literal output, corroborated
`code-grade.py --base $(merge-base origin/main bb3a31ed) --head bb3a31ed` → **exit 0, 35 records
(33 PASS + 2 FAIL)**. Matches the orchestrator's figures exactly.
- `tracked_paths` — grade 2, ABC driver (26.6), `RESULT: FAIL`, `SEVERITY: med`. Pre-existing,
  out of scope (F-1 surface); reason already recorded at c1 (Q2).
- `_literal_key_present` — grade 2, cyclomatic driver (12), `RESULT: FAIL`, `SEVERITY: med`. Same
  F-1 surface, backlogged, reason already recorded at c1.
- Every new helper (`_duplicate_or_malformed` 5, `_unnecessary_or_stale` 4, `_entry_finding` 5,
  `_registry_findings` 5, `_unit_integration_findings` 4, `_runner_selection_findings` 4,
  `_bin_planted`/`_bin_planted_findings`/`_is_untracked_exclusion` 5, `_tracked_outside_tests_findings`
  4, `_tracked_scan` 5) grades ≥4, confirmed.
- `violations` produces **no record** — I did not assume this was a filtering artefact, I read
  `code_grade.gated_set`/`_gate_file_records` (`code_grade.py:408-431`): a record is included only
  when `before is None or record.grade < before.grade`. I graded `violations` directly at both refs:
  merge-base = **grade 2** (cyclomatic 13, cognitive 11, abc 26.9 — the pre-feature shape),
  `bb3a31ed` = **grade 4** (cyclomatic 1, cognitive 0, abc 14.4, driver abc, line 203). Grade
  improved (4 is not `< 2`), so the tool correctly routes it to the discarded `informational` list
  rather than the printed `gated` set. Confirmed by direct import, not inferred.
- `code_grade: grade_2` (two backlogged grade-2 FAILs remain, already reasoned; nothing gates).

## B-1 — behaviour preservation of the decomposition: PASS
Diffed `bb3a31ed^..bb3a31ed` for `suite_layout.py` directly (not eyeballed): the change is a pure
extraction. Verified line-by-line:
- Every finding string is byte-identical (same f-strings, same literal text, moved not rewritten).
- Output order is identical: `_unit_integration_findings` → `_runner_selection_findings` →
  `_bin_planted_findings` → tracked-scan findings → `_registry_findings`, matching the old
  monolith's append order exactly.
- The one non-trivial control-flow point — old code left `tracked` as the *real* tuple (not `None`)
  when the self-ownership check failed (self-file absent from the index), because `tracked =
  tracked_paths(root)` had already succeeded before the `if ".../suite_layout.py" in tracked` test —
  and `_tracked_scan`'s `if ... not in tracked: return [], tracked` reproduces that exact case,
  passing the real tuple on to `_registry_findings` unchanged. This is the one place a careless
  extraction commonly loses information; it didn't.
- Exclusion-condition order in `_is_untracked_exclusion` differs syntactically from the old
  cascading `continue`s, but is logically identical (both are conjunctions/disjunctions of the same
  four predicates); confirmed by hand, not just by test count.

## D-03 — explicit verdict: PASS, structurally enforced
Read the code: the toplevel check lives inside `tracked_paths()` and can only raise *before*
returning; `_tracked_scan`'s self-ownership test operates solely on `tracked_paths()`'s return
value, so it is physically impossible for self-ownership to see tracked data that failed the
toplevel gate. This is not "sequenced by convention" — you cannot silently reorder it without
rewriting `tracked_paths` itself.

I then **drove the adversarial case** rather than trusting the docstring: built a two-repo fixture
(an outer checkout, a `root` nested inside it with its own real `.git`), edited `root/.git/config`
to add `core.worktree = <outer>` so `git rev-parse --show-toplevel` (cwd=root) genuinely disagrees
with `root` — the concrete way a root with its own `.git` directory still isn't its own toplevel,
which is the scenario `os.path.exists(root/.git)` alone can't catch. Planted the self-ownership file
*and* a rogue tracked test file in `root` first, so a silently-inert result would have gone
undetected. Result: `tracked_paths(root)` raises `LookupError: ... is not the toplevel of its own
Git index`; `violations(root)` reports it as `cannot enumerate tracked files under ...` — a real
violation, fail-closed, not a silent empty pass. This is the first time this scenario has been
empirically driven for this feature (c1's reviewer and QA both verified it "by inspection" only,
per `review-harness-code-reviewer-c1.md` and `review-harness-qa-c1.md` — QA's own QA-1 finding).

**`tracked_paths()` itself is byte-unchanged by `bb3a31ed`** (confirmed in the diff: 0 lines
touched in that function), so B-1 introduces no new risk here, and the pre-existing coverage gap
(no unit fixture constructs this exact scenario) is unchanged — already flagged c1 as QA-1,
advisory, non-gating, correctly not re-raised here.

## LookupError routes / registry rules / D-01-D-04 vocabulary: all confirmed intact
- All 7 raise sites in `tracked_paths` (git missing ×2, timeout ×2, non-zero exit ×2, toplevel
  mismatch) funnel into `_tracked_scan`'s single `except LookupError` → reported, none clean.
- All four registry self-policing rules (glob-shaped, duplicate, unnecessary, no-longer-tracked)
  fire via `_entry_finding`/`_duplicate_or_malformed`/`_unnecessary_or_stale`; each independently
  exercised by unit case 6 (`test-suite-layout.py:297-347`), all passing.
- Three vocabularies stay distinct (`_unit_integration_findings`: `test-*.py`;
  `_runner_selection_findings`: `test-*.py`/`test_*.py`/`*_test.py`; `_bin_planted`:
  `test-*.py`/`*.test.*`/`probe-*`); the repository-wide clause is the only caller of
  `is_test_shaped`, which remains the sole implementation — no vocabulary duplicated into a helper.

## Helper decomposition graded as code, not just numbers
Each boundary is a real responsibility split, matching the diff's mechanical extraction: format
validity (`_duplicate_or_malformed`) vs. current-state validity (`_unnecessary_or_stale`); "compute
planted paths" vs. "render planted findings" (`_bin_planted` / `_bin_planted_findings`) enables
reuse of the same `planted` list by both the bin clause and the tracked-outside-tests exclusion set
without a second glob. `_tracked_scan` returning `(findings, tracked)` is a genuine seam, not a
workaround: `tracked` is real shared state with two different downstream consumers (the
outside-tests scan, and the registry, which explicitly tolerates `tracked=None`), and the original
monolith had exactly this same data flow — the tuple return just makes it explicit instead of
implicit via a shared local variable. No arbitrary fragmentation found.

## B-3 — discriminating power: PASS, with one low-severity note
Built a scratch fixture (own tempdir, git-tracked copy of `suite_layout.py` + a stand-in
`run-unit-tests.sh` caller) and ran `_violations_callers`/`_is_violations_invocation` unmodified
against it:
- **Mutation: added a second real caller** (`scripts/rogue.py` calling
  `suite_layout.violations(...)`) → the caller set grew to two entries, failing the
  exact-equality assertion. **Mutant killed** — confirmed live, not asserted.
- **Immunity to documentation prose**: confirmed by construction, not just plausibility — `.md`
  files never pass the `SOURCE_EXTENSIONS` filter at all, so the nine `notes/`/`BRIEF.md` mentions
  cited in the dispatch cannot influence this check regardless of wording.
- **One residual, LOW severity, not gating**: the immunity is to *documentation*, not to all prose.
  A non-comment string literal (e.g. a docstring) inside a `.py`/`.sh`/`.ts`/… file *outside*
  `tests/`, containing the literal text `suite_layout.violations(` followed by a non-`)`
  non-whitespace character, would also flip the assertion red with no real call — confirmed by
  probe (`scripts/doc.py` with a bare docstring mentioning the call). No such file exists today
  (confirmed: the real run reports exactly one caller), and constructing one is a narrow, unlikely
  shape; recorded for completeness, not raised as a finding requiring action.

## Backlog items — assessed, not re-raised
- Registry-scoping med note (`_registry_findings` running outside the self-ownership `if`) —
  unchanged by this commit (pre-existing since before c1, `_registry_findings`'s call site in
  `violations()` is identical pre/post decomposition); already recorded c1 as MED/advisory
  (`review-harness-code-reviewer-c1.md` Q1). Not re-raised.
- F-1, F-2, case-11 `INAPPLICABLE` branch, integration case-2 single-sentinel clause, three stale
  BRIEF line pins — untouched by `bb3a31ed`; not re-raised.
- QA-1 (toplevel-mismatch route untested) — untouched by `bb3a31ed` (`tracked_paths` byte-identical
  pre/post); I independently *drove* this scenario this cycle (see D-03 above) and confirmed the
  code holds fail-closed, closing the "is it actually safe" half of QA-1 by evidence rather than
  inspection. The "no regression test exists for it" half remains correctly backlogged/advisory —
  not gating per `gates.review: advisory_unless_high`, and not part of this cycle's authorised scope
  (B-1/B-2/B-3 only).

## Out-of-scope observation (not a finding against this diff)
Running the full `--kind integration` suite surfaces 15 real `FAIL` lines in `test-plan-merge.py`
(sign-approval mechanics). Confirmed via `git diff --stat eb9d044e..bb3a31ed -- tests/integration/test-plan-merge.py
.claude/skills/harness/bin/plan_merge.py` that neither file is touched anywhere in this feature's
commit range — the file already existed, untouched, at the merge-base. Orthogonal, pre-existing,
out of this diff's scope; recorded for the record per rule 15, not smoothed over. The
layout-specific file the orchestrator's "14 PASS / 0 FAIL" figure refers to,
`tests/integration/test-run-unit-tests-layout.py` alone, independently reruns at **14 PASS / 0 FAIL,
exit 0** — that specific figure is corroborated exactly; read as "the whole integration kind" it
would be a false claim, so I'm stating the scope explicitly rather than letting the ambiguity stand.

## B-2 — SHA correction: independently reconfirmed
`4b343d8083d94d97477d3f2ebd7b848e83f01871` is an ancestor of `bb3a31ed` (`git merge-base
--is-ancestor` exit 0). `qa-tree-audit.md` carries exactly one fenced block (`grep -c '^```'` = 2).
Re-ran `tests/manual/suite-census.py tree-audit --ref HEAD` and diffed its 86-line output against
the note's fenced block, sorted: **identical row sets**, satisfying SC-12 in full.

## Other corroborations
`unit --kind unit`: 342 PASS / 0 FAIL, 27 files, exit 0 (matches). `test-suite-layout.py` alone: 47
PASS / 0 FAIL (matches "47 checks"). `--check-layout`: exit 0 (matches). `tree-audit`: `TOTAL 85
OUTSIDE 9 VIOLATIONS 0` (matches). No `[harness:human]` commits in `eb9d044e..bb3a31ed` (16 commits,
none human-tagged) — nothing inherits no-review status.
