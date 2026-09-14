# BRIEF — BUG-285-canonical-reader Canonical artifact readers

## Problem

Harness maintainers currently choose a parser at each data-read site, so the same artifact can be accepted, rejected, or silently treated as empty depending on its caller. This is latent for valid files but dangerous on the sanctioned hand-edit path: current `feature.json` readers use both strict JSON and permissive YAML, bare `plan.yaml` reads bypass schema validation, independent frontmatter parsers can disagree, and several gate paths suppress parse failures instead of reporting them.

## Done when — by perspective

**operator** — I can rely on the migration preserving every gate's observable violation set while eliminating parser-dependent and silent-default answers for the in-scope Python readers. No brittle shell scanner or heredoc parser is introduced to claim coverage of code the checker cannot parse reliably.

**code maintainer** — I can find every artifact reader in one dependency-light accessor module, use one typed failure contract per accessor, and make no parser choice at a call site. An AST guard prevents a new raw parse from landing, names the offending site and the accessor to use, and derives its work list from the current checkout rather than a frozen count.

**reader (reviewer / qa)** — I can grade parsing-semantic changes separately from import-and-name relocations, with fail-first evidence for the guard and accessor edge cases. The narrow #285 inverse fixture is visible in central reader coverage rather than attached to one caller.

## Success criteria

- SC-01 (code maintainer): An AST-based check over every `.py` source in `.claude/skills/harness/bin/` identifies genuine parse calls without matching docstrings or comments, classifies every current call by artifact or payload category, disposition, canonical remedy, and assigned migration task in one checked-in hand-classification artifact, reports each unresolved site with its canonical remedy, demonstrates a non-empty failing result before migration, and reports zero unresolved in-scope sites afterward; a second `state.yaml` reader is reported while the current sole reader is allowed. The artifact's complete file-and-symbol set must match the live AST result before migration begins; any newly discovered or unmatched site blocks execution until the plan's owning task scope and targeted verification are explicitly amended.
  verify: automated        evidence: integration
- SC-02 (code maintainer): One dependency-light artifact accessor module above `harness_yaml.py` owns `load_feature_json`, `load_harness_json`, `load_plan`, `load_fleet`, `manifest_domains`, `load_frontmatter`, `load_omp_config`, `read_hook_payload`, and `parse_gh_json`, and its module contract docstring is the authoritative complete read/write-route table, including the existing `write_feature_json`, a canonical `write_harness_json`, `plan-merge.py` verbs, `sync-agent-adapters.py`, the sole `state.yaml` reader trip-wire, and main-session-owned files. Automated checks prove every public function's ownership and behavior, every classified source/read/write route, and the AST guard's exhaustive enforcement without exporting the prose table as runtime API or asserting its wording.
  verify: automated        evidence: integration
- SC-03 (code maintainer): File accessors select parsing by extension, read inside their error boundary, reject duplicate mapping keys, convert malformed content, unreadable files, and non-UTF-8 bytes to the accessor's one documented error type, and retain `load_plan` schema validation and `load_fleet` validation without duplicating low-level YAML logic.
  verify: automated        evidence: unit
- SC-04 (operator): Every dispatchable in-scope Python bypass and existing correct-reader call site assigned by the complete hand-classification artifact uses the accessor module without changing its documented return, diagnostic, exit-code, mutation, or absence behavior, and `harness.json` writes use the canonical writer without weakening their atomic replacement behavior. A site absent from that artifact is not an undeclared edit: it requires an explicit plan amendment before migration.
  verify: automated        evidence: unit
- SC-05 (operator): Every DEC-174 gate, validator, hook, and its test that is changed by the Python cutover is updated main-session-direct; each gate's complete violation output set is captured before and after and is byte-identical, including the pre-existing `check-plan-routes.py` cases changed mechanically in the final zero-drift task, while newly added audit cases are accounted for separately and current silent broad-exception parse defaults are removed rather than moved behind the accessor.
  verify: automated        evidence: integration
- SC-06 (reader): Semantic bypass cutovers and mechanical relocations are presented as distinct diffs and receive distinct review findings, so a reviewer can inspect changed parsing and error behavior without relocation noise.
  verify: inspection
- SC-07 (reader): Central `load_feature_json` tests are shown failing before implementation and passing afterward for valid JSON, duplicate keys, unreadable and non-UTF-8 input, and a comment-bearing document that permissive YAML accepts but JSON rejects; this subsumes issue #285's caller-specific inverse fixture.
  verify: automated        evidence: unit
- SC-08 (operator): Raw parse sites inside `.sh` files are unchanged, excluded explicitly by the AST check, and remain blocked on #1674 rather than being covered by a token-aware scan, a bespoke heredoc extractor, or an unverified exemption count.
  verify: inspection

## Verification gaps

- none; the changed Python library and gate surfaces are covered by the active unit and integration runners.

## Constraints

- Issue #1594 and both operator-ruling comments are the live intent; issue #285 and its supersession comment are source context subsumed by SC-07.
- DEC-174 BLOCKS team execution for hooks, validators, gate scripts, and each gate's test. It SUPPLIES the dispatchable library/main-session-direct cutover seam and requires byte-identical pre/post gate violation sets.
- DEC-171 SUPPLIES `harness_yaml.py` as the required strict low-level YAML primitive. The accessor layer imports it; parsing logic is not copied.
- DEC-89 SUPPLIES the sanctioned hand-edit path that makes strict extension-based reads an observable contract rather than a hypothetical hardening.
- The accessor module must not add eager network, subprocess, or other heavy imports to hook paths. If a current dependency cannot cross that boundary safely, the implementation records the narrow exception instead of hiding a startup regression.
- The checked-in T-01 hand-classification artifact is the complete execution input for every migration task and its targeted verification. Task file lists record the current known assignment, not permission to absorb drift: if live AST output differs, execution stops until `plan.yaml` is explicitly amended and returned for approval.
- The checker and migration cover `.py` sources only. Existing `.sh` parse sites are neither migrated nor claimed as checked before #1674.

## Out of scope

- Raw parse sites in `.sh` files, including Python embedded in heredocs, until #1674 converts them into AST-readable `.py` modules.
- A token-aware shell scan or a maintained shell/heredoc parser; both were rejected as brittle technical debt.
- Adding a canonical `state.yaml` accessor while it has one reader and an enforced write route; the guard instead trips if a second reader appears.
- Changing gate policy, messages, exit codes, violation membership, or the semantics of already-canonical callers beyond the parser/error normalization required by the live ruling.
