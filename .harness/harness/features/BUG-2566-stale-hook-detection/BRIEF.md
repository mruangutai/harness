# BRIEF — BUG-2566-stale-hook-detection Refuse governed calls when the loaded Harness hook code no longer matches disk

## Problem

OMP loads `.omp/extensions/*.ts` once, when the process starts. A long-running session therefore
keeps enforcing whatever hook code and schema location it loaded, even after the checkout moves
under it, and it gives no sign that anything is wrong. This has been observed in practice. Session
`01a1ffe9` refused exact copies of its own injected schema after fd636495 reached the main
checkout. Sessions `01a1b652` and `01a204bb` failed with "digest schema directory …
bin/digest-schemas cannot be resolved (ENOENT)" after b788e9da moved the schemas. In both cases
the first symptom was a misleading refusal, never "restart omp". The operator lost the round trips
and then had to diagnose a process-age problem from transcripts and `git reflog` (issue #2566;
grilling `.harness/notes/grilling-stale-hook-detection-2026-11-27.md`).

## Done when — by perspective

**operator** — A running omp session never enforces Harness rules from hook code that no longer
matches the checkout it was loaded from. Every governed call is refused with one line telling me to
restart omp, except that a governed child may still yield a BLOCKED digest, so in-flight work can
say why it stopped; that yield still faces normal yield validation. My own reads, edits and
ordinary shell in the main session keep working, so I can
always recover. The record tells me which sessions cannot detect this.

**orchestrator** — My governed calls are refused only when the loaded code really differs from
disk, never because a timestamp was touched, a digest schema or agent definition was regenerated,
or another checkout changed. The check does not noticeably slow the calls I make.

**code maintainer** — What is fingerprinted is stated in one place in the hook module and derived
from where the module was loaded. The existing hook suite and the typecheck still pass.

## Success criteria

- SC-01 (operator): Take a copy of `.omp/extensions/` imported from a temporary root. Right after
  import, the copy's exported `staleHookRefusal()` returns `undefined`. It returns a reason naming
  `.omp/extensions/harness-hooks.ts`, relative to that root, after each of these changes alone,
  each case on a fresh copy: its bytes changed; its bytes changed at the same size with its
  load-time mtime restored, so an unchanged-stat shortcut cannot pass; the file deleted; the file
  replaced by a FIFO, where the call returns without waiting on it. The FIFO case runs in a
  separate, killable process with a deadline and must return normally with the reason, so a
  regression fails instead of hanging the suite. In every case the reason contains no newline and
  contains `restart omp`. qa shows the cases failing against the pre-change hook first.
  verify: automated        evidence: unit
- SC-02 (operator): `registerHarnessHooks` is driven with a stale check that returns a reason. Each
  of these calls is blocked with that reason, and the policy runner is never called for it: a
  persona session's `read`, `write`, `edit`, `bash`, `task`, a `yield` of a well-formed object with
  `VERDICT: PASS`, a `yield` of that object's JSON text, a `yield` of malformed text, a `yield`
  whose data is not an object, and a data-less finalize (`{type: "result"}` with no `data`); a
  persona session whose run is held (stale outranks held); Main's `task`; Main's `bash` running
  `echo merge` (any command matching `mainMergeGate`'s `\bmerge\b` prefilter). Main is initialized
  through its unmarked `before_agent_start` fixture. A persona's refusal is the reason followed by
  one space and the sentence "While this process is stale, you may yield only a BLOCKED digest
  that names this cause."; Main's is exactly the reason. The carve-out is
  exactly as narrow as the held-run gate's: a persona's `yield` with `VERDICT: BLOCKED`, in each of
  the four combinations of object or JSON text and ready or held run, is not refused by the stale
  check and reaches `validate-digest.py --hook` exactly once, with the decoded object as its
  `digest_object`. Each call is its own assertion. qa shows the refused calls failing against the
  pre-change hook first; the carve-out calls already reach validation there and are recorded as
  preserved.
  verify: automated        evidence: unit
- SC-03 (operator): The same stale check leaves Main's non-governed calls alone. Main's `read`,
  `edit`, `write` and `bash` running `git status` each return no block. Each is its own assertion.
  verify: automated        evidence: unit
- SC-04 (orchestrator): On a copied tree that also holds a real copy of `schemas/digest` under its
  `.agents/skills/harness/`, `staleHookRefusal()` stays `undefined` after each of these: the hook
  module's mtime touched with its bytes unchanged; the module rewritten with identical bytes; the
  module changed and then restored to its original bytes; a schema file's bytes changed; a schema
  file removed; a new `digest-schema.ts` created in `.omp/extensions/`, which the process never
  loaded. Edits to a second copied tree B leave tree A's `staleHookRefusal()` `undefined`, which is
  the main-checkout-versus-worktree case. qa shows the touch and restore cases, and SC-01's
  same-size fixed-mtime case, failing against a mutant of the implemented detector that records
  each file's mtime instead of its content hash. Only the hook module's timestamp cases set a
  controlled mtime, at least one second away from the load-time one; the schema and new
  `digest-schema.ts` cases are plain writes. SC-01's cases already fail a mutant whose root comes from `process.cwd()`, because
  the test's cwd is never the temporary root.
  verify: automated        evidence: unit
- SC-05 (orchestrator): The real module's `staleHookRefusal()` runs over this repository's tree 200
  times after 20 warm-up calls, with a median under 5 ms. The measured baseline at e12381fd was
  0.35 ms over a larger set than the one now fingerprinted; one gate process spawn costs 14 ms
  (`notes/research-stale-hook-detection.md`).
  verify: automated        evidence: unit
- SC-06 (code maintainer): Read at `git show <review_sha>:.omp/extensions/harness-hooks.ts`. The
  fingerprinted set is built only from `import.meta.url`: it is exactly the loaded hook module,
  listed in one module-level array, and no environment variable, cwd, ctx or tool input feeds it.
  Neither the digest schema directory nor `digest-schema.ts` nor `.omp/agents` is in it. The
  fingerprint and the check use only `node:fs` and `node:crypto`, with no process spawn. A path
  that is not a regular file is recorded by its kind without being opened, and a regular file is
  read only through the one nonblocking descriptor whose `fstat` confirms it is a regular file, so a
  FIFO swapped in after the kind check cannot block. The baseline is a
  module-level constant. Of the new code only `staleHookRefusal` is exported; the fingerprint type,
  builder, reason formatter and BLOCKED-yield predicate are module-private. The stale check is the
  first refusal in the `tool_call` handler, it skips only a persona's `yield` whose data decodes to
  an object with `VERDICT` exactly `BLOCKED`, and its merge test is the one regular expression
  `mainMergeGate` also uses. No identifier deleted by BUG-2565 (`DIGEST_SCHEMA_DIR`,
  `loadDigestSchemaBundle`) is used by the new code. `git ls-tree --name-only <review_sha>
  .omp/extensions/` lists no module beyond `harness-hooks.ts`.
  verify: inspection
- SC-07 (code maintainer): At the pin, `tests/unit/test-omp-hooks.py` passes, so the whole of
  `tests/unit/omp-hooks.test.ts`, existing cases included, is green.
  verify: automated        evidence: unit
- SC-08 (code maintainer): At the pin, `bun run typecheck` exits 0.
  verify: automated        evidence: typecheck
- SC-09 (operator): `git show <review_sha>:.harness/harness/docs/SPEC.md` §4.2 states all of the
  following:
  - what is fingerprinted (the loaded hook module), that it is resolved from the checkout the
    extension was loaded from, and why the digest schema directory and agent definitions are not;
  - that the comparison is by content;
  - that every governed call is refused (persona calls, Main's `task`, Main's merge Bash), with
    the restart-omp remedy, except a persona's yield of a BLOCKED digest;
  - that Main's other calls are unaffected;
  - that the baseline is taken at module load, so a session started before this shipped cannot
    detect staleness and must be restarted once.
  verify: inspection
- SC-10 (operator): After T-01 lands, I start omp with its cwd in this feature's worktree and add
  one comment line to that worktree's `.omp/extensions/harness-hooks.ts`. My next `task` dispatch is
  refused with one line telling me to restart omp, while my read and edit calls still work. After a
  restart, the same dispatch proceeds.
  verify: uat

## Verification gaps

- No test kind runs a live omp process. Three things rest on the OMP 19.2.1 docs and on SC-10,
  which the operator runs: that OMP imports the extension once per process, so the module-load
  baseline is the loaded code; that a blocked `tool_call` reason reaches the user verbatim; and
  that OMP rediscovers agent definitions on every task spawn (`task-agent-discovery.md`, checked by
  the main session), which is why `.omp/agents` is not fingerprinted. That an omp session started in
  a worktree loads that worktree's extension is [INFERENCE], also carried by SC-10.
- SC-05 bounds the cost on the test host. It is not a production latency measurement.
- typecheck is active and covers the touched `.ts` files (SC-08). component and ui have null
  runners, and their detect globs match no file this feature touches. functional and eval are
  excluded under DEC-187 and carry no SC.

## Constraints

- DEC-174 BLOCKS team execution. Every task is `execution_mode: main-session-direct`, because the
  change is to the hook that would enforce its own build. DEC-179 SUPPLIES declaring each surface
  before signature.
- Ordering, settled by the operator and recorded as plan decision D-04 for signature:
  BUG-2565-digest-frontmatter-contract lands first and the builds are sequential, because both
  edit `.omp/extensions/harness-hooks.ts`. 2565 deletes `DIGEST_SCHEMA_DIR`, the per-call schema
  injection and `.omp/extensions/digest-schema.ts`, so this plan anchors only on
  `registerHarnessHooks`, which 2565 keeps. T-01 does not build on a base where
  `.omp/extensions/digest-schema.ts` still exists or where a text grep for the known legacy import
  spelling (`from "./digest-schema`) finds a match in the hook; that grep is not import-aware, so
  the file's absence carries the condition. It stops there and reports BLOCKED. This plan makes no
  claim to build in the reverse order.
- The fingerprinted set was re-decided by the operator at the 2026-11-27 signature questions,
  overriding the grilling's settled set: only the hook module(s) the omp process actually loads,
  which after 2565 is `harness-hooks.ts` alone (plan D-03). The digest schema directory and
  `digest-schema.ts` are dropped, because the post-2565 hook reads neither; `.omp/agents` is not
  added, because OMP rediscovers agent definitions on every task spawn. `harness.json`,
  `team-config.yaml` and the Python gate scripts are not in it either.
- The fingerprint code lives inside `harness-hooks.ts`. OMP loads every module in
  `.omp/extensions/` as an extension, so a new module would be loaded code outside the fingerprinted set.
- DEC-100 SUPPLIES the outcome vocabulary. This is a hook refusal, not a gate's own failure, so it
  is never read as "unavailable".
- DEC-251 SUPPLIES the rule that non-governed calls remain unchanged. Main's non-governed calls are
  never checked.
- DEC-204 and DEC-100 SUPPLY the held-run BLOCKED-yield exception, kept unchanged. D-02's
  carve-out lets a persona's BLOCKED yield through a stale process exactly as through a held run,
  so both clauses stay true and no decision is amended. Passing the stale check only admits that
  yield to normal validation; it does not guarantee the run completes or releases its claim.
  DEC-202 (hook location) and DEC-237 (live
  yield validation, for calls that reach it) SUPPLY mechanisms this feature keeps unchanged.
- Assigned PRODUCT checkout:
  `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection`.
  Its `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent. The Harness docs
  under `.harness/harness/docs/` are the governing record.

## Out of scope

- Python gate scripts: each runs as a new process per call, so it is never stale.
- Hot-reloading extensions inside a running process.
- Everything in #2565 (frontmatter route, fail-closed yield).
- A warn-and-continue mode: the operator ruled it out.

## Approval

status: approved
approved-by: operator
date: 2026-11-27
