# Review — harness-ui-reviewer — FEAT-21-features-layout-migration (Mode A, s4)

BLUF: FAIL. One must_fix. `DESIGN.md` is legitimately absent — no rendered UI ships here. Per the
dispatch, the three named operator-diagnostic surfaces were audited against the plan's own verify
coverage, plus a sibling sweep of the two other reader-migration tasks. Four of five are clean. One
is not: `check-plan-routes.py`'s diagnostic strings are a stated requirement in T-04's intent with
zero enforcing assertion anywhere in the plan — including the detector itself.

## Scope check

- `ls .harness/features/FEAT-21-features-layout-migration/` — no `DESIGN.md`.
- `git status --short` on the feature directory shows it untracked as a whole; no design doc exists
  to review. Confirmed by direct filesystem check, not inferred from the dispatch's framing.
- This feature is shell/Python gate code plus a directory rename — no markup, no CSS, no rendered
  surface. Scoping out on that basis alone would be correct, per the dispatch's own framing.
- The dispatch names one adjacent in-remit surface: operator-facing diagnostic text emitted by
  `branch-create-gate.sh` (T-07 GROUP 2), `check-plan-routes.py` (T-04), and `check-state.sh`
  (T-05). Audited all three against the plan's actual verify blocks and the real files at HEAD, then
  swept T-02/T-03 (`team-config.yaml`, `check-domain.sh`) for the same gap class since they are the
  other two reader-migration tasks in the same coupled cluster.

## Finding 1 — must_fix, severity high

**T-04's verify does not check the two diagnostic-string sites its own intent requires updating, and
neither does the detector's own row for this file.**

- `plan.yaml:335-338` (T-04 intent) states: "Also update the DIAGNOSTIC STRINGS that tell a reader
  where the scan looked, so the message names the path actually scanned: the unreadable-path message
  and the scanning line that prints the glob it is about to walk."
- `plan.yaml:303-315` (T-04 verify) checks only the discovery-join call shape:
  `re.search(r'"\.harness", "features"', t)` / `re.search(r'"\.harness", [^,)]+, "features"', t)` —
  a Python `os.path.join(...)` tuple-argument pattern.
- The two message sites the intent names are plain string literals, not `os.path.join` calls, and
  the join-pattern regex does not match them:
  - `.claude/skills/harness/bin/check-plan-routes.py:632-633` —
    `f"check-plan-routes: {len(unreadable)} path(s) under .harness/features/ cannot be read — ..."`
  - `.claude/skills/harness/bin/check-plan-routes.py:651` —
    `print(f"scanning {root}/.harness/features/*/{{plan.yaml,PLAN.md}}")`
  Confirmed by direct read of the file at HEAD (2026-08-14); neither line matches T-04's verify
  regex, so a build that migrates the join call at line 539 but leaves these two literals untouched
  passes T-04's verify unchanged.
- No `SC` in `BRIEF.md` covers it either. `SC-07` is scoped to "agent files, skills, team
  definitions and the harness command," and both `SC-07`'s own sweep and `T-07`'s verify grep
  explicitly exclude `.claude/skills/harness/bin/` — exactly where this file lives (`plan.yaml:538`,
  `ex = (...'.claude/skills/harness/bin/')`). `SC-02` covers `layout_migration.py`'s detector
  output, a different file.
- `T-09`'s boundary test invokes `check-plan-routes.py <plan-path>` (the explicit-argv form). Per
  the file's own comment at `check-plan-routes.py:640-643` ("The root guard is ARGV-LESS ONLY"),
  that form bypasses `discover_plans()` entirely — neither message is exercised by anything in the
  plan.
- **The detector does not catch it either**, so this is not a residual gap something else already
  covers: `plan.yaml:320-322` states the detector's own reader-table row for `check-plan-routes.py`
  uses the identical narrow pattern pair — legacy `"\.harness", "features"`, migrated
  `"\.harness", [^,)]+, "features"`. Post-build, `layout_migration.py` would score this file
  CLEAN — evidence migrated with both stale message literals still in place, because its row was
  never written to see them.
- Consequence: a passing build can ship a "scanning" line and an "unreadable path" line that both
  still read `.harness/features/...` — the pre-move shape — while the join actually discovers under
  `.harness/<seg>/features/...`. An operator debugging a "zero plans found" incident (the exact
  failure mode issue #344 and this BRIEF exist to prevent) is misdirected to a path shape that no
  longer exists, and nothing in the plan — verify, SC, or detector — would ever redden for it.
- Remedy is cheap pre-build: add an assertion to T-04's verify (or a new SC) targeting the two
  print/f-string sites specifically — a blanket sweep for the literal `.harness/features/` across
  the whole file would be wrong, since the intent explicitly says to leave several narrative
  comments (`check-plan-routes.py:15,225,430,462`) untouched as "a record of a past state."

## Checked clean

- **T-05 (`check-state.sh`)**: no equivalent gap. Its finding messages (e.g. `INV-17`, `INV-26`
  lines) build path text from variables (`feat`, `rel`) derived from the same join sites the task
  migrates, not from separately hardcoded literals. Direct grep of the file for
  `.harness/features` outside the join calls found exactly one hit, a comment at line 51, never
  printed to a user.
- **T-07 GROUP 2 (`branch-create-gate.sh`)**: fully covered. Its verify does a whole-file negative
  search — `'.harness/features/' not in open(...).read()` — which catches both the lookup
  (line 77) and the deny message (line 78) in one assertion. This is the pattern T-04's verify
  should have used and didn't.
- **T-02 (`team-config.yaml`)** and **T-03 (`check-domain.sh`)**, swept for the same gap class
  though not named by the dispatch: both use a whole-*line* literal search —
  `re.search(r'\.harness/features/', l)` over every line in the file — not a narrow join-call
  pattern, so they would catch a message literal anywhere in either file. Direct grep of
  `check-domain.sh` confirms exactly the eight sites T-03's intent names (four `SWEEP_GLOBS`
  entries, four anchored regexes) and no additional message string carrying the literal. No gap.

## Not verifiable from source

Rendered/visual review does not apply here — everything in scope is CLI text and Python/shell
source; there is no markup, no CSS, no rendering to fail to observe.

## Mode A checklist

- Implementable: n/a — no design values to pin, this is code not a design contract.
- Complete for what's being built: gap found (Finding 1).
- Internally consistent: yes, aside from Finding 1.
- Both themes: n/a, no theme surface.
- Checkable: gap found — that is Finding 1 itself.
