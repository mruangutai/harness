# UI Reviewer — Mode A design-contract review — FEAT-58-corpus-outside-worktree (plan stage)

## BLUF

FAIL. The plan's entire human/model interface is a set of refusal-message strings and three
SKILL.md paragraphs, and neither is specified to the standard the rest of this plan holds code to.
Two things gate: (1) T-01's refusal-check wording, read literally, contradicts T-08's own expected
success case for the feature's central intended-good-path scenario — a converged worktree calling
`corpus_features()` — and needs pinning before anyone starts TDD against it (F2). (2) SC-11, the
sole defense against the prose-side fail-open BRIEF itself names ("an agent that runs `ls` and
concludes the record is gone"), is graded by token presence and enforced only by an unscheduled,
unnamed reviewer — the same closed-enumerated-set fragility D-02/T-13 explicitly reject for code
sweeps, left unaddressed for prose (F5, F6). Message actionability across all refusal contexts is
also unpinned — every task tests substring presence, none tests whether the reader can act (F1, F3).

Measured, not guessed: I read plan.yaml (all 755 lines, both halves), BRIEF.md, both arch-eng
receipts, and the grilling note (readable at the main-checkout path, not the worktree — as
instructed). I additionally grepped all 26 `.claude/skills/**/SKILL.md` files and all 16
`.claude/agents/*.md` persona files for feature-corpus-enumeration language to test T-14's "three
surfaces are enough" claim empirically rather than by inference.

## Q1 — CorpusIncomplete / refusal-message actionability

**F1 (high).** The message contract (T-01 intent) pins exactly three tokens — `N of M`, the corpus
root, provider+ref — and nothing else. Every test that touches it (T-01 case (c)/(g); T-03 case
(a); T-04's integration suite; T-05 case (a); SC-04; SC-05) asserts **substring presence only**. No
task or SC asserts the message names a remedy, a next step, or even that this is *this feature's*
known/expected condition rather than an unrelated error. `1 of 88 features materialised at
<root>, provider=path, ref=main` is not actionable to an operator or agent unaware FEAT-58 exists:
it states a fact, never an action. The dispatch's own framing — "these strings are the ENTIRE human
interface of this change" — makes this the single highest-leverage gap in the plan.

**F2 (high — internal contradiction, needs pinning before build).** T-01's `corpus_features`
spec: "compare the number of feature directories MATERIALISED under `os.getcwd()`'s own checkout
against `len(resolved)`. When materialised < resolved ... raise `CorpusIncomplete`." Read literally,
`os.getcwd()` is the *calling process's* checkout — inside a **correctly converged** worktree
(the feature's own intended end state, REQ-01) that is always `1`, while `resolved` (from git
history) is `M` (e.g. 88). `1 < 88` is true on every legitimate call from inside a converged
worktree, which means the literal spec raises `CorpusIncomplete` on **every** successful read, not
only broken ones. This directly contradicts T-08 case (c) — "from inside the worktree,
`corpus_features` resolves the SAME set of feature names as the owner root's default branch" with
no exception expected — and REQ-02/SC-01/SC-03, whose whole point is that enumeration succeeds
from inside a 1-feature worktree. Nothing in T-01, T-02, or T-08's unit tests exercises
`corpus_features` with `root=owner_root` while `os.getcwd()` is a sparse worktree (T-02's fixture is
a *plain* checkout where root==cwd; T-01's fixture (c) is a single-checkout partial-materialisation
case, also root==cwd). The one test that would exercise the real split (T-08 case (c)) asserts
success, which only holds if "materialised" is counted at `root`, not at `os.getcwd()` — the
opposite of what T-01 says. This is exactly the kind of internal-consistency gap Mode A exists to
catch pre-build: whichever reading is intended, T-01's prose needs to say so explicitly, or a TDD
implementer following T-01's text first will write a red-then-green test that later contradicts
T-08's.

**F3 (med).** The one-line shape is reused unchanged across every propagation site regardless of who
reads it. Only T-05 (merge-gate.py) adds an audience-specific clause ("the merge cannot be
attributed because the record could not be read") — an implicit concession that the bare message is
insufficient for a *model* reading a PreToolUse deny reason and deciding whether to retry, escalate,
or stop. That same augmentation is not extended to check-state.sh, the four T-04 validators, or
check-domain.sh (T-06), several of which run automatically as hooks a model reads via tool-call
stderr at least as often as a human runs them by hand in a terminal. No task differentiates message
content by trigger context (human CLI vs. automated hook read by a model).

**F4 (low/info).** T-08 STEP B's positive-control failure text ("print WHICH required path is
missing... exit non-zero") names the fact but not the cause class (stale derivation vs. genuine repo
drift) or the remedy. Lower severity: it fires only at worktree-creation time, read by whoever ran
`feature-worktree.py create`, who has more context than a downstream merge-gate reader.

## Q2 — T-14's three-file prose treatment

Measured: grepped every `.claude/skills/**/SKILL.md` (26 files) and every `.claude/agents/*.md` (16
persona files) for feature-corpus-enumeration patterns (`.harness/*/features`, `features/*`,
`ls .*features`, `enumerate.*feature`, `worktree.*enumerat`). **Zero hits outside the three T-14
targets** — `harness-curate/SKILL.md`'s enumeration loop is over `.harness/*/expertise/`, a
different corpus (Expertise, not the feature record), and `harness-team/SKILL.md`'s feature paths
are writes to the caller's *own* feature via `HARNESS_FEATURE_TREE_ROOT`, never cross-feature reads.
So for today's tree, the three files are the right three — no fourth violator exists right now.

**F5 (med) — the sweep test doesn't close the claim's actual scope.** SC-11 states "no live
agent-facing instruction directs a reader to enumerate the record relative to its own checkout" —
a claim over the whole prose corpus, present and future. T-14's `test-corpus-prose-anchor.py`
"reads each of the three files... asserts per file" — a **fixed, named 3-item enumeration**, not a
repo-wide sweep (e.g. a glob over `.claude/skills/**/SKILL.md` + `.claude/agents/*.md`). This is the
identical shape D-02 rejected for `corpus_features` ("the opt-in shape was rejected... a fifteenth
reader would silently reopen the fail-open") and the identical shape T-13's lint exists to catch for
code readers. Nothing plays that role for prose: a 27th skill file or a new agent-definition file
added later that describes reading another feature's record, without the anchor, reddens nothing.
BRIEF's own "Prose has no gate at all" concession is honest about SC-11 being inspection-only, but
even the inspection instrument (T-14's test) is scoped narrower than the claim it exists to serve.

## Q3 — BRIEF SC-01..SC-14 walk: design claims graded by a method blind to design

Walked all fourteen. Twelve (SC-01/02/03/06/07/08/09/10/12/13, plus the presence half of SC-14) are
factual/behavioral: counts, set equality, exit-status ordering, file-diff absence. A count or an
exit code cannot be gamed into looking like quality it isn't — these are sound as specified.

Two are different in kind:

- **SC-04 / SC-05** ("prints `N of M` with the corpus root" / "names what it could not resolve") —
  these grade the *presence* of the refusal message's identifying tokens, not whether the message
  is a **good** refusal (F1 above). A token-stuffed, unhelpful message and a genuinely actionable one
  both pass identically.
- **SC-11** — the clearest instance the dispatch names. "States where the corpus lives and how to
  read it" is a communication-quality claim; the evidence is "a named token in each file" plus an
  absence search with a positive control (T-14). A paragraph that contains the required keywords but
  buries the caveat, or explains the mechanism without explaining *when an agent needs to reach for
  it*, passes exactly as well as a clear one — the check cannot tell a good anchor from a
  token-stuffed one, which is precisely what Mode A asks me to test for.

**F6 (high) — SC-11 names an unscheduled gate.** BRIEF is explicit: "Prose has no gate at all...
only the reviewer catches it." That is an honest residual, but no task in plan.yaml names a
reviewer persona or schedules a review step for the prose/message surface specifically — every task
in this plan is `main-session-direct` or `team`/`harness-backend-dev`, with review left to the
standing ship-time pipeline, whose persona routing is discretionary. The clearest evidence this
routing is not reliable by default: **this very dispatch had to explicitly instruct a UI reviewer to
treat "REFUSAL MESSAGES and AGENT-FACING PROSE... as the design surface it is"** — if default
ship-time review routing already did that, the instruction would be redundant. Naming "the
reviewer" as SC-11's gate without naming *which* reviewer, or adding anything to the plan that
makes that dispatch non-discretionary, leaves the plan's only defense against the exact fail-open
this feature exists to close (in its prose form) resting on nobody's explicit obligation.

## Findings summary

| id | severity | question | one-line |
|---|---|---|---|
| F1 | high | Q1 | Refusal-message spec and every test on it pin tokens, never actionability |
| F2 | high | Q1 | T-01's materialised-vs-resolved check, as worded, contradicts T-08(c)'s expected success from a converged worktree |
| F3 | med | Q1 | Message shape undifferentiated by audience (human CLI vs. model reading a hook deny) |
| F4 | low | Q1 | T-08 STEP B failure text names the fact, not cause or remedy |
| F5 | med | Q2 | Prose sweep test is a fixed 3-file enumeration, not a corpus-wide lint; same shape D-02/T-13 reject for code |
| F6 | high | Q3 | SC-11's sole gate ("the reviewer") is unnamed and unscheduled; this dispatch itself had to override default routing to make it happen |

## Open questions for pm / eng-lead

- Q1: Is `corpus_features`'s incompleteness check meant to compare materialisation at `root`
  (owner root — always complete, so the check only fires on genuine corpus/ref-resolution failure)
  or at `os.getcwd()` (the calling checkout — which is 1 by design in every converged worktree, and
  would fire on every legitimate call)? T-01's text says the latter; T-08 case (c) requires the
  former. Pin this before T-01 is built — it decides whether the whole fail-closed contract is
  usable from its own intended success path. (blocking: true)
- Q2: Should ship-time review for FEAT-58 explicitly commit to dispatching a reviewer who treats
  refusal-message and prose quality as gate-worthy (this review had to be told to), rather than
  leaving that to standard discretionary routing? (blocking: false)
