# Goal-check, validate cycle 1: BUG-2566-stale-hook-detection

Pin: `8e18c053f60369b38c182ecbbea75ccc0002947e`. Diff: `87efcd8a..8e18c053`. Run: `2026-11-27-04-validate-validator`.
Reader: harness-pm (goalcheck). This note grades only. It fixes nothing and does not re-plan.

**BLUF: PASS.** The orchestrator and code maintainer perspectives are fully discharged. The operator
perspective is discharged on every automated and inspection SC. Only SC-10 (`verify: uat`) remains,
and it is pending the operator, not failed. None of the four D-NN choices departs from the shipped
code. `decisions_affected` holds six `keep` rows and no amend or strike rows. All six kept clauses
are still present and still true at the pin, and the diff leaves DECISIONS.md untouched.

## Method (what I ran, at the pin)

- I extracted a `git archive 8e18c053` to `/tmp/bug2566gc.Kg1F` and ran `bun install --frozen-lockfile`.
  `HARNESS_AGENT_TYPE` was unset for the runs.
- `python3 tests/unit/test-omp-hooks.py` exited 0 with **274 pass, 0 fail** and zero `(fail)` lines.
  `bun run typecheck` exited 0.
- I ran a 12-mutant harness, `-t BUG-2566`, applying one mutant at a time to the archive copy of
  `harness-hooks.ts`. The hook was restored afterwards, confirmed byte-equal. Results are below.
- A fail-open probe on a copied tree: the loaded module made unreadable (chmod 000), then replaced by a directory.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **partial: pending UAT only** | SC-01, SC-02, SC-03, SC-09 met; SC-10 pending | Refusal of every governed call, BLOCKED-yield carve-out, Main recovery and the SPEC record are all proven (rows below). The live-omp claims (once-per-process import, the reason reaching the user verbatim, worktree load) rest on SC-10, which the operator has not run. |
| orchestrator | **pass** | SC-04, SC-05 | No refusal on touch, identical rewrite, restore, schema edit or removal, a new unloaded module, or another checkout's edits. Median under 5 ms on the real module. |
| code maintainer | **pass** | SC-06, SC-07, SC-08 | One fingerprint array derived from `import.meta.url`, the whole suite green, typecheck 0. |

## SC rows

- **SC-01 met** (automated). Tests `BUG-2566 SC-01: …` (5 cases, `tests/unit/omp-hooks.test.ts`,
  describe `BUG-2566 stale hook fingerprint`). Mutant A (the pre-change hook from 87efcd8a) fails all
  five, which re-measures fail-first (26 RED, 8 preserved, matching `notes/fail-first-T-01.md`). Mutant J
  (an mtime detector) fails the same-size, fixed-mtime case. Mutant L (a blocking open with no stat)
  fails the FIFO case at its 5 s deadline instead of hanging. Mutant B (a cwd-derived module path) fails 4/5.
- **SC-02 met** (automated). 13 refused cases and 4 carve-out cases. Mutant C (the held-run gate before
  stale) fails the held-read case. D (carve-out widened to any yield) fails 5 yield cases. G (Main task
  ungoverned) and H (merge regex narrowed to `git merge`) each fail their own case. The carve-out
  predicate `isBlockedYieldData` uses the same decode and `VERDICT === "BLOCKED"` test as the held-run
  yield branch (`harness-hooks.ts`, the `!reason && toolName === "yield"` block), so it is exactly as narrow.
- **SC-03 met** (automated). There are 4 `BUG-2566 SC-03` cases. Mutant I (all Main bash governed) fails the `git status` case.
- **SC-04 met** (automated). There are 7 `BUG-2566 SC-04` cases. J fails touch, identical rewrite and restore.
  K (schema file and `digest-schema.ts` fingerprinted) fails the schema and new-module cases. B fails the other-checkout case.
- **SC-05 met** (automated). `BUG-2566 SC-05` is green in the pin run. It bounds the test host only (a signed gap).
- **SC-06 met** (inspection, `git show 8e18c053:.omp/extensions/harness-hooks.ts`). It holds at the following
  symbols: `HOOK_MODULE = fileURLToPath(import.meta.url)`; `HOOK_FINGERPRINT_MODULES = [HOOK_MODULE]`;
  `entryState` (statSync classifies kind, one `O_RDONLY|O_NONBLOCK` fd, `fstatSync` before
  `readFileSync(fd)`, closed in `finally`); `LOADED_HOOK_FINGERPRINT` is module-level; and `staleHookRefusal`
  is the only new export. In the `tool_call` handler, the stale block is the first `return` after `ompMainTask`.
  `governedCall` uses `MERGE_COMMAND_PREFILTER`, which `mainMergeGate` also tests. A grep finds no
  `DIGEST_SCHEMA_DIR`, `loadDigestSchemaBundle` or `digest-schema`, and no `process.cwd`/`process.env` in
  the new code. `git ls-tree` lists only `harness-hooks.ts` in `.omp/extensions/`.
- **SC-07 met** (automated). `tests/unit/test-omp-hooks.py` exits 0: 274/0 at the pin.
- **SC-08 met** (automated). `bun run typecheck` exits 0 at the pin.
- **SC-09 met** (inspection, `git show 8e18c053:.harness/harness/docs/SPEC.md`, §4.2, the paragraph
  `**Stale hook code (BUG-2566).**`). All five required statements are present. T-02's literal verify
  prints `SPEC 4.2 ok`.
- **SC-10 pending** (uat). It is the operator's to run. The steps are in `notes/receipt-main-session-build.md`, "Open for the operator".

## Decision dispositions

- **D-01 to D-04** (plan choices, not DEC rows; graded by inspection):
  - D-01 landed: full sha256 on every check, and stat only classifies.
  - D-02 landed: stale first, the persona suffix, a bare Main reason, the BLOCKED carve-out, and Main's other calls unchecked.
  - D-03 landed: the fingerprint holds the hook module alone and is resolved from `import.meta.url`.
  - D-04 held: `digest-schema.ts` is absent at the pin, and `grep -c 'from "./digest-schema'` returns 0.
- **The `decisions_affected` rows are all `keep`.** Per Mode 2 they are not graded. As a check, I
  confirmed each clause is verbatim at the pin in `.harness/harness/docs/DECISIONS.md` and still true:

  | DEC | Pinned line |
  |---|---|
  | DEC-174 | 4527 |
  | DEC-204 | 6615 |
  | DEC-100 | 1447 |
  | DEC-202 | 6294 |
  | DEC-237 | 8080 |
  | DEC-251 | 8298 |

  `git diff --quiet 87efcd8a 8e18c053 -- DECISIONS.md DECISIONS-INDEX.md` exits 0. The BRIEF
  `## Constraints` SUPPLIES list (DEC-100, 179, 202, 204, 237, 251) and the BLOCKS entry (DEC-174)
  remain consistent with the shipped code.

## Probes and advisories (none fails an SC)

1. **Fail-open hunt: fails closed.** Executed on a copied tree:
   - A loaded module made unreadable returns the stale reason (`unreadable:EACCES` differs from the
     load-time hash).
   - A loaded module replaced by a directory returns the stale reason.
   - A restored module returns `undefined`.
   - `entryState` catches every error, so the fingerprint never throws.
   - The module path comes from `import.meta.url`, never from a lookup that could fail.
2. **Advisory, low, substance, T-01. Survivor: mutant E.** E changes `isBlockedYieldData` to
   `String(VERDICT).trim().toUpperCase() === "BLOCKED"`, and all 34 BUG-2566 tests stay green. So the
   exact-match clause of the carve-out ("VERDICT exactly BLOCKED", SC-06) rests on inspection alone,
   with no case-level witness such as `"blocked"` or `" BLOCKED"`. The shipped code is exact, so SC-06
   is met. Repair: add one refused-yield case with a lowercase or padded VERDICT.
3. **Equivalent mutant, not a gap: mutant F.** F admits Main's yields to the carve-out and stays green.
   A Main yield is never governed, so `blockedYield` has no effect there.
4. **Form, low, T-01 (SC-06 wording).** The SC says the check uses "only `node:fs` and `node:crypto`".
   `staleHookReason` also uses `relative` from `node:path`, and `HOOK_MODULE` uses `fileURLToPath`
   from `node:url`. The signed T-01 intent prescribes both. Both are pure string helpers that spawn
   nothing and do no I/O, so the clause's purpose holds.
5. **UAT script absent.** There is no `notes/uat.md` at the pin. SC-10's steps live only in the build
   receipt. This is pm Mode 3 work, not a T-NN defect.
