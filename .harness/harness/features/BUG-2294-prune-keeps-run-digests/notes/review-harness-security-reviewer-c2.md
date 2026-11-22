# Security review — BUG-2294 — c2

PASS — **SEC-01 (substance / med / T-01) CLOSED at pin**, for the reported static run/UI-link shapes. No remaining T-01 must-fix. This is static assurance plus inspection of existing execution receipts, not an independently executed exploit or test pass.

Reviewed `c1724230c4d931ad46d433c8ba93df8cf312f898..88bf039f6ff31edbb1d5a4b2f6620762e3cc095a`, emphasizing `70981edd..e51277a4`. The live feature.json names the review pin; git merge-base confirms code commit `e51277a4ce11c91f2252026ae4dd6e0fbf12a503` is its ancestor, and the code/test diff from that commit to the pin is empty. No reliance on HEAD.

## SEC-01 disposition and destructive scope

At pinned `.claude/skills/harness/bin/prune-run-evidence.py:120–146`:
- `runs/build-alias -> kept-run`: even though keep_set admits directory links, `_ui_targets` checks the alias itself with islink before considering its UI; it reports a skip, never `rmtree(alias/ui)`. The actual kept run is independently excluded by keep membership.
- `runs/evil-alias -> outside-directory` containing ui/: the same run-link check excludes it before UI targeting; destination UI survives.
- A real run with `ui -> outside/ui`: the second islink check excludes the UI link and names it as skipped. This also avoids the previous leaf-link OSError.
- A real ui/ containing `ui/<child>` symlinks: shutil.rmtree removes those link entries, not their directory/file targets. Static Python library semantics; this shape is not exercised by the added regression.
- With stable, real ancestors, only real non-kept `runs/<name>/ui` directories reach rmtree; dry-run never calls it. Run records and non-UI siblings are outside that deletion subtree.

The regression binds all three reported link shapes and compares nonempty destination byte maps while requiring removal of the real prunable UI (`tests/unit/test-prune-run-evidence.py:150–194`). `notes/red-first-T-01.md`, section c1 fix, records four genuine assertion failures against 70981edd and 25 passing checks against the fix, with subject hashes. Receipts were inspected, not rerun; QA owns final execution.

## Boundaries and remaining limits

Ancestor links are **not** rejected: a linked root/.harness/segment/features/feature or a linked feature/runs container can still lead rmtree outside the lexical checkout. `_feature_dir:41–46` returns the lexical candidate; `_load_record:103–117` checks a marker and loads JSON, not realpath containment or authorization. root_above uses abspath and marker ancestry, not realpath authorization. An OS-resolved cwd or explicit canonical root does not prove the selected feature is authorized. These ancestor paths already reached whole-run rmtree at base; this patch narrows their deletion to UI, rather than introducing them. Concurrent ancestor/run replacement between checks and deletion is likewise not a proven containment guarantee. SEC-01 closure does not claim hostile-concurrent-filesystem or checkout-wide confinement.

Open question SEC-C2-Q1 (nonblocking): should a separate root/feature authorization task reject linked ancestors and traversal-bearing operator feature arguments, and define concurrent-writer expectations? Recommendation: decide that boundary separately; do not reopen the fixed static run-alias case or expand T-01 without approval.

## Other audit surfaces

SC-03 inspection: pinned pruner selectors, explicit keep validation, refusals and CLI are unchanged; ship-command diff changes only retention prose, leaving both invocations and step placement unchanged. Full 20-path census: pruner is destructive input/output surface; test is isolated fixture/subprocess code; ship and decision/index files describe that surface; remaining feature/plan/review/evidence records are non-executable review metadata. No new shell/SQL/template/spreadsheet sink, network/dependency/auth interface, or credentials identified. Full-diff credential-shaped scan matched only token accounting and prior review prose. Printed names/errors remain local operator diagnostics, not a new external secret sink. Product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent; no substitute guidance invented.

Canonical result: PASS; in_scope true; severity_max none; findings []; must_fix []; files_touched []; expertise_update []. Threat boundaries: run/UI aliases → deletion (T, mitigated); durable records → UI-only deletion (T, mitigated); ancestor-controlled selection → filesystem deletion (T, not mitigated, pre-existing and separately scoped). Open questions: SEC-C2-Q1 only.
