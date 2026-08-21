# receipt — harness-dev-ops — archreview S-A — FEAT-30 D-02/D-09/T-03/T-04/T-05

BLUF: D-09's blast-radius count (5) is exact, empirically confirmed by mutation. The
worktree_owner/linked_worktrees split is real and asymmetric (worktree-side vs owner-side),
which creates one accepted-cost state D-09 doesn't separately name (deleted `.git` file,
owner-side intact → swept but silently mis-normalised). T-05 in bash-write-guard.sh is the
only place a git-subcommand parser exists; check-domain.sh has none despite DEC-84 naming it
as that rule's intended home. The dev-ops early-return is confirmed by both code and
measurement. D-02's "fails OPEN" is measured TRUE for `harness_boundary.classify` (exit 1,
uncaught `NameError`) and PARTIALLY true overall — the shape-phase's *planned* absorbing
import, simulated here, correctly contains the failure to the D-09 narrowing rather than a
blanket fail-open.

**Note on the read-only boundary**: a `cd` inside a compound Bash command silently failed
(cwd resets between calls in this harness), and the following `git worktree add` ran against
the REAL checkout instead of the scratch dir, creating `.claude/worktrees/harness/FEAT-90` and
`.git/worktrees/FEAT-90`. Caught immediately via `git worktree list`, removed with
`git worktree remove --force`, pruned, and a stray `err.txt` from the same slip deleted.
Confirmed via `git status --porcelain` before/after: the only residue is pre-existing
concurrent-agent state (FEAT-30's own `plan.yaml`/`STATE.md`/`notes/`/`observations/`,
untracked FEAT-31), none of it mine. `git worktree list` now shows only the main checkout.

## Q1 — D-09 blast radius

**(a) Count.** Exactly 5, matching D-09's text, contradicting the "two" in an earlier pass.
Listed by line in `test-check-domain.py`'s `run_post`, all depending on `_norm`'s strip
(line 644) and/or `SWEEP_GLOBS`'s worktree arm (line 602):
- L1101 `"the sweep reaches a file inside .claude/worktrees/..."` (F-06, bare `wt1` fixture)
- L1179 iter 1 `"post Edit on a worktree file names the WORKTREE..."` (CLAUDE.md, `_wcm`)
- L1179 iter 2 `"post Edit (state file) ..."` (`_wfy`, feature.json)
- L1189 `"pre Write on a worktree file names the WORKTREE..."` (`_wcm`)
- L1198 `"the sweep still names the worktree it came from"` (`_wcm`, via sweep)
Each depends on the strip because `RE_CLAUDE_MD`/`RE_FEATURE_JSON` are anchored
(`check-domain.sh:663,669`) and only match the STRIPPED relative path.

**(b) Measured.** Copied `bin/`, neutered `_norm`'s regex (never matches) and dropped the
worktree arm of `SWEEP_GLOBS`, ran the suite with `CHECK_DOMAIN_BIN` pointed at the copy:
exactly those 5 named cases went red (`the sweep reaches a file inside .claude/worktrees/`,
`post Edit ...`, `post Edit (state file) ...`, `pre Write ...`, `the sweep still names the
worktree...`). One unrelated case (`schema/a CRASHING schema module DENIES...`) also reddened
under **any** `CHECK_DOMAIN_BIN` override, including an unmutated copy — confirmed as a
harness of the test (it mutates the real checkout's `feature_schema.py` by `__file__`, which
the copy's `check-domain.sh` never imports) — not part of D-09's blast radius.

**(c) Pointer sides, measured/read.** `worktree_owner` (`harness_boundary.py:355`) reads only
the **worktree-side** `.git` file — it walks up from the target path and parses that file's own
`gitdir:` line; it never opens the owner-side `.git/worktrees/<id>/gitdir` file, only derives
that path's expected string and checks legitimacy against it. Planned `linked_worktrees` (T-04)
is **owner-side only** per its own spec text ("reads the gitdir pointer file inside each
directory under `owner_root/.git/worktrees`... returns the realpath of each existing
directory") — it does not check that the worktree-side `.git` pointer is itself intact, only
that the target directory named by the owner-side pointer exists.

Enumerated states (✓=covered per the intact-registration case; consequences derived from the
code, not assumed):
| State | Swept? | Normalised (named-target)? | Budget miss? |
|---|---|---|---|
| bare hand-made dir, no pointer either side | No (not enumerable) | No (falls to base=root) | Yes — the D-09-named cost |
| owner-side pruned, worktree-side `.git` intact | **No** (`linked_worktrees` misses it) | **Yes** (`worktree_owner` is worktree-side, unaffected) | Only via the Bash-sweep route; named-target Write/Edit still catches it |
| worktree-side `.git` deleted, owner-side entry intact | **Yes** — `linked_worktrees` only checks the target directory exists, not that its own `.git` is valid, so the sweep still globs into it | **No** — `worktree_owner` walking up finds no `.git`, falls through to the OWNER's own `.git`, returns `(owner_root, owner_root, True)`; `checkout_relative`'s candidate is then skipped because checkout==base | **Yes**, even though reached: normalises to the unstripped path, matches no shape regex |
| `git worktree remove` leftovers (admin dir "prunable", no directory) | n/a — no directory exists | n/a | n/a — nothing to hold state |
| `feature-worktree.py create` failing mid-flight (T-01 step 3 parent-dir vs step 4/5 `git worktree add`) | MEASURED, not guessed: git 2.50.1, three real failure modes (dest pre-exists, branch already checked out, corrupted blob forcing checkout failure) **all either refuse before creating the destination at all, or roll back the destination AND its owner-side admin dir cleanly**. In none of the three did a partially-registered, one-sided leftover appear. So this named scenario, as literally specified in the dispatch, does **not** reproduce the accepted-cost gap under measured git behaviour — only the parent directory (empty) may be left, which holds no state file |

The most interesting real gap D-09's text does not separately spell out: **worktree-side `.git`
deleted, owner-side intact** — the file IS reached by the sweep (owner-side lookup doesn't
check the worktree-side pointer) but IS NOT correctly shape-checked (named-target
normalisation fails because it's worktree-side-driven), so it is a silent miss disguised as
"reached."

**(d) One-mechanism-no-narrowing shape.** Feasible only narrowly. A `**`-recursive glob
sweep is genuinely depth-agnostic and pointer-free, but its cost scales with the **total
directory tree size under every worktree**, not with worktree **count** — the opposite of
`linked_worktrees`' O(worktree-count) pointer-read cost the plan measured (0.371 ms/call at 5
worktrees). A real checked-out repo's `node_modules`/build output under a worktree would make
this materially more expensive per governed Bash write. It is also only anchorable for the
5 KNOWN sweep-pattern suffixes (you can derive the worktree-relative prefix by subtracting the
known suffix's segment count from the matched absolute path) — it does **not** generalise to
the other two D-02 consumers, `classify` and the resolve path, which must relativize
**arbitrary** governed-write targets with no known suffix to anchor against. So this shape
does not unify to "one mechanism" across all four D-02 consumers; it would be a third
mechanism layered beside `checkout_relative`, applicable only to the sweep/normaliser pair —
consistent with D-09's own "cannot all hold at once" trilemma, not a refutation of it.

## Q2 — which guard hosts the HEAD-move refusal

`.claude/settings.json`: `check-domain.sh` is registered for `PreToolUse` matcher `Write|Edit`
(never `Bash` pre-write) and `PostToolUse` matcher `Write|Edit|Bash` (via `--post`).
`bash-write-guard.sh` is registered for `PreToolUse` matcher `Bash` only. So **only
`bash-write-guard.sh` sees a Bash command before it runs**; `check-domain.sh` only sees Bash
post-hoc, and its post-Bash branch (`check-domain.sh:1003-1042`) reads no command text at all —
it globs the filesystem, deliberately ("classifying arbitrary shell... is the prediction
problem this mode exists to avoid").

`check-domain.sh` parses **no** git-subcommand or command text anywhere — grepped for
`destructive`/`rm -rf`/`--force`/`git push`/`git reset`: zero hits. DEC-84's own text
(`DECISIONS.md:1075-1076`) says the destructive-operation matcher is "a `Bash` matcher in
`check-domain.sh`... or it does not exist" — and empirically it does not exist there. The one
and only git-subcommand parser in either script is `bash-write-guard.sh`'s worktree
`add`/`move` walk (lines ~405-427, confirmed by reading), which T-05 plans to extend in place
(admitting `remove`/`prune`, and separately adding the HEAD-move vocabulary).

Given the routing (only `bash-write-guard.sh` receives Bash pre-write) and the parser's actual
location (only in `bash-write-guard.sh`), `check-domain.sh` could not host a git-subcommand
rule on the Bash pre-write route without **either** growing a second parser inside itself
**or** being newly registered on `PreToolUse: Bash` (a settings change T-05 as scoped does not
make and does not need). The two scripts do not see the same payload for a Bash call: only
`bash-write-guard.sh` sees it pre-write; `check-domain.sh` sees Bash only post-write, with no
command text exposed to it by design.

## Q3 — the dev-ops exemption

`bash-write-guard.sh:50-58`:
```
agent = d.get("agent_type") or ""
if not agent:            # 51 — no agent_type (main session) -> exit 0
    sys.exit(0)
...
if agent == "harness-dev-ops":   # 56 -> exit 0
    sys.exit(0)
if not agent.startswith("harness-"):   # 58 -> exit 0
    sys.exit(0)
```
Confirmed: dev-ops returns before any rule below line 58 fires, T-05's planned HEAD-move rule
included, since that rule is necessarily written after this point in the file.

Measured, current (unbuilt) state — `git checkout main` payload, three `agent_type`s, driven
directly against today's `bash-write-guard.sh`:
- `harness-dev-ops` → exit 0
- `harness-backend-dev` → exit 0
- `harness-orchestrator` → exit 0
All three exit 0 today because the HEAD-move rule does not exist yet (T-05 is unbuilt) — this
is the pre-T-05 baseline, not evidence about the rule's eventual reach. The code-level fact
that matters is structural: once T-05 lands, `harness-dev-ops` will still short-circuit at
line 56 and never reach the new rule, while `harness-backend-dev`/`harness-orchestrator` will
not (neither is named at 50-58; D-04 explicitly forbids exempting the orchestrator, and the
code confirms no such exemption exists).

Only two classes share an early-return before any rule: no `agent_type` at all (main
session/ungoverned tools), and `agent_type` not prefixed `harness-`. `harness-dev-ops` is the
only **named** persona exemption. `check-domain.sh` has no persona-specific early return at
all — grepped for `dev-ops`, zero hits — so no equivalent exemption exists there.

## Q4 — T-04 atomicity / fail-open

**(a) `classify` consumer, measured in a copy.** Deleted the `WORKTREE_REL_RE` definition
(`harness_boundary.py:37`) from a copy, leaving its internal reference at line 310 intact (an
in-file split of the same cutover T-04 must do atomically). Drove a real linked-worktree
fixture (`.git` file worktree-side, matching pointer owner-side) with a governed,
NOT-granted write (`harness-documentor` write to `notallowed/x.md`, granted only
`allowed/**`). Result: **exit 1**, an uncaught `NameError: name 'WORKTREE_REL_RE' is not
defined` at `harness_boundary.py:309` inside `classify`. Exit 1 is the guard's own documented
non-blocking code (`check-domain.sh:14` "exit 1 is a NON-blocking error and the write
proceeds") — the write is not refused. **D-02's claim is measured TRUE for this consumer.**

**(b) Shape-phase absorbing import, simulated.** T-04 hasn't landed, so there is no shipped
absorbing import to break — I built the minimal version T-04's own intent text specifies
(`try: import harness_boundary as _hb; _cr = _hb.checkout_relative(...) ... except Exception:
pass`) inside a copy's `_norm`, against a copy of `harness_boundary.py` that genuinely has no
`checkout_relative` (so the call raises `AttributeError`, caught by the `except`). Drove a
ROOT-level (non-worktree) over-budget `CLAUDE.md` (81 lines) through it: **exit 2**, identical
message to the real script (`CLAUDE.md is 81 lines — budget is 80 (DEC-181)`). The absorbing
design, as specified, correctly contains the missing-attribute failure to a fallback on the
base-relative path — it does not propagate to an uncaught exception the way the unguarded
`classify`/resolve-path references do.

**Verdict: D-02's "fails OPEN" claim is PARTIALLY correct.** Correct and measured for
`harness_boundary.classify` (used by every governed Write/Edit through `domain_check()`) — an
uncaught exception there is a **total** fail-open (no write refused for any reason, not only
worktree ones), which alone justifies T-04's atomicity. By identical unguarded-reference code
shape, the same applies to the `check-domain.sh` resolve-path access at line 212 (not
independently driven end-to-end here — same code pattern, not separately measured). It is
NOT correct as a blanket description of the shape-phase normaliser or the sweep-glob site:
those are specified with (and, simulated here, correctly implement) an ABSORBING import whose
failure degrades only to the narrower, already-accepted D-09 cost (worktree-scoped misses),
not a general fail-open. D-02's atomicity conclusion holds regardless — the `classify`
consumer alone is a sufficient, measured reason not to split T-04 per file — but the text's
phrasing understates that two of the four named consumers are designed not to fail open at
all.

## Open questions

None blocking. One process note, not a defect in FEAT-30's plan or code: my own probe
briefly created a real worktree in this checkout due to a `cd` silently failing between Bash
calls; cleaned up and verified via `git worktree list` / `git status --porcelain`. Recorded
here for the record per rule 15, not filed as an open question against this feature.
