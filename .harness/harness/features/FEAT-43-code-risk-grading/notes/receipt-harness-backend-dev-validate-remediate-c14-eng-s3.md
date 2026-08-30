# Receipt — harness-backend-dev — SEC-01 (validate-digest.py review_sha binding)

## BLUF

SEC-01 closed: `code_grade`'s claim is now bound to `feature.json`'s `review_sha` —
the system of record — never to whatever `reviewed:` range the digest itself names.
A forged no-op range (`reviewed:` head ≠ `review_sha`) is rejected with a named,
actionable error, for `pass`/`fail`/`grade_2`/`n_a` alike, before `code_grade`'s own
value is ever branched on. An honest range (head == `review_sha`) is accepted. The
live bypass was reproduced against the actual worktree and confirmed closed.
Test-first throughout; `test-validate-digest.py` is green (108/108 named cases,
exit 0); mutation proof kills the exact forged/honest cases and the file is restored
byte-identical.

## What changed

`.claude/skills/harness/bin/validate-digest.py`:
- New: `FEATURE_DIR_IN_ARTIFACT_RE`, `_feature_dir_from_artifact`, `_read_review_sha`,
  `resolve_review_sha`, `_parse_reviewed_range`, `code_grade_bound_to_review`,
  `_missing_field_default_hint`.
- `validate()` gained a `feature_dir=None` parameter (fixture-override seam, mirrors
  `review_config_path`'s `config_path`) and now calls
  `code_grade_bound_to_review(text, seen.get("reviewed"), feature_dir)`
  **unconditionally**, immediately on entering the `harness-code-reviewer` block,
  before `code_grade`'s value is read for branching.
- The missing-field hint loop's bare `else:` now delegates to
  `_missing_field_default_hint(field, allowed)`, which names `code_grade`'s four
  legal values instead of the generic "`[]` if there are none" (SC-19 stays intact:
  the field is still named literally in the outer message).
- A comment at the `harness-code-reviewer` schema-extension site states the
  canonical spelling: a gated, below-bar, non-grade-2 record is `code_grade: fail`
  — no fifth enum value.
- `reviewed_python_change` (the pre-existing grade-2 record) is **untouched** — the
  binding is its own cohesive function per the batch contract's steer, confirmed
  by `git diff` showing zero removed/changed lines inside it.

`.claude/skills/harness/bin/test-validate-digest.py`:
- `reviewer_digest()`'s default `reviewed` changed from the bypass-shaped
  `PRE_FEATURE_REVISION..PRE_FEATURE_REVISION` (a self-consistent no-op) to
  `HEAD..REVIEW_SHA` (honest — head matches the fixture's `review_sha`, base is
  merely resolvable and never checked).
- New `make_feature_dir()` fixture helper; `run_code_grade_cases()` now builds one
  real `feature.json` under a tempdir and threads `feature_dir` through every
  `validator.validate(...)` call.
- New cases: `check_review_sha_binding` (+ `_unconditional` / `_other_personas`
  splits), `check_resolve_review_sha_artifact_path`,
  `check_resolve_review_sha_feature_json`, and one CLI `case()` for the
  `code_grade` missing-field hint content.
- `check_reviewed_range`'s "n_a with no python diff must accept" case now passes an
  explicit self-consistent range **at the pin** (`REVIEW_SHA..REVIEW_SHA`) instead
  of relying on the (now honest, non-self-consistent) default.

## Test-first (RED confirmed before the GREEN fix)

Before writing `code_grade_bound_to_review`, I added
`check_review_sha_binding`'s forged-range assertion against the **unmodified**
validator and ran it: it failed with
`a resolvable no-op range whose head != review_sha must reject, naming review_sha`
— the pre-fix code accepted the forged range (`code_grade: n_a` with
`reviewed: "HEAD..HEAD"`, head ≠ the fixture's `review_sha`) exactly as the security
reviewer's live reproduction showed. Only then was `resolve_review_sha` /
`code_grade_bound_to_review` written and the case turned green.

## Verification run and reported

**1. `python3 .claude/skills/harness/bin/test-validate-digest.py`**

Exit status: **0**. Final line: `ALL PASSED.` — 66/66 CLI cases, 14/14 hook cases,
24/24 T-09 cases, 2/2 template cases, and the `code-grade and review-policy gates`
suite (which now hosts the SEC-01 cases) all `ok`. Named new/preserved cases:

- `check_review_sha_binding`: honest range accepts; forged no-op range rejects
  naming `review_sha`.
- `check_review_sha_binding_unconditional`: forged range rejects for
  `code_grade` in `{pass, fail, grade_2}`, not only `n_a`.
- `check_review_sha_binding` (unresolvable-feature branch): a missing
  `feature.json` directory fails closed (non-empty errors), not silent accept.
- `check_review_sha_binding_other_personas`: `harness-ui-reviewer` and
  `harness-security-reviewer` accept a digest with neither `code_grade` nor
  `reviewed` — SEC-01 binds `harness-code-reviewer` only.
- `check_resolve_review_sha_artifact_path`: white-box — derives the feature from
  the digest's own `artifact:` line + a stubbed checkout root; no `artifact:` line,
  a non-feature `artifact:` path, and no checkout root each fail closed.
- `check_resolve_review_sha_feature_json`: white-box — an unpinned
  (`review_sha: none`) and an absent `feature.json` each fail closed.
- CLI case `code_grade's missing-field hint names the four legal values, not the
  list wording` — `False`, mentions `["code_grade", "grade_2", "n_a",
  "!if there are none"]`.
- Preserved SC-19: `code reviewer omission of code_grade is rejected` — still `False`.
- Preserved SC-19/SC-20: `check_code_grade_state`'s `fail-plus-PASS must reject`
  and `grade_2 with a written reason must permit PASS` / `without reasons must
  reject` — unchanged, still passing.

**2. CLI bypass reproduction** (temp dir outside the repo, deleted after):

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01-repro/forged-digest.txt
VERDICT: BLOCKED (contract violation)
  - reviewed head '7ccfae8dd7644bc3aaea612dabf4317c0d804f99' does not resolve to this feature's pinned review_sha (94383e671e51f95d142f3220f97c8e453721d516) — write the range that ends at review_sha (feature.json), not a convenient no-op.
$ echo $?
1
```

Forged digest: `code_grade: n_a`, `reviewed: "<review-range-base>..<review-range-base>"`
(a resolvable, self-consistent no-op range at the review range's own `base`,
`7ccfae8d...` — distinct from this feature's real `review_sha`,
`94383e67...`), `artifact:` pointed at this real feature's own notes/ path. Before
this fix this exact shape produced `digest ok`, exit 0 (the security reviewer's
live reproduction). Confirmed the honest counterpart accepts:

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01-repro/honest-fail-digest.txt
digest ok
$ echo $?
0
```

(same feature, `reviewed:` head == `94383e67...` == the real `review_sha`,
`code_grade: fail` — chosen over `n_a` here specifically to isolate the binding
from the unrelated `reviewed_python_change` python-diff check, which independently
and correctly rejects an `n_a` claim over a range that does touch `.py` files —
verified separately and is not a regression.)

**3. `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/validate-digest.py`** (paths mode)

Every function added or modified grades 4 or better:

| qualname | grade |
|---|---|
| `_feature_dir_from_artifact` | 4 |
| `_read_review_sha` | 4 |
| `resolve_review_sha` | 4 |
| `_parse_reviewed_range` | 4 |
| `code_grade_bound_to_review` | 4 |
| `_missing_field_default_hint` | 5 |

`reviewed_python_change` (pre-existing grade-2 record) is confirmed **untouched**
(`git diff` shows zero changed lines inside its body) and stays grade 2, unchanged.

`validate()` itself is the one function I could not avoid touching structurally —
it is the single dispatcher every persona schema runs through, so the
unconditional binding call has to live there. It was **already grade 1 at the
pinned base commit** (measured: `git show 94383e67...:.../validate-digest.py`
graded via `code-grade.py`, `CYCLOMATIC: 101`, `GRADE: 1`, pre-existing and
unrelated to SEC-01). My footprint inside it is the documented minimum:
- one unconditional two-line call (`binding_error = ...; if binding_error: ...`)
  — the one branch this feature cannot avoid adding, since "runs unconditionally"
  is a control-flow requirement, not a style choice;
- a parameter addition (no branch);
- a schema-comment addition (no branch);
- the hint-fix delegates to a new grade-5 helper (`_missing_field_default_hint`)
  rather than adding an `elif`, specifically to avoid growing `validate`'s branch
  count for that fix.

Net: `CYCLOMATIC 101 -> 102` (+1, the unavoidable `if`). `validate` remains
`GRADE: 1`, `RESULT: FAIL`, `SEVERITY: high` — a pre-existing condition, not one
this batch introduces, and out of scope to fix here (a full decomposition of a
100+ branch, 300-line dispatcher is a separate, much larger effort than SEC-01's
remediation and would itself be undisciplined scope creep against "no more
specific than necessary").

**4. Mutation proof**

Mutated `code_grade_bound_to_review`'s `if head_oid != pin_oid:` to
`if head_oid == pin_oid:` (inverted the OID equality). Re-ran
`test-validate-digest.py`: **9 named cases failed**, including exactly the two the
proof requires:
- `an honest range whose head matches review_sha must accept` (now wrongly
  rejected — mutation flips the honest case to a false rejection)
- `a resolvable no-op range whose head != review_sha must reject, naming
  review_sha (the SEC-01 bypass)` (now wrongly accepted — mutation flips the
  forged case to a false accept)

Also caught (same root mutation, wider blast radius, expected): the three
`code_grade={pass,fail,grade_2}` unconditional cases, `grade_2 with a written
reason must permit PASS`, `n_a with no reviewed Python diff must accept`, `none
severity must be accepted by review policy`, `advisory must accept the same
digest` — every one of these relies on an honest range validating, which the
inverted mutation breaks.

Restored `if head_oid != pin_oid:` byte-identically; re-ran suite: exit 0,
`ALL PASSED.` (108/108). Confirmed with
`grep -n "head_oid != pin_oid\|head_oid == pin_oid" validate-digest.py` — exactly
one match, the `!=` form — and `git status --porcelain` on both files shows only
the intended (non-mutation) diff remains.

## Design decisions

- **Feature resolution mechanism**: `resolve_review_sha` derives the feature
  from the reviewer's **own `artifact:` line** (`.harness/<repo>/features/<FEAT>/`
  segment) plus the checkout root (`_root_or_none`, the existing FEAT-42
  `harness_boundary` seam) — never a persona-supplied field, an environment
  variable, or `subprocess` mocking. This mirrors `review_config_path`'s
  `config_path` override: `validate()`'s new `feature_dir` parameter, when given,
  skips derivation entirely — the seam tests use. Rationale: the artifact path is
  the one thing in a `harness-code-reviewer` digest that is not an attacker-chosen
  claim about which feature is under review (SPEC 8 fixes where every reviewer
  writes), so binding to it (rather than, say, a hypothetical `feature:` digest
  field) does not reopen the same hole with a different field name.
- **No-feature-resolved path fails closed, unconditionally**: every branch inside
  `resolve_review_sha` / `_feature_dir_from_artifact` / `_read_review_sha` returns
  `(None, <error>)` on failure, and `code_grade_bound_to_review` returns that error
  string directly — there is no code path in which an unresolved feature produces
  `None` (no binding error). Proven by
  `check_review_sha_binding`'s "unresolvable feature.json" case and by
  `check_resolve_review_sha_{artifact_path,feature_json}`'s six failure-mode
  cases (no artifact line, non-feature artifact path, no checkout root, unpinned
  `review_sha`, absent `feature.json`, unreadable `feature.json`).
- **`hook_mode`'s catch-all is not relied on**: `code_grade_bound_to_review` and
  everything it calls raise no exception type `hook_mode`'s `except Exception`
  handler at `:1083-1086` (old numbering) would swallow — every failure mode is an
  ordinary `(None, str)` return, never a raised exception, so an unresolvable
  feature or an unreadable `feature.json` becomes a **blocking validation error**
  (exit 2 under `--hook`), not a silent pass-through.
- **Only `head` is bound**, per the batch contract — `base` is validated only for
  shape (non-empty, exactly one `..`), never compared to anything, since it carries
  no independent system-of-record value today.

## Verdict

```yaml
VERDICT: PASS
DIGEST:
  headline: SEC-01 closed — code_grade is now bound to feature.json's review_sha, not the digest's own claimed range; forged no-op ranges reject with a named message, honest ranges accept, unconditionally across pass/fail/grade_2/n_a
  tests_added: 11
  suite: pass
  task: T-08
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/validate-digest.py
    - .claude/skills/harness/bin/test-validate-digest.py
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3.md
```
