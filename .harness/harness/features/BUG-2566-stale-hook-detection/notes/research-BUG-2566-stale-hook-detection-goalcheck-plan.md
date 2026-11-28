# Goal-check (plan) — BUG-2566-stale-hook-detection

## Cycle 3 — run 2026-11-27-03-plan-product (current)

**Verdict: PASS. The plan as it stands after the cycle-3 apply delivers the operator's intent as
amended. No gap blocks signature.** Graded against the grilling
(`.harness/notes/grilling-stale-hook-detection-2026-11-27.md`) with the later answers taking
precedence: run 01 (`notes/answers-2026-11-27-01-plan-product.md`) re-decided the fingerprint set
to the loaded hook module only, dropped `digest-schema.ts`, took the BLOCKED-yield carve-out, and
put Q-05 out of scope. Run 02 (`notes/answers-2026-11-27-02-plan-product.md`) folded the four
reader remedies into T-01, resolved PF-7f19ccf3 and PF-298aabb8, and kept the persona suffix.
Nothing still in the plan contradicts a re-decided grilling item. All 10 SCs are met in the plan.
Three non-blocking advisories follow.

Inputs: `BRIEF.md`, `plan.yaml` (`approval.status: pending`, unchanged by this check), and
`notes/research-apply-c3.md`. Read-only spot checks were made against the worktree hook at
e12381fd and against BUG-2565's pending plan. `plan-merge.py check --root <worktree>` reports
2 tasks, 3 anchors resolved and 0 failures.

### SC grading (method: plan inspection)

| SC | Carried by | Verdict | Anchor |
|---|---|---|---|
| SC-01 | T-01 tests (d); items 2, 5, 6 | met-in-plan | Every case has its own test: append, delete, same size with mtime fixed at M (size and mtime asserted), and FIFO in a killable `spawnSync` probe (timeout 5000, SIGKILL, test 15000 ms, signal null / status 0). The reason has no newline and names H relative to `gateRoot()`, which is derived from `import.meta.url` (hook `gateRoot`), so it is the temp root. |
| SC-02 | T-01 handler paragraph; tests (a), (b) | met-in-plan | (a) covers all 13 refused calls with exact reason P or the bare reason, plus `calls.length` unchanged. (b) covers 4 carve-out cases, each with exactly one `validate-digest.py` call, `args ["--hook"]` and `digest_object` deep-equal. `isBlockedYieldData` decodes like the hook's yield path (`JSON.parse` on string, non-array object), so it matches the held-run test `VERDICT !== "BLOCKED"`. |
| SC-03 | T-01 test (c) | met-in-plan | Main read, edit, write and `bash git status` are each their own test. `governedCall` excludes them. |
| SC-04 | T-01 test (e); mutant paragraph | met-in-plan | Covers touch, identical rewrite and restore (controlled mtimes on H only), schema change, schema removal, the never-loaded `digest-schema.ts`, and tree A versus tree B. The mtime mutant must also redden SC-01's same-size case. |
| SC-05 | T-01 test (f) | met-in-plan | 20 warm-up calls, then 200 timed calls, with a median under 5 ms on the real module. |
| SC-06 | T-01 items 1–7, MERGE_COMMAND_PREFILTER; verify greps | met-in-plan | `HOOK_FINGERPRINT_MODULES` = [HOOK_MODULE] from `import.meta.url`. One descriptor serves both the `O_NONBLOCK` open and the `fstat` check. Only item 6 is exported. D-04 makes `.omp/extensions/` hold only `harness-hooks.ts`. |
| SC-07 | T-01 verify `bun test` | met-in-plan | `tests/unit/test-omp-hooks.py` exists. The unit kind cmd is `run-unit-tests.py --kind unit` (harness.json). |
| SC-08 | T-01 verify `bun run typecheck` | met-in-plan | — |
| SC-09 | T-02 intent and verify (reads `HEAD:` SPEC.md) | met-in-plan | All five bullets appear in the T-02 paragraph content, and the verify asserts the 9 key phrases. |
| SC-10 | T-01 (traces); UAT script is Mode 3 | met-in-plan | It stays `not_met` until the operator runs it. `notes/uat.md` is not yet authored, which is expected at plan exit. |

Perspective coverage: operator (SC-01, 02, 03, 09, 10), orchestrator (SC-04, 05) and code
maintainer (SC-06, 07, 08) each have at least one SC, and every SC is traced by a task.

### Amended-intent map

| Intent item (source) | SC | Task / decision | Holds |
|---|---|---|---|
| Stale session refuses governed calls with one restart-omp line and never enforces silently (grilling Destination) | SC-01, SC-02, SC-10 | T-01, D-02 | yes |
| Fingerprint only the loaded hook module(s); schema dir dropped; `.omp/agents` not added (run-01 Q-02, overrides grilling Settled) | SC-04, SC-06 | T-01 item 4, D-03 | yes |
| `digest-schema.ts` entry dropped (run-01 Q-03) | SC-04 (sidecar case), SC-06 | T-01 precondition, D-04 | yes |
| BLOCKED-yield carve-out, as in the held-run gate (run-01 Q-04) | SC-02 (b), SC-09 | T-01 `blockedYield`, D-02, T-02 | yes |
| No warn-and-continue (grilling Settled) | SC-02 | D-02; BRIEF Out of scope | yes |
| Builds sequential, 2565 first (grilling Settled timing) | — (ordering, not an outcome) | D-04, T-01 precondition and verify lines 2–3 | yes |
| Main-session-direct under DEC-174 (grilling Settled) | — | T-01, T-02 `execution_mode`; lanes rows | yes |
| Per-call cost (grilling Not yet specified) | SC-05 | D-01 | yes |
| Interaction with #2565's schema-dir removal (grilling Not yet specified) | SC-04, SC-06 | Settled by Q-02 drop; D-03, D-04 | yes |
| harness.json and team-config not fingerprinted (grilling Settled, not re-decided) | SC-06 ("exactly the loaded hook module") | D-03 | yes |
| Out of scope: Python gates, hot reload, #2565 work, Q-05 backlog | — | No task touches `bin/`; T-02 leaves DECISIONS.md alone | yes |
| Run-02 Q-01 remedies PF-1cf493dc, PF-3eb8320f, PF-37c5f930, PF-292338b0 in T-01 | SC-01, SC-02, SC-04, SC-06 | T-01 tests (a), (b), (d), (e); item 2 | yes; each is `resolved_by: T-01` |
| Run-02 Q-02: PF-7f19ccf3, PF-298aabb8 resolved | — | `panel.findings`; D-04 and D-02 texts already corrected | yes |
| Run-02 Q-03: persona suffix verbatim; Main gets none | SC-02 | D-02 choice, T-01 handler and P | yes (verbatim in all three) |

Decision dispositions: every `decisions_affected` row is `keep`, so none is graded. BUG-2565's
pending plan amends DEC-100, DEC-202 and DEC-237, but at clauses different from this plan's keep
clauses. The DEC-237 amendment, for example, targets "Dispatch owns schema delivery", not "Yield
owns live validation".

### Advisories (non-blocking)

- **BRIEF SC-02, "The carve-out is exactly as narrow as the held-run gate's".** This overclaims
  by one case. The hook's yield path lets a held run's data-less finalize through
  (`if (digest == null && input.type === "result") return undefined;`), but stale refuses it
  (T-01 test (a)). The operator accepted that denial (run-02 Q-01), so this is a wording point
  about the data-bearing yields only. BUG-2565 may also remove that early return. The parenthetical
  in T-01 test (a), "before the existing data-less early return", would then describe code that
  no longer exists, but the assertion still holds.
- **T-01 verify export-grep omits `isBlockedYieldData`.** SC-06 (inspection) still makes it
  module-private, so the reviewer carries it. The grep line is a partial witness, not the
  criterion.
- **The orchestrator's "agent definition regenerated" has no behavioural case.** SC-04 shows
  exclusion behaviourally for schemas and the sidecar only. Exclusion of `.omp/agents` rests on
  SC-06's inspection that the set is exactly the hook module. That is a sufficient method,
  but there is only one.

## Cycle 1 (superseded — graded the pre-ruling plan; kept as history)


**Verdict: PASS. Yes, this plan delivers what the operator asked for.** The grilling artifact
`.harness/notes/grilling-stale-hook-detection-2026-11-27.md` says a stale omp process must refuse
governed calls with one restart-omp line and must never enforce old rules silently. T-01 builds
that, and T-02 records it. Every operator constraint holds. The plan also settles both of the
grilling's open questions: per-call cost is settled by D-01 and SC-05, and the interaction with
#2565 by D-04 together with the gateRoot/BIN derivation.

Inputs: BRIEF.md, plan.yaml (approval pending) and the hook at the worktree's
`.omp/extensions/harness-hooks.ts#registerHarnessHooks`. Nothing in the plan was changed.

## Perspectives

- **operator — pass.** These SCs carry it:
  - SC-01: the fingerprint trips, and names the path, for every change class.
  - SC-02: every governed call is blocked, and stale takes precedence over held.
  - SC-03: Main's read, edit, write and ordinary bash are unaffected.
  - SC-09: SPEC 4.2 states that sessions started before the ship must be restarted once.
  - SC-10: the operator runs the live restart-omp UAT.

  T-01 carries SC-01, SC-02, SC-03 and SC-10. T-02 carries SC-09.
- **orchestrator — pass.** SC-04 shows the check compares content, not mtime, and that a change
  in another checkout does not trip it. A planned mtime mutant proves the discrimination. SC-05
  requires a median under 5 ms (the baseline is 0.35 ms). T-01 carries both SCs.
- **code maintainer — pass.** SC-06 (by inspection) checks that the fingerprinted set lives in one
  place, is derived from `import.meta.url` and `gateRoot()`/`BIN`, and that only
  `staleHookRefusal` is exported. SC-07 (the hook suite) and SC-08 (typecheck) cover the rest.
  T-01 carries all three; T-01's verify greps confirm the export surface.

Every perspective has at least one SC, and a task carries every SC. No SC is orphaned.

## Operator constraints

| Constraint (grilling) | Plan | Holds |
|---|---|---|
| Every task main-session-direct (DEC-174) | T-01 and T-02 both have `execution_mode: main-session-direct`, and all lanes rows are main-session-direct. | yes |
| Fingerprint exactly the two extension modules plus the digest schema directory | `HOOK_FINGERPRINT_MODULES` = the module and its sibling `digest-schema.ts`. `HOOK_SCHEMA_DIR` = `gateRoot()/BIN/../schemas/digest`, plus each entry directly in it (D-03). harness.json and team-config are excluded (BRIEF Constraints). | yes |
| Every governed call refused with one restart-omp line; no warn-and-continue | `governedCall` = persona session, Main task, or Main bash matching the merge prefilter. The stale check runs before every other check, including held-run, MISSING_CAPABILITY and yield (D-02). The reason is one line containing `restart omp` (T-01 item 5). The BRIEF's Out of scope excludes warn-and-continue. | yes |
| Per-call check cheap | D-01 re-hashes the content with sha256 and does not take a stat shortcut. SC-05 requires a median under 5 ms. | yes |
| Python gate scripts out of scope | BRIEF Out of scope; no task touches `bin/`. | yes |

**The governed set matches the hook.** At e12381fd the `tool_call` handler sends Main bash only
through `mainMergeGate`'s `\bmerge\b` prefilter. It returns early for Main's other calls unless
the call is `ompMainTask` (`registerHarnessHooks` `tool_call`). So `governedCall` covers exactly
the calls that reach a policy gate, and DEC-251's carve-out for non-governed calls stays intact.

## Advisory (non-blocking)

- **T-01 cannot run yet.** At `main` e12381fd, `.omp/extensions/digest-schema.ts` still exists and
  `harness-hooks.ts` still imports it (`git ls-tree`, `git grep -c` → 1). Under D-04, T-01 will
  stop BLOCKED until BUG-2565 lands. That ordering is the one the operator chose.
- **Two fingerprint entries go beyond what the post-2565 hook loads.** The `schemas/digest`
  directory and `digest-schema.ts` both stay in the fingerprint because the operator settled
  them. Panel findings PF-03296… and PF-8ddb… challenge them. The plan follows the operator's
  intent, which is correct; whether to drop them is the operator's ruling.
- **All 10 panel findings are still recorded `disposition: open`.** The revised plan text appears
  to address PF-0050 (D-04), PF-6aff/PF-75ab (per-entry naming), PF-7f61 (FIFO never opened),
  PF-d595 (the DEC-204/DEC-100 amendments), PF-96c3 (the mutant is scheduled) and PF-8a3e (private
  internals). PF-45fe, which says a stale yield strands in-flight subagents, matches the
  operator's ruling: every governed call is refused, with no warn-and-continue. Recording the
  dispositions belongs to the panel/record-panel route, not to this check.
- **`before_subagent_spawn` and the session-start hooks are not guarded.** They are not tool
  calls. They are reached only after a `task` call, and the stale check already refuses that call
  when the code is stale.
