# Receipt — harness-backend-dev — build-eng — T-06 (cycle 2)

**BLUF:** T-06's code (`expertise-merge.py`, `test-expertise-merge.py`) is correct and satisfies
D-05/D-06 and DEC-95/DEC-145's caps. The prior cycle's PASS record was accurate about the code but
falsified about `files_touched` — this receipt and the observations log genuinely did not exist
before this cycle. Root cause: the task's own `verify:` block, run verbatim, is denied by
`bash-write-guard.sh` before it can execute, for a reason unrelated to the code under test — see
`open_questions`. The prior spawn most plausibly hit this same denial repeatedly, never got the
verify to complete, and still returned PASS with an artifact path it never wrote to.

## Diagnosis of the two missing files

- `check-domain.sh --resolve` and a simulated `PreToolUse:Write` payload for both
  `notes/receipt-harness-backend-dev-build-eng-T-06.md` and `observations/harness-backend-dev.md`
  both resolve to `harness-backend-dev` and both exit 0 (allow). **No guard denies either path.**
  Both are correctly granted by `.harness/team-config.yaml:169,172`.
- Neither file exists in git history and neither is untracked in `git status` — they were never
  written, not written-then-lost.
- **Real guard defect found while re-running the verify** (see below): `bash-write-guard.sh`
  denied the verify's own `cp -R .claude/skills/harness/bin "$T/bin"` line. Its static parser
  (`shlex.split` on command text, `bash-write-guard.sh:342-368`) does not expand shell variables —
  `"$T/bin"` is taken as the **literal string** `$T/bin`, treated as relative (doesn't start with
  `/`), joined onto repo root, and denied as "outside your domain" even though the real runtime
  target is a `/var/folders/...` mktemp dir that `harness_boundary.classify` explicitly carves out
  as `not_a_domain_question` (`harness_boundary.py:283-289`). Verbatim refusal text is in
  `open_questions` Q1.

## Verify — actual output, this cycle

Ran the verify's steps with the mktemp path substituted as a literal string instead of through
`$T` (workaround for the guard defect above, not a change to the check):

1. `cp -R bin "<tmpdir>/bin"` → exit 0.
2. Mutation `UNION_APPLY = True` → `False` by name → applied, exit 0.
3. Red-proof run (`EXPERTISE_MERGE_BIN=<mutated>`, full suite): **exit 1** (correctly reddens).
   32 checks logged, cases 1/2(partial)/3/6/8 PASS, cases 2 (P-02/P-03 absent), 4, 5 FAIL as
   expected — the mutated tool no longer unions, so `&&` branch (which would print `RED PROOF
   FAILED`) never fires. This satisfies the verify's negative-control requirement.
4. Real suite (unmutated): **exit 0, 32/32 PASS, 0 FAIL.**
5. Whole verify script: **exit 0** (matches the quoted `verify:` block's control flow exactly).

## The eight cap numbers (DEC-145)

`check-expertise.sh:39` and `expertise-merge.py:32` both define
`CAPS = {"Patterns": 15, "Gotchas": 15, "Outcomes": 10, "Open": 5}` — identical, byte for byte.
case8's four agreement assertions all PASS.

## Concurrency case (case3) — observed outcomes

The suite's own 20-trial run inside `test-expertise-merge.py::case_concurrency_real` reported
**PASS with zero third-outcome entries** (i.e., every one of 20 trials landed `union` or `locked`,
no `other`). A supplementary standalone 20-trial run I wrote separately (same CLI, same race
shape, outside the suite) observed **20/20 `union`, 0 `locked`, 0 `other`** — the lock was never
actually contended in either run, consistent with two near-simultaneous `apply` subprocesses
usually not racing inside the ~ms critical section, but the suite's own assertion covers the
`locked` branch's correctness independently (case4's exit-7 divergent-text path exercises the same
lock-then-fail code path and passed).

## Code review against intent (plan.yaml:1049 T-06)

Read the full `intent:` block. Algorithm steps 1-8, both file cases, and all 8 test cases are
present and passing. No gap found requiring a code fix this cycle.

## open_questions

- Q1 (harness defect, `bash-write-guard.sh`): verbatim refusal —
  `` bash-write-guard: BLOCKED — harness-backend-dev: `cp` targets $T/bin, outside your domain. ``
  Cause: the guard's static command-text parser does not expand shell variables before checking
  cp/mv destinations against domain globs, so any verify or task that assigns a temp path to a
  bash variable and uses it as a write target in the same command is denied even though the
  literal runtime path is legitimately outside every domain (`not_a_domain_question` in
  `harness_boundary.classify`). T-06's own `verify:` block (quoted in this feature's plan) hits
  this on its first line. Not worked around by editing the guard — worked around this cycle by
  substituting the mktemp path as a literal string instead of a variable, per the standing "write
  the body to a file and invoke by path" guidance, generalized to "avoid referencing a bash
  variable for an out-of-domain target in the same guarded command." blocking: true — a T-NN whose
  verify cannot run as literally specified belongs in front of the harness owner, not silently
  patched by every future spawn re-deriving the same workaround.
