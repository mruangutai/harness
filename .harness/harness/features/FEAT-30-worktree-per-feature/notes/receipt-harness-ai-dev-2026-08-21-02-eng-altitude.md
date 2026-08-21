# ALTITUDE angle — read-only — 49c528a..fbb3bc0

BLUF: one real finding earns action — three module-level safety switches
(`UNION_APPLY`, `REFUSE_ON_DIRTY`, `REQUIRE_LANDED`) are load-bearing but their only
red-proof is a one-time `plan.yaml` task `verify:`, never a persisted assertion in the
gate suite that runs on every future change to these files. Everything else audited at
this altitude — the two new modules' right to exist, the lock's adapter lifetime, one
docs restatement of the worktree path formula — is sound or negligible. `leave` on those.

## F-ALT-1 — the three mutation-proofs never entered the persisted suite

- **File/line**: `.claude/skills/harness/bin/expertise-merge.py:48` (`UNION_APPLY`),
  `.claude/skills/harness/bin/feature-worktree.py:28-29` (`REFUSE_ON_DIRTY`,
  `REQUIRE_LANDED`); the missing assertions belong in
  `.claude/skills/harness/bin/test-expertise-merge.py` and
  `.claude/skills/harness/bin/test-feature-worktree.py`.
- **Summary**: each constant's docstring claims "a test proves its own assertions are
  load-bearing by mutating this literal, by name" — true once, at build time, in
  `plan.yaml`'s task `verify:` (T-06 for `UNION_APPLY` at `plan.yaml:1032-1046`; T-02 for
  the other two, receipted in `receipt-harness-dev-ops-build-eng-T-02.md:36-38`). Grepped
  both checked-in test files for `UNION_APPLY`, `REFUSE_ON_DIRTY`, `REQUIRE_LANDED`: zero
  hits in either. Both files ARE in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` and run on
  every future gate — but neither contains the mutation that proved the switch matters.
- **Concrete cost**: a future edit that makes any of the three switches inert (e.g. a
  refactor of `compute_union` that no longer branches on `UNION_APPLY`, or a change to
  gate ordering that makes `REQUIRE_LANDED = False` behaviourally identical to `True`)
  passes every gate that exists today. The one proof that would have caught it ran once,
  by a human, and is not reachable again.
- **Alternative**: port the exact `plan.yaml` mutation (copy source dir, sed the literal
  by name, point `EXPERTISE_MERGE_BIN`/`FEATURE_WORKTREE_BIN` at the copy, assert the
  suite goes red) into the two test files as a permanent case. This is additive — no
  existing assertion is touched or weakened.
- **Apply marker**: `apply-candidate` (both test files are in the apply-permitted list).
- **Severity**: high.
- **Recommendation**: **briefing-row** — per dispatch instruction, a finding whose only
  remedy is adding a missing test case is not itself a simplify apply; it needs a task,
  not an edit from this pass.

## F-ALT-2 — deletion test on the two new modules

- **File/line**: `.claude/skills/harness/bin/feature-worktree.py` (whole file);
  `.claude/skills/harness/bin/expertise-merge.py` (whole file).
- **Summary**: imagining each deleted — `feature-worktree.py`'s `create`/`remove` are each
  called from exactly one place today (`.claude/commands/harness.md` step 0b and the
  worktree-lifecycle section of `harness/SKILL.md`), but that one call site is the main
  session's own governed boundary for every feature run across every served repo — delete
  the module and the branch/lock/gate logic (flow-id validation, dirty-tree refusal, landed
  artifact verification against the default branch) has to reappear inline in a markdown
  procedure, unverifiable. `expertise-merge.py` is called from `harness-distill/SKILL.md`,
  reached by five engineer personas plus the documentor at every distillation — deleting it
  reopens the exact DEC-95 last-writer-wins loss the tool exists to close.
- **Concrete cost**: none — both earn their keep.
- **Alternative**: none needed.
- **Apply marker**: apply-candidate (n/a — no change proposed).
- **Severity**: info.
- **Recommendation**: **leave**.

## F-ALT-3 — lock adapter lifetime in `expertise-merge.py`

- **File/line**: `.claude/skills/harness/bin/expertise-merge.py:159-247` (`cmd_apply`).
- **Summary**: `acquire_lock` runs before the `try:`; every exit from the body — normal
  return, every `sys.exit(N)`, and the unhandled-exception path — is inside the
  `try/finally`, so `os.remove(lock_path)` fires on all of them. The one narrow gap is
  between `acquire_lock`'s `os.open`/`os.close` succeeding and the `try:` line executing —
  a process kill in that window leaves a stale lock file, but that is true of any
  create-then-guard lock and is bounded to a single Python statement.
- **Concrete cost**: negligible — the gap is one line wide and requires a kill signal at
  that exact instant.
- **Alternative**: none warranted; a broader `try:` starting before `acquire_lock` would
  have to swallow the "could not acquire" exit path too, which is a worse shape.
- **Apply marker**: apply-candidate (n/a — no change proposed).
- **Severity**: info.
- **Recommendation**: **leave**.

## F-ALT-4 — worktree path formula restated in a flag-only doc

- **File/line**: `.claude/commands/harness.md` step "0b" (new), stating the concrete
  example `harness_root/.claude/worktrees/harness/<id>`, versus the one authoritative
  computation in `.claude/skills/harness/bin/feature-worktree.py`'s `dest_for()` (reads
  `harness_boundary.WORKTREES_SEGMENT` by name, never re-spelled as a literal).
- **Summary**: the actual segment string and join order live in exactly one place
  (`harness_boundary.WORKTREES_SEGMENT`); `harness.md`'s worked example is prose that
  would go stale silently if the layout ever changed, since nothing checks a doc's example
  string against the code.
- **Concrete cost**: low — a human reading a stale example gets confused; no runtime
  behaviour depends on the doc text.
- **Alternative**: state the rule ("owner_root / WORKTREES_SEGMENT / repo-segment / id")
  without a fully concrete worked path, or accept the drift risk as cosmetic.
- **Apply marker**: `flag-only/nobody` (`.claude/commands/harness.md`).
- **Severity**: low.
- **Recommendation**: **leave** — cosmetic, and `harness.md` is outside this pass's write
  access regardless.

## Note, not a new finding

`harness_boundary.py`'s `checkout_relative`/`linked_worktrees` (flag-only/DEC-174)
consolidate what were four independent, segment-counting re-derivations of "which
checkout is this path in" (`classify()`, `check-domain.sh`'s resolver, its sweep globs,
its `_norm()`) into one function each. This is the ALTITUDE question answered correctly
in the other direction — already reflected in settled F-6 and A-2; not re-scored here.
