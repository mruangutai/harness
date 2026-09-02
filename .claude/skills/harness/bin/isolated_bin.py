#!/usr/bin/env python3
"""Private copies of Harness's executable bin tree for destructive probes."""

import os
import shutil


def isolated_bin(dest_root):
    """Copy the live bin directory beneath dest_root and return the copied path."""
    source = os.path.dirname(os.path.realpath(__file__))
    # Four levels up from bin is the project root derived by copied hook scripts.
    destination = os.path.join(dest_root, ".claude", "skills", "harness", "bin")
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    return shutil.copytree(source, destination)
