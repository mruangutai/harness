# FEAT-43 final validation panel — code review — FAIL

**BLUF:** Stage 1 fails on a fact the tool itself reports at the pin: `code-grade.py` exits 1 over
this feature's own change, because six gated PRODUCTION functions — two of them inside
`code_grade.py` itself — grade 3 against a bar of 4. T-01's own verbatim instruction ("Keep every
function you write in `code_grade.py` at grade 4 or better... The tool must pass its own bar") is
unmet, in the tool's own file, verified by running the tool. This is a `must_fix`, `severity: high`.
A second, related `must_fix` at `severity: med`: neither the shipped guidance nor the `code_grade`
digest enum has a spelling for "gated grade-3-below-bar", so REQ-11's one-canonical-vocabulary
promise is unmet for a case this diff itself instantiates six times — not a hypothetical.

All prior findings from the `45328d7` review (six items: grade-1 gate open, missing fixture
derivation, ineffective grade-2 enforcement wiring, missing grade-movement assertion, ineffective
adverse-ordering proof, missing SC-17 boundary discriminators) are independently reverified CLOSED
at this pin, by reading the fixed source and by running the four affected test files myself.

## Pin, human commit, and census

Both objects resolve as commits: base `7ccfae8dd7644bc3aaea612dabf4317c0d804f99` (verified
`git rev-parse --verify` and `git merge-base` = base, confirming ancestry), review pin
`94383e671e51f95d142f3220f97c8e453721d516`. Reviewed exactly
`7ccfae8dd7644bc3aaea612dabf4317c0d804f99..94383e671e51f95d142f3220f97c8e453721d516`, never `HEAD`.
15 commits in range; the `[harness:human]` commit `45328d7a280d251a94b09672a7b6724d55a79f83`
("enforce reviewed code grades") is in scope and its paths (both reviewer agent definitions,
`test-check-plan-routes.py`, `test-validate-digest.py`, `validate-digest.py`) were reviewed as new
work in the prior pass and are unchanged since.

`git diff --stat` census: 78 files, +9792/-44. Comparing the non-note file set against the
`45328d7` review's 48-file census: the fix commit (`94383e6`) touched exactly
`code-grade.py`, `code_grade.py`, `test-check-plan-routes.py`, `test-code-grade-cli.py`,
`test-code-grade.py`, `test-validate-digest.py`, `validate-digest.py` — the seven files the six
prior findings named — plus feature bookkeeping (`STATE.md`, `feature.json`, `answers/`, new
`notes/` receipts and reviews). `.claude/skills/harness-code-risk-grading/SKILL.md`,
`.harness/glossary.md`, `.omp/agents/**`, `.claude/agents/**`, and `gate_policy.py` are
byte-identical to the `45328d7` pin (`git diff --stat 45328d7..94383e6 -- <those paths>` empty), so
their `45328d7`-pin verdicts carry forward unchanged. No scope leakage: every non-bookkeeping change
traces to a REQ-01..11 or D-01..12; the fix commit is scoped exactly to the six named prior
findings.

## The full tool run

```
python3 .claude/skills/harness/bin/code-grade.py \
  --base 7ccfae8dd7644bc3aaea612dabf4317c0d804f99 --head 94383e671e51f95d142f3220f97c8e453721d516
```

Exit status: **1**. `PASSING: 98`. Total gated records: **119** (`grep -c '^FUNCTION$'`). Grade
tally: grade 5 × 70, grade 4 × 26, grade 3 × 8, grade 2 × 15, grade 1 × 0. `RESULT: FAIL` × 21 =
15 grade-2 + 6 grade-3 (`GRADE: 3` ∧ `RESULT: FAIL`, all six against `BAR: 4`, all production —
none of the 8 grade-3 records is a test-code record, since test-code's bar is 3 and grade 3 there
is `RESULT: PASS`). Zero grade-1 records anywhere in the range.

The six grade-3 production `FAIL` records, read at the pin:

| path | line | qualname | cyc | cog | abc | driver |
|---|---|---|---|---|---|---|
| `check-plan-routes.py` | 91 | `resolution_manifest` | 8 | 11 | 22.0 | cognitive+abc |
| `code-grade.py` | 80 | `_diff_paths` | 7 | 11 | 19.2 | cognitive |
| `code_grade.py` | 232 | `_records.collect` | 4 | 11 | 9.1 | cognitive |
| `code_grade.py` | 318 | `_changed_python_files` | 6 | 11 | 14.6 | cognitive |
| `gate_policy.py` | 33 | `load_policy` | 8 | 11 | 17.3 | cognitive |
| `gate_policy.py` | 75 | `evaluate_qa` | 8 | 10 | 17.0 | cognitive |

This matches the dispatch's own claim exactly — verified independently, not taken on faith.

## Per-task verdicts, T-01..T-10

- **T-01 — `met` with the new ruling as a carve-out.** `code_grade.py:29-272` implements the pure
  API; `test-code-grade.py:19-56` carries 12+ hand-derived fixtures spanning all five grades
  (`{5,4,3,2,1}` asserted a subset at `:306-307` by rerun of `run-unit-tests.sh --kind unit`, exit
  0); direction pairs at `:59-125` now assert BOTH metric and grade movement (`:394-407`). **The one
  clause NOT met**: "Keep every function you write in `code_grade.py` at grade 4 or better... The
  tool must pass its own bar" — `_records.collect` (232) and `_changed_python_files` (318) are
  grade 3. See NEW RULING below.
- **T-02 — `met`.** `code_grade.py:366-388` `gated_set`; SC-07/SC-08's seven-way fixture at
  `test-code-grade.py:214-289` asserts the gated set by set equality plus five individual absence
  assertions (`improved`, `renamed_new`, `reformatted`, `signature_changed`, `moved`) and the
  untouched-grade-1 case both absent-from-gated and present-in-informational. Reran
  `test-code-grade.py` myself: `PASS test-code-grade`, exit 0.
- **T-03 — `met`.** `code-grade.py:1-179`: report fields per function (`:55-63`, `:123-141`),
  production/test bar from `test_kinds` (`:47-53`), grade-2 `REASON REQUIRED` (`:135-136`), parse
  errors to `UNGRADED` with distinct exit 3 (`_status` at `:144-148`; `_paths_report` at `:66-78`),
  four distinct exit statuses, determinism via explicit sort (`:169`). Reran
  `test-code-grade-cli.py` myself: `PASS test-code-grade-cli`, exit 0.
- **T-04 — `met`.** `.claude/skills/harness-code-risk-grading/SKILL.md` exists, unchanged since
  `45328d7`; five worked examples present (`grep -c '^EXPECTED GRADE:'` = 5) spanning
  `{5,4,3,1}` (asserted at `test-code-grade.py:330`); limits stated at `:162-165`.
- **T-05 — `met`.** Unchanged since `45328d7`; `sync-agent-adapters.py --check` was the verify
  command for that prior pass and both trees are byte-identical here.
- **T-06 — `met`.** `check_worked_examples` (`test-code-grade.py:311-330`) and `check_delivery`
  (`:334-364`, ten individually-labelled assertions, one per agent per tree, never a count) both
  ran clean in my `test-code-grade.py` rerun.
- **T-07 — `met`.** `gate_policy.py:33-89`, unchanged since `45328d7`. Reran `test-gate-policy.py`
  myself: all 27 named cases `ok`, exit 0, including the four individual key-resolution assertions
  and the clean-report-cannot-pass-alone pair (SC-12, below).
- **T-08 — `met` on the wiring, `not_met` on the enforcement completeness the NEW RULING exposes.**
  `validate-digest.py:232-236` (`review_config_path`), `:541-583` (`resolve_reviewed_commit`,
  `reviewed_python_change`), `:600-621` (`code_grade` schema entry and its `n_a`/`grade_2`/`fail`
  branches), `:756-763` (review-policy `evaluate_review` gate). Reran `test-validate-digest.py`
  myself: `ALL PASSED`, exit 0, including `run_code_grade_cases` (24/24 T-09 cases plus the
  code-grade group). The wiring the task describes is present and correct; what T-08 did not
  anticipate is a gated function at grade 3 (below bar, not grade 1 or 2) — see NEW RULING.
- **T-09 — `met`.** `check-plan-routes.py:91-108` (`resolution_manifest`, D-11), `:775-820` (`main`,
  `MANIFEST`/`DEVIATION` lines). `test-check-plan-routes.py:1411-1476` (`case_27`): owner-manifest
  control, the previous revision proven to report a false `OK` (`case_27b_prior_revision_false_ok`),
  and unreadable-owner exit 2. Reran `test-check-plan-routes.py` myself: `ALL PASS`, exit 0.
- **T-10 — `met`.** `.harness/glossary.md`, unchanged since `45328d7`; `grep -ni` confirms all six
  required terms (`risk grade`, `gated set`, `driver metric`, `ABC magnitude`, `cognitive
  complexity`, `cyclomatic complexity`) present with the severity-ladder cross-reference at line 5.

## D-01/D-02/D-03 — `code_grade.gated_set`, verified against every listed non-gating case

Read `code_grade.py:366-388` directly. The rule is stated over `.grade` comparison only
(`record.grade < before.grade`), never over diff text, satisfying D-02 by construction:

- **Reformat / comment / docstring edit** — none of cyclomatic, cognitive, or ABC counting reads
  comments, docstrings (explicitly stripped at `_body_hashes:341-345`), or whitespace; grade is
  unchanged, `record.grade < before.grade` is `False` → informational. Proven at
  `test-code-grade.py:249,266` (`reformatted` absent from gated).
- **Rename with identical body** — qualname lookup (`before_names.get`) misses, falls to body-hash
  lookup (`before_hashes.get(head_hashes[...])`), matches the identical-body predecessor, same
  grade → informational, never gated. Proven at `test-code-grade.py:248,265`
  (`renamed_new` absent).
- **Signature change without branching** — parameters are not assignment targets in the ABC/A
  count and add no branch/condition; grade unchanged → informational. Proven at
  `test-code-grade.py:250,267` (`signature_changed` absent).
- **Whole-file move** — `_changed_python_files` (`:318-332`) returns `(path, old_path)` from
  `git diff --find-renames`; `gated_set` (`:366-388`) reads the pre-image at `old_path` when the
  current path has none, so the qualname resolves and the grade is unchanged → informational.
  Proven at `test-code-grade.py:251,262,264` (`moved` absent from gated, `relocated.py` present in
  `informational_paths`).
- **Untouched pre-existing failure** — same mechanism as above (unchanged grade), and explicitly
  double-asserted absent-from-gated AND present-in-informational at `test-code-grade.py:252-253`
  (`already_bad`, a real grade-1 function under the fixture's bands).

All five non-gating cases and the ratchet-refusal case are each individually asserted, not merely
implied — I reran the file and it passes. D-01/D-02/D-03 are correctly and testably implemented.

## Per-SC evidence (the eight named, plus the rest by grounded citation)

- **SC-05 — `met`.** `test-code-grade-cli.py:80-93` iterates a tuple of 14 distinct field strings and
  calls `expect(field in result.stdout, ...)` once per field for text output (a single whole-string
  match would not satisfy this — it is genuinely one assertion per field); `:95-101` does the same
  per JSON key via a `for key, value in {...}.items()` loop asserting `record[key]` individually.
  Both are per-field, not whole-record.
- **SC-09 — `met`.** `test-code-grade.py:311-330` `check_worked_examples`: parses every
  ` ```python ` block followed by `EXPECTED GRADE: N` from the skill's `## Worked examples`
  section, asserts `grade_source(...)` equals the stated grade per example
  (`f"worked example {index}: {name}"`), asserts `len(examples) >= 5` (actual: 5, at the floor —
  matches the `## Worked examples` count directly, `grep -c` = 5), and asserts
  `{5,4,3,1}.issubset(grades)`.
- **SC-12 — `met`.** `test-gate-policy.py` case `check_review_evaluation` (rerun: `ok review blocks
  must_fix even without a severity escalation`, `ok review passes a clean medium-severity report`)
  — both directions of the pair asserted, both currently passing.
- **SC-14 — `met`.** `test-code-grade-cli.py:80-83` asserts `REASON REQUIRED: grade_two` present
  when a grade-2 gated function exists, and `:87` asserts `"REASON REQUIRED" in clean.stdout` is
  `False` for the grade-3-passing-as-test-code fixture. Both directions.
- **SC-15 — `met`, this note is the artifact that meets it.** All fifteen `REASON REQUIRED` demands
  the tool emitted at this pin are named and answered below, individually. The prior pass's failure
  mode — a verdict claiming reasons existed with no persisted file — is what this dispatch exists to
  fix; the reasons are written here, in the file, and confirmed by reading it back after writing.
- **SC-17 — `met`, prior finding #6 closed.** `test-code-grade-cli.py:187-230`
  `test_bars_follow_test_kinds` asserts all four boundary points from a fixture `test_kinds` config
  distinct from the live one: `src/grade-four.py` (grade 4, bar 4, `PASS`), `src/grade-three.py`
  (grade 3, bar 4, `FAIL`), `checks/grade-three.py` (grade 3, bar 3, `PASS`),
  `checks/grade-two.py` (grade 2, bar 3, `FAIL`) — production-pass, production-fail, test-pass,
  test-fail, each with its own `expect(...)` on exit code, `RESULT:`, `GRADE:`/`BAR:`, and the
  `grade < bar` boundary itself, plus a JSON-mode repeat of each. This is exactly the four
  discriminators SC-17 demands, and it derives the classification from the fixture's `test_kinds`
  rather than a hardcoded path (`test_bars_follow_test_kinds` swaps the whole `harness.json` to a
  `checks/**` detect glob and the test still resolves correctly).
- **SC-19 — `met`.** `validate-digest.py:604-605` adds `code_grade`/`reviewed` to the reviewer
  schema; a missing `code_grade` falls through the generic "missing field" branch
  (`:658-673`), whose message names the field literally (`f"missing {field!r} — ..."`); a
  `code_grade: fail` alongside `VERDICT: PASS` is separately rejected (`:762-764`). Reran
  `test-validate-digest.py`: `run_code_grade_cases` passes as part of `ALL PASSED`. One low-severity
  wording nit noted below in Stage 2 (not blocking).
- **SC-20 — `met`.** `validate-digest.py:750-764` reads `review` via `load_policy` and calls
  `evaluate_review`; `check_review_policy` (`test-validate-digest.py:1728-1739`) proves the SAME
  digest is rejected under `advisory_unless_high` and accepted under `advisory`;
  `check_config_errors` (`:1823-1832`) proves a `gates`-less config raises `ValueError` naming
  `gates`; `check_prior_validator` (`:1742-1758`) extracts the `45328d7`-predecessor validator via
  `git show` and proves IT accepts the guarded digest — the discriminating proof SC-20 requires.

Remaining SC verdicts, by grounded citation (unchanged from or reconfirmed at this pin):
SC-01 `met` (`test-code-grade.py:19-48`, 12+ fixtures, all five bands, `run-unit-tests.sh` rerun
clean); SC-02 `met` (every fixture including `bindings-and-calls` at `:22` now carries a hand
derivation — `A=2 B=2 C=0; abc=sqrt(8)=2.8`, checked by hand: correct — closing prior finding #3);
SC-03 `met` (`:394-407`, both metric and grade movement asserted, closing prior finding #4); SC-04
`met` (`test-code-grade-cli.py:266-278`, `_diff_paths` is monkeypatched to supply two literally
reversed path orders and stdout is asserted identical for both, closing prior finding #5 — this is
now a genuine discriminator, not reliant on Git's canonical enumeration order); SC-06 `met`
(`:108-112`, exit 3, `PARSE ERROR` stderr, `PASSING: 0`); SC-07/SC-08 `met` (above); SC-09/SC-10
`met` (above); SC-11 `verify: uat`, out of scope for this review by its own contract; SC-13 `met`
(`test-gate-policy.py`, all four keys individually resolved, unrecognised-value and absent-block
cases raise); SC-16 `met` (`case_27a/b/c`, above); SC-18 `met` (`SKILL.md:162-165`).

## Stage 2 — code quality

Entered, because Stage 1's failing item is a scope-and-completeness finding on the feature's own
declared bar, not a defect that makes the rest of the diff unreviewable.

1. **[positive, no action] `code_grade.commit_oid` (`:281-292`) is a correctly defended seam for
   untrusted revision strings.** Option-like input (`revision.startswith("-")`) is rejected before
   any subprocess call — proven at the resolver level by
   `test-validate-digest.py:1798-1820` (`check_resolve_reviewed_commit_guard`), which patches
   `subprocess.run` and asserts it is never called for `--upload-pack=touch /tmp/pwned`. `--end-of-
   options` and `^{commit}` are passed to `git rev-parse`, so even a revision that clears the
   leading-dash check cannot be read as a second flag and is forced to resolve to a commit object,
   not an arbitrary ref. Genuine defense-in-depth against `--base`/`--head` argument injection.
2. **[positive, no action] `validate-digest.py:resolve_reviewed_commit` (`:541-546`) is a sound
   fail-closed adapter.** `commit_oid(...)` raising `ValueError` on an invalid or option-like
   revision becomes `None`, which `reviewed_python_change` (`:549-560`) turns into a named blocking
   error message rather than a silent skip or a default "clean" result — the correct direction
   given this file's own stated purpose (SPEC 8.1's drift-detection charter). The `.encode()` call
   matches the byte-mode, NUL-safe `git diff -z` handling used consistently elsewhere in this
   feature (`code_grade.py:_changed_python_files`, `code-grade.py:_diff_paths`).
3. **[low, advisory] `validate-digest.py`'s generic missing-field hint is wrong for `code_grade`.**
   `code_grade` is not added to `GATE_FIELDS`/`GATE_FAIL_VALUES` for the `reviewer` persona (those
   dicts only key `dev`/`qa`/`dev-ops`, `:95-96,111-113`), so a missing `code_grade` falls through
   to the generic `else: hint = "\`[]\` if there are none"` branch (`:669-670`). The field is a
   four-value enum scalar (`pass`/`fail`/`grade_2`/`n_a`), not a list — writing `[]` on retry would
   fail the same run again with a different, equally unhelpful error. SC-19 itself is unaffected
   (rejection happens and correctly names the field), so this does not gate; it is worth a follow-up
   line so a reviewer omitting `code_grade` is not steered toward a second dead-end resubmission.
4. **[info] `code-grade.py:_is_test` re-reads and re-parses `.harness/harness.json` once per
   function record** (`:47-53`, called from `_record` per grade). Correctness is unaffected — the
   file is small and the run is a one-shot CLI invocation — but a caller running this against a
   very large gated set does repeated I/O for a value that is invariant across the whole run. Not a
   failure scenario, purely a possible efficiency note; not raised as a finding.

No fail-open pattern was found in the diff proper beyond the NEW RULING below: every lookup I traced
(`commit_oid`, `resolve_reviewed_commit`, `_git_show`'s `None`-on-deleted-path branch,
`gated_set`'s pre-image miss) blocks or degrades to a safe, individually-tested default on a miss.

## SC-15 — every REASON REQUIRED demand, answered

The command above emitted exactly fifteen `REASON REQUIRED` lines. Each is named and answered:

1. **`check-plan-routes.py:775 main`** — cyc 10, cog 13, abc 30.9, driver abc. *Reason:* it is the
   one CLI lifecycle joining mode/root selection, owner-manifest resolution (D-11), per-plan
   processing, deviation and invariant-collision accumulation, and the four-way exit status; keeping
   that lifecycle in one function preserves one auditable run.
2. **`code-grade.py:151 main`** — cyc 9, cog 13, abc 30.4, driver abc. *Reason:* the single CLI
   entry point joining argument validation (`--base`/`--head` XOR `paths`), revision resolution
   through `commit_oid`, path-vs-diff report selection, sort, and text/JSON emission — splitting it
   would scatter the one place that owns the four exit statuses (T-03's determinism/exit-status
   requirement is inherently one coordinated decision).
3. **`code_grade.py:338 _body_hashes.collect`** — cyc 9, cog 18, abc 17.3, driver cognitive.
   *Reason:* the recursive AST walk keeps qualname threading, docstring stripping, and per-node body
   hashing local to the single algorithm D-03 names as one identity resolution step; splitting the
   recursion out would separate state (`prefix`) from its only consumer.
4. **`code_grade.py:366 gated_set`** — cyc 8, cog 25, abc 24.9, driver cognitive. *Reason:* this is
   the ordered pre-image-resolution transaction D-01/D-02/D-03 specify as one rule (qualname, then
   body hash, then rename-aware old-path lookup) and the single partition into gated vs.
   informational; I verified above (D-01/D-02/D-03 section) that every one of its six non-gating
   cases is individually correct, which is the argument for keeping the decision in one place rather
   than distributing it across helpers that could disagree.
5. **`test-check-plan-routes.py:1411 _case_27_owner_manifest`** — cyc 5, cog 2, abc 27.0, driver
   abc. *Reason:* one fixture builder plus assertion couples owner/branch manifest divergence, the
   `DEVIATION` line, the `OK` grant line, and the prior-revision false-`OK` proof
   (`case_27b_prior_revision_false_ok`) — SC-16 explicitly requires the discriminating
   prior-revision proof live beside the new assertion.
6. **`test-code-grade-cli.py:64 test_paths`** — cyc 5, cog 2, abc 29.8, driver abc. *Reason:* SC-05
   requires one assertion per field, in both text and JSON, for the same fixture record; the
   per-field loops are inherently long and belong together so the two modes are proven against the
   identical input.
7. **`test-code-grade-cli.py:118 test_rejected_revisions`** — cyc 7, cog 15, abc 43.9, driver abc.
   *Reason:* proves option-like and blob revisions are rejected identically at both `--base` and
   `--head`, that Git is never invoked with the raw option, and that no file is written as a side
   effect of the injection attempt — one integration transaction over the `commit_oid` seam's full
   contract.
8. **`test-code-grade-cli.py:165 test_control_paths`** — cyc 6, cog 0, abc 29.1, driver abc.
   *Reason:* asserts NUL/control-byte path handling stays single-line and round-trips through text,
   parse-error, and ungraded rendering — three renderings of the same odd path in one deliberately
   shared fixture.
9. **`test-code-grade-cli.py:187 test_bars_follow_test_kinds`** — cyc 5, cog 6, abc 28.8, driver
   abc. *Reason:* this is SC-17's four-boundary-discriminator fixture; splitting it would risk the
   four cases silently drifting out of the shared `test_kinds` config they must all read from.
10. **`test-code-grade-cli.py:233 test_diff_and_determinism`** — cyc 5, cog 7, abc 40.5, driver
    abc. *Reason:* one repository fixture deliberately couples deletion handling, odd-path rename
    resolution, copied-checkout/CWD-independent determinism, and the injected-order proof that
    closes prior finding F-08 — all against one committed base/head pair.
11. **`test-code-grade.py:121 check_commit_resolution`** — cyc 4, cog 24, abc 24.4, driver
    cognitive. *Reason:* exercises `commit_oid`'s full contract (valid ref, option-like rejection,
    blob rejection, `^{commit}` peeling) against one synthetic repository built once.
12. **`test-code-grade.py:214 check_changed_function_resolution`** — cyc 5, cog 0, abc 33.3, driver
    abc. *Reason:* SC-07/SC-08's seven-way fixture — the D-01/D-02/D-03 verification I performed
    above depends on this being one commit with all seven cases present together, not split across
    fixtures that could drift apart.
13. **`test-code-grade.py:374 main`** — cyc 8, cog 13, abc 44.4, driver abc. *Reason:* the suite's
    entry point sequencing every fixture band, direction pair, resolution check, commit-resolution
    check, worked-example check, and delivery check as one ordered run whose final print is the
    single pass/fail signal `run-unit-tests.sh` consumes.
14. **`test-gate-policy.py:55 check_policy_loading`** — cyc 1, cog 0, abc 36.1, driver abc.
    *Reason:* SC-13 requires each of the four gate keys resolved individually plus loud failure on
    missing/invalid/unreadable/unparseable config — one shared temp-config lifecycle keeps all eight
    named cases from paying for their own fixture setup.
15. **`validate-digest.py:549 reviewed_python_change`** — cyc 11, cog 10, abc 18.6, driver
    cyclomatic. *Reason:* this is the sole gate on `code_grade: n_a`'s legitimacy (REQ-04's
    "only Python files the change is responsible for" rule, applied to the reviewer's own claim);
    keeping range-parsing, commit resolution, and the Python-file test in one function is what
    makes `check_reviewed_range`'s option-like-revision proof (`test-validate-digest.py:1780-1796`)
    exercise the real code path rather than a decomposed stand-in.

## NEW RULING — the feature's own change does not pass the gate it ships

**Yes, this is a T-01 spec violation.** T-01's intent (`plan.yaml`, T-01, final paragraph) states,
verbatim and unconditionally: *"Keep every function you write in code_grade.py at grade 4 or better
under the bands you are implementing. The tool must pass its own bar."* At the pin,
`code_grade.py:232 _records.collect` (grade 3) and `code_grade.py:318 _changed_python_files`
(grade 3) are both gated, both production, both below the production bar of 4, both actually
introduced by this diff (they do not exist at `7ccfae8d`). This is a fact I verified by running the
tool, not an inference. It is Stage 1's third question exactly: "do the details match the specific
values and constraints that were decided" — here they do not, in the tool's own file, against the
tool's own stated acceptance line.

**Yes, it is a blocking `must_fix`.** I searched the BRIEF's "Out of scope" section, all twelve
decisions (D-01..D-12), and the plan's constraints section for anything that exempts `code_grade.py`
or this feature's own change from the bar it ships. There is none. D-06 explicitly goes the other
way — "any divergence... is escalated rather than resolved by moving a band" — which forecloses the
option of treating the bar as negotiable for this file. I am not inferring an exemption from
convenience; none is cited anywhere in the signed record, so none exists. Reasoning from "the tool
is new and inherently self-referential, so of course it's exempt" would be exactly the
decide-first-reason-after shape this file's own CLAUDE.md instructs against.

**The honest `code_grade` enum value for this run is `fail`, not `grade_2`.** The contract given to
this panel defines `grade_2` as "a grade-2 function is in the gated set; PASS-compatible; REQUIRES
non-empty `grade_2_reasons`." That is a category for the grade-2-only case. Here there are ALSO six
gated grade-3 production functions below bar — a different, unaddressed case — and the tool's own
`_status` function (`code-grade.py:144-148`) already draws exactly this line for us: it returns
exit 1 for `grade < bar and grade != 2`, which means the tool treats a below-bar grade-3 record as
blocking, identically to grade 1, and treats grade-2 as the ONLY non-blocking below-bar case.
Reporting `code_grade: grade_2` here would launder six blocking-by-the-tool's-own-logic failures
under a label reserved for a different, non-blocking case. `code_grade: fail` is the only spelling
that matches the tool's actual exit status (1) and does not misrepresent what happened.

**Yes, the enum's silence on grade-3-below-bar is itself a defect against REQ-11.** REQ-11 demands
"one canonical spelling that the tool, the guidance and the review all share." Read together:
- **The tool** (`code-grade.py:113-122,144-148`) treats grade-3-below-bar as `RESULT: FAIL`,
  contributing to exit 1 identically to grade 1, but assigns it **no `SEVERITY` line at all** (the
  `severity` map at `:56` is `{1: "high", 2: "med"}`, with no entry for 3).
- **The guidance** (`harness-code-review/SKILL.md:53-68`, added by this diff) tells the reviewer
  what to record for grade-1 ("record a **high** finding") and grade-2 ("record a **med** finding
  ... written answer to every REASON REQUIRED line") and says nothing whatsoever about a gated
  grade-3-below-bar record — not that it is ignorable, not what severity to give it, not that it
  even exists as a distinct case.
- **The review digest schema** (`validate-digest.py:604`) has exactly four enum values —
  `pass`/`fail`/`grade_2`/`n_a` — with no dedicated spelling for "gated grade-3, below bar, no
  written-reason mechanism, no assigned severity."

The three surfaces do not currently disagree only because I derived, above, that `fail` is the
correct collapse for this case by reading the tool's exit-status arithmetic directly — a reviewer
without that derivation, following only the shipped guidance, has nothing telling them what to do
with six `RESULT: FAIL` blocks that carry no `SEVERITY:` line and no `REASON REQUIRED:` line. That
gap is real, is not hypothetical, and is instantiated six times in this feature's own diff. It is a
second `must_fix`, `severity: med` (distinct from finding item 1: this is a specification-completeness
gap in the delivered guidance/vocabulary, not a broken promise already made).

## Review result

- Verdict: **FAIL**
- `severity_max`: **high**
- Ranked substantive findings: **2 must_fix** (both above); **1 advisory** (Stage 2 item 3, low,
  non-blocking); **2 positive seam notes** (Stage 2 items 1–2, no action); **1 info** (Stage 2 item
  4, non-blocking)
- `must_fix`:
  1. `code_grade.py:232,318` — two functions this diff introduces are grade 3, violating T-01's own
     unconditional "the tool must pass its own bar" acceptance line; no BRIEF/plan/decision grants
     an exemption.
  2. `harness-code-review/SKILL.md` + `validate-digest.py:604` — no canonical spelling or reviewer
     instruction exists for a gated grade-3-below-bar record, contradicting REQ-11's
     one-vocabulary requirement, and this diff instantiates the gap six times.
- Grade-2 advisory reasons: **15**, all named and answered above (SC-15)
- Scope creep: none
- Open questions: none — both new findings are groundable in the signed record without asking
- File written by reviewer: `.harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-final-panel.md`
- Written, then read back to confirm existence, before this return.

No formatter, linter, project-wide build/suite, goal-check, UAT, ship, merge, deploy, or HEAD
movement was performed. Commands run were scoped to this feature's own test files
(`test-code-grade.py`, `test-code-grade-cli.py`, `test-gate-policy.py`, `test-check-plan-routes.py`,
`test-validate-digest.py`) and the pinned `code-grade.py` invocation itself.
