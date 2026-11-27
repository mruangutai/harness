# Census: per-file analysis state across the three split files — FEAT-2489 — 2026-11-24

Scout E2_PerFileCensus, read-only, at pin 25132b7e. Requested by the main session after ESC-2 so the class can be ruled once.

## Summary
No additional finding/exit/stderr change on the current clean tree was found. The real clean-tree observable changes are the Python-file census (101→103), candidate locators/line metadata, and inventory relocations. The census below distinguishes genuinely seam-sensitive rules from per-file implementation caches and checker-only rules that this particular split cannot affect. Existing QA evidence confirms alias-map counterexamples in both exit-code directions.

## Architecture
Both audit libraries are eagerly imported by the entry. Canonical auditing separately parses every bin/ Python file and compares file-qualified reader candidates against a repository-wide inventory. Structure auditing shares one invocation-local _AuditSession, but indexes each physical source independently; FEAT-61 and broad-catch rules scan all bin/ sources, while FEAT-62/69 symbol/read/authority rules target only check-state.py and check_state/*.py. There is no module-global source-index session.

## Report
# Exhaustive physical-source-file census

## Scope, evidence and notation

All code anchors below are relative to `.claude/skills/harness/bin/` in worktree W. E = `check-plan-routes.py`, C = `canonical_reader_audit.py`, S = `structure_audit.py`. Anchors are pin-side lines. “Current” means the actual split with its committed inventory/T07 updates, not an arbitrary additional plant. A clean-base counterexample is not evidence that the current tree is affected.

This was read-only source investigation: no checks were rerun. Measured examples below are attributed to the existing QA records. Other hypothetical examples are static deductions, marked [INFERENCE]. Inert mechanisms are explicitly identified: inventing a result-changing example for an observationally neutral cache would be incorrect.

**Bottom line for the current real tree:** no member below introduces a classification/consolidation finding, changes an audit exit, or adds stderr. QA’s unaffected-tree statement is consistent with the code and existing controls. It does not mean byte-identical output: the canonical summary changes **101→103 Python files**; returned candidate file/line metadata and two inventory identities also change. No universal equivalence claim over arbitrary perturbed trees is justified: QA measured canonical exits **2→0 and 0→2** through the alias map.

## A. Canonical reader analysis

### 1. Whole-file parse/read success is the admission boundary
- **C:199-204, 228-239.** One `ast.parse` covers the complete physical source; candidates are appended only after the complete parse/collection returns. OSError, UnicodeDecodeError or SyntaxError drops that file’s entire candidate set and adds one source_parse finding. `scanned` still includes the failed file.
- **Concrete seam:** syntax error in moved `_normalized_reader_name`; retained `_manifest_deviation` and `_load_plan_once` remain valid. Run a pristine same-revision auditor against the malformed target tree. QA measured base **7** classification findings versus pin **3**, exit **2/2**. Add an unclassified `json.loads` in retained `_clean`: pin additionally discovers it, while base’s whole-file failure hides it (base 7 versus pin 4 findings).
- **Accuracy:** pin is more precise about the readable portions; it stops falsely reporting retained rows absent and exposes otherwise masked candidates. Both remain unable to certify the malformed tree.
- **Current:** no; requires a source failure. Do not confuse this external-scanner experiment with executing the malformed entry itself (item 11).

### 2. File-wide, last-write-wins reader aliases
- **C:104-142, 199-204.** One alias dictionary spans all imports, imports-from, simple assignments and annotated assignments visited anywhere in the file, including function/class bodies. It is collected completely before any call is classified. It is neither lexical nor point-of-use Python binding analysis. Assignment resolution itself uses aliases accumulated so far; final call classification uses the final map.
- **Concrete seam, measured:** retained `_clean` contains `import math as json`. At base that final binding masks moved `_classification_document`’s `json.load`; base canonical exit **2**, pin **0**. The pin correctly isolates a function-local binding from a different module’s reader.
- **Reverse, measured:** retained `_clean` contains `import json as probe_json; probe_json.loads('{}')`; moved `_normalized_reader_name` contains later `import math as probe_json`. Base masks the unclassified reader and exits **0**; pin sees it and exits **2**. Pin is more accurate here too.
- **Other manifestations [INFERENCE]:** cross-seam alias chains stop resolving; a moved import can stop supplying a retained call’s classification; newly isolated assignment/import overwrites can restore or hide candidates. These are the same map mechanism, not independent caches.
- **Accuracy generally:** example-dependent. Smaller files reduce false cross-scope pollution, but this is still not lexical analysis; splitting can also remove an accidental mapping that happened to classify a call correctly.
- **Current:** no demonstrated alias-dependent finding change. QA’s measured plants are not present on the actual tree.

### 3. Candidate ordinal counters and source ordering
- **C:168-210.** `symbols`, `calls` and `ordinals` are fresh per source. Ordinal key is **(symbol, category)**, within that source—not one counter for the entire file and not repository-wide. Calls are numbered by `(line,column)`; IDs are `{file}::{symbol}::{category}#{ordinal}`. The returned candidate list itself remains visitor order; the sort assigns IDs without sorting that returned list.
- **Concrete seam [INFERENCE]:** one retained and one moved module-level `json.loads` are `<module>/json_string#1` and `#2` at base, but each is `#1` in its respective pin file. The same happens for repeated definitions sharing the identical qualified symbol string. Inventory matching can then differ if identities are not migrated correctly. Same exit/different findings, or clean→exit 2 for stale identities.
- **Important restriction:** moving distinct named functions intact does **not** reset one another’s counters: their symbol keys were already distinct. The actual `_classification_document` and `_task_files` retain their symbol/category `#1` suffixes.
- **Accuracy:** neutral physical identity convention, not semantic precision. Repeated-definition ordinals do not distinguish runtime liveness.
- **Current:** paths/line metadata change, but no ordinal-induced finding change; actual moved reader IDs are updated.

### 4. File-qualified candidate identity, live map and duplicate handling
- **C:242-254, 333-342, 450-460, 614-624, 673-687.** `live` is a repository-wide dictionary, but its key embeds the physical file. `_row_lookup` checks duplicate **full IDs across the whole document**, not duplicate symbols or calls per file. `live` has last-value dictionary semantics for duplicate candidate IDs; normal generation avoids duplicates by item 3.
- **Concrete seam [INFERENCE]:** move `_classification_document` but retain its old exempt row ID/file. Base is clean; pin gains an unaccounted candidate and a missing-row finding, exit **0→2**. This is identity migration, not newly introduced duplicate detection. Conversely, two distinct file-qualified rows are not duplicates merely because symbol/category/ordinal match.
- **Accuracy:** a stale inventory is correctly rejected. With correctly migrated identities, neutral.
- **Current:** no finding change; the moved IDs/files are updated at inventory lines **457-458, 470-471**.

### 5. Same-file/same-symbol remedy coverage
- **C:393-447, 450-460.** A canonical remedy candidate can account for a historical row with a different ID/category/ordinal, but must have the row’s **file and symbol**, unless an explicit relocation applies. There is no one-to-one consumption of candidates: one remedy can satisfy multiple rows in the same file/symbol.
- **Concrete seam [INFERENCE]:** two same-named top-level function definitions `f`, one containing a raw reader and one its canonical remedy, share the same file/symbol at base. A canonical row may be satisfied by the remedy despite the other definition. Put the two definitions on opposite sides of the split, preserving a row for the raw-reader file: the remedy in the other file no longer satisfies it. Base-clean/pin-fails is possible with an appropriately classified inventory. This requires repeated same-symbol code or stale relocation assumptions, not distinct intact functions.
- **Accuracy:** often more discriminating at pin, but repeated definitions and runtime reachability remain unmodeled. Ordinary stale-locator rejection is accurate.
- **Current:** no; actual unique-symbol reader moves have matching inventory updates.

### 6. Exempt/unmigrated same-site fallback aggregation
- **C:494-515.** If an exempt row’s exact ID is absent, it is accepted when **exactly one** candidate exists with the same file, symbol and category. Two such candidates do not qualify for this fallback. Ordinal changes can therefore be hidden or exposed by the file-local candidate count.
- **Concrete seam [INFERENCE]:** an exempt row uses stale `f/json_string#3`, while two live calls under repeated symbol `f` occupy #1/#2. Base reports absent row. Split the repeated-symbol definitions so the row’s file now has exactly one same-site candidate: pin accepts the fallback, potentially **2→0** when all other rows/manifests are valid. With ordinary exact IDs present this fallback is irrelevant.
- **Accuracy:** not uniformly better; accepting a stale ID based on uniqueness is heuristic and can associate the wrong call.
- **Current:** no; the moved exempt row uses its exact new `#1` identity.

### 7. Scanned-file manifest, traversal order, and summary
- **C:214-225, 228-239, 298-307, 462-469, 705-714, 770-783.** Sources are enumerated by sorted filenames at each os.walk level, with sorted descendant directories and `__pycache__` excluded. Candidate groups and scan-error order follow physical file traversal. The public classifier compares the scanned list **in exact order**; the task-specific path compares **sets**. Summary counts physical files, including files that failed parsing.
- **Concrete seam:** the split adds C and S, so the clean tree reports **101→103**. Leaving the old manifest produces a clean→exit 2 drift finding. Relocating two unclassified reader plants into different files can reorder their emitted findings because file grouping overrides their former shared source order [INFERENCE].
- **Accuracy:** new file count/manifest is correct; ordering is presentational. Exact-list versus set comparison is an existing API asymmetry.
- **Current:** **yes for summary and returned scanned list**, no for findings/exits because the manifest was updated. No finding-order difference can appear while both finding lists are empty.

### 8. Special filename normalization
- **C:145-165.** Only a file ending `/harness_yaml.py` treats bare `load_file` and `load_str` as `harness_yaml.*` primitives.
- **Concrete general seam [INFERENCE]:** move a bare `load_file` call out of harness_yaml.py with the helper imported under that bare name and without a resolvable import mapping: it can stop being a candidate, altering missing/unaccounted findings.
- **Accuracy:** heuristic, context-dependent.
- **Current/this E split:** **impossible through the specified move**: neither old E nor new C/S has the special suffix. No E↔C/S seam witness exists for this rule.

### 9. File-qualified T07 tables and remedy overrides
- **C:62-101, 380-390, 401-432, 557-624.** `T07_TERMINAL_REMEDIES` keys are full historical site IDs; `T07_RELOCATED_IMPLEMENTATIONS` stores explicit destination **file/symbol/category/callee** tuples. `_CLASSIFICATION_REMEDY_OVERRIDES` is also keyed by full ID. T07 duplicate counts are over exact IDs in the historical row subset, not independently per file.
- **Concrete seam [INFERENCE]:** move `_task_files` and its inventory row but leave the old T07 expected key: ordinary audit can be clean while `classification_task_findings(...,'T-07')` reports the old required row missing and the new one extra. Direction: base-clean/pin-fails for that API. A stale destination in a relocation tuple similarly turns a canonical row into missing/raw.
- **Actual handling:** the `_task_files` expected key is now **C:71**; retained `process_plan_yaml` remains E-qualified (**C:69, 97-98**) with destination `_load_plan_once`; no S-qualified T07 target exists. Other relocation destinations remain in their original modules. The sole remedy override concerns factory_config, not this seam.
- **Accuracy:** explicit ownership contract, neutral when maintained; stale tables are genuine inventory inconsistency.
- **Current:** no finding change; these updates are present.

### 10. Migration ownership is physical-file membership, not symbol ownership
- **C:277-296, 357-377, 717-745.** A row naming a `plan` is checked against that task’s expanded physical source paths. Globs are expanded in sorted order. A bare historical `task` without `plan` is provenance only (FEAT-71). `task_files` is grouped by plan and task, not a source-file analysis cache.
- **Concrete seam [INFERENCE]:** a plan-owned row moves to C while its task lists only E: base-clean/pin-fails with “task files omit this source,” even if ID, remedy and manifest were updated. Adding C to the owning task fixes the actual contract.
- **Accuracy:** pin correctly detects stale declared ownership.
- **Current:** no effect for the two moved historical rows: inventory lines **457-482** have no `plan`, so FEAT-71 deliberately performs no ownership check for them.

## B. Import/runtime source-module boundary

### 11. Compilation/import failure and stderr frames
- **E:39-45; S:13.** Both new libraries are imported eagerly before root resolution or mode dispatch, including ordinary route mode. Python compiles each source module separately.
- **Concrete seam, measured:** syntax error planted in moved `_normalized_reader_name`; execute each tree’s own entry. Base and pin both exit **1**, with empty stdout. Pin stderr adds the traceback header and E’s line-44 import frame (exactly four extra lines on QA’s Python 3.15), beyond the changed syntax-error file/line locator. A bad S module analogously fails at E:45 [INFERENCE].
- **Accuracy:** neither audit has run; this is failure provenance, not improved/worsened audit accuracy.
- **Current:** no, all modules import. Missing/unreadable new libraries would also introduce import-failure paths, but are not trees with only the valid split applied.

### 12. Python module namespaces and import cache
- **E:28-45; C:8-15, 18-101, 380-385; S:9-13, 38-48, 109-116, 307-342, 578-581, 771, 824-826.** Constants/functions now live in separate Python module dictionaries; ordinary global lookup resolves there. Python caches imported C/S modules, whereas executing E as a script does not make it the same object as an imported library.
- **Concrete extended seam [INFERENCE]:** a consumer mutates a broad-catch table on an E module object, expecting a previously co-resident audit function to use it. After migration that function uses S’s table instead. Similarly, cross-seam accidental global rebinding stops propagating. These require additional monkeypatches/callers or duplicate global definitions; they are not intrinsic findings of the unchanged current tree.
- **Accuracy:** interface/caller-dependent; not an audit judgment. No compatibility aliases should be assumed.
- **Current:** no such mutation was found in these three files. There is **no module-scope _AuditSession/_SourceIndex cache**. Policy tables are module globals, not per-audited-source mutable state. The sole module-global load cache is item 27 below and stays in E.

## C. Structure/consolidation source state

### 13. Per-file `_SourceIndex`: facts, parents, breadth-first order and lazy subtree membership
- **S:109-165.** Each parsed file gets `tree`, FIFO/BFS `nodes`, `parent`, node-kind `facts`, a per-node-type dispatch cache `_lists_of_type`, lazy `_members[(subject,kind)]`, and `program_texts`. These cover exactly that file, with subtree membership preserving AST breadth-first order.
- **Concrete seam [INFERENCE]:** valid code split into E/C/S yields three indexes rather than one. Index construction itself has **no independent result-changing witness**: rules use node/subtree facts and cannot ordinarily confuse nodes in distinct functions. Its observable effects are fully represented by per-file parsing, line dedup, function lookup, broad counts and ordering below.
- **Accuracy:** neutral indexing optimization; no additional rule/ceiling is hidden in the index.
- **Current:** allocation/traversal partition changes, not findings. It is incorrect to infer a new clean→dirty transition merely from creating more indexes.

### 14. `_AuditSession` text/index/error caches and census snapshot
- **S:167-219.** `_texts` and `_indexes` are keyed by normalized absolute path, not inode/realpath. Each stores a successful value or a cached `_SOURCE_ERRORS` exception (OSError, SyntaxError, ValueError); subsequent rule requests reuse/re-raise it. `_census` is one ordered path snapshot per invocation. `index`’s first supplied relative filename becomes the cached parse’s diagnostic filename. Sessions are fresh at public entry points (**S:902-905, 921-933**).
- **Concrete seam:** a moved malformed source is now one failed cache entry while retained E can be indexed; see item 15. For static valid files, splitting cache entries has **no independent result-changing witness**. Concurrent mutation between first requests could change snapshots [INFERENCE], but that is not a static source-tree counterexample and not a basis for claiming current impact.
- **Accuracy:** neutral optimization; smaller parse-failure domains improve confinement. Path normalization is not physical-inode deduplication.
- **Current:** no findings/exits change, no cross-invocation stale state.

### 15. Structure audit per-file failure suppression and repeated reporting
- **S:854-866, 892-900, 907-918, 927-947.** Consolidation skips all FEAT-61 rules for an unparseable file, while later broad census independently reports that file as unparseable. Shared cached errors are still converted into each rule’s own message. This is distinct from canonical candidate admission.
- **Concrete seam [INFERENCE]:** external pristine runner scans target containing a syntax error in moved code plus a retained station-literal violation in `_clean`. Base cannot run FEAT-61 over E and hides that literal; pin scans valid E and reports it. Broad-census parse findings persist. Same exit **1**, different finding set/count. Multiple malformed split files can produce more source_parse/census findings than one malformed monolith.
- **Accuracy:** pin more complete for parseable pieces, still fails closed.
- **Current:** no, requires malformed source. If executing that same malformed tree’s entry, item 11 happens before this scanner runs.

### 16. FEAT-61 station-table exemption is an entire-file exemption
- **S:38, 235-246, 927-945.** All station literal candidates in exactly `factory_config.py` are exempt from the lock, regardless of symbol.
- **General seam [INFERENCE]:** move a predicate returning `('plan','ready')` out of factory_config.py and it gains a finding; move it into that file and it loses one. Direction can be clean→fail or fail→clean.
- **Accuracy:** intentional location-based policy; not a global duplicate counter.
- **Current/this split:** no possible E↔C/S exemption crossing: all three are outside the exempt file. A station literal straddling this split is still prohibited on both sides.

### 17. Station-literal duplicate suppression and line sorting
- **S:222-246.** Finding dictionary is fresh per file and keyed only by **lineno**. Multiple candidate nodes on one line produce one finding; emitted findings are line-sorted. Wrapper Call/Tuple duplication is the intended case; distinct violations on one line are also collapsed, and first candidate wins the diagnostic text.
- **Concrete general seam [INFERENCE]:** two literal assignments on the same line in one module produce one finding; partition those statements into different modules and they produce two. Same exit **1**, different count/text. Changing which candidate appears first can change the named bucket.
- **Accuracy:** splitting distinct sites improves counting; wrapper dedup remains correct. But an intact function split does not separate same-line nodes.
- **Current/actual E function seam:** no triggering literal and no split within a source line. No extra finding or independently realizable same-line collision arises from moving intact top-level definitions here.

### 18. FEAT-61 module-loader home is file AND symbol
- **S:43-46, 254-265.** Every callee named `spec_from_file_location` is flagged except one exact `(harness_boundary.py, _load_repo_module)` pair. It is not “one allowance per file” and does not check aggregate uniqueness.
- **General seam [INFERENCE]:** move the home function unchanged to another file: base clean, pin finding. A second call within the allowed home function is not detected as “second” because both match the exemption.
- **Accuracy:** precise location policy but not a true global uniqueness proof.
- **Current/this split:** unaffected: E/C/S are all non-home files. A new call in moved code fails both, with locator change only.

### 19. Per-index enclosing-function lookup
- **S:268-276.** `_call_symbol` searches all indexed functions whose line interval encloses a node, selects the shortest interval, and otherwise uses `<module>`. This table includes nested/async functions but returns only the innermost **bare name**, not a qualified class/function path.
- **Concrete seam [INFERENCE]:** a violating loader/literal inside moved `_may_be_program` produces the same symbol under a new file/line locator. No independent changed finding count or exit exists for an intact function: valid unrelated functions’ source intervals do not overlap.
- **Accuracy:** neutral locator mapping; existing qualification limitations remain.
- **Current:** no findings to relabel; actual index/line coordinates change only.

### 20. FEAT-63/65 broad-catch count versus per-file ceiling
- **S:824-900.** Counts direct bare/`Exception` handlers and counts in qualifying embedded programs; compares the sum once per physical file against its bin-relative filename’s ceiling. Only `harness_boundary.py` has ceiling **2**; E/C/S each have **0**. One excess-file finding, not one finding per catch.
- **Concrete seam, measured:** add one broad catch in retained `_clean` and another in moved `_may_be_program`. Base: one finding, “E carries 2 ... ceiling 0”; pin: two findings, “E carries 1” and “S carries 1”; exits **1/1**.
- **Accuracy:** both identify all prohibited sites through aggregate counts. Pin gives finer file attribution, not a more permissive allowance.
- **Current:** no. For this exact split, broad-count conservation and all-zero ceilings prohibit either clean→fail or fail→clean by redistribution alone. Nonzero allowance stays with harness_boundary.py and cannot be borrowed by C/S or package siblings.

### 21. Embedded-program aggregation and cache
- **S:139, 214-219, 833-866.** Each qualifying string constant in a file contributes its parsed program’s catch count; aggregation belongs to the containing source file. Session `_programs` is keyed by exact string **text across all source files**, including cached None. Repeated identical constants are counted repeatedly despite shared parsing. Only one embedded level is analyzed.
- **Concrete seam:** broad catches embedded in strings in retained and moved functions reproduce item 20’s one-file→two-file findings [INFERENCE]. Moving an intact string does not alter its parsing or contribution. Identical strings on opposite sides are **not deduplicated** out of the count.
- **Accuracy:** neutral counting; parser cache is not an extra per-file state boundary. Splitting an embedded program string itself would be a code/content change, not this verbatim move.
- **Current:** no new count or finding. FEAT-65’s hook removals from the allowance table add no separate hidden file state.

## D. Checker-only physical-file rules: census present, but outside this split’s target surface

These rules live in moved S, but analyze **check-state.py and check_state/*.py**, not the files housing the rule implementations. Thus no E↔C/S seam-straddling witness exists for them unless extra checker-source edits are added. All are **Current: no change**.

### 22. Checker source selection, parse scope and order
- **S:307-315, 345-378, 907-918.** Entry first, then sorted direct `check_state/*.py` children; no recursive package scan here. Entry parse failure returns no trees and makes `_feat62_findings` return early, suppressing its other checks (including posture/broad census there); package parse failures drop only those module trees. Outer consolidation still has its own all-bin scan.
- **General seam [INFERENCE]:** malformed entry plus a package offense can suppress more than malformed package source; relocating checker code from entry to a package alters failure scope/order. Same failure exit, different findings. More confinement can improve diagnostics.
- **This split:** checker paths/content do not move, so none of these scopes changes.

### 23. Per-file trusted-bootstrap cutoff and top-level/invariant scope
- **S:381-388, 412-440, 445-475.** First top-level assignment to `root` sets the bootstrap cutoff for that file; everything up to that line is skipped. Top-level statement shape/read checks run independently per checker file. Reparse checks select only module-body synchronous functions matching `_INVARIANT_FN`; nested/async functions are not selected directly.
- **General seam [INFERENCE]:** a top-level `open(...)` before `root = ...` is exempt in one file, but moving it to a package file with no root assignment makes it a finding (clean→fail). A root assignment later in a package file can conversely exempt earlier statements. Function-preserving moves keep direct reparse detection, aside from locators.
- **Accuracy:** cutoff is trusted-bootstrap policy; relocating reads outside it is correctly stricter, but arbitrary root assignments can create misleading exemptions.
- **This split:** S’s own top-level constants/read helpers are not checked by this lock.

### 24. Per-file function/import tables and package cross-reference namespace
- **S:354-357, 468-522, 550-574, 662-672.** `_module_functions` maps top-level function names and direct class methods, with last definition winning; `_package_imports` maps top-level `from check_state.<module> import ...` aliases, last binding winning. `_PackageFunctions` combines these using basename module names, module-qualified function keys and special unqualified `Ctx.<method>` keys. Bare calls resolve same-module definitions before imports; only bare names and `ctx.method` are traversed. `_reachable` has a per-traversal set, not a per-file ceiling; row input unions are sorted/set-aggregated across reachable functions.
- **General seam [INFERENCE]:** move a helper to another checker file without a supported from-import: its undeclared input disappears from the row’s reachable set, potentially fail→clean (less accurate). Add the supported import and cross-file checking is preserved. Two same-named definitions in one file collapse; separating them into modules can restore visibility. Duplicate `Ctx` method keys in multiple files overwrite globally in tree iteration order, not per-file duplicate findings.
- **This split:** no helper in check_state moves; moving the implementation of `_PackageFunctions` itself does not change its analyzed namespace.

### 25. Table-local string aliases, Inv rows, family placement and authority
- **S:317-329, 525-547, 674-768.** `_string_constants` is a last-write-wins dictionary of literal top-level string assignments in one file. `_inv_rows` resolves reads aliases only through that dictionary. Only the first tree with basename `table` supplies audited Inv rows. Row run functions resolve from module `table`, and the defining module must equal `ROW_FAMILIES`’ expected family. Authority validation applies only to those rows. `_decisions_index` is a separately read document-wide DEC map, last matched entry wins; it is not a Python-source symbol table.
- **General seam [INFERENCE]:** moving an Inv call out of table.py makes it disappear from read/authority checks; moving a string alias without supported literal rebinding can yield invalid/None reads (and possibly an uncaught shape error); moving a run definition to the wrong checker family gains a placement finding. Directions depend on the move, not uniformly more accurate. Duplicate DEC entries are unrelated to the E/C/S source seam.
- **This split:** no table, run-family, alias or DEC document is relocated.

### 26. FEAT-62 posture per-file line scan
- **S:771-806.** Each direct workflow/hook file is read once; a finding requires both `check-state.py` and `--changed` on the same physical line. Files and directories are enumerated in stable order; unreadability produces one finding per file.
- **General seam [INFERENCE]:** moving text between physical lines/files can change matches, but it is already a same-line textual heuristic, not a shared-source aggregate or alias map. Accuracy depends on command syntax.
- **This split:** E/C/S are not in the posture directories, and no workflow/hook source is divided. No applicable seam witness.

## E. Entry state and remaining exclusions

### 27. `_PLAN_LOADS` is per input plan, not per Python source
- **E:645-661, 927-928.** Module-global dictionary keyed by plan realpath, storing a loaded document or YamlParseError; cleared on every main(). Discovery’s shipped check and route processing share the first result.
- **Seam result:** none. It stays in E; its keys are plan.yaml files, not the physical Python files containing its callers. Moving the audit code does not split or duplicate this cache.
- **Accuracy/current:** neutral and unchanged. This is the only persistent module-level load cache in the three files; S’s session is invocation-local.

### 28. Route/plan parsing and aggregation are not source-file-scoped analysis
- **E:48-73, 196-333, 414-596, 706-923, 927-985.** Task regexes apply once per PLAN.md; YAML loading and status checks apply per plan/task; task machine-line budget is explicitly per task, not per file. Resolver agents are aggregated per task; processed/violation counts are per invocation. Discovery `_seen` is keyed by feature path across corpus roots. BIN_DIR/root/manifest/resolver selection use E’s location, which is unchanged.
- **Seam result:** no source-bound witness; these govern input artifacts and remain in E. Moving canonical `_task_files` does not change route-mode `_PLAN_LOADS` or task parsing.
- **Current:** no split-induced route finding/exit change. Whole archived base/pin route outputs can differ because the feature’s own plan directory exists only at pin; QA explicitly identifies that as corpus difference, not source-file analysis leakage.

### 29. Other global aggregations are explicitly NOT per-file
- **C:318-330:** sole-state-reader exemption count is document-wide, not one allowance per file.
- **C:627-651:** migration-unit state aggregation is per inventory task, excluding plan-owned rows, not per source file.
- **C:705-714, 747-768:** final findings/violations and exit selection are invocation/document-wide; migrate violations follow inventory row order, not AST/file order.
- **S:662-716:** reachable input/resource sets and invalid-read `[:1]` cap are per row, not per source file.
- **S:950-955:** consolidation summary aggregates all findings, exit 1 if any. The split can affect inputs to this aggregate through earlier items, but adds no new file budget here.
- **No generic per-file duplicate-symbol/dead-symbol detector exists.** The only relevant duplicate mechanisms are reader full-ID checks, station line suppression, and dictionary overwrites already enumerated.
- **Current:** no independent effect; these cannot supply an additional source-seam counterexample beyond their enumerated file-sensitive dependencies.

## Current-tree impact ledger

1. **Findings, audit exits, stderr:** none changed by any newly discovered member. Existing QA controls show canonical 0/0, consolidation 0/0, empty stderr.
2. **Clean-tree summary:** canonical scanned count **101→103**, intentionally physical-file-based.
3. **Returned analysis data:** scanned source list gains C/S; moved candidate `file`, `id`, and source line/column metadata relocate. Candidate grouping follows file traversal. The two live moved reader symbols are `_classification_document` and `_task_files`; both keep `#1`.
4. **Inventory/contracts:** their file-qualified rows and the `_task_files` T07 key are migrated, preventing otherwise-real stale-location findings.
5. **Counterfactuals:** the alias collector genuinely permits both clean→fail and fail→clean on additional seam-straddling plants. Broad catches here only change grouping/text/count, not clean/fail status. Parse-error examples are already failing trees and must distinguish external scanning from in-tree compilation/import failure.

Therefore the strongest supported conclusion is **current-tree audit behavior preserved, not arbitrary-tree semantic equivalence**. Per-file indexes and caches do not add undisclosed clean-tree findings; checker-package locks are not accidentally re-scoped onto the new audit implementation modules.

## Addendum — census extension found at validate c2 (evidence maintenance per ESC-2 ruling Q4; not a contract change)


Item 18 lists the file/symbol exemption but omits the separate per-file decision to run the AST loader check at all. `structure_audit.py:944–945` requires the exact ASCII spelling of `spec_from_file_location` anywhere in the source text; `:249–265` tests the parser’s normalized callee. Static witness: a retained function contains a call whose callee normalizes to that name but whose source has a non-ASCII spelling. The old entry passes the prefilter because the moved rule itself spells the name; the pinned entry does not and silently skips that node. Python AST normalization and both branch conditions were checked on the Git blobs in memory; [INFERENCE] absent any other findings, consolidation goes 1→0. **Gate (i):** all unmodified E/C/S blobs have zero matching call nodes, and the bound clean receipt records identical consolidation output. **Gate (ii):** base `check-plan-routes.py:2623–2624` and pin `structure_audit.py:944–945` are byte-identical; only the source file supplying the ASCII text changed. This is a perturbed-tree false negative within the approved class, not a request to change the rule or widen the checker.

## Stage 2 — quality

No new unsanctioned fail-open branch. Canonical source and named-plan read errors accumulate findings before exit selection (`canonical_reader_audit.py:228–239,732–770`); consolidation reports failed source parses before skipping their locks and retains the existing census/error behavior (`structure_audit.py:892–918,927–955`). The two libraries own substantive audit behavior; the CLI imports their entry points without a shim. Pinned `code-grade.py`: 187 passing records, no grade-2 or high finding. No candidate gate or suite was rerun. CR-2 and SEC-1 were not reopened.

## Principles applied

- Migrate Callers, Then Delete Legacy APIs — checked that audit tests use the new module imports rather than retaining a loader-backed compatibility route.
