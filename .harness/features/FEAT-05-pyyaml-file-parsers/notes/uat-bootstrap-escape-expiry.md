# UAT — FEAT-05 the PyYAML bootstrap escape expires
status: ready              # draft | ready | passed | failed
branch: worktree-fix-harness-tooling-backlog
review_sha: 225cc98

**Ship is gated on this.** `harness.json:244` sets `uat: blocking_when_uat_criteria_exist` and SC-09
is `verify: uat`. Only you can run it: **SC-09 is the one criterion no test kind can create
honestly**, because it needs a genuinely NEW Claude Code session, and a test that fakes a session
boundary proves only that the fake works.

Do not mark this `passed` on my say-so. SC-09 stays `not_met` until you run it.

**Time: ~10 minutes.** Steps U-01..U-04 are one continuous sitting; U-05 and U-06 close it out.

## Setup

Work in a **scratch clone, never this checkout** — U-02 deliberately breaks the write guards, and
you want that damage disposable.

```bash
git clone /Users/molchairuangutai/GitHub/harness /tmp/uat-pyyaml
cd /tmp/uat-pyyaml && git checkout worktree-fix-harness-tooling-backlog
mkdir -p /tmp/uat-fakeyaml && printf 'raise ImportError("simulated: no PyYAML")\n' > /tmp/uat-fakeyaml/yaml.py
```

That last file is how PyYAML is made unimportable without uninstalling anything: a directory on
`PYTHONPATH` holding a `yaml.py` that raises. BRIEF `:131-135` says explicitly this is not an SC-05
violation — SC-05 forbids the *tester* setting `PYTHONPATH` to make the hook succeed; here it is set
to make it fail.

**Simpler alternative if you prefer:** `export PYTHONNOUSERSITE=1` before launching. PyYAML lives in
your user site-packages (`~/Library/Python/3.14/...`), so that one variable hides it with no files
created. Either works; the fake-module route is closer to a machine that genuinely lacks it.

## Steps

- **U-01 (SC-08):** With PyYAML hidden, start a NEW Claude Code session in `/tmp/uat-pyyaml` and ask
  any agent to write one file inside its own domain.
  expect: the write is **permitted**.
  result:

- **U-02 (SC-08):** Look at that agent's stderr / the hook output from U-01.
  expect: the **two-line install command** appears, the one beginning `python3 -m pip install pyyaml`.
  result:

- **U-03 (SC-08):** `ls -la /tmp/uat-pyyaml/.harness/.pyyaml-bootstrap`
  expect: the file **exists**.
  result:

- **U-04 (SC-08):** In the **same** session, ask for a second write in the same domain.
  expect: permitted, and **no second install message**. (A "used once ever" latch fails here — this
          step is what distinguishes a per-session grant from a per-write one.)
  result:

- **U-05 (SC-09 — the criterion this whole script exists for):** **Quit Claude Code entirely and
  start a genuinely new session** in the same clone, PyYAML still hidden. Ask for one write.
  expect: **BLOCKED**, with the install command printed.
  result:

- **U-06 (D-01):** Stop hiding PyYAML (`unset PYTHONNOUSERSITE`, or drop the fake dir from
  `PYTHONPATH`), start a session, ask for one write, then run `git status` in the clone.
  expect: the write is permitted, `.harness/.pyyaml-bootstrap` is **gone** (the marker self-unlinks
          once `import yaml` succeeds), and `git status` is **clean** — the marker never appeared as
          an untracked file at any point above.
  result:

## What each step is really testing

U-01..U-03 prove the escape **opens**: a machine without PyYAML is recoverable from inside the tool
rather than bricked. U-04 proves it is scoped to a **session**, not a single write — a one-write
grant would be useless, since recovery takes many. U-05 proves it **closes**, which is the whole
point: an escape that never expires is a permanent silent bypass (D-06). U-06 proves it **cleans up
after itself** and never dirties the tree, which matters because a dirty tree halts the next team
run with `BLOCKED` on the harness's own artifact.

## If a step fails

Record it in `result:` and stop — do not continue to the next step. U-05 failing OPEN (the write is
permitted in a new session) is the serious one: it means enforcement is off and nothing says so.
