# Plan-panel review — code-reviewer — BUG-1304 — cycle 2

## BLUF

L-01 through L-05 are all genuinely CLOSED, independently re-verified against `plan.yaml` text
and against source line anchors in the worktree — pm's repair note is not taken on trust anywhere
below. But the L-01 repair (D-10's unreadable-registry refusal) introduces a real, undisclosed
REQ-03 violation: it refuses *every* governed write, including ones squarely inside the writer's
own assigned worktree, whenever *any* registry anywhere in the whole worktree topology — not just
one this write touches — is unreadable. `must_fix`, HIGH. pm's own Q1 open question names a
narrower version of this (REQ-01 unbound agents) and defers it to signature as a soft cost; the
actual scope is broader and contradicts REQ-03's literal, unconditional text, so it is a finding,
not a ratifiable residue as currently worded.

## L-01..L-05 — CLOSED/STILL OPEN, independently verified

- **L-01: CLOSED.** REQ-05's third half (BRIEF.md) states the refuse case correctly: "a registry
  file that exists among the scanned roots but cannot be read as a claim list ... leaves the claim
  set INCOMPLETE ... the governed write is refused, naming the file to repair." D-10 states the
  same rule and preserves `_parse`'s claim/write fallback untouched. SC-10 is non-vacuous — refusal
  + a paired well-formed control (exit 0) + SC-06's ran-proof, three parts in one case, so it
  cannot be satisfied by the ordinary claim-set rule. T-01 cases 7–9 and T-02's `UnreadableRegistry`
  propagation match; T-03 case 14/15 and T-05 case 16/17 match verbatim. T-04/T-06 correctly route
  `UnreadableRegistry` to the *seam's* exit-2 path, explicitly *not* the quarantine-style fail-open
  branch — this is the fix that actually closes the silent-allow. **But see the new finding below:
  the repair over-corrects and creates a new REQ-03 gap.**
- **L-02: CLOSED.** T-09 (`plan.yaml`) names all six `_expire_where` callers plus `reconcile` and
  `_all_live` — eight sites total — with exact line anchors. I re-grepped the live worktree copy of
  `inflight_registry.py` and every anchor is byte-accurate today: `orphan_write` call at :297,
  `live_claim` :323, `live_children` :343, `claim_with_receipt` :375, `attach_runtime_identity`
  :432, `release` :472, `reconcile` :519 (`_expire([claim_entry], now)`), `_all_live` :593
  (`_expire(data.get("claims", []), now)`). The seam is stated correctly — `(answer_live,
  retained)`, retention writes only to `data["claims"]`, every caller's *return value* stays as it
  is today — and `case_bug1304_retention_admission` specifically pins `claim_with_receipt`'s
  single-flight admission at the unmodified `live` list. No third seam answer beyond Advisor
  RULING B is invented; the eight-site enumeration is RULING B's own five representative anchors
  (`:234/:323-328/:343-349/:519/:593`) expanded to every concrete caller RULING B's text implied but
  didn't individually name (`orphan_write`, `claim_with_receipt`, `attach_runtime_identity`,
  `release`) — a more complete instance of the same ruling, not a new one.
- **L-03: CLOSED, independently re-audited across all ten `verify:` blocks — see table below.**
  `T-07`'s fixed negative grep (`! grep -qi "Bash route keeps DEC-153's blanket allow"`) is
  confirmed red today: `DECISIONS.md:5338` reads "The Bash route keeps DEC-153's blanket allow ..."
  verbatim, matching the case-insensitive substring, so `!` fails today and will pass once T-07
  rewrites the sentence. `T-08`'s fixed pair is confirmed red today too: the string
  `worktree_for_feature(owner_root, flow)` does not exist yet (the live call at
  `dispatch-guard.sh:174` uses parameter name `declared`, not `flow`), and
  `os.path.basename(wt) == flow` at `:122` is present today, so `! grep -q ...` currently fails.
- **L-04: CLOSED.** I independently counted every refusal-producing case in T-03 and T-05's
  enumerated case lists (not pm's count): T-03 has exactly 9 (cases 1, 2, 3, 7's second half, 9,
  10, 11, 13, 14) and the verify floor is `-ge 9`; T-05 has exactly 11 (cases 1, 2, 3, 4, 8's
  second half, 10, 11, 12, 13's positive control, 15, 16) and the verify floor is `-ge 11`. Both
  match exactly. The helper is specified to be called "from EVERY refusal case in place of a
  hand-written exit-code check" on both T-03 and T-05, not just the first.
- **L-05: CLOSED.** T-09's opening states plainly the strike "OVERRIDES Advisor rulings A and B,"
  is "NOT symmetric with T-08's," and "leaves B-10 REACHABLE." D-09 carries the identical framing.
  SC-11 binds both halves: file-presence after `reconcile`/`live_children`/`orphan_write`-or-
  `release`, AND the dispatch/admission half via `claim_with_receipt` still admitting at 1200s.

## Ten-`verify:` audit (independent, not pm's count)

| Task | Can it fail today? | Binds the deliverable? |
|---|---|---|
| T-01 | Yes — `test "$a$b" = "11"` requires both suites red | Yes — pins "tests written before code" |
| T-02 | Yes — both suites must newly pass | Yes |
| T-03 | Yes — fixture/grep presence + `-ge 9` count + suite must stay red (`-eq 1`) | Yes — count matches enumerated cases exactly |
| T-04 | Yes — T-03's suite must go green | Yes |
| T-05 | Yes — same shape as T-03, `-ge 11`, matches count | Yes |
| T-06 | Yes — T-05's suite must go green | Yes |
| T-07 | Yes — 4 positive greps absent today (checked), negative grep present today (checked) | Yes |
| T-08 | Yes — both grep targets flip today→post-fix (checked against live source) | Yes |
| T-09 | Yes — `case_bug1304_retention,`/`_admission,` require CASES-tuple wiring, not just a `def` line (file's own bare-name-with-comma convention confirmed at :1073-1094) | Yes |
| T-10 | Yes — full suite + state checker, ordinary exit-code gate | Yes — explicitly the widest verification the plan carries |

No orphan REQ/SC, no dangling `traces:`, DAG unchanged and acyclic (T-08/T-09 both strikeable,
neither in T-10's `depends_on`, consistent with their strike text).

## New finding — HIGH — D-10's refusal has global blast radius REQ-03 does not authorize

`claim_worktrees(owner_root, agent_type)` (T-02) unconditionally scans **every** linked worktree's
registry plus the owner-root registry, for **every** governed write, before ever comparing the
resolved destination to S — the destination is not known to the function at all. If `live_claims`
raises `UnreadableRegistry` for *any* scanned root (T-01/T-02's design), `claim_worktrees` propagates
it, and T-04/T-06 catch it and exit 2 — **regardless of which registry was unreadable and
regardless of whether the write's own destination resolves cleanly inside the writer's own,
perfectly healthy, assigned worktree.** Concrete scenario: feature Y's registry crashes mid-write
(the exact class REQ-05 itself cites as plausible — "partial write, crash mid
`harness_merge.locked_update`"). A `harness-backend-dev` agent legitimately writing a file inside
feature X's own worktree — the paradigm case REQ-03 promises "keeps working unchanged" — is now
refused with exit 2, system-wide, for every governed persona on every feature, until someone
manually repairs feature Y's unrelated file. Before this repair, a corrupt registry anywhere was
silently treated as empty (fail-open, L-01's bug); after it, a corrupt registry anywhere blocks
everyone (a new, undisclosed fail-closed-globally property). No SC or task case in the plan
exercises "my own destination and my own claim's registry are both healthy, but an unrelated
feature's registry is corrupt" — it would ship unnoticed. This is materially broader than pm's own
Q1 ("reaches past bound-but-unplaceable into REQ-01 unbound agents"): it also breaks REQ-03's literal,
unconditional promise for writes that are unambiguously legitimate. Ratifying this at signature (Q1's
disposition) is not wrong in principle, but Q1's current wording undersells the cost to the operator
— it does not disclose that the blast radius is system-wide-for-a-write-that-was-never-in-question,
not merely "this persona's own write." Recommend either: state the true scope in D-10 and REQ-03's
own exception clause before signature, or narrow the implementation so an unreadable root only
poisons S when it could plausibly have contributed a member relevant to *this* write (e.g. resolve
the destination's own checkout first, and only require readability of registries that could
resolve to it or to a candidate the agent already holds).

## New finding — MED — pre-existing, out-of-scope sibling gap at the `linked_worktrees` layer

`harness_boundary.linked_worktrees` returns `[]` on any `OSError` listing `owner_root/.git/worktrees`
(`harness_boundary.py:171-173`), not just the documented "no worktrees exist" case — a permission
or filesystem hiccup on that one directory is indistinguishable from "no worktrees," and
`worktree_for_feature` then resolves every feature to `None`, so a live claim in a linked worktree
silently contributes nothing to S — the same shape L-01 just closed at the registry-file layer,
unclosed at the worktree-enumeration layer one level up. Not touched by any task in this plan
(`harness_boundary.py`'s `linked_worktrees` itself is not edited by T-01/T-02/T-04/T-06/T-08/T-09),
so it is not a repair regression, but it is the identical defect class BUG-1304 exists to close and
survives both panel cycles unaddressed. Lower likelihood than a corrupt JSON file (requires an I/O
fault on the directory itself, not just a bad write), hence med, not high.

## Q1 disposition — verdict

pm's own open question ("does D-10 reach past bound-but-unplaceable into REQ-01 unbound agents?")
correctly identifies that this is a real tension, but the disposition — punt to operator signature
as a soft, narrowly-scoped cost — is **not adequate as worded**, because it does not disclose the
REQ-03 violation above. Treat the HIGH finding above as the operative statement of the cost; Q1
should be resolved together with it, not signed off separately on its narrower framing.
