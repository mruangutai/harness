# Receipt — harness-ai-dev — r-20261121-5-simplify-eng-altitude — FEAT-2225

Angle: ALTITUDE only. Read-only over `git diff 594af2a8..fd8ffcdf` (read via `git show/diff` at the pin). Nothing run. Settled set (plan.yaml decisions, DEC-253 paths, receipts-not-queue, `_evidence_failures`, check-instruction-paths acceptance, `harness_segments()` listing) excluded. Owners: T-01 three files builder-owned; everything else FLAG-ONLY.

**BLUF: 6 findings (3 fold-in, 2 briefing-row, 1 leave). Highest-value: F1 (prose-derived distill authority at the tool vs registry-derived at the yield) and F2 (host re-implements the core's destination rules).**

## Findings (file · line · summary · cost · alternative · recommendation)

### F1 — expertise_apply trusts a prose marker; the yield gate trusts the registered run
- **File/line:** `.omp/extensions/harness-hooks.ts:1151` (`applyCallerRefusal`: `currentMission !== "distill"`, set from `MISSION_MARKER` at `:18/:1005/:1248`); counterpart `.claude/skills/harness/bin/validate-digest.py:2055,_require_distill_lineage`; `dispatch-guard.py:748-833`.
- **Summary:** "Is this a trusted distill run" has two authorities. dispatch-guard only *requires* the marker on children of a bound `distill-*` run (`_distill_preflight` returns when `_bound_distill_run()` is None); it never refuses a `HARNESS-MISSION: distill` line where no bound run exists. Its own comment says the mission is "DERIVED from the bound run, never from prose", but the host tool reads the prose.
- **Cost / behavior:** a governed child dispatched under a non-distill run that merely carries the marker line passes `applyCallerRefusal` and `expertise_apply` writes its own Expertise file and a receipt in the feature tree. validate-digest later refuses a yield *claiming* those ops (no registered distill lineage), but the file bytes already landed; the compensating controls are own-file-only scope, replay/merge-distill coverage and close verification, and they catch it late (merge time), not at the write. Bounded blast radius (own file), but the capability gate is weaker than the comment advertises.
- **Alternative:** one derivation. Make dispatch-guard symmetric: refuse a `HARNESS-MISSION: distill` start with no bound distill run (include the orchestrator, whose distill authority validate-digest derives from the feature's registered distill run via `_require_feature_distill`, not from a lead run, so `_bound_distill_feature` must learn that case or it will refuse a legitimate orchestrator distill). Effect: a mis-registered run id fails at dispatch instead of at yield; no change for correct distill runs.
- **Recommendation: fold-in** (dispatch-guard, main-session-direct; flag-only for me).

### F2 — host re-implements the core's destination and segment rules
- **File/line:** `.omp/extensions/harness-hooks.ts:493-497` (`REPOSITORY_SEGMENT`, `BATCH_ID`), `:520-540` (`applyDestination`), `:543-566` (`lstatOrUndefined`, `placementRefusal`); core: `expertise-merge.py:748-774` (`destination_rel`, `resolve_destination`, `SEGMENT_RE`, `segment != "expertise"`, declared-segment and exact-realpath checks).
- **Summary:** the host's own comment says it mirrors T-01 ("the same exact-path rule T-01's resolve_destination applies, checked before the core runs"). The core already refuses every case the host pre-checks (exit 9) and its receipt returns `destination` (`:1402,:1479`). Only the rel path is needed host-side, for the post-write `check-domain` Edit probe (`appliedPost`).
- **Cost / behavior:** a second statement of the path rule: if the core's segment grammar or declared-segment test changes, the host either refuses what the core accepts (tool unusable for a valid segment) or admits what the core then refuses (error surfaces as a generic tool failure). Behaviorally identical today; about 50 TS lines carry no unique protection.
- **Alternative:** pass `tier`/`repository` straight to `member-ops`, take the post-check path from the core's receipt `destination` joined to the resolved root, and delete `applyDestination`, `placementRefusal`, `lstatOrUndefined` and the mirrored regexes. Keep the zod regexes only as model-facing schema hints. The `applyArgumentRefusal` fence is a deliberate second layer for direct `execute` calls (tests call it past zod); leave it.
- **Recommendation: fold-in** (host file is main-session-direct; the core already carries the rule, so no T-01 change is needed).

### F3 — `distill-*` run-id token rule copied three times, plus two lead lists
- **File/line:** `.claude/skills/harness/bin/feature-record.py:628` (`DISTILL_RUN`), `dispatch-guard.py:756` (`DISTILL_RUN_RE`, `LEADS`), `validate-digest.py:1928/_is_distill_run` (`DISTILL_RUN_RE`, `LEAD_PERSONAS`); each carries a "feature-record.py's rule" comment.
- **Summary:** the rule that decides whether the dispatch gate demands the marker, and whether the yield gate trusts applied ops, is transcribed by hand. Both new copies already import `digest_destination` (`dest`/`destinations`), the module that resolves the registered run id.
- **Cost / behavior:** a drift (say a new `-distill` spelling) makes the gates disagree: the guard demands the marker but the validator refuses the ops, or the validator trusts a run the guard never bound. That reads as a hard-to-trace refusal at yield, not at dispatch. Nothing detects the drift: the comments are the only link.
- **Alternative:** one `is_distill_run(run_id)` (and one lead tuple) in `digest_destination.py`; `feature-record.py`, `dispatch-guard.py`, `validate-digest.py` import it.
- **Recommendation: fold-in** (shared-bin sources; flag-only for me, owner main-session).

### F4 — validate-digest reaches the Expertise core two ways and re-matches ops itself
- **File/line:** `validate-digest.py:2148-2157` (`load_repo_module` + `merge.load_active(...)[1]` in-process), `:2229-2247` (`_assign_items`, `_matching_slot`, `_unreported_errors`), `:2255-2272` (`_verify_receipt` subprocess); core `expertise-merge.py:1421-1440` (`_claimed_ops`, `_match_claimed` with the same exact-op `remove` and `unreported` semantic).
- **Summary:** the validator uses the core's internal batch dicts (`runtime_id`, `parent_id`, `destination`, `ops`, `persona`) in-process, matches claimed ops to batches with its own exact-op multiset logic, then shells out to `verify-receipt`, which repeats that match per runtime. The lineage rule (lead = own runtime plus children) is validator-only and legitimately cross-runtime.
- **Cost / behavior:** two coupling modes to one seam and two copies of "claimed op equals recorded op" (persona stripped, key-for-key equality). A change to the receipt's batch shape or op normalization in T-01 breaks the validator, fail-closed, so a valid distill return is refused with a "cannot be verified" message rather than a test failure. Reader load: about 120 validator lines that restate core semantics.
- **Alternative:** make the core the single reader: let `verify-receipt` (or a read-only `list-active`) take a lineage, or return the active batches as JSON that the validator consumes, so the validator keeps only the lead-lineage selection and the "report every active op" rule. That edits T-01's interface after it closed, hence a row, not a cut-in at build close.
- **Recommendation: briefing-row** (next touch of either file; T-01 core plus validate-digest owners).

### F5 — three shell-command parsers in the guards; the new one sits beside an older one in the same file
- **File/line:** `bash-write-guard.py:282-420` (`_command_words`, `_prefix_width`, `_python_script_words`, `_shell_command_string`, `_program_calls`; about 145 added lines) beside the existing `-c` extraction at `:647-660` (`_python_command_sources`) and the HEAD-move token walk (`:183-250`); `merge-gate.py:97-182` (`words`, `merge_ref`, `nested_merge`) is a third parser that finds `gh/git merge` through nested shell strings.
- **Summary:** the Expertise rule needs "which program runs, behind env/exec/interpreter/sh -c", which the file did not previously expose as one function, so it grew its own. Moving `SHELL_FEEDERS`/`PYTHON_EXECUTABLE` up to share constants is the only reuse done.
- **Cost / behavior:** every bypass fix (a new wrapper such as `xargs`, `timeout`, `busybox`) must be made in up to three parsers; the guards are allow-by-omission, so a miss in any of them is a silent pass, not a refusal. The deeper fix (the CLI refusing mutation itself) does not exist: a Bash-spawned process carries no trusted identity, which is why the guard is the right home for this check at all.
- **Alternative:** a shared `command_calls(text)` helper in `harness_boundary.py` used by bash-write-guard (both rules) and merge-gate. Larger than this feature, and it touches the HEAD-move and merge-detection behavior that the existing tests pin.
- **Recommendation: briefing-row** (next feature that adds a guard rule; do not fold at build close).

### F6 — merge-distill re-derives committed-blob equality that replay already reports
- **File/line:** `merge-gate.py:455-479` (`_blob_sha256`, `_replayed_hashes`, `_committed_replay`); core `expertise-merge.py:1201-1204` (`_check_coverage` refuses uncovered changed Expertise), `:1222-1229` (`up_to_date`, `current_sha256`, `result_sha256`).
- **Summary:** coverage and "file equals replay" are both computed by `replay --check` against the working file; merge-gate then repeats them against `git cat-file blob <head>:<rel>`.
- **Why leave:** `gh pr merge --match-head-commit <head>` merges the committed blob, not the working tree, so the head blob is the right authority and `_require_checkout` (HEAD equals PR head, clean `.harness`) is what makes the two coincide; the duplication is the compensating control for a worktree edited between verification and merge, under the owner lock. The residual to note: merge-gate's `EXPERTISE_PATH_RE` (`merge-gate.py:92`, any `[^/]+.md`) is wider than the core's persona-only `EXPERTISE_PATH_RE` (`expertise-merge.py:716`, `harness-*.md`). A PR changing only a non-persona `.harness/expertise/*.md` is classified a distill candidate and then refused ("no active receipt"). That fail-closed behavior is intended. The paths regex also exists in `check-expertise.py:88-90` (`classify_tier`), `harness_boundary.py:707`, `check-instruction-paths.py:30` and `expertise-merge.py:471`: five-plus transcriptions of "an Expertise path", which a later feature can fold into one `check-expertise` helper.
- **Recommendation: leave** (the blob comparison is deliberate and bounded).

### Also read, no finding
- Persona files (16): one-line pointer "Expertise only at distillation through `expertise_apply`" repeated per persona; mechanics live once in `harness-distill/SKILL.md` step 3. **leave** (each injected persona must name its own tool; the sentence is a pointer, not a restatement of the procedure).
- `harness_boundary.claim_set_refusal` advice text: correct redirect to the tool; tier parse duplicates the path regexes above (covered in F6 residual).
- `.harness/harness/docs/*` (T-02): out of the altitude angle for code; no finding.

## Principles applied
- **Delete First** (`references/delete-first.md`, read this run): F2 and F3 are recommended as removals (host mirror of the core rule, hand-copied regex) before any new code; F5 and F6 were declined as additions/rewrites of larger scope.

## Verification
Read-only; no checks run. All line numbers are from `git show fd8ffcdf:<path>`.
