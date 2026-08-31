# Altitude review — FEAT-45-adversarial-plan-panel (simplify/altitude angle)

BLUF: two real altitude findings. (1) The T-02/T-06 lead-transcription contract has two
homes and only one (`.omp/agents/harness-validator-lead.md`, T-06) is authoritative —
**fold-in**. (2) T-02's `should-not-exist` return contract omits the one detail that makes
it machine-parseable — the top-level YAML key name for the findings list — **fold-in**.
Everything else audited (D-05 hash mechanics, D-13 markers, literal-phrase greps in
T-01/T-02/T-10, T-03/T-04 near-sentence playbook prose, the eval residual) sits at the
right altitude or is already handled by the plan's own conventions; recommendations below
are `leave` / `briefing-row`.

## 1. Mechanism vs. behaviour

- **D-05 / T-09 — sha256 + first-8-hex + `PF-` + length 11.** The *shape* (`PF-` prefix,
  short hex suffix) is acceptance-worthy: it's referenced by humans reading `plan.yaml`
  findings and quoted verbatim in T-05's template comment. But the specific **algorithm**
  (sha256) is not forced by anything downstream — every consumer calls
  `panel_findings.py id …` and never computes a hash itself (T-05: "never typed by hand"),
  and T-09's own verify tests only behaviour (`A==B` on reword-insensitive input, `A!=C` on
  content change, `len==11`), never the algorithm name. D-05's "choice" prose commits to
  sha256 as if it were part of the signed decision, so a future swap to a different digest
  (e.g. for speed or a different truncation for lower collision odds) requires reopening a
  signed decision for a change nothing outside the helper can observe. Cost is low (one
  green-field, single-owner helper) but the decision text overstates what's forced.
  **leave** — real but too small to justify pm churn; note it as a comment-level nit, not a
  plan edit.
- **D-13 / T-07 / T-08 — literal marker comments, column zero, exact text.** Earned. D-13's
  argument rules out the two obvious alternatives (relative commit ref rots the moment T-07
  lands as its own commit; a pinned sha or vendored copy both rot in their own way) and the
  markers are the only thing T-08's `inv32-red` mutant case can grep to locate the region to
  delete — this is the same idiom `test-check-state.py` already uses twice (`T14_MARKER`,
  `T10_MARKER`). No looser spec would let the mutant test measure anything real. **leave**.
- **T-01 literal phrases ("wrapped non-harness reader", "plan-phase gate"), T-02/T-10
  verbatim reader questions.** Also earned, for the same reason: these are machine
  verification of prose *content*, and a grep for the exact precedent-naming phrase (T-01)
  or the exact question the reader must be asked verbatim (T-02/T-10, backed explicitly by
  SC-01: "asserted per reader, never as a file-global match or a count") is the only way a
  unit test can confirm REQ-02/03/04/11 were actually discharged instead of paraphrased into
  something weaker. **leave**.
- **T-03/T-04 near-sentence-level playbook prose.** Not over-specification despite the
  appearance: verify only greps a handful of tokens (`'The plan phase'`, `plan-panel`, the
  note-path spelling, `DEC-176`; T-04: `plan-panel`, `adversarial`, `DEC-176`,
  `approval.rulings`, `simplify`), leaving the builder free above that floor. The intent's
  extra sentence-level guidance exists because this prose is *executable* — the orchestrator
  literally reads `SKILL.md` and `harness-plan.md` at runtime and acts on the words — so an
  under-specified instruction here (e.g. a vaguely-worded note-path convention) reproduces
  exactly the measured hand-run failure BRIEF cites (pm denied the wrong path spelling). This
  is the plan correctly landing on the tight side of the mirror failure the dispatch warns
  about. **leave**.

## 2. Under-specified prompt contract (T-02, `should-not-exist` reader)

REQ-05's own text says this reader's return is validated by **nothing** — the wrapping lead
is the whole contract (T-06). T-02's intent fully specifies the per-entry field shape
(`reader`, `summary`, `severity`, `why`), the severity enum including `unrated`, and the
"empty list is valid, padding is worse" instruction — good coverage. But it never names the
**top-level YAML key** the findings list must be keyed under. "return ONE fenced yaml block
carrying a findings list" tells a builder *what's inside* but not *what wraps it* — a
`general-purpose` persona has no harness convention to fall back on (it isn't one of the 16
agents and doesn't inherit DEC-172's return-shape training), so two runs of the identically
worded prompt could legally produce `{findings: [...]}`, a bare top-level list, or
`{results: [...]}`, and the lead (T-06, which is assigned "parsing the reader's fenced yaml
block" as its own SHAPE job) has no fixed target to parse against — it has to guess intent
per run, which is exactly the CONTENT-vs-SHAPE line T-06 draws blurring back into the lead's
lap. Concrete cost: an inconsistent top-level shape across runs is indistinguishable from a
malformed return, both of which only get one `loop_back` retry (`max_cycles: 1`, D-11)
before `escalate` — a missing key name is a plausible, silent cause of spurious escalations
that have nothing to do with panel judgement.
**fold-in** — add one sentence to T-02's should-not-exist prompt spec: "the fenced yaml
block's top-level mapping has exactly one key, `findings`, whose value is the list;" this
belongs in the same paragraph that already specifies the per-entry schema, not a new task.

## 3 & 5. One rule, two homes — the lead's transcription contract

T-06 (`.omp/agents/harness-validator-lead.md`, "Hosting plan-panel" section) and T-02's
closing comment block on `plan-panel.yaml` both state the **same specific mechanics**:
transcribe with the reader's own severity, never assign a number to an `unrated` arrival,
assign the `PF-` content-hash id, de-duplicate across readers, carry `severity_max`, record
assessed-and-dismissed rather than dropping. `review.yaml`'s existing closing-comment
convention (lines 88-93, which T-02 is told to match "in review.yaml's style") only restates
**generic**, already-true lead behaviour (merge, dedupe, `severity_max`, trace, don't drop
silently) — it never repeats FEAT-45-specific new mechanics like the `unrated`-gates-as-high
rule or the PF- id assignment, because those live nowhere else *but* the lead's own agent
definition today. T-02, by contrast, restates T-06's new, panel-specific rules verbatim.
Two consequences: (a) nothing greps the closing comment's content in T-02's verify, so it can
drift silently the moment T-06 or a later feature revises the transcription mechanics — no
detector like `sync-agent-adapters.py` or `gen-decisions-index.py` watches this pairing; (b)
the agent definition is what's actually loaded at every validator-lead spawn and is the only
copy that governs real behaviour, so the team-file copy is decorative at best, actively
misleading at worst if it goes stale.
**fold-in** — trim T-02's closing comment to the `review.yaml`-style *generic* recap only
(merge, dedupe, `severity_max`, trace, assessed-and-dismissed) and drop the FEAT-45-specific
mechanics (unrated-as-high, PF- id assignment specifics) from it; those stay solely in T-06's
target file, which is the one place that's actually loaded and actually authoritative.

## 4. Accepted residual — eval quality gap (BRIEF `## Verification gaps`, SC-11)

The BRIEF is honest that nothing in this repo grades the panel readers' finding *quality*
(`eval: cmd: null`), and defers a standing eval runner to dev-ops backlog — correctly: that
infra investment is out of scope and reopening it here would violate the settled-scope
boundary. But the compensating control it names — "the operator, by eye" (SC-11) plus one
hand-run against FEAT-38's plan, n=1 — is weaker than it needs to be *without* touching the
standing-runner scope. A **feature-scoped** eval (a small reference set of 3-5 known
good/bad findings against the `should-not-exist` and `scope` prompts, a one-line rubric, a
stated pass threshold, run once by hand before sign-off and recorded in a receipt) is
squarely within what this feature's own author-the-eval role can produce, is materially
stronger than an unrepeatable eyeball check, and requires no `eval:` runner infrastructure
at all — it's a difference of authorship, not of scope. Model-independence's unprovability
(REQ-02, SC-14) is, by contrast, already handled at the right altitude: honestly disclaimed,
correctly bounded to what SC-14 *can* grade (dispatch-chain independence), nothing further
to add.
**briefing-row** — the BRIEF already has a working template for exactly this situation (the
plan-door id-collision paragraph: "named here so it is not lost, not so it is absorbed").
Add one line of the same shape to `## Verification gaps` naming a lightweight, per-feature
reference-set eval as a materially cheaper compensating control than eyeball+n=1, distinct
from the standing eval-runner backlog row — so it isn't lost, without expanding FEAT-45's
task list now.

## Verification

`git status --porcelain` against `plan.yaml`, `BRIEF.md`, and everything under `.claude/`
in this worktree returned no output — none of them were modified by this review.
