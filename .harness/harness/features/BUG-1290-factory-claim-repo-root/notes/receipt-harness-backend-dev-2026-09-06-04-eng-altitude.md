# ALTITUDE pass — B-3 fixture diff (tests/unit/test-factory-claim.py)

BLUF: two findings, no apply needed. (1) The CLOSED-issue registration for 954 is at the right
home — leave. (2) The diff's docstring and 5b's comment now both spell out the same specific
mechanism (T-99 → 954 closed), a mild new drift risk worth a backlog note — briefing-row. No
residual needs a deeper fix; the diff's own mutant evidence shows it closes exactly the gap it
targets.

## Commands run / lines read
- `git -C <worktree> diff -- tests/unit/test-factory-claim.py` (the +14/-9 subject).
- Read (absolute worktree path, per G-18 — a bare relative path resolved against the wrong
  checkout on my first attempt and had to be redone):
  - `tests/unit/test-factory-claim.py:1-72` (SEG_FEATURE const), `:324-389` (`build_features_root`,
    full docstring + kaya_seg/harness_seg block), `:1139-1233` (cases 5a/5b/5c bodies + comments).
  - `.claude/skills/harness/bin/factory_claim.py:18-209` (`issue_number`, `_blocker_gate`,
    `_blocker_reason_text`) — to ground where `rec.issue_data[954]` is actually consumed
    (`factory_gh.issue_view(repo, blocker_num, ["state"])` inside `_blocker_gate`), not to review
    it; production file is settled scope.

## Findings

**F1 — home of the 954/CLOSED registration.**
File: `tests/unit/test-factory-claim.py:1200` (`rec.issue_data[954] = issue_data(954, "T-99 do the
thing", state="CLOSED")`), inside case 5b's body, versus `build_features_root()` at
`:324-386` which owns only the plan.yaml/feature.json file fixtures. Cost if moved: none avoided —
`Recorder()` (`:1190`, fresh per case) is inherently per-test state, and 5a (`:1168`, issue 950) and
5c (`:1220`, issue 953) already register their own candidate `rec.issue_data[...]` entries the same
way in-body. Moving 954 into the shared fixture would put per-test mock state into
file-fixture-building code that returns a bare `harness_root` path and touches no `Recorder`, which
is the actual bolt-on. The current split (shared file fixture in `build_features_root`, per-case GH
mock in the case body) is the established, consistent home. **leave**

**F2 — near-duplicate mechanism narrative, docstring vs. case comment.**
File: `tests/unit/test-factory-claim.py:335-340` (`build_features_root` docstring) vs
`:1179-1183` (5b's comment). Pre-diff, the docstring stated the fixture's general shape ("harness's
T-77 is clear") and the comment carried case-specific mechanism; post-diff both now spell out the
identical specific chain — "harness clear via its dep T-99, which harness's own map resolves to a
closed issue" appears in both, nearly verbatim. Cost: two prose sites for one fact, and only the
comment sits next to the `check()` that actually enforces it — the docstring copy has no assertion
tying it to reality, so if 5b's dep/issue value ever changes, the docstring is the one nobody
remembers to update (matches P-01/G-02's stale-label caution). Authoritative statement is the
`check(name_5b, ...)` boolean at `:1202-1206`; the docstring, the comment, and `name_5b` itself
(`:1184`) are three independent prose descriptions of what that boolean already enforces, and only
the docstring's restatement is new to this diff. Low cost, comment-only, no assertion at stake —
worth a note, not worth reopening 5a/5c's identical established pattern to fix in isolation.
**briefing-row**

**F3 — no residual needs a deeper fix.**
Examined against: the mutant evidence already in the dispatch (`_BlockerCache.issue_number`
re-keyed on `feature` alone reddens 5b only post-edit, nothing pre-edit) and the production
mechanism at `factory_claim.py:169-178`. The diff's entire purpose — giving each segment its own
non-empty, differing issue map — is exactly what makes that per-repository cache-bleed bug visible;
there's no narrower or deeper fix available that doesn't touch settled scope (5a/5c-5f fixtures or
production `factory_claim.py`). Declining to find here: examined the same two files as F1/F2, no
narrower home exists to propose. **leave**

## Trap check
No restructuring of the two segment blocks (kaya_seg/harness_seg) is proposed. F1/F2/F3 leave that
block untouched; F2's docstring line is outside the segment-block pair itself (it's the function's
top-level docstring, not the per-segment `write_json`/`write_yaml` calls the trap warns about).
