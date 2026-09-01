# Review — harness-code-reviewer — BUG-1081-code-grade-enforcement — cycle 1

**VERDICT: PASS.** Spec compliance is complete (every REQ/SC met, all `verify: inspection`
criteria independently re-inspected at the pin, no scope creep). Code quality is clean: the
six adversarial fail-open reads each resolve to "cannot happen, structurally" or "already
tested/refused," bar one documentation-accuracy note (low, non-blocking). My own measured
grader run over the reviewed range: `base=9f2a0702bda6de929d42506f5aced2496669a2dc
head=827219b5`, **41 gated functions, 0 with SEVERITY, 0 grade-2, exit 0 → `pass`** —
matching the mechanical result the enforcement itself will expect from any digest naming
this range, including this one.

Reviewed `9f2a0702bda6de929d42506f5aced2496669a2dc..827219b5` (canonical, matches
`review_sha` in feature.json). No `[harness:human]` commits touch production code in range —
the sole human commit (965c0e35) adds only BRIEF.md/plan.yaml/feature.json/prior-review
notes, no `.py`/SKILL.md/DECISIONS.md changes.

## Stage 1 — spec compliance

### Requirements

| REQ | Verdict | Anchor |
|---|---|---|
| REQ-01 (claim checked, not trusted) | MET | `code_grade_enforcement_error` (validate-digest.py:761-785), wired into `validate()` at :1314-1320, replacing the old `code_grade == "n_a"`-only gate |
| REQ-02 (review_sha + repo-derived base, digest chooses neither) | MET | `_mechanical_code_grade` (:734-758) → `_canonical_review_range` (:648-683): head from `_read_review_sha(feature_dir)`, base from `_merge_base_or_none(root, default_ref, head_oid)`; digest's own `reviewed` base is resolved only for shape/injection-check and discarded (:776) |
| REQ-03 (missing/crashed/unparseable calc refuses) | MET | `_classify_canonical_range` (:711-731) catches `SyntaxError` and generic `Exception`, converts to a named `_GRADE_PREFIX`-prefixed refusal, never a traceback; `_load_test_kinds`/`_canonical_review_range` refuse equally on their own failure modes |
| REQ-04 (four enum names unchanged, bars/grade-2 unchanged) | MET | `CODE_GRADE_VALUES = {"pass","fail","grade_2","n_a"}` (:598); bars 3/4 and `fail`>`grade_2`>`pass` precedence *moved*, not changed, into `code_grade.classify`/`_blocks`/`_severity` (code_grade.py:460-507), confirmed by `test-code-grade-cli.py`'s presence/absence pairing (`_record`/`_severity`/`_blocks`/`_is_test`/`_result`/`_patterns` asserted ABSENT from `code-grade.py`; `classify`/`_is_test_path`/etc. asserted PRESENT in `code_grade.py`) |
| REQ-05 (must_fix/severity still override a clean grade) | MET, unchanged code path (grade_2_reasons check, fail+PASS check, review-policy `evaluate_review` block all untouched by the diff) + new `check_judgment_outranks_clean_grade` test |
| REQ-06 (plan reviews stay n_a, never grade) | MET | `not _is_plan_review(reviewed)` guard (:1314) plus pre-existing `_pending_plan_review_error`'s `code_grade != "n_a"` refusal (:993); `check_plan_review_never_grades` monkeypatches `gated_set` and asserts zero calls |

### Success criteria

| SC | verify | Verdict | Anchor |
|---|---|---|---|
| SC-01 | automated | MET | `check_hook_rejects_false_pass` (test-validate-digest.py:2397), real `--hook`, exit 2 pre-fix-shaped false pass |
| SC-02 | automated | MET | same function, second half: `fail`+`VERDICT: FAIL` accepted at exit 0 |
| SC-03 | automated | MET | `check_mechanical_result_discrimination` (:2367) over all four `GRADE_FIXTURES`, each with a wrong-value rejection naming the expected value |
| SC-04 | automated | MET | `check_committed_syntax_error` (:2424) — exit 2, "does not parse" named, no Traceback |
| SC-05 | automated | MET | `check_digest_base_cannot_move_result` (:2443) — both a canonical-base and a mid-range digest base still grade `fail`; a non-`review_sha` head is separately refused |
| SC-06 | unit+automated | MET | `test-code-grade.py::check_classify_bars/_grade_two_is_reasoned/_precedence` (unit, resolves plan-panel finding PF-7ab845aa) + pre-existing `grade_2_reasons` non-empty check |
| SC-07 | automated | MET | `check_plan_review_never_grades` (:2579) |
| SC-08 | automated | MET | `check_judgment_outranks_clean_grade` (:2554) |
| SC-09 | **inspection — performed** | MET | `git show 827219b5:.claude/skills/harness-code-review/SKILL.md` (section "The enum is an audit claim, not evidence of itself", ~lines 68-90): states validate-digest.py independently recomputes and refuses on disagreement; states "no changed Python path... means `n_a`", deletion-only is `pass` not `n_a`; states a mismatch refusal "names the value the repository expected" |
| SC-10 | **inspection — performed** | MET | `git show 827219b5:.claude/skills/harness/bin/test-validate-digest.py` lines 2215-2242: committed RED block quoting the exact pre-fix two-line reproduction (blocking-fn-accepted-as-pass, syntax-error-accepted, both exit 0/errors=[]), and `check_hook_rejects_false_pass`/`check_committed_syntax_error` drive the real `[VALIDATE, "--hook"]` subprocess entry path, not a stub |
| SC-11 | automated | MET | `check_unresolvable_default_branch` + `check_no_merge_base` (both now loop all four grades via `_assert_grade_refused`) + `check_derived_base_range`'s degenerate case — three named clauses, three dedicated fixtures, plus two extra availability checks (`check_missing_test_kinds`, `check_malformed_test_kinds`) beyond the letter of the SC |
| SC-12 | **inspection — performed** | MET | `git show 827219b5:.harness/harness/docs/DECISIONS.md` DEC-209 (line 6363): enforcement ownership, canonical-range derivation formula, availability trade-off (explicitly reversing FEAT-43's carve-out), fail-closed/no-traceback, deletion-is-pass, no-second-implementation/no-CLI-subprocess, retained human-judgment boundary, plan reviews untouched — all six named elements present; `DECISIONS-INDEX.md:208` row confirmed generated (not hand-edited) and non-empty |

No scope creep found: every changed line traces to T-01..T-04's declared `files:`. Task
lanes match DEC-174 exactly — `validate-digest.py`/`test-validate-digest.py` are the two
commits attributed `[harness:t-02]`/orchestrator-authored (T-02 has its own
`receipt-harness-orchestrator-T-02.md`, no team-agent receipt exists for those two files);
`code_grade.py`/`code-grade.py`/their tests are `harness-backend-dev` team commits (T-01,
receipts -c1/-c2); `DECISIONS.md`/`-INDEX.md` are `harness-documentor` team commits (T-04).

### Decisions D-01..D-07 — all honored, no re-litigation needed
D-01 (keep enum, compute+reject) / D-02 (default-branch merge-base + review_sha) / D-03 (one
importable seam, no CLI subprocess — confirmed: `from code_grade import classify, commit_oid,
gated_set`, zero `subprocess` calls to `code-grade.py`) / D-04 (`fail`>`grade_2`>`pass`;
`n_a` only for zero Python paths; deletion-only = `pass`) / D-05 (every derivation/grading
failure refuses, named, no digest-base fallback) / D-06 (plan reviews untouched) / D-07 (no
second grading implementation — `validate-digest.py` calls `code_grade.classify` directly,
never reimplements bar/precedence logic) are each independently confirmed against the
committed code above, not merely cited from the plan.

## Stage 2 — code quality, the six adversarial reads

**1. `_repo_root_for_feature`'s four `..` hops — depth/symlink/non-repo risk.**
**Cannot happen, structurally.** `feature_dir` reaches this function from exactly two
production sources — `_resolve_feature_dir` (via `_root_or_none()` +
`_feature_dir_from_artifact`) and `_hook_feature_dir` (via `inflight_registry.feature_root`,
which returns either a real linked-worktree path or falls back to `owner_root` — never an
arbitrary directory) — and BOTH construct `feature_dir` as
`os.path.join(<a real checkout root>, fm.group(1))`, where `fm.group(1)` is matched by
`FEATURE_DIR_IN_ARTIFACT_RE = r"(\.harness/[^/\s]+/features/[^/\s]+)(?:/|$)"`, i.e. always
exactly 4 path segments. No other production caller of `validate()` supplies `feature_dir`
(confirmed by grep — every other call site is a test fixture). So four `..` hops always land
back on the same root that constructed it, by construction, not convention. `os.path.realpath`
resolves any symlinks along the way to the canonical directory either root is reached
through. A `root` that is not actually a git repo does not crash: every downstream operation
is a `git -C root ...` subprocess call that fails closed (`_git_line_or_none`/`commit_oid`
return `None`/raise `ValueError` → named refusal), never a silent accept.

**2. Ordering of `code_grade_bound_to_review` then `code_grade_enforcement_error`.**
**Cannot produce an ACCEPT.** `err` (validate-digest.py:1097) is initialized `[]`, only ever
`.append()`-ed to, and returned verbatim at :1415 with no clearing/filtering anywhere in
between — traced the full body. `binding_error` and `grade_error` each independently append
on failure; a caller (`hook_mode()`) rejects on any non-empty `err`. Neither ordering
(binding-fails-then-grading-also-fails, or binding-fails-then-grading-would-have-passed) can
produce an empty `err`, because binding's append alone is sufficient and nothing downstream
removes it.

**3. The discarded `reviewed_python_change(root, reviewed)` call at :776 — is it really the
sole base-resolvability check?** **Yes — verified, and the reading in the dispatch is
correct, but the *written* justification for keeping it (in
`notes/receipt-harness-backend-dev-simplify-simplification.md`) is inaccurate and should not
be trusted as-is.** Traced both call sites: `code_grade_bound_to_review`'s
`_parse_reviewed_range` (:927-937) validates only *shape* (single `..`, non-empty base/head
strings) and discards `_base` — it never calls `resolve_reviewed_commit`/`commit_oid` on the
digest's base at all, only on `head` and on `review_sha` (:1066-1069). The discarded call at
:776 is the ONLY place the digest's raw `reviewed` base is resolved via `commit_oid`, which
is where `revision.startswith("-")`/`--end-of-options` injection defense lives
(code_grade.py:290-292). Deleting :775-778, as the simplify finding proposed, would silently
drop that check — the simplify receipt's claim that `code_grade_bound_to_review` performs
"the identical validation... over the identical (root, reviewed)" is true for shape but
false for resolvability/injection-defense of the base half. The finding was correctly left
unapplied (STATE.md: "simplify applied nothing... backlogged"), but not for the reason
recorded — nothing in the four simplify receipts or this feature's notes states the
injection-defense rationale. **Low-severity, non-blocking**: a future simplify/cleanup pass
reading only that receipt would delete a load-bearing (if low-impact — the base is otherwise
unused, so today this is defense-in-depth/early-detection rather than a live exploit path)
check believing it is pure duplication. Recommend a one-line comment at :776 next time this
file is touched; not worth reopening this cycle for.

**4. `_load_test_kinds` — is "no `detect`" the only malformed shape, and does every one
refuse?** **Enumerated; every malformed shape refuses.** `_load_test_kinds` (validate-digest.py:686-708)
only checks `test_kinds` is a non-empty dict — it does not inspect individual kinds. Malformed
shapes that reach `code_grade._is_test_path` (called only when a Python change exists AND at
least one gated function is present — an empty `gated_set()` never touches `test_kinds` at
all, which is why a deletion-only range can grade `pass` even with a broken policy):
missing `"detect"` (`KeyError`), non-string `"detect"`/`"exclude"` (`AttributeError` on
`.split`), a non-dict `kind` value (`AttributeError` on `.get`), `test_kinds` itself
non-dict (explicit `isinstance` guard). All five funnel through `_is_test_path`'s
`except (TypeError, KeyError, AttributeError)` → `TestKindsError` (a `ValueError` subclass) →
caught by `_classify_canonical_range`'s generic `except Exception` → named refusal
(`code_grade cannot be verified: ...`). Committed test `check_classify_rejects_bad_test_kinds`
(test-code-grade.py:450) exercises `None`, `[]`, a non-mapping kind value, and a
missing-`detect` kind — covers 4 of the 5 enumerated shapes directly; non-string
`detect`/`exclude` (AttributeError-on-.split) is not separately unit-tested but is the same
code path and same except-clause as the tested shapes, confirmed by direct read, not run.
Info-level test-coverage note only, not a defect.

**5. Is `_is_plan_review` the only skip, and can a crafted `reviewed:` reach it without being
a plan?** **Cannot happen.** `_is_plan_review` is a literal `reviewed.startswith("plan:")`
check — matching it *is* what "reaching plan mode" means; there is no second predicate
elsewhere. The pre-existing (unmodified) `_pending_plan_review_error` chain independently
requires: `code_grade == "n_a"` exactly, the named path resolves to *this* feature's exact
`plan.yaml`, the plan's `approval.status` is `pending`, AND `feature.json` carries no already
pinned `review_sha` (`_pinned_feature_review_error`). A real code review (this one included)
always has a pinned `review_sha`, so `reviewed: "plan:..."` on an in-review feature is refused
outright by the last check, regardless of `code_grade`. This matches the plan-review-stage
security reviewer's earlier concern about a missing explicit guard on the grading branch
(`review-harness-security-reviewer-planreview.md`) — that guard (`not _is_plan_review(reviewed)`
at :1314) is present in the shipped code.

**6. Sweep for other fail-open branches.** One pre-existing (not introduced by this diff, and
its own docstring/shape is byte-identical to before) narrow gap: `resolve_reviewed_commit`
(:555-565) only catches `ValueError` from `commit_oid`, not `OSError` (e.g. a missing `git`
binary). This is unchanged from the pre-fix file (verified: `git show <base>:...` has the
identical `except ValueError` shape) and was already reachable pre-BUG-1081 through
`code_grade_bound_to_review`'s unconditional-for-all-grades head/review_sha resolution, so
this diff does not widen that particular gap's blast radius. `hook_mode()`'s outer
`try/except Exception: return 0` ("passing through; this is our bug, not theirs") is also
untouched by this diff (confirmed via diff — zero hits for `hook_mode`/`passing through`) and
is DEC-127's documented crash-vs-rejection boundary, not new scope. No other branch found
where a miss inside the new grading/derivation code sails through as an accept; every new
helper (`_git_line_or_none`, `_canonical_review_range`, `_load_test_kinds`,
`_classify_canonical_range`, `_mechanical_code_grade`) returns `(value, error)` or raises into
a caught boundary, never `(value, None)` on a failure path.

## My own measured grader run (base..head, not narrated)

```
$ BASE=$(git -C <worktree> merge-base origin/main 827219b5)   # => 9f2a0702bda6de929d42506f5aced2496669a2dc
$ python3 .claude/skills/harness/bin/code-grade.py --base "$BASE" --head 827219b5
[... 41 FUNCTION records, all RESULT: PASS, zero SEVERITY lines ...]
PASSING: 41
$ echo $?
0
```
JSON cross-check: `len(records)==41`, `any(severity=='high')==False`, `any(grade==2)==False`,
`ungraded==[]`. Mechanical result: `pass` — matches STATE.md's own claim and is what
`validate-digest.py`'s new enforcement will independently compute and expect from this
digest's own `code_grade` field.

I also independently re-ran `test-validate-digest.py`, `test-code-grade.py`, and
`test-code-grade-cli.py` directly (not through the shared runner) — all three exit clean
("ALL PASSED." / "PASS test-code-grade" / "PASS test-code-grade-cli"), corroborating qa's
gate result rather than trusting it.

```yaml
VERDICT: PASS
DIGEST:
  headline: BUG-1081 enforcement is spec-complete and fail-closed on every branch checked; one low-severity documentation-accuracy note on a backlogged simplify residual, non-blocking
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "9f2a0702bda6de929d42506f5aced2496669a2dc..827219b5"
  human_commits_in_scope: [965c0e35]
  open_questions:
    - { id: Q1, question: "receipt-harness-backend-dev-simplify-simplification.md's Finding 1 overstates code_grade_bound_to_review's duplication of the discarded reviewed_python_change call at validate-digest.py:776 (it validates head/review_sha resolvability and reviewed's shape, never the digest's base's resolvability/injection-safety) — worth a corrective note or a one-line code comment before the next simplify pass acts on the backlog item as written, so it isn't deleted for the wrong reason.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-code-reviewer-c1.md
```
