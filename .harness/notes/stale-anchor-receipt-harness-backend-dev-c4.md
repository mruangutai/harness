# Receipt — harness-backend-dev — FEAT-44-omp-context-advisory — cycle 4 (stale-anchor-write-hazard) — factory writer policy conflict

**Path note:** the dispatch named `.harness/notes/stale-anchor-receipt-harness-backend-dev-c4.md`
(matching the c2/c3 receipts already there), but `check-domain.sh` denied that write —
`.harness/*/features/*/notes/receipt-harness-backend-dev-*.md` is my only granted receipt
glob, and `.harness/notes/...` isn't under any `features/*` segment. Written here instead,
under the same `FEAT-44-omp-context-advisory` id the c2/c3 receipts self-titled. Flagged as
Q1 below rather than worked around.

## BLUF

c3's fix was directionally right (shared lock/tempfile/fsync/replace core) but wrong on both
caller policies it hand-derived for `write_factory`: the never-create refusal was based on a
false premise, and the path-shape check assumed a canonical layout `factory_decompose` never
actually has. Fixed by making both policies genuinely caller-owned instead of hard-coded copies
of gh-sync's: `write_factory` now takes an explicit `feat_id` opt-in for creation (default
`None` still refuses — the never-create guard survives, just correctly scoped), and passes
`feature_json_write.write_feature_json` a factory-specific, looser `tail_regex` instead of the
gh-sync-only `FEATURE_JSON_TAIL`. `write_feature_json` itself gained one new optional keyword
(`tail_regex`, default unchanged) — no other policy logic moved into the shared core.
`gh-sync.py` is untouched; its never-create guarantee is unaffected because it was never
implemented in the shared core to begin with (each of its 3 call sites raises before ever
producing candidate text for an absent base — see `feature_json_write.py:128-132`,
`gh-sync.py:695-735`).

## Before — reproduced, verbatim

`python3 .claude/skills/harness/bin/test-factory-integration.py`: **18 of 123 FAILING.**

Never-create refusal (case F, `.harness/harness/features/FEAT-INTEG-HAPPY/feature.json`,
which DOES match the canonical layout):
```
MergeRefusal(9): .../FEAT-INTEG-HAPPY/feature.json: feature.json is absent. The orchestrator
instantiates feature.json from .agents/skills/harness/templates/feature.json on its first
cycle; writing one here would produce a document missing the schema's eight required keys.
Run this feature through the orchestrator's normal cycle first.
```

Path-shape refusal (case D-decompose, `<tmp>/feature/feature.json`, NOT under
`.harness/*/features/*/`):
```
MergeRefusal(9): REFUSED: /tmp/.../feature/feature.json is not a feature's feature.json under
a features directory.
```

Dispatch's own prior run reported 19 failures; my reproduction found 18 — small drift expected
from concurrent sibling work elsewhere in this worktree, same two refusal shapes/root causes.

## Design chosen, and why the alternative was rejected

**Kept `factory_decompose` on the shared core `write_feature_json`.** c3's move was sound: the
lock/tempfile/fsync/replace machinery is genuinely identical and worth sharing. Reverting to a
private primitive would resurrect the unlocked-writer race this whole feature exists to close.
The defect was never "should factory share the core" — it was "which caller policies were
copied onto it."

**Never-create: `write_factory(feat_dir, factory, feat_id=None)`.** `feat_id` is the opt-in.
`_main`'s five internal call sites (`factory_decompose.py:396,415,427,452,474,506`) always
have one — step 2b (`:326-330`) validates `plan.yaml`'s `feature:` key before any write can
happen — so real `decompose` runs create cleanly. A caller that omits `feat_id` still gets
`MergeRefusal(9)` on an absent base (`factory_decompose.py:194-195`), same shape gh-sync's own
callers use for the identical decision. This is NOT the shared core learning a create policy —
`write_feature_json` never had one and still doesn't; `transform(None)` was always the caller's
to interpret, and it still is.

**Path shape: a factory-specific `tail_regex`.** `feature_dir` is a plain, unconstrained CLI
positional argument (`factory_decompose.py:302`), unlike gh-sync's `feat_dir`, which is always
resolved from inside the canonical `.harness` tree by its own callers. Requiring
`FEATURE_JSON_TAIL`'s full shape for factory was importing a constraint that was never actually
true of this tool — proven by `test-factory-integration.py`'s own fixtures pointing `decompose`
at a bare `<tmp>/feature/` dir (`:635-636`, `:708-709`) and succeeding. `write_feature_json`
gained one new optional kwarg, `tail_regex` (default `FEATURE_JSON_TAIL`, so every existing
caller — all of gh-sync.py, `feature-json-merge.py`'s CLI — is unaffected by construction).
`write_factory` passes `FEATURE_JSON_BASENAME_TAIL = re.compile(r"(?:^|/)feature\.json$")`
(`factory_decompose.py:151-155`) — the resolved path must still be named `feature.json`
(`require_destination`'s realpath resolution still defeats a symlink/`..` escape), just not
constrained to a `.harness/*/features/*/` prefix.

**The trap (schema, code 11) — handled by building a real document, not by loosening
validation.** `write_factory`'s `transform` now builds a full 8-required-key document when
`base is None` and `feat_id` is given (`factory_decompose.py:196-206`), matching
`.agents/skills/harness/templates/feature.json`'s own defaults (`status: "Plan"`,
`max_total_cycles: 10`, etc.) with the given `feat_id` as `feature_id`. This produces a
schema-clean candidate against an empty baseline, so `write_feature_json`'s monotonic
non-regression check (unmodified) passes it honestly — no schema bypass, no special-casing.

## Tests — RED before, GREEN after

New/changed cases, confirmed RED against the pre-fix tree before implementing (both failures
were `TypeError: got an unexpected keyword argument`, i.e. red for the intended reason — the
new API surface didn't exist yet):

```
TypeError: write_feature_json() got an unexpected keyword argument 'tail_regex'
TypeError: write_factory() got an unexpected keyword argument 'feat_id'
```

- `test-feature-json-merge.py` case_14 (`tail_regex_is_caller_overridable`): default
  `tail_regex` still refuses a non-canonical path code 9 AND creates nothing; a caller-supplied
  lax `tail_regex` accepts the same path. Pins the shared core's contract directly, not just
  through factory.
- `test-factory-decompose.py` C4-1/C4-2 (replacing the now-false C3-3, which pinned "always
  refuses outside `.harness/*/features/*/`" — a premise this fix deliberately overturns for
  factory specifically): C4-1 pins that `write_factory` WITH `feat_id`, against an absent base
  at a non-canonical path, creates a document carrying the given `feature_id`, every one of
  `feature-schema.json`'s required keys, and the given `factory.repo`. C4-2 pins that the SAME
  call WITHOUT `feat_id` still refuses, code 9, nothing created — the gh-sync-shaped direction.

## The never-create guard test named (per acceptance)

`test-gh-sync.py`'s `_dabsentT02` case (~`:2079`, "save_recorded refuses, loudly, when
feature.json is absent") is the test that would REDDEN if gh-sync's never-create guarantee
were removed. Untouched by this fix — `gh-sync.py` was not edited at all, and
`write_feature_json`'s only change (`tail_regex`) is additive with an unchanged default, so
`save_recorded`'s three call sites (which never pass it) are byte-for-byte unaffected.

## Verify — all observed directly

- `python3 .claude/skills/harness/bin/test-factory-integration.py` — **131/131 checks passed.**
- `python3 .claude/skills/harness/bin/test-factory-decompose.py` — **163/163 checks passed.**
- `python3 .claude/skills/harness/bin/test-gh-sync.py` — **ALL PASSED.**
- `python3 .claude/skills/harness/bin/test-feature-json-merge.py` — **37/37 checks passed.**
- `python3 .claude/skills/harness/bin/test-harness-merge.py` — **18/18 checks passed.**
- `bash .claude/skills/harness/bin/run-unit-tests.sh` — **exit 0, 0 `FAIL` lines** (captured to
  a log and grepped for `^FAIL `: zero matches, 1038 `PASS`-prefixed script names printed).

## DEC-174 boundary

`git status --porcelain` on the worktree shows `.omp/extensions/harness-hooks.ts`,
`omp-hooks.test.ts`, `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh`,
`validate-digest.py`, `dispatch-guard.sh` — I never opened `.omp/extensions/harness-hooks.ts`,
`check-state.sh`, `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, or
`dispatch-guard.sh` with a write or edit tool this session. `omp-hooks.test.ts` and
`gh-sync.py` DO show as modified in `git status`, but those are pre-existing/concurrent
sibling changes — confirmed by never having called write/edit against either path in this
session's own tool history.

## Residual risk

- `write_factory`'s creation path is reachable only through `_main`'s five call sites, which
  always supply `feat_id`; a future direct caller of `write_factory` that forgets `feat_id` on
  an absent-file path gets a clear refusal rather than silent data loss, so the failure mode on
  misuse is loud, not silent.
- The lax `FEATURE_JSON_BASENAME_TAIL` means `factory_decompose` can now write a `feature.json`
  literally anywhere the operator points its CLI arg — this was already true of every OTHER
  file `factory_decompose` reads (`plan.yaml`, `BRIEF.md`) and matches the tool's own
  documented contract (a plain positional `feature-dir` argument); not a new exposure this fix
  introduces, just no longer artificially narrower for feature.json alone.
- `.agents/skills/harness/bin/factory_decompose.py` (the duplicate copy outside
  `.claude/skills/harness/bin/`) was left untouched — out of the stated file-ownership scope;
  its own drift from this fix is unscoped, same accepted gap the c3 receipt already noted.
