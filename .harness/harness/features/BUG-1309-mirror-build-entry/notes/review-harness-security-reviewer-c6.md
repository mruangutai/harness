# Security review — c6 — gate-integrity audit — BUG-1309-mirror-build-entry

Pin: `894adc0f08c71c108ef8432f1f7a3cc8a2a763c0`. Subject: `.claude/skills/harness/bin/merge-gate.py`.
All fixtures built and run from `/tmp/secprobe`; nothing in the tracked tree touched. Every claim below is
from an executed fixture, not reasoning; raw driver scripts remain at `/tmp/secprobe/*.py` for replay.

## Answer A — can a DENY be induced on a healthy repo? **YES, but not via the axis this pin fixed.**

The axis this pin closed (unattributable-record: non-dict/unparseable/hostile-`branch`-value, own or
foreign, anywhere in the tree) is **fixed**. 11 constructed combinations (own record crashed mid-write,
foreign non-dict, foreign unparseable, foreign dict-no-branch, 20 foreign malformed records, hostile
embedded-newline `branch` value) all → ALLOW as designed, matching the doc-comment intent. No deny was
induced on this axis.

A **different, pre-existing axis still induces a DENY on a healthy branch**: two *well-formed* dict
records both legitimately claiming the same `branch` value. `feature_for` (merge-gate.py:98-109) takes
the first `glob.glob()` match — `glob.glob` gives no ordering guarantee, and empirically in this
environment resolves to **whichever record was written most recently**. Constructed: a real, healthy
feature (`entry=opened`, created first) plus an unrelated feature directory created *second* that
merely copies the same `branch` value with an owed receipt → **DENY naming the unrelated feature**,
reproduced 5/5 (`/tmp/secprobe/group_a_spoof_dos.py`, cases A14.0–A14.4). This denies an actual healthy
merge and names a feature the operator has no business investigating.

## Answer B — can an ALLOW be induced on a repo owing a receipt? **YES, two ways.**

**1. Self-corruption of the owing feature's own record — this pin's own trade, and it is a bypass, not
an acceptable one.** A feature that owes a receipt gets ALLOWED the instant its own `feature.json`
becomes non-dict, truncated/unparseable, or is deleted outright (`/tmp/secprobe/group_b_bypass.py`
B2/B3/B4 — all ALLOW, silent, no stderr). Verdict: **bypass primitive**, not a signed trade, because:
  - the beneficiary is exactly the actor the receipt exists to constrain — the feature whose *own*
    merge is gated — and corrupting the one record that would deny them is a self-service escape
    hatch, not an accident that lands on a bystander.
  - **it is a regression introduced at this exact pin for the non-dict sub-case.** Built and ran the
    parent (`894adc0f^`) merge-gate.py directly against the identical B2 fixture
    (`/tmp/secprobe/parent_compare.py`): the parent's scan-wide `unusable` sentinel caught this and
    **DENIED** ("could not evaluate a feature's Build-entry receipt"). At this pin the same input
    **ALLOWS**. The unparseable/deleted sub-cases (B3/B4) were already ALLOW at the parent — not new.
  - it leaves zero audit trail: no stderr line, no distinguishing reason — indistinguishable from "this
    branch legitimately owes nothing."

**2. Branch-field spoofing — pre-existing, not introduced by this diff, never previously closed.** Any
actor able to write a `feature.json` anywhere under `.harness/*/features/*/` — not necessarily their
own feature's directory — can grant an owing feature an ALLOW by dropping an unrelated record claiming
the *same* `branch` with `build_entry: opened`. Constructed: real owing feature created first, spoof
record (`entry: opened`) created second, same branch → **ALLOW, 5/5**
(`/tmp/secprobe/group_b_spoof.py`). Confirmed pre-existing: same input against the parent
(`894adc0f^`) also ALLOWS, 3/3 (`parent_compare.py` PARENT-B9). The matching loop
(`document.get("branch") == branch`, first match wins) is untouched by this diff — this axis was never
in scope for any of the five closed cycles, which addressed malformed/unusable records, not two valid
records colliding on identity. Reachability note: `team-config.yaml:45` grants the ORCHESTRATOR
`.harness/*/features/**` (not scoped to its own feature id despite the comment's stated intent), and
one orchestrator instance runs per concurrently in-flight feature — so this is not a hypothetical
external attacker, it is a write surface already held by a routine harness role.

## Additional confirmed finding — the gate can be made structurally blind (pre-existing, not this diff)

`merge_ref`/`git_merge` do static token matching with no shell semantics. All four below → **silent
ALLOW, no stderr, regardless of the actual receipt state** — confirmed against an *owing* fixture
(`/tmp/secprobe/group_evasion.py`, `group_evasion2.py`):
- `B=feature/test; git merge $B` — branch resolves to the literal string `"$B"`, never expanded (E3).
- `eval "$G merge feature/test"` — the verb itself is never recognized as `git` (E4).
- **`git -C /tmp merge feature/test`, `git --work-tree /tmp merge ...`, `git -c k=v merge ...`** — any
  value-taking global git flag shifts `git_merge`'s naive `args[0] != "merge"` position check off by
  one (E9, E13 ×3). This is not exotic — `-C`/`--work-tree` are ordinary, common invocations (the
  repo's own `gate()` test helper and `local_branch()` inside merge-gate.py itself use `git -C`).
- Nesting depth ≥ 3 wraps of `bash -c` (4 literal `bash -c` layers) evades `nested_merge`'s depth cap
  by design (E11, confirmed ALLOW); 3 layers is still caught (E12, confirmed DENY) — the cap is real
  and working exactly as coded, just evadable with one more wrap.
Confirmed pre-existing: `git diff 894adc0f^ 894adc0f -- merge-gate.py` touches only `feature_for`/`main`
(lines 95-141); `words`/`is_bin`/`direct_merge`/`gh_merge`/`git_merge`/`nested_merge`/`merge_ref` are
byte-identical across the pin. Not part of this diff's regression, but live today and squarely within
the dispatch's ask to characterize evasion.

## Enumeration — axes and reachability

| # | Axis | States exercised | Result |
|---|---|---|---|
|1|command form|`git merge`, `gh pr merge`, non-merge (`git status`)|non-merge → return early, untouched (existing green test)|
|2|remote read (gh)|succeeds (fake `gh`), fails (`/nonexistent/gh`)|both combined with every axis-4 state above (GH1/GH2)|
|3|branch matched by usable record|yes / no|see A-series (no-match) vs B-series (match)|
|4|branch's own record|healthy dict / non-dict / unparseable / absent|A7-A9, B2-B4|
|5|foreign unusable record elsewhere|yes/no, ×20 at once|A2-A4, A11 — never influences a healthy or no-record branch|
|6|receipt state on matched record|held/owed/era-exempt/repo-unpinned/plan-unevaluable|B1 (sanity), B7, B8 — all fail closed as signed|

**Unreachable, with reason:** era-exempt spoofing (`feature_schema.BUILD_ENTRY_ERA_EXEMPT` is a fixed
set baked into `feature_schema.py`, not attacker input — no combination of `tool_input.command` or
`feature.json` content changes membership); untrusted-`ROOT`-changes-import (`sys.path.insert(0,
os.path.dirname(__file__))` uses the script's own directory, never `ROOT`/`sys.argv[1]` — structurally
disconnected, confirmed by reading merge-gate.py:10 against the code that consumes `ROOT`, which is
only `glob.glob` and the `harness.json` open); `GH_BIN`-redirection-as-command-input (it is an
environment variable read once by the hook process, never derived from `tool_input.command` text — a
Bash command cannot set the hook's own env before the hook that intercepts it runs).

**Assessed and dismissed:** secrets/token exposure in stderr/deny text — no message embeds `GH_BIN`,
tokens, or raw `gh` credential text; `gh_head`'s echoed first line is a `gh` CLI human error string
(e.g. process-not-found), not credential material. `os.path.realpath(feat_dir)` in operator-facing
messages — discloses an absolute local path, but the recipient is the same actor whose own `cwd` is
inside that tree, so no privilege gain (P-02). `origin/` prefix stripping — correct and single-level
only (double-prefixed branch names don't collapse twice; no realistic branch is literally named
`origin/origin/...`, so this is not a finding).

## Severity

- **high** — self-corruption bypass (B2), confirmed regression at this exact pin vs. parent.
- **high** — branch-field spoofing, both directions (bypass B9, DoS A14) — pre-existing, live, never
  previously reviewed by cycles 0/2/3/4/5.
- **high** — command-string structural blindness (env-var/eval indirection, git flag-value evasion) —
  pre-existing, live, zero-sophistication reachable via ordinary git idioms.

None reach critical: this is a local git-workflow guard, not a remote-facing or credential-handling
surface.

## Corrections/confirmations against the record supplied

Cycle 5's sentinel is confirmed gone (read + executed). The four validator-lead-verified scenarios
reproduce as stated. The "signed policy" fail-closed claims (era exempt fires only on a real match;
repo-unpinned denies; plan.yaml-unevaluable denies) all reproduce (B1, B7, B8).
