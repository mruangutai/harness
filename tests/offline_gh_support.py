#!/usr/bin/env python3
"""THE one offline-gh confinement contract for tests that launch gh-sync or factory code (FEAT-2452).

    offline_gh_env(fake_path, tmp)   -> (env, sentinel_log)
    assert_sentinel_unused(sentinel_log)

`env` is a copy of os.environ with every inherited GH_* variable removed (gh host/token config and
any retired override), FACTORY_GH set to `fake_path`, and PATH prefixed by a fresh directory under
`tmp` that holds only an executable `gh` sentinel. The sentinel appends its argv to `sentinel_log`
and exits 97 without network access, so any dispatch that ignores FACTORY_GH and reaches the
default binary is recorded rather than sent to GitHub. FACTORY_GH is the only binary override.
"""
import os
import tempfile

_SENTINEL = """#!/bin/sh
printf '%s\\n' "$*" >> {log}
exit 97
"""


def offline_gh_env(fake_path, tmp):
    """The confined child environment and the sentinel log path it writes to."""
    sentinel_dir = tempfile.mkdtemp(prefix="offline-gh-sentinel-", dir=tmp)
    if os.path.realpath(str(fake_path)).startswith(os.path.realpath(sentinel_dir) + os.sep):
        raise AssertionError(f"FACTORY_GH fake {fake_path} lies inside the sentinel directory")
    sentinel_log = os.path.join(sentinel_dir, "sentinel.log")
    sentinel = os.path.join(sentinel_dir, "gh")
    with open(sentinel, "w", encoding="utf-8") as handle:
        handle.write(_SENTINEL.format(log=_shell_quote(sentinel_log)))
    os.chmod(sentinel, 0o755)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GH_")}
    env["FACTORY_GH"] = str(fake_path)
    env["PATH"] = sentinel_dir + os.pathsep + env.get("PATH", "")
    return env, sentinel_log


def assert_sentinel_unused(sentinel_log):
    """Pass when the default-binary sentinel never ran; otherwise fail naming its logged argv."""
    if not os.path.exists(sentinel_log):
        return
    with open(sentinel_log, encoding="utf-8") as handle:
        logged = handle.read()
    if logged:
        raise AssertionError(f"default gh binary was dispatched: {logged.strip()!r}")


def _shell_quote(text):
    return "'" + text.replace("'", "'\\''") + "'"
