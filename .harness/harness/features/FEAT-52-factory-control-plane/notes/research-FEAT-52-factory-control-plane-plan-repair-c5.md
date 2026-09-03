# Plan repair c5 — PF-93ebe15db8b5 (HIGH) applied — FEAT-52

**BLUF: the ruled HIGH finding is closed by two complementary changes and nothing else moved.**
T-02's checker rule now rejects BOTH anchor directions from one shared predicate, and a new T-15
carries BRIEF SC-04 and SC-11's per-site, pinned-tree direction assertions that no task in the
previous 14 implemented. `plan.yaml` holds 15 tasks, no `approval:`, `status: plan`.
`check-plan-routes.py` exits 0.

## One judgement call the operator should see

The dispatch pinned the third class's predicate as "does not continue `.harness/<one segment>/features/`".
Applied literally that would have flagged **11 correct spans**: the templates spell the feature
directory `.harness/features/<FEAT>/…` with no repo segment, and T-07 anchors exactly those five
README rows plus others to the feature tree. Counted over the declared scope at
`e8e1b78be3379d4a669aa7e28aef8f76eb942471`: `.harness/harness/features/` 31, `.harness/<repo>/features/` 4,
`.harness/<product>/features/` 1, `.harness/features/` 11.

So the intent now specifies **one named helper**, called by both classes:
`^\.harness/([^/]+/)?features/` — `.harness/`, optionally one segment, `features/`. Class 2 fires when
a `<HARNESS_CONTROL_PLANE_ROOT>/` remainder matches it; class 3 fires when a
`<HARNESS_FEATURE_TREE_ROOT>/` remainder does not. This *widens* class 2 by the unsegmented spelling
(strictly a strengthening, no correct span becomes a violation) and is what makes the mirror
un-re-narrowable: two predicates free to drift apart is how the asymmetry returns. A test row was
added asserting all four combinations of the two spellings against the two anchors.

Without this, T-12's whole-scope run would have gone red on correct T-07 work.

## Move 1 — T-02 `intent`

Added, verbatim message string preserved:
`VIOLATION <path>:<lineno>: control-plane path anchored to the feature tree`.
The paragraph states why it is the mirror and not an extra rule (D-06 gives
`<HARNESS_FEATURE_TREE_ROOT>/` exactly one job) and names the panel's concrete case —
`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json` in `harness-qa-gate/SKILL.md`, which satisfies
THE RULE and escapes class 2, and at runtime resolves the qa gate's own matrix against the feature
worktree.

New TEST FILE rows: MIRROR RED (two known lines, one inline span, one fenced block; exit 1, both
line numbers named separately, summary 2 violations); MIRROR GREEN twin; an explicit clause that the
mirror fixture and the class-2 fixture are DISTINCT documents; and the four-way shared-predicate row.

`verify:` unchanged, byte-identical (below). Scope list, MAIN_SESSION_ONLY exemptions, exit-2
empty-scope rule, SCOPE COMPLETENESS five assertions, KIND-DRIFT registration note and the
closing "do not run the checker over the live tree" all retained — each asserted present.

## Move 2 — T-15

`Per-site direction assertions at the pinned tree, plus the whole-scope run at the reviewed sha`
· `traces: [REQ-02, REQ-04, REQ-06]` · `change_type: logic` · `execution_mode: main-session-direct`
· `depends_on: [T-12]` · files `.claude/skills/harness/bin/test-anchor-directions.py` and
`run-unit-tests.sh` · `verify: python3 .agents/skills/harness/bin/test-anchor-directions.py`.

- **Ref:** `HARNESS_REVIEW_SHA` when set and non-empty, else literal `HEAD`; validated with
  `git rev-parse --verify <ref>^{commit}`. Unresolvable ref = hard failure, never a working-tree
  fallback, never a skip. Every asserted byte comes from `git -C <root> show <ref>:<path>`.
- **Seven named rows, never a count** — SC-04 S1..S5 direction, plus SC-11's S2 observations path
  (both spellings, two rows) and S3's receipt path (row 3, shared with SC-04's S3).
- **Discriminating both ways:** helper `direction_failures(content, token_regex, expected_anchor)`
  fails when *no* anchored occurrence exists AND for *each* occurrence carrying the wrong anchor.
  This is precisely what the panel found missing from T-04/T-06/T-10/T-11's bare placeholder greps.
- **Red proof per row:** the helper is fired at a fixture *string* carrying the wrong anchor for
  that row and must return a non-empty failure list. Takes content, not a path, so nothing on disk
  is touched.
- **SC-04's remaining clause:** `--list-scope`, materialise each listed path's pinned bytes into a
  temp root at the same relative path, run the checker there with `--root`; assert exit 0, 0
  violations, and scanned count == materialised count (a lower count means the temp root did not
  reproduce the scope). T-12's run reads the working tree in CI and cannot discharge a criterion
  naming the reviewed sha.
- Registered in `UNIT_SCRIPTS`, explicitly NOT in `test_kinds.integration.detect`.

## Evidence

1. `plan-merge.py amend tasks:T-02.intent` — two invocations (the first applied the mirror, the
   second replaced it with the shared-predicate version after the 11-span count came back).
   `--expect-sha256 55a1c11cb6073d363ea66566dd41a35ab62817d1bacfc34ee7a660dae043a1d9` then
   `--expect-sha256 38d785bcee0a72b215cac225b74d9fd24099d24f63c13d222d11fdc687f06e64`; both printed
   `AMENDED tasks:T-02.intent` / `APPLIED …/plan.yaml`, `EXIT=0`.
   `plan-merge.py apply --proposal -` printed `ADDED T-15` / `APPLIED …/plan.yaml`, `EXIT=0`.
   A third amend corrected `tasks:T-15.execution_reason`
   (`--expect-sha256 f2919da0c1228efc86e6def56d034bf43959ef515d5f0d7c8d39267cf9da156e`): the first
   draft asserted `run-unit-tests.sh` resolves to NOBODY, which `check-plan-routes.py` disproved
   (granted to `harness-backend-dev, harness-dev-ops`). `AMENDED tasks:T-15.execution_reason`.
2. `len(tasks): 15` · `'approval' in doc: False` · `doc['status']: 'plan'` · task ids `T-01..T-15`
   · every task status `ready` · decisions `D-01..D-08`.
3. **The prescribed before-copy does not exist.**
   `git show HEAD:.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml` → exit **128**,
   `fatal: path … exists on disk, but not in 'HEAD'`; `git status --porcelain` →
   `?? .harness/harness/features/FEAT-52-factory-control-plane/`. The whole feature directory is
   untracked. Substituted with the pre-change values captured at read snapshot `#9524`, taken
   before either write:
   - T-01..T-14 `title`/`traces`/`change_type` unchanged: **True** (14/14, no mismatch).
   - T-02 `verify` byte comparison —
     before `b'python3 .agents/skills/harness/bin/test-check-instruction-paths.py\n'`,
     after identical, sha256 `a474a377b52edc72…` both sides.
   - T-02 non-intent fields all unchanged (id, title, traces, change_type, execution_mode,
     execution_reason, depends_on, status, files).
   - T-12 `verify` and `intent` tail byte-identical to the pre-change read.
   - `panel` untouched: 8 findings, `PF-93ebe15db8b/high`, `PF-4ea5b56692f/med`,
     `PF-da16f6e14be/med`, `PF-afe3e3d65fe/low`, `PF-8653185d920/low`, three `info` — **every one
     still `disposition: open`**, including the HIGH one (transcribing its resolution is a later
     segment's write, not this one's).
   - `sorted(tasks) == sorted(T-01..T-14 + T-15)` → **True**: only T-15 added, nothing removed.
4. `python3 .agents/skills/harness/bin/check-plan-routes.py <plan.yaml>` → `0 violation(s) across
   1 plan(s)`, `EXIT=0`. T-15's `DEVIATION` line is identical in shape to T-02's and T-12's — the
   expected DEC-174 carve-out output; only `VIOLATION` gates.
5. Files written, by path:
   - `.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml` (via `plan-merge.py` only)
   - `.harness/harness/features/FEAT-52-factory-control-plane/notes/research-FEAT-52-factory-control-plane-plan-repair-c5.md` (this file)
   - `/tmp/feat52-t02-intent.txt`, `/tmp/feat52-t15-proposal.yaml`, `/tmp/feat52-t15-reason.txt`,
     `/tmp/feat52-verify.py`, `/tmp/feat52-before-after.py` — scratch, outside the repository.

Nothing committed, nothing pushed, HEAD untouched, `run-unit-tests.sh` not run.

## Open for the next reader

- The `approval:` mapping is still absent — the separate, unruled operator blocker.
- The other seven panel findings remain `open` by instruction, for the batched signature review.
- Q1 (non-blocking): the shared predicate widened class 2 to the unsegmented `.harness/features/`
  spelling. If the operator wants class 2 left exactly as originally worded, the 11 template spans
  need their own exemption instead — say so before T-02 is built.
