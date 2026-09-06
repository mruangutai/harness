## Code review — BUG-1303, cycle 4, review_sha 59c5de97 (base 63404ef0)

**VERDICT: FAIL** — one high-severity gap (Q-A) in the DEC-217 predicate documentation, plus a
should-fix (Q-C) test-coverage blind spot and a should-fix (SC-06) index-idempotence break, both
attributable to a *bundled, non-BUG-1303* commit in the same reviewed range. BUG-1303's own five
task commits are clean.

Files read: `BRIEF.md`, `plan.yaml` (full), `.omp/agents/harness-code-reviewer.md`,
`.claude/agents/harness-code-reviewer.md`, `.claude/skills/harness-code-review/SKILL.md`,
`.claude/skills/harness-qa-gate/SKILL.md`, `.claude/skills/harness-verification-rules/SKILL.md`,
`.claude/skills/harness/templates/harness.json`, `.harness/harness.json`,
`.harness/harness/docs/DECISIONS.md` (DEC-215..217), `DECISIONS-INDEX.md`,
`tests/integration/test-validate-digest.py` (new section, full), `tests/unit/test-config-shape-matrix.py`
(full), plus `.claude/skills/harness/bin/validate-digest.py` (schema-extension site only).

### Important scope note — the nine-path diff is two initiatives, not one

`git log 63404ef..59c5de97` shows 9 commits. **8 belong to BUG-1303**
(7563c479..602d375f, 59c5de97). **1 does not**: `e014ede3 "Route bugfix test kinds by changed
surface"`, landed *after* BUG-1303's review_sha pin (602d375f) and *before* its final commit,
touching `.claude/skills/harness/templates/harness.json`, `.harness/harness.json`,
`DECISIONS.md`/`DECISIONS-INDEX.md` (adds DEC-217) and `tests/unit/test-config-shape-matrix.py` —
none of which are files any BUG-1303 task lists. This is the origin of DEC-217 and everything Q-A/Q-B
ask about. I graded it because the dispatch's contract names it as in-scope, but it is not
attributable to BUG-1303's own requirements, and `case_skills_teach_the_new_predicate` (unchanged by
this diff) is the same function DEC-212 relies on — it was simply never extended for DEC-217.

### Self-demonstrated finding (informational, not gating)

My own injected `## Output`/write-grant text (this session's system prompt) is byte-identical to
`/Users/molchairuangutai/GitHub/harness/.omp/agents/harness-code-reviewer.md:35` (the **stale
main-checkout copy**, pre-fix: `<HARNESS_CONTROL_PLANE_ROOT>/.harness/notes/review-harness-code-reviewer-<runid>.md`),
not to the worktree's fixed copy at `.omp/agents/harness-code-reviewer.md:35,99` (verified fixed).
Only because my task dispatch separately hard-coded the correct notes path did this not misfire. This
is expected self-reference (a feature editing the reviewer's own contract can't be reviewed by an
agent loaded from that same edited contract until it lands on main) rather than a lasting defect, but
worth confirming: `open_questions` below.

---

## Q-A (primary) — DEC-217's predicates undocumented in the qa skills: **DEFECT, high**

Confirmed by direct read: `.claude/skills/harness-qa-gate/SKILL.md` and
`.claude/skills/harness-verification-rules/SKILL.md` mention `touches_config_shape`/DEC-212 (lines
44-48 and 36-38 respectively) but **zero occurrences** of `touches_runtime_code`,
`fix_confined_to_tests_and_contract_docs`, or `DEC-217` in either file (grep, both files, zero
matches). `tests/unit/test-config-shape-matrix.py`'s `case_skills_teach_the_new_predicate` (lines
132-143) is **unchanged** by this diff — it still only asserts `touches_config_shape`/DEC-212, never
the two new names. `case_decision_217_exists_and_defines_bugfix_predicates` (new, line 117) asserts
only that DEC-217's own body in `DECISIONS.md` defines the predicates — it never opens either skill
file.

**Failure scenario:** `harness-qa`/`harness-qa-gate` reads `test_matrix.bugfix.when` from
`.harness/harness.json` per its own step 3 ("apply it as read"), sees `{"kind": "unit", "if":
"touches_runtime_code"}` and `{"kind": "integration", "if": "fix_confined_to_tests_and_contract_docs"}`,
and has **no preloaded doctrine** defining either name — unlike `touches_config_shape`, which got a
full worked paragraph (container-type-vs-value-tweak) precisely because DEC-212 required the skill to
teach it. DEC-217's actual definition (`DECISIONS.md:6824-6826`, not preloaded into the qa persona) is
strict: "not under `tests/**`, not a `*.md` ... file, and not under `.harness/`" — broad enough to
include a bare JSON config/template file. A qa persona reading only the bare predicate *name*, with no
citation to consult, could plausibly judge a bugfix diff confined to (say)
`.claude/skills/harness/templates/harness.json` as *neither* "runtime code" (colloquially, config
isn't code) *nor* "confined to tests and contract docs" (a JSON file is neither `*.md` nor
`tests/**`) — landing in the practical gap the formal predicates are designed to make impossible (see
Q-B): **zero required test kinds**, a fail-open the matrix's `always: []` was supposed to never allow.

**Remedy:** add a short paragraph to both `harness-qa-gate/SKILL.md` and
`harness-verification-rules/SKILL.md`, mirroring DEC-212's treatment, defining `touches_runtime_code`
and `fix_confined_to_tests_and_contract_docs` verbatim from DEC-217 and citing it; extend
`case_skills_teach_the_new_predicate` (or add a sibling case) in `tests/unit/test-config-shape-matrix.py`
to assert both new predicate names and `DEC-217` appear in both files — closing the exact class of gap
DEC-216 exists to prevent, this time on DEC-217's own commit.

## Q-B — can the three `bugfix.when` legs leave zero kinds required: **NO gap, proven**

`touches_runtime_code` (`DECISIONS.md:6824-6826`) = "∃ a non-`.harness` file that is not `*.md` and
not under `tests/**`". `fix_confined_to_tests_and_contract_docs` = "∀ non-`.harness` files: `*.md` or
under `tests/**`". These are **exact logical complements** over the same domain (including the
vacuous case of zero non-`.harness` files) — `touches_runtime_code ≡ ¬fix_confined_to_tests_and_contract_docs`
for every diff, so **exactly one always fires**, guaranteeing at least one of `{unit, integration}`
regardless of `match_bug_class`. Verified against three shapes:
- **`.harness/**`-only diff:** no non-`.harness` files ⇒ `touches_runtime_code=False`,
  `fix_confined=True` (vacuous) ⇒ required = `{integration}`.
- **`tests/**` + runtime code:** a non-md/non-tests/non-`.harness` file present ⇒
  `touches_runtime_code=True`, `fix_confined=False` ⇒ required = `{unit}`.
- **This feature's own nine-path diff:** only `.claude/skills/harness/templates/harness.json`
  qualifies as non-`.harness`/non-md/non-tests ⇒ `touches_runtime_code=True` ⇒ required = `{unit}`;
  actual diff ships both `tests/unit/test-config-shape-matrix.py` (unit) and
  `tests/integration/test-validate-digest.py` (integration) — floor met with margin.

The formal logic has no hole. The risk is entirely operational (Q-A): a persona without the
predicates' technical definition can misapply them in a way the formal logic itself never permits.

## Q-C — red-capability, every new assertion

**tests/unit/test-config-shape-matrix.py** (7 new checks, all argued via (b) reachability — each is
a direct equality/`isinstance`/substring test against real JSON/text with an obvious alternate value):
`bugfix has no unconditional test kind` (`always==[]`), `bugfix predicates are complete and unique`
(`when==expected`, order-sensitive), `_matrix_provenance.bugfix exists`, `provenance records moved and
added kinds`, `provenance is signed DEC-217`, `## DEC-217` heading presence, `DEC-217 defines both
predicates` (2500-char window, entry is ~1.3KB — ample margin). All red-capable by inspection; no
special defect found.

**tests/integration/test-validate-digest.py**, argued via **(a) empirical mutant, in-memory only, zero
files touched** (all 4 probes below run and printed; see commands, not repeated here):
- **SC-02 discrimination, both directions:** a mutant `documented_contract_gaps` that always returns
  `[]` reddens direction 1 (`pre_fix_gaps==["code_grade"]` → False); a mutant that always returns every
  field reddens direction 2 (`with_code_grade gaps==[]` → False). **Confirmed both directions
  red-capable.**
- **SC-05 completeness, "empty" branch:** reintroducing the pre-T-01 bug (checking `is None` instead
  of falsy) makes the `empty` persona loop zero times and emit **no line at all**; `_completeness_ok`
  correctly goes red (the exact historical regression class PF-87f1837e closed).
- **SC-05 completeness, "outside" branch:** a whole-file-search mutant (grading `text` instead of
  `documented_block(...)`) makes `outside` wrongly pass (`(True, 'outside: outside.md')`);
  `_completeness_ok` correctly goes red — proves the block-scoping is load-bearing, not decorative.
- **Reviewer plan-mode assertions (T-01 step 6), all 8:** monkeypatched `_contract_source` to return
  synthetic pre-fix content (agent file = `PRE_FIX_REVIEWER_BLOCK`, SKILL.md = a stub with no
  plan-phase section) → **8/8 assertions go red**, independently corroborating T-01's own claimed red
  state.

**Finding (should_fix, med) — SC-05's "absent-from-disk" and "unlocatable-block" checks are not
mutually discriminating.** Mutant: weaken the `read_source(...) is None` guard to `read_source(...) or
""` (swallowing the absent-source case into the unlocatable-block branch). Result:
`_completeness_ok` stays **green** — because the synthetic check is
`_contains_line(failures, "absent.md", "absent")`, and *every* failure line for the `absent` persona
is prefixed `"absent: ..."` regardless of which branch produced it, so the second term is satisfied by
the persona's own name, not by the intended message text (`"documented-contract source absent"`).
The reverse mutant (swallowing "block is None" into the gaps-check) *is* correctly caught, so the gap
is one-directional. This is the assertion-subject pitfall (issue #979): the check's subject is the
literal word "absent", not the code path that produced it. Remedy: tighten the "absent" check to
`_contains_line(failures, "absent.md", "documented-contract source absent")`.

---

## SC-04, SC-06, SC-07, SC-08

- **SC-04 — PASS.** `git diff --name-only 63404ef..59c5de97` (34 entries, captured in full) names
  neither `validate-digest.py` nor anything under `.claude/skills/harness/bin/`. Confirmed by direct
  grep: zero matches for `bin/`. Full suite run independently: `ALL PASSED` (26/26 sections incl. the
  new one), corroborating pre-existing SEC-01/BUG-1081/branch-corroboration cases still pass.
- **SC-06 — PARTIAL.** DEC-216's own row and entry regenerate byte-identical
  (`DECISIONS.md:6792`, `DECISIONS-INDEX.md` row present, ruling after ` :: ` present). **But**
  `.agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` at
  review_sha is **not** byte-identical: the committed DEC-217 row carries tags `[tests,qa,state]`
  while the generator now produces `[tests,docs,digest,plan]` for the same entry (single-line diff,
  reproduced twice, deterministic). This is `e014ede3`'s row, not BUG-1303's T-04 — DEC-216's row is
  unaffected — but SC-06 as literally worded ("re-running ... leaves the index byte-identical")
  fails at this pinned SHA. should_fix (med): rerun the generator and commit the corrected DEC-217 row
  (not a BUG-1303 task file, so this belongs to whoever owns DEC-217/e014ede3).
- **SC-07 — PASS.** `.claude/skills/harness-code-review/SKILL.md:163` ("## Before there is a SHA:
  plan-phase review") sits immediately after "## Review a pinned SHA" (`:155-161`) and immediately
  before "## Red flags" (`:179`), same heading depth; DEC-207 cited at `:166`.
- **SC-08 — PASS.** `sync-agent-adapters.py --check` exits 0; independently diffed both files from
  `# Harness: Code Reviewer` onward: byte-identical, 3668 chars each side.

## code_grade

`python3 .claude/skills/harness/bin/code-grade.py --base 63404ef06cd798c6d933b52336bf73de7b248028
--head 59c5de9764c363eebd67a55cd2f55285bacda69a` → 19 gated functions, all `RESULT: PASS`, 0 `FAIL`,
`PASSING: 19`. No grade-1/grade-2/below-bar records. **code_grade: pass.**
