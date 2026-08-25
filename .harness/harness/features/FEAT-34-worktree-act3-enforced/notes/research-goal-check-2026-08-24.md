# Goal-check — FEAT-34, pin `513c4a46e34cbe327d96922c01cebdd18e85d62e`

**BLUF: fourteen of sixteen criteria met, one `not_met` and one `concern` — and the feature's one
shipped defect is invisible to every criterion in the signed brief.** `REQ-02` is violated in
practice (INV-29 prints a removal command that fails for a short-named worktree), yet `SC-01` and
`SC-05` are both **met exactly as written**. That is a coverage gap in the brief, not a grading
error, and it is the operator's to close. `SC-06`'s squash clause is **unsatisfiable by any
implementation** — reproduced, forced by git — so `REQ-07` is unmet on that path and the remedy is a
criterion change, never code. `SC-08` is **met**: it is `verify: automated`, not UAT, and the
dispatch premise that said otherwise does not survive the artifact.

Every automated verdict below rests on my own sole-runner run of `--kind integration` at this pin:
**exit 0**, wall clock **229s** (`3:49.12`), `ps`-verified clean before start. `check-state.sh`:
**exit 0**, zero `VIOLATION` lines, zero `INV-29`/`INV-30` findings.

---

## The criteria question — SC-01 and SC-05 are met, and REQ-02 is still violated

Both panel readings re-derived at the pin against the test source, not inherited.

- **`SC-01`'s command assertion runs on an exact-named fixture.** `test-check-state.py` group (b)
  builds `FEAT-T29` and asserts `"--id FEAT-T29" in line` (`case_inv29`, `(b.3)`). In that fixture
  the landed directory name and the worktree basename are the same string, so the two derivations
  coincide and the defect cannot appear. **SC-01 is met in full**: its literal demand is that the
  firing line carry the removal command *with the found worktree's own path substituted into it*,
  and `(b.1)` asserts exactly that, composed from the fixture path (`wt in line or
  os.path.realpath(wt) in line`) — the line does carry `(path: %s)`. SC-01 never ties `--id` to the
  path.
- **`SC-05` group (f.3) asserts firing and nothing else.** `results.append(("(f.3) …",
  len(_i29_for(out, wt_short)) == 1, …))`. The fixture is the one that *can* exhibit the bug —
  `wt_short = FEAT-SHORT`, landed dir `FEAT-SHORT-named-in-full` — and the criterion inspects no
  command text. **SC-05 is met in full**: it demands only that each of the four worktrees fires or
  stays silent, per worktree, and all four assertions do that.

**So a signed requirement has no criterion that can falsify it.** SC-01 grades command text on a
fixture where the bug is invisible; SC-05 uses the fixture where the bug is live but grades only
firing. No third criterion touches the command. The four defect links re-derived independently at
the pin — `worktree_terminal.py:248-251,271-275`, `check-state.sh:1320-1329`,
`feature-worktree.py:56-59,207-214`, `post-merge-sweep.sh:150` — all hold as stated.

### Paste-ready: the criterion that closes it

```markdown
### Added success criterion

- SC-17: **The printed removal command must actually run.** Over the same one fixture `SC-05`
  grades — four standing worktrees, including the **short-named** worktree whose landed directory on
  the default branch is full-named and `Done` — the `INV-29` line for THAT worktree is graded on its
  command text, three clauses each asserted separately and never by one substring match: **(a)** the
  line carries a `feature-worktree.py remove` command; **(b)** the command's `--id` value is composed
  from the found worktree's OWN directory basename, asserted as an exact string built from the
  fixture's worktree path and NOT from the landed directory name — the two differ in this fixture and
  are identical in every exact-named one, which is why this criterion names the short-named worktree
  specifically; **(c)** running the printed command verbatim exits 0 and that worktree is gone
  afterwards. **Red proof, demonstrated failing before the fix:** an implementation composing `--id`
  from the resolved landed feature id passes (a), passes every clause of `SC-01` and every clause of
  `SC-05`, and fails (b) and (c) — `feature-worktree.py remove`'s GATE 1 exits 3, "not a linked
  worktree". This is also `D-02`'s guarantee stated as a criterion: `post-merge-sweep.sh:150` already
  derives the id from the record's own path, and the gate must not disagree with the hook.
  verify: automated        evidence: integration
```

---

## SC-08 — automated, met; the outstanding item is the verification gap, not the criterion

Re-derived, not inherited. `grep -in uat` over `BRIEF.md` and `plan.yaml` at the pin returns
**exactly two hits, both in `BRIEF.md`, neither a success criterion**: `:220` and `:350`, inside
`## Verification gaps` / `### Added verification gaps`. `BRIEF.md:202-205` declares SC-08
`verify: automated   evidence: integration`; `plan.yaml` T-13 (`status: done`) names
`test-hooks-install.py` as its grader.

Graded by its declared method: **met**. My sole run shows `(a) SC-08 first half: before the setup
step, core.hooksPath does not resolve to the tracked hooks directory`, `(b) SC-08 second half #1:
after the setup step, core.hooksPath resolves to the tracked hooks directory`, `(b) SC-08 second
half #2: the post-merge file there is executable` — both halves, three separate assertions.

**Which of the two is actually outstanding: the verification gap, not the SC.** `BRIEF.md:217-221`
and `:346-352` both say the same thing in the brief's own words — nothing grades whether *this
operator's own clone* ever gets `core.hooksPath` repointed, and the brief **deliberately refuses to
make it an SC** because "a fixture can fake it and this one cannot be faked". It is carried by
INV-29 plus one UAT observation at ship. The operator holds it; I make the choice legible and do not
settle it.

---

## SC-06 — unsatisfiable as written, reproduced

I reproduced the claim in a throwaway repository rather than reasoning about it. `git merge
--squash` fires `post-merge` with `$1 = 1` **while the default branch ref still points at its
pre-squash commit** — `git cat-file -e HEAD:feat/feature.json` returns non-zero at hook-fire time —
and the separate `git commit` that completes the squash **does not re-fire** `post-merge` (the hook
log holds exactly one `FIRE` entry after both). INV-29 reads the default branch's `feature.json`, so
a feature landed BY the squash is invisible when the hook runs and visible only when nothing will
fire again.

**Forced by git, not chosen.** No implementation of a `post-merge` hook can satisfy SC-06's wording
on the squash path, and `test-post-merge-sweep.py` case (b) says so in its own comment: it lands the
feature *before* the squash to decouple the shape from the timing gap. `REQ-07` is unmet on that
path. **Do not route code for this.**

### Paste-ready: amended SC-06 plus its gap

```markdown
- SC-06: In a throwaway repository the hook fires on **both** measured merge shapes — fast-forward
  (`$1 = 0`) and `merge --squash` plus commit (`$1 = 1`) — and each shape is asserted separately. On
  the fast-forward shape, the worktree of the feature **landed by that merge** is removed. On the
  squash shape, the worktree of a feature already landed on the default branch before the squash is
  removed. A feature landed BY the squash is out of the hook's reach and is covered by the
  verification gap below, never by this criterion.
  verify: automated        evidence: integration
```

```markdown
- **A feature landed by `git merge --squash` is never removed by the hook, and no implementation can
  change that.** Measured 2026-08-24 in a throwaway repository: `--squash` fires `post-merge` with
  `$1 = 1` while the default branch's ref still points at its PRE-squash commit, so the landed
  `feature.json` is not readable on the default branch at hook-fire time; and the separate
  `git commit` that completes the squash does **not** re-fire `post-merge`. `REQ-07` is therefore
  unmet on the squash path, forced by git's hook semantics rather than chosen. What carries it:
  `INV-29` refuses at the next `check-state.sh` run — the same mechanism the brief already relies on
  for every missed removal. The practical path after a PR merge is `git pull`, a fast-forward, and it
  is proven in full.
```

---

## T-10's `verify:` cannot go red

Verbatim from `plan.yaml:750`, one line:

```
for a in .claude/agents/harness-*.md; do grep -q "worktree" "$a" || true; done; grep -lc "worktree remove" .claude/skills/harness-handoff/SKILL.md .claude/skills/harness-expertise/SKILL.md .claude/skills/harness-principles/SKILL.md | wc -l
```

Run at the pin: prints `1`, **exit 0**. Four independent reasons it proves nothing — the loop's
result is discarded by `|| true` and consumed by nothing; `-l` overrides `-c` so no count is
produced; `wc -l` always exits 0 and no threshold is compared; and the file list is wrong (the rule
landed in `harness-handoff` and `harness/SKILL.md`, so `grep -l` matched **1 of 3** named files and
the command still passed). It also never resolves agent → preloaded skill, which is what SC-09
requires.

**Recommended replacement, tested green at this pin (`exit 0`, `agents=16`) and shown red when the
phrase set is unmatchable (names each uncovered agent, `fail=1`):**

```yaml
    verify: |
      fail=0; n=0
      for a in .claude/agents/harness-*.md; do
        n=$((n+1)); ok=0
        for s in $(awk "/^skills:/{f=1;next} f&&/^ *- /{print \$2;next} f{exit}" "$a"); do
          f=".claude/skills/$s/SKILL.md"
          [ -f "$f" ] && grep -qi worktree "$f" && grep -qiE "never yours|not your act|belongs to the main session" "$f" && ok=1
        done
        [ $ok -eq 1 ] || { echo "UNCOVERED $a"; fail=1; }
      done
      [ $n -eq 16 ] || { echo "expected 16 agents, saw $n"; fail=1; }
      exit $fail
```

A non-failing `verify:` is **not** acceptable here: SC-09 is `verify: inspection` quantifying over
sixteen agents, and this is the only planned artefact that could discharge it. It was in fact
discharged by two unplanned enumerations (panel and qa) plus mine.

---

## SC-09 — my own per-agent enumeration

Sixteen files under `.claude/agents/harness-*.md` at the pin, each agent's `skills:` frontmatter
parsed individually. Fifteen preload `harness-handoff`, whose `SKILL.md:82` states both halves of the
rule. `harness-orchestrator` preloads `harness` alone, whose `SKILL.md:434-437` states it
("Act 3 is never yours… Removal is not your act"). **16/16, none by a file-global count.**
Note for whoever rewrites T-10's verify: the two skills use *different wording*, so a single literal
phrase misses the orchestrator — the narrow variant `removing a worktree` returns
`uncovered=['harness-orchestrator.md']`.

---

## The stale banners — paste-ready strike

`BRIEF.md:246-247` and `:359-363` both assert "NOT YET RE-SIGNED" while `:449` records
`amendments-signed: Amendment 1, Amendment 2, Amendment 3`. Confirmed at the pin. A future
goal-check reading either banner concludes SC-11..SC-15 are unapproved.

Replace `:246-247`:

```markdown
**RE-SIGNED 2026-08-24.** The `## Approval` block below carries this amendment under
`amendments-signed: Amendment 1`. The original signature of 2026-08-23 covered the brief without it.
```

Replace `:359-363`:

```markdown
**PURELY ADDITIVE. RE-SIGNED 2026-08-24.** This amendment adds one success criterion, `SC-15`. It
changes no existing requirement, no existing success criterion and no existing verification gap; every
word of `REQ-01`..`REQ-13` and `SC-01`..`SC-14` above stands exactly as signed. The `## Approval`
block below carries it under `amendments-signed: Amendment 2`.
```

---

## REQ coverage

`REQ-01`, `REQ-03`..`REQ-06` → `worktree_terminal.py` + `check-state.sh` INV-29 (T-01/T-02/T-06/T-07).
`REQ-07`..`REQ-08`, `REQ-11` → `post-merge-sweep.sh` (T-03/T-04). `REQ-09`, `REQ-13` →
`hooks/post-merge` + `harness-init/SKILL.md` (T-11/T-12/T-13). `REQ-10` → `harness-handoff/SKILL.md:82`
+ `harness/SKILL.md:434-437` (T-10). `REQ-12` → INV-30 (T-08/T-09).

Two exceptions, both above: **`REQ-02` violated in practice** (the printed command fails for a
short-named worktree) and **`REQ-07` unmet on the squash path** (forced by git).

## Two grading residuals, recorded rather than dropped

- **SC-11's first half is not asserted.** The criterion is "the sweep **records each feature's
  terminal status** and closes each feature's milestone, asserted per feature".
  `test-post-merge-sweep.py` `case_per_feature_record` asserts the milestone close per feature
  (`milestones/801` and `milestones/802`, separately) but nothing reads the recorded status back,
  and the fixture cannot exhibit it — `_commit_feature(..., "Done", ...)` lands both features
  already `Done`, so the status write is unobservable. The milestone half is the one the brief's own
  Amendment 1 calls the fact with exactly one writer, and it is fully graded. Verdict: **concern**.
- **SC-15's "exactly one" is not literally asserted.** `by_repo = {r.get("repo"): r for r in recs …}`
  is a dict keyed by repo segment, so a duplicate record for `unenum-repo` would be silently
  collapsed rather than caught. Class and path are asserted as two separate claims, and the two red
  proofs discriminate (a) from (b), so the criterion's substance holds. Verdict: **met**, weakening
  recorded.

## Open questions for the operator

1. **Adopt `SC-17`?** Without it `REQ-02` has no criterion that can falsify it. Blocking on what
   "done" means.
2. **Adopt the amended `SC-06` plus its gap?** Blocking: as worded, SC-06 cannot be met by anything.
3. **SC-08's disposition** — the SC is met by its declared method; the operator's clone is the
   outstanding item and it is a verification gap the brief refuses to make a criterion.
4. Strike the two stale banners; correct T-10's `verify:`. Both non-blocking.
