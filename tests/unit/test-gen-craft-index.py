#!/usr/bin/env python3
"""harness-craft's `## Principles` block is generated from the leaves' frontmatter. Three
things must hold or the index drifts from the rules it points at:

1. The committed block matches a fresh render (`--check` exits 0).
2. Every leaf parses under the generator's own frontmatter grammar, so a leaf with a bad
   `seats` list or an unquoted description is refused rather than silently dropped.
3. Every leaf lands in at least one seat's section and every cited path exists — an index
   line pointing at a missing leaf is the drift this test exists to catch.
"""
import os
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)

import importlib.util

spec = importlib.util.spec_from_file_location("gen_craft_index", os.path.join(BIN_DIR, "gen-craft-index.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def main():
    os.chdir(ROOT)
    proc = subprocess.run([sys.executable, os.path.join(BIN_DIR, "gen-craft-index.py"), "--check"],
                          capture_output=True, text=True)
    check("committed_index_matches_fresh_render", proc.returncode == 0, proc.stderr.strip())

    try:
        leaves = gen.load_leaves()
    except gen.LeafError as err:
        check("every_leaf_parses", False, str(err))
        return 1
    check("every_leaf_parses", True)
    check("at_least_ten_leaves", len(leaves) >= 10, f"only {len(leaves)}")

    block = gen.render(leaves)
    for leaf in leaves:
        path = os.path.join(gen.SKILL_DIR, "references", leaf["slug"] + ".md")
        check(f"{leaf['slug']}_indexed", f"`references/{leaf['slug']}.md`" in block, "absent from index")
        check(f"{leaf['slug']}_exists", os.path.isfile(path), path)

    bad = {"name": "x", "title": "X", "description": '"Never"', "seats": "[harness-qa]"}
    text = "---\n" + "\n".join(f"{k}: {v}" for k, v in bad.items()) + "\n---\nbody\n"
    try:
        gen.parse_frontmatter("x.md", text)
        check("description_must_start_with_apply", False, "accepted a non-Apply description")
    except gen.LeafError:
        check("description_must_start_with_apply", True)

    text = '---\nname: x\ntitle: X\ndescription: "Apply when"\nseats: [harness-qa, harness-frontend-dev]\n---\nbody\n'
    try:
        gen.parse_frontmatter("x.md", text)
        check("seats_must_be_canonical_order", False, "accepted [harness-qa, harness-frontend-dev]")
    except gen.LeafError:
        check("seats_must_be_canonical_order", True)

    if failures:
        print(f"\n{len(failures)} failure(s): {failures}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
