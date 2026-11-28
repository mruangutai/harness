# Goal-check, validate cycle 2: BUG-2566-stale-hook-detection

Pin: `f4048ad3f9fbe9326d9799485fb97d87547d27be`. Diff: `87efcd8a..f4048ad3`. Fix-round delta: `8e18c053..f4048ad3`.
Reader: harness-pm (goalcheck). This note grades only. It fixes nothing and does not re-plan. E-01 is settled and not re-raised.

**BLUF: PASS.** Both must_fix items from run 04 close at the pin, and I re-measured each one.
- **FIFO construction.** The FIFO case now fails when `mkfifo` cannot run.
- **Relative to that root.** The `process.cwd()` reason-root mutant now fails 6 cases.

The orchestrator and code maintainer perspectives pass. The operator perspective is discharged on
every automated and inspection SC. SC-10 (uat) is still pending the operator. `decisions_affected`
has only `keep` rows, so there are no amend or strike dispositions to grade.

## Method (run by me, at the pin)

- I extracted `git archive f4048ad3` to `/tmp/bug2566c2.jMbJ` and ran `bun install --frozen-lockfile`.
  `HARNESS_AGENT_TYPE` was unset. The probe script is `/tmp/bug2566c2.jMbJ/gc_probe.py`.
- `python3 tests/unit/test-omp-hooks.py` exited 0 with 274 pass, 0 fail and zero `(fail)` lines.
  `bun run typecheck` exited 0.
- The fix round touches no code: `git diff --quiet 8e18c053 f4048ad3 -- .omp .harness/harness/docs/SPEC.md` exits 0.
- `71d686d6` matches `f4048ad3` everywhere except `feature.json` (diff quiet, exit 0).
- The delta to the tests is the 8 lines of `tests/unit/omp-hooks.test.ts`, inside `expectStale` and the FIFO probe.
- Mutants were applied one at a time to the archive copy, with `-t BUG-2566` (34 cases). The hook was restored afterwards and checked byte-equal.

| Probe | Result |
|---|---|
| Baseline | 34 pass / 0 fail |
| M3: `staleHookRefusal` passes `process.cwd()` as the reason root | 28 pass / 6 fail. Fails SC-01 appended, deleted, same-size fixed-mtime and FIFO; SC-04 restore and other-checkout |
| L: blocking `openSync(O_RDONLY)` with no `statSync` kind check | 33 / 1. The FIFO case fails at its 5 s deadline and does not hang |
| Pre-change hook (87efcd8a) | 8 / 26. All 5 SC-01 cases, 13 SC-02 refused cases, 7 SC-04, SC-05 fail. The 8 survivors are the preserved carve-out and SC-03 cases |
| `mkfifo` absent from PATH (FIFO case only) | exit 1, FIFO case fails (`status` 3 ≠ 0). It is not mistaken for the deletion case |

## Must_fix closure (P-06: premise re-measured, implementation repair under the same contract)

1. **FIFO construction (SC-01, "the file replaced by a FIFO")**: closed.
   - The probe now captures `spawnSync("mkfifo", …)`.
   - It calls `process.exit(3)` unless `made.status === 0` and `lstatSync(path).isFIFO()`.
   - The test asserts `[signal, error, status]` equals `[null, undefined, 0]`.
   - Measured with `mkfifo` unavailable: the case fails. It no longer passes as a disguised deletion.
2. **"Relative to that root" (SC-01)**: closed.
   - `expectStale` asserts ``no longer matches ${H} on disk``.
   - With the cwd root, `relative()` yields a `../…` path, so the substring no longer matches.
   - M3 measured at 6 fails, matching the receipt's claim of 7 pass / 6 fail within the 13-case fingerprint describe.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **partial: pending UAT only** | SC-01, SC-02, SC-03, SC-09 met; SC-10 pending | Every governed call is refused, the BLOCKED carve-out holds, Main keeps its recovery calls, and SPEC §4.2 records it (rows below). The live-omp claims (once-per-process import, the reason reaching the user verbatim, worktree load) rest on SC-10. Its steps are now in `notes/uat.md` (OQ-02), and the result is unrecorded. |
| orchestrator | **pass** | SC-04, SC-05 | No refusal for a touch, an identical rewrite, a restore, a schema edit or removal, a new unloaded module, or another checkout's edits. The median is under 5 ms. |
| code maintainer | **pass** | SC-06, SC-07, SC-08 | One array derived from `import.meta.url`; the suite is green and typecheck exits 0. |

## SC rows

- **SC-01 met** (automated). There are 5 `BUG-2566 SC-01` cases in `tests/unit/omp-hooks.test.ts`, describe `BUG-2566 stale hook fingerprint`.
  - The pre-change hook fails all 5.
  - L fails the FIFO case at its deadline.
  - M3 fails the 4 stale cases.
  - The FIFO-construction and root-relative clauses are discriminated (above).
- **SC-02 met** (automated). There are 13 refused cases and 4 carve-out cases. All 13 refused cases are red on the pre-change hook, and the 4 carve-outs are preserved there. The hook is unchanged since c1, where mutants C, D, G and H each failed their own case.
- **SC-03 met** (automated). There are 4 cases, preserved on the pre-change hook. The hook is unchanged since c1, where mutant I failed the `git status` case.
- **SC-04 met** (automated). There are 7 cases, all red on the pre-change hook. M3 fails the other-checkout case. The mtime mutant J (c1) fails touch, rewrite and restore; the hook and these tests are unchanged since then.
- **SC-05 met** (automated). It is green in the pin run and bounds the test host only (a signed gap).
- **SC-06 met** (inspection, `git show f4048ad3:.omp/extensions/harness-hooks.ts`):
  - `HOOK_MODULE = fileURLToPath(import.meta.url)` and `HOOK_FINGERPRINT_MODULES = [HOOK_MODULE]`.
  - `entryState`: `statSync` classifies the kind, then one `O_RDONLY|O_NONBLOCK` fd is opened, `fstatSync` runs before `readFileSync(fd)`, and the fd is closed in `finally`.
  - `LOADED_HOOK_FINGERPRINT` is module-level, and `staleHookRefusal` is the only new export.
  - The reason root is `gateRoot()`, which is also `import.meta.url`-derived.
  - A grep finds 0 hits for `DIGEST_SCHEMA_DIR`, `loadDigestSchemaBundle` and `digest-schema`.
  - `git ls-tree` lists only `harness-hooks.ts`.
  - The c1 form note still applies and does not fail the SC: `relative` comes from `node:path` and `fileURLToPath` from `node:url`; both are pure string helpers that the signed T-01 intent prescribes.
- **SC-07 met** (automated). `test-omp-hooks.py` exits 0, with 274/0.
- **SC-08 met** (automated). `bun run typecheck` exits 0.
- **SC-09 met** (inspection). In `git show f4048ad3:.harness/harness/docs/SPEC.md`, the paragraph `**Stale hook code (BUG-2566).**` is at line 799. It is byte-unchanged since c1, where all five required statements were confirmed.
- **SC-10 pending** (uat). It is the operator's to run, from `notes/uat.md`. No result is recorded there yet.

## Decision dispositions

`plan.yaml decisions_affected` holds only `keep` rows: DEC-174, DEC-204, DEC-100, DEC-202, DEC-237 and DEC-251. Per Mode 2 these are not graded, and there are no amend or strike rows. `git diff --quiet 87efcd8a f4048ad3 -- DECISIONS.md DECISIONS-INDEX.md` exits 0. The headings at the pin are at:

| DEC | Heading line |
|---|---|
| DEC-100 | 1336 |
| DEC-174 | 4485 |
| DEC-202 | 6287 |
| DEC-204 | 6567 |
| DEC-237 | 8048 |
| DEC-251 | 8232 |

D-01 to D-04 are unchanged since c1, because the code is unchanged. D-04 still holds: `digest-schema` has 0 hits and the module is absent.

## Advisory (carried, not failing)

- Mutant E from c1 still applies: a case-insensitive `VERDICT` match has no case-level witness. The test delta did not add one. SC-06 is met by inspection.

## Open questions

None.
