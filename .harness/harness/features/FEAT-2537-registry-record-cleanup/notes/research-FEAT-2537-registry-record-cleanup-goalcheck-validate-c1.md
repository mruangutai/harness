# Goal-check — FEAT-2537 validate cycle 1 (run r-20261125-2-validate-validator)

Pin `8ae96bea9dd8eb0f412c654158cbb3050322cfff`, base `a24eacee718898c4512379de1fe87b9611a7df43`. I read everything at the pin (`git show`/`git grep <pin>`). I ran no suite.

**BLUF.** Both perspectives are delivered on the evidence I could collect at the pin. The two inspection SCs (SC-03, SC-04) are **met**, and all three DEC amend rows are **met**. The two automated SCs (SC-01, SC-02) are **partial**, for one reason only: their test-run clauses ("the whole file passes", qa's base-red demonstration, the case-25 mutant, the base-module swap) are qa's evidence, and no qa DIGEST exists at this pin yet. Every inspection-reachable clause of both SCs holds. One genuine behaviour delta falls outside the signer's three ruled deltas (F-1, low). It needs an operator acknowledgement, not a code change.

## Perspectives

| Perspective | Verdict | Carried by | Evidence at the pin |
|---|---|---|---|
| operator | pass — the ledger half is met, and the behaviour-class half waits only on qa's SC-02 run | SC-02, SC-03 | Ledger: all three old clauses are absent and their successors are present (below). Behaviour: case 18 asserts both v1 inputs in both directions, with a per-state control for each of the five writer-producible states (`tests/integration/test-inflight-registry.py#case_18_v1_registry_fails_closed`). The builder's red receipt (`notes/t01-red-receipt.md`) shows 5 v1-direction FAILs and 20/20 controls green on the unmodified module. |
| code maintainer | pass — all inspection clauses are met, and the test-run clauses wait on qa | SC-01, SC-04 | `live_children` is deleted. No persona-axis selector remains, the cases are re-driven onto production call shapes, the hook comments are true, and the frozen records are byte-identical. |

## SC rows

- **SC-01 — partial.** The met clauses:
  - `git grep -n live_children 8ae96bea -- .claude/skills/harness/bin .omp/extensions` exits 1.
  - The positive control `parent_agent_id=agent_id` matches once in `validate-digest.py`.
  - The base tree matches `inflight_registry.py` (the old `def live_children`), so the absence check discriminates.
  - Cases 2b and 2c and their `CASES` entries are gone.
  - Case 25 binds through `claim_with_receipt` and `attach_runtime_identity` (it asserts `True`), then asserts through exact-parent `live_claims` that it returns `["BackendChild"]`, that OtherLead gets `[]`, and that the stranded child gets `[]`.
  - Case 29 re-drives through `live_claim(root, "harness-qa", ...)`, expecting `(None, 1)`.

  Owed by qa: the whole-file pass at the pin, and case 25 red under a stranded-stays-live mutant. The main session's 183/183 is not evidence. 183 = 191 − 10 (the 2b/2c checks) + 2 (case 25's new checks), so the count is consistent with the receipt.
- **SC-02 — partial.** Case 18 matches the clause. Each of the 2 v1 inputs (the persona map and `{}`) gets 4 assertions: a strict `UnreadableRegistry`, the writer returning `(None, 0)`, the "treating as empty" warning, and an empty v2 file left on disk. Each of the 5 controls gets 4 assertions: the strict outcome, the file after the strict read, the writer outcome, and the file after the writer. The receipt shows the required red/green split against the unmodified module, but it was the builder's run before the commit, not qa's `INFLIGHT_REGISTRY_DIR` swap at the pin. Owed by qa: that swap run, and the candidate all-green.
  - Form note (low): the controls compare `json.loads` of the file, not raw bytes. This is adequate here because `_update_registry` serialisation is unchanged between base and pin.
- **SC-03 — met (inspection).** Each part checked at the pin:
  - **Old clauses gone.** Under whitespace- and backtick-normalisation, all three old clauses are absent from `git show 8ae96bea:.harness/harness/docs/DECISIONS.md`.
  - **Successors present.** Each successor is present in place:
    - DEC-199, in the paragraph "The refusal keeps no state" (pinned line 6038).
    - DEC-204 (pinned line 6615).
    - DEC-218, in the enumeration sentence (pinned line 7263).
  - **No amendment paragraph.** The diff is 5 lines removed and 7 added, all inside the three existing paragraphs.
  - **Index.** `gen-decisions-index.py --stdout` equals the pinned `DECISIONS-INDEX.md` (diff exit 0). The working-tree `DECISIONS.md` and the generator equal the pin.
  - **Ordering.** d1777a89 touches only the two ledger files, and the only commit touching `inflight_registry.py` is 8764b820, its child. The ledger is unchanged after d1777a89.
  - **Immutables.** `git diff --stat a24eacee 8ae96bea` on the fixture, `test-validate-digest.py`, `canonical-reader-classification.json` and `validate-digest.py` is empty.
- **SC-04 — met (inspection).** Each clause checked at the pin:
  - **agent_start comment.** It matches the code: `if (!currentAgent || runGate.state === "ready") return;` means a `held` run falls through to `openRun`.
  - **Lifecycle comment.** It matches omp 19.1.1 `utils/event-bus.ts`. `emit` calls `handler(data)` without awaiting it. `safeHandler` catches the error and calls `logger.error`, so the bus reports a failure but does not await it.
  - **Named barriers exist.** The `pi.on("tool_result"` release awaits `releaseClaims`, and `validate-digest.py` has `_settle_in`/`_settle_claim`.
  - **Comment-only diff.** All 6 changed lines are `//` comments.

## Decision dispositions (amend rows)

All three are verified at the pin. No old clause remains, and no amendment paragraph was added (DEC-205).

| DEC | Verdict | Evidence |
|---|---|---|
| DEC-199 | met | Pinned line 6038 holds "through the exact-parent strict read `live_claims(root, None, parent_agent_id=...)`, which writes nothing". This is D-02. |
| DEC-204 | met | Pinned line 6615 holds "Only version 2 is read or written: a strict reader refuses a version-1 persona-keyed object, or any other non-v2 object, as unreadable …". This is D-01. |
| DEC-218 | met | Pinned line 7263 holds "single-flight admission, the held-child read (exact-parent `live_claims`), and reconciliation counts". This is D-02. |

## Findings

- **F-1 (substance, low, T-01): a behaviour delta beyond the three ruled ones.**
  - **The shape.** A non-v2 dict that carries a `claims` list under a foreign `schema_version`, for example `{"schema_version": 1, "claims": [<live omp claim>]}`.
  - **Before.** The base writer migrated the shape and kept the live claim: `live_claim` returned `c1` and the claim was rewritten into v2 on disk.
  - **After.** The pin writer folds it to empty with a warning: the result is `(None, 0)` and `{"claims": [], "schema_version": 2}` on disk. The live claim is dropped. Strict readers refuse the shape on both sides.
  - **How measured.** A probe against `git archive` copies of both modules.
  - **Failure scenario.** A forward or foreign-version registry holding a live child is silently-but-audibly emptied by the next locked write. The parent's held-child refusal then reads no claim.
  - **Proportionality.** No writer produces the shape, so the operator's writer-producible class is intact. D-01's signed text ("any other non-v2 object … folded to empty with a warning") covers it. However, the signoff ruled only `{}`, the malformed-v2 warning ("on-disk bytes unchanged") and the v1 expired flip, and it says any other delta stops for a ruling.
  - **Route.** An operator acknowledgement that D-01's class includes it. No code change is implied.

## Principles applied

- P-16 (harness-pm Expertise): I graded the signed D-01 and signoff prose against measured writer behaviour, which surfaced F-1.
- P-05 (harness-pm Expertise): SC-01 and SC-02 are graded partial on missing qa evidence alone, without inventing a product defect.
