# Code review c1 — PASS

No actionable findings for T-01 or T-02. Spec compliance passed before quality review. Reviewed pinned objects, not main-checkout source: `e239d88156c508c948d49cd31238ea13b3b39865..125a04f847db18bcc2ead0b9003a6b2826f9cd55`; merge-base(origin/main, pin) equals that baseline.

## Stage 1 — specification

- **SC-01 / T-01:** `.claude/skills/harness-simplify/references/angle-reuse.md:14` asks the second-matcher question; `.claude/skills/harness-simplify/references/angle-simplification.md:19` asks the alias question while retaining the anchoring warning. `.claude/skills/harness-craft/references/model-the-domain.md:13-20` is the single home for all three naming bullets and bootstrap exception; frontmatter unchanged. Planned `.agents/skills` paths resolve through its pinned `../.claude/skills` symlink.
- **SC-02 / T-02:** `.claude/skills/harness/bin/check-domain.py:1493-1494,2317-2323` preserves the handoff route language and terminal-cycle refusal. Compared with baseline `:1486-1487,2296,2311-2317`, non-greedy phase plus optional cycle backtracks to consume the terminal suffix: `handoff-x-c1-c2.md` canonicalizes to `notes/handoff-x-c1.md`; `handoff-X-C1-C2.md` produces the same lowercase name. Unsuffixed phases return no cycle problem; refusal text is identical. The removed helper's broader prefix was unreachable through its sole production caller, already selected by the full feature-notes route.
- **SC-02 / T-02:** `.claude/skills/harness/bin/check-domain.py:956-957,963-966,1501` shares one plan pattern text with named feature_dir and preserves flag asymmetry. Legacy conversion at `:1196` still precedes shape plan refusal at `:2537-2541,2561-2562`: mixed-case `Plan.yaml` beside `PLAN.md` skips the case-sensitive legacy matcher; lowercase conversion retains the earlier legacy diagnostic.
- **SC-02 / T-02:** `.claude/skills/harness/bin/check-domain.py:1490,1500` preserves protected literal bytes, single-physical-line declaration layout and aligned assignment spacing, replacing only trailing flags. Absolute offsets move from baseline `:1485/:1493`; the source extractor at `tests/integration/test-check-domain-artifact.py:586-613` depends on declaration layout, not numeric offsets. `_I` and all eight uses, the duplicate cycle matcher, and live VERB are removed. The diagnostic rename preserves both messages; the stale comment is corrected at `:1488`. `_FEATURE_ID_RE` at `:1005` equals `dispatch-guard.py:255`; `_FEATURE_DIR_RE`, STAMP, SWEEP_WINDOW_S, protected literals and RE_RUN_IDENTITY including fallback are otherwise unchanged.
- **SC-04 / T-01,T-02:** `.claude/skills/harness-simplify/references/angle-reuse.md:14`, `.claude/skills/harness-simplify/references/angle-simplification.md:19`, `.claude/skills/harness-craft/references/model-the-domain.md:16`, and `.claude/skills/harness/bin/check-domain.py:956` anchor the four production paths in the complete baseline-to-pin diff. Commit `df6ae1cc` lands only the three guidance files before `ffe320f5` refactors the gate. No tests, fixture, extra implementation document, imports, lint or cross-file consolidation changed; remaining paths are feature records/evidence. No build amendments supplied.
- **SC-03:** baseline/post receipts record rc=0 in 11s/10s; QA owns integration execution and full output adjudication. Existing tests bind real hook behavior (`test-check-domain-post.py:909-948`, `test-check-domain-approval.py:304-320`) and literal presence/equality (`test-check-domain-artifact.py:603-613`), not multi-cycle or diagnostic ordering. No invented fail-first obligation applies to this semantics-preserving regression criterion.

## Stage 2 — quality

No new fail-open path, silent failure, duplicate matcher, shim or speculative seam found. Main's supplementary, uncommitted `notes/code-grade-e239d881-125a04f8.md` records pinned-range diff-mode rc=0, no gated records, and path-mode grades on the exact pinned blob c6824c8a73f465054e966fca63b5043301fc6880: legacy_plan_conversion_guard **4** (cyclomatic 6, cognitive 5, ABC 13.9), _head **5** (1, 0, 0.0), _handoff_cycle_problems **5** (3, 3, 6.0). Code grade pass; no grade-2 reasons.

Only dirty tracked paths observed were this feature's STATE.md and feature.json. Human commit in scope: `b3c32171` (signature), reviewed without inherited clearance. This reader executed no builds, tests, linters, formatters or grading and edited no source.

## Principles applied

- Model the Domain — checked named phase/cycle variants and meaningful diagnostic naming without introducing an abstraction.
- Delete First — checked removal of the obsolete matcher rather than retaining a compatibility layer.

Open questions: none. Must fix: none.
