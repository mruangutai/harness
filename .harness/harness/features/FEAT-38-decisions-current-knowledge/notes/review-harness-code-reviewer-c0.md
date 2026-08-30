# Code review — FEAT-38-decisions-current-knowledge @ 3928c70

Reviewed: `7ebfc9e..3928c70`. All citations below are `git show <sha>:<path>`, never a working-tree
read (confirmed the worktree HEAD `a1bc873` is byte-identical to `3928c70` on every file cited here,
via `git diff 3928c70 HEAD -- <path>`, before treating a live-run check as pin-equivalent evidence).

## Stage 1 — spec compliance: **PASS**

### SC-11 — the meaning-preservation sample (my primary assignment)

**Sampled 10 of the 15 rewritten entries** (BRIEF requires ≥8, and requires DEC-138/174/194 be
included): **DEC-11, DEC-138, DEC-142, DEC-158, DEC-171, DEC-174, DEC-181, DEC-189, DEC-193, DEC-194.**
For each, read the pre-fold text at `7ebfc9e` and the folded form at `3928c70` side by side and checked
that both (a) the prior belief and (b) what falsified it survive. **Result: 10/10 PASS — no falsified
claim was deleted rather than restated.** Per-entry:

| Entry | Falsified claim(s) checked (per the build's own digest table) | Verdict |
|---|---|---|
| DEC-11 | `hooks` was listed as a frontmatter capability; corrected — it does not fire for subagents | **preserved** — `DECISIONS.md:161` still carries `hooks` is NOT one of the frontmatter capabilities… do not fire for spawned subagents…proven across three attempts |
| DEC-138 | (4 claims: `absorbs:` struck; `parent_origin` null on FEAT-34/35 orphaned #728; closed cards don't move — #818–#830; blanket comment ban too wide, line is PROVENANCE) | **preserved, all 4** — `DECISIONS.md:2925-3040`. Also confirmed the 4 amendments (5–8) physically misfiled inside DEC-168's base span landed in DEC-138's own folded body, not DEC-168's (`:3994-4020` at review carries none of that content) |
| DEC-142 | name-vs-title: a name omitting the flow id "has been tried and it fails" | **preserved** — `:3114-3130` |
| DEC-158 | (3 claims: frequency criterion falsified by gh-sync/context-probe; pointers fail silently vs preload; red-flag table carried no rule of its own) | **preserved, all 3** — `:3606-3648` |
| DEC-171 | graceful degradation reversed; fail-open on missing PyYAML rejected for the two guards | **preserved, both** — `:4101-4155` |
| DEC-174 (REVERSAL, mandatory) | factory-workspace route: prior "NOBODY" belief named explicitly and marked superseded ("A reader who has been told that route resolves to NOBODY… is reading the tree as it stood before the removal"); board declaration: BOTH intermediate shapes (fleet-level key, then per-repo `board:` block) named before the final ruling (harness.json per-repo) | **preserved, both — intermediate state survives, not just the final ruling** — `:4268-4470`. This was the one case explicitly flagged as highest-risk (a fold that states only the final ruling loses the intermediate); it does not lose it |
| DEC-181 | STRUCK-IN-PART status folded to one live rule + a clause that the propagation-checker half is gone | **preserved** — `:4769-4820`; also carries the D-10-format claim markers (verified live, see below) |
| DEC-189 (misfiled-amendment check) | "the docs entry" amendment, physically misfiled inside DEC-194's base span (`:6401` at `7ebfc9e`), landed in DEC-189's own folded body at review (`:5147-5230`), not DEC-194's | **preserved and correctly filed** |
| DEC-193 | "preserved" held for 2/3 fleet states, not 3; `<product>` was a second name for one segment | **preserved, both** — `:5297-5340` |
| DEC-194 (mandatory) | applicability-by-own-path fails by construction; any-first-level-`.harness/` glob forces uncleaable MIXED; "every finding names a reader" overclaimed — `blame()` can return empty | **preserved, all 3** — `:5393-5486` |

Corroborated independently, not accepted on report: the lead's pre-measured facts (all 15 deleted
ids have zero `## DEC-<id>` heading; `## DEC-90 — STRUCK 2026-08-21` at `:1057`; `## DEC-205` at
`:6240`; zero amendment/supersession patterns) all reproduce identically against `git show 3928c70:`.

**Bonus, not required by SC-01's literal patterns:** three additional amendment-shaped paragraphs the
build's own product digest flagged as outside T-08's grep-defined unit of work (`**Amended same day`,
`**Superseded:**`, `**Amended by #836`) were *also* folded into current-truth prose by the time of the
pin — not left as an open gap. Confirmed each rewritten location by content match; none read as
history-with-a-marker any more.

### Other REQs/SCs checked at the pin

- **REQ-03/SC-02/SC-03** — zero `## DEC-<id>` headings for all 15 deleted ids in `DECISIONS.md`;
  zero as index rows or in any `refs:` graph entry in `DECISIONS-INDEX.md`; `DEC-90` row present at
  index `:100` with its strike record intact. Confirmed via `git show` grep, not working-tree.
- **REQ-04 (citation sweep, item 4 of the dispatch — swept, not sampled)** — grepped the FULL body of
  `DECISIONS.md`, `DECISIONS-INDEX.md`, every touched file under `.claude/skills/harness/bin/**`,
  `BUILD.md`, `SPEC.md`, `.harness/harness.json` and `.github/workflows/tests.yml` for
  `DEC-(19|20|37|67|82|88|92|102|103|104|137|140|186|192|196)\b`: **zero hits everywhere in scope.**
  Read the actual rewrites in `BUILD.md`/`SPEC.md` (11 sites) to check they state something TRUE
  about the successor rather than blind id-swap: `DEC-82→` corrected to `DEC-83` (verified DEC-83's
  own body is literally "Third correction to the same fact… what the earlier reading got wrong: it
  said nesting is off by default" — a real successor, not a mechanical increment);
  `DEC-192→"DEC-203 item 6"` (verified DEC-203's numbered clause 6 is the status-field rule DEC-192
  pointed at); several others (`DEC-19`, `DEC-92`, `DEC-104`, `DEC-102`) correctly dropped to bare
  prose with **no citation**, per the BRIEF's own prescribed remedy for a pattern-name citation with
  no successor to carry it. No id-swap defects found in the sampled/swept rewrites.
- **REQ-05/SC-12** — front matter (`DECISIONS.md:1-4`) no longer states APPEND-ONLY; states the
  rewrite-in-place convention instead. `harness-documentor.md` P-01 rewritten to match (no longer
  instructs "place inside the amended decision's own section"). `DEC-205` (`:6240`) states where the
  convention now lives.
- **REQ-06/SC-06 (generator residue, item 6)** — `grep` for all seven forbidden symbols
  (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`, `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE`,
  `compute_amendments`, `format_amendment_span`, `compute_supersession_target`) plus `amend`/`Amend`/
  `SUPERSED`/`supersed` case-insensitive across the whole script: **zero matches** — no residue in a
  docstring, header, or dead helper either. `build_index`'s orphan detection is intact and unchanged
  in shape (still a hard error on a row whose heading vanished). `compute_refs` (`gen-decisions-
  index.py:134-142`) filters `n not in live_nums` before ever emitting a ref — this is D-04's clause
  implemented, not merely claimed: the generated `DEC-188` row (`DECISIONS-INDEX.md:190`) now reads
  `refs: DEC-90 DEC-165 DEC-181`, correctly missing the phantom `DEC-103 DEC-104` the BRIEF names as
  the proof case. Ran `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` live at the pinned
  content: **clean diff**, confirming SC-05.
- **REQ-07/SC-07/SC-08** — ran `check-decision-anchors.py` live against `git show 3928c70:` content:
  `examined 20 anchor(s), 0 failed`, exit 0. Ran it against `git show 7ebfc9e:` content (via process
  substitution, no file write): `examined 32 anchor(s), 3 failed` — **exactly** the three
  `feature.yaml`-named anchors the BRIEF predicts. All three SC-08 observations reproduced live.
- **REQ-08/SC-09** — ran `check-decision-claims.py` live: `examined 11 claim(s), 0 failed`, exit 0.
  Mutated DEC-181's marker (`budget is 80` → `budget is 81`) via process substitution and re-ran:
  reddened exactly, naming `DEC-181 — CLAUDE.md gets a line budget of 80` and the mismatched
  substring. SC-09 reproduces live, exactly as specified.
- **Registration, both sides** — `run-unit-tests.sh:31` `INTEGRATION_SCRIPTS` carries both
  `test-check-decision-anchors.py` and `test-check-decision-claims.py`. `.github/workflows/tests.yml`
  runs `run-unit-tests.sh --kind integration` as its own CI step, so CI does reach both new checkers'
  live-authority tests (see Stage 2). No `harness.json` `integration` detect-glob edit was needed for
  this registration path — the runner's own name-list is what CI invokes, and it already carries both.

**No spec violations found.** No scope creep, no omission against a REQ/D, no mismatch against a
specific decided value. Everything named in the dispatch's six numbered risk areas checked out
against actual bytes at the pin, not on report.

## Stage 2 — code quality (only entered because Stage 1 passed)

### HIGH — `check-decision-claims.py`'s marker parse is not strict; a malformed marker is silently
excluded from "the suite," never reported, never counted as a failure

`CLAIM_RE` (`check-decision-claims.py:29`) is the only extraction path (`extract_claims`,
`:69-84`); a line that does not match it is not a claim, full stop — not a warning, not a failure,
not present in `examined N claim(s)`. Proved live (in-process, via `importlib.util`, no file writes):

```
well-formed        -> claims found: 1
single-colon-typo   (":: " -> ": ")  -> claims found: 0   # silently invisible
trailing-text       (prose after -->) -> claims found: 0   # silently invisible
```

**Concrete failure scenario.** DEC-181's two live markers are hand-authored HTML comments tracking
`check-domain.sh`'s exact message string. The next time `harness-documentor` (or a human) edits one
of them — bumping the budget number, or re-wording the anchor around it — a single dropped colon or
a stray trailing character removes that marker from consideration entirely. `check-decision-claims.py`
still exits 0, still prints a non-zero `examined` count (because the OTHER marker in the file still
parses), and CI stays green. The stale, unverified claim then sits in the org's frozen authority
document indefinitely — exactly the meaning-loss REQ-08 and DEC-205 exist to prevent, reintroduced by
the checker meant to prevent it. This is the identical failure shape DEC-169 already names in this
same file ("an absence check proves only that the wrong words are gone… every absence check needs a
presence check beside it") generalized to a *coverage* check: the SIMPLIFY pass's fix
(`test_live_authority_claims_all_hold`) binds the *aggregate* count to non-zero, which defends only
against a *total* regex break — it does not and cannot catch one marker silently dropping out of a
file that still has others. No test in `test-check-decision-claims.py` exercises a near-miss/malformed
marker; the equivalent safety net the SAME author built for index rows (`gen-decisions-index.py`'s
`ROW_LOOKALIKE_RE`, which raises `MalformedRow` rather than silently skipping a hand-written row that
almost-but-not-quite parses) has no counterpart here.

**Companion note, same class, lower currently-manifest risk, not separately gating:**
`check-decision-anchors.py`'s `ANCHOR_RE` (`:24-26`) has the identical "no-match = invisible" shape
for an anchor citing an extension outside its allowlist (`py|sh|md|json|yaml|yml|ts|toml`). Checked
the live document: every anchor extension in use today (`.md .py .sh .yaml .yml`) is inside the
allowlist, so this is not manifesting now — but it is the same structural gap, undefended by any test.

**What this does NOT affect:** SC-08 and SC-09 as literally specified both pass exactly (verified
live above) — the SC's own chosen mutation (a wrong *value*, not a malformed *marker shape*) is
squarely inside what the checker catches. The gap is a class the SC never tests for, not a
regression against what it does test for.

### No other Stage 2 findings rise above style/opinion.

Read the ~20 swept `bin/` scripts' diffs for the citation-rewrite pattern specifically (item 4's
ask) and for fail-open shape generally; nothing else showed a branch where a miss sails through
silently. `run-unit-tests.sh`'s `KIND-DRIFT` cross-check (`:78-128`) is unchanged in shape and still
enforces both directions (an `INTEGRATION_SCRIPTS` name must be in the config's detect; no
`UNIT_SCRIPTS` name may be).

## LEAVE LIST — confirmed, not re-raised

- SC-04's residual gap (main-session-direct NOBODY paths) reproduces exactly as described; not a
  finding.
- The three unsatisfiable `verify:` blocks (T-10, T-15, T-19) and the two order-dependent ones
  (T-03, T-21) were not re-derived; taken as already confirmed at source per the dispatch.
- `docs`/`config` zero-required-test-kind floor: not re-litigated; qa's domain.

## Verdict basis

`must_fix` is non-empty (the claims-checker finding) and `severity_max` is `high`, so per
`harness-code-review`'s gate rule this is **FAIL** — Stage 1 passed cleanly; Stage 2 produced one
high-severity, concretely-demonstrated fail-open in a gate this feature itself installs. Per
`.harness/harness.json`'s `advisory_unless_high` policy this **does** gate, since the finding clears
the `high` bar.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 (spec compliance) PASSES cleanly — 10-entry SC-11 sample incl. mandatory DEC-138/174/194 all preserve both the prior belief and its falsification, both misfiled-amendment cases land correctly, D-04's refs-graph clause is implemented and proven on the DEC-188 row, SC-05/06/07/08/09 all reproduce live against the pinned bytes. Stage 2 found one HIGH fail-open: check-decision-claims.py's marker regex silently drops a malformed claim marker from consideration with no error and no count signal, defended against total-zero but not partial silent loss — the same absence-without-presence-check shape DEC-169 already names in this file, now present in the checker meant to close it."
  stage1: PASS
  stage2: FAIL
  severity_max: high
  findings: 1
  must_fix:
    - "check-decision-claims.py:29 (CLAIM_RE) — a malformed claim marker (e.g. single `:` instead of `::`, or trailing text after `-->`) is silently excluded from extract_claims, never counted, never failed; only a total-zero regression is caught by the live-authority test. Add a lookalike/near-miss detector (mirroring gen-decisions-index.py's ROW_LOOKALIKE_RE -> MalformedRow pattern) so an almost-valid `<!-- claim` line raises rather than vanishes."
  spec_violations: []
  reviewed: "7ebfc9e..3928c70"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "check-decision-anchors.py's ANCHOR_RE has the identical silent-no-match shape for an out-of-allowlist file extension. Not currently manifesting (all live anchors use allowlisted extensions) — worth the same lookalike-detector fix while touching the sibling checker, or a separate backlog item?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-code-reviewer-c0.md
```
