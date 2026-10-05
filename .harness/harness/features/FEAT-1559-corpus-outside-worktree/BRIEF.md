# BRIEF — FEAT-1559 Corpus outside the worktree

## Problem

Every record-bearing checkout currently materialises the landed feature corpus, although its writers own only one active feature. Feature worktrees, fleet planning worktrees and validator pins multiply the reference files and their growth. Simply hiding them makes filesystem-based gates liable to grade an incomplete population as clean; the operator observed an audit of 1 of 88 features returning success (issue #1559).

## Done when — by perspective

**operator** — I can create or retain a record-bearing checkout without materialising other features, regardless of which creation route I use. My landed records remain readable and unaltered, existing clean checkouts converge without losing dirty work, and ordinary clones and CI keep their behavior.

**reader** — I can read landed precedent on disk and trust that an audit examines its declared subject rather than silently accepting a smaller population. Duplicate branch claims remain detectable even from a sparse checkout.

**code maintainer** — I can rely on one deterministic, idempotent state command and explicit failure reasons, enforced at checkout, merge, rebase and gate boundaries rather than instructions someone must remember.

## Success criteria

Every automated criterion requires its discriminating failing state to be demonstrated before the corresponding production change; existing positive controls are not claimed as fail-first evidence.

- SC-01 (operator): File-count mode: each harness feature worktree, fleet planning worktree and validator pin materialises exactly the active feature-directory name set across all .harness/*/features segments, with no other feature files. New tracked top-level directories and non-features .harness subtrees, including .agents/skills, remain present without an include-list edit. Existing active records select their exact artifact segment, never the worktree segment; pins use _pin_name's <feature>--<run-id>--<persona> form. When no segment holds a record directory for the id, checkout identity (worktree directory id, feat/<id> branch or pin name) supplies the active id and the cone includes .harness/*/features/<id> across ALL segments before first record creation. Multiple claiming segments or underivable identity refuse explicitly.
  verify: automated evidence: integration
- SC-02 (reader): From inside each harness feature worktree, fleet planning worktree and validator pin, ordinary absolute-path reads at the resolved owner root return landed other-feature BRIEF and note bytes equal to the main corpus, and that other feature's directory does not exist in the checkout. For the fleet planning worktree the other feature is in a different segment from its active record. An unavailable owner root or required landed path refuses by name; in-progress siblings are not searched. Both registered Write/Edit and Bash guard entrypoints refuse a governed write into the main corpus. BUG-1016 rooting preserves these absolute read paths and selectors; a relative-path control still roots to the active checkout. (Amended 2026-10-04 by the operator: checkout classes named, direct read assertion added to T-03.)
  verify: automated evidence: integration
- SC-03 (reader): The active-feature audit in check_state/ produces the same normalised selected-subject finding set in full and sparse synthetic checkouts. Instrumented checkout-local feature-file opens are confined to its own record, including BRIEF, plans, states and runs; separately declared repo-wide predicates read landed owner-root records rather than siblings. An explicit missing --feature selection refuses rather than yielding a clean empty audit.
  verify: automated evidence: integration
- SC-04 (reader): Audit discovery compares expected and reached directory NAME SETS, not feature.json counts; missing required entries refuse before downstream invariants with N of M counts, sorted missing/unexpected names and the remedy. Fresh non-linked clones retain the full audit; unexpected-only uncommitted directories are reported non-gating. Repo-wide record readers use the resolved main corpus and refuse unresolved roots or missing expected entries rather than auditing their local sparse subset. Source census detects unmarked wildcard feature enumerations, including one injected scratch site; every detected site has exactly one scope marker and owner-root sites name feature_corpus.
  verify: automated evidence: integration
- SC-05 (reader): Branch uniqueness computes claims on demand from landed main-corpus records across segments. A new duplicate yields one finding naming both features; literal none, missing and empty branches yield none. The exact historical FEAT-02 / FEAT-03-subissue-mirror pair is era-exempt with a nonempty reason; a third claimant or an empty reason makes it collide again. Merge and branch-create gates are graded by their permissionDecision payloads, with allow controls, not exit status; neither a sparse local subset nor an unresolved corpus root may silently allow a verdict requiring corpus discovery.
  verify: automated evidence: integration
- SC-06 (operator): Fresh non-linked synthetic clones keep the full corpus and pre-change audit findings; worktree-state.py --verify is a no-op there. Existing required suites remain green in a plain clone, with no change to CI workflow, checkout depth or runner selection. Collected baseline comparisons use the immutable planning baseline; SC-11's one-time receipt resolves and freezes its own pre endpoint at execution.
  verify: automated evidence: integration
- SC-07 (code maintainer): worktree-state.py --verify and --repair retain named exits: cone 3, cleared skip-bits 4, materialised feature set 7 and class-C dirty tree 8. Verify never changes filesystem/index/config bytes. Repair classifies every status entry before mutation: A is outside the target cone, absent on disk, index entry == HEAD (set skip-worktree, touch zero disk bytes); B is outside cone, present and byte-identical to index (remove); C is any content divergence, including real edits, staged index != HEAD including staged deletion, cone-internal deletion and untracked files in hidden feature directories. Any C anywhere refuses exit 8 without mutation, including mixed A/B/C. Hidden-feature unstaged deletion is A by design; provenance markers are rejected. A/B repair is idempotent. Plain clones and non-record-bearing probes are no-ops. Recordless identity follows SC-01; ambiguous segments or underivable identity refuse.
  verify: automated evidence: integration
- SC-08 (code maintainer): post-checkout, post-merge and post-rewrite repair the checkout affected by Git, whoever creates it. First creation before any record exists converges via BOTH feature-worktree.py create and bare git worktree add using checkout identity and all-segment <id> includes; ambiguity still refuses. Tests discriminate class-A hidden-feature merge repro, class-B identical materialised content, class-C real edit and staged deletion, and mixed A/B/C refusal with nothing mutated. A repairable merge and rebase leave status clean with skip-bits intact. Each executable shim resolves its delegate, attributes missing/failing delegates, exits 0 and preserves post-rewrite stdin; the terminal sweep remains intact.
  verify: automated evidence: integration
- SC-09 (code maintainer): Before any invariant runs in a record-bearing linked checkout, check_state/ calls verify, never repair. Structural failures 3, 4 and 7 refuse; dirty exit 8 is reported non-gating so pre-commit does not deadlock. Corpus-dependent gates likewise verify their checkout before deciding over records and emit their established refusal shape on structural failure. Fixture assertions include a downstream-not-run witness and a structural positive control alongside the dirty case.
  verify: automated evidence: integration
- SC-10 (operator): One explicit conversion pass inventories standing record-bearing worktrees and pins by path and HEAD, reports and skips any class-C input unchanged, and repairs clean or class-A/B inputs without removal, force or pruning. A durable per-checkout manifest records pre/post materialised feature-directory names and file counts, verify result and class-C skip reason; a second pass is unchanged. Measurements use file-count mode, never du-as-savings. (Amended 2026-10-05 by the operator: the conversion pass runs after FEAT-1559 merges, under #2101, so other sessions' worktrees are never sparse under pre-1559 tools; T-06 is abandoned here and SC-10 is met by #2101's receipt, not by this feature's review.)
  verify: automated evidence: integration
- SC-11 (operator): At one-time receipt execution, resolve merge-base(review_sha, main), record its full immutable SHA as pre_change_sha and the resolved main endpoint, and freeze both diff endpoints. The whole-feature diff to review_sha changes no path under any other feature directory in any segment; main-corpus manifests retain their bytes. 652e70d4 is the planning baseline only. Endpoint absence or shallow unresolvability is an announced skip, not a pass; authoritative observation is local in a full clone before ship.
  verify: inspection evidence: one-time immutable-endpoint receipt inspected at review_sha; no permanently collected frozen diff assertion
- SC-12 (reader): Read-only real-owner-root checks observe actual audited feature-directory names equal the on-disk corpus across all segments, no missing-set refusal and a >70 host non-vacuity floor, not a fixed census expectation. A staged missing-producing mutant and wrong-root synthetic override fail the same equality assertion. A disposable real worktree pinned at current owner HEAD resolved at collected-test execution proves dirty non-gating versus structural refusal; live worktrees and owner records are never mutated. Missing host prerequisites are announced skips, not met evidence. Frozen review endpoints are reserved for one-time receipts.
  verify: automated evidence: integration
- SC-13 (code maintainer): Unit assertions cover sparse directory-set derivation, exact active segment and pin-name classification, owner-root resolution, linked_worktrees parity from owner versus worktree, branch sentinels and exact-set exemptions, and census discrimination. Each relevant predicate has a negative case and fail-first evidence; no collected test derives a pre-change subject from a moving ref.
  verify: automated evidence: unit
- SC-14 (reader): At git show <review_sha>:AGENTS.md and the pinned harness and verification skill documents named in T-05, read instructions distinguish active feature writes from absolute landed-main-corpus reads, declare no in-progress sibling provider and no symlink/git content provider, and document repair, verify and dirty-skip behavior without claiming core.hooksPath travels with a clone.
  verify: inspection

## Verification gaps

- Unit and integration runners are active and detect the proposed tests under tests/unit and tests/integration. Component, ui and typecheck have null runners but this feature adds no browser, component or TypeScript production surface; none carries an SC. Functional and eval remain excluded under DEC-187.
- No interactive end-user surface changes; no DESIGN.md or prototype is necessary. No SC requires user-run UAT. Host conversion and read-only real-owner evidence require the main session under DEC-174; synthetic proof cannot substitute for those receipts.
- The owner corpus is a mutable on-disk checkout, not a version-addressed sibling provider. The grilling explicitly accepts landed records only. Historical annotation in carried decisions is not a claim of current execution.

## Constraints

- DEC-95 supplies one-feature-per-worktree concurrency; only the active feature's records are writable locally. DEC-214 supplies the injected HARNESS_CONTROL_PLANE_ROOT for agent reads and the dispatched HARNESS_FEATURE_TREE_ROOT for feature writes.
- DEC-174 blocks team execution of this enforcement-layer change and its tests: every task is main-session-direct, with all relative edits confined to this feature worktree. DEC-193 supplies existing cross-checkout write refusal and forbids git subprocesses on governed write paths; corpus content is never read through git.
- DEC-251 supplies lexical file-tool rooting: explicit absolute owner-root reads are unchanged. DEC-213 supplies directory-selected unit/integration tests; DEC-231 supplies perspectives and SC traces in place of obsolete REQ-NN plan fields.
- Grilling and operator rulings replace FEAT-58's symlink provider and six-exit specification: no .harness/corpus, retained exits 3/4/7/8, content classes A/B/C, every .harness/*/features excluded and exact existing active segment re-added; recordless checkout-identity ids are included across all segments.
- Hook scripts are tracked; core.hooksPath is local config, not cloned. Onboarding sets it and INV-31 refuses a clone where it is wrong. CI is not reordered to make a host-only proof pass.
- Operator ruling 3 supersedes Q-01: FEAT-57-review-latency was abandoned (#1655 closed, label abandoned). No replay receipt or T-19 serialization is an execution prerequisite.
- Archive D-05/06/11/13/14/15/16/17 are carried verbatim; their historical N-NN, FEAT-58 and shell references are interpreted by the current task/source mapping in the research artifact, never dispatched as stale paths. D-01/02/03/07/10/12 are re-anchored, D-04 dropped, D-08 and D-09 re-decided. No archived branch is merged.

Binding pre-signature rulings are recorded in notes/answers-operator-2026-10-04-signature-rulings.md: content classification replaces provenance and fresh recordless ids converge through checkout identity without creator edits. T-05 operator guidance and T-06 migration record must name the old-layout consequence for class-C skips and recovery: preserve work by commit/stash (including untracked files), run repair then verify for that checkout, rerun the refused audit/gate and recheck after restoring saved work; never force repair.

## Out of scope

- Clone-on-write copies: the operator's 2026-09-09 ruling is "never materialised".
- Hardlink aliasing: #1638 (FEAT-58 D-14).
- The gh-sync loader dropping non-T-NN task ids: #2060; this plan uses T-NN only.
- Reading records through git: rejected in favour of B, and forbidden in hooks by DEC-193. Git structural/index queries and immutable diff evidence are not corpus content providers.
- Removing stale worktrees: a separate manual cleanup. This feature converts worktrees; it does not prune them.
- Reading in-progress features from sibling worktrees: ruled out by the grilling.

## Approval

status: approved
approved-by: mruangutai
date: 2026-10-04
