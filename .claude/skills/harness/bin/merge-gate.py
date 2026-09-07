#!/usr/bin/env python3
"""PreToolUse guard for merges while a Build-entry mirror receipt is owed."""
import glob
import json
import os
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

ROOT = sys.argv[1]
OPS = {";", "&", "&&", "|", "||", "(", ")", "<", ">", ">>", "\n"}


def words(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return [word for word in lexer if word not in OPS]
    except ValueError:
        return command.split()


def is_bin(token, name):
    return os.path.basename(token.strip("\\'\"$()`")) == name


# GRADE-2 REASON: token scanning is the security boundary; splitting the gh and git forms
# would duplicate the ordered token walk and make command detection drift.
def direct_merge(tokens):
    for index, token in enumerate(tokens):
        rest = tokens[index + 1:]
        found = gh_merge(rest) if is_bin(token, "gh") else git_merge(rest) if is_bin(token, "git") else None
        if found:
            return found
    return None


def gh_merge(rest):
    if rest[:2] != ["pr", "merge"]:
        return None
    return "gh", next((word for word in rest[2:] if word.isdigit()), None)


def git_merge(rest):
    args = [word for word in rest if not word.startswith("-")]
    if not args or args[0] != "merge":
        return None
    return "git", args[1] if len(args) > 1 else None


def nested_merge(tokens, depth):
    if depth >= 3:
        return None
    for token in tokens:
        if len(token.split()) > 1:
            found = merge_ref(token, depth + 1)
            if found:
                return found
    return None


def merge_ref(command, depth=0):
    tokens = words(command)
    return direct_merge(tokens) or nested_merge(tokens, depth)


def local_branch(cwd):
    result = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def gh_head(number, repo):
    try:
        result = subprocess.run(
            [os.environ.get("GH_BIN", "gh"), "pr", "view", number, "--repo", repo,
             "--json", "headRefName", "-q", ".headRefName"],
            capture_output=True, text=True,
        )
    except OSError as exc:
        return "", str(exc)
    text = (result.stderr or result.stdout).strip()
    return result.stdout.strip(), text.splitlines()[0] if text else "gh pr view failed"


def head_branch(command, cwd, repo):
    kind, value = merge_ref(command)
    if kind == "git" and value:
        return value.removeprefix("origin/"), None
    if kind != "gh" or not value:
        return local_branch(cwd), None
    branch, failure = gh_head(value, repo)
    return (branch, None) if branch else (local_branch(cwd), failure)


def feature_for(branch):
    for path in glob.glob(os.path.join(ROOT, ".harness", "*", "features", "*", "feature.json")):
        try:
            with open(path) as f:
                document = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if document.get("branch") == branch:
            return os.path.dirname(path), document
    return None, None


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def repo_pinned(repo):
    return isinstance(repo, str) and "/" in repo and bool(repo)


# GRADE-2 REASON: this is the gate's orchestration boundary; helpers own parsing,
# resolution and rendering, while this function preserves the policy's ordered exits.
def main():
    try:
        with open(os.path.join(ROOT, ".harness", "harness.json")) as f:
            github = json.load(f).get("github") or {}
        command = (json.load(sys.stdin).get("tool_input") or {}).get("command") or ""
    except Exception:
        return
    if not github.get("sync") or not merge_ref(command):
        return
    import feature_schema
    branch, failure = head_branch(command, os.getcwd(), github.get("repo") or "")
    feat_dir, document = feature_for(branch)
    if document is None:
        if failure:
            print(f"merge-gate: could not verify this merge - the head branch could not be resolved through gh ({failure}) and the local branch {branch} owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).", file=sys.stderr)
        return
    feat = os.path.basename(feat_dir)
    entry = (document.get("github") or {}).get("build_entry")
    if feat in feature_schema.BUILD_ENTRY_ERA_EXEMPT:
        print(f"merge-gate: {feat} predates the build-entry receipt (feature_schema.BUILD_ENTRY_ERA_EXEMPT), so this merge is allowed. Its terminal receipt is created only by an explicit operator-approved gh-sync.py recover-terminal {os.path.realpath(feat_dir)} --yes.", file=sys.stderr)
        return
    if entry in {"opened", "not-applicable", "recovered-terminal"}:
        if failure:
            print(f"merge-gate: could not verify this merge - the head branch could not be resolved through gh ({failure}) and the local branch {branch} owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).", file=sys.stderr)
        return
    value = entry or "absent"
    if not repo_pinned(github.get("repo")):
        deny(f"merge-gate: {feat} records github.build_entry={value}, and this project has github.sync true with github.repo NOT pinned, so the mirror records nothing here and no receipt can ever be written for it (D-09). NO COMMAND CLEARS THIS BY ITSELF. Pin github.repo in {ROOT}/.harness/harness.json to the value of gh repo view --json nameWithOwner -q .nameWithOwner, or set github.sync to false, and then re-run the Build entry.")
        return
    command_name = feature_schema.recovery_command_for(feat_dir)
    command_line = (f"python3 .claude/skills/harness/bin/gh-sync.py {command_name} {os.path.realpath(feat_dir)}" + (" --yes" if command_name == "recover-terminal" else ""))
    deny(f"merge-gate: {feat} records github.build_entry={value}, so no Build entry receipt exists for it. This merge is denied until {command_line} records one.")


if __name__ == "__main__":
    main()
