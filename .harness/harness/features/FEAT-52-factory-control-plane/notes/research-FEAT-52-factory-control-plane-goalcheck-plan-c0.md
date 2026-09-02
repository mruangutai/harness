# Goal-check — FEAT-52 drafted plan vs the operator's stated intent — cycle 0

**No. The plan does not yet deliver the stated intent.** Two of the three settled items land; the third
(`BOTH` a lint `AND` a spawn-time assertion) is `partial`; and the plan carries one absolute root for
both control-plane READS and feature-tree WRITES, which — measured, not inferred — sends a
worktree-based agent's receipt and observations writes into the MAIN checkout, off the reviewed branch.
Premise grade: **sound with caveat, and the caveat is not encoded**. Unsignable as drafted.

Ran without `notes/research-factory-control-plane.md` (absent; `notes/` was empty). Not a defect:
grepped the feature dir for `notes/research-` — **no citation to it anywhere** in BRIEF.md or plan.yaml.

## A. The three settled items

1. **Absolute root injected into every factory agent's preamble — `delivered`.**
   REQ-01, SC-01 (BRIEF.md:71-74), T-01 steps 1-2 + test cases (plan.yaml:100-149). Coverage of "every
   factory agent" holds: the injector fires only for `^harness-[a-z0-9-]+$` (inject-expertise.sh:27-29,
   settings.json:8) and **all 16 dispatchable agents are `harness-*`** (`.omp/agents/*.md`), so the
   matcher's set equals the dispatchable set. The main session is not a subagent and receives no
   injection — consistent with #356 comment 2's triage, and with T-03's three exemptions.
2. **Read-only skill read through that root, product writes unchanged — `delivered`.**
   REQ-03, SC-06 (both directions, BRIEF.md:95-99) + SC-07; T-05 steps 1-3 (plan.yaml:343-367), D-05
   (plan.yaml:75-84, grounded: settings.json registers PreToolUse for Write|Edit, Bash, Task|Agent only
   — nothing matches Read). T-05 step 2 explicitly forbids a `team-config.yaml` grant.
3. **BOTH a static lint AND a spawn-time assertion — `partial`.**
   Lint: REQ-04, SC-03/04/05, T-03 + T-06 + T-07 — specified, with a real red proof (SC-05). Spawn-time:
   D-04 (plan.yaml:65-74) and T-01 step 3 assert only that the ROOT RESOLVED; **no task asserts anything
   about a path at spawn**. The grilling's question was "how is path drift prevented"; a root-resolution
   self-report does not enforce the path contract. Narrowing that reading is the operator's call, not
   mine (gap M1).

## B. The four questions

- **Coverage both ways: clean.** REQ-01 (T-01,T-08), REQ-02 (T-02,T-04,T-05,T-06,T-08), REQ-03
  (T-02,T-05,T-08), REQ-04 (T-03,T-07), REQ-05 (T-01). All 8 tasks trace to a REQ that exists. No orphan
  in either direction. SC-07 is carried by no task — correct, it is a no-change criterion.
- **SC-01..SC-09, individually.** 01 falsifiable but **non-discriminating**: it asserts an absolute
  existing directory, never that it differs from cwd, and in the test the two coincide (gap L3).
  02 first clause tested; the second, "no branch of the script exits non-zero", quantifies over the whole
  file with no stated assertion (greppable — the live script has zero `exit [1-9]`) (L1). 03 per-item, five
  separate assertions — the shape (i) attack fails, **but** the graded set is the checker's own
  `--list-scope`, i.e. derived from the artifact under grading, and T-03's five sites are not BRIEF's
  F1-F5 (harness-tdd-enforcement substituted) (L2). 04 per-site via `git show <review_sha>:` — good — but
  its whole-scope clause is a file-global command over a scope with a real hole (M2) and a rule with a
  real blind spot (H2), so it can be green while intent is unmet. 05 **the strongest SC in the set**:
  fixture, exit 1, named file AND line, summary count — the gate is shown red. 06 discriminating in both
  directions. 07 falsifiable (base-sha vs review-sha diff of write patterns). 08 shape (ii) failure: it
  asserts the step's TEXT is present in the `integration:` block; nothing establishes the JOB can report
  red (M3). 09 falsifiable via the DEC entry plus index row.
- **Scope.** Out-of-scope respected: no kaya-ai code, no write widening (D-05, T-05 step 2), #357 named
  as neither upstream nor downstream (BRIEF.md:58, T-08). Nothing the grilling settled is dropped —
  including the fifth family and the read-policy ruling it left open (D-05). T-06's 12-skill sweep is
  wider than the grilling's four families; it follows from REQ-02 and from #356's "found by looking, not
  by a check", so advisory, not creep.
- **The premise:** below.

## C. The premise — `sound with caveat`

Both wrinkles resolve, and a third does not.

- **Matcher gate: not a defect.** Resolved above (item 1). Every dispatchable agent is `harness-*`.
- **Empty-body drop: closed by T-01.** `emit` drops an empty body (inject-expertise.sh:58-62), but T-01
  step 2 (plan.yaml:116-118) emits the control-plane block FIRST and UNCONDITIONALLY, so the body is
  never empty for a matched agent, and T-01 step 5 case 1 asserts exactly the no-Expertise spawn. The
  conditional itself is left standing, correctly — it no longer has a reachable false branch.
- **The caveat, measured, and it is the finding: one root for two jobs.**
  `resolve_root` is script-directory-relative: the MAIN bin resolves to `/…/GitHub/harness`, the
  worktree bin resolves to `/…/worktrees/harness/FEAT-52-factory-control-plane`. The registered command
  is `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/inject-expertise.sh` (settings.json:12), and #322
  (via #356 comment 4) measured `CLAUDE_PROJECT_DIR` as the MAIN checkout even for a worktree agent — so
  the injected root is always the main checkout. `/…/GitHub/harness/.harness/harness/features/FEAT-52-factory-control-plane`
  is **ABSENT** (checked). T-02 (plan.yaml:183-184) and T-04 F3/F4 anchor the receipt and observations
  **write** paths to that root. Today they resolve against cwd and land correctly on the feature branch;
  after this plan they land in the main checkout, off-branch, invisible at `review_sha`. Nothing in
  REQ, D-01..D-05 or any task distinguishes "the control plane" from "the tree this feature is being
  built in".

## Gaps — 2 high, 3 med, 3 low

- **H1 high** — control-plane root conflated with the feature's own tree; anchored write families (F3, F4)
  break worktree-based development. Needs a REQ/D-NN ruling, not a task tweak.
- **H2 high** — T-03's rule (plan.yaml:216-218) matches only backtick-delimited spans, so it is blind to
  FENCED code blocks. `harness-expertise/SKILL.md:36-37` carries the F3 write path inside a ```bash
  block; T-04 hand-anchors it (plan.yaml:307-311) while the lint cannot protect it. REQ-04 unmet for
  that shape — the exact "this class returns" the grilling built the check for.
- **M1 med** — settled item 3's spawn-time half asserts root resolution, never the path contract.
- **M2 med** — declared scope omits `.claude/skills/harness/templates/*.md`; `templates/PLAN.md:9` and
  `templates/README.md:8-16` carry relative control-plane paths and reach harness-pm.
- **M3 med** — SC-08 proves wiring by reading YAML; the CI job is never shown able to report red.
- **L1 low** — SC-02's "no branch exits non-zero" has no stated assertion.
- **L2 low** — SC-03/04's "five canonical sites" ≠ BRIEF's F1-F5 enumeration.
- **L3 low** — SC-01 does not require the injected root to differ from cwd.

## Open questions for the operator

- **Q1 (blocking)** — H1: should the injected value be ONE root, or two (control-plane root for reads;
  feature-tree root for receipts/observations)? Until this is ruled, T-02/T-04's write anchoring is a
  regression for every harness self-development run.
- **Q2 (blocking)** — Item 3 / M1: does "spawn-time assertion" mean root resolution (as drafted), or an
  assertion over the path contract itself?
