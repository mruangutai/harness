## BUG-1290 · plan panel · executability read — VERDICT: FAIL

**Headline:** the plan is otherwise sound and its two most load-bearing mechanisms (T-05's mutation
proxy, T-04's reader-row probe) hold up under hostile tracing — but T-02/T-03 cannot both complete
as scoped: a SECOND hardcoded-`harness`-segment fixture in `tests/integration/test-factory-integration.py`
(case (H), `:1245-1246`) is outside every task's edit permission, and it will redden T-03's own
verify chain after a *correct* T-03 implementation.

### PANEL-01 — severity: high — must_fix — targets T-02, T-03

`tests/integration/test-factory-integration.py` has **two** end-to-end cases that build a feature
fixture under the literal `.harness/harness/features/...` while driving `claim --repo REPO` with
`REPO = "acme/widget"` (`:487`): case (F) at `:881-882` (fixed by T-02) and case (H)
`FEAT-INTEG-TWOBOARD` at `:1245-1246` (**not touched by any task**). T-02's own intent (`plan.yaml`
T-02 step 3) says *"Change nothing else... and no second case is added"* — case (H) is explicitly
out of T-02's reach. T-03's `files:` list (`factory_claim.py`, `feature-worktree.py`,
`factory_config.py`) does not include this test file either.

Traced concretely against the real, unmodified code: post-T-03, `_BlockerCache` resolves
`factory_config.features_root("acme/widget")` → segment `widget`. Case (H)'s plan lives at the
`harness` segment, so `cache.plan_loaded(feature)` is `False` → `_blocker_gate` returns
`("no_plan", ...)` (`factory_claim.py:176-177`). Case (H) calls `claim` **without** `--issue`
(poll mode, `test-factory-integration.py:1259-1262`), so the `no_plan` branch takes the
`print(...); continue` path (`factory_claim.py:290-294`), not `factory_cli.refuse`. With only one
candidate, the loop exhausts and hits `factory_cli.nothing_to_do(TOOL, "no claimable work")`
(`factory_claim.py:300-301`), which is `sys.exit(EXIT_NOTHING)` = **1** (`factory_cli.py:27,56-57`).
That reddens `check("(H) claim against the two-board fleet exits 0", r2.returncode == 0, ...)`
(`:1266-1267`). The file has one global `FAILS` counter and one `sys.exit(1 if FAILS else 0)`
(confirmed by the eng-segment's AR-05 finding, already applied elsewhere in this plan), so this one
case reddens the WHOLE file, which is chained with `&&` inside T-03's verify. **T-03 as scoped
cannot pass its own verify without a doer silently going out of `files:` scope to fix case (H), or
the plan widening T-02 (or adding a task) to migrate it too.**

Remedy is mechanical and cheap: extend T-02 to move both `:882` and `:1246`'s `feat_dir` onto
`REPO`'s segment, and drop T-02's "no second case is added" prohibition, or split case (H)'s move
into its own step. Either way this is a plan edit, not mine to make.

### PANEL-02 (P1 / F-04) — severity: med — advisory, not must_fix — targets SC-05, REQ-07, T-01 step 2

**Verdict: prose is not sufficient as an automated gate, but a full mechanical fix is hard, and the
plan's own doctrine already accepts an analogous residue elsewhere.** SC-05/REQ-07's "the two
module-scope cases … are gone rather than re-pinned" clause is enforced only by T-01 step 2's prose
("do not convert the two deleted cases into weaker assertions"). No task step or verify command
scans for it: T-01's verify only requires per-case `FAIL` markers for 5a-5f; T-03's verify checks
suite-exit-0 plus a text scan for the literal string `FEATURES_ROOT` in `factory_claim.py` — neither
would notice two *replacement* checks sitting where `:58-68` used to be, so long as they're
independently true (e.g. duplicating case 5e's `hasattr` assertion under new names). This is the
same class of gap segment 1 closed for F-03/F-05/F-06 with real markers/probes, and this residue
was left non-gating there too — I concur it's advisory, not must_fix, because (a) a fully mechanical
scan can't distinguish "weakened" from merely "differently phrased" any more than D-03's own scan
can (D-03's `because:` explicitly accepts this class of residue for SC-06), and (b) two
conspicuously "extra" checks sitting where two clear deletions were instructed is the kind of thing
an ordinary diff read catches. Recommend (not required): a lightweight case-count or line-count
invariant near the deletion site, mirroring D-03's spirit, if the operator wants this closed
mechanically rather than by review.

### PANEL-03 (P2 / T-05 mechanism) — no finding, mechanism verified sound — targets SC-08, T-05

Traced the attribute-lookup order concretely and it holds. `factory_claim.factory_config` is
rebound to the proxy; `factory_claim`'s production code resolves the name `factory_config` via
`LOAD_GLOBAL` **at call time**, so it always sees the current (rebound) value — this is how the
proxy intercepts even though T-01's suite patches `factory_config.features_root` on the real
module. The proxy's wrapped `features_root` re-fetches the delegate's *current* `features_root`
attribute at call time (not a value snapshotted at proxy-construction), so it correctly picks up
the suite's own per-run patch and discards only the `repo_name` argument — exactly reproducing
"one root for every candidate."

I also settled the `runpy.run_path(..., run_name="__main__")` re-import concern empirically rather
than assuming it: built a throwaway harness (`sys.modules` pre-populated with a stub module,
mutated its attribute *between* two `runpy.run_path` calls of a script that does a plain
`import`) — the mutation **survived** into the second run, confirming CPython's import cache means
`import factory_claim` inside the re-executed script does not reset or reload an
already-imported module. This matches this plan's own recorded measurement in
`notes/research-BUG-1290-factory-claim-repo-root-fix-c2.md` ("a `mruangutai/kaya-ai` candidate
resolves to `…/.harness/harness/features` … Attribute delegation is at call time, so the mutant
survives the suite's patch"). Baseline-then-mutant ordering is safe: the proxy is installed only
*after* baseline evidence is captured, and the single restore-at-exit is adequate because
`run_pool.py` runs every `tests/unit/test-*.py` file as its own subprocess
(`run_pool.py:61-62`) — there is no shared-interpreter cross-file leakage to guard against; the
restore is good hygiene for this file alone, not a cross-file safety requirement.

### PANEL-04 (P3 / T-04 case-22 comment) — no finding, legitimate — targets T-04 step 3

A comment-only edit is inherently unverifiable — comments aren't executable, so no assertion can
bind them. T-04's actual deliverable (the reader-row MOVE) is gated by two things I ran myself, not
merely trusted from the digests: `python3 tests/integration/test-layout-migration.py` (exit 0,
case 22 `ok`, unchanged) and the verify's inline reader-row probe (exit 1, `READER ROW PROBE: FAIL`,
five rows, `factory_claim.py` still classified `migrated` — i.e. genuinely red at `eb9d044e`,
confirming it will discriminate once the row moves). Requiring every prose change to carry its own
gate is an unreasonable bar when the substantive change is already gated. Legitimate scope, not a
defect — matches segment 1's own (non-gating) read.

### Stage A — scope and traceability: no findings

All of REQ-01..08 appear in at least one task's `traces:` (T-01: REQ-01..07; T-02: REQ-01,07; T-03:
REQ-01..06; T-04: REQ-08; T-05: REQ-07) — no orphans, no task citing a nonexistent id.
`depends_on` (`T-01:[]`, `T-02:[T-01]`, `T-03:[T-01,T-02]`, `T-04:[T-03]`, `T-05:[T-03]`) is a valid
topological order; T-05 doesn't list T-01 directly but reaches it transitively through T-03, which
is fine. No task's `files:` omits a file its `intent:` edits (checked all five). No task's `verify:`
asserts something a predecessor deletes.

### Anchor audit (item 4) — all confirmed exact, no drift

Re-read at the worktree tip, not taken from any digest: `factory_claim.py:26-29,48-50,341,343`
(`FEATURES_ROOT` + docstring + construction site); `factory_config.py:382-387` (`workspace_path`);
`feature-worktree.py:64-87` (`resolve_repo`); `layout_migration.py:92-94` (the reader row) and
`:98-104` (FEAT-42 precedent comment); `layout_fixtures.py:45-48,53-56,68-71` (STUB keys + import
guard); `test-layout-migration.py:422-425` (case 22 comment); `test-factory-integration.py:487,
879-883` (REPO + case F fixture). Every one matches the plan's citation exactly. D-03's regex was
re-run directly (not trusted from the fix-c2 note): 0 matches in `factory_claim.py`, 1 in
`feature-worktree.py:86`, 1 in `factory_config.py:386` — matches the plan's measurement.

### Closed ground — not re-raised

F-03 (T-01 aggregate exit code), F-05 (T-04 case-22 insufficiency), F-06 (SC-06 one-spelling scan),
F-02/SC-08 (mutation proof had no carrier) are all applied with T-05 added as the real carrier;
confirmed via the digests plus my own re-run of the D-03 scan and the T-04 probe rather than taking
either on trust. Not re-litigated.

### Byte-stability

`BRIEF.md` and `plan.yaml` were only ever opened via the `read` tool this session — no `write`/`edit`
call was made against either path.
