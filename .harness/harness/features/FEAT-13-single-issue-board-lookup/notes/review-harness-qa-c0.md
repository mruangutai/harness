# QA gate re-run (reviewer panel) — FEAT-13 T-01 — pinned at `d4951c2`

## The pin, verified

`git diff --stat 56abf27..d4951c2` — confirmed empty of source: touches only `feature.yaml`,
`notes/qa-FEAT-13-T-01-c0.md`, `receipt-harness-backend-dev-live-spot-check.md`. The real source
diff is `6dfbf7c..56abf27` (== `6dfbf7c..d4951c2` on source paths); `d4951c2` adds only the T-02
receipt/note. Re-running the matrix at `d4951c2` therefore re-executes the SAME tree my prior gate
already passed at `56abf27` — no new source to re-review, just a fresh execution at the SHA the
panel pins.

## Matrix result — `matrix_ok: true`

`change_type: cross_module` requires `unit` + `integration`, always (`.harness/harness.json`).
Ran the CONFIGURED commands (not the task's narrower `verify:` line):

- `unit`: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0. 10 scripts green,
  including `test-factory-claim.py` 95/95, `test-factory-land.py` 56/56, `test-factory-gh.py`,
  `test-factory-decompose.py` all green.
- `integration`: `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` — exit 0. All
  named suites green, including `test-factory-integration.py` 97/97 and `test-check-state.py`.

Both kinds `status: active` with real `cmd`; both ran against a tree where the required-kind test
files are themselves part of the source diff (P-05). No `functional`/`component`/`ui`/`eval`
kind is triggered by `cross_module`.

**Configured vs. task `verify:` command — they DO diverge (G-04), gated on the broader one.** The
task's own `verify:` ran `test-factory-integration.py` directly, one script. The CONFIGURED
`integration` command (`run-unit-tests.sh --kind integration`) runs the full integration bucket —
11+ scripts including `test-check-state.py`, `test-bash-write-guard.py`, `test-gh-sync.py`, etc.
— of which `test-factory-integration.py` is one. Both passed here, so the divergence didn't change
the outcome this run, but the gate is taken on the CONFIGURED command per dispatch instruction, not
the task's narrower one.

**SC-01..SC-09 evidence — carried forward, not re-derived this run.** This dispatch is GATE-ONLY
re-execution at a pin confirmed source-identical to `56abf27` (see above); I did not re-walk each
SC's `file:line` anchor this pass. The per-SC table in
`notes/qa-FEAT-13-T-01-c0.md` (written at `56abf27`) stands as the evidence, on the basis that the
source tree is byte-identical at `d4951c2` — verified by the diff-stat above, not re-asserted from
memory.

## Routed coverage question — answered

**Direct answer first: the specific always-refuse hypothesis in the dispatch — "an
implementation where `.get("state")` returns `None` because `state` was never fetched on that
path, so `!= OPEN` is always true" — WOULD be caught, loudly, if the bug were "drop `state` from
the check condition" or "the field simply isn't in the dict the code branches on."** Four named
assertions redden under that shape:

- `test-factory-claim.py:472` (R4/61, `--issue`) — expects exit **3** (lost race at `create_ref`);
  an always-refuse would exit 2 before ever reaching `create_ref`.
- `test-factory-claim.py:487` (R4/62, `--issue`, self-owned re-entry) — expects exit **0**.
- `test-factory-claim.py:718` (B7, `--issue`, blocked) — expects stderr to name the blocking
  `T-02`; a state refusal instead of the blocker-gate refusal names neither.
- `test-factory-claim.py:330,343,381` (poll mode, M7/M4/C2) and `test-factory-land.py:192,224`
  (M1) — all expect exit 0 on the (explicit-default) OPEN fixture.

So the coarse "always refuses" shape is covered. **The gap is one level down, and it is
demonstrated, not just reasoned about — see the mutant proof below.**

### Proven gap: the fields list requested from `issue_view` is unpinned, on BOTH call sites

`test-factory-claim.py`'s and `test-factory-land.py`'s fakes for `issue_view(repo, number,
fields)` **ignore the `fields` argument entirely** and return a canned dict regardless of what was
asked for:

- `test-factory-claim.py:100-105` — `Recorder.issue_view` returns `dict(self.issue_data[num])`,
  never consulting `fields`.
- `test-factory-land.py:104-106` — `Recorder.issue_view` returns
  `{"title": self.issue_title, "state": self.issue_state}` unconditionally.

Neither suite has an assertion pinning the *literal fields tuple* passed to `issue_view` at the
call sites (`factory_claim.py:274`: `["number", "title", "state", "assignees", "labels"]`;
`factory_land.py:63`: `["title", "state"]`) — only call **counts** are asserted
(`test-factory-claim.py:303,513-514`). The comment at `test-factory-land.py:330-333` describes the
widened field list in prose but nothing checks it.

**Proven live** (isolated copy in scratchpad, never the worktree — restored to source of truth
after; `git status --porcelain` on the worktree is clean throughout, nothing here touched the
tracked tree): dropped `"state"` from both field lists —
`["number","title","state","assignees","labels"]` → `["number","title","assignees","labels"]` in
`factory_claim.py:274`, and `["title","state"]` → `["title"]` in `factory_land.py:63` — and reran
both suites unmodified. **Both stayed fully green: `test-factory-claim.py` 95/95,
`test-factory-land.py` 56/56, identical to baseline.** In production this field-list change would
mean `gh` never returns `state` (it wasn't requested), `.get("state")` → `None`,
`None != "OPEN"` → always true, and every claim/land call refuses — the exact fail-open-inverted
(fail-closed-on-everything) defect the dispatch asked about. The fakes cannot detect it because
they hand back `state` unconditionally, independent of what was requested.

This is real, demonstrated, and applies to **both** `claim` and `land`, not narrowly to
`claim --issue` as I first scoped it before mutation-testing (my initial framing —that only
`--issue` lacked a happy-path exit-0/mutating assertion — undersold the actual mechanism; the
`--issue` framing was reasoned from reading, this is proven by a reddened mutant per P-09/
`coverage-findings-need-assertions`).

## `_ISSUE_ITEM_QUERY` literal-text pinning — routed question

Confirmed: `factory_gh.py:295-305`, the query string, carries no `state` field and no `is:open`
argument (comment at `:293` and docstring at `:321` both assert this in prose). `test-factory-
gh.py` asserts structure and behavior around `issue_board_item_id` extensively (`:645-839`) —
call count, argv shape (repo halves, issue number), and the full RAISES/None-return decision
matrix — but **no assertion reads the literal `query=` text** the way `:344-350` does for a
DIFFERENT function (`_project_field_set`, checking "no plural field-connection selection", "no
connection argument"). Grep for `state`/`is:open`/`query` in `test-factory-gh.py` around
`issue_board_item_id`'s block returns nothing pinning the query body itself.

**Severity: low-to-moderate, backlog not gate — not mutant-proven, reasoned only** (ran out of a
clean discriminating mutation for this one in the time available: `_ISSUE_ITEM_QUERY`'s text isn't
parsed as GraphQL by the fake, so a text-only mutation doesn't obviously reach an assertion either
way without deeper fixture work). A future edit reintroducing a state filter into
`_ISSUE_ITEM_QUERY` would silently narrow the lookup back toward the whole-board-scan defect
D-01 exists to remove — SC-06/SC-07's closed-issue tests would likely still pass (they exercise
the CALLER's post-fetch state check, not what the GraphQL query itself returned for a closed
issue's item), so this is a plausible latent regression path, same class as the proven fields-list
gap above but not independently demonstrated. (1) it requires a future edit to trigger, not a
defect in the current diff; (2) fixing it means amending an approved plan's assertion list, which
per the dispatch is pm's call under the operator's signature, not something this gate can add
unilaterally. Recommend: **do not gate this ship on it** — file as a backlog coverage item
alongside the proven fields-list gap, name both explicitly so neither is assumed covered.

## Already-adjudicated items — seen, not relitigated

`argv[:2]` prose-vs-code (pm's), `claim --issue` exit-2 delta (ratified, Q1), `land`'s closed-
issue bug (#238, out of scope), #218/#241/#242 (known).

## Bounds observed

Read-only on source throughout — no edits, no `gh` calls, no commits. No mutants run (none
requested; the routed questions were answerable by direct grep/read of existing fixtures).
