# Goal-check — FEAT-11 GraphQL field resolve — at `2ea9af3`

**FAIL, and the reason is one missing assertion, not a broken feature.** Eleven of twelve criteria
hold on their own declared method. **SC-11 is `not_met`**: it names two distinctions and only one is
asserted, so an implementation that reports a misspelled owner as a missing board passes the whole
suite green. **SC-01 is `uat`** — the documented expected end state, not a defect. All five REQs
trace to shipped code. Two things need the operator: **E-1** (recommendation below) and a
**BRIEF/ruling contradiction about board 6** that will otherwise tell the next reader to delete a
retained fixture.

## REQ coverage

| REQ | Traced to | Via |
|---|---|---|
| REQ-01 | `factory_gh.py:202-219` `_FIELD_QUERY`, `:236-284` resolver | one cost-1 query replaces `field-list` (102) + `view` (2); `_field_list` deleted |
| REQ-02 | `factory_gh.py:206-210`, `:251-256` frozen wordings | D-04 freeze, now enforced by rendered-literal assertions `test-factory-gh.py:331`, `:623` |
| REQ-03 | `factory_gh.py:255-266` branches (a) and (b) | separate `what` per cause, read `__typename` before `projectV2` |
| REQ-04 | `factory_gh.py:236-284` + `project_field_set` | every failure raises; zero `item-edit` asserted in six cases |
| REQ-05 | three sha256 pins, `plan.yaml:88-90` | `test-factory-decompose/claim/land.py` unedited and green in the unit kind |

Nothing was dropped.

## SC verdicts — each by its own declared method

| SC | Verdict | Method | Evidence (named anchor) |
|---|---|---|---|
| SC-01 | `uat` | uat | Operator-run only. `BRIEF.md:42-46`; script at `notes/uat-SC-01-graphql-cost.md`. **See the arithmetic warning below.** |
| SC-02 | met | unit | `test-factory-gh.py:288` (exactly two calls), `:292` graphql first, `:294` item-edit second; survival half = `plan.yaml:80-81` grep clauses, 0 hits in `factory_gh.py` |
| SC-03 | met | unit | `test-factory-gh.py:309/:311/:313` — three regexes on the query text **pulled from the emitted argv** (`:304-308`), not the constant; plus `plan.yaml:83-85` |
| SC-04 | met | unit | field: `test-factory-gh.py:620` names `NoSuchField`; option: `:326` names `NotAnOption`; frozen wordings `:623`, `:331` |
| SC-05 | met | unit | `test-factory-gh.py:432` inside the two-fixture loop `:418-419` — `GRAPHQL_ORG_UNREACHABLE_JSON` (`:91`, exit 1) and `GRAPHQL_ORG_OK_JSON` (`:85`, exit 0). Fixture (b) derived, disclosed at `BRIEF.md:138-145` |
| SC-06 | met | unit | `test-factory-gh.py:455` (names `acmeuser project 3`) and `:459` (message differs from the org message) |
| SC-07 | met | unit | `test-factory-gh.py:362` (`--project-id` is `PVT_kwFAKE`, never `"3"`); zero-item-edit at `:328`, `:385`, `:412`, `:434`, `:457`, `:478`. **The E-1 envelope does not violate it — clause quoted below** |
| SC-08 | met | unit | unedited: `plan.yaml:88-90` sha256 pins, re-run twice (`feature.yaml gate_status.task_verify`); passing: all three are in `UNIT_SCRIPTS` (`run-unit-tests.sh:17`), and the unit kind ran 10/10 scripts (`runs/t01-qa-validator/digest.md` `kind_results`) |
| SC-09 | met | integration | deletion half: `plan.yaml:78-79` grep clauses, 0 hits in `test-factory-integration.py`; passing half: the **integration kind** ran 12/12 scripts, `test-factory-integration.py` 97/97 (`runs/t01-qa-validator/digest.md` `kind_results`) — the first time the kind itself was shown green |
| SC-10 | met | unit | positive: `test-factory-gh.py:410`, `:432`, `:455`, all on value `acmeuser`, **mutant-proved** — drop the value and `:411` reddens once, `:433` twice (`feature.yaml gate_status.mf1_mutant_proof`, `runs/mf1-eng/digest.md`). negative: `:414`, `:439`, `:461`, `:480`, `:334`, `:390`, `:626` |
| SC-11 | **not_met** | unit | see below |
| SC-12 | met | unit | `test-factory-gh.py:474` — `GRAPHQL_FIELD_NOT_SINGLE_SELECT_JSON` (`:107`, exit 0, `field: {}`) raises the same rendered field-not-found string; `factory_gh.py:274` is `if not field_obj:` |

### SC-11 — the gap, stated as weakly as the evidence supports

SC-11 requires the unknown-owner error to be distinct from **both** the organization refusal **and**
the board-not-found error. Only one comparison exists:

- `test-factory-gh.py:436-438` asserts `str(org_exc) != str(unknown_exc)` — the org half. Holds.
- `:459-460` asserts `str(board_exc) != str(org_exc)` — that is SC-06's clause, not SC-11's.
- **Nothing compares `unknown_exc` to `board_exc`.** Verified by grepping every use of both names at
  the pin: `:405`, `:407`, `:411`, `:415`, `:437` and `:450`, `:452`, `:456`, `:460`, `:462`.

Inequality is not transitive. An implementation whose branch (a) raised the **board-not-found**
message passes `:411` (`acmeuser` is in it), `:415`, `:437` (still differs from the org message),
`:456`, `:460` — the whole suite stays green while a misspelled owner is reported as a missing board.

The shipped code is correct (`factory_gh.py:255-260` vs `:267-271` raise different `what` values).
**Reading that is inspection, and SC-11 declared `automated`** — the method is fixed at approval, so
a source read cannot close it. Verdict `not_met`.

**Remedy — one line, and it routes to eng, not qa.** Add after `:460`:
`check("unknown owner: message differs from the board-absent message", str(unknown_exc) != str(board_exc), ...)`.
`harness-qa` cannot author it: `feature.yaml residuals.qa_cannot_author_here` records that qa's
grants (`tests/**`, `web/src/**/*.test.*`) match no file under `.claude/skills/harness/bin/`. The
precedent is MF-1 → `runs/mf1-eng` → `harness-backend-dev`.

**This is the second instance of the MF-1 defect class in this feature** — a criterion reported
covered by an assertion that cannot report red — and the qa gate did not catch this one. `qa-c0.md:71`
records SC-11 as "distinct from org and board-absent"; the second half is not in the tree.

### SC-10, corrected at source rather than relayed

I ran the substring test myself on `factory_gh.py:264-266` at the pin. The two prose strings are
`organization-owned board not supported` and `run against a user-owned board`: `grep -o 'own[a-z]*'`
returns **`owned` twice and `owner` once**, and the single `owner` is the Python argument identifier
on the value line, not message text. So the rendered message carries no `owner` substring and
`:428` (now `:433`) was already discriminating. qa's MF-1 named two vacuous assertions; **one was**.
SC-10 was partially proven before the MF-1 cycle and is **fully proven after it**. All four remedy
sites were still warranted — `:437` and `:460` cross-compare for inequality, so moving one case's
value alone would make those pass on the value rather than on the wording.

## SC-07 versus the E-1 envelope — the ruling holds, and here is the clause

The discriminating question is what "a failed resolution" means. **`plan.yaml:53` forecloses the
exit-code reading in its own signed words: "the exit code does not partition the failure set."** If a
non-zero exit is not what makes a resolution failed, then a resolution is failed when it cannot
produce ids. In E-1's envelope the resolver produces all three ids from a complete `data` payload
with no null anywhere — the resolution **succeeded**. SC-07's second clause is also untouched: the
`--project-id` passed is the resolved `PVT_` node id, never the bare board number.

SC-07 is `met` as written **and** the hazard is real as a residual against D-03. That split is
consistent, not a contradiction, and neither half softens the other.

## E-1 — recommendation: ACCEPT as a recorded residual against D-03

**What an operator experiences if it fires.** The factory moves an item on the board while `gh`
reported that call as failed. `project_field_set` returns successfully, the run continues green, and
**no error is recorded anywhere** — the run looks clean. Recovery is manual: move the item back by
hand. Nothing is corrupted and nothing is lost; what is lost is the signal.

**Frequency: unmeasured.** E-1's envelope — exit non-zero, complete `data`, no null, non-empty
`errors` — has **no row in the six-row measured transport table** (`plan.yaml:119-126`). I am not
estimating a rate, and nobody should.

| | Accept as residual | Amend D-03 (a new `D-NN`, operator-approved) |
|---|---|---|
| Cost | an unmeasured fail-open **write** path stays in a tool that writes to boards | an approval cycle, a new fixture for a shape nobody has observed |
| Risk | a silent success on a call GitHub flagged | a guard on non-empty `errors` could refuse valid work if GitHub ever returns benign errors alongside good data — *educated guess, not measured* |
| Who can close it | operator records it; no code moves | eng, only after the operator signs the amendment |

There is no free option. **The load-bearing reason for accepting is that the hazard is unmeasured
and the remedy contradicts a signed decision** — not the benign-errors argument above, which is a
guess. If it is ever observed live, the recorded remedy shape is: walk the envelope first, then
raise if the walk found no fault and `errors` is non-empty. That preserves every measured row's
diagnosis. **Not implemented here.**

## Emergent criterion — genuinely new, and it reaches the operator

**"A GraphQL response carrying a non-empty `errors` array is never treated as a successful
resolution."** No existing SC covers it: SC-07 is about the id passed to `item-edit`, SC-05/06/11/12
are per-diagnosis-state, SC-10 is about message content. It is the criterion E-1 would be graded
against, and it changes what "done" means — so it is raised for the operator, not slipped in. I have
not written it into `BRIEF.md`; SCs carry the signature.

## Open records the operator must settle

1. **The BRIEF still says to delete the fixture.** `BRIEF.md:162-163` — "Board 6 is the throwaway
   that already exists and is already owed cleanup" — contradicts `plan.yaml` `approval.rulings` (2)
   and (3) and `feature.yaml sc01_ruling`, which make board 6 and
   `mruangutai/harness-factory-smoke-a1` **retained fixtures, not cleanup owed**. The rulings govern;
   the BRIEF is what the next reader opens. I did not edit it — the BRIEF is approved and a content
   change there is a re-signature, not a record correction.
2. **SC-01's "single-digit total" clause is arithmetically at risk** — see the UAT script's expected
   breakdown. A fresh four-task run also pays 1 for the station validation read
   (`factory_decompose.py:377` → `:261`) and four `gh project item-add` mutations
   (`factory_gh.py:158-163`, cost never measured), none of which this feature changed. Floor from
   measured components alone is 9 **before** item-add. The per-move clause (2 against 104) is the
   discriminating one and is safe. If the operator reads a double-digit total with 2 per move, the
   feature worked and the total clause was mis-specified — that is a plan-level correction, not a
   build defect.
3. **The UAT cannot be run without an explicit `--fleet`, and the fleet it needs does not exist.**
   `factory_decompose` takes the board from the fleet file, not a flag (`factory_config.py:50`,
   `factory_decompose.py:377`), and the default `.harness/factory/fleet.yaml` declares
   `board.number: 3`, `station_field: Status`, repo `mruangutai/harness` — **not board 6**. A run
   without `--fleet` writes stations to board 3 while the preservation procedure protects board 6.
   Step 0 of the UAT script pins the fleet and asserts `board.number == 6`; the operator has to
   create that fleet file first.

## Record corrections made to `plan.yaml`

- `tasks[0].status`: `pending` → `done`. T-01 is built (`5c433f2`), its verify passes twice
  (`feature.yaml gate_status.task_verify`) and sub-issue #215 is closed. `done` is the enum in use —
  `.claude/skills/harness/templates/plan.yaml:73` documents `pending | done` and
  `FEAT-10-software-factory/plan.yaml:110` uses `done`.
- `intent:` anchor `factory_gh.py:43` → `:45`. Confirmed at the pin: `:43` is `self.stdout = stdout`
  and `super().__init__(factory_cli.body(...))` is at `:45`.

Nothing else in the file was touched. The `verify:` literal block is byte-identical to the pin,
checked by sha256 over the loaded scalar, not by eye.
