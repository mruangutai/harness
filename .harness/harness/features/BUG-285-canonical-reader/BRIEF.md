# BRIEF — BUG-285-canonical-reader Canonical artifact readers

## Problem

Harness maintainers currently choose a parser at each data-read site, so the same artifact can be accepted, rejected, or silently treated as empty depending on its caller. This is latent for valid files but dangerous on the sanctioned hand-edit path: current `feature.json` readers use both strict JSON and permissive YAML, bare `plan.yaml` reads bypass schema validation, independent frontmatter parsers can disagree, and several enforcement paths suppress parse failures instead of reporting them.

## Done when — by perspective

**operator** — I can rely on every in-scope reader giving the same observable answer at every consumer, while each hook, gate, and validator retains its established violation set, diagnostics, and exit behavior.

**code maintainer** — I can find every in-scope artifact reader in one dependency-light module, use one documented failure contract per accessor, and make no parser choice at a call site. All Python entrypoints are visible to one AST guard that names any bypass and the canonical remedy.

**reader (reviewer / qa)** — I can grade parsing-semantic changes separately from import-and-name relocations, with fail-first evidence for the guard and new accessor edge cases. The already-landed issue 285 inverse fixture remains visible in central reader coverage and is not represented as new work.

## Success criteria

- SC-01 (code maintainer): An AST-based check parses every Python source under `.claude/skills/harness/bin/`, inspects genuine `Call` nodes without matching comments, docstrings, or string-contained helper programs, and emits a deterministic hand-classification row for every current raw parse or existing artifact-reader call. Each row records file, enclosing symbol, parse category, artifact or payload, disposition, canonical remedy, assigned migration task or justified exemption, and DEC-174 route. Its live inventory explicitly includes the parse-bearing Python entrypoints made visible by PR 1688, including `bash-write-guard.py`, `branch-create-gate.py`, `check-domain.py`, `check-state.py`, `dispatch-guard.py`, `inject-expertise.py`, `post-merge-sweep.py`, and the converted Python gate files. The complete live AST result and checked-in classification must agree before migration; the check is demonstrated non-empty and failing before migration, reports every unresolved site with its remedy, reports zero unresolved sites afterward, and reports a synthetic second `state.yaml` reader while allowing the current sole reader.
  verify: automated        evidence: integration
- SC-02 (code maintainer): One dependency-light artifact accessor module above `harness_yaml.py` owns `load_feature_json`, `load_harness_json`, `load_plan`, `load_fleet`, `manifest_domains`, `load_frontmatter`, `load_omp_config`, `read_hook_payload`, and `parse_gh_json`. Its module contract names the sanctioned write or source routes, including `write_feature_json`, a canonical `write_harness_json`, `plan-merge.py` verbs, `sync-agent-adapters.py`, main-session-owned files, and the sole `state.yaml` reader trip-wire; the prose is maintainer guidance rather than a tested runtime API. Automated checks prove each public reader or writer behavior and the AST guard proves coverage of the live parse surface.
  verify: automated        evidence: integration
- SC-03 (code maintainer): File accessors select parsing by extension, read inside their error boundary, reject duplicate mapping keys and the non-standard JSON constants `NaN`, `Infinity`, and `-Infinity`, convert malformed content, unreadable files, and non-UTF-8 bytes to the accessor's documented error type, and retain `load_plan` schema validation and `load_fleet` validation without duplicating low-level YAML logic. At each real `feature.json` consumer, a present `github` or `factory` nested field with the wrong type is observably refused rather than treated as absent; consumer-level evidence proves wrong-typed parent and issue records cannot trigger duplicate GitHub parent or task issue creation.
  verify: automated        evidence: integration
- SC-04 (operator): Every dispatchable in-scope Python bypass and existing correct-reader call identified by the complete hand-classification artifact uses the canonical accessor module without changing its documented return, diagnostic, exit-code, mutation, or absence behavior, and `harness.json` writes use the canonical writer without weakening atomic replacement. A live site absent from the signed classification requires a plan amendment before migration.
  verify: automated        evidence: unit
- SC-05 (operator): Every hook, gate, validator, and its test changed by the migration is updated main-session-direct under DEC-174 by category. This includes the enforcement files converted to Python by PR 1688. Each enforcement surface's complete normalized violation output is captured before and after and is byte-identical; newly added audit cases are kept separate, and existing silent broad-exception parse defaults are removed rather than moved behind an accessor.
  verify: automated        evidence: integration
- SC-06 (reader): Semantic bypass cutovers and mechanical relocations are presented as distinct diffs and receive distinct review findings, so parsing and error-contract changes can be inspected without relocation noise.
  verify: inspection
- SC-07 (reader): The central coverage already landed at `tests/unit/test-feature-json-reader.py`, including issue 285's comment-bearing document that permissive YAML accepts but JSON rejects, remains green and is extended rather than rebuilt. New issue 1682 cases for non-standard JSON constants and wrong-typed nested parent or issue fields are demonstrated failing before implementation and passing afterward through the central accessor and observable consumers.
  verify: automated        evidence: unit

## Verification gaps

- none; the changed Python library and enforcement surfaces are covered by the active unit and integration runners.

## Constraints

- `source_issues: [285, 1594]` records provenance. Issue 1594 and its operator rulings are the live intent; issue 285 is closed by the narrower reader fix already on current main, and issue 1682 remains a hardening requirement inside SC-03 rather than a source issue.
- The authoritative planning base is `8e3bda037bf62e89966d898ccfdf8c9cabcdcdea`. PR 1688 closed issue 1674 and made every former shell entrypoint Python and AST-visible; the inventory and migration cover that current surface without a frozen count.
- DEC-174 BLOCKS team execution for hooks, validators, gate scripts, and each gate's test. It SUPPLIES the dispatchable-library versus main-session-direct seam and requires byte-identical pre/post enforcement output.
- DEC-171 SUPPLIES `harness_yaml.py` as the strict low-level YAML primitive. The accessor layer imports it; parsing logic is not copied.
- DEC-89 SUPPLIES the sanctioned hand-edit path that makes strict extension-based reads observable rather than hypothetical.
- The accessor module must not add eager network, subprocess, or other heavy imports to hook paths.
- The checked-in T-01 hand-classification artifact is the complete execution input for each migration task. If live AST output differs, execution stops until `plan.yaml` is amended and returned for approval.

## Out of scope

- A token-aware source scan or maintained heredoc/string-program parser; Python's AST is the enforcement mechanism.
- Adding a canonical `state.yaml` accessor while it has one reader and an enforced write route; the guard trips if a second reader appears.
- Changing gate policy, messages, exit codes, violation membership, or the semantics of already-canonical callers beyond the parser and error normalization required by SC-03.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-14
