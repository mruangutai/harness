# Security review — FEAT-27 expertise-repository-tier — c0

Diff graded: `b4659cd..9b929de` (branch `feat/FEAT-27-expertise-repository-tier`). This is the
feature's **first** security review — `qa-final-validator/digest.md` confirms no code-reviewer,
security-reviewer or ui-reviewer artifact exists anywhere in the feature dir before this run.

## Verdict: PASS, no must-fix. severity_max = med (one accepted-risk item; see why below)

## 1. The regex/segment-filter claim — verified TRUE, not over- or understated

`inject-expertise.sh:27` (`^harness-[a-z0-9-]+$`) rejects every character that traversal or
injection needs: `/`, `.`, `*`, `;`, `` ` ``, `$`, space, quotes are all outside `[a-z0-9-]`. Traced
every use of `$agent` (grep, 5 sites, `inject-expertise.sh:27,32,33,68`) — all quoted, none reach
`eval`/subprocess. **Path traversal and glob/command injection via `$agent` are closed**, not by
convention but by the character class being mathematically incompatible with the needed
metacharacters. Confirmed against `test-inject-expertise.py` case12's four hostile values
(`"harness-"`, `"harness-qa/../../etc"`, `"harness-*"`, `"harness-qa;id"`) — each independently
fails the regex for a different reason (empty suffix / `.``/` / `*` / `;`), so the closure holds
even though (per the QA census, already settled) those particular assertions cannot redden.

The segment filter (`:75-77`, same `[a-z0-9-]` class applied to directory basenames) closes the
same class for the printed header text (`:114`) — no header-injection vector via segment name.

**What the filters do NOT do — and the plan says so, correctly.** `plan.yaml` D-01 states verbatim:
the filter "keeps traversal and shell metacharacters out ... it does NOT stop a legitimately named
stray such as `.harness/backup/expertise/harness-qa.md` from being injected into every qa spawn."
I verified this independently before reading D-01 (same conclusion, same file). **The claim is
accurate as stated — neither overstated nor understated.** This is an authorization question, not a
character-hygiene question, and the two are correctly kept separate in the comments at
`inject-expertise.sh:22-26`.

## 2. Ordering — validation runs before any path is built. No bug.

Regex check (`:21-29`) executes and can `exit 0` before `root`/`proj`/`glob` are ever assigned
(`:31-33`) or the repo glob runs (`:68`). A rejected `agent_type` never reaches path construction or
`emit()`. This is distinct from the already-settled ordering items in the QA census (segment *sort*
order, `test-inject-expertise.py:123` and `:225-233`) — I checked the separate
validate-before-construct question the dispatch asked about, and it holds.

## 3. Write authorization — the 16 new grants do NOT create a cross-agent escalation

Each new `team-config.yaml` line is `.harness/*/expertise/harness-<own-name>.md` — wildcard on the
*repository segment*, literal on the agent name. `check-domain.sh` delegates matching to
`harness_boundary.py:glob_to_re`, which translates bare `*` to `[^/]*` (does not cross `/`) —
confirmed by that file's own comment (`:43-46`) explaining why `fnmatch` was rejected for exactly
this reason. So the wildcard can only ever match **one** path segment (the repo name), never a
deeper path, and the agent-name field of every grant is a literal string. Result: agent X can write
`.harness/<any-single-segment>/expertise/harness-X.md` and nothing else — it cannot write another
agent's file, craft or repository tier. **No grant is wider than intended; this is not an
authorization defect.** (`dev-ops`'s pre-existing Bash bypass of `check-domain.sh` entirely, DEC-85,
is unchanged by this diff — it already had unrestricted write power before repository tier existed,
so the new file class doesn't meaningfully widen that specific sharp edge.)

## 4. Context poisoning / cross-repository bleed — real, tested, and already a signed decision (D-01)

Because a lower-trust agent cannot write a higher-trust agent's Expertise file (§3), there is no
new **cross-agent** poisoning path. There is a real **cross-repository** one: `inject-expertise.sh`
globs `.harness/*/expertise/<agent>.md` and injects **every** matching segment on **every** spawn,
with no way to know which repository the spawn is for (`SPEC.md` says this explicitly). Proven live
by `test-inject-expertise.py` case2: two segments ("harness" and "kaya") both fire simultaneously
for one spawn, in one context. The only mitigation is a text label
("not authoritative for your work — read the segment name") that the model is trusted to honor —
no code enforces it.

This is not a new discovery: `plan.yaml` D-01 names exactly this cost, including the unbounded
aggregate-size angle ("400 lines... at ten repositories... nothing measures total injected size"),
and states a deliberate non-fix with a named revisit trigger (unit 7, when grants become
repo-aware). `plan.yaml:4-7` shows the plan is `approved` by the operator. **I could not find a
must-fix here because the risk was already surfaced and signed, not because it doesn't exist.**

Rated `med`, not `high`, on **precondition-absent** grounds (G-11): today exactly one segment exists
in the shipped tree (`harness`, self-referential — verified via `git diff --stat`, all 6 new
`.harness/harness/expertise/*.md` files hold facts about this repo itself; "kaya" appears only in
test fixtures, never in real data). The mechanism that would make this a live cross-tenant leak
needs a second, *actually distinct and sensitive*, repository segment to exist — that doesn't
happen in this diff. Two things worth the operator's attention going forward, neither blocking this
ship: (a) `SPEC.md §5.6`'s "Risk to accept" bullet lists only the global-tier risk ("a wrong global
entry silently misleads every project at once") — the equivalent repository-tier risk (D-01's) isn't
echoed there for a reader who doesn't open `plan.yaml`; (b) the orchestrator's own carried Expertise
entry (`.harness/harness/expertise/harness-orchestrator.md` O-01, moved verbatim from the old
`OQ-02`) already states there is **no lineage protection** on any Expertise file — "an undeclared
edit... rides any cluster commit and only a human notices" — and repository tier multiplies the
count of such files per agent from 1 to 1+N without closing that gap. Human diff review remains the
only backstop for content-level (semantic) poisoning; `check-expertise.sh` checks structure/budget
only, never meaning.

## 5. Fail-open cost — unchanged, inherited, correctly scoped

The hook's `exit 0`-always contract (pre-existing, header comment `:7-9`, unchanged by this diff)
means a hostile or malformed `agent_type` produces **zero trace**: no stderr, no log line, nothing
distinguishes "rejected by the regex" from "no Expertise file exists yet." That is the accepted
design for a hook that must never block a spawn, not a regression — flagged for completeness, not
as a finding.

## 6. Data exposure via stdout/stderr — none beyond intended consumer

`inject-expertise.sh` emits only the querying agent's own craft + its own repository-tier files +
the codebase index — the injected consumer is exactly the spawned agent (by design). No path,
secret, or unrelated-agent content in its output. `check-expertise.sh`'s new advisory lines
(`:150-156`) print only the path already supplied as an argv by the caller and a token already
present in the file being linted — nothing new is disclosed to a party who didn't already have read
access. Grepped the full diff for credential-shaped strings (API keys, tokens, private-key headers)
— none found.

## 7. Advisory scan never gates — confirmed in code

`check-expertise.sh`'s repository-token advisory list is appended to a separate `advisories` list,
never to `problems`, and `sys.exit(1 if failed else 0)` reads only `failed`. The advisory scan
structurally cannot flip the exit code — confirmed by reading the control flow, not by re-running
the (already green) test suite.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| `SubagentStart` payload `agent_type` -> path construction / header | T, I | true — regex closes metacharacter classes; validated before any path use |
| `team-config.yaml` repository-tier grant -> `check-domain.sh` write | E | true — `[^/]*` single-segment match verified in `harness_boundary.py`, agent-name field literal |
| Repository-tier files -> injected across all segments into every spawn | I | false, precondition-absent — mechanism proven live (case2), signed accepted risk (D-01), only 1 real segment exists today |
| Expertise file content -> semantic/prompt injection into a future spawn | T, I | false, pre-existing (O-01), blast radius widened by file count, sole control is human PR review |
| `dev-ops` Bash bypass of `check-domain.sh` | E | false, pre-existing (DEC-85), unchanged by this diff |

## Not re-derived (already settled per dispatch)

case12 hostile values, test-check-expertise.py case2's `FEAT-\d+` sub-case, the two ordering
assertions at `test-inject-expertise.py:123` and `:225-233`, the `[ -r ]` guard's masked half, the
unreached global-tier branch at `:98-101`, and DEC-27/SPEC paraphrase falsification — all per
`runs/qa-final-validator/digest.md`, already routed.
