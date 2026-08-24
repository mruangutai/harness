#!/usr/bin/env python3
"""Merge the harness hook prerequisites into a project's .claude/settings.json.

WHY THIS IS A SCRIPT AND NOT AN INSTRUCTION: every entry degrades SILENTLY if
absent — no error, no warning, just a harness with memoryless agents that can write
anywhere. Hand-merging JSON into a file that already has the project's own hooks is
exactly where one of them quietly goes missing. So the merge is deterministic
and re-runnable, and `--check` can assert the result.

  merge-settings.py <project-root> [--check] [--template <path>]

  (default)  merge and write. Idempotent: running twice changes nothing.
  --check    verify only; exit 1 and print what is missing. Writes nothing.

Exit 0 = settings are correct (or were written). Exit 1 = a problem the caller must
surface. This gates a workflow step, not a tool call, so exit 1 is right; the
exit-2 rule applies only to PreToolUse hooks.

PRESERVATION IS THE POINT. Target projects have their own hooks — kaya-ai has five.
Every existing key, every existing hook on every event, survives. We add our entries
only where an equivalent one is not already present, matched by the SCRIPT NAME in
the command string, so a project that points the same hook at a different absolute
path is recognised rather than duplicated.
"""
import json
import os
import re
import shutil
import sys

# The hook prerequisites, each keyed by the (event, script basename) pair that identifies
# it — check-domain.sh appears on TWO events and they are two separate prerequisites.
#
# THE COUNT IS DERIVED FROM THIS LIST, never written as a word. At origin/main the word
# "six" appeared on 5 lines of this file and 3 times in the snippet, and "seven" on 5
# lines of harness-init/SKILL.md (counting the spawn-depth env var); adding the
# PostToolUse entry for issue #132 made every one of them wrong at once. A prose count
# that disagrees with the code is how a reader concludes an entry is spurious and
# deletes it.
#
# The numbers above are `git show origin/main:<file> | grep -ci`. An earlier draft of
# this comment said "three places and one" from memory and was wrong in both halves —
# in the very comment arguing that unchecked counts rot. Caught by review.
HOOK_SPECS = [
    {
        "event": "SubagentStart",
        "script": "inject-expertise.sh",
        "matcher": "harness-.*",
        "why": "Expertise injection. Absent -> every agent starts with no Expertise "
               "and nothing is raised.",
    },
    {
        "event": "PreToolUse",
        "script": "check-domain.sh",
        # NO agent-name matcher, deliberately: one registration serves all 16 and the
        # script dispatches on `agent_type` from the payload (DEC-110/111).
        "matcher": "Write|Edit",
        "why": "Domain enforcement. Absent -> every agent can write anywhere, "
               "fail-open and silent. Agent-frontmatter PreToolUse hooks DO NOT FIRE "
               "(DEC-110), so settings.json is the only place this works.",
    },
    {
        # SAME SCRIPT, DIFFERENT EVENT — and `hook_present` keys on (event, basename),
        # so this is a genuinely separate prerequisite rather than a duplicate of the
        # PreToolUse entry above. Registered on Bash too, which the PreToolUse entry
        # deliberately is not: pre-Bash there is nothing to shape-check, post-Bash the
        # file is on disk.
        "event": "PostToolUse",
        "script": "check-domain.sh",
        "args": " --post",
        "matcher": "Write|Edit|Bash",
        "why": "State-file SHAPE enforcement on the routes PreToolUse cannot reach "
               "(issue #132). Absent -> the DEC-150 line and comment budgets bind only "
               "a `Write` by a harness agent, which is 1 of 4 routes; Edit, Bash and "
               "the main session all write over budget in silence.",
    },
    {
        "event": "SubagentStop",
        "script": "validate-digest.py",
        "args": " --hook",
        # No agent matcher: one registration serves all 16, and the script passes
        # through anything that is not a harness agent (DEC-122).
        "matcher": "harness-.*",
        "why": "Digest contract enforcement. Absent -> malformed returns are accepted "
               "by whoever reads them, and the runner routes on fields that are not "
               "there. A validator nothing runs does not exist (DEC-101, DEC-119).",
    },
    {
        "event": "PreToolUse",
        "script": "branch-create-gate.sh",
        # Bash matcher, separate entry from check-domain (Write|Edit). SELF-GATING on
        # harness.json github.sync — registered everywhere, no-op where the mirror is
        # off, so registration stays unconditional like every prerequisite (DEC-144).
        "matcher": "Bash",
        "why": "Branch-creation work-tracking gate. Absent -> branches with no issue or "
               "flow behind them, silently.",
    },
    {
        # Rides the same Bash matcher entry as branch-create-gate when installed from
        # the snippet; hook_present matches on basename so either shape is recognized.
        # Was in the snippet since DEC-151 but missing HERE — the one-way template
        # check never caught it, so deploys silently skipped it.
        "event": "PreToolUse",
        "script": "bash-write-guard.sh",
        "matcher": "Bash",
        "why": "Bash write-bypass guard (DEC-151). Absent -> the common shell write "
               "shapes (sed -i, tee, redirects) bypass domain enforcement silently.",
    },
    {
        "event": "PreToolUse",
        "script": "dispatch-guard.sh",
        # No agent matcher: the script passes through anything that is not a harness
        # agent, and the main session (no agent_type) is never governed (DEC-156).
        "matcher": "Task|Agent",
        "why": "Dispatch-parameter guard (DEC-155/156). Absent -> a lead can silently "
               "override a member's pinned model per-dispatch; the tier design is "
               "unenforced and the spend is unattributed.",
    },
]
DEPTH_KEY = "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"
DEPTH_VAL = "3"
DEPTH_WHY = ("Pins nesting to main-session -> orchestrator -> lead -> member (DEC-120). "
             "Verified at this value: layers 1 and 2 can spawn, layer 3 runs with Agent "
             "withheld, layer 4 is unreachable — so members stay leaves.")

CMD = "${CLAUDE_PROJECT_DIR}/.agents/skills/harness/bin/%s"


# The matcher values that are literal TOOL alternations, as opposed to agent-name regexes
# like `harness-.*`. Only these can be checked for tool coverage; for the others a matcher
# is not a list of anything and presence is the whole question.
_TOOL_NAMES = {"Write", "Edit", "NotebookEdit", "Bash", "Task", "Agent", "Read", "Glob", "Grep"}


def _runs_script(cmd, script):
    """Does this command actually invoke `script`, as opposed to merely mentioning it?

    SUBSTRING MATCHING WAS THE HOLE (review W1/W2). `check-domain.sh.disabled` contains
    `check-domain.sh`, so a decoy entry naming a disabled copy widened the coverage set and
    let the real registration be narrowed back to `Write` with every gate green. The token
    must BE the script, not contain it. This does not resolve the path or check the file
    exists — a registration pointing at a deleted file still reads as present, and that
    residual is recorded rather than papered over.
    """
    for tok in str(cmd).split():
        if os.path.basename(tok) == script:
            return True
    return False


def _matcher_covers(raw, tool):
    """Does a settings.json matcher select `tool`? The matcher is a REGEX, not a list.

    THIS IS THE WHOLE LESSON OF PR #149's FIRST FIX. Binding the matcher was right — an
    unbound one let `Write|Edit|Bash` be narrowed to `Write` with every gate green. But the
    first attempt compared `set(raw.split("|"))` to a required set, which treats a regex as
    a literal alternation and rejects six legitimate registrations a reviewer enumerated:
    an ABSENT matcher (which matches every tool, and is the common real-world shape),
    `".*"`, `"(Write|Edit|Bash)"`, `"^(Write|Edit|Bash)$"`, spaced alternations, and — worst
    — three separate per-tool entries that together cover the requirement.

    A false negative here is not a missed warning. `hook_present` decides whether to ADD a
    registration, so rejecting a valid one DUPLICATES it: proven in write mode, 3 entries
    became 4 with byte-identical commands, and every Write then fired the hook twice. The
    same fixture made `--check` report the hook MISSING, which harness-init treats as a
    HARD GATE. Over-strictness broke the thing it was protecting.
    """
    if raw is None or str(raw).strip() in ("", "*"):
        return True                      # no matcher selects every tool
    try:
        rx = re.compile(str(raw))
    except re.error:
        # An unparseable matcher is the project's problem, not evidence of absence. Claiming
        # "missing" here would duplicate the hook on a config we simply cannot read.
        return True
    return bool(rx.search(tool))


def hook_present(entries, script, matcher=None, args=None):
    """True if this event ALREADY runs `script` across every tool the spec requires.

    Matched on basename, not the full command string: a project may legitimately have
    registered the same hook via an absolute path or a different variable. Matching
    the literal string would add a second, duplicate registration that fires twice.

    COVERAGE IS UNIONED ACROSS ENTRIES, because a project may split one requirement over
    several registrations and each is as valid as our single combined one. The question is
    "is every required tool covered by some entry running this script", never "does one
    entry look like ours".
    """
    want = set(str(matcher or "").split("|")) & _TOOL_NAMES
    covered, found = set(), False
    for entry in entries or []:
        for h in (entry.get("hooks") or []):
            cmd = str(h.get("command", ""))
            if not _runs_script(cmd, script):
                continue
            # TOKEN comparison, not substring: `args.strip() in cmd` made `--post` match a
            # command containing `--posture`, so a hook registered with an unrelated flag
            # would read as ours. Reviewer finding.
            if args is not None and args.strip() not in cmd.split():
                continue
            found = True
            covered |= {t for t in want if _matcher_covers(entry.get("matcher"), t)}
    if not found:
        return False
    # `want` is empty for the agent-name specs (`harness-.*`), where a matcher enumerates
    # no tools and presence is the entire prerequisite — exactly the pre-#149 behaviour.
    return want <= covered


def main():
    args = [a for a in sys.argv[1:]]
    check_only = "--check" in args
    args = [a for a in args if a != "--check"]

    template = None
    if "--template" in args:
        i = args.index("--template")
        template = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]

    if not args:
        print(__doc__.strip().splitlines()[0])
        print("usage: merge-settings.py <project-root> [--check] [--template <path>]")
        return 1
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print(f"merge-settings: {root} is not a directory")
        return 1

    # The template is documentation of intent; HOOK_SPECS above is what actually
    # executes. Read it only to fail loudly if the two have drifted apart, so the
    # snippet a human reads cannot silently stop describing what runs.
    if template and os.path.isfile(template):
        try:
            t = json.load(open(template, encoding="utf-8"))
            t_depth = (t.get("env") or {}).get(DEPTH_KEY)
            if t_depth != DEPTH_VAL:
                print(f"merge-settings: template says {DEPTH_KEY}={t_depth!r}, "
                      f"this script writes {DEPTH_VAL!r} — reconcile them.")
                return 1
            for spec in HOOK_SPECS:
                if not hook_present((t.get("hooks") or {}).get(spec["event"]), spec["script"],
                                    spec.get("matcher"), spec.get("args")):
                    print(f"merge-settings: template is missing {spec['script']} on "
                          f"{spec['event']} — reconcile it with this script.")
                    return 1
        except Exception as e:
            print(f"merge-settings: template {template} is unreadable ({e})")
            return 1

    path = os.path.join(root, ".claude", "settings.json")
    settings, existed = {}, os.path.isfile(path)
    if existed:
        raw = open(path, encoding="utf-8").read()
        if raw.strip():
            try:
                settings = json.loads(raw)
            except Exception as e:
                # Never overwrite a file we cannot parse — that would destroy the
                # project's own configuration to install ours.
                print(f"merge-settings: {path} is not valid JSON ({e}). "
                      f"Refusing to touch it. Fix the file, then re-run.")
                return 1
        if not isinstance(settings, dict):
            print(f"merge-settings: {path} is not a JSON object. Refusing to touch it.")
            return 1

    missing, added = [], []

    env = settings.get("env")
    if not isinstance(env, dict):
        env = {} if env is None else None
        if env is None:
            print(f"merge-settings: {path} has a non-object `env`. Refusing to touch it.")
            return 1
    if env.get(DEPTH_KEY) != DEPTH_VAL:
        missing.append(f"env.{DEPTH_KEY} = \"{DEPTH_VAL}\"  — {DEPTH_WHY}")
        added.append(("env", DEPTH_KEY))
        env[DEPTH_KEY] = DEPTH_VAL
    settings["env"] = env

    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        if hooks is not None:
            print(f"merge-settings: {path} has a non-object `hooks`. Refusing to touch it.")
            return 1
        hooks = {}
    for spec in HOOK_SPECS:
        entries = hooks.get(spec["event"])
        if entries is None:
            entries = []
        if not isinstance(entries, list):
            print(f"merge-settings: {path} hooks.{spec['event']} is not a list. "
                  f"Refusing to touch it.")
            return 1
        if not hook_present(entries, spec["script"], spec.get("matcher"), spec.get("args")):
            missing.append(f"hooks.{spec['event']} -> {spec['script']}  — {spec['why']}")
            added.append(("hooks", spec["event"]))
            entries.append({
                "matcher": spec["matcher"],
                "hooks": [{"type": "command",
                           "command": (CMD % spec["script"]) + spec.get("args", "")}],
            })
        hooks[spec["event"]] = entries
    settings["hooks"] = hooks

    if check_only:
        if missing:
            print("merge-settings: MISSING prerequisites (each fails silently):")
            for m in missing:
                print(f"  - {m}")
            return 1
        print(f"merge-settings: all {len(HOOK_SPECS) + 1} prerequisites present "
              f"({len(HOOK_SPECS)} hooks + {DEPTH_KEY}).")
        return 0

    if not missing:
        print(f"merge-settings: already correct — {path} unchanged.")
        return 0

    os.makedirs(os.path.dirname(path), exist_ok=True)
    if existed:
        # A backup, because this edits a file the project owns and we do not.
        shutil.copyfile(path, path + ".harness-bak")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)

    verb = "updated" if existed else "created"
    print(f"merge-settings: {verb} {path}")
    for m in missing:
        print(f"  + {m.split('  — ')[0]}")
    if existed:
        print(f"  (existing keys and hooks preserved; backup at {path}.harness-bak)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
