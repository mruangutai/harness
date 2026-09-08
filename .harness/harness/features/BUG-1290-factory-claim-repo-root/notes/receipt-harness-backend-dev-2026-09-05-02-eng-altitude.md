# Receipt — harness-backend-dev — ALTITUDE angle — BUG-1290 — 2026-09-05-02-eng-altitude

**BLUF:** Two real findings. D-01 defers the resolver's module home as a "reversible" free choice,
but factory_config.py already carries the identical "name after the owner" split inside
`workspace_path` (docstring: "the one place that derivation exists") — landing the new resolver
anywhere else reopens the exact "several statements that can drift" problem REQ-05 exists to close,
and SC-06's source scan is blind to it because it never reads factory_config.py. Second, T-01 step 1
commits the shared resolver to accepting a "bare segment harness" input that no production caller
(feature-worktree.py's harness branch returns early before reaching the shared call; factory_claim's
repo names are always GitHub owner/repo strings) and no listed test case (5a–5f) actually exercises —
an untestable clause the builder must either silently skip or implement blind. Everything else
checked at the right altitude. Read-only: BRIEF.md, plan.yaml, and every file under
`.agents/skills/harness/bin/` and `tests/` are byte-unchanged.

## Findings

- id: A-01
  file: plan.yaml (D-01, REQ-05, SC-06 / T-01 step 5f, T-03 step 1)
  line: D-01 (L22-31), REQ-05 (BRIEF L32-33), T-01 step 5f (L112-114), T-03 step 1 (L167-172)
  summary: D-01 calls the resolver's module placement freely reversible between
    factory_config.py and harness_boundary.py, but factory_config.py's existing `workspace_path`
    (factory_config.py:382-387) already implements and claims sole ownership of the exact same
    "name after the owner" split ("This is the one place that derivation exists"). Landing the new
    resolver in harness_boundary.py (which has zero repo/fleet-name domain knowledge — confirmed by
    reading its full definition list) creates a second independent split-based derivation inside
    factory_config.py's own module boundary, and SC-06's source scan only reads factory_claim.py and
    the chosen resolver module — never factory_config.py — so this duplication ships undetected.
  cost: REQ-05's whole point ("one home... no second owner-stripping derivation remains") is
    reopened one file over, invisibly, the moment the builder picks harness_boundary.py; a future
    edit to "name after owner" then has three call sites to update in lockstep instead of one, and
    the acceptance suite (SC-06) will report green regardless.
  alternative: pin D-01 to factory_config.py (the module that already owns repo-name domain logic:
    repo_entry, workspace_path, station_column-style "the only place" conventions), and have the new
    resolver call/reuse the exact split `workspace_path` already performs rather than reimplement it;
    extend SC-06's source scan to also assert factory_config.py contains exactly one owner-stripping
    derivation, not just factory_claim.py and feature-worktree.py.
  severity: high
  targets: D-01
  gates_signature: true
  closing: fold-in

- id: A-02
  file: plan.yaml (T-01 step 1, step 5)
  line: T-01 step 1 (L82-87), T-01 step 5a-f (L100-114)
  summary: T-01 step 1 fixes the shared resolver's input contract as accepting "owner/repo, or the
    bare segment harness". Tracing both callers: feature-worktree.py's `resolve_repo` returns early
    for the literal `repo == "harness"` case (feature-worktree.py:67-69) before reaching the shared
    call that T-03 step 2 retargets (only the else-branch split at :86 moves) — so the bare-segment
    branch of the shared function is never reached from that caller. factory_claim.py's repo names
    come from GitHub's `content.repository` field (`_repo_name_of`), always owner/repo form, never a
    bare literal. None of T-01's six listed cases (5a-5f) exercises a bare "harness" input either —
    5d's SC-04 case is "a fixture fleet entry whose name ends in harness", i.e. owner/repo form.
  cost: the builder must implement a branch (bare-name handling with no owner to strip) that no test
    in this plan proves correct and no production caller supplies — dead code mandated by prose with
    no compensating acceptance check, which is exactly the "residual accepted without its
    compensating control named" case the altitude pass exists to catch.
  alternative: either drop "or the bare segment harness" from the resolver's stated contract (its
    callers only ever need owner/repo) and leave feature-worktree.py's existing harness-literal
    early-return exactly as-is and unrelated to the shared function, or, if genuinely required for
    forward-compatibility, add an explicit case to T-01 step 5 exercising it so it is not a
    silently-untested clause.
  severity: med
  targets: T-01
  gates_signature: true
  closing: fold-in

- id: A-03
  file: plan.yaml (T-03 step 4)
  line: T-03 step 4 (L181-186)
  summary: Checked explicitly per this angle's dispatch — T-03 step 4 names `_BlockerCache`'s
    existing private fields (`_plans`, `_issue_maps`) and its existing `os.path.abspath` behavior.
    These are not new implementation choices; they are the exact symbols already in
    factory_claim.py:94-157 today, and the task is a precise in-place refactor of that existing code
    (change what the fields are keyed on; keep the class's public contract, including its "path stays
    absolute" no_plan message, otherwise unchanged). Naming the current symbols orients the builder
    to exactly which lines move, matching this plan's own convention elsewhere (e.g. T-01 step 2's
    literal `:58-68`/`:7-16` line citations).
  summary_verdict: this is acceptance-appropriate precision on an existing-code refactor, not
    over-specification of a green-field implementation choice.
  severity: low
  targets: T-03
  gates_signature: false
  closing: leave

## Also checked, no finding

- BRIEF Constraints' disclosure that a live `main` claim still reports `no_plan` for FEAT-04 after
  this fix: the compensating control IS named — ownership of closing that gap is explicitly assigned
  to "FEAT-04's [landing], not this bug's." Correctly bounded; not a bare accepted residual.
- T-01 step 1 deliberately leaves the resolver's NAME unfixed in prose (only its test-code import
  fixes it) and D-01 explicitly defers exact module placement to T-01/T-03 — both are the right
  altitude: the test file itself becomes the one authoritative statement of the name, per D-01's own
  "fixed by T-01 and matched by T-03," rather than restating a name in three prose blocks.
- D-02 (cache keys on (repo, feature)) and D-04 (layout reader row retargeting) are stated once each,
  with a compensating reason ("because") tied to a concrete measured fact (the FEAT-04 dual-tree
  collision; the CANNOT_VERIFY/INV-27 chain) — right altitude, no drift risk found.

Files touched: none (BRIEF.md, plan.yaml, and everything under `.agents/skills/harness/bin/` and
`tests/` are byte-unchanged — read-only session).
