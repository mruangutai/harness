# FEAT-01 — four-angle plan quality pass

**PASS — all four readers returned and all four angle-named receipts were read on disk. Five advisory mechanisms retained for pm; nothing applied.** `cycles_used: 0`. Approval, BRIEF, plan and product unchanged. No installs, tests, builds, linters, formatters, smoke runs, credential inspection or gh-sync performed.

15 submitted findings collapse to 13 mechanisms: R-2/F-2 share value authority; R-4/S-5 share test-selection authority. Five mechanisms remain flag-only; eight are skipped with reasons. Duplicate reports remain below under their originating angle, with all five parts, but are not separate requests to pm. No angle was empty: reuse 4, simplification 6, efficiency 3, altitude 2 (plus 3 checked-and-left residuals).

## Inputs and receipts

All finding references `plan.yaml` and `BRIEF.md` resolve under `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/` (feature directory). Receipts are in its `notes/`:

| Angle | Persona | Receipt | Angle file |
| --- | --- | --- | --- |
| reuse | harness-backend-dev | receipt-harness-backend-dev-2026-10-05-3-simplify-eng.md | /Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-reuse.md |
| simplification | harness-frontend-dev | receipt-harness-frontend-dev-2026-10-05-3-simplify-eng.md | /Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-simplification.md |
| efficiency | harness-dev-ops | receipt-harness-dev-ops-2026-10-05-3-simplify-eng.md | /Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-efficiency.md |
| altitude | harness-data-engineer | receipt-harness-data-engineer-2026-10-05-3-simplify-eng.md | /Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-altitude.md |

Readers reviewed the draft and BRIEF with read-only Kaya context at `/Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform`, architecture and decisions, plus the supplied intake. The lead adjudicated disputed/truncated premises against full raw plan lines 144–258 and 260–307, BRIEF lines 1–62, and architecture lines 24–98. Findings are proposals, not observed implementation defects. All timing and future-drift costs are [INFERENCE], not measurements.

## REUSE

### R-1 — flag-only; medium
- **File / line:** `plan.yaml:272–273`, compared with `194–195,225`.
- **Summary:** T-08 separately describes env/project validation, privileged Supabase probing and pool/store initialization already owned by T-03/T-05.
- **Concrete cost:** [INFERENCE] independently implementing those descriptions would duplicate project-ref/5432 checks, TLS configuration and adapter initialization; later changes could miss the operator probe.
- **Alternative:** explicitly have T-08 consume the existing server-only env, safe Supabase probe and storage operations; keep confirmation, catalog/Data API checks and transactional SQL application probe-local. T-05 already permits shutdown for the owning process/probe; preserve process ownership rather than invent another per-request pool.
- **Lead assessment:** retain as a reuse clarification, not proof that two implementations exist. Do not mandate a new factory/seam if the existing storage interface suffices.

### R-2 — flag-only; low; canonical value-authority finding (also ALTITUDE F-2)
- **File / line:** `plan.yaml:195,225–226,240,272`.
- **Summary:** the server resource identity, provider and model are repeated without naming an implementation authority/export.
- **Concrete cost:** [INFERENCE] route metadata and the agent's selected model/resource could drift if separately hard-coded, while T-06 cannot edit T-05's owned files.
- **Alternative:** name the T-03 resource authority and T-05 provider/model authority; production consumers reuse those values. Keep independent expected literals in behavioral/live tests where they pin the accepted contract; T-10 records shipped values and actual compatibility evidence.
- **Lead assessment:** merge F-2 here. Reject the reader's optional suggestion that live assertions merely compare against imported implementation constants: that would weaken independent contract checks. D-01, the model-compatibility blocker and all accepted value constraints remain unchanged.

### R-3 — skip; low
- **File / line:** `plan.yaml:177,195,240,307`.
- **Summary:** status/error mappings are restated in tests, server contracts, route contract and documentation.
- **Concrete cost:** reader alleges four synchronized spellings and classification drift on future status changes [INFERENCE].
- **Alternative:** reader proposes T-05 error kinds and one T-06 status table, referenced rather than enumerated by T-02/T-10.
- **Skip reason:** enumerating the same public behavior for an independent test, its implementing task and operator documentation is not evidence of duplicate implementation. The current map is coherent. T-06 owns HTTP translation; T-03 owns its boundary results. Removing independent expected behavior risks assertion weakening and reduces self-contained dispatch context.

### R-4 — skip; low; canonical selection-authority finding (also SIMPLIFICATION S-5)
- **File / line:** `plan.yaml:150,287`.
- **Summary:** Vitest selectors and Harness detect strings state the same four-kind partition.
- **Concrete cost:** reader alleges future glob drift could silently misattribute test kinds [INFERENCE].
- **Alternative:** derive/compare Harness detection with Vitest project selection, or copy the T-01 receipt's authoritative partition.
- **Skip reason:** T-09 already says “Match Vitest discovery exactly, show each test is selected once in its intended kind and fail on no selected tests.” Both tools genuinely need their own configuration. The missing-comparison premise is false on the full text; no generator or additional abstraction is warranted. This does not claim the future gate has already run.

## SIMPLIFICATION

### S-1 — flag-only; low
- **File / line:** `plan.yaml:247,264`.
- **Summary:** the static landing depends on the API route; the probe's API dependency is hidden transitively through the landing.
- **Concrete cost:** [INFERENCE] T-07 carries a backend sequencing dependency despite forbidding browser imports of server/Mastra; the actual T-08 prerequisites become less local and obvious.
- **Alternative:** T-07 depends on T-02; T-08 explicitly depends on T-06 and T-07.
- **Lead assessment:** retain as task-graph clarity, not a promised parallel-build speedup. Mutating work remains serialized and no task/SC/settled lane is removed or amended by this pass.

### S-2 — skip; low
- **File / line:** `plan.yaml:256`; `BRIEF.md:15`.
- **Summary:** the approved-system light/dark styling alternative is called a dead reference because no styling system is installed.
- **Concrete cost:** reader alleges implementer/reviewer ambiguity over what qualifies [INFERENCE].
- **Alternative:** require only native/system colours and light/dark colour-scheme in both plan and SC-01.
- **Skip reason:** this reopens the expressly settled PF-86e4a4c3 static-document baseline and proposes changing the settled SC set. The conditional existing-system option does not authorize adding a dependency. No SC rewrite is routed.

### S-3 — skip; low
- **File / line:** `plan.yaml:177,255–257`; `BRIEF.md:15`.
- **Summary:** the landing's semantic, visual and scope acceptance appears in SC-01, red-test delivery and implementation instructions.
- **Concrete cost:** reader alleges synchronized future edits could drift [INFERENCE].
- **Alternative:** keep SC-01's complete conditions, replace task lists with “per SC-01,” and retain only task-specific ownership/red-receipt rules.
- **Skip reason:** these instructions are the applied, settled design finding and independently dispatched test/implementation obligations. T-02 also explicitly distinguishes DOM evidence from contrast/overflow UAT, so the lists are not identical. No evidence establishes avoidable complexity beyond necessary acceptance traceability.

### S-4 — skip; low
- **File / line:** `plan.yaml:46–54`.
- **Summary:** the frontend `app/*.tsx` lane overlaps the test lane; the additional `__tests__/*.test.ts` QA row is a subset of the broader test row.
- **Concrete cost:** reader alleges first-match ownership ambiguity for `page.test.tsx` and future redundant-row drift [INFERENCE].
- **Alternative:** list only `layout.tsx`/`page.tsx` as frontend lanes and remove the redundant QA subset row.
- **Skip reason:** the current tasks explicitly assign the exact test to QA in T-02 and only two production files to frontend in T-07, which forbids test edits. No first-match route mechanism was demonstrated; lane metadata is not the central write grant. Redundant prose alone does not support the alleged ownership defect. Settled grants are not widened or changed.

### S-5 — duplicate of R-4; skip; low
- **File / line:** `plan.yaml:150–151,287`.
- **Summary:** the unit exclusion/project partition is repeated within T-01 and in T-09 detection.
- **Concrete cost:** reader alleges drift could produce double- or zero-selection [INFERENCE].
- **Alternative:** state the partition in T-01 and make T-09 mirror its project globs, retaining Harness-specific settings only.
- **Skip reason:** same mechanism as R-4. T-09 already requires the exact match and per-kind single selection; T-01's explicit exclusion protects the QA-owned subsystem tests. No second action routed.

### S-6 — skip; low
- **File / line:** `plan.yaml:148,257,305`; `BRIEF.md:25,44`.
- **Summary:** prohibitions on speculative packages, flat source layout and Turbo/Nx recur in scaffold, landing and docs instructions.
- **Concrete cost:** reader alleges non-identical wording creates multiple standards for SC-06 [INFERENCE].
- **Alternative:** keep the rule only in SC-06/T-01 and remove it from T-07/T-10.
- **Skip reason:** no contradictory standard is present. Reaffirming the binding source-organization constraints in isolated implementation and documentation dispatches has a purpose; T-10 must document the accepted layout rather than advise a different one. Cosmetic trimming does not establish concrete avoided complexity.

## EFFICIENCY

### E-1 — flag-only; low
- **File / line:** `plan.yaml:253`.
- **Summary:** T-07 starts two pnpm/Vitest processes for its layout-unit and page-component files.
- **Concrete cost:** [INFERENCE] one additional cold start, estimated by the reader at 1–3 seconds; unmeasured and one-shot.
- **Alternative:** one filtered Vitest invocation selecting both projects and both exact files, only if each project's no-selection failure and all existing assertions remain equally enforced.
- **Lead assessment:** retain as optional minor startup savings, not a requirement to merge test kinds or omit any suite. Reader estimates do not establish a runtime target failure.

### E-2 — skip; low
- **File / line:** `plan.yaml:150,289`; `BRIEF.md:15`.
- **Summary:** root `test` may launch each of the four offline projects separately.
- **Concrete cost:** reader estimates 4–10 seconds of startup/config overhead per full gate [INFERENCE].
- **Alternative:** retain per-kind commands but run one all-project Vitest invocation for root `test`.
- **Skip reason:** the full T-01 text expressly defines the cumulative gate as chaining the four suites; distinct kind execution and zero-selection behavior are deliberate. No measured unnecessary work or observed budget failure exists. Do not pin a runner optimization before proving equivalent per-project failures.

### E-3 — skip; low
- **File / line:** `plan.yaml:150,271,285,289`.
- **Summary:** the reader could not see the truncated gate definition/probe-startup policy and hypothesized a second Next compilation.
- **Concrete cost:** a hypothetical dev compile or duplicate build could add tens of seconds against the under-60-second target [INFERENCE].
- **Alternative:** have the terminal offline probe use the preceding `.next` output via `next start`; concurrently run typecheck/lint ahead of sequential build/probe.
- **Skip reason:** an unobserved duplicate compilation is not established waste. Full T-01 text defines suites/typecheck/lint/build/smoke chaining; T-08 requires a real bounded local process but leaves its startup implementation open. Prescribing concurrency or build reuse now risks breaking T-08's standalone task gate before any predecessor build exists. Preserve the cost target and actual timing receipt, not speculative extra configuration.
- **Reader question resolved:** dev-ops Q-1 is not forwarded as an operator question. The raw plan does not select `next start` versus dev for the independent offline probe; this is a reversible implementation choice constrained by T-08's standalone verify and T-09's measured terminal gate, not missing operator information.

## ALTITUDE

### F-1 — flag-only; low; briefing-row
- **File / line:** `plan.yaml:267,273`; compare `205–209` and Kaya `docs/ARCHITECTURE.md:69,76`.
- **Summary:** `schema:apply` is a mutating setup mode in the e2e probe rather than a separately housed repository-maintenance command.
- **Concrete cost:** [INFERENCE] future migrations might treat this bootstrap-specific executor as a general migration contract or extend the probe instead of resolving issue #8; mutating setup and verifying modes share one file.
- **Alternative (reader):** add a briefing row describing the setup command's placement as provisional, keep migration execution under #8, and require a `scripts/**` lane before any later relocation; do not restructure now.
- **Lead assessment:** retain only the narrow briefing clarification: this feature delivers complete, project-confirmed Mastra bootstrap, not a general migration-execution contract for #8. Do not label required platform behavior unfinished/provisional, add a runner, relocate files or expand lane grants. This is a documentation/evidence-limit note for pm, not architecture work in this pass.
- **Disposition:** briefing-row.

### F-2 — duplicate of R-2; flag-only; low; fold-in
- **File / line:** `plan.yaml:225–226,177,240,271–273,307,114`.
- **Summary:** model/resource/schema/pool/connection settings recur without a named authority for every value.
- **Concrete cost:** reader alleges a changed value could leave tests/probe/docs behind and surface at T-09 or in operator instructions [INFERENCE].
- **Alternative:** name T-05's storage/agent authorities; consumers reference them, tests retain independent expected values where required, docs derive the shipped values.
- **Lead assessment:** merge with R-2; no second action. Narrow the allegation: pool numeric bounds are explicit in T-05 but not independently repeated numerically in all cited consumers. D-01 remains the connection authority; do not give T-05 permission to override it or let failed model compatibility authorize substitution. Preserve independent contract tests.
- **Disposition:** fold-in.

### Checked and left — no additional findings
- **leave:** static T-04 SQL inspection versus T-08 hosted catalog/Data API/UAT evidence are distinct; accepted evidence limit is explicit.
- **leave:** Vitest/Harness selection descriptions have matching/single-selection obligations (supports skipping R-4/S-5, without asserting those future gates have run).
- **leave:** D-02's localhost-token residual is explicit and future account authorization remains issue #2.

## Routing and limits

Pm receives only R-1, merged R-2/F-2, S-1, E-1 and F-1 as advisory candidates. All original reports and skip reasons are retained above. No changes were applied, no amendments issued, no assertion weakened, no SC or settled decision reopened. No operator question remains. PASS certifies this four-reader flag-only pass, not plan signature, implementation correctness, live UAT, timings or ship readiness.
