# UI Review — FEAT-41 cycle 4

`review_sha` `64f42ef86b5c388544f34c02a8f9b5831250df73` (`64f42ef8`), merge-base `6ddcac3`. Worked
from a `git archive 64f42ef8` extraction at `/tmp/feat41-c4-ui-2`; worktree left untouched
(confirmed clean before and after). Mode B (post-build). No `DESIGN.md` exists for this feature
and this is a hooks/validators feature with no rendered application UI, so my surface is entirely
operator-facing CLI/hook text, per the dispatch's four measured items below. **Both stages ran**:
stage 1 = spec compliance (REQ-01 "loudly", SC-03, SC-07 against the actual emitted text) below in
§2-3; stage 2 = quality/completeness of that text (does it teach a safe action, is it internally
consistent) in §1 and §4.

## 1. INV-34 remediation text — the one item most likely to be a finding, and it is

`check-state.sh:1141-1147` (source at `64f42ef8`), triggered live via `harness_yaml.load_plan()`
and by reading the emitted `bad.append(...)` string directly:

> `INV-34: <dir> has no plan.yaml, so it has nowhere to record its station — feature.json cannot
> hold one (the schema declares no `status` key). Create a station-only record: `schema: plan/1`,
> `feature:`, `status: <station>`, `station_only: true`, `tasks: []`, written through
> `plan-merge.py apply`. The marker is REQUIRED and is not inferred from an empty `tasks:` — an
> emptied plan is not a station-only record.`

Good: it names the exact keys, states the marker is required (not inferred), and routes through
`plan-merge.py apply` rather than an editor — matches REQ-05's one-writer rule and cycle 3's own
PASS that the literal record it prescribes loads clean (`harness_yaml.load_plan` accepts it — I
re-confirmed this).

**What is missing, and it is the WHEN, exactly what the dispatch flagged**: the message is
unconditional. It never distinguishes the two causes INV-34 can have — (a) a directory that
legitimately never had a tracked plan (predates the format, or a bug opened with none — the case
the source comment at `check-state.sh:1130-1136` reasons about, arguing against *inventing tasks*),
versus (b) a directory whose `plan.yaml` **existed with real tasks and was deleted** (exactly the
BUG-1030 incident the same comment block cites: `T-07 deleted status: Review from BUG-1030 ...
Twelve directories were backfilled with station-only plans`). In case (b), writing a station-only
stub is not remediation, it is **quietly discarding the feature's real task history** behind a
schema-valid record — and once written, INV-34 goes permanently silent, so nothing re-flags the
loss. The message gives no instruction to check `git log -- <dir>/plan.yaml` (or any other
recovery step) before stubbing, and neither does the source comment above it — the caution against
*fabricating tasks* is present, the caution against *discarding real ones* is not.

This is a real gap against PRINCIPLES rule 15 ("never falsify the record") and against this
feature's own stated ethos (REQ-01: refuse loudly rather than silently obey) — a silent write here
would not even be visibly logged as a loss, unlike the sibling "emptied plan" case at
`harness_yaml.py:326-351`, which the code goes out of its way to make *louder* ("AN ABSENCE CANNOT
BE A CREDENTIAL"). The INV-34 remediation text does not carry that same discipline.

**Severity: med.** Written reason: this cannot itself corrupt data — it requires a human (or
agent) to act on the instruction, and it is advisory text, not an automated write. But it
positively teaches an operation with a real, plausible failure mode with no safeguard offered, and
that is squarely what a UI-text review exists to catch. Concrete scenario: `rm
.harness/harness/features/BUG-XXXX/plan.yaml` (whether by accident or a bad Bash command) while
that plan carried real in-flight tasks; `check-state.sh` fires INV-34; the reader follows the
message verbatim, running `plan-merge.py apply` with `tasks: []` / `station_only: true`; the
directory now passes every gate and the feature's real task history is unrecoverable from
`plan.yaml` going forward (recoverable only if the reader independently thinks to check `git log`,
which nothing here prompts).

## 2. Refusal messages — triggered live, quoted verbatim

**`plan-sign-gate.py` (SC-07).** Fired the real gate with a payload carrying `agent_type` and a
`sign-approval` command:

```
Refused: sign-approval writes the approval signature, which is the USER'S and is relayed by
the main session alone (DEC-120). An agent may ask for a signature and be refused; it
cannot write one.

Return awaiting_user with what you need signed. Do not call sign-approval, and do not edit the
approval block by hand — the main session runs sign-approval itself once the user has given
their word:
  python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file <plan.yaml> ...

Every other verb of this tool stays open to you: apply, add-tasks, set-task-station and
set-feature-station. This gate refuses one verb, not the tool.
```
Carries the literal string `sign-approval` (four times) and the sanctioned route
(`awaiting_user`) — SC-07 satisfied. `test-plan-sign-gate.py:93-98` independently asserts both.
**Pass.**

**`check-domain.sh`'s `plan.yaml` write denial (T-09).** Fired the real hook subprocess (reusing
`test-check-domain.py`'s own `_approval_root`/`_fire_write` fixtures, case-3 shape) as an agent
Write of a legal plan:

```
check-domain: DENIED — .harness/harness/features/FEAT-99-fixture/plan.yaml: plan.yaml has exactly
ONE writer, plan-merge.py, because every station value must be validated against the vocabulary
before it lands on disk. An editor write cannot do that, so this is not a shape violation to be
measured — it is a route that no longer exists (FEAT-41 REQ-05, reversing DEC-182).
  Record a task's station:      python3 .claude/skills/harness/bin/plan-merge.py set-task-station
  ...
  Record the feature's station: python3 .claude/skills/harness/bin/plan-merge.py set-feature-station ...
  Add tasks:                    python3 .claude/skills/harness/bin/plan-merge.py add-tasks ...
  Apply a proposal:             python3 .claude/skills/harness/bin/plan-merge.py apply ...
```
This is the residual PB-07 tracks (SC-05 struck, so no criterion asserts this) — I judged it
directly. **It states the REASON, not merely the verb**: "every station value must be validated
against the vocabulary before it lands on disk... it is a route that no longer exists" — a reader
who has never seen this code can tell this is a closed route by design, not a stuck gate, and gets
four concrete next commands. T-09's intent calling this clause load-bearing is discharged in the
actual text, not just in prose. **Pass.**

**Out-of-vocabulary station refusals (REQ-01 "refused loudly", SC-03 "names the value").**
Triggered three independent sites live:
- `factory_config.validate_board` on a `harness.json` declaring `stations:
  [...,'build',...]` (a bad key): `fleet key invalid: github.board.stations — set it to the
  ordered list ['backlog', 'plan', 'ready', 'building', 'review', 'done'] in /tmp/harness.json —
  these six names are FIXED and may not be renamed, reordered or extended...` — names the exact
  key (`github.board.stations`), the exact fix, and the file. **Pass.**
- `plan-merge.py set-task-station --station bogus`: `plan-merge: 'bogus' is not a legal station —
  expected one of: backlog, plan, ready, building, review, done, abandoned` exit 4. **Pass.**
- `check-plan-routes.py` against a fixture plan with `status: sideways` (feature) and `status:
  pending` (task): `VIOLATION top-level status 'sideways' is not one of (...) (case sensitive)` and
  `VIOLATION T-01: status 'pending' is not one of (...) (case sensitive)`. Names the value and,
  for the task case, the task id. **Pass.**

All three name the offending value; REQ-01/SC-03 hold at the pin.

## 3. D-14 documentation sites

Both sites D-14 names are correct at `64f42ef8` and consistent with the code triggered above:
- `SKILL.md:151-154` (`.claude/skills/harness/` and its `.agents/skills/harness/` symlink — one
  file, verified via `git ls-tree`, `.agents/skills` is a `120000` symlink to `skills`, not a
  second copy): `gh-sync.py status <feature-dir> review ... The station argument is LOWERCASE —
  one vocabulary, and gh-sync.py refuses anything else (FEAT-41).` Matches `cmd_status`'s
  `station not in STATION_VALUES` refusal, live-confirmed.
- `SKILL.md:294-297`: `feature.json holds NO status: key (FEAT-41) and no phase: key (DEC-191)...
  One file records the station, and it is the plan.` Matches `feature-schema.json`'s
  `additionalProperties: false` and the removal of `gh-sync.py`'s old `STATUS_VALUES` constant
  (confirmed absent by grep). No contradiction between the two sites, and neither contradicts the
  code. **Pass.**

Non-gating note, **out of this feature's scope**: `references/github-mirror.md` (not one of D-14's
two named sites, and untouched by this diff except one unrelated row —
`git diff --stat 6ddcac3 64f42ef8` shows exactly one changed line, the "a phase transition happens"
row) describes the same abandon-to-backlog event twice with different casing: `returns every card
to the **backlog** station` (line 42, prose/bold, lowercase) versus `An abandoned card is returned
to \`Backlog\` instead` (line 100, code-quoted, capitalized). Both refer to the same GitHub board
write (`gh-sync.py`'s `_place(..., "backlog", ...)`, capitalized to `Backlog` for the actual
GitHub call). This predates FEAT-41 and is not part of D-14's disclosed scope — recorded as a low,
non-blocking observation, not filed as a finding against this feature.

## 4. Generated `ship-review-*.html`

Two exist under this feature's `notes/`: `ship-review-2026-08-29-01.html`,
`ship-review-2026-08-30-01.html`. Their generator, `render-brief.py`, is **unchanged** in this
diff — `git diff --stat 6ddcac3 64f42ef8 -- .claude/skills/harness/bin/render-brief.py
.agents/skills/harness/bin/render-brief.py` returns no output. Per the dispatch's own rule ("If it
did not change, say so and move on") — no rendering check performed, none warranted.

## Verdict basis

Census for items 1-4, as measured: item 1 (INV-34 text) read at the pin and triggered via
`load_plan`; item 2, three refusal families fired live against the real scripts (5 live
invocations total); item 3, both D-14 sites read byte-for-byte and cross-checked against triggered
code behaviour, plus a scoped-out sweep of one adjacent pre-existing file; item 4, one `git diff
--stat` check on the renderer, confirming no change and no rendering to verify. One `med` finding
(§1). Everything else in scope is a **pass**, confirmed by direct execution, not inference.

## Open questions
None blocking my own scope. See DIGEST for the one advisory item.
