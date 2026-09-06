# Plan panel cycle 2 — scope reader — BUG-1305-run-state-clobber

**BLUF: the mechanism is correctly reachable on both routes for the modal collision (Q1 holds up on
the merits), but the plan ships a detection mechanism whose sole forensic artifact — the witness
`.run-identity.json` — is protected by nothing on any write route, and one of REQ-07's own evidence
tasks (T-08) is asked to run project-wide suites the BRIEF's own Constraints forbid. Neither is a
hypothetical; both are verified at source. `code_grade: n_a` — no code exists yet.**

## Q1 — modal-collision reachability: HOLDS

Traced the modal case (prior run_id A/F/S/H + `run_uid` U1; incoming agrees on all four seed fields,
carries no `run_uid`) through both routes at `c369fb1f`. Write: `content` parses to `doc`
(`check-domain.sh:1479`-ish), `absolute_path is not None` block reads `prior_state`, parses to
`prior_doc` (dict, run_id A). Issue-1124 compare at `:1567-1574` is an **inequality** test
(`if str(prior_run_id) != str(new_run_id): return`); run_ids are EQUAL in the modal case, so it does
NOT return, and falls through to wherever T-09 places `uid_conflict(prior_doc, doc)` next —
`prior_doc.run_uid=U1`, `doc.run_uid` absent → the "missing run_uid" branch fires → refused. Edit:
`check-domain.sh:1905-1923` reconstructs the full post-edit content into the SAME `content` variable
before the RE_STATE_YAML branch runs, so it reaches the identical code path. Confirmed correct as
specified, on both routes. **Not a finding.**

## Q2 — deferral hole: none I could exploit into a genuine gap; one accepted asymmetry

Enumerated prior×witness states per the dispatch. In every case where `prior_has_uid` is `False`
(prior absent/zero-byte/unparseable/non-mapping/no-run_uid/None/empty-string/whitespace-after-strip),
T-02's witness compare runs and is the sole gate; where `prior_has_uid` is `True`, the witness compare
is skipped but the ladder (Issue-1106/1124 + T-09's `uid_conflict`) always still runs unconditionally
on that prior — I could not construct a state where BOTH are skipped. The one real asymmetry: once
`prior_has_uid` is `True`, `conflict()`'s feature/squad/host compare against the WITNESS never runs
for that write — only run_id (Issue-1124) and run_uid (T-09) are checked. A write carrying the correct
`run_id` and the correct `run_uid` but a *different* feature/squad/host would sail through unchecked.
This requires possession of the real `run_uid`, which is exactly the disclosed forgery residual
(REQ-01) — not a new hole, and BRIEF's own text says the witness compare "defers... to the identity
refusal below, whose message is the more specific of the two." **Not a finding**, noted for the
record per P-15.

## Q3/Q4 — the finding: the witness is unwritten-guarded on every route (HIGH — must be addressed or
explicitly disclosed before signature)

`bash-write-guard.sh:762-763` — `_run_artifact_guard` — matches only `harness_boundary.RE_RUN_DIGEST`
and `RE_STATE_YAML`. `check-domain.sh`'s `SHAPE_PATTERNS` (`:1185`) is
`(RE_FEATURE_JSON, RE_STATE_YAML, RE_HANDOFF, RE_STATE_MD, RE_CLAUDE_MD, RE_PLAN_YAML)` plus the
separately-matched `RE_RUN_DIGEST`. **None of these, and no pattern added anywhere in T-01–T-12,
matches `.run-identity.json`** (`MARKER_NAME`, T-01). Consequence: any writer with ordinary domain
access to a run's `runs/<dir>/` — which every legitimate lead already has, since it writes
`state.yaml`/`digest.md` there — can delete or overwrite `.run-identity.json` via Bash, Write or Edit
with **zero refusal from anything this plan adds**. `record_seed`'s "write-once" is a property of that
one Python function; nothing stops a direct tool write to the marker path from outside it.

Why this gates REQ-02, not just T-01: `uid_conflict` still refuses correctly off the PRIOR CHECKPOINT
alone (Q1 above), so write-time prevention degrades only where the prior is ALSO absent/zeroed — but
**T-03's post-hoc detection (REQ-02/SC-02/SC-03/SC-09) reads NOTHING but the marker.** Delete or
rewrite `.run-identity.json` after any of the plan's own disclosed residual routes fires (first-write
race D-13/F-08, forgery, a bootstrap-grant session DEC-171, or an ungoverned NotebookEdit route T-11
is still measuring) and the clobber becomes not merely "undetected" (already accepted) but
**undetectable and its forensic trail erased**, with `check-state.sh` reporting nothing, forever. The
Goal states "if one ever is [replaced], the harness says so on its own" — that promise does not hold
against a route requiring no more privilege than the write it is meant to catch.

One nuance the dispatch's own framing got wrong and worth correcting for the record: item 4's premise
("bash-write-guard.sh:744-767 refuses a Bash write or removal of a run artifact") is not what the code
says — it names two specific patterns, neither of which is the marker. T-12's own cleanup instruction
repeats the same over-broad claim ("bash-write-guard.sh refuses a Bash write or removal of a run
artifact, and the probe directory is one") to justify using `os.remove`/`os.rmdir` instead of shell
`rm` — accurate for `state.yaml`, not accurate for `.run-identity.json`, though the safer-anyway
`python3` removal means T-12 itself doesn't misbehave from this.

**This must be resolved or explicitly disclosed before signature** — either add a guard (matching
`.run-identity.json` in both `_run_artifact_guard` and a `SHAPE_PATTERNS`-adjacent PRE rule that
refuses any Write/Edit to it once written, since it is deliberately write-once), or add REQ-01/REQ-02
language accepting "witness tampering by any writer with ordinary directory access" as a residual the
operator is signing off on, the same way the run_uid-forgery residual is named plainly. Leaving it
silent means the operator signs a detection guarantee that does not hold against ordinary tool access.

## Item 6(ii), independently verified: T-08's "four pairs" omits a fifth refusing branch (MED — operator
can rule at signature)

T-05 adds a new fail-closed branch in `validate-digest.py`'s `check_artifact_file` (`return 2` when a
candidate root resolves, the run directory exists, and the artifact file does not). T-08's intent says
"EVERY refusing or reporting branch this feature adds is paired with a write that must STILL be
permitted, and the pairs are the four below" — but there are five refusing/reporting branches
(T-02 seed-field, T-09 identity, T-03 invariant, T-05 fail-closed, and T-06's digest-guard message is
the fourth named — T-05's is the omitted fifth). SC-07's FAILS-if does not name this omission either,
so SC-07 can read `met` without T-05's branch ever being cross-checked against a permitted-write case
in the regression-delta note (T-05's own task-local test does cover its permitted side, just not
folded into the SC-07 evidence artifact). pm's own send-back-1 note flags this exact gap verbatim
("Noted, not acted on... Raising it as a finding is the panel's call, not this pass's") — I'm raising
it. Fix is cheap: add a fifth pair to T-08's list and to SC-07's FAILS-if enumeration.

## New: BRIEF's own Constraints line contradicts SC-07 and T-08's instruction (MED — operator can
reconcile at signature)

BRIEF Constraints: "Focused tests only. No formatter, no linter, no build, no **project-wide suite**."
T-08 instructs "Run BOTH — `run-unit-tests.sh --kind unit` and `run-unit-tests.sh --kind integration`."
Verified at source (`run-unit-tests.sh:26-29`): `--kind unit` → `SCRIPTS=(tests/unit/test-*.py)`,
`--kind integration` → `SCRIPTS=(tests/integration/test-*.py)` — both are **repo-wide globs**, not
scoped to this feature's four touched files. This is not an implementer error: **SC-07 itself requires
it** ("every refusal asserted by the harness `unit` and `integration` suites at `c369fb1f` is still
asserted at the pinned review sha" — comparable only against a full run), and T-08's own text
acknowledges the tension ("a full-suite run under concurrent sibling load does not fit a 60-second
bound; the full-suite evidence lives in this note and is what SC-07 is graded on"). The Constraints
bullet, read literally, is false the moment SC-07 is satisfied. Not a functional defect — the full run
is correctly necessary — but a self-contradiction in the signed text that should be reconciled (narrow
the Constraints bullet to exempt T-08's own regression-evidence run) before an operator cites
"Constraints: no project-wide suite" as binding elsewhere in good faith.

## Item 6(i), D-13 vs T-03/SC-09 (LOW/INFO — already tracked by pm as non-blocking Q1, confirmed cosmetic)

`D-13.choice` still reads "judges a run directory only when its witness AND its checkpoint both carry
a run_uid" — narrower than the three paths T-03 actually implements (unreadable witness; seed-field
disagreement, no run_uid required on either side; run_uid disagreement). Read `T-03`'s own body and
`SC-09` and both carry the correct, broader set — so the inconsistency is confined to `D-13`'s one
summary sentence and is cosmetic, not functional. Confirmed by direct comparison; not re-litigating
pm's disposition, just confirming it holds on the merits.

## T-12/SC-12 dates the load-bearing assumption once, does not close it (LOW/MED — operator can rule
at signature, already substantially disclosed)

`check-state.sh:840-941` (INV-9) verified to check only that `.claude/settings.json`'s PostToolUse
matcher is a syntactically valid registered regex — registration, not delivery. SC-12/T-12 record one
live Write's outcome, once, at signature time. Nothing in the plan re-verifies delivery afterward. A
later silent host regression (version upgrade, settings drift not caught by INV-9's regex-validity
check) would leave every run directory permanently legacy — refused by nothing, reported by nothing —
with the whole suite green, exactly the "nobody notices until a human does" failure mode Mode A's own
Problem statement names for the original bug. SC-12's own text is honest about the scope of what it
measures, so this is disclosed rather than hidden — flagging so the operator is explicit that
signing accepts a one-time dated measurement, not a standing guarantee. (Independently, peer
`ShouldNotExist` also found T-12/SC-12 is confounded pre-merge by which checkout's `check-domain.sh`
main-session-direct tasks execute from — a different, complementary defect on the same task; see their
digest.)

## Other checks performed, no findings

- REQ↔task↔SC traceability: every REQ-01..08 traces to at least one live task and SC; T-04/T-10
  correctly `traces: []`; `depends_on` graph (T-01←[]; T-02,T-03←[T-01]; T-09,T-12←[T-02];
  T-06←[T-02,T-09]; T-08←[T-02,T-03,T-05,T-06,T-09]) is a valid DAG, no cycles.
- Spot-checked `verify:` blocks for T-01/T-02/T-03/T-05/T-06/T-07/T-09 against source anchors
  (`check-domain.sh:1508,1526,1529,1530,1567-1574,1905-1923,1930`; `check-state.sh:840-941,1390,1426`;
  `SKILL.md:272-274` does contain the literal string `task-or-purpose` T-07's negative grep targets)
  — all anchors verified accurate at `c369fb1f`, all commands are syntactically executable as written.
- Re-derived every arity claim send-back-1 corrected against its own recount; found no further
  falsified count.

## Working tree

`git status --porcelain` at the pinned worktree: `?? .harness/harness/features/BUG-1305-run-state-clobber/`
only — the same single untracked line the c3/c4 notes report. No tracked file modified by this review.
