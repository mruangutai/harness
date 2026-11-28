# BUG-2566 build receipt: main-session-direct (DEC-174)

Both tasks are `execution_mode: main-session-direct`. The main session built them in the product checkout on `feat/BUG-2566-stale-hook-detection`, after merging `main` at 87efcd8a (BUG-2565 landed, D-04).

| Task | Commit | Verify |
|---|---|---|
| T-01 hook fingerprint and stale refusal | `a9691cbb` | exit 0: both D-04 checks; `bun test tests/unit/omp-hooks.test.ts` 274 pass / 0 fail; `bun run typecheck` exit 0; the three grep counts match |
| T-02 SPEC §4.2 | `07cf4954` | `SPEC 4.2 ok`, exit 0 |

## Test-first evidence

`notes/fail-first-T-01.md` records:

- 26 new cases RED against the unchanged hook;
- 8 cases preserved (the four BLOCKED-yield carve-outs and the four SC-03 Main cases);
- GREEN afterwards;
- the mtime mutant failing exactly the four discriminating cases (the three SC-04 timestamp cases and SC-01's same-size, fixed-mtime case), with the hook restored and confirmed by `cmp`.

T-02 is `docs`, so it is exempt.

## Form note

T-02 asked for one paragraph. The SPEC text is one bold run-in followed by four short paragraphs and a three-item list, all in the order the intent gives, and it carries every required phrase. It was split for readability only; no content departs from the intent.

## SIMPLIFY pass

Under DEC-174 the main session ran the four angles itself, read-only, over `87efcd8a..07cf4954`:

- **reuse.** One candidate, not applied: `isBlockedYieldData` repeats the yield handler's JSON-text decode (`harness-hooks.ts`, the `JSON.parse(digest)` in the yield branch). The signed T-01 text prescribes that function and its behaviour exactly, so folding the two would depart from the signed task.
- **simplification.** Empty.
- **efficiency.** Empty. The check hashes one ~104 KB file per governed call. SC-05's test bounds the median under 5 ms on the real module, against a 14 ms gate spawn (`notes/research-stale-hook-detection.md`).
- **altitude.** Leave. The check lives in the one module it fingerprints, as the constraint requires (a new module would itself be unfingerprinted loaded code).

## Open for the operator

SC-10 is `verify: uat`: start omp in this worktree, add a comment line to its `harness-hooks.ts`, and confirm that a `task` dispatch is refused with the restart line while read and edit still work, and that it proceeds after a restart.

## Fix round 1 (validate run 2026-11-27-04, ESCALATE)

Operator rulings are in `notes/answers-2026-11-27-validate-c1.md`:

- E-01 is accepted as is and not documented.
- The SC-10 steps are now `notes/uat.md`.

The two must_fix items are test-only, in `tests/unit/omp-hooks.test.ts`:

- **FIFO probe.** It now exits 3 unless `mkfifo` succeeded and `lstatSync(path).isFIFO()` holds, so a failed `mkfifo` can no longer pass as the deletion case.
- **`expectStale`.** It asserts `no longer matches ${H} on disk`, which witnesses that the path is relative to the loaded checkout's root.

Mutant M3 (`staleHookRefusal` using `process.cwd()` as the reason root) now fails 6 fingerprint cases: `bun test tests/unit/omp-hooks.test.ts -t 'BUG-2566 stale hook fingerprint'`, exit 1, 7 pass / 6 fail. The hook was restored from the saved copy, and `cmp` confirmed it equal, with `git diff` empty.

After the last edit:

- `bun test tests/unit/omp-hooks.test.ts`: 274 pass / 0 fail.
- `bun run typecheck`: exit 0.
