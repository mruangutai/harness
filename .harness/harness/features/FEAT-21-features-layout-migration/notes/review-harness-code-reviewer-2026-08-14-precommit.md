# Review — harness-code-reviewer — FEAT-21 — precommit (T-09 not yet run)

**Ground-pin (as required):** `git rev-parse HEAD` = `ea937b17e132fdcc7780cbb5a65ab579eb57bb7d`,
branch `feat/FEAT-21-features-layout-migration`, `.harness/features` absent (ls fails), rename
staged as `git mv`. Matches the handoff's expectation. Reviewed target: `git diff HEAD` (working
tree, uncommitted) plus the staged rename — **not** a commit range, because none exists yet.

**Verdict: FAIL — one must_fix (T-05, high). Two med findings raised as open questions, not
decided. Rest is low/informational.**

## Stage 1 — spec compliance

Reconciled every task's `files:` list (T-02..T-07, T-10) against `git diff HEAD --name-only`
(script comparison, not eyeballing): **zero files claimed by two tasks, zero task-declared files
missing from the diff except the two explicitly excused** (`test-layout-migration.py` — T-01,
already its own earlier commit, correctly absent here; `test-validate-digest.py` — T-06 audit-only,
correctly unchanged, and I independently re-ran the audit: every `.harness/features/...` occurrence
in that file is inert placeholder text substituted out via `.replace()` before use, e.g.
`test-validate-digest.py:548-549`, never resolved against a real path — the "leave it" call was
right, it just was never written down anywhere, see low finding below). One incidental diff outside
any task's file list: `.harness/logs/2026-08-14.md`, which is ordinary main-session append-only
logging (`main_session.writes` grants `.harness/logs/**`), not scope creep.

**SC-02** (verify: inspection) — checked against `notes/layout-boundary-2026-08-14.md`. Pre-move
block reads `features: CLEAN — evidence legacy`, `docs: CLEAN — evidence legacy`,
`0 mixed, 0 cannot-verify` (lines 7-11); post-move block reads `features: CLEAN — evidence
migrated`, `docs: CLEAN — evidence legacy`, `0 mixed, 0 cannot-verify` (lines 64-68); check-state.sh
exit 0 both sides, INV-27 lines: 0 post-move (line 75). Matches SC-02's pinned wording exactly.

**SC-07** (verify: inspection) — repo-wide `git grep -l '\.harness/features/' -- .claude/agents
.claude/commands .claude/skills`, not diff-scoped. All 19 T-07 prose files correctly carry the
literal `.harness/harness/features/...` (D-01's prose form). Survivors outside `templates/` and
`harness-init/SKILL.md`: `check-plan-routes.py`, `check-state.sh`, `gh-sync.py` (each one stale
historical/explanatory comment, true as written, not agent-facing write instructions — see low
findings below); `layout_fixtures.py`/`layout_migration.py` (the detector's own legacy-pattern
table, meant to carry the literal); `merge-gitignore.sh`, `test-factory-claim.py`,
`test-factory-integration.py` (named unit-9 survivors, already ruled sanctioned); `test-validate-
feature-json.py` (the named `FEAT-99-x` display-path survivor, already ruled);
`test-harness-yaml-corpus.py` (untouched by this diff — checked, its one occurrence at line 232 is
synthetic YAML-parser-corpus fixture text unrelated to real path resolution, self-consistent, no
finding); `test-validate-digest.py` (confirmed inert, above). SC-07 holds as written.

**SC-11** — `git diff HEAD --stat -- docs/harness/` returns nothing. Clean.

**SC-12** — cannot be evaluated pre-commit; it asserts a landed-commit shape (two commits total)
that does not exist yet. Not a finding against this diff; T-09's own job.

### Finding 1 — MUST FIX, high, blocks T-09 — check-state.sh finding labels never got the segment (T-05)

T-05's intent is explicit and gives a worked example: *"where a finding names a path, build the
label FROM THE DISCOVERED PATH — the segment-qualified relative path the glob returned... Every
finding today identifies a feature by a bare directory name, and most build a path from it -
'FEAT-21/BRIEF.md'."* That literal example maps one-to-one onto the code.

Every `bad.append`/`warn.append` in the diff still uses the bare `{feat}` prefix, unchanged —
`check-state.sh:109,111,114,124,127,134,140,142,150,154,162,183,187,569,865` and more, e.g.
`bad.append(f"{feat}/BRIEF.md has no '## Approval' section...")`. The path is not merely
unqualified — it is **structurally unavailable**: `briefs`, `plans`, `plan_docs`, `states` are all
built as `{os.path.basename(os.path.dirname(p)): read(p) for p in glob.glob(...)}` (lines ~53-66),
which discards `p` the moment the dict comprehension finishes, so the discovered path never reaches
the finding-construction code that follows. This wasn't partially done — it wasn't done.

Failure scenario: after this lands, a session-entry gate finding reads `FEAT-21/BRIEF.md has no
'## Approval' section`. `FEAT-21/BRIEF.md` names no file on disk (the real path is
`.harness/harness/features/FEAT-21.../BRIEF.md`); an operator trying to open exactly what the
finding names cannot. Once a second repository segment lands this also becomes ambiguous — the
exact operator-facing harm SC-14/T-05's own reasoning is built to prevent for the discovery layer,
left unaddressed at the presentation layer.

No gate catches this: T-05's own verify only checks the discovery-join regex form
(`os.path.join(H, [^,)]+, "features"`), not finding text; T-09's verify greps only for `INV-27`
absence, not label content. This is exactly the class of thing the DEC-174 carve-out's compensating
control — a human reading the diff against the plan — exists to catch. Kind: **omission**. Ref:
T-05 intent, D-08's "finding LABEL" clause.

### Finding 2 — med, advisory, not blocking — check-plan-routes.py's segment-level glob can silently swallow a whole repository segment (T-04)

`discover_plans()` now globs `.harness/*/features` (line 540) via `seg_dirs = sorted(d for d in
glob.glob(feats) if os.path.isdir(d))` (line 553) with **no readability guard at the segment
level** — the readability guard this file is famous for (the whole "THE READABILITY GUARD" comment
block, case_22's four fixtures) only fires per-feature-directory, *inside* the loop over
`seg_dirs`.

Demonstrated (python, not read from the regex): a segment directory `.harness/<seg>` at mode 0
disappears from `glob.glob('.harness/*/features')` results with no exception —
`os.path.isdir()` swallows the `PermissionError` from the stat call. Reproduced live:
```
before chmod: ['.../segA/features', '.../segB/features']
after chmod 000 on segB: ['.../segA/features']
```
`case_22` (test-check-plan-routes.py:533-556) only chmods a **feature** directory
(`.harness/harness/features/FEAT-A`), never a **segment** directory, so this gap is untested.

Per your advice, traced through to the CI backstop rather than stopping at the demonstration: with
only one segment unreadable and one readable (the minimum needed to make the swallow silent —
`seg_dirs` non-empty, `plans` possibly empty for legitimate reasons), `examined` would undercount
but not go to zero, so `.github/workflows/tests.yml`'s `examined -eq 0` loud-error path (line
~168) would **not** necessarily fire — the undercounting is silent by construction whenever at
least one other segment stays readable. This needs two segments to manifest, which is exactly
D-08's deferred firing precondition ("cannot fire here, because one repository exists") — except
D-08's deferral is a written, reasoned decision in the plan, and this one is not: it is an
unrecognized regression against a guarantee this specific file's design (and its dedicated test
suite) exists to provide. Not blocking this atomic commit — matches D-08's own rationale against
adding new guard mechanism for a defect that cannot fire on the landed tree — but it should be
routed to whichever unit lands the second segment (unit 5 or 8, alongside D-08's cross-repo key
collision), with a `case_22` sibling that chmods the segment directory rather than the feature
directory.

### Finding 3 — med, open question, not decided — branch-create-gate.sh may have the wrong side of D-01 (T-07)

`branch-create-gate.sh:77-78` now reads `ls -d "$root/.harness/harness/features/${flow}"*` — a
**literal** segment. This dispatch explicitly names `branch-create-gate.sh` on the wildcard side of
the D-01 sweep ("Check ... `branch-create-gate.sh` ... against the 19 agent/skill/team/command
files ... and `test-factory-cli.py`" — i.e., expected to pattern with the glob/regex group, not the
prose group), and structurally `ls -d "..."*` is a discovery glob, the same shape as
`check-domain.sh`'s `SWEEP_GLOBS` and `check-plan-routes.py`'s `discover_plans()` glob — both of
which correctly took the wildcard form under T-03/T-04. D-01's own text is unqualified on globs:
"Grants, globs and regexes take a WILDCARD... never a hardcoded harness segment."

But the counter-argument is real: `root` here is `CLAUDE_PROJECT_DIR` (line 27), i.e. per-repo, not
a shared multi-repo control plane view — this is the file:line-verified pattern the boundary note's
own `factory_claim.py` ruling states explicitly: *"product features live at
`.harness/<product>/features/`, so the fix is a per-repo join, not a segment insert"*
(`notes/layout-boundary-2026-08-14.md:100`). If that reasoning applies here too, a wildcard would
be a **false grant**: `ls -d .harness/*/features/FEAT-12*` would validate a branch against *any*
segment's flow, not just this repo's own — and DEC-133 coins FEAT ids per-BRIEF with no cross-repo
uniqueness rule, so a same-numbered flow in another segment is not exotic.

I am not deciding this — it needs the same explicit D-01 boundary ruling the plan gave
`team-config.yaml`/`check-domain.sh`/`check-plan-routes.py` (a ROW AUDIT), which
`branch-create-gate.sh` never got. Cannot fire today (one segment); when it does fire it is LOUD
(deny, naming the searched path) either way, so it is not an urgent block — flagging as an
`open_question` rather than a must_fix.

### Finding 4 — low, informational — gh-sync.py's walk-up probes team-config.yaml, not the harness.json the plan text pins (T-10)

T-10's intent says twice, unambiguously: *"walk UP from the absolute feature directory and return
the first ancestor holding `.harness/harness.json`"* / *"the first such ancestor is `<tmp>` ...
`<repo>`"*. The shipped code (`gh-sync.py:733-750`) probes `.harness/team-config.yaml` instead,
with its own comment explaining why: `test-check-plan-routes.py`'s pre-existing `case_20` (not part
of this feature) requires every root-probe in `bin/*.py`/`*.sh` to name `team-config.yaml` as the
manifest or be added to a two-item exception list. I confirmed this constraint independently
(re-read `case_20`, `test-check-plan-routes.py:1098-1194`) before reading the boundary note, which
documents the same call at `notes/layout-boundary-2026-08-14.md:97`. The deviation from the pinned
plan text is real (per your own rule: report it regardless of merit) but it was forced by a
pre-existing gate, is behaviorally inert here (`team-config.yaml` and `harness.json` always
co-locate in this repo and in both new fixtures), and is at least written down in the evidence note
— just never folded back into `plan.yaml`'s own decision record. Neither new test case
(`migrated_depth`, `not_onboarded` in `test-gh-sync.py`) discriminates which file is actually
probed — both stage both files together — so the choice of manifest remains proven only by
inspection, not by a test that would fail if it silently changed again. Recommend: fold this into a
plan.yaml decision (or amend D-07) rather than leaving it only in the boundary note.

### Finding 5 — low, informational — stale comment in check-state.sh (T-05)

`check-state.sh:51` — `# BRIEF/PLAN are PER-FEATURE since DEC-129 — .harness/features/<FEAT>/{BRIEF,PLAN}.md.`
— states the OLD path as present-tense fact. Post-move this is false (real path is
`.harness/harness/features/<FEAT>/...`). Not one of the sanctioned "historical, true-as-written"
comments (those describe a past measurement; this describes present-tense current shape). Cosmetic
— comment no longer matches the code it sits above.

## Stage 2 — code quality

No additional findings beyond the fail-open items already raised in Stage 1 (findings 1-2 are both
fail-open/silent-failure findings and were reported there per the task's "hunt fail-open first"
framing). T-05's `os.listdir` → `glob` conversion (`check-state.sh:95-103`) correctly preserves the
`isdir` guard, `sorted()` ordering, and builds `_fj_p` from the glob-returned `_fd` rather than
re-joining `H` + bare name — matches intent verbatim. T-04's regexes and T-03's four shape regexes
were verified to match a real post-move path (executed, not just read). T-08's rename is a clean
`git mv`-shaped diff (567 pure renames), FEAT-21's own concurrently-modified bookkeeping excluded
per the dispatch's instruction, untracked FEAT-20 review notes correctly traveled with the
directory rename.

## Summary table

| # | File | Task | Severity | Blocking |
|---|---|---|---|---|
| 1 | check-state.sh | T-05 | high | **yes — must_fix** |
| 2 | check-plan-routes.py | T-04 | med | no (advisory) |
| 3 | branch-create-gate.sh | T-07 | med | no (open question) |
| 4 | gh-sync.py | T-10 | low | no |
| 5 | check-state.sh:51 | T-05 | low | no |
