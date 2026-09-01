# pm feature-close distillation — FEAT-45-adversarial-plan-panel

**BLUF. All three relayed candidates accepted; five craft displacements paid for them and two
self-derived craft entries; five repository-tier entries added into free space. Four candidates from
my own log died — two as harness defects, two at cap with nothing weaker to displace.**

Files modified: `.harness/expertise/harness-pm.md` (craft), `.harness/harness/expertise/harness-pm.md`
(repository). Applied through `expertise-merge.py apply`, one invocation per tier, exit 0 both.

## Counts

| Tier | Patterns | Gotchas | Outcomes | Open | Lines |
|---|---|---|---|---|---|
| craft BEFORE | 15/15 | 15/15 | 10/10 | 0/5 | 133 |
| craft AFTER | 15/15 | 15/15 | 10/10 | 0/5 | 45 |
| repo BEFORE | 0/15 | 10/15 | 0/10 | 0/5 | 15 |
| repo AFTER | 1/15 | 14/15 | 0/10 | 0/5 | 20 |

The craft line drop is the merge tool's canonical render — it folds each wrapped entry onto one line
and drops inter-section blanks. **No entry was lost**: 40 entries before, 40 after (35 `PRESERVED` +
5 `ADDED`, minus the 5 I deleted first). Per-entry word counts of all ten new entries: 37–49, cap 50.

## Accepted, and what each displaced

The merge tool is union-only — a same-id/different-text proposal exits 7 and a new id in a full
section exits 8 — so each displacement was a surgical line delete of the weaker entry first, then a
merge-add under a fresh id. No whole-file write.

| New | Source | Displaced | Why the displaced entry was weaker |
|---|---|---|---|
| `P-16` generator reachability / refusal branches | relay (b), my log | `P-09` mutate-the-tool-to-test-a-coverage-claim | subsumed by the six-entry Outcomes mutation cluster (`O-01`, `O-02`, `O-06`), which states aiming and reach-confirmation more precisely |
| `P-17` approved consequence needs a task | relay (c), `research-team-count-tripwire.md` | `P-10` anchor on content plus identifier | narrowest of the citation rules and already carried in substance by `G-01`/`G-05`'s re-derive discipline |
| `O-11` reuse the target's own red idiom | relay (a), my log | `O-09` dangling symlink for an unreadable path | a single-use recipe for a rare criterion; `O-11` governs every failing-first proof I author |
| `O-12` symlink the data, COPY the script | my log, 2026-08-31 | `O-10` copy tool and test module to a temp dir | direct predecessor, and weaker: it assumes the tool needs no repo layout. `O-12` handles the case where it does, and adds the `sys.path[0]` symlink trap |
| `O-13` non-zero on the unbuilt tree is not proof of discrimination | my log, `research-FEAT-45-planfix-c1.md` §"Two defects" | `O-05` mutating a resolved lookup to a literal | its payload (a no-op mutation reads as coverage) is `O-02`'s aiming rule applied once |

Relay judgments, stated: **(a) is distinct from craft `G-11`** — `G-11` governs a verify block
asserting a current failure; `O-11` governs the idiom of a *shipped standing* proof, and names the
relative-commit-ref drift `G-11` does not reach. **(b) is distinct from `P-15`** — `P-15` is derived
versus copied *fields*; `P-16` is whether the propagating code path is *reachable at all*.
**(c) is the complement of `P-06`**, not a restatement: `P-06` routes an unmeetable criterion,
`P-17` routes an approved consequence no task owns.

Repository tier (all five in free space, no displacement): `P-01` `evidence: unit` versus the script
array that actually runs the assertions — the mislabel I only caught at goal-check; `G-11` the
`.agents/skills` → `.claude/skills` symlink identity; `G-12` `DEVIATION` at exit 0 is the expected
carve-out output; `G-13` the hand-written ` :: <ruling>` index tail; `G-14` a `check-state.sh` mutant
must live in the harness bin directory.

## Rejected, with reasons

1. **`plan-merge.py` refuses the create path when the proposal carries `approval:` (exit 8).**
   A harness defect, already raised as an open question — a workaround in Expertise outlives the fix.
   The operational half is already repo `G-07`.
2. **`bash-write-guard.sh` blocks a heredoc feeding `--entries -`, and no in-domain temp path exists.**
   Covered by repo `G-01`; the missing-temp-path half is a defect, not a rule.
3. **"Sweep for the struck CLAIM, not only the struck NAME" (an eighth propagation site the dispatch
   did not list).** Real, and partially held by `P-12` (derive the pattern from the weakest fragment)
   and `P-14` (test the presupposed claim). At cap, nothing surviving was weaker. It dies.
4. **"A verify token list pinning data the intent says not to hardcode is a self-blocking task."**
   Detected by `P-08`'s discipline of running the verify against the intent prose; no weaker
   survivor to displace. It dies.

## The `P-01` advisory — ruled, and it stays craft

`.harness/expertise/harness-pm.md` `P-01` names `.harness/harness/features/` as an exemplar pointer.
The rule — a grep that would already have passed is non-discriminating — is true in a repository I
have never seen; the path only says where a live example sits, which `harness-distill` explicitly
sanctions ("a recipe qualifies only as a pointer to a living in-repo exemplar"). Not moved, not
rewritten. The advisory stands as an advisory.

## Not run

`check-expertise.sh` (the orchestrator validates centrally), no commit, no formatter, no suite.
