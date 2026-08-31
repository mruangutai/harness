# Distillation report — harness-security-reviewer — FEAT-45-adversarial-plan-panel merge

## BLUF

Repository tier got 3 new entries (2 Patterns, 1 Gotcha), applied cleanly through
`expertise-merge.py apply`. Craft tier got **zero** applied changes — not because nothing was
learned, but because **the merge tool has no replace/drop primitive**, confirmed empirically
against the live file (see "Tooling finding" below), and all three of craft's non-Open sections
(Patterns 15/15, Gotchas 15/15, Outcomes 10/10) are already at their DEC-145 caps. Six candidates
I judge genuinely superior to a specific existing entry are recorded below for a future
`/harness-curate` pass to actually execute.

## Tooling finding — expertise-merge.py apply is strictly add/preserve, never replace

Read `expertise-merge.py`'s `compute_union` and confirmed by two live probes against the real
craft file (both true no-ops — `MergeRefusal` raises before any bytes are written, and I verified
the file's line count was unchanged after each probe):

- Proposing `P-06` with new (better) text against the unchanged base text → `CONFLICT
  section=Patterns id=P-06`, **exit 7, nothing applied**.
- Proposing a new id (`P-99`) into an already-full `Patterns` section → `CAP EXCEEDED
  section=Patterns cap=15 union_size=16`, **exit 8, nothing applied**.

The tool is a monotonic union: it can ADD an id that doesn't exist yet and PRESERVE ids that do,
but it can never overwrite an existing id's text or remove one. "Displacing a weaker entry" — the
model this dispatch and `harness-distill` describe — has no execution path through this CLI for a
solo, non-concurrent distillation run. This is a harness defect/gap, not a judgment failure on my
part; raised as a non-blocking `open_question` rather than recorded in Expertise (a tooling bug
report does not belong in Expertise — it ages the moment the tool is fixed).

## Craft — accepted in judgment, blocked by tooling (would `replace`, cannot apply)

Each names the entry it would displace and why it is stronger. None of these are applied; a
future curation pass with a capable tool should act on them.

1. **Displaces P-15** (dispatch item c, self-corroborated at c3 §3): "WHEN a new lookup/coalescing
   mechanism's every failure mode converges on the pre-existing, already-audited fallback path DO
   rate it a reliability regression to prior behavior, not a bypass — 'fails to prior behavior'
   and 'fails open' are different verdicts; only the latter gates." P-15's near-miss-compensating-
   control framing is narrower and this generalizes to any coalescing/lookup mechanism.
2. **Displaces G-06** (dispatch item a, c3 §4): "WHEN a control's safety holds only because a
   check happens to run before a read/write — not from intrinsic containment or validation — DO
   rate it low/backlog as 'correct only by call-order,' and name the absent test that would catch
   a future reorder." G-06's "diff lands on a different repository" scenario is rarer/narrower.
3. **Displaces P-07** (dispatch item b, c3 §2): "WHEN asking whether an input is spoofable DO
   trace it to its actual producer first — often decidable (e.g. a host-set value, assigned
   pre-subagent, whose conflicting-setter throws) — and only if tracing is genuinely blocked DO
   close on provenance, naming the assumption that reopens it." Sharpens P-07 rather than
   contradicting it: closing via unverifiable-provenance is now explicitly the fallback, not the
   first move.
4. **Displaces P-06** (self-derived, c2 Finding 1 — the SEC-01 sibling-branch asymmetry, the
   feature's one HIGH finding): "WHEN auditing a branch-dispatched guard (hook tool_name routing,
   a digest-binding mode selector) DO diff every branch against its most-hardened sibling — a new
   branch parallel to an already-armored one commonly omits a corroboration step the sibling has,
   invisible from reading either branch alone." Generalizes P-06's original PreToolUse/PostToolUse
   framing to the actual bug class the feature found.
5. **Displaces G-15** (self-derived, c2 Finding 2 — the `SKIPPED` roll-up bypass, the feature's
   other HIGH finding): "WHEN a schema adds a self-asserted exemption field (e.g. `status:
   skipped`) that excuses an entry from a downstream gating check DO verify its scope is bound to
   something the reporter can't control (an allow-listed persona) — an escape hatch built for one
   narrow case is usable by every reporter." G-15's own-recommendation self-check is narrower.
6. **Displaces O-02** (self-derived, c4 §2 — the B-1/M4 closure): "WHEN closing a theoretical
   vulnerability class (ReDoS backtracking, path-precedence, race ordering) DO produce a runnable
   measurement rather than a structural argument alone — except a cryptographic-hardness claim
   (hash width, preimage resistance), where no test can probe the space and a birthday-bound
   argument is the correct, sufficient closure." This is a genuine, evidence-backed exception to
   O-02 as written, not a contradiction of it.

## Craft — rejected on merits (not tooling)

- **c2 Findings 3/4 (INV-32 absent/null-severity and unattributed-overrule non-regressions)** —
  the underlying technique (trace `.get()` default vs. present-null through every downstream
  branch; check structured `mitigated` field, not just prose) is already fully covered by existing
  O-01 and G-13. Not distinct enough to warrant a seventh displacement candidate.
- **c4's doc-staleness findings (stale `verify:`/`intent:` text describing an already-widened
  value)** — real and well-reasoned (a future engineer could "fix" code back toward a closed gap
  to satisfy stale prose), but it is a specific instance of the general pattern already split
  across G-08 (verify a diff's own safety-asserting comment now) and P-08 (diff against pre-change
  state, not zero). Folding it in would blur two already-distinct, already-used entries rather
  than sharpen either.
- **The `gateRoot()`/`.agents/skills` symlink finding in `handoff-validate.md`** (hooks always
  execute main's copy, so an in-flight fix is unverifiable pre-merge) — genuinely interesting and
  repo-specific, but it is not my own finding: grepped all five of my own cycle notes for it and
  found nothing; it belongs to whoever wrote that handoff (reads as validator-lead). Per this
  dispatch's own-material rule, I did not distill from it.

## G-01 advisory (DEC-100 citation) — ruled: leave as craft

`G-01`'s rule — "only `exit 2` blocks a Claude Code hook; any other exit, including an uncaught
exception, is non-blocking" — is a platform fact true of any repository using Claude Code hooks,
not something that depends on DEC-100 existing. `(DEC-100)` is cited as *provenance* (where this
repo empirically verified it, per `DECISIONS.md:1299`), not as a condition the rule turns on. Left
as craft, no change applied (and none was mechanically possible this run regardless — see tooling
finding above).

## Repository — applied

Two Patterns, one Gotcha, all self-derived from my own cycle notes, all newly created ids (clean
adds, no cap pressure — repo tier was 3/0/0/0 before, room throughout):

- `P-04`: `validate-digest.py`'s binding-check modes must each call the branch-corroboration
  helper (or equivalent host-only check) the way the original code-review mode does — the
  feature's central HIGH finding was exactly one mode skipping this.
- `P-05`: agent-definition/doctrine changes must be diffed against both `.claude/` and `.omp/`
  copies for byte-identical additions — confirmed as the review's standing practice across all
  five cycles, and this repo's `.claude`/`.omp` asymmetry (missing `spawns:` field) is a known,
  pre-existing, non-gating gap, not a signal to re-raise on sight.
- `G-01` (repo): the panel-finding severity vocabulary is declared independently across roughly
  six doctrine/agent files with no single source of truth — diff all copies, not a sample.

## Section counts

| Tier | Section | Before | After |
|---|---|---|---|
| Craft | Patterns | 15 | 15 |
| Craft | Gotchas | 15 | 15 |
| Craft | Outcomes | 10 | 10 |
| Craft | Open | 0 | 0 |
| Repository | Patterns | 3 | 5 |
| Repository | Gotchas | 0 | 1 |
| Repository | Outcomes | 0 | 0 |
| Repository | Open | 0 | 0 |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Repository tier: 3 entries added (2 Patterns, 1 Gotcha), applied cleanly. Craft tier: 0 applied — all three non-Open sections are at their DEC-145 cap and expertise-merge.py has no replace/drop primitive (confirmed live: exit 7 conflict, exit 8 cap-overflow, both true no-ops); 6 judged-superior candidates recorded for a future /harness-curate pass."
  files_touched: [".harness/harness/expertise/harness-security-reviewer.md", ".harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-distill.md"]
  expertise_update:
    - { op: add, target: null, section: Patterns, entry: "P-04 (repository tier) — validate-digest.py binding-mode corroboration inheritance", why: "the feature's central HIGH finding was one binding mode skipping the branch-corroboration helper its sibling calls" }
    - { op: add, target: null, section: Patterns, entry: "P-05 (repository tier) — diff .claude/ and .omp/ agent/doctrine copies for byte-identical additions", why: "standing practice used every one of the five review cycles this feature" }
    - { op: add, target: null, section: Gotchas, entry: "G-01 (repository tier) — panel-finding severity vocabulary has no single source of truth across ~6 doctrine files", why: "re-derived and confirmed byte-identical across all six sources at c1; durable structural fact about this repo's doctrine layout" }
  open_questions:
    - { id: Q1, question: "expertise-merge.py apply is strictly add/preserve — it refuses (exit 7/8, true no-op) rather than replacing or dropping an existing entry. A solo feature-close distillation therefore cannot ever displace a weaker entry in an already-capped section, contradicting the displacement model harness-distill and this dispatch describe. Should displacement be a distinct tool capability, or is it intentionally reserved for a separate /harness-curate pass with different tooling/authority?", blocking: false }
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-distill.md
```
