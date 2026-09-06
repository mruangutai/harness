# BRIEF — BUG-1305-run-state-clobber

Issue #1305 — *Prevent Harness run-state clobbering and false digest-write refusal*. The title is the
scope statement: **two distinct failure modes**, kept separate in every requirement and every
criterion below, because a fix that closes one and leaves the other open would otherwise read as done.

- **Mode A — run-state clobber.** An earlier run's durable checkpoint is destroyed by a later run.
- **Mode B — durable digest, ungraded and unrepairable.** A run's durable digest violates the lead
  digest contract, reaches the factory's record, and nothing automatically grades it; meanwhile the
  one guard that does fire refuses a class of legitimate in-place correction.

## Problem

**Mode A.** Two runs in BUG-1286 had their `state.yaml` clobbered by a later run and needed repair by
hand. Nothing prevents this on at least one live write route: the run-identity guard's only test is a
string comparison of the prior `run_id` against the new one, and no mechanism binds `run_id` to
anything but itself — the value is author-chosen and conventionally equals the run-directory slug,
whose naming rule enforces no uniqueness. Two genuinely different runs that choose the same slug
produce equal `run_id`s, and the second write is accepted as a legitimate upsert of the first. Worse,
**nothing detects a clobber that has already happened**: `check-state.sh`'s run invariants grade a
`state.yaml`'s own shape and never ask whether the checkpoint sitting in a run directory belongs to
the run that owns it. So the operator learns about a destroyed checkpoint only when a human notices
that a record they remember writing is gone — which is how both BUG-1286 instances were found.

**Mode B.** A durable lead digest in the same feature — `runs/2026-09-05-02-validator/digest.md` —
carried no `artifact:` line, failing the lead digest contract, and stayed that way in the factory's
record. No automatic path grades a durable digest file: the digest hook's file check fails open by
design under worktree or working-directory drift and names `check-state.sh` as its backstop, and
`check-state.sh` is registered in no hook at all, so it runs only when a human runs it. At the same
time the digest content guard refuses any same-run correction that is not a pure append, on both the
Write and the Edit route — so a lead who wants to repair its own record mid-file has no route through
the guards, and the file's own inline comment describing that guard as "intentionally Write/PRE-only"
is a false statement that misleads the next reader of the exact guard this issue names. The cost is
the one that matters most: the factory's own record contains a false-looking entry, and a record the
factory cannot be trusted to grade is a record no downstream loop can safely read.

The specific BUG-1286 run directories are gone — gitignored, worktree removed — so neither mode can
be reproduced from the original evidence. Both were confirmed at the BUG-1286 ship briefing (row
B-11) and both mechanisms were re-derived against live code in this feature's diagnosis note
(`notes/receipt-harness-dev-ops-diag-c1.md`).

## Goal

A run's durable record can be trusted without a human standing over it. A checkpoint one run wrote
cannot be quietly replaced by another run, and if one ever is, the harness says so on its own rather
than waiting for someone to notice. A durable digest that breaks the lead digest contract is caught
by the factory automatically instead of surviving in the record, and a lead that wrote a bad digest
has a way to correct it that the guards permit — so the guard's refusal protects the record rather
than freezing a defect into it.

## Requirements

- **REQ-01 (Mode A — prevention):** A durable checkpoint written by one run cannot silently replace a
  different run's checkpoint. "Silently" is the operative word: the write is either refused or
  recorded as an identity conflict, never accepted as a routine update. Prevention rests on a
  **machine-minted run identity the checkpoint itself carries**, and on refusals decidable from what
  is on disk. No refusal consults a session identity.
  - **The minted identity — `run_uid`.** Every run checkpoint carries a top-level `run_uid` holding a
    collision-resistant value the harness mints and no author chooses. `run_id` is untouched: it keeps
    its human-legible meaning, its author, and every display use it has today. Two runs that choose
    the same directory slug therefore share a `run_id` and still differ in `run_uid`.
    `run_uid` is a collision-avoidance token and **not a capability**: anyone who can write the
    directory can read it. That is deliberate, and the residual below is its consequence.
  - **Two refusals, separated by what each can see.** The minted identity lives INSIDE the
    checkpoint, so it is readable only where the prior checkpoint parses. The run directory's
    recorded identity — the witness — is a SEPARATE FILE, so it is readable even when the prior is
    absent, empty or unreadable. Each refusal owns exactly the cases the other cannot see, and each
    carries its own message.
  - **The seed-field refusal — Write and Edit, wherever the checkpoint's own identity is
    unavailable.** An incoming checkpoint that disagrees with the run directory's recorded identity
    on run_id, feature, squad or host is refused on both routes. It answers whenever the prior
    checkpoint is absent, zero-byte, or present but carrying no readable `run_uid`. Where the prior
    does carry one, it defers to the identity refusal below, whose message is the more specific of
    the two.
  - **The identity refusal — on a PRESENT prior, Write and Edit.** When the prior checkpoint in the
    run directory carries a `run_uid`, an incoming checkpoint is refused if it carries a *different*
    one, and refused if it carries *none*. Both are the ladder shape the harness already uses for a
    disagreeing or missing `run_id` — the second is the one a foreign run actually presents, because
    a run that never wrote a checkpoint has no `run_uid` to carry.
  - **No refusal is keyed on an empty or absent prior — none, on any route.** A run directory holding
    no checkpoint, or holding a zero-byte one, accepts a write exactly as it does today: an owner
    recovering a zeroed or hand-deleted checkpoint agrees with its own recorded identity on every
    seed field, so both refusals pass it. That is the B-11 recovery action itself, and refusing it
    would refuse the only repair that works.
  - **What this feature does NOT repair, said where you sign: a TRUNCATED checkpoint.** A prior that
    is non-empty and will not parse is refused ALREADY, before this feature, by the fail-closed
    branch added for issue #1106 gap (b) (`check-domain.sh:1539-1545` at `c369fb1f`) — and this
    feature does not reverse it. Reversing it would weaken exactly the protection this feature
    exists to strengthen: a prior nobody can read is precisely where a silent overwrite hides. So a
    truncated `state.yaml` is repaired by a human outside the guards, and the no-refusal rule above
    is promised for the zeroed and absent forms only. It is out of scope BY NATURE, not by
    acceptance, and no criterion below grades it.
  - **Legacy is quiet by construction, there is no migration, and the first-write window is the
    residual instance of this very bug.** A prior carrying no `run_uid` is legacy: today's behaviour
    exactly, no new refusal, nothing reported. A directory leaves legacy on its own, at the first
    governed write whose minting lands. Nothing backfills the historical corpus and nothing needs
    to. **The price, named rather than left as "the legacy window":** two runs that choose the same
    fresh slug before either has had a checkpoint landed and minted collide exactly as issue #1305
    describes — the second write is permitted, and detection can never see it because no witness
    exists. That is unchanged from today and not made worse by anything here; it is the one shape of
    the modal collision this mechanism does not close, and it shrinks to nothing once a directory
    has had one governed landing.
  - **A resumed run is never refused, and that is a requirement, not a side effect.** A resumed owner
    presents the SAME `run_uid`, because it reads it out of its own checkpoint — the file it is about
    to update. It is never refused however many sessions it has spanned, and no refusal in this
    feature may consult the writer's session identity: a resumed owner and a foreign run reusing the
    slug carry identical seed fields and different sessions by construction, so a session-keyed
    denial refuses exactly the writes this feature exists to protect.
  - **The cost of the identity refusal, stated where you sign.** An owner that rewrites its checkpoint
    from scratch and DROPS `run_uid` is refused until it carries the field. That is a new refusal of a
    write legitimate today, it is the price of the mechanism, and it is bounded three ways: the
    refusal message names the exact `run_uid:` line to carry forward and where to read it; the harness
    re-injects the field after every governed landing, so the value is always present in the file the
    author reads; and the seed doctrine that tells leads to carry it forward is part of the work.
  - **Bash — already closed, and not by this feature.** `bash-write-guard.sh`'s `_run_artifact_guard`
    (:744-767 at `c369fb1f`) refuses a Bash write to any run's `state.yaml` in any checkout. Nothing
    here changes it and no criterion re-grades it.
  - **NotebookEdit — measured, not assumed.** It is reached by the registered `Write|Edit` matcher
    only if the host matches tool names by substring, and `check-domain.sh:1931` already asserts in a
    comment that POST sees it. Nobody has measured either claim. This feature MEASURES it once and
    records the answer; an unguarded route is a reported finding, never a silent acceptance.
  - **End-to-end mint DELIVERY is UNMEASURED, and that is part of what you accept by signing.** The
    minting CODE is proven by SC-10, which invokes `check-domain.sh --post` directly over an isolated
    bin root. Whether the HOST actually delivers PostToolUse for the Write and Edit tools is a
    different question, and this feature does not measure it. **Why measuring it before this merges
    is not available:** `.claude/settings.json` registers POST as
    `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh --post`, and every task here is
    `main-session-direct` — so the script that fires is the MAIN checkout's, which does not carry
    this feature's change, while the minting lands only in this feature's worktree. A pre-merge probe
    therefore reports which checkout the hook points at, never whether the host delivers. It was
    specified as T-12 and graded by SC-12, and both are struck for exactly that reason rather than
    respecified. **What you are accepting:** if this host does not deliver PostToolUse, no `run_uid`
    is ever minted and no witness is ever written, every run directory stays legacy — refused by
    nothing new, reported by nothing — and the whole suite is still green. This plan does not observe
    that end to end. INV-9 asserts the matcher is REGISTERED, which is not delivery; the first
    governed write after this merges is what settles it.
  - **THE RESIDUAL — and it IS a residual you are being asked to accept.** One case survives: a
    foreign run that reads the prior checkpoint and COPIES its `run_uid` into its own write. On disk
    that is indistinguishable from the owner, so no rule this feature may adopt separates them, and
    detection cannot either. It is deliberate forgery of another run's identity rather than the
    accidental slug reuse issue #1305 is about, and the accidental collision this bug records is
    closed. But "bounded by its nature" is not "absent": approving this brief accepts a mechanism
    whose stated residual is an undetectable clobber by a writer willing to copy the field. An
    earlier draft of this brief said this was "not a risk you are being asked to accept"; that was
    false, and it is corrected here rather than quietly dropped.
- **REQ-02 (Mode A — detection, standalone):** A checkpoint that has already been replaced by a
  foreign run is detectable after the fact, by a check that reads the repository and needs no memory
  of the incident and no human recollection. This is deliberately not folded into REQ-01: prevention
  on the routes reachable today does not detect a clobber that has already landed, or one that
  arrives by a route nobody anticipated. **Detection is SELF-LIMITING, and that is the design, not a
  shortfall.** It judges exactly the run directories that carry the minted identity on both sides —
  a witness recorded when the directory was first written under the mechanism, and a checkpoint
  carrying a `run_uid`. A directory missing either is legacy and reports nothing, so no historical
  directory, no sibling worktree and no control-plane root can turn the gate red on the day it ships,
  and no corpus migration is part of this work. **What that leaves uncovered, stated plainly:** a
  checkpoint carrying no `run_uid` over a witness that carries one is NOT reported, because a
  legitimate write in a session where the hooks are not registered reaches the same state, and INV-9
  already asserts hook registration.
  - **The witness is protected like the checkpoint it witnesses.** Detection reads nothing but the
    run directory's witness, so a witness that any writer with ordinary directory access can
    overwrite or delete would turn an accepted UNDETECTED clobber into an UNDETECTABLE one with the
    forensic trail erased. This feature makes the witness a guarded run artifact on the same three
    surfaces that already protect `state.yaml` and the run digest — the Bash route's run-artifact
    guard, the boundary module's shared path patterns, and `check-domain.sh`'s Write/Edit route
    denial — and the rule is WRITE-ONCE: no governed route may rewrite or remove it, and the refusal
    names what the file is and what to do instead. The harness's own POST hook writes it from inside
    `check-domain.sh` rather than through a governed tool call, so it needs no exemption, and that
    writer is itself write-once. Graded by SC-13.
- **REQ-03 (Mode A — detection is actionable):** The detection result names the affected run
  directory and distinguishes a clobbered checkpoint from a merely malformed one, so an operator
  reading only the checker's output knows what was lost and what to repair.
- **REQ-04 (Mode B — automatic grading):** A durable digest that violates the lead digest contract is
  graded by the factory automatically. Whether a non-compliant digest is caught must not depend on
  someone choosing to run a checker by hand.
- **REQ-05 (Mode B — legitimate repair):** A lead whose own run's durable digest violates the
  contract can bring that digest into compliance within its own run, without allocating a new run
  directory and without a human editing the file outside the guards. The outcome is what a lead can
  *do*; the route is not specified here. This requirement is bounded by the signed rule that a
  recorded digest is extended and never replaced (DEC-208 ruling 3) — a remedy incompatible with that
  rule is an escalation, not a decision the plan may take.
- **REQ-06 (Mode B — the record about the guard is true):** The description `check-domain.sh` gives
  of which tool routes its digest content guard covers matches what that guard actually does.
  **In scope, and deliberately its own requirement so it can be struck independently at signature.**
  The inline comment calling that guard "intentionally Write/PRE-only" is contradicted by the guard's
  own runtime and by direct probe; it is a false statement about the exact guard this issue names,
  and the next person to read it is the next person to be misled.
- **REQ-07 (Modes A and B — no protection traded away, and none newly invented):** No change made
  for either mode opens a write that the harness refuses today, **and no change made for either mode
  refuses a write that the harness permits today.** Both directions bind. The second exists because
  an over-broad new refusal removes no prior assertion and breaks no prior test, so a guard that
  refuses the very writes it was built to protect can otherwise ship with every gate green. Tagged
  to both modes because the two remedies land on the same guard scripts and the same write routes,
  so each one's change is the other's regression risk.
- **REQ-08 — STRUCK at signature:** Run-directory slug unification is not part of this bug fix.
  With REQ-01's minted identity, equal-slug collisions are refused under either live grammar, so
  grammar unification changes collision frequency rather than correctness. The proposed
  supersession mechanism also contradicts DEC-205, which requires an in-place rewrite of current
  truth. Both grammars remain live; a later doctrine change may reconcile them under DEC-205.

## Constraints

**Bounding — things this feature must work within, not remove:**

- **DEC-174 (blocks execution, not planning).** The harness plans changes to its own hooks,
  validators and gate scripts but never executes them. Every task touching `check-domain.sh`,
  `bash-write-guard.sh`, `check-state.sh`, `validate-digest.py` or `.claude/settings.json` — and each
  gate's own tests — carries `execution_mode: main-session-direct`.
- **DEC-179 (supplies the mechanism for the above).** That routing is resolved at plan time by
  `check-plan-routes.py`, so an ungranted surface becomes a *declared* main-session step rather than
  a write rejected mid-build. A `DEVIATION` line on a granted path executed by the main session is
  the expected DEC-174 shape, not a failure.
- **DEC-171 — the PyYAML-absent fail-open is an operator-ruled tradeoff and is NOT this feature's to
  reverse.** PyYAML is REQUIRED with no fallback; `check-domain.sh` and `bash-write-guard.sh` fail
  CLOSED without it; the bootstrap grant permits writes for that session only and expires by
  construction. The diagnosis names a bootstrap-grant session as a non-discriminable second candidate
  mechanism for Mode A. That candidate is acknowledged and bounded: narrowing or removing the
  bootstrap grant is out of scope here, and REQ-02's detection is what covers a clobber arriving
  through it — which holds only if the detection work actually lands. **A clobber arriving that way
  is detected only where the directory already carries the minted identity on both sides**, which is
  the self-limiting bound REQ-02 states; a legacy directory clobbered through a bootstrap-grant
  session is covered by nothing, exactly as it is today. What forces DELIVERY of the detection work
  is a criterion — SC-02 standing on its own — not the task graph. (This is DEC-171. It is *not*
  DEC-154, which rules that `state.yaml` is a checkpoint
  rather than a notebook — a different subject.)
- **DEC-208 ruling 3 (bounds REQ-05, corrected at signature).** A recorded run digest is extended,
  never replaced. Its former Write-only scope sentence was measured false: check-domain reconstructs
  Edit content and applies the same preservation rule. The operator authorized DEC-205's in-place
  correction to state the current Write/Edit truth. REQ-06 separately corrects the gate's own stale
  inline comment.
- **DEC-145 (unchanged).** The operator declined the proposed run-directory grammar unification at
  signature. DEC-145's purpose-squad sentence and harness-team's date-seq form both remain live;
  REQ-01's `run_uid` refusal absorbs an equal-slug collision. No decision is superseded or rewritten
  by this feature.
- **DEC-213 (supplies).** Harness tests live under `tests/unit/**` and `tests/integration/**`, and
  the directory selects the kind.

**Scope — issue #1305 only:**

- Siblings #1302, #1303, #1304, #1306 and #1308 own their own defects. In particular, **B-9 —
  `validate-digest.py` demanding `code_grade` and rejecting every value while `review_sha` is
  unpinned — belongs to #1303, not here**, even though `validate-digest.py` is also named in this
  diagnosis. That overlap is precisely the route by which scope would leak.
- Focused tests drive implementation; after they pass, run the project-wide unit and integration suites to prove no existing refusal was traded away. No formatter, linter, or build.
- Existing unrelated working-tree changes remain untouched.

**Evidence that no longer exists:**

- The BUG-1286 run directories are gitignored and their worktree is removed. No requirement or
  criterion here depends on inspecting them, and none may be added that does.

## Verification gaps

- None on the surface this feature touches. Every changed surface is a shell gate script or a Python
  validator plus its tests under `tests/unit/**` and `tests/integration/**`, covered by the `unit`
  and `integration` kinds, both `active` with a real runner in `harness.json`. The kinds carrying
  `cmd: null` — `component`, `ui`, `typecheck` — detect surfaces this feature does not touch, so no
  criterion below rests on one.

## Success Criteria

Every criterion is settled by the state of the repository and a command anyone can run — never by an
agent's report of it. Criteria naming an automated test also require that the test be **shown to fail
on the pre-change tree**, so a criterion cannot be met by an assertion that was always true.

- **SC-01 (Mode A — prevention):** Each lettered case below is pinned by its own test in the harness
  suite over an isolated bin root, and the letters are not one-to-one with tests: **(d) is two cases
  and (f) is two**, and each half of each must be present in its own right. Each refusing case is
  demonstrated to fail against the pinned pre-change copy
  of the script; each permitting case is recorded as passing on both trees rather than implied to be
  red.
  **(a) the seed-field refusal — and it fires wherever the checkpoint's own identity is
  unavailable.** A checkpoint write whose run_id, feature, squad or host disagrees with the run
  directory's recorded identity is refused on the Write route and on the Edit route, and the refusal
  message names the identity conflict rather than a generic shape error. The case is graded on a run
  directory whose prior checkpoint is ABSENT and whose witness disagrees, which is where the witness
  is the only identity on disk.
  **(b) the modal collision — equal seed fields, different minted identity.** A run directory holds a
  PRESENT prior checkpoint carrying `run_uid` U1, and an incoming checkpoint agreeing on run_id,
  feature, squad and host — the equal-slug case — carries a different `run_uid` U2. Refused on the
  Write route and on the Edit route; the message names both `run_uid` values and no field
  disagreement.
  **(c) the modal collision as a foreign run actually presents it.** The same PRESENT prior carrying
  U1, and an incoming checkpoint carrying NO `run_uid` at all — the state of any run that has not
  written a checkpoint of its own. Refused on both routes, with a message that names U1, says where
  it is recorded, and tells a writer that is not that run to use a run directory of its own.
  **(d) the recovering owner is never refused — two cases, and both must be present.** A checkpoint
  Write into a run directory whose `state.yaml` is a readable ZERO-BYTE file exits 0, and one into a
  run directory holding NO `state.yaml` exits 0 — in both cases with a witness already present in the
  directory recording a `run_uid`. This is the B-11 hand-repair action and refusing it would refuse
  the only repair that works.
  **(e) the resumed owner is never refused.** A Write updating an existing checkpoint, carrying that
  checkpoint's own `run_uid` and arriving with a different session id, exits 0. That case is
  simultaneously the DEC-154 upsert allowance and the proof that no session-keyed denial was
  installed.
  **(f) the two refusals do not collide — precedence is pinned, not assumed.** A run directory
  holding a witness for run_id A AND a prior checkpoint for run_id A carrying `run_uid` U1, against
  an incoming checkpoint for run_id B carrying U1, is refused with the EXISTING issue #1124 run_id
  wording — proving the seed-field refusal deferred to the more specific message. And a run
  directory holding a witness for run_id A and a prior that PARSES but carries no `run_uid`, against
  an incoming run_id B, is refused with the issue #1305 witness wording — proving the seed-field
  refusal answers where the checkpoint's own identity is unavailable. Both assertions read the
  message, not merely the exit code.
  **SC-01 FAILS if** (a) is absent from the suite at the review sha, or asserts an exit of 0, or is
  graded on a case where a parsing prior carries a `run_uid`; if any of (d) or (e) is absent or
  asserts a non-zero exit; if (b) or (c) is absent or is not shown red on the pre-change copy; or if
  either half of (f) is absent or asserts only an exit code.
  **Graded on exactly these routes:** Write and Edit. The Bash route is refused wholesale by
  `bash-write-guard.sh`'s `_run_artifact_guard` (:744-767 at `c369fb1f`) and is not re-graded here;
  NotebookEdit is graded by SC-11, which measures the route rather than assuming it.
  verify: automated        evidence: integration
- **SC-02 (Mode A — detection):** Running the harness state checker over a fixture tree containing
  one run directory whose checkpoint carries a `run_uid` disagreeing with the one its witness
  records, and one whose checkpoint and witness agree, reports a violation for the first and reports
  nothing for the second, and exits non-zero for the first tree and zero for a tree holding only the
  second. Both cases live in the harness suite, and the violating case is demonstrated to go
  unreported on the pre-change tree.
  verify: automated        evidence: integration
- **SC-03 (Mode A — detection shape):** The violation the checker emits names the affected run
  directory and states that the checkpoint's recorded identity disagrees with the identity recorded
  when the directory was first written, so an operator reading only that output can tell a clobbered
  checkpoint from a malformed one and knows which record to recover. **The falsifiable rule: the
  emitted text must name the run directory and both disagreeing values, and must NOT reuse INV-16's
  existing `non-checkpoint top-level key` wording** — that wording is the malformed-shape finding, so
  reusing it makes the two indistinguishable to the reader this criterion is about. Graded by reading
  the emitted message and the code that produces it, both read at the plan's pinned review sha with
  `git show REVIEW_SHA:` and never from the working tree.
  verify: inspection
- **SC-04 (Mode B — automatic grading):** A run directory whose `digest.md` carries no `artifact:`
  line is reported as a lead-digest-contract violation by a path that runs without anyone invoking a
  checker by hand. A test in the harness suite exercises that path against such a fixture, asserts
  the violation is reported and names the offending run directory, and asserts a compliant fixture in
  the same tree is not reported.
  verify: automated        evidence: integration
- **SC-05 (Mode B — legitimate repair):** A lead can bring its own run's non-compliant durable digest
  into compliance within that run, without allocating a new run directory; and the same route still
  refuses a write that would replace a different run's recorded digest. A test in the harness suite
  asserts both halves — the permitted correction succeeds, the cross-run replacement is refused — so
  the allowance cannot be satisfied by simply removing the guard.
  verify: automated        evidence: integration
- **SC-06 (Mode B — the guard's own record is true):** No comment or docstring in `check-domain.sh`
  asserts that its digest content guard applies only to the Write route or only to the PRE payload,
  and the description it does carry agrees with the routes SC-05's test observes the guard acting on.
  Graded by reading the guard and its surrounding comments at the pinned review sha
  (`git show REVIEW_SHA:.claude/skills/harness/bin/check-domain.sh`) against that test's observed behaviour.
  verify: inspection
- **SC-07 (Modes A and B — no protection traded away, and none newly invented):** Graded in two
  directions against `notes/regression-delta-BUG-1305.md`, the artifact the regression task produces.
  **Direction one — nothing removed.** Every refusal asserted by the harness `unit` and `integration`
  suites at `c369fb1f` is still asserted at the pinned review sha, and every assertion removed,
  weakened, or changed in its expected exit code, message or route is enumerated and justified under
  that note's `## Removed or altered assertions` heading. Compared by reading
  `git show c369fb1f:<path>` against `git show REVIEW_SHA:<path>` for every test file under
  `tests/unit/` and `tests/integration/` that this feature touched.
  **Direction two — nothing newly refused.** Each refusing or reporting branch this feature adds is
  paired in that note, under the heading `## Newly refused writes`, with the write it must still
  permit, and the grader COMPARES that note's six named pairs against the suite at the review sha:
  the legacy directory — prior and incoming both carrying no `run_uid` — still accepting an
  equal-run_id update; the resumed owner, carrying its own checkpoint's `run_uid` from a different
  session, still exiting 0, together with BOTH recovering-owner cases of SC-01(d) exiting 0; the
  lead's own-run digest append repair still exiting 0; `check-state.sh` exiting 0 over a fixture
  tree of legacy run directories that carry checkpoints and no witness at all; and the fifth pair,
  T-05's new fail-closed `return 2` in `validate-digest.py`, still exiting 0 over a run directory
  whose `digest.md` exists and is compliant and over the no-root-resolves case that fails open; and
  the sixth pair, the witness guard's route denials in `bash-write-guard.sh` and `check-domain.sh`,
  still permitting — in the same run directory — a Write of `state.yaml` and a Write of `digest.md`
  at exit 0, and leaving a Bash write to an unrelated ordinary file in that directory unaffected,
  so the denial is scoped to the one filename rather than to the directory.
  The note also records
  `check-state.sh`'s exit code and findings over this repository's own `.harness` tree, and states
  the one newly refused write this feature knowingly introduces — an owner that rewrites its
  checkpoint and drops `run_uid` — with the test that pins its message.
  **It FAILS if any of these holds:** an assertion present at `c369fb1f` is absent or weakened at the
  review sha and is not enumerated under the first heading; any one of the six permitted-write cases
  is absent from the suite at the review sha or is asserted to exit non-zero; `check-state.sh`
  reports a run directory whose checkpoint and witness agree, or reports any directory carrying no
  witness; either heading is
  absent; the `## Suite results` heading is absent, or records a non-zero exit or any FAIL line for
  either suite; or the note's BLUF states that a refusal holding at `c369fb1f` no longer holds, or
  that a write permitted at `c369fb1f` is now refused other than the disclosed dropped-`run_uid` one.
  verify: inspection
- **SC-08 — RETIRED with struck REQ-08:** No grammar-unification artifact is required. This
  criterion is retained only to record the signature decision: the change was frequency-only and
  its proposed supersession mechanics contradicted DEC-205.
- **SC-09 (Mode A — detection is self-limiting, so nothing historical can redden it):** The new
  invariant judges a run directory only where a WITNESS sits beside the checkpoint. That is the
  whole of the limit, and it covers every path the checker reports: an unreadable witness, a
  witness/checkpoint disagreement on a seed field, and a witness/checkpoint disagreement on
  `run_uid`. **A directory carrying no witness is invisible to the invariant** — it is reported by
  nothing, whatever its checkpoint contains, and no backfill of the historical corpus is part of
  this work. (D-13's summary sentence names the `run_uid` half only; the reported set is the three
  paths above, and T-03's task body is authoritative for it.) Pinned five ways at the pinned review
  sha, all in the harness suite unless stated: a test asserts the checker exits 0 and reports
  nothing over a fixture tree of run directories holding checkpoints and NO witness; a test asserts
  it reports nothing for a directory whose witness carries a `run_uid` and whose checkpoint carries
  none; a test asserts it DOES report a directory whose witness is unreadable; a test asserts it
  DOES report a directory whose witness and checkpoint disagree on a seed field; and
  `notes/regression-delta-BUG-1305.md` records the checker's exit code and findings over this
  machine's own control-plane root, whose `.harness` tree held 630 witness-less run-directory
  `state.yaml` files at `c369fb1f` on 2026-09-05 and grows continuously. **It FAILS if** any of the
  four tests is absent; if either silence test asserts a report; if either reporting test asserts
  silence; or if the recorded run over the control-plane root shows any finding from this invariant.
  verify: automated        evidence: integration
- **SC-10 (Mode A — the identity is minted, carried and witnessed):** With `check-domain.sh --post`
  invoked directly over an isolated bin root, a landed `state.yaml` in a fresh run directory carries
  a top-level `run_uid` matching `^[0-9a-f]{32}$` that the write payload did not contain, and
  `.run-identity.json` in the same directory records the same value. A second landed checkpoint in
  that directory leaves both values unchanged, and a landed checkpoint whose payload already carries
  a `run_uid` is left byte-identical to what was written. A test in the harness suite asserts all
  four, and the minting case is demonstrated to fail on the pre-change tree.
  **THE DIRECT INVOCATION IS THE EVIDENCE HERE, AND IT LEAVES ONE THING UNMEASURED:** whether the
  host actually DELIVERS PostToolUse for the Write and Edit tools. This criterion cannot observe
  that — it calls the hook's own script by hand — and NOTHING in this feature measures it. Delivery
  is DISCLOSED instead, in REQ-01's "End-to-end mint DELIVERY is UNMEASURED" bullet, which states why
  it cannot be measured before this merges and what signing accepts. (An earlier draft forwarded the
  question to SC-12; that criterion is retired.) Read alone, a met
  SC-10 proves the minting CODE and says nothing about whether it ever runs.
  **It FAILS if** any of the four assertions is absent from the suite at the review sha, or if the
  minting case is not shown red on the pre-change tree.
  verify: automated        evidence: integration
- **SC-11 (Mode A — the NotebookEdit route is measured, not assumed):** At the pinned review sha,
  `notes/probe-notebookedit-BUG-1305.md` records, at column 0, `route_reachable: yes|no` and
  `guard_fires: yes|no|n_a`, each with the verbatim command and output that produced it. If the probe
  shows a reachable route on which the guard does not fire, the note carries a `## Reported` section
  naming it as an open defect with the evidence, and the goal-check carries it to the operator.
  **It FAILS if** either line is absent, if a recorded answer has no command and output beside it, or
  if an unguarded reachable route is recorded without the `## Reported` section.
  verify: inspection
- **SC-12 — RETIRED, struck with T-12 (Mode A — the hook actually fires, observed once end to end):**
  This criterion graded `notes/probe-postmint-BUG-1305.md`, the one live-Write probe of PostToolUse
  delivery. It is retired in place rather than deleted, because the record of why it is gone is worth
  more than a clean list. **Why:** the probe it graded is `main-session-direct`, so it executes under
  the MAIN checkout's registered `check-domain.sh` while this feature's minting lands only in this
  worktree — `post_mint_observed: no` was guaranteed by construction, and the probe's mandatory
  `## Reported` section would then have published a false claim that this feature's prevention and
  detection are inert in practice. A criterion whose evidence is a guaranteed answer grades nothing.
  **What carries the question instead:** SC-10 proves the minting CODE, and REQ-01 discloses, where
  you sign, that end-to-end DELIVERY is unmeasured until this feature merges. Nothing grades SC-12,
  and no task produces the note it named.
- **SC-13 (Mode A — the witness cannot be destroyed by a governed write):** The run directory's
  witness — the sole input REQ-02's detection reads — is refused on EVERY governed write route the
  checkpoint is refused on, and the routes are named rather than assumed: a Bash write to it and a
  Bash removal of it are denied by `bash-write-guard.sh`'s `_run_artifact_guard`, and a Write and an
  Edit of it are denied by `check-domain.sh` before the write lands. Tests in the harness suite
  assert each of those four refusals, assert the path pattern matches the witness and not its
  sibling `state.yaml` or `digest.md`, and assert that a Write of `state.yaml` and a Write of
  `digest.md` in the same run directory are unaffected — so the denial is shown to be scoped to the
  one filename rather than to the directory. Each refusal is demonstrated to land at exit 0 against
  the pinned pre-change copies of the two guard scripts.
  **The POST hook is not an exception and needs no exemption:** it writes the witness from inside
  `check-domain.sh`'s own process, which is not a governed tool write, and its writer is itself
  write-once — the two halves agree rather than one covering for the other.
  **It FAILS if** any of the four route refusals is absent from the suite at the review sha or is
  asserted to exit 0; if the guard is asserted only on one of the two guard scripts; if the
  sibling-`state.yaml`/`digest.md` cases are absent or are asserted to be refused; or if the
  refusals are not shown green-before/red-after against the pre-change copies.
  verify: automated        evidence: integration

## Approval

status: approved
approved-by: operator
date: 2026-09-05
