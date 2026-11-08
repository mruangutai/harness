# BUG-2181 · T-01 · Security review c0

**PASS — no actionable introduced security findings.** Static review of `5f935b55..5d78ffc3ccf4d1c49aae47b9183a2c305c0be6a7`; no live GitHub calls, tests, builds, lint or formatters executed.

## Scope and boundaries

In scope: the new absent-card mutation crosses local configured project/issue identity → authenticated GitHub project membership. Reviewed all eight changed paths: production mutation and provisioning guidance are security-relevant; three test paths exercise that boundary using fakes; feature.json, plan.yaml and build evidence change lifecycle records, not authorization. Complete diff credential sweep found no credential material. Prior security-review history is not established by this review.

- **Injection / tampering:** `gh_board.py:387-397` looks up first, adds only on None, forwards the configured owner/number and fixed-origin `https://github.com/{repo}/issues/{issue_number}`, then writes the returned item ID. `factory_gh.py:271-276,146-153` builds list-form argv without a shell. Project number normalization is existing (`factory_config.py:145-160`); the URL is a flag value with a fixed HTTPS prefix, not a command or positional option. No issue title/body enters this new call.
- **Authorization / disclosure:** the new call uses the same gh binary, environment and GitHub credential boundary as existing project writes (`factory_gh.py:93-96,178-195`). No credential forwarding, token URL, new identity source or independent authorization bypass is introduced. An actor editing operator configuration already controls existing project-write destinations; this is not a newly acquired capability.
- **Errors / logging:** lookup/add/set GhError remains BoardError (`gh_board.py:396-397`), preserving caller stderr handling (`board-station.py:180-184`, `gh-sync.py:168-172`). Existing gh errors may include the first stderr/stdout line (`factory_gh.py:187-193`); optional cost logging records argv (`gh_cost_log.py:121-145`). This adds project/issue identifiers to those established paths, not secrets or issue contents.
- **Pre-existing distinction:** lookup matches project number rather than project owner (`factory_gh.py:1024-1026`); the unchanged field-write path already consumes that result. The new addition itself explicitly uses configured owner and number. No demonstrated cross-user privilege gain warrants a finding.

## Acceptance pointer

SC-03: pinned diff, `.claude/skills/harness/references/repo-board-provisioning.md:39-42`, adds the Auto-add-is-not-required paragraph; unchanged lines 31-37 retain Item closed, Auto-close issue and Pull request merged as registration requirements. SC-01/SC-02 execution evidence remains QA's responsibility; build evidence was read, not independently executed.

Findings: none. Must fix: none. Open questions: none. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` remain unavailable; the approved BRIEF and settled intake supply the bounded contract.
