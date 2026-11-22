# T-01 red-first evidence

Worktree: `.claude/worktrees/harness/BUG-2305-schema-copy-idempotent`, branch HEAD b9707eb5, base 7f9cc9d8.

## Red — tests extended, hook still at base

`git diff --quiet 7f9cc9d8 -- .omp/extensions/harness-hooks.ts` → hook identical to base.

Command: `bun test tests/unit/omp-hooks.test.ts` → exit 1, `159 pass / 5 fail`. All five are assertion failures, not setup or import errors:

| Test | Assertion failure on base |
|---|---|
| injects every one of the 16 personas' own strict bundle, leaving other targets and fields alone | `expect(result).not.toHaveProperty("additionalContext")` received `"The hook injected outputSchema and schemaMode into this task call; never copy these fields into a task call."` |
| injects into a flat governed dispatch and keeps its other fields | `toEqual` diff: received an extra `additionalContext` with the note |
| BUG-2305: every persona's injected bundle, copied back strict, is accepted flat and per item | `harness-ai-dev` flat copy: `block: true`, reason `Harness dispatches never carry outputSchema, schemaMode: ...` |
| BUG-2305: a batch accepts copies at any position beside plain and non-harness items | `expect(result?.block).toBeUndefined()` received `true` |
| BUG-2305: an accepted copy never masks a later invalid item | reason was `never carry tasks[0].outputSchema, tasks[0].schemaMode, tasks[2].outputSchema, tasks[2].schemaMode: ...`, so the accepted item 0 was refused too |

The SC-02 refusal tests (`every other schema control is refused flat and per item...`, `batch top-level controls stay refused...`, `a copied pair for a persona whose bundle cannot load...`) passed on base, as expected: the base hook refused every control.

## Green — after the hook change

- `bun test tests/unit/omp-hooks.test.ts` → exit 0, `164 pass / 0 fail`, 1218 expect() calls.
- `.agents/skills/harness/bin/run-unit-tests.py --kind unit` → rc 0 (63 files).
- `gen-decisions-index.py` regenerated the index; `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` → exit 0, so a second run produces no diff.
- Typecheck: `.harness/harness.json` `typecheck.cmd` is null and its status is unresolved (#2257). No tsc is installed, so no typecheck was run.
