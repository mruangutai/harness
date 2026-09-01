# BRIEF — FEAT-50-run-artifact-integrity

## Problem

Three ways a run silently loses its own record, all measured during FEAT-45 and all recovered by
hand. Five structured returns came back empty or null and were only found because leads re-measured;
`validate-digest.py` saw them and passed them through (#1056). Agents wrote feature artifacts into
the main checkout instead of their worktree six times, and three of those artifacts existed nowhere
else (#1057). A lead reusing a run directory across cycles overwrote an earlier lead digest and
destroyed the cycle-0 record outright (#1058). The cost is paid by whoever comes next: every one of
these looks like a clean run from the outside, so the loss is discovered by a human noticing an
absence, or not at all.

A fourth way was found live during this feature's own planning run, and the operator added it to
scope on 2026-08-31. `validate-digest.py` resolves a lead's relative `artifact:` path against the
checkout the INSTALLED script sits in, which is always the main one, so for every lead running in
a worktree the digest file is not found, the DEC-156 file-shape check is SKIPPED, and the hook
prints a pass-through line that reads like housekeeping. Three lead `digest.md` files in FEAT-50
itself fail that contract and were passed by this hook for exactly that reason. Same shape as the
other three: the loss looks like a clean run from the outside.

## Goal

A run's artifacts survive the run. An empty structured return is refused where it happens rather
than recovered later; a governed agent's feature artifact lands in the checkout that feature is
being developed in — on the tool route and on the shell route alike; a recorded digest cannot be
destroyed by a later write; and a lead's digest file is shape-checked in the checkout the lead is
actually running in. Each defect gets a regression that has been shown able to report red, and
the two fixes FEAT-45 shipped stay in force.

## Requirements

- REQ-01: A harness persona's structured return that is present and empty is refused at the
  boundary on first presentation and the persona is re-prompted; the pre-existing
  `stop_hook_active` passthrough means a second identical return is not re-validated, which is
  recorded as a known limit.
- REQ-02: A return the boundary genuinely cannot validate — because the platform supplied no
  message at all — is still passed through, and the pass-through is stated in a form the
  dispatching tier can see, so an unvalidated return is never indistinguishable from a validated one.
- REQ-03: A governed agent's write of a feature artifact lands in the checkout that feature is being
  developed in, and the same write aimed at the MAIN checkout of this repository is refused. The
  sibling-worktree shape is deliberately NOT claimed: #1057's evidence is six main-checkout writes
  and zero sibling-worktree ones, and the extraction the remedy uses reads a path that is
  worktree-prefixed for any worktree-resident target, so it cannot reach that shape.
- REQ-04: A `Write` that would replace an existing non-empty `runs/<runid>/digest.md` with content
  that does not preserve the recorded text is refused, so a cycle's record survives the next
  cycle's `Write`. The guarantee is scoped to `Write` deliberately: it is the only tool route that
  carries a whole-file payload to the gate before the write lands, and it is therefore the only
  route on which the prior content still exists to compare against.
- REQ-05: The two fixes FEAT-45 shipped stay in force: INV-32's fail-closed handling of a missing,
  absent or null panel-finding severity, and the test runner's collection of every registered test
  file.
- REQ-06: Every defect this feature fixes — the three filed issues and the fourth found live
  during this planning run — carries a deterministic regression that has been DEMONSTRATED able
  to report red, not merely observed passing.
- REQ-07: The rules these fixes install are recorded in the decision record, so a later reader finds
  the ruling instead of inferring it from three enforcement scripts.
- REQ-08: The checkout binding of REQ-03 is ROUTE-COMPLETE across both governed write surfaces:
  a governed agent's SHELL write of a feature artifact aimed at the MAIN checkout — a redirect,
  a `cp`, a `perl -pi`, any of the command shapes `bash-write-guard.sh` already extracts a write
  target from — is refused too, so the refusal on the tool route cannot be routed around by
  switching tools. The binding is the same selection the tool route uses, not a second copy of
  it. It is scoped to the CHECKOUT question and deliberately does not extend REQ-04.
- REQ-09: A lead's written `digest.md` is located and shape-checked in the checkout the lead is
  actually running in, so the DEC-156 file check is not silently inert for every
  worktree-resident lead. Where the payload does not say which feature the lead is running, the
  resolution is unchanged from today's.

## Constraints

Decisions that SUPPLY the mechanism this feature uses — none of these is an obstruction:

- DEC-143 supplies the raw-then-worktree-stripped glob match in `check-domain.sh`. REQ-03 NARROWS
  after that match succeeds and never changes it; the stripped match is the design that lets an
  agent in a worktree write what its domain grants, and breaking it breaks every build dispatch.
- DEC-95 supplies one worktree per feature, which is the registry REQ-03 binds a write to.
- DEC-180 supplies the write-payload shape route in `check-domain.sh`, which binds every author,
  and is where REQ-04 is enforceable at a moment the author can still fix it.
- DEC-154 and DEC-156 supply the run `state.yaml` checkpoint and the lead's durable `digest.md`,
  which is the artifact REQ-04 protects.
- DEC-122 and DEC-127 supply `validate-digest.py`'s `SubagentStop` hook and its fail-open-loudly
  discipline, which is the site of REQ-01 and REQ-02.
- DEC-179 supplies `check-domain.sh --resolve`, which resolved every lane in `plan.yaml`.
- DEC-151 supplies `bash-write-guard.sh`, the governed Bash write route. REQ-08 NARROWS its
  allow-continue and never widens it. That hook exists because an agent routed around the tool
  route, so binding one surface and leaving the other silent is a bypass by construction.

Decisions and rules that BLOCK, bound or forbid:

- DEC-174 governs execution: every hook, validator and gate script, and the test file of each, is
  planned through the harness and never executed through it. `validate-digest.py`,
  `check-domain.sh`, `check-state.sh` and their tests are therefore main-session-direct, and
  `--resolve` GRANTING them to `harness-backend-dev`/`harness-dev-ops` does not override that.
- DEC-191 closes `feature.json` with `additionalProperties: false`. Adding a `worktree` key would
  be a schema change; this feature does not add one and derives the checkout from git instead.
- DEC-193 allows code under harness authority in exactly two locations; REQ-03's refusal is
  consistent with it and does not extend it.
- PRINCIPLES rule 15 forbids the 32-plan `panel:` backfill. It was OFFERED to the operator as
  option (b) of the INV-32 question, recorded as available and not recommended, and it was NOT
  TAKEN: the operator ruled `choice: d` on 2026-08-31 (`notes/answers-2026-08-31-plan.md`). No
  task in `plan.yaml` backfills any plan and none may be added — rewriting 32 signed records to
  describe a panel that never ran is falsifying the record.
- Scope is issues #1056, #1057 and #1058, plus the fourth defect the operator added to this
  feature on 2026-08-31 — `validate-digest.py`'s artifact-path resolution in a worktree — and
  their tests. Nothing else. No unrelated documentation or enforcement change. INV-32 is not
  moved here at all; the ruling took it out of this feature (see the section below). Q4, INV-6
  versus a plan-phase validator run, was ruled non-blocking and out of scope, and no
  requirement, criterion or task addresses it.

## Success Criteria

Every criterion names its own evidence command. No criterion rests on "the suite is green".
`<review_sha>` is the sha `feature.json review_sha` carries when the criterion is graded.

- SC-01: A `SubagentStop` payload whose `last_assistant_message` is present and empty or
  whitespace-only exits 2 and names the persona; the same payload with the key ABSENT, and with the
  key NULL, exits 0 and says on stderr that the return was not validated.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-validate-digest.py`
- SC-02: SC-01's assertion can report red. The suite's own `empty-red` case builds a mutant copy of
  `validate-digest.py` with the present-and-empty discrimination removed, runs both over the same
  payload, and asserts the real script exits 2 while the mutant exits 0.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-validate-digest.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-validate-digest.py | grep -q 'empty-red'`
- SC-03: With `<FEAT>`'s worktree registered, a governed-agent `PreToolUse` write to the MAIN
  checkout's `.harness/<repo>/features/<FEAT>/BRIEF.md` exits 2 naming the checkout it should have
  used; the identical write inside that worktree exits 0; and with no worktree registered for
  `<FEAT>` the main-checkout write exits 0. A fourth clause, and it is the one an equality-matching
  implementation fails: the same exit-2 denial holds when the registered worktree's basename is the
  SHORT flow id `<FEAT>` extends, which is the spelling this repository measured in the wild.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-domain.py`
- SC-04: SC-03's assertion can report red. The suite's own `feature-checkout-red` case runs a mutant
  copy of `check-domain.sh` beside the original with the binding removed and asserts the mutant
  allows the main-checkout write the real script refuses, its exit code being 0 or 2 with no python
  traceback on stderr.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-domain.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-check-domain.py | grep -q 'feature-checkout-red'`
- SC-05: A `Write` to an existing non-empty `runs/<runid>/digest.md` whose payload does not carry
  the existing text as a prefix exits 2; a `Write` that carries it as a prefix exits 0; and a
  `Write` creating the file exits 0. The `digest-clobber` and `digest-clobber-red` fixtures place
  that `digest.md` INSIDE a registered worktree, not in the fixture root — with root and checkout
  coincident the rule passes whether it reads the right file or the wrong one, so a root-resident
  fixture would grade a rule that is inert where leads actually run. A fourth clause: the same
  clobbering payload on the POST named-target route exits 0, because the rule is PRE-`Write`-only
  by construction.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-domain.py`
- SC-06: SC-05's assertion can report red, proven by the same mutant idiom as SC-04 in the suite's
  own `digest-clobber-red` case.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-domain.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-check-domain.py | grep -q 'digest-clobber-red'`
- SC-07: DEC-143's behaviour is intact. Every pre-existing worktree-strip case in
  `test-check-domain.py` still passes, and `check-domain.sh --resolve` still answers
  `harness-backend-dev, harness-dev-ops` for `.claude/skills/harness/bin/check-domain.sh`.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-domain.py` and
  `bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/check-domain.sh | grep -q 'harness-backend-dev'`
- SC-08: FEAT-45's INV-32 fail-closed fix is untouched. `test-check-state.py` carries ONE INV-32
  case, `case_inv32` (`test-check-state.py:3091`), and it still passes. Its checks cover the
  missing-panel, high-severity-open, stale-override, missing-reader and mutant-red directions
  internally; those are directions inside one case, not five named cases, so the grading signal is
  the suite's exit status — `test-check-state.py:3203` exits 1 when any case returns false.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-check-state.py` exiting 0, and
  `grep -q 'def case_inv32' .claude/skills/harness/bin/test-check-state.py`
- SC-09: FEAT-45's zero-collection fix is untouched: the runner still collects every registered test
  file for both kinds and neither kind collects zero.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-run-unit-tests-kinds.py`
- SC-10: Neither suite regresses, measured rather than inferred. For `--kind unit`: exit status 0,
  ZERO lines matching `^FAIL `, and an output-line count NOT BELOW 1463. For `--kind integration`:
  exit status 0, zero `^FAIL ` lines, and a count not below 1945. Both baselines observed at
  `75daa3b`. The exit status is captured separately from the output because the runner's last line
  is the last script's own summary, so a tail read of a red suite reads green, and the line count is
  what catches a gate that passes while discovering nothing.
  verify: automated        evidence: integration
  command, once per kind with `unit` then `integration` and its own baseline:
  `out=$(.claude/skills/harness/bin/run-unit-tests.sh --kind unit); rc=$?; test "$rc" -eq 0 && ! printf '%s\n' "$out" | grep -q '^FAIL ' && test "$(printf '%s\n' "$out" | wc -l)" -ge 1463`
- SC-11: `bash .claude/skills/harness/bin/check-state.sh` exits 0, AND no violation row names
  `FEAT-50` — in particular no `INV-32` row, which is what binds FEAT-50's own approval to carry
  a complete `panel:` result. BOTH clauses bind. The exit-0 clause is the operator's stated
  intent constraint 4 restored as written, after the ruling of 2026-08-31
  (`notes/answers-2026-08-31-plan.md`, `## Operator ruling — INV-32`, `choice: d`): form (c),
  which graded only the FEAT-50 clause and deliberately did NOT require exit 0, was a WEAKENING
  and is refused. The FEAT-50 clause is kept ALONGSIDE the exit-0 clause, because adding a
  clause is not weakening one.
  THIS CRITERION IS NOT REACHABLE FROM THIS FEATURE'S DIFF, and that is a stated external
  blocker, not a plan defect. The 32 retroactive `INV-32` rows are being fixed IN ANOTHER
  SESSION, outside FEAT-50's scope and outside its branch, so no task here clears them and none
  tries (D-09). SC-11 therefore becomes gradeable only once that external fix has landed on the
  default branch and FEAT-50's feature directory is present. The corpus-wide `INV-32` row count
  stays a dated measurement and is NOT graded: 32 at `75daa3b`, re-measured 32 on 2026-08-31
  with the FEAT-50 feature directory on disk and its plan unapproved. Not graded because the
  corpus is shared — a concurrent feature's approval elsewhere in this repository moves the
  count for reasons that have nothing to do with this diff.
  THE SECOND CLAUSE IS RED TODAY TOO, AND UNLIKE THE FIRST IT IS REACHABLE. That difference is
  why both clauses are stated, and a signer must not have to discover it by running the command.
  Measured in this feature's worktree at `5d12e68` on 2026-08-31: FIVE `  VIOLATION ` rows name
  `FEAT-50`. Each is cleared by a NAMED act, and none of those acts is a task in this plan.
  (1) `BRIEF.md is NOT approved` — cleared by the operator's signature, which D-09 already holds
  until the external INV-32 fix lands.
  (2) `a validator run exists but review_sha is not pinned` — cleared when the review segment pins
  `feature.json review_sha`, the same sha every `<review_sha>` above resolves to.
  (3), (4), (5) three INV-15/DEC-156 rows — `runs/2026-08-31-1-validator/digest.md`,
  `runs/2026-08-31-2-validator/digest.md`, `runs/2026-08-31-1-product/digest.md`. Each is a real
  lead digest whose prose is intact but which carries no fenced `VERDICT:`/`DIGEST:` contract
  block, so `validate-digest.py lead` reports `BLOCKED (contract violation)` on all three. They
  are artifacts of THIS planning run and they are the fourth defect's own footprint: the
  SubagentStop hook that should have refused them was inert for exactly the reason T-11 fixes.
  Cleared by the AUTHORING lead re-emitting its own digest with the contract block, which
  completes the record rather than rewriting it; a third party editing another agent's digest
  would falsify it (PRINCIPLES rule 15) and is forbidden here. They also cannot reach the default
  branch: `.gitignore:7` excludes `.harness/*/features/*/runs/**`, so no run artifact is ever
  committed and the worktree holding these three is removed post-merge.
  The criterion is graded from the repository root of the checkout the feature LANDS in, which is
  what makes that last sentence load-bearing rather than a technicality: rows (3) to (5) are
  absent there by construction, and present in this worktree until their authors re-emit.
  verify: automated        evidence: integration
  command, the positive control first so an errored or aborted run cannot pass as a clean one. The
  control keys on the reporting block's OWN unconditional output (`check-state.sh:1868-1871`):
  every run that reaches that block prints at least one `VIOLATION ` row, one `note ` row, or the
  literal `all state invariants hold.` line. It deliberately does NOT key on an `INV-` substring —
  `INV-` appearing on a `note` row is a property of TODAY'S corpus, not of the gate, and the
  corpus getting cleaner, which is precisely what the external INV-32 fix does, would make an
  `INV-`-keyed control fail on a correct run. That is the same failure mode SC-13 and SC-14 refuse
  when they decline to pin a count or a decision number. The empty output an errored or aborted run
  leaves matches none of the three alternatives and fails the control, which is the case the
  control exists for. The FEAT-50 clause is anchored on the `  VIOLATION ` row prefix rather than
  grepping the whole output, because `check-state.sh:1868-1869` prefixes the two row kinds
  distinctly and a `warn` row is by design not a violation — INV-21, INV-22 and INV-28 all emit
  feature-named `note` rows on a perfectly healthy feature, so an unprefixed grep would grade
  something this criterion does not claim and could go red over a benign note:
  `out=$(bash .claude/skills/harness/bin/check-state.sh 2>&1); rc=$?; printf '%s\n' "$out" | grep -qE '^  (VIOLATION |note |all state invariants hold\.)' && test "$rc" -eq 0 && ! printf '%s\n' "$out" | grep -qE '^  VIOLATION .*FEAT-50'`
- SC-12: The operator's INV-32 ruling is on the record, as the ruling actually taken. Graded by
  reading ONE place and nothing else: an `## Operator ruling — INV-32` section in
  `.harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md`,
  the answers file DEC-44 already makes the durable home for an operator answer, recording
  `choice: d`, a non-empty `who`, a `date`, and the note that INV-32 is being fixed in another
  session with FEAT-50's signature and build held until it lands. NOT met while that section is
  absent, and NOT met if it has been restated in the (a)/(b)/(c) shape this brief originally
  offered — the operator took none of those three, and recording a fourth option as one of them
  falsifies the record (PRINCIPLES rule 15).
  It is deliberately NOT graded on `plan.yaml`'s `approval.rulings`: `check-state.sh:189-204`
  validates every entry there against `panel.findings` and demands a `finding` id present in that
  list plus a non-empty `who` and a `YYYY-MM-DD` `date`, so an INV-32 entry written there emits
  two `INV-32` VIOLATION rows naming FEAT-50 and falsifies SC-11. SC-11 and SC-12 are satisfiable
  together precisely because of that split: the ruling lands in a notes file `check-state.sh`
  never reads, and `approval.rulings` is left ABSENT, which `check-state.sh:189` reads as the
  empty list and iterates zero times. That reasoning is doubly right now that NO overrule was
  taken at all — the operator directed both open `high` findings be FIXED, not overruled — so
  `approval.rulings` has nothing it could legitimately hold.
  verify: inspection
- SC-13: `check-plan-routes.py` exits 0 over this feature's plan and reports
  `0 violation(s) across 1 plan(s)`. The corpus-wide invocation is a DIFFERENT measurement and is
  recorded rather than graded: with no argument at `75daa3b` it reported
  `0 violation(s) across 0 plan(s)` over NOT FEWER THAN 45 feature dir(s) examined, this being the
  first live `plan.yaml`. A floor rather than an equality for two reasons: the count was 46 on
  2026-08-31 because a feature directory added anywhere in this repository moves it, and the
  file-argument command this criterion actually grades emits no `examined` line at all, so the
  number is not reachable from the graded command. The `DEVIATION` lines for the DEC-174
  carve-out tasks are the expected shape and do not gate; only `VIOLATION` lines do. There are
  NINE of them after this plan's amendment, measured on 2026-08-31 (T-01, T-02, T-03, T-04,
  T-05, T-09, T-10, T-11, T-12); it was five before T-09 to T-12 were added. Recorded rather
  than graded, because adding a carve-out task moves the count.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml`
- SC-14: The three rules are in the decision record as ONE new decision, and the generated index
  matches the authority byte for byte. Graded by heading text, not by number: the number is
  resolved at landing time (D-08) because a concurrent feature can consume the next one, so a
  criterion pinning `DEC-208` would go red over correct delivery.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` and
  `git show <review_sha>:.harness/harness/docs/DECISIONS.md | grep -c "^## DEC-[0-9]* — A run.s own record is enforced"` returning exactly `1`
- SC-15: `harness_boundary.worktree_for_feature` selects a feature's registered worktree by prefix
  — the exact basename and the short flow id the feature id extends both resolve, `FEAT-XY` does
  not resolve `FEAT-X`, no candidate returns None — and two candidates raise `AmbiguousWorktree`
  naming both. The `test-harness-boundary.py` cases must be shown failing against the pre-change
  module before the change lands. Scoped to that one file because it is a `UNIT_SCRIPTS` entry and
  `unit` is what this criterion declares; the cutover's own behaviour is SC-16.
  verify: automated        evidence: unit
  command: `python3 .claude/skills/harness/bin/test-harness-boundary.py`
- SC-16: The `inflight_registry.feature_root` cutover changes exactly ONE observable answer and
  nothing else. Its contract holds unchanged — no registered worktree resolves to the supplied
  owner root, an exact-basename worktree resolves to that worktree, an ambiguity falls back to the
  owner root and nothing is raised out of `feature_root` — and the one intended widening is that a
  SHORT-form worktree now resolves to it where it previously fell back. The module's inline
  basename loop is gone, no other function in it changes, and every pre-existing
  `test-inflight-registry.py` case passes unchanged. Declared `integration` because
  `test-inflight-registry.py` is an `INTEGRATION_SCRIPTS` entry (`run-unit-tests.sh:31`) while
  `test-harness-boundary.py` is a `UNIT_SCRIPTS` one: one criterion cannot declare both kinds, and
  a single `unit` claim over both files would rest half its assertions on a kind that never ran
  them.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-inflight-registry.py` and
  `test "$(git show <review_sha>:.claude/skills/harness/bin/inflight_registry.py | grep -cF 'os.path.basename(worktree)')" -eq 0`
  — `-F` is load-bearing: without it the parentheses are read as a regex group, the pattern matches
  nothing on the PRE-change file too, and the check greens without discriminating (measured: `-c`
  returns 0 and `-cF` returns 1 against today's module).
- SC-17: `test-validate-digest.py` no longer asserts exit 0 for a present-and-empty
  `last_assistant_message`. The obsolete case whose description reads
  `pass-through: empty last_assistant_message passes with a stated reason` — at
  `test-validate-digest.py:738-739`, measured at `5d12e68`, asserting exit 0 for exactly the
  payload D-01 redirects to exit 2 — is GONE, while the other two DEC-122 pass-throughs
  (non-harness `agent_type`, `stop_hook_active`) are still present. Graded rather than merely
  instructed in T-02, because a surviving copy makes T-02 unable to pass its own `verify:` and a
  goal-check that only reads the instruction cannot tell.
  verify: automated        evidence: integration
  command — `-F` is load-bearing, and the two `-q` greps are the positive control that proves the
  file was read at all rather than an errored search counting zero:
  `T=$(git show <review_sha>:.claude/skills/harness/bin/test-validate-digest.py); test "$(printf '%s\n' "$T" | grep -cF 'pass-through: empty last_assistant_message passes with a stated reason')" -eq 0 && printf '%s\n' "$T" | grep -q 'stop_hook_active avoids the infinite-block loop' && printf '%s\n' "$T" | grep -q 'empty-string'`
- SC-18: The checkout binding is route-complete. With `<FEAT>`'s worktree registered, a
  governed-agent Bash write — `echo hi > <main checkout>/.harness/<repo>/features/<FEAT>/BRIEF.md`
  — exits 2 and the message names BOTH the target and the worktree the write belonged in; the
  same write inside that worktree exits 0; with no worktree registered the main-checkout write
  exits 0; and the same exit-2 denial holds when the registered worktree's basename is the SHORT
  flow id `<FEAT>` extends, which is the clause an equality-matching implementation fails. The
  DEC-153 `.claude/worktrees/` carve-out and the product-workspace `..` exclusion are untouched.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-bash-write-guard.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-bash-write-guard.py | grep -q 'bash-feature-checkout-short'`
- SC-19: SC-18's assertion can report red. The suite's own `bash-feature-checkout-red` case runs
  a marker-free mutant copy of `bash-write-guard.sh` beside the original with the binding
  removed and asserts the mutant ALLOWS the main-checkout write the real script refuses, its
  exit code being 0 or 2 with no python traceback on stderr.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-bash-write-guard.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-bash-write-guard.py | grep -q 'bash-feature-checkout-red'`
- SC-20: A lead's digest file is found in the checkout the lead runs in. With a `digest.md`
  INSIDE a registered worktree and `harness_feature` in the payload, a narrative digest with no
  contract block exits 2 naming the digest FILE — today the identical fixture exits 0 with the
  INV-15 pass-through line — a valid one exits 0, and the same fixture with NO `harness_feature`
  key exits 0 and still prints the INV-15 pointer, which is what pins the fallback as today's
  behaviour and fail-open-loudly as intact. The fixture's root and checkout must DIFFER: the
  existing `_dec156_case` helper (`test-validate-digest.py:750-769`) makes them coincident, which
  is precisely the shape that cannot see this defect.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-validate-digest.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-validate-digest.py | grep -q 'dec156-worktree-nofeature'`
- SC-21: SC-20's assertion can report red. The suite's own `dec156-worktree-red` case runs a
  marker-free mutant copy of `validate-digest.py` with the resolution reverted to the bare
  `_root_or_none()` join and asserts the mutant exits 0 where the real script exits 2, its exit
  code being 0 or 2 with no python traceback on stderr.
  verify: automated        evidence: integration
  command: `python3 .claude/skills/harness/bin/test-validate-digest.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-validate-digest.py | grep -q 'dec156-worktree-red'`

## Verification gaps

- `INV-32` is an EXTERNALLY OWNED BLOCKER on this feature, not a red it grades around. Measured
  at `75daa3b` and again on 2026-08-31: `check-state.sh` exits 1 with 32 `INV-32` VIOLATION rows
  — "plan is approved with no complete panel result recorded" — one per plan approved before
  FEAT-45 shipped the panel, FEAT-45's own plan included. SC-11 now grades the exit code
  DIRECTLY and unweakened, so this feature does NOT route around the red: it BLOCKS on it. The
  remedy is being applied in another session, outside this branch (D-09, and the ruling section
  below), so no task here can clear it, SC-11 is ungradeable until that fix lands on the default
  branch, and this plan is unsignable and its build unstartable until then. What is therefore
  NOT proven by anything in this feature is that `check-state.sh` exits 0; what carries it is
  the external fix, and the gate on this plan's signature.
- `component`, `ui`, `eval` and `typecheck` all carry `cmd: null` in `.harness/harness.json`
  `test_kinds`, and `functional` is `excluded` under DEC-187. No criterion above rests on any of
  them: every surface this feature touches is Python or bash under
  `.claude/skills/harness/bin/**`, one markdown skill and the decision record, all covered by
  `unit` or `integration`, both `active`. No standing runner gap is reachable from this change, so
  none is raised here.
- SC-02, SC-04, SC-06, SC-19 and SC-21 prove reachability through a case INSIDE the suite whose
  reachability is in question. That is the FEAT-45 precedent (`inv32-red` in
  `test-check-state.py`) and it is a real limit: the mutant proves the assertion discriminates,
  and nothing here proves the mutant harness itself was invoked against the real artifact other
  than its own assertion that the mutant text differs from the source and produced no traceback.
  Five instances of the limit rather than three does not change its shape, but it does widen it:
  every one of the five is trusted on the same unproven premise.
- REQ-04's guarantee reaches ONE tool route. The gate's pre route is `Write`-only
  (`check-domain.sh:1367-1368`), and it is the only route that carries a whole-file payload while
  the prior content still exists. A digest destroyed by an `Edit` with an `old_string` spanning the
  whole prior text, by a `NotebookEdit`, or by `cat > digest.md` from Bash is refused NOWHERE and
  no criterion above tests those routes. The bite is real rather than theoretical: D-05's own
  protected case — a lead revising its own digest inside one run — is realistically an `Edit`, so
  the legitimate path is the unenforced one and the enforced path is the destructive one. The
  compensating control is T-06's playbook edit, which tells leads the rule in the place they read
  before opening a run dir, and the fact that every harness lead writes its digest with `Write`
  because the digest is composed in one turn. Closing the other routes needs a mechanism this plan
  does not contain and would be a scope change, not a review edit.
  And note what the plan amendment does NOT do. T-09's Bash-route binding closes the CHECKOUT
  question (REQ-03, REQ-08) only. It does NOT extend REQ-04's preservation rule to Bash, and it
  cannot: that rule needs the file's PRIOR content, which only a whole-file `Write` payload
  carries to the gate — a shell command hands it nothing to compare against. D-06's residual and
  D-10's scope fence are the same residual, unchanged by the amendment and disclosed rather
  than closed.
- REQ-01's refusal is a FIRST-PRESENTATION refusal only. `validate-digest.py:1493-1494` returns 0
  unconditionally when the payload carries `stop_hook_active`, ahead of every check, so exit 2 buys
  one re-prompt and the retry is then accepted in silence — quieter than today's code, which at
  least prints its passthrough line every time. T-01 deliberately leaves that passthrough alone: it
  is pre-existing, DEC-127-sanctioned and outside this feature. Nothing above proves an empty
  return is refused twice, and no criterion claims it.
- T-03's binding does not run at all in a session with no PyYAML. `domain_check()` is called under
  `if _run_domain and not _no_parser:` (`check-domain.sh:872`), so the documented bootstrap-grant
  escape hatch disables REQ-03's refusal, while REQ-04's digest rule — which lives in the shape
  phase below that call — still runs. Nothing above claims otherwise. Making the domain route
  parser-free is a mechanism this plan does not contain and would be a scope change; the honest
  statement of the guarantee is therefore "in any session that has a YAML parser".
- SC-11's dependency on a top-level `panel:` key is owed by no `T-NN`, deliberately rather than by
  omission. INV-32 asks an APPROVED plan for a complete panel result, and that key is transcribed
  out of band by pm from the validator lead's digest after the panel segment runs
  (`harness-spec-driven`), which is why no task in this plan produces it. Before approval INV-32
  does not apply to this plan at all (`check-state.sh:176-179`), so SC-11 becomes gradeable only
  once the signature and the transcribed panel both exist — and a reader six months on should read
  the absence of a task as the panel segment's ownership, not as a forgotten dependency.

## The INV-32 ruling, and the external blocker it creates

**This is answered.** The operator ruled on 2026-08-31. The ruling is recorded verbatim at
`.harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md`,
section `## Operator ruling — INV-32`, as `choice: d`: INV-32 is being fixed in another session;
hold FEAT-50's signature and build until that fix lands; do not alter INV-32 here, and do not
weaken the exact `check-state.sh` exit-0 success criterion.

That is a FOURTH option — none of the three this brief previously offered — and it is recorded
as `d` rather than folded into the nearest of them, because recording it as one of them would
falsify what was ruled (PRINCIPLES rule 15).

**What it settles.**

- **FEAT-50 plans NO INV-32 work.** No `approval.date` scoping, no 32-plan `panel:` backfill.
  `check-state.sh` is edited by no task in `plan.yaml`; its lane row stays declared-but-unedited
  because SC-08 and SC-11 read it. D-09 records this and D-08 no longer defers it.
- **The exit-0 criterion is restored, not weakened.** SC-11 requires
  `bash .claude/skills/harness/bin/check-state.sh` to exit 0, which is the operator's stated
  intent constraint 4 as written, with the "no violation row names FEAT-50" clause kept
  alongside it.
- **Signature and build are BLOCKED on an external event.** THIS PLAN IS COMPLETE BUT NOT
  SIGNABLE, AND ITS BUILD MUST NOT START, until the external INV-32 fix has landed on the default
  branch and `check-state.sh` exits 0 with FEAT-50's feature directory present. That is a stated
  external blocker rather than an unresolved plan defect, and it is the only thing standing
  between this plan and signature.
- **2026-08-31: the operator reported the external INV-32 fix MERGED into `main`**, so D-09's
  precondition is REPORTED MET and the hold on signature is lifted; the feature branch is updated
  from `origin/main` by the main session after the plan-phase commit, so SC-11 is not yet
  gradeable in this worktree. Recorded at
  `.harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md`.

`plan.yaml`'s `approval.rulings` key is ABSENT and must stay absent. It exists to record an
OVERRULE of a panel finding and nothing else, and no overrule was taken: the operator directed
that both open `high` findings be FIXED, which the amended plan does. Writing the INV-32 ruling
there instead would be actively harmful — `check-state.sh:189-204` validates every entry against
`panel.findings` and demands a `finding` id present in that list plus a non-empty `who` and a
`YYYY-MM-DD` `date`, so an `{id: INV-32, ...}` entry emits two `INV-32` VIOLATION rows naming
FEAT-50 and makes the signature itself the act that falsifies SC-11. `check-state.sh:189` reads
the absent key as the empty list and iterates zero times. SC-12 is graded by reading the
answers-note section and nothing else, which is what makes SC-11 and SC-12 satisfiable together.

The remaining five panel findings — two `med`, three `low` — were not ruled on and stay OPEN and
un-overruled. This brief takes no position on them.

## Approval

status: pending
approved-by:
date:
