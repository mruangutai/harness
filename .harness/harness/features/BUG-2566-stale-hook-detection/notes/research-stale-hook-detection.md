# Research — BUG-2566 stale hook detection (observed at e12381fd, 2026-11-27)

BLUF: hash the settled set in-process on every governed call (0.35 ms median, no stat shortcut),
baseline at module load, paths from the module's own location; the check lives inside
`harness-hooks.ts` and runs first in its `tool_call` handler. BUG-2565 deletes
`digest-schema.ts`, so a fingerprint entry must treat "absent" as a recordable state.

## Cost (D-01)

Measured with bun 1.3.14 on the worktree at e12381fd, 500 iterations after 50 warm-up:

| method | median | p99 |
|---|---|---|
| sha256 of harness-hooks.ts + digest-schema.ts + all 17 files in schemas/digest (≈200 KB) | 0.352 ms | 0.450 ms |
| stat (size, mtime, ino) of the same set | 0.058 ms | 0.080 ms |
| one `python3 -c pass` spawn (what every gate costs, at minimum) | 14.3 ms | — |

A governed call already spawns 1–5 Python gates, so a full re-hash is under 3% of one gate spawn.
The stat shortcut would save 0.3 ms and add a second code path whose false negative (a rewrite with
equal size and mtime) is exactly the silent-stale outcome this bug exists to remove. The plan
re-hashes on every governed call. The SC budget is 5 ms median, 14x the measured figure, so a
slower CI runner does not make it flaky.

## The governed set (question c)

From `registerHarnessHooks`'s `tool_call` handler at e12381fd, a call reaches a Harness gate when:

1. the session carries a Harness persona (`currentAgent` set): every tool, `yield` included;
2. Main's `task` call (`ompMainTask`: no persona, agent id `Main`, no parent), which runs dispatch-guard;
3. Main's `bash` whose command matches `\bmerge\b`, the `mainMergeGate` prefilter that spawns merge-gate.py.

Every other Main call (read, edit, write, non-merge bash) returns before any gate and is not
governed; the stale check leaves those alone, so the operator can always repair and restart.

## Paths (question a)

`gateRoot()` already derives the checkout from `import.meta.url`. OMP loads project extensions once
per process from the checkout it started in (grilling fact, OMP 19.2.1). Subagents run in the same
process and share the module, so they share the baseline. The fingerprinted set is therefore
`fileURLToPath(import.meta.url)`, its sibling `digest-schema.ts`, and
`join(gateRoot(), BIN, "..", "schemas", "digest")`, all in the checkout the module was loaded from.
A session started in the main checkout does not react when only a worktree copy changes, because
the code it is running did not change. It trips when the main checkout changes: a pull after a
merge, a branch switch, or a direct edit.

## Self-edit (question b)

The main session builds this feature by editing worktree copies, which leaves the main checkout's
loaded files untouched. A main session started inside the worktree would trip after its first
edit, but only on `task` and merge-bash. Edits, test runs and non-merge Bash are not governed and
keep working, and every build task here is main-session-direct with no dispatch. After the merge
and pull, every running session's next governed call is refused, including the session that did
the merge. Restarting omp is the intended recovery.

## Baseline timing (question d)

The baseline is a module-level constant, computed when OMP imports `harness-hooks.ts`. A process
started before this code is on disk has no baseline and no check, so it cannot self-detect. The
operator must restart each running omp session once after this ships.

## BUG-2565 interaction (ordering assumption: 2565 lands first)

2565's T-02 deletes `DIGEST_SCHEMA_DIR`, `isInjectedCopy`, `schemaControlRefusal`,
`withDigestSchemas` and the import from `./digest-schema.ts`, and deletes
`.omp/extensions/digest-schema.ts` itself (2565 plan.yaml, task T-02 intent). It keeps
`registerHarnessHooks`, `gateRoot`, `BIN` and the `tool_call` handler. This plan therefore:

- derives the schema directory itself from `gateRoot()` and `BIN`, never from `DIGEST_SCHEMA_DIR`;
- anchors on `harness-hooks.ts#registerHarnessHooks`;
- records each entry as a content hash, `absent` or `unreadable:<code>`, so a digest-schema.ts that
  is already gone at load is a stable `absent`, and its later deletion (the other merge order) trips.

After 2565 the hook no longer reads schema files at all. The schema directory stays in the
fingerprint because the operator settled it: its content changes together with the regenerated
`.omp/agents/*` frontmatter that OMP also reads at start. Whether `.omp/agents/` belongs in the
fingerprint is left to the operator as a non-blocking question.

## Where the code lives

OMP loads every module in `.omp/extensions/` as an extension (`digest-schema.ts` exports a no-op
default extension for exactly that reason). A third module for the fingerprint would itself be
loaded code outside the settled set, so the code goes inside `harness-hooks.ts`.

## Test seam

`tests/unit/omp-hooks.test.ts` already has `copiedHooks(root)`, which copies `.omp/extensions/` into
a temp root and dynamically imports the copy. Its `gateRoot()` and its module-load baseline then
belong to that root. This proves module-located paths and load-time capture against real files.
`registerHarnessHooks` gains a third optional parameter, so handler cases can stub staleness without
touching disk.

## [INFERENCE] not measured

- That an omp session started with cwd inside a feature worktree loads that worktree's
  `.omp/extensions/`. The UAT step (SC-10) observes it directly.
