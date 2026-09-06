# Plan fix cycle 2 — BUG-1305 — prevention moved to marker acquisition

**All seven findings applied, none declined. Prevention no longer reads a session identity anywhere:
T-09 now refuses the write that ACQUIRES a run directory another run holds (marker present, no prior
`state.yaml`), which is decidable from disk alone. T-04 is retired in place — nothing branches on its
answer any more. A new T-10 seeds the 630 marker-less run directories and then makes marker-absent a
reported violation. `check-plan-routes.py` exits 0; `approval.status` stays `pending`.**

## The two properties, and where each is proven

- **(a) A resumed owning run is never refused.** It writes over its own prior `state.yaml`, so it
  CONTINUES and never reaches the acquisition branch. Proven in: T-09 fail-open row `b`; T-09's
  "THE RESUMED OWNER" integration case (exit 0 with a *different* session id); SC-01 clause (c),
  which FAILS if that case is absent or asserts non-zero.
- **(b) A new run cannot acquire a directory another run holds.** Proven in: T-09's refusal condition
  (`marker is not None` and `prior_state == ""` and not `prior_unreadable`); T-09's LEADING
  integration case (equal seed fields, exit 2); T-09's `## SC-01-acquisition` red proof against the
  recorded `baseline_sha`; SC-01 clause (b).

## Disposition by finding

| ID | Applied |
|---|---|
| F-01 | T-09 re-specified in place (title, intent, verify, files, `depends_on: [T-02]`) — no new id, no stale twin. D-01 `choice`+`because` rewritten: identity is recorded evidence and a denial input nowhere; prevention rests on creation-vs-continuation. T-04 retired (station `abandoned`). REQ-01 and SC-01 rewritten for the new rule and the new residual. |
| F-02 | REQ-07 is two-directional. SC-07 direction two names the four permitted-write pairs a grader COMPARES and five FAIL conditions. T-08 intent+verify now produce and grep `## Newly refused writes`. |
| F-03 | Dissolved by F-01 — no contingent language survives in REQ-01 or SC-01; the residual is stated as fact, not as a branch. T-04's retirement body records the `inconclusive` evidence. |
| F-04 | New T-10: `run_identity.py --seed <root>` backfill, then marker-absent becomes a reported outcome of T-03's invariant. Graded by new **SC-09** (traces REQ-02, widened). Order is inside one task so no intermediate state fires on history. |
| F-05 | `_run_artifact_guard (:744-767 at c369fb1f)` in REQ-01 and SC-01. Re-derived: HEAD is `c369fb1f` and the def is at `bash-write-guard.sh:744`. |
| F-06 | SC-08 narrowed to "the two documents T-07 changes", and says explicitly that DEC-145's own sentence standing is the design. |
| F-07 | `T-06.depends_on: [T-02, T-09]`. |

## What I checked at source rather than adopted

- `prior_state` is `""` **only** in the `FileNotFoundError` branch where `os.path.lexists` is also
  false (`check-domain.sh:1514-1516`), and the file's bytes otherwise (`:1513`); `if prior_state:`
  gates the seed compare at `:1530`. The orchestrator's reading survives — prior-absent is CREATION.
- **The acquisition refusal is Write-only, by construction.** An Edit reconstructs against the
  on-disk prior, so it cannot occur while `prior_state` is empty. REQ-01, SC-01 and T-09 all say so;
  no unconstructible Edit case was written.
- **Corpus, re-measured 2026-09-05 at `c369fb1f`: 630, not 575** (356 under `.harness/…`, 274 under
  `.claude/worktrees/…`), zero markers. It grew during planning, which is why T-10 is an idempotent
  script and not a list. Run dirs are gitignored (`.gitignore:7`) and untracked, so the corpus is
  machine-local: a fresh clone has no legacy exposure.

## The residual, unhidden

Marker present **and** prior present **and** seed fields equal is identical on disk to a resumed
owner. It cannot be closed without the signal D-01 forbids, and **T-03's detection does not catch it
either**, because the sweep keys on the same `conflict()`. Stated in REQ-01 as fact, pinned by an
SC-01 test case, narrower than before (the foreign run must now land on an already-matching
checkpoint rather than on any reused slug).

## Writes

`plan-merge.py amend` (compare-and-swap, all exit 0, no CAS failure): D-01 `choice`, `because`;
T-01 `intent`; T-02 `intent`; T-03 `intent`; T-04 `title`,`intent`,`verify`,`depends_on`;
T-06 `depends_on`; T-08 `depends_on`,`verify`,`intent`; T-09 `title`,`verify`,`intent`,
`depends_on`,`files`. `plan-merge.py set-task-station` → T-04 `abandoned`.
`plan-merge.py apply` → T-10. BRIEF.md edited directly; `## Approval` untouched.

Graph (acyclic): `T-01 → T-02 → T-09 → T-06 → T-08`, `T-01 → T-03 → T-10 → T-08`, `T-05 → T-08`;
T-07 standalone; T-04 abandoned with no edges in or out.

## Gates

- `python3 .claude/skills/harness/bin/check-plan-routes.py <plan> ` → **exit 0**, 0 violations
  (10 DEVIATION lines, the expected DEC-174 shape).
- `python3 .claude/skills/harness/bin/check-instruction-paths.py <plan>` → **exit 2**,
  `selects nothing in scope` — that checker's scope is `.claude/agents/*.md` and
  `.claude/skills/*/SKILL.md` (`--list-scope`); a plan.yaml is out of its scope by design, and this
  plan touches no file in it.
- `yaml.safe_load` loads; `status: plan`; `approval: {status: pending}`; no `panel:` key; all 10
  tasks carry `traces`/`change_type`/`execution_mode`/`files`/`verify`/`intent`; zero folded `>`
  verify blocks.

## Open question for the operator

Retiring T-04 leaves `run_identity.identity_disagreement()` written by T-01 and called by nothing.
It is kept deliberately as the seam a later feature would use if a run-stable identity ever exists.
Striking it is a one-line change to T-01 if you would rather not ship dead code.

**RESOLVED — struck. See `## Send-back: the identity predicate` below; the paragraph above records
the question as it was asked, not the standing plan.**

## Send-back: the identity predicate

**Q1 above is answered NO by the product lead: the uncalled predicate is struck, the recorded field
stays.** `grep -n identity_disagreement plan.yaml BRIEF.md` now exits 1 with no output. The seam
argument does not survive harness-principles rule 12 — structure is earned by a real bottleneck,
never designed in anticipation of one — and a predicate the enforcement layer carries and no gate
calls is dead code an adversarial reviewer gates on. Nothing else in the accepted disposition set
moves: the acquisition rule, D-01, T-09, T-10, SC-09, the REQ/SC set and every ordering edge stand.

### The three amends, all `plan-merge.py amend`, all compare-and-swap, all exit 0

| Field | Was | Now |
|---|---|---|
| `T-01.intent` | `identity_disagreement(marker, identity) -> bool` in the public surface (:144-146); "written here and called by nothing" (:153); a unit case for it (:174-175) | public surface is five names, with an explicit prohibition on any identity-comparison predicate or helper; `record_seed`'s six-key contract and the write-once property untouched — `identity` is still one of the six; the D-01 comment now sits on `conflict()` and says the recorded identity is forensic evidence a human reads out of the marker, that `conflict()` must never consult it, and that no gate in this feature consumes it; the removed case is replaced by one pinning that `conflict()` returns None when the marker recorded an identity no incoming checkpoint carries |
| `T-03.intent` | "Do NOT call `identity_disagreement()` here" (:302-305) — named a function that will not exist | forbids what it must: no reading or comparing of the marker's recorded identity in the sweep, because the sweep has no hook payload and therefore no live identity; the recorded identity is forensic evidence and a gate input nowhere (D-01); `conflict()` is the only marker predicate that exists. Detection invariant, message rule and all five cases unchanged |
| `T-04.intent` | retirement body said the predicate "is still written by T-01 and is still called by nothing" (:362-363) | true as of now: no identity-comparison predicate is planned at all, and what survives of the identity signal is the marker's recorded FIELD, written by `record_seed`, read by a human recovering a clobbered directory. Everything else in the retirement record unchanged |

T-01 took two amends: the first draft of the prohibition spelled the struck name literally, which
would have kept the grep non-empty. Re-amended under a fresh sha; both exits 0, no CAS failure.

### One judgement beyond the strike, recorded

Removing the predicate's unit case would have left the test list with nothing pinning that identity
is not a denial input. I added one case in its place — `conflict()` returns None when marker and doc
agree on all four seed fields but the marker recorded an identity the doc does not carry. It fails if
anyone later wires the recorded field into `conflict()`, which is exactly the drift the comment warns
against. No other case moved.

### Gates, re-run after the amends

- `grep -n identity_disagreement plan.yaml BRIEF.md` → **exit 1**, no output. BRIEF.md was never a
  factor: `grep -c` over it returned `0` before any amend, so nothing there needed to change.
- Six-key contract intact, quoted from `T-01.intent`:
  `Otherwise write a JSON object with exactly the keys run_id, feature, squad, host, identity,` /
  `created_at: ...`
- `python3 .claude/skills/harness/bin/check-plan-routes.py plan.yaml` → **exit 0**, 0 violations.
- `yaml.safe_load` loads; `status: plan`; `approval: {status: pending}`; no `panel:` key; 10 tasks,
  each carrying `traces`/`change_type`/`execution_mode`/`files`/`verify`/`intent`; 10 literal `|`
  verify blocks, 0 folded. Stations unchanged, T-04 still `abandoned`.
- `git status --porcelain` → `?? .harness/harness/features/BUG-1305-run-state-clobber/` only; no
  tracked file outside this feature's directory is modified.
