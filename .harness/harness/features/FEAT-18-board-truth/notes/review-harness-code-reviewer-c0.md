# Code review — FEAT-18-board-truth — `main...6d2d61b`

## Verdict: FAIL — severity_max high, one gating finding, carve-out escalation (not a fix cycle)

**Stage 1 (spec compliance): clean.** No scope creep, no omission, no mismatch found against
REQ-01..08 / D-01..08 / SC-01..07, SC-09 (SC-08 correctly STRUCK, not counted; 8 live criteria).
The finding below is a **Stage 2 quality finding** — the code matches T-04's and D-07's signed
letter exactly. This is not a backend-dev execution error; it is a gap in the composition of two
tasks that individually did what they were told.

## The finding

**`gh_board.derive_station` returning `None` for an illegal task status silences `check-state.sh`
INV-26 for the WHOLE feature, not just the bad task — exactly the shape D-07 forbids on the
board side, now present on the plan side.**

D-07's own reasoning (`plan.yaml:225-232`) states the principle: "a lookup keyed by a
runtime-discovered value that misses makes both sides of a comparison empty... so the absent-key
branch has to exist and has to be loud." That principle is honored for a **card-side** miss
(`gh_board.read_station` → `"not on the board"`/`"no station set"` → `CANNOT VERIFY` violation,
`check-state.sh:1171-1178`). It is **not** honored for a **plan-side** miss: an illegal task
status (e.g. `Building`, capital B — the board's own spelling, and T-01's own comment calls this
"the typo a person will actually make", `check-plan-routes.py:334-336`) makes
`gh_board.derive_station` fall through both `any(... == "building")` and
`all(... == "done")` and return `None` (`gh_board.py:114-118`). `check-state.sh` then does
`if _derived is None: continue` (`check-state.sh:1143-1146`) — **the entire feature is skipped,
silently, with zero violation recorded**, not merely the mistyped task.

**Empirically verified**, not just read: extracted `gh_board.py` at the pinned SHA (`git show
6d2d61b:...`) and called `derive_station` directly —

```
plan {T-01: done, T-02: "Building"} -> derive_station -> None
plan {T-01: done, T-02: "building"} -> derive_station -> Building
```

**Both halves of the compound failure:**
1. **The parent goes stale silently.** `start-task` still moves the *sub-issue* card correctly —
   the station passed there is the code literal `"Building"` (`gh-sync.py:574`), untouched by the
   plan's status string. But `_apply_parent_rule` (`gh-sync.py:185-186`) calls `derive_station`,
   gets `None`, and no-ops the parent write. The parent card goes stale and INV-26 — the detector
   built specifically to catch a stale parent — reports nothing for that feature at all, because
   `_derived is None` short-circuits every per-task and per-parent check in the same loop
   iteration (`check-state.sh:1143-1146`).
2. **Lesser sibling, same shape:** an illegal status on a *non-driving* task (one that doesn't
   flip the feature-level derivation) is separately swallowed by `_want = _EXPECT.get(...)` →
   `None` → `continue` (`check-state.sh:1168-1170`) — that one task's own comparison is silently
   skipped even when the rest of the feature is still checked.

**Why this is realistic, not a contrived edge:** the status writer is the orchestrator, an LLM
performing "~15 bookkeeping duties per cycle with nothing validating any of them" by
`check-state.sh`'s own header (`check-state.sh:4-8`) — case-sensitivity slips are a plausible LLM
failure mode, not a hypothetical one. The edit channel is demonstrated in this very artifact:
`plan.yaml`'s approval block records two mid-build hand amendments to this exact plan
(`plan.yaml:8-19`). And the window is real: no hook re-runs `check-plan-routes.py`'s
`LEGAL_TASK_STATUSES` enum after signature — confirmed by reading `.claude/settings.json`'s
`PreToolUse` hooks (`check-domain.sh`, `branch-create-gate.sh`, `bash-write-guard.sh`,
`dispatch-guard.sh` only) and `check-state.sh`'s own invariant list (INV-3/4/5 validate schema
shape, never status legality). A typo introduced mid-build is invisible to INV-26 for the rest of
that build — the same silent-window shape FEAT-14's own failure occupied, which is this feature's
stated reason to exist.

**Carve-out — operator escalation, not a fix cycle.** Both natural remediation sites —
`check-state.sh` (validate status legality before trusting `derive_station`'s `None`, or report a
distinct "cannot derive — illegal status" violation) and/or `gh_board.py` (have `derive_station`
distinguish "legally mixed, no verdict" from "illegal input, cannot verify") — are DEC-174
carve-out surfaces. Per CLAUDE.md, changes to `check-state.sh` are never made through a team run
whose gates are the thing being changed. Naming the surfaces is as far as this review goes;
remediation design is the operator's call.

## What I verified and how (falsification evidence, not just reading)

- **The pin is the whole feature.** `git diff 6d2d61b..HEAD --stat -- .claude/skills/harness
  .harness/harness.json` → empty. `git log 6d2d61b..6303683` → two commits, both bookkeeping
  (`89ecc11`, `6303683`), neither touches source. `human_commits_in_scope: []` — confirmed by
  grep, not assumed.
- **Fail-open hunt, direct probes:**
  - `derive_station` typo behavior: reproduced live (above), not inferred from the docstring.
  - `set_station` call sites (`gh-sync.py:196`, `:574`): both wrap `gh_board.BoardError` in
    `try/except`, print to stderr, and the caller continues — `_apply_parent_rule` at `:578` is
    called unconditionally after the try/except in `cmd_start_task`, and `cmd_close_task` orders
    the parent write before the closing `gh()` call that can `sys.exit(0)` (`:591-593`). Matches
    D-02's ordering requirement.
  - SC-03's loud/quiet split: read `gh-sync.py:107-142` and cross-checked against
    `test-gh-sync.py:1149-1185`'s two-fixture pair (item-edit fails vs. `gh` absent) — both halves
    assert on distinct evidence (stderr content + the following call still happening, vs. a single
    SKIP line and zero calls). Genuine, not vacuous.
  - `check-state.sh` INV-26's own quiet branches (no `github` block, `load_board` → `None`, `gh
    auth status` fails, truncated/failed board read) all correctly wrap the per-feature loop in
    `if _stations is not None:` and record nothing — matches D-07's environmental-precondition
    half. **Empty-but-successful board read** (`_stations == {}`) is NOT the same as a failed
    read: `{} is not None` so the loop still runs, and every card lookup then correctly reports
    `CANNOT VERIFY` via `read_station`'s `"not on the board"` branch — this is loud, not a
    fail-open, confirmed by reading `read_station`'s three-way return shape (`gh_board.py:154-171`).
  - SC-04 no-retry: grepped `gh-sync.py` and `gh_board.py` for `retry|while True|for _ in range` —
    zero hits outside comment text. Both `set_station` call sites are single `try`/`except`, no
    loop.
  - `check-plan-routes.py`'s status enum (T-01, SC-06): `status not in LEGAL_TASK_STATUSES`
    without `str()` coercion first — rejects, does not coerce (`check-plan-routes.py:329-338`).
  - T-05 (`branch-create-gate.sh`): read the diff directly — the four config keys and the
    board-flip block are deleted cleanly; the pre-existing `[ "$state" = "OPEN" ] || deny ...`
    line is untouched. **Ran the gate live** against the bad-flow branch payload from the task's
    own verify command: `permissionDecision: "deny"`, reason names `FEAT-99-nope` — confirmed
    myself, not just cited from qa's note.
- **SKILL.md vs. D-02's amendment (premise 2):** read `plan.yaml`'s D-02 `amended:` clause
  (lines 94-135) and `SKILL.md`'s diff — "no board configured" is correctly absent from the
  environmental-precondition bullet and correctly described as narrower ("the issue lifecycle
  still runs to completion"). No finding; the divergence from the pre-amendment text is the fix
  working as intended.
- **D-01 / DEC-186 bound:** read INV-26's block end-to-end — it only ever appends to `bad`/`warn`
  and prints; no write to `plan.yaml`, `BRIEF.md`, `feature.json` or any approval block anywhere
  in the new code. No finding, per the plan's own instruction not to raise this.
- **Dismissed, recorded so it isn't re-raised:** `.harness/harness.json`'s `board` mapping carries
  a fourth key, `_note`, beside D-05's stated "exactly three keys" — this is the same
  underscore-prefixed comment-key idiom already used throughout this exact file (`github._note`
  pre-exists the diff, `_test_kinds_note`, every kind's `_reason`); not a real config key, not a
  finding.
- **`isinstance(_parent, int)` guard** (`check-state.sh:1187`): `feature-schema.json` types
  `github.parent` as `["integer", "null"]` in both the DEC-191-closed feature schema locations —
  schema-guaranteed, not a fail-open gap.

## Mutation evidence

Not re-measured; not load-bearing for this verdict. T-02/T-04's "6 of 6"/"5 of 5" mutation figures
are a **relayed claim** with no substantiating artifact in this repo — see
`notes/mutation-record-T-02-T-04.md`. Not repeated here as measured coverage.

## SC-08

Struck (DEC-188 shape, `plan.yaml:234-270` / `BRIEF.md` SC-08). Not counted as unmet, not
evaluated.
