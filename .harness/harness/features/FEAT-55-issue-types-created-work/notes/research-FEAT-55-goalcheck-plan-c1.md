# Goal-check c1 — does FEAT-55's REPAIRED plan deliver the operator's stated intent?

**NOT YET — one `high` finding stands, and it is the same out-of-scope breach F-01 named, now on the
41 receipts that already exist.** All nine c0 findings are CLOSED on the forward path: the adoption
marker, the role-based typing ruling (D-18), the read-only probe (D-19) and the pinned read-back
wording are all in the plan text, each with a named fixture. But T-04 §6's backfill is a
**key-presence** test on a mapping that is net-new, so every parent recorded *before* this feature
ships reads as "not typed yet" and gets typed — including the two parents `DECISIONS.md` itself
records as hand-recorded (**N-01**, `high`). Graded against
`.harness/notes/grilling-issue-types-2026-09-04.md`, not the BRIEF. Plan anchors are working-tree
lines at `plan.yaml` sha256 `eb9b9f03…` (untracked; see `## plan.yaml unchanged`).

**No new BRIEF drift.** REQ-03/REQ-04 stay compatible with D-18 (a task sub-issue is an
implementation task, so `Feature` is carried by parents and by backlog `enhancement`). The one place
the BRIEF *had* drifted under D-19 — SC-10's two-verdict enumeration — is amended this cycle to
three (`BRIEF.md:140-148`), the single authorised BRIEF edit.

## c0 findings, dispositioned individually

| F | Status | Plan text that closes it (not the repair note's claim) |
|---|---|---|
| F-01 high | **CLOSED for adoptions recorded from now on; the pre-existing population is N-01.** | `typed` is two-valued and read by key presence, never truthiness: T-04 §6 `:463-466`, `:470-475`; the adopt branch writes `typed["parent"] = "adopted"` in the same `save_recorded` as the number, T-04 §7 `:478-486` (gh-sync, `--parent` at `:934-937`); the factory exemption that did not exist at c0 is T-08 §8 `:764-774` (`factory_decompose.py:404-407`). **Both** backfills are bounded ("never on this run and not on any later one", `:475` and `:772`). Fixtures: **T-03 case H2** `:384-389` (adopt with `--parent`, rerun *without*, zero `updateIssue` for that node id, marker still `"adopted"`) and **T-07 case F** `:684-691` (same on the factory route); T-03 case H `:380-383` asserts the marker in the adopting run. |
| F-02 med | **CLOSED.** | T-10 `verify` `:823-834` no longer greps a constant: it resolves `github.repo` from `.harness/harness.json` and requires the verdict line to name it (`:825`, `:829`), requires exactly one verdict line (`:828`), fails if the default run mentions a create (`:830`), and runs a second leg with `PATH` stripped of `gh` that must `SKIP` and exit 0 (`:831-833`). A constant-echo stub cannot satisfy both legs. Residue: **N-03**. |
| F-03 high (c0: med) | **CLOSED.** | The pinned line authorises the **issue-level** id read: "the numeric and node identifiers of an issue whose number Harness already recorded locally — existing practice named here for the first time, read by `gh_issues.internal_id_args` for sub-issue attach and detach and by `gh_issue_types.node_id_args` before a type-apply" — T-11 §3 `:937` and T-12 §1 `:984`, **byte-identical** (511 chars, sha256 `7f065a7a5225`, re-derived here). T-11 §3 `:941-944` names the three existing call sites (`gh-sync.py:974`, `:1215`, `factory_gh.py:981`, at `eb9d044e`) and states the feature removes none. The probe's type read-back is the third clause and T-10 §5 `:865-866` makes the default path do **no** issue-level read at all. Mechanism, not assertion: T-12 `verify` `:966-977` machine-compares the two copies. |
| F-04 med | **CLOSED.** | T-05 case D `:535-545` (available rerun: zero creates, **exactly one** `issueTypes` argv, zero diagnostic lines) and new case F `:550-556` (compatibility rerun: exactly one `^gh-sync: issue types ` line); T-07 new case G `:692-697` (zero-create factory rerun, exactly one `^factory: issue types ` line). T-06 §2 `:582-588` no longer overclaims and states the unreachable residue in-plan (`main()` refuses a `backlog` with no items, `gh-sync.py:1777-1778`). |
| F-05 med | **CLOSED via D-18.** | D-18 `:116-119` and the rewritten D-02 `:51-54`; `DEFAULT_TYPE_BY_CHANGE_TYPE["feature"] = "Task"` in T-02 `:230-232`; three role-scoped resolvers named T-02 `:223-226`; T-01 assertion 1 `:155-160`. Proven on both sub-issue routes by fixtures that carry a `feature` task: T-03 `:341-345`, case A `:352-353` (`IT_task`), T-07 `:655-656`, case A `:662-665`. Override key `feature` stays legal (T-01 assertion 5 `:167-172`, D-12). |
| F-06 low | **CLOSED.** | T-01 `verify` `:136-139` greps all fifteen values plus `UnknownWorkNature`. Residue, small: a file that merely *lists* the fifteen strings with no assertions still reports RED-as-required; the discriminator is the greps, not assertion count. |
| F-07 low | **CLOSED, behaviourally.** | T-06 §5 `:602-611` gates the receipt on `state == "available"` and states the compatibility path is byte-for-byte today's; D-13 `:96-98` amended to carry the gate; asserted, not asserted-about: T-05 case C `:529-534` (no `backlog-issues.json` in compat mode) and case F `:550-556` (a compat rerun still makes three MORE creates — today's duplicate behaviour). |
| F-08 low | **CLOSED via D-19.** | D-19 `:120-123`; T-10 `:842-844` (creates nothing by default), `:862-866` (`CAPABILITY PRESENT`, read-only), `:867-884` (`--create-in <owner/name>` must equal the configured repo or exit 2 creating nothing; close in a `finally`; removal command printed); T-09 `:804-807` registers the **default** invocation and forbids the flag in `cmd`. |
| F-09 low | **CLOSED.** | The compatibility control is now inside the gates: T-04 `verify` `:404`, T-06 `verify` `:569`, T-08 `verify` `:711-712`. |

## `## Settled`, re-graded clause by clause

| # | Clause | Delivered by | Verdict |
|---|---|---|---|
| 1 | Overrides required; defaults Bug / Feature / Task | D-01, D-03, D-04, D-12, D-18; T-02 `:230-259`, T-01 cases 1-6, T-04 §2/§4, T-06 §3, T-08 §4/§6 | **met** |
| 2 | Feature and factory parents default `Feature`, same override mechanism | D-18 `:117`, D-12; `type_for_parent` T-02 `:259`; T-04 §4 `:447-448`, T-08 §6 `:752-753`; tests T-03 A/E, T-07 A/D | **met** |
| 3 | Types unavailable → labels preserved exactly, one diagnostic per invocation | D-15; T-04 §3/§5, T-06 §2/§4/§5, T-08 §5/§7; tests T-03 C/D/I, T-05 C/F, T-07 C/G | **met** — F-04 and F-07 both repaired the two holes c0 found here |
| 4 | Types active → competing `bug`/`chore` labels not applied | T-04 §5 `:450-454`, T-06 §4, T-08 §7; tests T-03 B, T-05 B, T-07 B | **met** |
| 5 | Create-then-type-fail → rerun identifies and classifies, never deletes or duplicates | D-10, D-13; T-04 §6 `:467-473`, T-06 §5, T-08 §8; tests T-03 G, T-05 E, T-07 E | **met for issues Harness created** — the same backfill is N-01 for issues it did not |

## `## Out of scope`, dispositioned individually

| Item | Disposition |
|---|---|
| (a) Changing adopted/source issues | **honoured prospectively, BREACHED on pre-existing receipts — N-01 (high).** Forward adoptions carry the marker (T-04 §7, T-08 §8) and `source_issues` are excluded twice (`:475`, `:382`). A parent recorded before the `typed` mapping existed carries no marker, and key-presence then reads it as a backfill candidate. |
| (b) Enabling/bootstrapping Issue Types | **honoured.** No task writes a repository type definition; `refusal_text` only names the repair (T-02 `:297-300`). The probe's live create is now opt-in and repo-retyping (T-10 §6), and it creates an *issue*, never a type. |

## The five creation routes, and D-18 agreement per route

| Route | Owning task | Expected type in the fixture | Verdict |
|---|---|---|---|
| Feature parent (`gh-sync.py:941-943`) | T-04 §4/§6 | `IT_feature` via `type_for_parent`, T-03 A `:351` | typed; N-01 on the legacy rerun |
| Planned task sub-issue (`:957-967`) | T-04 §5/§6 | `IT_bug` / `IT_task` / `IT_task` / **`IT_task` for the `feature` task**, T-03 A `:351-353` | typed, agrees with D-18 |
| Ship-review backlog issue (`cmd_backlog :1410-1429`) | T-06 | `IT_bug` bug, `IT_task` chore, `IT_feature` enhancement, T-05 A `:523-526` | typed; a backlog item types by nature, not role, which is clause 1 |
| Factory parent (`factory_decompose.py:421-425`) | T-08 §8 | `IT_feature` via `type_for_parent`, T-07 A `:661-665` | typed; N-01 on the legacy rerun |
| Factory task (`:433-437`) | T-08 §7/§8 | `IT_bug` / `IT_task` / **`IT_task` for the `feature` task**, T-07 A `:661-664` | typed, agrees with D-18 |

**No route types a sub-issue `Feature`** — checked in the fixture expectations themselves, not in the
decision prose: T-03 A `:352-353` and T-07 A `:662-665` both spell the `feature`-change_type task's
expectation as `IT_task`, and both say so in as many words. Override fixtures declare the names they
assert (T-03 `:329`: Defect, Epic; T-07 `:650`: Story), so no case asserts an undeclared type.

## New findings the repair introduced

**N-01 · high · the adoption marker bounds only adoptions recorded after this ships; 41 existing
receipts read as backfill candidates.** T-04 §6 `:470-475` backfills "if the number is already
recorded, the key is ABSENT from `rec["typed"]` and the state is available"; `rec["typed"]` is
net-new (T-04 §6 `:459-462`), so on a pre-existing `feature.json` the key is absent for *every*
parent — created, hand-recorded or adopted alike. Measured in this tree: **41 of 41** `feature.json`
files with a numeric `github.parent` carry no `typed` and no origin key
(`.harness/harness/features/*/feature.json`), and `DECISIONS.md:2977-2979` records that **#728
(FEAT-34) and #751 (FEAT-35) were recorded by hand** — issues Harness did not create. The first
`gh-sync open` on either directory against an Issue-Types-enabled repository applies a native type
to them. T-08 §8 `:769-772` has the identical shape on `factory.yaml`. The same decision entry also
records that an origin marker *was already tried and failed for exactly this reason* ("`parent_origin`
read **null** … because both parents were recorded by hand"), so this is a known failure mode being
re-entered under a new key name. Latent today only because the pinned repo returns `issueTypes:
null`. **Repair:** make the marker written *before* the apply, not only after — record
`typed[key] = "created"` in the same `save_recorded` as the number, promote it to `True` after the
apply, and backfill **only** where the recorded value is `"created"`. Absent then means
unknown-provenance and is never typed, which is the safe reading and matches DEC-138's own
absent-origin default. Add a T-03 case and a T-07 case whose fixture is a receipt with a numeric
parent and **no** `typed` mapping at all, asserting zero `updateIssue` for it.

**N-02 · low · the backfill path sits outside the pre-creation refusal.** T-04 §4 `:436-446` builds
the required-type set from the parent and tasks that will be **created** (already-recorded ones are
explicitly skipped, `:439-442`), while §6 `:470-473` applies a type to recorded-but-untyped ones.
A backfill whose type name is not in `declared` is therefore never refused and has no specified
behaviour — the `declared[name]` lookup is unreachable in the plan text. T-08 §6/§8 has the same
gap. REQ-07's "refuse before creating any issue" is vacuous on an invocation that creates nothing.
**Repair:** include the backfill set in `missing_types`, or say in §6 what happens when the type
name is undeclared (the honest answer is the same refusal, exit 2, before any apply).

**N-03 · low · T-10's gate proves environment-sensitivity, not that the API was consulted.** The
`verify` `:823-834` discriminates a constant-echo stub (it must `SKIP` with `gh` off `PATH`), but a
probe that merely checks `command -v gh` and otherwise prints `CAPABILITY ABSENT` also passes,
because `CAPABILITY ABSENT` is the expected verdict against the pinned repo. Inherent to the
environment — the BRIEF's `## Verification gaps` already carries the class — and unfixable here
without an enabled repository; recorded so nobody reads T-10's green as live-API proof.

**N-04 · info · c0's blocking Q1 was answered by the plan, not by the operator.** D-18 `:116-119`
rules that a `feature` sub-issue types `Task`. The ruling is derived from the grilling's own words
("chores/implementation tasks to `Task`") and from #1289, so it is a faithful reading rather than a
new choice — but it is recorded as a `D-NN` and the operator's signature is the only place it is
ratified. Q2 (the probe's live write) is answered conservatively by D-19: no write without an
explicit opt-in, so no grant is needed.

## plan.yaml unchanged

`plan.yaml` is **byte-unchanged** this cycle. Confirmed two ways, before and after the BRIEF edit:
`sha256sum` = `eb9b9f034fd634d484203b6d987e9cfbd64d45763a693dd7e32e5d4dd25c5fd4` at both points, and
`git status --porcelain` on that path reports `??` at both points (the whole feature directory is
untracked on `feat/issue-1289-issue-types`, so there is no tracked baseline to diff — the sha is the
baseline). `check-plan-routes.py <plan>` re-run here: `0 violation(s)`, exit 0.

## The BRIEF amendment

`BRIEF.md:140-148` — SC-10 now enumerates **three** verdicts (live pass under the create opt-in;
capability-present, creating nothing, which is D-19's read-only default against an enabled
repository; capability-absent), and still carries the sentence naming it the carrier of #1289's
enabled-repository acceptance, the "never reports a pass derived from a fixture" clause, and
`verify: automated  evidence: issue_types_live`. Six lines replaced by nine (net +3); no other SC,
no REQ, no Constraints, no `## Verification gaps` text and no approval value changed — 11 REQs, 11
SCs, `status: pending`, all re-counted after the edit. The file is untracked, so `git diff` on it
returns nothing ("Did you forget to 'git add'?"); the extent above is the edit's own range.

## Open questions for the operator

- **Q1 (blocking, N-01):** an `open` or `decompose` rerun on any of the 41 pre-existing features will
  type its recorded parent once Issue Types are live. Is repairing the marker (`"created"` written
  before the apply) in scope for this feature, or does the operator accept the retype on legacy
  receipts?
- **Q2 (non-blocking):** the probe's `SKIP` verdict — no `gh`, `sync: false`, unpinned repo, failed
  capability query, `--create-in` mismatch — is a fourth outcome SC-10 does not enumerate. It was
  outside the one authorised amendment, so SC-10 still names three. Add it, or leave `SKIP` as an
  environmental non-verdict?
- **Q3 (non-blocking):** the opt-in live create (T-10 §6) is not named in the BRIEF's
  `## Verification gaps` block, which this cycle was forbidden to touch. Worth one line there at
  signature so the operator signs the live write knowingly.
