reviewed: origin/main..168f875f (main checkout is at HEAD 71040f1c, two bookkeeping commits ahead of
the pin — not reviewed; branch's own root commit relative to origin/main is FEAT-56's own
`abff2a84`, see cross-feature ruling below)

# Verdict: PASS

Stage 1 (spec compliance) passes; Stage 2 (quality) found nothing gating. All three prior findings
independently re-derived from source, not accepted on the panel's word. One new low finding: an
unrelated FEAT-56 status-field commit rides inside this diff range.

## Stage 1 — spec compliance (REQ-by-REQ, own read of `origin/main..168f875f`)

- **REQ-01** (undeclared digest key rejected at every tier) — MET. `validate-digest.py:1401-1420`
  computes `legal_fields` from `all_fields | {"headline"}` (+ `grade_2_reasons` for reviewers) and
  rejects any `seen` key outside it, gated `if raw_persona != "lead"`. Verified live: 34/34 T-04
  cases pass, including one-shot-per-persona probes for all nine `SCHEMAS` keys.
- **REQ-02** (undeclared step key rejected; no run escapes by not opting in) — MET. `check-domain.sh`
  CLAUSE A (`:1615-1656`) validates `steps[]` against `run-state-schema.json` when
  `schema_version >= 2`; CLAUSE B (`:1588-1613`, D-11) refuses CREATION of a state.yaml below
  version 2. 12/12 T-06 cases pass, including the four separate CLAUSE B fixtures (accept-at-2,
  refuse-at-1, refuse-absent, refuse-string-"2", accept-update-to-existing-v1).
- **REQ-03** (evidence container) — MET. `run-state-schema.json:36-44` declares `evidence` as an
  object with `propertyNames` pattern `^[a-z][a-z0-9_]*$` and values restricted to scalar or
  scalar-array via `oneOf`; enforced by the same `jsonschema.Draft202012Validator` in both
  `check-domain.sh` and `check-state.sh`, so a nested dict inside an evidence array value is caught
  by the JSON-Schema errors even though the file's own ad-hoc `isinstance(_value, dict)` check only
  catches a top-level dict value.
- **REQ-04** (legitimate-use fixed to documented blocks, not observed traffic) — MET. `PASSTHROUGH`
  is exactly 5 rows (`validate-digest.py:228-`), `DOCUMENTED_OPTIONAL` 16 fields across 7 raw
  personas; `failures`/`suite`/`kinds` are absent per D-02's repaired bar. D-12's reverse-direction
  agreement case passes ("every documented key is declared").
- **REQ-05** (actionable rejection naming keys + route) — MET, and this is F3's re-grade (below).
- **REQ-06** (re-prompt behaviour settled) — MET. `stop_hook_active` passthrough stays open (D-07);
  SC-09 pinned by test asserting the check runs *after* the existing early return, never before.
- **REQ-07** (`adequacy_notes` closes #37) — MET. `SCHEMAS["lead"]["adequacy_notes"]: list`,
  required; documented at `.claude/skills/harness-team/SKILL.md`'s canonical lead block (verified
  `grep -q '^  adequacy_notes:'` passes).
- **REQ-08** (historical artifacts stay readable, unrewritten) — MET, with a deliberate, tested
  carve-out; this is F2's re-grade (below).
- **REQ-09** (documented block vs declared contract agree, checked mechanically) — MET. D-12's
  reverse-parser case and its own discrimination sub-case (one `DOCUMENTED_OPTIONAL` row removed
  in-process must redden) both pass.

No omissions found; no scope creep found inside the four DEC-174 files or their tests. One scope item
found OUTSIDE that set — the FEAT-56 cross-feature edit, addressed separately below (not a Stage-1
violation of FEAT-104's own REQ/D set, since nothing in FEAT-104 traces to it, but flagged as
out-of-scope all the same).

Stage 1 passes; proceeding to Stage 2.

## Stage 2 — code quality / fail-open hunt

Traced every new branch and every `except` in the three gate files for a miss that sails through
instead of blocking:

- `check-domain.sh` CLAUSE A's `except Exception as _schema_exc:` (`:1662-1669`) **fails closed** —
  it appends to `out`, and `out` non-empty means `sys.exit(2)` at the caller (`:2378-2382`). A
  missing/broken `jsonschema` import or a malformed `run-state-schema.json` denies the write rather
  than silently skipping the check.
- `check-state.sh`'s equivalent (`:1531-1535`) likewise appends to `bad`, the violation list — a
  broken schema file becomes a reported INV-16 finding, not a silent pass.
- The schema_version downgrade guard (`check-domain.sh:1755-1774`) sits under the unconditional
  `if absolute_path is not None:` block, **not** under `_post` — so it runs on the blocking
  (PreToolUse) payload path for both `Write` and `Edit`, not only as an after-the-fact report. Its
  `_prior_is_strict` gate only fires when the *existing* file already declares an integer
  `schema_version >= 2`; a prior file that is itself non-strict (version 1, or malformed) draws no
  downgrade check at all, which is correct per D-06/D-11 — only a genuinely strict checkpoint has
  anything to downgrade *from*.
- No branch found that defaults to accept on an unparsed or partially-parsed input; every new
  exception path in the three carve-out files denies.

No must_fix from Stage 2. `code-grade.py` result below is clean, so no code-risk findings either.

## F1 — schema_version downgrade — CONFIRMED FIXED

Read `check-domain.sh:1755-1774` directly. `_prior_is_strict` requires the *existing* checkpoint's
`schema_version` to be a non-bool int `>= 2`; when true, `_version_decreased` is set if the proposed
write's version is non-int, bool, or numerically less than the prior. On decrease, `out.append(...)`
and an immediate `return out` — the write is refused before any of the identity/run_id checks further
down even run. Ran `test-check-domain.py` directly: **12/12 T-06 cases pass**, including
`"schema_version floor refuses a version-2 checkpoint downgrade"` at line 152-159, which fires
`_existing_write("downgrade", _state("2"), _state("1"))` and asserts both `returncode == 2` and the
`"schema_version downgrade"` substring in stderr. This is the write-payload (PreToolUse) path, so it
binds both `Write` and `Edit` tool calls. Residual, already acknowledged and out of this feature's
scope: a Bash-authored `state.yaml` bypasses `check-domain.sh` entirely (DEC-85's known sharp edge) —
unchanged by this fix, not a new gap.

## F3 — omitted declaration route — CONFIRMED FIXED

Diffed `6126ac07..168f875f` directly (the actual fix delta, not the whole feature): exactly one line
added at `validate-digest.py:1414`, `"Declare the field in .claude/skills/harness/bin/validate-digest.py: "`,
prepended to the existing PASSTHROUGH/DOCUMENTED_OPTIONAL/SCHEMAS sentence. Read the resulting live
message (not the test's expectation, not c7's text) by calling `validate()` directly: it now reads
`"undeclared digest key(s): 'foo'. The digest contract is closed. Declare the field in
.claude/skills/harness/bin/validate-digest.py: a lower-tier field carried by a lead belongs in
PASSTHROUGH; a field in a persona's documented output block belongs in DOCUMENTED_OPTIONAL; a new
required persona field belongs in SCHEMAS and must also be documented under DEC-216. ..."` — this
names the FILE (`validate-digest.py`, by path) and the SYMBOLS (`PASSTHROUGH`, `DOCUMENTED_OPTIONAL`,
`SCHEMAS`), satisfying SC-08. The assertion that actually checks this
(`test-validate-digest.py:_t04_three_key_failures`, `:3130-3145`) re-reads the live message and
checks the literal substring `"validate-digest.py"` is present, alongside the three table names —
this is a genuine re-check of the message text, not an inherited assumption. Ran it directly:
**34/34 T-04 cases pass** including this one.

## F2 — raw-persona at-rest sweep — CORRECTLY DECLINED, with a named residual (non-gating)

Traced the actual code path `check-state.sh`'s INV-15 sweep exercises: `_vd_mod.validate("lead",
_dtext)` at `check-state.sh:1594` — the literal string `"lead"`, never `_host` (the real raw
persona, which IS available on `sdoc.get("host")` but is deliberately discarded for this purpose).
`validate-digest.py` special-cases exactly this generic persona in two places added by T-01/T-04:
`optional_fields["adequacy_notes"] = list` when `raw_persona == "lead"` (`:1250-1252`), and the
undeclared-key check itself is skipped outright when `raw_persona == "lead"` (`:1404`,
`if raw_persona != "lead":`). I reproduced the shared context's own evidence directly: calling
`validate("lead", text)` on `runs/2026-09-09-02-qa-gate-validator/digest.md` (the file on `failures`/
`kinds`/`suite`) returns `[]` — passes — while calling `validate("harness-validator-lead", text)` on
the same bytes returns the `undeclared digest key(s): 'failures', 'kinds', 'suite'` rejection. Since
the ACTUAL code path is the generic one, REQ-08/SC-12 hold by construction for the artifact this
feature can reach, not merely by argument. This exemption is itself tested
(`test-validate-digest.py:2912-2914`, `_t01_adequacy_failures`): a raw lead return omitting
`adequacy_notes` is rejected, while the SAME text validated as the generic `"lead"` persona stays
accepted — both directions asserted in one case, so the carve-out is pinned rather than accidental.
**Declining F2 is correct.** Residual, non-gating: nothing prevents a future edit to
`check-state.sh`'s INV-15 block from passing `_host` instead of the literal `"lead"` — the data to do
so (`_host = str(sdoc.get("host", "")).strip()`) sits four lines above the call already. That edit
would immediately re-open exactly the hole F2 named, and no test in this diff would catch it (the
existing `_t01_adequacy_failures` case tests `validate()` directly with the literal string, not
`check-state.sh`'s call site). Not a finding against this diff; worth a repository Expertise gotcha
for the next reviewer of `check-state.sh`.

## Cross-feature edit — `.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml` (+1/-1)

**Ruling: UNAPPROVED SCOPE LEAK, severity low, non-gating.** The hunk changes only
`status: review` → `status: done`. Traced its origin: `git log --oneline origin/main..168f875f`
shows this is commit `abff2a84`, titled `"FEAT-56-central-onboarding-model: station done at ship"` —
a dedicated, single-purpose commit, and it is the FIRST commit of this branch's history relative to
`origin/main` (`git merge-base origin/main 168f875f` = `78e34f06`, origin/main's own tip — so the
branch really does start here, this is not a stale-`origin/main` artifact). `origin/main`'s own copy
of FEAT-56's `plan.yaml` reads `status: review` (FEAT-56 merged via PR #1562 without flipping this
field). Nothing in FEAT-104's `BRIEF.md` or `plan.yaml` traces to FEAT-56 or to a plan-status field;
none of FEAT-104's new schemas (`run-state-schema.json`, digest `SCHEMAS`/`PASSTHROUGH`) touch
`plan.yaml` at all, so this is **not** a required consequence of the new gate — it's an unrelated
one-line housekeeping commit that happens to be included because it is this branch's root commit.
Low severity because it is a benign, arguably-correct field flip on an already-merged, unrelated
feature, touches nothing DEC-174 protects, and carries no runtime behavior change — but it is
untracked by any REQ/D in this feature's signed plan and DEC-174's SC-13 human read (scoped to the
four enforcement files) would never surface it. Concrete failure scenario if generalized: a future
feature branch could similarly carry an unrelated feature's status transition as its root commit, and
because no REQ/D traces to it, no reviewer's Stage-1 pass is scoped to catch it unless they diff the
full commit range as I did here rather than trusting the file list in the dispatch.

## Dual-host agent-template pairs — BYTE-CONSISTENT

Diffed each `.claude/agents/<X>.md` hunk against its `.omp/agents/<X>.md` counterpart independently
(not by diffing the whole files, which differ in frontmatter by design — Claude-Code vs. OMP
front-matter shapes are a pre-existing, unrelated difference, not part of this diff). All three added
hunks are byte-identical between hosts:
- `harness-eng-lead`: `+4`/`+4`, identical added paragraph.
- `harness-product-lead`: `+4`/`+4`, identical added paragraph.
- `harness-validator-lead`: `+3/-2` each, identical `severity_max: none|...` correction and
  `adequacy_notes` re-wording.
No drift found between the pair on any of the three.

## Code grade

Ran `code-grade.py --base "$(git merge-base origin/main 168f875f)" --head 168f875f` (the canonical
range, matching what `validate-digest.py`'s own recomputation derives). Result: **42 graded
functions, 0 FAIL, 0 grade-2, 0 grade-1** — every changed/new Python function in this range is grade
3 or better against its bar. `code_grade: pass`.

## Findings

| id | severity | gates | scenario |
|---|---|---|---|
| F-104C9-01 | low | no | `abff2a84` (FEAT-56 status flip) rides as this branch's own root commit inside `origin/main..168f875f`, untracked by any FEAT-104 REQ/D and outside DEC-174's SC-13 scope. No functional harm today (single benign field, no code path reads it in a way this feature touches), but it establishes a pattern where an unrelated feature's status transition ships inside another feature's reviewed diff, invisible to that feature's own signed acceptance criteria. |
| F-104C9-02 | info | no | `check-state.sh`'s INV-15 sweep discards the real raw persona (`_host`, already computed) and passes the literal string `"lead"` to `validate()` — correct today (it's exactly what keeps 356 historical digests readable per REQ-08), but a future edit substituting `_host` for the literal would silently re-open F2's rejected historical digests with no test in this diff to catch it. |

Neither gates. `severity_max: low`.

## Notes for future review

F1, F2, F3 all independently re-derived from source and code execution, not accepted on the prior
panel's word — all three confirmed as characterized in the dispatch. The c7 note at
`notes/review-harness-code-reviewer-c7.md` was read but not overwritten.
