## Conclusion first

D-2 ("corpus read-only through the symlink") is **already enforced today**, verified by my own
probe, and does **not** rest on `check-domain.sh:2150`'s broken tier — the halted plan's carried-
forward claim conflates two independent worktree-detection code paths in the same file. Ruling:
**check-domain.sh:2150's defect is a SEPARATE TICKET**, folded here into D-3 (it is a peer-sweep
bug, not a D-2 enforcement gap). M-1's command is new (`bin/worktree-state.py`), its include list
is git-derived and proven to reach `.agents/skills`. D-4's two live data conditions are confirmed
unchanged on disk. Every item in E stays DEAD; none is forced back.

## A — M-1, the mechanism surface

**(a) Path:** new file `.claude/skills/harness/bin/worktree-state.py`, sibling of
`feature-worktree.py` and `worktree_terminal.py`, neither an extension of either.
`feature-worktree.py` (`bin/feature-worktree.py:99-136,207-315`) owns worktree **lifecycle** CRUD
(create/list/path/remove/behind) with module-level gate constants (`REFUSE_ON_DIRTY`,
`REQUIRE_LANDED`, :41-42) — no `--verify`/`--repair` exists there and adding one conflates
"create/destroy a worktree" with "assert/repair a standing worktree's state". `worktree_terminal.py`
(`worktree_terminal.py:398-489`) is a read-only **classifier over every standing worktree** for
cleanup eligibility (`classify`/`classify_all`) — the opposite cardinality of M-1, which asserts/
repairs **one** worktree (the caller's own, implicit cwd, invoked from a hook). It already
establishes the import-by-path precedent for a hyphenated sibling (`_import_feature_worktree`,
:38-45) that `worktree-state.py` reuses to call `resolve_repo`/`dest_for`.

**(b) Derivation source — proven, not asserted:** `git ls-tree -d --name-only HEAD` at the owner
root (top-level tracked dirs) minus `.harness`, plus `.harness/harness/features/<id>` where `id` is
the worktree's own basename (the naming invariant `dest_for` already establishes,
`feature-worktree.py:58-61`). Probe (`/tmp/f58-be-sparse-probe`, removed): derived set
`.agents .claude .github .omp council docs tests` + feature dir; after `git sparse-checkout set` +
default cone reapply, `ls .agents/skills` **PRESENT**. Second probe (`/tmp/f58-be-synth`, a bare
`git init` fixture): adding a new top-level tracked dir with zero source edits changed
`git ls-tree -d --name-only HEAD`'s output to include it — proves the list is derived, not literal.

**(c) The five checks, concrete command + pass condition** (git 2.50.1, confirmed installed):
1. Cone matches derived list + this worktree's feature — `git sparse-checkout list`, pass = set
   equality against (b)'s derivation.
2. `git sparse-checkout reapply`, pass = exit 0 (idempotent; reproduced twice, second run exit 0,
   no further change).
3. `.harness/corpus` resolves to `<owner-root>/.harness/harness/features` — pass =
   `os.path.realpath('.harness/corpus') == os.path.realpath(owner_root + "/.harness/harness/features")`
   and `os.path.islink('.harness/corpus')`.
4. Exactly one feature directory materialised — pass = `len(os.listdir('.harness/harness/features')) == 1`
   and that one name equals the worktree's own basename.
5. Working tree clean — `git status --porcelain`, pass = empty.

**Six broken inputs, six distinct proposed exit codes** (distinguishable on this host, reproduced at
`/tmp/f58-be-skipbit-probe`, removed): wrong cone → **3** (`sparse-checkout list` ≠ derived set);
skip-bits cleared → **4**, detected via `git ls-files -t` counting the `S`/`H` prefix
(measured: clean sparse checkout `129 H / 3678 S`; simulated corruption via
`git update-index --no-skip-worktree` on every `S` path → `3807 H / 0 S`, `git status --porcelain`
goes from 0 to 3678 lines — reproduces the note's mechanism exactly, then `git sparse-checkout
reapply` restores `129 H / 3678 S` and 0 dirty); symlink absent → **5** (`os.path.islink` False);
symlink pointing elsewhere → **6** (realpath mismatch, check 3 above); more than one feature
directory materialised → **7** (check 4 above, count > 1); dirty tree → **8** (check 5 above).
`--verify` runs all five checks and returns the first failing code without repairing (own test:
compare `git status --porcelain` and a checksum of `.git/info/sparse-checkout` before/after
`--verify` on a broken tree — must be byte-identical).

`.git` in a linked worktree is a **FILE**, confirmed directly:
`cat .claude/worktrees/harness/FEAT-58-corpus-outside-worktree/.git` →
`gitdir: /Users/…/harness/.git/worktrees/FEAT-58-corpus-outside-worktree`.

## B — D-3, the audit change

Every glob call site in `check-state.sh` reads the same `H = os.path.join(root, ".harness")`
(`check-state.sh:68`) via **21 independent** `glob.glob(H, "*", "features", "*", …)` calls,
starting with `_feat_dirs` at `check-state.sh:118-120`, then repeated at `:127-130, :136-137, :242,
:271-272, :295, :608, :840, :1151, :1225, :1289-1290, :1312, :1341, :1376, :1433, :1575-1576,
:1614-1615, :1725-1726, :2024-2025, :2126-2127, :2176, :2370-2371`. **Peer sweep:**
`check-domain.sh:2140-2153`'s `_sweep`/`SWEEP_GLOBS` loop, plus its own bugged sub-call
`_hb_sweep.linked_worktrees(root)` at `:2150` — **confirmed as the exact defect the halted plan's
receipts describe** (`receipt-harness-backend-dev-framefix-eng.md:96-100`,
`research-FEAT-58-finalapply-dispositions.md` item 4): `root` there is the **current** worktree
(`.git` a file), so `linked_worktrees(root)` does `os.listdir(root+"/.git/worktrees")`, gets
`NotADirectoryError` (an `OSError`), and the bare `except: pass` around the whole `_sweep` build
(`:2148-2153`) silently drops it to `[]` — the worktree half of the STATE.md-budget sweep never
runs from inside a worktree. **This is real and unfixed, but it is a peer-sweep completeness bug,
not the write-authorization mechanism** (see D). Fix: call
`_hb_sweep.linked_worktrees(_hb_sweep.worktree_owner(root)[1] or root)` — `worktree_owner` already
parses the `.git` file correctly (`harness_boundary.py:715-793`, verified by my D probe).

**Active feature resolution — nothing invented:** `feature-worktree.py:58-61`'s `dest_for` names
worktrees `<owner_root>/<segment>/<id>`, so the worktree's own basename **is** the feature id; grep
confirms `_ID_RE` (`feature-worktree.py:46`) is the sole accepted form. The fix belongs at
`check-state.sh:118-120`: after building `_feat_dirs`, assert
`len(_feat_dirs) == 1 and next(iter(_feat_dirs)) == os.path.basename(root)` (guarded by
`harness_boundary.worktree_owner(root)` legitimacy) and `sys.exit(2)` naming the mismatch before any
of the 20 downstream sites run — a single choke point, since every later site reads the same `H`.

**Baseline measurement — could not reproduce "1 of 88, exit 0".** Built a sparse worktree at
`.claude/worktrees/harness/f58-be-legit-probe` (removed) materialising exactly one real, merged
feature (`FEAT-10-software-factory`); `check-state.sh` there **exited 1**, not 0 — driven by
`INV-25`/`INV-29` (this probe path collided with a stray `/tmp` worktree left over from an earlier
probe of mine, an unrelated global worktree-placement invariant) and `INV-27` (repo-layout shape
check), plus FEAT-10's own genuine findings. With **zero** feature dirs materialised, `INV-27`
alone still catches it (`"CANNOT VERIFY features"`), non-zero exit. I could not construct a sparse
tree that reproduces a **silent clean exit 0** with the wrong feature set present — the failure
mode the note measured plausibly needed the specific mid-merge skip-bit corruption from M-1's
scenario, not a bare sparse checkout. **Do not carry the note's "1 of 88, exit 0" figure forward as
independently confirmed** — pm should treat it as the original author's measurement only, or ask
that agent for its exact repro steps.

**No-corpus-reach instrument:** wrap `builtins.open`/`glob.glob` (test-only monkeypatch on the
`exec()`'d module namespace) to record every path touched during a run, then assert
`os.path.commonpath([os.path.realpath(p), os.path.realpath(root)]) == os.path.realpath(root)` for
all of them — a read reaching through `.harness/corpus` resolves outside `root` and fails this
immediately.

**D-3 equivalence artifact:** the full stderr text for feature X (`grep`-filtered to lines naming
X), with the checkout's absolute root path replaced by a fixed placeholder token before diffing
sparse-run output against full-checkout output — normalises the only expected difference (absolute
paths) while comparing everything else byte-for-byte.

## C — D-4, the uniqueness index

Generation/consumption: no such index exists yet. `merge-gate.py:132-142`'s `feature_for(branch)`
is today's ad hoc equivalent — one `glob.glob(ROOT, ".harness","*","features","*","feature.json")`
per merge, no cache, called once per PreToolUse Bash merge command
(`merge-gate.py:154-198`, gated by `github.sync` and `merge_ref(command)`). D-4's index would
replace this glob with a pre-built row set; where it is generated/refreshed is an open question (no
existing generator to point at — see below).

**Both live data conditions confirmed independently, today, at this pin:**
```
FEAT-02: branch=feat/harness-native-foundation
FEAT-03-subissue-mirror: branch=feat/harness-native-foundation
FEAT-01 / FEAT-15-domain-product-base / FEAT-19-central-product-config / FEAT-28-ci-wiring-asserted: branch=none
```
(read via `json.load` over each `feature.json`, 79 `feature.json` rows total —
`git ls-files ".harness/*/features/*/feature.json" | wc -l` = 79, matching the note's row count).
Dedup scan over all 79: exactly one collision (`feat/harness-native-foundation`, FEAT-02/FEAT-03),
exactly four literal `"none"` values, matching the note exactly — **the data has not moved.**

`merge-gate.py:167-171` (`if not owners: return`): an unresolvable branch **allows** the merge
silently (with a stderr note only when `gh` resolution itself failed) — DEC-138's stated fail-open
for GitHub-as-mirror. The uniqueness index does not change this branch; it only changes how
`owners` gets populated (pre-built rows vs. live glob) and does not touch the `len(owners) > 1`
deny path (`:172-175`) or this `not owners` allow path. No fix proposed — out of scope per dispatch.

## D — the ruling: check-domain.sh:2150 vs D-2's enforcement

**Probe, my own, reproduced twice:** from cwd inside this worktree, created a scratch symlink
`.harness/corpus_probe -> <owner-root>/.harness/harness/features` (removed via `os.remove`; `git
status --porcelain` clean afterward), then invoked `check-domain.sh` exactly as the PreToolUse hook
does — JSON on stdin (`agent_type: harness-backend-dev`, `tool_name: Write`,
`tool_input.file_path` pointed at `.harness/corpus_probe/FEAT-10-software-factory/BRIEF.md`) — from
that cwd. Result: **exit 2**, `check-domain: BLOCKED — …/corpus_probe/FEAT-10-software-factory/
BRIEF.md is in /Users/…/harness, but this session is rooted in /Users/…/FEAT-58-corpus-outside-
worktree.` The write is **refused**.

**Why:** this refusal comes from `domain_check()`'s call to `harness_boundary.classify()`
(`check-domain.sh:921`), which resolves the symlink via `real(abs_target)` and calls
`worktree_owner()` (`harness_boundary.py:715-793`) — a function that **correctly** parses a `.git`
FILE (opens it, regexes `gitdir:`, walks to the owning `.git` directory) and returns UNKNOWN rather
than "not a worktree" on any parse failure (:759-765). It never calls `linked_worktrees()`. The
`wrong_checkout` outcome (`classify()` :615-633) fires because the resolved target and the session
root share the same owning repository but different checkouts — exactly this case. **`linked_
worktrees(root)`, the function broken at `check-domain.sh:2150`, is never reached on this path** —
it belongs to a different, later region of the same file (the STATE.md-budget report sweep, see B),
which the domain-check `sys.exit(2)` above short-circuits before it is ever reached.

**Ruling: SEPARATE TICKET, and D-2's enforcement does not rest on the `:2150` tier.** The halted
plan's carried-forward note (`STATE.md:15`) misattributes D-2's enforcement to the wrong function.
D-2 is enforced **today**, by `classify()`/`checkout_relative()`/`worktree_owner()`, verified above
by direct invocation the way the hook invokes it. The `:2150` defect is real (fixed in B, folded
into D-3's peer-sweep work) but governs only the budget-violation *report*, never a write decision.
pm's D-2 test can point straight at the probe above (a governed Write through a symlink resolving
to another checkout, asserted DENIED with exit 2) with no new mechanism required.

## E — what the re-derivation kills

All six: **DEAD**, none forced back.
- **Migration/convergence task** — DEAD (note :172-179: 3 live worktrees, no subject left).
- **Corpus-root anchor concept** (`corpus_root`/`corpus_features`/`corpus_read` API) — DEAD.
  Replaced by the fixed `.harness/corpus` symlink path (`STATE.md:13`); my D probe shows the
  existing `worktree_owner`/`checkout_relative`/`classify` machinery already enforces read/write
  boundaries around it with zero new API surface.
- **Fifteen-reader ledger** — DEAD. Ruling (3) in the note: no invariant reads a second feature;
  there is no set of "readers" needing conversion to a corpus API that doesn't exist.
- **Reflink/clonefile mechanism** — DEAD, explicitly excluded (note "What must NOT be written").
- **Byte-count criterion** — DEAD, same exclusion; `du`/byte bounds are satisfiable by clonefile.
- **Incremental-sweep cache** — DEAD, explicitly dropped by the operator (note :56-57).

## Open questions

- { id: Q1, question: "worktree-state.py's --verify/--repair needs a place to run its own tests (synthetic fixture per the note) — does pm want it under tests/unit/ alongside feature-worktree.py's existing suite, or a new test-worktree-state.py file? No existing convention names one.", blocking: false }
- { id: Q2, question: "D-4's uniqueness index generation/refresh point (a script run at merge-gate time vs. a maintained file) has no existing generator to extend — is this eng-lead's call to make in the plan, or does it need an operator decision given it touches merge-gate.py's hot path?", blocking: true }
- { id: Q3, question: "check-domain.sh:2150's fix (linked_worktrees(worktree_owner(root)[1] or root)) — since this sits in check-domain.sh, which DevOpsArch may also be touching for hook-wiring reasons, should this specific line-level fix be assigned to my D-3 task or coordinated with DevOpsArch to avoid a collision on the same file?", blocking: false }

## Revert proof

`git -C .claude/worktrees/harness/FEAT-58-corpus-outside-worktree status --porcelain` after all
probes: only this receipt plus pre-existing concurrent-sibling changes (`STATE.md`, `feature.json`,
`BRIEF.md`, `observations/harness-pm.md` — all modified by other agents mid-run, not by me; `notes/
receipt-harness-dev-ops-arch2-eng.md` and `.harness/notes/dod-worktree-corpus-2026-09-10.md` are
untracked files from siblings/earlier context, also not mine). No probe symlink, worktree, or
scratch file remains under this worktree or under `/Users/molchairuangutai/GitHub/harness` proper;
all four probe worktrees (`/tmp/f58-be-sparse-probe`, `.claude/worktrees/harness/f58-be-legit-
probe`, `/tmp/f58-be-checkstate-probe`, `/tmp/f58-be-skipbit-probe`) were removed via `git -C <main>
worktree remove --force <path>` from outside them; `git -C <main> worktree list` confirms none
remain.
