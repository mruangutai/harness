# FEAT-58 — the converted H-01 task, added as N-14

**N-14 is in `plan.yaml`, added through `plan-merge.py apply`. Task count 12 -> 13. `approval:` is
untouched — still `approved`, still seven rulings — and no decision, criterion or existing task
moved.** The only other line in the working diff for `plan.yaml` is `status: plan -> ready` at line
3, which pre-existed this run (it is the signature-time station move, not mine).

## The task

|Field|Value|
|---|---|
|`id` / `title`|`N-14` — assert the feature-directory name set the shipped audit reaches at the owner root equals the corpus on disk, with two collected red proofs|
|`traces`|`REQ-03`, `SC-16`|
|`change_type`|`scaffolding`|
|`execution_mode`|`main-session-direct` (DEC-174 — runs the shipped `check-state.sh`, reads `harness_boundary.py`)|
|`depends_on`|`[N-06, N-10, N-13]`|
|`files`|`tests/integration/test-check-state-audited-root.py`|
|`verify`|literal `|` block: `python3 tests/integration/test-check-state-audited-root.py`|
|`status`|`ready`|

**The assertion is a NAME SET, never a count.** The reached side is a disk glob over the resolved
root's `.harness/*/features/*` (`check-state.sh:118-120`, pre-N-06), so name-set equality is
exactly and only a claim about *which root was resolved* — which is M-01's named remedy, folded in
per the operator's Q1 without touching SC-16.

**Three runs, all collected, all read-only.** RUN A green at the owner root, with a MARKER-less
`HARNESS_PROJECT_DIR` as a root witness (the discard notice names the derived root; N-13's stripped
run and its notice-absent clause are unchanged). **RUN B is the MISSING-producing mutation**: a
staged copy of the bin directory whose reached-side comprehension excludes exactly one real feature
name, chosen at run time as the lexicographically first entry that is not this feature's id —
expected minus reached is non-empty, the audit gates, and the shared assertion function reddens
naming that name. RUN C runs the shipped script against a synthetic MARKER-carrying temp root,
proving the silent honoured-override branch is observable and the equality is root-sensitive.

**The cycle-8 staging is named WITHDRAWN in the task text**, with the reason (`MISSING=[]` /
`UNEXPECTED=10` arithmetically; tolerated by clause 1 as PP-03 loosened it; recording it as a red
would be a falsified record).

## `depends_on` — N-13 is in, N-02 is out

N-13 **is** a dependency: N-14 is the red proof for the PART 1 surface N-13 establishes, and the
green baseline must exist first. Acyclic — N-13's own `depends_on` is `[N-02, N-06, N-10]` and does
not name N-14 (verified by loading the file). **N-02 is dropped** from N-13's set: it ships
`worktree-state.py`, which only N-13 PART 2's disposable-worktree half uses. N-14 creates no
worktree and never calls it, so the edge would be false ordering.

## `change_type: scaffolding` — the justification

`scaffolding` has `always: []` in `.agents/skills/harness/templates/harness.json:88-90`, and N-14
adds one test file and no production code — so the label demands no test kind the task cannot
supply, which is the shape VL-05 was raised for. It is what N-13 carries for the same reason.

## Anchor correction, carried into the task text

The dispatch and the M-01 finding cite the silent honoured-override return at
`harness_boundary.py:78`. Re-derived against the file: `:78` is the `os.environ.get` read, the
silent `return os.path.abspath(override)` is at **`:81`**, and the discard-notice print is at
**`:82-86`**. The task instructs re-derivation again at build time.

## Untouched — verified on disk, not assumed

`git diff --numstat` on `plan.yaml`: `165 1`. The single removed line is `status: plan`; the 164
added lines are one hunk at `@@ -3815,0 +3816,164 @@`, all inside N-14. Reloaded with `safe_load`:
13 tasks, `approval.status: approved`, 7 rulings. `check-plan-routes.py` on this plan exits **0**
(N-14 prints the same DEC-174 TASK `DEVIATION` line every sibling task prints; 0 violations).

## Open questions

- **Q1 (non-blocking):** N-13 PART 1's own RED PROOF paragraph still instructs the withdrawn
  cycle-8 staging verbatim. N-14's text names it as withdrawn, but N-13's task body was out of
  scope here, so the executor of N-13 meets the withdrawn instruction first. The operator may want
  `amend` on N-13's `intent` to point at N-14 — that is a change to an existing task and therefore
  not mine.
