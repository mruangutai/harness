#!/usr/bin/env python3
"""Merge the four harness prerequisites into a project's .claude/settings.json.

WHY THIS IS A SCRIPT AND NOT AN INSTRUCTION: all four entries degrade SILENTLY if
absent — no error, no warning, just a harness with memoryless agents that can write
anywhere. Hand-merging JSON into a file that already has the project's own hooks is
exactly where one of the four quietly goes missing. So the merge is deterministic
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
import shutil
import sys

# The four prerequisites, each keyed by the script basename that identifies it.
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
        # NO agent-name matcher, deliberately: one registration serves all 15 and the
        # script dispatches on `agent_type` from the payload (DEC-110/111).
        "matcher": "Write|Edit",
        "why": "Domain enforcement. Absent -> every agent can write anywhere, "
               "fail-open and silent. Agent-frontmatter PreToolUse hooks DO NOT FIRE "
               "(DEC-110), so settings.json is the only place this works.",
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
]
DEPTH_KEY = "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"
DEPTH_VAL = "3"
DEPTH_WHY = ("Pins nesting to main-session -> orchestrator -> lead -> member (DEC-120). "
             "Verified at this value: layers 1 and 2 can spawn, layer 3 runs with Agent "
             "withheld, layer 4 is unreachable — so members stay leaves.")

CMD = "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/%s"


def hook_present(entries, script):
    """True if any registration on this event already runs `script`.

    Matched on basename, not the full command string: a project may legitimately have
    registered the same hook via an absolute path or a different variable. Matching
    the literal string would add a second, duplicate registration that fires twice.
    """
    for entry in entries or []:
        for h in (entry.get("hooks") or []):
            if script in str(h.get("command", "")):
                return True
    return False


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
                if not hook_present((t.get("hooks") or {}).get(spec["event"]), spec["script"]):
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
        if not hook_present(entries, spec["script"]):
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
        print("merge-settings: all four prerequisites present.")
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
