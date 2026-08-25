# T-02 probe — core.hooksPath installed, and a real merge fires the sweep

sweep_fired: yes scratch_clone=/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/scratchpad/sweep-probe merge_commit=fb3c3e34a5f06ca10e7d373e5dc5200380845e14

The merge created a real merge commit — **2 parents**, asserted, not assumed. An
"Already up to date" merge fires no post-merge hook, so a merge commit is the precondition
for the measurement meaning anything.

## Captured hook output, verbatim

```
Merge made by the 'ort' strategy.
 .sweep-probe.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 .sweep-probe.txt
post-merge-sweep: resolved repository root: /private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/scratchpad/sweep-probe
post-merge-sweep: resolved main checkout root: /private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/scratchpad/sweep-probe
```

Two `post-merge-sweep:` lines are present. That is the **first** of the two outcomes the task
allows: the shim resolved AND `post-merge-sweep.sh` executed. The shim's
"post-merge: ... is missing or not executable" line does not appear.

## core.hooksPath in the owner clone /Users/molchairuangutai/GitHub/harness

| | Value |
|---|---|
| before | `/Users/molchairuangutai/GitHub/harness/.git/hooks` |
| after | `.claude/skills/harness/hooks` |

The new value is **relative on purpose**. An absolute path is what produced the broken value,
because it pins one checkout's location into config that every worktree inherits.

## Listing of the old hooks directory, before the change

```
  total 128
  drwxr-xr-x  16 molchairuangutai  staff   512 Apr  4 19:34 .
  drwxr-xr-x  16 molchairuangutai  staff   512 Aug 25 12:07 ..
  -rwxr-xr-x   1 molchairuangutai  staff   478 Apr  4 19:34 applypatch-msg.sample
  -rwxr-xr-x   1 molchairuangutai  staff   896 Apr  4 19:34 commit-msg.sample
  -rwxr-xr-x   1 molchairuangutai  staff  4726 Apr  4 19:34 fsmonitor-watchman.sample
  -rwxr-xr-x   1 molchairuangutai  staff   189 Apr  4 19:34 post-update.sample
  -rwxr-xr-x   1 molchairuangutai  staff   424 Apr  4 19:34 pre-applypatch.sample
  -rwxr-xr-x   1 molchairuangutai  staff  1649 Apr  4 19:34 pre-commit.sample
  -rwxr-xr-x   1 molchairuangutai  staff   416 Apr  4 19:34 pre-merge-commit.sample
  -rwxr-xr-x   1 molchairuangutai  staff  1374 Apr  4 19:34 pre-push.sample
  -rwxr-xr-x   1 molchairuangutai  staff  4898 Apr  4 19:34 pre-rebase.sample
  -rwxr-xr-x   1 molchairuangutai  staff   544 Apr  4 19:34 pre-receive.sample
  -rwxr-xr-x   1 molchairuangutai  staff  1492 Apr  4 19:34 prepare-commit-msg.sample
  -rwxr-xr-x   1 molchairuangutai  staff  2783 Apr  4 19:34 push-to-checkout.sample
  -rwxr-xr-x   1 molchairuangutai  staff  2308 Apr  4 19:34 sendemail-validate.sample
  -rwxr-xr-x   1 molchairuangutai  staff  3650 Apr  4 19:34 update.sample
```

**Fourteen files, every one a `.sample`.** A `find` for executable non-sample files returned
nothing, so no hook the operator wrote was being bypassed and step 3's stop condition did not
apply. `.claude/skills/harness/hooks` holds one hook: `post-merge`.

## What was measured, and what it does not cover

I measured that a merge creating a commit, in a clone configured this way, executes
`post-merge-sweep.sh`. I did **not** measure what the sweep then does — that it finds a shipped
feature, or that it runs `gh-sync.py ship` correctly. T-10 measures that end to end against
FEAT-34.

The probe ran in a throwaway `--no-hardlinks` clone in the session scratchpad, never in the owner
clone and never in a feature worktree, so no real merge history was disturbed. The clone was
deleted after the capture.
