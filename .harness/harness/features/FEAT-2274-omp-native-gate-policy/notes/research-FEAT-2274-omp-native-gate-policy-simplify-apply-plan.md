# FEAT-2274 simplify-apply

PASS: F1–F3 folded into the pending draft; F5 pointer applied now; F4/F6 retained. Authorized check exits 0: 27 anchors resolved. No implementation, reader, panel recording, goal-check rerun, git, builds, tests, lint, formatter or smoke invocation. Cycle-1 goal-check stands under SC-09; cycles used 0. Open questions: none. Draft still requires operator approval.

## Adequacy and dispositions

- F1 applied: D-01 choice and T-01 intent require one Python emitter beside hook_guard, script-path-derived identity, preserved stderr diagnostic names, and inline emission only for bootstrap import failure. Explicit counterexample: validate-digest emits gate validate-digest, not diagnostic label check-digest.
- F2 applied: BRIEF SC-02 and T-01 intent name existing narrow-gate spelling/exemption corpora as shared acceptance surface for BOTH extension-side and Python-side classifiers, including startup failure. Matching arrangement remains open; unrelated-command overmatching remains rejected.
- F3 applied: T-01 intent identifies exact legacy assertions: tests/integration/test-gh-close-gate.py FEAT-65 unexpected resolver defect (original lines 263–265, also requires empty stdout); test-branch-create-gate.py run_feat65 (259–261); test-plan-sign-gate.py FEAT-65 unexpected resolver defect (543–545). Each asserts returncode not in (0, 2), injecting resolve_root RuntimeError into a copied isolated bin. Convert matching faults to exit-2 named refusals and retain unrelated bypass controls under the same fault. Crucially plan-sign's existing input is git status (541), so keep that as unrelated control and add a matching gated feature-record command. Reuse fixture idiom where practical, without mandated abstraction.
- F4 skipped (retain as requested): SC-06 adapter refusal-versus-unavailable is a distinct seam. T-01 explicitly retains its controls; no coverage deletion or weakening.
- F5 applied now, not deferred: BRIEF SC-04 and T-03 intent point directly to /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-enforcement-a-2026-11-21.md, section Facts I verified (so pm does not re-derive them). Observed lines 72–83 distinguish published OMP 19.1.0 from stale installed source and identify shared runStructuredSubagent / assertDepthAndSpawnAllowed authority. This owner-checkout note is external evidence, NOT review_sha content. Product inspection retains git show review_sha:path provenance separately.
- F6 skipped (retain as requested): local wire-contract repetition is useful task clarity; T-03 already references D-01. No mandatory change warranted.

Spot-check substantive pointer: T-01 intent's final paragraph identifies plan-sign's git status fixture as an unrelated bypass, rather than converting it incorrectly into a matching denial. This is grounded in tests/integration/test-plan-sign-gate.py original FEAT-65 block, command at line 541.

## Protected-field receipt

Before edits: approval mapping {status: pending}; top-level status plan. Panel captured from panel: through immediately before lanes:; SHA256 264dfefef7c3b8431e9d92d60d49f89b32153b56c07bcda306ae101356d34b5f.

After edits: approval mapping {status: pending}; top-level status plan. Same panel byte-slice SHA256 264dfefef7c3b8431e9d92d60d49f89b32153b56c07bcda306ae101356d34b5f; PANEL_BYTE_DIGEST_IDENTICAL True. T-02 intent unchanged True (SHA256 54bdb938a41ddfcd518932417934594b14fcb4e0a8cabbc57e6425162ff7f23e). No whole-list rewrite: only decisions:D-01.choice, tasks:T-01.intent, tasks:T-03.intent amended; unrelated tasks/fields preserved by field-scoped verbs. BRIEF approval untouched.

## Controlled amendment stdout receipt

All three invocations used control-plane plan-merge.py amend with --expect-sha256 and --value-file /dev/stdin; no direct plan write. Expected field hashes from amend --show: D-01.choice 2433309af568b4a2a6495854409e23fedaafc53957fdfb1be89a26d5baca2537; T-01.intent a0c92b8f29d6a94236c982d4e7d1ee1e3e1dabcc4e2813f52ed2aa3bef013299; T-03.intent eadb97daddaec42285d103cc598715314c0df33c3b7833d585c0dc31adf5250a. Each exited 0. Full captured stdout follows (no stderr). No APPROVAL-RESET: receipt occurred; no remote call was made. The automatic changed-state notices below do not authorize Build or approval; they are preserved, not treated as check failures or repaired outside scope.

```text
AMENDED decisions:D-01.choice
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2274-omp-native-gate-policy/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2274-omp-native-gate-policy: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy.
  note       .harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2274-omp-native-gate-policy: run r-20261121-3-simplify-apply-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2274-omp-native-gate-policy (not gating).
AMENDED tasks:T-01.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2274-omp-native-gate-policy/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2274-omp-native-gate-policy: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy.
  note       .harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2274-omp-native-gate-policy: run r-20261121-3-simplify-apply-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2274-omp-native-gate-policy (not gating).
AMENDED tasks:T-03.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2274-omp-native-gate-policy/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-37 FEAT-2274-omp-native-gate-policy: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy.
  note       .harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2274-omp-native-gate-policy: run r-20261121-3-simplify-apply-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2274-omp-native-gate-policy (not gating).
```

## Authorized check — full output

Invoked exactly once after draft edits:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy
OK T-01 19 anchor(s) resolved
OK T-02 5 anchor(s) resolved
OK T-03 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/.harness/harness/features/FEAT-2274-omp-native-gate-policy/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy: 3 task(s), 27 anchor(s) resolved, 0 failure(s)
CHECK_EXIT=0
```

Changed draft paths: feature BRIEF.md (SC-02/SC-04) and plan.yaml (D-01.choice, T-01.intent, T-03.intent). This note is the required receipt. No production or test file changed.
