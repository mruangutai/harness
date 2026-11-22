# Inventory — FEAT-2340 — read-only scout Inv2340 at e239d881, 2026-11-22 (copied verbatim by harness-orchestrator from agent://Inv2340/report)

## Scope and notation
All bin paths below are relative to `.claude/skills/harness/bin/` (B). Every `file:line` in the tables uses that prefix. Inventory includes top-level Python and both Python subpackages. R counts module-scope `re.compile` declarations, not function-local compilation or imported pattern references. A counts flag-alias declarations. D counts distinct overlapping **path-concept families**, keyed below, not a claim that the regex languages are identical. S is a reproducible short-name candidate inventory: uppercase module assignments with 1–4 characters after removing a leading underscore; these are naming-review candidates, not automatically defects. check-domain's additional semantic candidates are called out separately.

## 1. check-domain.py: flag alias and every occurrence
`_I = re.IGNORECASE` at B/check-domain.py:1477 is the only regex-flag alias found across bin Python sources.

Eight executable uses (seven shape declarations plus the cycle matcher):
- RE_FEATURE_JSON:1478
- RE_STATE_YAML:1485
- RE_HANDOFF:1486-1487 (argument on :1487)
- RE_STATE_MD:1488
- RE_CLAUDE_MD:1491
- RE_RUN_DIGEST:1493
- RE_PLAN_YAML:1494
- _RE_HANDOFF_CYCLE:2296

There is also one explanatory comment occurrence at :1505. Thus **10 lexical occurrences = declaration + 8 uses + comment**. All eight uses supply IGNORECASE; no current handoff flag mismatch exists (:1486-1487,:2296).

## 2. check-domain.py: every module-scope compiled regex, grouped by concept
Patterns below are literal regex text, not Python string repr. Unless specified, flags are none.

| Concept | Name and B/check-domain.py line | Pattern | Flags / overlap |
|---|---|---|---|
| Observations log | _OBSERVATIONS_LOG_RE:919 | `^\.harness/[^/]+/features/[^/]+/observations/[^/]+\.md$` | none |
| plan.yaml | _PLAN_YAML_ROUTE_RE:951 | `^(\.harness/[^/]+/features/[^/]+)/plan\.yaml$` | none; overlaps next row |
| plan.yaml | RE_PLAN_YAML:1494 | `^\.harness/[^/]+/features/[^/]+/plan\.yaml$` | IGNORECASE; same basic path, capture/flags differ |
| Feature identifier (not a path) | _FEATURE_ID_RE:999 | `(?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+` | none |
| Immediate feature artifact | _FEATURE_DIR_RE:1000 | `^(\.harness/[^/]+/features/([^/]+))/[^/]+$` | none; structural superset of feature.json, STATE.md and plan.yaml routes |
| feature.json | RE_FEATURE_JSON:1478 | `^\.harness/[^/]+/features/[^/]+/feature\.json$` | IGNORECASE |
| Run state.yaml | RE_STATE_YAML:1485 | `^\.harness/[^/]+/features/[^/]+/runs/[^/]+/state\.yaml$` | IGNORECASE; intentional boundary respelling |
| Handoff note | RE_HANDOFF:1486-1487 | `^\.harness/[^/]+/features/[^/]+/notes/handoff-[a-z0-9-]+\.md$` | IGNORECASE; includes cycle-suffixed notes |
| Cycle-suffixed handoff note | _RE_HANDOFF_CYCLE:2296 | `^.*/(notes/handoff-[a-z0-9-]+?)-c[0-9]+\.md$` | IGNORECASE; overlap with RE_HANDOFF; broader directory prefix, captures canonical stem |
| STATE.md | RE_STATE_MD:1488 | `^\.harness/[^/]+/features/[^/]+/STATE\.md$` | IGNORECASE |
| Root CLAUDE.md | RE_CLAUDE_MD:1491 | `^CLAUDE\.md$` | IGNORECASE |
| Run digest | RE_RUN_DIGEST:1493 | `^\.harness/[^/]+/features/[^/]+/runs/[^/]+/digest\.md$` | IGNORECASE; intentional boundary respelling |
| Run identity import-failure sentinel | RE_RUN_IDENTITY:1501 | `(?!x)x` | none; deliberately matches nothing |

Normal RE_RUN_IDENTITY is **imported**, not locally compiled: B/check-domain.py:1495-1501. Its owner composes `^\.harness/[^/]+/features/[^/]+/runs/[^/]+/` + `re.escape(_RUN_IDENTITY_MARKER)` + `$`, IGNORECASE, at B/harness_boundary.py:50-54; marker imported from run_identity at :26.

The known handoff pair is at **:1486**, not approximately :1462 in this checkout. Preserve identical case-fold behavior, but do not treat their whole patterns as identical except for the suffix: prefix anchoring and capture groups differ (:1486-1487,:2296). The cycle matcher is used at :2313; canonical output is lowercased at :2316.

Function-local compilation excluded from the module inventory: B/check-domain.py:1979 (schema-derived evidence-name pattern); corresponding check-state logic is B/check_state/run_state.py:106-115.

## 3. Deliberate respellings and exact tests
- **Keep RE_STATE_YAML and RE_RUN_DIGEST locally spelled**, rather than importing from harness_boundary. Shape-phase import must remain absorbing so the main session can repair a broken boundary module: B/check-domain.py:1479-1485,:1492-1501. Boundary originals: B/harness_boundary.py:46-49.
- The actual asserting test is `run_bug1106_shared_pattern_consistency`, **tests/integration/test-check-domain-artifact.py:575-613**. Literal extraction :584-601; digest equality :607-608; state equality :612-613. These compare literal pattern text, **not flags**. They also locate declarations using spacing-sensitive marker strings (:598-601); reformatting assignment spacing can break this source-text test.
- The nearby production comment says `test-check-domain.py`, but the assertions now live in `test-check-domain-artifact.py` (B/check-domain.py:1483-1484 versus test location above).
- Run identity is a separate intentional fallback, not a second real matcher: B/check-domain.py:1495-1501.

## 4. check-domain.py: naming candidates
- `_I`:1477 — cryptic single-letter spelling of IGNORECASE; eight uses listed above.
- `VERB`:1467 — actually the mode-dependent refusal/budget diagnostic label; consumed at :1587. A domain-specific name would expose its purpose.
- `STAMP`:1365 — sweep-stamp relative path, consumed at :2703; short but not a flag alias.
- `SWEEP_WINDOW_S`:1354 — unit abbreviation; used at :2710,:2716. Lower-priority than `_I`, since `S` conveys seconds in a named window.
`RE_`, `ID`, `JSON`, `YAML`, `MD` in the explicit artifact names are conventional format/domain vocabulary, not equivalent to the opaque `_I` alias (declarations :999-1000,:1478-1501).

## 5. Remaining bin/: per-file counts (non-zero only)
A=0 for every row; bin's sole A=1 is check-domain.py:1477 above. D keys refer to the fully cited cross-file groups in the next section. A dash means zero.

| B-relative file and regex declaration lines | R | D | S count: names and lines |
|---|---:|---|---|
| amendment_contract.py:19 | 1 | — | 1: KEYS:16 |
| bash-write-guard.py:302,308,612 | 3 | — | 0 |
| board-station.py:59 | 0 | — | 1: HERE:59 |
| board_lifecycle.py:1256 | 1 | — | 1: _TOOL:267 |
| branch-create-gate.py:47,149 | 0 | — | 2: GATE:47, GH:149 |
| check-decision-anchors.py:46,56 | 2 | — | 0 |
| check-expertise.py:77-90 | 6 | 1 E | 1: CAPS:60 |
| check-fixture-secrets.py:44-45 | 2 | — | 0 |
| check-instruction-paths.py:25-31 | 5 | 2 F,E | 1: HERE:8 |
| check-integration-shards.py:82-83 | 2 | — | 2: ROOT:62, KIND:81 |
| check-omp-port.py:53-54 | 2 | — | 0 |
| check-plan-routes.py:44,59,61-66,2000-2001 | 8 | — | 0 |
| check-skill-refs.py:61-68 | 6 | — | 0 |
| check_state/brief.py:21,23,80-81,207-210 | 8 | — | 0 |
| check_state/ctx.py:56-57 | 2 | — | 0 |
| check_state/feature_record.py:494,496 | 2 | — | 0 |
| check_state/plan.py:67,70 | 2 | — | 0 |
| check_state/runner.py:6,38 | 2 | 1 F | 0 |
| digest_record.py:26 | 1 | — | 0 |
| dispatch-guard.py:255,278,519,748 | 4 | — | 0 |
| expertise-merge.py:67-68,471,710-716 | 10 | 1 E | 1: CAPS:63 |
| factory_claim.py:42 | 1 | — | 1: TOOL:38 |
| factory_decompose.py:173 | 1 | 1 J | 1: TOOL:57 |
| factory_land.py:28 | 0 | — | 1: TOOL:28 |
| feature-record.py:660-664 | 3 | — | 1: _HERE:739 |
| feature-worktree.py:55 | 1 | — | 0 |
| feature_corpus.py:39-40,312 | 3 | 1 F | 2: _BIN:31, PIN:49 |
| feature_json_write.py:41-43 | 1 | 1 J | 1: _WHAT:45 |
| feature_schema.py:251,491 | 2 | — | 0 |
| gen-craft-index.py:36 | 1 | — | 1: END:29 |
| gen-decisions-index.py:28-29,81,86 | 4 | — | 0 |
| gh-close-gate.py:49,57-59 | 4 | — | 3: GATE:45, OPS:48, ROOT:221 |
| gh-sync.py:133 | 0 | — | 1: GH:133 |
| handoff_done_when.py:14-19,24-25 | 8 | 1 F | 0 |
| harness_boundary.py:46-54,74,400,463,724,1381 | 8 | 6 F,J,Y,E,S,G | 0 |
| harness_yaml.py:326-327,381-382 | 4 | — | 0 |
| inject-expertise.py:45-47 | 3 | — | 0 |
| layout_fixtures.py:29 | 0 | — | 1: STUB:29 |
| merge-gate.py:92 | 1 | 1 E | 3: ROOT:68, BIN:91, OPS:97 |
| observations-merge.py:49-54 | 2 | 1 O | 0 |
| panel_findings.py:27 | 1 | — | 0 |
| plan-merge.py:156 | 0 | — | 1: _FILE:156 |
| plan-sign-gate.py:125,139 | 2 | — | 7: GATE:71, VERB:73, TOOL:74, OPS:82, SEP:87, RAW:101, ROOT:397 |
| plan_anchors.py:37 | 1 | — | 0 |
| plan_merge/approval.py:356-358,482 | 4 | — | 0 |
| plan_merge/check.py:200,207-208 | 3 | — | 0 |
| plan_merge/guards.py:23-25 | 1 | 1 Y | 0 |
| plan_merge/stations.py:29,187,190 | 3 | — | 0 |
| plan_merge/text.py:8,11,218,221,264 | 5 | — | 0 |
| prune-run-evidence.py:64 | 1 | — | 0 |
| run-unit-tests.py:59 | 0 | — | 1: ROOT:59 |
| validate-digest.py:590-593,709,1143-1148,1941-1943,2495 | 12 | 2 F,G | 2: SEV:41, RANK:1836 |
| worktree-state.py:46,56 | 0 | — | 2: _BIN:46, SELF:56 |

S is intentionally broader than 'bad alias': ROOT/HERE/BIN and GATE/TOOL often have clear local meaning. Stronger review targets include SEV (severity list), OPS (shell operators), SEP (CLI separator), RAW (compiled raw-command matcher mapping), _WHAT (destination-description text), PIN (population selection label), and domain's _I; their definitions are anchored in the table. Do not mechanically rename every short name.

Module-scope boundary fallback in check-domain.py is included above; function-local `re.compile` at B/harness_boundary.py:788, B/plan-sign-gate.py:97, B/plan_merge/approval.py:87, B/check_state/run_state.py:115 and B/check-domain.py:1979 are excluded from R. In particular, check_state/run_state.py has no module-level compiled-regex finding.

### Cross-file overlapping path concepts (D)
These groups supply **both/all sites**, not merely counts:
- **F — feature tree/artifact prefix:** B/check-domain.py:1000; B/harness_boundary.py:400; B/feature_corpus.py:40,:312; B/check_state/runner.py:38; B/check-instruction-paths.py:26,:29; B/handoff_done_when.py:14; B/validate-digest.py:709. They differ in accepted depth, captures, identifier strictness and optional repository tier.
- **J — feature.json destination:** B/check-domain.py:1478; B/feature_json_write.py:41-43; B/factory_decompose.py:173 (basename-only, deliberately broader); B/harness_boundary.py:463-464 (union with plan.yaml).
- **Y — plan.yaml destination:** B/check-domain.py:951,:1494; B/plan_merge/guards.py:23-25; B/harness_boundary.py:463-464.
- **O — observation note:** B/check-domain.py:919 versus B/observations-merge.py:49-52; the writer restricts basenames to `harness-[a-z0-9-]+.md`, while the route guard accepts any Markdown basename.
- **E — expertise path/tier:** B/check-expertise.py:88,:90; B/check-instruction-paths.py:30; B/expertise-merge.py:470-471,:716; B/merge-gate.py:92; B/harness_boundary.py:724. Prefix detection, full destination checks and persona-capturing variants overlap but are not interchangeable.
- **S — run state.yaml:** B/check-domain.py:1485 and B/harness_boundary.py:48-49; intentional identical pattern-text exception, both IGNORECASE.
- **G — run digest:** B/check-domain.py:1493; B/harness_boundary.py:46-47 (intentional identical pair, IGNORECASE); B/validate-digest.py:1942-1943 (absolute/root-capturing durable-run variant, no explicit flags).

### Additional reuse findings outside path concepts
Useful T-02 scope candidates, **not counted as D**:
- Identical strict feature-slug regex: B/check-domain.py:999 and B/dispatch-guard.py:255. Another identical, looser identifier pair: B/feature-worktree.py:55 and B/feature_corpus.py:39; the latter explicitly cites the former at :37-38.
- Identical distill-run token regex: B/feature-record.py:664, B/dispatch-guard.py:748, B/validate-digest.py:1941. Validate/fix token recognition overlaps B/feature-record.py:660-661 with B/prune-run-evidence.py:64.
- Identical shell assignment prefix: B/bash-write-guard.py:308 and B/harness_yaml.py:327.
- Identical perspective-heading pattern text: B/check_state/brief.py:21 and B/handoff_done_when.py:24; flags intentionally differ (MULTILINE|IGNORECASE versus IGNORECASE) because search scope differs (:29 versus handoff_done_when.py:212).
- Identical expertise section regex: B/check-expertise.py:77 and B/expertise-merge.py:67; entry variants differ at :78 versus :68.
- Identical persona matcher: B/expertise-merge.py:710 and B/inject-expertise.py:45. Segment matchers overlap but differ in first-character constraint (:711 versus inject-expertise.py:47).
- DEC identifier matching overlaps B/check-skill-refs.py:61, B/harness_yaml.py:381-382 and B/gen-decisions-index.py:29; anchoring/capture/boundary differences need preservation.

## 6. Tests relevant to pattern changes
All files matching `test-check-domain*.py` are currently integration files:
- tests/integration/test-check-domain.py:22,171,208,300 — state.yaml write routes/schema behavior.
- tests/integration/test-check-domain-artifact.py:108,183,369,575-613 — digest/state routes and intentional literal equality checks.
- tests/integration/test-check-domain-post.py:68,153-165,491,619,909-949 — post shape routes, handoff grammar, canonical/cycle names and Write/Edit parity. Cycle case variants include `Build-c1`, `build-C1`, `VALIDATE-C12` at :919-921; canonical-output case assertions :925-931.
- tests/integration/test-check-domain-approval.py:277-318,481-496 — plan casing/non-plan lookalikes and feature/handoff/STATE mixed-case routing.
- tests/integration/test-check-domain-grant.py:215-241,375-392 — state-shape behavior with/without grants.
- tests/integration/test-check-domain-worktree.py:253-296,328-346 — STATE.md/feature.json shape routing in worktrees.
- tests/integration/test-check-domain-claims.py:474 — case-insensitive path ownership context, not direct compiled-pattern equality coverage.
- tests/integration/test-check-domain-worktree-parity.py:1 — additional route-parity suite; not a pattern-literal test.

There are no `tests/unit/test-check-domain*.py` matches. Related unit coverage: tests/unit/test-handoff-done-when.py:62,147,280,419 (handoff authority/parser); tests/unit/test-harness-boundary.py:436,1018-1048 (shared boundary and hook integration); tests/unit/test-artifact-accessors.py:185 (shared step-contract use); tests/unit/omp-hooks.test.ts:139-158,979-1003 (hook path/post dispatch, not regex literal identity).

## 7. Simplify angles and guidance placement
- **REUSE**, .agents/skills/harness-simplify/references/angle-reuse.md:13: **“On a code surface: a constant, helper or fixture restated where an importable one exists.”** Its required evidence/cost is :15-16: “Name the existing thing by file and line, and name the concrete cost — usually that two spellings must now be edited in lockstep, and the one nobody remembers goes stale silently.” This is the current duplicated-helper/matcher angle (the word 'matcher' itself is not in the prompt).
- **SIMPLIFICATION**, .agents/skills/harness-simplify/references/angle-simplification.md:11-13: “On a plan surface: the same fact asserted twice through different spellings, one rule restated in two places that can drift apart …”. Its code-surface prompt at :15-18 concerns redundant conjuncts, change-narrating comments and simpler pipelines, explicitly preserving anchoring semantics. It does **not** currently explicitly ask for duplicated helpers/matchers.
- Best craft home: **`# Model the Domain`**, .agents/skills/harness-craft/references/model-the-domain.md:7; existing naming sentence at :13: **“Name the structure in the domain's own vocabulary”**. Domain ownership/repeated-shape context at :9-11,:20-25 fits one matcher per concept plus explicit bootstrap exceptions.
- Best design home: **`## Reader load — the two axes`**, .agents/skills/harness-codebase-design/SKILL.md:47-55; current text says **“name an invariant once at the seam”** (:52-53) and asks whether a new reader can locate a value's origin/change surface in 30 seconds (:53-55). Explicit meaningful constant names fit here.
- Supporting existing guidance: **`# Delete First`**, .agents/skills/harness-craft/references/delete-first.md:7, especially **“Sweat the small leaks”** at :18 (“… duplicated choices …”); **`## Glossary`**, .agents/skills/harness-codebase-design/SKILL.md:14-24 defines Leverage/Locality as one implementation across callers/tests and concentrated maintenance.

## T-02 reach recommendation [INFERENCE]
Start with _I and the two same-file concept overlaps; preserve handoff case semantics and deliberate state/digest/bootstrap exceptions. The cross-file groups above establish a real wider inventory, but consolidation must preserve each consumer's anchoring, captures, flags and accepted tree layouts—not indiscriminately replace all path recognition with one permissive matcher. Existing literal-equality tests and mixed-case/cycle regressions are the first checks the implementing/main agent should run.