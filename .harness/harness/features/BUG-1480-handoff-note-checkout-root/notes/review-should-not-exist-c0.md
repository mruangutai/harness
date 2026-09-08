# Review — should-not-exist reader, cycle 0

Feature: BUG-1480-handoff-note-checkout-root
Pinned: review_sha 4de92e751508f4144e4c1233fcfa715947532ee2 (branch feat/BUG-1480-handoff-note-checkout-root, base 64fcaa34)
Reader: ShipB1.ReviewPanel.ShouldNotExist (independent, read-only)
All line anchors below measured at review_sha via `git show 4de92e75:<file>`.

## Verdict on the assignment's three questions

### 1. Is this the right change at all? — Yes. No part of it is work that should not exist.

Mechanism verified end-to-end at the pin: `_checkout_root` (check-domain.sh:1151-1163) mirrors
`_norm`'s absorb-and-fall-back shape exactly (same `try/except Exception`, same
`real(_ck[0]) != real(root)` guard, falls back to `root`, raises nothing, exits nowhere), and the
ONLY behavioural change is the argument swap at the `handoff_done_when.problems(...)` call inside
the `RE_HANDOFF` branch of `shape_problems` (check-domain.sh:1761-1762). Every dispatch route —
PRE Edit identity, PRE Edit reconstructed, PRE Write, POST named-file, and the POST sweep — builds
the uniform 4-tuple with a real absolute path as its fourth element (the sweep's
`targets.append((_norm(_p), _f.read(), _show(_p), _p))` carries `_p` absolute), so the fix covers
the sweep route with no extra code. The `not path -> root` guard is reachable only if a route ever
passes None, and then the pre-fix behaviour is preserved rather than a crash. Nothing here is
speculative scaffolding; every line is load-bearing.

### 2. REQ-06's containment narrowing — NOT worse than info, on corpus evidence.

I surveyed every handoff note in the repository (65 files under the main checkout's
`.harness/harness/features/*/notes/handoff-*.md`, 30 under this branch's copy). Every single
`finding:` and `approval:` pointer targets an artifact of the note's OWN feature — its BRIEF.md,
STATE.md, plan.yaml, or a sibling note in the same feature dir. Zero cite `.harness/DECISIONS.md`,
zero cite a cross-feature artifact, zero cite anything that exists only in the main checkout.
Feature dirs are git-tracked, so a worktree's checkout carries every feature-local artifact its
branch point knew. The theoretical main-only shapes (a DEC heading recorded in main after the
branch diverged; an uncommitted sibling feature's finding) do not occur once in the observed
corpus, and when they eventually do occur the refusal is loud and names the pointer and target.
The open info item stays info.

HOWEVER — the same survey surfaced a sharper, distinct problem the BRIEF does not see; it is
finding 1 below.

### 3. Are the four rows the right four? — Yes, and each earns its place; the real absence is a fifth.

- fixture row (test-check-domain.py:4417): guards against `make_linked_worktree` or the fixture
  accidentally materialising a main-root copy — without it row 2 can pass vacuously. Buys something.
- `feature dir resolves` (:4420): the red-then-green core. Buys the fix.
- `unresolvable pointer refused` (:4426): green both sides; the vacuity control. Buys row 2's meaning.
- `brief-sc pointer refused` (:4432): second red-then-green with the worktree BRIEF.md path needle;
  proves WHICH copy is read, which row 2 alone cannot. Buys the direction of resolution.

None is dead weight. But all four exercise ONLY the `_feature_dir`-family resolvers (`plan-task:`
via plan.yaml, `brief-sc:` via BRIEF.md). The path-bearing family — `finding:`/`approval:`, which
join `root / match.group(1)` and run `_read_target`'s containment against the same root
(handoff_done_when.py:143, :161, :78) — has NO worktree row at all, positive or negative. The
negative half is the known backlog row (REQ-06 containment, carried; not re-derived here). The
POSITIVE half is distinct and absent: finding 2 below.

## Findings

```yaml
findings:
  - severity: med
    summary: "Every existing handoff note teaches the now-wrong pointer spelling for worktree notes: the corpus-dominant `finding:`/`approval:` PATH is main-root-relative (`.claude/worktrees/harness/<FEAT>/...`), which a worktree-standing note now cannot resolve, and neither the template nor any doc states that PATH became relative to the checkout the note stands in."
    evidence: ".claude/skills/harness/bin/handoff_done_when.py:143,161 (root / match.group(1)) + .claude/skills/harness/templates/HANDOFF.md:13,45 (bare PATH, no root semantics) + e.g. .harness/harness/features/BUG-1286-test-tree-enforcement/notes/handoff-plan.md:57 (one of 30+ notes spelled `.claude/worktrees/harness/...`)"
    scenario: "Post-fix, an agent finally writes handoff-plan.md INSIDE its worktree and copies the precedent spelling `approval:.claude/worktrees/harness/<FEAT>/.harness/harness/features/<FEAT>/BRIEF.md#Approval` (the shape in 30+ prior notes). The resolver joins it to the worktree root, producing `<wt>/.claude/worktrees/...` which does not exist -> 'cannot resolve target' -> exit 2 on an honest note. The agent's cheapest observed escape is the pre-fix workaround — write the note in the MAIN feature dir with the old spelling, which still validates — so precedent quietly steers every future note back to the split-brain location this fix exists to end."
  - severity: low
    summary: "No worktree test row exercises the path-bearing resolver family (`finding:`/`approval:`) positively: both red-then-green rows go through _feature_dir (plan.yaml / BRIEF.md lookup), so the resolver family real notes use most — root-joined pointer path plus _read_target containment against the boundary-returned root — is unproven in the worktree context."
    evidence: "tests/integration/test-check-domain.py:4401-4441 (rows cite only plan-task:T-03.verify, plan-task:T-99.verify, brief-sc:SC-99) vs .claude/skills/harness/bin/handoff_done_when.py:143,161,78 (distinct root / match.group(1) + relative_to path)"
    scenario: "A future regression confined to the root-joined path branch — e.g. containment computed against a differently-normalised spelling of the checkout root than harness_boundary returns — keeps all four new rows green (they never touch that branch) while every real worktree note citing `approval:...BRIEF.md#Approval`, the single most common pointer in the corpus, is refused; the suite reports nothing."
```

## Known residuals honoured (not re-derived, no attention spent)

- `RE_FEATURE_JSON` schema lookup's rel/root mismatch (`for_path=os.path.join(root, rel)` inside
  `shape_problems`) — confirmed it is the ONLY other `root` consumer in the function, so D-03's
  sibling-helper shape leaves no third undiscovered branch live; carried backlog row, not a finding.
- REQ-06 containment has no executable row — carried backlog row; the low finding above is the
  POSITIVE-resolution gap of the same family, which is a different absence.

## D-03 assessment

The sibling helper is the weakest sufficient change, not a workaround. The defect was never in
`harness_boundary` (it already returns the checkout root) nor in `_norm`'s answer (its string
contract is consumed by pattern matching at eleven sites); the defect was DISCARDING `_ck[0]`, and
the helper re-exposes exactly that discarded value at the one site that needs it. Pushing root
derivation down into `handoff_done_when` would import a `harness_boundary` dependency into the
validator and break REQ-03's absorb-at-the-shape-layer design. The duplicate `checkout_relative`
walk per handoff write costs ~0.023 ms by the module's own measurement — immaterial.

[unverified]: I did not re-run the integration suite or the pre-fix RED reproduction; those are the
qa gate's evidence (`notes/qa-BUG-1480-c0.md`, PASS) and the SC-06 peer's assignment. Everything
else above was read directly from `git show 4de92e75:` output.
