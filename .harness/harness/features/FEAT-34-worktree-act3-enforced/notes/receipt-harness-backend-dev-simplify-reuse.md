# REUSE angle — FEAT-34, diff 9165162..513c4a4

BLUF: four findings. Three are genuine, low-cost duplications (a private helper re-spelled,
a raw enumeration re-spelled three ways, and test fixtures re-spelled three ways with an
existing shared-fixture pattern unused). One is a prose rule now stated independently in two
skill files. All are `backlog row after ship` — none reach into behaviour, all are cheap to
fold later, and this pass is flag-only against a pinned SHA regardless.

## Finding 1 — `_repo_arg_for_segment` re-spelled verbatim

`.claude/skills/harness/bin/worktree_terminal.py:107-130` and
`.claude/skills/harness/bin/post-merge-sweep.sh:100-119` carry the identical algorithm
(match `"harness"` literally, else load `fleet.yaml` and match an entry's trailing segment) —
diffed byte-for-byte, only parameter names and docstrings differ, the body is identical.
post-merge-sweep.sh's own docstring names the reason: `worktree_terminal.py`'s module
docstring restricts its public surface to `CLASSES`, `classify`, `classify_all` (D-10), so the
private, same-named helper is "not for import" and gets re-derived instead.

Cost: the fleet-matching rule (currently: `name.split("/", 1)[-1] == segment`) now has two
call sites that must be edited in lockstep on any change to how a repo segment resolves to a
`--repo` argument — e.g. if fleet entries ever gain aliases or a repo can appear at more than
one segment. Nothing enforces the two stay identical; the module's own docstring is what
created the second copy, not an oversight in post-merge-sweep.sh.

Alternative: promote `_repo_arg_for_segment` to worktree_terminal.py's public surface (it
already takes `factory_config` as an explicit parameter, so it has no hidden coupling to the
module's private import cache) and have post-merge-sweep.sh call
`worktree_terminal.repo_arg_for_segment(segment, factory_config)`. D-10 named the public
surface as `CLASSES`/`classify`/`classify_all` only — widening it is a plan-level call, not
mine to make silently.

severity: low
call: backlog row after ship

## Finding 2 — `git worktree list --porcelain` enumerated and parsed three separate times

Three independent copies of the same operation (run `git worktree list --porcelain` with a
given cwd, split on blank lines, pull the `worktree <path>` line):
- `.claude/skills/harness/bin/check-state.sh:1117` (INV-25, untouched by this diff)
- `.claude/skills/harness/bin/worktree_terminal.py:56-70` (`_worktree_list_raw`/`_worktree_paths`, new, private)
- `.claude/skills/harness/bin/post-merge-sweep.sh:65-97` (`_resolve_main_checkout_root`, new)

The dispatch asked me to check the plan's claim that INV-29 replaces INV-25's enumeration
rather than duplicating it. **That claim holds for INV-29 itself** — INV-29's own comment
block at check-state.sh (~line 1191) states plainly "THE ENUMERATION IS NOT REPEATED HERE"
and it is true: INV-29 calls `worktree_terminal.classify_all(root)` and never runs its own
`git worktree list`. But INV-25, several hundred lines earlier in the same file
(check-state.sh:1109-1189, entirely outside this diff's `+`/`-` hunks), still runs its own
raw enumeration and its own blank-line parse — it was never migrated to call
`worktree_terminal.classify`/`_worktree_paths`, so the "replaces" framing is true of INV-29's
relationship to INV-25's *logic*, not of INV-25's own code, which still exists unchanged.
worktree_terminal.py's own docstring at `_worktree_paths` even says it "reuses the exact
parsing shape check-state.sh already uses at :1117-:1135 ... rather than a second parser" —
which describes cloning the shape, not eliminating the original.

post-merge-sweep.sh's third copy exists because `worktree_terminal.classify()` deliberately
skips porcelain index 0 (the main checkout) from its returned records, so a caller that needs
the main checkout path itself — as post-merge-sweep.sh does, to resolve where a *landed*
feature dir lives — cannot get it from the public `classify`/`classify_all` surface at all,
and has no public helper to call instead.

Cost: the porcelain parsing shape (blank-line records, `worktree <path>` line, first record is
always the main checkout) is asserted as a load-bearing invariant in comments in all three
places, but is implemented three times. A change to git's porcelain format, or a bug in the
blank-line split (e.g. a path containing a blank line, or `bare`/`detached` records handled
differently), has to be fixed in three places, and nothing signals when one drifts from the
other two — check-state.sh's own INV-25 is explicitly named in the brief as "already built,
do not rebuild," so this file is the one most likely to go stale silently.

Alternative: add a public `main_checkout_path(root)` to worktree_terminal.py — a thin wrapper
around the existing private `_worktree_paths(root)[0]` — and have both check-state.sh's INV-25
and post-merge-sweep.sh's `_resolve_main_checkout_root` call it instead of running their own
subprocess. That reduces three implementations to one, consistent with D-02's own stated
purpose ("one predicate the gate and the hook cross, so they can never disagree").

severity: med
call: backlog row after ship

## Finding 3 — test fixture helpers re-spelled across three new/extended suites, with an
## existing shared-fixture module unused

`_repo`, `_commit_feature`, `_add_wt`, `_extract_resolved_root`/`_assert_resolved_root_in_fixture`,
`_stub_gh`, and `_sweep_env` are defined independently, with near-identical bodies, in:
- `.claude/skills/harness/bin/test-worktree-terminal.py:32-70` (`_repo`, `_commit_feature`, `_add_wt`)
- `.claude/skills/harness/bin/test-post-merge-sweep.py:90-115,145-184,257-262` (`_extract_resolved_root`,
  `_assert_resolved_root_in_fixture`, `_repo`, `_commit_feature`, `_add_wt`, `_stub_gh`, `_sweep_env`)
- `.claude/skills/harness/bin/test-hooks-install.py:66-89,90-192` (the same set again)

Diffed pairwise (`_commit_feature` between test-post-merge-sweep.py and test-hooks-install.py,
`_add_wt` between the same two, `_extract_resolved_root`/`_assert_resolved_root_in_fixture`
between the same two): bodies are identical or near-identical, differing only in a widened
signature (an added optional `milestone`/`ref`/`new_branch` param, present in
test-post-merge-sweep.py, absent in test-hooks-install.py's older copy) or docstring
presence.

The tree already has the fix for exactly this shape: `.claude/skills/harness/bin/layout_fixtures.py`,
whose own header states the problem this pass would flag verbatim — "Before this module the
stub text, the reader lists and the marker's fleet content were maintained in triplicate...
Edit the table -> edit the stubs HERE, once" (issue #382) — and it is imported by
test-layout-migration.py (`import layout_fixtures as lf`, line 54) and test-check-state.py.
FEAT-34's four new/extended suites did not follow that precedent.

Cost: test-post-merge-sweep.py's `_commit_feature` already widened its signature with
`milestone=None` for INV-30's fixture needs while test-hooks-install.py's copy was not
updated to match (confirmed by diff — test-hooks-install.py:146 has no `milestone` param).
That is the failure this shape produces in practice, already happening once at HEAD: a future
test-hooks-install.py case that needs a milestone on its fixture feature will silently fail to
get one, or a contributor will have to remember to hand-port the change into a third file.

Alternative: a `worktree_test_fixtures.py` (or extend `layout_fixtures.py`'s own convention)
holding `repo()`, `commit_feature()`, `add_wt()`, `extract_resolved_root()`,
`assert_resolved_root_in_fixture()`, `stub_gh()`, `sweep_env()` once, imported by all three
suites — mirroring the exact pattern `layout_fixtures.py` already established and that
`run-unit-tests.sh`'s own drift detector already knows to skip (non-`test-*.py` fixture
modules are excluded from the file-naming scan per layout_fixtures.py's own docstring).

severity: med
call: backlog row after ship

## Finding 4 — Act 3's rule restated in two skill files

The rule "a worktree is never removed from inside itself, because `git worktree remove` exits
0 from inside the tree it deletes" is now asserted independently in:
- `.claude/skills/harness/SKILL.md:434-437` ("**Act 3 is never yours, and the reason is
  mechanical.** `git worktree remove` succeeds at exit 0 from inside the tree it removes...")
- `.claude/skills/harness-handoff/SKILL.md:82` ("**One act is never yours, whatever the table
  says: removing a worktree.** ... because `git worktree remove` exits 0 when run from INSIDE
  the tree it deletes...")

Both are new in this diff (harness/SKILL.md:424-437 gained the enforced-not-remembered
paragraph; harness-handoff/SKILL.md:82 is a wholly new line). They state the same mechanical
fact and the same consequence in different prose, and name the exception differently — the
first says "the main session or the `post-merge` hook", the second says "the main session or
the `post-merge` hook" too, so the *who* is currently consistent, but nothing ties the two
sentences together if either changes: `harness/SKILL.md` is a per-agent doc (worktree
lifecycle for a member/orchestrator standing inside one), `harness-handoff/SKILL.md` restates
it in the "decide or ask" reversibility table's addendum — two different audiences reading
the same rule from two owners.

Cost: a future change to who may remove a worktree (e.g. if the post-merge hook's authority
is later scoped to landed-only merges and a new exception is carved for orchestrators) has to
be applied in both files by hand; there is no cross-reference from one to the other, so a
reviewer changing `harness/SKILL.md` has no signal that `harness-handoff/SKILL.md` carries the
same assertion.

Alternative: state the mechanical fact once in `harness/SKILL.md` (where the fuller three-act
lifecycle context already lives) and have `harness-handoff/SKILL.md`'s line point at it by
reference ("see harness/SKILL.md's Act 3" or similar) rather than re-deriving the git
mechanics in its own words.

severity: low
call: backlog row after ship

## Not flagged

- `check-state.sh`'s INV-30 imports `gh_board` (`_gb30`) purely as an import-liveness check
  and never calls anything on it — this mirrors INV-25/INV-29's own established pattern of
  gating on "the module ships with this repo, so failing to import is a tree defect." Not a
  reuse issue; it is the established idiom applied consistently.
- INV-30's own `gh api --paginate .../milestones` call is a different shape than gh-sync.py's
  existing single-title milestone lookup (`gh-sync.py:722`) and follows INV-26's own
  established precedent of resolving the `gh` binary via `FACTORY_GH` and shelling out
  directly rather than importing gh-sync.py (which is itself a `main`-only script, not a
  library). Consistent with existing convention, not a new duplication.
