# Review — PR #1251 (BUG-671-answers-provenance)

VERDICT: **FAIL**

## Stage 1 — spec compliance / internal consistency

**Everything the commit message claims about scope was independently verified true**, except one
gap the fix itself introduces:

1. **team-config.yaml grant claim — TRUE, verified against the actual matcher.**
   `harness_boundary.matches()`/`classify()` (imported directly by `check-domain.sh`, the real
   runtime hook) has no exclusion/deny syntax — confirmed by reading `glob_to_re`/`matches`/
   `classify` in full. The orchestrator's `.harness/*/features/**` grant, which ends in `/**`,
   translates to a regex whose `.*` crosses `/`, so it already matches
   `.harness/*/features/*/notes/answers-*.md` independent of the narrower, now-redundant line 46
   entry. Deleting that line would be a mechanical no-op. The reasoning holds.

2. **Adapter sync — TRUE, verified by running the tool, not trusting the diff.**
   `python3 .claude/skills/harness/bin/sync-agent-adapters.py --check` exits 0 with no drift
   output against this worktree. That function does a byte-exact comparison of every
   `.omp/agents/harness-*.md` → `.claude/agents/harness-*.md` rendering, so the generated adapter
   is provably what `--apply` would produce, not a hand-edit that happens to match today.

3. **`test-answers-provenance.py`'s 11 cases — ran green (11/11).** Assertions are mostly
   *complete, load-bearing sentences* copied verbatim from the new prose (not independent
   generic-word pairs like `"issue #671" and "trust"` anywhere in the doc), and every negative
   check is paired with the corresponding positive one three lines above it (DEC-169 pattern:
   presence of the new sentence + absence of the specific stale sentence it replaced). This is a
   defensible verification shape for a prompt-contract fix, matching the established
   `test-orchestrator-playbook.py` convention the docstring cites. Residual weakness noted below
   is structural to *any* pure-prose gate, not unique to this PR.

4. **Broad sweep for other stale `answers-` wording (task 5) — no live-authority gap found.**
   `DECISIONS.md`, `DECISIONS-INDEX.md`, and `BUILD.md` still say "the orchestrator asks" in
   several places (DEC-42/43/44, the DEC-120 entry's domain-grant note, BUILD.md task 14,
   task tables). SPEC.md's own preamble (`SPEC.md:3-5`) states these two files are rationale/history/
   sequencing, explicitly *not* present-tense authority — leaving their as-decided wording
   unedited is correct per "never falsify the record," not an omission. `templates/team-config.yaml`
   carries the identical unrevoked grant as the live manifest, consistently with finding (1).
   No stale *live*-authority document was missed.

## Stage 1 finding that gates: the fix leaves an unreconciled internal contradiction

**`SPEC.md:120-124` and `SKILL.md:209-217`** (both files this PR edited) contain, three lines
apart, in the exact section reworked for consistency:

> "Lateral lead→lead routing uses the same file, since two leads share no run dir." (SPEC.md:121-122,
> unchanged by this diff) / "Lateral routing writes to that same file (DEC-44), since two leads
> share no run dir." (SKILL.md:211-212, unchanged by this diff)

immediately followed by the new rule this PR adds:

> "The orchestrator trusts ONLY the path named in its `resume` dispatch (issue #671) ... never
> writes one itself" (SPEC.md:124/127) / "You never write this file yourself; that channel belongs
> to the main session alone." (SKILL.md:216-217, new)

Both sentences point at the **same path glob**, `notes/answers-*.md`. No lead holds a write grant
to that glob in `team-config.yaml` (checked all three `leads:` entries) — only the orchestrator
and the main session do. So if "lateral lead→lead routing uses the same file" describes a real,
live mechanism (the orchestrator relaying a lateral lead's resolved answer back into a paused
lead's run via `resume_from`, the same file-based checkpoint mechanism the round-trip itself uses),
**the orchestrator is the only agent that could ever perform that write** — directly contradicting
the blanket "never writes it, at all" rule added three lines later in the same document.

Failure scenario: an orchestrator resolves a lateral lead→lead question (SKILL.md's documented
rung 2 of the ladder) for a lead whose run needs to resume from a checkpoint. Following the
still-standing "lateral routing writes to that same file" sentence, it writes a self-authored
`notes/answers-<runid>.md` — mechanically permitted, since `team-config.yaml`'s grant is
deliberately left unchanged (finding 1 above confirms it is not the no-op the commit's reasoning
assumed for *this* case, only for the narrow-vs-broad-grant question it was actually answering).
That self-authored file is now indistinguishable from a main-session-authored one from inside a
later resume — precisely the forgery vector issue #671 exists to close, just reopened via the
lateral path the fix's own prose still affirmatively describes as valid.

The competing, and more likely correct, reading is that DEC-78 ("Escalation resolutions are
recorded in the DIGEST" — `DECISIONS.md:906`) already superseded DEC-44's file-based lateral
mechanism for the *live, same-run* case, and SKILL.md's ladder step 2 already says the resolution
goes to the `escalations` trace, not a file (`SKILL.md:204`). If so, the "lateral routing writes
to that same file" sentence in both documents is simply dead, pre-DEC-78 text that this PR's own
reconciliation pass should have caught and removed — it is not new, and it was not part of what
this diff touched, but it now sits directly beside, and in tension with, text this diff *did* add
to close exactly this kind of contradiction.

Either reading points to the same fix: resolve or delete the "lateral lead→lead routing uses the
same file" sentence in both `SPEC.md` and `SKILL.md` so it doesn't read as authorizing a second,
undocumented write path into the exact glob the new rule declares off-limits to the orchestrator.

## Stage 2 — code quality

N/A in the conventional sense — this is a pure prompt/doc diff, `code_grade: n_a` (no Python
production code changed; `test-answers-provenance.py` is itself a test file). No correctness bugs,
resource leaks, or copy-paste divergence to report beyond the Stage 1 finding above.

## Other observations (non-gating)

- `run-unit-tests.sh` registration verified: `test-answers-provenance.py` appears exactly once in
  `UNIT_SCRIPTS`, so it actually runs under the gate (checked, not assumed — Expertise G-04).
- The three-rung-ladder language newly added to `SPEC.md` step 3 is not invented — it matches
  pre-existing, untouched text elsewhere in the same file (`SPEC.md:234-237`, `:2196-2200`) and in
  `SKILL.md`'s own "you are the middle of it" section. This is a correction toward consistency, not
  scope creep.
- `.claude/commands/harness.md`'s relay table row was already correctly attributed to "You" (the
  main session) pre-PR; the diff only adds the trust-only clause. No pre-existing misattribution
  there.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The fix closes the user-answer forgery vector but leaves an unreconciled, three-lines-away contradiction that reopens the same vector via the still-documented lateral lead-to-lead file write."
  severity_max: high
  findings: 2
  must_fix:
    - "SPEC.md:120-129 and SKILL.md:209-217 — 'lateral lead-to-lead routing uses the same file' sits three lines from the new 'orchestrator never writes it' rule, both targeting notes/answers-*.md; no lead holds a write grant to that glob (team-config.yaml), so the orchestrator is the only agent that could perform the lateral write the sentence describes, directly conflicting with the new blanket rule and leaving a live path to reopen the #671 forgery vector via lateral routing. Resolve by deleting/updating the stale sentence (DEC-78's escalations trace appears to already supersede it) or by scoping the new rule to exclude a documented lateral-write case."
  spec_violations:
    - { kind: omission, path: ".harness/harness/docs/SPEC.md", ref: "issue #671" }
    - { kind: omission, path: ".claude/skills/harness/SKILL.md", ref: "issue #671" }
  reviewed: "main..2cb7efe1 (no feature.json/plan.yaml for this direct-flow PR; review_sha pin not applicable per dispatch)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Is DEC-78's escalations trace the sole current mechanism for lateral lead-to-lead resolution (making the 'lateral routing writes to that same file' sentence in SPEC.md/SKILL.md simply dead pre-DEC-78 text), or does resuming a checkpointed lead's run after a lateral hop still require a file-based handoff through notes/answers-*.md? The answer determines whether the fix is a one-line deletion (delete the stale sentence) or needs a scoped carve-out in the new rule.", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-671-answers-provenance/notes/review-harness-code-reviewer-pr1251.md
```
