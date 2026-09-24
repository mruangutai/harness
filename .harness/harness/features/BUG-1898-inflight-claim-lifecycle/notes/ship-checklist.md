# BUG-1898 ship checklist: merge gate, cutover, and follow-up

**BLUF.** The operator runs this in order.

1. Record a live probe PASS before merge.
2. Do the one-time cutover after merge and before any OMP session loads the changed hook.
3. On the first real feature after merge, record its claim evidence. That record is follow-up
   evidence only; it is not a merge or ship gate.

This implementation clears **no** existing row, and that includes FEAT-65's current live and
leaked rows. Every release in step 2 is one the operator makes on exact evidence.

## 1. Before merge

- [ ] Run the live probe from this feature's worktree. The receipt must show **PASS**, appended
      to `notes/live-omp-probe.md` (SC-07). A dry run is not a receipt.

      ```sh
      cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle
      python3 tests/manual/probe-inflight-claim-lifecycle.py
      ```

- [ ] Rebase onto `origin/main` if it moved, then re-run the task verifies.
- [ ] The merge is the operator's.

## 2. Cutover, once: after merge, before any live session loads the changed hook

Rows written before this change can block the new run-start step:

- a pre-bound dispatch name;
- a receipt no child ever bound;
- the claim of an agent that settled but was never released.

For example, a leaked `harness-pm` row refuses every later PM for its feature: the refusal is
retryable, but nothing ever settles that row. Clear such rows by hand, one at a time, only on
exact evidence.

### 2a. Enumerate every registry, read-only

Read each registry's raw JSON directly. Do not use `inflight_registry.py list` for this step: it
reads through the registry's liveness query rather than showing the file as it stands.

```sh
cd /Users/molchairuangutai/GitHub/harness
git worktree list --porcelain | sed -n 's/^worktree //p' | while read -r checkout; do
  registry="$checkout/.harness/.inflight-claims.json"
  [ -f "$registry" ] || continue
  echo "== $registry"
  jq -c '.claims[] | {claim_id, feature, agent, agent_id, parent_agent_id, dispatcher,
                      supervisor_pid, supervisor_started_at, started_at}' "$registry"
done
```

Save this output. It is the "before" enumeration.

### 2b. Classify each row from exact runtime evidence

A row is **known-dead** only when one of these holds:

- **Dead supervisor.** `ps -o lstart= -p <supervisor_pid>` prints nothing, or the PID was
  reused: its start time in epoch seconds differs from the row's `supervisor_started_at`. On
  macOS, get that start time with:
  `date -j -f "%a %b %d %T %Y" "$(ps -o lstart= -p <supervisor_pid>)" +%s`
- **Settled run.** The row's `agent_id` names a run whose OMP session shows it settled, for
  example in `hub jobs` or its `history://<agent_id>` transcript, and that run has not been
  woken since.
- **Orphaned receipt.** The row has no `agent_id` (an unbound receipt), and the task call that
  dispatched it has returned. In that call's session, the task result or tool call shows no child
  of this persona still running under that parent.

A row is **live** when its supervisor is alive and its run is still working. It is
**ambiguous** when the evidence is incomplete or points both ways. Leave live and ambiguous rows
alone. Write down the evidence for every row you classify as known-dead.

### 2c. Release each known-dead row, individually

Run one command per row, naming the row's feature and its `claim_id`, or its exact `agent_id`
when the row has one. Pass `--root` as the checkout whose registry holds the row.

```sh
python3 .agents/skills/harness/bin/inflight_registry.py release \
  --feature <feature> --claim-id <claim_id> --root <checkout>
```

**Forbidden in this cutover:**

- any automatic or scripted bulk cleanup;
- `release-all`;
- a persona-only selector (`--agent <persona>`);
- `reconcile` as a substitute for evidence;
- any action on a live or ambiguous row.

If a `release` refuses because more than one row matches, stop: that row is ambiguous.

### 2d. Enumerate every registry again

Re-run 2a and compare it with the saved "before" output. The only rows gone should be exactly the
ones released in 2c, and every remaining row should be one you classified as live or ambiguous.
Record both enumerations and the per-row evidence in this feature's notes.

### What this cutover does not touch

The implementation clears nothing on its own, including FEAT-65's current live or leaked rows. A
FEAT-65 row is released in 2c only if its own evidence makes it known-dead. Otherwise it stays
for FEAT-65's owner.

## 3. After merge: the first real feature

- [ ] The first real feature planned, built and validated after merge must record, in **its own**
      notes:
  - each governed run's claim at run start, bound to its exact runtime id;
  - its settlement release;
  - an empty registry for that feature at the end.

This is follow-up evidence of the end-to-end cycle. It is **not** a merge gate or a ship gate for
BUG-1898, and a gap found there becomes its own issue.

## Out of scope for this feature

- #1919: Main's eval `agent()` spawns of governed personas skip dispatch-guard.
- #1882, linked as related only.
- Any mechanical retry limit on held runs.
- Any automatic stale-claim cleanup.
