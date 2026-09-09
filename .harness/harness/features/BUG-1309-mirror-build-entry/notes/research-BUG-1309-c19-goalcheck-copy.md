# c19 goal-check — merge-gate refusal copy at 4857818b — BUG-1309 — 2026-09-09

**BLUF: the shipped copy meets the operator's intent. SC-04 stays MET and does NOT regress; SC-10
stays NOT MET, awaiting the operator's own execution of UAT Step 3. The UAT already matches the
rendered string character for character — NO edit was owed and none was made. R-7 §3 is CONFIRMED:
no criterion text moves, so no BRIEF amendment and no re-signature are owed. One backlog finding,
zero must_fix.**

## 1. The message against the two criteria

`merge-gate.py:192` carries exactly two placeholders, `{feat}` and `{command_line}`
(`{command_line}` built at `:191` as `python3 .claude/skills/harness/bin/gh-sync.py <name>
<realpath(feat_dir)>[ --yes]`). Rendered string = shared-context measurement 2; I did not re-derive it.

- **SC-04 (`BRIEF.md:108-111`) — SATISFIES, no regression.** Its clause is "that single-owner deny
  carries a reason naming the feature and the re-run command". The rendered string names
  `FEAT-9001-uat-scratch` and carries the complete copyable `gh-sync.py open <dir>`. Both survive; the
  criterion never required the recorded `github.build_entry` value be printed. Every other clause of
  SC-04 (ambiguity, era-exempt allow, unpinned repo, gh-unavailable allow) is emitted by
  `merge-gate.py:174/179-180/184/188/194`, all untouched by this commit (measurement 4: 2 files, 3
  hunks).
- **SC-10 (`BRIEF.md:157-159`) — the copy SATISFIES the readability intent, criterion stays UNMET.**
  The sentence leads with the feature id and a plain-English fault, and ends with a runnable command;
  the two phrases the operator judged unreadable (`github.build_entry=<value>`, "no Build entry
  receipt exists for it") are gone. `verify: uat` — only the human closes it (§4 below).

### The `{feat}` non-discrimination (measurement 3) — behaviour met, evidence incidental, BACKLOG

Corroborated at source, not merely accepted: `fixture()` names the feature directory after the
feature id (`test-merge-gate.py:21,28`), and `{command_line}` embeds `os.path.realpath(feat_dir)`
(`merge-gate.py:191`), so `"FEAT-9001-fixture-non-era" in reason` (`:69`, `:102`) stays true with
`{feat}` deleted. **SC-04's behaviour is still met**: the criterion grades what the deny CARRIES, and
at the pin the feature is named twice — once as `{feat}`, once inside the path. What is weak is the
EVIDENCE for the "names the feature" clause, and that predicate at `:68-69` is **pre-existing and
untouched by 4857818b** (the commit re-anchored only `:64-65` and `:99-102`).

**Not a must_fix, for three independent reasons:** (a) the commit did not create or worsen it;
(b) strengthening that assertion requires editing `tests/integration/test-merge-gate.py`, which the
signed carve-out forbids to every agent (`plan.yaml:47-49`, `:73-75`, T-05 `execution_mode`
`:1047-1048`, D-11); (c) SC-04 was already ruled MET on inspected-correct source rather than on
discriminating automated evidence (`notes/research-BUG-1309-c18-sc04-ruling.md:3-6,79`), so this is
the same accepted evidence class, not a new gap. **Backlog finding**, alongside the two already open
in that note: add a distinct-token assertion for the feature name (e.g. a fixture whose directory
basename differs from `feature_id`) so `{feat}` becomes defended, not merely proven.

The commit's own re-anchors ARE discriminating: dropping the sentence reddens `:65`, dropping
`{command_line}` reddens `:68` and `:101` (measurement 3). Suite at the pin: rc=0, 36 ok, 0 FAIL,
matching the c18 baseline (`notes/qa-c18.md` §1).

## 2. UAT copy — already exact, NOTHING CHANGED

Hypothesis in the dispatch: CONFIRMED by my own read.

- **Step 3 quoted block `:161-163`** — joined across the blockquote wrap, character for character the
  measurement-2 string, ending in the resolved `/private/tmp/...` dir, with `:165-166` pre-empting the
  `/private` confusion. Match.
- **Step 3b observe line `:211-214`** — quotes a true contiguous SUBSTRING of the emitted reason
  (`needs its GitHub mirror recovery completed before this merge can continue. Run: python3
  .claude/skills/harness/bin/gh-sync.py open …`), from the same `recovery-required` fixture (`:188`),
  so `recovery_command_for` resolves `open` exactly as in Step 3. No fragment the gate does not emit.
- **Every residual `build_entry` in the note is fixture write or JSON read, never expected gate copy**:
  `:86` (fixture write), `:119-120` (the fixture script's own summary print), `:241`, `:294`, `:305`
  (`json.load` output the operator reads back). No `github.build_entry=<value>` and no "Build entry
  receipt exists" survives as expected gate text anywhere in the note.
- **Step 6/Step 7 untouched.** Note an anchor correction for the record: the `recover-terminal … --yes`
  / not-`open` expectation the dispatch and R-7 §5.3 cite as "Step 6 (`:300`)" is in fact **Step 7,
  `:303`** (`## Step 6` is the now-allowed merge at `:258`). It stays TRUE under the new copy —
  `recovery_command_for` returns `recover-terminal` for the merged station and `:191` appends `--yes`
  — and I did not touch it.

No renumbering, no step added or removed, no PASS/FAIL rule altered. `files_touched: []` beyond this note.

## 3. Does any criterion move? — R-7 §3 CONFIRMED

Read against the criterion text itself: SC-04 (`BRIEF.md:108-111`) and SC-10 (`:157-159`) are both
satisfiable by the new copy and neither requires a word the copy removed. **No BRIEF amendment and no
re-signature are owed.** D-19 (`plan.yaml:330-352`) records the copy and names T-05's intent quote
superseded rather than rewriting it — correct under PRINCIPLES rule 15. No open question here.

## 4. SC-10 — the exact operator action and PASS condition

- **Action:** run UAT Step 3 (`notes/uat-BUG-1309-mirror-build-entry.md:150-177`) in the worktree —
  `python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT recovery-required`, then
  `printf '{"tool_input":{"command":"git merge feature/uat-scratch"}}' | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh`
  (Steps 1-2 first, `:32-148`).
- **PASS condition, quoted `:175-177`:** "**PASS** if the message names the feature, says what is
  wrong, and gives you a command you could run without opening any source file. **FAIL** if you would
  have to go read code to work out what to do — or if no deny appeared at all."

Until they run it, SC-10 is `not_met — awaiting operator execution`. It is not waived, not partial.

## Open questions

- Q1 (non-blocking, backlog): the "names the feature" evidence at `test-merge-gate.py:68-69` cannot
  redden on a `{feat}` deletion. Needs a cycle that may edit the carved-out test file.
