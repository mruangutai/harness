# Security review — BUG-1081-code-grade-enforcement (c2)

review_sha `2562e45a` (re-pinned), range `827219b5..2562e45a` (the two-file panel-cycle-1 fix).

## VERDICT ON CYCLE 1's CRITICAL: **CLOSED**

`_contained_feature_dir` refuses every traversal, encoding, and symlink construction I threw
at it, including the exact exploit string c1 demonstrated. Evidence below is freshly re-run
against the real worktree and the real pre-fix git blob — not adopted from the briefing or
from c1's note.

## 1. Before/after, re-derived myself

**Before** (827219b5) — ran the *verbatim* pre-fix `_feature_dir_from_artifact` /
`_repo_root_for_feature` source (copied byte-for-byte from `git show
827219b5:.claude/skills/harness/bin/validate-digest.py`, not reimplemented) against the real
worktree root:

```
text = "artifact: .harness/../features/../notes/fake.md\n"
_feature_dir_from_artifact(text, root) -> .../BUG-1081-code-grade-enforcement/.harness/../features/..
_repo_root_for_feature(feature_dir)    -> /Users/molchairuangutai/GitHub/harness
worktree under review                  -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement
SAME AS worktree under review?         -> False
```

`git worktree list` confirms `/Users/molchairuangutai/GitHub/harness` is the **main checkout**
(branch `main`) and this worktree is one of its linked worktrees, sharing the same object
store — the exact redirect c1 measured, reproduced independently.

**After** (2562e45a, imported the real module via `importlib.util.spec_from_file_location`,
no reimplementation):

```
_feature_dir_from_artifact(".harness/../features/../notes/fake.md", root)
  -> feature_dir=None
  -> error="code_grade cannot be bound to review_sha: artifact path '.harness/../features/..'
            contains a relative segment — write your review under this feature's own
            .harness/<repo>/features/<FEAT>/notes/ directory, not a path that traverses out
            of it."
```

The honest line still resolves, and its root is the checkout under review, not the parent:

```
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-...-c2.md
  -> feature_dir = <worktree>/.harness/harness/features/BUG-1081-code-grade-enforcement
  -> _repo_root_for_feature(feature_dir) == <worktree>   (== real root, not the parent repo)
```

## 2. Defeat attempts — every one, including the negatives

All run via the real `_feature_dir_from_artifact`/`_contained_feature_dir` imported from the
pin. `feature_dir is None` = refused.

| Attempt | Input | Outcome |
|---|---|---|
| URL-encoded `..` | `.harness/%2e%2e/features/%2e%2e/notes/fake.md` | **Not a defeat.** `os.path` never URL-decodes; `%2e%2e` is a literal (nonexistent) directory name, contained under root. Resolves to a dir on disk that doesn't exist — a normal `feature.json`-unreadable refusal downstream, not a traversal. |
| Unicode dot look-alikes (fullwidth `．．`, one-dot-leader `․․`) | `.harness/．．/features/．．/notes/fake.md` | **Not a defeat.** Same reasoning — literal segment names, not filesystem-special; `os.path.realpath` does not fold them to `.`/`..`. Contained. |
| Trailing-dot segment `...` | `.harness/.../features/x/notes/fake.md` | **Not a defeat.** Three dots is a literal directory name to POSIX, distinct from `..`; `_contained_feature_dir`'s realpath check leaves it under root. |
| `. .` (dot-space segment) | `.harness/. ./features/x/notes/fake.md` | **Refused, but earlier than expected** — `artifact:\s*(\S+)` only captures up to the first whitespace, so the artifact value truncates to `.harness/.` before `_contained_feature_dir` ever runs. Refused by the earlier "does not name a `.harness/<repo>/features/<FEAT>/` location" branch, not by the segment check. Same outcome, different gate — worth recording so a reader doesn't credit the wrong function. |
| Whitespace-only segment | `.harness/   /features/x/notes/fake.md` | **Refused**, same `\S+`-truncation mechanism as above. |
| Trailing dot on a real name, `harness.` | `.harness/harness./features/x/notes/fake.md` | **Not a defeat.** `harness.` != `..` to POSIX; contained, just a directory that doesn't exist. |
| **`<repo>` segment is a symlink out of the tree** | fixture: `<tmp_root>/.harness/evilrepo` → symlink → `<tmp_root_outside>` | **Refused.** `_contained_feature_dir` returns `(None, "...resolves outside this checkout...")`. This is the one the token check structurally cannot see — confirmed the realpath check is what catches it, built and tested live under a `/tmp` fixture root (never the worktree). |
| **`<FEAT>` segment is a symlink out of the tree** | `<tmp_root>/.harness/honestrepo/features/evilfeat` → symlink → outside | **Refused**, same mechanism. |
| Resolves exactly **to** `root`, not strictly below | symlink `<tmp_root>/.harness/selfrepo/features/selffeat` → `<tmp_root>` itself | **Refused.** `startswith(real_root + os.sep)` requires strictly more than `root`'s own realpath — an exact match fails the `+os.sep` startswith and is rejected, not silently accepted. Also confirmed directly: `_contained_feature_dir(root, "")` is refused earlier, by the empty-segment check. |
| Absolute artifact path | `/etc/.harness/x/features/y/notes/a.md` | **Not reachable at all — safe by construction, not by the containment check.** `FEATURE_DIR_IN_ARTIFACT_RE.search()` is unanchored, so it matches the substring starting at the literal `.harness/` and **discards** the `/etc/` prefix entirely; the captured group can never itself begin with `/` (the regex always starts the capture at `\.harness`). `os.path.join(root, relative)` with a non-absolute second argument can never override `root`. Confirmed: resolves to `<root>/.harness/x/features/y`, inert. |
| Windows-style separator | `.harness\..\features\x\notes\fake.md` | **Refused, but by accident of platform, not design intent being exercised.** `path.replace(os.sep, "/")` is a no-op on this POSIX host (`os.sep == "/"`), so the backslash-separated string never matches `FEATURE_DIR_IN_ARTIFACT_RE` (which requires literal `/`) and is rejected as "does not name a `.harness/<repo>/features/<FEAT>/` location" before `_contained_feature_dir` runs. Does not matter in this deployment — this validator only ever runs from this repo's own POSIX tooling (hook script, CLI, tests); there is no Windows execution path in this repo to make the no-op consequential. |

## 3. `feature_dir=` override seam — reachability from a digest

**Not reachable from a digest, in production.** Grepped every production call site of
`validate(..., feature_dir=...)` in `.claude/skills/harness/bin/`:

- `check-state.sh` (line ~1077, via the cached `_vd_mod.validate("lead", ...)`): **no
  `feature_dir` argument at all** — falls to `None`, i.e. the digest-derived,
  now-contained path.
- `validate-digest.py`'s own `hook_mode()` (line ~1710): `feature_dir=_hook_feature_dir(text,
  d.get("harness_feature"))` — the **one** production caller that supplies it.
- Every other `feature_dir=` occurrence in the tree is in `test-validate-digest.py` (test
  fixtures only, unreachable in production).

`_hook_feature_dir`'s own inputs are host-controlled, not digest-controlled:
`owner_root = _root_or_none()` (git/filesystem introspection) and `feature =
d.get("harness_feature")` — a field of the **SubagentStop hook payload**, populated by the
harness runtime's own dispatch bookkeeping (which agent, which feature this subagent was
spawned under), not extracted from the agent's own returned text (`d.get("last_assistant_message")`
is the separate field that becomes `text`). And even so, `_hook_feature_dir` still routes its
result through `_feature_dir_from_artifact(text, checkout_root) → _contained_feature_dir`
before returning — so even the one production seam that DOES pass `feature_dir=` is itself
gated by the same containment check, just measured against a registry-resolved root instead
of the ambient one.

## 4. `_hook_feature_dir`'s registry-resolved root — can a digest move it?

**No.** `inflight_registry.feature_root(owner_root, feature)` looks `feature` up in a
host-maintained registry mapping feature ids to their assigned worktree; a digest that
somehow forced an unexpected `feature` value would at worst hit a legitimate *different*
harness-managed worktree (wrong-feature confusion, not root escape) or fall back to
`owner_root` on any lookup exception. Every candidate that function can return is still run
through `_contained_feature_dir` before it reaches `_read_review_sha`. `_hook_feature_dir`'s
broad `except Exception: return None` is pre-existing (unchanged by this delta) and, on
failure, degrades to the ambient-root derivation path — same containment, potentially wrong
feature identity, never a root escape. Out of this delta's scope; noted, not a new finding.

## 5. `_contained_feature_dir` fails closed on every branch

Read every return and every exception path (`validate-digest.py:793-825`): two explicit
`(None, error)` refusals (relative-segment token check; realpath-descendant check) and one
success return. No `try/except` inside the function, and none is needed — `str.split("/")`
and `os.path.realpath()` do not raise for the inputs this function receives (a regex-captured
string). Both error messages name the offending path (`{relative!r}`) and the required
location (`.harness/<repo>/features/<FEAT>/notes/`) — a reviewer who hits either honestly can
repair it without guessing.

## 6. STRIDE, re-derived at this pin

| Boundary | STRIDE | Mitigated |
|---|---|---|
| digest `artifact:` text → feature_dir/root resolution | T | **true** (was false at c1; closed by `_contained_feature_dir`, defeat-tested above) |
| digest `reviewed:`/`code_grade:` enum vs. repository-computed mechanical result | E | **true** (was false at c1; the comparison was always correct, only the root feeding it was forgeable) |
| `review_sha`/`branch` binding via `feature.json` | T | **true** (was false at c1; `feature_dir` is contained before `feature.json` is ever opened) |
| symlinked `<repo>`/`<FEAT>` path component | T | **true** (new boundary this delta introduces a defence for; realpath-descendant check demonstrated to catch it) |
| `feature_dir=` override seam reachable from digest content | T | **true** — not reachable; host-controlled input only, and still gated by the same containment when supplied |
| git argv construction (`commit_oid`, all `-C` invocations) | T | true (c1-closed, unaffected by this delta) |
| grading crash surfaced to the digest author (`_classify_canonical_range`) | I | true (c1-closed, unaffected by this delta) |

## 7. Residual — none blocking

No new finding at this pin. One pre-existing, out-of-delta-scope observation, assessed and
dismissed rather than silently dropped: `_hook_feature_dir`'s blanket `except Exception:
return None` (unchanged by this delta) degrades a registry-lookup failure to the ambient-root
derivation, which could bind a review to the wrong feature within the same owner checkout —
never a root escape, since containment still applies. **Nature: chore. Severity: low.**
Backlog-worthy if anyone wants tighter feature-identity guarantees; not a security gap this
delta introduced or is asked to close.

## 8. Housekeeping

- `sha256sum` of both reviewed files matches `git show 2562e45a:<path>` exactly — confirmed no
  worktree writes outside this note.
- Full `test-validate-digest.py` suite: `ALL PASSED` (includes the new
  `check_artifact_path_traversal`/`_assert_honest_artifact_resolves` cases).
- `code-grade.py --base $(git merge-base origin/main 2562e45a) --head 2562e45a`: every
  function `RESULT: PASS`, `PASSING: 44`, no `RESULT: FAIL` anywhere in the output —
  reproduces the briefing's claim independently.

```yaml
VERDICT: PASS
DIGEST:
  headline: "CLOSED: _contained_feature_dir refuses the c1 exploit string and every encoding/symlink/root-equality variant I tried against it, while the honest artifact path still resolves to the worktree under review — re-derived independently against both the pre-fix and post-fix source, not adopted from the briefing."
  in_scope: true
  scope_reason: "Direct re-verification of a prior critical finding on the trust boundary between a reviewer's own artifact: text and the repository root every code-grade git operation runs against (T/E across digest<->feature.json/git)."
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "digest artifact: text -> feature_dir/root resolution (_feature_dir_from_artifact/_contained_feature_dir)", stride: T, mitigated: true }
    - { boundary: "digest reviewed:/code_grade: enum vs repository-computed mechanical result (code_grade_enforcement_error)", stride: E, mitigated: true }
    - { boundary: "review_sha/branch binding via feature.json (code_grade_bound_to_review, _branch_corroboration_error)", stride: T, mitigated: true }
    - { boundary: "symlinked <repo>/<FEAT> path component defeating the token check alone", stride: T, mitigated: true }
    - { boundary: "feature_dir= override parameter reachability from digest content", stride: T, mitigated: true }
    - { boundary: "git argv construction (commit_oid, all -C invocations)", stride: T, mitigated: true }
    - { boundary: "grading crash surfaced to the digest author (_classify_canonical_range)", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-security-reviewer-c2.md
```
