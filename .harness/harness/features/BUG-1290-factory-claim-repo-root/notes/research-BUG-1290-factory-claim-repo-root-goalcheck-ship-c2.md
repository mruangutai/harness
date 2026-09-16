# Goal-check c2 — BUG-1290, pin `7104aa43`

**All nine success criteria are MET. SC-02's B-3 residue is CLOSED, not relocated — proven by my own
two-seam mutant — but the proof is undefended by anything committed, so SC-02 is MET-with-residue.**
Every verdict below rests on a command I ran at this pin; nothing is transcribed from cycle 1. Runs
prefixed `env -u HARNESS_AGENT_TYPE`. The nine `verify:` strings were cross-checked against
`BRIEF.md:54-105` — no mismatch.

Delta re-measured: `git diff --stat 76e26386 7104aa43 -- .agents/ .claude/skills/` is empty;
production code is byte-identical between pins. The whole source delta is
`tests/unit/test-factory-claim.py` (+14/-9) plus feature bookkeeping. Working tree clean for
`tests/`, `.agents/`, `.claude/skills/` at HEAD `7104aa43`.

## Per-criterion verdicts

| SC | `verify:` as BRIEF writes it | What I ran at the pin | Observed | Grade | Status |
|---|---|---|---|---|---|
| 01 | test — `tests/unit/test-factory-claim.py` | suite | `ok BUG-1290 5a` … `124/124 checks passed.` | MET | carried forward |
| 02 | test — same | suite + my own two-seam mutant (below) | `ok BUG-1290 5b`; both mutants redden 5b | MET (residue) | **re-graded from scratch** |
| 03 | test — same | suite; read case at pin | `ok BUG-1290 5c`; asserts `"no plan could be read"` AND `expected_path` built with segment `zzz-missing-segment` (`:1224-1230`) | MET | carried forward |
| 04 | test — same | suite; read case at pin | `ok BUG-1290 5d`; calls production `fc.features_root("owner/harness")` unpatched vs `<root>/.harness/harness/features` (`:1236-1244`) | MET | carried forward |
| 05 | test — same | suite; `git show 7104aa43:tests/unit/test-factory-claim.py \| grep -n FEATURES_ROOT`; import probe | `ok BUG-1290 5e`; grep returns only `1246/1248/1250/1251` (the 5e hasattr case) — the two `eb9d044e:58-68` module-scope cases are gone, not re-pinned; `hasattr FEATURES_ROOT: False` | MET | carried forward |
| 06 | test — same, case `BUG-1290 5f` | suite; **D-03's regex re-run by me over the three pinned blobs** | `ok BUG-1290 5f`; counts `factory_claim.py 0`, `feature-worktree.py 0`, `factory_config.py 1` — the single hit `factory_config.py:387 return repo_name.split("/", 1)[-1]`. Reach: `factory_claim.py:95/119/137 factory_config.features_root(repo)` → `factory_config.py:395 seg = segment_of(...)`; `feature-worktree.py:86` direct; `factory_config.py:403` (workspace_path) direct | MET | carried forward |
| 07 | test — `tests/integration/test-factory-integration.py` | suite (named lines, not exit code — one global FAILS counter) | `131/131 checks passed.`, `ok (F) claim exits 0`, `ok (H) claim against the two-board fleet exits 0`, zero `FAIL` lines. Non-vacuous: fixture segment is `acme/widget` → `widget` (`:488`, `:883`, `:1247`) | MET | carried forward |
| 08 | test — `tests/unit/test-factory-claim-mutation.py` | suite (marker lines, not exit code) | `BASELINE 3/3 ok`, `MUTANT ACTIVE`, `FAIL BUG-1290 5a/5b/5c`, `MUTATION PROOF: 3/3 cases reddened` | MET | carried forward |
| 09 | test — `tests/integration/test-layout-migration.py`, plus T-04's reader-row probe | suite + T-04's probe verbatim from `plan.yaml` | `ok - case 22: real root's harness/features surface is CLEAN with migrated evidence`; `READER ROW PROBE: ok 5 {...factory_config.py: 'migrated'...}` rc 0 — five features rows, `factory_claim.py` absent, pattern ladder live | MET | carried forward |

Tally: **9 MET, 0 UNMET.** Gate records agree and were re-read, not assumed: qa PASS `matrix_ok: true`
(`notes/qa-2026-09-06-03-validator.md:3,117-119`), panel PASS `must_fix: []`
(`runs/2026-09-06-05-validator/digest.md`).

## SC-02 — my own two-seam mutant, raw output

Harness `/tmp/bug1290-c2-pm/mutant.py` (mine, not the orchestrator's probe): patches
`_BlockerCache._plan` or `_BlockerCache.issue_number` to key on `feature` alone, then runs a given
copy of `test-factory-claim.py` in-process via `runpy`. Each pin's suite blob extracted with
`git show <pin>:tests/unit/test-factory-claim.py` into a temp root whose `.claude` is a symlink to
the worktree's, so the real production module is imported.

```
# suite at OLD pin 76e26386
MUTANT[none]   {5a: ok, 5b: ok,   5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['124/124 checks passed.']
MUTANT[plans]  {5a: ok, 5b: FAIL, 5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['1 of 124 FAILING.']
MUTANT[issues] {5a: ok, 5b: ok,   5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['124/124 checks passed.']
# suite at NEW pin 7104aa43
MUTANT[none]   {5a: ok, 5b: ok,   5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['124/124 checks passed.']
MUTANT[plans]  {5a: ok, 5b: FAIL, 5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['1 of 124 FAILING.']
MUTANT[issues] {5a: ok, 5b: FAIL, 5c: ok, 5d: ok, 5e: ok, 5f: ok} | ['1 of 124 FAILING.']
```

Reading: the plan-cache seam discriminated at both pins. The **issue-map seam reddened NOTHING before
the delta and reddens 5b after it** — that is exactly the B-3 gap, measured by me, closed. Check count
is 124 at both pins, so nothing was traded away to get it.

## Q1 — is the B-3 residue closed, or relocated?

**Closed at this pin, and undefended. SC-02 is MET on the criterion's own words.**

I reproduced the panel's finding myself: deleting the single fixture fragment `depends_on=["T-99"]` at
`tests/unit/test-factory-claim.py:382` (variant built in `/tmp/bug1290-c2-pm/nodep/`) gives

```
MUTANT[none]   {... 5b: ok ...} | ['124/124 checks passed.']
MUTANT[plans]  {... 5b: FAIL ...}
MUTANT[issues] {... 5b: ok ...} | ['124/124 checks passed.']
```

— the issue-map seam is blind again and the suite stays fully green, so no committed assertion would
report the loss. The property is therefore **proven, not defended**.

SC-02's words are: "each candidate's verdict is computed from its own plan; a case proves the second
candidate does not receive the first's cached task." At `7104aa43` a case does prove that, and the
issue-map half of REQ-02 is now proven too. Fragility of a fixture is a durability weakness, not a
failed criterion — and converting it into a gate would be adopting a criterion BRIEF never stated. It
goes back as backlog row **R-1 (chore)**, below, not as UNMET.

## Q2 — did any SC get met for a weaker reason?

**No SC weakened. One got stronger; the rest are unchanged.**

`build_features_root()`'s two edited segment roots are consumed by exactly two cases —
`SEG_FEATURE`/`REPO_KAYA`/`REPO_HARNESS_SEG` appear only at `:65-71`, `:336-383` (the builder) and
`:1162-1200` (5a, 5b). 5c uses a deliberately absent segment; 5d/5e/5f touch no fixture.

- **SC-01 (5a): unchanged.** kaya-ai's DAG is untouched (`T-77` depends on `T-88`); the added map entry
  `{"T-77": 850}` is not the blocker key looked up, so `unresolvable blocker` still comes from `T-88`
  being absent from kaya's own map.
- **SC-02 (5b): stronger.** The harness candidate's "clear" verdict was previously vacuous (`T-77`, no
  deps); it now requires resolving `T-99` through the harness segment's OWN map to closed issue 954.
  The clear verdict now exercises the issue-map path instead of skipping it.
- **SC-08: unchanged.** Re-run at this pin: `BASELINE 3/3 ok` / `MUTATION PROOF: 3/3 cases reddened`.
- **SC-03/04/05/06/07/09: unchanged** — no fixture or production input they read is in the delta.

## Residual findings for the briefing backlog

- **R-1 (chore, SC-02's residue).** Nothing committed defends the issue-map proof: deleting one fixture
  fragment (`:382`) restores the blind state with `124/124` green. Cheapest durable fix is a second
  mutant in `tests/unit/test-factory-claim-mutation.py` that discards the repository argument at the
  issue-map seam and requires 5b to redden — the same shape T-05 already uses for `features_root`.
- **R-2 (record note, not a question).** REQ-05's prose still says the rule is "called by
  `factory_claim.py`" where the measured reach is transitive through `features_root` (re-measured at
  this pin, SC-06 row above). Unresolved **by the operator's explicit choice** to leave approved
  artifacts unchanged; recorded here only so the record is not silent about it.

## Emergent criteria

**None.** Nothing the delivered change makes necessary sits outside BRIEF's nine criteria; R-1 is a
durability improvement to SC-02's existing evidence, not a new criterion.
