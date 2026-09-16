# Goal-check c5 (plan revision c6) — does this plan deliver the operator's stated intent?

**NO — by one criterion, and one only: SC-06 is not provable by any planned test after R3's
narrowing. The remedy is a TASK change, not a criterion change.** Everything else holds: all
eleven REQs are carried, eleven of twelve SCs are gated, `check-plan-routes.py` prints
**`0 violation(s) across 1 plan(s)`** (exit 0), and none of the eleven c4 baseline findings was
broken by c6. All five rulings R1–R5 are present in `plan.yaml` and were verified against the file,
not against pm's account.

Read-only proof — `git -C <worktree> diff --stat` at exit:
```
 .../FEAT-55-issue-types-created-work/BRIEF.md      |   8 +-
 .../observations/harness-pm.md                     |   7 +
 .../FEAT-55-issue-types-created-work/plan.yaml     | 278 +++++++++++++++------
 3 files changed, 208 insertions(+), 85 deletions(-)
```
`BRIEF.md` and `plan.yaml` carry c6's edits only; the sole delta I introduced is +3 lines in my
observations log (c6 left it at `4 +` / `205 insertions`). This note is untracked.
`plan.yaml` sha256 `3e1ffeb71b9a…`, `BRIEF.md` sha256 `36a7c6ab3f28…` (recomputed after my last read).

## Intent reversals across the four artifacts — none

The three ruling notes amend the grilling in one direction only. The T-10 destination thread widens
monotonically: c1 authorises the opt-in probe at all → c2 lets `--create-in` name a repository other
than `github.repo` → c3 R4 exempts that opt-in from the configured-repository availability gate. No
pair settles a question oppositely. R3's four-key narrowing is not a reversal either: the grilling
settles "repository-specific **type-name** overrides", which is exactly what `Bug/Feature/Task/parent`
are; the sixteen internal keys were a plan-side draft nobody ruled.

The one sentence that *was* falsified is BRIEF SC-10's, and it is an artifact written under the
earlier rulings, not an intent artifact. c6 fixed it (§5 below).

## 1. The verbatim question

**Does this plan deliver the operator's stated intent? — NO.** The doubt is named and singular:
BRIEF SC-06 (`BRIEF.md`, "declaring different type names for defect, capability and chore work").

## 2. Roll-call — REQ

| REQ | delivered by |
|---|---|
| REQ-01 all five routes | T-03/T-04 (open parent+task), T-05/T-06 (backlog), T-07/T-08 (factory); each task's `traces:` carries REQ-01 |
| REQ-02 per-repo capability, no inferred ids | T-01 assertions 7–8, T-02 `classify_capability`/`capability_query_args`, T-04 §3 `detect_issue_types`, T-08 §4 "Capability is per target repository and is never inherited" |
| REQ-03 defaults + name overrides | D-12 (four legal keys, "NET-NEW key inside the existing github block"), D-18 role mapping, T-02 `LEGAL_OVERRIDE_KEYS = ("Bug", "Feature", "Task", "parent")`, T-01 assertions 5/6/12. **Delivered** — REQ-03 asks that the type NAMES be renameable, and the four keys are exactly those names |
| REQ-04 total mapping | T-01 assertions 1/2/4 (twelve change_types, three natures, `UnknownWorkNature`), T-02 `DEFAULT_TYPE_BY_CHANGE_TYPE` "All twelve keys spelled out" |
| REQ-05 labels preserved, one diagnostic | T-03 C/D/I, T-05 C/D, T-07 G; T-04 §3, T-06 §2 "FIRST statement of cmd_backlog", T-08 §5 "ONCE, unconditionally" |
| REQ-06 no bug/chore when active | T-03 B, T-05 B, T-07 B; T-04 §5, T-06 §4, T-08 §7 |
| REQ-07 refuse before creating | T-03 F, T-05 G, T-07 I; T-04 §4, T-06 §3, T-08 §6 |
| REQ-08 not recorded until typed; rerun recovers | T-03 F/G, T-05 E, T-07 E; T-04 §6, T-06 §5, T-08 §8 |
| REQ-09 amended authority | T-11 (DEC-138/DEC-203 + index), T-12 (github-mirror.md, main-session-direct) |
| REQ-10 never type what we did not create | T-03 H/H2, T-07 F, T-04 §7 `"adopted"`, T-08 §8; traces now on T-03/T-04/T-07/T-08 (R5) |
| REQ-11 runnable live probe | T-09 (`issue_types_live` registration), T-10 (probe) |

## 3. Roll-call — BRIEF SC

| SC | verdict |
|---|---|
| SC-01 per-issue typing, open+backlog | delivered — T-03 case A (`IT_feature` parent, `IT_bug`, `IT_task`×3), T-05 case A (three items, per-issue) |
| SC-02 factory parent+tasks | delivered — T-07 case A |
| SC-03 null capability ⇒ identical labels, one diagnostic | delivered — T-03 C (five issues, "EXACTLY ONE line"), null-returning fakes at T-03/T-05/T-07 fake specs |
| SC-04 no hard-coded type ids | delivered (inspection) — T-02 `classify_capability` returns `declared` name→id; all ids flow from it |
| SC-05 table-driven, red first | delivered — T-01 assertions 1/2/4 + `verify:` "UNEXPECTED PASS: this test must be RED before T-02" |
| **SC-06 declared names for defect, capability and chore** | **NOT DELIVERED — see below** |
| SC-07 labels under active types | delivered — T-03 B/C, T-05 B, T-07 B |
| SC-08 per-command refusal, zero creates and zero type calls | delivered — T-03 F, T-05 G, T-07 I, each now with a named zero-`updateIssue`-against-the-remnant assertion |
| SC-09 crash between create and type | delivered — T-03 G, T-05 E, T-07 E |
| SC-10 live probe verdicts | delivered as a plan (T-09 + T-10); stays `not_met` until the operator records a verdict — see §5 |
| SC-11 DECISIONS amended | delivered — T-11 |
| SC-12 adopted issues never typed | delivered — T-03 H/H2, T-07 F; SC-12 byte-unchanged by c6 |

### SC-06 — still provable *in principle*, not provable *by this plan*

SC-06 requires declared (non-default) names for **defect, capability and chore work**, on a task
sub-issue and a parent, with `evidence: integration`. The only two integration override fixtures are:

- T-03 case E — `{"Bug": "Defect", "parent": "Epic"}`, and it **asserts the chore leg carries the
  default**: "the config task's and the feature task's still carry `IT_task`".
- T-07 case D — `{"Bug": "Story", "parent": "Story"}`, plus an explicit instruction **"Do not
  override Task in this case"**.

T-05 (backlog, the only route with an `enhancement`→`Feature` nature) has no override case at all.
So the chore leg has no fixture anywhere, and the capability leg is proved only through the `parent`
key, never through the canonical `Feature` key. Part of an enumeration is not met.

**The criterion is not unmeetable.** A single legal config — `{"Bug": "Defect", "Task":
"Maintenance", "parent": "Epic"}` — declares all three and is exactly what D-12 permits; "renaming
Task renames every task issue at once" is a consequence SC-06 does not forbid, and it makes the
assertion *stronger* (three keys, three distinct type ids). **Remedy = TASK change**, cheapest at
T-03 case E: widen its override map with `"Task": "Maintenance"`, assert the config and feature tasks
carry `IT_maintenance`, add `Maintenance IT_maintenance` to that task's `available` fake node list,
and add the new literal to T-03's `verify:` required-string loop. T-07 case D's isolation argument can
stay as it is. This is undone work, not an unmeetable criterion — route it to the build lane, not to
the operator.

## 4. Route violations

`python3 .agents/skills/harness/bin/check-plan-routes.py <FD>/plan.yaml` (no `--help`; the tool takes
the plan path positionally and prints `ERROR: --help does not exist` otherwise). Tail, verbatim:

`OK T-12: declared main-session-direct (.claude/skills/harness/references/github-mirror.md ungranted)`
then **`0 violation(s) across 1 plan(s)`**, exit 0. **Count printed by the tool: 0.** Matches the c4
baseline. c6 moved no path and deleted none — every `files:` list is byte-unchanged (only `intent:`,
`traces:`, and four `decisions:` values were amended), so there is no old path to re-check.

## 5. BRIEF SC-10's c6 edit — before / after

Before:
> **An environmental skip is not a verdict and never satisfies this criterion**: no `gh` on PATH,
> `github.sync` false, an unpinned repo, or a failed capability query all make the probe report
> nothing about the repository, so they are outside the three verdicts and are never read as a
> pass — SC-10 stays unmet until one of the three is recorded.

After:
> **An environmental skip is not a verdict and never satisfies this criterion**: no `gh` on PATH, a
> failed capability query, or — on the default invocation, which reports on the configured
> repository — `github.sync` false or an unpinned repo, all make the probe report nothing about the
> repository, so they are outside the three verdicts and are never read as a pass — SC-10 stays
> unmet until one of the three is recorded. Under the explicit create opt-in the
> configured-repository availability gate does not apply, because the repository reported on is the
> one the operator named.

**Still falsifiable.** The three verdicts, the "never a pass from a fixture" clause and the
"stays unmet until one of the three is recorded" bar are untouched; the edit only scopes two of the
four skip conditions to the invocation they actually describe, which is precisely what R4 changed in
T-10 §1 ("THE EXPLICIT OPT-IN IS EXEMPT FROM THE CONFIGURED-REPOSITORY AVAILABILITY GATE"). The host
gate — absent `gh`, failed `gh auth status` — still applies on every invocation, and T-10's `verify:`
PATH-stripped leg still asserts it. The edit did not weaken the criterion into unfalsifiability.

## 6. The eleven c4 baseline findings — re-anchored on content, all still closed

| F | verdict | re-verified content anchor (c6 text) |
|---|---|---|
| F-01 high | closed | T-03 H/H2 "the rerun backfill must skip an adopted parent forever, not once"; T-07 F "the marker is still \"adopted\", never True and never \"created\""; T-04 §7 `rec["typed"]["parent"] = "adopted"`; T-08 §8 `factory.setdefault("typed", {})["parent"] = "adopted"` |
| F-02 med | closed | T-10 `verify:` repo leg `grep -Eq "^probe-issue-types: (CAPABILITY ABSENT\|CAPABILITY PRESENT) $repo "` and PATH-stripped leg `skip=$(env PATH=/usr/bin:/bin …)` — byte-unchanged by c6, and still correct under R4's host gate |
| F-03 med | closed | the two 511-char rows (T-11 "eighth read-back purpose" body, T-12 "character for character" body) recomputed: both length 511, string-identical, sha256 `7f065a7a5225` — same value c4 recorded |
| F-04 med | closed | T-03 D "still EXACTLY ONE line matching \"^gh-sync: issue types \"… the invocation that prints zero if the detector is called lazily"; T-05 D "EXACTLY ONE argv" query on a zero-create rerun; T-07 G "EXACTLY ONE line matching \"^factory: issue types \"" |
| F-05 med | closed | D-18 "a TASK SUB-ISSUE, planned or factory, types as Bug when its change_type is bugfix and as Task for every other change_type INCLUDING feature"; T-03 A "IT_task for the FEATURE task (D-18…)"; T-07 A "no task issue on any route ever carries IT_feature" |
| F-06 low | closed | T-01 `verify:` `grep -q "UnknownWorkNature" tests/unit/test-issue-types.py \|\| { echo "MISSING the unrecognised-value assertion"…` |
| F-07 low | closed | T-06 §5 "it exists ONLY on the available path… Where the state is not \"available\", cmd_backlog behaves byte for byte as it does today"; T-05 C/F unchanged. R2 changed the *writer primitive* inside §5, not its availability gate |
| F-08 low | closed | D-19 "creates nothing by default"; T-09 "never register the create opt-in flag in cmd, and never add an argument to it" |
| F-09 low | closed | T-06 `verify:` runs `tests/integration/test-gh-sync.py`; T-08 `verify:` runs `test-factory-decompose.py` and `tests/unit/test-factory-gh.py` |
| N-01 high | closed | D-20 provenance vocabulary reproduced verbatim in T-04 §6 and T-08 §8 ("ABSENT — provenance is UNKNOWN. NEVER typed"), graded by T-03 J and T-07 H ("ABSENT PROVENANCE IS NEVER TYPED") |
| N-02 low | closed | T-04 §4 "THE REQUIRED SET IS NOT ONLY WHAT WILL BE CREATED: add the type of every already-recorded key that section 6 will backfill"; T-08 §6 "THE REQUIRED SET ALSO COVERS THE BACKFILL". R1's remnant fixtures now *exercise* both, which strengthens N-01/N-02 rather than disturbing them |

## 7. R1–R5 verified against `plan.yaml`, not against pm's account

- **R1** — T-03 F seeds `501` with `github.typed[...] = "created"` and asserts the remnant "still holds
  501 and github.typed for it is still exactly the string \"created\""; T-05 G seeds `"bug:a defect"`
  → `601`, `typed false`, and asserts it unchanged plus "holds no entry for the chore item or the
  enhancement item"; T-07 I seeds `701` → `"created"` with "THE REMNANT IS UNCHANGED". Ordering
  statements present: T-04 §6 "It runs only after section 4's refusal check has passed"; T-08 §8
  "before the create branch and AFTER step 6's refusal check has passed". Case F's closing prose "and
  this case is what fails when it does" now has a non-empty backfill set, as claimed.
- **R2** — D-13 "written through the established locked atomic writer, harness_merge.locked_update";
  T-06 §5 "Every state change goes through harness_merge.locked_update(path, transform)… never a
  plain truncating dump". Acceptance stated, not implementation. ✔
- **R3** — D-12 four legal keys + the corrected "NET-NEW key" claim; D-02 "renames the canonical Task
  key… there is no per-change_type override key"; T-01 a5 (incl. the negative
  `type_for_change_type("bugfix", {"bugfix": "Defect"}) == "Bug"`), a6 (illegal key dropped), a12
  (`github.issue_types.Task`); T-02 `LEGAL_OVERRIDE_KEYS`; T-03 E and T-07 D re-keyed; T-04 §4 /
  T-06 §3 / T-08 §6 all say "the CANONICAL override key… never a change_type". No surviving
  change_type- or nature-keyed override outside the two deliberate negatives. ✔ — with the SC-06
  consequence in §3 above, which the narrowing itself created.
- **R4** — T-10 §1 splits host gate from configured-repository gate, verbatim as claimed; residue (a)
  at §6 ("resolve the type a real create would use — `gh_issue_types.type_for_parent(overrides)` read
  from the same harness.json") is untouched, as pm stated. ✔
- **R5** — T-07 `traces: [REQ-01, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08, REQ-10]`; T-08 adds REQ-02.
  ✔

**One inaccuracy in pm's own c6 account, for the record:** its opening paragraph says "one qualifying
edit to BRIEF.md **SC-12**"; the edit is to **SC-10** (its own later section says so correctly, and
the diff carries a single hunk inside SC-10). SC-12 is byte-unchanged. No plan consequence.

## Open questions

- **Q1 (blocking the "YES"):** SC-06's chore leg. Task change at T-03 case E as specified in §3, or
  the operator narrows SC-06. My grade is task change; the criterion is meetable as written.
- **Q2 (carried from c4, non-blocking):** three panel findings still carry stale dispositions
  (`PF-60f3544b…` `awaiting_user`, `PF-08da2089…` and `PF-8b585322…` `batched_to_signature_review`)
  after being ruled. c6 did not touch `panel:`, correctly. Who moves them — a pm write dispatch, or
  the main session's `approval.rulings`?
