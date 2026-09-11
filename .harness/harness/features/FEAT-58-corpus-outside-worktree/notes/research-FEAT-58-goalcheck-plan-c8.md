# Goal-check — FEAT-58 plan, cycle 8 (final) — does this plan deliver the operator's stated intent?

**YES. Nothing structural. One new high, six axes clean, three low.** All five things done means are
DELIVERED by a producing task, not merely tested for; all seven binding items each hold their own REQ
and at least one automated SC; the three weight-bearing proofs can each report RED; the two-route D-2
denial and the positive controls are intact; nothing the DoD kills has crept back. Four of the six
cycle-8 fixes landed whole. Two did not: **PP-04's red proof cannot redden as instructed** (high), and
**PP-01's env-strip witness is always-green** (med). Under the operator's Q8 terms both are LISTED, not
fixed. Plan-stage verdicts below grade *coverage*, never shipped outcomes — nothing is built.

## Findings

**H-01 · N-13 PART 1 `PART 1 RED PROOF` (plan.yaml:3239-3247) · high · CLAUSE DEFECT, and a build test
will NOT catch it — it fails by staying green.**
The proof stages the pre-fix `feature.json`-keyed derivation and requires "clause 1 REDDENED naming the
mismatch between the directory count and the record count". It cannot. Measured at the owner root just
now: the pre-fix derivation yields **MISSING = [] and UNEXPECTED = 10** (79 tracked records, all of whose
directories exist; the 10 record-less dirs are the whole gap). Clause 1 as PP-03 loosened it asserts
only *no refusal* + *missing set empty*, and explicitly **TOLERATES an unexpected-only report**
(:3207-3211); N-06 PART 1 rules an unexpected-only report **NON-GATING outside a linked worktree**
(:2278-2288). So the staged pre-fix copy passes clause 1, clause 2 and clause 3 identically to the
shipped one. Consequence, and it is the real one: **PART 1's four assertions do not discriminate the
pre-fix derivation from the shipped derivation at the owner root at all** — the surface added because
three controls were found blind is itself blind to the derivation change it was built for.
*Concrete change:* stage a mutation that produces a **MISSING** name (e.g. a derivation returning one
name that is not on disk), so the choke point's gating branch is what reddens; record the 89-vs-79
observation as the tolerated printed report, never as the red. *Not structural:* SC-16's owner-root half
as the operator amended it is the **absence of a refusal**, and the plan matches that text; REQ-03's
refusal behaviour is proven by N-06 PART 3 (b) and test-check-state-scope.py case 2, which do redden.

**M-01 · N-13 PART 1 discard-notice assertion (plan.yaml:3184-3193) · med · CLAUSE DEFECT, always-green,
build will NOT catch it.**
The clause exists because `resolve_root` prefers a MARKER-carrying `HARNESS_PROJECT_DIR` override
(`harness_boundary.py:79-81`, verified) and this worktree carries MARKER — so a stray override redirects
even a by-path run. But the discard notice is printed **only when the override is set and does NOT carry
MARKER** (`harness_boundary.py:82-86`). The dangerous case — override carrying MARKER — is honoured
**silently**. Notice-absent is therefore true when the strip works *and* true in the exact failure it was
added to detect. Clause 3's `>70` floor does not backstop it either: this worktree is a full checkout,
so a worktree-rooted run reads 89 and clears the floor. *Concrete change:* assert the audited root, not
the notice — e.g. assert the reached feature-directory NAME SET equals `os.listdir(<owner_root>/.harness/harness/features)`.

**M-02 · N-13 PART 2 clauses 3 and 4 (plan.yaml:3292-3300) · med · CLAUSE DEFECT, build catches it.**
"Run the shipped `check-state.sh` **with cwd at the probe**" is the spelling the operator struck one
paragraph above at Q1: `cwd` is inert (`check-state.sh:20-47`). Read as the owner root's copy, the
preflight is skipped (not a linked worktree) and clause 3's dirty-tree report never appears; clause 4's
structural refusal likewise grades the wrong tree. *Concrete change:* name
`<probe>/.claude/skills/harness/bin/check-state.sh` by absolute path, and strip `HARNESS_PROJECT_DIR`
from that child env too, for M-01's reason.

**L-01 · N-13 PART 2 guard citation (plan.yaml:3276-3280) · low · CLAUSE DEFECT.** Two errors in one
sentence. The creation door is `bash-write-guard.sh:575-642`, not `:624-741` — the no-destination and
relative-destination refusals it names sit at `:607-619`, *below* the cited range, and `:701-741` is
`feature_checkout_guard`. And "refuses ANY `--force` flag" is false for `add`: the force refusal at
`:582` is inside `if _sub in ("remove","prune")` (`:577`); `--force` on `add` is skipped as an ordinary
flag at `:538`. The instruction it justifies (absolute path, no `--force`, and clause 5's unforced
`worktree remove`) stays correct and executable. *Concrete change:* re-anchor to `:575-642` and scope the
force claim to `remove`/`prune`.

**L-02 · BRIEF.md:401-403 `## Constraints` · low · CLAUSE DEFECT.** Still reads "`core.hooksPath` is
`.claude/skills/harness/hooks`, **tracked so it travels with a clone**" — the precise claim the operator
withdrew at cycle 8 (`answers-operator-c8.md:74-96`; DoD `:102-108`). N-13 carries the corrected framing;
the approval-gated artifact the operator signs does not. *Concrete change:* one line — replace with the
`harness-init/SKILL.md:81` + INV-31 framing already in N-13.

**L-03 · N-09 note template vs its own verify (plan.yaml:2735-2744 / :2670) · low · CLAUSE DEFECT, build
catches it.** The shape block indents `## AUDIT UNCHANGED` six columns deeper than `## NOTHING ALTERED`,
reading as a nested sub-block, while the task's verify greps `grep -qxF '## AUDIT UNCHANGED'` — a
whole-line, column-0 match. *Concrete change:* dedent that heading and its three fields in the template.

## The ten axes

1. **The five things done means — DELIVERED, not merely tested for. Clean.** (1) N-02 checks 1/4b +
   N-04's `post-checkout`; tested N-05. (2) N-02 check 3/4a creates the symlink, N-03 gitignores it;
   tested N-03/N-05. (3) N-06 PART 1 narrows at the single choke point (`check-state.sh:118-120`).
   (4) N-07 PART 1/2 — predicate plus the `merge-gate.py:132-142` consumer swap, the DoD's own consumer.
   (5) N-02's three-condition scope guard plus D-03's run-don't-exec shims; tested N-09 (a)-(d).
2. **The seven binding items — clean.** Read as REQ text, not the table: D-1→REQ-01→SC-01;
   D-2→REQ-02→SC-01/02; D-3→REQ-03→SC-04/05/06/14/16; D-4→REQ-04→SC-07; D-5→REQ-05→SC-12;
   M-1→REQ-06→SC-09/10/16; M-2→REQ-07→SC-11. None merged, none deferred, **all fifteen criteria are
   `verify: automated evidence: integration`** — nothing a runner could grade is left to inspection.
3. **The three that carry the weight — all three can report RED. Clean.** (a) N-04 PART 2 clause 4 keeps
   the pre-change reproduction *in the file* (shim without the repair call) and asserts the two runs
   DIFFER; the 3337/3807 figures stay a receipt-recorded host residual, never a fixture expectation
   (:1983-1987, :2004-2007). (b) N-06's equivalence test excludes exit status and carries both the
   at-least-one-real-finding precondition and the perturb-and-expect-inequality clause (:2447-2467).
   (c) N-02's `test-worktree-state-norepair.py` compares manifest **plus** skip-bit set per break and
   carries a red proof routing one break through `--repair` (:1835-1853).
4. **Two-route D-2 denial — undisturbed. Clean.** N-03 (c): Write/Edit via `check-domain.sh`'s registered
   payload and Bash via `bash-write-guard.sh` — `:855` verified as the `wrong_checkout` branch — with the
   paired positive control at :1906-1907. D-02 and D-14 both still record it.
5. **Positive controls — clean.** N-05 GROUP 2 asserts per path, never by exit status, including both
   `.claude` and `.agents` spellings with `realpath` equality, the three non-features `.harness` subtrees
   separately, `.harness/harness.json` separately, and `.harness/corpus` as `islink` + `realpath`.
   GROUP 3 proves derivation at three levels with the no-source-edit clause and a literal-list red proof.
6. **The six fixes — four whole, two defective.** (i) LANDED: by-absolute-path invocation, no `cwd`
   reliance, no review-sha framing (0 occurrences of the variable in N-13), matching the amended SC-16.
   (ii) LANDED (:3207-3218). (iii) **DEFECTIVE — H-01.** (iv) LANDED: the fourth skip names INV-31 and
   its wording, with its own discrimination (:3320-3347); the anchor is self-correcting — `:2508-2567`
   as written, verified. (v) LANDED: N-06 PART 4 `THE ZERO-MATCH REFUSAL CASE` (:2416-2426). (vi)
   **DEFECTIVE — M-01** (the strip itself is right; its witness is not).
7. **Executability — one med, one low, otherwise clean.** Every `verify:` resolves: neighbours
   `test-post-merge-sweep.py` and `test-hooks-install.py` exist on disk; `--strict` is specified in
   N-01 (:1655-1661) before N-09 consumes it; `feature_corpus.corpus_root` is created by N-10, which
   N-13 depends on; INV-31, `_ID_RE` (`feature-worktree.py:46`), `branch-create-gate.sh:89/:63-66/:91-92`,
   `board_lifecycle.py:472-477`, `validate-feature-json.py:40-55`, `harness_boundary.py:66-78` and
   `check-state.sh:36-46` all verified against the files. `check-plan-routes.py` on this plan: **0
   violations, exit 0**; every DEVIATION is the DEC-174 carve-out. Defects: M-02 and L-03.
8. **Coverage — 45 is right, 48 is wrong. No row dropped, no demotion hidden.** The ledger's subject is
   fixed by its own header (`runs/consolidate-eng/digest.md:66-68`): the DoD matrix rows A-01..A-23 plus
   X-1/X-2 plus finding-derived rows — a provenance map from a source set to landing places, never a
   census of graded assertions. `apply-c5.md:61-63` settles it by precedent: the struck
   `test-nonregression-notes.py` and N-01's list-equals-plan comparison were ruled **not ledger rows**.
   The three c8 items are the same class — a case inside an existing row's file, a D-13 one-time proof,
   and a discrimination clause inside a skip. Counting them would oblige counting the dozens already
   unenumerated (N-05 GROUP 2 alone is ~10 named assertions), giving a number far past 48. The two D-13
   demotions remain visible by name in `BRIEF.md:341-350`. **Nothing dropped, nothing silently demoted.**
9. **Shape — clean.** Twelve tasks, each a coherent surface; N-06's four parts are one subject (the
   audit) and N-10's fold is D-14's recorded consequence. `change_type` vs `harness.json`: every
   `cross_module` (N-02/06/10) and `feature` (N-04/07) task ships both a unit and an integration file;
   `config` (N-03) ships the integration its shape triggers; the six `scaffolding` tasks require none and
   ship tests anyway. No task's kind demands evidence it cannot honestly produce.
10. **What the DoD kills — clean, none crept back.** No migration/convergence task exists (the
    `lanes:` `migration-record.md` row is declared a vestige of a struck task in D-07 :278-281, produced
    by nothing, and the block is unwritable). Corpus-root anchor and the fifteen-reader ledger are
    rejected in D-09 with the reason recorded. `clonefile`/`reflink` appears **once**, at :1665, inside
    N-01's exclusion assertion. No criterion or verify is gated on a byte figure or `du`; N-03's
    sha256 is byte *identity*, the DoD's own strong form. No cache: D-01 and N-10 PART 1 forbid it.

## Open questions for the operator

- **Q1 (non-blocking):** H-01's remedy is a different staged mutation, not a criterion edit — SC-16's text
  is yours and the plan matches it. Accept at signature, or convert to a build-phase task on N-13.
- **Record correction, no action:** `research-fixpp-c8.md:86-89` says `harness_boundary.py` "is not in any
  task's `files:`". It is — N-06 (plan.yaml:2202) is its writer, so pinning the notice string is in scope
  for N-06 if M-01's remedy needs it.
