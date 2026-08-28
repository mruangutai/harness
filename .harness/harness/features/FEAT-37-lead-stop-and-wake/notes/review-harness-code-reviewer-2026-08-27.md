# Review — FEAT-37 lead-stop-and-wake — code-reviewer panel — `4e652f9`

**Note on artifact path:** the dispatch named
`notes/review-code-reviewer-panel-2026-08-27.md`; my write domain only permits
`notes/review-harness-code-reviewer-*.md` (`check-domain.sh` denied the named path). Writing here
instead — flagged as an open question below, not worked around.

## BLUF

**PASS.** SC-04 and SC-05 both `met`, evidence below. No `must_fix`. Stage 1 (spec compliance) clean
across the 9-file surface — every change traces to REQ-01..07 or a signed plan decision (D-12/D-13/
D-17), no scope creep, no omission. Stage 2 (quality) found nothing above `low`: the fail-open hunt on
`inflight_registry.py` and `run-unit-tests.sh` came back clean — both were rewritten in this diff
specifically to remove a fail-open the operator measured live (#628 ambiguous-release, and the cwd/root
resolution fallback).

## Scope confirmed

`git -C <worktree> diff --stat 8fc87f8..4e652f9` on the 9 named paths only:
`.claude/skills/harness-team/SKILL.md`, `.claude/skills/harness/bin/inflight_registry.py`,
`.claude/skills/harness/bin/run-unit-tests.sh`, `.claude/skills/harness/bin/test-inflight-registry.py`,
`.claude/skills/harness/bin/test-lead-stop-and-wake.py`, `.harness/harness/docs/DECISIONS-INDEX.md`,
`.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/SPEC.md`,
`.harness/notes/backlog-orchestrator-inoculation-2026-08-27.md`. No `[harness:human]` commits in
`8fc87f8..4e652f9` (`git log` shows none). HEAD not moved.

## SC-05 — `met`

Line numbers re-measured myself via `git show 4e652f9:.claude/skills/harness-team/SKILL.md | cat -n`
(255 lines total). **My numbers agree with the dispatch's corrected table exactly**: `:81`, `:126`,
`:196`.

- **Step 3 framing** (`SKILL.md:81,83`) — "Until every step is terminal, or you halt:" / "This loop
  runs across turns, not inside one." Neutral-to-reinforcing: states the loop crosses turns rather
  than looping in place inside one. No stay-alive reading.
- **Step d** (`SKILL.md:116-124`) — "**Never wait for a member — end your turn.**" (`:116`);
  "Stopping is safe, because the platform wakes you when the member completes — ending your turn is
  HOW you wait" (`:118-119`); inoculation's three clauses present and separable (`:121` refusal
  expected, `:122` end turn again, `:122-123` recurs on later wake).
- **Step e** (`SKILL.md:126-127`) — "**e. Collect returns.** You collect on waking, after the turn
  ended — never by staying alive to receive." Explicit denial of receive-in-place.
- **Step f** (`SKILL.md:139-162`) — `on_fail`/`loop_back` mechanics. No waiting language of any kind.
- **§5 Close out** (`SKILL.md:199-216`) — "Set `status: complete`… write your team digest…" No waiting
  language.

**Sweep**, patterns searched: `wait|poll|stay|alive|receive|busy|idle|remain|loop.?in.?place` (case
-insensitive) over the whole 255-line file. Matches occur **only** at lines 116-131 — the newly
inserted d/e block — and every one of them is the denial ("never wait", "do not poll… do not sleep…
do not restate that you are waiting", "never by staying alive to receive"), never an assertion. Zero
matches in §1/§2 preamble, the Red flags table (`:246-255`), or "Reporting up" (`:217-242`).

**Sensitivity check (a known positive, per instructions):** the same sweep against
`git show 8fc87f8:.claude/skills/harness-team/SKILL.md` returns **zero** matches (confirms REQ-01's
premise — total silence pre-change). Against the pre-`c5e59aa` orchestrator playbook
(`git show c5e59aa^:.claude/skills/harness/SKILL.md`), the identical grep pattern **does** fire —
`:45` "**NEVER WAIT FOR A LEAD. END YOUR TURN.**", `:46` "never poll for it, never sleep, and never
invent activity to stay alive" — proving the sweep pattern catches this exact class of language when
it is present. No surviving stay-alive/receive-in-place/loop-in-place reading found anywhere in the
reviewed file.

## SC-04 — `met`

Clause: `SKILL.md:118-120` — "…ending your turn is HOW you wait, not a way of giving up. **The
dispatch tool will tell you to continue other work in the meantime, and that is not licence to
manufacture activity: this rule overrides it.**"

Tested against the sentence-boundary rule qa's own detector uses (split on `. ` / blank line): this is
one sentence — it names the tool's exact nudge ("continue other work… in the meantime") and denies it
("is not licence to manufacture activity") **and** states precedence ("this rule overrides it"), all
in the same sentence. That is the **stronger** of the two verdicts the dispatch asked me to
distinguish: it *names* the tool's nudge and *denies* it in one sentence, inside the d-to-e region —
not a bare rule that happens to conflict.

**One-line resolution test:** a lead reading only the `Agent` tool's "continue other work… in the
meantime" text and only this clause resolves them the same way — both are present in the lead's
context and the clause explicitly overrides the tool's implied license, so the lead ends its turn
regardless of what the tool text suggested.

## Stage 1 — spec compliance

Every file traces: `SKILL.md` d/e-block → REQ-01/02/03/04; `DECISIONS.md`/`DECISIONS-INDEX.md` DEC-201
→ REQ-05 (heading + scope sentence + index row all name the lead tier, confirmed:
`DECISIONS.md` heading "Neither an orchestrator nor a lead ever waits", scope sentence "the never-wait
rule binds the orchestrator AND THE THREE DOMAIN LEADS"; index row "Neither an orchestrator nor a lead
waits"); `DECISIONS.md`/`inflight_registry.py` bound-qualifier edits → REQ-06 (verified both sites
carry "per consecutive stop sequence" in the same sentence as the "fires… once" claim —
`inflight_registry.py:338-341`, `DECISIONS.md` DEC-199 body); `test-lead-stop-and-wake.py` +
`test-inflight-registry.py` additions → REQ-07 (guards that survive a reword — regex-set matching, not
literal-string matching). `SPEC.md`/`DECISIONS.md` DEC-70 narrowing → plan decision D-17, signed.
`backlog-orchestrator-inoculation-2026-08-27.md` → plan decision D-12 (STRUCK AT SIGNATURE), operator-
approved, filed #903 — per the operator's note, not re-litigated here.

No scope creep found in the 9 files. No omission found against REQ-01..07.

## Stage 2 — quality, fail-open hunt

- `inflight_registry.py` `release()` (line ~247-280): the diff **fixes** a measured fail-open
  (#628 — oldest-pop released the wrong holder's claim). New behaviour: 2+ live claims → refuses,
  returns `0`, removes nothing, reports the count on stderr. Correct direction — ambiguity now blocks
  rather than guesses. `test-inflight-registry.py:case_13_release_refuses_ambiguous` asserts both the
  refusal and that both claims remain on disk untouched — a presence assertion beside the absence
  assertion (DEC-169-shaped).
- `_resolve_root` (inflight_registry.py, CLI): `harness_boundary.resolve_root` wrapped in
  `try/except ValueError → root = None`; a `None` root then fails closed in `main()` ("no checkout
  root…", exit 1). No path where a resolution failure silently proceeds.
- `run-unit-tests.sh`: root resolution now refuses (exit 2) rather than falling back to `pwd`, closing
  the fallback-to-wrong-tree fail-open named in the file's own header comment. The
  discovery-count-binding concern raised in the dispatch is already answered structurally: the "drift
  detector" (loop comparing `test-*.py` glob against the two explicit arrays) and the "KIND CROSS-CHECK"
  (comparing the arrays against `harness.json`'s `test_kinds.integration.detect`) both run
  unconditionally, on every `--kind`, and both exit 2 loudly on any mismatch — an empty or shrunk
  `SCRIPTS` array cannot pass silently, because the drift detector iterates the full glob independent
  of which kind was selected.
- `test-lead-stop-and-wake.py` bound-site occurrence naming (`case_occurrence_{site}_{ln}_{idx}`):
  explicit collision handling for two once-only matches on one line, documented in a comment — no
  finding, just confirms a reviewer read that far.

No `high`/`critical` findings. One `low`, informational only:

- **low** — `test-lead-stop-and-wake.py`'s Red flags / "Reporting up" sections of `SKILL.md` are not
  covered by any automated case (only `--self-check`'s synthetic skeleton and the named case8/case9
  windows are checked). My manual sweep found nothing there, so this is not a defect — just an
  observation that the automated floor stops short of the full-file sweep an inspection review has to
  do by hand each time. Not `must_fix`; style/coverage-shape note only.

## Verdict

```yaml
VERDICT: PASS
DIGEST:
  headline: SC-04 and SC-05 both met with file:line evidence; no scope creep or omission in the 9-file surface; the two rewritten fail-open paths (release() ambiguity, root resolution) are fixes, not regressions.
  sc_status:
    - { id: SC-04, verdict: met, file: ".claude/skills/harness-team/SKILL.md:118-120", evidence: "single sentence names the dispatch tool's \"continue other work…in the meantime\" nudge and denies it (\"is not licence to manufacture activity: this rule overrides it\")" }
    - { id: SC-05, verdict: met, file: ".claude/skills/harness-team/SKILL.md:81,116-124,126-127,139-162,199-216", evidence: "sweep for wait|poll|stay|alive|receive|busy|idle|remain over the whole 255-line file matches only the new denial language at 116-131; zero matches at 8fc87f8; sweep confirmed sensitive against a known positive at c5e59aa^:.claude/skills/harness/SKILL.md:45-46" }
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "8fc87f8..4e652f9"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Dispatch named the artifact path notes/review-code-reviewer-panel-2026-08-27.md; check-domain.sh only permits notes/review-harness-code-reviewer-*.md for this agent. Written to the permitted path instead — should team-config.yaml's routing for this role be updated to match the panel-naming convention, or should dispatches for this role use the agent-name pattern going forward?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/review-harness-code-reviewer-2026-08-27.md
```
