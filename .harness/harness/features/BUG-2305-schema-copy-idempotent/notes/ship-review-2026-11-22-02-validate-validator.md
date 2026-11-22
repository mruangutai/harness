# Ship review — BUG-2305-schema-copy-idempotent

**Ready to ship.** The validate panel over review_sha `29791331` returned PASS with an empty must-fix list, severity_max `none`, 164/164 unit tests at the pin, and both signed perspectives graded met. No rework round was used (ruling: 1 round / 45 min; cycles 0 / 10). The merge is yours; nothing was pushed, no PR opened.

No report round was spawned. This briefing is assembled from disk: `runs/2026-11-22-01-patch-product/digest.md` (patch intake), `runs/2026-11-22-02-validate-validator/digest.md` (validate), the reader notes `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c1.md`, `notes/research-BUG-2305-schema-copy-idempotent-goalcheck-validate-c1.md`, and the main session's build records `notes/red-first-T-01.md` and `notes/simplify-pass.md`. The build itself was main-session-direct (DEC-174), so it has no lead digest.

## Definition of done, graded (validate goal-check, c1)

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator** — I can reuse an unchanged strict Harness dispatch without a false refusal, while attempts to replace or loosen the persona's contract remain visibly refused. | met | SC-01, SC-02 | `tests/unit/omp-hooks.test.ts:1743–1859` (16 personas, flat and tasks[] item, independent and key-reordered copies, every refusal variant, later invalid item); `.omp/extensions/harness-hooks.ts:379–427, 1474–1490`; qa `notes/review-harness-qa-c1.md:16,24–26,35–37` — 164/164 at pin, 5 base assertion failures reproduced |
| **code maintainer** — I have a regression covering every persona and both call shapes, without the obsolete workaround note or decision prose contradicting the behavior. | met | SC-03, SC-04 | note removal `tests/unit/omp-hooks.test.ts:1702–1723, 1862–1873`, red on base / green at pin (qa `:27–28,38`); DEC-237 amendment at pin `DECISIONS.md:7917–7928`, index `DECISIONS-INDEX.md:231–237`, live-yield and durable-record clauses unchanged (goalcheck note `:21`) |

## What shipped

One task, T-01, four files (`git diff --stat 7f9cc9d8 29791331`): `.omp/extensions/harness-hooks.ts` (+41/−), `tests/unit/omp-hooks.test.ts` (+145), `DECISIONS.md` (DEC-237 amended), `DECISIONS-INDEX.md` (regenerated). `schemaControlRefusal` now accepts only an unchanged strict copy of the target harness persona's own bundle, on a flat call or an individual tasks[] item, via `isDeepStrictEqual` (key-order-insensitive), then re-injects the canonical bundle and strict mode. Batch top level, non-harness targets, changed schemas, any non-strict mode and lone fields stay refused naming the location. `SCHEMA_INJECTION_NOTE` and its additionalContext are gone.

## Leads

- **Product (patch intake)** — PASS, `runs/2026-11-22-01-patch-product/digest.md`: BRIEF with four SCs and a one-task plan, T-01 main-session-direct; flagged that the coupled index regeneration needed explicit authorization — granted at signature (Q-01, `notes/answers-2026-11-22-signoff.md`).
- **Build (main-session-direct, no lead)** — `notes/red-first-T-01.md`: 5 assertion failures against base 7f9cc9d8 with the hook untouched, then 164/164. `notes/simplify-pass.md`: four angles, no findings. Typecheck did not run — `harness.json` `typecheck.cmd` is null (#2257, disclosed in BRIEF).
- **Validator** — PASS, `runs/2026-11-22-02-validate-validator/digest.md`: qa, code, security, ui (self-scoped out, no visual surface) and pm goal-check all PASS; qa independently reran the literal T-01 verify at the pin and reproduced the five base reds; no finding above advisory. The lead notes qa's attribution of the Bun-file discovery gap to #2257 was not adopted (that issue covers typecheck).

## Open questions and escalations

None. No question reached `awaiting_user`; no escalations were recorded.

## Spend and ledger

`feature-record.py spend`: 2 runs, 17 wall-clock minutes, 101,912 tokens, rework 0 rounds / 8 min inside the 1 round / 45 min ruling. Cycles 0 / 10. Judgements: 1 (`mission: patch`). `max_total_runs` not exceeded.

## Amendments (DEC-229/DEC-230)

| at | decision | reason | overruled |
|---|---|---|---|
| — | — | the build amended nothing | — |

overrule rate: 0/0

## UAT

Not required (BRIEF `## Verification gaps`: no UAT; OMP host persistence is supplied evidence and outside this patch).

## Proposed backlog

Residual findings that survived collation but do not gate. Strike by ID; unstruck rows become issues on ship acceptance (DEC-138).

| ID | Nature | Finding | Source |
|---|---|---|---|
| B-1 | chore | `run-unit-tests.py` does not discover or execute Bun test files such as `tests/unit/omp-hooks.test.ts`; the hook regression is proven only by T-01's literal `bun test` verify, not by the configured unit runner. Distinct from #2257 (typecheck). | qa `notes/review-harness-qa-c1.md:16`; validator digest adequacy_notes |
| B-2 | enhancement | SC-02 refusal tests are green on the pre-fix hook by construction (it refused everything), so their discrimination against an over-permissive hook is unshown; a mutant run (accept any strict, or JSON-string equality) would close that. | qa `notes/review-harness-qa-c1.md:32`; digest coverage_gaps |
| B-3 | enhancement | The base fail-first loop stops at the first persona and the reordered-key red is not isolated; sixteen independently observed base reds were not demonstrated (all arms pass at pin). | qa advisories; digest coverage_gaps |
| B-4 | chore | Operators' live sessions keep the pre-fix hook until the merge lands; dispatches copying injected schema fields remain refused until then (observed in this run: the hook still injected and the note still fired on the validate dispatch). | this run's dispatch |

## Next

Your call: **ship** (merge `feat/BUG-2305-schema-copy-idempotent` at `29791331`+bookkeeping), fix, re-scope, or stop.
