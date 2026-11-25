# BRIEF — FEAT-2537-registry-record-cleanup Enforcement-layer registry record cleanup

## Problem

The enforcement layer carries records that misdescribe what it does. `live_children` in `.claude/skills/harness/bin/inflight_registry.py` selects children by dispatcher persona and expires claims on disk, but nothing in production calls it: the held-child refusal is `_held_children` in `validate-digest.py`, a strict exact-parent `live_claims(root, None, parent_agent_id=...)` read. The registry still migrates a version-1 persona-keyed file that no writer produces; the census on 2026-11-25 found four registries, all empty v2 and none v1. Two comments in `.omp/extensions/harness-hooks.ts` are false or incomplete. DEC-199, DEC-204 and DEC-218 still describe the dead function and the migration. Spike F found the cost: auditors reading these records reported a "second lifecycle engine", and the false EventBus comment nearly licensed deleting the release paths that keep ordering. Source: issue #2537, ruled in `.harness/notes/grilling-registry-cleanup-f-2026-11-25.md`, with facts in `.harness/notes/facts-registry-cleanup-f-2026-11-25.md`.

## Done when — by perspective

**operator** — When I audit the ledger, it describes only the registry APIs and promises that exist. A registry file in the extinct v1 shape is refused as unreadable and never read as "no claims". Every registry state that today's writers can produce behaves exactly as before.

**code maintainer** — No code path can select children by dispatcher persona. The registry tests exercise the production call shapes. The hook comments describe what the hooks and omp's bus actually do. The frozen prior-revision evidence is left exactly as it was.

## Success criteria

- SC-01 (code maintainer): At the review_sha, `git grep live_children` over `.claude/skills/harness/bin` and `.omp/extensions` finds no match (exit 1, not an error exit), and a positive control `git grep parent_agent_id=agent_id` over `validate-digest.py` matches. In `tests/integration/test-inflight-registry.py`, cases 2b and 2c are gone. Case 25 binds lineage with `attach_runtime_identity` and asserts through `live_claims(root, None, parent_agent_id=...)` that a live child is returned and a stranded child is not. Case 29 asserts its no-runtime claim through `live_claim`. The whole file passes. qa first shows the `live_children` absence check red on the base tree, then shows rewritten case 25 red under a mutant that keeps a stranded claim live.
  verify: automated        evidence: integration
- SC-02 (operator): **The registry read-behaviour class holds.**
  - **Writer-producible states.** Each state gets its own assertion: missing file, empty file, corrupt JSON, non-object JSON, and valid v2 holding a live claim. For each, the strict reader `live_claims` and the locked writer `live_claim` give the same result on the candidate module as on the base module: return value, raise or no raise, and the file bytes after the call.
  - **The v1 shape.** This covers a persona-keyed map holding a claim, and also the empty object `{}`. `live_claims` raises `UnreadableRegistry`. `live_claim` returns no claim, writes a warning to stderr, and leaves `{"schema_version": 2, "claims": []}` on disk.
  - **Case 18 is the witness** and asserts both directions. qa runs the suite with the base module swapped in through `INFLIGHT_REGISTRY_DIR`: case 18's v1 assertions are red and the writer-producible assertions are green. Against the candidate module, all are green.
  verify: automated        evidence: integration
- SC-03 (operator): **The ledger no longer names the retired API or promise** in `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, read with whitespace and backticks normalised.
  - **DEC-199** no longer says `live_children` "is a read that only expires dead claims". In place, it names the exact-parent strict `live_claims` read.
  - **DEC-204** no longer says the persona-keyed object "is read once for migration". In place, it states that the registry is v2-only and fails closed for v1.
  - **DEC-218** no longer lists `live_children` among "single-flight admission, ... and reconciliation counts". In place, it names the held-child read.
  - **No amendment paragraphs** are added (DEC-205). `DECISIONS-INDEX.md` equals `gen-decisions-index.py --stdout` at that sha.
  - **Ordering.** No branch commit changes `inflight_registry.py` while `DECISIONS.md` at that commit still holds an old clause.
  - **Immutable records.** `tests/integration/fixtures/prior-validate-digest.py.fixture` and `tests/integration/test-validate-digest.py` are byte-identical between the merge-base and the review_sha.
  verify: inspection
- SC-04 (code maintainer): Both hook comments state verified behaviour at the review_sha.
  - **The comment above `pi.on("agent_start"`** says that a held first run (`runGate.state` "held") is also re-opened there, as the intended ordinary run-start retry.
  - **The comment above `pi.events.on("task:subagent:lifecycle"`** says the bus reports a listener's failure but does not await it. It names the awaited `tool_result` release and the yield-side settle as the ordering barriers.
  - **Comment-only diff.** Every `+` or `-` line of `git diff <merge-base> <review_sha> -- .omp/extensions/harness-hooks.ts` is a `//` comment line, so code tokens do not change.
  verify: inspection

## Verification gaps

- **No gap for SC-01 or SC-02.** Unit and integration have active runners in `.harness/harness.json` `test_kinds`, and `tests/integration/**` detects the edited suite. Unit runs as a regression floor; no unit file changes.
- **typecheck** (`bun run typecheck`, active) covers the `harness-hooks.ts` edit. Because the edit is comment-only, typecheck proves nothing about whether the comments are true. SC-04 carries that by inspection.
- **No test grades prose truth (SC-03, SC-04).**
  - SC-03 rests on a reviewer reading the pinned `DECISIONS.md`.
  - SC-04's EventBus claim rests on the Spike F read of omp 19.1.1 `utils/event-bus.ts` (`.harness/notes/answers-spike-f-2026-11-24.md`). No test re-runs that read.
- **omp_session_accessor** (`locally_run`) is not owed. Its runner_note binds changes to `inflight_registry.py`'s session-file resolution, and this patch leaves that untouched.

## Constraints

- **The behaviour class replaces the ticket's "zero behaviour change".** Nothing changes for any state current writers can produce: missing, empty, corrupt, non-object and v2. Every non-v2 object fails closed, including the extinct v1 map and `{}`. Today `{}` reads as an empty claim set; after this patch a strict reader refuses it. Any further behaviour change found during the build stops for a ruling.
- **Case 18 must assert both directions:** the strict reader raises, and the writer folds the file to empty. Asserting only one re-opens the "cannot read" = "no claims" hole that DEC-218 closed.
- **The ledger lands first.** DEC-199, DEC-204 and DEC-218 are rewritten in place before the code edits, inside T-01. DEC-205 BLOCKS adding amendment paragraphs and requires current-truth text. DEC-188 SUPPLIES "amend softer changes".
- **DEC-174 BLOCKS team execution.** `inflight_registry.py`, `harness-hooks.ts` and their tests are enforcement-layer files, so T-01 is main-session-direct inside this feature worktree. This overrides patch-lane.md's default. DEC-225 SUPPLIES the patch lane: this BRIEF, a one-task plan, no panel and no goal-check.
- **DEC-218 SUPPLIES the fail-closed rule** that unreadable means incomplete, and the writers' "treat-as-empty recovery". DEC-233 SUPPLIES expire-on-query for claims without a runtime.
- **Immutable records.** `tests/integration/fixtures/prior-validate-digest.py.fixture` is the frozen SC-20 clause-4 evidence, and the "neutering live_children" comment in `tests/integration/test-validate-digest.py` is an MF-2 record. Neither is in T-01's `files:`, and any diff touching either is a stop-and-rule event. The ticket's fixture edit is struck.
- **Symbols stay named.** `_parse` and `_read_strict` are not renamed, so `tests/integration/canonical-reader-classification.json` stays unchanged.
- **Rework ruling proposed to the signer: 1 round, 45 minutes.** A surprise, such as hidden coupling or an unexpected suite failure, triggers stop-and-rule rather than a second round.
- **Product guidance.** `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent. AGENTS.md names `.harness/harness/docs/SPEC.md` and `DECISIONS.md` as authority, and SPEC.md has no registry section.

## Out of scope

- **Everything issue #2537 already excludes.** The settled scope stays as ruled.
- **Fixture or `test-validate-digest.py` edits.** They are immutable prior-revision and panel records (grilling Q2a).
- **Removing `LEGACY_FEATURE`.** It also serves featureless claims, in case 28 and in `_held_children`, not only v1 (grilling Q3).
- **Renaming `_parse` or `_read_strict`, or changing the canonical-reader-classification inventory.** Keeping the names keeps the inventory a no-op (grilling Q2d).
- **Fixing the wake-turn refusal race, or centralising release behind the lifecycle listener.** Both are backlog rows from Spike F, and both would change behaviour on the hot path.

## Approval

status: pending
approved-by:
date:
