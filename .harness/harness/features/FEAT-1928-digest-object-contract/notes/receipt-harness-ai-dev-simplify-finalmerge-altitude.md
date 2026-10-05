# Receipt — altitude, final merge (harness-ai-dev, read-only, task:none)

BLUF: no altitude finding requires action. Three observations, all `leave`.

## Findings

1. `.omp/extensions/harness-hooks.ts:1013-1023` vs `:1079-1098` — identity/feature/pin/mission extraction runs in two places: `before_agent_start` reads `event.systemPrompt`, and `adoptPersistedRun` reads `session_init.systemPrompt`.
   Cost: about 6 duplicated lines, so a new marker has to be added twice.
   Alternative: a shared `adoptMarkers(systemPrompt)`.
   Reason to hold: the two sites take different inputs. The cold path also calls `captureDispatchFromMessage` on `init.task`, and it never touches `digestBinding`. `openRun` still resets `digestBinding` and `featureRootCache` (`:995-997`) for both paths, so the lifetimes stay separate. The cold path adds no assistant-text or YAML fallback. **leave**

2. `tests/integration/canonical-reader-classification.json` — the file-level `plan` is `BUG-285-canonical-reader` (`:2`). Rows owned by this feature carry `FEAT-1928.../plan.yaml` plus T-01 (`:456`, `:575`, `:589`, `:1250`). Exempt rows keep `task: none`.
   Cost: two plan authorities in one file.
   Reason to hold: this is the approved retained per-row ownership metadata. Collapsing it would reopen the settled decision. **leave**

3. `.claude/skills/harness/references/distillation.md:25-29` — the sequential product/validator PM rule (#2033) is stated once, here. A grep for `sequential` found nothing elsewhere in this file, so there is no duplicate statement to drift. I read `DECISIONS-INDEX.md` lines 36-234. DEC-227 (`:222`, spend) and DEC-237 (`:231`, object returns) match the merged authority. I found no internal inconsistency. **leave**

## Not read
I did not read `DECISIONS.md` in full, `feature-record.py`, `prune-run-evidence.py`, the tests, or `tests.yml`. I executed nothing.

## Principles applied
None cited; I read no craft leaf.
