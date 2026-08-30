# FEAT-38 fold read-back

Base form: `git show 7ebfc9e:.harness/harness/docs/DECISIONS.md`.
Folded form: `git show 2557950:.harness/harness/docs/DECISIONS.md`; the working copy was byte-identical when read.
Every entry below preserves both the governing belief and the evidence that corrected or bounded it. Dates and amendment labels are intentionally left to `git log --follow -- .harness/harness/docs/DECISIONS.md`.

## DEC-11
BELIEF — The policy/capability split survives in “team membership, lead, `consult-when` and `domain` in the manifest; `name`, `description`, `tools`, `model`, `color`, `skills` and `effort` in agent frontmatter.”
FALSIFICATION — The bad capability survives as a correction: “`hooks` is NOT one of the frontmatter capabilities,” because frontmatter `PreToolUse` hooks “do not fire for spawned subagents in this environment, proven across three attempts.”

## DEC-138
BELIEF — The rejected origin-based closure rule remains named: “closing one the feature created, leaving an adopted one open, leaving an unrecorded one open.”
FALSIFICATION — The counterexample remains: “`parent_origin` read **null** on FEAT-34 and FEAT-35,” leaving #728 open after all thirteen children finished; the folded ruling says “Origin no longer decides anything; an open child does.”

## DEC-142
BELIEF — The former dispatch practice remains explicit: “Titles were free text at each dispatching tier.”
FALSIFICATION — The name-field measurement remains: its regex excludes spaces and `·`, so “the `·` separator and the spaces of the title form are illegal in a name.”

## DEC-145
BELIEF — The durable pipeline survives: “Distillation is a three-party pipeline, not diffusion,” with bounded lead candidates and member acceptance or reasoned rejection.
FALSIFICATION — The failed discipline-only control survives: “Where the caps were authored but the checker was not yet deployed, 9 of 15 Expertise files failed it again within a day of being distilled.”

## DEC-149
BELIEF — The retired mission remains described as “a between-features architecture scan … that read the codebase map.”
FALSIFICATION — Its missing substrate remains measured: “the map tier was removed after 35 features never built one — leaving the mission nothing to scan.”

## DEC-152
BELIEF — The rejected rationale remains: putting domain leads in `high` “because they assess what their members return.”
FALSIFICATION — The folded entry says that assignment “has been tried and reversed” because leads route and consolidate while the error-catching work happens in reviewers and the orchestrator.

## DEC-157
BELIEF — The original unit remains: “`cycles_used` counts REWORK ONLY.”
FALSIFICATION — The blind spot remains measured: with first-pass runs contributing zero, “FEAT-03 ran **19 times against a 6-cycle count** and tripped nothing.”

## DEC-158
BELIEF — The rejected extraction test remains: “Keying it on frequency — rare work moves, every-ship work stays.”
FALSIFICATION — Its counterexamples remain: `gh-sync.py` runs every ship and the context probe every wake, yet both are bounded procedures needed only when triggered.

## DEC-171
BELIEF — The former zero-dependency rule remains: “no YAML library, the manifest reader a narrow line scanner so these could run on any machine without an install step.”
FALSIFICATION — The concrete parser failure remains: “the scanner dropped an entire run from `runs` on a legal trailing `# comment`.”

## DEC-174
BELIEF — The superseded factory-workspace reading remains explicit: “that route resolves to NOBODY, or that it is merely unsanctioned.”
FALSIFICATION — The post-removal measurement remains: an undeclared factory-workspace repository makes `check-domain.sh --resolve` exit **2**, not return NOBODY.

## DEC-183
BELIEF — The rejected implementation is still characterized: “The harness was too heavy” because it cloned a workspace and executed workflow bodies.
FALSIFICATION — The deeper boundary remains: `pull_request` runs the workflow from the PR’s own ref, so “one PR edits a step and its guard together.”

## DEC-189
BELIEF — The overstated path count remains visible in the correction: “The argument carries exactly ONE of the four named paths, not two.”
FALSIFICATION — The relocated docs surface remains the reason: `.harness/*/docs/**` now matches the documentor grant after design docs moved to `.harness/harness/docs/`.

## DEC-193
BELIEF — The outside-repository Bash pass-through remains, narrowed rather than removed, and explicitly “holds for two of the three fleet states, not all three.”
FALSIFICATION — The malformed-fleet exception remains measured: “absent 0, valid 0, malformed 0 before and **2** now.”

## DEC-194
BELIEF — The rejected applicability rule remains named: keying applicability to `check-state.sh`’s own path “is wrong by construction.”
FALSIFICATION — The observed consequence remains: init installed that marker in every product, so every product became applicable, held neither layout, and reported `CANNOT VERIFY` forever.

## DEC-181
BELIEF — The misleading earlier reading remains: beginning after the cleanup made the file read “as though the file had always been small.”
FALSIFICATION — The historical measurement remains: “The file was 208-214 lines from April through 2026-07-27; DEC-135 then cut it to 50.”
