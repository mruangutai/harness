# SC-11 read-back — DEC-159, DEC-198, DEC-201 fold

Method: pre-fold at `git show 141eca6:.harness/harness/docs/DECISIONS.md`; folded read from working
tree at the stated absolute worktree path. Cross-checked the whole diff via `git diff 141eca6 --
.harness/harness/docs/DECISIONS.md` (artifact://2176) to catch anything outside the paragraphs the
documentor's table cited. All three claimed folded spans verified byte-accurate against the current
working tree (3674-3745, 5601-5669, 5809-5941 — the header-to-header boundaries match exactly).

## DEC-159 — PASS

- Governing belief present: `DECISIONS.md:3727-3729` — "delivery was once
  `.claude/skills/harness/bin/context-watch-hook.py`, a PostToolUse hook registered in
  `.claude/settings.json` on the `Write|Edit|Bash` matcher".
- Falsifier present: `DECISIONS.md:3726-3730` — "No Claude hook is registered for this any more, and
  none is to be proposed again... FEAT-44 (issue #923) deleted that file and removed the
  registration — the capability changed host, it was not retired."
- Turn-count nudge still deferred: preserved verbatim in substance (~3732-3735). Advises-never-refuses
  survives at `:3726` ("The warning advises and never refuses; the orchestrator decides.").
- Dropped, judged DEFENSIBLE: the retired hook's exact plumbing — "PostToolUse fires after the tool
  has already run, so its exit 2 carries text back to the orchestrator and stops nothing" — is gone,
  not restated. It describes the retired mechanism's internals, not the falsified claim itself (which
  does survive); the current delivery path is separately and fully described. The literal quote "this
  advises only; the orchestrator decides" is paraphrased rather than quoted — substance intact.

## DEC-198 — PASS (both falsified claims)

- Claim (a) — 200000 sourced to `context-watch.py`, retired because it read Claude sidecars while
  `.omp/config.yml` disables Claude discovery: present at `DECISIONS.md:5607-5610`, re-homing-not-
  redefinition clause at `:5611-5612`.
- Claim (b) — an earlier amendment draft asserted `.harness/harness.json` LACKED the key, which would
  have contradicted the entry's own un-amended paragraph: present at `DECISIONS.md:5615-5619`, citing
  anchors `:169`/`:170`.
- Anchor independently re-read via Python (not grep, per the corrupted-grep warning):
  - line 169: `"orchestrator_context_warn_tokens": 200000,`
  - line 170: `"_orchestrator_context_warn_tokens_rationale": "INFORMATIONAL, NOT A GATE. ..."`
  Matches the folded entry's citation and the lead's prior check.
- Miss-path set, all SIX members present verbatim at `:5606-5607`: file missing, unreadable, not JSON,
  no `budgets` dict, key absent, value not a number (bools excluded).
- No measured item dropped for this entry.

## DEC-201 — PASS (the highest-risk entry)

- The nuance holds: `DECISIONS.md:5875-5878` — "Its two-call constraint was CORRECT and died with the
  mechanism rather than being found wrong ... A claim that was right and became inapplicable is not a
  claim that was refuted." This is the exact shape the criterion demanded and it is not flattened.
- Governing belief (old nonce+grep, "needed no new code"): `:5872-5875`. Falsifier/replacement
  (`ctx.sessionManager.getSessionFile()`, no nonce/probe/second call): `:5865-5870`.
- No new supersession: `:5870-5872` states DEC-204's existing supersession without extending it —
  confirmed against the diff, which only touches this paragraph and the amendment removal, nothing
  else in the entry.

**Six-item evidence table:**

| # | Item | Status | Pointer |
|---|---|---|---|
| 1 | measured on ONE OMP build, twice, one machine, 2026-08-28 and 2026-08-29 | PRESENT | `:5881-5882` |
| 2 | probe + raw output committed at `FEAT-44-omp-context-advisory/evidence/README.md` | PRESENT (path verified to exist in tree) | `:5882-5883` |
| 3 | version-floor risk — later OMP may rename/drop the accessor | PRESENT | `:5883-5884` |
| 4 | `probe-omp-session-accessor.py` dispatches a real subagent, fails-never-skips | PRESENT (path verified to exist in tree) | `:5885-5886` |
| 5 | MANUAL check, not CI — needs omp binary + live credentials, CI has neither | PRESENT | `:5886-5888` |
| 6 | one build's observed behaviour, not a timeless OMP API property | PRESENT | `:5888-5889` |

- Untouched-by-diff, confirmed line-for-line via `git diff 141eca6`: never-wait ruling, the `echo
  hold` incident numbers (354/450, 341 `echo hold`, the 13-call/12-string breakdown), the three
  2026-08-23 probes, the 1057.1s data point with its dispatch-level-override limit, the threshold
  bands, and the lineage paragraph. None of these fall inside any diff hunk for this entry.
- Dropped, judged DEFENSIBLE: the retired mechanism's own verification detail — "Measured end to end
  at `569d417`, resolving a live orchestrator to its own row in about a second. Zero matches and
  two-or-more matches both SKIP the check for that wake" — is gone, not restated. This corroborated
  the retired nonce+grep design's correctness with a commit SHA and a duration; the qualitative
  reasoning it supported (why one call can't work) is preserved verbatim, and the replacement
  mechanism carries its own complete, separately-sourced evidence trail (the six items above). Not a
  loss of the falsified claim or its falsifier — a loss of one retired-mechanism's corroborating
  measurement, not required to survive by the entry's own two-part test.

## Verdict

Three of three PASS. No must_fix. Two minor advisory drops noted above (DEC-159's exit-code-2
plumbing detail, DEC-201's `569d417`/duration/skip-behaviour detail) — both judged defensible: neither
is the falsified claim or its falsifier, both describe internals of a fully-retired mechanism whose
core reasoning and replacement are otherwise completely recorded.
