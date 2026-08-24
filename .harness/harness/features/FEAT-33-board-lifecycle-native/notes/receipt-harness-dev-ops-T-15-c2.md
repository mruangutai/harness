# Receipt — harness-dev-ops — T-15 — c2 (fix for issue #783)

## BLUF

`board_lifecycle.py audit`'s STATUS class ignored `--repo`: `_status_findings` always walked
THIS checkout's own on-disk `.harness/*/features/*`, then compared each feature's recorded
parent against whatever repo `--repo` selected — producing 18 false findings out of 29 on
board 2 against `mruangutai/kaya-ai`. **Fixed by self-skip**, not scoping: STATUS now runs
ONLY when the audited repo is this checkout's own declared repo, and prints one line saying so
otherwise. `reconcile` shared the exact same leak (same `_audit_findings` call) and is fixed by
the identical change, with no second check needed. Both directions RED-proved by reverting
`board_lifecycle.py` to HEAD (never `git stash`), GREEN restored, full suite green.

## The decision: self-skip, not scope-by-recorded-repo — and why

Two candidate rulings were on the table. **Self-skip is the one built**, because scoping is not
available: it would require a `github.repo` field on `feature.json` that does not exist.
Checked directly — `grep -n "\"repo\"" .harness/harness/features/*/feature.json` across every
feature.json in this tree returns nothing, and `factory_config.product_config` (the actual
mechanism that answers "what is repo X's config") reads a served fleet member's
`.harness/harness.json` **remotely** via `factory_gh.file_at_ref` (a `gh api
repos/<repo>/contents/.harness/harness.json?ref=<default_branch>` call) — never from a local
directory. `_feature_dirs`'s glob (`<root>/.harness/*/features/*/feature.json`) can only ever
walk THIS checkout's own tree; a served repo's features are never reachable from here at all.
Inventing a filter field would be guessing what does not exist on disk; self-skip states the
real limit instead.

**The exact code comment** (module docstring, `AUDIT` section):

```
STATUS (T-15, below) adds a SIXTH finding class but no fifth network call: it reads every
feature's `feature.json` off disk and reuses call 3's already-fetched station map. STATUS runs
ONLY when the audited repo is THIS checkout's own declared repo (#783's fix, below) — it
self-skips, printing one line, for any other `--repo`, since the on-disk features it reads are
never that repo's.
```

and, more fully, in `_status_findings`'s own docstring (`.claude/skills/harness/bin/board_lifecycle.py:337-353`):

```
THE RULING (#783), stated once here because it has to be explicit rather than implied by a
filter: `_feature_dirs` walks `<root>/.harness/*/features/*` -- ALWAYS this checkout's own
on-disk tree, regardless of which repo `--repo` names. A served fleet repository's features
are never there; its own `.harness/harness.json` is read REMOTELY
(`factory_config.product_config` -> `factory_gh.file_at_ref`), never from a directory in
this checkout, and no feature.json anywhere records a `github.repo` field to filter by
(checked: none of this tree's feature.json files carry one). Scoping this class to
"features whose recorded repo matches the audited one" would mean inventing a field that
does not exist on disk. Self-skip is the honest alternative, and it is what `_audit_findings`
does: this class runs ONLY for this checkout's own repo, and prints one line saying so for
any other `--repo`, rather than silently comparing this checkout's features against a
foreign board (the live defect measured on board 2 with `--repo mruangutai/kaya-ai`: 18 of
29 findings were this checkout's own harness issues compared against kaya-ai's board).
```

## Where the fix lives

`_audit_findings`'s Class 6 section, `board_lifecycle.py:561-570`:

```python
own_repo = _own_repo(root)
if repo_name == own_repo:
    findings.extend(_status_findings(root, board, stations))
else:
    _out(f"STATUS: skipped -- auditing {repo_name!r}, not this checkout's own repo "
         f"({own_repo!r}); this checkout's on-disk features are never that repo's")
```

`_own_repo(root)` was already an existing helper (reads local `harness.json`'s `github.repo`,
no network) — reused, not re-authored. This adds no network call: it is a local file read
already made once per invocation by `_resolve_board`; calling it a second time here costs
nothing over the wire, and the module docstring's network-call-count claims (still exactly
four for audit, four-plus-writes for reconcile) are unchanged and still true.

## `reconcile` shares the leak — checked, and fixed by the same change

Yes, it shared it: `cmd_reconcile` calls the SAME `_audit_findings(root, board, repo_name)`
detection function `cmd_audit` calls (never re-derived), so before the fix a `reconcile --repo
<other>` run would preview (and, under `--apply`, actually attempt) a `gh_board.set_station`
write against the SERVED repo's card, using a station computed by comparing it to THIS
checkout's own, unrelated `feature.json`. Proved with a dry-run-only fixture (no `--apply`,
per the brief's own caution against writing against a class known to be wrong) — see the RED
proof below, case "reconcile #783". Because the fix lives once in `_audit_findings`, both
`audit` and `reconcile` inherit it with no second check; documented explicitly in the module
docstring's RECONCILE section (`board_lifecycle.py:67-72`).

## The five other finding classes — unchanged

DECLARATION, STATION, REASON, LABEL and WORKFLOW: zero lines touched in their detection code
(`_audit_findings`'s classes 1–5), and every pre-existing test for them stayed PASS in every
run below, including the full 128-plus-check `test-board-lifecycle.py` suite. `_missing_options`
remains the single DECLARATION/provision comparison (D-05), untouched. `cmd_audit`'s
`try/except factory_gh.GhError: sys.exit(4)` wrapper is untouched.

## The regression guard — cross-repo fixture, RED-proved

Added to `test-board-lifecycle.py`:

1. **Contents-endpoint dispatch** in the fake `gh` (`*"/contents/"*` case) plus a
   `CONTENTS_B64`/`contents_b64=` plumbing through `run()`, and `_served_board_contents_b64`
   — needed because `--repo` naming a genuine fleet member resolves its board via
   `factory_config.product_config`'s remote read, which this file's fake `gh` had never
   answered before (only `test-factory-integration.py`'s fake did).
2. **Audit case 8b** (`FEAT-CROSSREPO-783`): this checkout's OWN feature on disk, `status:
   Done`, `parent: 950`; `--repo acme/gadget` (a fleet member, never this checkout's own repo
   `acme/widget`) resolves a served board where issue #950 reads `Backlog`. Three assertions:
   exits 0, no `"records status"` finding text, and the skip line names both repos.
3. **Reconcile case 6b** (`FEAT-CROSSREPO-RECON-783`): same shape with `status: Building`
   (non-Done, otherwise fixable) and `parent: 960` reading `Ready` on the served board, run
   under `reconcile --repo acme/gadget` **with no `--apply`** — the preview text alone is the
   discriminator, so the case stays a read even against the pre-fix code. Three assertions:
   exits 0 with "0 fixable finding(s) previewed", never mentions `#960`, and zero mutation
   calls reached the fake.

### RED proof (by on-disk mutation, restored byte-identical — never `git stash`, per #780)

```bash
cp .claude/skills/harness/bin/board_lifecycle.py <scratch>/board_lifecycle.py.new
git show HEAD:.claude/skills/harness/bin/board_lifecycle.py > .claude/skills/harness/bin/board_lifecycle.py
diff -q <(git show HEAD:...) .claude/skills/harness/bin/board_lifecycle.py   # RESTORED_TO_HEAD_OK
python3 .claude/skills/harness/bin/test-board-lifecycle.py
```

Against HEAD (pre-fix): **5 FAIL lines**, exactly the 3 audit-#783 assertions and the 2 (of 3)
reconcile-#783 assertions that could discriminate — every other check, including the third
reconcile-#783 assertion ("zero mutations", true under dry-run regardless of the bug) and every
pre-existing case, stayed PASS. Actual reddened output confirms the live defect exactly:

```
board_lifecycle: STATUS: <root>/.harness/widget/features/FEAT-CROSSREPO-783 records status
'Done' (column 'Done') but its parent #950 reads 'Backlog'
board_lifecycle: 1 finding(s)
```
```
board_lifecycle: DRY-RUN would fix -- STATUS: <root>/.harness/widget/features/FEAT-CROSSREPO-RECON-783
records status 'Building' (column 'Building') but its parent #960 reads 'Ready'
board_lifecycle: 1 fixable finding(s) previewed; 0 finding(s) require a human (see above) --
re-run with --apply to write
```

Restore:
```bash
cp <scratch>/board_lifecycle.py.new .claude/skills/harness/bin/board_lifecycle.py
diff -q <scratch>/board_lifecycle.py.new .claude/skills/harness/bin/board_lifecycle.py   # RESTORED_FIX_OK, exit 0
python3 .claude/skills/harness/bin/test-board-lifecycle.py   # all checks passed.
```
Confirmed identical both times (two separate RED/GREEN cycles, one per commit of the fix).

## Verify: `.claude/skills/harness/bin/run-unit-tests.sh --kind all`

Command, independently re-extracted from `plan.yaml`'s T-15 `verify:` field
(`.harness/harness/features/FEAT-33-board-lifecycle-native/plan.yaml:1355-1356`), byte-identical
to what was run:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind all
```

Full run (33 scripts, 2808 output lines), background-notified `completed (exit code 0)`. Zero
literal `^FAIL ` lines. Every non-anchored `FAIL` substring hit is inside a passing assertion
NAME describing a FAIL-shaped scenario under test (e.g. `test-branch-create-gate.py`'s "a
FAILING invocation creates no log file", `test-validate-digest.py`'s "dev-ops task_verify: n/a +
FAIL is accepted") — checked individually, none is a real failure. `test-board-lifecycle.py`
and `test-factory-integration.py` both printed `PASS` in the log. `git status --short` after the
run showed only this task's two files (`board_lifecycle.py`, `test-board-lifecycle.py`) plus the
same pre-existing, untouched-by-me changes already present at dispatch start
(`feature.json`/`plan.yaml` and the `notes/migration-*`/`notes/retitle-*` files) — confirmed by
`git diff --stat` on those two before I started, which I never opened or edited.

## Digest note (issue #778, reiterated per the dispatch's instruction)

`validate-digest.py:158` restricts `dev-ops`'s `change_type` enum to `{config, scaffolding,
infra, ci}`. This is a defect fix to existing `feature`-typed code, not a new PLAN task, so
there is no task-level `change_type` to substitute here — the digest below carries
`change_type: infra` as the closest available value for a bin-script behavioural fix, matching
T-15 c1's own prior substitution for the identical reason.

## Is the honest fix smaller or larger than the brief assumed?

**Smaller than assumed** on the core fix (a caller-side guard plus documentation, ~25 lines in
one function and its docstrings) but **larger on the regression guard**, because proving the
cross-repo shape genuinely required teaching `test-board-lifecycle.py`'s fake `gh` a network
endpoint (the remote `contents` read for a fleet member's board) it had never needed before —
that plumbing (the fake dispatch case, `run()`'s new param, `_served_board_contents_b64`) is
more code than the fix itself. Reconcile's own regression case added on top of the brief's
literal ask (a STATUS class fixture) because "check whether reconcile shares the leak" is only
answered by evidence, not narration, once a discriminating dry-run fixture existed at almost no
marginal cost.

## Open questions

None blocking. #778 (dev-ops digest enum) already filed, not re-filed as new.
