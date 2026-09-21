# Checkout prerequisites — every clone of the Harness repository

Read this from `harness-init` step 1, or from `harness-add-repo`'s preflight, in the main session.
A fresh checkout of an already-onboarded Harness repository needs it as much as a fresh init does.
It is a HARD GATE: a `MISSING` you cannot clear, or a denied install, is a **stop**, not a detour.

## The two prerequisites — do this first

Enforcement under OMP is `.omp/extensions/harness-hooks.ts`, loaded with the session; nothing is
merged into a settings file (DEC-233). What a checkout needs installed is two Python packages
and the ignore rules:

```bash
.agents/skills/harness/bin/merge-gitignore.py .
python3 -c 'import yaml' 2>/dev/null && echo OK || echo MISSING          # PyYAML
python3 -c 'import jsonschema' 2>/dev/null && echo OK || echo MISSING   # jsonschema
```

**If either line prints `MISSING`, STOP.** Both packages are REQUIRED, not optional.

**PyYAML** (DEC-171): there is no line-scan fallback anywhere in `bin/`, deliberately, because
a fallback leaves the hand-rolled parser it exists to remove.

**jsonschema**: a feature's execution state is schema-checked at write time, and **a validator that
passes silently when its checker is absent is a gate that looks real and does nothing.**

Print this for the user to run, then re-check:

```
python3 -m pip install pyyaml jsonschema
# only one of them missing? then just the one, e.g.:
python3 -m pip install jsonschema
# if either fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml jsonschema
```

Quote the command from `harness_yaml.INSTALL_COMMAND` (D-07), never retype it. This shell check is
advisory — the write hooks self-report `MISSING` from their own environment; `check-domain.py` is
authoritative.

**If the packages cannot be installed, STOP HERE and tell the user.** A half-installed init looks
finished but has no domain enforcement, which is worse than a refused one (observed in testing).

Enforcement is live **immediately, in this session** — `harness-hooks.ts` is loaded with the OMP
session and its wiring is graded by `check-omp-port.py` on every run. Nothing here waits on a
restart.

## The per-checkout step: point git at the tracked hooks directory

**This is NOT a third prerequisite and the count above does not change.** The two are packages a
checkout needs importable. This one is a git config a checkout carries, so a fresh checkout of an
already-onboarded Harness repository still needs it and the packages will already be in place.

**Why:** git ignores the tracked `post-merge` hook at `.claude/skills/harness/hooks/` until
`core.hooksPath` points at it, and an absolute value (what this checkout had) is clone-specific.
A relative path resolves against the repository root in every clone.

Run these three checks in order. Do not skip the hooks configuration.

```bash
# 1. Read what is there. Exit 1 means unset, which is normal — tolerate it.
git config --get core.hooksPath || echo "(unset)"
```

**2. Unset, or already `.claude/skills/harness/hooks`?** Set it, and say which of the two you
found:

```bash
git config core.hooksPath .claude/skills/harness/hooks
git config --get core.hooksPath      # must print .claude/skills/harness/hooks
```

**The path is RELATIVE, deliberately.** Running this step twice leaves the same value and is not
an error.

**3. Set to ANYTHING ELSE? STOP and ask the user before writing.** Print the value you found, tell
them it is a hooks directory the harness did not write, and tell them what pointing git at the
harness directory will do to it:

> `core.hooksPath` takes over hook resolution for the **whole clone**, not for one hook. Every hook
> git looks for is resolved in the directory it names, and the previous directory is bypassed
> entirely. So every hook currently resolved from `<the value you found>` stops running.

**Never overwrite an operator's own hooks path silently.** If they agree, their hooks must move
into `.claude/skills/harness/hooks/` or they stop firing — say that too, rather than leaving them
to discover it at the next merge.

A clone that skips this is caught: `check-state.py` INV-31 reports an unresolvable `core.hooksPath`
and a missing or non-executable `post-merge` on every run. Without the hook the post-merge sweep
never fires and (DEC-203) nothing runs `ship`.
