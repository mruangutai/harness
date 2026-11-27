# Grilling — STATE.md goes stale at sign-off (#2423) — 2026-11-26

## Destination
STATE.md stops restating anything that can be derived, and so stops going stale. Station comes from `plan.yaml` and the active run from `feature.json`. STATE.md is optional and holds only `## Open Questions`. Enforcement keeps it that way:
- at write time (check-domain);
- for every feature not yet shipped (a new check-state violation);
- at ship (gh-sync).

## Mission
mission: plan
reason: The changes include a new check-state invariant, a changed check-domain write gate, a changed `gh-sync.py ship` behaviour, a template contract change and about 12 doc surfaces. That is three enforcement surfaces plus a new DEC, so this is not a patch.
confirmed-by: operator (questions and signature delegated to fable-advisor, 2026-11-26)

## Settled
All answers are from fable-advisor, on the operator's behalf.

- **Q1: the shape of STATE.md → A, derive.**
  - `## Current` is deleted. STATE.md holds only `## Open Questions` and is optional; absent means there are no open questions.
  - Readers get the station from `plan.yaml` top-level `status:` (DEC-191). They get the active run, squad and BLOCKED verdict from `feature.json` `runs[]`.
  - A blocker is either a lead's BLOCKED verdict, which feature.json and the digest already record, or an Open Questions entry ("question, and who is blocked on it").
  - A' (keep a `- blocked:` line) is rejected: the free-text status line is the field that drifted worst.
  - B (a writer in sign-approval, gh-sync status or ship) is rejected: it races the DEC-120 single writer to maintain a copy of derivable data.
  - Keep the name STATE.md and the #671 answers-file protocol, and rewrite the template header.
- **Q2: the drift rule → both of the following, as violations under a new INV** (not INV-23, which has warning severity):
  - (i) Structural: a STATE.md carrying `## Current`, or any `- feature:`/`- run:`/`- squad:`/`- status:`/`- station:` line, is a violation. It parses no prose.
  - (ii) Signer questions: once `plan.yaml` `approval.status` is `approved`, no Open Questions entry may carry the `signer` tag. The tag is matched as a token in the entry's leading parenthetical. The signer clears these entries in the sign-off commit, which becomes an explicit step in `.omp/commands/harness-plan.md` (sign-off steps ~:37-59) and `harness-patch.md` (~:32-51).
  - The plan must say plainly that this INV protects only features before ship: check-state audits no shipped feature (FEAT-2206).
- **The co-equal enforcement deliverable is the check-domain write gate** (`check-domain.py` ~:2391-2396; DEC-180 binds every author, shipped or not). It must deny a `## Current` section at write time. The ROUTING constant (~:1308), which today tells writers to "REPLACE STATE.md ## Current", must be rewritten, or the same tool contradicts itself.
- **Q3: shipped features → (a) plus (b).** `gh-sync.py ship` refuses while STATE.md has a non-empty `## Open Questions`, and deletes STATE.md in the ship commit otherwise. Deleting alone could destroy an unanswered user-facing question. Once signer entries are cleared at sign-off, a non-empty file at ship is an anomaly that should stop the line.
- **Migrating the existing files is a separate chore PR from a main-based worktree, after the feature merges**, because FEAT-1559 forbids editing other features' directories from the feature worktree.
  - The chore deletes the STATE.md of every shipped feature.
  - It relocates kaya FEAT-01's recovery context (wrong-repository GitHub receipt, prototype acceptance, planning/code roots) into that feature's handoff note, the home `succession.md` designs for it, rather than deleting it.
  - PR #2424 is closed as superseded, unmerged.
- **Q4: mission and records → plan, main-session-direct (DEC-174).** check-state, check-domain and gh-sync are all enforcement. Dispatches go only to product-lead, validator-lead and fable-advisor.
  - Record a **new DEC** for derive-don't-copy, cross-referencing DEC-45, DEC-120 and DEC-191.
  - Edit DEC-45 and SPEC in place to state current truth (DEC-205: no amendments, current truth only).
- **SPEC surfaces that carry weight:**
  - The artifact-table row (~SPEC.md:83) gets the new shape.
  - The repair-table row "STATE points at a task absent from PLAN → halt" (~:186) goes.
  - The pause/resume text (~:229-251) is rewritten to rest on plan.yaml, feature.json and the handoff note.
- **Every reader handles absence.** The SKILL.md loop step 1 (~:39), its re-read (~:77) and the after-close-run write (~:92) read or write STATE.md only "if present", and lose the "REPLACE ## Current" duty.
  - INV-2 and INV-5 survive, applying only when the file exists. INV-5's T-id check still covers question prose.
  - `succession.md:17` ("STATE.md log entry", which contradicts no-history) and `:49-51` (STATE.md `## Current` as the recovery path) are rewritten.

## Not yet specified
- The new INV's number and table row wording, and whether the ship refusal reuses `cmd_ship`'s existing refusal ordering (`gh-sync.py` ~:682-697) unchanged. pm settles both from the code.

## Out of scope
- Migrating the 34 existing STATE.md files: the separate chore PR above.
- Renaming STATE.md or moving Open Questions elsewhere: rejected as churn across the same surfaces with no gain in enforcement.
- Any status or phase field in `feature.json` (the #2423 constraint and DEC-191).

## Facts I verified (so pm does not re-derive them)
- 35 STATE.md files exist and 34 belong to features whose `plan.yaml` `status:` is `done`. Only one is consistent (idle, no questions); the rest say awaiting-user (13), in-flight, review, in_review, validated-clean, distilled, 'building;', active or awaiting_user. Checked with a shell loop comparing the `- status:` line with plan.yaml's top-level `status:`, at e83c4e20; the advisor re-ran it independently.
- FEAT-2542 (shipped 2026-11-26) still lists SQ-1..SQ-7 tagged `(blocking, signer)`/`(signer)` with status awaiting-user. Checked by `cat` of its STATE.md, at e83c4e20.
- The only non-done feature with a STATE.md is `.harness/kaya/features/FEAT-01-kaya-platform` (plan `ready`, STATE says blocked). Checked by the same loop, at e83c4e20.
- Six shipped features never had a STATE.md: BUG-2141, BUG-2187, BUG-2253, BUG-2390, BUG-2399-run-records-tracked and FEAT-2389, all main-session-direct. Checked with `ls`, at e83c4e20.
- check-state never audits a shipped feature: `check_state/ctx.py` `_load_features` → `_split_shipped` (FEAT-2206). Checked by reading the code, at e83c4e20.
- The current STATE.md checks are INV-2 and INV-5 (`check_state/plan.py:272-298`) and INV-23 (`check_state/feature_record.py:454-485`, warnings). The write gate is `check-domain.py:2391-2396`, and ROUTING is at `:1308`. Checked with rg and by reading the code, at e83c4e20.
- STATE.md is named outside feature directories in: harness SKILL.md, check-domain.py, check-plan-routes.py, check_state/{ctx,feature_record,plan,table}.py, feature_schema.py, harness_yaml.py, structure_audit.py, references/{ledger,succession}.md, templates/{README.md,STATE.md,team-config.yaml}, .harness/README.md, docs/{BUILD,DECISIONS-INDEX,DECISIONS,SPEC}.md, docs/org.html, .harness/team-config.yaml, .omp/agents/{harness-orchestrator,harness-product-lead}.md, plus tests/integration/test-check-{domain-*,state-*}.py, test-harness-yaml.py, test-validate-feature-json.py and tests/unit/test-{answers-provenance,check-state-shipped-ctx}.py. Checked with `rg -l --hidden 'STATE\.md'`, at e83c4e20.
- PR #2424 (chore/refresh-stale-state-md, 22 files) has been open since 2026-11-23. Checked with `gh pr view`.
