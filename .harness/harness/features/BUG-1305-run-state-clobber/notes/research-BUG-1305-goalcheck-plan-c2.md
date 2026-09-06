# Goal-check — BUG-1305 plan, cycle 2 — does this plan deliver the operator's stated intent?

**Mostly, and not yet safely: the plan closes both modes the operator named and discloses its one
residual honestly, but T-09's new denial can refuse a legitimate write by the run that owns the
directory, and no requirement or criterion in this plan grades over-refusal — so that defect ships
green.**

**Disclosure, not disclaimer.** I authored `BRIEF.md` and `plan.yaml` and I am grading them. That is
a conflict the harness compensates for with the operator's signature and the adversarial panel; the
panel is the independent read. It does not soften a verdict below — the two findings I rate `high`
are gating, and I am the one raising them against my own artifact.

Graded fresh against the sources, not against `research-BUG-1305-goalcheck-plan-c1.md`: the grilling
note's Settled/Issue-specific-source rows (`.harness/notes/grilling-six-residual-bugs-2026-09-05.md`
:9, :21), `issue://1305` (body: a residual finding, B-11 is the content), and B-11 itself
(`.harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.md:87`
— two clobbered `state.yaml`s needing hand repair, plus one digest failing the lead digest contract).
Every verdict below was re-derived from `plan.yaml` and `BRIEF.md` as they stand after the cycle-2
amends; the c1 note was consulted only for which areas were touched.

## Findings

### F-01 · high · T-09's denial refuses the owning run when the run outlives its session

`_resolve_identity` (`harness_yaml.py:511-546`) resolves identity from the hook payload's
`session_id`, falling back to the transcript stem and two env vars. Identity is therefore a property
of the **session**, not of the **run**. T-09's denial fires when the marker's identity and the
write's identity are both resolvable and differ (plan.yaml T-09 §2), and its seven enumerated
fail-open rows (a–g) cover marker-absent, identity-null, unresolvable, equal, no-claim, OMP, and
non-discriminating runtime. **None covers the same run writing from a later session.**

Failure scenario: a cycle is interrupted — context exhausted, crash, the operator returns the next
morning — and `/harness` re-entry resumes it. The lead re-spawns, a fresh claim is recorded with
runtime `claude`, the checkpoint's `run_id`, `feature`, `squad` and `host` are unchanged, and the
write's identity is the new session's. Marker identity S1, write identity S2, both resolvable,
disagreeing, live claim non-OMP → **refused**. The run cannot update its own checkpoint, which is
precisely the durability B-11 asks for. D-01's `because` clause states the opposite as settled fact
("an absent, unresolvable or OMP-claimed signal can never refuse a legitimate resumed-session or OMP
child write") — true of those three signals, false of the resumed-session case, and it is inside the
text the operator signs.

Compounding it: T-04 asks one question — do two *different* concurrent runs carry different identity
values (plan.yaml T-04 method §3). It never asks whether one run carries a *stable* identity across
its own writes. So even a `discriminates: yes` answer does not establish the denial is safe to
enable, and `yes` is exactly the answer that enables it.

Only bites in the `discriminates: yes` branch; the no-op branch is unaffected.

### F-02 · high · No REQ and no SC grades a change that CLOSES a legitimate write

REQ-07 is one-directional: "No change made for either mode **opens** a write that the harness refuses
today", and SC-07 grades it by diffing assertions that existed at `c369fb1f` and by requiring both
suites green. A new refusal that is too broad removes no prior assertion and breaks no prior test, so
it passes SC-07 unseen; SC-01 grades that refusals *happen*, never that they are correctly bounded.
T-02's "same-run update exits 0" case and T-06's permitted-repair case pin two instances of
non-over-refusal by hand, which is exactly the evidence that no criterion generalises them.

Failure scenario: F-01 ships. Every gate is green, the goal-check passes, and the operator discovers
it the first time a resumed cycle is refused by the guard installed to protect it. This is the
structural reason F-01 is invisible, and it applies to any future tightening of these guards.

### F-03 · med · `inconclusive` is the near-certain outcome, and the BRIEF frames it as a coin flip

T-04 lists markers created after T-02 lands and refuses to manufacture runs or extrapolate
(plan.yaml T-04 §1, §4). At the point T-04 runs, the only markers in existence are those the build's
own worktree produced. `_visible` (`inflight_registry.py:252-259`) retains the session filter for
non-OMP claims because subagents in one Claude Code session share a session id — so under the
compatibility host two sibling runs driven from one session carry the *same* identity, and the
honest answer is `no` or `inconclusive` for the very runtime the residual is about.

Failure scenario: the operator reads REQ-01's "If it discriminates, the route is closed. If it does
not, the route remains open" as balanced, signs, and learns at ship that Mode A's **leading** route
(the diagnosis's own words, `notes/receipt-harness-dev-ops-diag-c1.md:52`) was never going to close.
Nothing here is false — the disclosure is real and SC-01's contingent clause grades the record — but
the framing understates which branch the evidence base points at.

### F-04 · med · A run directory that never acquires a marker is unprotected and unobservable

`record_seed` is best-effort and returns `False` without raising on any failure (T-01), and both
consumers treat marker-absent as "append nothing" (T-02 PRE, T-03 §marker absent). That is correct
for directories predating the mechanism. But nothing distinguishes "predates the mechanism" from
"the marker write failed" or "this checkpoint arrived by a route that never reaches POST", and no
task or criterion reports the difference.

Failure scenario: a run directory silently misses its marker; prevention never fires and detection
never reports; the operator believes the clobber protection covers a directory it does not, and
learns otherwise the way B-11 was learned — by noticing a record is gone.

### F-05 · low · SC-01's excluded-route anchor carries no sha

BRIEF SC-01 and REQ-01 cite `bash-write-guard.sh`'s `_run_artifact_guard (:744-767)` with no
observation sha, while every other pinned claim in the brief carries `c369fb1f`. No task touches that
file and nothing is graded on the anchor, so the cost is a reader sent to the wrong lines after an
unrelated edit — not a wrong verdict.

### F-06 · low · SC-08's leading clause is broader than its enumeration

"the repository prescribes exactly one run-directory slug grammar" is followed by an enumeration that
requires DEC-145's purpose-squad sentence to survive, superseded rather than rewritten. A reader
taking the leading clause literally finds `DECISIONS.md:3243` still prescribing the other form. The
enumeration resolves it, and the grammar corpus is small and now confirmed: at `c369fb1f` exactly two
sites prescribe purpose-squad (`.claude/skills/harness/SKILL.md:272`, `DECISIONS.md:3243`) and the
date-seq form appears in `harness-team/SKILL.md:45` and `SPEC.md:2123`, both already the surviving
grammar. T-07's `files:` covers every site that must change.

### F-07 · info · T-06 and T-09 edit the same two files with no ordering edge

Both touch `check-domain.sh` and `tests/integration/test-check-domain.py` in different regions, and
neither depends on the other. Both are `main-session-direct`, which serialises them by construction,
so this is a note rather than a risk.

## The Act-1 amends — did they do what they were meant to, and nothing else

Both applied under compare-and-swap, exit 0. `T-09.traces` is now `[REQ-01, REQ-07]`; `T-08.depends_on`
is now `[T-02, T-03, T-05, T-06, T-09]`; order preserved, one element added each.

They close the ordering gap on the merits. T-09 edits `check-domain.sh` and
`tests/integration/test-check-domain.py`, so its changes fall inside REQ-07's scope and now trace it;
and T-08 — the sole producer of the `notes/regression-delta-BUG-1305.md` that SC-07 is graded on —
can no longer be written before T-09's changes exist. The resulting chain
`T-01 → T-02 → T-04 → T-09 → T-08` is acyclic, and T-04 terminates unconditionally because its method
permits recording `inconclusive`. `check-plan-routes.py` exits 0 on the amended plan.

They introduce nothing. They do not, however, help F-01 or F-02: SC-07 grades removed and weakened
assertions, so an over-broad *new* refusal remains outside what the delta note can catch.

## The rest of the grade

**F-01's cycle-1 closure, on the merits.** In the `discriminates: yes` branch the equal-slug route is
genuinely closed: two runs sharing a slug share `run_id`, `feature`, `squad` and `host`, `conflict()`
returns None, and T-09's identity denial is the only thing that separates them — it fires, scoped to
the runtimes the T-04 table records. In the `no`/`inconclusive` branch the hole is disclosed, not
silent: T-04 records the consequence, T-09 §6 writes `disposition: not-executed` with the residual in
the operator's terms, SC-01's contingent clause makes that record a grading condition, and REQ-01
states it as the operator's ruling. **Can the denial fail to fire on two genuinely different runs
with resolvable, disagreeing signals?** Yes, in one case — neither directory holds a marker (F-04).
**Can it refuse a legitimate write?** Yes — F-01.

**SC determinism, all eight, re-derived.** No criterion anchors on a line number or a population
count. SC-01 (two enumerated routes plus a contingent clause with an explicit not-met condition),
SC-02, SC-04 and SC-05 each name the fixture and both halves of the expected outcome. SC-03 carries a
falsifiable wording rule and forbids reusing INV-16's shape wording. SC-06 is scoped to the digest
content guard, not to the file. SC-07 enumerates three explicit FAIL conditions and its full-suite
clause discharges the broader leading claim. SC-08 is pinned to the review sha. Only F-06 leaves room
for two readers to differ, and its enumeration resolves the difference.

**Chains, per mode.** Mode A: REQ-01 → T-01, T-02, T-04, T-09 → SC-01; REQ-02 → T-01, T-03 → SC-02;
REQ-03 → T-03 → SC-03. Mode B: REQ-04 → T-05 → SC-04; REQ-05 → T-06 → SC-05; REQ-06 → T-06 → SC-06.
Both: REQ-07 → T-02, T-05, T-06, T-08, T-09 → SC-07. Doctrine: REQ-08 → T-07 → SC-08. Every REQ has a
task; every task traces a REQ it can move (T-04 changes no code, but its recorded answer is T-09's
enabling condition and SC-01's contingent evidence). **Neither mode can be declared done while the
other is open** — SC-07 spans both and its only producer, T-08, now depends on tasks from both.

**D-08's premise re-checked at source:** `validate-digest.py --hook` is registered as the
`SubagentStop` hook with matcher `harness-.*` (`.claude/settings.json:69-78`), so REQ-04's "without
anyone invoking a checker by hand" rests on a registration that exists.

**Signature-blocking residue is visible and framed as choice, not fact.** The contingent Mode-A
residual (REQ-01's last bullet, SC-01's contingent clause), the DEC-145 partial supersession
(Constraints: "only your signature authorises that"; striking REQ-08 declines it), and the DEC-208
false-clause ruling (Constraints: amend in a separate authorised act, or knowingly leave it standing;
D-04 refuses to settle it) each reach a reader of `BRIEF.md` alone, each as an open choice. F-03 is
the one place the framing is weaker than the evidence.

## Fitness

- **Fit for the adversarial panel: yes.** It is coherent, fully specified, route-checked and
  internally traceable; the panel has something real to attack.
- **Fit for signature: no.** F-01 and F-02 are `high` and therefore gating. F-01 needs either an
  eighth fail-open row and a T-04 question about within-run identity stability, or D-01's safety
  clause corrected to state the exposure; F-02 needs REQ-07 or a criterion to cover over-refusal.
  F-03, F-04, F-05 and F-06 are not gating.

## Open questions

- **Q1 (blocking):** does the operator want F-01 closed by widening T-09's fail-open enumeration and
  T-04's measurement, or by narrowing D-01's claim and disclosing the exposure? Both are plan edits;
  neither is mine to choose.
- **Q2 (non-blocking):** should REQ-07 be made two-directional — no protection traded away *and* no
  legitimate write newly refused? That widens an approved requirement's scope.
