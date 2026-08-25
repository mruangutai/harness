# DESIGN — FEAT-40 The harness writes Done

**Scope: the operator-facing command surface only.** This feature has no graphical surface and
**no prototype is required** (the gate is at the end of this document, and it is derived here, not
inherited from FEAT-19). What is designed is the text a human reads at a terminal — `ship`'s two
new report lines, `abandon`'s confirmation flow, the Bash gate's refusal, and `INV-31`'s two
violation lines — because this project already treats that text as a designed artifact, with its
grammar centralized in `gh-sync.py`'s `skip`/`die`/`refuse` helpers (`gh-sync.py:103-121`) and its
stream and exit rules in that module's docstring (`gh-sync.py:40-57`).

**Measured statements cite a file and line. Everything else is a contract on code that does not
exist yet** and is marked as such. No sentence here is a measurement of the post-change tree.

## BLUF

Three findings, in the order they cost the operator:

1. **The plan's refusal text sends a finished ticket down the abandon path.** T-07's example
   refusal names `gh-sync.py abandon` as "the only sanctioned close". `abandon` closes
   `not_planned` and applies the `abandoned` label (`gh-sync.py:986-991`). An operator whose
   ticket is *done* — the common case for a hand-typed `gh issue close` — obeys the refusal and
   marks shipped work abandoned. **Contract 4 splits the refusal by intent.**
2. **`ship`'s two new lines collide with `post-merge-sweep.sh`'s positive-signal gate.** That
   gate greps the combined stdout+stderr for the literal `gh-sync: SKIP`
   (`post-merge-sweep.sh:187-194`). Neither new line may contain it. **Contract 2 pins that.**
   Whether the incomplete terminal batch should *deliberately* emit `SKIP` to reuse that gate was
   my Q1; D-11 settles it — it emits the new literal `FAILED`, and the sweep learns to read it.
3. **The plan's held-open line and its batch summary both say "not moved to Done".** T-04 step 5c
   and step 7 share that phrase, and step 7's list includes the held card. A healthy skip and a
   failed write then appear in one list, separated only by a free-text parenthetical.
   **Contract 2 splits them into two lines with two literals.**

Confirmation is **not** a prompt: no script under `.claude/skills/harness/bin/` calls `input()`
(measured across every non-test `.py`), and `ship` is already invoked with captured output by
`post-merge-sweep.sh:174-177`. Contract 3 makes that structural rather than a `isatty()` check.

## Contract 1 — the prefix taxonomy new lines must join

Measured, `gh-sync.py` prints five shapes after the `gh-sync: ` prefix:

| Shape | Meaning | Exit | Cite |
|---|---|---|---|
| `SKIP — ` | environmental no-go, nothing written | 0 | `:104` |
| `ERROR — ` (em dash) | caller error, the dispatch is wrong | 1 | `:110` |
| `REFUSED — ` | a value failed validation | 2 | `:118` |
| `ERROR - ` (hyphen), stderr | one card's write failed, run continues | 0 | `:245, :838, :941, :953, :959` |
| bare | progress | 0 | `:243, :836, :939` |

The two `ERROR` spellings carry different exit semantics under one word. That is undesigned and
this feature must not widen it: **no new line may spell `ERROR` a third way, and no new line may
use `SKIP` or `REFUSED`** (contract). A roll-up needs its own token — see Contract 2.

## Contract 2 — `ship`'s two reports, and why they must not read alike

**The hard constraint, measured:** `post-merge-sweep.sh:192` treats the substring `gh-sync: SKIP`
anywhere in `ship`'s combined output as proof the terminal status was not recorded, and declines
the worktree removal (`:193`). **Neither new line may contain that substring** (contract).

**The held-open line** (SC-02, T-04 step 5c) — deliberate, correct, and printed on stdout:

```
gh-sync: HELD — #728 waiting on open child #830 (not at Done)
```

A child absent from the board and a child with a null station both produce this same line
(D-03); the parenthetical reads `not on the board` for the absent case, so the operator can tell
an unstationed child from a stationed one without a second command.

**The batch summary** (SC-02's sibling, T-04 step 7) is **two lines, never one merged list**:

```
gh-sync: HELD 2 of 15 — #728 (child #830), #830 (child #831)
gh-sync: FAILED 1 of 15 — #822 did not reach Done and nothing downstream reports it
```

| Rule | Why |
|---|---|
| `FAILED` appears only for a write failure, never for a held card | held is correct behaviour; a word shared with failure teaches the operator to ignore it |
| the `FAILED` line is printed **only** when something failed | its presence is the signal — the operator greps one literal, not a count |
| the `HELD` line is printed whenever anything is held, even if nothing failed | a parent that did not land is news whether or not it is a fault |
| neither class occurred → the plan's own line, unchanged: `gh-sync: every recorded card is at Done` | |
| `FAILED` is a new token, not a reuse of `ERROR - ` | the per-card `ERROR - ` line already fires N times per run; a roll-up under the same word is unfindable in the merge output it is buried in |

The per-card cause stays where it is: one `gh-sync: ERROR - ` line on stderr per failed write
(`gh-sync.py:838` precedent). The summary names *which cards*, not *why* — the why is above it.

This is the whole answer to "are items 1 and 2 distinguishable in a real run": by literal
(`HELD` vs `FAILED`), by presence (`FAILED` only on fault), and by grep.

## Contract 3 — `abandon` asks by argv, never by prompt

**Measured:** no script in `.claude/skills/harness/bin/` calls `input()`; every `sys.stdin` read
there is a whole-stream `read()` of piped data (`expertise-merge.py:205`, `plan-merge.py:359`,
`observations-merge.py:153`, `context-watch-hook.py:46`, `validate-digest.py:826`). A TTY prompt
would be the first in the codebase.

**Contract.** Confirmation is the `--yes` flag and nothing else. There is no `isatty()` branch,
no default-on-no-TTY, and no stdin read — the failure the operator named is designed out by
construction rather than guarded against. Specifically:

1. **Without `--yes`:** one line per write it *would* make, prefixed `gh-sync: would `, **in the
   order `abandon` performs them** — the reason comment, then each sub-issue, then the milestone,
   then the parent (`gh-sync.py:977-1008`) — so the dry run and the real run can be diffed by eye.
2. **The parent is labelled as the parent**, not listed as a bare number:
   `gh-sync: would close parent #728 (not_planned) and label it abandoned`. It is the most
   destructive item, and under this feature it closes unconditionally where it previously turned
   on `parent_origin` (`gh-sync.py:1000-1008`). The line must not let it read as one more child.
3. **One renderer, two callers** (contract): the dry-run listing and the `--yes` run print the
   same numbers in the same order from the same function. Two renderers drift, and the drift is
   invisible until it destroys the wrong ticket.
4. **The closing line** is the plan's, unchanged:
   `gh-sync: abandon is a decision the operator makes — re-run with --yes to close the issues listed above`.
5. **Non-confirmation is the default and does nothing:** zero GitHub calls, no `_record_status`,
   exit 0.
6. **`--yes` is stripped by name-search before positional parsing**, as every existing flag is
   (`gh-sync.py:1111-1145`), so `abandon --yes <dir>` and `abandon <dir> --yes` behave alike.
   Without this, the first form dies with `<dir> is not a directory` (`gh-sync.py:1155`) — a
   confusing failure at exactly the moment the operator is being careful.
7. **`--yes` on any other subcommand is a caller error** (`die`, exit 1), never silently ignored.
   A flag that silently does nothing teaches the operator it is harmless everywhere.

## Contract 4 — the gate's refusal must route by intent, not name one command

**Measured precedent:** `branch-create-gate.sh`'s deny reasons are two sentences — what is wrong,
then something runnable. `:87` says "Install it (+ gh auth login), or branch under a flow id
instead"; `:78` says "plan first, then branch"; `:85` gives the exact name form.

SC-07 requires only the substring `gh-sync.py abandon`. **A bare command name satisfies SC-07 and
still strands the operator** — worse, it strands them toward the destructive branch, because
`abandon` closes `not_planned` and labels `abandoned` (`gh-sync.py:986-991`). Contract, stricter
than SC-07 and still containing its substring:

```
Refused: the harness closes tickets by landing their card at Done, never by closing an issue.
If the work is finished, do nothing here — gh-sync.py ship writes Done at the merge and GitHub
closes the issue. If it is being dropped, run:
  python3 .claude/skills/harness/bin/gh-sync.py abandon <feature-dir> --reason-file <path> --yes
If the issue is not tracked by the harness at all, close it in the GitHub web UI; this gate
cannot tell tracked from untracked, by design.
```

Three clauses, three reasons:

- **The finished branch first**, because it is the likeliest intent behind a hand-typed
  `gh issue close`, and its answer is "type nothing" — the operator must not be routed to
  `abandon` to reach it.
- **The abandon branch is runnable, not a name.** `gh-sync.py abandon` alone is not a command an
  operator can paste; it omits the interpreter, the path, the feature dir, the mandatory
  `--reason-file` (`gh-sync.py:972`) and the new `--yes`.
- **The untracked escape**, because T-07 forbids the gate from resolving the issue number, so a
  legitimate close of an untracked issue is a false deny. T-07 accepts false denies as
  recoverable — that only holds if the refusal says how to recover.

The gate also denies `gh api ... state=closed` on issues. The same three clauses cover it; no
second refusal text (contract).

## Contract 5 — INV-31's two lines differ in subject, not only in tail

SC-08 grades two *distinct* violations. A shared sentence with a variable tail would pass a
distinctness check on the string while reading identically to a human. The contract is that the
**subject** differs — one line is about a config value, the other about a file — and each carries
its own fix, because the two are different failures: a misconfigured clone, and a damaged
checkout.

```
INV-31: core.hooksPath is <unset | "<value found>">, not .claude/skills/harness/hooks — no
        harness hook runs on this clone. Fix: git config core.hooksPath .claude/skills/harness/hooks
INV-31: .claude/skills/harness/hooks/post-merge is <missing | not executable (mode <m>)> — the
        hook path resolves but the merge sweep cannot run. Fix: restore it | chmod +x it
```

Both follow the file's measured grammar (`INV-NN: <subject> <what is wrong> — <consequence>`,
`check-state.sh:1260`), and the unreadable-git-config case follows its `CANNOT RUN` form
(`check-state.sh:1084, :1191, :1346`).

**Both go to `bad`, not `warn`** (contract, and reversible). `INV-28` is `warn` on the stated
reason that "the mirror is never a gate" (`check-state.sh:1020`). INV-31 is not a mirror fact: it
is whether the machine runs the hook that runs `ship`. After this feature the sweep is the only
caller of `ship`, so a clone without it silently stops closing tickets — the exact silence this
feature exists to end.

## The prototype gate

**`needs_prototype: false`.**

The reason is **not** FEAT-19's. FEAT-19 answered false because its surface was "one
non-interactive command with one line of output… no multi-step flow a person operates"
(`FEAT-19/DESIGN.md:131-133`). That reasoning does not survive `abandon`, which is a two-step
operated flow around a destructive act. The derivation here is different:

- **For a terminal surface the contract *is* the rendered artifact, character for character.** A
  palette and a spacing scale are not the experience of a screen — you have to see it. The exact
  strings in Contracts 2, 3 and 4 are the experience of this surface, in full. A prototype could
  add nothing a reader of those strings does not already have.
- **The flow's steps are each non-interactive.** Measured against the plan, `abandon` never reads
  stdin; the "multi-step flow" is *run a command, read a list, run it again with a flag*. There
  is no state to hold between steps, no control to operate, and nothing whose feel differs from
  its transcript.
- **The manifest's declared `conventions:` are `astryx-design-system` and `supabase`
  (`team-config.yaml:83-90, :144-150`)** — a web component substrate and a backend. Neither
  applies, so there is no design system to build a high-fidelity prototype *on*. The applicable
  design system is `gh-sync.py`'s own line grammar, which Contract 1 measures and the rest writes
  against.
- **SC-06, SC-07 and SC-11 put the real commands in the operator's hands at UAT**, on the real
  board, with the real refusal.

**Rejected:** a shell script rendering a fake `abandon` session. It would restate Contract 3 with
a `$` in front of it, could not be checked against the code, and would need to be kept in step
with the strings it mimics — a second place for the wording to drift.

**What would flip this to `true`:** an `abandon` that reads stdin. If the operator overrules
Contract 3 and wants a real y/N prompt, a prototype becomes necessary, because a prompt's
behaviour under no-TTY, under a pipe, and under the sweep's captured-output caller is not
judgeable from its text.

## Open questions

- **Q1 — answered, closed. Nothing here for the operator to decide.** *What I measured:* the
  brief's premise that a half-written terminal batch has "no gate downstream" is incomplete —
  `post-merge-sweep.sh:192-194` already declines the worktree removal when `ship`'s output
  contains `gh-sync: SKIP`, and the sweep's own comment calls the standing worktree "the only
  remaining evidence". *What I recommended:* emit `SKIP` on an incomplete batch, reusing that
  gate. *What D-11 chose:* the incomplete batch emits the new literal `gh-sync: FAILED`, never
  `gh-sync: SKIP`, and the sweep gains `FAILED` as a second condition of the same
  positive-signal gate. D-11 adopts the measurement and rejects the mechanism, and its
  `because:` supersedes my recommendation: `SKIP` is reserved for an environmental no-go where
  nothing was written, so reusing it would report a partial write as no write at all — trading
  Contract 1's one-meaning-per-token rule for the sake of not adding a literal. The worktree
  evidence I was protecting is preserved either way. Contract 2 already states the
  `HELD`/`FAILED` pair D-11 names; the sweep-side half is T-04 step 7b's.
- **Q2 (non-blocking).** `abandon`'s dry run exits 0. Nothing wraps `abandon` today (grepped:
  `gh-sync.py:9` usage and `github-mirror.md:32` prose are its only references), so no caller
  misreads 0 as "abandoned". If one is ever written, the dry run needs a distinct exit.
