# T-06 intent — adapter-generation direction corrected

**The batch premise is confirmed at source, and T-06's signed intent had the direction backwards.**
One field amended: `tasks[T-06].intent`. Approval bytes untouched; no re-signature needed.

## Measured direction — `.claude/skills/harness/bin/sync-agent-adapters.py` (304 lines, read in the worktree)

| Lines | What they establish |
|---|---|
| 2-5 (docstring) | "Canonical role policy lives in `.omp/agents`. Claude files are generated compatibility adapters; edit the OMP source, then run `--apply`." |
| 229-242 | `expected_adapters(canonical_dir)` — the READ: globs `harness-*.md` under the canonical dir, renders each via `claude_adapter(path)` |
| 258-281 `sync()` | `canonical_dir = root/".omp"/"agents"` (259), `adapter_dir = root/".claude"/"agents"` (260); WRITES are `target.write_text(content)` into `adapter_dir` (272) and `(adapter_dir/name).unlink()` (276) |
| 284-300 `main()` | `--apply` → `sync(root, check=False)`; `--check` → same with `check=True` (297) |
| 245-255 `bootstrap()` | the ONLY claude→omp direction, behind `--bootstrap-from-claude`, and it raises when `.omp/agents` already holds harness agents (251-252) |

Direction: **`.omp/agents` is read, `.claude/agents` is written.** `bootstrap()` line numbers sit two
lines later than the batch context stated (245-255 vs 240-255 / 258-281 vs 258-282); the behaviour is
identical. No contradiction — the amend proceeded.

## Before → after (only these clauses changed)

- Item 4 opening, before: `4. .claude/agents/harness-dev-ops.md, the test-runner detection job at ~52-53. The write`
  after: `4. .omp/agents/harness-dev-ops.md is the CANONICAL source and is the file to EDIT: the` / `test-runner detection job at ~52-53. The write`
- Item 5 opening, before: `5. .omp/agents/harness-dev-ops.md is a DISTINCT FILE in the adapter format, not a link. Do not hand-edit it. Run`
  after: `5. .claude/agents/harness-dev-ops.md is a DISTINCT FILE in the adapter format, not a link: it is a GENERATED compatibility adapter, PRODUCED from the canonical .omp source. Do not hand-edit it. After the canonical edit in item 4, run`
- Item 5, before: `to regenerate it from the .claude copy, then` → after: `which reads .omp/agents and writes the Claude adapter, then`
- Item 5, added after the `check-omp-port.py` step: `Editing the Claude adapter directly is OVERWRITTEN by the next --apply, and that is how this was found: an edit to .claude/agents/harness-dev-ops.md followed by --apply was overwritten with the old .omp text.`

Carried word for word: the four-line preamble, items 1-3, both write-target cases of item 4, the
fleet-member `.harness/harness.json` clause, the default-branch landing, the never-push /
never-write-`fleet.yaml` clause, "Keep the verify-every-cmd paragraph and everything after it
unchanged", the `check-omp-port.py` "OMP port surface: ok" step, the side-effect-sweep clause, and
the `~line 12` / `~line 18` / `~7 and ~12` / `~52-53` anchors.

## Evidence

- Amend: `plan-merge.py amend --key tasks --id T-06 --field intent --expect-sha256
  e132766814d83079cb8f907b20bd67d88b0303b30c075efb4af449cb99537f4a --value-file …` →
  `AMENDED tasks:T-06.intent` / `APPLIED …`. (The verb's flags are `--key/--id`, not `--task`.)
- Byte-identity check: loaded T-06 from `git show HEAD:…plan.yaml` and from the working tree —
  fields differing are `['status', 'intent']` only (`status: ready→building` predates this run; it
  already read `building` before the amend), and preamble+items 1-3 compare equal at 1688 bytes.
  Unified diff of the intent shows exactly the four clause hunks above.
- `approval` reloads as `{'date': '2026-09-08', 'approved_by': 'molchairuangutai', 'status':
  'approved'}`; `files` and the nine-line `verify:` block reload unchanged and byte-match the
  dispatch's verbatim copy.
- `git diff` on plan.yaml contains **zero** `+`/`-` lines matching `approval|approved_by|molchairuangutai`.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0.

## Open

- `git diff --stat` lists 15 files; 14 are sibling T-01/T-05/T-08 work already in the tree before
  this dispatch. plan.yaml is the only file this run touched.
- The `~52-53` anchor is preserved as instructed but now points into the `.omp` file, whose adapter
  formatting may put the test-runner job at a different line. Non-blocking: the anchor is prefixed
  `~` and the surrounding text names the job.
