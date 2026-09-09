# Goal-check — the AMENDED plan vs the operator's stated intent — BUG-1309, cycle c1

**Does this plan deliver the operator's stated intent? Qualified yes.** Graded at
`lanes.resolved_at: 4e8f5ea1`. Both c0 blocking gaps are genuinely closed. Five of the eight settled
bullets are delivered outright, three are partial, none is missing. One NEW exposure the amendment
itself created is blocking for signature: the era-exempt skip lives only in T-06, so T-04 and T-05
refuse every pre-existing sync-enabled feature and name a remedy that exits 2. Authority:
`/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-mirror-build-entry-2026-09-06.md`,
not BRIEF.md. This note SUPERSEDES `…-goalcheck-plan-c0.md`.

## Settled bullets — one row each, re-read at 4e8f5ea1

| # | Settled bullet | Carried by | Verdict |
|---|---|---|---|
| 1 | Ship = post-merge terminal phase | T-08 (github-mirror.md block + row), T-03 ship message, T-07, T-09 | delivered |
| 2 | Build entry = signed-plan transition running `open`; never Ship | T-08 (SKILL.md new step 1; trigger cell replaces the `ab4d2fdc` phrase), T-02, T-09 | delivered |
| 3 | Build refuses when the local outcome is absent; proceeds on a recorded temporary failure | T-04 (`plan.yaml:317-352`) | **partial — E1** |
| 4 | Enabled sync → `opened` / `recovery-required`; config-contract errors and partial writes block Build | T-02 steps 4–5 (`:185-202`), D-04, T-01 | **partial — E2** |
| 5 | Disabled/unconfigured sync → `not-applicable`, gates nothing | T-02 step 5, T-04 (`:357-359`), T-05 step 1, T-06 first skip, T-07 sync guard | delivered |
| 6 | `recovery-required` → rerun idempotent `open`; the user's merge action refused until a normal receipt | T-05 (`:432-448`), D-02, D-07, T-02 idempotence | **partial — E1** |
| 7 | Legacy recovery = terminal receipt only, never historical sub-issues | T-03 (`:249-265`), D-05, D-03 | delivered |
| 8 | Legacy recovery during an outage stays non-terminal, keeps its worktree | T-03 skip funnel (`:267-270`) + T-07 (`:634-645`) | delivered |

**E1 and E2 are the only two closing clauses in this note.** Both are one clause each; both are below.

## 1 — The two c0 blocking gaps: both ACTUALLY closed

**(a) T-05/D-07 fail-open.** Closed. Step 3 now carries "THE GH ROUTE MAY FAIL … That is not a
verdict" and falls back to the local `rev-parse` (`plan.yaml:425-428`); step 5 states the deny "is
earned by the local file" (`:434-436`) and, flatly, "There is no branch in this script that denies on
a read failure" (`:448`). D-07's `choice:` now reads "FAILS OPEN on a GitHub read failure" (`:84`).
The test list replaced the drafted deny-on-unresolvable case with two offline `GH_BIN` cases,
including one asserting the deny reason does NOT carry the gh failure text (`:489-492`).
Consequence: a GitHub outage no longer denies every `gh pr merge` in the repo. R1 satisfied.

**(b) T-04/D-08 station-based command.** Closed. The absent branch is now keyed on "the feature's OWN
recorded station, never by whether it is merged" (`:320-325`), resolves through
`feature_schema.recovery_command_for(feat_dir)` (`:329`), and the `recover-terminal` line "must not
contain the token `open` at all" (`:343-344`). T-06 carries the identical rule for INV-37's own
message (`:529-548`) — the residue the c1 follow-up closed. The string "already merged" is gone from
T-04. R2 satisfied.

## 2 — The amendments' own new exposures

**(i) The three refusals do NOT share one rule — and that is E1, the blocking one.** The classifier is
shared for the COMMAND only. The FIRING condition diverges: T-06 skips a feature in
`BUILD_ENTRY_ERA_EXEMPT` (`:522`); **T-04 and T-05 have no era skip at all.** So every one of the ~76
pre-existing sync-enabled feature directories — none of which can carry `build_entry` — is Build-refused
at `cmd_start_task` and merge-denied by merge-gate, and because era membership makes
`recovery_command_for` return `recover-terminal` (`:574`), the named remedy is `recover-terminal`,
which T-03 refuses at **exit 2** when the feature already records a milestone AND a parent (`:263-265`).
Concrete: FEAT-55 — this bug's own subject — records milestone 52, parent 1289, 12 issues and no
`build_entry`; resuming any task on it, or merging its branch, is refused with a command that refuses.
No named command clears it. 48 of the 65 legacy `feature.json` files record a milestone, so this is the
majority case, not an edge.
**Closing clause (E1):** give T-04's absent branch and T-05 step 5 the SAME era skip T-06 makes —
"a feature whose directory basename is in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` continues / exits 0" —
so all three refusals fire on one rule from the one shared source.

**(ii) Ordering: no task's `verify:` is unpassable in the declared order.** `depends_on` is
T-01[] → T-02, T-06; T-02 → T-03, T-05; T-03 → T-04, T-07; T-06 → T-04, T-05; T-04..T-08 → T-09.
Each `verify:` runs a suite whose fixtures are self-contained: T-05's allow-on-`recovered-terminal`
case is a feature.json fixture value and does not need T-03; T-07 fakes gh-sync's output. One
non-blocking risk, not an ordering one: T-04's `verify:` greps the SUITE'S STDOUT for `build entry`
(`:312`), so it passes only if a case name prints that phrase — the refusal text living in the source
does not satisfy it. Same shape as T-02/T-03/T-06, which the doer controls; worth one word in the
intent, not a signature gate.

## 3 — The four delegated decisions, and SC-01

D-01 (`:59-61`), D-02 (`:63-65`), D-03 (`:67-69`), D-04 (`:71-73`) are unchanged at c1 and each is
still the simplest durable behaviour consistent with settled policy: absence must be meaningful
because no legacy `feature.json` carries the field and the era guard depends on that; a state-based-only
merge refusal produces exactly bullet 6 and an age knob would produce no behaviour the state check
does not; `recover-terminal --yes` mirrors `cmd_abandon`'s report-and-ask, which bullet 7's
"explicit operator-approved" requires; and recording NOTHING after a partial remote write is what
makes bullet 4's two cases separable from the local receipt alone.

**SC-01 recheck — E2, still open, and now blessed by the BRIEF.** Verified at source: T-02 step 5 still
passes `build_entry="not-applicable"` to BOTH config-resolver skips, naming the
"github.repo is not pinned" one explicitly (`plan.yaml:195-198`); T-01's schema description repeats it
("`github.sync` is false or absent, **or `github.repo` is unpinned**", `:127-128`); and BRIEF SC-01 now
asserts it as correct (`BRIEF.md:80-85`). That skip is reachable ONLY when `github.sync` is true — the
resolver tests sync first — so it is precisely a local configuration error under enabled sync, which
settled bullet 4 says BLOCKS Build. As written, such a project becomes an approved no-mirror project
and Build proceeds. **The plan gets this wrong.**
**Closing clause (E2):** in T-02 step 5, pass `build_entry="not-applicable"` to the
`github.sync is not enabled` skip ONLY; the `github.repo is not pinned` skip passes nothing, leaving
the field absent — the state that already blocks — with T-01's description and SC-01 restated to match.
(Bullets 4 and 5 do collide on this case — "unconfigured GitHub sync" could be read to cover it. The
ruling is the operator's; what the plan must not do is resolve it silently, which is what it does now.)

## 4 — DEC-138 conformance, per refusal

| Refusal | Decides on | Verdict |
|---|---|---|
| T-04 Build refusal | LOCAL — `rec["build_entry"]` from `load_recorded` (`:317-318`); classifier reads feature dir name + plan.yaml (`:571-579`) | conforms |
| T-05 merge deny | LOCAL — step 5 reads the located `feature.json` only (`:432-436`); the gh read locates the feature and never decides, with a local fallback (`:425-428`) | conforms |
| T-06 INV-37 | LOCAL — `feature.json` + `harness.json` + `plan.yaml` (`:520-534`) | conforms |
| T-07 retention (not a refusal, same posture) | LOCAL — `feature.json` read with `json.load` (`:634-645`) | conforms |

**No refusal reads GitHub to decide.** Zero not-delivered rows arise from item 4.

## 5 — The destination

**(a) Forward: yes.** For a feature created from this change onward, Build entry runs `open`
(T-08 SKILL.md step 1), the outcome is recorded (T-02), and every path that could lose it is caught —
Build refuses on absence (T-04), the merge is denied (T-05), INV-37 reports a terminal feature with no
receipt (T-06), and the worktree survives (T-07). Nothing is silent.

**(b) The BRIEF's recording is honest, with one stale sentence.** `BRIEF.md:140-147` names all 17
sync-enabled directories with no milestone by id, calls them KNOWINGLY UNRECOVERED, states the
guarantee is forward-only and that each is recovered only by an explicit operator-approved
`recover-terminal`. That is an honest disclosure of what is not covered. One correction is owed, and
it is non-blocking: `BRIEF.md:11-13` still says the operator's late-`open` workaround "would create a
milestone and twelve historical task sub-issues" — measured, it already ran; FEAT-55 records
milestone 52, parent 1289 and 12 issues. FEAT-55 is unreported, not unmirrored, and the conditional
now reads as a risk that was avoided.
**The destination sentence as the operator wrote it — "A sync-enabled feature never silently loses its
mirror lifecycle" — is only forward-only-satisfied.** The 17 keep a lost lifecycle that no gate names,
by deliberate scope boundary the BRIEF states.

## Open questions

- **Q1 — E1, blocking for signature.** One clause (item 2i). The operator should also confirm they
  accept that every legacy feature is thereby exempted from the merge gate, not just from INV-37.
- **Q2 — E2, blocking for signature.** One clause (item 3), plus which of bullets 4/5 owns the
  unpinned-repo case. That ruling is the operator's, not pm's.
- **Q3 — non-blocking.** `BRIEF.md:11-13` conditional (item 5b); T-04's stdout-grep `verify:` (item 2ii).

## Not graded here

`check-plan-routes.py`, the `depends_on` acyclicity, and the T-04/T-05 string checks were measured by
the orchestrator on this plan and were NOT re-run. `plan.yaml` and `BRIEF.md` were not written by this
run; the c0 note was not modified.
