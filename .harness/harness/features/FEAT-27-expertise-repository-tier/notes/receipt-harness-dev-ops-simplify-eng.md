# EFFICIENCY review — `git diff b4659cd..252fa72` — harness-dev-ops (simplify, angle: efficiency)

## BLUF

No wasted work found. Wall-clock is unchanged (measured, within noise). The one real cost the
architecture review flagged — the N×40 repository-tier context bound — is confirmed real and
confirmed NOT narrowed by the shipped code, but that is a scope/governance fact about the feature
as designed, not waste this diff introduced or could cheaply avoid. No apply-worthy finding.

## Measurements

**Hot path — `inject-expertise.sh`, real hook payload (`{"agent_type":"harness-dev-ops"}`),
`CLAUDE_PROJECT_DIR` set, 20 invocations each:**

| Version | user+sys / 20 runs | ms/run |
|---|---|---|
| old (`b4659cd`) | 1.186s | 59.3 |
| new (`252fa72`) | 1.119s | 56.0 |

Delta is negative (new measured *faster*, within shell/spawn noise) — the added glob loop over
`.harness/*/expertise/<agent>.md`, the segment-sort subshell (`sort -t: -k2` + one more subprocess
when a repository tier is present), and `cap_body`'s new `$2` budget arg do not register against
the ~50ms floor set by the script's two `python3 -c` spawns (parse `agent_type` in, build the JSON
envelope out — both present unchanged since before this diff). This machine's `.harness/` today has
exactly one first-level dir with an `expertise/` subdir (`.harness/harness/`), so the loop runs
once around a length-1 array in the steady state.

**Standalone glob-loop cost** (50 iterations, ballpark, isolated from the python spawns): 0.004s
total — a rounding error, consistent with the head-to-head result above.

**Token/context bound — is N×40 narrowed by the shipped code?** No. Verified empirically: planted
`expertise/harness-dev-ops.md` under three more first-level dirs (`.harness/factory`,
`.harness/logs`, `.harness/notes`) and re-ran the hook — all four segments were picked up and
injected in a single call (confirmed via the emitted JSON's header list), on top of the pre-existing
`harness/` segment. Cleaned up immediately after (`rm -rf` the three planted `expertise/` dirs);
`git status --porcelain -- .harness/factory .harness/logs .harness/notes` came back empty, tree is
as it was. Neither of the two mechanisms the brief asked me to check narrows N:
- The agent-name regex (`^harness-[a-z0-9-]+$`) validates the *interpolated agent string*, not the
  number of directories scanned — its own adjacent comment says exactly this
  (`inject-expertise.sh:22-26`).
- The segment charset filter (`case "$segment" in ''|*[!a-z0-9-]*) continue ;; esac`,
  `inject-expertise.sh:73-77`) rejects malformed segment *names*; it does not cap how many
  well-formed segments can exist.

So the shipped bound is genuinely N×40 where N = "first-level `.harness/*/` dirs holding
`expertise/<agent>.md`", up to today's 5 first-level dirs (`expertise`, `factory`, `harness`,
`logs`, `notes`) — worst case 5×40=200 lines on top of craft's 150+150 and the index's 80, i.e. up
to ~580 lines injected per spawn if every first-level dir acquired a file for one agent. This is not
new waste from this diff's mechanics; it is the repository-tier feature working as designed. Capping
N is a `.harness/team-config.yaml` / directory-layout governance question, not something
`inject-expertise.sh` can or should decide unilaterally — noted for the record, not flagged as a
defect.

**Unit-suite registration — `run-unit-tests.sh`:**

| Run | wall time |
|---|---|
| `test-inject-expertise.py` alone (19 cases, each shelling out to bash + 2 python3 spawns) | 0.841s |
| `test-check-expertise.py` alone (22 cases) | 0.691s |
| full `--kind unit` (16 scripts incl. the new one) | 4.422s |

`test-inject-expertise.py` is ~19% of the unit-kind wall time, added once per full suite invocation
(CI / qa boundary gate) — not per spawn. Per the brief, deliberate full-suite runs at boundary steps
are the evidence the boundary exists, not waste; recorded here as the number, not flagged.

## Findings

None. Empty return per the brief's own guidance — a measured "the hook costs ~56ms and the added
loop is a rounding error" is the expected outcome here, and the token bound question the review
asked me to settle came back "no, not narrowed," which is a fact to carry forward, not a
fixable-waste finding (nothing in the diff can narrow it without deciding policy that is out of a
dev-ops-simplify-reader's remit).

## Files touched

- `.harness/harness/features/FEAT-27-expertise-repository-tier/notes/receipt-harness-dev-ops-simplify-eng.md` (this file)
- `.harness/harness/features/FEAT-27-expertise-repository-tier/observations/harness-dev-ops.md` (one dated bullet appended)

No source, test, or config file was modified. Three throwaway `expertise/harness-dev-ops.md` files
were planted under `.harness/{factory,logs,notes}/expertise/` for the empirical N-count check and
removed before this receipt was written; `git status --porcelain` on those paths confirms clean.
