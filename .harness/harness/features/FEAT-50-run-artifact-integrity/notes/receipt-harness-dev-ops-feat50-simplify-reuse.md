# REUSE angle — FEAT-50 plan surface

**Conclusion:** one real finding (T-03 hand-rolls a feature→worktree lookup that already exists
verbatim in `inflight_registry.py`), the other two named checks come back clean with the
plan's own reasoning confirmed against source. No `verify:` clause hand-rolls an existing check.

## Findings

| id | severity | element | summary |
|---|---|---|---|
| REUSE-01 | med | T-03 (`plan.yaml:288-306`) | duplicates `inflight_registry.feature_root()` and `harness_boundary.checkout_relative()` instead of calling them |

### REUSE-01 — T-03 re-derives a feature→worktree lookup `inflight_registry.py` already has

**Element:** T-03, `plan.yaml:289-306` (intent body), i.e. the future body of
`.claude/skills/harness/bin/check-domain.sh`.

**Summary:** T-03's intent spells out, step by step, "call `linked_worktrees(root)`, select the
checkout whose basename equals the feature id, then check the target resolves inside it" — but
`inflight_registry.py:260-268` already has exactly this function:

```python
def feature_root(owner_root, feature):
    """Resolve the checkout assigned to `feature`, falling back to the supplied owner root."""
    try:
        for worktree in harness_boundary.linked_worktrees(owner_root):
            if os.path.basename(worktree) == feature:
                return worktree
    except Exception:
        pass
    return owner_root
```
(`.claude/skills/harness/bin/inflight_registry.py:260-268`)

This is the identical "enumerate `linked_worktrees`, match by basename, fall back when absent"
algorithm T-03 asks for, already exercised by the single-flight PM claim path. The second half of
T-03's intent — "resolve both sides through `harness_boundary.real` before comparing" so "the
target resolves inside it" — is also already solved, by `harness_boundary.checkout_relative()`
(`harness_boundary.py:102-135`), which answers "which checkout does THIS path actually stand in"
directly (via `worktree_owner`, `harness_boundary.py:515`) rather than by enumerating every linked
worktree and testing containment against the one that was picked. `check-domain.sh` already calls
`checkout_relative` this way at `check-domain.sh:250-251` and `check-domain.sh:1009-1012` for the
worktree-stripped candidate and the display path.

**Failure scenario:** T-03's intent does not pin the containment test's implementation (it only
says "resolve both sides through `real` before comparing"). The natural hand-rolled form is a
string-prefix or `startswith` test on `real(target)` against `real(selected_worktree)`. That is
exactly the bug class `worktree_owner`'s own docstring calls out and had to fix once already:
`<root>/.claude/worktrees-old/wt` must not read as inside `<root>/.claude/worktrees`
(`harness_boundary.py:548-549`). A sibling worktree whose directory name happens to prefix-match
the selected one (e.g. a rename-in-progress checkout, or two features sharing a numeric prefix)
would then be misclassified as "inside" the target worktree, silently defeating T-03's own fix —
the identical failure shape #103 fixed once in `worktree_owner`, reappearing because the
comparison was re-derived instead of reused. Separately, two independent re-implementations of
"which worktree does the feature id name" (`inflight_registry.feature_root` and T-03's inline
version) is the two-spellings-in-lockstep cost this angle exists to flag: a later change to
`linked_worktrees`'s ordering, or to how a feature id is derived, has one caller updated and one
forgotten.

**Alternative:** have T-03's intent call the two existing functions instead of re-deriving them:
`wt = inflight_registry.feature_root(root, feature_id)`; if `wt == root` (no match — the fallback
`feature_root` already returns), the check does not fire, matching T-03's own "no registered
worktree" branch exactly. Otherwise get the checkout the TARGET itself stands in via
`ck = harness_boundary.checkout_relative(target)` and compare `harness_boundary.real(ck[0] if ck
else root)` against `harness_boundary.real(wt)` — a direct equality on two already-correctly-computed
checkout directories, never a prefix/containment test. This drops the intent's own enumerate-then-
contain paragraph (`plan.yaml:289-306`) to one lookup plus one equality, and reuses code with an
existing worktrees-old-prefix regression test behind it rather than opening the same hole again.

## The three named checks

**1. D-03/D-04 checkout binding vs `harness_boundary.py`.** NOT clean — see REUSE-01 above.
Confirmed: `worktree_owner` (`harness_boundary.py:515`), `checkout_relative` (`:102`),
`linked_worktrees` (`:138`), `real` (`:258`), `root_above` (`:84`) all read. `root_above` is not
implicated — it answers "which checkout is the SESSION rooted in" (a `_root()` bootstrap concern),
not "which checkout does a WRITE TARGET stand in", so T-03 composing on top of it would be the
wrong primitive; T-03 correctly does not use it. The FEAT-42 one-root resolver
(`resolve_root`/`root_from_script`) is a separate, correctly-untouched concern (session root, not
per-write checkout) and T-03 does not duplicate it.

**2. D-05/T-04 digest preservation vs `harness_merge.py`.** Clean. Read `harness_merge.py` in full
and DEC-199 (`DECISIONS.md:5674-5743`) in full. DEC-199 scopes the locked union-merge core to
**exactly four named consumers** — `plan-merge.py`, `observations-merge.py`,
`expertise-merge.py`, `inflight_registry.py` — each keyed on an identity a prose digest does not
have (task id, entry id, whitespace-normalised bullet text; `DECISIONS.md:5690-5694`). `digest.md`
is unstructured narrative with no such key, so it does not fit the union scaffolding without
inventing a new keying scheme DEC-199 does not define. More to the point, the two mechanisms solve
different observable requirements: `harness_merge` MERGES two concurrent writes into one union;
REQ-04 (`plan.yaml:331`, D-05 `plan.yaml:109-119`) is a SEQUENTIAL clobber across cycles by one
writer at a time, and the requirement is that the SECOND write be REFUSED, not silently combined
with the first — a lead reusing a stale run dir should be told to take a fresh one, not have its
new digest spliced onto the old one. D-05's own `because:` clause already states this reasoning.
Building the refusal in `check-domain.sh`'s existing shape-rule family (D-06, beside
`RE_STATE_YAML`) is the mechanism REQ-04 actually forces; routing it through `harness_merge`
instead would have been the wrong-mechanism move this angle looks for, and the plan did not make
it.

**3. T-02/T-05 mutant-copy idiom vs FEAT-45 precedent.** Clean, with the existing convention
already the same shape T-02/T-05 follow. `test-check-state.py`'s `inv32-red` case has its own
NAMED, file-local pair of helpers (`_inv32_mutant_fixture_passes`,
`_inv32_mutant_is_discriminating`, `test-check-state.py:3058-3089`) — not exported, not imported
by any other test file. `test-check-domain.py` itself already hand-rolls the identical
copy-beside-original/chmod/finally-remove idiom **inline, twice, independently**, with no shared
helper even within that one file (the sweep/clean-tracked case at
`test-check-domain.py:2229-2270` and the SC-07 write-path case at `:2368-2382`). No cross-file
test-helper module exists anywhere under `.claude/skills/harness/bin/` (`grep` for
`test_helpers`/`mutant_helper`/a shared import between `test-*.py` files returns nothing). Given
that established convention, T-05 explicitly instructing case 7 to "reuse case 4's mutant helper"
(`plan.yaml:455-457`) is already an IMPROVEMENT over the file's own existing precedent (which
duplicates twice, unshared), not a gap. T-02 has exactly one reachability case (`empty-red`), so
there is no intra-file duplication risk to flag there, and a cross-file (`test-validate-digest.py`
↔ `test-check-domain.py`) shared helper would be a new abstraction with zero precedent anywhere in
this codebase for a mechanism that mutates two different scripts with two different search
strings — not a case of the plan re-implementing something that exists, so not flaggable under
this angle.

**Verify clauses:** scanned all seven tasks' `verify:` blocks (T-01 through T-07). None hand-rolls
a check an existing script already performs — T-03's verify reuses `check-domain.sh --resolve`
itself; T-07's verify reuses `gen-decisions-index.py --stdout` via diff rather than re-deriving the
index format. T-04's inline Python `verify` block does source-text regex assertions
(`RE_RUN_DIGEST` present, in `SHAPE_PATTERNS`, absent from the sweep list) that no existing script
performs, so nothing to flag there.

## What was read
`.claude/skills/harness/bin/harness_boundary.py` (`worktree_owner`, `checkout_relative`,
`linked_worktrees`, `real`, `root_above`, `resolve_root`, `classify` advertise block), full
`.claude/skills/harness/bin/harness_merge.py`, `.claude/skills/harness/bin/inflight_registry.py`
(top-level imports, `_matches`, `_visible`, `feature_root`), `.claude/skills/harness/bin/check-domain.sh`
(all `harness_boundary`/worktree-stripping call sites), `.harness/harness/docs/DECISIONS.md` DEC-199
(full entry) plus DEC-154/DEC-180 headers, `.claude/skills/harness/bin/test-check-state.py`
(`inv32-red` helpers), `.claude/skills/harness/bin/test-check-domain.py` (both inline mutant
sites), `.claude/skills/harness/bin/test-validate-digest.py` (grepped for a mutant helper — none
found), full `plan.yaml` (all seven tasks, all eight decisions, all `verify:` blocks).
