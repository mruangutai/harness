# QA scoped re-review — FEAT-05, cycle 1 — do the new tests DISCRIMINATE?

Reviewer: harness-qa · range `340e18a..9da3986`

## STEP 0 — verbatim

```
$ git rev-parse HEAD
924b961ad626b79c8810a9de7ae420ccc634e4fd

$ git status --porcelain
(empty)

$ git diff --stat 340e18a..9da3986
 .claude/skills/harness/bin/check-state.sh          |  88 +++++--
 .claude/skills/harness/bin/gh-sync.py              |   7 +-
 .claude/skills/harness/bin/harness_yaml.py         |  35 ++-
 .claude/skills/harness/bin/run-unit-tests.sh       |   2 +-
 .claude/skills/harness/bin/test-check-domain.py    |  26 ++
 .claude/skills/harness/bin/test-gh-sync.py         |  44 ++++
 .claude/skills/harness/bin/test-upgrade-config.py  | 157 +++++++++++
 .claude/skills/harness/bin/upgrade-config.py       |   9 +
 [... .harness/ docs/notes files, not code ...]
19 files changed, 1309 insertions(+), 56 deletions(-)

$ git log --oneline 340e18a..9da3986
9da3986 docs(brief): Q2 ruled a pinning error — the non-goal stands (Amendment 2)
20b5af3 fix: the panel's mediums and five of six open questions (F-04, F-05, Q1, Q3, Q4, Q6)
bb6ab8c fix(bin): the three high findings from the review panel (F-01, F-02, F-03)
d727870 chore(state): re-pin review_sha to 340e18a for the review panel
```

**HEAD is `924b961`, one commit ahead of `9da3986`.** Checked before proceeding: that commit
(`git diff 9da3986..924b961`) touches only `feature.yaml:9` — `review_sha: 340e18a` →
`review_sha: 9da3986` — a state re-pin, not code. No file under review is dirty or ahead of the
pinned range. Proceeded.

## F-03 — `test-upgrade-config.py` — **PARTIALLY CLOSED. Half the file's cases are decorative.**

**1. GREEN 6/6 at 9da3986/HEAD — confirmed, live:**
```
ok    the script RUNS as a subprocess (F-03: NameError on every invocation)
ok    it reads a real manifest without raising
ok    a malformed manifest does not pass silently
ok    a QUOTED schema_version behaves like a bare one (was read as absent)
ok    prose containing `name:` is not harvested as an agent
ok    --check never rewrites team-config.yaml (safe_dump would strip its comments)
6/6 cases passed.
```

**2/3. Against `340e18a`'s broken import, the current test file scores 4/6 passed (2 red):**
```
FAIL  the script RUNS as a subprocess (F-03: NameError on every invocation)
FAIL  it reads a real manifest without raising
ok    a malformed manifest does not pass silently
ok    a QUOTED schema_version behaves like a bare one (was read as absent)
ok    prose containing `name:` is not harvested as an agent
ok    --check never rewrites team-config.yaml (safe_dump would strip its comments)
```
Reproduced twice. I initially read the dispatch's "RED 4/6" as "4 tests fail" and flagged a
mismatch; on reflection the harness's own `4/6 cases passed` line is exactly what I measured,
so "RED 4/6" most plausibly denotes "run is red, score 4/6" — the same run I got. **Not a
finding by itself.** Retracted as a headline item; the count is not in dispute once read as a
score rather than a fail-tally.

**The two genuinely defect-linked cases fail for exactly the right reason** — quoted stderr,
both cases, identical call site:
```
File ".../upgrade-config.py", line 124, in yaml_version
    doc = harness_yaml.load_str(text, "<manifest>")
NameError: name 'harness_yaml' is not defined
```

**The real finding is not the count — it's that tests 3, 4 and 5 do not discriminate anything,
at ANY baseline, because their assertions are structurally too weak to see the defects they
name.** I checked this properly against the *correct* baseline per defect, not just `340e18a`
(applying the same reasoning F-04 required — the regex-era code, not the broken-import code,
is what tests 3–5 claim to be regression tests for):

- **Test 4** (`"a QUOTED schema_version behaves like a bare one"`) only compares the exit codes
  of `--check` between a quoted-`"1"` and bare-`1` project, never the parsed value. Materialized
  the true pre-conversion regex script (`37a8a66`, before T-03/T-04 touched the file) and ran
  the regex directly: quoted `schema_version: "1"` is parsed as `None`, bare as `1` — the actual
  documented defect, present. But the fixture's template pins `schema_version: 2`, so **both**
  `None` and `1` differ from `2` and both trips give exit 1 regardless. Ran the current test
  file against `37a8a66`'s script live: **6/6 pass, including test 4** — it cannot detect the
  bug it is named for at the one baseline where the bug is real.
- **Test 5** (`"prose containing name: is not harvested as an agent"`) checks that the string
  `"not-an-agent"` never appears in stdout. Traced the regex-era `yaml_names` directly against
  the NOISY fixture: it DOES harvest `"not-an-agent"` from the folded block scalar (confirmed:
  `['build', 'not-an-agent']`). But `main()` only prints names that `startswith("harness-")`
  before flagging them as new — `"not-an-agent"` is filtered out downstream regardless of
  whether the regex over-harvested it. The assertion can never fail no matter what `yaml_names`
  returns for a non-`harness-`-prefixed string. Confirmed live: **6/6 pass at `37a8a66`**,
  including test 5, with the harvesting bug provably still present underneath.
- **Test 3** (`"a malformed manifest does not pass silently"`) accepts `returncode != 0` as
  success — but the regex-era script exits 1 on ANY schema-version mismatch from the template,
  malformed or not, so a malformed file "passing" this check proves only that the file's
  garbled `schema_version` differed from the template's `2`, not that malformation was
  detected. Confirmed live at `37a8a66`: passes, same non-discriminating shape.

Against `340e18a` (broken import), these same three additionally pass **vacuously** for a
second, independent reason — both branches of each comparison raise the identical `NameError`
before reaching the code the assertion is about, so equality/absence checks hold trivially. Two
different ways to be green for the wrong reason, same three tests, at two different baselines.
**Test 6** (`--check` never rewrites) is the one case among 3–6 that is a legitimate, if
non-regression, spec assertion — the script never writes `team-config.yaml` in any version, so
this holds for a real reason at every baseline; it just isn't proving anything about the
conversion.

**T-04's own three PLAN-mandated tests were never delivered.** `PLAN.md:450-452` requires:
(a) names extracted from the **real** `.harness/team-config.yaml` compared against an inlined
pre-change fixture, (b) `schema_version` returns an `int` (a type assertion), (c) a manifest
whose `name:` is all-digits is returned `str`, not `int` (D-08 coercion). Grepped the delivered
file for `team-config.yaml` reads, `isinstance`/`type(`, and an all-digit `name:` fixture: none
of the three exist. `project()` always writes a synthetic manifest into a tempdir; nothing reads
the repo's actual manifest; nothing asserts a type; no all-digit name appears anywhere in the
file. D-08's `str()` coercion in `upgrade-config.py` (which the task explicitly calls out) has
**zero** test coverage. This is a matrix-floor gap on the exact task whose absent test file
caused F-03 to ship broken in the first place.

**5. Registration — the cycle-0 gate hole.** `run-unit-tests.sh:6`'s `SCRIPTS` array lists
`"test-upgrade-config.py"` as its 12th entry (confirmed by grep). A live full run
(`CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh`) reports **12 suites**,
all `PASS`, exit 0. Separately verified the runner's behavior when a `SCRIPTS`-listed script is
absent from disk, using a disposable simulation (not editing the real `bin/`): `python3` fails
to open the missing file, `status=$?` is non-zero, the wrapper prints `FAIL <script>` and the
overall exit is **1** — loud failure, not a silent skip. That half of the cycle-0 gate hole is
closed.

**F-03: PARTIALLY CLOSED.** The import is fixed and verified (tests 1–2 discriminate cleanly at
every baseline checked). Registration is real and the runner fails loudly on a missing entry.
But three of the file's six cases (3, 4, 5) do not discriminate the defects they claim to catch
at *any* baseline — the assertions are structurally too weak, not merely coincidentally green —
and none of T-04's own three mandated tests (real-manifest name diff, `int` type assertion,
D-08 str-coercion on an all-digit name) were written. D-08's coercion path in `upgrade-config.py`
has no coverage at all.

## F-04 — the two `load_recorded` tests (T-06 Part C) — **CLOSED**

Both PLAN-mandated cases are present at `test-gh-sync.py:710-740`: the trailing-`#`-comment
case (`parent`, `milestone`, `issues` all carry trailing comments; `milestone` is additionally
quoted) and the missing-`github:`-block default case.

**Note on scope:** T-06's *conversion* (Part A) already landed before `340e18a` (commit
`35b7b9f` is an ancestor of `340e18a`) — confirmed live: `load_recorded` at `340e18a` already
parses the trailing-comment/quoted-milestone fixture correctly. What was actually missing at
`340e18a` was Part C's *tests* and the stale `text ops — no yaml dependency` comment (confirmed
present verbatim at `340e18a`, corrected in the current file at `gh-sync.py:178-181`). So a
genuine RED proof needs the truly pre-conversion regex script (`35b7b9f~1`, i.e. `60b266c`),
not `340e18a`.

Ran the current two tests directly against that pre-conversion `load_recorded` (materialized to
`/tmp`, module exec'd in isolation):

```
CASE1 (trailing comment / quoted milestone) at pre-T-06 regex script:
  {'milestone': None, 'parent': 40, 'parent_origin': 'adopted',
   'attached': ['T-01'], 'issues': {'T-01': 41}}
  CASE1 PASS? False   <- milestone silently lost, parent survives, exactly as claimed

CASE2 (no github: block) at pre-T-06 regex script:
  {'milestone': None, 'parent': None, 'parent_origin': None, 'attached': [], 'issues': {}}
  CASE2 PASS? True    <- this script already handled the absent block correctly
```

Case 1 is a genuine RED, correctly attributed (milestone lost, parent kept, matching the
docstring's claim exactly), against the true pre-conversion code, and PASSES at both `340e18a`
and HEAD. Case 2 does not discriminate against the pre-conversion script (it was already correct
there) — it is a spec-compliance assertion, not a regression-catcher, which is a legitimate
thing for a mandated test to be.

**F-04: CLOSED.** Both mandated cases exist; one is empirically proven to discriminate for the
right reason against the actual pre-fix parser; the other correctly documents pre-existing
behavior. Cycle 0's RELAYED/UNVERIFIED status is resolved to verified-true.

## Cross-cutting sweep — every test added/modified in `340e18a..9da3986`

| File | Change | Discriminates pre-fix, right reason? |
|---|---|---|
| `test-upgrade-config.py` (new, 157 lines) | 6 cases | Tests 1–2: **yes**, NameError, exact site, at `340e18a`. Test 6: legitimate spec assertion, holds everywhere for a real reason. Tests 3, 4, 5: **no, at any baseline** — assertions too weak to see their named defects even against the true pre-conversion (`37a8a66`) script; additionally vacuous against `340e18a`'s crash. |
| `test-gh-sync.py` +44 (T-06C block) | 2 cases | Case 1: **yes**, verified RED against true pre-conversion (`60b266c`-era) script. Case 2: not a regression test (pre-existing code already correct) but a legitimate spec-compliance assertion. |
| `test-check-domain.py` +26 (F-01 block) | 2 cases (bad-UTF-8 manifest, manifest-as-directory) | **Yes, both.** Ran current tests against `340e18a`'s `check-domain.sh` in a disposable `git worktree add /tmp/feat05-c0-qa 340e18a` (removed after; empty `git status --porcelain` before removal). Both FAIL with exit 1 + Python traceback — the exact "crashes non-blocking, fail-open" defect F-01 names — and both PASS at HEAD (exit 2, blocked). Not explicitly assigned to me, but the dispatch asked for every test in the range; included. |
| `run-unit-tests.sh` (2-line diff) | adds `"test-upgrade-config.py"` to `SCRIPTS` | Not a test — registration fix, verified above (12 suites; loud-fail-on-missing confirmed via simulation). |
| `harness_yaml.py` (+35) | production fix (F-01), not a test | Out of scope for test-discrimination, but the two `test-check-domain.py` F-01 cases exercise it and do discriminate (above). |

## Q3 spot-check — **CLOSED**

`notes/uat-bootstrap-escape-expiry.md:3` carries exactly ONE `sc_08:` status now — `met` — with
a correction comment; no contradictory frontmatter/body pair remains (grepped the whole file:
one `sc_08:` hit, one unrelated `not_met` for `sc_09` inside a quoted historical instruction to a
different agent, not a live status). Backing assertion confirmed live at
`test-check-domain.py:288` (`SC-08: the install command reaches a channel the user SEES
(systemMessage)`), present and passing in the full suite run above.

## Q1 spot-check — **CLOSED**

`notes/receipt-post-change-run-inventory.md` exists. Its per-feature `declared` counts (1, 4,
19, 15, 4) sum to **43**, reproduced independently by parsing every
`.harness/features/*/feature.yaml`'s `runs:` list with `harness_yaml.load_file` directly (not
relayed): FEAT-01=1, FEAT-02=4, FEAT-03-subissue-mirror=19, FEAT-04-decisions-index=15,
FEAT-05-pyyaml-file-parsers=4, sum=43. The declared side of "43 parsed / 43 declared" reproduces
exactly.

## Post-run cleanup

`git worktree remove /tmp/feat05-c0-qa --force` and temp dirs under `/tmp` both removed. Final
`git status --porcelain` on the worktree root is empty — no poisoning.

---

VERDICT: FAIL

DIGEST:
  headline: F-04 closes and discriminates cleanly. F-03's import/registration fix is real and its two core cases discriminate the NameError correctly, but 3 of its 6 cases (and all 3 of T-04's own PLAN-mandated tests) are structurally unable to catch the defects they claim to cover, at any baseline — including D-08's str-coercion path, which now has zero coverage.
  suite: pass
  failures: 0
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh", named_tests: 12 }
  coverage_gaps:
    - "upgrade-config.py: T-04's three PLAN-mandated tests (real-manifest name diff, schema_version int-type assertion, D-08 all-digit-name str coercion) were never written"
    - "test-upgrade-config.py tests 3-5: assertions too weak to discriminate their named defects at any baseline (quoted-schema_version, name-harvesting, malformed-manifest cases)"
  sc_evidence:
    - { id: SC-03, test: ".claude/skills/harness/bin/test-upgrade-config.py:82 (case 1, discriminating)" }
    - { id: SC-08, test: ".claude/skills/harness/bin/test-check-domain.py:288" }
    - { id: SC-13, test: ".harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-post-change-run-inventory.md, reproduced independently (43=43)" }
  open_questions:
    - { id: Q1, question: "T-04's own three mandated tests (real-manifest name diff, int-type assertion, D-08 str-coercion on an all-digit name) were never written, and 3 of the 6 delivered cases cannot detect their named defects at any baseline. Does F-03 close as-is, or does upgrade-config.py's test file need a follow-up pass before this feature ships?", blocking: true }
  files_touched: [".harness/features/FEAT-05-pyyaml-file-parsers/notes/qa-c1.md"]
  expertise_update: []

artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog/.harness/features/FEAT-05-pyyaml-file-parsers/notes/qa-c1.md
