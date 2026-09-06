# Plan-panel review — BUG-1305, cycle 1 (reader B) — spec-compliance / scope read

**BLUF: structurally sound (REQ↔task↔SC tracing is complete, the dependency graph forces the order
the prose claims, and the disclosed marker+checkpoint-match residual is honestly placed) but two
`high` gaps ship green: T-09's acquisition denial can refuse the true owner recovering its own lost
checkpoint, and T-10's one-shot backfill does not survive the corpus growth the plan's own
measurement admits is continuous. Neither is covered by SC-01, SC-07's four enumerated pairs, or
SC-09. `code_grade: n_a` — no code exists to grade.**

This is an independent read; nothing in cycle-1/cycle-2 goal-check history binds it. Traceability
audit (REQ-01..08 × T-01..T-10 × SC-01..09) is clean: every REQ has ≥1 tracing task, every task
traces a live REQ, every SC has exactly one producing task, no orphan or dangling reference found.
`depends_on` is acyclic and matches the ordering claims in T-02's/T-10's intent bodies and the
DEC-171 BRIEF paragraph verbatim (T-10 depends on T-03; T-08 depends on `[T-02,T-03,T-05,T-06,T-09,
T-10]` exactly as T-02's intent quotes it). T-10's `files:` correctly declares the `check-state.sh`
region it supersedes from T-03, so that specific dispatch concern is clean.

## Findings

### F-01 · high · T-09's acquisition refusal blocks the true owner recreating its own lost checkpoint — REQ-01's "never refused" claim is narrower than stated

T-09 denies whenever `marker is not None AND prior_unreadable is False AND prior_state == ""`
(plan.yaml T-09 §"THE REFUSAL CONDITION"). Per `check-domain.sh:1508-1518` at `c369fb1f` (read at
that sha), `prior_state == ""` is produced by **two** code paths, not one: the `FileNotFoundError`
branch where `os.path.lexists` is false (genuinely no file), **and** the ordinary `open().read()`
path when the file exists but is zero bytes. T-09's own text asserts the opposite — "That local is
already computed…: it is set to "" only in the FileNotFoundError branch" — which is measurably false
against the cited lines, and that inaccurate claim is what a later engineer is instructed to write
into the shipped code comment.

Failure scenario: a run's own `state.yaml` is lost after the marker was recorded — truncated by a
crash, zeroed by an interrupted external write, or removed by an operator mid hand-repair (exactly
the recovery action B-11 needed) — while the marker persists (write-once, never deleted). The same
owning run then writes a fresh checkpoint carrying its own `run_id`/`feature`/`squad`/`host`. T-02's
`conflict()` passes (fields agree with the marker). T-09 now fires: marker present, prior readable,
`prior_state == ""` → refused, with the message telling the owner to "allocate a directory of its
own." BRIEF's REQ-01 states unconditionally "A resumed run is never refused, and that is a
requirement, not a side effect" — true only when the prior checkpoint file is still present; the
plan never states that boundary condition where the operator reads residuals (BRIEF's own "THE
RESIDUAL" bullet), only inside T-09's task-body comment instructions ("neither is separable from the
other on disk"), where it is framed as an unavoidable ambiguity rather than surfaced as a second,
distinct residual alongside the disclosed marker+checkpoint-match one.

Not caught by any criterion: SC-01(c)'s resumed-owner case and SC-07 direction two's four enumerated
pairs (`## Newly refused writes`) all assume the prior state.yaml is **intact**; none exercises "prior
present-but-empty" or "prior deleted between writes." REQ-07 direction two ("no legitimate write
newly refused") is unfalsifiable against exactly this case because no pair names it.

### F-02 · high · T-10's backfill-then-enable is a one-shot snapshot; the corpus it measures is proven to grow continuously, and nothing re-seeds before the invariant is exercised in production

T-10's own intent states the corpus "GROWS while this feature is planned and built (it was 575
earlier the same day)" and that this is why the remedy must be "an idempotent script re-run at
execution time." But the task only *runs* the seeder once, inside this feature's own build (in the
`BUG-1305` worktree), then enables the `check-state.sh` invariant in the same commit sequence.
`check-state.sh` resolves a single root via `harness_boundary.resolve_root` and sweeps only
`<that root>/.harness/*/features/*/runs/*/state.yaml` (`check-state.sh:67,1426` at `c369fb1f` —
confirmed by reading the source; no worktree traversal in the invariant loop itself). The seeder's
own two-glob description (`.harness/*/features/*/runs/*/` **and**
`.claude/worktrees/*/*/.harness/*/features/*/runs/*/`) shows the corpus it backfills spans the
control-plane root's tree *plus every nested worktree's own tree* — and the control-plane root's
`.harness` tree (356 of the 630) is exactly the tree this repository's own concurrently-running
harness activity writes into continuously (this session's own hub roster shows half a dozen
unrelated feature builds live right now, each writing run directories there under the *pre-fix*
`check-domain.sh`).

Failure scenario: between the moment T-10's seeder snapshots the corpus and the moment this feature
merges and `check-state.sh`'s new invariant is actually exercised against the control-plane root, any
concurrent feature build writes new, entirely legitimate run directories through the still-unmerged
`check-domain.sh`, which does not yet call `record_seed`. Those directories carry no marker. Once
merged, the invariant reports every one of them as "nothing prevents another run from writing into
it" — a wave of false positives on ship, for directories that are neither clobbered nor malformed,
undermining REQ-03's own "an operator reading only the checker's output knows what was lost" promise
on day one. Nothing in T-10 or T-08 re-runs the seeder at merge/deploy time, and SC-09 only requires
`remaining_unseeded: 0` as a **build-time** snapshot fact plus a synthetic fixture test — neither
checks the state of the control-plane root at the moment the invariant actually goes live.

### Notes, not gating

- `execution_mode: main-session-direct` is correctly justified for all ten tasks under the `lanes:`
  table and DEC-174/179; the retired T-04 carries a vestigial reason but does nothing, so it costs
  nothing.
- The disclosed marker+checkpoint-match residual (BRIEF "THE RESIDUAL", SC-01(c)) is placed correctly
  and is honest; it is a *different* case from F-01 above and remains correctly closed neither by
  prevention nor detection, as stated.
- Plan is specified concretely enough (exact line ranges, exact key sets, exact wording) for a human
  to execute unaided; no ambiguity found there.

## code_grade
n_a — plan-phase panel per DEC-207; no code exists to grade, `review_sha: none`.
