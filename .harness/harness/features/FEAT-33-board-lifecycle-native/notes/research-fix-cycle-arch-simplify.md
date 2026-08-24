# Fix pass — arch-eng + simplify-eng findings applied to BRIEF.md and plan.yaml

**Both artifacts stay `pending`. Nothing signed. One question is still the operator's and is
marked as such in the BRIEF rather than resolved either way.**

Re-pinned every measurement from `d065b3b` to **`e3c9187`** (8 sites in `plan.yaml`, 1 in
`BRIEF.md`). The pin was not stale in substance: `git diff --name-only d065b3b..e3c9187` returns
only files under this feature's own directory, and `d065b3b` is still `main`'s tip — so FEAT-31,
FEAT-26 and FEAT-32 have landed nothing on any surface this plan reads. Every code anchor cited
below was re-opened at `e3c9187`, not carried over.

## The two defects each found twice, fixed once each

**M1 / L1 — T-02's fixture blast radius.** The two readers named partly different files; T-02 now
carries the **union**: 10 source files plus `harness.json`, and the intent enumerates **19 sites in
9 files**, split into six centralised constants (one edit each) and thirteen inline literals. Three
of the nine are integration-kind (`test-gh-sync.py`, `test-check-state.py`,
`test-factory-integration.py`), which is why T-02's verify moved to `--kind all` — under `--kind
unit` those three fail invisibly and resurface inside T-07. Also added: the four prose sites that
assert "five" and **invert** with the change, and two sites that must NOT change
(`test-factory-config.py:427`, `test-gh-board.py:146` — both already-rejecting cases).

**M2 / L4 — the missing edge.** `T-07: depends_on: [T-02]`, `T-08: depends_on: [T-02, T-07]`. One
edge, not two remedies.

## Applied — must-fix

- **M3.** T-03 gains a `project_resolve(owner, number)` primitive returning `None` (not raising) for
  an absent project. `factory_gh.py:435-457` re-verified: four conditions, one `GhError`, and
  `:452-454` deliberately collapses "field absent" with "not single-select". T-04 step 2 now says in
  terms that no code path may call `project_create` on any outcome other than `project_resolve`
  returning `None`, step 3 splits the two field shapes (create vs **exit 2 refusing**), and two new
  test cases assert `createProjectV2` is *not* in any argv when the project exists.
- **L2 — resolved without retyping and without touching the runner.** Verified at my own tier:
  `harness.json:40-49` requires `unit`+`integration` for `feature`; `integration.detect`
  (`:119`) is `tests/integration/**` plus six explicit filenames; `run-unit-tests.sh:18` is a
  14-name array — both byte-identical in worktree and main. And the discriminating check the digests
  did not run: **`harness-qa-gate` SKILL.md line 60 — "Presence is not satisfied by an unrelated
  existing test."** So the gate genuinely FAILs, not merely under-covers. **New D-12:** integration
  cases go in `test-factory-integration.py`, which is already in *both* lists, is by its own
  docstring the only file that forks a real process against a stateful stub `gh`, and at `:225`
  already answers `_project_field_resolve`'s query. `change_type: feature` therefore stands honestly
  on T-04/T-05/T-06; no runner array and no matrix entry is edited. **This also caught the same
  defect in T-03**, which neither digest flagged: `api.when` fires `integration` on
  `touches_db_or_external`, and adding GraphQL mutations plainly does — T-03 gets a case there too.
- **L3.** T-06's LABEL fix now shells out to `gh label create --color b60205` itself. Two verified
  reasons in the intent: `gh-sync.py` is hyphenated so its `ensure_labels` (`:520-531`) is
  unreachable by import, and `factory_gh.ensure_labels` (`:186-195`) uses `--force` with
  `_LABEL_COLOR = "5319e7"` (`:30`) so it would repaint the label purple every run. `depends_on`
  gains T-08.

## Applied — should-fix and angles

S1 (`grep -qi`, plain `grep -q` — also closes L7) · S2 (reconcile's exit code counts only STATION,
REASON, LABEL; audit keeps all five, so SC-09 is untouched) · S3 (`gh-sync.py:626-627`'s literal
`"Building"` → `board["stations"]["building"]`, with a fixture whose building station is *not*
"Building") · S4 (T-11 now owns SC-10's negative clause as a real `git diff --name-only` over the
five enforcement paths, plus `check-state.sh`) · S5 (T-02 runs `check-state.sh` before **and**
after and asserts the finding **set** identical, not both exit 0 — DEC-174 am.4's own idiom; also
discharges SC-10's orphaned half) · S6 (`--kind all` on T-07/T-08 with the reason stated) ·
S7/L5 (`.harness/harness.json` dropped from T-04's `files:`) · S8 (T-01's abandon path = a revert PR
on kaya-ai's `master`, new **D-13**) · S9 (T-02 case (c) explicitly labelled *not* SC-08's
discriminating assertion) · L6 (T-10 anchors on the "GitHub Issues mirror" section by name;
`SKILL.md:200` sits after both `### 7` at `:174` and the unnumbered map-the-codebase section at
`:189`) · B3 (T-10 states org-owned boards cannot be provisioned) · B6 (T-11 says the `0 findings`
grep is not evidence; the live `audit` exit 0 is) · REUSE (`factory_config.harness_root()`, cited
with its three existing callers) · SIMPLIFICATION (**four** network calls, not five — the
enumeration supports four) · ALTITUDE (one named helper `_missing_options`, authored in T-04, called
by T-05's DECLARATION class).

## Declined, on purpose

**EFFICIENCY / E1 — LEAVE, and every build task went the *other* way to `--kind all` (new D-14).**
The 153s-vs-73s measurement is real and the cost is named in D-14 rather than hidden: `--kind all`
exceeds the 60-second verify guideline by minutes, per task, per iteration. It is still the right
trade — M1 spans both kinds, `harness.json:121` declares the integration cmd as exactly
`run-unit-tests.sh --kind integration` so a per-script verify forks a second spelling of the
authority, and a direct script call skips the `MISCONFIGURED` drift detector (`:41-55`) that is the
only thing catching the unregistered new test file this plan adds. The reader's own convention
caveat was the right instinct.

## Left alone, deliberately

**M4 — untouched and flagged.** `REQ-02`, T-03's fifth primitive `project_workflows`, T-05's
finding class 5, T-10's workflow steps and SC-12 are byte-identical to the draft; verified by diff.
The BRIEF gains a blockquote under the DEC-186 constraint naming the two branches the operator must
choose between. Neither is pre-applied. Two incidental touches nearby that do **not** change M4's
substance: the network-call count fix (five → four) enumerates the workflows call without changing
its status, and T-03's primitive count went five → six because `project_resolve` was inserted as
item 0, so "fifth primitive" still points at `project_workflows`.

`validate_board`'s `team` lane and D-06's cross-repo ordering were not re-litigated.

## Corrected in the record

The `run-unit-tests.sh` "positional KIND" claim appears in **neither** artifact, so nothing needed
fixing there. Confirmed at `:23-27`: `--kind` is accepted, `all` is the default, and a bare
positional exits 2.

**BRIEF's null-kind count was wrong and its reason was wrong.** There are **five**, not four —
`functional`:113, `component`:127, `ui`:134, `eval`:141, `typecheck`:148 — and they split into two
mechanisms the original folded together: `functional` is `status: excluded` with a signed DEC-187
and its own `excluded_because`, the only soft skip this config permits; the other four are
`status: unresolved`, and `harness.json:102` states in terms that a null cmd is **BLOCKED in the qa
gate, never a skip**. The reason no criterion rests on them is not that this feature touches none of
those surfaces (not the matrix's test, per B5b) but that none is *selected* by this feature's change
types.

## Validation run

`safe_load` clean · every `verify:` a literal `|` block, zero folded `>` scalars · every task carries
`files`/`verify`/`traces`/`change_type`/`execution_mode`/`depends_on` · DAG acyclic, all `depends_on`
resolve · `check-plan-routes.py` **exit 0, 0 violations** (the two T-11/T-12 DEVIATIONs are the
pre-existing declared ones) · `check-state.sh` reports only the expected
`BRIEF.md is NOT approved` and `plan.yaml approval is pending`, plus an orphaned run dir
`2026-08-22-02-product` that `feature.json` does not record — **the orchestrator's to reconcile, not
mine.**

## Open for the tier above

1. **Blocking — the operator's.** DEC-186 amend-to-four (bounded to `/harness-init`) or drop REQ-02.
2. **Non-blocking.** T-04 still adds one line to `run-unit-tests.sh`'s `UNIT_SCRIPTS`, a contended
   file. The dispatch said not to plan an edit there; I read that as scoping to the L2 remedy (which
   it does — D-12 edits no array) and kept the registration, because the drift detector at `:41-55`
   makes an unregistered `test-*.py` exit 2 `MISCONFIGURED` and break **every** verify in the plan at
   once. Flagging rather than silently overriding. If the operator wants zero edits to that file,
   the only alternative is to fold every board-lifecycle test into an existing test script, and I
   would recommend against it.
3. **Non-blocking, not mine.** `check-domain.sh --post` blocks on pre-existing violations in
   `FEAT-31`'s `feature.json` (`undeclared key 'agent'` at `/runs/9`-`/runs/20`). Unrelated to this
   feature; it will obstruct anyone committing in that worktree.
