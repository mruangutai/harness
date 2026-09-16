# T-09 receipt

BLUF: The obsolete shell differential tool is absent; the scoped T-09 verification passed.

- Branch: `feat/BUG-285-canonical-reader`
- Repository source change: deleted `.claude/skills/harness/bin/sh-to-py-differential.py`; no replacement, parser classification, or audit exemption was added.
- Verification command (run from the assigned worktree):

  ```sh
  test ! -e .claude/skills/harness/bin/sh-to-py-differential.py
  ```

  Verbatim command output: *(empty)*
  Exit status: `0`
