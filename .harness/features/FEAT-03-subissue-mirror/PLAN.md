# PLAN — FEAT-03-subissue-mirror

Eight tasks. T-01 makes the `unit` gate able to see `gh-sync.py` at all (it cannot today), T-02
extracts the shared GitHub primitives, T-03–T-06 rewrite the four GitHub Issues commands around one
sub-issue per `T-NN`, T-07 adds the missing-parent invariant, T-08 records the reversed contract.

Order: T-01 → T-02 → T-03 → T-04 → T-05 → T-06 → T-07 → T-08. T-01 and T-02 are independent of each
other; every later task's `verify:` runs through T-01's runner, and T-03–T-06 all edit
`gh-sync.py`, so they are serial.

**The task count and decomposition are unchanged from the reviewed plan** — eight tasks, T-05 and
T-06 not merged. The budget pressure that motivated the merge advisory was resolved outside this
plan (`harness.json budgets.per_feature_usd` 40 → 120, user decision at `1ce886a`), so there is no
reason to move a decomposition the user is being asked to sign.

## Verify receipts — the convention this cycle introduces

Every `verify:` below carries `observed @f929d44:` — the exit status the command actually produced
against the tree at the review sha, recorded next to the status expected after the task lands.
`f929d44` and the **pinned review baseline `1ce886a`** (`feature.yaml review_sha`; HEAD has moved on
since, and re-anchoring this clause to whatever HEAD is today would only reproduce the rot) are
byte-identical under
`.claude/skills/harness/bin/**` (`git diff --stat f929d44 HEAD -- .claude/skills/harness/bin` is
empty — still empty at `a8fce12`, re-run this cycle), so every receipt below is valid at both.

Two rules the receipts enforce:

- **An absence-grep that already passes is void.** It proves nothing about the change. A correct one
  must FAIL today (`observed @f929d44: exit 1`) and pass only after its task lands.
- **A receipt of `127` or `2` because the file does not exist yet is not a discriminating receipt.**
  It is recorded for honesty and labelled as such; the discriminating receipt for those tasks is a
  positive one — a named `ok` label that is provably absent from today's suite output.
- **The one intentional exception is labelled inline:** `! grep -nE 'parent_args|blocked_by_args'
  gh-sync.py` passes today (exit 0) and is written as a **standing regression guard** for D-01, not
  as evidence that any task changed something.

## Preconditions and hand-offs

Three things this plan depends on that are **not tasks**, because no agent domain covers the files.

- **`__pycache__` is already handled — no task, no requirement.** T-02 makes `gh_issues.py` an
  import target, so `.claude/skills/harness/bin/__pycache__/*.pyc` gets written on every
  wayfind/gh-sync invocation, and untracked files outside `.harness/**` stop the review gate
  (`harness-review/SKILL.md:41`). The main-session edit that fixes it **has landed at `f929d44`**:
  `.gitignore:18-19` and `.claude/skills/harness/templates/gitignore.snippet:8-9` both carry
  `__pycache__/` and `*.pyc`; `git ls-files | grep -c pycache` is 0. Recorded as a **satisfied
  precondition**, verified, not planned.
- **`.claude/skills/harness/SKILL.md` is a main-session pre-ship step (MF-5 / REQ-09 / SC-13).**
  `:137` still reads "closes its issue and everything it absorbs" (1 match, verified at `f929d44`)
  and `:144`'s ship row still says only "closes the milestone". No agent domain covers that file
  (`team-config.yaml` grants `.claude/skills/harness/bin/**` only), so the orchestrator must return
  it to the main session **before ship**, alongside T-08. **Consequence for `check-docs.sh`, stated
  so it does not return as a second FAIL:** T-08 declares **no** `<!-- stale: … -->` marker for
  either phrase, because a marker whose wording is still live turns `check-docs.sh` red and gates
  every `/harness` entry on an edit no agent may make. `check-docs.sh` therefore stays exit 0 for
  the whole feature (observed exit 0 at `f929d44`, "no stale statements found", 45 patterns / 69
  files) and is **silent about this gap by design**. What detects it instead is SC-13's grep at the
  ship gate. If the main session prefers the mechanical route, the ordering is: land the SKILL.md
  edit **first**, then a marker may be declared — never before.
- **T-08 is a lateral hop.** `harness-documentor` is a member of the **product** squad
  (`team-config.yaml:112`), so eng-lead cannot spawn it; the build segment needs the orchestrator to
  route T-08 to product-lead.

## Decisions

- **D-01 — the parent is adopted-or-created by `open`, and its number is recorded, never
  discovered.** Precedence, first match wins: (1) `feature.yaml github.parent` already holds a
  number (the orchestrator recorded an adopted wayfinding map issue or absorbed backlog issue — the
  grilling's origins 1 and 2); (2) `--parent <n>` passed on the command line; (3) no parent recorded
  → `open` creates one, titled `<feature-dir-basename> — <human phrase from BRIEF's H1>`, body =
  BRIEF `## Problem` + `## Goal`. Rejected: calling the parent endpoint to find it. That is a READ,
  and DEC-138 makes the mirror write-only; idempotency comes from local receipts, so a discovery
  path would be a second, contradictory source of truth. Consequence a future scan will re-suggest
  and must not: `gh-sync.py` importing `parent_of` is a defect, not a convenience.
  **The origin is recorded too, at `github.parent_origin` (`created` | `adopted`), because the
  recorded origin governs BOTH terminal subcommands: `abandon` branches on it (SC-03) and `ship`
  branches on it the same way (SC-04) — a created parent closes (`not_planned` on abandon,
  `completed` on ship), an adopted one and an absent origin are left open by either.** A parent this
  feature *created* exists only to hold its tasks — left open
  with every child closed `not_planned` it is an orphan nothing will ever close — while closing an
  *adopted* one would assert something false about someone else's live item. Re-deriving which it was
  at abandon time would mean reading GitHub, which DEC-138 forbids, so the receipt is written at the
  same moment the number is. **This preserves the grilling's decision rather than reversing it**
  (`notes/grilling-subissue-mirror-2026-07-31.md:34-35` says "leaves an **adopted** parent open" —
  the word is already there); the created case is what D-01 introduced and what SC-03 previously
  generalised over by mistake. **Absent or unrecognised origin ⇒ treat as adopted, i.e. leave open**
  — the specified default, because SC-10 forbids editing existing `github:` blocks so pre-existing
  features (this one included: `feature.yaml:41` is `parent: none`) will never carry a marker.
  No new `D-NN`: this is D-01's "recorded, never discovered" applied to a field D-01 already owns,
  and it fails DEC-149's bar on all three counts.
- **D-02 — `absorbs:` stops closing anything.** It becomes citation-only: the absorbed numbers stay
  in the task's issue body (already the behaviour at create) and `close-task` closes exactly one
  issue. This **reverses DEC-138 am.1's "they close with it"** and inverts two live assertions
  (`test-gh-sync.py:177-178`). Trade-off, accepted: watchers of an absorbed issue no longer see it
  close automatically, so the only route from "the feature covered this" to "this is closed" is a
  human signature — the same briefing-gated route DEC-138 am.4 uses for residual findings, chosen
  because absorption is normally *partial* (kaya's #315/#209/#309/#312/#305 were each only partly
  covered) and a script must not infer that a partly-covered issue is done.
- **D-03 — one new module `gh_issues.py`, exposing argv builders plus one lookup, not executors.**
  The two callers have deliberately different failure semantics — `gh-sync.py` skips and exits 0 on
  an environmental failure, `wayfind.py` dies exit 1, and `wayfind.py` is dry-run by default. A
  shared executor would have to pick one and would silently give `gh-sync.py` a gate. So the module
  owns the *knowledge* (endpoint shapes, the id-not-number trap, the `GH_SYNC_GH` binary override)
  and each caller keeps its own runner. Underscored filename because it must be importable.
  **Scope of the module is exactly REQ-06's three primitives plus `gh_bin()` — the sub-issue LIST
  and blocker LIST reads keep their inline endpoint strings in `wayfind.py`.** Adding list builders
  would take the module to five and contradicts REQ-06's "each exist in exactly one place, shared by
  every caller": the lists have one caller and always will, so a builder for them buys locality
  nobody needs. Rejected explicitly so a future scan does not re-suggest it.
  **Under D-03 the internal-id lookup is a builder, not an execution** — the settled answer to the
  spec question: `internal_id_args(repo, num)` returns the argv, and `wayfind.py` keeps executing it
  through its own `gh_json()`. So the literal `"--jq", ".id"` argv pair leaves `wayfind.py`
  (today `:271`, `:279`) while the call itself stays. That is what makes it grep-checkable.
- **D-04 — the `unit` kind becomes a runner (remedy (a)), rather than pinning the GitHub Issues SCs to
  inspection.** `unit.cmd` is one script today and `unit.detect` matches zero files here (verified:
  the glob set resolves to `[]`), so an SC claiming `evidence: unit` would be proven by a test that
  never touches `gh-sync.py` — DEC-163's gate-that-looks-real-and-does-nothing. Cost:
  `.harness/harness.json` is dev-ops's domain, so T-01 is a dev-ops task. Rejected: BRIEF-recorded
  gap + `verify: inspection` on eight SCs — cheaper to write, permanently weaker, and it leaves the
  next feature with the same blind gate.
- **D-05 — the missing-parent invariant is INV-21 at warn level.** Warn, not violation: the GitHub Issues sync is
  never a gate, and an unrecorded parent is a per-feature bookkeeping gap that a re-run of `open`
  fixes. INV-20 is the warn-level precedent (flows still run). Contrast INV-13, which *is*
  violation-level, because `sync: true` with `repo: null` is a config contradiction that makes every
  sync silently skip.
- **D-06 — every task is `change_type: logic | bugfix | config | docs`.** Those rows of `test_matrix`
  resolve to `unit` only (or `[]`). `feature` and `api` would pull in `functional` and `integration`,
  both `cmd: null`, reintroducing DEC-163's invisible gate through a field value. The work genuinely
  is script logic behind an existing CLI, so this is honest, not gaming — but it is recorded because
  "this adds a subcommand, so it is `feature`" is the obvious wrong call.

## Tasks

### T-01 — make the `unit` gate actually run the bin test scripts
- owner: harness-dev-ops
- change_type: config
- traces: REQ-08, D-04
- files:
  - create `.claude/skills/harness/bin/run-unit-tests.sh`
  - edit `.harness/harness.json` (`test_kinds.unit.cmd`, `test_kinds.unit.detect`)
- intent: `run-unit-tests.sh` is `set -uo pipefail`, `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`, and holds
  an **explicit list** of test scripts to run in order — `test-validate-digest.py`, `test-gh-sync.py`
  — executing each and collecting failures rather than stopping at the first.
  - **It STREAMS each child's stdout and stderr through, unfiltered and unbuffered.** This is the
    load-bearing property, not a nicety: run each script as a bare `python3 "$s"` with **no**
    redirection, no command substitution, no `tee`, no `2>/dev/null` — the child inherits the
    runner's fds. The runner's own `PASS <script>` / `FAIL <script>` line is printed *after* the
    child's output, never in place of it. Five downstream tasks' verifies read `ok` lines emitted by
    `test-gh-sync.py`, and seven SCs' `evidence: unit` need qa to name the test that exercised them;
    a runner that captured and discarded child output would satisfy the letter of "one PASS/FAIL line
    per script" and silently void all of them.
  - Before running any, it globs `.claude/skills/harness/bin/test-*.py` and, for any script not in
    the explicit list, prints a line beginning `MISCONFIGURED:` naming the file and **exits 2** —
    distinct from `1` (a real assertion failure), so qa routes it as *misconfigured → BLOCKED* per
    `harness-verification-rules:44` rather than FAIL-ing the person who last touched source. Exit 0
    only if all listed scripts passed; exit 1 if any assertion failed.
  - In `.harness/harness.json`: set `test_kinds.unit.cmd` to
    `.claude/skills/harness/bin/run-unit-tests.sh`, and append
    `|.claude/skills/harness/bin/test-*.py` to `test_kinds.unit.detect`. The existing globs
    (`tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py`) resolve to `[]` in this repo (verified)
    because both scripts are hyphenated and live under the hidden `.claude/` tree, so qa's detect
    step sees **no test files matched**, which is *misconfigured → BLOCKED* per
    `harness-verification-rules:44` — **not** `missing → FAIL`, correcting the reviewed plan's
    rationale by one word. Leave `exclude` unchanged. Do not touch any other key.
- verify:
  - `.claude/skills/harness/bin/run-unit-tests.sh` (after `chmod +x`) → exit 0, output names both
    scripts PASS **and contains `ALL PASSED` emitted by `test-gh-sync.py` itself** — the streaming
    proof, not just the runner's summary.
    `observed @f929d44: exit 127` (file absent — not a discriminating receipt; the streaming half is
    what must be checked by eye on the output).
  - `python3 -c "import json,glob;p=json.load(open('.harness/harness.json'))['test_kinds']['unit'];print(sorted({f for g in p['detect'].split('|') for f in glob.glob(g,recursive=True)}))"`
    → prints both `test-validate-digest.py` and `test-gh-sync.py`.
    `observed @f929d44: exit 0, printed []` — the discriminating receipt for the harness.json half.
  - `touch .claude/skills/harness/bin/test-orphan.py`, then
    `.claude/skills/harness/bin/run-unit-tests.sh 2>&1 | grep -c MISCONFIGURED` → **≥1** with
    `${PIPESTATUS[0]}` = **2**, the line naming `test-orphan.py`. The `2>&1` is deliberate: it checks
    the **stderr** half of MF-3's streaming requirement, which a stdout-only check would miss. Then
    delete the file and confirm `git status --porcelain` no longer mentions it.
    `observed @f929d44: exit 127` (file absent — not discriminating).

### T-02 — extract the three GitHub primitives into one shared module
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-06, D-03
- files:
  - create `.claude/skills/harness/bin/gh_issues.py`
  - edit `.claude/skills/harness/bin/wayfind.py`
- intent: the new module is stdlib-only and holds, with the trap documented **once** in its
  docstring ("the sub-issue and dependency endpoints take an issue's internal `id`, never its
  `number`"):
  - `gh_bin()` → `os.environ.get("GH_SYNC_GH", "gh")`. Both callers route through it, so the fake
    `gh` in `test-gh-sync.py` intercepts helper-built calls too; today `wayfind.py` hardcodes
    `"gh"` in every `subprocess.run`.
  - `internal_id_args(repo, num)` → `["api", f"repos/{repo}/issues/{num}", "--jq", ".id"]`
  - `attach_sub_issue_args(repo, parent, child_id)` →
    `["api", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={child_id}"]`
  - `parent_args(repo, num)` → `["api", f"repos/{repo}/issues/{num}/parent"]`
  - `blocked_by_args(repo, num, blocker_id)` →
    `["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by", "-F", f"issue_id={blocker_id}"]`
  Argv builders only — the module executes nothing; each caller executes with its own runner, because
  `wayfind.py` dies exit 1 and is dry-run by default while `gh-sync.py` skips exit 0 (D-03).
- intent, `wayfind.py` side — **exactly three call sites convert, and the two list reads do not**:
  - import the module with `sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))`
    (`realpath`, not `abspath`: reached through a symlink, `abspath(__file__)` resolves to the
    symlink's directory, not the module's).
  - `parent_of()` (`:147`) takes its argv from `parent_args`.
  - the `ticket` attach (`:271-272`) takes its argv from `internal_id_args` and
    `attach_sub_issue_args`.
  - the `block` edge (`:279-281`) takes its argv from `internal_id_args` and `blocked_by_args`.
  - **`sub_issues()` (`:113`) and `blockers()` (`:117`) are NOT touched. Their endpoint strings stay
    inline.** They are wayfinding list reads with one caller, not among REQ-06's three primitives,
    and D-03 fixes the module at three primitives plus `gh_bin()`. Do not add list builders; do not
    "finish the job" by moving them. They are also the reason SC-06's checks are payload-scoped: the
    string `repos/{repo}/issues/{num}/sub_issues` must still appear in `wayfind.py` after this task.
- intent, deviations from byte-identical — **this list is exhaustive; anything else is a defect**:
  1. `GH_SYNC_GH` now influences `wayfind.py` too, via `gh_bin()` in `gh_json()` and `do()`. Intended:
     it is what lets a fake intercept helper-built calls.
  2. The `ticket` dry-run print at `:262-263` stays **verbatim**, including its literal
     `-F sub_issue_id=<...>` prose. It is documentation of the trap, not an argv build — which is why
     SC-06's check is scoped to the argv form `"-F", f"sub_issue_id=` and not the bare substring.
  3. The third `"gh"` site — `append_gist`'s direct `subprocess.run(["gh", "issue", "edit", …])` at
     **`:173`** — converts to `gh_bin()`. Named explicitly because `! grep -q '"gh"'` catches it
     loudly and the wrong repair under pressure is to weaken the grep.
  4. **`:270`'s redundant `issue(repo, num, "id")` pre-attempt is left exactly as it is.** It is a
     pre-existing redundancy (two `issue view` calls before the `--jq .id` fallback at `:271`);
     deleting it would change the live call count, which "byte-identical" forbids. Out of scope,
     noted so it is not tidied silently.
- verify:
  - `python3 -c "import sys;sys.path.insert(0,'.claude/skills/harness/bin');import gh_issues as g;print(g.gh_bin(),g.internal_id_args('o/r',5),g.attach_sub_issue_args('o/r',1,999),g.parent_args('o/r',5),g.blocked_by_args('o/r',5,7))"`
    → exit 0, prints the five forms above. `observed @f929d44: exit 1` (ModuleNotFoundError — not a
    discriminating receipt, but it does prove the module does not exist yet).
  - `! grep -qF '"-F", f"sub_issue_id=' .claude/skills/harness/bin/wayfind.py` → exit 0.
    `observed @f929d44: exit 1` (matches `:272` — **correctly fails today**).
  - `! grep -qF '"-F", f"issue_id=' .claude/skills/harness/bin/wayfind.py` → exit 0.
    `observed @f929d44: exit 1` (matches `:281`). The `-F`-scoped form is required: a bare
    `issue_id=` also matches `sub_issue_id=` at `:263` and `:272`.
  - `! grep -qF '"--jq", ".id"' .claude/skills/harness/bin/wayfind.py` → exit 0.
    `observed @f929d44: exit 1` (matches `:271`, `:279`). **Use this exact literal, two argv items.**
    `grep -- '--jq .id'` is a **false green** — it returns zero matches today
    (`observed @f929d44: exit 0`) and would pass vacuously forever.
  - `! grep -q '/parent"' .claude/skills/harness/bin/wayfind.py` → exit 0.
    `observed @f929d44: exit 1` (matches `:147`). Legal despite looking path-shaped: the parent read
    has no retained twin.
  - The carve-out must **still be there** afterwards, so these are *presence* checks, not absence:
    `grep -c 'sub_issues", "--paginate"' .claude/skills/harness/bin/wayfind.py` → **1**
    (`observed @f929d44: 1` — `:113`, unchanged by this task, non-discriminating by design), and
    `grep -c 'dependencies/blocked_by",$' .claude/skills/harness/bin/wayfind.py` → **1**
    (`observed @f929d44: 2` — `:117` the retained list GET and `:280` the extracted write; after the
    task only `:117` remains, so this one *is* discriminating in both directions: 2 today, 1 after,
    and **0 would mean the list GET was wrongly extracted**).
  - `! grep -q '"gh"' .claude/skills/harness/bin/wayfind.py` → exit 0.
    `observed @f929d44: exit 1` (matches `:69`, `:86`, `:173`).
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0.
    `observed @f929d44: exit 127` (T-01 not landed — not discriminating).

### T-03 — `open` creates one sub-issue per `T-NN` under one recorded parent
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-01, REQ-05, SC-01, SC-05, SC-12, D-01
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent:
  - `parse_brief` also returns `phrase`: the H1's trailing segment — from
    `# BRIEF — <feat-id> — <human phrase>`, take what follows the second em-dash; empty if absent.
    **When the phrase is empty the title is the bare feat-id with no trailing em-dash** — not
    `FEAT-05-export-fix — FEAT-05-export-fix`.
  - `load_recorded` reads `parent` from the `github:` block (`^\s*parent:\s*(\d+)`; `none`/absent →
    `None`) plus an `attached:` list of `T-NN` ids **and `parent_origin`**, and `save_recorded` writes
    `parent:`, `parent_origin:` and `attached:` alongside `milestone:` and `issues:`. **Both extend — today `save_recorded`
    regexes out the whole `github:` block and rewrites it as milestone+issues, which would delete
    the `parent: none` line this feature's own `feature.yaml` already carries.**
  - **On-disk forms, pinned — this is a corruption trap, not a style choice.** `load_recorded`'s
    issue reader is `^\s{4}(T-\d+):\s*(\d+)` (exactly four spaces, `T-NN`, digits), so a nested
    mapping under `attached:` (`    T-01: 1`) is re-read as an issue number and SC-05's round trip
    silently corrupts the issue map. Write `attached:` as a **single-line inline list at two-space
    indent**: `  attached: [T-01, T-02]`, and `  attached: []` when empty. The null parent is
    lowercase `none` (`  parent: none`) — `f"  parent: {rec['parent']}"` would emit the literal
    `None`, which neither the template nor INV-21 recognises.
  - **The origin receipt is a sibling key at two-space indent, chosen over a flag on the `parent:`
    line precisely because it leaves that line's shape untouched.** On disk, byte-exact:
    `  parent_origin: created` · `  parent_origin: adopted` · `  parent_origin: none` when there is
    no parent. `load_recorded` reads it with `^\s*parent_origin:\s*(created|adopted)\b` (anything
    else, including absent → `None`), `save_recorded` emits
    `f"  parent_origin: {rec['parent_origin'] or 'none'}"`, and the line is written **before
    `  issues:`** — `issues:` stays last because its entries are the only nested ones, and any key
    written after it would land inside the issue mapping. Verdicts on the three readers of this
    shape, each checked rather than assumed:
    1. **The issues reader `^\s{4}(T-\d+):\s*(\d+)` (`gh-sync.py:152`) — unaffected.** Two-space
       indent and the key is not `T-NN`, so nothing is re-read as an issue number. A nested mapping
       under a new key *would* have corrupted the issue map; that is why the form is a flat scalar.
    2. **`load_recorded`'s parent reader and `save_recorded`'s writer — extended, exactly as
       specified above.** The existing `^\s*parent:\s*(\d+)` cannot false-match
       `  parent_origin: created` (it fails at the `_`), so the number and the origin are read by two
       independent, non-overlapping patterns and neither shadows the other.
    3. **T-07's INV-21 — unaffected: no intent change, no fixture change, no new `ok` label.** It
       keys on a numeric `parent:`, and the origin key cannot satisfy that pattern anchored or
       unanchored because its values are never numeric. Verified, not patched — **T-07's intent,
       fixtures and `ok` labels are unchanged by this receipt.** (Its prose carries one
       terminology-only rename at `:529`, from CHANGE 2, which touches no detection logic.)
  - **`parent` and `parent_origin` are written by the same `save_recorded` call, always.** A crash
    between the two would leave a created parent reading as absent-origin, which degrades to
    leave-open and reproduces the exact orphan the receipt exists to prevent — DEC-131 crash
    discipline, the same reasoning as the attach receipt below.
  - `main()` accepts an optional `--parent <n>` for `open`, stripped from argv before dispatch.
  - `cmd_open`: after the milestone step, resolve the parent by D-01's precedence, **recording
    `rec["parent_origin"]` in the same `save_recorded` call as `rec["parent"]`** — `adopted` for
    precedence branches 1 and 2, `created` for branch 3. A parent already recorded with an origin
    keeps it; a parent already recorded *without* one is left without one (SC-10 forbids editing an
    existing `github:` block, and absent means leave-open, which is the safe reading). Adopted (recorded
    or `--parent`) → record it and print `parent #<n> adopted`; none → create the issue with
    `--title "<feat-id> — <phrase>"` (or the bare feat-id if the phrase is empty), `--body` = BRIEF
    `## Problem` + `\n\n**Goal:** ` + `## Goal`, `--label harness`, no milestone; record it
    **immediately** (DEC-131 crash discipline, as the milestone already does) and print
    `parent #<n> created`.
  - Per task, unchanged: create the issue exactly as today (title, body, `absorbs:` citation,
    derived labels, milestone), record, save. Then **attach it to the parent**: look up the child's
    internal id via `internal_id_args`, then POST `attach_sub_issue_args`. Both calls go through the
    existing `gh()` helper, so a failure is a SKIP exit 0, never a gate. **The attach carries its own
    receipt:** on success append the `T-NN` to `rec["attached"]` and `save_recorded` immediately.
    The idempotency test is per-step, not per-task — a task in `rec["issues"]` skips the *create*, a
    task in `rec["attached"]` skips the *attach*. Without the second receipt, a crash between
    recording and attaching (the failure `gh-sync.py:204-208` memorialises for the milestone) would
    leave a recorded-but-unattached, permanently unreachable sub-issue that no re-run repairs and
    INV-21 cannot see, because the parent *is* recorded. Re-attaching an already-attached child would
    422, which is why the receipt is what gates it rather than a lookup.
  - Do **not** import or call `parent_args`/`blocked_by_args` (BRIEF `## Out of scope`, D-01).
  - In `test-gh-sync.py`, extend the fake `gh` to answer the two new API shapes: a GET of
    `repos/*/issues/<n>` (with `--jq .id`) echoes a **distinct** internal id derived from the
    number, `9000<n>`; a POST to `repos/*/issues/<n>/sub_issues` echoes `{}`. Without this both
    calls fall through to bare `exit 0` with empty stdout and the attach would post an empty
    `sub_issue_id`. **Give fixture H1 a human phrase** — its BRIEF (`test-gh-sync.py:48`) is
    `# BRIEF — FEAT-05-export-fix` with none, so the phrase-parsing path is otherwise only ever
    exercised on its empty fallback. Assert both: a phrase-bearing H1 titles the parent
    `<feat-id> — <phrase>`, and an H1 with no phrase titles it the bare feat-id.
    Add assertions with these exact `ok` labels (each verified absent from today's output):
    parent created and recorded in `feature.yaml`; three sub-issues created (unchanged count) and
    **three** attach POSTs to the parent's `/sub_issues`; every attach carries `sub_issue_id=9000…`,
    i.e. the internal id and **not** the issue number; `--parent 55` adopts instead of creating; a
    re-run creates and attaches nothing; **crash resume** — pre-seed a `feature.yaml` whose
    `github:` block has `issues: {T-01: 41}` and no `attached:` entry for it, run `open`, assert
    exactly one attach POST for T-01 and no `issue create` for it; **round trip both ways** — a
    `feature.yaml` that already carries `parent: 40` still carries it after the per-task
    `save_recorded` calls, and the issue map survives writing the parent.
    **Three more, all for the origin receipt (SC-05's landing site is here, not in a task of its
    own):** a created parent writes `  parent_origin: created` on disk and `load_recorded` reads it
    back as `created`; `--parent 55` writes `  parent_origin: adopted`; and the origin **survives the
    per-task `save_recorded` calls** — read the file after the last task and assert the line is still
    there, since the round-trip trap at `save_recorded` (it rewrites the whole `github:` block) is
    exactly what would drop it and make SC-03's parent distinction undecidable again. Assert on the
    file text, not only on the in-memory `rec`.
- verify:
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0, with `ok` lines for
    "parent created and recorded", "three sub-issues attached to the parent", "attach uses internal
    id not number", "--parent adopts", "re-run open creates nothing", "recorded-not-attached task is
    attached on re-run", "pre-existing parent survives per-task saves", "parent title carries the
    H1 phrase", "empty phrase titles the parent with no trailing em-dash", "created parent records
    origin created", "adopted parent records origin adopted", "parent_origin survives per-task
    saves", and the retained "re-run open creates nothing".
    `observed @f929d44:` `python3 .claude/skills/harness/bin/test-gh-sync.py` exits 0 / `ALL PASSED`,
    and `grep -cF` was run for every label above against that output:
    - **absent today (`0`), so discriminating** — "parent created and recorded", "three sub-issues
      attached to the parent", "attach uses internal id not number", "--parent adopts",
      "recorded-not-attached task is attached on re-run", "pre-existing parent survives per-task
      saves", "parent title carries the H1 phrase", "empty phrase titles the parent with no trailing
      em-dash", and this cycle's three origin-receipt labels — "created parent records origin
      created", "adopted parent records origin adopted", "parent_origin survives per-task saves"
      (each `grep -cF` = **0** against the suite output produced by
      `python3 .claude/skills/harness/bin/test-gh-sync.py`, run on a tree byte-identical to
      `f929d44` under `.claude/skills/harness/bin/**` — the same equivalence `## Verify receipts`
      relies on, re-verified empty this cycle). Eleven of the twelve.
      Two source-side receipts for the same, also run: `grep -c parent_origin
      .claude/skills/harness/bin/gh-sync.py` is **0** and the same against `test-gh-sync.py` is
      **0** — both must be ≥1 after this task.
    - **already present today (`1`) and already passing** — "re-run open creates nothing"
      (`test-gh-sync.py:172`). It is **retained as the idempotency guard, not evidence of change**:
      it must keep passing once the attach step exists, which is a real regression risk, but it
      proves nothing about this task on its own.
  - `! grep -nE 'parent_args|blocked_by_args' .claude/skills/harness/bin/gh-sync.py` → exit 0.
    `observed @f929d44: exit 0` — **this one passes today and is therefore NOT evidence that T-03
    changed anything.** It is written in as a **standing regression guard** for D-01 and SC-06's
    second half: it turns "a future scan will re-suggest importing the parent read" from a warning
    into a check that fails the moment someone does.

### T-04 — `close-task` closes exactly one issue; `absorbs:` stops closing
- owner: harness-backend-dev
- change_type: bugfix
- traces: REQ-02, REQ-03, D-02
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: delete the `for n in tasks.get(tid, {}).get("absorbs", [])` loop and its two `gh issue
  close` calls from `cmd_close_task` (`gh-sync.py:240-242`). The function closes `rec["issues"][tid]`
  and nothing else.
  **The contradiction in the reviewed plan is resolved as: keep `parse_tasks`, keep the print.**
  The two were mutually exclusive — the absorbed numbers exist only in `PLAN.md` via `parse_tasks` —
  and the print wins because it is where the operator sees *where the absorbed items went*, and
  because keeping the call preserves `close-task`'s existing exit-1-on-unparseable-`PLAN.md`
  behaviour (a caller-error guard, DEC-138's split, worth not losing by accident). So: the
  `parse_tasks(feat_dir)` call **stays**, and after the close the command prints one line naming any
  absorbed numbers as **left open for the ship briefing**.
  Consequence for the guard, and it is the reason MF-2 was filed: the negative assertion must be
  scoped to the **fake-gh call log**, never to stdout — the new print line contains `#12` and `#14`
  by design, so a stdout-wide substring test would fail on this task's own output. Use a
  `not any(...)` over the same whitespace-delimited `closes` list the current assertion uses.
  In `test-gh-sync.py`, this is an **inversion of two existing assertions, not an addition**: line
  177's `close-task closes issue + 2 absorbed` / `len(closes) == 3` becomes
  `close-task closes exactly one issue` / `len(closes) == 1`, and line 178's `absorbed #12 #14
  closed` becomes the positive regression guard **`absorbed #12 #14 NOT closed`**. Do not delete
  either assertion; a dropped assertion loses the guard.
- verify:
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for "close-task closes
    exactly one issue" and "absorbed #12 #14 NOT closed".
    `observed @f929d44:` today's suite exits 0 and `grep -cF` was run for both labels against its
    output — **0** and **0** (today's output carries the two labels being inverted instead:
    `close-task closes issue + 2 absorbed` and `absorbed #12 #14 closed`) — discriminating.
  - `! grep -qE 'len\(closes\) == 3|absorbed #12 #14 closed' .claude/skills/harness/bin/test-gh-sync.py`
    → exit 0. `observed @f929d44: exit 1` (both strings present at `:177-178` — correctly fails today).

### T-05 — `cmd_abandon --reason-file`: the second terminal state
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-04, SC-03, SC-12, D-01
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: a **new** subcommand (`gh-sync.py abandon <feature-dir> --reason-file <path>`) wired into
  `main()`'s dispatch and the module docstring's usage block.
  **The file-bearing-post contract, classified under DEC-138's split (exit 1 = caller error, exit 0 +
  SKIP = environmental). Add one helper, `post_body_path(path, flag)`, and use it for both this
  subcommand's `--reason-file` and T-06's `--body-file`:**
  - flag missing entirely → `die` (exit 1).
  - path is not a file (`os.path.isfile` false) → `die` (exit 1).
  - file exists but is **empty** (`os.path.getsize(path) == 0`) → `die` (exit 1). This is the sharp
    one: `isfile` passes, `gh` rejects the post, `gh()` converts that rejection into a SKIP exit 0 —
    so an abandonment would post no reason and report success. An empty artifact handed by the
    dispatch is a caller error, never environmental.
  - file exists but is **unreadable** (`open(path).read()` raises `OSError`) → `die` (exit 1). Same
    contract, same reason: the dispatch handed a bad artifact. The read is a validation read only;
    the post still passes the **path** to `--body-file` (DEC-138 am.6 — the mirror never composes).
  No recorded milestone **and** no recorded issues → `skip` (environmental: `open` was never run).
  Sequence, all through `gh()` so environmental failure is one SKIP line exit 0:
  1. Post the reason on the parent, verbatim from the path:
     `gh issue comment <parent> --repo <repo> --body-file <path>`. No parent recorded → print one
     line saying the reason was not posted, and continue.
  2. Close each `rec["issues"]` value with `state_reason: not_planned`:
     `gh api -X PATCH repos/<repo>/issues/<n> -f state=closed -f state_reason=not_planned`. The enum
     is exactly `completed`/`not_planned`/`duplicate` — `not_doing` is a 422 (DEC-138 am.5), so do
     not invent a value or a label.
  3. Close the milestone — **only if one is recorded.** `gh api -X PATCH
     repos/<repo>/milestones/<n> -f state=closed` (milestones take no `state_reason`). The skip
     condition above is `no milestone AND no issues`, so *issues recorded with no milestone* reaches
     this step and an unconditional PATCH would build the URL `milestones/None`. `cmd_ship` guards
     this at `gh-sync.py:269-270`; `abandon` must too — and it is reachable via exactly the partial
     `github:` block T-07's INV-21 exists to detect. Guard it with `if rec["milestone"] is not
     None:`, else print one line saying no milestone was recorded and **exit 0** — the sub-issues
     were already closed, so this is neither `skip()` (work happened) nor `die` (nothing is wrong
     with the caller).
  4. **The parent's fate is conditional on `rec["parent_origin"]` (D-01, SC-03) — it is not
     unconditional leave-open.**
     - `adopted` → **leave OPEN.** Someone else's live item; closing it would assert something false.
     - `created` → **close it with `state_reason: not_planned`**, using the *same* PATCH form as step
       2 (`gh api -X PATCH repos/<repo>/issues/<parent> -f state=closed -f state_reason=not_planned`),
       not `gh issue close`. One form means one fake-`gh` case and one enum, so am.5's `not_doing`
       422 cannot creep back in. A created parent exists only to hold this feature's tasks: left open
       with every child closed it is an orphan nobody wants and nothing will ever close, and
       `not_planned` asserts nothing false about it.
     - **absent or unrecognised origin → leave OPEN.** The specified default, not an undefined case:
       SC-10 forbids editing an existing `github:` block, so every pre-existing feature (this one
       included — `feature.yaml:41` is `parent: none`) reaches `abandon` with no marker, and the false
       assertion is the strictly worse of the two errors.
     This preserves the grilling's decision (`:34-35`, "leaves an **adopted** parent open") and adds
     the origin D-01 introduced afterwards; it does not reopen it.
  Do not read or assert on `sub_issues_summary` (eventually consistent, DEC-168). Tests: fake `gh`
  needs a case for `api -X PATCH repos/*/issues/*` echoing `{}`. Assert — one PATCH per recorded
  task issue, each carrying `state_reason=not_planned`; the milestone PATCHed closed;
  **the parent, in three fixtures, and each assertion is scoped to the parent's own URL over the
  fake-gh call log — never to a bare `state_reason=not_planned` count, because step 2 already emits
  one of those per sub-issue:**
  - `parent: 40` + `parent_origin: adopted` → **no call naming #40 in either close form.** Cover
    **both** shapes — `issue close 40` and `PATCH repos/*/issues/40` — since an implementation
    closing it by the other form would otherwise pass a one-form check (the MF-1 class).
  - `parent: 40` + `parent_origin: created` → **exactly one** call whose URL ends `issues/40`,
    carrying `state=closed` **and** `state_reason=not_planned`, and no `issue close 40`.
  - `parent: 40` and **no `parent_origin:` line at all** — exactly `feature.yaml:41`'s shape but with
    a real number, so the default is actually exercised rather than passing vacuously on a null
    parent → **no call naming #40 in either form.** Without this fixture the absent-origin default is
    a third state with no test. **The fixture's premise is protected because `cmd_abandon` writes no
    receipt: steps 1–4 close and comment only, and never call `save_recorded`** — so the absent
    `parent_origin:` line cannot be back-filled mid-test by T-03's writer. Assert the line is still
    absent from the file after the run, which is what makes that property checked rather than assumed.
  Also assert: the comment call uses `--body-file` and the log contains none of the file's
  text; missing `--reason-file` → exit 1; an **empty** reason file → exit 1 and **zero** gh calls;
  issues recorded with `milestone: none` → exit 0, subs PATCHed, and **no** call whose URL contains
  `milestones/None`; `sync: false` → SKIP exit 0.
- verify: `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for "abandon closes
  3 subs not_planned", "abandon closes the milestone", **"abandon leaves an adopted parent open"**,
  **"abandon closes a created parent not_planned"**, **"abandon leaves a parent with no recorded
  origin open"**, "abandon
  posts via --body-file", "abandon without --reason-file exits 1", "abandon with an empty reason file
  exits 1", "abandon with no recorded milestone never builds milestones/None". The single label
  "abandon leaves the parent open" is **gone — it split into the three parent labels above**, because
  one label cannot report a conditional and would have gone green defending the wrong behaviour.
  `observed @f929d44:` today's suite exits 0 / `ALL PASSED` and `grep -cF` was run for each of those
  nine labels against its output — **all 0**, none pre-exists (the retired label greps **0** as well,
  so nothing is being left behind). Also
  `grep -c 'def cmd_abandon' .claude/skills/harness/bin/gh-sync.py` → **0** (run, not assumed).
  Discriminating on every line.

### T-06 — `ship` closes the milestone, and the parent only if `open` created it
- owner: harness-backend-dev
- change_type: logic
- traces: REQ-04, SC-04, SC-12, D-01
- files: edit `.claude/skills/harness/bin/gh-sync.py`, edit `.claude/skills/harness/bin/test-gh-sync.py`
- intent: `cmd_ship` gains an optional `--body-file <path>` (stripped in `main()`), validated by
  **T-05's `post_body_path` helper — identically: missing flag value, non-file, empty file and
  unreadable file are all `die` exit 1.** One contract, one implementation, so the two subcommands
  cannot drift; T-05 lands first and owns the helper. Order: if `--body-file` is given and a parent
  is recorded, `gh issue comment <parent> --repo <repo> --body-file <path>` (the signed ship review,
  verbatim — DEC-138 am.6); then the parent's close, conditional per below; then PATCH the milestone
  closed exactly as today. **The comment is UNCONDITIONAL** — it posts on any recorded parent
  whatever its origin, because commenting on an adopted parent asserts nothing false, and T-05 step 1
  has the identical shape. Only the close branches.
  **The parent's close is conditional on `rec["parent_origin"]` (D-01, SC-04) — the mirror image of
  T-05 step 4, not an unconditional close:**
  - `created` → **close it**, `gh issue close <parent> --repo <repo>` — i.e. `state_reason:
    completed`, the default. **The close form is unchanged from the reviewed plan** (not the PATCH
    form T-05 uses for its `not_planned` close), so the existing fake-`gh` `issue close` case covers
    it untouched. A created parent exists only to hold this feature's tasks, so when they are all
    closed it is genuinely done.
  - `adopted` → **leave OPEN.** Closing someone else's live backlog item as `completed` asserts that
    the user's item is done — exactly as false as closing it `not_planned` would have been.
  - **absent or unrecognised origin → leave OPEN.** The specified default, not an undefined case, and
    the same one T-05 step 4 carries: SC-10 forbids editing an existing `github:` block, so every
    pre-existing feature (this one included — `feature.yaml:41` is `parent: none`) reaches `ship` with
    no marker, and the false assertion is the strictly worse of the two errors.
  **The milestone is unaffected: it PATCHes closed in all three cases.** No recorded parent → close
  the milestone only and print one line saying so; no recorded milestone → `skip`, as today
  (unchanged, `gh-sync.py:269-270`).
  Tests — **the parent, in three fixtures, each assertion scoped to the parent's own number over the
  fake-gh call log:**
  - `parent: 40` + `parent_origin: created` → **exactly one** `issue close 40`, and the milestone
    PATCHed closed **after** it (the ordering assertion lives inside this fixture's assertion body,
    not in a label of its own — a compound label cannot report which half broke).
  - `parent: 40` + `parent_origin: adopted` → **no call naming #40 in either close form.** Cover
    **both** shapes — `issue close 40` and `PATCH repos/*/issues/40` — since an implementation closing
    it by the other form would otherwise pass a one-form check (the MF-1 class). Assert in this same
    fixture that the milestone **is** still PATCHed closed, which is the discriminating case for
    "the milestone is unconditional": a close of both under one `if origin == "created":` would pass
    every parent label and the retained milestone assertion, and nothing else would catch it. **This
    fixture is where the `ok` label "ship closes the milestone regardless of parent origin" is
    emitted, once**; the other two fixtures assert the milestone inline, unlabelled.
  - `parent: 40` and **no `parent_origin:` line at all** → **no call naming #40 in either form**, and
    the milestone still PATCHed closed. Without this fixture the absent-origin default is a third
    state with no test, distinct from recognised-`adopted`. **The fixture's premise is protected
    because `cmd_ship` writes no receipt: `save_recorded` greps 0 in `cmd_ship`'s region
    (`gh-sync.py:267` to end of file, verified this cycle at `a8fce12`)** — so the absent
    `parent_origin:` line cannot be back-filled mid-test by T-03's writer. Assert the line is still
    absent from the file after the run, which is what makes that property checked rather than assumed.
  Also assert: `--body-file` posts once via `--body-file` (on an adopted parent, so the comment's
  unconditionality is what is being checked); ship without `--body-file` posts nothing; `--body-file`
  naming an empty file exits 1 with zero gh calls.
- verify: `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 with `ok` lines for **"ship closes a
  created parent completed"**, **"ship leaves an adopted parent open"**, **"ship leaves a parent with
  no recorded origin open"**, **"ship closes the milestone regardless of parent origin"**, "ship
  --body-file posts once", "ship without --body-file posts nothing", "ship with an empty body file
  exits 1". The single label "ship closes parent then milestone" is **gone — it split into the three
  parent labels above plus the milestone label**, because one label cannot report a conditional and
  would have gone green defending the wrong behaviour.
  `observed @f929d44:` today's suite exits 0 / `ALL PASSED` and `grep -cF` was run for each of those
  seven labels against its output — **all 0**, none pre-exists, and the **retired** label "ship closes
  parent then milestone" greps **0** as well, so nothing is left behind. The only ship assertion
  present today is `ship PATCHes milestone closed` (`test-gh-sync.py:185-186` — the reviewed plan's
  `:186` was the assertion's second line; the label is at `:185`), which this task must keep passing.
  The suite was run with `python3 .claude/skills/harness/bin/test-gh-sync.py` on a tree byte-identical
  to `f929d44` under `.claude/skills/harness/bin/**` (`git diff --stat` empty, re-run this cycle at
  `a8fce12`), the same equivalence `## Verify receipts` relies on; `run-unit-tests.sh` itself does not
  exist until T-01 lands. Discriminating on every line.

### T-07 — INV-21: a mirrored feature with no recorded parent
- owner: harness-dev-ops
- change_type: logic
- traces: REQ-07, SC-08, D-05
- files:
  - edit `.claude/skills/harness/bin/check-state.sh`
  - create `.claude/skills/harness/bin/test-check-state.py`
  - edit `.claude/skills/harness/bin/run-unit-tests.sh` (add the new script to the explicit list)
- intent: in `check-state.sh`'s embedded python block, after the INV-20 block (`:342`) and before
  INV-13 (`:366`), add **INV-21 at warn level** (`warn.append`, never `bad`): when `harness.json`
  `github.sync` is true (`cj` is already in scope there), then for each
  `.harness/features/*/feature.yaml` whose `github:` block has a non-empty `issues:` map and no
  numeric `parent:`, warn naming the feature — the feature's task issues exist but their container is
  unrecorded, so `ship` and `abandon` cannot close it and `open` will not re-derive it (the mirror is
  write-only, DEC-138). `INV-21` is a free number (0 matches in the file today). Parse with the same
  regex-on-text style the file already uses; no YAML dependency. It must stay **vacuous when
  `github.sync` is false**, which is the case in this repo, so the check costs nothing here.
  `test-check-state.py` builds temp dirs and runs `check-state.sh` with `CLAUDE_PROJECT_DIR` pointed
  at each (the script already honours it, `check-state.sh:14`), asserting: (a) `sync: true` +
  `issues: {T-01: 41}` + no `parent` → the INV-21 note appears and the exit code is unchanged by it;
  (b) same fixture with `parent: 40` → no INV-21 note; (c) `sync: false` + issues + no parent → no
  INV-21 note. Fixtures need whatever minimal `.harness/` shape the earlier invariants require to
  avoid unrelated violations; assert on the INV-21 substring, **never** on the whole output.
- verify:
  - `python3 .claude/skills/harness/bin/test-check-state.py` → exit 0, three cases pass.
    `observed @f929d44: exit 2` (file absent — not discriminating). Discriminating receipt:
    `grep -c 'INV-21' .claude/skills/harness/bin/check-state.sh` is **0** today and must be ≥1 after.
  - `.claude/skills/harness/bin/run-unit-tests.sh` → exit 0 (the new script is listed, so the orphan
    check does not fire; an unlisted one would exit **2**). `observed @f929d44: exit 127`.
  - `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh` → its output contains **no**
    `INV-21` line in this repo (`github.sync` is false), and its **exit code is unchanged from the
    pre-change baseline**. `observed @f929d44: exit 1` — do **not** assert exit 0 here: the 1 comes
    from `FEAT-03-subissue-mirror/BRIEF.md is NOT approved` plus an orphaned run dir, both unrelated
    to this task. Record the baseline before the edit and compare.

### T-08 — record the reversed contract in DECISIONS.md
- owner: harness-documentor (product squad — routed laterally, see `## Preconditions and hand-offs`)
- change_type: docs
- traces: REQ-09, SC-11, D-02
- files: edit `docs/harness/DECISIONS.md`
- intent: append **DEC-138 amendment 7** (verified free: `grep -c 'amendment 7'` is 0 and am.6 at
  `:4271` is the last) recording, in the file's existing voice: one sub-issue per `T-NN` under one
  parent per feature; the parent adopted-or-created and **recorded** at `feature.yaml github.parent`,
  never discovered; `close-task` closes exactly one issue and **`absorbs:` no longer closes
  anything** — explicitly superseding am.1's "they close with it", with the reason (partial
  absorption is the norm; a work item changes state through a human signature); `ship` closes the
  milestone unconditionally, `abandon` closes the feature's sub-issues `not_planned` and closes the
  milestone, and **both terminal subcommands branch on the parent's recorded origin**
  (`feature.yaml github.parent_origin`) — a parent `open` created is closed by `ship` with the default
  `completed` and by `abandon` as `not_planned`, while an adopted parent and an absent origin are left
  **open by either**. Record the reasons, since they are what stops the branch being re-litigated: a
  created parent is this feature's own container, and left open with every child closed it is an
  orphan nothing will ever close; closing an adopted one asserts something false about someone else's
  live item, whichever `state_reason` is used; and **absent origin defaults to leave-open** — record
  that default explicitly, since no pre-existing feature carries the marker. Name the
  `abandon` row's existence so a reader is not left with three sync points; the three
  primitives now live in `bin/gh_issues.py`; migration is new features only. Note that Feature B
  (`depends_on:`, `blocked_by` edges) is sequenced separately and that no `blocked_by` edge is
  emitted by the GitHub Issues sync yet.
  **Declare NO `<!-- stale: … -->` marker for the two `.claude/skills/harness/SKILL.md` phrases
  (`:137` "closes its issue and everything it absorbs", `:144` ship "closes the milestone"), and
  record instead, in the amendment's prose, that those edits are a named main-session pre-ship
  step.** The consequence is stated in `## Preconditions and hand-offs` and is deliberate:
  `check-docs.sh` scans `.claude/skills/**/*.md`, so a marker declared while the phrases are live
  turns it red and gates every `/harness` entry on an edit no agent domain covers. `check-docs.sh`
  therefore stays green and is **silent about that gap**; SC-13's grep at the ship gate is what
  carries it. Declare markers only for wording that this feature's own tasks have already changed
  inside `docs/**`.
- verify:
  - `.claude/skills/harness/bin/check-docs.sh` → exit 0, "no stale statements found".
    `observed @f929d44: exit 0` (45 patterns across 69 files) — **a baseline, not a discriminating
    receipt**: this task's contract is that the checker's status does not change.
  - `grep -c 'amendment 7' docs/harness/DECISIONS.md` → ≥1. `observed @f929d44: 0` — discriminating.
  - `CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/check-state.sh` → output contains no
    `INV-10` line, and the exit code is unchanged from the pre-change baseline.
    `observed @f929d44: exit 1, no INV-10 line` — as in T-07, do not assert exit 0.

## Approval

status: pending
