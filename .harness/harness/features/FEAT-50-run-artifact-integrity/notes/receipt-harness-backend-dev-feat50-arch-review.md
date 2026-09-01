i# Architecture review — FEAT-50-run-artifact-integrity plan

## BLUF

Two real structural gaps, both in the direction of "the remedy passes its own listed tests but
does not close the defect it was written for": (1) D-01/T-01's presence-discriminator has a third
real payload shape — present-but-empty caused by the platform, not the persona — that it puts in
the WRONG bucket, exactly the misclassification issue #1056 was filed to fix; (2) T-04/D-06's
digest-clobber rule is reachable only through the `Write` tool's PRE route — `Edit` and `Bash`
writes to `digest.md`, including the append use case D-05 explicitly protects, have **zero**
enforcement at any stage, pre or post. A third finding: T-03's and T-04's own `verify:` are
text-presence checks, not behavioral proofs; the actual proof is deferred two tasks downstream to
T-05, which itself bundles two independent rule-proofs into one atomic gate. D-03's basename
equality is also demonstrably not load-bearing against this repo's own sanctioned short-id
worktree convention. Seams (judgement 4) and the settled DEC-174 routing are sound as drafted.

## Findings

| id | severity | element | summary |
|---|---|---|---|
| ARCH-01 | critical | D-01, T-01 (`validate-digest.py:1580`) | presence discriminator misclassifies a platform-caused present-empty message as a persona violation |
| ARCH-02 | high | D-03, T-03 (`plan.yaml:87-108,267-327`) | exact basename==feature-id equality fails against the tool's own sanctioned short-id worktree naming |
| ARCH-03 | critical | D-04, D-06, T-04 (`check-domain.sh:1361-1381`) | digest-clobber rule is reachable only via `Write`; `Edit`/`Bash` writes bypass it at every stage, including the append case D-05 protects |
| ARCH-04 | med | T-03, T-04 `verify:` | verify commands prove only that a string exists in source, not that the logic fires or fires correctly; real proof deferred to T-05 |
| ARCH-05 | med | T-05 | one task, one atomic verify, proves two independent rules (checkout binding, digest preservation); a failure/abort in one obscures the other |

## 1 — #1056 crux: does the discriminator discriminate?

Read `hook_mode()` in full (`validate-digest.py:1437-1621`) plus the branch it replaces
(:1580-1584). The docstring's three pass-throughs are: (1) no/non-harness `agent_type`
(:1470-1477), (2) `stop_hook_active` (:1478-1479), (3) our own failure — unreadable payload
(:1458-1463), unknown persona (:1586-1589), an exception in `validate()` (:1601-1607). T-01's
intent names and preserves (1) and (2) verbatim and never touches the three sites making up (3) —
its edit is scoped to :1580-1584 alone. All three pass-throughs survive T-01 intact.

**ARCH-01 — critical — D-01, T-01.** D-01 discriminates on PRESENCE: absent/null is our gap (open,
exit 0), present-empty is the persona's violation (closed, exit 2). That is sound for a payload
where "present but empty" can *only* arise from a persona that produced no text. But a present,
structurally-empty `last_assistant_message` is also exactly what a **tool-only final turn**
produces — a persona whose last action is a bare `yield`/tool call with no preceding or
accompanying assistant text. This harness's own tool docs describe exactly that path as
legitimate: "when `data` is omitted, your last assistant turn becomes the raw final result" (this
session's `_yield` tool schema) — language that only makes sense if a text-less final turn is a
supported shape the platform is expected to harvest from elsewhere, not a contract violation.
`last_assistant_message`, if it is (as its name implies) the text content of the final assistant
turn, is then present-and-empty for a reason that is the **platform's** turn-shape, not the
**persona's** silence — the same platform-vs-persona conflation issue #1056 exists to separate,
just relocated from "absent+null+empty are one bucket" to "empty is in the wrong bucket."

*Failure scenario:* an agent ends its turn with a tool-only final action (a `yield` call, or a
turn truncated by a context/token limit after tool use). `last_assistant_message` arrives present
and empty. T-01 exits 2, telling the agent to "fix" a text field the turn was never expected to
carry content in for that call pattern. The agent retries under the same conditions, produces the
same shape, loops until `stop_hook_active` (pass-through 2) silently swallows it — which reports
nothing to the dispatching tier, so the loop resolves by going quiet rather than by being fixed.
This is worse than the pre-fix behavior, which at least printed "returned no final message... 
passing through" every time.

*Alternative:* before committing D-01's two-way split, confirm from the platform's own hook
payload documentation (not inferable from this repo) whether a tool-only final turn produces
`last_assistant_message: ""` or omits the key/sets it null. If the former, D-01 needs a third
state: "present-empty AND the turn's last recorded action was a tool call with no text" must
resolve to fail-open like the absent/null case, not fail-closed. Weakest fix: keep D-01's split
but add the payload's own `stop_hook_active`-style signal (if the hook payload carries anything
identifying a tool-only turn) as an open_question to pm/operator rather than assuming presence is
sufficient — do not commit the exit-2 direction for state 2 without that confirmation.

## 2 — #1057 crux: is the derivation sound?

Read the `if _run_domain:` placement (`check-domain.sh:366-423`) and D-03/D-04/T-03
(`plan.yaml:87-108,267-327`). Placement is correctly inside the governed-agent-only branch, after
the raw-then-stripped match — confirmed reachable and ordered as claimed.

**ARCH-02 — high — D-03, T-03.** D-03/T-03 select the worktree "whose basename equals that
feature id" — exact string equality. `feature-worktree.py` — the tool this repo actually uses to
create worktrees — accepts `--id` matching `_ID_RE = ^(FEAT|BUG)-[0-9]+[a-z0-9-]*$`
(`feature-worktree.py:46`), i.e. the SHORT flow id (`FEAT-50`) is legal input, with no requirement
that it equal the full feature-directory slug (`FEAT-50-run-artifact-integrity`). The tool's own
`remove` subcommand (`feature-worktree.py:241-248`) resolves this divergence by PREFIX match
(`d.startswith(args.id + "-")`) — a built-in admission that basename and feature-directory name
are expected to differ. `git worktree list` on this very checkout shows worktrees named
`597-omp-behavior-baseline`, `BUG-1071-inv32-era-guard`, `close-gate-apostrophe`,
`omp-long-running-harness-supervision` — none of them a `FEAT-NN-slug` basename at all, confirming
basename drift is the observed norm, not a hypothetical.

*Failure scenario:* a dispatcher runs `feature-worktree.py create --id FEAT-50` (legal, short
form) for `FEAT-50-run-artifact-integrity`. T-03's exact match finds no worktree whose basename
equals `FEAT-50-run-artifact-integrity`, concludes "no registered worktree for that feature" per
its own documented behavior, and the binding does not fire — silently, with no signal, for the
entire feature's write history. This is precisely the "silent failure" class T-03's own intent
worries about elsewhere (the absorbing-exception clause) but does not defend against here.

*Alternative:* match by PREFIX against `harness_boundary.linked_worktrees`, the same rule
`feature-worktree.py remove` already uses: a worktree qualifies when its basename equals the
feature id OR the feature id starts with `<basename>-`. Concretely, in T-03's intent, replace
"select the one whose basename equals that feature id" with "select the one whose basename equals
the feature id, or of which the feature id is a `<basename>-`-prefixed extension" — reusing the
exact ambiguity-resolution idiom already coded at `feature-worktree.py:244-248` rather than
introducing a second one.

The absorbing-exception question: `linked_worktrees()` already catches every internal failure
(`OSError`, unreadable/non-UTF-8 pointer) and returns `[]` rather than raising
(`harness_boundary.py:157-182`), and by the time T-03's code runs, `harness_boundary` has already
been imported successfully under a FAIL-CLOSED guard one block up (:383-392). So an exception
reaching T-03's own call site is a narrow residual case (e.g. a `root` that is not a directory at
all), and absorbing it matches this file's own established precedent — narrowing checks fail open
on their own bugs, everywhere else in this file. Sound as drafted; no separate finding.

## 3 — #1058 crux: can the enforcement point see the write?

Read `has_shape_rules`/`shape_problems` (:1050-1353) and both call sites (:1361-1381, :1546-1547).

**ARCH-03 — critical — D-04 (placement), D-06, T-04.** The PRE route is gated explicitly:
"PRE. Only `Write` carries a whole-file `content` to measure ... `if _tool != 'Write' or not
target: sys.exit(0)`" (:1361-1368). `Edit`'s `tool_input` carries only `old_string`/`new_string`,
never full content, so an `Edit` to `digest.md` never reaches `shape_problems` in PRE mode at all
— confirmed by the file's own comment at :1323 ("`Edit` is never blocked pre-hoc").

For the OTHER four shape rules this is an accepted, pre-existing weaker guarantee: their checks
are self-contained (line counts, key whitelists) and an `Edit` that slips past PRE is still caught
by the immediate POST single-target route (:1372-1381, which reads the file as it landed) or the
periodic sweep. `RE_RUN_DIGEST` is different in kind: its check needs the **prior** content,
compared against the **incoming** content. The immediate POST route reads the landed file once and
passes that single reading as both `content` and (inside the branch) as the freshly re-read
"existing" file — the same bytes on both sides of the comparison, always. T-04's own intent admits
exactly this for "the sweep" ("on the sweep the content passed in IS the file's own content...
reports nothing... intended"), but that reasoning applies equally to the immediate single-target
POST route, which T-04 step 1 explicitly wires up via `SHAPE_PATTERNS`/`has_shape_rules` — the
same predicate the single-target POST route consults (:1377). And D-06 deliberately excludes
`RE_RUN_DIGEST` from `SWEEP_GLOBS`, so the periodic sweep never reaches it either.

Net effect: `RE_RUN_DIGEST` is enforceable **only** on a `Write` tool call reaching the PRE route.
Every other route — `Edit` (append or replace), `NotebookEdit`, and any `Bash` write
(`cat > digest.md`, `python3 -c "open(...).write(...)"`) — is completely unenforced, at every
stage, forever, not merely "unblocked before the fact and caught after" like the other four rules.

*Failure scenario:* D-05's own stated legitimate case — "a lead revising its own digest within one
run" — is realistically done with `Edit` (append text) rather than re-`Write`ing the whole file.
The identical mechanism, used destructively (a lead reuses another cycle's run dir and `Edit`s
`digest.md` with an `old_string` spanning the whole prior text), is refused nowhere: not PRE (not
`Write`), not the immediate POST (self-referential comparison), not the sweep (excluded by D-06).
Cycle-0's digest is destroyed exactly as issue #1058 describes, and T-05's test matrix (all framed
generically as "a write", never naming the tool) would not catch it because none of its seven
cases exercises `Edit` or `Bash` against `digest.md`.

*Alternative:* T-04's intent should state the gap explicitly rather than imply parity with the
other four rules, and either (a) narrow REQ-04/SC-05 to "a `Write` of a full-file replacement is
refused" (weaker, honestly scoped, matches what is actually built), or (b) extend coverage: add an
immediate-POST-route case for `RE_RUN_DIGEST` that diffs the landed content against the file's
`git`-tracked blob or a repo-side shadow copy captured at PRE time — out of scope for a narrowing
review to design in full, but the plan should at minimum add one sentence to D-06 naming the
`Edit`/`Bash` gap as accepted residual risk rather than presenting "the sweep would report
nothing" as the only case that "costs nothing" to skip.

## 4 — Seams and depth

One seam or three remedies: **three**, correctly. #1056 lives in a different script and hook
(`SubagentStop`/`validate-digest.py`) from #1057/#1058 (`PreToolUse`/`check-domain.sh`); #1057 and
#1058, though co-located in `check-domain.sh`, land in different existing mechanism families
(domain verdict vs. shape rule) with no shared state, no shared interface, and independently
triggerable failure modes. Deletion test: removing any one of the three changes leaves the other
two fully functional and independently testable. No shallow module is created — both edited files
are already the deep modules that own this class of decision, and D-07's marker-free mutant-copy
discipline keeps every test crossing the real CLI interface rather than reaching past it into
internals.

`harness_boundary.py` vs. inline in `check-domain.sh` for D-04's binding: `harness_boundary.py`
already owns "which checkout does this path belong to" (`linked_worktrees`, `worktree_owner`,
`checkout_relative`), but D-04's specific predicate — derive feature id from path, then match
against a registered worktree's basename — has exactly one caller today. Extracting it into
`harness_boundary.py` now would be premature: no second consumer exists, and this repo's own
"excavate, do not architect" discipline argues against factoring out a single-caller predicate in
anticipation of reuse. Sound as drafted; not flagged as a finding.

## 5 — Task decomposition

`depends_on` edges are correct except where T-05 is undersized (see ARCH-05): T-01←[] and T-03←[]
correctly mark the two independent starting points; T-02←[T-01], T-04←[T-03] (same-file
serialization, legitimate even though the changes are logically independent), T-06←[T-04],
T-07←[all] are all right. No missing edge and no over-serialization found elsewhere.

**ARCH-04 — med — T-03, T-04 `verify:`.** T-03's verify (`plan.yaml:323-327`) is `bash -n` (syntax
only) + a grep for the literal string `'belongs in the worktree'` anywhere in the file (satisfied
by a comment or dead code, not only a reachable, correctly-guarded deny path) + a `--resolve`
check that exercises the file's *domain lane*, unrelated to the new binding entirely. Nothing in
T-03's own verify actually invokes the binding logic — no fixture, no exit-code assertion for
"main-checkout write with worktree registered." T-04's verify (:383-393) is the same pattern: pure
text/AST-adjacent assertions over source (`'RE_RUN_DIGEST' in t`, membership in the
`SHAPE_PATTERNS` line, absence from the sweep-glob line), never executing the comparison. Real
behavioral proof for both is deferred entirely to T-05.

*Failure scenario:* T-03 lands with an inverted condition (denies the in-worktree write, allows
the main-checkout one — a plausible transcription slip given D-04's "narrows an ALLOWED verdict"
framing). T-03's own verify passes (the message string exists somewhere, syntax is valid, the
unrelated `--resolve` check is unaffected); the task is marked done. Two tasks and one
serialization edge later, T-05's `feature-checkout-main`/`feature-checkout-inside` cases would
eventually catch it — but only if T-05 is executed in the same pass and its cases are not
themselves broken by whatever caused the inversion. A reviewer reading T-03's PASS in isolation has
no basis for trusting the binding works.

*Alternative:* add one inline behavioral assertion to each of T-03's and T-04's own `verify:`
blocks — a minimal fixture (a temp dir with a `.git/worktrees/<id>/gitdir` pointer for T-03, or a
`runs/<id>/digest.md` with non-empty content for T-04) invoked directly against
`check-domain.sh`'s `--resolve`-style CLI, asserting the one exit code each rule is supposed to
produce for its own positive case. This does not replace T-05's fuller matrix; it removes the gap
where a task's own gate proves nothing about its own change.

**ARCH-05 — med — T-05.** Seven cases spanning two independently-triggerable rules (checkout
binding: cases 1-4; digest preservation: cases 5-7) plus one extra assertion, in one task with one
verify (`test-check-domain.py` must exit 0 AND four greps must all match). If case 5 or 7 aborts
uncleanly (uncaught exception in the mutant-copy machinery, e.g. the same import-path fragility
D-07/T-05's own case 4/7 guard against) rather than failing a named assertion, a script that
aborts mid-run typically leaves no per-check tally for the cases after it — losing the proof for
both `digest-append` and `digest-clobber-red` even though neither is related to whatever caused
the abort in an unrelated checkout-binding case earlier in the file. Conversely a bug isolated to
the checkout-binding cases blocks the whole task and, transitively, blocks T-06/T-07, even though
the digest-preservation rule (T-04) may be completely correct.

*Alternative:* split into T-05a ("Test the checkout-binding rule and prove it can report red" —
cases 1-4, `depends_on: [T-03]`) and T-05b ("Test the digest-preservation rule and prove it can
report red" — cases 5-7 plus the sweep-unaffected assertion, `depends_on: [T-04]`, and note it may
reuse T-05a's mutant-copy helper rather than duplicating it, per T-05's own instruction to reuse
case 4's helper). T-07's `depends_on` becomes
`[T-01, T-02, T-03, T-04, T-05a, T-05b, T-06]` in place of the current `T-05` entry.

## What I read

`validate-digest.py` (:1374-1643, `hook_mode` in full plus its two neighboring functions),
`check-domain.sh` (:339-423, :546-712, :903-1090, :1200-1236, :1299-1550 — signature-protection,
`domain_check`, `has_shape_rules`/`shape_problems`, sweep machinery, PRE/POST target construction),
`harness_boundary.py` (:102-183 `checkout_relative`/`linked_worktrees`, :384-593
`classify`/`worktree_owner`), `feature-worktree.py` (full — `dest_for`, `_ID_RE`, create/remove
id-resolution), `plan.yaml` (full — all decisions and all seven tasks), `BRIEF.md` (REQ-01..07,
SC-01..14, constraints, open ruling), `git worktree list` on this checkout.

## Open questions

None blocking my own read. ARCH-01's failure scenario turns on platform behavior (how Claude
Code/OMP actually populates `last_assistant_message` for a tool-only final turn) that is not
verifiable from inside this repository — flagged as `[INFERENCE]` in the finding itself and routed
to pm as an open question rather than asserted as fact.
