### Receipt — harness-backend-dev — SIMPLIFICATION angle, plan surface — BUG-1290

BLUF: two real findings, both low/med, neither gate-signature-blocking. The three
"same fact restated across REQ/SC/D/T" shapes named in the dispatch are all
necessary carries (each downstream task dispatch reads only its own task text,
so the resolver contract and the single-home property must be self-contained
in each of D-01/T-01/T-03), not drift risk — I did not flag them. Every cited
line anchor was opened; all but two point exactly at what the plan says.
`BRIEF.md`, `plan.yaml`, everything under `.agents/skills/harness/bin/` and
every file under `tests/` are byte-unchanged — I only read them.

#### Findings

- id: S-01
  file: .agents/skills/harness/bin/factory_claim.py
  line: "94-146 (cited by T-03 step 4) vs. 94-157 (actual class extent)"
  summary: >-
    `_BlockerCache (:94-146)`'s cited range excludes the tail of `issue_number`
    (lines 147-157), where `self._issue_maps[feature]` is checked, assigned,
    and returned keyed on `feature` alone — exactly the key step 4 requires
    moving to `(repo, feature)`.
  cost: >-
    A builder scoping their diff to the cited 94-146 range can leave
    `issue_number`'s dict keyed on `feature` alone while everything else
    moves to `(repo, feature)`; that reopens the exact cross-repo
    feature-id collision D-02 exists to close, silently serving one
    repository's cached issue map to another's candidate.
  alternative: Recite the anchor as `:94-157`, or add `:147-157` explicitly alongside `:94-146`.
  severity: med
  targets: T-03
  gates_signature: false

- id: S-02
  file: tests/unit/test-factory-claim.py
  line: "7-16 (cited by T-01 step 2) vs. 14-16 (actual scope of the described sentences)"
  summary: >-
    Only lines 14-16 ("The deliberate exception: two cases at module
    scope...") describe the two module-scope FEATURES_ROOT-pinning cases
    slated for deletion. Lines 7-12 describe the file's general fixture rig
    (`build_features_root()`, FEAT-01-demo, FEAT-02-block) used by every
    other case in the file and remain true in substance after the change.
  cost: >-
    Literal execution of "DELETE... the docstring sentences... at :7-16"
    removes legitimate, still-true documentation about the fixture setup,
    not just the two-case exception being retired — a real content loss
    dressed as a targeted cleanup, though doc-only (no suite/behavior
    impact either way).
  alternative: >-
    Cite the deletion at `:14-16` only; separately instruct rewording
    `:7-8`'s "`FEATURES_ROOT` is monkeypatched to..." to name the new
    resolver-patch mechanism instead of deleting it.
  severity: low
  targets: T-01
  gates_signature: false

#### Anchors checked (every one named in the dispatch)

| anchor | verdict |
|---|---|
| factory_claim.py:26-29 | ok |
| factory_claim.py:46-50 | ok |
| factory_claim.py:94-146 | wrong — class is 94-157, see S-01 |
| factory_claim.py:341 | ok |
| factory_claim.py:343 | ok |
| feature-worktree.py:64-87 | ok |
| feature-worktree.py:86 | ok |
| feature-worktree.py:67-69 | ok |
| tests/unit/test-factory-claim.py:7-16 | wrong — see S-02, actual scope 14-16 |
| tests/unit/test-factory-claim.py:54-57 | ok |
| tests/unit/test-factory-claim.py:58-68 | ok |
| tests/unit/test-factory-claim.py:393-394 | ok |
| tests/unit/test-factory-claim.py:420 | ok |
| tests/unit/test-factory-claim.py:850-867 | ok |
| tests/integration/test-factory-integration.py:28-30 | ok |
| tests/integration/test-factory-integration.py:487 | ok |
| tests/integration/test-factory-integration.py:881-883 | ok |
| layout_migration.py:92-94 | ok |
| layout_migration.py:98-104 | ok |
| layout_fixtures.py:68-71 | ok |
| check-state.sh:2363-2367 | ok |

#### Triplications judged and NOT flagged

- D-01's resolver contract (signature: repo name in, absolute path out) restated
  in D-01, T-01 step 1, T-03 step 1 — necessary carry: T-01 and T-03 are
  separate dispatches, each reads only its own task text, and each needs the
  exact contract to write/implement against independently.
- REQ-06/SC-05/T-03 step 3/T-03's verify all pinning `FEATURES_ROOT`'s death —
  standard BRIEF→SC→task traceability (the `traces:` field), not accidental
  duplication; the verify grep is a belt-and-suspenders proof independent of
  whether the prose instruction is followed.
- REQ-05/SC-06/D-03/T-01 step 5f pinning the single-home property — same
  traceability shape, same reasoning.

No files touched.
