# Goal-check — FEAT-56 revised plan vs the operator's re-scope (plan phase, cycle 1)

**BLUF — does this plan deliver the operator's stated intent? NO, on two of the seven
instructions.** The split, the new skill, the BRIEF/approval/design eviction and the door port are all
traced and specified. But **the cut leaves `harness-init` unable to do the one job the operator
isolated it to** — the only instruction that instantiates the control plane's own `.harness/harness.json`
and `.harness/team-config.yaml` sits at `harness-init/SKILL.md:279-282`, inside the `:245-283` block
T-10 moves into `harness-add-repo` and T-11 deletes — and **"actually reachable through OMP" has no
criterion of any method.** Graded against `notes/answers-rescope-2026-09-08.md` (governing), plan and
BRIEF as read today, worktree tip.

## Trace table — one row per instruction in the answers file

| # | Instruction | Discharged by | Grade |
|---|---|---|---|
| 1 | Revise #206 in place; no narrowed FEAT-56, no successor | D-07; BRIEF Non-goals "Creating a successor feature…"; T-01..T-08 stay `done` | DELIVERED |
| 2 | Provider-neutral SKILL `harness-add-repo` for adding a repo to a configured fleet | REQ-07, D-10, T-09, T-10; SC-01, SC-12 | DELIVERED |
| 3 | The OMP command-door port **in this same feature**, so the surface is *actually reachable through OMP* | REQ-09, REQ-10, D-11, T-13, T-14; SC-13 | **PARTIAL** |
| 4 | First-BRIEF, approval, design leave onboarding; a BRIEF-less fleet repo routes to `/harness-plan` | REQ-08, D-09; T-10 (drops steps 6–8), T-11, T-12, T-15, T-16, T-17; SC-14 | DELIVERED |
| 5 | `harness-init` isolated to first-time configuration of a fresh Harness checkout | REQ-01, REQ-02, T-11; SC-11 | **MISSING** |
| 6 | `harness-add-repo` registers a repository into the configured control plane | REQ-07, T-10, D-04; SC-01, SC-12 | **PARTIAL** |
| 7 | The OMP surface works with Claude Code, OpenAI and other providers **through OMP** | REQ-09, D-11, T-13/T-14; T-10's `! grep 'claude --version'` | **PARTIAL** |

**Consequences.**
- **Row 5 (MISSING).** T-11 KEEPs only preflight, step 1, step 5, step 9, `--upgrade`, and deletes
  `:239-418` whole. That range holds (a) `:279-282`, the sole "for the control plane itself,
  instantiate its own `.harness/harness.json` and `.harness/team-config.yaml`" instruction, (b) the
  technical interview `:284-291` and (c) dev-ops detection `:292-323`, whose report surviving step 5
  still demands (`:163-164` "the real path from dev-ops's report") and whose `test_kinds` write
  targets *the control plane's own harness.json*. T-15's own intent asserts detection "lives … in
  `harness-init` for this control plane's own `harness.json`" — **no task puts it there.** So an
  operator following the cut skill installs the eight prerequisites, is told to seed `# SEED` globs in
  a manifest that was never instantiated, and reaches step 9 where `check-state.sh` cannot exit 0 on a
  checkout with no `.harness/harness.json`. Nothing catches it: T-11's verify is all absence-of-Track-B
  greps plus the two hooks strings; it never greps `dev-ops`, `harness.json` or `team-config`.
- **Row 6 (PARTIAL).** Because T-10 moves `:245-283` verbatim, that same `:279-282` sentence lands
  *inside the registration skill*, and T-10's ban is `! grep -qF 'templates/team-config.yaml'`, which
  the sentence's wording ("from the templates") does not match. T-10 also inherits the "I'll copy the
  new team-config over theirs" Red-flags row. Consequence: an operator registering `kaya-web` is told
  to instantiate a `team-config.yaml` — the exact one-file-rule violation this feature exists to stop —
  and SC-01's ban plus T-17's split test both look elsewhere.
- **Row 3 / Row 7 (PARTIAL).** See Q1 and Q7 below. Row 7 additionally: `harness-init`'s preflight keeps
  `claude --version` and the "CLI < 2.1.217 → Stop" bullet (`SKILL.md:34, :40`). No task removes it, so
  an operator standing up a fresh control plane under OMP/OpenAI hits a hard STOP for a CLI they need
  not have — a Claude-Code-only path surviving in the artifact the operator isolated.

**Cycle-0 rows this revision reopens:** c0's PARTIAL S3 (interview re-homes) and S5 (step 5 narrowed)
and its Q2 answer "all six destinations are stated" — the split removes the interview's and detection's
`harness-init` destination without restating them. c0's D2 (#203) and D3 (#168) stay closed: BRIEF
Constraints carries #203, and T-12's verify reloads `templates/team-config.yaml`.

## The six questions

**1. The reachability claim.** Honest grading: the file-existence clause would **not** have passed
while today's defect was live. `.omp/commands/` does not exist at the tip (only `.claude/commands/`
carries the four doors) and `.omp/config.yml:2-3` sets `disabledProviders: [claude]`;
`.omp/extensions/harness-hooks.ts` registers no slash command. SC-13 clause 2 fails today, and T-14's
generator treats an orphan `.claude/commands/harness*.md` as an ERROR — today's exact state. So the
criterion **can** see today's bug. Clauses 3 and 4 close a *different* gap (a checker that looks at
nothing / a `check-omp-port.py` left unedited) and are worth keeping. What none of the four clauses can
see is a **wrong canonical root**: if OMP does not read `.omp/commands`, every clause is green, the
checker is green, and `/harness-plan` still falls through as prompt text — the same silent, symptomless
failure being fixed, now recorded as REQ-09 met. The whole basis is one documentation read
(`omp://config-usage.md`, cited in D-11) and no criterion, not even a `uat` one, requires the observation.
*Disposition: PARTIAL — add one clause to SC-12 (or a third `uat` criterion): the operator opens an OMP
session and confirms `/harness-plan` resolves from `.omp/commands/`; it is the only method that can see
a wrong root.*

**2. Nothing retained.** SC-05 is the only one of the five genuinely untouched — no T-09..T-17 `files:`
list names `factory_config.py` or `test-fleet-product-config.py`. The other four all have their subject
rewritten by a new task: **SC-02**'s blob by T-11 (which renumbers around the two hooks commands),
**SC-10**'s file by T-12 (comment header), **SC-06**'s unit suite by T-17 (`test-no-distribution.py`),
**SC-07**'s integration suite by T-14 and T-17 (two new files). Each per-SC paragraph does say
"regression check"/"standing gate", but the section preamble (`BRIEF.md:143-147`) says the five are
"already met" and "this revision does NOT re-prove them" — and the preamble is the sentence a later
goal-check reads. *Disposition: PARTIAL — the preamble must exempt SC-02, SC-06, SC-07 and SC-10 and
require each to be re-taken at `<review_sha>`; as written it licenses carrying a `12f74ea8` grade onto a
blob T-11 rewrote, which is a retained grade under another name.*

**3. The split hole.** Not preserved. Two hazards are clean: the **Red flags** table is fully
partitioned (6 rows to T-10, 4 to T-11, 2 dropped by D-09 = all 12 at `:423-434`), and the
**`--upgrade` cross-reference** `:212` is explicitly re-pointed at the new skill. The **preflight** is
kept by T-11 and re-authored for T-10, no duplication — but keeps `claude --version` (Q7). **Step
numbering** is handled, seven dangling sites named. Orphaned: `:279-282` (control-plane instantiation),
`:284-291` (technical interview), `:292-323` (dev-ops detection) as far as `harness-init` is concerned,
plus `:163-164`'s reference to a report no surviving step produces — not in T-11's seven-site list.
Duplicated: the "interview IS a grilling" note `:25-28`, which T-10 keeps and T-11 leaves unstated; its
second clause is control-plane-only, so the copy in `harness-add-repo` carries a clause about the wrong
repository. *Disposition: FAIL — T-11 needs an explicit KEEP for control-plane instantiation, the
technical interview and dev-ops detection scoped to this checkout, and its verify needs a positive grep
for each; T-10 needs `:279-282` struck from what moves in.*

**4. Dependency shape.** Five of nine new tasks are `main-session-direct` (T-10, T-11, T-12, T-13,
T-15), not six. Real edges: T-09→T-10 (the anchor gate reddens the moment the skill exists),
T-12→T-13 (T-13 byte-copies T-12's corrected door text), T-13→T-14 (the checker runs `--check` against
the real adapters). Serialization by habit: **T-12, T-15 and T-16 all depend on T-11 but need only
T-10** — none of their verifies or file lists reads `harness-init/SKILL.md`; each needs the *name*
`harness-add-repo` to exist, which is T-10. T-11 therefore blocks three tasks it does not gate.
T-17's `[T-13, T-15]` is sound because T-11 and T-12 are transitive ancestors through T-13.
*Disposition: advisory — re-point T-12, T-15 and T-16 at `depends_on: [T-10]`; T-15 and T-16 then run
in parallel with the T-11→T-12→T-13→T-14 chain.*

**5. Coverage arithmetic.** No orphans in either direction. REQ-01→T-01,T-11; REQ-02→T-01,T-11;
REQ-03→T-02,T-12; REQ-04→T-05..T-08,T-12,T-15,T-16; REQ-05→T-01,T-04; REQ-06→T-03,T-17;
REQ-07→T-09,T-10; REQ-08→T-10,T-11,T-12,T-15,T-16,T-17; REQ-09→T-13,T-14,T-16; REQ-10→T-14. Every
T-09..T-17 traces ≥1 REQ. Every SC is reachable: SC-01→T-10; SC-02→T-11; SC-03→T-02+T-09;
SC-04→T-12,T-15,T-16 (+T-05..T-08); SC-05→T-04; SC-06/07→suites; SC-08→T-09+T-14; SC-10→T-12;
SC-11→T-11; SC-12→T-10; SC-13→T-13,T-14; SC-14→T-17. Both `automated` kinds are ACTIVE in
`.harness/harness.json`: `unit` — `.agents/skills/harness/bin/run-unit-tests.sh --kind unit`
(`:284-289`); `integration` — the same script `--kind integration` (`:319-324`). No SC rests on a null
kind (`component`, `ui`, `typecheck` unresolved; `functional`, `eval` excluded). *Disposition: PASS,
with one advisory the BRIEF already discloses — SC-01, SC-02, SC-10 and SC-13's first two clauses are
labelled `evidence: integration` while their assertions live in task `verify:` blocks, not under
`tests/integration/`, so running the integration kind does not grade them.*

**6. The two UAT criteria.** Genuinely distinct: SC-11 grades fresh-checkout fitness by reading, SC-12
grades registration by *following* the procedure for one real candidate up to the fleet entry, including
its preflight and D-04's order. Against the three prior failures — **structure** (one 434-line skill
doing two jobs) and **scope** (BRIEF, approval, design inside onboarding) are both caught: SC-11's
"every step is about the checkout in front of them / nothing asks them to register a repository, write
a BRIEF, take an approval or run a design pass" is exactly that test. **The jargon failure they MISS.**
The recorded FAIL was comprehension — "'control-plane clone' is ambiguous" (`notes/uat-FEAT-56.md:80,
:85`) and, at U-01, "it is not clear why reversing it is dangerous" (`:45`) — and every confirmation in
SC-11 and SC-12 is a presence/absence question, none asking whether a term was understood or whether the
operator knows *why* a rule holds. SC-11 is also a read, so it cannot surface row 5's missing step: a
procedure that never mentions instantiating `harness.json` reads as coherent. *Disposition: PARTIAL —
each of SC-11/SC-12 needs one comprehension clause ("name any term you could not resolve without
asking; state why the config-first order matters"), and SC-11's script should have the operator run
step 1 and step 2 against the scratch clone rather than read them.*

## Open questions

- **Q1 (blocking, operator/eng-lead):** row 5's hole is a plan defect, not a build defect — does T-11
  gain the three KEEPs, or does a new task own the control plane's own configuration steps?
- **Q2 (non-blocking):** carried from replan Q2 — no gate can prove provider discovery. Recommendation
  above is a `uat` clause; the operator decides whether that is sufficient for REQ-09.
