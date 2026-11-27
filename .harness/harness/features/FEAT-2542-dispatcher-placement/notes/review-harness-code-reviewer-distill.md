# Plan-scope reviewer distillation

**Both candidates accepted.** One craft replacement and one repository addition are recorded in the shared receipt. No plan or diff reviewed; no suite run. No open questions.

**Caps before judgment:** Craft Patterns 15/15, Gotchas 15/15, and Outcomes 10/10 were full; Open was 0/5. No repository section was full.

| Candidate | Judgment and applied op | Batch ID |
| --- | --- | --- |
| CR1 | **Accepted — craft `replace Patterns/P-14`.** The cause matrix in the scope read did not cover the shape of a successful result; validation caught the null success row falling back to the declared feature. P-08 traces sources and scope; P-07 compares predicates after refactoring. Neither requires an inventory of success-field shapes at plan time. That check is more broadly useful than the guarded-import exception-ownership rule displaced at the cap. | `49b600e921a2cf60555efc2b734a981232d410b8377e0e4570d443bc8e26e314` |
| CR2 | **Accepted — Harness `add Gotchas/G-12`.** `inflight_registry.py:34,339` defaults an omitted key to `LEGACY_FEATURE` (`"legacy"`) but returns explicit null, empty, and non-string values as stored. Reviewers should expect the omitted case to pass the feature-validity check, not confuse it with a malformed value. The cited falsy normalization (`:870`) belongs to `release_cmd`; the entry makes no writer claim. | `5d5e7b7df3c85c3eec1590c0df4d4c10fcd9af4a237747113f7e7428381bb975` |

**Tool counts (before → after):**

| Tier | Patterns (15) | Gotchas (15) | Outcomes (10) | Open (5) |
| --- | ---: | ---: | ---: | ---: |
| Craft | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |
| Harness | 3 → 3 | 11 → 12 | 0 → 0 | 0 → 0 |

Both updates passed the tool's Expertise checks, including the repository 40-line limit. Both batch operations appear in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/expertise-receipt-9dd9fecf8b6d1646b0dda8bdc3e4d3a7056360cf91abf5cca9790a33c16bfaab.json`.

**No additional entry.** The signature re-read confirmed the fail-first and final-pin fixes. Craft P-06 already addresses per-branch baseline discrimination; P-03/P-04 cover moved-pin evidence and rerunning after the last mutation. Sources: `review-harness-code-reviewer-plan-c1.md`, `runs/plan-product/{digest,panel-c1}.md`, and `answers-2026-11-26-{signoff,validate-c0}.md`.
