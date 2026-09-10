# Research — FEAT-104 strict digest + step schema — key triage, cycle 0

**BLUF.** The drift is roughly **eight times worse** than issue #104 recorded five weeks ago:
**65** distinct out-of-schema digest keys (ticket: 8) and **202** distinct `steps[]` keys
(ticket: 95). Both levels are triaged below to a closed partition — every measured key has a
disposition. `adequacy_notes` is resolved **into `SCHEMAS["lead"]` as a required list** (#37
closed in this feature). The passthrough mechanism is **generalized into a declared typed
table**, not extended in place, because a `SCHEMAS` member is *required* (DEC-121) and DEC-216
would then force `matrix_ok` into every lead's documented block.

## Measurement — method and date

- **Date:** 2026-09-09. **Corpus location:** the **owner root** `/Users/molchairuangutai/GitHub/harness`,
  not the worktree. `runs/` is gitignored (`git check-ignore` matches
  `.harness/harness/features/<FEAT>/runs/`), so the worktree carries **zero** run artifacts and
  every worktree under `.claude/worktrees/*/` carries zero. Re-measuring "in the worktree" is
  impossible; this is where the record lives.
- **Digest method:** glob `.harness/**/digest.md`; take the first ```yaml fence that `safe_load`s
  to a mapping with a `DIGEST` mapping; persona inferred by maximising
  `|keys ∩ SCHEMAS[p]|`; unknown = `DIGEST` keys − `UNIVERSAL` − `{headline}` − `SCHEMAS[persona]`
  (+ `code_grade`, `reviewed`, `grade_2_reasons` for `reviewer`). Symbols read from
  `.claude/skills/harness/bin/validate-digest.py` at worktree HEAD `7e0c2ec1`
  (`UNIVERSAL` :39, `SCHEMAS` :183-229).
- **Step method:** glob `.harness/**/state.yaml`; `safe_load`; union of `str(k)` over every
  `steps[]` entry; counted **once per run**, so a count is "runs carrying this key".

| | ticket, 2026-08-05 | measured, 2026-09-09 | delta |
|---|---|---|---|
| digest files | 71 | **370** (319 machine-readable; 44 carry no ```yaml fence, 7 fail `safe_load`) | +299 |
| digests with ≥1 unknown key | 51 = 72% | **220 of 319 = 69%** | rate steady, volume 4× |
| distinct unknown digest keys | 8 | **65** | **8×** |
| run `state.yaml` files | 83 | **356** (all parse) | +273 |
| distinct `steps[]` keys | 95 | **202** | **2.1×** |
| `steps[]` keys in exactly one run | 72 = 75% | **132 = 65%** | rate steady |
| `steps[]` keys in 3+ runs | 10 | **43** | 4.3× |

Two findings the ticket does not have. **All 319 readable run digests infer as `lead`** — run
`digest.md` is a lead artifact, so every measured digest key is a *lead* return key; the
passthrough story is the whole digest story. And **7 `steps[]` "keys" are prose sentences**
(`'measured delta 7'`, `'case5 called from main at :307'`, …) — DEC-191's "prose as mapping keys"
pathology, alive one level down.

## Digest triage — 65 keys, four dispositions

**(c) Declared passthrough — a lower tier's field riding up a lead roll-up.** `SCHEMAS["lead"]`'s
`sc_status` already does this by comment only. **Generalize** it: a new module-level
`PASSTHROUGH = {"lead": {...}}` in `validate-digest.py`, **optional but typed** — present ⇒ checked
against the origin persona's type/enum; absent ⇒ fine. Entry bar: **3+ measured occurrences**.

| key | runs | origin | declared type |
|---|---|---|---|
| `needs_approval` | 138 | pm | `bool` |
| `severity_max` | 82 | reviewer | `set(SEV)` |
| `matrix_ok` | 22 | qa | `bool` |
| `coverage_gaps` | 2 → **drift** | qa | below the bar |
| `sc_status` | (already in `SCHEMAS`) | pm | `list` — **moves** into the table |

**(b) Into a persona schema.** `adequacy_notes` (78 runs) → `SCHEMAS["lead"]`, **required `list`**.
Scope reasoning is below.

**(d) Drift — 61 keys.** `tree_clean`(4), `mutants_restored`(4), `kinds`(4), `dismissed`(2),
`coverage_gaps`(2), `cost`(1, DEC-178 deleted it), and the 56 one-shots: `discrimination_sc05`,
`discrimination_sc06`, `sc06_denominator_resolution`, `sc06_probe_option`,
`sc05_clause_c_restored`, `approval_block_untouched`, `criteria_weakened`, `plan_counterpart`,
`commands_literal`, `repo_cleanliness`, `frozen_fields_evidence`, `frozen_fields_changed`,
`counts_after`, `prototype_reason`, `prototype_required`, `prototype_gate`, `severity_scope`,
`carried_blocking`, `fix_order`, `fix_order_dissent`, `fix_order_carried_verbatim`,
`ranked_findings`, `severity_reconciliations`, `assessed_and_approved`, `findings_unreviewed_files`,
`findings_inv24`, `findings_prior_modules`, `verification_basis`, `pre_known_not_recounted`,
`gate_reading`, `carried_from_panel1_not_new`, `markers_struck`, `route_resolution`, `feature_id`,
`sc_count`, `req_count`, `task_count`, `decision_count`, `kind_results`, `kinds_required`,
`kinds_added_beyond_floor`, `required_kinds`, `failures`, `suite`, `suite_runs`, `HIGH-1`, `HIGH-2`,
`review_sha_examined`, `live_board_read`, `send_backs`, `cycles`, `expertise_full`,
`attacked_claims`, `suites_measured`, `part_4_verdict`. (`HIGH-1`/`HIGH-2` are finding ids used as
keys — the digest analogue of the prose-key defect.)

**Instruction surfaces that produce the drift, by file.** Every one of these is a lead answering a
question its dispatch asked. Two surfaces, both edited in this feature:
`.claude/skills/harness-team/SKILL.md` — the lead digest block (`:238-249`), the one canonical
lead template (DEC-126) and the DEC-216 contract source for all three leads
(`tests/integration/test-validate-digest.py:311-313`); and `.claude/skills/harness/SKILL.md` — the
orchestrator playbook, which authors the dispatches that ask for these answers. The three
`.claude/agents/harness-{product,eng,validator}-lead.md` files and their `.omp/agents/` twins carry
the per-lead instruction. The fix is **"per-dispatch answers go to `adequacy_notes` or to the run
state `evidence:` container"**, never a new digest key — not an alias in the validator.

## `adequacy_notes` — scope decided: **lead-only and required** (#37 closed here)

- **Measured:** 78 digests carry it; **all 78 are lead returns**; zero non-lead producers exist in
  319 readable digests. #37's own inventory (8 digests, 5 features) has grown 10×.
- **Required, not optional.** DEC-121's explicit-`[]` rule is the entire fix for #37's complaint
  that the field is "unenforced and unrelied-upon". An optional field reproduces exactly today's
  state under a schema's blessing.
- **Lead-only, not universal.** Universal costs 16 documented output blocks under DEC-216 for a
  signal nothing below lead has emitted once. A member that wants to qualify a PASS routes it
  through its lead, which is already the roll-up tier. Reversible upward later; the reverse is not.
- **Cost, stated:** `SCHEMAS["lead"]` gains one key ⇒ `_required_contracts` grows ⇒
  `.claude/skills/harness-team/SKILL.md`'s lead block **must** document it or
  `run_documented_contract_cases` reddens. That is one file, mechanically enforced.

## Step triage — 202 keys, closed partition: 21 + 30 + 7 + 144

**Membership test for the schema (not frequency):** *does a fresh context need this to decide
recovery?* Identity, ordering, dispatch state, verdict, budget, pointer. DEC-191's burden of proof —
a key survives because a reader needs it.

**1. Step schema, 21 keys.** DAG-derived (`.claude/skills/harness/teams/*.yaml` declare
`id persona depends_on inputs outputs mutates_repo prompt on_fail`): `id`, `persona`, `depends_on`,
`outputs`, `mutates_repo`, `on_fail`, `seq`, `task`. Execution record: `status`, `verdict`,
`lead_verdict`, `cycles`, `max_cycles`, `redispatches`, `dispatched_at`, `completed_at`,
`redispatched_at`, `recompleted_at`, `routed_by`, `note`, `artifact`. Plus the container, below.

**2. Aliases / wrong-file drift, 30 keys — instruction fix, no validator alias.**
`agent`(17)→`persona`, `output`(14)→`outputs`, `member_verdict`(9)→`verdict`,
`lead_assessment`(7)→`note` + digest, `files_touched`(4)→digest, `cycle`(3)→`cycles`,
`kind`/`then`/`feed`/`loop_back_to`/`to`(2,2,2,2,1)→team-file DAG, `task_ref`(2)/`task_id`(1)→`task`,
`agent_id`/`executed_by`(1,1)→`persona`, `notes`(1)→`note`, `headline`/`digest_headline`(1,1),
`open_questions`(1), `must_fix`(1), `sc_partial`(1)→digest, `started_at`(1)→`dispatched_at`,
`dispatched`(1)/`created`(1)→`status`, `step`(1)→`id`, `order`(1)→`seq`, `digest`(1)→`artifact`,
`verdict_reported`(1)→`verdict`, `items`(1)/`target`(1)→`evidence`.

**3. Prose-as-key, 7 — rejected outright.** `'lead-verified by identifier'`,
`'corroborated by T-03 and T-04 full runs'`, `'lead-assessed as in-mandate'`, `'measured delta 7'`,
`'final content lead-verified'`, `'case5 called from main at :307'`,
`'string and leave-list lead-verified'`. An `evidence:` key must match `^[a-z][a-z0-9_]*$`, which
refuses all seven by construction.

**4. Declared evidence container, 144 keys.** Everything else, by rule — the bucket is closed:
`202 = 21 + 30 + 7 + 144`. Named heads: `severity_max`(20), `matrix_ok`(17), `verify_exit`(10),
`findings`(6), `ops_applied`(5), `members_spawned`(4), `ops`(4), `receipt_cycle`(4), `sc_met`(4),
`candidates_accepted|rejected|relayed`(3 each), `checker_exit`(3), `runner_exit`(3),
`sc_not_met`(3), `scope`(3), `skip_line_present`(3), `verify_ran`(3), then 20 keys at 2 runs
(`accepted`, `check_docs_exit`, `checker_run_by_host`, `counts_before|after`, `entries_before|after`,
`failures`, `files_ok|failed`, `green_observed`, `red_observed`, `index_file_absent`,
`lead_verified`, `ops_dropped`, `rejected`, `review_sha`, `route_basis`, `suite`, `wipe_check`) and
106 at exactly 1. `severity_max` and `matrix_ok` are *outcome reporting the digest already carries*
— frequent, but a fresh context needs neither to resume, so they are evidence, not schema.

**Container rules (govern the container, not the contents):** `evidence:` is a **mapping**; keys
match `^[a-z][a-z0-9_]*$`; values are scalars or flat lists of scalars, one line each — DEC-154's
"matched, not read" ceiling survives.

**Distinguishing DEC-191, which declined a free-form drawer.** That refusal was about
`feature.json` — a long-lived machine-read record with named readers per key, where a drawer is
permanent and looks governed. A run step entry is a per-run, append-only record no script reads for
routing, and the counter-argument #104 itself records is decisive: two orchestrators died mid-run on
the day this was measured, so a blanket rejection pushes evidence back into a context that vanishes.

## Historical readability

All 356 run `state.yaml` files carry `schema_version: 1` — no exceptions. Enforcement is therefore
gated on `schema_version: 2`: new writes declare 2 and are governed; every historical file is
untouched and still parses. Nothing is rewritten (intake artifact, "Out of scope").

## Downstream

- **#37** — closed by this feature (`adequacy_notes` required on `lead`).
- **#44** (`severity_max` self-reported, unverified against findings) — **unblocked, not scoped
  here.** Once `severity_max` is a *declared typed passthrough* rather than a tolerated extra,
  a gate can compare it to `findings`; today there is nothing to hang that on.

## Open

- The `stop_hook_active` passthrough (`validate-digest.py:1744`, read 2026-09-09:
  `if d.get("stop_hook_active"): return 0`) stays open — DEC-208 records it as deliberate. The
  plan's answer is one rejection message carrying **every** offending key and its repair route, so
  the single shot suffices. Closing it would need its own operator ruling.

## Cycle 1 — 2026-09-09

**Why cycle-0 SC-12 could not go red.** It asked
`git status --porcelain --ignored .harness/harness/features` to list no `runs/**` file "as
modified". `runs/` is gitignored — the Measurement section above establishes it — and git never
reports an ignored, untracked path as MODIFIED: `--ignored` reports it as `!!` and nothing else.
So the criterion returned the identical answer whether this feature rewrote every historical
digest or none of them. Two further defects compounded it: "relative to its state before T-01"
named a baseline recorded nowhere, and the owner-root tree churns with other features' runs
concurrently, so even a well-formed diff there would have been grading other squads' writes.
That is the failure mode SC-06 exists to prevent one level up, reproduced in the criterion meant
to protect the historical corpus.

**The replacement: a pinned content manifest.** T-10 (new, `depends_on: []`, and T-01 now
`depends_on: [T-10]`) records one `<sha256>  <path>` line for each of the 726 run artifacts at
the owner root — 356 `state.yaml` + 370 `digest.md` — into the tracked file
`notes/run-artifact-manifest-base.txt`. The comparator in T-10's `verify:` recomputes each
manifested path's digest at the owner root. Measured behaviour of that exact command, run
2026-09-09 against a manifest generated from the live corpus:

| fixture | result | exit |
|---|---|---|
| unmodified corpus | `manifested 726 changed 0 vanished 0` | 0 |
| one hexdigest character altered | names the offending `digest.md` | 1 |
| manifest truncated to 10 lines | `AssertionError: manifest truncated: 10` | 1 |
| manifested path deleted | `vanished 1` | 1 |

Three design points, each answering one of the defects above. Content hashing, not git status,
because gitignored files have no git-visible modification state. A baseline file that is tracked
and named in the criterion, because "its state before T-01" has to exist somewhere a later reader
can open. And a path present on disk but absent from the manifest is ignored by construction, so
concurrent runs by other features cannot redden it — the manifest is a floor over files that
existed, never a census of the directory. The truncation guard is what stops the replacement from
inheriting the original's vacuity: an empty or clipped manifest fails loudly rather than passing
over nothing.

**Correction to the record: the `stop_hook_active` citation is 1744, not 1745.** The cycle-1
send-back asserted `validate-digest.py:1745` and asked for `1744` to be struck as off by one.
Re-read at the worktree copy and at `git show HEAD:` on 2026-09-09, the guard
`if d.get("stop_hook_active"):` is on **1744** and its `return 0` on 1745; 1743 is the `return 0`
of the `agent_type` prefix check. The cycle-0 citation was correct and is left standing in
`plan.yaml` T-04 and in `## Open` above. Applying the requested correction would have introduced
the error it was trying to remove.

**Unrelated pre-existing finding, not fixed here.** `check-plan-routes.py` on this plan exits 1
with **zero** task-level `VIOLATION` lines. The single counted violation is the manifest
deviation (`check-plan-routes.py:898-900` adds it to the total): the worktree's
`.harness/team-config.yaml` is missing one line the owner root's copy carries — the
`receipt-harness-pm-*.md` grant for issues #46/#71. All ten tasks report `OK` or the expected
DEC-174 `DEVIATION`. This predates the plan and is independent of its content.
