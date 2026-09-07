# Goal-check of the drafted plan against stated intent — BUG-1290, cycle c1

**Does this plan deliver the operator's stated intent?**

Yes with 3 gaps — every settled item and every `Done when` bullet has a plan element that carries it,
but the single-resolver shape deviates (named in `D-01`, legibly), and the ticket's "mutation-proven at
the unit boundary" rests on `SC-08`, whose declared method (`verify: test — test-factory-claim.py`)
cannot reach it.

Graded against `.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md` and `#1290` only;
`BRIEF.md` is derived from both and was used solely to locate carriers. 13 items graded, 3 not
`delivered`. No `BRIEF.md`/`plan.yaml` byte changed (see Evidence).

## Table 1 — grilling `## Settled` (7 items)

| # | Settled item (short) | Grade | Carried by |
|---|---|---|---|
| S1 | BUG flow: one eng squad, no product/design/UAT, `verify: test` only | delivered | `BRIEF.md:99-100` (DEC-139); `plan.yaml` lanes `:8-19` all `harness-backend-dev`; every SC uses `verify: test` |
| S2 | Contract = existing `.harness/<segment>/features/<FEAT>`, segment = fleet name minus owner, literal `harness` for this repo | delivered | `REQ-01`, `REQ-04`; `D-01` choice; `T-03` step 1 (`features_root` join) |
| S3 | ONE resolver called by both `factory_claim.py` and `feature-worktree.py:resolve_repo`; module placement eng's call | **deviates** | `D-01` (`plan.yaml:22-34`): TWO functions, shared one is `segment_of`, home pinned to `factory_config.py`. See §1 |
| S4 | `FEATURES_ROOT` deleted, no alias; tests migrate; the two module-scope cases at `:58-68` deleted, not re-pinned | delivered | `REQ-06`, `SC-05`; `T-01` step 2 (+ its no-weakening clause), step 3; `T-03` step 3 + verify's substring check `plan.yaml:212`. Weakening residue: §3 / F-04 |
| S5 | `_BlockerCache` keys on `(repo, feature)` | delivered | `D-02`; `REQ-02`, `SC-02`; `T-03` step 4 (both `_plans` and `_issue_maps`); `T-01` step 5b |
| S6 | No new refusal path; absent per-repo root → existing `no_plan` naming the resolved path | delivered | `REQ-03`, `SC-03`; `T-03` steps 3-4 (`root_exists` becomes the candidate's own root); `T-01` step 5c; `BRIEF.md:106-107` |
| S7 | "Harness claims still work" is fixture-only regression, not live behaviour | delivered | `REQ-04`, `SC-04` (both state fixture-only, DEC-174); `T-01` step 5d |

## Table 2 — `#1290` `Done when` (6 bullets)

| # | Bullet (short) | Grade | Carried by |
|---|---|---|---|
| D1 | Claim on a served fleet repo reads that plan and evaluates the blocker gate (unit + integration) | delivered | `SC-01`/`T-01` step 5a; `SC-07`/`T-02` (moves the composed case's fixture onto `widget`) |
| D2 | Two repos, same feature id → own plans, neither reads the other's | delivered | `SC-02`; `T-01` steps 4 and 5b (two segment roots, same id, different DAGs; cache non-bleed asserted) |
| D3 | Segment `harness` still resolves to `.harness/harness/features` | delivered | `SC-04`; `T-01` step 5d; scoped to `owner/harness` by SF-02, not the CLI literal |
| D4 | Absent root → existing `no_plan` naming the resolved absolute path | delivered | `SC-03`; `T-01` step 5c (asserts the message contains the segment-carrying absolute path) |
| D5 | `feature-worktree.py` and `factory_claim.py` **share the resolver**; no second `split("/",1)[-1]` | **deviates** | The second half is carried (`SC-06`, `T-01` step 5f, `T-03` step 2). The first half is not as worded: they share `segment_of`, not the `repo name → features root` resolver the ticket's Scope specifies; `features_root` has exactly one caller (`D-01`, `plan.yaml:28-29`). §1 |
| D6 | Regression mutation-proven at the unit boundary, covered once at integration | **partially delivered** | Integration: `SC-07`/`T-02`. Mutation: `SC-08` only, and no task step produces the evidence after `T-03` lands; `T-01`'s pre-change red is suite-granular. F-02 |

## §1 — The D-01 deviation

**Verdict: intent delivered, words not; and the deviation is legible inside `D-01`'s own text.**

(a) The operator's intent — one home for the segment rule, reached by both callers — is delivered.
`segment_of` is that one home and has three callers (`plan.yaml:25-27`), and `REQ-05`/`SC-06` bind the
property by scanning all three files. The `because` is measured, not asserted: `resolve_repo`
(`feature-worktree.py:64-87`) composes the segment with `workspace_path`'s workspace root
(`factory_config.py:382-387`, read and confirmed), not with the harness root, so a single
features-root function would force it to recover the segment from a path built for another consumer.
Pinning the home is justified by the same file: `workspace_path:386` carries a live second derivation
and its docstring (`:384-385`) already claims to be "the one place that derivation exists".

(b) Legible. `plan.yaml:30-34` states, in `D-01`'s choice text, that the settled wording was one
resolver called by both, that the shared function is now `segment_of` and not a features-root
function, that `features_root` is a thin single-caller wrapper, and that the home is no longer
engineering's free choice. A signer who has read only the grilling note and `D-01` learns all four
facts without the eng digest. **One advisory gap (F-01):** `D-01` names the deviation against the
*grilling wording* only; `#1290`'s Scope bullet ("Add **one** `repo name → features root` resolver …
and have both call it") deviates identically and is not mentioned, so a signer grading against the
ticket must map the two themselves.

## §2 — Scope creep in the other direction

**Verdict: two ADOPTED surfaces beyond the forced set; no parked item has crept back.**

| Surface | Forced / adopted | Reason |
|---|---|---|
| `factory_config.py` — add `segment_of` + `features_root` (`T-03` step 1) | FORCED | The rule needs a home outside `factory_claim.py`; `D-01`'s measurement rules out the alternatives |
| `factory_config.workspace_path` rewritten onto `segment_of` (`T-03` step 1) | **ADOPTED** | The bug lands correctly without it. It is forced only by `SC-06`'s own "exactly one derivation in `factory_config.py`" clause — a criterion this plan authored. Circular forcing; defensible (it retires a real duplicate) but it is added surface, F-07 |
| `tests/integration/test-factory-integration.py` (`T-02`) | FORCED | `:879-883` relies on the import-time default; `#1290` names it under Tests |
| `layout_migration.py` + `layout_fixtures.py` (`T-04` steps 1-2) | FORCED | Confirmed at source: the row at `layout_migration.py:92-94` keys on `factory_claim.py`'s literal `".harness", "features"` join, which `T-03` deletes; DEC-194 makes a reader matching neither form cannot-verify, and INV-27 reports that as failure. *The MOVE rather than the removal is adopted-within-forced* (`D-04`) |
| `tests/integration/test-layout-migration.py` case 22 comment (`T-04` step 3) | **ADOPTED** | Comment only; `:422-425` becomes false but nothing executes it. Already raised as Q2. F-08 |

Parked items: `post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`,
`feature_schema.py:231` appear in the plan **only** at `plan.yaml:244-245` as an explicit do-not-touch,
and in no task's `files:`. **None has crept back.**

## §3 — Coverage of the operator's constraints

**Verdict: three of four fully covered; the fourth (deletion-not-weakened) is covered in prose but not
by its declared method.**

- `FEATURES_ROOT` deleted, no alias, no fallback — **covered twice**: `SC-05`'s `hasattr` case and
  `T-03` verify's text check (`plan.yaml:212`). A re-pin of the old default also crashes the suite at
  module scope, so it cannot ship green.
- `_BlockerCache` keyed on `(repo, feature)` — **covered behaviourally**, `T-01` step 5b asserts the
  second candidate receives neither the first's cached plan task nor its issue map.
- Unit **and** integration, mutation-proven at unit — **partial**; see F-02.
- The two cases at `test-factory-claim.py:58-68` deleted, **not re-pinned or weakened** — the deletion
  is instructed (`T-01` step 2) and a re-pin is caught, but a *weakened* conversion (e.g. asserting
  `not hasattr` in their place) leaves the suite green and no criterion reads the file. **F-04**, owner
  `SC-05`.

## §4 — Verify-passes-intent-undelivered

**Verdict: T-01 and T-04 can each green hollow; T-03 has one narrow route; T-02 is sound but
non-attributing.**

- **T-01** — `python3 …; test $? -ne 0`. Aggregate. Any single red case, or an `ImportError` from a
  typo, satisfies it, so cases 5d/5e/5f could be written non-discriminating and nothing notices. Note
  5f is red today only because of `feature-worktree.py`: its `factory_claim.py` and its "exactly one in
  `factory_config.py`" clauses both already pass at `eb9d044e` (verified: `workspace_path:386` is the
  one). **F-03**, owner `T-01` verify.
- **T-02** — the `^FAIL  (F) claim exits 0` marker is real (`test-factory-integration.py:81,925`) and
  discriminating, but it asserts *red*, not *why*: a mistyped fixture path produces the same line.
  Low risk, because `T-03`'s verify requires the same case green afterwards. Advisory only.
- **T-03** — all three suites plus the `FEATURES_ROOT` text check. One route: step 2's single-home
  property is guarded textually by `SC-06`'s "split-on-slash form", so a re-derivation in
  `feature-worktree.py` spelled `rsplit`/`partition` passes the scan, and `test-feature-worktree.py`
  (green at `eb9d044e`, so non-discriminating for a *correct* duplicate) passes too. Done-when D5 then
  stays undelivered under a green verify. **F-06**, owner `SC-06` / `T-01` step 5f / `D-03`.
- **T-04** — `test-layout-migration.py` exit 0. Case 22 (`:426-429`) asserts only `features: CLEAN —
  evidence migrated`. It greens if the row is **removed** instead of moved (four rows still clean), and
  greens with a legacy pattern that matches nothing, since only the migrated pattern is exercised. The
  "features surface keeps five reader rows" clause of `REQ-08`/`SC-09`/`D-04` is asserted by nothing,
  and step 3's comment reword is unverified. **F-05**, owner `SC-09` / `T-04` verify.

## Findings (addressable, none fixed here)

| id | Owner element | Finding | Severity |
|---|---|---|---|
| F-02 | `SC-08`, `REQ-07` | Declared method cannot reach it: no test performs the revert-mutation, and no step produces the evidence after `T-03`. `T-01`'s red is suite-granular | gating |
| F-03 | `T-01` `verify:` | Aggregate non-zero; one red case or an import error satisfies six cases | gating |
| F-05 | `SC-09`, `T-04` `verify:` | Case 22 greens on row removal and on a dead legacy pattern; five-row clause unasserted | gating |
| F-06 | `SC-06`, `T-01` 5f, `D-03` | Scan pins one spelling; a `rsplit`/`partition` re-derivation ships green | non-gating |
| F-04 | `SC-05`, `T-01` step 2 | A *weakened* replacement of the deleted cases is forbidden in prose only | non-gating |
| F-01 | `D-01` choice text | Deviation named against the grilling wording only, not `#1290`'s Scope bullet | advisory |
| F-07 | `T-03` step 1, `SC-06` | `workspace_path` rewrite is adopted scope, forced only by a criterion this plan authored | advisory |
| F-08 | `T-04` step 3 | Case 22 comment reword is adopted scope, unverified (= Q2) | advisory |

## Evidence

- `git -C <worktree> status --porcelain` → exactly two untracked entries:
  `.harness/harness/features/BUG-1290-factory-claim-repo-root/` and
  `.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md`. The feature directory is untracked
  as a whole, so byte-stability is pinned by digest instead: `BRIEF.md`
  `6b855c5bce54677e6175f2f893ffb5b9d1507b11182c1d7ed97acbce53456548` (7819 B), `plan.yaml`
  `c8855ab77434f86e0c82e5ca4d4ff21c9bf74cc2c981bfbca8a84aa0d84532c2` (19942 B), taken before this note
  was written and unchanged by it (no write tool was pointed at either path).
- Anchors re-read at the worktree tip, not taken from the digests: `factory_config.py:382-387`,
  `layout_migration.py:76-111`, `test-layout-migration.py:421-429`,
  `test-factory-integration.py:74-81,924-943`, `test-factory-claim.py:1-68`. All as the plan recites.
- `approval.status` is `pending` (`plan.yaml:3-4`); no `panel:` key; neither was touched.
