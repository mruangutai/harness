#!/usr/bin/env python3
"""harness-craft's `## Principles` block is generated from the leaves' frontmatter. Three
things must hold or the index drifts from the rules it points at:

1. The committed block matches a fresh render (`--check` exits 0).
2. Every leaf parses under the generator's own frontmatter grammar, so a leaf with a bad
   `seats` list or an unquoted description is refused rather than silently dropped.
3. Every leaf lands in at least one seat's section and every cited path exists — an index
   line pointing at a missing leaf is the drift this test exists to catch.
"""
from unit_support import ROOT, BIN, load_script

import os
import subprocess
import sys

from check_support import Checks

GEN_PATH = BIN / "gen-craft-index.py"
gen = load_script("gen-craft-index.py")

C = Checks()
check = C.check


def refuses(text):
    """True when parse_frontmatter rejects text with LeafError; any other error propagates."""
    try:
        gen.parse_frontmatter("x.md", text)
    except gen.LeafError:
        return True
    return False


def main():
    os.chdir(ROOT)
    proc = subprocess.run([sys.executable, str(GEN_PATH), "--check"],
                          capture_output=True, text=True)
    check("committed_index_matches_fresh_render", proc.returncode == 0, proc.stderr.strip())

    try:
        leaves = gen.load_leaves()
    except gen.LeafError as err:
        check("every_leaf_parses", False, str(err))
        return C.report()
    check("every_leaf_parses", True)
    check("at_least_ten_leaves", len(leaves) >= 10, f"only {len(leaves)}")

    block = gen.render(leaves)
    for leaf in leaves:
        path = os.path.join(gen.SKILL_DIR, "references", leaf["slug"] + ".md")
        check(f"{leaf['slug']}_indexed", f"`references/{leaf['slug']}.md`" in block, "absent from index")
        check(f"{leaf['slug']}_exists", os.path.isfile(path), path)

    text = '---\nname: x\ntitle: X\ndescription: "Never"\nseats: [harness-qa]\n---\nbody\n'
    check("description_must_start_with_apply", refuses(text), "accepted a non-Apply description")

    text = '---\nname: x\ntitle: X\ndescription: "Apply when"\nseats: [harness-qa, harness-frontend-dev]\n---\nbody\n'
    check("seats_must_be_canonical_order", refuses(text), "accepted [harness-qa, harness-frontend-dev]")

    return C.report()


if __name__ == "__main__":
    sys.exit(main())
