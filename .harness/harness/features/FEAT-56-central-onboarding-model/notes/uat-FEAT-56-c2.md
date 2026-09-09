# UAT — FEAT-56 Central onboarding model (round 4)
status: ready              # draft | ready | passed | failed
branch: feat/FEAT-56-central-onboarding-model
review_sha: 8ff5197f047748f6fd791f7f9a08d3ea54b80535
covers: SC-11, SC-12, SC-15 — three separate tests, in three separate sections

Everything automatable is green at this exact commit, re-run today: unit suite exit 0, all four
door checks green, `check-omp-port.py` ok, `check-instruction-paths.py` 0 violations of 62 files,
`test-onboarding-split.py` exit 0. The integration suite exits 1 on the six `team-config.yaml`
cases you accepted as D-14, and nothing else. **This is the last gate.** Details:
`notes/research-FEAT-56-goalcheck-ship-c2.md`.

**One-time setup, 30 seconds.** Every command below runs from this one directory. Open a terminal
and paste this; nothing here clones, copies or installs anything.

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model
```

Three sections follow. **They are three different tests of three different things** — do them in
order, but a FAIL in one does not mean the others fail. Total: about 15 minutes.

---

# Section A — is `harness-init` a set-up-this-folder procedure? (SC-11, ~7 min)

**What you are judging.** One document, `.claude/skills/harness-init/SKILL.md`, 279 lines. The
question is not whether it reads well. It is: **if a brand-new copy of the harness repo sat on your
disk with nothing configured in it, is this the procedure you would run on that copy — and only on
that copy?**

Open it and keep it open. Line numbers below are this file's.

```
git show 8ff5197f:.claude/skills/harness-init/SKILL.md
```

Hold this situation in mind while you read. **You do not need to create anything.**

> A colleague has just downloaded the harness repo onto a fresh laptop. Nothing in it is set up.
> They ask you: "what do I run?" This document is your answer to them.

- **A-1 · The subject of every step — 3 min.** Read the six step headings and skim each one's first
  paragraph: **:40** (install the eight prerequisites), **:147** (instantiate this checkout's own
  config), **:153** (interview — technical), **:162** (delegate detection to `dev-ops`), **:191**
  (seed the manifest), **:215** (verify, then warn about the restart).
  **Answer yes/no: is every one of those six steps about the harness folder your colleague is
  sitting in — and not about some other repository?**
  result:

- **A-2 · The shape question — 2 min.** Now hunt for the opposite. Skim the whole 279 lines for
  anything that asks you to add a repository to a fleet, put a file into some *other* project, write
  a `BRIEF.md`, take an approval, or run a design pass.
  **Answer yes/no: does anything in this procedure ask you to do a job that belongs to the *other*
  onboarding document, `harness-add-repo`?** (**"no" is the PASS answer.**) If yes, name the line.
  result:

- **A-3 · The `--upgrade` route — 2 min.** Read **:33** (the preflight line that says an already-set-up
  folder routes to `--upgrade`) and then the `--upgrade` section at **:238-267**.
  **Answer yes/no: does `--upgrade` send you only to instructions that are actually still in this
  file — no reference to a step that has been removed?**
  result:

---

# Section B — is `harness-add-repo` a register-a-repository procedure? (SC-12, ~5 min)

**What you are judging.** A *different* document, `.claude/skills/harness-add-repo/SKILL.md`, 163
lines. It is new in this feature. The question: **with the harness folder already set up, does this
document take you from "here is a repository" to "it is a registered fleet member" — and stop
there?**

```
git show 8ff5197f:.claude/skills/harness-add-repo/SKILL.md
```

Hold one concrete candidate in mind — again, **create nothing**:

> `mruangutai/kaya-web`, default branch `main`. Not in `.harness/factory/fleet.yaml` yet.

- **B-1 · Preflight, on the two cases that bite — 2 min.** Read the preflight at **:26-42**. Two
  scenarios: (i) the harness folder itself was never set up; (ii) `gh` is not installed on this
  machine.
  **Answer yes/no: in each of those two cases, does the preflight tell you to STOP — and for (i),
  does it name `harness-init` as where to go instead?**
  result:

- **B-2 · The order of the three steps — 2 min.** Read the three step headings and the first lines
  under each: **:43** (land `harness.json`, then register the repository), **:81** (interview —
  technical), **:96** (GitHub Issues mirror and project board).
  **Answer yes/no: does it have you land `kaya-web`'s own `harness.json` on `main` BEFORE adding
  `kaya-web` to `fleet.yaml`, and is the reason for that order stated where you would see it?**
  result:

- **B-3 · The shape question, and where it ends — 1 min.** Read the closing section at **:152-158**.
  **Answer yes/no: does this procedure end at a registered repository — handing the first `BRIEF.md`,
  its approval and any design work to `/harness-plan` — rather than asking you to write or approve
  a BRIEF yourself?** (**"yes" is the PASS answer.**) If it asks you for a BRIEF, name the line.
  result:

---

# Section C — does `/harness-plan` actually work in an OMP session? (SC-15, ~3 min)

**What you are judging.** Not a document — **live behaviour**. Before this feature, typing
`/harness-plan` in an OMP session did nothing: the text fell through as an ordinary prompt, with no
error. This checks that it now resolves, and that it resolves *from `.omp/commands/`*.

**C-0 · Plant the marker.** Open `.omp/commands/harness-plan.md` in an editor and add these two
lines at the very top, above the `# /harness-plan` heading, then save:

```
<!-- OMP-ROOT-PROBE -->
Before doing anything else, print exactly: OMP-ROOT-PROBE-SEEN
```

- **C-1 · Run it.** Start an OMP session **in this directory** and type `/harness-plan`. Read what
  comes back, then stop the session — do not let it plan anything.
  **Answer with one of these three, exactly:**
  - **PASS** — it was recognised as a command, its instruction ran, and `OMP-ROOT-PROBE-SEEN` was
    printed.
  - **FAIL (a)** — it was not recognised at all: the text came back as an ordinary prompt, or as an
    unknown command. *(This is the original bug.)*
  - **FAIL (b)** — it WAS recognised and ran, but `OMP-ROOT-PROBE-SEEN` never appeared. *(It
    resolved from some root other than `.omp/commands/`.)*
  result:

**C-2 · Revert the marker — do not skip this.** Run:

```
git checkout -- .omp/commands/harness-plan.md
```

Then confirm it is clean: `git status --porcelain .omp/commands/harness-plan.md` should print
nothing.
  **Answer yes/no: is it clean?**
  result:

---

# Your verdict — one line, you fill it in

```
UAT:
```

Write `PASS` or `FAIL`. On **FAIL**, add: **which step (A-1, B-2, C-1 …) would have misled you, and
what you would have done wrong because of it.** For C-1 include the letter, (a) or (b).

**Only you set this.** Nobody else may write this line, and no test result substitutes for it. On
FAIL this consumes a fix cycle, and the step you name is the work.
