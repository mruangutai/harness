Nine rulings on the corrected corpus mechanism. pm applies these to plan.yaml/BRIEF.md; source not touched here.

## PRECEDENCE (cycle 2, read this before applying items 2/4/6/7/8)
Item 7 (relocation, adopted, scoped to T-03 + T-04's four validators) is the base ruling. It forces
three consequential edits, applied in-place below and each tagged **AMENDED — forced by item 7**:
  1. Item 2's H-1 union is redefined against the caller's own cwd, not against `root` — item 7 pins
     `root` at the owner copy, which never materialises an in-flight feature.
  2. Item 4 is reversed: `corpus_open` is RULED OUT (zero callers under relocation), returning
     T-01's API to the three functions its own intent already specs (`corpus_root`, `corpus_features`,
     `corpus_read` — plan.yaml T-01:97-131). Item 7's own last sentence ("`corpus_open` remains
     needed only for T-05") is superseded by this and struck.
  3. Item 8's caller attribution is corrected to match (2); item 8's DECISION (no batching) is
     unchanged — it never depended on which function T-05 calls.
Item 6's closure instrument is separately replaced (R3, unrelated to items 4/7); item 6's source
verification and remedy (a) are untouched. Wherever this note and plan.yaml's current T-01/T-04
intent text disagree, this note's corrected text governs — pm encodes the correction, not the older
wording still on disk.

**Cycle-3 amendment to items 2/4:** items 2 and 4 disagreed about where a union-only (in-flight)
feature's files are read from once relocation pins T-03/T-04's content reads at `root` — item 2's
cwd union member is never materialised at `root`, so item 4's blanket
`open(os.path.join(root, relpath))` would raise `FileNotFoundError` for it. Item 2 now states the
base-resolution rule (a `bases` mapping, computed once, feature→base-dir); item 4's T-03/T-04
per-reader text is corrected to read through it. No other item's substance changes.

## 1. C-1/MF-1 — predicate subject
**DECISION:** `corpus_features(root, ...)` compares the number of feature directories materialised **under `root` itself** (the value already passed in — for a worktree caller this is `corpus_root(cwd)`'s owner root, per T-01 intent) against `len(resolved)`. It never re-derives a second, independent `os.getcwd()`. `BRIEF.md REQ-04:49`, `SC-04:95`, `plan.yaml` T-01 intent (`harness_boundary.py`, corpus_features clause) all need this same correction; it's a requirement defect (identical wording in three places), not a T-01-only fix.
**REJECTED:** comparing against the caller's own checkout (`os.getcwd()`, as drafted). **FAILURE:** inside any converged worktree this is `1 vs 88` on every legitimate call — `corpus_features` never returns, contradicting T-08(c)/SC-03/REQ-02 which require the opposite outcome from the identical call.
**Reachable failure states under the corrected predicate**, enumerated:
  - (A) `root` unresolvable (no owner root, `resolve_root` fallback also fails) → refusal, but no `N of M` — a different message ("root unresolvable").
  - (B) history-side ref unresolvable / `git ls-tree` fails while building the resolved set → refusal naming the ref (T-01 case (e)), still no `N of M`.
  - (C) `root` resolves to a real directory whose *own* materialised set is short of resolved → **this is the only `N of M` trigger**. In production this fires only if the owner root's own invariant — "the one root that must always be whole" (D-01/T-08/T-09 never sparsify it) — is violated: a migration script mistargeting the owner root, a manual `git sparse-checkout` run there, or partial corruption. Rare, but it is the last-line defense of that invariant, not dead code. In tests it's the ordinary case — a fixture repo standing in as its own corpus root with M committed, 1 materialised, which is a direct test of the predicate itself, not a synthesised unreachable state.
  - Blobless/partial clone of the owner root does **not** trigger (C): directory/tree listing is unaffected by a blob filter, only content reads (`corpus_read`) would fail later. Call this out explicitly so nobody expects (C) to catch it.
**Intrinsic?** Yes, unchanged — no opt-out, same unconditional compare inside `corpus_features`, T-01 case (g) unaffected.
**SC-04 for the seven sweeps**: keep the existing fixture shape (own root, partial materialisation) — it already tests the corrected predicate correctly; no change needed to the fixture, only to what it's compared against.

## 2. H-1 — in-flight feature **[AMENDED — forced by item 7]**
**DECISION:** `corpus_features()` itself stays **ref-only**, unchanged — this is what keeps T-08(c)'s "SAME set as the owner root's default branch" true by construction. The union happens one level up, at the **caller**, and — under item 7's relocation — is taken against the caller's **own cwd** (the value `corpus_root(os.getcwd())` was itself computed from, e.g. `HARNESS-FEATURE-TREE-ROOT` for T-03/T-04), not against `root`: each sweep's scope is `corpus_features(root) UNION (feature dirs physically materialised under os.getcwd()'s own checkout, minus anything already in that set)` — i.e. check-state.sh adds the active in-flight feature to its own grading scope by globbing the SAME cwd it always had, before it ever computes `root`. Completeness (item 1's predicate) is compared over the **ref-resolved set alone**, unaffected by this union; nothing in item 7 moves that comparison off `root`.
**Why relocation doesn't reopen this:** `root` (the owner copy) never materialises an in-flight feature — it exists only in its own feature worktree, on its own branch, never on the default-branch ref `root` is pinned whole against. The original item-2 wording said "in this checkout," meaning the caller's own cwd; relocating the CONTENT reads to `root` does not take `cwd` away from the script — it is still the argument the script received and already passed to `corpus_root()`. Stating the union's subject explicitly as cwd (never `root`) is the correction this cycle makes.
**REJECTED (original):** doing the union inside `corpus_features()` itself. **FAILURE:** a worktree's `corpus_features()` would then return one more name than the owner root's own call on default branch (the active feature never exists there) — breaking T-08(c)'s literal set-equality assertion, and inflating `M` in every `N of M` message with an entry the owner root can never satisfy.
**REJECTED (cycle 2, considered and dropped):** enumerating linked worktrees from the owner root (`git worktree list` against `root`) instead of reading cwd directly. **FAILURE:** this pulls in every OTHER in-flight feature across every worktree on the machine, not just the one the caller is actually grading — INV-6/INV-33 grade the ACTIVE feature, singular; a global enumeration over-grades and needs its own scoping rule to claw back down to one, which is exactly what reading cwd already gives for free.
**Locally-materialised-at-no-ref directory:** graded by the caller-side (cwd) union (INV-6/33 keep seeing it); invisible to `corpus_features()`'s own list and to its completeness math.

**AMENDED — cycle 3: base-resolution rule (forced; closes the item-2/item-4 gap).** In T-03/T-04,
once relocation (item 7) is applied, every content read resolves against a **per-feature base**,
never uniformly against `root`. This is computed **once**, immediately beside the
`corpus_features(root)` completeness gate at the top of the script, as an ordered
`bases: dict[str, Path]` built from data item 1/2 already have: every name in the ref-resolved set
maps to `root`; the single in-flight feature name added by this item's cwd union (if any) maps to
the caller's own `os.getcwd()`. Every subsequent read is `open(os.path.join(bases[feat], relpath))`,
keyed by which **feature** the read is for. This is a per-FEATURE base lookup, decided once for the
whole run from set membership already known, **not** a per-PATH existence branch — it does not
reintroduce H-3/item 4's deleted branch because no read site tests a path's existence to pick its
base; there is exactly one fixed arm per feature, chosen before any read runs, never re-decided
per path. Item 1's completeness count is unaffected — still the ref-resolved set alone, computed
before this union or mapping exists. `corpus_open` stays ruled out: this mapping is a one-time,
whole-run lookup built from set membership, not the per-site materialised-or-history test item 4
deleted — the thing item 4 kept (one gate) versus the thing it deleted (per-read branching) are
unchanged by adding this mapping.
**REJECTED (cycle 3):** on `FileNotFoundError` under `root`, fall back to `corpus_read(path, ref)`
at the resolved ref (the obvious symmetric move, mirroring T-05). **FAILURE:** the only ref this
fallback could name is the same default-branch ref item 1/2's ref-resolved set is built from, and
item 2 already establishes that ref never materialises the in-flight feature — it exists only on
its own feature branch. So the fallback would deterministically miss for exactly the feature this
union exists to grade, and it fails **silently**: `corpus_read` returns "not found at ref,"
indistinguishable from a genuine invariant absence, masking that the file exists under cwd. It also
reintroduces the per-site materialised-or-history branch item 4 deleted, at every one of T-03/T-04's
~25 read sites — the H-3 regression this correction exists to prevent.

## 3. H-2 — provider signature
**DECISION:** `corpus_features(root, *, provider="history", ref=None)`. `provider="history"`: `ref` given or defaulted to the repo's default branch (as originally drafted) — no raise. `provider="path"`: enumerates on-disk directories under `root`; raises `ValueError` if `ref` is also given (path enumeration is ref-independent — a supplied ref there is a contradiction, not a silent ignore). Unknown provider → `ValueError`. Refusal (item 1) fires identically under either provider — `provider` selects *which read kind*, never whether the completeness check runs, so it is not the opt-out D-02/case(g) forbids.
**REJECTED:** no explicit `provider` kwarg, inferring path-vs-history from whether `ref` is `None`. **FAILURE:** conflates "no ref because path mode needs none" with "no ref because I want the default-branch history" — ambiguous, and D-04/D-05/T-12 already spell `provider` as a distinct declared token (`HARNESS-CORPUS-PROVIDER`), so a signature without it can't be traced back to the dispatch-guard declaration it's supposed to correspond to.
T-06 calls `corpus_features(corpus_root(...), provider="path")` for real on-disk names/inodes — this is what makes the parameter reachable, not unreachable as drafted.

## 4. H-3 / altitude item 4 — branch sites **[AMENDED — forced by item 7; reverses cycle-1's item 4]**
**DECISION: `corpus_open` is RULED OUT.** T-01's own intent (plan.yaml:97-131) already specs exactly three functions — `corpus_root`, `corpus_features`, `corpus_read` — and no fourth is needed once item 7's relocation is adopted. Per-reader disposition, enumerated against every task id this note names:
  - **T-03** (`check-state.sh`) and **T-04's four** (`board_lifecycle.py`, `check-plan-routes.py`, `validate-feature-json.py`, `layout_migration.py`): relocated (item 7). Each calls `corpus_features(root)` ONCE at the top, propagating `CorpusIncomplete` before any content read. That single gate already proves `root` is whole for the rest of the run, so every subsequent read is a plain `open(os.path.join(root, relpath))` — no per-site branch, no fallback, because the branch's condition ("not materialised") cannot fire once the top-level gate has passed. (T-03/T-04's plan.yaml intent text, which still says "read it through `corpus_read` at the resolved ref when the path is not materialised," is the wording this correction supersedes — pm updates both intents to plain `open()` against `root`.)
  - **T-05** (`merge-gate.py`): NOT relocated (hook-bound). Calls `corpus_read(path, ref)` directly, per its own plan.yaml intent (:305-306) — it never called `corpus_open`; cycle-1's item 8 misattributed this caller and is corrected below. The reason `corpus_read` and not plain `open()`: T-05 must name the read's ref in its deny message (D-05 provenance), and it wants that ref pinned to the same resolved ref its own `corpus_features(root)` call just used — a distinct concern from "materialised or not."
  - **T-06** (`check-domain.sh`): PATH provider only (item 3), no content read at all — confirmed by its own plan.yaml intent (:347-355).
  - **T-12** (`dispatch-guard.sh`): no corpus content read and no `corpus_features`/`corpus_read` call of any kind — it only compares declared `HARNESS-CORPUS-PROVIDER`/`HARNESS-CORPUS-REF` strings against the dispatch text (plan.yaml:620-639). It is not a corpus reader in the content-read sense; list it as such in T-07/T-13 so nobody hunts for an API call that isn't there.
  - `branch-create-gate.sh` (item 6's fifteenth reader): remedy (a) already specifies `corpus_features(root, provider="path")`, never `corpus_open` — unaffected by this ruling.
  - **DELETION TEST result:** at this caller count `corpus_open` has ZERO callers. Deleting it is correct, not merely reachable-with-one-caller.
**What remains of the HISTORY provider and `corpus_read`:** the HISTORY provider (`corpus_features(provider="history")`, the default) stays live with two callers — the top-of-script completeness gate in T-03/T-04, and T-08(c)'s set-equality check. `corpus_read` (content-at-a-ref) survives with exactly **one** caller: **T-15**'s manifest test, which reads content at a specific *recorded, possibly-stale* ref (plan.yaml:743-746) — genuinely different from "current tip," which is the variation that justifies keeping `corpus_read` as a seam distinct from plain `open()`. (T-05 is a second, narrower caller for provenance-naming reasons stated above; T-08(c) is a `corpus_features` caller, not a `corpus_read` caller — cycle-1's dispatch listed it as a candidate and this rules it out of that role.) D-04's two-provider split for `corpus_features` still has two live providers (path: T-06, `branch-create-gate.sh`; history: T-03/T-04's gate, T-08(c)). One caller is not an unused function: T-15's need (content at a pinned ref that may not be `root`'s current state) is exactly what `corpus_read` exists for, and it is real, not speculative.
**REJECTED:** keeping `corpus_open` as a wrapper over the now-unreachable branch (status quo of cycle-1's item 4). **FAILURE:** the "two things that vary across the seam" test fails — under relocation, "materialised on disk at `root`" is true unconditionally once the top-level gate has passed, so the branch's two arms collapse to one and the wrapper is dead code masquerading as an abstraction; D-01's own precedent (cutting `materialised_count`) applies identically here.
**AMENDED — cycle 3: T-03/T-04 read via `bases[feat]`.** The bullet above ("every subsequent read
is a plain `open(os.path.join(root, relpath))`") holds for ref-resolved-set members; for the single
in-flight feature admitted by item 2's cwd union it is `open(os.path.join(bases[feat], relpath))`
per item 2's base-resolution rule (`bases[feat] == root` for every ref-resolved feature, `==
os.getcwd()` for the in-flight one). "No per-site branch" still holds — the branch is item 2's
one-time mapping, decided once at the top, never a per-read decision. **Absence under cwd** (e.g.
missing `BRIEF.md` for the in-flight feature) **is an ordinary per-invariant absence**, handled
exactly like any other feature's missing-required-file finding, never a hard refusal and never an
uncaught `FileNotFoundError` — T-03/T-04 already produce a normal invariant-failed result for a
missing required file per feature; the in-flight feature goes through that same path, nothing new.

## 5. H-4 — T-13 lint allow-list
**DECISION:** exact-basename allow-list of exactly two, each with its own reason: `feature-worktree.py` (T-08's `sparse_include_list` builds the cone the API itself depends on — runs *before* any corpus is readable) and `migrate-worktree-corpus.py` (T-09 enumerates across multiple linked worktrees during migration, not through any single resolved root). T-06 is **not** allow-listed — its intent is corrected (item 3) to call `corpus_features(root, provider="path")` instead of hand-rolling a glob, which removes it from the lint trip at the source rather than exempting it. `T-13.depends_on` corrected to `[T-03, T-04, T-05, T-06, T-08, T-09]` (adds T-08/T-09, whose files the allow-list names).
**REJECTED:** pattern-weakening or suppression comments (both explicitly forbidden). **FAILURE (weakening):** narrowing the pattern to `glob.glob(...)` literals only lets a hand-written `os.listdir` + string-join enumeration slip through undetected — the exact bypass D-08 exists to close. **FAILURE (suppression):** a `# lint: allow` comment recreates D-05's own named residual (presence-checked, correspondence never checked) one layer down — nothing rechecks that the comment's justification still holds after a later edit.

## 6. MF-2 — branch-create-gate.sh, fifteenth reader
**Verified at source**, `branch-create-gate.sh:37-38`: `root="$(python3 ... harness_boundary.resolve_root(sys.argv[1]) ...)"` — `resolve_root`, not `worktree_owner`/`corpus_root`. `harness_boundary.py:66-67`'s own docstring: `resolve_root` is "environment-aware… reads HARNESS_PROJECT_DIR," with no owner-root derivation — confirming this is the **worktree's own root**, not the corpus root, exactly as the validator claimed. Line 89 then globs `$root/.harness/harness/features/${flow}*` at that (wrong) root.
**(a) Remedy:** replace `resolve_root(_selfbin)` with `corpus_root(_selfbin)` at line 38, and replace the raw `ls -d` glob at line 89 with an inline python call (the script already shells to python3 twice) that imports `harness_boundary` and checks flow-prefix membership via `corpus_features(root, provider="path")` — this both fixes the false deny and keeps the script off D-08's lint (it now calls the API instead of globbing directly).
**(b) Ledger status: OPEN, not closed by folding this one entry in.** MF-2 surfaced from an incidental grep, not a re-audit — the dedicated arch-eng reader-classification run already missed it once. Patching the count to fifteen repeats the exact enumerate-and-edit-each shape D-02 rejected for the refusal design itself.
**Closure instrument [REPLACED — cycle 2]:** cycle-1's instrument compared T-07's named-reader set against "the set of files T-13's lint discovers" — but T-13 (item 5, D-08) discovers VIOLATORS, and after this feature lands that set is empty by construction (every real reader calls the API); the equality was either vacuous or permanently red. Replace it with a second, DISCOVERY scan, run by T-07 alongside T-13's violation scan, over the same git-index tracked-file set:
  - **Pattern:** a file containing a call to `harness_boundary.corpus_features(`, `harness_boundary.corpus_read(`, or `harness_boundary.corpus_root(` (or the bare names after `from harness_boundary import ...`), excluding `harness_boundary.py` itself (same allow-list rule as T-13).
  - **Assertion, and its shape:** every file the discovery pattern finds is a member of T-07's named-reader list (⊆, not ==). This is a SOUNDNESS check, not a completeness one: T-07's fourteen (soon fifteen, once `branch-create-gate.sh` gets a task) also names readers cleared by inspection because they touch NO corpus API and NO violating glob shape at all (`quarantine.py`, `factory_decompose.py`, `feature_json_write.py` among them) — no regex derives that clearance, so completeness against the full ledger cannot be mechanised, and this note says so rather than inventing an instrument that can't fire.
  - **What this buys:** a fifteenth reader is now caught by ONE of two mechanisms — if it bypasses the API, T-13's violation scan flags it; if it calls the API correctly but was never added to T-07's list, this new subset assertion reddens (this is what would have caught `branch-create-gate.sh` today, once remedy (a) lands, if it were later dropped from T-07's list). Only a reader that touches the corpus through neither shape stays undetectable by grep — and such a reader, by definition, has no corpus-contract behavior to grade.

## 7. H-9 / altitude item 1 — relocate vs repoint (ADOPTED, scoped) **[forces items 2/4/8 above; struck line noted]**
**DECISION: ADOPT** relocation for the five non-hook-bound scripts only — T-03 (`check-state.sh`) and T-04's four validators. Measured (`.claude/settings.json`): only `check-domain.sh`, `merge-gate.sh`, `dispatch-guard.sh` are hook-registered; nothing binds these five to the caller's cwd. Each resolves `root = corpus_root(os.getcwd())` **once**, at the top (already drafted), then joins every subsequent corpus-relative read directly against `root` — no per-site materialised-or-history branch, because `root` (the owner root) is by design always whole. SC-04's per-reader refusal requirement is discharged by the single `corpus_features(root)` call at the top (propagating `CorpusIncomplete`) — that call tests the corrected predicate itself, independent of how the internal ~25 reads are shaped, so relocating does not weaken SC-04. ~~`corpus_open` (item 4) remains needed only for T-05 (hook-bound, executes against the caller's actual worktree at merge time) — T-06 needs no content read at all.~~ **Struck: item 4 above now rules `corpus_open` out entirely; T-06's no-content-read fact stands, restated there.**
**REJECTED:** repoint every reader (status quo, ~25 sites). **FAILURE:** same as item 4's — 25 independently-maintained branches in the tree's highest-traffic gate script, one missed site silently reopens the fail-open. This is unaddressed by any D-01..D-10; record it as a new decision.

## 8. M-6 — batching (RULED OUT) **[AMENDED — caller attribution corrected, forced by item 7/4]**
**DECISION:** do **not** implement `git cat-file --batch` batching anywhere, now. Item 7's relocation eliminates the case the 13.69 ms/call, ~13-14 s/run measurement was about — T-03/T-04's content reads become plain local `open()` calls once pinned at `root`, not `git show` subprocesses (item 4). The one surviving `corpus_read` caller with a real-time cost, **T-05**, reads O(1-2) candidate `feature.json` files per merge via `corpus_read` directly (its own plan.yaml intent, not `corpus_open` — cycle-1's item 8 named the wrong function; the caller and its cost profile are otherwise unchanged) — not O(88), so batching a handful of calls is noise against interpreter startup cost.
**REJECTED:** building batch-mode plumbing into `corpus_read` speculatively. **FAILURE:** this architects a subprocess-pipe protocol (`git cat-file --batch`'s newline-delimited format) for a bottleneck item 7 just removed; if a future caller reintroduces bulk reads its actual call shape may not match what's guessed at today. `check-state.sh` is confirmed not hook-registered regardless (a human waits once per manual run), which was already the dev-ops finding's own mitigating note.

## 9. Reuse angle — F1-F6, individually
- **F1 CONFIRMED** — chain the six existing `test-check-state-{records,worktrees,handoff,inv26,plans,entry}.py` into T-03's verify.
- **F2 CONFIRMED** — chain `test-board-lifecycle.py`, `test-check-plan-routes.py`, `test-validate-feature-json.py`, `test-layout-migration.py` into T-04's verify.
- **F3 CONFIRMED** — name `check_domain_support.py`'s `drive()`/`_env()` as T-06's required import; add (at minimum) `test-check-domain-worktree.py` to T-06's verify.
- **F4 CONFIRMED** — add `test-feature-worktree.py` to T-08's verify.
- **F5 CONFIRMED** — T-08 names `verify_required_paths(root)` as a public function in `feature-worktree.py`; T-09's intent is corrected to state `migrate-worktree-corpus.py` imports and calls it via `importlib` (mirroring its existing `sparse_include_list` import), not a re-derived list.
- **F6 CONFIRMED, resolution named** — `<sha>` (T-03d, T-04, T-05a, T-06a, T-12a) resolves to `git merge-base(<default-branch>, HEAD)` at task-execution time, matching this repo's own convention (`code-grade.py --base "$(git merge-base origin/main HEAD)"`). Rejected: "the commit immediately before my own task's edit" — ambiguous once tasks land sequentially in this same plan, since task N's "immediately before" already includes task N-1's fix, silently changing what a pinned RED assertion proves.

## Per-task cross-check (single non-contradictory instruction, verified against this finished note)
- **T-01:** three functions only (`corpus_root`, `corpus_features`, `corpus_read`) — item 4. No `corpus_open` anywhere else in this note.
- **T-03:** relocate to `root`; one top-level `corpus_features(root)` gate; reads resolve via
  `bases[feat]` — `root` for ref-resolved members, cwd for the in-flight union member, mapping built
  once at the top — items 7, 4, 2 (cycle-3 amended). No other instruction touches T-03.
- **T-04 (four validators):** identical to T-03 — items 7, 4, 2 (cycle-3 amended). No other
  instruction touches T-04.
- **T-05:** NOT relocated; calls `corpus_read(path, ref)` directly for provenance naming — items 4, 8. No other instruction touches T-05.
- **T-06:** PATH provider, no content read, not allow-listed on T-13 — items 3, 5, 4. No other instruction touches T-06.
- **T-07:** fourteen(→fifteen)-reader ledger, per-reader parity as originally speced, PLUS the new discovery-subset assertion against T-13's tracked-file scan — item 6. No other instruction touches T-07.
- **T-12:** enforces declared provider/ref strings only; not a content reader; listed as such in T-07 — item 4. No other instruction touches T-12.
- **T-13:** violation lint unchanged (item 5); its tracked-file enumeration is reused, not duplicated, by T-07's new discovery scan (item 6). No other instruction touches T-13.
- **T-15:** unaffected; sole `corpus_read` caller reading a pinned historical ref — item 4. No other instruction touches T-15.
Every id carries exactly one ruling above; none of the nine items assigns a second, different
instruction to any of them — re-verified against this cycle's item 2/4 amendment: T-03/T-04's
amended text (base-resolution via `bases[feat]`) refines items 2/4's existing rulings, it does not
add a new one, so the statement still holds.
