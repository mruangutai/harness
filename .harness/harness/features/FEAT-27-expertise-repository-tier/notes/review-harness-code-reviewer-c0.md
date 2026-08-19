# Code review — harness-code-reviewer — FEAT-27 — c0

**Verdict: PASS.** Diffed `b4659cd..9b929de` (the pinned `review_sha`, tip of
`feat/FEAT-27-expertise-repository-tier`). No `must_fix`, `severity_max: med`. Stage 1 (spec
compliance) is clean — every hunk traces to a REQ/D, no scope creep, no omission found beyond what
qa/validator already carried forward. Stage 2 surfaces one new, verified defect (F-1) plus one
already-known low item repeated for completeness (F-2).

## What I did not re-derive

Per dispatch, treated as settled and NOT re-investigated: qa-final-validator's six-item
could-not-fail census in `test-inject-expertise.py` (case12 hostile values, case2's `FEAT-\d+`
sub-case in `test-check-expertise.py`, case2's ordering assertion at :123, case9a's vacuous `all()`
at :225-233, the `[ -r ]` guard's masked non-matching-glob duty, the unreachable global-tier branch
at `inject-expertise.sh:98-101`); DEC-27's falsification (already routed to the operator, and
`9b929de` independently confirms it fixed the SPEC-side paraphrases while leaving DEC-27 itself
unstruck, exactly as its own commit message discloses). I re-read `9b929de` in full (docs-only,
`.harness/harness/docs/SPEC.md` + receipt/observations) to confirm it doesn't touch executable
surface — it doesn't.

## F-1 (med, NEW) — `check-expertise.sh` validates repository-tier segment names that
`inject-expertise.sh` will silently never inject

**Premise checked at base (`b4659cd`):** `check-expertise.sh` had no tier concept at all
(`LINE_BUDGET = 150` uniform, confirmed by `git show b4659cd:.claude/skills/harness/bin/check-expertise.sh`),
and `inject-expertise.sh` had no repository glob or segment filter. Both halves of this
inconsistency are new in this diff — not inherited.

**The gap.** `check-expertise.sh`'s `REPO_TIER_RE` (`check-expertise.sh:56`) is
`(^|/)\.harness/[^/]+/expertise/[^/]+\.md$` — the segment class is `[^/]+`, unrestricted. But
`inject-expertise.sh`'s segment filter (`:75-77`) is
`case "$segment" in ''|*[!a-z0-9-]*) continue ;; esac` — only lowercase-alnum-hyphen segments are
ever read; anything else is skipped **silently**, per 1d's own intent ("Skipping is silent; the
hook never warns and never blocks").

I confirmed both regexes independently, without writing any file (no Write access to source,
and Bash write is guarded off for this role — confirmed the guard fires even against the
scratchpad). Ran the two classifiers as inline, read-only Python/bash against literal path
strings copied verbatim from each script:

```
/tmp/x/.harness/My_Repo/expertise/harness-qa.md  -> classify_tier() = "repo" (40-line budget, OK if well-formed)
/tmp/x/.harness/foo.bar/expertise/harness-qa.md  -> classify_tier() = "repo" (40-line budget, OK if well-formed)
My_Repo  -> REJECTED by inject-expertise.sh's segment case-filter
foo.bar  -> REJECTED by inject-expertise.sh's segment case-filter
harness  -> accepted by both (today's only real segment)
```

I also confirmed the write guard does not block such a path: `harness_boundary.glob_to_re`
(`.claude/skills/harness/bin/harness_boundary.py:56-57`) translates a single `*` to `[^/]*` —
unrestricted by case or character class — so the repository grant
`.harness/*/expertise/harness-<agent>.md` (added by this diff's T-01, 16 lines in
`team-config.yaml`) permits writing `.harness/My_Repo/expertise/harness-qa.md` today.

**Concrete failure scenario.** A future distillation (this feature's own D-01/D-02 name unit 7,
multi-repo, as the point at which more segments appear) writes a repository-tier file under a
segment whose name mirrors a real directory with a case or punctuation the hook's filter excludes —
`My_Repo`, `Kaya-Frontend.git`, anything with an uppercase letter, underscore or dot. The write
guard allows it. `check-expertise.sh` (the only authoring-time gate, and the one `harness-curate`'s
T-06-updated audit loop now calls per-segment) reports `OK`, applies the 40-line budget correctly,
and gives **no advisory, no warning, nothing** to indicate the file is dead on arrival. Every
subsequent spawn for that agent silently never sees the content — permanently, because nothing
between authoring and injection re-validates the segment the way the hook does. This is the
inverse of D-01's disclosed risk (over-injection from a stray *legitimately*-named directory);
here the checker actively signs off on a configuration the hook will never honor, which is worse
than an absent check because it reads as validated.

**Why not `high`:** the only segment that exists in this tree today is `harness`, which is
lowercase and passes both filters — no current spawn is affected, and no SC or REQ requires
`check-expertise.sh` to validate segment well-formedness (REQ-04's text is scoped to budget and
the advisory scan only). This is a latent trap for exactly the future work D-01/D-02 already flag
as the revisit trigger, not a break in the shipped feature. Rated `med`: real, silent, and
undetectable by any gate in this feature, but not exercised by anything currently in the tree.

**Suggested fix direction (not mine to make):** either have `classify_tier`'s `REPO_TIER_RE`
require the same `[a-z0-9-]+` segment class the hook enforces (and fail or warn on a near-miss), or
have `check-expertise.sh` print an advisory when a repository-tier path's segment would be
rejected by the hook's filter.

## F-2 (low, already surfaced by qa, repeated for completeness) — stale caps line in
`harness-curate/SKILL.md`

`harness-curate/SKILL.md:34`'s per-file distillation checklist still reads "Respect caps
(15/15/10/5, 150 lines)" — unconditional 150, no mention of the repository tier's 40 — even
though the same file's step 1 (line 15, this diff) now correctly audits both tiers. A distiller
working a repository-tier file via this checklist is told the wrong budget by the step that does
the actual editing. Confirmed present at `9b929de` (`grep -n` above). Non-gating: T-06's `verify:`
only checks steps 1/4's audit commands, not the checklist prose, so this was never going to be
caught mechanically. qa's `runs/qa-final-validator/digest.md` already carries this exact item
under "SMALLER, NON-GATING" — I re-confirmed it at source rather than re-deriving it, and am
listing it here only so it isn't lost between qa's digest and the review panel's own record.

## Stage 1 spot-checks (no violations found)

- **T-01 grants**: 16 sibling lines added to `team-config.yaml`, one per agent already holding a
  craft grant, each `.harness/*/expertise/harness-<agent>.md` — matches D-02's wildcard-not-pinned
  choice exactly, matches SC-02's agent list exactly (count and names).
- **T-02/T-03 code**: headers, precedence line wording, and `cap_body`'s budget parameterization
  match the BRIEF's specified literal strings byte-for-byte (`inject-expertise.sh:94-117`).
- **T-04 migration**: stat-level entry counts removed from the six craft files are consistent with
  the eleven listed movers; SC-03's inspection was already re-run by validator at 252fa72 and
  nothing in `b7c40d6`/`9b929de` touches those files again — not re-verified line-by-line here.
- **T-05/T-06 docs**: `9b929de` closes the one concrete gap I could check mechanically (the global/
  project budget-relationship paraphrase at old SPEC.md:974-975) without touching any executable
  surface, and its own commit message discloses the one thing it deliberately leaves open (DEC-27).
- **No-touch constraints honored**: `git diff --stat` confirms `fleet.yaml`, `harness.json`,
  `gh_board.py`, `load_board`, `factory_claim.py`, `check-state.sh`, `check-domain.sh`,
  `bash-write-guard.sh`, `validate-digest.py`, and everything under `FEAT-24-*/` are absent from
  this diff.
- **No YAML parse dependency added** to `inject-expertise.sh` — read the full current file; no
  `import yaml`, no `python3 -c` block touching `team-config.yaml` or `fleet.yaml`.

## Open question for the panel/orchestrator

Not mine to answer, surfacing per the validator's own open question Q1 (unresigned-plan-amendment
gap in `check-state.sh`, under the DEC-174 carve-out) — my review is orthogonal to it and does not
change its status.
