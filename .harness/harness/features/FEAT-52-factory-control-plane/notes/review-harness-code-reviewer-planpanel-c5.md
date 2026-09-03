# Plan-panel review — scope reader — FEAT-52 cycle 5 (plan-only, no `review_sha`, DEC-207 `code_grade: n_a`)

## PF-93ebe15db8b54c3a43adc1c2ad877278 — **CLOSED**, both halves, judged separately

**Rule half — CLOSED.** Traced token by token through the specified predicate against the exact
cycle-4 counterexample, `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json` written into
`harness-qa-gate/SKILL.md`:
- THE RULE (class 1, `plan.yaml:159-163`): satisfied — a placeholder immediately precedes the token.
- Class 2 (`:176-181`): does not apply — the anchor present is `HARNESS_FEATURE_TREE_ROOT`, not
  `HARNESS_CONTROL_PLANE_ROOT`, so class 2's own precondition never fires.
- **Class 3, the new mirror (`:190-197`): fires.** Remainder = `.harness/harness.json`. Apply the
  shared predicate `^\.harness/([^/]+/)?features/`: after `.harness/`, the next literal segment
  must be `features/` (zero-segment case) or `<one-segment>/features/`. `harness.json` is neither —
  no `features` segment anywhere in the remainder — so the predicate does **not** match, the
  remainder is **not** feature-directory-shaped, and class 3's condition (`FEATURE_TREE`-anchored
  AND not feature-shaped) is satisfied. `VIOLATION harness-qa-gate/SKILL.md:<line>: control-plane
  path anchored to the feature tree` fires. The exact defeat is caught.

**Carrier half — CLOSED.** T-15 (`plan.yaml:1054-1164`) is a real task, `depends_on: [T-12]`,
carrying exactly what SC-04 and SC-11 name and nothing T-01..T-14 implemented: seven named rows,
read via `git -C <root> show <ref>:<path>` (never the working tree), each with its own per-row RED
proof against a fixture string. I verified all seven rows' premises against the **current, on-disk,
pre-anchoring** file content in the worktree — every cited token literally exists today at the
location the row claims:

| Row | File | Token found at |
|---|---|---|
| 1 | `harness-qa-gate/SKILL.md` | `:45` (`.harness/harness.json`) |
| 2 | `harness-expertise/SKILL.md` | `:17` (`.harness/expertise/<your-agent-name>.md`) |
| 3 | `harness-handoff/SKILL.md` | receipt sentence (`.harness/harness/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`) |
| 4 | `.omp/agents/harness-backend-dev.md` | debugging-skill line (`.agents/skills/harness-systematic-debugging/SKILL.md`) |
| 5 | `templates/PLAN.md` | `:9` (`.harness/team-config.yaml`) |
| 6 | `harness-expertise/SKILL.md` | `:16`, table row (`.harness/harness/features/<FEAT>/observations/<your-agent-name>.md`) |
| 7 | `harness-expertise/SKILL.md` | `:37`, fenced `observations-merge.py --file` line — **confirmed a genuinely different span from row 6**, same file, different line, one prose one fenced |

Every one is unimplementable-as-written only if the anchoring tasks fail to preserve the exact
remainder text — which T-04's own intent (`:411-427`) independently cites the same two line numbers
(16 and 37) for F3, corroborating row 6/7's split from the other direction. Row-3's premise is
independently confirmed by T-08's intent (`:664-668`), which names the same "line 80" receipt
sentence as its own edit target. **Both halves of PF-93ebe15d are closed by the repair; nothing
reopens it.**

## Hunted items

**1. The widened predicate `^\.harness/([^/]+/)?features/`.**
- *Hole in class 2?* No. Widening only makes the predicate match **more** text (segment now
  optional instead of mandatory), so it can only add class-2 detections, never remove one — a
  feature-directory-shaped remainder that would have matched the old, stricter predicate still
  matches the new one. The old, mandatory-segment predicate is what had the hole (it let the
  zero-segment templates spelling escape class 2 entirely); the repair closes that, it does not open
  a new one for class 2.
  The theoretical risk runs the *other* way: a genuinely control-plane-only path whose text happened
  to contain a literal `<segment>/features/` component unrelated to the per-`FEAT` convention would
  now be *mis-flagged* by class 2 as feature-directory-shaped (a false positive, not an escape). I
  found no such site in the declared scope — every real `features/` directory component in this
  corpus is the genuine per-`FEAT` container. Recorded per Expertise P-15 as considered and
  dismissed, not a defect (**NF-4**, info).
- *Still satisfies SC-11's literal wording?* Yes. SC-11 names the one-segment spelling
  (`<HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/features/`) specifically; the widened predicate is
  a strict superset of the old one, so the one-segment case still matches and class 2 still fires on
  it. T-02's retained SECOND CLASS test cases and the new four-assertion SHARED PREDICATE case both
  exercise this literal spelling and assert exit 1. No narrowing occurred.
- *Occurrence counts, re-derived at `e8e1b78be3379d4a669aa7e28aef8f76eb942471` over the declared
  scope (62 files, `MAIN_SESSION_ONLY` excluded by path):* `.harness/harness/features/` **31**,
  `.harness/<repo>/features/` (literal) **4**, `.harness/<product>/features/` (literal) **1** — sum
  **36**, matching the plan exactly, confirmed by an independent single-regex sanity pass
  (`\.harness/[A-Za-z0-9_<>.-]+/features/` also returns 36). The unsegmented
  `.harness/features/` count is **9**, not the 11 the plan states — all nine in `templates/`
  (`README.md:11,13,14,15,16` = 5, `BRIEF.md:44` = 1, `STATE.md:1,17,25` = 3; `PLAN.md`, `DESIGN.md`,
  `HANDOFF.md`, `MAP.md` carry zero). This does not change the widening decision's correctness — even
  at 9, a mandatory-segment predicate would still falsely flag all nine correct T-07 spans — but it
  is a measured claim in the intent that is factually wrong (**NF-3**, low).

**2. T-15's seven rows — premises verified against on-disk content.** All seven check out (table
above). Rows 6 and 7 are confirmed as two distinct spans in one file, at lines 16 and 37
respectively — a prose table row and a fenced `observations-merge.py` invocation — matching T-04's
own citation of the same two line numbers for F3.

**3. Can T-15 go red — genuinely, in both directions?** **Partially, not fully — NF-1 (med).** The
spec's `direction_failures` must fail on two shapes: (a) no anchored occurrence found at all (token
vanished or never anchored), and (b) an occurrence found with the wrong anchor. The mandated RED
PROOF, however, only constructs a fixture for shape (b) — "taking that row's token and prefixing it
with the WRONG anchor" always produces exactly one match (the pattern matches either placeholder), so
every required red-proof fixture exercises only the wrong-anchor branch. No row's red proof ever
constructs a fixture with the token present-but-completely-unanchored, or absent altogether, to prove
shape (a) fires. Concrete scenario: an implementation of `direction_failures` whose "no occurrence"
branch is missing or inverted (e.g., an empty match list is read as vacuously fine rather than a
failure — the fail-open pattern this codebase's history repeats) passes every mandated test in
T-15, and passes on real content too as long as every token stays present-and-correctly-anchored. The
gap only surfaces the day a real reference is later deleted rather than mis-anchored — at which point
T-15's own row assertion silently reports zero failures on a real regression. This is exactly the "for
every absence assertion, what presence assertion sits beside it" question (DEC-169) applied to the
red-proof's own two claimed halves.

**4. The seam between T-02 (shape, whole-scope) and T-15 (site, 7 named spans) — NF-2 (med).** T-02's
mirror-pair is airtight for *misdirected* anchors: since shape is purely a function of the token's
own remainder text, any wrong-anchor-with-shape-mismatch is caught by class 2 or class 3 regardless
of which of the ~62 scope files it appears in — this is not limited to T-15's 7 rows. What neither
mechanism catches is **silent deletion of a required reference.** T-02 can only judge a token that is
present; it has no rule asserting a specific reference must continue to exist. T-15 covers existence
for exactly 7 spans. Every other Harness-owned path this plan touches — F1's other 7 sites
(`harness-verification-rules/SKILL.md`, `harness-tdd-enforcement/SKILL.md`, 5 agent files), F3/F4's
occurrences in every agent file besides `harness-expertise`/`harness-handoff`, and the bulk of T-06's
12 skills, T-07's other 6 templates plus README's 3 read rows, T-10/T-11's paths — has no existence
assertion at either the working tree (T-12) or the pinned tree (T-15). Concrete scenario: T-04's
mechanical sweep across ~20 files accidentally deletes, rather than anchors, the F1 sentence in
`harness-tdd-enforcement/SKILL.md:106` — T-02 sees zero matching tokens there, exits 0; T-12's
whole-scope run is clean; T-15 never names that file. The instruction silently vanishes — the exact
"missing read with no signal at all" severity class the BRIEF opens with — and nothing in this plan's
gates detects it. This is inherent to a shape-lint's design, not something the repair introduced, and
is only partially mitigated (for 7 sites) by T-15.

**5. Traceability and dependency shape, 15 tasks.** Every `traces:` id across all 15 tasks resolves
to REQ-01..REQ-06 in `BRIEF.md` — no dangling reference (checked every `traces:` line in the plan
dump). `depends_on` is a strict DAG in ascending task-id order, no forward reference, no cycle
(T-01/T-02 `[]`; T-03/04/06/07 `[T-02]`; T-05 `[T-02,T-04]`; T-08 `[T-01,T-02,T-03]`; T-09 `[T-01]`;
T-10 `[T-06,T-08,T-09]`; T-11 `[T-04,T-09]`; T-12 `[T-04,T-05,T-06,T-07,T-08,T-10,T-11]`; T-13/T-15
`[T-12]`; T-14 `[T-03]`). **`T-15: depends_on: [T-12]` is sufficient**: every task that actually
writes one of the seven cited spans — T-04 (rows 1, 2, 6, 7), T-05 (row 4), T-07 (row 5), T-08 (row
3) — is a **direct** member of T-12's own `depends_on` list, so standard DAG execution (T-12 cannot
run until all of its own dependencies have landed) transitively guarantees all four are complete
before T-12 runs, and therefore before T-15 runs. No finding here; the dependency is correctly scoped
and confirmed by the transitive closure, not merely asserted.

**6. Dead weight and altitude — is T-15 a task, or a test that belonged inside T-12?** **A task,
correctly.** T-12's own deliverable is CI *wiring* (a workflow step, plus a red-proven assertion that
the wiring itself can fail) verified against the *working tree*. T-15's deliverable is a *different*
file (`test-anchor-directions.py`), a *different* verification target (`git show <ref>`, the
*reviewed sha*, never the working tree — which SC-04 and SC-11 require by name), and a *different*
concern (per-site literal correctness vs. generic shape). Folding it into T-12 would smuggle a
significant new test file with 7 named assertions and its own pinned-tree whole-scope run into an
already large task, and would re-create exactly the auditability problem cycle-4's HIGH finding
exists to fix — a missing carrier is easiest to verify closed when its fix is its own nameable task.
Not dead weight; not a restatement (unlike PF-da16f6e1's T-11 finding, left open, not re-litigated
here).

## New findings

| id | severity | summary |
|---|---|---|
| NF-1 | med | T-15's mandated RED PROOF only exercises `direction_failures`'s "wrong anchor present" branch, never its "no occurrence found" branch — a fail-open bug in the latter ships undetected by every specified test, and only bites the day a real reference is deleted rather than mis-anchored. |
| NF-2 | med | The T-02/T-15 seam has no mechanism, at either the working tree or the pinned tree, to detect silent deletion of any of the ~30+ required Harness-owned path references outside T-15's 7 named spans — a shape-lint can only judge a token that is present. |
| NF-3 | low | T-02's intent claims the unsegmented `.harness/features/` spelling occurs 11 times at the pinned sha; re-derived, it is 9 (all in `templates/`). Does not change the widening decision. |
| NF-4 | info | The widened predicate's optional segment could theoretically over-flag a control-plane path whose real name happens to contain a `<segment>/features/` component; no such site exists in the current scope — considered, dismissed, recorded per P-15. |

## Not re-raised

The seven surviving cycle-4 findings (PF-4ea5b566/med, PF-da16f6e1/med, PF-afe3e3d6/low,
PF-8653185d/low, three info judgements on D-06/D-07/D-08) stand as `disposition: open` for the
batched signature review; none appears wrong on re-reading, none re-litigated. The absent `approval:`
mapping is the known, separately-routed blocker, not a panel finding.
