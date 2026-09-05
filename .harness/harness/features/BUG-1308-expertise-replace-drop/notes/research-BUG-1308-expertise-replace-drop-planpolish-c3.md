# Plan polish — BUG-1308 cycle 3, the three advisory imprecisions (A1/A2/A3)

**All three closed inside ONE field — `tasks:T-02.intent` — and nothing else in the plan was
touched.** Q3 was settled by widening the case, not by narrowing the criterion, so BRIEF.md was not
edited. `plan.yaml` loads under `safe_load`; `approval.status` is still `pending`; `panel` is
byte-identical in substance (14 findings, 13 `resolved` + 1 `open`, 3 readers — the same before and
after, and the parsed-panel sha256 `9541eaa6…3d35bc38` is unchanged across the write).

## Q1 (A1) — the u13/u14 mis-attribution

Re-derived from the definitions, not the gloss: `u13` is the missing/empty-`section` shape refusal
(plan.yaml T-01 intent, `u13 MISSING SECTION IS A SHAPE REFUSAL`), `u14` is the payload-not-a-list
case (`u14 A PAYLOAD THAT IS NOT A LIST`). case20(a)/(b) are the section cases; case20(c) is the
DIGEST-shaped-mapping case. The closing gloss now reads: *"…(D-02, D-05, SC-04), and u13 is their
unit half; sub-case (c) is the payload-shape refusal, and u14 is its unit half."*

## Q2 (A2) — the analogy that pointed at nothing

Read case8 at `tests/integration/test-expertise-merge.py:259-283`: it regexes `CAPS = {…}` out of two
files and compares the four section caps. There is no vocabulary in it, so *"collected the way case 8
collects its vocabulary"* named a mechanism that does not exist. Chose route (i): the real collection
mechanism is now spelled out in case17's own words — locate, in `NORMALISED`, the ONE pipe-separated
verb list the ops example's `op:` key carries (currently `op: replace # add | replace | merge | drop`
in `.claude/skills/harness-distill/SKILL.md:116`), take each token; **zero or multiple matches FAIL
the case loudly**, never a fallback to an empty or hard-coded set — an empty `CONTRACT` would satisfy
the first direction by construction. That locator is what the three mutation copies operate on, so
inserting `prune` or removing `drop` from that line still moves `CONTRACT`.

The header phrase *"the same idiom as case 8"* was left standing: case8 reads two artifacts as TEXT
and asserts they agree rather than restating a third literal — that IS case17's idiom, and it is
true.

## Q3 (A3) — SC-04 widened at the case, not narrowed at the brief

**Chose (a).** Evidence: T-01 Step A pins the shape refusal line as `MALFORMED OPS <one line naming
the op index, the offending key or verb, and what was expected>` (T-01 `intent`, Step A), and
`cmd_ops` "Print refusal lines to stdout and sys.exit(refusal.code)" (T-01 `intent`, item 2) — the
CLI emits the resolver's line verbatim, so the op index IS genuinely present at the CLI. Narrowing
SC-04 would have deleted an assertion the mechanism already supports. case20(a) now asserts *"…names
BOTH the offending key, the literal token section, AND the op's INDEX in the payload — cmd_ops prints
resolve_ops's refusal lines verbatim, so the CLI line IS the resolver line…"*; case20(b) asserts
*"exit 12, MALFORMED OPS, the literal token section AND the op's index in the payload both named,
sha256 unchanged."* BRIEF.md SC-04 (`:76-81`) is unchanged and is now fully discharged by its own
cases at both layers.

## Scope of the write

One field amended: `tasks:T-02.intent`, via `plan-merge.py amend --expect-sha256
df700855…805044de`. No other task, decision, criterion, `files:`, `verify:`, `depends_on:`,
`traces:`, `panel:`, `approval:` or brief line changed. `git status --porcelain` shows plan.yaml
modified alongside pre-existing cycle-2/3 modifications (BRIEF.md, feature.json, observations,
untracked notes) that this run did not author.

## Open

- None blocking. The plan is ready for signature as far as these three findings go.
