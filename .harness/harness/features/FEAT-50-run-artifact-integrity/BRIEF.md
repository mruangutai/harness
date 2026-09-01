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

## Goal

A run's artifacts survive the run. An empty structured return is refused where it happens rather
than recovered later; a governed agent's feature artifact lands in the checkout that feature is
being developed in; and a recorded digest cannot be destroyed by a later write. Each of the three
gets a regression that has been shown able to report red, and the two fixes FEAT-45 shipped stay in
force.

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
- REQ-06: Each of the three defects carries a deterministic regression that has been DEMONSTRATED
  able to report red, not merely observed passing.
- REQ-07: The rules these fixes install are recorded in the decision record, so a later reader finds
  the ruling instead of inferring it from three enforcement scripts.

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

Decisions and rules that BLOCK, bound or forbid:

- DEC-174 governs execution: every hook, validator and gate script, and the test file of each, is
  planned through the harness and never executed through it. `validate-digest.py`,
  `check-domain.sh`, `check-state.sh` and their tests are therefore main-session-direct, and
  `--resolve` GRANTING them to `harness-backend-dev`/`harness-dev-ops` does not override that.
- DEC-191 closes `feature.json` with `additionalProperties: false`. Adding a `worktree` key would
  be a schema change; this feature does not add one and derives the checkout from git instead.
- DEC-193 allows code under harness authority in exactly two locations; REQ-03's refusal is
  consistent with it and does not extend it.
- PRINCIPLES rule 15 forbids the 32-plan `panel:` backfill — option (b) of the open INV-32 ruling.
  It is recorded as available and not recommended, never taken silently.
- Scope is the three issues and their tests. No unrelated documentation or enforcement change, and
  nothing that moves the INV-32 backlog before the operator rules on it.

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
- SC-11: No `check-state.sh` violation row names `FEAT-50` — in particular no `INV-32` row, which
  is what binds FEAT-50's own approval to carry a complete `panel:` result. This is form (c) of the
  open operator ruling below and it deliberately does NOT require exit 0. The corpus-wide `INV-32`
  row count is recorded as a dated measurement and is NOT graded: 32 at `75daa3b`, re-measured 32
  on 2026-08-31 with the FEAT-50 feature directory on disk and its plan unapproved. It is not
  graded because the corpus is shared — a concurrent feature's approval elsewhere in this
  repository moves the count for reasons that have nothing to do with this diff, and an equality
  against a drafting-time snapshot would then go red over correct delivery.
  verify: automated        evidence: integration
  command, the positive control first so an errored run cannot pass as a clean one:
  `out=$(bash .claude/skills/harness/bin/check-state.sh 2>&1); printf '%s\n' "$out" | grep -q 'INV-' && ! printf '%s\n' "$out" | grep -q 'FEAT-50'`
- SC-12: The operator has ruled between INV-32 options (a), (b) and (c), or has recorded that the
  criterion ships in form (c) with the ruling outstanding. Graded by reading ONE place and nothing
  else: an `## Operator ruling — INV-32` section in
  `.harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md`, the
  answers file DEC-44 already makes the durable home for an operator answer. NOT met while that
  section is absent. It is deliberately NOT graded on `plan.yaml`'s `approval.rulings`:
  `check-state.sh:189-204` validates every entry there against `panel.findings` and demands a
  `finding` id present in that list plus a non-empty `who` and a `YYYY-MM-DD` `date`, so an INV-32
  entry written there emits two `INV-32` VIOLATION rows naming FEAT-50 and falsifies SC-11. SC-11
  and SC-12 are satisfiable together precisely because of that split: the ruling lands in a notes
  file `check-state.sh` never reads, and `approval.rulings` is left ABSENT, which
  `check-state.sh:189` reads as the empty list and iterates zero times.
  verify: inspection
- SC-13: `check-plan-routes.py` exits 0 over this feature's plan and reports
  `0 violation(s) across 1 plan(s)`. The corpus-wide invocation is a DIFFERENT measurement and is
  recorded rather than graded: with no argument at `75daa3b` it reported
  `0 violation(s) across 0 plan(s)` over NOT FEWER THAN 45 feature dir(s) examined, this being the
  first live `plan.yaml`. A floor rather than an equality for two reasons: the count was 46 on
  2026-08-31 because a feature directory added anywhere in this repository moves it, and the
  file-argument command this criterion actually grades emits no `examined` line at all, so the
  number is not reachable from the graded command. The five `DEVIATION` lines for the DEC-174
  carve-out tasks are the expected shape and do not gate; only `VIOLATION` lines do.
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

## Verification gaps

- `INV-32` is retroactively RED across the whole corpus and this feature does not fix it. Measured
  at `75daa3b`: `check-state.sh` exits 1 with 32 `INV-32` VIOLATION rows — "plan is approved with no
  complete panel result recorded" — one per plan approved before FEAT-45 shipped the panel,
  FEAT-45's own plan included. That is a known red, disclosed here rather than routed around:
  SC-11 grades only that no violation row names FEAT-50, not the exit code, so `check-state.sh`
  exiting 0 is NOT proven by this feature and is not claimed. The remedy is the open ruling below.
- `component`, `ui`, `eval` and `typecheck` all carry `cmd: null` in `.harness/harness.json`
  `test_kinds`, and `functional` is `excluded` under DEC-187. No criterion above rests on any of
  them: every surface this feature touches is Python or bash under
  `.claude/skills/harness/bin/**`, one markdown skill and the decision record, all covered by
  `unit` or `integration`, both `active`. No standing runner gap is reachable from this change, so
  none is raised here.
- SC-02, SC-04 and SC-06 prove reachability through a case INSIDE the suite whose reachability is in
  question. That is the FEAT-45 precedent (`inv32-red` in `test-check-state.py`) and it is a real
  limit: the mutant proves the assertion discriminates, and nothing here proves the mutant harness
  itself was invoked against the real artifact other than its own assertion that the mutant text
  differs from the source and produced no traceback.
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

## Open ruling required from the operator — blocking

The operator's stated intent requires the three canonical commands — including `check-state.sh` — to
exit 0 (`notes/answers-2026-08-31-plan.md` constraint 4), and that cannot be reached by
fixing these three issues. Three options, none of which pm or the orchestrator may choose because
each changes what "done" means:

- (a) Scope INV-32 to plans whose `approval.date` is on or after DEC-207, so a plan predating the
  panel is not asked for one. Smallest change; touches `check-state.sh`, which is
  main-session-direct.
- (b) Backfill a `panel:` key into 32 approved plans. Rewrites 32 signed records to describe a panel
  that never ran. PRINCIPLES rule 15 forbids it. Recorded as available and NOT recommended.
- (c) Restate the criterion as SC-11 above: no `check-state.sh` violation row names FEAT-50, with
  the corpus-wide INV-32 count recorded as a dated measurement rather than graded. Meets the intent
  of constraint 4 without touching the backlog and leaves (a) as its own ticket.

The plan ships carrying (c). No task in `plan.yaml` implements (a) or (b); either would be added
after the ruling.

Record your choice by adding a section to
`.harness/harness/features/FEAT-50-run-artifact-integrity/notes/answers-2026-08-31-plan.md` — the
answers file DEC-44 already makes the durable home for an operator answer — in exactly this shape,
and nowhere else:

```yaml
## Operator ruling — INV-32
choice: a | b | c
who: <your name>
date: <YYYY-MM-DD>
note: <one line>
```

SC-12 is graded by reading that section and nothing else. Do NOT record it in `plan.yaml`'s
`approval:` block. `check-state.sh:189-204` validates EVERY `approval.rulings` entry against
`panel.findings` and requires a `finding` id present in that list, a non-empty `who` and a
`YYYY-MM-DD` `date`, so an `{id: INV-32, choice: ...}` entry emits two `INV-32` VIOLATION rows
naming FEAT-50 — "unattributed or has an invalid date" and "STALE OVERRIDE" — which would make
your signature the act that falsifies SC-11. `approval.rulings` exists to overrule a panel
finding and nothing else; this plan leaves the key ABSENT, which `check-state.sh:189` reads as the
empty list. Following this instruction literally adds ZERO `INV-32` rows.

Recording `c` here defers the remedy — `check-state.sh` will still exit 1 with these 32 rows
outstanding — and leaves (a) as its own future ticket; it is not the same as ruling (a) or (b)
closed. This file's `## Approval` below carries the signature itself.

## Approval

status: pending
approved-by:
date:
