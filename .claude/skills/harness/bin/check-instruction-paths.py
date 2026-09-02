#!/usr/bin/env python3
"""Validate control-plane and feature-tree anchors in agent instructions."""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness_boundary

MAIN_SESSION_ONLY = (
    "harness-init",  # main session only
    "harness-grilling",  # main session only
    "harness-wayfinding",  # main session only
)
TOKEN = re.compile(r"\.(?:harness|claude|agents|omp)/[^\s\"']+")
FEATURE_RE = re.compile(r"^\.harness/(?:[^/]+/)?features/")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(?:.*)$")


def is_feature_path(path):
    return bool(FEATURE_RE.match(path))


def scope(root):
    paths = []
    for directory, pattern in (
        (".omp/agents", "*.md"),
        (".claude/agents", "*.md"),
        (".claude/skills", "harness-*/SKILL.md"),
        (".claude/skills/harness/references", "*.md"),
        (".claude/skills/harness/templates", "*.md"),
    ):
        base = os.path.join(root, directory)
        if not os.path.isdir(base):
            continue
        if pattern == "harness-*/SKILL.md":
            for name in os.listdir(base):
                candidate = os.path.join(base, name, "SKILL.md")
                if name.startswith("harness-") and name not in MAIN_SESSION_ONLY and os.path.isfile(candidate):
                    paths.append(candidate)
        else:
            for current, _dirs, names in os.walk(base):
                for name in names:
                    if name.endswith(".md"):
                        paths.append(os.path.join(current, name))
    own = os.path.join(root, ".claude/skills/harness/SKILL.md")
    if os.path.isfile(own):
        paths.append(own)
    return sorted(set(paths))


def _tokens(line, fenced):
    if fenced:
        return ((match, match.start()) for match in TOKEN.finditer(line))
    return (
        (match, span.start(1) + match.start())
        for span in re.finditer(r"`([^`]*)`", line)
        for match in TOKEN.finditer(span.group(1))
    )
def violations(path, root):
    found = []
    fence_char = None
    fence_count = 0
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            opener = FENCE.match(line)
            if fence_char is None and opener:
                fence_char, fence_count = opener.group(1)[0], len(opener.group(1))
                continue
            if fence_char is not None and opener and opener.group(1)[0] == fence_char and len(opener.group(1)) >= fence_count:
                fence_char = None
                fence_count = 0
                continue
            for match, start in _tokens(line, fence_char is not None):
                token = match.group(0).rstrip(".,:;)]}")
                prefix = line[:start]
                if prefix.endswith("<HARNESS_CONTROL_PLANE_ROOT>/") or prefix.endswith("<HARNESS_FEATURE_TREE_ROOT>/"):
                    anchored = "feature" if prefix.endswith("<HARNESS_FEATURE_TREE_ROOT>/") else "control"
                    if anchored == "control" and is_feature_path(token):
                        found.append((number, "feature-directory path anchored to the control plane", token))
                    elif anchored == "feature" and not is_feature_path(token):
                        found.append((number, "control-plane path anchored to the feature tree", token))
                else:
                    found.append((number, "unanchored instruction path", token))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--list-scope", action="store_true")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    try:
        root = os.path.abspath(args.root) if args.root else harness_boundary.resolve_root(HERE)
    except ValueError:
        print("check-instruction-paths: no harness root could be resolved", file=sys.stderr)
        return 2
    files = scope(root)
    if args.list_scope:
        print("\n".join(os.path.relpath(path, root) for path in files))
        return 0
    if not files:
        print("check-instruction-paths: scope is empty", file=sys.stderr)
        return 2
    if args.paths:
        selected = set()
        for raw in args.paths:
            target = os.path.abspath(raw)
            matches = [path for path in files if path == target or (os.path.isdir(target) and path.startswith(target + os.sep))]
            if not matches:
                print(f"check-instruction-paths: {raw} selects nothing in scope", file=sys.stderr)
                return 2
            selected.update(matches)
        files = sorted(selected)
    total = 0
    for path in files:
        for line, reason, token in violations(path, root):
            print(f"VIOLATION {os.path.relpath(path, root)}:{line}: {reason}: {token}")
            total += 1
    print(f"scanned {len(files)} file(s), {total} violation(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
