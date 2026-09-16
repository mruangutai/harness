# UI Review C2 — FEAT-56 — operator-surface audit at 9768681c (Mode B)

BLUF: The two split procedures and the four doors are structurally sound — six/three numbered
steps respectively, no stale headings, all eight of T-11's own enumerated dangling step-references
resolved bar one imprecise (non-breaking) wording, negative-token bans (Track A/B, BRIEF/approval/
design-pass/visual-designer, claude --version/2.1.217) confirmed absent by direct grep at the pin.
No finding reaches `high`. Six genuine, non-gating operator-experience defects found, all at
`med`/`low`/`info`. VERDICT: PASS with advisory findings.

## 1. `harness-init/SKILL.md` walkthrough (six-step fresh-checkout procedure)

Read via `git show 9768681c:.claude/skills/harness-init/SKILL.md` (279 lines).

Preflight → Step 1 (eight prerequisites + per-checkout hooks subsection) → Step 2 (instantiate
config) → Step 3 (interview) → Step 4 (delegate to dev-ops) → Step 5 (seed manifest) → Step 6
(verify + restart warning) → `--upgrade`. Confirmed exactly six `### N.` headings
(`grep -n -E "^### |^## "`), no stray `### 7`–`### 9`.

**Nothing asks the operator to register a repo, write a BRIEF, take an approval, or run a design
pass** — confirmed by grep for `Track [AB]`, `BRIEF`, `approval`, `Design pass`,
`harness-visual-designer`, `claude --version`, `2.1.217`, `factory/fleet.yaml`, `register`: the
only hits are the intro's *negative* statement ("does not register a repository… no first BRIEF
yet goes to /harness-plan"), a `dev-ops never writes fleet.yaml` negation, and the --upgrade
section's "BRIEF.md… never touched." All correctly scoped.

**Cross-reference census — T-11's plan.yaml intent claims eight dangling step-references resolved
(counted across 7 bullets, one bullet naming two).** Verified each against the pinned file:
- `before step 2` → now "before you go on" (line 52). RESOLVED.
- `skip to step 2` / `proceed to step 2` → both gone; no residue (grepped `skip|proceed`). RESOLVED.
- `steps 4 and 8 below run with enforcement on` + `step 9 has the one real restart caveat` → now
  "steps 4 and 5 below run *with* enforcement on… step 6 has the one real restart caveat" (line
  146). RESOLVED, correctly.
- `will fail if the brief is pending (step 7)` → deleted outright (no "brief is pending" anywhere).
  RESOLVED.
- `land its merged harness.json through step 2` (in `--upgrade`) → now "through `harness-add-repo`"
  (naming the skill, not a stale number). RESOLVED.
- `which is why steps 4 and 8 work` → **NOT cleanly resolved** — see Finding 4 below.

## 2. `harness-add-repo/SKILL.md` walkthrough (three-step registration procedure, NEW)

Read via `git show 9768681c:.claude/skills/harness-add-repo/SKILL.md` (163 lines). Headings:
Preflight → `### 1.` (land+register, 5 sub-steps) → `### 2.` (interview) → `### 3.` (GitHub mirror
+ board) → "Next: plan the first feature" → Red flags. Confirmed exactly `### 1.`/`### 2.`/`### 3.`,
no `### 4`–`### 9` survivors (`grep -n -E "^### "`).

**Preflight** catches unconfigured-control-plane (bullet 1, routes to `harness-init`) and
missing-`gh` (bullet 3, "STOP: this procedure cannot complete without it") — both present, in
config-first order (control plane → templates → gh → branch/access → not-already-registered).

**Order (D-04):** `default_branch` mentioned before `factory/fleet.yaml` before
`.harness/<segment>/` — confirmed in the opening paragraph and in the numbered sub-steps (land →
register → tree). T-10's own verify checks this by first-line-number comparison; textually
confirmed at the pin.

**Can an operator with no memory of the old combined skill complete a registration from this text
alone?** Mostly yes, with one real gap — see Finding 6.

**"Ends with `--check-product-configs` rather than with a BRIEF" (SC-12 wording)** — the
*substance* holds: the file's last section routes to `/harness-plan` for the first BRIEF, never
writing one itself. But literally, `--check-product-configs` (sub-step 1.4) is not the file's last
executable content — sub-step 1.5 (central-tree creation) and top-level steps 2 and 3 (interview,
GitHub mirror/board) all follow it. This is a wording-precision question for SC-12's own text, not
a defect in the skill; flagged as an open question for whoever grades SC-12 literally vs. in spirit.

## 3. Pair consistency

No contradiction found about which artifact owns which job — both files' opening paragraphs
correctly route to each other and to `/harness-plan`. The 7/8-bullet dev-ops-contract duplication
this panel found previously **stays fixed**: `harness-add-repo` cross-references
"the same dev-ops contract as harness-init's 'Delegate detection to dev-ops' section" rather than
repeating it (`comm -12` sorted-line diff confirms no verbatim multi-line contract survives
duplicated). See Finding 5 for one smaller duplicate that does survive.

## 4. The four doors — reader experience

`.omp/commands/{harness,harness-plan,harness-ship,harness-grilling}.md` vs.
`.claude/commands/*.md`: confirmed byte-identical past a one-line banner
(`diff <(git show …omp…) <(git show …claude…)` → only the banner line differs, for all four).
Banner: `<!-- Generated from .omp/commands/{name}; do not edit. Run
bin/sync-command-adapters.py --apply. -->` — clearly names the source and says don't edit. See
Findings 1 and 2 for two content-level gaps neither `check-omp-port.py` nor
`sync-command-adapters.py --check` can see (lead 2's exact question).

## Findings

**F1 — [med] `.omp/commands/harness-plan.md` and `.omp/commands/harness-ship.md` self-reference
the wrong root.** Both open with "Read `.claude/commands/harness.md` and follow it…" — a
Claude-Code-specific path, hardcoded inside the file that is now the *canonical, provider-neutral*
copy. Confirmed pre-existing verbatim since base `4b5dbb23` (`diff` against base shows zero change
to this line); T-13's own intent says "Change no word of any door's prose in this task," so it
carried the bug into the new canonical home unmodified. Confirmed neither gate can see it:
`check-omp-port.py`'s command-door block (lines ~166–179) only asserts the four `.omp/commands/*.md`
files *exist*, and shells out to `sync-command-adapters.py --check`, which only proves byte-parity
between the two copies — neither inspects whether the canonical prose's own internal references
point at the neutral root. This is precisely the "a wrong canonical root fails exactly as silently
as the bug" case the review brief asks about. Functionally harmless today (content is identical
either way), but it is an internal contradiction of the neutral-root claim and would break the
moment the Claude adapter tree is ever retired. Task: T-13. Writability: `.omp/commands/**` →
main-session-direct.

**F2 — [med] Generated-adapter banner names an unreachable path.** `sync-command-adapters.py:15`'s
`BANNER` constant says "Run `bin/sync-command-adapters.py --apply`." Confirmed there is no
top-level `bin/` directory in this repo (`git show 9768681c: | grep -E "^(bin|\.agents|\.claude|
\.omp)\b"` shows only `.agents/`, `.claude/`, `.omp/`); the real script is
`.claude/skills/harness/bin/sync-command-adapters.py`. A human or agent following the banner
literally from repo root gets "No such file or directory." Stamped identically onto all four
generated `.claude/commands/*.md` adapters (one generator, one constant). Task: T-14. Writability:
`.claude/skills/harness/bin/sync-command-adapters.py` → squad-writable.

**F3 — [med] `harness-grilling/SKILL.md`'s "Onboarding" bullet re-merges the split.** Line ~103,
under "## Done, and what follows": "**Onboarding:** the answers seed `harness.json`, the domain
description, and the first glossary terms." Confirmed unchanged since base (`diff` against
`4b5dbb23` shows only the frontmatter description and one other clause at line 23 changed — this
line was never touched). It blends harness-init's outcome (domain description + glossary, control
-plane-only) with harness-add-repo's outcome (a member's `harness.json`) into one undifferentiated
"Onboarding" bucket — exactly the pre-split model REQ-04 says must not survive. A reader finishing
an `harness-add-repo` interview and consulting this line is told their answers also seed "the
domain description" and "first glossary terms," which T-10's own intent explicitly excludes from
add-repo. `harness-grilling/SKILL.md` is in SC-04's named file set; this line names neither of the
two artifacts correctly. Task: T-12 (file is in its `files:` list; its intent's stated scope — one
frontmatter edit, one clause at line 23 — stopped short of this line). Writability: main-session
-direct.

**F4 — [low] `harness-init/SKILL.md:233` keeps an imprecise "steps 4 and 5" reference T-11's own
plan says should read "step 4 alone."** "...agents that deploy installed before this session
started are spawnable now, which is why steps 4 and 5 work." T-11's intent explicitly reasons this
site is about agent-spawnability, which only step 4 (spawns `harness-dev-ops`) needs — step 5 is a
manual main-session edit (seed the manifest) that spawns no agent. A *different*, legitimately
shared "steps 4 and 5" phrase exists earlier in the file (line 146, about domain-enforcement hooks
being live, correctly applying to both steps), and the mechanical verify's ban pattern
(`steps? [7-9]`) cannot tell the two occurrences apart, so this one slipped through unfixed. Not
functionally blocking — both steps do work without a restart — but a careful reader could
conclude, wrongly, that seeding the manifest needs already-spawnable agent definitions. Task: T-11.
Writability: main-session-direct.

**F5 — [info] Small verbatim duplication survives, of the same class already found and fixed
once.** "**Run this in the main session.** Only the main session can call `AskUserQuestion` — a
subagent has no channel to the user. Delegate the *mechanical detection* to `dev-ops`; never
delegate the interview." is byte-identical across both `harness-init/SKILL.md` and
`harness-add-repo/SKILL.md`, with no cross-reference between them (unlike the dev-ops-contract
paragraph, which `harness-add-repo` correctly references instead of repeating). Low risk given its
brevity and stability, but the same drift-risk pattern the panel already flagged once for the
longer dev-ops contract. Not gating.

**F6 — [med, past SC-12's UAT boundary] `harness-add-repo`'s config-verification step is not
re-run after the data that fills the config arrives.** Sub-step 1.1 explicitly defers filling
`test_kinds` and the GitHub block ("during the technical detection **below**", "during the mirror
question **below**" — i.e., steps 2 and 3, which come later in the document). Yet sub-steps 1.2–1.5
(land → register in fleet.yaml → verify via `--check-product-configs` → create central tree) read
as executed immediately, before step 2 or 3 ever run. Steps 2 and 3 each separately say to re-land
"through step 1" after they add their data, but the document never says whether the
`--check-product-configs` verification (sub-step 1.4) should also repeat — so the *last*-landed,
fully-filled `harness.json` is the one whose reachability the documented procedure never
re-verifies. SC-12's UAT script only requires the operator go "up to the point of the fleet entry"
(~sub-step 1.3), so this sits just past the UAT's ten-minute boundary and would surface only on a
full end-to-end run. Task: T-10. Writability: main-session-direct.

**Not re-filed (already disclaimed):** `templates/README.md`'s Versioning paragraph spells
"`/harness-init --upgrade`" as a slash command. This is exactly the un-slashing defect the BRIEF's
Non-goals section already names as out of scope ("a separate chore… not to be mistaken for
delivered work"). Cited only for completeness of census, not filed as new.

## What only the operator can determine

- **SC-15** — whether an actual OMP session resolves `/harness-plan` from `.omp/commands/` at all,
  vs. some other root. Structurally invisible to source review; the marker-line technique in the
  BRIEF is the only way to tell.
- **SC-11 / SC-12's PASS/FAIL call itself** — I surfaced concrete candidate stumbling points (F3,
  F4, F6) a live ten-minute read might or might not actually trip on; whether they register as a
  stall for a human reading cold is a judgment this review cannot make from text alone.
- Whether `gh` auth / push-access preflight checks in `harness-add-repo` behave as described
  against a *real* candidate repository — I confirmed the bullets exist and are ordered correctly,
  not that they fire correctly at runtime.
- Whether a full (not UAT-truncated) registration run actually hits the F6 ambiguity in practice,
  or whether an experienced operator resolves it by inference without noticing a gap.

## Census / methods

All graded content read via `git show 9768681c:<path>` (never plain `read`), including full
byte-for-bybyte diffs against base `4b5dbb23` for `harness-init/SKILL.md`,
`harness-grilling/SKILL.md`, all four door pairs, and both agent-adapter pairs. Duplication check
used `comm -12` on sorted, blank-stripped lines of both onboarding skills (not grep) to find every
verbatim shared line. `check-omp-port.py` and `sync-command-adapters.py` read directly to confirm
what their checks do and do not assert (F1/F2 basis).
