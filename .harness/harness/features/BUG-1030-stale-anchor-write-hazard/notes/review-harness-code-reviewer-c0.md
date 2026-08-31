```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 (spec compliance) PASSES with one low-severity documentation-accuracy note; Stage 2 gates FAIL on one HIGH finding — the PRE-domain edit route carries the identical silent-zero .map() the whole feature exists to close, is completely uncovered by any test, and is never mentioned by the analysis note or handoff, unlike its POST-route twin which this diff did fix."
  severity_max: high
  findings: 2
  must_fix:
    - "harness-hooks.ts:219-234/684 (preDomain edit branch) — an edit tool_call whose patch text does not match extractEditPaths' two regexes silently skips check-domain.sh's PRE (blocking) domain check with zero signal anywhere; S2 is POST-only and does not cover this route. Uncovered by any test (grep-confirmed zero tool_call/edit cases). See finding A."
  spec_violations:
    - { kind: mismatch, path: ".harness/notes/analysis-stale-anchor-write-hazard.md", ref: "F3 (§4 table)" }
  reviewed: "6d6d1cea..83282dea"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1030-stale-anchor-write-hazard/.harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-code-reviewer-c0.md
```

# Review — BUG-1030-stale-anchor-write-hazard — review-c0

Diffed `6d6d1cea..83282dea` in the pinned worktree (never `..HEAD`; HEAD `c88eb764` adds only governance
records, confirmed by `git log` — **executed**). No `[harness:human]` commits in range — **executed**
(`git log --format` over the range, zero hits).

## Stage 1 — spec compliance: **PASS**, one low note

Checked every claim in `.harness/notes/analysis-stale-anchor-write-hazard.md` §1-4 (F1/F2/F3 table,
S1-S4 list) against source and tests.

- **F1** (locked `feature_json_write.py`, monotonic-non-regression, `require_destination`) — true at
  source (`feature_json_write.py:84-176`) and by test: `test-feature-json-merge.py` **37/37 PASS**
  (**executed**, includes case_11-13 pinning the ratchet baseline exactly as documented).
- **F2** (`gh-sync.py`'s three sites rewired, `_atomic_write`/`tempfile` deleted, no shim) — confirmed:
  grep for `_atomic_write`/`import tempfile` in `gh-sync.py` finds zero live references, only prose
  (**executed**). `test-gh-sync.py` **ALL PASSED** (**executed**). Absent-file tolerance,
  `save_recorded`'s verbatim `SystemExit`, and `pr` idempotence read correctly at source
  (`gh-sync.py:534-736`, **reasoned**, corroborated by the green run).
- **F3 — FALSE as final state, not corrected at its own site.** The table row claims write_factory's
  "absent-file contract converged onto `save_recorded`'s refusal after checking every caller — none is
  a legitimate first writer." Cycle 4 (same document, further down) explicitly reverses this: `feat_id`
  is now a creation opt-in and `write_factory` **is** a legitimate first writer
  (`factory_decompose.py:158-217`, **executed**: `test-factory-decompose.py` case C4-1 creates a
  document; **163/163 PASS**). The correction lives only in the later "Cycle 4" section; the F3 row
  itself is never struck through or amended. Low severity — the document as a whole is not misleading
  (the correction is present), but a reader who trusts the table the dispatch specifically flags
  ("especially the F1/F2/F3 table") is told something false at the point of the claim. Not gating.
- **S1** (integration test for the edit route) — shipped: six new cases in `omp-hooks.test.ts`,
  confirmed by diff and by running `bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` →
  **48 pass, 0 fail** (**executed**), matching the handoff's claimed count exactly.
- **S2** (non-blocking notice on the POST zero-path case) — shipped and behaves as documented; see
  Stage 2 answer (c) below.
- **S3** (guidance in the orchestrator playbook) — accurately reported as **not shipped**: `git diff
  --stat` over the range touches no skill/playbook path (**executed**).
- **S4** (DEC-199 amendment) — correctly left as an unshipped, approval-gated open question, not
  fabricated as done.
- `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays register every new/changed test
  file (`test-feature-json-merge.py` added to `UNIT_SCRIPTS`; `test-gh-sync.py`/`test-factory-decompose.py`
  already present) and `test-omp-hooks.py` (already registered) shells out to `bun test
  omp-hooks.test.ts`, so the six new edit-route cases run inside the real gate, not just standalone
  (**executed**, per-Expertise G-04 check for this repo).

## Stage 2 — code quality

### Finding A — MUST FIX, high: PRE-domain edit route is an uncovered, unmentioned silent fail-open of the identical shape

**`.omp/extensions/harness-hooks.ts:219-234`** (`preDomain`'s `edit` branch) and its call site at
`:684` inside the `tool_call` handler.

`preDomain`'s edit branch is `extractEditPaths(input.input).map((filePath) => runner(...))` — the
exact shape `postDomain`'s edit branch had before S2, and the shape this whole feature exists to make
observable. When `extractEditPaths` returns `[]` (any patch text that does not match either
`^\[...#XXXX\]$` or `^MV ...$` — a malformed patch, or any future drift in the patch format, which is
precisely the kind of extraction/format mismatch this incident class is about), `preDomain` returns
`[]`, `reason` stays `undefined`, and the `tool_call` handler falls through without `{ block: true,
... }` — **the edit proceeds with zero domain check and zero signal anywhere.** This is the
**preventive, blocking** gate (`reason` truthy → `{ block: true, reason }`, confirmed at source
`:748`), not the diagnostic one S1/S2 cover — worse in kind than the POST gap this diff fixed, since a
bypass here lets an out-of-domain edit land at all, rather than merely going undetected after landing.
S2 does not cover it: S2 only assigns `advisory` inside the `tool_result`/POST handler
(`:833-846`), never inside `tool_call`/PRE.

**Uncovered, confirmed by grep** (**executed**): `omp-hooks.test.ts` has zero occurrences of
`handlers.get("tool_call")` combined with `toolName: "edit"` — all six new cases exercise
`tool_result` only. **Unmentioned, confirmed by grep** (**executed**): neither
`analysis-stale-anchor-write-hazard.md` nor `handoff-build.md` contains `preDomain`, `PreToolUse`, or
`:234` anywhere — this is not a decided out-of-scope item, it is an unexamined gap of the same shape
the squad found and fixed on the other side of the same function pair, in the same file this diff
already touches.

That the domain gate is load-bearing in practice is not hypothetical: my own `bash` call earlier in
this review was blocked by exactly this enforcement layer on an unintended heredoc redirect
(**executed**, this session) — confirming the mechanism a bypass here would silently skip is real and
active, not vestigial.

**Alternative**: mirror S1 on the PRE route (assert a `tool_call` with `toolName: "edit"` reaches
`check-domain.sh` with the extracted path and no `--post`), and give PRE an S2-equivalent signal for
the zero-extraction case — since `tool_call` can only `block` or `revise` (no free-form advisory
channel like `tool_result`'s `content` array), the natural shape is a stderr/debug-log line (this file
already has a `debug()` helper, `:60`+) so the skip is at least visible in the transcript rather than
indistinguishable from "no domain issue found."

### Finding B — should_fix, med: the two-caller create/no-create split is caller-site discipline only, not core-enforced

**`feature_json_write.py:84-176`** (`write_feature_json` — no create/no-create concept at all),
**`gh-sync.py:534-736`** (three sites, each independently re-raising on `base is None`),
**`factory_decompose.py:158-217`** (`write_factory`'s `feat_id` opt-in, entirely local to that one
caller).

Demonstrated by **executed** experiment (`python3` against the actual worktree modules, read-only): a
closure shaped exactly like `write_factory`'s creation branch, but built to mimic what a gh-sync site
could trivially become, was handed straight to `write_feature_json` with the SAME default
`tail_regex` gh-sync's real call sites use — it succeeded and created a fully schema-clean
`feature.json` at a canonical `.harness/features/FEAT-99-test/feature.json` path, with no refusal of
any kind. `write_feature_json` has no `feat_id`/`allow_create`-shaped parameter; nothing at the shared
core distinguishes "a gh-sync-style caller" from "a factory_decompose-style caller" — only the fact
that gh-sync's three closures today choose to raise on `base is None` before ever reaching the schema
check. (I also confirmed the *backstop* that does exist: a **partial**, schema-incomplete document
built on an absent base is refused — **executed**, `MergeRefusal(11)` naming the missing required
keys. That backstop catches accidental garbage; it does not catch a deliberate, schema-complete
creation, which is exactly what the experiment above produced with zero refusal.)

Failure scenario: a future, plausible edit to `_record_status`/`_record_pr`/`save_recorded` (e.g.
"back-fill `feature.json` for a card synced from an external board") that assembled a full 8-key
document on `base is None`, mirroring `write_factory`'s own pattern, would silently reopen
tool-owned instantiation of `feature.json` — the exact class DEC-119/DEC-199 assign to the
orchestrator alone — and no existing test would catch it: `test-gh-sync.py` only exercises today's
three closures as literally written, and `test-feature-json-merge.py`'s `case_14` tests path-shape
overridability, not a creation-opt-in boundary.

**Alternative**: add an explicit `allow_create: bool = False` parameter to `write_feature_json` that
the shared `_transform` checks before ever invoking the caller's `transform` on a `None` base,
replacing three independently-hand-written refusal sites with one core-enforced gate; pin it with one
boundary test in `test-feature-json-merge.py` asserting the core itself refuses creation with no
opt-in regardless of what `transform` would have returned.

## Direct answers to the dispatch's four sharp questions

**(a) Genuine two-caller policy split, or one permissive policy wearing two names?** One permissive
shared core wearing two names by convention. Today's three gh-sync call sites and factory_decompose's
`feat_id` opt-in are each individually correct (**executed**, confirmed via test-gh-sync.py/
test-factory-decompose.py green runs and source read), but nothing at `write_feature_json` itself
enforces or even tests the split — see Finding B, demonstrated live.

**(b) Does the core retain a destination invariant with caller-supplied `tail_regex`?** Only
trivially. `require_destination`'s realpath resolution still defeats symlink/`..` tricks against
*whatever* regex is supplied (**reasoned**, confirmed by re-reading `harness_merge.py:156-176`), and
for `factory_decompose`'s basename-only regex that resolution is the **entire** surviving invariant —
"must be literally named `feature.json`," no directory constraint at all (**executed**, reproduced
`case_14`'s lax-tail behavior independently). This matches the disclosed residual's own framing and is
not a regression versus pre-feature behavior: `factory_decompose`'s CLI positional, and the private
atomic-write primitive it used before this diff, carried no path check either (**executed**, grep
confirms no `tempfile.mkstemp`/`os.replace` primitive with any path validation remains in the deleted
code's docstring references). I concur with the note's own "med, deliberate, non-regression" rating.

**(c) Can S2 set `isError`?** No, on any input — proven structurally, not just observed.
`extractEditPaths` is a pure, synchronous, deterministic function (regex matching only, no I/O, no
shared state — **reasoned**, read in full at `:70-84`). S2's guard
(`toolName === "edit" && extractEditPaths(input.input).length === 0`) and `postDomain`'s own
`.map()` call the identical function on the identical `input.input` with no `await` between them
(**reasoned**, traced the handler body `:833-855`), so whenever S2 sets `advisory`, `postDomain`'s
edit branch is guaranteed to have produced `[]` too, making `reason` falsy — the ONLY thing that
drives `isError: true` (`:854`, `else` branch). Advisory-set and `reason`-truthy are therefore
mutually exclusive by construction for the edit route. Corroborated by **executed** evidence: the
shipped suite is 48/48 green, including an explicit `expect("isError" in (result as any)).toBe(false)`
assertion on the zero-path case.

**(d) Is the PRE-domain edit route still uncovered?** Yes — confirmed by grep, zero matches for
`tool_call` combined with `toolName: "edit"` anywhere in `omp-hooks.test.ts` (**executed**). See
Finding A, `must_fix`.

## Confirmed, not new: the other disclosed residuals

- **DEC-199 "exactly four consumers" is false, now six** — confirmed at source
  (`feature_json_write.py` + its `gh-sync.py`/`factory_decompose.py` callers). Correctly left
  unshipped as an approval-gated open question (S4/Q2), not fabricated as done.
- **S3 has not shipped** — confirmed, `git diff --stat` touches no skill/playbook path.
- **`.agents/skills/harness/bin/factory_decompose.py` duplicate left untouched, now drifting** —
  confirmed present and byte-identical to base (`git diff` over the range is empty for that path,
  **executed**).

## What I did not find a defect in

`_atomic_write`'s deletion is clean (no shim, no dead import — **executed** grep). The migration to a
fresh in-lock re-read for `_record_status`/`_record_pr`/`save_recorded` **closes** a race rather than
opening one: the pre-lock read is used only for early-exit optimizations (existence, already-recorded
idempotence), and the actual write always re-derives from the freshly-locked `base`
(**reasoned**, confirmed by reading all three functions in full, corroborated by
`test-gh-sync.py` ALL PASSED). The monotonic-non-regression baseline is genuinely strict on an
absent/unparseable base — confirmed both by the existing green `case_11-13` and by my own creation
experiments (a schema-incomplete document on an absent base is refused, code 11, naming every missing
key). I found no string-collision path by which a candidate's genuinely new schema problem could hide
behind an unrelated baseline entry — jsonschema's messages embed the offending pointer and/or value,
so two different problems do not produce equal strings (**reasoned**).
