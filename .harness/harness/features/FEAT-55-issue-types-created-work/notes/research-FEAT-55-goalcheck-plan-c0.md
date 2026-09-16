# Goal-check — does FEAT-55's plan deliver the operator's stated intent?

**NO — not yet.** All five `## Settled` clauses and all five creation routes have owning tasks, but the
plan quietly does one of the two things the operator put out of scope: on a rerun it applies a native
type to an **adopted** parent issue Harness did not create. One `high` finding gates the signature; the
rest are repairable in place.

Graded against `.harness/notes/grilling-issue-types-2026-09-04.md`, not the BRIEF. **No BRIEF drift
found**: REQ-04 (total mapping, unrecognised value reported) and REQ-11 (host-only probe) are absent
from `## Settled` but are verbatim consequences of #1289's "Required behavior" 4 / "Acceptance", which
the grilling note names as its source. Legitimate, not drift.

## `## Settled`, clause by clause

| # | Clause | Delivered by | Verdict |
|---|---|---|---|
| 1 | Repo-specific type-name overrides required; defaults Bug / Feature / Task | D-01, D-03, D-04, D-12; T-02 (`type_for_*`, `overrides_from_config`), T-01 cases 1–6, T-04 §2, T-06 §1, T-08 §4 | **met** |
| 2 | Feature parents and factory parents default `Feature`, same override mechanism | D-02, D-12 (`parent` key); T-02 `type_for_parent`, T-04 §4, T-08 §6; tests T-03 A/E, T-07 A/D | **met** |
| 3 | Types unavailable → labels preserved exactly, one diagnostic per command invocation | D-15; T-04 §3/§5, T-06 §2/§4, T-08 §5/§7; tests T-03 C+D, T-05 C, T-07 C | **met, weakly verified** — F-04, F-09 |
| 4 | Types active → competing `bug`/`chore` labels not applied | T-04 §5, T-06 §4, T-08 §7; tests T-03 B, T-05 B, T-07 B | **met** |
| 5 | Create-then-type-fail → rerun identifies and classifies, never deletes or duplicates | D-10, D-13; T-04 §6, T-06 §5, T-08 §8; tests T-03 G, T-05 E, T-07 E | **met** — but its backfill causes F-01 |

## `## Out of scope`, dispositioned individually

| Item | Disposition |
|---|---|
| (a) Changing adopted/source issues | **BREACHED — see F-01 (high).** `plan.yaml` T-04 §7 forbids typing an adopted parent in the adopting run, then T-04 §6's recorded-but-untyped backfill types it on the next run; T-08 §8 has no exemption at all. `feature.json` carries no adoption marker (`gh-sync.py:496-497` record keys; adopt branch `:934-937`; `factory_decompose.py:404-407`). `source_issues` are correctly untouched. |
| (b) Enabling/bootstrapping Issue Types | **honoured.** No task writes repository type definitions. `refusal_text` (T-02) only *tells* the operator to add the type or set `github.issue_types`; T-10 creates a scratch issue but never a type. Related live-write scope: F-08. |

## The five creation routes

| Route | Owning task | Verdict |
|---|---|---|
| Feature parent (`gh-sync.py:941-943`) | T-04 §4/§6 + T-03 A | typed; adoption leak F-01 |
| Planned task sub-issue (`:957-967`) | T-04 §5/§6 + T-03 A/B | typed |
| Ship-review backlog issue (`cmd_backlog :1410-1429`) | T-06 + T-05 A–E | typed; net-new receipt F-07 |
| Factory parent (`factory_decompose.py:421-425`) | T-08 §6/§8 + T-07 A | typed; adoption leak F-01 |
| Factory task (`:433-437`) | T-08 §7/§8 + T-07 A/B | typed |

## Findings

**F-01 · high · adopted parents get retyped on the next run.** `plan.yaml` T-04 §6 (`:424-427`) says
"for the parent, if the number is already recorded but the typed flag is not set … apply the type" —
and T-04 §7 (`:430-432`) deliberately leaves an adopted parent with a recorded number and **no** typed
flag. The receipt cannot distinguish adopted from created (`gh-sync.py:496-497` / `:857-863` write
`parent` as a bare int), so the second `gh-sync open` types an issue Harness did not create. T-08 §8
(`:653-655`) is worse: it has no adopted-parent exemption at all, and `factory_decompose.py:404-407`
records `--parent` the same way. Test T-03 H only covers the adopting run, so nothing catches it.
**Repair:** record adoption in the receipt (e.g. `typed["parent"] = "adopted"` written in the adopt
branch, or an `adopted: true` flag) and exclude it from both backfills; add T-03 case H2 and T-07 case
F — adopt with `--parent`, rerun without it, assert zero `updateIssue` argv for that node id.

**F-02 · med · T-10's verify passes on a stub.** `verify: python3 tests/manual/probe-issue-types.py |
grep -Eq "^probe-issue-types: (LIVE PASS|CAPABILITY ABSENT) "` (`plan.yaml:700`) is satisfied by a file
whose only statement prints that line. SC-10 is the sole carrier of #1289's live acceptance, so its
task's gate must not be a string match on a constant. It also fails, not skips, when `gh` is absent
(the probe then prints `SKIP`). **Repair:** require the verdict line to name the repo resolved from
`.harness/harness.json github.repo`, and add a second run with `PATH` stripped of `gh` asserting the
`SKIP` verdict — proving the probe actually consults the API.

**F-03 · med · the eighth read-back purpose does not cover what T-10 reads.** R4's row wording is
pinned character-for-character in T-11 §3 and T-12 §1: *"whether a target repository supports native
Issue Types, and which native issue types a repository declares"* — repository-level metadata. T-10 §5
(`plan.yaml:726`) reads back `issue(number:N){ issueType { name } }`, an **issue-level** read, which is
exactly the class DEC-203 bounds. The plan therefore ships an unauthorised read-back. **Repair:** widen
the pinned wording in both copies to include the type assigned to an issue Harness created, or add a
second row for the probe's read-back — either way it is a plan edit, since the wording is pinned twice.

**F-04 · med · the zero-create invocation is untested on two of three commands.** The receipt's §5
measured the real trap: a lazily-called detector prints nothing on a rerun. T-03 case D asserts exactly
one line on a zero-create `open` rerun. T-05 case D asserts zero creates but **not** the diagnostic, and
T-07 has no zero-create case at all — yet T-06 §2 and T-08 §5 both claim "a run that creates nothing
still prints exactly one line". **Repair:** extend T-05 D and add a T-07 case asserting exactly one
`^factory: issue types ` / `^gh-sync: issue types ` line on an invocation that creates nothing.

**F-05 · med · `change_type: feature` on a sub-issue types `Feature`, against the operator's axis.** The
operator classifies by nature: capabilities/enhancements `Feature`, **implementation tasks** `Task`.
D-03 (`:56-58`) reasons that "a planned T-NN of any of those shapes is an implementation task or a
chore" — then D-02 exempts `feature` from that same reasoning, so T-07 case A expects `IT_feature` for a
task sub-issue *inside* a Feature-typed parent. Two Features nested is not what "chores and
implementation tasks become Task" says. **Repair:** either map `change_type: feature` to `Task` on the
sub-issue routes while parents keep `type_for_parent` (a one-line change in T-02 plus T-03 A / T-07 A),
or record the operator's explicit ruling that a sub-issue inherits the capability nature.

**F-06 · low · T-01's red-check is satisfiable by an empty test.** `gh_issue_types` does not exist at
T-01 (no deps), so any file importing it exits non-zero and the verify (`:126-129`) reports "RED as
required" — including a file with zero assertions. SC-05's twelve-plus-three enumeration is then
unenforced by any gate. (T-03/T-05/T-07 do not have this hole: their module exists, so an assertionless
test would go green and fail the red-check.) **Repair:** add to T-01's verify a grep asserting each of
the twelve `change_type` spellings and the three natures appears in the file.

**F-07 · low · the backlog receipt changes compatibility-mode behaviour.** D-13/T-06 §5 make the
receipt unconditional, so in *label* mode a `backlog` rerun no longer duplicates and T-06 §6 prints a
new skipped-item line. Clause 3 says preserve today's behaviour; the operator asked for rerun-safety
only for the create-then-type-fail case. Defensible and honestly recorded in D-13 — but it is
un-granted behaviour change on the compatibility path. **Repair:** either state it in the BRIEF's
compatibility sentence, or gate the receipt read on `state == "available"`.

**F-08 · low · the probe creates a real issue in the operator's repository.** T-10 §5 creates, types,
reads back and closes a live issue labelled `harness`. Nothing in the grilling note or #1289 grants a
live write; #1289 asks for an acceptance *observation*. Unreachable against the pinned repo today
(`issueTypes: null`), so the cost is latent. **Repair:** name the live create in the BRIEF's
verification-gaps block so the operator signs it knowingly, and title-prefix the scratch issue so a
leaked one is identifiable.

**F-09 · low · the compatibility control is in no verify.** T-04 and T-08 tell the member to run
`tests/integration/test-gh-sync.py` / `test-factory-decompose.py` "and report", but their `verify:`
blocks (`:363-364`, `:602-603`) run only the new file. The plan's own stated control for "labels
preserved exactly" is therefore outside every gate. **Repair:** append the control suite to both
`verify:` blocks.

## Open questions for the operator

- **Q1 (blocking, F-05):** does a planned/factory task whose `change_type` is `feature` type as
  `Feature`, or as `Task` like every other implementation task?
- **Q2 (non-blocking, F-08):** is the probe permitted to create and close a throwaway issue in the
  target repository as its live acceptance?
