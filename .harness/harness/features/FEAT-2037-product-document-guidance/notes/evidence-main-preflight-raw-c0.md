# Raw live preflight excerpts — main observation

This is a bounded, explicitly instructed preflight, **not UAT or an unprimed behavior grade**. Main independently parsed the actual persisted JSONL records, rather than adopting a child assertion. Raw root: `/tmp/harness-2037-build-preflight/2026-10-05T04-21-40-001Z_01a10a4b-c421-7000-b585-6ba82fabc0b3/`. The command-output artifact lost middle bytes; these persisted raw files remain available.

## Actual injected shared guidance
Every following record is `type: custom_message`, `customType: skill-prompt`, `details.name: harness-principles`, `attribution: agent`. Its actual `details.path` is `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-principles/SKILL.md`, and its injected content contains **Consult the assigned product, not Harness**.

| Persona | Raw relative JSONL | Line | Record id | Injection time UTC |
|---|---|---:|---|---|
| orchestrator | SuccessfulCougar.jsonl | 9 | 1501e6c2 | 2026-10-05T04:23:14.964Z |
| product lead | SuccessfulCougar/SuccessfulCougar.ProudWildebeest.jsonl | 7 | 6918e57d | 2026-10-05T04:26:14.047Z |
| pm | SuccessfulCougar/SuccessfulCougar.ProudWildebeest/SuccessfulCougar.ProudWildebeest.CurrentWombat.jsonl | 7 | d1d4ecbc | 2026-10-05T04:26:47.562Z |
| eng lead | SuccessfulCougar/SuccessfulCougar.QuietSwordfish.jsonl | 7 | 6a26096b | 2026-10-05T04:26:14.048Z |
| dev-ops | SuccessfulCougar/SuccessfulCougar.QuietSwordfish/SuccessfulCougar.QuietSwordfish.ProvincialFlea.jsonl | 8 | 50245f6c | 2026-10-05T04:27:39.327Z |

These are source-labelled injection records, not a grep of production files or a phrase inserted in a dispatch. They establish delivery to these five personas, not all sixteen exercised at runtime.

## Actual PM read attempts before its terminal answer
In the PM raw JSONL above:

- Line 19 at 04:26:57.277Z: `read(path="/Users/molchairuangutai/GitHub/harness/docs/spec.md:1-100")`; matching call result line 21 at 04:26:57.309Z: `Path '/Users/molchairuangutai/GitHub/harness/docs/spec.md' not found`.
- Line 22 at 04:27:00.125Z: `read(path="/Users/molchairuangutai/GitHub/harness/docs/decisions.md:1-100")`; matching result line 24 at 04:27:00.159Z: `Path '/Users/molchairuangutai/GitHub/harness/docs/decisions.md' not found`.
- Line 25 at 04:27:03.161Z: `read(path="/Users/molchairuangutai/GitHub/harness/docs/architecture.md:1-100")`; matching result line 27 at 04:27:03.195Z: `Path '/Users/molchairuangutai/GitHub/harness/docs/architecture.md' not found`.
- Terminal typed `yield` is line 31 at 04:27:40.188Z, after all three reads. The accepted product digest reports unknown empty-return, separator and component answers tied to those exact missing PRODUCT paths, not CONTROL substitutes. Its real nested prompt is retained in `runs/preflight-product/digest.md` lines 23–49.

## Limits retained
The preflight explicitly instructed reads and gap reporting, so it cannot establish independent uptake of the new policy or satisfy the approved conduct assertions. It created no PRODUCT fixture or CONTROL decoy. Cross-squad batching and the engineering lead's refused binding are recorded in `notes/preflight-main-live-delivery.md`; the engineering result is not an accepted return. Subsequent owner baseline synchronization and successful integration were independently executed by main and recorded in `notes/verification-main-c0.md`, not inferred from the preflight.
