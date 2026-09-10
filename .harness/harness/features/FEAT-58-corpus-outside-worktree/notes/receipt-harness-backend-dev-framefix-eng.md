Two rulings closing goal-check Q1 (REQ-05 frame honesty in the relocated sweeps) and G-6 (the second
corpus enumeration in `check-domain.sh`). Both are plan-only; nothing executed. D-11, D-12 and T-01's
three-function surface are unchanged inputs, re-verified as still consistent with each ruling below.

## Ruling 1 — REQ-05 frame: TWO frames, never merged into one line

**DECISION:** the completeness gate stays exactly as D-12 already fixes it —
`corpus_features(root)` (provider defaults to `history`, at the resolved ref) — unchanged, once, before
any content read. What changes is that T-03/T-04 record **two separate frame lines**, never one:
1. **enumeration frame** — `provider=history, ref=<resolved ref>` — what the completeness gate used.
2. **content frame** — `provider=path, base=<root>` — what every subsequent read actually consulted.
When D-12's cwd union added the active in-flight feature to this run's scope, the content frame **names
that feature and its distinct base explicitly**, e.g.
`provider=path, base=<root> (default); <feature-id>: base=<cwd>` — never a single aggregate
`base=<root>` line, which would silently misattribute that feature's bytes to the owner root when they
in fact came from a different checkout entirely. A frame line that covers a cwd-sourced member without
saying so is the exact defect REQ-05 exists to prevent, one layer down from the sweep it names.

**REJECTED: (a) one frame, `provider="path"` for both the completeness gate and the content read.**
`corpus_features(root, provider="path")` lists directories materialised **under `root` itself** — it has
no independent "what should be there" side to compare against (T-01's own signature forbids passing a
`ref` in path mode, because path enumeration is ref-independent by construction). Replacing the
completeness gate's history call with this collapses the compare to root-against-itself: it is trivially
"complete" every time, because both sides of the comparison are now the same on-disk listing.
**Concrete failure:** a migration script mistargets the owner root and sparsifies it to 1 of 88 feature
directories — under path-only completeness `corpus_features(root, provider="path")` enumerates just the
1 present directory as the whole known set and reports "1 of 1," never refusing. This is precisely the
corruption case T-01's case (C) / REQ-04 / SC-04 exist as a last-line defence against (`plan.yaml`
T-01 intent, case (C)), and it also strands T-08 (c)'s set-equality assertion, which is stated against
the owner root's **default-branch** set — a history-relative comparison that a path-only call cannot
reproduce.

**D-12 consistency, restated (fixed, not reopened):** the union is still spelled exactly per the
planfix-eng receipt's item 2 cycle-3 amendment — computed at the caller against the caller's own
`os.getcwd()`, beside the top-level `corpus_features(root)` gate, feeding a `bases: dict[str, Path]`
built once (`root` for every ref-resolved name, `os.getcwd()` for the single in-flight name the union
adds). This ruling adds nothing to *when* or *how* that union runs — only to what the run's printed
output states about it.

**Paste-ready wording for pm:**

- **T-03** (`plan.yaml:277`) — replace the sentence "Record the frame (provider and ref) once in the
  run's output so a recorded sweep states what it read (REQ-05)" with:
  > "Record TWO frame lines in the run's output, never one collapsed line: (1) the ENUMERATION frame —
  > `provider=history, ref=<resolved ref>` — naming what the top-level `corpus_features(root)` gate used,
  > unchanged by this task; and (2) the CONTENT frame — `provider=path, base=<root>` — naming that every
  > subsequent read came from the owner root's on-disk working tree. When the D-12 cwd union added the
  > active in-flight feature to this run's scope, the content frame additionally names that feature by id
  > and its distinct base explicitly, e.g. `provider=path, base=<root> (default); <feature-id>:
  > base=<cwd>` — never a single aggregate base line that would silently attribute that feature's bytes
  > to `root`. This discharges REQ-05: the completeness gate's history frame and the content read's path
  > frame are never merged into one line."

- **T-04** (`plan.yaml:356`) — identical wording, applied per module ("each module records..."), AND add
  `REQ-05` to T-04's `traces:` list (`plan.yaml:358` currently reads
  `[REQ-03, REQ-04, SC-04, SC-05, SC-09]`, omitting REQ-05 even though its four validators are the same
  relocated-sweep shape as T-03 and goal-check Q1 names T-04 as a co-owner). Paste the same block as
  T-03's, substituting "each module" for "the script."

- **T-05, T-12: unaffected, explicitly.** T-05 is not relocated (D-11) and calls `corpus_read(path, ref)`
  directly — its enumeration and its content read are the *same* call at the *same* ref, so there is
  only ever one frame and no merging risk. T-12 performs no corpus read at all (prior ruling, item 4).
  Neither task's intent needs a paste.

- **`BRIEF.md` REQ-05** (`:63-64`) — optional strengthening, not required to close Q1, but named since the
  dispatch asks: append one sentence after the existing text —
  > "A sweep that uses more than one provider in the same run (for example a history-backed
  > completeness gate alongside a path-backed content read) states each frame on its own, naming the
  > base each provider actually used; one merged line covering two different reads is auditable as
  > neither." SC-05 (`:130-133`) needs no change — it governs the unresolvable-corpus refusal path, not
  > frame recording, and this ruling does not touch that path.

## Ruling 2 — `check-domain.sh`'s `SWEEP_GLOBS`: CONVERT under T-06

**Anchors re-verified this run:** `_SWEEP_PATTERNS` (`check-domain.sh:1052-1062`, six literal strings —
`CLAUDE.md` plus five `.harness/*/features/*`-shaped patterns), aliased `SWEEP_GLOBS` at `:1069`,
consumed at `:2147` (`root`) and `:2150-2151` (`linked_worktrees(root)`, each linked worktree). Existing
`_hardlink_plan` glob at `:1916` (T-06's own conversion target, called from `:1947` inside `_plan_route`
and from `:2105`'s `next(...)` chain).

**DECISION: CONVERT, folded into T-06 (`plan.yaml:476`) — same file, same mechanism, one task, not a
second.** T-06 already computes `harness_boundary.corpus_features(harness_boundary.corpus_root(root),
provider="path")` once for `_hardlink_plan`; the Bash-route sweep (`else:` branch, `:2118-2154`) reuses
that identical call — computed once per invocation, in whichever branch runs, never twice — to get the
sorted feature-name list, and builds the five `_SWEEP_PATTERNS` suffixes (`feature.json`,
`runs/*/state.yaml`, `notes/handoff-*.md`, `STATE.md`, `plan.yaml`) as **relative-to-a-known-feature-dir**
constants joined per name, instead of a literal `.harness/*/features/*` wildcard string. `CLAUDE.md`
stays a literal single-file check — it is the one non-corpus pattern in `_SWEEP_PATTERNS` and this
ruling does not touch it. `runs/*/state.yaml` and `notes/handoff-*.md` keep their own inner wildcards
(they enumerate runs/handoffs *within* one already-named feature, never the FEATURE position itself, so
T-13's lint — "a wildcard in the FEATURE position" — does not trip on them either).

**`root` for this hook-bound script:** unchanged in meaning — `root` still comes from `_root()`
(`resolve_root`, env-aware) exactly as today, and the per-checkout loop still iterates `root` itself plus
every entry `linked_worktrees(...)` returns; that mechanism is orthogonal to feature enumeration and is
not what changes. What does change: the bare `linked_worktrees(root)` call at `:2150` is corrected to
`linked_worktrees(harness_boundary.corpus_root(root))` — reusing the SAME `owner_root` value already
computed once for the feature-name lookup, rather than assuming `root` already is the owner (the same
robustness T-06 already applies for `corpus_features`). **The worktree tier at `:2149-2151` SURVIVES,
unsubsumed and unreplaced** — it enumerates *checkouts* via git's own worktree pointer files, an
orthogonal axis to *which features exist*, which is now enumerated via the API. Losing it silently
would reopen the exact 38-file regression the `:1044-1051` comment records; this ruling keeps it and
only strengthens its root argument.

**REJECTED: exempt `check-domain.sh` in T-13's allow-list.** No cost or correctness argument survives:
the measurement below shows conversion is free-to-negative, and this file is hook-registered and
already NOT allow-listed for `_hardlink_plan` — a second enumeration two hundred lines below the first
one T-06 already converts, left un-converted, is the identical fail-open class T-13 exists to close, one
call-site over. `planfix-eng` item 5 already refused to allow-list this file for the same reason.

**MEASUREMENT** (`/tmp/measure_sweep2.py`, this repo's real corpus — `.harness/harness/features`, 88
feature directories, 100 samples per approach, glob vs. API-plus-per-feature-join, one representative
checkout):

```
$ python3 /tmp/measure_sweep2.py
corpus size: 88 features
current (5x glob.glob over .harness/*/features/*/<suffix>): 5.6278 ms/checkout, 100 samples
converted (corpus_features path-provider once + per-feature join): 5.4527 ms/checkout, 100 samples
delta per checkout per invocation: -0.1751 ms
```

Converted is **0.175 ms faster per checkout**, not slower — the five independent `glob.glob` traversals
of `.harness/*/features/*` (fnmatch overhead, five separate directory walks) cost more than one
`os.listdir` plus per-name `os.path.exists`/small globs. Scaled by checkout count (owner + N linked
worktrees, per `linked_worktrees`' own measured `+0.22 ms`/call), the total remains a net wash against
the ~38 ms interpreter start-up the hook already pays on every write. State the number even though it is
negligible: **-0.18 ms/checkout, N=100, corpus size 88**, command `python3 /tmp/measure_sweep2.py`
(script not committed — throwaway, `/tmp` only, nothing executed against the tree).

**Not reopened:** D-11 (this file stays hook-bound, not relocated), D-12 (cwd union, unrelated to this
enumeration), T-01's three-function surface (this ruling calls exactly `corpus_root` and
`corpus_features`, provider `"path"`, no ref — the same two functions and the same call shape T-06
already specifies for `_hardlink_plan`).

## Open questions
None blocking. One non-blocking note for pm: T-04's `traces:` list is missing `REQ-05` (see Ruling 1);
folding Ruling 2 into T-06 needs no `traces:` change since T-06 already carries `REQ-03, REQ-04, SC-04,
SC-09` and this ruling adds no new requirement, only closes G-6 against the existing ones.
