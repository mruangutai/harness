# UAT — FEAT-05 the PyYAML bootstrap escape expires
status: passed             # draft | ready | passed | failed — SC-09 (the only uat criterion) PASSED
sc_08: not_met             # U-02 failed; SC-08 is verify:automated, re-verify at unit level
sc_09: met                 # U-05 passed against a genuine session boundary
run_on: 2026-08-03 by Mike Ruangutai, scratch clone /tmp/uat-pyyaml at fd42409
run_note: >-
  Five of six steps passed; U-02 FAILED (SC-08's "channel the user sees" clause).
  Run at branch HEAD fd42409, NOT the pinned review_sha 225cc98 —
  0775862 ("the bootstrap escape was INERT — wire up its decision") lands between them,
  so 225cc98 would have tested unwired code. PyYAML hidden via PYTHONNOUSERSITE=1.
  Session boundaries verified genuine: three distinct transcript UUIDs
  (d079e08e / bd1846b4 / 8ef3b7b8) under ~/.claude/projects/-private-tmp-uat-pyyaml/.
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
  result: **PASS.** `notes/uat-scratch.md` written (10 bytes) by a spawned `harness-orchestrator`.
    NOTE the permit came from the ESCAPE, not the domain grant: with no parser
    `check-domain.sh:122-123` exits 0 before `domain_check()` is reachable. Two separate
    agents initially mis-attributed this to `team-config.yaml:28`. The marker appearing
    (U-03) is what proves the escape ran.
    CAVEAT for re-runs: the write MUST go through a spawned `harness-*` subagent. A
    main-session write exits 0 at `check-domain.sh:72-74` and tests nothing.

- **U-02 (SC-08):** Look at that agent's stderr / the hook output from U-01.
  expect: the **two-line install command** appears, the one beginning `python3 -m pip install pyyaml`.
  result: **FAIL** — against SC-08 as written. Corrected from an earlier PASS.
    The message IS emitted: replaying the hook directly (marker absent, PyYAML hidden, valid
    payload on stdin) prints all four lines to stderr and exits 0. But BRIEF.md:105-106 requires
    it be emitted "**on a channel the user sees**", and it is not: the tester saw nothing, and
    `grep -rc "pip install pyyaml" ~/.claude/projects/-private-tmp-uat-pyyaml/` returns 0 across
    all three sessions. Claude Code does not surface hook stderr when the hook ALLOWS (exit 0).
    Emitted-to-stderr is not the criterion; user-visible is. See D-14b below.
    RE-RUN TRAP: `check-domain.sh:26` reads the payload from STDIN and overwrites `$HOOK_PAYLOAD`.
    An env-var payload, or malformed JSON, yields no agent identity and a SILENT exit 0 that
    looks exactly like a pass. Treat any silent exit 0 as suspect until the payload is verified.

- **U-03 (SC-08):** `ls -la /tmp/uat-pyyaml/.harness/.pyyaml-bootstrap`
  expect: the file **exists**.
  result: **PASS.** Exists, 36 bytes, containing `d079e08e-6b93-4f96-ad5a-057a8823b3a9` — byte-identical
    to the session's transcript directory name under `~/.claude/projects/-private-tmp-uat-pyyaml/`.
    Confirmed absent immediately before U-01, so its appearance is real. Its presence is also the
    proof PyYAML was genuinely hidden from the hook, since `harness_yaml.py:238-243` unlinks it
    whenever `import yaml` succeeds.

- **U-04 (SC-08):** In the **same** session, ask for a second write in the same domain.
  expect: permitted, and **no second install message**. (A "used once ever" latch fails here — this
          step is what distinguishes a per-session grant from a per-write one.)
  result: **PASS.** `notes/uat-scratch-4.md` written (11 bytes) by subagent `a9e9cb374c7ab5e42`,
    no install message. Proven by elimination rather than by observation, since "allow silently"
    leaves no trace: of the four branches at `harness_yaml.py:236-266`, *marker absent* is ruled
    out (marker unchanged, still the U-01 value), and *identity mismatch* / *marker unreadable*
    are ruled out (both block; the file exists). Only *present + identity matches* remains.
    So there was no message to miss — the absence IS the pass.
    FIRST ATTEMPT WAS VOID: the session wrote the file itself with no delegation, hitting the
    main-session carve-out. Re-run with delegation stated explicitly. Watch for an actual
    subagent spawn; unlike U-01 there is no filesystem trace to catch this after the fact.

- **U-05 (SC-09 — the criterion this whole script exists for):** **Quit Claude Code entirely and
  start a genuinely new session** in the same clone, PyYAML still hidden. Ask for one write.
  expect: **BLOCKED**, with the install command printed.
  result: **PASS on the block — but the stated expectation is WRONG about the message.**
    Blocked correctly: `uat-scratch-3.md` never appeared, marker still held the OLD session id,
    and the new session `bd1846b4-a180-4f3a-b994-3ec5e40d6fee` is a distinct transcript directory
    (a real process restart, not `/clear` or `--resume`). Enforcement CLOSED — the failure mode
    `:78-79` warns about did not occur.
    The block is SILENT. No install command, no reason, zero bytes of stderr — reproduced
    directly (`exit=2`, stderr 0 bytes) and independently hit live: the agent saw only
    "PreToolUse:Write hook error: No stderr output". `bash-write-guard.sh` is affected too —
    even `echo hi` was refused with nothing printed. See D-14a below.
    AMEND THE EXPECTATION to "BLOCKED, silently" until D-14a is fixed. A block WITH a message
    would mean some other branch fired and needs a second look.

- **U-06 (D-01):** Stop hiding PyYAML (`unset PYTHONNOUSERSITE`, or drop the fake dir from
  `PYTHONPATH`), start a session, ask for one write, then run `git status` in the clone.
  expect: the write is permitted, `.harness/.pyyaml-bootstrap` is **gone** (the marker self-unlinks
          once `import yaml` succeeds), and `git status` is **clean** — the marker never appeared as
          an untracked file at any point above.
  result: **PASS on all three halves.** Session `8ef3b7b8-9e8e-4be7-9821-2cadfdd1891c`, PyYAML
    restored. Write permitted (`uat-scratch-6.md`, 10 bytes); `.harness/.pyyaml-bootstrap` GONE,
    self-unlinked by `harness_yaml.py:238-243` with nobody deleting it; `git status` showed only
    the four intentional probe files — the marker never appeared as untracked across all three
    sessions, so the `.gitignore:13` chain holds in a real clone (`git check-ignore -v` confirms).
    This is the ONLY step in the whole script where `domain_check()` actually executes — every
    prior step exits at `check-domain.sh:122-123` for want of a parser. The domain guard is
    therefore exercised exactly once here, and nowhere else in this UAT.

## What each step is really testing

U-01..U-03 prove the escape **opens**: a machine without PyYAML is recoverable from inside the tool
rather than bricked. U-04 proves it is scoped to a **session**, not a single write — a one-write
grant would be useless, since recovery takes many. U-05 proves it **closes**, which is the whole
point: an escape that never expires is a permanent silent bypass (D-06). U-06 proves it **cleans up
after itself** and never dirties the tree, which matters because a dirty tree halts the next team
run with `BLOCKED` on the harness's own artifact.

## Outcome — 2026-08-03

**SC-09 is MET. SC-08 is NOT.** Five of six steps pass; **U-02 fails.**

The mechanism works: the escape opens on a PyYAML-less machine, is scoped to one session,
closes at a genuine session boundary, and self-cleans without ever dirtying the tree. What
fails is that the user is never *told* any of it.

**Scope of this gate:** only SC-09 is `verify: uat` (BRIEF.md:110); SC-08 is
`verify: automated  evidence: unit` (BRIEF.md:107). So `harness.json:244` gates ship on U-05,
which passed. U-02's failure is a real SC-08 failure surfaced *incidentally* by this hand-run —
it needs a unit-level fix and re-verification, and it does not block on this file's `status:`.
**[needs your call]** whether SC-08's unit test asserts the wrong thing: if it checks only that
stderr was written, it passes while the criterion it traces to fails.

Two defects found, one expectation to amend, one non-finding to dismiss.
(Numbered D-14 because **D-10 is already taken** — `PLAN.md:41,208,819` use it for the launch
consolidation. Highest id in use across BRIEF/PLAN is D-13.)

- **D-14b (SC-08 FAILURE): the install command is emitted where nobody sees it.** It goes to
  stderr on the **allow** path (exit 0), and Claude Code surfaces hook stderr only on a block.
  BRIEF.md:106 requires "a channel the user sees." Note D-14a's fix does NOT close this — that
  one works precisely because exit 2 reaches the agent (DEC-100). A grant-path message needs a
  different channel to be visible at all. Fixing one and assuming both are closed is the trap.

- **D-14a (does not block SC-09): the block is silent.** `harness_yaml.py` returns
  `False` without writing to stderr on three branches — `:259` (marker unreadable), `:260`
  (identity mismatch), `:266` (marker write fails). Both callers assume the callee already
  printed: `check-domain.sh:110-112` says so in a comment, `bash-write-guard.sh:75-77` likewise.
  That assumption holds only for the no-identity path at `:247-251`. Consequence: a user whose
  grant has expired gets every Write AND every Bash command refused with no explanation and no
  install command — recoverable only by reading the source. Fix: print `INSTALL_COMMAND` on
  those three branches, matching `:247-251`.
  **Per DEC-174 this is an enforcement-layer edit — make it directly, run the tests explicitly,
  read the diff. Do NOT dispatch it through a team run whose gates are the thing being changed.**
  Severity note: this fails CLOSED, the safe direction. It is a usability defect, not a
  security one.

- **U-05's written expectation is wrong** and should be amended to "BLOCKED, silently" until
  D-14a is fixed, so a future tester does not read a correct silent block as a failure.

- **DISMISSED — the "hook interpreter" alarm.** The orchestrator, blocked and reasoning from
  source with no Bash, inferred that the surviving marker contradicted `feature.yaml:41-43`
  (T-01: yaml 6.0.3 importable by bare python3) and suspected a different python3 in the hook
  subprocess. It does not. PyYAML was unimportable because the UAT setup deliberately hides it
  (`:31-32`). Verified: `env -u PYTHONNOUSERSITE python3 -c "import yaml"` → 6.0.3, importable.
  Minor imprecision worth noting separately: `feature.yaml:41` names the homebrew interpreter,
  but the import actually resolves from user site-packages
  (`~/Library/Python/3.14/lib/python/site-packages/yaml/`) — which is exactly why
  `PYTHONNOUSERSITE` hides it.

Cleanup: `rm -rf /tmp/uat-pyyaml`. Nothing outside that clone was touched.

## If a step fails

Record it in `result:` and stop — do not continue to the next step. U-05 failing OPEN (the write is
permitted in a new session) is the serious one: it means enforcement is off and nothing says so.

## Disposition — 2026-08-03, main session

Both defects this hand-run found are **FIXED**, at commit noted below. The UAT itself is not
re-run: SC-09 passed and its mechanism is unchanged.

**D-14a — FIXED.** `harness_yaml.require_or_bootstrap` now writes a reason and the install
command on all three previously-silent `return False` branches (marker unreadable, identity
mismatch, marker write fails). The mismatch block now reads:

> PyYAML is not importable, and this session's one-time bootstrap grant was already used by an
> EARLIER session — failing closed. Install PyYAML to restore normal operation:

Locked by `test-check-domain.py`'s `D-14a: the block SAYS WHY and carries the install command`,
which asserts non-empty stderr rather than merely a non-zero exit. Your reading was right that
stderr is the correct channel *here* — exit 2 surfaces it (DEC-100), which is exactly why the
grant path needed a different one.

**D-14b — FIXED, and your warning that D-14a would not close it was correct.** The grant path
now also emits `{"systemMessage": ...}` on **stdout**, the PreToolUse contract's user-visible
channel. Not assumed: `branch-create-gate.sh:82,111` already emits that shape on its own allow
path and is registered in `.claude/settings.json`, so the channel is proven live in this repo.
Emitted last, so a failure there cannot cost the stderr copy the agent reads.

**Your `[needs your call]` on SC-08's unit test — you were right, and it was my defect.** It
asserted `"pip install" in stderr`, i.e. that the message was *written*, never that it was
*seen*. It passed while the criterion failed. Renamed to
`[partial SC-08] ... (NOT proof the user sees it — D-14b)` and a real assertion added that parses
the `systemMessage` payload. Same verify-method defect class as T-09's greps and the plan's
`^[0-9]\.` — the third instance in this feature, and the only one in a test I wrote myself.

**SC-08 status:** the automated evidence now covers the user-visible channel, so it is met at
unit level. Whether it should be re-confirmed by hand before ship is the reviewer's call —
`verify: automated` does not require another hand-run, and the mechanism is now asserted.

**Two re-run traps you documented are kept verbatim above** and are worth more than the result:
the write must go through a spawned `harness-*` subagent (a main-session write exits at the
carve-out and tests nothing), and any silent exit 0 is suspect until the payload is verified.
