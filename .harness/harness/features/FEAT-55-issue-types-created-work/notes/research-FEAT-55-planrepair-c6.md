# FEAT-55 — plan revision c6 — the operator's five rulings, applied

**All five rulings are in, in one revision, through `plan-merge.py amend` only. Nothing else wrote
plan.yaml.** Twelve amends across four decisions and eight tasks, plus one qualifying edit to
BRIEF.md SC-12 that R4 made necessary. `approval:`, `panel:` and `## Approval` are untouched;
`approval.status` is still `pending`. `check-plan-routes.py <plan>` exits 0, 0 violations.
`git diff --stat` under the feature dir: `BRIEF.md` (+8/-... 8 lines) and `plan.yaml` only.

Every amend used `--show` to obtain the sha256, then `--expect-sha256` + `--value-file`.

| # | key | id | field |
|---|---|---|---|
| 1 | decisions | D-02 | choice |
| 2 | decisions | D-12 | choice |
| 3 | decisions | D-12 | because |
| 4 | decisions | D-13 | choice |
| 5 | tasks | T-01 | intent |
| 6 | tasks | T-02 | intent |
| 7 | tasks | T-03 | intent |
| 8 | tasks | T-04 | intent |
| 9 | tasks | T-05 | intent |
| 10 | tasks | T-06 | intent |
| 11 | tasks | T-07 | intent + traces (`--yaml-value`) |
| 12 | tasks | T-08 | intent + traces (`--yaml-value`), T-10 intent |

## R1 — PF-df3caaeb (high): the three partial-Type refusal fixtures get a remnant

Remedy (a) only. Zero CASE-marker edits, zero `verify:` edits on account of R1. No new cases, no new
routes.

- **T-03 case F** (`plan.yaml:636`, was `:609`). Before: "fresh fixture". After: feature.json
  pre-records the BUGFIX task's number `501` with `github.typed[<tid>] = "created"` — type `Bug`,
  which the `partial` fake declares, so it is a real member of the T-04 §4 backfill set. Added: zero
  updateIssue argv carrying a node id derived from 501, **named separately**, and the remnant's
  recorded number and provenance are identical after the refusal (`501`, still exactly `"created"`).
- **T-05 case G** (`plan.yaml:~908`, was `:862`). Same shape, in the form this route has: the backlog
  receipt is pre-seeded with `"bug:a defect"` → number `601`, `typed: false`. **Decision:** the
  backlog route has no `"created"` string — `typed: false` beside a recorded number IS its
  created-but-not-yet-typed provenance (the state T-05 case E asserts a crashed run leaves), and
  T-06 §5's rerun apply is its backfill. `Bug` is declared by `partial`. Added: zero updateIssue
  against 601, and the receipt afterwards holds exactly that one entry, `typed` still `false`.
  The old clause "NO backlog-issues.json exists afterwards" had to change — the fixture now seeds
  one; it is replaced by the stronger "holds exactly the seeded entry and no entry for the other two
  items".
- **T-07 case I** (`plan.yaml:~1122`, was `:1046`). factory.yaml pre-records the bugfix task's number
  `701` with `factory["typed"][tid] = "created"`. Added: zero updateIssue against 701, and the
  remnant unchanged. The pre-existing "records no parent number and no task issue number" became
  "…other than the seeded remnant".

**Consequence checked, as instructed:** T-03 case F's prose *"and this case is what fails when it
does"* now reads TRUE (`plan.yaml:654-655`). It was inert before — a fresh fixture made the backfill
set empty. No silent rewording was needed.

**Two ordering statements were added so the assertion has a correct implementation to pass against**
— T-04 §6 ("the backfill runs only after §4's refusal check has passed") and T-08 §8 ("before the
create branch AND after step 6's refusal check"). Without them the spec never says the order the
new assertion grades, and the assertion would still be ungradeable.

## R2 — PF-1286544c (med): the backlog receipt uses the established atomic writer

Anchors re-verified in the real file at this worktree before writing: `load_recorded` is
**gh-sync.py:471**, `save_recorded` is **gh-sync.py:806**, the zero-byte-window defect and its fix
are narrated at **gh-sync.py:441-449**. `save_recorded` routes through
`feature_json_write.write_feature_json` (DEC-199), which is a thin wrapper over
**`harness_merge.locked_update`** (`harness_merge.py:121`) — fcntl lock on the sibling `.lock`,
same-directory tempfile, fsync, `os.replace`. `write_feature_json` refuses a non-feature.json path
(code 9), so the primitive the net-new receipt must name is `harness_merge.locked_update`.

- **T-06 §5** (`plan.yaml:~1006`): "Write it with a plain json.dump of the whole document after every
  state change" → every state change goes through `harness_merge.locked_update(path, transform)`,
  explicitly not `open(path, "w")` + `json.dump`, and not a second lock/rename primitive.
  **Acceptance stated, not implementation**: a crash at any instant leaves the receipt byte-identical
  to its old content or completely written to its new one — never truncated, empty or a prefix,
  because an empty receipt reads as "nothing recorded" and duplicates the issues REQ-08 forbids.
- **D-13 choice** carries the same requirement and the same acceptance, so the decision (not only the
  task) records it.

## R3 — PF-595ce69d (low): four canonical override keys, and the sweep

D-12 is now: a flat map at `github.issue_types` with exactly four legal keys — `Bug`, `Feature`,
`Task`, `parent` — keyed by canonical type NAME; any other key is ignored and the default applies.
**The factual error is corrected in the same edit:** `github.issue_types` is a NET-NEW key, not an
existing one. Re-verified: `grep -n issue_types /Users/molchairuangutai/GitHub/harness/.harness/harness.json`
returns nothing (exit 1); that file has a `github` block at `:357` and no `issue_types` key, and
D-16 keeps it out of the shipped template.

Dependents swept:

- **D-02**: "The override key feature stays legal…" (false) → "…renames the canonical Task key, one
  of D-12's four override keys; there is no per-change_type override key." D-02's actual mapping
  ruling (feature → Task on a sub-issue, Feature on a parent) is unchanged.
- **D-12 because**: records why four and not sixteen (renaming Task repo-wide would need eleven
  change_type keys plus `chore` in lockstep; a partial set splits one role across two declared types).
- **T-01 assertion 5** (`plan.yaml:~406`): overrides re-expressed canonically —
  `{"Bug": "Defect"}`, `{"Task": "Story"}`, `{"parent": "Epic"}`, `{"Task": "Maintenance"}` — plus a
  new negative: `type_for_change_type("bugfix", {"bugfix": "Defect"}) == "Bug"`, a change_type key is
  ignored. **`Defect`, `Story`, `Epic`, `Maintenance` all survive, so T-01's `verify:` string loop
  needs no edit.**
- **T-01 assertion 6**: `overrides_from_config` drops an illegal key —
  `{"github": {"issue_types": {"bugfix": "Defect"}}}` → `{}`.
- **T-01 assertion 12** (`plan.yaml:441`): `github.issue_types.chore` → `refusal_text("owner/name",
  "Maintenance", "Task")` naming `github.issue_types.Task`.
- **T-02**: `LEGAL_OVERRIDE_KEYS = ("Bug", "Feature", "Task", "parent")` added; both resolvers now
  resolve the canonical default first and look the override up **by that name**;
  `overrides_from_config` drops every key outside the four; `refusal_text`'s `config_key` documented
  as one of the four.
- **T-03 case E** (`plan.yaml:~630`): `{"bugfix": "Defect", "parent": "Epic"}` →
  `{"Bug": "Defect", "parent": "Epic"}`. Assertions (IT_defect, IT_epic, IT_task) unchanged and still
  reachable, so T-03's `verify:` loop needs no edit.
- **T-07 case D** (`plan.yaml:~1057`): `{"bugfix": "Story", "parent": "Story"}` →
  `{"Bug": "Story", "parent": "Story"}`; the trailing "do not assert an override on the feature key"
  gloss (a key that no longer exists) → "do not override Task here, it would rename all three task
  issues at once". `IT_story` survives, so T-07's loop needs no edit.
- **T-04 §4 and T-08 §6**: `refusal_text(..., key)` — "key is the change_type or the literal parent"
  → "key is the CANONICAL override key… never a change_type, which the configuration does not accept
  and which would name a repair that cannot be made."

**No `verify:` string-loop entry pinned a key literal that stopped existing**, so no verify was
edited at all. Proof of the sweep, run against the revised files:

```
python3 -c "<walk every scalar of plan.yaml except panel:, regex
  issue_types\.(bugfix|feature|logic|…|chore|enhancement) | \{\"(bugfix|chore|feature|…)\": >"
  -> 4 hits, all legitimate:
     T-01 the negative assertion {"bugfix": "Defect"} == "Bug"  (a change_type key must be ignored)
     T-01 the overrides_from_config drop case
     T-02 DEFAULT_TYPE_BY_CHANGE_TYPE  (internal table, not an override map)
     T-02 DEFAULT_TYPE_BY_NATURE       (same)
grep -n 'github\.issue_types\.[A-Za-z_]*' plan.yaml BRIEF.md
  -> :258 (inside panel:, the finding's own text — not edited), :441 github.issue_types.Task,
     :554 the generic f-string {config_key}.
```

No surviving reference anywhere in plan.yaml or BRIEF.md to a change_type-keyed or
backlog-nature-keyed override. BRIEF REQ-03 and SC-06 were re-read and remain TRUE under the
four-key surface — they speak of overriding the type NAMES, which is exactly what the four keys do —
so R3 required no BRIEF edit.

## R4 — T-10 §1: the opt-in is exempt from the configured-repository gate

`plan.yaml:~1340` (was `:1157-1160`). §1 now splits the gate: **no `gh` on PATH or a failing
`gh auth status` still SKIPs on every invocation** (a host gate), while **`github.sync false` or an
unpinned `github.repo` SKIP only when no `--create-in TARGET` was supplied.** With the flag, neither
condition ends the run; the configured repository is simply not consulted for reachability.

**Residue (a) is untouched.** `plan.yaml:1389` still reads "resolve the type a real create would use
— `gh_issue_types.type_for_parent(overrides)` read from the same harness.json", verbatim.

## R5 — PF-3626edaf: `REQ-10` added to T-07 and T-08 traces

`amend --field traces --yaml-value`. T-07 is now `[REQ-01, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08,
REQ-10]`; T-08 is now `[REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07, REQ-08, REQ-10]`. Nothing
else.

## BRIEF.md — the one edit, and the sentence R4 falsified

**Sentence made false by R4**, in BRIEF.md SC-10, at what was `:153-157`:

> "**An environmental skip is not a verdict and never satisfies this criterion**: no `gh` on PATH,
> `github.sync` false, an unpinned repo, or a failed capability query all make the probe report
> nothing about the repository…"

Under R4 the probe with `--create-in TARGET` reports on the TARGET even when `github.sync` is false
or the repo unpinned, so that clause no longer holds. Now (`BRIEF.md:153-159`) the `github.sync` and
unpinned-repo clauses are scoped to the default invocation, and one sentence states the opt-in
exemption. The rule the sentence exists to carry — an environmental skip is never a pass — is
unchanged. `## Approval` untouched, still `pending`.

## LEAVE roll-call — each unruled finding still reproduces

| Finding | Anchor checked (post-revision) | Reproduces |
|---|---|---|
| PF-56a2ce7a provenance marker in BRIEF SC-12 | `BRIEF.md:168` SC-12, `adopted` at `:171` | yes — SC-12 body untouched |
| PF-45294813 T-06 verify omits test-gh-issue-types.py | verify `plan.yaml:945-947` runs backlog + gh-sync only; intent `:952` still says "run test-gh-issue-types.py too" | yes |
| PF-e27f1c30 T-05 case F three-more-create-argv | `plan.yaml:903` "three MORE \"issue create\" argv" | yes — case F verbatim |
| PF-0c12a033 `adopted` is inert | `plan.yaml:777` (T-04 §6) and `:1238` (T-08 §8) still list `"adopted"`; T-03 H/H2 at `:666-676`, T-07 F unchanged | yes |
| PF-9a71cb9a duplicated 511-char eighth-purpose row | D-08 `plan.yaml:76`; T-11/T-12 untouched | yes |
| PF-62b2b8ae two SKIP wordings, one query_failed state | `plan.yaml:1382` and `:1386` — both wordings verbatim | yes |
| PF-e74a2da8 c5 verify loop is file-global | T-03 verify `plan.yaml:572` unchanged | yes |
| PF-1280cd8f residue (a) foreign TARGET, local overrides | `plan.yaml:1389` verbatim | yes |

No ruled edit collided with any of them.

## What I decided (and why it was mine to decide)

1. **T-05's remnant is `typed: false`, not the string `created`.** The backlog receipt has no
   `created` vocabulary — the ruling's "declared-type remnant that the backfill set would pick up" is
   `{"number": 601, "typed": false}` on that route. Reversible, and named in the case text so a
   reviewer can object.
2. **Added the backfill-after-refusal ordering to T-04 §6 and T-08 §8.** R1's new assertion grades an
   ordering the spec did not previously state; without it the remedy is untestable. Inside R1's
   scope, not beyond it.
3. **`overrides_from_config` DROPS an illegal key rather than refusing.** R3 says "do not expose"
   internal keys; a refusal would turn a stale config into a hard failure on an unrelated run.
   Recorded as T-01 assertion 6 so it is graded.
4. **T-05 case G's "no backlog-issues.json afterwards" clause was replaced, not deleted** — the
   fixture now seeds one, so the byte-level "nothing was recorded before the refusal" guarantee is
   carried by "holds exactly the seeded entry and no other".

## Open questions — none blocking

- **Q1 (non-blocking):** T-07 case D now overrides only `Bug` and `parent`. BRIEF SC-06 asks for
  "defect, capability and chore work". Under the four-key surface, proving the chore leg means
  overriding `Task`, which renames every task issue at once — so SC-06's three-way wording is
  awkward against the canonical surface. Not ruled, not touched, and the panel may well raise it.
