# FEAT-45 — code review, cycle 4 (FINAL)

Pin: `bdd566679377eb5a55d1092064fe444e86d2f49f`. Scope: `git diff 302ae9d bdd5666` (the B-1
width-widening delta: `panel_findings.py`'s `PF-` id widened `digest[:8]`→`digest[:32]`, 11→35
chars) plus its regression impact across the feature's full contribution
(`git diff main...bdd5666`, 78 files). Broader feature not re-reviewed — clean across c0–c3.

## VERDICT: PASS. No must_fix. All findings are IMPROVEMENT (backlog), none reachable by any gate.

## Stage 1 — spec compliance

`git diff 302ae9d bdd5666` touches exactly 3 functional/plan paths (plus two `ship-review` notes,
not spec-bearing): `panel_findings.py`, `test-panel-findings.py`, feature `plan.yaml`. Read all
three at the pin (`git show bdd5666:<path>`).

- `panel_findings.py:29,33` — docstring "first 32 characters ... Length 35" and code
  `return f"PF-{digest[:32]}"` **agree**: `3 + 32 = 35`. Verified live:
  `panel_findings.py id --reader scope --summary 'T-04 traces REQ-99, which does not exist'` →
  `PF-87ea6603a72829829a3983c3c766f884` (35 chars). No mismatch.
- `plan.yaml:157-158` (D-05's `choice:`) says "the first 32 hex characters of sha256" — matches
  the code exactly. D-05 and the code **agree** on the width.
- `test-panel-findings.py` case1/case6 assertions updated in lockstep (`len(fid) == 35`,
  `len(hexpart) == 32`, hex-charset check) — traces to the same D-05.
- No scope creep: every changed line in the 3-file delta serves this one width change. No
  omission: nothing else in this narrow delta needed touching for D-05 to hold.

**Suite corroboration**, re-run directly at the pin (not restated from the dispatch):
`test-panel-findings.py` 9/9 PASS; `run-unit-tests.sh --kind unit` rc=0, 0 `^FAIL `, matches
main's reported 433-line, no-KIND-DRIFT numbers. `code-grade.py --base 302ae9d --head bdd5666`:
`PASSING: 0`, exit 0, no `SEVERITY`/`RESULT: FAIL` lines — the delta touches no function whose
shape changed (a literal `8`→`32` inside an unchanged control-flow body), so nothing gates on
grade.

## Stage 2 — code quality on the delta

The delta is a single-literal width change plus matching docstring/test-assertion updates; no
new branches, no new I/O, no new error path. `digest[:32]` against a 64-char sha256 hexdigest
cannot raise or truncate short (Python slicing never IndexErrors) — no fail-open introduced.
`normalize_summary`/`finding_id`'s existing validation (empty reader, whitespace-only summary →
CLI exit 2) is untouched by this delta. Nothing to flag here.

## Stage 3 — the stale-width dependency hunt (the substance of this cycle)

Searched the full feature contribution (`git diff main...bdd5666`'s 78 files, read at the pin —
worktree HEAD `a44eb57` differs from the pin only in `feature.json`, confirmed via
`git diff bdd5666 a44eb57 --stat`) for hardcoded lengths (`11`, `8`, `== 11`, `test N -eq`),
slices (`[:8]`, `[3:11]`, `cut -c`, `substr`), id-shape regexes (`PF-[0-9a-f]{8}` and kin), and
any fixture/doc/template carrying an 8-hex `PF-` example. Repo-wide `grep` for `PF-` (not
diff-scoped) across the whole worktree, plus targeted greps for slice/length idioms in every
functional file the full contribution touches (`check-state.sh`, `validate-digest.py`,
`sync-agent-adapters.py`, `test-check-state.py`, `test-harness-yaml-corpus.py`,
`test-validate-digest.py`, both `harness-validator-lead.md` copies, `harness-spec-driven/SKILL.md`,
`harness-team/SKILL.md`, `harness/SKILL.md`, `teams/plan-panel.yaml`, `templates/plan.yaml`,
`DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`).

**Zero functionally binding hits.** `check-state.sh`'s INV-32 treats the `id` field as an
**opaque string** throughout (`str(item.get("id","")).strip()`, membership tests against a set) —
confirmed by reading the INV-32 block (`:174-242`): no length check, no regex, no slice anywhere
in it. `test-check-state.py`'s INV-32 fixtures (`PF-deadbeef`, `PF-cafebabe`, `PF-unrated`, etc.)
are opaque test literals that never round-trip through `finding_id()`, so they are unaffected by
width. The live pm-facing instruction that actually governs how a real id gets into a real plan —
`harness-spec-driven/SKILL.md:109-110`, "Compute every id with `panel_findings.py id --reader <r>
--summary <s>`; never type it." — carries **no width** at all, so it cannot be stale and nothing
downstream of it can be misled by width. `teams/plan-panel.yaml:58` and both
`harness-validator-lead.md` copies (`.claude/agents`, `.omp/agents`) state "does not assign PF-
ids" / "Never assign a PF- id" with **no width mentioned** — these are the shipped, live-loaded
surfaces T-04/T-06's task intent (plan.yaml:473,773) *describes*, and the implementer correctly
did **not** propagate the width detail into them. `code-grade.py` and `validate-digest.py`
likewise never reference the id's shape.

Three prose/example sites remain stale, **all cosmetic — plan-history or a template example, none
executed, none gated**:

- **`plan.yaml:473`** ("A lead that invents an **8-hex** string...") and **`plan.yaml:641`** ("id
  PF- plus **8 hex**, produced by panel_findings.py, never typed") — both inside other tasks'
  (T-04, T-05) `intent:` prose, describing what should be written into shipped files. Checked the
  actual shipped files those intents produced: neither carries the "8-hex" wording (confirmed
  above). **Only the plan's historical task-assignment text is stale; the shipped surfaces it
  describes are not.** COSMETIC.
- **`plan.yaml:1019,1031,1052`** (T-09's own `verify:` clause `test 11 -eq "${#A}"` and `intent:`
  "first 8 characters... Total length 11" / "PF- plus 8 lowercase hex, length 11") — T-09's own
  frozen build-time instructions for the task that is the actual site of the width change. See T-09
  grading below. COSMETIC (not executed), but the record inconsistency is real.
- **`.claude/skills/harness/templates/plan.yaml:56`** (`id: PF-0123abcd`, 8 hex) — added by this
  same feature's earlier commit `7ee3f65` (confirmed via `git log`), **untouched by the B-1
  delta**. This is the generic template every future feature's `plan.yaml` is scaffolded from, so
  it is genuinely operator/pm-facing and copyable. Judged whether copying it produces a broken
  plan: it does **not** — `harness-spec-driven/SKILL.md`'s live instruction (above) tells pm to
  compute every id via the script and never type it, and no invariant validates id shape (INV-32
  is opaque-string), so a stale example here cannot itself break a signed plan or fail a gate.
  It is a genuine but low-stakes documentation drift: the highest-leverage of the three because it
  is prescriptive, not retrospective, but still COSMETIC by the "does copying it break a run"
  test — nothing consumes this literal string as code.

No hit beyond the three sets above, and beyond what the lead's own pre-reads already named — this
review corroborates rather than extends the list. `STATE.md:41-43` also carries a stale
`digest[:8]` reference (harness-security-reviewer's now-resolved M4 recommendation) and
`ship-review-2026-08-31.md`'s B-1 row was correctly struck by this same delta — noted for
completeness but outside code-reviewer's domain (STATE.md is validator-lead's own artifact, not
part of the 3-file functional delta).

## T-09 record-inconsistency verdict: BACKLOG, not gating

**Reasoning.** `check-state.sh` (read in full for `verify` handling) never executes or replays a
task's `verify:` shell text — its ~1800 python lines are static analysis over `plan.yaml`'s
structure and cross-file greps; the only place `verify` appears is a corpus test asserting the
YAML field exists and is a string (`test-harness-yaml.py:637`), never that it's *true*.
`run-unit-tests.sh` runs the registered test **scripts** (`test-panel-findings.py`, which is
correctly updated and green), not the plan's prose `verify:` field. No invariant, hook, or QA-gate
mechanism in this repo replays a `done` task's `verify:` clause. I ran T-09's literal verify
clause by hand at the pin as ground truth (not to prove a gate — to confirm the premise): it
**fails**, `rc=1`, actual id length 35 not 11, matching the lead's pre-read exactly.

Given nothing re-runs it, T-09's stale `verify`/`intent` text cannot redden CI, cannot block
signature, and cannot silently ship a defect — it is inert historical narrative on a task already
`done`, describing what was true when T-09 was built and superseded by this delta's own code
change without a matching plan-text update. That is a genuine record-hygiene gap (the "Never
falsify the record" principle argues for keeping it accurate) but it is not a live functional
risk today. **Graded BACKLOG**: worth a cheap follow-up sweep of `plan.yaml:473,641,1019,1031,1052`
and `templates/plan.yaml:56` to keep the plan self-consistent with D-05, not a `must_fix` that
should block this final cycle over unexecuted prose with the panel's own last cycle available.

One forward-looking note, not a finding: if a future `check-state.sh`/qa-gate revision ever adds
"replay a done task's `verify:` clause" (plausible given this feature's own theme — making plans
honest), T-09's clause is a landmine that will immediately misfire. Recording this so the backlog
sweep, whenever it happens, catches the clause too and not just the prose.

## Corroboration

Independently reproduced against `Feat45Build.InsufficientGoat.QaC4`'s
(`review-harness-qa-c4.md`) and `Feat45Build.InsufficientGoat.UiC4`'s
(`review-harness-ui-reviewer-c4.md`) notes, both already on disk at this pin: same 3 stale-site
set (`:473`, `:641`, T-09's verify/intent, `templates/plan.yaml:56`), same live id
(`PF-87ea6603a72829829a3983c3c766f884`), same "opaque string, no gate replays verify" conclusion,
same IMPROVEMENT-not-DEFECT grading. No new site found beyond what both peers and the lead's
pre-reads already named — this note is the code-quality-lens confirmation both peers explicitly
routed to.

```yaml
VERDICT: PASS
DIGEST:
  headline: "D-05 and code agree on 32-hex/35-char width; delta introduces no fail-open and grades clean; three cosmetic stale-width prose/template sites found (plan.yaml:473,641,1019/1031/1052, templates/plan.yaml:56), all opaque to every live gate — backlog, not must_fix."
  severity_max: none
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: "302ae9d..bdd5666"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Backlog sweep: update plan.yaml:473,641,1019,1031,1052 (stale 8-hex/length-11 prose in T-04/T-05/T-09) and templates/plan.yaml:56 (id: PF-0123abcd example) to the shipped 32-hex/35-char width. None gate; recommend a cheap follow-up task rather than blocking ship on it.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c4.md
```
