---
name: harness-review
description: Review a change against a pinned SHA — spec compliance first, then code quality. Pins review_sha so later commits cannot shift what was reviewed, and reconciles any human hand-edits. Use before shipping or merging, or when asked to review a feature branch or working diff.
---

# Harness: Review

Review a change against **a pinned commit, never a moving `HEAD`**, in two ordered stages.

Two invariants: **the diff target cannot move** (a commit mid-review must not change what you
reviewed), and **hand-edits never inherit a passing review**.

## Process

### 1. Pin the SHA

```bash
git rev-parse HEAD                      # this is review_sha
git merge-base HEAD <base>              # this is base
```

Record it:

```
.harness/features/<FEAT>/review_sha     # contains the SHA and the timestamp
```

Every subsequent step diffs `base..<review_sha>`. **Never `..HEAD`.** If a `review_sha` already exists
from an earlier cycle, note both — what changed between them is the fix cycle's work.

### 2. Reconcile human edits — do this BEFORE reviewing

```bash
git log --format='%h %s' <previous_review_sha>..<review_sha> | grep '\[harness:human\]'
git status --porcelain
```

| Found | Action |
|---|---|
| `[harness:human]` commits since the last pin | **Report them explicitly** and treat the paths they touch as unreviewed. They do not inherit any earlier pass |
| Uncommitted changes outside `.harness/**` | **Stop.** Report the dirty tree and ask the user to commit (with `[harness:human]`) or stash. Reviewing a tree that does not match any commit produces a meaningless verdict |
| Unattributed commits that look manual | Report as a finding — attribution is what makes recovery and review scope derivable |

The invariant: **a hand edit is never silently in scope.** Shipping on a green review that never saw the
user's change is worse than halting.

### 3. Stage one — spec compliance

**Ordered first deliberately** — wrong-thing-built-well is the costlier failure, and finding it
second wastes the quality pass.

Read `.harness/features/<FEAT>/BRIEF.md`. For each `REQ-NN` and each `SC-NN`:

- Is it delivered by this diff, or explicitly out of scope for this change?
- For `verify: automated` criteria — does the named test kind actually exercise it? (`harness-qa-gate`
  owns running them; you check the mapping exists.)
- For `verify: inspection` criteria — **this is where you verify them.** Cite `file:line`.
- For `verify: uat` criteria — note them as pending the user, not as met.

Also flag **scope leakage**: work in the diff that no REQ asked for. Unrequested changes are a finding
even when they are improvements.

### 4. Stage two — code quality

Only after stage one. Judge against the codebase's existing conventions, not an abstract ideal.

Look for: correctness bugs, unhandled errors, silent failure paths, missing input validation, dropped
async rejections, off-by-one and boundary conditions, resource leaks, dead code left behind,
copy-paste divergence, and comments that no longer match the code.

**Do not** report formatting a linter would catch, or restyle to personal preference.

### 5. Classify findings, and gate honestly

Severity levels are defined in `harness-code-review` (one canonical copy). Gate rule:
`must_fix` non-empty or `severity_max ≥ high` → `FAIL`; otherwise `PASS` with notes. Style and
opinion never gate — one permanent nit must not loop forever.

Every finding needs a concrete failure scenario: **specific inputs or state → specific wrong outcome.**
"This could be fragile" is not a finding. If you cannot state how it breaks, drop it.

## Output

```
VERDICT: FAIL      reviewed base a1b2c3d..def5678 (pinned)

Human edits       1 commit — [harness:human] fix filter import.
                  Touches web/src/filter.ts. Not covered by any earlier
                  review; included in this one.

Spec compliance   REQ-01 delivered. REQ-02 NOT delivered — filter state
                  is not persisted, so it won't survive a reload.
                  SC-03 verified: no PII on the filter path (filter.ts:22-40).
                  SC-02 pending your UAT.

Must fix
  1. REQ-02 unimplemented — no persistence for filter state.
  2. filter.ts:31 — unhandled rejection if the author list fetch fails;
     the control renders empty with no error, so a network blip looks
     like "no authors".

Notes (not blocking)
  - filter.ts:52 duplicates the sort in list.ts:88; worth extracting.
```

## Red flags

| Thought | Reality |
|---|---|
| "I'll just diff against HEAD" | Then a commit mid-review silently changes what you reviewed. Pin it |
| "There are uncommitted changes, I'll review them too" | You cannot pin what is not committed. Stop and ask |
| "The user edited that file, so presumably it's fine" | A hand edit is the *least* reviewed code in the diff |
| "Quality first, spec after" | Wrong order. Wrong-thing-built-well is the more expensive failure |
| "This is ugly, that's a must_fix" | Style never gates. `must_fix` means it is broken |
| "I found 30 things" | Rank them. A list nobody reads gates nothing |
