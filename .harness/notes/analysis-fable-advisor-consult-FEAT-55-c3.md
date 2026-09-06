# Advisor consult — FEAT-55 — unresolved questions before the operator's batched signature

**Path note.** The dispatch named
`.harness/harness/features/FEAT-55-issue-types-created-work/notes/review-fable-advisor-consult-c3.md`.
`check-domain.sh` refuses that path to `harness-validator-lead` (a lead's grants are
`runs/*-validator/**`, its own expertise/observations, and `.harness/notes/analysis-*.md`), so this
note lives at the durable path I do own. `runs/**` was rejected as the alternative because run
digests are gitignored in this repository and would not survive the worktree.

**Persona: `fable-advisor` (the same external reader that served as the cycle-3 plan panel's
`should-not-exist` step). It RESOLVED — it was not skipped, and no substitute answered.**
Read-only, no write grant; this note is the validator lead's transcription of its return
(`agent://FinalizeIssueTypesPlan.AdvisorConsult.AdvisorC3`, transcript
`history://FinalizeIssueTypesPlan.AdvisorConsult.AdvisorC3`).

**Nothing in this note resolves, accepts or waives anything.** Every item is a recommendation to the
operator, who rules. No plan edit was made by this consult (DEC-176).

**Advisor headline.** *F1 HOLDS on every premise (verified at source), but its consequence is milder
than the `high` grade implies; the cheapest binding remedy is re-specifying the three existing
`partial` cases' fixtures, not adding cases.*

---

## Q1 — F1 (BLOCKING)

**Premise verdict: HOLDS.** Re-derived at source by the advisor, and independently re-measured by
the lead before dispatch:

- `FAKE_TYPES=partial` is a test case at exactly three sites — T-03 F (`plan.yaml:532`), T-05 G
  (`:786`), T-07 I (`:970`); other occurrences are fixture-shape text (`:490`, `:737`, `:904`) or
  whole-file required-string loops (`:470`, `:724`, `:887`).
- All three specify fresh state: `:532` "fresh fixture", `:787` "fresh feature directory",
  `:971` "fresh fixture".
- The backfill set is "every already-recorded key whose recorded provenance value is the string
  `created`" — T-04 §4 `:623-626`, T-08 §6 `:1037-1040`; on the backlog route T-06 §5 `:848-860`
  backfills `typed:false` receipt entries. All empty by construction on a fresh fixture.
- The dissolution condition the panel itself named does not fire: no `partial` case pre-records a
  remnant. The only remnant-producing case, T-03 G (`:540`), runs under `available`.
- Advisor addition: on a fresh fixture the new clause is also subsumed by the pre-existing
  zero-`issue create` assertion, since a node id can only come from a create.

**Advisor disagrees with the panel on CONSEQUENCE, not premise.** Both panel readers graded `high`
citing "mutates a real existing issue's native type". The advisor's re-derivation: a backfill-first
bug applies the *intended, declared* type to a *Harness-created* issue on a run that then refuses,
and the receipt ends consistent; if the remnant's own type is the undeclared one, resolution fails
before any apply. The irreversible class — typing an adopted or foreign issue — is bound by
provenance rules that *are* tested with seeded fixtures (T-03 H/H2/J `:545-563`, T-07 F/H). What F1
actually leaves untested is ordering discipline on refusing runs, confined to Harness's own issues,
plus the false sentence at `:539` ("this case is what fails when it does") entering a signed record.

**Recommendation — fix, by the CHEAP remedy, not the panel's.** Re-specify T-03 F / T-05 G / T-07 I
from fresh to pre-seeded with one remnant whose type IS declared under `partial` (open/factory:
number + `typed: "created"`; backlog: a `backlog-issues.json` entry with `typed:false`), plus one
assertion per case that the remnant is unchanged afterwards. A backfill-first implementation then
emits `updateIssue` and the existing zero-`updateIssue` assertion reddens — falsifiable exactly
where it already sits. Cost: **zero** CASE-marker-loop and **zero** required-string-loop edits,
against the panel's three new cases plus six loop edits. Two forced wording changes: T-05 G's "no
`backlog-issues.json` afterwards" (`:790-792`) → "receipt byte-identical to the seeded content"
(proves strictly more); T-07 I's "records no parent number and no task issue number" (`:977-978`) →
"exactly the seeded entry and nothing else". Given up: the pure-fresh `partial` permutation (whose
recorded-skip branch is already covered by cases D/H2) and single-purpose case clarity.
**All three routes are needed** — required-set construction and backfill ordering are per-caller
glue (T-04 §4, T-06 §5, T-08 §6/§8), not shared-module code under D-11, and the operator's own
ruling already rejected open-route-only red-green for REQ-07 refusal (`:794-796`, `:981-984`).

**Consequence of the alternative (`accepted-untested`).** Defensible, advised against. An
implementer who structures the loop backfill-then-check ships green; exposure is a crashed-mid-typing
directory rerun against a repo missing a needed type, applying correct types to Harness's own issues
before exiting 2 — confusing, reversible, discovered when the operator sees typing side effects from
a run that printed a refusal. Modest harm, cheap fix. If the operator does rule accepted-untested,
`:539`'s sentence is untrue as written and should at least be named in the ruling.

## Q2 — T-10 §6's two SKIP wordings

**Recommend: delete the third bullet (`:1193-1196`), fold it into the second** — one wording,
`SKIP capability query failed on <target> (<message>)`. The fold removes a latent *contradiction*,
not merely an ambiguity: T-01 assertion 7 pins a NOT_FOUND errors array to `query_failed`, which
bullet two already renders, while bullet three claims not-found for itself. gh's own error text
survives inside `<message>`, so diagnostics are retained.
**Alternative (pin a rule):** the only coherent rule is a per-host `gh auth status --hostname`
pre-probe → "cannot reach", any `classify_capability` `query_failed` → "query failed"; consequence
is extra detection machinery and a permanently unverified branch maintained to vary one human-read
word. **Leaving as-is:** two implementers reasonably diverge on a fully-specified contract.

## Q3 — N5's two residues

**(a) Local overrides applied to a foreign TARGET (`:1197-1199`) — benign; recommend accept.** It
does not re-create the removed shape: the equality requirement constrained *where* the probe writes;
this constrains *what* it applies, and it fails safe (missing type → SKIP + `refusal_text`, nothing
created, `:1199-1201`). It is arguably the point — the probe validates *this* project's configured
type. Consequence of accepting: with an exotic local override and a vanilla scratch TARGET the live
gate SKIPs and SC-10's live verdict needs the type declared in the scratch repo — a vacuous-probe
risk the SKIP line itself explains, since `refusal_text` names the type. Consequence of "fixing"
(resolve from the TARGET's declared set): the probe stops testing the configuration in use, gutting
its purpose.

**(b) §1's configured-repo gate fronting the opt-in (`:1157-1160`) — a genuine partial residue;
recommend accept for this signature and record it.** `github.sync:false` or an unpinned repo kills a
`--create-in` aimed at an unrelated TARGET although neither bears on that write's safety — a fragment
of the coupling the `allow` ruling (`notes/answers-plan-panel-20260904-c2.md`) paid to remove. Moot
in this project (repo pinned, sync on) and fails in the safe direction. If the operator orders the
Q1 fix, folding in a one-line "with `--create-in`, step 1 requires only `gh` on PATH" is nearly free.
Consequence of accepting permanently: in a sync-off project the opt-in exits 0 with a SKIP an invoker
may misread as a soft pass — discovered at first use, no data harm.

## Q4 — the six carried findings (recommendations only; none dispositioned)

| id | advisor recommendation | consequence of accepting |
|---|---|---|
| `PF-1286544c197d1b0eb4a9b0dc8e1234dc` | **fix now** — one sentence pointing T-06 §5 (`:860`) at the locked atomic writer already in `gh-sync.py`. Highest consequence-per-fix-cost of the six | a crash mid-write truncates the receipt, the rerun re-creates every backlog issue — the duplicates REQ-08 forbids, in a live repo, cleaned by hand |
| `PF-0c12a033f69bb6bc60b8f96134f94fd0` | **accept (keep the marker)** — the advisor's OWN earlier finding; it now judges it not worth the operator's attention. Inertness is real, but the consumer is human receipt audit plus case H2's positive-record argument (`:949-951`); unwinding costs a signed SC, two decisions and three cases | a third receipt vocabulary value maintained forever; benign |
| `PF-56a2ce7a053111a3aff62a4b97c5902e` | **rule jointly with `PF-0c12a033` in one breath**; if the marker stays it dissolves at zero cost | ruling them separately risks an inconsistent pair that forces a signed-SC rewrite later |
| `PF-452948136bf467869d223e027191ae49` | **fix if any edit batch is ordered** (one added `verify` line), otherwise accept | a `cmd_open` regression introduced while rewiring `main()` rides green through T-06's gate; caught only at the feature-level suite — a later, costlier debugging loop, not a shipped defect |
| `PF-e27f1c3018b6b8477547a1b028607f96` | **accept** — the "three MORE issue create" tripwire is defensible; it proves compat behaviour was preserved exactly | a future duplicate-fix feature must find and delete a green test asserting the old behaviour — visible, cheap. Fixing it instead loses the proof this feature changed nothing on the compat path |
| `PF-9a71cb9a0c590b06b890ff1517b80385` | **defer to backlog** — also the advisor's own finding; it withdraws its claim on this signature's attention, since post-gate drift protection is outside this feature's power | lockstep 511-char edits across two files on any reword; post-gate drift silent. `[unverified]` — the 511 count and the `:1265`/`:1312` anchors remain the goal-check's measurement, not re-measured here |

## Q5 — do the two harness defects change what the operator should decide?

**No. Recommend signing against the `2026-09-04-19-validator` digest without discounting it.** The
advisor verified rather than asserted: it compared the `should-not-exist` reader's full return
(`agent://FinalizeIssueTypesPlan.PlanPanelC3.ShouldNotExist` — the one return with no disk note of
its own, hence the one at risk) against the consolidated digest and found all nine findings present
with severities verbatim (F1 high; N4/N5 low; N2/N6 info; four corroborations med/low/low/info),
including the F1 subsumption addition and the no-REQ addition to `PF-9a71cb9a`. The scope reader has
an independent disk anchor that matches. Defect (a) degraded **transport**, not content, and the
content is verifiable at both endpoints. Defect (b) produced an explicit roll-call in
`adequacy_notes` and a transparently explained second run directory, with `-18`'s `state.yaml` named
as checkpoint of record. Both remain real harness defects worth their upward report; neither is a
FEAT-55 signal. **Consequence of the alternative** (treating the record as suspect and re-running the
panel): a full cycle spent reproducing a demonstrably faithful record, plus the precedent that any
validator bug voids a panel's work even when every finding is independently anchored.

---

**Still open, for the operator alone:** F1's disposition (fix cheap / fix per panel /
accepted-untested), Q2, Q3(a), Q3(b), and all six carried `PF-` ids. Nothing above moves any of them.
