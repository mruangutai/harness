# Receipt — harness-dev-ops — stalestrings-eng

**BLUF:** All three assigned/reported false per-product-copy claims replaced with the
true central model (one control-plane clone, many product repos, each with its own
harness.json read from its own default branch). Conclusions and the `panel finding F2`
/ `BUG-1071 panel finding F2` attributions preserved verbatim. No code changed —
comment/config-string edits only. All acceptance checks pass, including the third
string's, run in this follow-up dispatch. The Q1 I raised on the prior pass (sibling
occurrence in `_handoff_done_when_baseline_note`) is now fixed and closed, per lead
authorization confirming it is the last live occurrence in the tree.

## 1. check-state.sh (comment block, lines 373–381 pre-edit)

Before (`check-state.sh:373-374`, verified at HEAD via Read):
> `# THE BOUNDARY IS PER-PROJECT CONFIG, NOT A LITERAL (panel finding F2). This file is`
> `# COPIED INTO EVERY ONBOARDED PROJECT by /harness-init, so a hardcoded date would export`

After (`check-state.sh:373-374`, post-edit):
> `# THE BOUNDARY IS PER-PROJECT CONFIG, NOT A LITERAL (panel finding F2). One`
> `# control-plane clone runs this script against MANY product repositories, each`
> `# carrying its own `.harness/harness.json`, read from that repository's own default`
> `# branch, so a hardcoded date would still export one repository's history as another's`

Conclusion (the 2026-08-31 consequence sentence and the upgrade-config.py
additive-merge sentence, `check-state.sh:376-380`) kept verbatim, only the false premise
sentence was rewritten. Block still spans `# WHY AN ERA GUARD EXISTS AT ALL` (line 364)
through `_era_cfg = read(...)` (now line 384, unchanged), `#`-prefix and line-width style
preserved (all new lines ≤ 86 chars incl. `# `).

## 2. .harness/harness.json `_panel_era_start_note` (line 4)

Before (verified via Read at line 4):
> "...null means this project has no pre-panel era, so every approved plan is graded —
> the right value for a project onboarded after FEAT-45. **check-state.sh is copied into
> every onboarded project, so this MUST be per-project**: a hardcoded date would export
> one repository's history as another's gate (BUG-1071 panel finding F2)."

After (line 4):
> "...null means this project has no pre-panel era, so every approved plan is graded —
> the right value for a project onboarded after FEAT-45. **Each repository's
> harness.json is its own, read from that repository's own default branch, so this MUST
> be per-project**: a hardcoded date would export one repository's history as another's
> gate (BUG-1071 panel finding F2)."

Conclusion ("this MUST be per-project" / the hardcoded-date consequence) and the
`(BUG-1071 panel finding F2)` attribution kept verbatim. No other key touched;
`panel_era_start` value (line 5, `"2026-08-31"`) unchanged.

## 3. .harness/harness.json `_handoff_done_when_baseline_note` (line 6) — Q1, now fixed

Before (verified via Read at line 6, tail sentence):
> "It is per-project because check-state.sh is copied into every onboarded project; a
> global list would export this repository's history as another's policy."

After (line 6, tail sentence):
> "It is per-project because each repository's `harness.json` is its own, read from
> that repository's own default branch, so the baseline list is scoped to the
> repository whose history it describes; a global list would export this repository's
> history as another's policy."

Same false premise as the two fixed in the prior pass (check-state.sh is copied into
every onboarded project — it is not; it lives and runs only in the control-plane
clone). Conclusion ("a global list would export this repository's history as another's
policy") kept verbatim; only the reason clause was rewritten. Rest of the note (frozen
list, `a12aa4e9` merge-base citation, `git ls-tree` derivation, INV-17 sentence, MUST
NEVER GROW rule, D-08 reference) unchanged — confirmed byte-identical except the one
clause. `handoff_done_when_baseline` array (lines 7–154, 147 entries) unchanged.

**Q1 resolution:** fixed under this follow-up dispatch, authorized by the lead after
confirming (tree-wide sweep) this is the last LIVE occurrence — all remaining hits are
archival record (closed-feature plans, receipts, review/research notes) and out of
scope by design.

## Acceptance checks

1. **JSON validity:** `env -u HARNESS_AGENT_TYPE python3 -c "import json;json.load(open('.harness/harness.json'))"` → exit 0.
2. **Bash syntax:** `env -u HARNESS_AGENT_TYPE bash -n .claude/skills/harness/bin/check-state.sh` → exit 0.
3. **Behavioral parity (before/after check-state.sh):**
   - Baseline captured by swapping in `git show HEAD:...check-state.sh` in place (not via
     `/tmp` copy — a bare `/tmp` copy breaks `harness_boundary` module resolution
     alongside the script, which is a false negative, not a real baseline; caught this
     and redid it correctly), ran it, then restored my edited file.
   - BEFORE: exit `1`, 1349 lines (`/tmp/cs-before.txt`).
   - AFTER (my edited script, restored): exit `1`, 1349 lines (`/tmp/cs-after2.txt`).
   - `diff /tmp/cs-before.txt /tmp/cs-after2.txt` → **empty, exit 0**. No output-volume
     change; my edit is comment-only as intended.
4. **Unit tests:** `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh --kind unit` → **exit 0**. Exactly 4 `^FAIL ` lines, all from
   `tests/unit/test-factory-claim-mutation.py` (BUG-1290 5a/5b/5b/5c) — the documented
   by-design failures. No FAIL lines from any other file.
5. **git status --porcelain:** shows only `.claude/skills/harness/bin/check-state.sh`,
   `.harness/harness.json` (mine), `.claude/skills/harness/templates/harness.json`
   (main session's concurrent work, untouched by me), plus concurrent peer artifacts
   (`observations/harness-pm.md`, `notes/research-FEAT-56-goalcheck-ship-c0.md`,
   `notes/uat-FEAT-56.md`) and this receipt — none of which I wrote or touched. No commit
   made.

## This-pass acceptance checks (string 3, `_handoff_done_when_baseline_note`)

6. **JSON validity (re-run):** same command → exit 0.
7. **Diff-key isolation:**
   `env -u HARNESS_AGENT_TYPE python3 -c "import json,subprocess;a=json.loads(subprocess.run(['git','show','HEAD:.harness/harness.json'],capture_output=True,text=True).stdout);b=json.load(open('.harness/harness.json'));print(sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k)))"`
   → `['_handoff_done_when_baseline_note', '_panel_era_start_note']`, exactly the two
   authorized keys, nothing else. `handoff_done_when_baseline` array membership
   unchanged (confirmed by this same key-diff: it does not appear).
8. **check-state.sh parity vs. prior dispatch:** `env -u HARNESS_AGENT_TYPE
   .claude/skills/harness/bin/check-state.sh` → exit `1`, `wc -l` **1349** — identical
   to the prior dispatch's recorded values (exit 1, 1349 lines). Discovery volume
   unchanged; not a FAIL.
9. **Unit tests (re-run):** `env -u HARNESS_AGENT_TYPE
   .claude/skills/harness/bin/run-unit-tests.sh --kind unit` → **exit 0**. Same 4
   `^FAIL ` lines from `test-factory-claim-mutation.py` (BUG-1290 5a/5b/5b/5c), no
   other-file FAILs.
10. **git status --porcelain (re-run):** `.harness/harness.json` (mine, string 3 now
    included), `check-state.sh`, `templates/harness.json` (main session's), this
    receipt, and the same concurrent peer artifacts as before
    (`observations/harness-pm.md`, `notes/research-FEAT-56-goalcheck-ship-c0.md`,
    `notes/uat-FEAT-56.md`) — none authored by me. No commit made.
