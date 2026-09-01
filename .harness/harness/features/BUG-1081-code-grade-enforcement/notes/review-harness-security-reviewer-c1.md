# Security review — BUG-1081-code-grade-enforcement (c1)

review_sha `827219b5`, range `9f2a0702..827219b5`.

## Headline

**CRITICAL, demonstrated: the digest's own `artifact:` line can redirect every git operation
`code_grade_enforcement_error`/`code_grade_bound_to_review` performs — including which
`feature.json` is read as the "system of record" — to a directory the reviewed branch's own
author fully controls, defeating both this feature's mechanical recomputation and the
pre-existing SEC-01 SHA-binding at once.** Everything else audited (argument injection, the
other refusal branches, error-message leakage, secrets) is closed or correctly fail-closed.

## 1. Argument injection into git — closed

`commit_oid` (`code_grade.py:290`, unchanged) refuses any revision starting with `-` before
Git ever runs, and resolves through `git rev-parse --verify --end-of-options
<revision>^{commit}` — an option-like or ref-metacharacter string never reaches a live git
flag position. Every new subprocess call in `validate-digest.py`
(`reviewed_python_change`, `_git_line_or_none`, `_canonical_review_range`,
`_classify_canonical_range` via `code_grade.gated_set`/`_git_show`) passes only: (a) already
`commit_oid`-resolved 40-hex OIDs, (b) `root` (see §2 — a path, never option-like: always
produced by `os.path.realpath`, which cannot start with `-`), or (c) fixed literal git
subcommand names. `reviewed_python_change`'s own `reviewed.count("..") != 1` shape check and
`commit_oid` resolution are unchanged in effect (still validate the digest's own `reviewed`
field), matching the dispatch's SEC-01 concern. No injection surface found.

## 2. Path traversal / root confusion — CRITICAL, exploitable

**`FEATURE_DIR_IN_ARTIFACT_RE = re.compile(r"(\.harness/[^/\s]+/features/[^/\s]+)(?:/|$)")`**
(pre-existing, `validate-digest.py:790`) captures `<repo>` and `<FEAT>` with `[^/\s]+` —
excludes `/` and whitespace only, so **`..` is a legal token for either segment.**
`_repo_root_for_feature` (new, `validate-digest.py:~553`) walks exactly four `..` off
whatever `_feature_dir_from_artifact` returns. Before this diff that arithmetic only fed the
*additive-only* branch-corroboration check (`_current_branch_or_none`) — a wrong root there
could only turn an accept into a reject. **This diff reuses the same function for
`resolve_reviewed_commit`, `_canonical_review_range`, `_load_test_kinds`, and
`_classify_canonical_range` — i.e. the entire mechanical grade computation — so the same
pre-existing traversal now decides an ACCEPT, not just a false reject.**

Proven against the real worktree, calling the actual functions (no reimplementation, no
writes):

```
text = "artifact: .harness/../features/../notes/fake.md\n"
_feature_dir_from_artifact(text, root)   -> no error; group1 = ".harness/../features/.."
_repo_root_for_feature(feature_dir)      -> /Users/.../GitHub/harness   (the MAIN checkout,
                                             not .../worktrees/harness/BUG-1081-...)
git -C <escaped root> rev-parse --is-inside-work-tree  -> true
git -C <escaped root> rev-parse --show-toplevel differs from the real worktree's toplevel
git -C <escaped root> cat-file -t <worktree's own HEAD sha>  -> "commit"   (shared object DB —
    `git worktree list` confirms this checkout is a linked worktree of that main repo)
```

So an attacker-chosen `artifact:` line moves the `-C` root for **every** grading git call to
a *different, fully valid, git checkout that shares this repo's object database* — any commit
the attacker creates in their own worktree (even unpushed, unreferenced by any branch) is
resolvable from there.

**Why this isn't yet a full sail-through today, and why that's incidental, not a control:**
`_read_review_sha(feature_dir)` — called *before* `_repo_root_for_feature` in both
`code_grade_bound_to_review` and `code_grade_enforcement_error` — opens
`feature_dir/feature.json` with a real `open()`, which (unlike `os.path.realpath`) requires
every intermediate component to exist on disk. Confirmed live: this fails today only because
`<worktree>/features/` doesn't happen to exist
(`os.path.isdir(root/"features") == False`) — an accident of this worktree's current
contents, not a validated invariant. **The attacker who owns the branch under review can
trivially make it exist**: commit a `features/.gitkeep` and a top-level `feature.json` in
their own worktree (both fully within their write access — it's their PR), with a forged
`review_sha` (any commit resolvable from the escaped root, e.g. a throwaway one-line commit
they mint on top of the escaped root's own default-branch tip — mechanically grades `n_a` or
trivially `pass`) and a forged `branch` field matching whatever branch the escaped root
happens to be checked out to. That single crafted digest then:
- satisfies `code_grade_bound_to_review`'s SHA binding (their own digest's `reviewed:` head
  is simply set to the same forged `review_sha` — both sides are the attacker's own values),
- satisfies `_branch_corroboration_error` (the forged `feature.json`'s `branch` field is
  chosen to match),
- and makes `code_grade_enforcement_error` compute `expected` over the forged, cherry-picked
  range instead of the real reviewed commits — so any `code_grade` the attacker asserts can be
  made to match, regardless of what the real reviewed diff contains.

This is not a decision question against D-03/D-05/D-07: the fix is a containment check
(`FEATURE_DIR_IN_ARTIFACT_RE` must reject `.`/`..` tokens, or `_repo_root_for_feature`'s
result must be verified to still resolve `feature_dir` as its literal descendant) inside the
one existing seam — it doesn't add a second grader, a CLI subprocess, or an availability
carve-out.

Not previously caught: neither `notes/review-harness-security-reviewer-planreview.md` nor
`notes/receipt-harness-orchestrator-reachability.md` mentions this path, and
`test-validate-digest.py` has no case constructing an `artifact:` line with `..` tokens.

**must_fix.**

## 3. Fail-open — otherwise clean

Every other new refusal branch blocks correctly: `_git_line_or_none` catches
`(OSError, SubprocessError)` and a non-zero exit → `None` → caller treats `None` as failure,
never success; `_canonical_review_range`'s four named conditions (unresolvable default
branch, unresolvable `review_sha`, no merge base, degenerate range) all return
`(None, None, error)`; `_load_test_kinds` catches `(OSError, ValueError)`; `reviewed_python_change`
checks `result.returncode` explicitly. All of these ultimately reach `err.append(...)` in
`validate()`, and `hook_mode()` exits 2 on any non-empty `err` (DEC-100/DEC-122 blocking
contract, unchanged). §2's finding is exactly the "miss sails through" shape the dispatch
asked to hunt for — it just sails through via data forgery at a reachable path, not via an
uncaught exception.

## 4. Data exposure — clean

`_classify_canonical_range` wraps `gated_set`/`classify` in `try/except (SyntaxError,
Exception)` and returns a named string (`f"grading {oid[:12]}..{oid[:12]} failed
({type(exc).__name__}: {exc})")` — no traceback, matching D-05's "named repair, no
traceback" requirement; `type(exc).__name__: exc` echoes only the exception's own str, never
process environment or unrelated file contents. Error strings elsewhere echo `path` (repo-
relative `.harness/harness.json`) and `review_sha`/`reviewed` values already visible to
whoever is reading their own digest — no new information disclosed beyond what a refusal
needs to name a repair.

## 5. Secrets — none

Full-diff sweep (`api[_-]?key|secret|password|token|BEGIN (RSA|OPENSSH|PGP)|AKIA...|ghp_...`)
returns only prose discussing the *concept* of a secret/token (SEC-01 commentary, an SC-09
checklist item, and a `dis`/`tokenize` stdlib-module mention) — no credential material.

## D-03/D-05/D-07 status

Unaffected by §2's finding: the remedy stays inside the one importable seam, keeps every
grading/derivation failure a named refusal, and adds no second grader or subprocess CLI call.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Crafted artifact: traversal redirects grading's -C root to an attacker-reachable checkout, defeating both SEC-01's SHA-binding and BUG-1081's mechanical recomputation at once — critical, demonstrated against the real worktree."
  in_scope: true
  scope_reason: "Diff adds a gate whose entire purpose is to stop a reviewer's digest from asserting an unearned code_grade; the threat model (adversarial digest, gate-decision integrity) is exactly Tampering/EoP across the digest/feature.json trust boundary."
  severity_max: critical
  findings: 1
  must_fix:
    - "validate-digest.py: FEATURE_DIR_IN_ARTIFACT_RE / _repo_root_for_feature accept `.`/`..` tokens in the artifact:-derived <repo>/<FEAT> segments, letting a crafted digest (paired with two files the reviewed branch's own author can freely commit into their own worktree) redirect every code-grade git operation to a different checkout that shares this repo's object store — defeating the SHA binding, the branch corroboration, and the new mechanical recomputation simultaneously. Reject '.'/'..' (and any non-identifier) tokens in the captured segments, or verify the resolved feature_dir is a literal descendant of root before trusting it."
  threat_model:
    - { boundary: "digest artifact: text -> feature_dir/root resolution (validate-digest.py:_feature_dir_from_artifact/_repo_root_for_feature)", stride: T, mitigated: false }
    - { boundary: "digest reviewed:/code_grade: enum vs repository-computed mechanical result (code_grade_enforcement_error)", stride: E, mitigated: false }
    - { boundary: "review_sha/branch binding via feature.json (code_grade_bound_to_review, _branch_corroboration_error)", stride: T, mitigated: false }
    - { boundary: "git argv construction (commit_oid, all -C invocations)", stride: T, mitigated: true }
    - { boundary: "grading crash surfaced to the digest author (_classify_canonical_range)", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-security-reviewer-c1.md
```
