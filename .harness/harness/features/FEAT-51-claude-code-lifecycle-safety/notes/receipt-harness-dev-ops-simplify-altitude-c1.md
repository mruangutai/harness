# SIMPLIFY — ALTITUDE angle — FEAT-51 (0bc57c88..HEAD)

**BLUF:** 3 findings, all `leave` or `briefing-row`, 0 `fold-in`. Depth is mostly right:
`quarantine.py` is a thin CLI correctly delegating to `inflight_registry.py`/`plan-merge.py`/
`harness_merge.py`, and the orphan-write *predicate* lives once, authoritatively, in
`inflight_registry.py`. The two real altitude costs are (a) the DEC-210 guard tests pin the
DECISIONS.md *prose*, not the enforcement *behaviour* — confirmed, as asked, not news — and
(b) the human-readable refusal *message* (not the predicate) is hand-duplicated across
`check-domain.sh` and `plan-sign-gate.py`. Both touch DEC-174-frozen files, so both are
`applicable: report-only`; no apply is possible or attempted this run.

## F1 — DEC-210's guard tests pin WORDS, not BEHAVIOUR (the assigned question)

- **File/line:** `.claude/skills/harness/bin/test-gen-decisions-index.py:872-1006` (the three
  `test_dec_210_*` functions + `_dec_region` helper), asserting against
  `.harness/harness/docs/DECISIONS.md:6495` and `DECISIONS-INDEX.md:210`.
- **Summary:** all three tests do literal substring/whole-word matching on DECISIONS.md/
  DECISIONS-INDEX.md prose (`"check-domain.sh"`, `"plan-sign-gate.sh"`, `"quarantine.py adopt"`,
  `\bBash\b`, a `". "`-split "same sentence" heuristic for `plan.yaml`+`plan-merge.py`, and
  `"Claude Code"` in the index ruling half). None of the three ever imports or executes
  `check-domain.sh`, `plan-sign-gate.py`/`.sh`, or `quarantine.py`.
- **Concrete cost — what reddens on a pure reword:** an author who legitimately rephrases the
  entry without changing the enforcement it describes reddens a test for no behavioural reason —
  e.g. writing "the domain guard" instead of naming `check-domain.sh` fails F1's clause 1;
  restructuring the plan.yaml/plan-merge.py sentence across a colon or semicolon instead of
  `". "` fails clause 2's brittle sentence-split heuristic; saying "Anthropic's CLI" instead of
  "Claude Code" fails the index-row test. None of these reword scenarios touch behaviour.
- **What stays green on a real regression:** if `check-domain.sh` or `plan-sign-gate.sh` actually
  stopped enforcing the boundary (e.g. the PreToolUse registration in `.claude/settings.json` were
  dropped, or `orphan_write` were made to always return `False`), all three DEC-210 tests would
  stay fully green — they never run those scripts, only read prose about them.
- **Alternative:** none needed — see verdict below. If ever hardened, the direction would be a
  behavioural harness (spawn a fake orphan claim, invoke `check-domain.sh`/`plan-sign-gate.py`
  against it, assert exit 2) rather than tighter prose regexes, which only relocates the same
  word-coupling problem.
- **Why this is correct as-is, not a defect:** DEC-210's own entry states plainly that
  `check-domain.sh`, `plan-sign-gate.sh` and `quarantine.py` are "each... verified by its own
  explicit test script rather than by the gates under change" (`test-check-domain.py`,
  `test-plan-sign-gate.py`, `test-quarantine.py` — all pre-existing/updated elsewhere in this
  diff, not touched by T-08). Those tests exercise the real predicate
  (`inflight_registry.orphan_write`/`quarantine_rel`) end-to-end. T-08's three tests have a
  narrower, different job: stop the DECISIONS.md entry from silently losing a fact (dropping one
  of the two gate names, or splitting the compound plan.yaml/plan-merge.py claim into two
  unrelated sentences that no longer jointly assert the fact) — a doc-fidelity guard, not a
  behaviour guard. DECISIONS.md's own header states it is written "in its own voice", i.e. free
  prose by design, so a mechanized check on it can only ever anchor to today's wording; a stronger
  semantic check isn't achievable without parsing intent, and this repo's existing precedent
  (`test-gen-decisions-index.py`'s pre-existing tests, and the repository Expertise's own G-12
  entry on the six code-grade refusal strings) already treats word-anchored assertions against a
  frozen authority record as an accepted, structural residual rather than a fresh defect.
- **applicable:** report-only (the test file is squad-writable, but the coupling being asked
  about is the *design* of a settled, already-reviewed T-08 task — reworking it would be new
  scope, not a simplify-pass apply).
- **Verdict: leave.**

## F2 — Orphan-refusal *message text* is hand-duplicated across the two gates; the *predicate* is not

- **Files/lines:** `.claude/skills/harness/bin/check-domain.sh:1695-1701` (quarantine refusal
  block under the Write/Edit hook) vs. `.claude/skills/harness/bin/plan-sign-gate.py:400-414`
  (quarantine refusal block under the Bash hook).
- **Summary:** both gates correctly call the *same* authoritative predicate
  (`inflight_registry.orphan_write`, `.quarantine_rel`, `.canonical_artifact` — one home, no
  restatement) to *decide* whether a write is orphaned. But each then hand-assembles its own
  stderr message telling the operator what happened and what to do — two independently worded
  paragraphs that both explain "canonical but no live claim… write to quarantine instead… becomes
  canonical only when a resumed parent runs `quarantine.py adopt`", built with different string
  templates and different field order.
- **Concrete cost:** a future edit to the refusal wording (e.g. clarifying the discard-is-legal
  caveat, or fixing a typo) that only reaches one of the two files leaves the other route giving
  the operator a stale or inconsistent explanation for the identical refusal — exactly the "several
  statements that can drift" case altitude review exists to catch. It has already drifted once in
  form even though not yet in substance: `plan-sign-gate.py`'s message branches on `tool ==
  ADOPT_TOOL` to substitute a different remedy line, a case `check-domain.sh`'s copy has no
  equivalent for (it only ever refuses Write/Edit, never a Bash `quarantine.py adopt` call), so the
  two are not simply copy-paste twins but a real behavioural fork of the *same* explanatory text.
- **Alternative:** a single `inflight_registry.refusal_message(rel, agent, feature,
  quarantine_rel, tool)` (or two small functions, one per gate's needed shape) added to
  `inflight_registry.py`, called from both `check-domain.sh`'s embedded Python and
  `plan-sign-gate.py` (both already `import inflight_registry`), so the prose lives in the one
  module that also owns the predicate it describes.
- **applicable:** report-only — `check-domain.sh`, `plan-sign-gate.py`/`.sh`, and
  `inflight_registry.py` are all in the DEC-174-frozen, non-writable set for this feature.
- **Verdict: briefing-row** (worth a backlog row for whichever squad next touches the enforcement
  layer; not appliable now, and not large enough to justify reopening DEC-174's freeze for this
  feature).

## F3 — SUSPENDED/quarantine conduct is restated near-verbatim in both playbooks

- **Files/lines:** `.claude/skills/harness/SKILL.md:42-53` (orchestrator playbook, step 4) vs.
  `.claude/skills/harness-team/SKILL.md:126-135` (team playbook, lead's async-boundary rule).
  Both added/reworded in `f260b5fb` (T-05), same commit, same day.
- **Summary:** the same rule — end a live-child turn only with `VERDICT: SUSPENDED` + an
  `awaiting:` list, take no polling/heartbeat action, the registry blocks a replacement parent
  while the claim is live, and on waking run `quarantine.py list`/`adopt`/`discard` before
  deciding anything — is written out twice, in different prose, once per playbook.
- **Concrete cost:** two independent prose statements of one behavioural contract can drift (one
  already omits the phrase "and nothing else" the other has, though not yet a substantive gap).
  Confirmed each side has its own bespoke regex test (`test-orchestrator-playbook.py:161-171`,
  `test-lead-stop-and-wake.py:194-213`) checking its own copy — there is no test asserting the two
  playbooks agree with each other.
- **Why this is not a fresh defect:** this exact duplicate-statement pattern already existed for
  the *prior* wording of the same rule before T-05 touched it (both files already had a "never
  wait — end your turn" paragraph, per DEC-201, before this feature). Each playbook is read
  standalone at spawn by a different agent role, and DEC-17 ("`shared_context` stays minimal")
  deliberately rejects a shared cross-playbook include as context bloat — so there is no
  established mechanism in this repo for one playbook to reference the other's prose at read time,
  and building one would be a repo-wide progressive-disclosure redesign, not a fold-in local to
  this diff.
- **Alternative:** none proposed for this pass; the honest fix (a shared, injected rule fragment)
  reopens DEC-17, which is out of this feature's scope.
- **applicable:** report-only — both `.claude/skills/harness/SKILL.md` and
  `.claude/skills/harness-team/SKILL.md` are named DEC-174-frozen for this feature.
- **Verdict: leave.**

## Explicit answers to the other seeded questions

- **`quarantine.py`'s home relative to `inflight_registry.py`/`plan-merge.py`:** correct.
  `cmd_adopt`/`cmd_discard` in `.claude/skills/harness/bin/quarantine.py:100-165` delegate
  plan.yaml's merge to `plan-merge.py apply` (subprocess, exit code surfaced verbatim) and the
  other three canonical artifacts to `harness_merge.locked_update`; it reads constants
  (`CANONICAL_ARTIFACTS`) from `inflight_registry` rather than restating them. `quarantine.py` is a
  thin caller carrying no capability that belongs in the modules it calls. No finding.
- **Is the quarantine-refusal *rule* stated once authoritatively?** The decision predicate
  (`orphan_write`, `quarantine_rel`, `canonical_artifact`) is stated exactly once, in
  `inflight_registry.py`, and both gates call it rather than reimplementing it. Only the
  human-facing *message* is restated — see F2.

DIGEST: findings_count=3 (0 fold-in, 1 briefing-row, 2 leave, all report-only).
