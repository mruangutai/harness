# UI Review — FEAT-05-pyyaml-file-parsers — c1 — Q4 retraction audit

**VERDICT: PASS (scoped out; Q4 adjudicated as a courtesy read, not a gate)**

## Step 0 — required, verbatim

```
$ git rev-parse HEAD
924b961ad626b79c8810a9de7ae420ccc634e4fd
$ git status --porcelain
(empty — clean)
$ git log --oneline 340e18a..9da3986
9da3986 docs(brief): Q2 ruled a pinning error — the non-goal stands (Amendment 2)
20b5af3 fix: the panel's mediums and five of six open questions (F-04, F-05, Q1, Q3, Q4, Q6)
bb6ab8c fix(bin): the three high findings from the review panel (F-01, F-02, F-03)
d727870 chore(state): re-pin review_sha to 340e18a for the review panel
```

HEAD is **924b961**, one commit past the dispatch's stated `9da3986` — `git log 9da3986..HEAD`
shows only `924b961 chore(state): re-pin review_sha to HEAD for the fix re-review`, a state re-pin,
not a code change (`git merge-base --is-ancestor 9da3986 HEAD` → yes). Tree clean. Not treated as a
blocker for this task; flagged per instruction.

## Assignment 1 — Q4: is the retraction sound?

**VERDICT: RETRACTION SOUND on the mechanism; the receipt's stronger clause ("the ui-reviewer's
inference is wrong") overreaches what its own evidence proves.**

### What the dispatch's prior got wrong, checkably

The prior argued the receipt's 15-fire probe tested only "the project dir as resolved inside an
already-running script" and never tested "which binary settings.json invoked." That is incorrect —
the receipt (`notes/receipt-main-session-hook-resolution-probe.md:97-103`) reports **two** separate
measurements per fire: `file = __file__` (worktree path, all 15 fires) **and** `cpd` (sometimes
unset). `__file__` inside a directly-exec'd script (no `python3` prefix in the settings.json command
— it runs on its shebang) *is* the invoked-binary identity, not a proxy for it; a wrong binary having
run would show up as a different `__file__`, not a merely-unset env var. This is the exact
discriminator the prior said was missing. The prior conflated the `file` and `cpd` rows.

### Independent, read-only re-verification (not taking the receipt's self-report on faith)

1. **Command-path template is identical across checkouts and has no third registration.**
   Worktree `.claude/settings.json:SubagentStop` and main checkout's both read
   `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/validate-digest.py --hook` verbatim. User-level
   `~/.claude/settings.json` has no `SubagentStop` entry at all (checked its `hooks` key directly).
   No stray third hook could have fired.

2. **DEC-173 was already in the worktree's file at the pinned review commit**, not added later:
   `git show 340e18a:.claude/skills/harness/bin/validate-digest.py | grep DEC-173` returns the
   `NULLABLE`/`GATE_FIELDS` block. So there is no "worktree hadn't caught up yet" alternative
   explanation for old-schema behaviour — if the worktree copy ran, at any point since 340e18a,
   DEC-173 was in force.

3. **Ran the actual functional discriminator myself, read-only, no subprocess needed** —
   `validate("reviewer", text)` is an importable function. Fed an in_scope:false /
   `severity_max: n/a` digest shaped exactly like my own c0 return to both copies:

   ```
   worktree .claude/skills/harness/bin/validate-digest.py  -> []                (accepts)
   main     .claude/skills/harness/bin/validate-digest.py  -> ["severity_max='n/a' is not in
                                                                ['critical', 'high', 'info',
                                                                 'low', 'med']."]   (rejects)
   ```

   This is the live discriminator: a `severity_max: n/a` scoped-out reviewer digest **is** the
   exact symptom a rejection under the main checkout's schema would produce, and it is the only
   plausible mechanical source of the observation attributed to me in
   `runs/2026-08-03-01-validator/digest.md:36` (Q4's text). Combined with (1) file identity always
   resolving to the worktree and (2) DEC-173 already present there at 340e18a, **the operative
   conclusion — DEC-173's schema is in force for a reviewer spawned in this worktree at
   `SubagentStop` — is now solidly supported**, independent of the receipt's own self-report.

### Where the receipt overreaches

- Its own SubagentStop probe (`receipt-...:93-96`) spawned a throwaway `harness-documentor`
  returning "a well-formed digest" — not a reviewer digest carrying `severity_max: n/a`. It proved
  file identity, not the specific functional symptom. I closed that gap myself above (point 3);
  the receipt did not.
- The CPD-unset-in-SubagentStop finding is real and useful (matches
  `validate-digest.py:597,621`'s documented `payload.cwd`→env→`os.getcwd()` fallback), but the
  receipt itself only says this is "**plausibly**" what I noticed and mis-attributed
  (`receipt-...:112`) — an honest hedge. The digest text the panel will read states flatly "the
  ui-reviewer's inference is wrong," which is stronger than "plausibly." **That specific causal
  claim — CPD-unset explains what I saw — remains unverified**, separate from the mechanism claim
  above, which is now well-supported.
- **My own c0 artifact (`notes/review-harness-ui-reviewer-c0.md`) contains no mention of this
  observation at all**, and no `observations/harness-ui-reviewer.md` file exists for this feature
  (checked; only `harness-backend-dev.md` is present in `observations/`). Whatever I said live is
  unrecoverable from any durable source. Q4 entered the panel digest citing a member observation
  the member never wrote down — that is a record gap, not evidence either way, and it means "the
  ui-reviewer's inference is wrong" cannot be fully confirmed as stated (there is nothing left to
  compare it against) even though the underlying mechanism is now settled.

### Net

State the replacement plainly, for the record the panel is about to close on: **the binary
identity and schema-in-force question is settled (worktree runs, DEC-173 applies) — treat that as
closed. The specific claim that I inferred main-checkout-execution and that CPD-unset explains why
is neither confirmed nor refutable from any durable record, and should not be written up as a
settled fact.** Amendment 2 holding for `SubagentStop` does not depend on resolving that part.

## Assignment 2 — re-scope

`git diff --stat 340e18a..9da3986` (19 files, 1309+/56-): `bin/` scripts (`harness_yaml.py`,
`check-state.sh`, `gh-sync.py`, `upgrade-config.py`, `run-unit-tests.sh`), their test files,
`.harness` feature process artifacts (BRIEF/feature.yaml/notes/receipts), `team-config.yaml`. No
HTML/CSS/component/`DESIGN.md`. **`in_scope: false` still holds.**

The one candidate operator-facing surface introduced by this range is F-01's fix
(`harness_yaml.py:92-137`, widening `load_str`/`load_file` to catch `UnicodeDecodeError`/`OSError`
and route them into `YamlParseError`). Read the two call sites that render it to an operator:
`check-domain.sh:153-158` (manifest) and `check-domain.sh:320-324` (state.yaml) — both print a
named cause (`e.original`, carrying the underlying `OSError`/`UnicodeDecodeError` text), the
consequence (closed/blocked, not partial), and at least one site names the remedy and owner ("Fix
the file (the main session owns it), then retry."). Consistent with the clear-messaging standard
already confirmed in c0 for the bootstrap-escape path. No new finding.

## Handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: "Q4 retraction is sound on the mechanism (worktree's validate-digest.py runs at SubagentStop, DEC-173 in force — verified directly by running validate() against both copies with a severity_max:n/a reviewer digest) but the receipt's 'the ui-reviewer's inference is wrong' clause overreaches: my c0 artifact has no record of the original observation, so it can be neither confirmed nor refuted. in_scope false stands; F-01's new operator-facing messages are clear."
  mode: B
  in_scope: false
  severity_max: n/a
  findings: 0
  must_fix: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q4-followup, question: "Q4's digest text states 'the ui-reviewer's inference is wrong' as settled, but no durable artifact (c0 note, observations log) records what the ui-reviewer actually observed or why. Recommend the panel record: mechanism settled (worktree runs, DEC-173 in force, confirmed independently here) / causal attribution (CPD-unset explains the original claim) unconfirmed and unfalsifiable from any record. This is a record-keeping gap (no per-run observation captured for a live claim later cited in a gating digest), not a UI finding.", blocking: false }
  files_touched: [".harness/features/FEAT-05-pyyaml-file-parsers/notes/review-harness-ui-reviewer-c1.md"]
  expertise_update: []
artifact: .harness/features/FEAT-05-pyyaml-file-parsers/notes/review-harness-ui-reviewer-c1.md
```
