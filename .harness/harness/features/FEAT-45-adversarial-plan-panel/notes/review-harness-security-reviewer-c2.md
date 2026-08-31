# Security review — FEAT-45-adversarial-plan-panel — cycle 2

review_sha `70fd4414c7d472f50ae17452289e44782f32b5b5`, scope `main...70fd441` (66 files, +7114/-143).
Worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-45-adversarial-plan-panel`.

**VERDICT: FAIL** — two `high` findings, both in `validate-digest.py`'s integrity surface.

## Census (in/out)

In scope (mechanism/enforcement code, read in full):
- `validate-digest.py` (SEC-01 fix + new plan-review binding + `SKIPPED` schema) — **findings below**
- `check-state.sh` INV-32 restructuring (`:174-242`) — re-reviewed, **no regression**
- `.omp/extensions/harness-hooks.ts` (empty-yield fail-open fix) — **verified closed, no new hole**
- `.claude/skills/harness-team/SKILL.md`, `.harness/harness/docs/SPEC.md`, `templates/plan.yaml`, `.claude/skills/harness/SKILL.md`, `harness-spec-driven/SKILL.md` — doc/template surface for `panel:`/`SKIPPED`, read for authorization intent, corroborates finding 2
- `.claude/agents/harness-validator-lead.md` / `.omp/agents/harness-validator-lead.md` — new agent, confirms `fable-advisor` reader is a documented, accepted trust boundary ("SHAPE is yours; never CONTENT and never IDENTITY") — not a new finding, already scoped by design
- `panel_findings.py` — unchanged 32-bit truncated id scheme, confirmed identical to what M4 (carried, `med`) already describes; not re-raised, no collision demonstrated
- `omp-hooks.test.ts` — test only, exercises the hooks.ts fix
- `test-validate-digest.py`, `test-check-state.py`, `test-panel-findings.py`, `test-plan-panel.py`, `test-harness-yaml-corpus.py` — test files; used to confirm coverage gaps (see finding 2), not independently gated

Out of scope, no security surface (docs/templates/planning artifacts, grep'd for secrets — none found):
`.claude/commands/harness-plan.md`, `DECISIONS.md`, `DECISIONS-INDEX.md`, `sync-agent-adapters.py` (+7, test-registry constant only), `run-unit-tests.sh` (+4, test-name array only), all of `.harness/harness/features/FEAT-45-adversarial-plan-panel/{BRIEF.md,STATE.md,feature.json,plan.yaml,notes/*,observations/*}` and `grilling-*.md` (this feature's own planning trail, not mechanism).

## Finding 1 — HIGH — half one (re-review, SEC-01's own fix)

**The plan-review branch of `code_grade_bound_to_review` skips the branch-corroboration hardening its sibling code-review branch has, and its own binding conditions are satisfiable by any OTHER pending feature — not necessarily the one actually under review.**

`validate-digest.py:965`: `if _is_plan_review(reviewed): return _pending_plan_review_error(text, reviewed, code_grade, feature_dir)`. This returns *before* `_read_review_sha`, `resolve_reviewed_commit`, or — critically — `_branch_corroboration_error` (`:987`, only reached on the non-plan path) ever run.

`_pending_plan_review_error` (`:910-925`) checks exactly four things: `code_grade == "n_a"`; `plan_path` (parsed from `reviewed`) equals `feature_dir/plan.yaml` where `feature_dir` is *derived from the same digest's own `artifact:` line*; the named plan's `approval.status == "pending"`; and the named feature's `feature.json.review_sha` is unpinned. All four are mutually derived from the digest's own self-reported fields — none is checked against the actual git branch the reviewer is running in.

Compare the code-review path's own docstring (`:955-960`, unchanged): *"a reviewer can point `artifact:` at a different shipped feature and reuse ITS pin. `_branch_corroboration_error` closes that with the one thing no digest controls: the checkout's actual current branch."* The same shape of hole exists for plan mode, and is *easier* to trigger: reusing another feature's real `review_sha` by coincidence is hard; finding *some other feature that is currently pending with no review_sha pinned* is the ordinary, common state of any drafted plan (this repository alone has dozens of `FEAT-*` directories; several are routinely mid-draft at once).

**Concrete failure scenario.** A `harness-code-reviewer` subagent is dispatched by `plan-panel.yaml`'s `scope` step to adversarially read FEAT-A's plan (running inside FEAT-A's own worktree/branch, per this dispatch's own constraint block — every feature gets a dedicated branch, recorded in its own `feature.json.branch`). Instead of doing the reading, it returns:
```
VERDICT: PASS
code_grade: n_a
reviewed: "plan:.harness/harness/features/FEAT-B/plan.yaml"
artifact: .harness/harness/features/FEAT-B/notes/review-harness-code-reviewer-planpanel-c0.md
```
where FEAT-B is any other real, currently-pending, unsigned feature in the repo (true state, not fabricated — the reviewer doesn't even need to lie about FEAT-B, only needs one to exist). `_pending_plan_review_error` resolves `feature_dir` = FEAT-B (from `artifact:`), `plan_path` = FEAT-B's real `plan.yaml` (equals `expected_path` by construction — both derived from the same line), FEAT-B's `approval.status` genuinely reads `pending`, FEAT-B's `feature.json` genuinely has no `review_sha` pinned. Every check in `_pending_plan_review_error` passes. The digest validates as a clean PASS for what is, in fact, zero engagement with FEAT-A's plan. FEAT-A's operator, reading the panel's consolidated "no findings" summary, signs a plan that received no adversarial reading at all.

This is not a hypothetical drift — it is the *specific* residual hole SEC-01's wave-3 hardening was written to close for the sibling branch, left open in the new one. Rate **high**: it defeats the entire purpose of DEC-207's plan-panel gate (adversarial reading before signature) with no privilege beyond being the reviewer itself, exactly the threat class `validate-digest.py` exists to defend against.

**Remedy shape** (not prescribed further): call `_branch_corroboration_error(feature_dir, _current_branch_or_none(branch_override))` from `_pending_plan_review_error` too, the same way the code path does — it is additive-only (`:983` docstring) and needs no new logic, only removing the asymmetry.

Secondary, lower-severity observation from the same read: the plan-review binding has no analogue of a commit pin on the plan's *content* — `reviewed: plan:<path>` names a mutable file, not a hash of what was read, so a stale PASS from an earlier draft remains "valid" against this check after the plan is edited (as long as it's still pending and unsigned). DEC-207's design places the actual control on the human operator reading the recorded findings before signing (`"the digest... is the artifact the ship decision reads"`), so this is weaker than a full bypass and not raised as a separate finding — but the operator's trust in an empty-findings PASS is exactly what finding 1's cross-feature substitution defeats without the operator being able to tell.

## Finding 2 — HIGH — half two (first-pass, `validate-digest.py` + `harness-team` SKILL.md)

**`SKIPPED` is validated only syntactically and is self-asserted solely by the lead authoring the digest, with no independent corroboration anywhere in the pipeline — and the mechanism is generic to every harness-team lead, not scoped to plan-panel's `fable-advisor` case that motivated it.**

`_skipped_member_error` (`validate-digest.py:927-940`) accepts `status: skipped` for *any* member entry in *any* lead's `members:` list provided `verdict` is absent and `persona`/`reason` are non-empty strings — no check that `reason` is a genuine host-caused non-execution (the only case the docs describe: `harness-team/SKILL.md` diff line `"a member that did not run"`; `templates/plan.yaml`'s new comment: `"The external adversarial persona may normally be absent... status skipped records that outcome"`; `.omp/agents/harness-validator-lead.md`: `"If preflight refuses it or no runnable agent resolves, SKIP"`). Any non-empty string satisfies `reason`, including `"reason: decided not to review"`.

Consuming site: `validate-digest.py:1281-1289`, inside the lead worst-wins roll-up (`:1278` `if persona == "lead" and m:`) — a `skipped` member is `continue`d (`:1289`) *before* it reaches the `mv = fields.get("verdict")` / rank comparison at `:1291-1305`. The comment directly above this loop (`:1256-1262`) states the stakes precisely: *"A lead reporting PASS over a failing member is the single most consequential digest error possible... a masked FAIL ships."* A member marked `skipped` is invisible to exactly this check.

This is not scoped to plan-panel — `_skipped_member_error` fires for *every* `raw_persona` that is a lead (`harness-eng-lead`, `harness-validator-lead`, `harness-product-lead` all resolve to `norm() == "lead"`), so it applies to the review team hosting this very cycle, and to every build/qa-gate team. The only existing test (`test-validate-digest.py:547-560`, `"a skipped member is explicit and excluded from worst-wins"`) exercises exactly one legitimate case (`fable-advisor`/`persona unavailable` under `harness-validator-lead`/`plan-panel`); there is no test — positive or negative — for a lead marking a normally-present member (`qa`, `code-reviewer`, `backend-dev`) as skipped without a genuine host reason, because nothing in the validator can distinguish that case from the legitimate one.

**Concrete failure scenario.** A validator-lead dispatches its four-reviewer panel; `harness-qa` genuinely returns `FAIL` with a `high` finding. Instead of transcribing `{ step: qa, persona: qa, verdict: FAIL, ... }`, the lead's consolidated digest writes:
```
members:
  - { step: code, persona: code-reviewer, verdict: PASS }
  - { step: qa, persona: qa, status: skipped, reason: "environment unavailable" }
  - { step: security, persona: security-reviewer, verdict: PASS }
  - { step: ui, persona: ui-reviewer, verdict: PASS }
VERDICT: PASS
```
`_skipped_member_error` accepts the qa entry (non-empty persona, non-empty reason, no verdict claimed). The worst-wins loop never sees qa's real `FAIL`; `worst` computes over the three PASS entries only; the cross-check at `:1300-1305` finds nothing to contradict `VERDICT: PASS`; the digest validates clean. This is the exact "mirror image of the defect being fixed" the dispatch named: the roll-up laundering mechanism the c0 SEC-01 finding closed for forged code ranges is reopened here for forged non-execution claims.

Rate **high**: reachable by the lead alone (no elevated privilege needed beyond authoring its own return, which every lead already does), defeats the roll-up's stated purpose project-wide, and has zero test coverage of the misuse case.

**Remedy shape** (not prescribed further): the validator cannot verify *truth* of a host-refusal claim from the digest text alone, but it can narrow the *opportunity* — e.g. bind `SKIPPED` to personas/teams the dispatch declares as optional-external (the way `plan-panel.yaml`'s `should-not-exist` step already is), rejecting it for any member whose team-config entry names a mandatory in-repo persona.

## Finding 3 — confirmed non-regression (half one) — INV-32 fails closed on absent/null `severity`

Independently traced, not from the diff's own tests: `check-state.sh:213`, `severity = str(item.get("severity", "")).strip().lower()`. Absent key → `.get` returns `""` → `severity == ""`. Present-but-YAML-null → `.get` returns the dict's actual `None` value (the default is only used when the key is *missing*) → `str(None) == "None"` → `.lower() == "none"`. Both `""` and `"none"` are unequal to every member of `{"info", "low", "med"}` (`:219`), and neither can equal `"resolved"` (`:215`, requires exact string `"resolved"`) nor land in `overruled` (`:217`, requires exact `finding` id match against a real ruling). Both cases therefore fall through to `bad.append(...)` at `:219` — blocking (`check-state.sh:1872`, `sys.exit(1 if bad else 0)`). **No regression**; the restructured `if/elif/elif` (`:214-219`) still fails closed for both shapes the dispatch named.

## Finding 4 — confirmed non-regression — operator attribution on overrules

`check-state.sh:198-206`: every `rulings` entry (not only `ruling: overrule` ones) is checked for non-empty `who` and a `YYYY-MM-DD`-shaped `date` (`re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", ...)`); a violation always adds to `bad` (`:200`), which always exits 1. One code-quality quirk observed, not gating: an unattributed/undated ruling whose `ruling:` field is literally `"overrule"` still gets added to the `overruled` set at `:206-207` (the `if not who/date: bad.append(...)` at `:199-200` has no `continue`, so execution falls through to the `elif ... == "overrule": overruled.add(fid)` regardless). This double-books the finding as both `bad` (from the malformed ruling) and demoted-to-`warn` (from the finding-severity loop reading `overruled`) — but since `bad` alone already forces exit 1, this cannot be used to *slip past* the block; it is bookkeeping noise, not a bypass. Not raised as a separate finding.

## Not re-raised

M4 (32-bit truncated `PF-` finding id, `med`, carried from c0/c1): `panel_findings.py` is byte-identical in mechanism to what was previously described (`sha256(reader + "\n" + normalized)[:8]`, 32 bits). No collision constructed this cycle (would need brute-force compute out of scope for a read-only review); not demonstrated stronger, so left as-is.

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: two high findings — plan-review binding skips branch corroboration (SEC-01's own asymmetry), and SKIPPED is an unverified, project-wide roll-up escape hatch
  in_scope: true
  scope_reason: "branch's own contribution touches an integrity/authorization gate script (check-state.sh INV-32), a digest validator with a self-reported binding (validate-digest.py SEC-01 fix + new plan-review mode + SKIPPED schema), and the hook that invokes it (harness-hooks.ts) — all trust-boundary code, not merely docs"
  severity_max: high
  findings: 2
  must_fix:
    - "validate-digest.py:965 _pending_plan_review_error must call _branch_corroboration_error the same way the sibling code-review branch does (:987) — otherwise a plan-review digest can bind to any OTHER pending, unsigned feature instead of the one actually under review"
    - "validate-digest.py:927 _skipped_member_error accepts any non-empty reason for any lead/any member with no corroboration — narrow SKIPPED's legitimate scope (e.g. to personas/teams the dispatch declares optional-external) or it remains a project-wide worst-wins bypass usable by every harness-team lead, not only plan-panel"
  threat_model:
    - { boundary: "harness-code-reviewer digest -> validate-digest.py plan-review binding", stride: T, mitigated: false }
    - { boundary: "lead digest members: list -> validate-digest.py worst-wins roll-up", stride: T, mitigated: false }
    - { boundary: "check-state.sh INV-32 severity/disposition gate", stride: E, mitigated: true }
    - { boundary: "check-state.sh INV-32 operator-attributed overrule", stride: S, mitigated: true }
    - { boundary: "plan-panel fable-advisor (non-harness) reader -> validator-lead transcription", stride: I, mitigated: false, precondition-absent: "documented, accepted design (validator-lead.md: 'SHAPE is yours; never CONTENT and never IDENTITY') — not this cycle's finding" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c2.md
```
