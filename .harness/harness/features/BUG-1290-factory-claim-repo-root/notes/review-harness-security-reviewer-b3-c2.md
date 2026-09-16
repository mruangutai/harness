# Security review — BUG-1290 factory-claim-repo-root — B-3 fix cycle (c2)

**Verdict: PASS, severity_max=none.** Reviewed pin `7104aa43` (test-only, +14/-9 in one file)
against base `76e26386`. Production code (`.agents/skills/harness/bin/`, `.claude/skills/harness/bin/`)
is byte-identical over the full range — reverified myself: `git diff 76e26386 7104aa43 --stat --
.agents/ .claude/skills/` is empty. No must-fix findings, no new findings of any severity.

## The panel's question, answered

Yes — the changed fixture now actually binds REQ-02's issue-map clause. Before this diff,
`kaya_seg`/`harness_seg` both carried an EMPTY `factory.issues` map, so a mutant that re-keys
`_BlockerCache.issue_number`'s cache on `feature` alone had nothing to alias between segments
(empty vs empty is indistinguishable) — the boundary was asserted but unguarded. I independently
reproduced this myself, not by trusting the orchestrator's measurement: monkeypatched
`_BlockerCache.issue_number` in-process to drop `repo` from the cache key, re-ran the real test
file via `runpy.run_path` against the real `.claude/skills/harness/bin/factory_claim.py` at this
pin. Result: case 5b **FAILs** under the mutant, cases 5a/5c/5d/5e/5f stay green, matching the
orchestrator's independent probe. The unmutated baseline is the already-reported 124/124 `ok`.
Command used is reproducible from `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root`
(python3 -c script patching `factory_claim._BlockerCache.issue_number`, then `runpy.run_path` on
`tests/unit/test-factory-claim.py`).

## 1. Cache-isolation boundary — bound, not merely apparent

Confirmed above. `_BlockerCache` (in the real, unmutated production file) keys both `_plans` and
`_issue_maps` on `(repo, feature)` tuples (`factory_claim.py` — this repo's copy, not the stale
main-checkout copy a plain relative read/grep resolves to; verified I was reading the worktree
copy via absolute path after an early false start). `factory_config.features_root(repo_name)`
does the per-segment join. This matches the previous panel's (c1) Q2 finding exactly and the
B-3 fixture is what finally makes the issue-map half of that keying falsifiable.

## 2. Fixture safety — nothing attacker-influenced introduced

The delta only changes fixture DATA: `SEG_FEATURE = "FEAT-99-seg"` (unchanged, module constant),
two new `factory.issues` map entries (`{"T-77": 850}`, `{"T-99": 954}`) and one new
`rec.issue_data[954]` entry — all literals, hand-written in the test file, never derived from
issue/PR/label content, environment, or network input. `tempfile.mkdtemp` usage is unchanged
(same prefix pattern as every other case in this file). No issue number, label, or task id from
this diff flows into a path join except through the SAME `os.path.join(root, feature, ...)` seam
already reviewed pre-existing at c1 (INFO-2, unchanged shape). No new tempdir handling, no new
subprocess call, no new network path.

## 3. Bookkeeping (STATE.md, feature.json, plan.yaml) — no exposure

`plan.yaml` has zero diff over the full range (`git diff 76e26386 7104aa43 --stat --
.../plan.yaml` empty) — nothing to assess. `STATE.md`/`feature.json` diff (55/16 lines) is
narrative-and-run-bookkeeping only: cycle counts, run history entries (squad/agent/verdict
triples), the operator's already-public B-3 instruction, and open questions carried from the
prior cycle. Swept the WHOLE commit range (not just the named files) for secrets/token/key
patterns (`ghp_`, `sk-`, `api[_-]?key`, `secret`, `password`, `BEGIN ... PRIVATE KEY`, etc.) —
zero hits. Absolute paths naming the operator's own machine
(`/Users/molchairuangutai/GitHub/harness/...`) appear in several notes files in this commit
(ship-review html/md, handoff notes) — this is expected in this project's threat model (a
single-operator local harness, not a multi-tenant service; the path names the operator's own
checkout, not a secret), consistent with prior-cycle assessment. Not a finding.

## 4. Carried INFO items — reachability unchanged by this delta

`INFO-1` (`features_root`'s join not traversal-safe in isolation, inert because every call site
is fleet.yaml-exact-match constrained) and `INFO-2` (the `feature`-label-derived join has no
input validation, pre-existing) are backlog rows from the c1 review
(`notes/review-harness-security-reviewer-c1.md`). Not re-litigated as new findings here — they
are pre-existing, carried, and this run's `severity_max` reflects only NEW findings raised in
this delta (none). Since this delta touches `tests/unit/test-factory-claim.py` only and leaves
`factory_config.py`/`factory_claim.py` byte-identical, neither item's reachability moved in
either direction — the step-4 fleet.yaml membership filter and the unsanitised `feature` join
are exactly as they were at c1.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| served-repo A candidate reading served-repo B's issue-map cache | Information disclosure | true — `(repo, feature)` keying, now mutation-proven on BOTH the plan and issue-map halves (this fixture closes the gap the pre-B3 fixture left open) |
| fixture data (issue numbers, feature id) reaching a filesystem join | Tampering | true — all fixture values are static literals, not attacker-influenced; not a new surface |
| bookkeeping files (STATE.md/feature.json) leaking secrets or credentials | Information disclosure | true — swept whole commit, zero hits |
| carried INFO-1/INFO-2 reachability | Tampering / Information disclosure | true — unchanged by this delta, still gated by the pre-existing step-4 exact-match filter (INFO-1) / still low-impact pre-existing (INFO-2) |

## Findings

None gating. No must_fix. No new findings at any severity (carried INFO-1/INFO-2 are prior-cycle
backlog rows, unaffected by this delta — see §4).
