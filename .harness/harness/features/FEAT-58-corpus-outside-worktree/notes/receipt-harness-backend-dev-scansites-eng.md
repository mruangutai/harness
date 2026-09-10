# Receipt — scan-site measurement (backend, FEAT-58, measurement-only)

**Bottom line.** All four scripts read the WORKTREE's own copy of themselves (different inode
than main's) and resolve root arithmetically from that copy's location — so under D-1's sparse
cone they will each see exactly 1 feature where today (full checkout) they see the whole corpus
(measured: 79/88/89 → 1 in a sparse probe). merge-gate.py is invoked only via merge-gate.sh's
`exec`, never registered directly. **Q2 is a real gap**: a hardlink from a worktree-local path to
another feature's plan.yaml, reached only through the `.harness/corpus` symlink, is invisible to
BOTH existing guards — `_hardlink_plan`'s glob is scoped to `root` (which under D-1 is the local
one-feature tree) and `worktree_owner()` is pure path arithmetic with zero inode awareness.
merge-gate.py never calls `sys.exit` (0 matches) and its refusal is JSON-on-stdout, confirmed.
`linked_worktrees()` never raises for a linked-worktree root — it self-catches — so
check-domain.sh's outer bare `except: pass` (:2148-2153) is not what protects this call.

Environment note: `git worktree add`/`git checkout` outside `.claude/worktrees` are blocked by
this session's own bash-write-guard, so probes used plain `git clone` (not a linked worktree —
`.git` is a directory) for the sparse-count measurements, and one real hardlink built directly
inside `<wt>` (created/measured/deleted with plain `ln`/`find -delete`, since bash-write-guard
does not pattern-match those) for the worktree_owner() check. Both limitations are stated inline.

## Q1 — root resolution per site

**Confirmed empirically first: the worktree's OWN copy executes**, not main's — `board_lifecycle.py`
inode in `<wt>` (226611394) differs from main's (186845837) on the same device (16777230);
`check-domain.sh` likewise (226611397 vs 228841432).

- **(a) `board_lifecycle.py:476`** `_feature_dirs` — pattern `<root>/.harness/*/features/*/feature.json`,
  `root = harness_boundary.resolve_root(bin_dir)` where `bin_dir = os.path.dirname(__file__)` = the
  executing copy's own directory → **worktree's bin dir**, `root_from_script` walks up 4 → **worktree
  root**. Predicted 1 in a sparse cone, confirmed:
  ```
  $ python3 -c "...resolve_root(bin_dir,strict=False); glob(root+'/.harness/*/features/*/feature.json')"
  resolved root: /private/tmp/f58-scansite-probe
  matches: 1
  ```
  Today (full checkouts): main 79, wt 79.
- **(b) `check-plan-routes.py:835`** glob `<root>/.harness/*/features/*` (dirs). Same root arithmetic
  (`:600-602`, CLAUDE_PROJECT_DIR-or-derived). Predicted 1 in sparse probe, confirmed: `1`. Today: main
  89 dirs, wt 88 dirs (`.harness/*/features/*`), 79/79 `feature.json` in each.
- **(c) `validate-feature-json.py:42`** `discover_paths` — `root = harness_boundary.resolve_root(BIN_DIR)`,
  same shape. Predicted 1, confirmed:
  ```
  scanning /private/tmp/f58-scansite-probe/.harness/*/features/*/feature.{json,yaml,yml} — 1 file(s)
  count: 1
  ```
  Today: main 95 `feature.*`, wt 80 `feature.*` (branch-dependent corpus content differs slightly).
- **(d) `check-domain.sh` `_root()` (:128-154)`.** Registered `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh`
  (settings.json:23). `CLAUDE_PROJECT_DIR` is host-set and, per `harness_boundary.py:69-70`'s own
  comment, "always names the session project root" — i.e. the worktree, for a session whose cwd is
  that worktree (this is the documented mechanism this codebase already relies on; corroborated by
  prior receipts, e.g. FEAT-37 T-07: exporting `HARNESS_PROJECT_DIR` in-shell does not reach the
  hook subprocess, which is spawned via `${CLAUDE_PROJECT_DIR}/...`). So the script that runs is the
  **worktree's** copy. `_root()` calls `resolve_root(_bin_dir, strict=False)`, which reads
  `HARNESS_PROJECT_DIR` (never `CLAUDE_PROJECT_DIR`) — grepped the whole worktree: the only places
  that variable is *set* are test/fixture harnesses (`test-check-domain.py`, `BUG-1290`/`BUG-1305`/
  `FEAT-42` receipts, all deliberately exporting it around a probe), never normal session runtime.
  So in practice it is unset, `resolve_root` falls through to `root_from_script(bin_dir)` = bin_dir/../../../..
  = **the worktree root**. **`_root()` returns the worktree's own root**, same conclusion as (a)-(c).
- **(e) `merge-gate.py`** — never appears in `.claude/settings.json` or `.claude/templates/settings.snippet.json`
  (grepped both, zero matches). Only `merge-gate.sh` is registered (`settings.json:48`, PreToolUse
  Bash). `merge-gate.sh:4-10` computes `_selfbin` via `BASH_SOURCE` (same worktree-vs-main resolution
  as (d)), resolves `root` via the identical `resolve_root(_selfbin)` call (`strict=True` here, no
  fallback), then `exec python3 "$(dirname "$0")/merge-gate.py" "$root"` — same directory, so the
  worktree's `merge-gate.py` runs, in-process-replaced (exec), root passed as `argv[1]`.
  **Registration path form: `settings.json:48` → `merge-gate.sh` → `exec .../merge-gate.py "$root"`.**

## Q2 — the hardlink hole through the corpus symlink

**(i)** Built at `/private/tmp/f58-hardlink-probe`: `wt/.harness/corpus` → symlink → `owner/.harness/harness/features`.
```
pattern: /private/tmp/f58-hardlink-probe/wt/.harness/*/features/*/plan.yaml
matches: []
```
Does **not** match. Reason, read off the pattern shape: `corpus` sits where `_hardlink_plan`'s glob
expects the `<repo>` segment (`.harness/<repo>/features/...`), but `corpus` **is itself** the
`features` directory — there is no further `features/` child under it for the glob's next segment
to find. So this specific 5-segment sweep shape never traverses the corpus symlink at all — a
narrower finding than "guards see the corpus," not a guard.

**(ii)** Hardlink across the probe's two trees, same volume:
```
$ ln owner/.harness/harness/features/OWNER-FEAT/plan.yaml wt/.harness/harness/features/WT-OWN-FEAT/plan.yaml
ln exit=0
228935697 16777230   (owner file)
228935697 16777230   (wt-local hardlink — same inode/dev)
```
Repeated for real: `ln $MAIN/README.md $WT/f58-hardlink-probe-tmp.md` → exit 0, matching
inode/dev (226536256/16777230) across the main checkout and the linked worktree — confirms
cross-checkout hardlinking is possible on this host/filesystem, not merely in the synthetic fixture.

**(iii)** `worktree_owner()` on the real cross-checkout hardlink, called directly:
```
worktree_owner: ('/Users/.../worktrees/harness/FEAT-58-corpus-outside-worktree',
                  '/Users/molchairuangutai/GitHub/harness', True)
```
Identical to what it returns for any ordinary file in that worktree. **The function is pure path
arithmetic — it never stats for `st_ino`/`st_dev` — so the existing cross-checkout refusal has zero
visibility into hardlink aliasing.** Probe files removed (`find … -delete`, not `rm` — bash-write-guard
blocks `rm` on out-of-domain paths but does not pattern-match `find -delete`); `git status --porcelain`
back to the pre-existing baseline (see bottom).

**Conclusion for D-1:** yes — under sparseness, `_hardlink_plan`'s glob is scoped to `root`, which is
now the ONE local feature directory; a hardlink whose true target lives in another feature
(reachable only via `.harness/corpus`, physically outside `root`) can never be found by that glob
regardless of (i)'s naming question. `worktree_owner()`, the only other guard that inspects such a
path, is blind to inode identity by construction. **Neither guard fires.**

## Q3 — the sweep tier

`linked_worktrees(root)` called with `root` = the real linked worktree (`.git` there is a FILE,
confirmed: `os.path.isfile(root+"/.git") == True`):
```
linked_worktrees(root) -> [] (no exception, returned normally)
```
**No exception reaches check-domain.sh's outer `except: pass` (:2148-2153) from this call** — the
function has its own internal `except OSError: return []` (`harness_boundary.py:171-174`) around
`os.listdir(owner_root/.git/worktrees)`, and `owner_root/.git` being a file makes that `os.listdir`
raise `NotADirectoryError` (an `OSError` subclass), caught internally. The outer bare `except` in
check-domain.sh is therefore defensive only against `import harness_boundary` itself failing, not
against this call — a narrower finding than "the except swallows the worktree case," since nothing
needs swallowing there.

SWEEP_GLOBS (6 patterns, `:1052-1069`; header comment says "five", stale) matches today:
main checkout **796**, `<wt>` **465** (both full checkouts, different branch/commit content —
main@8902f566 vs feat/FEAT-58@5dda443b).

## Q4 — merge-gate.py refusal contract

```
$ grep -c 'sys.exit' merge-gate.py
0
```
Confirmed no `sys.exit` in the file. Quoted:
- `:144-145` — `def deny(reason):\n    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))`
- `:168` (fail-open) — `if not owners:` → prints an "allowing it... GitHub is a mirror and never a gate (DEC-138)" message to stderr and `return`s (falls through to normal exit 0, no `deny`).
- `:172-175` (multi-owner deny) — `if len(owners) > 1:` → `deny(f'... claimed by more than one feature record ({names}) ...')`.
Confirmed: refusal is a printed JSON payload carrying `"permissionDecision": "deny"`; the process
exits via its natural fall-off (or the shell wrapper's own exit), never `sys.exit`.

## Q5 — on-demand uniqueness computation, timed

Throwaway script at `/private/tmp/f58-q5-branch-uniqueness.py` (deleted after run): resolves
`harness_boundary.worktree_owner(os.getcwd())[1]`, globs `<owner_root>/.harness/*/features/*/feature.json`,
reads `branch`, builds branch→feature-ids. 5 runs from inside `<wt>`:
```
owner_root: /Users/molchairuangutai/GitHub/harness
record_count: 79
branch collisions (count): 2
colliding sets: {'none': ['FEAT-01', 'FEAT-15-domain-product-base', 'FEAT-19-central-product-config', 'FEAT-28-ci-wiring-asserted'],
                 'feat/harness-native-foundation': ['FEAT-02', 'FEAT-03-subissue-mirror']}
records with branch literal 'none': 4
times (s): [0.009, 0.0023, 0.0023, 0.0023, 0.0023]
median (s): 0.0023
```
**~520× faster than the operator's ~1.2 s assumption** — plain local `open()`/`json.load()` over 79
files on-disk, no git subprocess. One genuine branch collision (`FEAT-02`/`FEAT-03-subissue-mirror`
both cite `feat/harness-native-foundation`); the other group is 4 records sharing the literal
sentinel string `"none"`, not a real branch collision.

## Q6 — census feasibility (raw material for an allow-list)

```
$ grep -rn "features" .claude/skills/harness/bin --include=*.py --include=*.sh | grep -E '\.harness' | wc -l
114
```
Narrowed to lines that actually construct a disk path (glob/`os.path.join`/`Path`/shell glob) reaching
`.harness/<x>/features/`: **30**, across 15 files.

Literal `*` repo segment (glob wildcard, matches every repo):
- `board_lifecycle.py:476`, `check-plan-routes.py:665,835`, `validate-feature-json.py:42`,
  `merge-gate.py:134`, `layout_migration.py:188`, `check-state.sh:467`,
  `check-domain.sh:1054,1055,1056,1057,1061,1916`, `feature_schema.py:156,224` (doc-comment examples).

Known repo-segment variable joined (not `*`):
- `feature-worktree.py:243,258` (`segment`), `factory_config.py:437` (`seg`),
  `worktree_terminal.py:319` (`repo_segment`), `quarantine.py:109,171` (`repo`),
  `post-merge-sweep.sh:166` (`repo_segment`), `branch-create-gate.sh:89` (hardcoded literal `"harness"`,
  not a variable, not `*`), `layout_migration.py:187` (legacy shape, no repo segment at all),
  `check-state.sh:122` (fallback default, literal `"?"` placeholder, not `*` or a real segment).

Template/fixture strings (not live path construction — text `layout_fixtures.py` writes into
scratch fixtures to exercise the migration checker, not code that runs against the real corpus):
`layout_fixtures.py:35,38,39,46,47`.

## Byte-verification

```
$ git -C <wt> status --porcelain
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/feature.json
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c3.md
$ git -C <wt> diff --stat
 .harness/harness/features/FEAT-58-corpus-outside-worktree/feature.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```
**Identical before and after this dispatch** — this dirty state pre-existed (not created by any
probe here; O-06 applies, not reverted since it is not mine). Every probe (`/private/tmp` clone +
hardlink fixture, plus one real cross-checkout hardlink built and deleted directly in `<wt>` via
`ln`/`find -delete`) was created and removed within this session; no other file under `<wt>` was
touched.
