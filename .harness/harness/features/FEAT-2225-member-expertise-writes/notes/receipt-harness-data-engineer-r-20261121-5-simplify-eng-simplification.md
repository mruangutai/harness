# Receipt — harness-data-engineer — r-20261121-5-simplify-eng — SIMPLIFICATION

BLUF: 9 findings, none blocking, none changes an SC/decision/task. Read-only at pinned `fd8ffcdf` (`git show`/`git diff 594af2a8..fd8ffcdf`). Code files read: expertise-merge.py (new 650-1500), merge-gate.py (distill 307-596), validate-digest.py (1926-2272), dispatch-guard.py (455-510, 747-839), bash-write-guard.py (152-425), harness_boundary.py, check-instruction-paths.py, `.omp/extensions/harness-hooks.ts` (490-610, 1128-1250, 1368-1395). Not read in depth: tests, common.json, JSON classification. No checks run. Only expertise-merge.py (T-01) is builder-owned; every other finding is FLAG-ONLY.

Settled and not flagged: DEC-253 paths, receipts-not-queue, `_evidence_failures`, check-instruction-paths acceptance, shared `harness_segments()`, all plan decisions.

## Findings (file · line · summary · cost · alternative)

**F1 · medium · `.omp/extensions/harness-hooks.ts:538-574, 1160-1172, 1197`** — host recomputes destination and containment that the core already owns.
`applyDestination` re-implements `destination_rel` (tier/segment/`!== "expertise"` carve-out; `REPOSITORY_SEGMENT`/`BATCH_ID` copy `SEGMENT_RE`/`HEX64_RE`), and `placementRefusal` re-implements `resolve_destination` (declared segment + no symlink in chain). `member_ops` runs both before any write (expertise-merge.py:1391-1392) and passes `--tier/--repository`, never `rel`.
Cost: one rule in two languages that must drift together (comment at 496/560 admits it); ~40 lines + a 2nd error vocabulary.
Alternative: delete `applyDestination`/`placementRefusal`; the post-write check path comes from the receipt the core returns (`result["destination"]`, expertise-merge.py:1402) joined to the root. Keep only `featureRoot`, `mainBase` (host-derived base) and the argument allow-list.
Behavior: a bad tier/segment/symlink still refuses (core exit 9 → `memberOpsReceipt` → `refuseApply`); only wording changes. `applyArgumentRefusal` (524-535) is a "second fence behind the host schema" (its own comment) — `.strict()` zod already refuses extra keys; `ops`/`supersedes` shape is re-checked by `_decode_ops`/`_supersedes_refs`. Candidate to drop with F1 unless the host may skip schema validation (unevidenced).

**F2 · medium · `validate-digest.py:2255-2272` (+2182-2247, 2148-2154)** — verify-receipt run as a subprocess though the module is already loaded in-process; matching done twice.
`_active_batches` loads `expertise_merge` via `load_repo_module`, then `_verify_receipt` spawns `expertise-merge.py verify-receipt` per slot, re-deriving `--tier/--repository` from `destination.split("/")` (a third spelling of the path grammar). `_assign_items`/`_unreported_errors` already do the multiset op-matching that `_match_claimed` repeats in the CLI; verify-receipt's `unreported` field (expertise-merge.py:1468,1480) has no consumer anywhere in `bin/`.
Cost: process spawn + 60s timeout path + exit-code scraping per slot; two matchers that can disagree.
Alternative: call `merge.verify_receipt(...)` in-process (the function exists, expertise-merge.py:1452) and catch `MergeRefusal`; drop `unreported` from the result (`preserved` stays — plan T-01 names it). Caveat: the dispatch names the CLI as the seam; the function sits behind that same CLI, so no new seam, but confirm the lead reads the CLI as the contract before applying.
Behavior: same refusals; saves ≈ one Python start per receipt slot at validate time.

**F3 · low-medium · `dispatch-guard.py:756`, `validate-digest.py:1941,1955-1956`, `feature-record.py:628`** — one rule, three regex copies.
`(?:^|-)distill-` is restated in dispatch-guard and validate-digest, each with a comment pointing at the feature-record original; `LEADS` (dispatch-guard:757) and `LEAD_PERSONAS` (validate-digest:1945) are a second pair of restatements. A change to the run-id token rule silently splits "trusted distill" (validate) from "distill child must carry the mission" (dispatch).
Alternative: one `is_distill_run(run_id)` in `harness_boundary.py` (both guards already import it); feature-record.py may adopt it later. Behavior unchanged.

**F4 · low-medium · `merge-gate.py:482-487, 528`** — `_check_expertise` re-checks bytes already proven checked.
`_committed_replay` (465-479) requires every changed file's committed blob sha == the replay `result_sha256`; the replay already ran `check_candidate` (check-expertise on those exact bytes at their real relative path, expertise-merge.py:820-835) and refuses on failure (`replayed` must be true, 449). `_require_checkout` (424-434) pins the worktree to the same head and clean `.harness`.
Cost: a second subprocess and refusal path, ~8 lines, for no new information.
Alternative: delete `_check_expertise` and its call. Behavior: none while both steps stay; a checker change between the two calls is the only difference.

**F5 · low · `dispatch-guard.py:760-806`** — four-deep chain for one fact.
`_distill_preflight → _bound_distill_run → _bound_distill_feature → _distill_run_feature → _registered_run_id`. `_bound_distill_run`'s `involves_lead` guard is the same two conditions `_bound_distill_feature` re-tests (790, 794); its docstring is identical to the callee's. Reader-load: layers axis.
Alternative: fold `_bound_distill_run` into `_bound_distill_feature` (keep the early `None` so `_destinations()` stays lazy) and inline `_distill_run_feature` (one expression). Behavior unchanged.

**F6 · low · `expertise-merge.py:856-863` (T-01, builder-owned)** — `_destination_form_ok` is a third statement of the expertise-path grammar in the same file (`EXPERTISE_PATH_RE` 716, `destination_rel` 748-758), including the `!= "expertise"` carve-out twice.
Alternative: accept `rel` iff `EXPERTISE_PATH_RE.match(rel) and rel.endswith(f"/{persona}.md")` plus the single carve-out, or compare against `destination_rel(persona, tier, segment)` for the parsed pair. Behavior unchanged for valid receipts; confirm the `tests/unit` receipt-shape cases still pin it.

**F7 · low · `bash-write-guard.py:252-259` vs `301-305`** — the existing HEAD-move loop still hand-rolls `try: shlex.split … except ValueError: split()` that the new `_split_words` now provides; the file now has two segment→tokens→basename walkers. Alternative: HEAD-move loop uses `_split_words` (no behavior change; the fail-open comment at 539-545 is a separate function). Do not merge `_git_subcommand` into `_subcommand` — git needs flag-value coupling (documented 197-199), an anchor that took rounds to get right.

**F8 · low · `validate-digest.py:2138-2145`** — `_foreign_persona_errors` is redundant for refusal: a foreign-persona item cannot match any slot of a non-lead's lineage (`_lineage_batches` own runtime only; `_stranger_personas` enforces persona), so `_assign_items` already errors via `_unmatched_error`. It only improves the message. Alternative: delete and reword `_unmatched_error`. Behavior: still refused; message loses the "consolidating others' is a lead's" hint (a deliberate teaching string; keep if the hint is wanted).

**F9 · low · `expertise-merge.py:1170-1178` (T-01, builder-owned)** — `_candidate_refusal` scrapes `section=(\w+)` out of `refusal.lines[0]` (prose emitted by `_check_caps`). A structured fact recovered by regex over a message; a wording change in `_check_caps` silently makes `section` null. Alternative: let the cap refusal carry the section (attribute on `MergeRefusal` or a returned tuple) — touches `harness_merge`/`_check_caps` callers, so only if the lead wants it.

## Checked and judged NOT complexity (anchors kept)
- `_confirm_agreement` re-read, `receipt`-after-`target` ordering, `EXIT_*` codes: deliberate fail-closed evidence (module header 697-705).
- bash-write-guard "list the reads, not the mutators" and basename identity (281-289): anchored direction, same as HEAD-move rule.
- merge-gate `_recheck` re-reading PR head and live main; `_git`/`_run` wrappers differ from expertise-merge's `_git` only in failure type (DistillRefusal vs MergeRefusal) — not worth a shared helper.
- `EXPERTISE_PATH_RE` in merge-gate (any `*.md`) vs expertise-merge (`harness-*.md`): differing strictness is semantic (merge-gate must catch more, coverage must name receipts).
- harness_boundary `_EXPERTISE_DESTINATION` / check-instruction-paths `EXPERTISE_RE`: settled/one-line.

## Principles applied
- Delete First (`references/delete-first.md`, read): F1, F4, F5, F8 propose removals (duplicated host fence, repeated check, pass-through layers, message-only guard) before any addition; F3/F6 consolidate restated rules.
- codebase-design deletion test + reader-load axes: F2, F5 (layers to trace).

## Open questions
- F2: is the CLI or the `verify_receipt` function the contractual seam for T-04? (affects whether in-process call is allowed.)
- F1: does the host guarantee zod validation ran? If not, keep `applyArgumentRefusal`.
