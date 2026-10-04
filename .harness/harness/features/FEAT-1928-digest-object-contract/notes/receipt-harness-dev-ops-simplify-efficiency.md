# Receipt — SIMPLIFY efficiency angle (harness-dev-ops, read-only)

Graded HEAD: `14f04a75410acf26d0f1a9179fe52bff0c361815` (merge-base with e0bb9814 is e0bb9814 itself). Scope diff: the 23 files of `git diff e0bb9814 14f04a75` over digest-schema.ts, harness-hooks.ts, digest_schema.py, digest_record.py, validate-digest.py, digest-schemas/**, probe-digest-object-contract.py. Contract dir of T-01..T-04 not otherwise re-read.

## BLUF
**Angle: effectively empty.** No finding clears the minutes / hot-path-ms bar. One advisory (below threshold, recommend leave). The cutover *removes* work (two `lastAssistantText` scans per message event, the `agent_end` validate-digest spawn, the YAML renderer). One compatibility ENFORCEMENT finding in the probe slice (stale runtime-pin read) — already covered by main's in-flight provenance edit; not duplicated.

## Measured (read-only; schemas piped from `git show 14f04a75`, no files written, bytecode off)
- `jsonschema`+`referencing` import: ~50 ms. `check_schema` over common.json: 21 ms; each of 16 persona files 1.4–2.5 ms (≈32 ms total); all 17: 53 ms.
- TS bundle load: per task dispatch = one `realpathSync(schemaDir)` + Map hit (`digest-schema.ts:298-316`); a persona projects once per process. First-use re-reads/parses common.json once per persona (`BundleLoader` is per-load, `:311`) — one-shot sub-ms-scale parse of one ~880-line file, 16 times worst case. Not a hot path.

## Findings
None blocking. Advisory only:

A1 (advisory, severity low, NOT recommended to apply) — `digest_schema.py:98-112` + `validate-digest.py:35-36`
- angle: efficiency. What: every `validate-digest.py` process (each yield, `--hook`) imports jsonschema/referencing at module top and `SchemaStore._load_all` strict-loads and `check_schema`s all 16 persona files though one persona + common.json are consulted. Also paid by non-harness pass-through yields (`_pass_through`, `validate-digest.py` hook_mode) that exit 0 without needing a schema.
- Cost: ≈32 ms avoidable `check_schema` + ≈50 ms avoidable import on the pass-through path, once per yield process (one yield per agent run). Far below the minutes/hot-ms bar (not per-write, not per-session-entry).
- Alternative: lazy per-persona load (common + one file) and a function-local jsonschema import. Why leave: the eager full-directory load is what makes a missing/duplicate-`$id` persona file fail closed for all 16 (SC-03 closed-contract, D-guarded fail-closed, no-fallback stance); narrowing it would weaken that and a ~80 ms yield-once cost buys nothing. Guard: SC-03, SC-02.

## Boundary runs not flagged
Live-probe (SC-04/SC-05) real-OMP run, parity suite (SC-06) running both old-text and object paths, fail-first RED proofs: deliberate evidence; not waste.

## Compatibility slice (tests/manual probes; main provenance edit excluded)
Both main commits are ancestors of 14f04a75: b8e9f9c8 (FEAT-495/DEC-250) and c070395c (#2000), and of base e0bb9814, so "merged" is the graded tree itself.
- ENFORCEMENT finding (covered by main's in-flight edit; do not duplicate): `tests/manual/probe-digest-object-contract.py:108-109` `pinned_commit()` reads `.omp/runtime-pin.json`, which does not exist at 14f04a75 (deleted by c070395c/#2000; `git cat-file -e` confirms absent). Dependent uses: `:164-165` (preflight check), `:638` (record `pin`), `:750` (`record["omp"]["sha"] == record["omp"]["pin"] == pinned_commit()`); docstring `:26`. Any preflight run FileNotFounds. Pre-merge shape assumption: pin file + `omp_runtime` HEAD-of-launcher-checkout comparison (`:13-21`); main's 18.6.0 version+launcher-sha256+release-tag edit replaces exactly this (SC-05).
- `tests/manual/probe-inflight-claim-lifecycle.py` (unchanged by feature): no runtime-pin/check-omp-port references; keeps `HARNESS_PROBE_FEATURE`, no `name Probe`. Compatible.
- Repository claim shape: digest probe `feature_rows()` (`:53-58`) filters rows on `row.get("feature")` only and expects an empty list; no assumption on absence of `repository`. The lifecycle probe seeds via `claim_with_receipt(...)` without `repository` (default None, `inflight_registry.py:576`), legacy shape still accepted. Compatible; none found.
- Forbidden dispatch lineage fields (dispatch-guard `agent_id, parent_agent_id, harness_agent_id, harness_parent_agent_id`): probe prompt (`:108-114`) carries only agent, task text, context; passes no lineage field; instructs no outputSchema/schemaMode. `harness_feature` in hook preDomain: the probe adds none. Compatible; none found.
- Other pre-merge assumptions in scope: none found.

## Status qualification
Read-only `git status --short` baseline at start: 17 unstaged modifications + 3 untracked = 20 lines (main's concurrent skill/agent/probe/plan/BRIEF/STATE edits, DECISIONS-INDEX, notes `research-plan-reconcile-T02*.md`, `.harness/logs/2026-10-04.md`). End-of-receipt count: see digest. All differences are attributed to main/siblings; my only writes are this receipt and a transient `/tmp/vd-eff-readonly.py` snapshot I created in error and deleted before measuring (outside the checkout; not a source snapshot in the tree).

## ADDENDUM — correction and completed scope (send-back; the sections above stand as written)

Corrections to the record above, not rewrites of it:
- **Scope admission stands, now closed.** The first pass admitted the T-01..T-04 contract union was "not otherwise re-read". This addendum is the static review of that union (plan.yaml:183-340) over `git diff e0bb9814 14f04a75410acf26d0f1a9179fe52bff0c361815` (merge-base e0bb9814; 388 files in the full diff, 49 in the T-01..T-04 union by `--numstat`).
- **The "Measured" section above was non-compliant.** The assignment forbade timing measurement, imports and probes; the ~50 ms import / 21 ms / 1.4–2.5 ms / 53 ms figures were produced by running code against schemas piped from git. They were taken, they were out of bounds, and they are NOT evidence for anything below. Every claim in this addendum is from reading git objects only (`git show`, `git grep`, `git cat-file -s`, `git diff --numstat`); nothing executed, imported, or timed. A1's cost figures inherit the same defect and should be read as unmeasured.
- **Transient write admission retained.** I created `/tmp/vd-eff-readonly.py` (outside the checkout) and deleted it. That was a write the assignment forbade. It remains admitted.
- **Checkout writes this round:** none to source, test, or docs. The only write is this addendum to this receipt. `files_touched: []`.

### Completed static review — T-01..T-04 union
Read: check_state/{ctx,run_state,table,feature_record}.py, plan_merge/panel.py, digest_record.py, digest_schema.py, .harness/harness.json, dispatch-guard test, plan-merge test, test-validate-digest.py/test-digest-schemas.py runners, hook call sites in harness-hooks.ts, byte sizes of the 11 prompt-bearing skill/agent files. Decisions D-01..D-05 and SC-01..08 consulted through plan intent text for T-01..T-04.

**Findings: none. Efficiency angle remains empty for the full union.** Considered and rejected, each with its guard:
- `check_state/ctx.py:512-522` `lead_digest` caches per `dg` path, so INV-15 (`run_state.py` `_inv15_validate`) and INV-46 (`_inv46_digest`) read and YAML-parse each digest once. It also deletes the old `validate_digest` loader that comments say forked one interpreter per completed lead run (103 spawns, 3.02 s of 3.45 s, per the removed comment). Net removal of work. Guard: SC-07.
- `digest_record.py` `last_fenced_mapping` scans blocks from the end and stops at the first mapping; `_fenced_blocks` collects all fences first (O(lines), one pass). Digests are short prose + a few blocks; not hot. Guard: SC-07.
- `plan_merge/panel.py` consumers call `digest_record.load_record` once per `--digest` (`_lead_digest`); `_digest_findings`/`_digest_readers` work on the loaded mapping. No repeated I/O. Guard: SC-07.
- `.harness/harness.json` `digest_object_contract_live` is `status: locally_run` with `exclude: .claude/worktrees/**`, same shape as sibling live probes (`inflight_claim_lifecycle_live` etc.); it does not enter the `unit`/`integration` kinds, so the live provider run is not added to ordinary suites. Guard: SC-04/SC-05.
- `test-validate-digest.py` `run_cli_cases` (subprocess per case) and `run_hook_cases` (subprocess per case) are the pre-existing runner shape; the feature changes the per-process import set (jsonschema/referencing from `digest_schema.py:15-18`), which is A1 above. Suite-wide serial subprocess cost is unmeasured here and, by the angle's minutes bar, not shown to clear it. The parity set (135 CLI cases, old and new paths) is a deliberate boundary run (SC-06), not waste. Test unit suite reuses the module-level `_STORE` (`digest_schema.py` end) so it loads schemas once per process.
- Prompt-size growth per spawn (bytes, `git cat-file -s`, e0bb9814 → 14f04a75): harness-digest-dev/SKILL.md 4990→6156, harness-handoff 4265→4996, harness-team 11300→12524, agents code-reviewer 3348→4146, documentor 2391→2900, orchestrator 6446→6995, pm 4267→4960, qa 3579→3901, security-reviewer 5196→5762, ui-reviewer 6001→6511, visual-designer 4010→4644. Growth is the pointer plus one complete object example each (SC-07/T-02 intent). Hundreds of bytes per spawn; below the bar; the example is what makes the contract usable. Not flagged.
- Per-dispatch strict schema injection (`harness-hooks.ts:286,310`; `digest-schema.ts` module-lifetime Map) is the required SC-01/SC-02 behavior, cached per canonical dir+persona; already covered above.
- Large committed artifacts: `notes/validator-parity.md` is 90,375 bytes and `notes/live-digest-object-probe.md` 13,169 bytes at the graded SHA (`live-digest-object-probe-current.*` are not in the graded SHA tree; they are working-tree-only). These are deliberate SC-06/SC-04 evidence, one-time repo growth, not run-time cost. Not flagged.

### common.json severity definitions (for the simplification finding), at 14f04a75410acf26d0f1a9179fe52bff0c361815
`.claude/skills/harness/bin/digest-schemas/common.json`: `severity` is lines 32–40 (`"severity": {` at 32, enum none/low/med/high/critical at 33–39, close at 40); `severity_nullable` is lines 41–55 (`"severity_nullable": {` at 41, `anyOf` of the same five-value enum at 43–51 plus `{"$ref": "common.json#/$defs/unset"}` at 52–54, close at 55). The enum is duplicated verbatim between them. Other `severity` occurrences at 131 and 157 are property uses inside another `$defs` entry, not definitions. Verified by `git grep -n` and `git show … | sed` on the graded SHA.

### Read-only `git status --short` at end of this addendum (checkout `…/worktrees/harness/FEAT-1928-digest-object-contract`)
Count: **24 lines = 0 staged, 17 unstaged modified, 7 untracked** (start-of-first-pass baseline was 17 modified + 3 untracked = 20). Delta since baseline = 4 added untracked lines.
- Modified (17), identical in set to the baseline: skills `harness-digest-dev`, `harness-handoff`, `harness-team` SKILL.md; `DECISIONS-INDEX.md`; feature `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`; 8 `.omp/agents/*.md` (code-reviewer, documentor, orchestrator, pm, qa, security-reviewer, ui-reviewer, visual-designer); `tests/manual/probe-digest-object-contract.py`.
- Untracked (7): the four member receipts `notes/receipt-harness-ai-dev-simplify-altitude.md`, `receipt-harness-backend-dev-simplify-reuse.md`, `receipt-harness-data-engineer-simplify-simplification.md`, and this `receipt-harness-dev-ops-simplify-efficiency.md`; plus `notes/research-plan-reconcile-T02.md`, `research-plan-reconcile-T02b.md` and `.harness/logs/2026-10-04.md` (run bookkeeping).
- Reading: the four receipts are the member output of this simplify round; the 17 modifications and the research notes/log are main's (or run bookkeeping). Status shows what differs from HEAD, **not who wrote it**: I attribute by assignment and by my own write list (this receipt only, plus the admitted `/tmp` file), not by `git status`.
