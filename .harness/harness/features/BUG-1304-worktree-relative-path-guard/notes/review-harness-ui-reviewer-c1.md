# UI Review — BUG-1304 — panel-c1 — af5ddd7a

## Scope verdict: no rendered UI surface; one operator-facing text surface audited (dispatch-directed)

**Census (measured, not predicted).** Extensions across the full 12-file diff (`b64b2d53..6dd081a1`,
name-only, `sed 's/.*\.//' | sort -u`): `fixture md py sh`. Zero of `html css scss tsx jsx vue svelte
less`. `find .harness/harness/features/BUG-1304-worktree-relative-path-guard -iname DESIGN.md` →
empty; no design contract exists for this feature. Conventional Mode B (rendered surface vs.
DESIGN.md) is out of scope by measurement, not assumption.

**In-remit per dispatch (P-06):** the refusal strings the two guards print are the operator interface
at the moment a write is blocked. Audited below against REQ-06 and DEC-218.

## What changed, read at af5ddd7a

Both guards gained `claim_checkout_guard()` (check-domain.sh +51/-0, bash-write-guard.sh +43 net),
consuming shared primitives added to `harness_boundary.py` (`inside`, `claim_worktrees`,
`claim_set_refusal`, +70/-5). Three refusal shapes, identical logic on both routes:

1. **Ambiguous claim** (`harness_boundary.AmbiguousWorktree`)
2. **Unreadable registry** (`inflight_registry.UnreadableRegistry`)
3. **Normal claim/destination mismatch** (`claim_set_refusal`, expertise-route branch and default branch)

## Per-message audit against REQ-06

REQ-06: *"names the worktrees the agent holds and the destination the agent should have written, and
never advises removing a worktree. For a destination under `.harness/expertise/`, the advice is the
sanctioned CLI, never 'write it in your worktree'."* DEC-218: *"both ... exit 2, name the members of
$S$, and name the destination's proper home."*

### 1. Normal mismatch — default branch
`harness_boundary.py:294-297` (`claim_set_refusal`), emitted at
`check-domain.sh:806` / `bash-write-guard.sh:762`:
> `{agent_type} holds worktree claim(s): {held}. Destination {destination} belongs in its proper
> checkout at {home}; write it from a bound worktree.`
Names held worktrees (sorted, deduped, absolute — copy-pasteable, not a raw dump), names the attempted
destination, names the correct checkout (`root_above`). Never advises removal. **PASS**, both routes
identical at this layer.

### 2. Normal mismatch — expertise-route branch
`harness_boundary.py:287-292`, same call sites:
> `{agent_type} holds worktree claim(s): {held}. Destination {destination} belongs to the
> control-plane expertise route. Use the sanctioned python3 expertise-merge.py apply command.`
Names the CLI route exactly as REQ-06 requires, never "write it in your worktree." **PASS** at this
layer — see Finding 1 for what bash-write-guard.sh's wrapper does to it.

### 3. Unreadable registry
`harness_boundary.py:279-285`:
> `{agent_type} binding cannot be determined for destination {destination}; the write is refused
> because these claim registries are unreadable: {files}. Repair or remove those registry files,
> then retry.`
Names destination and the specific unreadable file(s) to repair. `"repair or remove ... registry
files"` refers to the `.inflight-claims.json` state file, not a worktree — does not trip the
never-remove-a-worktree clause. **PASS**.
Test-verified: `test-check-domain.py::run_bug1304_claim_set` ("unreadable registry refuses and names
file", asserts `unreadable_registry in text`) and the parallel Bash-route case.

### 4. Ambiguous claim — genuine gap
`check-domain.sh:775-779` / `bash-write-guard.sh:733`:
> `{agent} has an ambiguous worktree claim: feature 'FEAT-X' matches 2 linked worktrees: FEAT, FEAT-X`
Comprehensible (feature id, count, sorted basenames — not a raw dump). **But `destination` is never
printed in this branch on either route**, and DEC-218 itself states every refusal should "name the
destination's proper home." An operator hitting this mid-task sees which worktrees are ambiguous but
not what they were trying to write or where. `test-check-domain.py`'s own case ("ambiguous claim
refuses and names candidates") only asserts `"FEAT, FEAT-X" in text` — it does not assert destination
presence, so the gap is untested as well as unimplemented.
**Severity: high** — this is the shape DEC-218 explicitly commits to and both routes silently drop it
identically (a consistent gap is still a gap against a pinned decision, not a stylistic choice).

## Finding 1 — cross-route inconsistency: bash-write-guard.sh appends contradictory boilerplate

`bash-write-guard.sh`'s three new `claim_checkout_guard` call sites route every refusal through the
pre-existing `deny()` (bash-write-guard.sh:647-653), which unconditionally appends:
> `  File changes go through the Write tool, where your domain is enforced. A path the domain hook
> denied does not become writable by switching tools — that is guardrail evasion (DEC-151). If the
> file should be yours, raise it as an open_question.`
`check-domain.sh`'s three parallel call sites print the bare `claim_set_refusal()` text with no such
line (check-domain.sh:775-825). Confirmed by direct read at af5ddd7a on both files — not inferred from
one side.

**Concrete failure scenario:** `harness-backend-dev` holds a claim on worktree A only, and runs
`echo x > $EXPERTISE/harness-backend-dev.md` via Bash. It is refused with:
```
bash-write-guard: BLOCKED — harness-backend-dev holds worktree claim(s): <A>. Destination
<expertise-path> belongs to the control-plane expertise route. Use the sanctioned
python3 expertise-merge.py apply command.
  File changes go through the Write tool, where your domain is enforced. A path the domain hook
  denied does not become writable by switching tools — that is guardrail evasion (DEC-151)...
```
Line 1 gives the one correct remedy (the CLI route). Line 2 then tells the operator to use "the Write
tool" instead — but a `Write` attempt at the identical path hits check-domain.sh's identical
`claim_checkout_guard`/`claim_set_refusal` and is refused with the *same* expertise-route text, not
allowed. The appended line is not merely redundant, it is actively wrong for this refusal class: it
implies a working alternative that does not exist, for the exact destination class REQ-06 singles out
as "never advise relocation, only the CLI route." The same wrapper fires for the ambiguous-claim and
unreadable-registry shapes too, so every one of the three refusal types is Bash-route-longer and
harder to parse than its Write-route twin — an operator who hits the same refusal through both tools
must learn two vocabularies, which is exactly the failure mode the dispatch named.
**Severity: high.** `deny()` is pre-existing infrastructure (written for the REVIEWERS/domain-shape
case where "switch to Write" really is the fix); its reuse for `claim_checkout_guard`'s three new call
sites is new in this diff and was not exercised by any added test — `test-bash-write-guard.py`'s own
`"expertise refusal does not advise writing in worktree"` case checks only for the absence of one
literal phrase, not for the presence of the contradictory boilerplate.

## Actionability, in the round

- Next step present and unambiguous: **yes** for the default and expertise branches on
  check-domain.sh; **degraded** on bash-write-guard.sh by Finding 1's second line; **absent** for the
  ambiguous-claim branch on both routes (Finding, "4" above).
- Never advises worktree removal: confirmed clean on all six call sites (three shapes × two routes).
- Theme/contrast/reading-order: not applicable — plain stderr text, no rendered surface.
- Rendered-size/layout: not verifiable from source (n/a here — no markup exists to misrender).

## Verdict

FAIL. Two `high` findings against operator-facing text this diff adds: the ambiguous-claim branch
never names the destination on either route (a DEC-218-committed property, silently dropped), and
bash-write-guard.sh's `deny()` wrapper appends contradictory next-step guidance to all three new
refusal shapes, breaking the same-vocabulary requirement the dispatch called out. Neither is a matter
of taste; both leave the operator with an ambiguous or actively misleading next action at the exact
moment their work was blocked.
