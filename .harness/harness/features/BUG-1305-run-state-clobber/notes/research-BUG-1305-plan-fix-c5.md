# Plan fix c5 — BUG-1305 — the two panel highs are closed and the panel is transcribed

**BLUF: both gating findings are resolved with the panel's own prescribed remedies — T-12 and SC-12
are struck (retired in place), and the witness `.run-identity.json` is now a guarded run artifact
inside T-02 with SC-13 grading it. The whole cycle-2 panel, ranks 1–9 and both readers, is in
`plan.yaml`'s top-level `panel:` key. Approval is untouched: `status: pending`, feature station
`plan`. Ranks 3, 5, 6, 8, 9 are transcribed `open` — they are the operator's rulings at signature.
`cycles_used: 1` — one send-back, recorded below.**

## What changed, and the verb behind every write

Every `plan.yaml` write went through `plan-merge.py`: `amend` (compare-and-swap, one field at a
time), `set-task-station` for T-12's station, `set-panel` for the panel mapping. No compare-and-swap
failed. `BRIEF.md` was edited directly; `## Approval` untouched.

- **Rank 1 (high) — struck.** T-12 retired in place in the shape T-04 and T-10 use: `RETIRED - `
  title, `traces: []`, `depends_on: []`, `status: abandoned`, `verify: test ! -e …/notes/probe-postmint-BUG-1305.md`.
  Its intent opens `DO NOT EXECUTE THIS TASK.` and records the main-checkout hook confound
  (`.claude/settings.json` registers `${CLAUDE_PROJECT_DIR}/…/check-domain.sh --post`), that
  `post_mint_observed: no` was guaranteed by construction, and that the mandatory `## Reported`
  section would therefore have published a false claim. SC-12 retired in place in BRIEF; SC-10's
  dangling pointer re-aimed at the new REQ-01 disclosure. T-04's own body said REQ-01 was covered by
  "T-01, T-02, T-09, T-11 and T-12 — every one of them live"; corrected in the same pass.
- **Rank 2 (high) — guarded, not disclosed.** No task owned `bash-write-guard.sh` or
  `harness_boundary.py` (grep of every `files:` list), so both went into **T-02**, the task that makes
  the witness exist. T-02 now adds `RE_RUN_IDENTITY` to `harness_boundary.py` (:42-45), the Bash
  `_run_artifact_guard` (:744-767), and a `SHAPE_PATTERNS` (:1185) route denial in `shape_problems`
  (:1203) — explicitly NOT `SWEEP_GLOBS` (:1016), which would report every legitimate witness forever.
  Write-once and the refusal text are specified, and the intent states that the POST hook's own
  `record_seed` is not a governed tool write and needs no exemption while being itself write-once.
  New files: the two guard scripts plus `tests/unit/test-harness-boundary.py` and
  `tests/integration/test-bash-write-guard.py` (both confirmed present). `verify:` and T-08's
  `verify:` extended to run them. **SC-13** is the new criterion (`verify: automated`,
  `evidence: integration`) — a new SC rather than an SC-01 amendment, because SC-01 grades checkpoint
  refusals and SC-01's FAILS-if is already six clauses long.
- **The two cheap closes, both taken (one clause each).** `D-13.choice` now names T-03's three
  reported paths. T-08's pairs are **six**, naming T-05's fail-closed `return 2` and the
  witness-guard denials; SC-07 says six in both its enumeration and its FAILS-if.
- **Send-back 1 — the rank-2 remedy falsified the rank-4 arity in the same pass.** Guarding the
  witness ADDED refusing branches to this feature (Bash write and removal denials, Write/Edit route
  denial for `.run-identity.json`), and T-08 direction two claims EVERY refusing branch this feature
  adds is paired — so the count that grades refusing branches had to follow the branch that was just
  created. Fixed as a sixth pair in T-08's `intent` (permitted side: `state.yaml` and `digest.md`
  Writes in the SAME run directory still exit 0, an unrelated ordinary Bash write there unaffected,
  so the denial is shown scoped to the filename not the directory), six in SC-07's enumeration and
  FAILS-if, and rank 4's `resolution:` restated. Every `summary:` left byte-identical, so all nine
  `PF-` ids recompute to the first pass's values. SC-13 grades the branch's test coverage; this pair
  is its place in the REQ-07 no-protection-traded-away accounting — the two are not substitutes.

## Verification

- Greps: nothing in `plan.yaml` `depends_on` T-12 (its only remaining mentions are inside its own
  retirement body); no BRIEF criterion grades T-12 or its note — SC-12 is retired in place and the
  two other `SC-12` hits are narrative pointers saying so.
- `yaml.safe_load` loads the plan; `approval.status: pending`; top-level `status: plan`; `panel:`
  well-formed; all nine finding ids recomputed from their own `summary:` with `panel_findings.py` and
  matched exactly; every live task carries `traces`/`change_type`/`execution_mode`/`files`/`verify`/
  `intent`; the three retired tasks are retired in place, none deleted.
- `check-plan-routes.py <plan> → exit 0, 0 violations`; `check-instruction-paths.py → exit 0, 62
  files, 0 violations`. The only line my change moved is T-02's DEVIATION, now naming the four added
  paths. No VIOLATION added or removed.
- `git -C <worktree> status --porcelain` → `?? .harness/harness/features/BUG-1305-run-state-clobber/`
  and nothing else.
- **Re-run after send-back 1** (verbs: `amend` on `tasks:T-08.intent` with `--expect-sha256`
  `801ff8a0…`, `set-panel` for the panel; BRIEF edited directly, `## Approval` untouched; no
  compare-and-swap failed): `check-plan-routes.py <plan>` → exit 0, 0 violations, 1 plan;
  `check-instruction-paths.py /Users/molchairuangutai/GitHub/harness` → exit 0, 62 files, 0
  violations (handed the plan path it exits 2 `selects nothing in scope` — a plan.yaml is outside
  its `.claude/agents/*.md` + `.claude/skills/*/SKILL.md` scope by design). All nine `PF-` ids
  recomputed identical. `yaml.safe_load` loads; `approval.status: pending`; `status: plan`.

## Open — and one of these is a harness limitation, not a plan choice

- **No `plan-merge.py` verb reaches `lanes:`.** `amend` is scoped to `tasks|decisions`; `apply` exits
  7 CONFLICT on a top-level key that differs from the base. So the three new surfaces are recorded in
  **T-02's `execution_reason`** instead, with the `--resolve` answer (`harness-backend-dev`,
  `harness-dev-ops`; `+harness-qa` for the tests) and the reason the lanes block could not carry it.
  Nothing was hand-edited around the refusal.
- Ranks 3, 5, 6, 8, 9 are transcribed `open`, priced in the return. Nobody below the operator may
  mark a finding `accepted`.
