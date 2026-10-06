# Research-backed merge proposal; archival carry entries are supplied from the immutable archive by the recorded apply command.
schema: plan/1
feature: FEAT-1559-corpus-outside-worktree
status: plan
source_issues: [1559]
lanes:
  resolved_at: 652e70d4
  rows:
    - surface: .claude/skills/harness/bin/**
      lane: main-session-direct
      reason: DEC-174 forbids execution through the enforcement layer being changed.
    - surface: .claude/skills/harness/hooks/**
      lane: main-session-direct
      reason: DEC-174 covers executable git hooks and their tests.
    - surface: tests/**
      lane: main-session-direct
      reason: DEC-174 includes enforcement-layer tests.
    - surface: AGENTS.md
      lane: main-session-direct
      reason: Main session completes the enforcement cutover documentation.
    - surface: .claude/skills/harness/SKILL.md
      lane: main-session-direct
      reason: Main session completes the enforcement cutover documentation.
    - surface: .claude/skills/harness-verification-rules/SKILL.md
      lane: main-session-direct
      reason: Main session completes the enforcement cutover documentation.
    - surface: .harness/README.md
      lane: main-session-direct
      reason: Main session completes the enforcement cutover documentation.
    - surface: .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/**
      lane: main-session-direct
      reason: Main session owns host measurements and immutable verification receipts.
decisions:
  - id: D-01
    choice: Keep only the uniquely resolved active feature directory materialised in record-bearing linked checkouts, across every .harness segment; leave plain clones and non-record-bearing probes unchanged.
    because: The operator ruled never materialised, not clone-on-write; feature worktrees, fleet planning worktrees and validator pins all multiply reference records.
    dec: DEC-95
  - id: D-02
    choice: Read other landed feature records as ordinary absolute files at the resolved worktree owner root; agents use injected HARNESS_CONTROL_PLANE_ROOT and tools use harness_boundary owner resolution, with explicit named refusal if unavailable.
    because: B preserves filesystem readers and existing cross-checkout write refusal without a symlink provider or git content reads; BUG-1016 leaves absolute read targets unchanged.
    dec: DEC-193
  - id: D-03
    choice: Separate checkout-local active-feature auditing from owner-root repo-wide record auditing and peer-worktree enumeration; verify the named subject set before constructing downstream invariant context.
    because: Filtering ctx.features after loading every BRIEF, plan and state still reads the whole corpus; a sparse success over a subset is not an audit.
    dec: none
  - id: D-07
    choice: Execute every enforcement, hook, validator and test task directly in the main session under DEC-174; planning is permitted now, execution waits for the FEAT-57 frozen-and-spot-checked replay receipt and serialized audit edits.
    because: The enforcement layer cannot reliably supervise its own cutover and the source issue retains a pre-build dataset prerequisite.
    dec: DEC-174
  - id: D-08
    choice: Derive the sparse directory set from tracked directory metadata, exclude every .harness/*/features subtree, and re-add the exact active directory in its uniquely discovered artifact segment; use no top-level allowlist.
    because: Cone mode includes sibling files in parent directories, fleet planning records may live outside the worktree segment, and newly tracked top-level directories must survive without manual list edits.
    dec: none
  - id: D-09
    choice: Replace the archived symlink corpus provider with owner-root filesystem reads and a small feature_corpus seam shared by record population readers; never search in-progress sibling records.
    because: The settled B choice avoids .harness/corpus, sentinel materialisation and alternate content-provider abstractions; missing roots are errors rather than fallback subsets.
    dec: none
  - id: D-10
    choice: Apply worktree-state.py repair from post-checkout, post-merge and post-rewrite and verify at audit or corpus-dependent gate entrypoints; leave feature-worktree.py and pinned-checkout.py creation algorithms unchanged.
    because: Git hooks cover the shared worktree creation boundary regardless of creator; helper-only repair misses bare git worktree add, merge-induced skip-bit changes and rebase.
    dec: DEC-95
  - id: D-12
    choice: Retain distinct failures cone 3, skip-bits 4, materialised feature names 7 and dirty tree 8; verify never mutates, repair refuses dirty inputs, and audit treats dirty 8 as a non-gating report while structural failures refuse.
    because: Removing the symlink provider removes exits 5 and 6; pre-commit must not deadlock dirty work and no gate may repair the state it is judging.
    dec: none
tasks:
  - id: T-01
    title: Build the sparse state command and minimal synthetic checkout fixture
    traces: [SC-01, SC-02, SC-04, SC-05, SC-06, SC-07, SC-13]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 covers the enforcement command and its tests; do not delegate execution.
    depends_on: []
    status: ready
    files:
      - .claude/skills/harness/bin/worktree-state.py
      - .claude/skills/harness/bin/feature_corpus.py
      - tests/unit/test-feature-corpus.py
      - tests/integration/f58_sparse_fixture.py
      - tests/integration/test-worktree-state.py
      - tests/unit/test-worktree-state.py
      - .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/suite-baseline.md
    verify: |
      set -e
      python3 tests/unit/test-worktree-state.py
      python3 tests/integration/test-worktree-state.py
      python3 tests/unit/test-feature-corpus.py
      # Expected: each exits 0 within 60 seconds, with named negative cases and no host worktree mutations.
    intent: |
      Work only in the feature worktree and execute directly in the main session under DEC-174. Before any production edit, confirm the FEAT-57 frozen-and-spot-checked replay receipt and serialized ownership of check_state/ edits; record the immutable pre_change_sha resolved from supplied 652e70d4 in suite-baseline.md. Run each new behavior assertion against the pre-change implementation to capture discriminating failure before the implementation; absent new command is a bootstrap red only, not proof of every predicate. Use tests/integration/f58_sparse_fixture.py as the carried archive D-11 fixture name: git init a minimal temporary repository, commit synthetic nested .harness records in harness and a fleet segment, required non-feature paths and a newly tracked top-level directory, then create real git worktrees and disposable pins. Never copy this checkout or its .git directory. A context manager removes only its owned temporary fixtures and exposes roots and creation commands.
      Define REQUIRED_PATHS once in f58_sparse_fixture.py for fixture assertions, including .agents/skills, .claude/skills/harness, .harness/harness/docs, .harness/expertise, .harness/factory, .harness/domains, .harness/examples and .harness/notes. Synthetic fixture contents create these non-feature paths. Tests import this constant rather than duplicating it; production sparse derivation never uses it as an allowlist and the rejected .harness/corpus symlink is not a required path.
      Add a CLI worktree-state.py with mutually exclusive --verify and --repair and optional --checkout PATH defaulting to the caller's checkout. Reuse harness_boundary worktree_owner to distinguish non-linked clones, recognized record-bearing worktrees and non-record-bearing arbitrary probes; verification and repair on non-linked clones and non-record-bearing probes return 0 and describe the no-op. Recognize harness planning worktrees by their FEAT/BUG directory id, fleet planning worktrees by the same class even when records are in a different artifact segment, and .pins names by pinned-checkout.py _pin_name's exact feature--run-id--persona form. Code-only fleet checkout roots with no harness marker are no-op subjects, not harness planning trees. Bare arbitrary probes remain no-op even if records exist at their revision.
      Add --json for machine consumers: one object containing checkout, checkout_class, active_feature, artifact_segment, mode, noop and findings; findings is an ordered array of objects with code, label and sorted paths. Labels are dirty, cone, skip-bits and materialisation, with codes 8, 3, 4 and 7 respectively. All detected categories are retained even when the process selects one code. Human output names the same categories and repair command. Gate callers use --verify --json and inspect every structural finding, not a text substring or only the selected exit.
      Discover the active artifact directory from exact active-id paths across .harness segments in tracked structural metadata and existing checkout/owner directory entries. Do not infer it from the worktree segment. Do not require feature.json: record-less directories count. If no exact active directory can be established or more than one segment claims it, refuse with the candidate names and cone exit 3; no fallback to the harness segment. Derive includes from all tracked directories, keeping every top-level source tree and every non-feature .harness subtree, exclude all feature subtree siblings, then add the exact active directory. Verify actual cone configuration, skip-worktree bits and materialised feature-directory names independently, in stable priority order dirty 8, cone 3, skip-bits 4, materialisation 7. Report all concrete discrepancies even when one code wins. Never invent symlink-provider exits 5 or 6. Both modes diagnose dirty input first; neither force nor mutate dirty work. Verify hashes filesystem/config/index before and after to prove no mutation. Repair clean inputs with sparse-checkout and index operations only, and prove a second repair changes neither bytes nor configuration. Materialisation assertions inspect all feature directories and files, including ignored/untracked sentinels, so unexpected directories cannot hide behind tracked-only counts. Non-feature content must remain available.
      Unit cases exercise pure directory-set derivation, newly tracked top-level inclusion, active fleet segment and pin parsing, absent/ambiguous active ids, and failure-code prioritisation. Integration cases cover all three record-bearing classes, fresh clone no-op, arbitrary probe no-op, wrong cone, cleared skip-bits, another materialised feature, a dirty tree, repair idempotence and dirty non-mutation. Inject nested record-bearing and record-less directories to prove the name-set subject. Record the exact baseline subject, BRIEF pending condition, baseline commands and raw exits; do not run the standing full suite from this fixture.
      Execute directly under DEC-174. Capture discriminating failures before implementation and use T-01 fixtures, never a full repository copy. Add one small feature_corpus.py seam reusing harness_boundary owner resolution. Expose complete landed directory and record discovery, on-demand branch claims and checkout-local active selection without a provider-class hierarchy, cache, symlink or git-content fallback. Owner reads are absolute ordinary files. Unknown/unreadable owner roots and missing expected directory names raise one named discovery error propagated as the caller's established refusal shape; never return an empty list in place of an error. Compare structural expected directory names with reached names, including record-less directories; distinguish legitimate plain-clone empty corpora from missing required roots. Do not search sibling in-progress records. Use actual record files for legacy .json/.yaml/.yml validation; missing metadata remains available to the consuming invariant rather than being erased from the directory census.
      Compute branch claims on demand, no exemption JSON writes. The only era exemption is the exact FEAT-02 and FEAT-03-subissue-mirror feature-id set, with the reason beside the predicate; missing, empty and literal none branches are sentinels. Emptying the reason or adding a third claimant defeats the exemption. One collision produces one finding listing every claimant in sorted order. Do not rewrite historical feature.json records.
  - id: T-02
    title: Scope audit preload and add named-set verification before invariant dispatch
    traces: [SC-03, SC-04, SC-05, SC-06, SC-09, SC-13]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 covers check_state and its tests; direct execution only.
    depends_on: [T-01]
    status: ready
    files:
      - .claude/skills/harness/bin/check_state/ctx.py#Ctx
      - .claude/skills/harness/bin/check_state/runner.py#main
      - .claude/skills/harness/bin/check_state/table.py#INVARIANTS
      - .claude/skills/harness/bin/check_state/board.py
      - .claude/skills/harness/bin/check_state/worktrees.py
      - .claude/skills/harness/bin/check_state/corpus.py
      - tests/integration/test-check-state-corpus.py
      - tests/unit/test-check-state-corpus.py
    verify: |
      set -e
      python3 tests/unit/test-check-state-corpus.py
      python3 tests/integration/test-check-state-corpus.py
      # Expected: both exit 0 within 60 seconds; full/sparse finding equality and open-name confinement are asserted.
    intent: |
      Execute directly under DEC-174, using the T-01 synthetic fixture and fail-first evidence before production edits. Preserve all invariant predicates and findings except new explicit subject/layout refusals. In runner.main, before Ctx construction and any invariant dispatch, call worktree-state.py --verify --json on record-bearing linked callers, never --repair. Codes 3, 4 and 7 refuse with the concrete layout diagnosis and command to repair; code 8 reports the dirty state and continues the ordinary audit. Combined dirty and structural discrepancies still refuse structurally, by inspecting every finding in the JSON report instead of masking structural findings behind the selected dirty exit. An unusable JSON report is an attributed refusal, never permission to continue. --list remains metadata-only. Plain clones retain full auditing.
      Determine the audit subject before any feature-file preload. A record-bearing linked checkout's default is its one active feature; an explicit --feature must name an available checkout-local subject or refuse before Ctx. Do not silently widen to owner-root data or narrow to an empty selection. Ctx _load_features, _load_plans, _load_plan_docs and _load_states_and_abandoned iterate the selected feature directories only, including run reads reached by invariants. A plain clone with no explicit selector still loads its full corpus. Keep repo-wide invariants separate from feature-local data; route global record populations through feature_corpus supplied by T-01, while retaining host config reads locally. Do not add compatibility fallback scans; T-01's seam exists before this task begins.
      Add a separate lazy owner-record view for truly repo-wide record predicates, without changing the checkout root used by host/git/config invariants. Use that view for factory claim population in board.inv_24, global board population discovery, and worktrees.inv_29's landed-terminal lookup, preserving each invariant's explicit selector semantics and existing environmental silences. Do not preload main's BRIEF, state or run files merely to inspect branch claims. Add check_state/corpus.py inv_52 and register INV-52 in table.INVARIANTS as a repo-scoped branch-claims row declaring its feature.json read dependency; use feature_corpus's on-demand landed branch predicate, even for a --feature invocation. The exact era exemption, sentinels and collision-name formatting are T-01's contract. Audit failure must not hide the new branch invariant behind a local one-record population. Instrumented tests distinguish selected checkout-local feature opens from declared owner-root global opens; the former stay confined to the active feature, the latter read only the records required by their named repo-wide predicate. Unit and integration cases include a duplicate owned by two other landed features while the active checkout remains sparse. INV-23's budgets and feature-specific build-entry expectations retain their selected-subject semantics, not an accidental whole-corpus widening.
      Compare expected and reached directory name sets using structural/index metadata plus current directories, not a feature.json glob. Record-less directories must participate. Missing expected names refuse before downstream invariants with counts, sorted missing/unexpected names and a checkout/repair remedy; unexpected-only uncommitted names are a non-gating report. Preserve selected-subject findings for full versus sparse synthetic subjects after normalising checkout prefixes, without hiding expected warnings. Add unit checks of subject selection and set diagnostics, and integration open instrumentation showing no other checkout-local feature's BRIEF, plan, state, feature.json or run file is read. Owner-root opens are permitted only for explicitly declared repo-wide predicates and are instrumented separately. Include a deliberately missing selected feature, a missing record-less directory, one downstream-not-run witness and dirty/non-dirty structural controls. Mark detected local feature enumeration sites with the exact scope vocabulary supplied by T-03's census; table declarations keep their meaning and are not record-content providers.
  - id: T-03
    title: Centralise owner-corpus discovery and migrate global gates and peer enumeration
    traces: [SC-02, SC-04, SC-05, SC-09, SC-13]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 covers gate scripts, boundary resolution and their tests; direct execution only.
    depends_on: [T-01, T-02]
    status: ready
    files:
      - .claude/skills/harness/bin/harness_boundary.py#linked_worktrees
      - .claude/skills/harness/bin/merge-gate.py#feature_for
      - .claude/skills/harness/bin/branch-create-gate.py
      - .claude/skills/harness/bin/check-domain.py
      - .claude/skills/harness/bin/board_lifecycle.py#_feature_dirs
      - .claude/skills/harness/bin/check-plan-routes.py#discover_plans
      - .claude/skills/harness/bin/validate-feature-json.py#discover_paths
      - .claude/skills/harness/bin/layout_migration.py
      - .claude/skills/harness/bin/layout_fixtures.py
      - .claude/skills/harness/bin/dispatch-guard.py
      - .claude/skills/harness/bin/digest_destination.py
      - tests/unit/test-feature-corpus-gates.py
      - tests/integration/test-feature-corpus.py
      - tests/integration/test-feature-corpus-census.py
    verify: |
      set -e
      python3 tests/unit/test-feature-corpus-gates.py
      python3 tests/integration/test-feature-corpus.py
      python3 tests/integration/test-feature-corpus-census.py
      # Expected: each exits 0 within 60 seconds; allow/deny is asserted from hook JSON, not process exits.
    intent: |
      Execute directly under DEC-174 and capture discriminating failures before every behavior edit. Use the completed T-01 fixture and feature_corpus seam; do not reimplement or edit that seam here. The task owns the consumer cutover and census, not provider files. Each corpus-dependent gate invokes worktree-state.py --verify --json and refuses every structural finding even when dirty is the selected process exit; invalid report data refuses with an attributed error.
      In harness_boundary.linked_worktrees normalize any linked caller to its owning root before enumerating .git/worktrees, preserving arbitrary registered peers and existing shared-owner legitimacy checks. This fixes check-domain and validate-digest callers without replacing the existing worktree enumeration with record discovery. Direct governed write paths retain DEC-193's no-git-subprocess property; do not call worktree-state or structural git queries from those Write/Edit/Bash guards. Test their existing refusal against resolved main corpus paths using the registered entrypoints and inspect the actual decision carrier rather than assuming an exit means denial. check-domain's governed-run sweep remains own-checkout local, with no sibling record provider. Its hardlink scan behavior is untouched.
      Migrate merge-gate.feature_for, branch-create-gate's flow discovery, board_lifecycle._feature_dirs, default check-plan-routes discovery and default validate-feature-json discovery to owner-root population reads. Explicit path arguments remain explicit checkout-local subjects. Branch-create flow existence can consider its own active unlanded record plus landed owners, but never siblings; branch uniqueness is landed-only as the grilling accepts. Before corpus-dependent gate scans, call verify without repair and map structural findings to their established refusal payload; dirty is a non-gating report, not a refusal by itself. Preserve merge policy and branch-create branch checks, including zero-owner rules where no corpus verdict is required, rather than inventing blanket branch denial. Test sparse controls, missing roots and missing directory sets, all reported through permissionDecision when applicable.
      Classify layout migration evidence as checkout-local and preserve its migration semantics; adjust its coupled-reader table and fixtures when joins move to feature_corpus, without retaining dead signature rows just to satisfy tests. digest_destination and dispatch-guard authorization reads stay explicitly bound to their selected feature root; add local-scope markers, not owner-root redirection. Add the census test over actual Python AST call sites and imported glob aliases. Preserve the archive's closed four-value vocabulary: corpus-scope: owner-root, corpus-scope: active-feature, corpus-scope: checkout-local and corpus-scope: not-a-corpus-read. A detected owner-root site must sit in a file that names feature_corpus, not necessarily in its marker. Detect wildcard feature-directory enumerations and glob patterns supplied via named constants, excluding mere regex shape strings, docs and deliberate fixture text. Quantify both assertions over detected sites only: exactly one vocabulary marker per detected site, and every detected owner-root site sits in a file naming feature_corpus. No assertion quantifies over the marked set; do not require markers on undetectable sites, especially linked_worktrees' .git/worktrees enumeration. Do not pin a scanner census figure. Record the blind class of dynamically assembled patterns whose feature segment is not statically detectable in the final census receipt. An injected scratch glob site without a marker must fail. T-02 owns its marker edits and uses this same vocabulary; do not edit its files here. Unit proof covers owner resolution, peer enumeration parity, duplicate/sentinel/exact-exemption predicates. Integration proof uses main-versus-sparse reads, branch and merge payloads, both write guard routes, unresolved corpus root, missing record-less directory, and scanner discrimination. Do not change gh-sync's loader, stale feature records, hardlink semantics or worktree removal.
  - id: T-04
    title: Enforce repair at Git checkout merge and rewrite hooks
    traces: [SC-01, SC-07, SC-08, SC-09]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 forbids hook and hook-test delegation.
    depends_on: [T-01, T-03]
    status: ready
    files:
      - .claude/skills/harness/hooks/post-checkout
      - .claude/skills/harness/hooks/post-merge
      - .claude/skills/harness/hooks/post-rewrite
      - tests/unit/test-worktree-state-hooks.py
      - tests/integration/test-worktree-state-hooks.py
    verify: |
      set -e
      python3 tests/unit/test-worktree-state-hooks.py
      python3 tests/integration/test-worktree-state-hooks.py
      # Expected: both exit 0 within 60 seconds; shims return 0 and each named Git operation preserves layout and delegate integrity.
    intent: |
      Execute directly under DEC-174 and capture each hook behavior failure before production edits. Install tracked executable post-checkout and post-rewrite scripts beside the existing post-merge; modify post-merge without replacing the terminal sweep or changing core.hooksPath configuration. Each shim resolves the implementation relative to the hook installation but applies worktree-state.py --repair to git's current affected checkout, not the owner of an absolute hook script path. Do not use a helper-specific hook or change feature-worktree.py or pinned-checkout.py. In post-merge retain post-merge-sweep.py after repair; remove unconditional exec so delegate failures can be attributed and the shim still exits 0. Report absent implementations, nonzero delegate statuses and dirty skips explicitly; all shims exit 0 because post hooks cannot veto the Git operation. Preserve hook argv and post-rewrite stdin for delegates and do not let repair consume it. Repair refusing dirty state must leave files/index/config unchanged. Verify is still the authoritative gate; a fail-open post-hook exit is never evidence the layout is valid.
      Unit tests exercise every shim, executable mode and delegation under spaces in paths, missing/failing command and post-merge sweep preservation. Integration tests start from minimal T-01 repositories configured with the hooks and prove direct bare git worktree add, feature-worktree creation and pinned-checkout creation all converge. Fleet planning creation uses a distinct artifact segment and pins retain _pin_name naming. Reproduce a merge touching a hidden feature that previously clears skip-bits or stages unexpected deletions, and a rebase invoking post-rewrite; require clean status and verifier success after each. A dirty tree reports a skipped repair and remains byte-identical. No test installs hooks in the live owner checkout or mutates its worktree registrations.
  - id: T-05
    title: Lock real-owner evidence non-regression and current operator guidance
    traces: [SC-02, SC-04, SC-06, SC-11, SC-12, SC-13, SC-14]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 includes enforcement regression tests and real host evidence; direct execution only.
    depends_on: [T-02, T-03, T-04]
    status: ready
    files:
      - tests/integration/test-corpus-real-owner.py
      - tests/integration/test-corpus-non-regression.py
      - tests/unit/test-corpus-regression.py
      - tests/unit/omp-hooks.test.ts
      - AGENTS.md
      - .harness/README.md
      - .claude/skills/harness/SKILL.md
      - .claude/skills/harness-verification-rules/SKILL.md
      - .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/non-regression-receipt.md
    verify: |
      set -e
      python3 tests/unit/test-corpus-regression.py
      python3 tests/integration/test-corpus-non-regression.py
      python3 tests/integration/test-corpus-real-owner.py
      # Expected: each exits 0 within 60 seconds with explicit host/endpoint skips where unavailable; local ship evidence requires the non-skipped assertions.
    intent: |
      Execute directly under DEC-174, only after the cutover tasks land. Capture new regression assertions failing first where behavior changes; existing BUG-1016 positive controls are not red-first claims. Add a corpus-specific ordinary absolute read case to the existing OMP lifecycle adapter tests using absolute owner root plus a line selector and quoted input. Assert the adapter does not invoke feature-root for an all-absolute call, bytes remain unchanged, and a relative control roots to the active feature. No TypeScript production change is warranted: research has probed rootTarget and existing DEC-251 behavior. Test the existing write guard boundaries through their registered interfaces, not a reimplemented predicate.
      Add collected non-regression tests that accept only explicit immutable endpoint SHAs. If either endpoint is unavailable, including shallow clone restrictions, announce the precise skip; do not silently choose a moving merge-base, branch or previous commit. With the supplied full-clone endpoints, inspect the whole-feature diff and owner corpus manifests: no changed path under .harness/*/features except this feature and no altered historical record bytes. Separately prove a fresh non-linked synthetic clone retains full directory names and normalized pre-change finding sets. Do not embed a moving git ref in a collected baseline assertion.
      Add read-only real-owner integration assertions using actual harness_boundary owner resolution from both owner and active worktree callers: audited directory name sets across every segment equal the on-disk expected names, there is no missing-set refusal and dispatch proceeds past the choke point, and this host has more than 70 reached feature directories as a non-vacuity floor rather than a fixed expected census. File-name equality includes the record-less historical directory, without editing it. Do not stage missing entries in the real corpus; build a synthetic wrong-root override and staged missing-producing mutant using T-01 fixtures and make the identical equality assertion reject them. Create one disposable validator pin of this actual repository at the immutable review endpoint, using pinned-checkout.py's naming and registration, to prove dirty report/non-gating versus a structural refusal before downstream invariants. Only that owned probe may be written; remove its temporary registration at fixture teardown, never dirty standing/live trees or change owner corpus/source files. Standard collection announces missing host prerequisites and skips without pretending they passed. The main session must run the non-skipped local real-owner checks before ship, and record commands, exact roots, immutable review endpoint, subjects and raw stdout in non-regression-receipt.md.
      After all production changes land, the main session runs the registered unit and integration kinds once, and all directly changed legacy entrypoint tests once as required by the active test matrix; record raw exits and timings in the receipt. This whole-tree verification belongs here, not intermediate tasks; do not change CI, checkout depth or test runner selection. Task-local commands above are individually bounded under 60 seconds; record the full-suite timings separately without imposing an unmeasured sub-60-second claim on them. If an unchanged historical failure appears, retain its immutable baseline evidence, never suppress it or rewrite records; any new failure is not a deliverable.
      Update AGENTS.md, .harness/README.md, harness/SKILL.md and harness-verification-rules/SKILL.md to describe active-local writes and absolute landed-main reads, injected control-plane root, no in-progress sibling provider, sparse command flags and four named error exits, dirty skip versus structural refusal, hooks on all three Git events, plain-clone no-op, explicit conversion, file-count measurement and immutable evidence. State core.hooksPath is local and onboarding/INV-31 remain authoritative. No UI prototype or DESIGN.md is warranted. Reviewer must inspect these source files at git show review_sha, not the working copy; this discharges SC-14.
  - id: T-06
    title: Perform the explicit clean-checkout conversion and file-count receipt
    traces: [SC-01, SC-07, SC-10, SC-11, SC-12]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: DEC-174 and dirty-state safety require the main session to execute this host conversion after all gates and tests land.
    depends_on: [T-05]
    status: ready
    files:
      - .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/conversion-manifest.json
      - .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/migration-record.md
    verify: |
      set -e
      python3 tests/integration/test-corpus-non-regression.py --conversion-manifest .harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/conversion-manifest.json
      # Expected: exit 0 within 60 seconds; every inventoried record-bearing checkout is either verified clean and idempotent or explicitly skipped dirty with unchanged bytes.
    intent: |
      Execute this operational task only in the main session after T-05's full-suite and non-skipped real-owner receipts. Inventory current standing harness feature and fleet planning worktrees and .pins validators by exact path, HEAD, checkout class and artifact segment, without removing or pruning anything. Reuse worktree-state.py --verify and --repair; do not create a second migration command. Enumerate materialised feature-directory names and file counts before conversion using ordinary filesystem traversal, and capture dirty state plus pre/post file/index/config digests. For every dirty checkout, report the dirty reason and skip without mutating even if its layout is wrong. For every clean record-bearing checkout, run repair explicitly once, then verify; run a second repair to prove unchanged bytes/config. Record active-id, expected and observed directory-name sets, counts, raw command exits, sorted missing/unexpected names and the exact skip reason in conversion-manifest.json. The T-05 non-regression script owns automated receipt validation, including dirty non-mutation and clean idempotence; this task owns only host evidence files. A no-op corpus-free/code-only probe is labelled excluded, never counted as a converted planning checkout. Missing or ambiguous active records must be named and resolved before a clean checkout is claimed converted, not guessed from harness worktree segment.
      Write migration-record.md with the same immutable endpoints as T-05, per-class inventory and counts, before/after feature file totals and unchanged main corpus manifest. File-count mode is the chosen measurement mode: do not claim du differences are disk savings or claim an unmeasured byte delta. Existing seven worktrees' 48–61 MB logical sizes and +1.1 MB/day historical growth motivate the feature but are not conversion evidence. No forced dirty repair, stale worktree removal, corpus historical rewrite, symlink provider or scaffold cleanup is in scope. Retain the failed/skip evidence honestly; a dirty checkout is intentionally skipped, not falsely verified. Non-regression validation inspects the manifest and read-only live state, with missing endpoints announced rather than fabricated.
