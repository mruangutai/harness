# Fix receipt - BUG-2169 - c1 (main-session-direct, DEC-174)

Owner of T-01 is the main session, so the fix step is the main session's; no dev persona ran.
Must-fix list: `notes/must-fix-c0.md`. Raw output: `/tmp/bug2169-evidence/fix-c1/`.
Base trees were built on the host (working files with `bin/` from `c4e8bbc8`, verified
byte-identical) because `git checkout` cannot run inside the container on a worktree mount.

## F-1 - D-14a

`test-check-domain-grant.py` D-14a now accepts any of `harness_yaml.install_command()`'s real
command lines, like the SC-08 lines. Red before (QA c0: pin 26/27, `FAIL D-14a` on the image);
container after: `ok D-14a`, `ok SC-08 ...`; Mac grant exit 0.

## GC-01 (b) - advice fails on behaviour at base

New checks in `bug2169_advice` judge `harness_yaml.INSTALL_COMMAND` - which exists at base -
against platform facts the test reads itself, before the `install_command` presence check:
`advice/printed-not-per-user` always; `advice/printed-homebrew` on a Homebrew prefix;
`advice/printed-debian` on Debian's system python3.

| State | Mac (Homebrew 3.15) | Image (Debian, 3.14.4) |
|---|---|---|
| base `c4e8bbc8` bin | FAIL not-per-user, FAIL homebrew (56/59) | FAIL not-per-user, FAIL debian |
| fixed | PASS both (64/64) | PASS both (64/64) |

## GC-01 (a) - single install without the C loader

In the image, `/usr/lib/python3/dist-packages/yaml/_yaml*.so` deleted: one system-wide
pure-Python PyYAML (`__with_libyaml__` False, no `CSafeLoader`).

| State | dispatch-guard | preflight | start-return |
|---|---|---|---|
| base, C loader | exit 1, 110/135, 21 tag-None | exit 1, 35/59, 20 tag-None | exit 1, 13/36, 21 tag-None |
| base, no C loader | exit 0, 135/135 | exit 1, 56/59 (advice only), 0 tag-None | exit 0, 57/57 |
| fixed, C loader | exit 0, 135/135 | exit 0, 64/64 | exit 0, 57/57 |
| fixed, no C loader | exit 0, 135/135 | exit 0, 64/64 | exit 0, 57/57 |

The reimport defect is C-loader-specific; starts succeed after the fix with or without it.
At base the grant test stops before its SC-08/D-14a lines, because its advice set calls the
not-yet-existing `install_command`; its red-before is QA c0's pin measurement.
