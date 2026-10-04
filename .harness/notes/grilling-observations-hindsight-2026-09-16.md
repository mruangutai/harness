# Grilling — observations retained in Hindsight for cross-feature recall — 2026-09-16

## Destination
Every observation an agent appends is also retained in a shared Hindsight bank, and at
distillation the agent recalls its own observations across all features and repos before
judging what enters Expertise. On-disk observation logs remain the committed, reviewed record.

## Mission
mission: plan
reason: new surface others read — a network dependency and exit code in observations-merge.py (the sole writer the domain hook and tests rely on), a committed project-level omp backend change, a metadata contract a later feature depends on, and preloaded skill text.
confirmed-by: operator

## Settled
- Destination → cross-feature recall at distillation; disk logs stay the record; not a replacement of the logs.
- Retain site → `observations-merge.py` dual-writes: after the locked union-merge succeeds it retains the ADDED records to Hindsight over HTTP (stdlib only, `HINDSIGHT_API_URL`/`HINDSIGHT_API_TOKEN` from env). No hook change, no reliance on agent obedience.
- Server unreachable → **fail-closed**: the append refuses with its own exit code; nothing lands on disk without landing in memory.
- Server → **local Docker on this Mac for now** (`http://localhost:8888`, the omp default). Fail-closed is coherent while every harness run happens on the machine hosting the server; if Docker is down, the first append refuses and names the cause — accepted. **Upgrade to an always-on self-hosted VPS (private, over Tailscale) is a prerequisite of running harness features from a second machine**, not of this feature. Nothing in the design changes at that point except `HINDSIGHT_API_URL`.
- Backfill → one-time idempotent script retains the existing observation corpus (~10.9k lines across `.harness/*/features/*/observations/`) with the same metadata as live retains; re-runnable on the second machine.
- omp backend → `memory.backend: hindsight` in the committed `.omp/config.yml`, so every harness session and subagent shares the bank and has `recall`/`retain`/`reflect`. Token lives in each machine's env, never in config.
- Recall mechanism at distillation → omp's `recall` tool, persona name in the query. No bin recall script.
- Metadata on each retained observation → `agent`, `feature` (FEAT/BUG id), `repo` (segment), `date`.
- Tiering → observations are stored **global** (no omp project tag); `repo` is metadata. Two recalls at distillation: cross-repo (craft-tier evidence) and one whose query names the repo segment (repository-tier evidence). The repo boundary is semantic bias, not a wall — the model has agency; the layer test in `harness-distill`, not recall scope, decides which Expertise file an entry lands in.
- Granularity → Hindsight is the permanent home of granular knowledge; Expertise stays the small curated set of working rules. Recipe-grade observations (library behaviour, config values) are not promoted; they stay recallable.
- Mid-run recall → permitted, not prescribed: one sentence in `harness-expertise` says recall is available when a task resembles past work. No procedure, no gate.
- `retain` tool → observations go only through `observations-merge.py`; the `retain` tool is not for observations. One sentence in `harness-expertise`. Not mechanically enforced.
- Ticket → open a feature issue in `mruangutai/harness` for this effort; a second wayfinding ticket for decisions tiering.
- Metadata contract is an explicit output of this feature: global storage, `repo=<segment>` metadata, persona tag. The decisions feature reuses it verbatim.

## Not yet specified
- Content shape of one retained memory: the bullet verbatim, or bullet plus the log's title context. Whether Hindsight's world-fact / experience-fact split is used or everything is retained as experience.
- Idempotency key for backfill and re-runs (normalised bullet text as the merge tool already keys on is the obvious candidate).
- The exact two query templates `harness-distill` step 1 prescribes, and how the distiller reports recall evidence in its DIGEST (per-source accept counts already exist for lead-relayed candidates).
- How the fail-closed refusal is tested without a live server (fixture HTTP server vs recorded responses), under the stdlib-only constraint.
- Whether `hindsight.autoRetain` of the primary session's turns should stay on for harness sessions or be off so the bank holds observations only.

## Out of scope
- Moving Expertise files, `plan.yaml`, BRIEF, STATE, feature.json, runs, or logs into Hindsight — anything a gate, test, or CI job reads stays on disk.
- **Decisions tiering (global + repo) and a Hindsight mirror of DECISIONS.md** — separate feature, sequenced after this one; depends on this feature's metadata contract. Facts for it: the authority already sits at the repo-segment path `.harness/harness/docs/DECISIONS.md`; no global tier exists; `plan.yaml` `decisions:` point at `DEC-NNN` or `dec: none`.
- Prescribed mid-run recall at task start (rejected for per-spawn cost; may be revisited after measuring what recall returns).
- A hard repo filter on recall (bin script with `--repo`); rejected in favour of model agency.
- Retiring the on-disk observation logs.

## Facts I verified (so pm does not re-derive them)
- Every reader of `observations/` in the skill tree is single-feature: `harness-distill` step 1, `harness/references/distillation.md`, `harness-curate` step 3, `harness/references/artifact-paths.md` ("never injected into any spawn") — grep of `.claude/skills`, `.omp/agents`, `.omp/commands` at `f5ffdcf4`.
- `observations-merge.py` is the sole writer of observation logs, stdlib-only by contract, exit codes 0/6/9 today, keys union on whitespace-normalised bullet text — file header at `f5ffdcf4`.
- Expertise volumes: craft files 19–48 lines against the 150 budget; repo-tier 7–32 against 40; 831 lines total across 29 files. Observations: ~10,927 lines across features — `wc -l` at `f5ffdcf4`.
- Expertise is injected once per agent per session by `harness-hooks.ts` `before_agent_start` → `inject-expertise.sh`, as a hidden `harness-expertise` message; `agent_end` handler exists in the same extension — `.omp/extensions/harness-hooks.ts:750-779,1065`.
- omp Hindsight backend: subagents alias the parent's client/bank/scope for explicit calls but run no auto recall/retain; `per-project-tagged` recall returns this project's tag plus untagged memories only, so cross-repo recall requires observations stored untagged; project name is the lowercased basename of the primary checkout root, so worktrees share one scope; failures are logged and non-fatal — `omp://memory.md` (Hindsight section) and `omp://environment-variables.md:485-503`.
- No existing open issue covers memory or Hindsight — `issue://mruangutai/harness?state=open&limit=40` on 2026-09-15.
- `github.sync: true`, repo `mruangutai/harness` — `.harness/harness.json:385-387`.
- DEC-23 (choice vs observation), DEC-65 (native memory rejected to preserve tool-grant limits), DEC-145 (record/distill split, 150-line cap as physics), DEC-205 (DECISIONS.md current truth, anchor rot) read at their index anchors; none contradicts this design, and DEC-65's reasoning is why `retain` is not made a write path for Expertise.
