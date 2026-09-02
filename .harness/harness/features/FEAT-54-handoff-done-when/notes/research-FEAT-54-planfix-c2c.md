# planfix-c2c — D-01 amend and c2 panel record — FEAT-54-handoff-done-when

## BLUF

Both c2 must-fixes are closed inside `plan.yaml` and nothing else moved. D-01 no longer asserts that
the persisted pass resolves pointer targets — it now decides only the frozen-baseline discriminator,
says GRAMMAR-not-resolution when the section is present, and defers the write-time/persisted split to
D-10 by id. The `panel:` mapping is retranscribed at `cycle: 2`, `last_run: 2026-09-02-c2-validator`,
both readers `ran`, seven findings, `severity_max: med`, with each of the operator's two batched
rulings recorded and the three unruled c0 findings recorded `open` as re-derived STANDING.
`check-plan-routes.py` reports **0 violation(s)**; all seven `PF-` ids re-derive from their own landed
summaries; all 12 tasks and all 8 non-D-01 decisions are byte-identical pre vs post; `approval:` is
still `{status: pending}` with no `rulings:` key.

## 1. D-01 — before/after, with all four sha256s

Route: `plan-merge.py amend --key decisions --id D-01`, compare-and-swap on each field's sha256.

| field | before sha256 | after sha256 |
|---|---|---|
| `choice` | `f85213b2368fe694f6e4fdf2d8f7bae4ff39994dcfe721e9f7a8fc35ae2b16c3` | `35c41a6af4462ce21ba69c654c53882d95824b8662d6dedcc758474481e62b5b` |
| `because` | `36a4398f0d28a399f7fc18b0e800cb8558b3aabc00fba5be615d7965b43c76ae` | `84f86b9f3097422478478da375a753d8fa7696bc9ecc3c34e213115901e3538d` |

**What changed in `choice`.** The struck clause was *"block shape and pointer resolution are checked
whenever the section is present, whoever wrote it"*. It now reads that the persisted pass checks
"block shape and pointer GRAMMAR, never target resolution", the discriminator sentence is stated as
the decision's whole scope (absent from `handoff_done_when_baseline` in `.harness/harness.json`, 141
paths, notes tracked at b7956fc4 that lack the section), and a closing sentence defers the
write-time-versus-persisted split to D-10. `id` and `dec: none` untouched.

**What changed in `because`.** The frozen-list rationale is carried word-for-word — no git history so
the answer cannot change with clone depth in a depth-1 CI checkout, the dead-entry failure mode which
exempts nothing, and a historical note leaving the set only by becoming compliant. One clause is
appended and nothing else: what each pass checks once the section is present is D-10's ruling, not
this one's, deferred to it by id. No resolution semantics were added.

**Acceptance 1 (run).** `grep` over the landed file for `pointer resolution|resolution are
checked|re-resolv|resolves.*persisted|persisted.*resolution` returns only: D-02's "one implementation
of block parsing and pointer resolution" (a single-implementation claim, not a persisted-pass claim);
`panel.findings[0].summary`, which is the c0 defect being recorded, not asserted; and negations —
T-06 "(e1) is the D-10 guard on the persisted pass never re-resolving a target", T-07 "This pass
NEVER opens a pointer's target (D-10)", T-10 "NOT re-resolved by the persisted-corpus check
afterwards (D-10)" and "never re-resolves a target (D-10)". **No surviving claim says the
state/persisted check resolves targets.**

## 2. The transcribed c2 panel

`last_run: 2026-09-02-c2-validator`, `cycle: 2`, `readers:` exactly `should-not-exist` (ran) and
`scope` (ran), each carrying only `reader` and `status` — neither was skipped, so neither carries a
persona or reason key. Severities present: `med`, `low`, `info`. Nothing high, critical or unrated; no
severity was invented, softened, or reassigned.

| id | sev | reader | disposition |
|---|---|---|---|
| `PF-4205e7e2f84e2eb24d421c924f4d7ac3` | med | should-not-exist | **ACCEPTED** at the batched ruling of 2026-09-02, implemented as **D-10**, carried by T-01, T-02, T-06(e1,e2), T-07; notes that D-01 no longer contradicts it after this amend |
| `PF-1e45eb3a962725a1b45e3e0e90a271c6` | info | should-not-exist | **REJECTED** at the same ruling — D-04 stands, the probe kept whole, T-09/T-12/SC-09 retained |
| `PF-570b9c87adac19d62513b5e90cce0f81` | low | should-not-exist | `open` — no ruling exists; both c2 readers independently re-derived it as **STANDING** |
| `PF-918326616878584f5958be94fba0ede7` | low | scope | `open` — same, STANDING |
| `PF-d0ea19ffc351a13d6b569f0169222109` | low | should-not-exist | `open` — same, STANDING |
| `PF-f2aee0d45b76412d69f7e8a9496f86a8` | med | scope | **resolved by this run** — D-01's `choice`/`because` amended; T-07's `per D-01` citation now agrees with its `resolve=False` body |
| `PF-bd92960a1606d9794331d84a14e0b978` | info | should-not-exist | `open` — see the ruling below |

**The new `info` finding is `open`, and the plan does not answer it.** Decided against the plan text,
not hedged: `D-03` fixes the four authority types and the frozen baseline (D-01, D-08) exempts
**section presence only** — never grammar. No decision, task or criterion in the plan covers a later
rename or narrowing of an authority type or an id format, so a future feature doing either reddens
every five-section note already written. T-08 and T-10 restate the four types as normative prose,
which pins today's grammar but supplies no versioning mechanism, and SC-15 guards only that targets
are not re-opened. A grammar-version analogue of the frozen baseline is out of this feature's scope;
the disposition records the gap for that feature's planner instead of repairing it here.

The panel's own dismissal is honoured and not re-litigated: goal-check **F-03 is absent** from
`findings` — it was dismissed at source (T-04 already carries the gate-prose clause, SC-08 already
covers comments and messages), so it never became a finding to dispose of.

## 3. The id re-derivation check — all 7 MATCH

Every landed summary was fed back through `panel_findings.py id --reader <its reader> --summary <its
landed summary>` by loading the landed YAML and looping (`/tmp/feat54-verify.py`):

```
PF-4205e7e2f84e2eb24d421c924f4d7ac3 -> MATCH      PF-918326616878584f5958be94fba0ede7 -> MATCH
PF-1e45eb3a962725a1b45e3e0e90a271c6 -> MATCH      PF-d0ea19ffc351a13d6b569f0169222109 -> MATCH
PF-570b9c87adac19d62513b5e90cce0f81 -> MATCH      PF-f2aee0d45b76412d69f7e8a9496f86a8 -> MATCH
                                                  PF-bd92960a1606d9794331d84a14e0b978 -> MATCH
```

The five carried-over summaries were **not retyped**: the build script (`/tmp/feat54-build-panel.py`)
read them out of the pre-existing `panel.findings` and copied the `severity`/`reader`/`summary` values
verbatim. `set-panel` re-dumped them through `yaml.safe_dump`, so their LINE BREAKS moved; the ids
re-derive anyway because `panel_findings.py` lowercases and collapses whitespace before hashing. The
proof is the id, not the diff. The two new ids were computed from the exact drafted summary text
before it was written, never typed.

## 4. Nothing but `decisions` and `panel` moved

A pre-image was copied to `/tmp/feat54-plan-preimage.yaml`
(sha256 `59a8c40d16f8e337998c929750e1a2903d49ab1c00e9e78c259799e2599eb925`) **before the first write**,
then compared item by item on serialized form:

- **tasks:** T-01..T-12 — all 12 `IDENTICAL`.
- **decisions:** D-01 `CHANGED` (expected); D-02, D-03, D-04, D-05, D-06, D-07, D-08, D-10 all
  `IDENTICAL`.
- **top-level keys whose value moved:** exactly `['decisions', 'panel']`. Top-level key order
  preserved.
- `approval == {'status': 'pending'}`, `rulings` key **absent**. `status: 'plan'`. The file parses
  under `safe_load`.

`cd <worktree root> && python3 .claude/skills/harness/bin/check-plan-routes.py
.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml` →

```
0 violation(s) across 1 plan(s)
```

exit 0. The twelve `DEVIATION` lines it also prints are the pre-existing DEC-174 carve-out output
(granted paths declared `main-session-direct`); only `VIOLATION` lines gate, and there are none.

## Open questions for the tier above

- The three `low` c0 findings still carry no operator ruling after two cycles. Recorded `open` with
  the STANDING re-derivation; ruling them is the operator's, not mine.
- The operator's batched ruling of 2026-09-02 is now legible in `panel.findings[].disposition`, but
  `approval:` still carries no `rulings:` key — validator-lead escalation E1. That write is the main
  session's alone (DEC-120) and was deliberately not made here.

## planfix-c2d — 2026-09-02 — the missing `goalcheck` reader

**BLUF: `panel.readers` now records all three readers `check-state.sh` INV-32 expects; nothing else
in plan.yaml changed.** One entry was appended — `reader: goalcheck`, `status: ran`. `last_run`
stays `2026-09-02-c2-validator` and `cycle` stays 2.

**Why the entry is authorised, not invented.** `check-state.sh:519` reads
`expected_readers = {"should-not-exist", "scope", "goalcheck"}`, so a two-entry list is an
incomplete record rather than a clean one. The goalcheck reader DID run this cycle (run
`2026-09-02-c2goalcheck-product`) and its artifact is on disk at
`notes/research-FEAT-54-goalcheck-plan-c2.md` (VERDICT: YES). Recording it as `ran` transcribes what
happened; it is not a `skipped` entry needing a persona and reason.

**How it was written.** Pre-image snapshotted to `/tmp/feat54-plan-pre.yaml`; the replacement value
was built programmatically by loading that pre-image with `harness_yaml.load_file`, appending the one
reader dict to `doc['panel']` and dumping that mapping alone. No finding was retyped. Applied with
`plan-merge.py set-panel --file <plan.yaml> --value-file <tmp>` — the only write route to `panel:`.
`safe_dump` re-wrapped some long summary scalars; every parsed value is character-identical, proved
below.

**Verification — all four acceptance checks pass.**

```
PASS panel.readers == 3 entries in order, all ran -- [('should-not-exist', 'ran'), ('scope', 'ran'), ('goalcheck', 'ran')]
PASS panel.cycle == 2 -- 2
PASS panel.last_run == 2026-09-02-c2-validator -- '2026-09-02-c2-validator'
PASS PF- ids re-derive from post-write reader+summary: 7/7
PASS approval.status == pending -- 'pending'
PASS status == plan -- 'plan'
PASS tasks are exactly T-01..T-12 (12)
PASS decisions are exactly D-01..D-08 + D-10 (9)
PASS tasks: every id's whole mapping compares equal pre vs post -- equal=T-01,T-02,T-03,T-04,T-05,T-06,T-07,T-08,T-09,T-10,T-11,T-12 differing=none
PASS decisions: every id's whole mapping compares equal pre vs post -- equal=D-01,D-02,D-03,D-04,D-05,D-06,D-07,D-08,D-10 differing=none
PASS all 7 findings equal on id/severity/reader/summary/disposition -- equal=7/7 differing=none
PASS post minus the goalcheck reader == pre-image exactly (no other delta)
```

The seven ids were re-derived by invoking `panel_findings.py id --reader <r> --summary <s>` once per
finding with the POST-write values and comparing to the stored id: 7/7 equal, so the re-wrap changed
no summary. `check-plan-routes.py` on this plan: `0 violation(s) across 1 plan(s)`, exit 0 (the
twelve `DEVIATION` lines remain the DEC-174 carve-out output; only `VIOLATION` gates).

`approval:` untouched and still `status: pending` — the c2c open questions above stand unchanged.
