# Goal-check c1 — BUG-201 revised plan vs the operator's stated intent (plan panel, step 1)

**does this plan deliver the operator's stated intent?**

**Yes.** Graded against the grilling (`.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
`Settled` + `Out of scope`) and the operator's Q-A ruling (`notes/answers-plan-c0.md`), not the BRIEF.
The destination sentence is delivered on both routes (write: T-02/T-03; read: every `load_plan`
consumer), the Q-A widening is delivered at all three swallow sites (REQ-05, D-05, T-05→T-06), and
valid plans are proven unchanged by their own suites (SC-06/SC-07) rather than asserted. Three c1
defects I found are repaired below; after them every SC-01..SC-09 is `met`. Nothing is left `partial`.

## The ten c0 findings — c1 disposition, evidence on disk

| id | c1 disposition | evidence at HEAD |
|---|---|---|
| PF-d26198 (Q-A) | **delivered** | operator ruling `notes/answers-plan-c0.md`; `BRIEF.md` REQ-05 names all three sites, SC-08/SC-09 pin them, `plan.yaml` D-05 + T-05 + T-06 |
| PF-6dda61 (SC-02) | **repaired** | `BRIEF.md` SC-02: "exits with status EXACTLY 5 … `ILLEGAL PLAN` and `T-99` … sha256 unchanged … AND the paired allow … Exit 9 … does not satisfy". Matches T-02 (a)+(b) |
| PF-cc2bcf (SC-05) | **repaired** | SC-05 now requires import + reaching cases, paired-allows PASS in the same run, and enumerates the FAIL set (cases 1,3,5,6c). Import/fixture error excluded explicitly |
| PF-e9eff4 (REQ-04 2nd half) | **repaired** | T-03 `verify:` is eight suites (lines 301-308), T-06 the same eight (459-467); SC-06 (3 unit) and SC-07 (4 integration) bind them, split by `evidence:` kind |
| PF-4e8683 (D-03 lane) | **repaired, then SETTLED by ruling** | D-03 `because` cites the "The enforcement layer, enumerated:" paragraph and the `check-domain.sh --resolve` reading; advisor 2026-09-07 ruled T-03/T-06 stay `team` |
| PF-4f9180 (exit-2 surface) | **unchanged-deliberately** | info; exit 2 from `check-plan-routes.py` already stops consumption pre-signature and its stderr interpolates the exception. No artifact change was needed and none was made |
| PF-092cbd (self-dep sentence) | **repaired** | T-03 intent 342-345: "NON-NORMATIVE NOTE … NOT a behaviour to implement … Write no branch, no special case and no test for it" |
| PF-7beea1 (SC-03 count) | **repaired** | SC-03 is a floor with provenance (67 committed at `af859ee8`, 68 in this worktree); agrees with T-04's "AT LEAST 67". Re-measured today: 68 files, 0 dangling |
| PF-3116cd (T-01 case 6) | **repaired** | T-01 case 6 is three mixed-type sub-assertions (int ids + string entry, the mirror, int ids + `[3]` rejected) and names the one-side-coercion variant it catches (235-247) |
| PF-e159de (non-list widening) | **unchanged in plan, strengthened in BRIEF** | it was recorded only in T-01 case 5 / T-03; the operator reads BRIEF, so I added the disclosure there (`## Constraints`, "ONE DECLARED WIDENING"), with the exposure I measured: 0 of 68 |

## SC grades — as a specification, one line each

| SC | grade | why its literal wording discriminates |
|---|---|---|
| SC-01 | met | names both ids; deny-everything is excluded by SC-03/SC-06/SC-07 on the read route |
| SC-02 | met | exit EXACTLY 5 + `ILLEGAL PLAN` + `T-99` + sha256 unchanged + paired allow at 0; exit 9 excluded |
| SC-03 | met | invariant + floor-with-provenance; a zero-match walk fails, a grown corpus does not. Verified: 68/0/0 |
| SC-04 | met | inspection of the reviewed tree for one implementation; reachable via D-01 and T-03's "touch NO other file" |
| SC-05 | met | pre-rule run must import, paired-allows must pass, FAIL set enumerated exactly. **Repaired**: the set was glossed as "the dangling-reference cases", which excludes case 5 (non-list); the gloss is gone |
| SC-06 | met | three named `unit` suites must pass AND be named in T-03 and T-06's `verify:` — checked literally, all three appear in both blocks. A crash-everywhere build reddens them |
| SC-07 | met | four named `integration` suites, same terms — all four appear in T-03's block and in T-06's. Verified name by name |
| SC-08 | met | both ids present, "no plan could be read" absent (that string is real: `factory_claim.py:190`,`:194`), returns rather than raises, poll continues, paired legal case |
| SC-09 | met **after repair** | as written, its `_projected_for` clause was greenable by the `_status_plan_doc` fix alone: `status Ready` exits 2 from its own approval guard (`gh-sync.py:1306-1307`) and T-06's new stderr line carries both ids. **Repaired** in BRIEF and in T-05 case d: the invocation is `start-task <fixture> T-NN` with a board, which under an unrepaired `_projected_for` prints "no station follows from the plan" and exits **0** |

Reachability of that invocation was checked, not assumed: `_projected_for` is called at `gh-sync.py:302`,
`:1246`, `:1336`; `start-task`'s prior plan write does **not** refuse a dangling base
(`plan-merge.py cmd_set_task_station` validates only the station name, 908-941), and
`tests/integration/test-gh-sync.py:1514-1537` already stages exactly this shape.

## Tracing, DAG, verify existence, scope

- **REQ → task:** REQ-01 T-01,T-03 · REQ-02 T-01,T-03 · REQ-03 T-02,T-03 · REQ-04 T-03,T-04,T-06 ·
  REQ-05 T-05,T-06. **Task → REQ:** every `traces:` names an existing REQ; no orphan, no dangling REQ.
  Every task carries `change_type: bugfix` and `execution_mode: team`.
- **DAG, read from the loaded document:** T-01 [] · T-02 [] · T-03 [T-01,T-02] · T-04 [T-03] ·
  T-05 [T-03] · T-06 [T-05]. Topological, no dangling edge. `check-plan-routes.py` over this plan
  after my write: `OK T-01`…`OK T-06`, `0 violation(s) across 1 plan(s)`, exit 0.
- **Every `verify:` command exists:** the seven existing suites are on disk; the only absent file,
  `tests/unit/test-plan-depends-on.py`, is created by T-01, which precedes every task naming it.
- **Scope, both ways:** no task validates self-dependencies, cycles or ordering (T-01 249-250,
  T-03 339-345, T-05 tail); nothing in `Settled` is missing. The one widening (non-list `depends_on`)
  is now declared where the operator signs.
- **REQ-05 / D-05 vs the operator's words:** all three sites, no site dropped, no degradation left —
  and no new gate: `_status_plan_doc` keeps its exit and flow, `factory_claim` keeps returning None
  and keeps blocking the same candidates, correct plans take today's path. Anchors re-derived at HEAD;
  two in the BRIEF were wrong and are fixed (see writes).

## Writes — verb and receipt

1. `plan-merge.py amend --key tasks --id T-05 --field intent --expect-sha256 e747036…` (sha from
   `--show`) → `AMENDED tasks:T-05.intent` / `APPLIED …/plan.yaml`, exit 0. Case d now names
   `start-task` and forbids `status Ready` for that case.
2. `Edit` on `BRIEF.md` (my section, not `## Approval`): REQ-05 anchors corrected —
   `_blocker_reason_text` `:190-198`→`:193-196`, `_status_plan_doc` `:1265-1267`→`:1263-1266`
   (re-read at HEAD; the plan already had them right) — and SC-09 rewritten with the named invocation.
3. `Edit` on `BRIEF.md`: `## Constraints` gains the non-list widening disclosure with the measured
   exposure (0 of 68); SC-05's "dangling-reference cases" gloss dropped.

No other file was touched by those three writes. Nothing under `runs/`, no product code, no test file
— and the same holds for the c1 panel repairs below.

Writes added after the c1 panel (see the section below): `amend --key tasks --id T-03 --field verify`
and the same for `T-06`, both `AMENDED tasks:T-0N.verify` / `APPLIED …/plan.yaml` at exit 0;
`set-panel --value-file` → `PANEL cycle 1 -> …/plan.yaml` / `APPLIED …/plan.yaml` at exit 0; two
`Edit`s on `BRIEF.md` (SC-04, SC-07 — not `## Approval`).

## c1 panel repairs — after the 2026-09-07-02 panel, before signature

**The panel's two cheap findings are repaired in the specification itself; no new task, no scope
change.** Nothing else a reader graded was touched.

**V-1 (`med`, `should-not-exist`) — REQ-04's second-half proof bound four of six consumers.**
`PF-e9eff4`'s own text enumerated four consumers and the c1 repair bound three; `check-state.sh:140`
was a fourth unbound consumer neither had named. Three edits:

1. `BRIEF.md` SC-07 now names six integration suites, adding
   `tests/integration/test-factory-decompose.py` and `tests/integration/test-check-state.py`, on its
   existing terms (each passes after the change AND each is named in T-03's and T-06's `verify:`).
   SC-06 is unchanged — both added suites live under `tests/integration/`, the `integration` kind's
   `detect` glob.
2. SC-07 now carries the consumer anchors and the whole enumeration, so a reader CHECKS it rather
   than trusting it.
3. `plan.yaml` T-03 `verify:` and T-06 `verify:` each gained the same two commands at the tail —
   ten `&&`-joined lines, still a literal `|` block scalar (re-read from disk after the amends).

**The consumer set is CLOSED at six files** — `grep load_plan` over
`.claude/skills/harness/bin/` at HEAD, re-run by me, not adopted: `check-plan-routes.py:366`,
`check-state.sh:140`, `factory_claim.py:107`, `factory_decompose.py:471`, `gh-sync.py:357`/`:1154`/
`:1264` call `harness_yaml.load_plan`; `plan-merge.py` reaches the same rule through
`validate_plan_doc` directly and never calls `load_plan` (its two `load_plan` mentions, `:465` and
`:499`, are comments). `harness_yaml.py:295` is the definition. `.agents/` has no consumer;
`.claude/hooks/` and `tools/` do not exist in this worktree. `gh-sync.py:357` is a third call site in
an already-bound file, not a seventh consumer. **No unbindable consumer:** every one of the six has a
named suite in SC-06 or SC-07 and in both `verify:` blocks.

**S-2 (`low`, `scope`) — SC-04 mandated a grep and named no term.** SC-04 now names
`_validate_plan_depends_on` — confirmed against T-03's `intent:` (`plan.yaml:320`, `def
_validate_plan_depends_on(tasks, path)`), so it is the name the task actually creates — and states
what the grep must find: exactly one definition and exactly one call site, both inside
`.claude/skills/harness/bin/harness_yaml.py`, no further match in the tree, and no second
implementation of the rule under any name in `plan-merge.py`, `check-plan-routes.py` or any other
consumer. `verify: inspection` unchanged.

**Panel record — `panel:` at cycle 1**, one `set-panel` value file, `last_run:
2026-09-07-02-validator`, both readers `ran` (`scope`/`harness-code-reviewer`,
`should-not-exist`/`fable-advisor`; the digest records no skip). **19 findings**, 19 distinct ids:
six surviving c1 findings, three c1 rows the lead assessed and dismissed (each carrying its reason),
and the ten c0 ids copied byte-for-byte and re-dispositioned. Ids minted here with
`panel_findings.py id` over the summary exactly as stored:

| reader id | PF- id | severity | disposition |
|---|---|---|---|
| V-1 | `PF-1bb62463…` | med | repaired |
| L-1 | `PF-bb596497…` | info | open |
| S-1 | `PF-12330e2e…` | low | open |
| S-2 | `PF-72604111…` | low | repaired |
| S-3 | `PF-503d2620…` | info | open |
| S-4 | `PF-d39b8324…` | info | open |
| SCOPE-C1-01 | `PF-4159ab1b…` | med | dismissed |
| SNE-C1-3 | `PF-cd8aa259…` | info | dismissed |
| SNE-C1-2 | `PF-93642943…` | info | dismissed |

c0 dispositions: `PF-d26198` delivered · `PF-6dda61`, `PF-cc2bcf`, `PF-092cbd`, `PF-7beea1`,
`PF-3116cd`, `PF-e159de`, `PF-e9eff4` repaired · `PF-4f9180` unchanged_deliberately · `PF-4e8683`
settled_by_ruling. My own c1 verification agrees with every one.

**`PF-e9eff4`'s c1 repair was PARTIAL until now, and the record says so.** My c1 table called it
`repaired`; the panel was right that it bound three of the four consumers its own text enumerated and
dropped `factory_decompose.py`. Its summary in `panel.findings` now records the partial, names V-1,
and states that `repaired` holds as of this transcription rather than as of the c1 build.

## Approval — read after the last write

- `plan.yaml:3-4` → `approval:` / `  status: pending` (also `{'status': 'pending'}` via `load_plan`).
- `BRIEF.md:153,155` → `## Approval` / `status: pending`.
- `check-plan-routes.py` over this plan after every write: `OK T-01`…`OK T-06`,
  `0 violation(s) across 1 plan(s)`, exit 0.

## Open questions

- **Q1 (non-blocking, not a re-opening):** `plan-merge.py` has no write route to the top-level
  `lanes` key (`apply` exits 7, `AMENDABLE_KEYS == ("tasks","decisions")`), so `factory_claim.py` and
  `gh-sync.py` cannot be added to `lanes.rows`. The advisor ruled on 2026-09-07 that the plan is
  signable with `lanes.rows` unchanged and the lane fact carried by D-03 — that stands. This is a
  dev-ops backlog chore on the tool, not a defect of this plan.
