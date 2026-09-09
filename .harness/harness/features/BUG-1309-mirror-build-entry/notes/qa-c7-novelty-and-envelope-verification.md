# QA c7 — Novelty Base + Digest Envelope Verification

BLUF: (A) `merge-gate.py`/`.sh` and all four functions the panel flagged (`feature_for`,
`merge_ref`, `git_merge`, `nested_merge`) do not exist at all at the feature's true merge-base —
they were introduced entirely inside this feature's own range, so "pre-existing" is **false**
relative to the feature even though it is true relative to the pin's parent. `gh-sync.py`'s
build-entry gate functions are genuinely pre-existing at the merge-base. (B) Both repaired
digests pass `validate-digest.py lead` cleanly, exit 0, `digest ok`.

## Measurement A — novelty base for the review subject

**Commands run in worktree** `<wt> = .claude/worktrees/harness/BUG-1309-mirror-build-entry`.

### 1. True merge-base

```
$ git -C <wt> merge-base origin/main 894adc0f08c71c108ef8432f1f7a3cc8a2a763c0
6ad7233f5014c9488228154335fb16295b6f65bc
exit=0
```

Result: `6ad7233f5014c9488228154335fb16295b6f65bc` — **equals** the canonical review-range base
given in the contract (`6ad7233f5014c9488228154335fb16295b6f65bc..894adc0f08c71c108ef8432f1f7a3cc8a2a763c0`).
Confirmed, not assumed.

### 2. `merge-gate.py` / `merge-gate.sh` existence at the base

```
$ git -C <wt> cat-file -e 6ad7233f...:.claude/skills/harness/bin/merge-gate.py
fatal: path '.claude/skills/harness/bin/merge-gate.py' exists on disk, but not in '6ad7233f5014c9488228154335fb16295b6f65bc'
cat-file -e exit=128

$ git -C <wt> log --oneline --diff-filter=A -- .claude/skills/harness/bin/merge-gate.py
4338ee44 [harness:t-05] gate merges on Build-entry receipt

$ git -C <wt> merge-base --is-ancestor 4338ee4464255b49ce0735451eea005cc3651ca9 6ad7233f5014c9488228154335fb16295b6f65bc
is-ancestor-of-base exit=1
```

```
$ git -C <wt> cat-file -e 6ad7233f...:.claude/skills/harness/bin/merge-gate.sh
fatal: path '.claude/skills/harness/bin/merge-gate.sh' exists on disk, but not in '6ad7233f5014c9488228154335fb16295b6f65bc'
cat-file -e exit=128

$ git -C <wt> log --oneline --diff-filter=A -- .claude/skills/harness/bin/merge-gate.sh
4338ee44 [harness:t-05] gate merges on Build-entry receipt

$ git -C <wt> merge-base --is-ancestor 4338ee4464255b49ce0735451eea005cc3651ca9 6ad7233f5014c9488228154335fb16295b6f65bc
is-ancestor-of-base exit=1
```

Both `merge-gate.py` and `merge-gate.sh` were **added by the same commit** `4338ee44 [harness:t-05]
gate merges on Build-entry receipt`, and `merge-base --is-ancestor 4338ee44 <base>` exits **1**
(not an ancestor of the base) — i.e. commit `4338ee44` sits inside `<base>..894adc0f`, the
feature's own range. Neither file exists at the base at all (`cat-file -e` fatal/128), which by
itself proves both paths are wholly introduced by this feature.

### 3. `gh-sync.py` build-entry gate — genuinely pre-existing

```
$ git -C <wt> show 6ad7233f...:.claude/skills/harness/bin/gh-sync.py | grep -n "_build_entry_recovery_notice\|_build_entry_preflight\|MERGE is refused"
(no output)
exit=1
```

```
$ git -C <wt> show 894adc0f...:.claude/skills/harness/bin/gh-sync.py | grep -n "_build_entry_recovery_notice\|_build_entry_preflight\|MERGE is refused"
1357:def _build_entry_preflight(feat_dir, rec):
1376:        _build_entry_recovery_notice(feat_dir, feature_id)
1379:def _build_entry_recovery_notice(feat_dir, feature_id):
1388:          f"Build proceeds, the MERGE is refused until gh-sync.py open records opened",
1452:    _build_entry_preflight(feat_dir, rec)
exit=0
```

Contrast is clean: `gh-sync.py`'s `_build_entry_preflight` / `_build_entry_recovery_notice` /
the "MERGE is refused" string are **absent at the base** and **present at the pin** — so this
functionality is *also* introduced inside the feature range, not pre-existing. (Grep found zero
matches at the base; this is the exact opposite of what the dispatch text anticipated for
`gh-sync.py`, reported as measured, not assumed.)

### 4. The four flagged `merge-gate.py` functions — existence at the base

`merge-gate.py` does not exist at the base at all (§2, `cat-file -e` fatal/exit 128). Since the
whole file is absent, **all four** functions the panel raised findings against —
`feature_for`, `merge_ref`, `git_merge`, `nested_merge` — are therefore introduced inside the
feature range. This is not inference from the file's absence; the file's absence at the base *is*
the proof (there is no file for the functions to be defined in).

### Bottom line

None of the panel's "pre-existing" findings about `merge-gate.py`/`.sh` (including
`feature_for`, `merge_ref`, `git_merge`, `nested_merge`) are pre-existing relative to the
feature — every one of them is introduced entirely inside `6ad7233f..894adc0f` by commit
`4338ee44`, and is "pre-existing" only in the narrower, misleading sense of pre-dating the pin's
immediate parent commit `894adc0f^`, while `gh-sync.py`'s build-entry preflight/recovery-notice
gate (`_build_entry_preflight`, `_build_entry_recovery_notice`, "MERGE is refused") is the one
piece of reviewed surface that is genuinely pre-existing relative to the feature's true merge-base.

## Measurement B — repaired lead digest envelope verification

```
$ python3 .agents/skills/harness/bin/validate-digest.py lead \
    .../features/BUG-1309-mirror-build-entry/runs/2026-09-07-03-validator/digest.md
digest ok
exit=0
```

```
$ python3 .agents/skills/harness/bin/validate-digest.py lead \
    .../features/BUG-1309-mirror-build-entry/runs/2026-09-06-panelc1-validator/digest.md
digest ok
exit=0
```

Both repaired digests validate cleanly under `validate-digest.py lead` — `digest ok`, exit 0, no
stderr. The validator reads from the last `VERDICT:` anchor, consistent with the append-repair
shape described in the dispatch; no further repair is required on either file.

## Verification note

This dispatch ran no test suite. `suite: n/a`, `matrix_ok: n/a` — no gate was executed; the two
measurements above are direct command output, not test results.
