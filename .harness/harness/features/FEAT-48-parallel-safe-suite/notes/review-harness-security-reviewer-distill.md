# Distillation — harness-security-reviewer — FEAT-48-parallel-safe-suite

## BLUF

Repository tier: 3 new Gotchas applied cleanly (headroom existed: 2/15 → 5/15). Craft tier:
**0 applied** — Patterns/Gotchas/Outcomes are all at their DEC-145 hard caps (15/15, 15/15,
10/10) with zero headroom, and `expertise-merge.py apply` — the sole legal write route — is
**measurably union-only**: it has no mechanism to shrink or update an existing entry. I confirmed
this live, not from reading the source alone: a same-ID/different-text proposal against P-09
returned `CONFLICT … exit=7`, and two separate new-ID proposals against Patterns and Gotchas both
returned `CAP EXCEEDED … exit=8`. All three attempts left the craft file byte-identical
(still 45 lines, still 15/15/15/10/10/0). Per the shared contract's own rule — "a write is
ACTUALLY DENIED → return the ops verbatim, quoting the exact denial" — I am returning five
craft-tier ops verbatim in `expertise_update` rather than silently dropping them or working around
the guard. This is filed as a harness defect in `open_questions`, not folded into Expertise.

## What I judged (five candidates, all judged strong enough to displace a named weaker peer)

1. **(relayed a) dating a finding pre-existing vs. introduced changes routing, not severity** —
   would replace craft P-09 (an O-01-adjacent specific instance of "prove identity, not shape").
2. **(own) symmetric OSError-swallow in a before/after snapshot diff** — the exact technique that
   found this cycle's one deterministic, non-racy `high` bypass (chmod a new dir to 0600; both
   snapshot passes hit the identical `PermissionError`, so a key-union diff never fires). Would
   replace craft G-03 (narrower backward-compat-widening scenario).
3. **(own) `git diff` 0/0 is vacuous for an untracked/gitignored signed record** — measured this
   cycle against a gitignored run digest. Would replace craft G-06 (rarer cross-repo scenario).
4. **(relayed b) parse a coverage claim's logical form (necessary- vs. sufficient-condition)
   before charging overclaim** — a direct self-correction; my own c9 charge against a
   necessary-condition sentence didn't hold on a literal reading. Would replace craft G-10.
5. **(relayed c) a high-severity finding with no failing SC and an un-editable remedy file still
   gets full severity — fixability/routing is downstream, never a reviewer discount** — would
   replace craft O-03 (narrower prompt-injection-scan scenario).

None of the three relayed candidates were accepted as-is (recall, not judgment, per contract);
each was re-derived, re-worded, and independently judged on its own merit against the craft file's
actual weakest peers. All five cleared the six-spawns bar. None could be written — see BLUF.

## Repository-tier additions (applied)

Three Gotchas, all naming exact files/decisions unique to this repo (`bin/run_pool.py`,
DEC-211, `plan.yaml` D-11, `.gitignore:7`): the two known, accepted-as-backlog gaps in the
mutation detector; the DEC-211-vs-D-11 coverage-claim divergence; and the gitignored-run-digest
git-diff-vacuity fact. See `expertise_update` for full text.

## Harness defect (not Expertise)

`harness-distill/SKILL.md` and this task's shared contract both describe a `replace` op as how a
full section is meant to accept a stronger candidate ("displacing one you judge weaker"). The only
tool with write authority, `expertise-merge.py apply`, has no code path that removes or updates an
existing id — `compute_union` unconditionally seeds `merged_list` from every base entry and either
appends a genuinely new id or refuses (conflict / cap). Confirmed live on this exact file, twice.
Per-feature distillation dispatches on a full section are therefore currently unable to displace
anything, contradicting the documented contract. See `open_questions`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Repo tier: 3 Gotchas added (2/15→5/15). Craft tier: 0 applied — all three sections are at DEC-145 hard cap and expertise-merge.py apply is measurably union-only (no replace/drop path), confirmed live (exit 7 conflict, exit 8x2 cap-exceeded); 5 judged-strong craft ops returned verbatim per the write-denied clause"
  in_scope: true
  scope_reason: "Distillation dispatch for harness-security-reviewer's own two Expertise files, per DEC-145/harness-distill"
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  counts:
    craft:
      path: .harness/expertise/harness-security-reviewer.md
      before: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 0 }
      after:  { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 0 }
      note: "unchanged — every apply attempt was refused (exit 7 or exit 8), confirmed live"
    repository:
      path: .harness/harness/expertise/harness-security-reviewer.md
      before: { Patterns: 5, Gotchas: 2, Outcomes: 0, Open: 0 }
      after:  { Patterns: 5, Gotchas: 5, Outcomes: 0, Open: 0 }
      note: "Outcomes/Open not created — no material warranted them"
  accepted:
    - candidate: "repo: run_pool.py known gaps (chmod-0600 bypass, __pycache__ basename skip) — self-derived"
      entry_id: "G-03 (repository tier)"
    - candidate: "repo: DEC-211 vs plan.yaml D-11 coverage-claim divergence — self-derived"
      entry_id: "G-04 (repository tier)"
    - candidate: "repo: git diff 0/0 vacuous for gitignored run-digest tree — self-derived"
      entry_id: "G-05 (repository tier)"
  rejected: []
  blocked_by_tool:
    - candidate: "(relayed a, reworded) dating a finding pre-existing vs. introduced changes downstream routing (backlog/operator decision) but not severity_max — reproduce against base commit and say so explicitly"
      would_replace: "craft P-09"
      reason_blocked: "exit 8: CAP EXCEEDED section=Patterns cap=15 union_size=16 — union-only tool, no removal path"
    - candidate: "(own) symmetric except-OSError swallow in a before/after snapshot diff is invisible to a key-union comparison when the identical error fires on both passes"
      would_replace: "craft G-03"
      reason_blocked: "exit 8: CAP EXCEEDED section=Gotchas cap=15 union_size=16 (live-tested)"
    - candidate: "(own) git diff 0 insertions/0 deletions on a signed record is vacuous, not proof of additive-only edit, when the file is untracked/gitignored"
      would_replace: "craft G-06"
      reason_blocked: "same union-only mechanism as above (code path identical across sections; not separately re-tested)"
    - candidate: "(relayed b, reworded) an overclaim charge against documentation must first parse the sentence's logical form — 'caught only when X' is a necessary condition, not falsified by an uncaught case outside X"
      would_replace: "craft G-10"
      reason_blocked: "same union-only mechanism (not separately re-tested)"
    - candidate: "(relayed c, reworded) a high-severity finding with no failing SC and an un-editable remedy file still earns full severity in must_fix; fixability/routing is a downstream, not a reviewer, concern"
      would_replace: "craft O-03"
      reason_blocked: "exit 7 mechanism verified same code path; Outcomes is also 10/10 full — not separately re-tested"
  open_questions:
    - id: Q1
      question: "expertise-merge.py apply is provably union-only (confirmed live: exit 7 on same-id/different-text, exit 8 on new-id/cap-exceeded, both leave the file byte-identical) — it has no replace or drop path. harness-distill/SKILL.md and this task's shared contract both describe displacing a weaker entry at a full section as a supported op. A per-feature distillation dispatch on any already-full section is currently unable to act on a judged-stronger candidate, no matter how clear the judgment. Does curation-capable shrinking belong in expertise-merge.py itself, or is it intentionally reserved for the separate harness-curate flow, and if so should harness-distill/the shared contract say that explicitly instead of describing a 'replace op' the CLI does not support?"
      blocking: true
  files_touched:
    - .harness/harness/expertise/harness-security-reviewer.md
  expertise_update:
    - op: add
      target: null
      section: Gotchas
      entry: "WHEN auditing bin/run_pool.py's snapshot()-based mutation detector DO check `_record`'s except-OSError swallow for the chmod-0600-directory bypass and the `__pycache__` basename skip preceding the symlink branch — both are known, accepted-as-backlog gaps present since the feature's first commit, not new regressions."
      why: "Repo-specific: names the exact file, function and two live gaps in this codebase's file-integrity gate, reproduced end to end and confirmed pre-existing at this repo's own base commit."
      applied: true
      entry_id: "G-03 (repository tier)"
    - op: add
      target: null
      section: Gotchas
      entry: "WHEN evaluating a coverage claim about run_pool.py's detector DO check DEC-211 and plan.yaml D-11 separately — DEC-211's metadata-tuple sentence is a narrow, accurate necessary-condition claim, while D-11's affirmative 'vector-agnostic inside DIR' claim is broader and can be false even when DEC-211 holds."
      why: "Repo-specific: names the exact decision record and plan clause in this repo where the two coverage claims live and can diverge."
      applied: true
      entry_id: "G-04 (repository tier)"
    - op: add
      target: null
      section: Gotchas
      entry: "WHEN auditing a signed run digest under `.harness/*/features/*/runs/**` for rule-15 (additive-only) compliance DO note that `.gitignore:7` excludes this whole tree from git — `git diff`/`log` structurally cannot verify prose-preservation there; `validate-digest.py`'s structural pass is the only available check."
      why: "Repo-specific: names the exact gitignore line and path pattern that makes git-based provenance checks vacuous for this repo's run-digest audit trail."
      applied: true
      entry_id: "G-05 (repository tier)"
    - op: replace
      target: "P-09 (craft)"
      section: Patterns
      entry: "WHEN a finding could be either introduced by this diff or pre-existing DO reproduce it against the base/pre-diff commit and state the result explicitly in the writeup — it doesn't change severity_max, but dating it pre-existing changes downstream routing from a blocking fix cycle to a recorded operator/backlog decision."
      why: "P-09 is substantially an instance of O-01's broader identity-level-evidence principle; the dating practice is new and produced a real routing decision this feature."
      applied: false
      denial: "exit 8: CAP EXCEEDED section=Patterns cap=15 union_size=16"
    - op: replace
      target: "G-03 (craft)"
      section: Gotchas
      entry: "WHEN auditing an except-OSError swallow inside a before/after snapshot diff DO check the symmetric case — the identical error firing on both passes (e.g. a directory missing its execute bit) drops the entry from both snapshots, defeating a key-union diff that already catches the asymmetric present-in-one case."
      why: "This exact technique found the one deterministic, non-racy, high-severity gate bypass this feature produced."
      applied: false
      denial: "exit 8: CAP EXCEEDED section=Gotchas cap=15 union_size=16"
    - op: replace
      target: "G-06 (craft)"
      section: Gotchas
      entry: "WHEN a git diff shows 0 insertions/0 deletions for a signed or audit-trail file DO check `git ls-files`/`log` first — an untracked or gitignored file makes that 0/0 vacuously true, not evidence the edit was additive-only or unchanged."
      why: "Directly measured this feature: a signed run digest lives in a permanently gitignored path, so git diff --numstat read 0/0 with no baseline to compare against."
      applied: false
      denial: "same union-only refusal path (verified on Patterns and Gotchas; not separately re-invoked for this id)"
    - op: replace
      target: "G-10 (craft)"
      section: Gotchas
      entry: "WHEN charging a documentation or comment claim as an overclaim DO parse its literal logical form first — a 'caught only when X' sentence is a necessary condition, not falsified by an uncaught case outside X; check every affirmative claim (e.g. 'vector-agnostic') separately before charging."
      why: "Self-correction: a charge I made against a necessary-condition sentence did not hold on a literal reading; the actual overclaim was a separate affirmative sentence."
      applied: false
      denial: "same union-only refusal path (verified on Patterns and Gotchas; not separately re-invoked for this id)"
    - op: replace
      target: "O-03 (craft)"
      section: Outcomes
      entry: "WHEN a high-severity finding has no failing approved success criterion behind it, or its remedy lives in a file outside any squad's write authority, DO still report it at full severity in must_fix — fixability and routing to an operator decision are downstream concerns, never grounds to discount severity yourself."
      why: "Measured this feature: a high-severity, deterministic gate bypass had no failing SC and lived in a main-session-direct file no squad could edit; it stayed at full severity and correctly resolved as an operator ship decision."
      applied: false
      denial: "same union-only refusal path (verified on Patterns and Gotchas; not separately re-invoked for this id)"
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-distill.md
```
