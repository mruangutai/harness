# QA distill at close — harness-qa — FEAT-2488-plan-merge-atomicity

**BLUF:** 4 craft replaces and 1 repository add were applied. Two lead candidates (1 and 2) were accepted, split into three rules. From my own log, two items were accepted and the rest rejected. All craft sections were at their caps, so each new rule displaced a weaker entry or sharpened an existing one. No suite was run and no diff was reviewed (distill mission).

## Batches
- Craft: `ea6bdcfb32d704ab6582b2258b364de967a3c26b789d1fb82648bc73b8aa8d00`. Counts before → after: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 1→1. The first attempt was refused with exit 14 because P-07 ran to 51 words; it was trimmed and re-applied. Nothing was written by the refused attempt.
- Repository `harness`: `76aafb9111d574416f2aec64aa6f949d3e587dd643807a04392ee3108f13c270`. Counts before → after: Gotchas 13→14, Patterns 0→0, Outcomes 0→0, Open 0→0.
- Receipt: `notes/expertise-receipt-ebe6f5ba1a0fe949c181da36a97fc5c710e4b81f0d8ab356af82d093d54f8b83.json`

## Candidate dispositions
| Candidate | Disposition |
|---|---|
| 1. Probe one boundary beyond the contract before saying "closed" | **Applied** as craft P-11. It displaces the old P-11 (whole-file `grep -q`), which P-02 and G-05 already cover. |
| 2a. Fixture state window | **Applied** as craft G-09. It displaces the old G-09 (use the exact enum token), because validate-digest now enforces exact tokens. |
| 2b. CI env parity | **Applied** as craft G-11. It replaces the old G-11 (inherited project-root env vars) with one env-parity rule that covers the old rule's case. |
| 3a. Run the whole kind, not the task's hand-picked verify list | **Rejected.** Craft G-04 already says this. |
| 3b. Prove the env strip is load-bearing (PYTHONUNBUFFERED) | **Rejected** as a separate rule. It is an instance of G-03 (set the bypass env var explicitly) plus P-09 (neuter the effect to check discrimination). The env angle is also partly covered by the new G-11. |
| 3c. In-memory mutant drivers vs source copies | **Split.** The general lesson was applied as a sharpened craft P-07: in-process old-blob loading misses subprocess cases that re-import from disk. The repo-specific route was applied as repository G-14: the PLAN_MERGE_BIN / CHECK_DOMAIN_BIN overrides, whose env names I confirmed at `tests/integration/test-plan-merge.py:37` and `check_domain_support.py:32`. Repository G-06 already holds the in-memory monkeypatch technique. |
| Other log items | **Rejected.** `_PROBE` and `_load_owner` patching is a recipe. The lstat mutant survival and the `_journal_names` fail-closed behaviour are product facts that belong to backlog or review. The D2 probe-only gap is a feature-specific coverage gap. The exec-shim pickling item with its sha256 fallback is niche, and O-03 covers fail-first grading. |

## Open questions
None.
